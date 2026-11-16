"""End-to-end v0.2 run on Part A: planner -> deterministic execution -> renderer, then the frozen scorer.

    python -m secqa.evaluation.run_v2 --split dev      # writes results/dev/pipeline/run_<prompts-sha8>_<UTC>.json

Development runs use the dev split only; the test split is run once, after the engine freeze. The engine
package never imports a scorer; this harness does, after every item has been produced. Reports, per run:
  - structured execution correctness (outcome, result within tolerance, required warning codes present),
  - final answer correctness of the rendered text (frozen scorer 2.1),
  - renderer-caused losses: items whose execution was right but whose rendered answer was not, by cause.
Each run is a new file, never written over.
"""
import argparse
import datetime
import hashlib
import json
import time
from collections import Counter

import yaml

from .. import config
from ..engine import execute, llm, plan, render, resolve
from ..facts import Store
from .v2 import score as scorer

OUT = config.REPO_ROOT / "results"
TOL_PP, TOL_REL = 0.1, 0.005


def scorer_result(r):
    """Engine result -> the scorer record's `result` field."""
    res = r.get("result") or {}
    intent = r.get("intent")
    if r.get("outcome") == "not_meaningful":
        return {"outcome": "not_meaningful"}
    if intent in ("fact_lookup", "ratio"):
        return {"val": res.get("value")}
    if intent == "restated_value_lookup":
        return {"val": res.get("current")}
    if intent in ("multi_period_lookup", "cross_company_comparison"):
        return {"vals": list((res.get("values") or {}).values())}
    if intent == "absolute_change":
        return {"val": res.get("absolute_change")}
    if intent == "percent_change":
        return {"val": res.get("percent_change")}
    if intent == "percentage_point_change":
        return {"val": res.get("pp_change")}
    return {}


def execution_correct(item, r):
    want = item["gold_outcome"] if item["gold_outcome"] != "ambiguous_year" else "answer"
    if r.get("outcome") != want:
        return False
    if want != "answer":
        return True
    gres, sres = item["gold_result"], scorer_result(r)
    tol = item.get("tolerance") or {"kind": "relative", "rel": TOL_REL}

    def close(a, b):
        if a is None or b is None:
            return False
        return abs(a - b) <= (tol["rel"] * max(abs(b), 1e-9) if tol["kind"] == "relative" else tol["abs"])
    if "vals" in gres:
        ok = len(sres.get("vals") or []) == len(gres["vals"]) and all(close(a, b) for a, b in zip(sres["vals"], gres["vals"]))
    elif item["gold_plan"]["intent"] == "restated_value_lookup":
        res = r.get("result") or {}
        ok = close(res.get("current"), gres["val"]) and close(res.get("original"), gres["original_val"])
    else:
        ok = close(sres.get("val"), gres.get("val"))
    codes = {w["code"] for w in r.get("warnings", [])}
    return ok and set(item["required_warnings"]) <= codes


def run(split):
    items = json.loads((config.EVAL_DIR / "v0.2" / f"qa_{split}.json").read_text(encoding="utf-8"))
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    src = resolve.SnapshotSource(Store())
    prompts_sha = hashlib.sha256((plan.system_prompt() + render.SYSTEM).encode("utf-8")).hexdigest()
    started = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for it in items:                                   # production pass: no gold, no scorer
        log = llm.CallLog()
        t0 = time.perf_counter()
        p = plan.make_plan(it["question"], log)
        if p["status"] != "valid":
            r = {"outcome": "invalid_plan", "warnings": [], "evidence": []}
            rendered = {"answer": "", "renderer_input": None}
        else:
            r = execute.execute(p["plan"], it["question"], src, o)
            rendered = render.render(it["question"], p["plan"], r, log)
        rows.append({"id": it["id"], "question": it["question"], "plan": p, "execution": r, "render": rendered,
                     "calls": log.calls, "seconds": round(time.perf_counter() - t0, 3)})
    alts = scorer.load_gold(split)[1]                 # scoring pass
    gold = {it["id"]: it for it in items}
    for row in rows:
        it, r = gold[row["id"]], row["execution"]
        rec = {"id": it["id"], "system": "v0.2", "answer": row["render"]["answer"],
               "evidence": [{k: e.get(k) for k in ("ticker", "metric", "concept", "value", "unit", "accession", "period_end")}
                            | {"period": e.get("fy")} for e in r.get("evidence", [])],
               "plan": row["plan"]["plan"], "result": scorer_result(r)}
        s = scorer.score_item(it, rec, alts.get(it["id"]), o)
        row["score"] = {k: v for k, v in s.items() if k != "detail"} | {"detail": s["detail"]}
        row["execution_correct"] = execution_correct(it, r)
    summary = summarize(rows)
    run_info = {"split": split, "started_utc": started.isoformat(timespec="seconds"), "model": config.DEFAULT_MODEL,
                "options": llm.OPTIONS, "planner_prompt_sha256": hashlib.sha256(plan.system_prompt().encode()).hexdigest(),
                "renderer_prompt_sha256": hashlib.sha256(render.SYSTEM.encode()).hexdigest(), "scorer_version": scorer.V}
    out = OUT / split / "pipeline"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"run_{prompts_sha[:8]}_{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps({"run": run_info, "summary": summary, "items": rows}, indent=1, default=str) + "\n",
                    encoding="utf-8", newline="\n")
    print(path.name)
    print(json.dumps(summary, indent=1))


def summarize(rows):
    n = len(rows)
    loss = Counter()
    for r in rows:
        if r["execution_correct"] and not r["score"]["final_correct"]:
            d = r["score"]["detail"].get("canonical", {}) if isinstance(r["score"]["detail"].get("canonical"), dict) else {}
            if d.get("missing"):
                loss["number_missing_or_changed"] += 1
            if d.get("contradiction"):
                loss["contradicting_number"] += 1
            if d.get("sign_ok") is False:
                loss["direction"] += 1
            if d.get("warnings_missing"):
                loss["warning_missing"] += 1
            if d.get("fiscal_years_ok") is False:
                loss["fiscal_year"] += 1
            if r["score"]["path"] in ("refusal", "not_meaningful"):
                loss["refusal_or_not_meaningful_wording"] += 1
    calls = [c for r in rows for c in r["calls"]]
    return {"items": n,
            "plan_valid": sum(r["plan"]["status"] == "valid" for r in rows),
            "execution_correct": sum(r["execution_correct"] for r in rows),
            "final_correct": sum(r["score"]["final_correct"] for r in rows),
            "execution_right_render_wrong": sum(r["execution_correct"] and not r["score"]["final_correct"] for r in rows),
            "execution_wrong_render_right": sum(not r["execution_correct"] and r["score"]["final_correct"] for r in rows),
            "renderer_losses_by_cause": dict(loss),
            "evidence_complete": sum(r["score"]["evidence_complete"] for r in rows),
            "concept_canonical": sum(r["score"]["concept"] == "canonical" for r in rows),
            "period_ok": sum(bool(r["score"]["period_ok"]) for r in rows),
            "calculation_ok": sum(bool(r["score"]["calculation_ok"]) for r in rows),
            "intent_ok": sum(bool(r["score"]["intent_ok"]) for r in rows),
            "model_calls": len(calls), "seconds_total": round(sum(r["seconds"] for r in rows), 1),
            "prompt_tokens": sum(c["prompt_tokens"] or 0 for c in calls) if calls else None,
            "output_tokens": sum(c["output_tokens"] or 0 for c in calls) if calls else None}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev"])     # test is run once, after the engine freeze
    run(ap.parse_args().split)
