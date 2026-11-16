"""Part A: pre-registered qualified alternative answers (written before the scorer and before any run).

    python -m secqa.evaluation.v2.qualified_alternatives   # writes data/eval/v0.2/qualified_alternatives.json

Only for `long_term_debt`. The canonical gold stays LongTermDebt (current plus noncurrent portion, frozen
ontology). A balance-sheet line titled "Long-term debt" is often the noncurrent portion only, so an answer
built entirely on LongTermDebtNoncurrent is accepted as `qualified_alternative` when it says so explicitly.
Values come from the raw companyfacts rows through gold.value, same period end and same value policy
(latest_in_snapshot) as the canonical cell. The scorer may use only what is in this file; it never looks
for an alternative in a system's output.
"""
import json

from ... import config
from . import gold

QA = [config.EVAL_DIR / "v0.2" / f for f in ("qa_test.json", "qa_dev.json")]
OUT = config.EVAL_DIR / "v0.2" / "qualified_alternatives.json"
METRIC, ALT_TAG = "long_term_debt", "LongTermDebtNoncurrent"
QUALIFIER = ("the answer states that the figure is the noncurrent portion only, e.g. 'noncurrent portion', "
             "'excluding current maturities' or 'excludes the current portion'")


def main():
    items = [it for path in QA for it in json.loads(path.read_text(encoding="utf-8"))]
    out = []
    for it in items:
        if not it["gold_plan"] or it["gold_plan"]["metric"] != METRIC or it["gold_outcome"] != "answer":
            continue
        intent = it["gold_plan"]["intent"]
        cells = []
        for c in it["gold_cells"]:
            v = gold.value(c["ticker"], ALT_TAG, int(c["period"][2:]), "instant")
            assert v and v["end"] == c["period_end"], (it["id"], c["ticker"], c["period"])
            cells.append({"ticker": c["ticker"], "period": c["period"], "concept": ALT_TAG, "value": v["val"],
                          "unit": v["unit"], "accession": v["accn"], "period_end": v["end"]})
        vals = [c["value"] for c in cells]
        if intent == "fact_lookup":
            result = {"outcome": "answer", "val": vals[0]}
        elif intent == "cross_company_comparison":
            result = {"outcome": "answer", "vals": vals, "difference": vals[0] - vals[1]}
        elif intent == "multi_period_lookup":
            result = {"outcome": "answer", "vals": vals}
        elif intent == "percent_change":
            r = gold.change(vals[0], vals[1], intent)
            result = {**r, "val": r["val"] * 100, "unit": "percent", "formula": "(v2 - v1) / v1"}
        else:
            raise ValueError(intent)
        out.append({"item": it["id"], "split": it["id"].split("-")[1], "status": "qualified_alternative", "canonical_concept": "LongTermDebt",
                    "alternative_concept": ALT_TAG, "required_qualifier": QUALIFIER,
                    "same_basis_required": "every cell of the answer on the alternative concept; mixing "
                                           "LongTermDebt and LongTermDebtNoncurrent is wrong",
                    "required_warnings": it["required_warnings"], "tolerance": it["tolerance"],
                    "cells": cells, "result": result})
    OUT.write_text(json.dumps({"rule": "docs/benchmark-v0.2.md, Part A, 'Qualified alternatives'",
                               "items": out}, indent=1) + "\n", encoding="utf-8", newline="\n")
    for a in out:
        print(a["item"], a["result"])


if __name__ == "__main__":
    main()
