"""Development run of the real planner on the 40 A-dev questions (one complete run, no code change midway).

    python -m secqa.engine.devrun_planner      # writes results/dev/planner/run_<prompt-sha8>_<UTC time>.json

Protocol: the planner sees only the question (and, for one repair, its own invalid plan and the schema
errors). The dev gold plans are read only AFTER all questions have been planned, to score the run. Each run
is a new file; a changed prompt is a new development version, never written over an earlier run.
"""
import datetime
import hashlib
import json
import time

import requests

from .. import config
from . import llm, plan

OUT = config.REPO_ROOT / "results" / "dev" / "planner"
DEV = config.EVAL_DIR / "v0.2" / "qa_dev.json"
OPS = {"fact_lookup": "lookup", "restated_value_lookup": "lookup"}


def ollama_info(model):
    v = requests.get(f"{config.OLLAMA_HOST}/api/version", timeout=10).json().get("version")
    tags = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=10).json().get("models", [])
    digest = next((m.get("digest") for m in tags if m.get("name") == model or m.get("model") == model), None)
    return {"ollama_version": v, "model": model, "model_digest": digest}


def run():
    model = config.DEFAULT_MODEL
    prompt_sha = hashlib.sha256(plan.system_prompt().encode("utf-8")).hexdigest()
    questions = [(it["id"], it["question"]) for it in json.loads(DEV.read_text(encoding="utf-8"))]
    info = ollama_info(model)
    started = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for iid, q in questions:            # planning pass: no gold in scope
        log = llm.CallLog()
        t0 = time.perf_counter()
        r = plan.make_plan(q, log)
        rows.append({"id": iid, "question": q, "status": r["status"], "first_pass_valid": r["first_pass_valid"],
                     "repaired": r["repaired"], "plan": r["plan"], "attempts": r["attempts"],
                     "calls": log.calls, "seconds": round(time.perf_counter() - t0, 3)})
    gold = {it["id"]: it for it in json.loads(DEV.read_text(encoding="utf-8"))}   # scoring pass only
    for row in rows:
        row["score"] = score(row["plan"], gold[row["id"]])
    summary = summarize(rows)
    doc = {"run": {"started_utc": started.isoformat(timespec="seconds"), **info, "options": llm.OPTIONS,
                   "think": False, "planner_prompt_sha256": prompt_sha, "max_repairs": plan.MAX_REPAIRS,
                   "plan_schema_sha256": hashlib.sha256(plan.SCHEMA_PATH.read_bytes()).hexdigest()},
           "summary": summary, "items": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"run_{prompt_sha[:8]}_{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(path.name)
    print(json.dumps(summary, indent=1))
    return doc


def score(p, it):
    g = it["gold_plan"]
    if p is None:
        return {"valid": False}
    if it["gold_outcome"] in ("out_of_ontology", "unsupported", "out_of_range", "unsupported_operation") and not g:
        return {"valid": True, "refusal_expected": it["gold_outcome"], "refuse_ok": p.get("refuse") == it["gold_outcome"]}
    if "refuse" in p:
        return {"valid": True, "refused": p["refuse"], "intent": False, "metric": False, "companies": False,
                "periods": False, "operation": False}
    return {"valid": True, "intent": p.get("intent") == g["intent"], "metric": p.get("metric") == g["metric"],
            "companies": p.get("companies") == g["companies"], "periods": p.get("periods") == g["periods"],
            "operation": OPS.get(p.get("intent"), p.get("intent")) == OPS.get(g["intent"], g["intent"])}


def summarize(rows):
    n = len(rows)
    ans = [r for r in rows if "refusal_expected" not in r["score"]]
    ref = [r for r in rows if "refusal_expected" in r["score"]]
    calls = [c for r in rows for c in r["calls"]]

    def tot(k):
        vals = [c[k] for c in calls if c[k] is not None]
        return sum(vals) if vals else None
    out = {"items": n, "first_pass_valid": sum(r["first_pass_valid"] for r in rows),
           "repair_attempted": sum(not r["first_pass_valid"] for r in rows),
           "repair_succeeded": sum(r["repaired"] for r in rows),
           "final_valid": sum(r["status"] == "valid" for r in rows),
           "answer_items": len(ans), "refusal_items": len(ref),
           "refusal_correct": sum(r["score"].get("refuse_ok", False) for r in ref),
           "model_calls": len(calls), "prompt_tokens": tot("prompt_tokens"), "output_tokens": tot("output_tokens"),
           "seconds_total": round(sum(r["seconds"] for r in rows), 1),
           "seconds_median_item": sorted(r["seconds"] for r in rows)[n // 2]}
    for k in ("intent", "metric", "companies", "periods", "operation"):
        out[f"{k}_correct"] = sum(r["score"].get(k, False) for r in ans)
    out["all_fields_correct"] = sum(all(r["score"].get(k, False) for k in ("intent", "metric", "companies", "periods"))
                                    for r in ans)
    return out


if __name__ == "__main__":
    run()
