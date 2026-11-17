"""How often the router sends a question to the right engine (expected routes fixed before the run).

    python -m secqa.evaluation.route_eval        # writes results/test/routing/route_<UTC>.json

Expected routes: every v0.2 Part A test question (160) -> typed: they all ask for figures, advice, forecasts or
unsupported metrics, which the typed engine answers or refuses. v0.1 test questions (96): narrative,
narrative_absent and clarify_company -> agent (filing text, or a question that names no company); every other
type -> typed. The router prompt was written without looking at these questions and is not tuned on them.
"""
import datetime
import json
from collections import Counter

from .. import config
from ..engine import llm, router

AGENT_TYPES = {"narrative", "narrative_absent", "clarify_company"}


def items():
    a = json.loads((config.EVAL_DIR / "v0.2" / "qa_test.json").read_text(encoding="utf-8"))
    b = json.loads((config.EVAL_DIR / "gold_test.json").read_text(encoding="utf-8"))
    return ([{"set": "v0.2", "id": x["id"], "kind": x["layer"], "question": x["question"], "expected": "typed"} for x in a]
            + [{"set": "v0.1", "id": x["id"], "kind": x["question_type"], "question": x["query"],
                "expected": "agent" if x["question_type"] in AGENT_TYPES else "typed"} for x in b])


def main():
    rows, log = [], llm.CallLog()
    for it in items():
        r = router.route(it["question"], log=log)
        rows.append(it | {"routed": r["route"], "why": r["why"], "ok": r["route"] == it["expected"]})
    by = Counter((r["set"], r["expected"], r["ok"]) for r in rows)
    summary = {"n": len(rows), "correct": sum(r["ok"] for r in rows),
               "by_set_and_expected": {f"{s}:{e}": {"n": by[(s, e, True)] + by[(s, e, False)], "correct": by[(s, e, True)]}
                                       for s, e in sorted({(r["set"], r["expected"]) for r in rows})},
               "errors": [{k: r[k] for k in ("set", "id", "kind", "question", "expected", "routed", "why")} for r in rows if not r["ok"]],
               "model_calls": len(log.calls), "seconds": round(sum(c["seconds"] for c in log.calls), 1)}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = config.REPO_ROOT / "results" / "test" / "routing"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"route_{ts}.json").write_text(json.dumps({"model": config.DEFAULT_MODEL, "summary": summary, "rows": rows},
                                                     indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "errors"}, indent=1))
    for e in summary["errors"]:
        print(e["set"], e["id"], e["kind"], "expected", e["expected"], "->", e["routed"], "|", e["question"][:90])


if __name__ == "__main__":
    main()
