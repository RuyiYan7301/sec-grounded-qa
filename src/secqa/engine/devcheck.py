"""Module-level development report: resolver, period engine and calculation on the DEV split only.

    python -m secqa.engine.devcheck      # writes results/dev/engine_module_report.json

Part A: each dev item's gold plan is executed directly (planner and renderer not involved) and compared with
the dev gold: outcome, concept, period end, value of every gold cell, and the result. Part B: the CSCO dev
case, every metric through FilingFactIndex (exact target accession), compared with the CSCO provenance.
Test items and test cases are never read.
"""
import json
from collections import Counter

from .. import config, ontology
from ..facts import Store
from . import execute, resolve

OUT = config.REPO_ROOT / "results" / "dev" / "engine_module_report.json"
REL, PP = 0.005, 0.1


def close(a, b, rel=REL):
    return a is not None and b is not None and abs(a - b) <= rel * max(abs(b), 1e-9)


def gold_result_value(it):
    r = it["gold_result"]
    return r.get("val"), r.get("vals")


def part_a(o, store):
    items = json.loads((config.EVAL_DIR / "v0.2" / "qa_dev.json").read_text(encoding="utf-8"))
    src = resolve.SnapshotSource(store)
    rows = []
    for it in items:
        plan = it["gold_plan"] or {"refuse": it["gold_outcome"], "reason": "gold refusal"}
        if it["gold_outcome"] == "not_reported" and it["gold_plan"]:
            plan = it["gold_plan"]
        r = execute.execute(plan, it["question"], src, o)
        want = it["gold_outcome"] if it["gold_outcome"] != "ambiguous_year" else "answer"
        cells_ok = all(any(c["concept"] == g["concept"] and c["period_end"] == g["period_end"] and close(c["value"], g["value"])
                           and c["ticker"] == g["ticker"] for c in r.get("cells", [])) for g in it["gold_cells"])
        gv, gvals = gold_result_value(it)
        res = r.get("result") or {}
        intent = (it["gold_plan"] or {}).get("intent")
        if r["outcome"] != "answer" or want != "answer":
            result_ok = r["outcome"] == want
        elif intent in ("percent_change",):
            result_ok = res.get("percent_change") is not None and abs(res["percent_change"] - gv) <= PP
        elif intent == "percentage_point_change":
            result_ok = abs(res.get("pp_change", 1e9) - gv) <= PP
        elif intent == "ratio":
            result_ok = abs(res.get("value", 1e9) - gv) <= PP
        elif intent == "absolute_change":
            result_ok = close(res.get("absolute_change"), gv)
        elif intent in ("multi_period_lookup",):
            result_ok = all(close(a, b) for a, b in zip(res.get("values", {}).values(), gvals))
        elif intent == "cross_company_comparison":
            result_ok = all(close(a, b) for a, b in zip(res.get("values", {}).values(), gvals))
        else:
            result_ok = close(res.get("value"), gv)
        codes = {w["code"] for w in r.get("warnings", [])}
        warn_ok = set(it["required_warnings"]) <= codes
        rows.append({"id": it["id"], "intent": intent, "gold_outcome": it["gold_outcome"], "outcome": r["outcome"],
                     "outcome_ok": r["outcome"] == want, "cells_ok": cells_ok, "result_ok": result_ok,
                     "required_warnings": it["required_warnings"], "warning_codes": sorted(codes), "warnings_ok": warn_ok})
    return rows


def part_b(o):
    prov = json.loads((config.EVAL_DIR / "v0.2" / "cases" / "provenance.json").read_text(encoding="utf-8"))
    case = prov["cases"]["CSCO_FY2024"]
    idx = resolve.FilingFactIndex("CSCO", 2024)
    rows = []
    for it in case["items"]:
        gvals = [v for v in it["values"] if "value" in v]
        got = []
        for fy in (2023, 2024):
            v = execute.resolve_value(idx, o, "CSCO", it["metric"], fy)
            got += v["cells"]
        ok = len(got) == len(gvals) and all(any(
            c["concept"] == g["concept"] and c["period_end"] == g["period_end"] and close(c["value"], g["value"])
            and c["accession"] == g["reported_in_accession"] for c in got) for g in gvals)
        rows.append({"id": it["id"], "label": it["label"], "gold_values": len(gvals), "engine_values": len(got),
                     "all_match": ok, "target_accession": idx.target_accession})
    return rows


def main():
    o = ontology.load()
    store = Store()
    a, b = part_a(o, store), part_b(o)
    summary = {"A_dev_items": len(a), **{k: sum(r[k] for r in a) for k in ("outcome_ok", "cells_ok", "result_ok", "warnings_ok")},
               "A_outcomes": {f"{g} -> {e}": n for (g, e), n in Counter((r["gold_outcome"], r["outcome"]) for r in a).items()},
               "B_CSCO_items": len(b), "B_all_match": sum(r["all_match"] for r in b)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "part_a": a, "part_b": b}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))
    for r in a:
        if not (r["outcome_ok"] and r["cells_ok"] and r["result_ok"] and r["warnings_ok"]):
            print("A", r)
    for r in b:
        if not r["all_match"]:
            print("B", r)


if __name__ == "__main__":
    main()
