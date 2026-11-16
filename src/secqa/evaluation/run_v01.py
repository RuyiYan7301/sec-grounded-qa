"""v0.1 arm of the v0.2 Part A comparison: the v0.1 agent (code identical to tag v0.1.0, verify mode) on the
v0.2 questions, turned into scorer records by an adapter that reads its tool trace.

    python -m secqa.evaluation.run_v01 --split test [--subset noise]
    # writes results/<split>/v01/run_<UTC>[_noise].json, never over an earlier file

Adapter (fixed before the test run): `answer` is the agent's final answer; `evidence` is every fact the
agent looked up, i.e. each fact returned by get_fact and each found row returned by compare, with ticker,
concept (the XBRL tag), value, unit, accession, period_end and the fiscal year. `metric` is left empty
(v0.1 never names an ontology metric; the scorer then matches on ticker and concept). `plan` and `result`
are null, as the scorer specifies for v0.1. Same model and options as the v0.2 run (qwen3:8b, temperature 0).
"""
import argparse
import datetime
import json
import subprocess
from collections import Counter

from .. import agent, config
from .v2 import score as scorer

OUT = config.REPO_ROOT / "results"
ARM = "verify"


def evidence_from_trace(trace):
    ev = []
    for step in trace or []:
        tool, res, args = step.get("tool"), step.get("result") or {}, step.get("args") or {}
        if tool == "get_fact" and res.get("found"):
            for f in res.get("facts") or []:
                ev.append({"ticker": res.get("ticker"), "metric": None, "concept": res.get("tag"),
                           "value": f.get("val"), "unit": f.get("unit"), "accession": f.get("accn"),
                           "period_end": f.get("end"),
                           "period": f"FY{f['fiscal_year']}" if f.get("fiscal_year") else res.get("period")})
        elif tool == "compare":
            for r in res.get("rows") or []:
                if r.get("found"):
                    ev.append({"ticker": r.get("ticker"), "metric": None, "concept": r.get("tag"),
                               "value": r.get("val"), "unit": r.get("unit"), "accession": r.get("accn"),
                               "period_end": r.get("end"), "period": res.get("period") or args.get("period")})
    seen, out = set(), []
    for e in ev:
        k = json.dumps(e, sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=config.REPO_ROOT, capture_output=True,
                              text=True).stdout.strip() or None
    except OSError:
        return None


def run(split, subset=None, model=None):
    model = model or config.DEFAULT_MODEL
    items = json.loads((config.EVAL_DIR / "v0.2" / f"qa_{split}.json").read_text(encoding="utf-8"))
    if subset == "noise":
        ids = set(json.loads((config.EVAL_DIR / "v0.2" / "noise_subset.json").read_text(encoding="utf-8"))["ids"])
        items = [it for it in items if it["id"] in ids]
    started = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for it in items:                                   # production pass: no gold, no scorer
        out = agent.ask(it["question"], model=model, arm=ARM)
        rows.append({"id": it["id"], "question": it["question"], "answer": out["answer"], "draft": out.get("draft"),
                     "trace": out.get("trace"), "grounded": out.get("grounded"), "revised": out.get("revised"),
                     "latency_s": out.get("latency_s"), "tokens_in": out.get("tokens_in"),
                     "tokens_out": out.get("tokens_out"), "llm_calls": out.get("llm_calls")})
    gold, alts = scorer.load_gold(split)               # scoring pass
    o = scorer_ontology()
    for row in rows:
        rec = {"id": row["id"], "system": "v0.1", "answer": row["answer"],
               "evidence": evidence_from_trace(row["trace"]), "plan": None, "result": None}
        row["record"] = rec
        s = scorer.score_item(gold[row["id"]], rec, alts.get(row["id"]), o)
        row["score"] = {k: v for k, v in s.items() if k != "detail"} | {"detail": s["detail"]}
    summary = {"items": len(rows), "final_correct": sum(r["score"]["final_correct"] for r in rows),
               "by_layer": {k: {"n": n, "final_correct": sum(r["score"]["final_correct"] for r in rows
                                                              if r["score"]["layer"] == k)}
                            for k, n in Counter(r["score"]["layer"] for r in rows).items()},
               "evidence_complete": sum(bool(r["score"]["evidence_complete"]) for r in rows),
               "seconds_total": round(sum(r["latency_s"] or 0 for r in rows), 1)}
    info = {"system": "v0.1", "arm": ARM, "split": split, "subset": subset, "model": model,
            "started_utc": started.isoformat(timespec="seconds"), "commit": commit(), "scorer_version": scorer.V}
    d = OUT / split / "v01"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"run_{started.strftime('%Y%m%dT%H%M%SZ')}{'_' + subset if subset else ''}.json"
    path.write_text(json.dumps({"run": info, "summary": summary, "items": rows}, indent=1, default=str) + "\n",
                    encoding="utf-8", newline="\n")
    print(path.name)
    print(json.dumps(summary, indent=1))


def scorer_ontology():
    import yaml
    return yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--subset", choices=["noise"])
    a = ap.parse_args()
    run(a.split, a.subset)
