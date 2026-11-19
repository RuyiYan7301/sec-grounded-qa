"""v0.4 step 2, test runs (docs/v0.4-plan.md 3d): plans from every arm -> frozen executor -> 8B renderer ->
frozen scorer 2.1, plus the secondary provenance count (evaluation/v4/provenance.py).

    python -m secqa.evaluation.v4.run_step2 gold   --set t1            # gold plans through the v0.4 engine
    python -m secqa.evaluation.v4.run_step2 plan8b --set t1            # arm T: frozen qwen3:8b planner
    python -m secqa.evaluation.v4.run_step2 render --set t1 --plans results/v0.4/step2/t1/plans_S.json

Test sets: t1 = frozen v0.2 Part A test (data/eval/v0.2/qa_test.json, qualified alternatives as in v0.2),
t2 = qa_heldout_2611 (generated, held-out templates, test companies). Excluded items (EXCLUDE) are fixed
in the plan amendment before any test run. Plans of the 1.7B arms come from train/eval_planner.py (same
item order, `plan` = validated plan or null); arm T plans come from `plan8b`. `render` executes each plan
with the same per-plan fact stores as 2b, renders with the frozen 8B renderer and scores.
"""
import argparse
import datetime
import json
import time

import yaml

from ... import config, universe
from ...engine import execute, llm, plan as planmod, render
from ..run_v01 import commit
from ..run_v2 import execution_correct, scorer_result, summarize
from ..v2 import score as scorer
from . import provenance
from .run_2b import Stores

SETS = {"t1": config.EVAL_DIR / "v0.2" / "qa_test.json", "t2": config.EVAL_DIR / "v0.4" / "qa_heldout_2611.json"}
# A-test-adv-033 "What was Microsoft's net income in fiscal 2021?": gold out_of_range under the v0.2 year
# range; v0.4 covers FY2019-FY2025, so the gold no longer holds (plan amendment 2026-11-19).
EXCLUDE = {"t1": {"A-test-adv-033"}, "t2": set()}
OUT = config.REPO_ROOT / "results" / "v0.4" / "step2"
REFUSALS = {"out_of_ontology", "unsupported", "out_of_range", "unsupported_operation", "invalid_plan"}
ANSWERABLE = ("answer", "not_meaningful", "ambiguous_year")


def load(name):
    d = json.loads(SETS[name].read_text(encoding="utf-8"))
    items = d["items"] if isinstance(d, dict) else d
    return [it for it in items if it["id"] not in EXCLUDE[name]]


def template_half(question):
    """'train' / 'test': the template half a generated t1 question came from (plan clarification 2026-11-18).
    A question can match a generic template too ("What was {co}'s {m} in fiscal {y}?"); the template with
    the longest literal text wins."""
    import re
    sp = json.loads((config.REPO_ROOT / "data" / "train" / "v0.4" / "splits.json").read_text(encoding="utf-8"))["templates"]
    hits = []
    for half, d in sp.items():
        for ts in d.values():
            for t in ts:
                if re.match("^" + re.sub(r"\\{\w+\\}", ".+?", re.escape(t)) + "$", question):
                    hits.append((len(re.sub(r"\{\w+\}", "", t)), half))
    return max(hits)[1] if hits else None


def ontology():
    return yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))


def gold(name):
    """Execution check of each item's gold plan under the current engine (harness and gold agree?)."""
    from ...train.build_data import target
    universe.activate()
    o, stores, bad = ontology(), Stores(), []
    items = load(name)
    for it in items:
        p = target(it)
        src = None if "refuse" in p else stores.source(p.get("companies") or [])
        r = execute.execute(p, it["question"], src, o)
        if not execution_correct(it, r):
            bad.append({"id": it["id"], "question": it["question"], "gold_outcome": it["gold_outcome"],
                        "engine_outcome": r.get("outcome"), "engine_result": r.get("result")})
    print(json.dumps({"set": name, "items": len(items), "gold_plan_execution_correct": len(items) - len(bad),
                      "disagree": bad}, indent=1, default=str))


def plan8b(name):
    universe.activate()
    rows = []
    for k, it in enumerate(load(name), 1):
        log = llm.CallLog()
        t0 = time.perf_counter()
        p = planmod.make_plan(it["question"], log)
        rows.append({"id": it["id"], "question": it["question"], "plan": p["plan"], "status": p["status"],
                     "repaired": p.get("repaired"), "raw": p["attempts"], "seconds": round(time.perf_counter() - t0, 3)})
        print(k, it["id"], p["status"], rows[-1]["seconds"], flush=True)
    out = OUT / name / "plans_T.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"args": {"arm": "T", "model": config.DEFAULT_MODEL, "options": llm.OPTIONS,
                                        "commit": commit()}, "items": rows}, indent=1, default=str), encoding="utf-8")
    print(out)


