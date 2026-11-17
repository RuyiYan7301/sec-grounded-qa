"""The whole product (router -> typed engine or agent) on the v0.1 test set, scored by the frozen v0.1 scorer.

    python -m secqa.evaluation.product_eval      # writes results/test/product/product_<UTC>.json

The v0.1 test set (96 queries: figures, narrative, clarification, advice, forecasts) is answered the way
`secqa ask --engine auto` answers: the router picks the engine; the agent runs in verify mode, as in v0.1's
main run. Scoring is `run_eval.score`, unchanged. Adapter for typed answers, fixed before the run: the scorer
reads the agent's tool trace in two places, so a typed answer gets a synthetic trace from the engine's own
output: one step whose result holds every evidence value and every number of the computed result (so the
grounding check sees the figures the engine used), and, when the engine raised `period_mismatch`, a
`compare` step with `period_mismatch: true` (the cross-company flag check). Nothing is read from the
answer text to build it. Compared question by question with v0.1's main run (qwen3:8b, verify, t2).
"""
import datetime
import json
from collections import Counter

from .. import agent, config, tools
from ..engine import llm, router
from . import run_eval


def typed_trace(a, ex_numbers, mismatch):
    trace = [{"tool": "typed_engine", "args": {}, "result": {"values": ex_numbers}}]
    if mismatch:
        trace.append({"tool": "compare", "args": {}, "result": {"period_mismatch": True, "rows": []}})
    return trace


def run_one(q, model=None):
    from .. import typed_answer
    if tools.INJECT != bool(q.get("inject")):
        tools.INJECT, tools._index = bool(q.get("inject")), None
    log = llm.CallLog()
    r = router.route(q["query"], log=log, model=model)
    if r["route"] == "typed":
        captured = {}
        orig = typed_answer.untraced_numbers

        def spy(answer, ex):                      # keep the engine result for the adapter
            captured["ex"] = ex
            return orig(answer, ex)
        typed_answer.untraced_numbers = spy
        try:
            a = typed_answer.ask(q["query"], model=model, route_calls=log.calls)
        finally:
            typed_answer.untraced_numbers = orig
        ex = captured.get("ex", {})
        nums = [e["value"] for e in ex.get("evidence", []) if isinstance(e.get("value"), (int, float))]
        nums += typed_answer._result_numbers(ex.get("result"))
        out = {"trace": typed_trace(a, nums, any(w["code"] == "period_mismatch" for w in a.warnings))}
        s = run_eval.score(q, a.answer, out)
        return {"id": q["id"], "type": q["question_type"], "route": "typed", "why": r["why"], "answer": a.answer,
                "status": a.status, "draft": a.draft, "latency_s": a.latency_s, "llm_calls": a.llm_calls, "score": s}
    raw = agent.ask(q["query"], model=model, arm="verify")
    s = run_eval.score(q, raw["answer"], raw)
    return {"id": q["id"], "type": q["question_type"], "route": "agent", "why": r["why"], "answer": raw["answer"],
            "status": None, "draft": raw.get("draft"), "latency_s": raw["latency_s"], "llm_calls": raw["llm_calls"] + 1,
            "score": s}


def main():
    qs = json.loads((config.EVAL_DIR / "gold_test.json").read_text(encoding="utf-8"))
    rows = [run_one(q) for q in qs]
    base = {r["id"]: r["score"]["correct"] for r in json.loads(
        (config.REPO_ROOT / "results" / "test" / "verify_qwen3_8b_all_t2.json").read_text(encoding="utf-8"))["queries"]}
    pair = Counter((r["score"]["correct"], base[r["id"]]) for r in rows)
    by_type = {t: {"n": n, "product": sum(r["score"]["correct"] for r in rows if r["type"] == t)}
               for t, n in Counter(r["type"] for r in rows).items()}
    summary = {"n": len(rows), "product_correct": sum(r["score"]["correct"] for r in rows),
               "v01_verify_8b_t2_correct": sum(base[r["id"]] for r in rows),
               "paired": {"both": pair[(True, True)], "product_only": pair[(True, False)],
                          "v01_only": pair[(False, True)], "neither": pair[(False, False)]},
               "routes": dict(Counter(r["route"] for r in rows)), "by_type": by_type,
               "median_latency_s": sorted(r["latency_s"] for r in rows)[len(rows) // 2]}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = config.REPO_ROOT / "results" / "test" / "product"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"product_{ts}.json").write_text(json.dumps({"model": config.DEFAULT_MODEL, "summary": summary, "rows": rows},
                                                       indent=1, ensure_ascii=False, default=str) + "\n",
                                            encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