def render_arm(name, plans_path, tag):
    universe.activate()
    items = {it["id"]: it for it in load(name)}
    prows = [r for r in json.loads((config.REPO_ROOT / plans_path).read_text(encoding="utf-8"))["items"] if r["id"] in items]
    assert [r["id"] for r in prows] == list(items), "plan file and test set differ in items or order"
    o, stores = ontology(), Stores()
    alts = scorer.load_gold("test")[1] if name == "t1" else {}
    started = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for k, pr in enumerate(prows, 1):
        it, p = items[pr["id"]], pr["plan"]
        log = llm.CallLog()
        t0 = time.perf_counter()
        if p is None:
            r = {"outcome": "invalid_plan", "warnings": [], "evidence": []}
            rendered = {"answer": "", "renderer_input": None}
        else:
            src = None if "refuse" in p else stores.source(p.get("companies") or [])
            try:
                r = execute.execute(p, it["question"], src, o)
            except Exception as e:                   # noqa: BLE001  frozen executor crash on a valid plan
                r = {"outcome": "executor_error", "error": repr(e), "warnings": [], "evidence": []}
            if r["outcome"] == "executor_error":     # no answer to render; scored wrong
                rendered = {"answer": "", "renderer_input": None}
            else:
                rendered = render.render(it["question"], p, r, log)
        rec = {"id": it["id"], "system": "v0.2", "answer": rendered["answer"],
               "evidence": [{k2: e.get(k2) for k2 in ("ticker", "metric", "concept", "value", "unit", "accession", "period_end")}
                            | {"period": e.get("fy")} for e in r.get("evidence", [])],
               "plan": p, "result": scorer_result(r)}
        s = scorer.score_item(it, rec, alts.get(it["id"]), o)
        s2 = provenance.score_item(it, rec, r, o)
        gp = it.get("gold_plan") or {}
        rows.append({"id": it["id"], "layer": it.get("layer"), "question": it["question"],
                     "gold_outcome": it["gold_outcome"], "gold_intent": gp.get("intent"),
                     "plan": {"plan": p, "status": "valid" if p is not None else "invalid_plan"},
                     "plan_seconds": pr.get("seconds"), "execution": r, "render": rendered, "calls": log.calls,
                     "seconds": round(time.perf_counter() - t0, 3),
                     "score": {k2: v for k2, v in s.items() if k2 != "detail"} | {"detail": s["detail"]},
                     "final_correct_provenance": s2["final_correct"], "provenance_masked": s2["provenance_masked"],
                     "execution_correct": execution_correct(it, r),
                     "extra_period_restated": bool(p and gp.get("intent") == "restated_value_lookup"
                                                   and "refuse" not in p and set(p.get("periods") or []) != set(gp["periods"]))})
        print(k, it["id"], r.get("outcome"), rows[-1]["score"]["final_correct"], rows[-1]["seconds"], flush=True)
    summary = summarize(rows)
    ans = [r for r in rows if r["gold_outcome"] in ANSWERABLE]
    summary |= {"final_correct_provenance": sum(r["final_correct_provenance"] for r in rows),
                "provenance_masked_items": sum(r["provenance_masked"] > 0 for r in rows),
                "answerable": len(ans),
                "refused_answerable": sum(r["execution"].get("outcome") in REFUSALS for r in ans),
                # an answer came out (not a refusal, not invalid) and it is scored wrong
                "silent_wrong": sum(r["execution"].get("outcome") not in REFUSALS | {"executor_error"} and not r["score"]["final_correct"]
                                    for r in rows),
                "executor_error": sum(r["execution"].get("outcome") == "executor_error" for r in rows),
                "restated_plans_extra_period": sum(r["extra_period_restated"] for r in rows),
                "median_plan_seconds": sorted(r["plan_seconds"] or 0 for r in rows)[len(rows) // 2]}
    out = OUT / name / f"run_{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"run": {"set": name, "arm": tag, "plans": str(plans_path), "commit": commit(),
                                       "started_utc": started.isoformat(timespec="seconds"), "model": config.DEFAULT_MODEL,
                                       "options": llm.OPTIONS, "scorer_version": scorer.V, "excluded": sorted(EXCLUDE[name])},
                               "summary": summary, "items": rows}, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(out)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gold", "plan8b", "render"])
    ap.add_argument("--set", required=True, choices=list(SETS))
    ap.add_argument("--plans")
    ap.add_argument("--tag")
    a = ap.parse_args()
    if a.cmd == "gold":
        gold(a.set)
    elif a.cmd == "plan8b":
        plan8b(a.set)
    else:
        render_arm(a.set, a.plans, a.tag)
