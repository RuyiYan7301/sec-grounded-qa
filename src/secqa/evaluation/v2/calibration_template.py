"""Blank calibration template for the Part A scorer: 30 slots, 15 expected to pass, 15 expected to fail.

    python -m secqa.evaluation.v2.calibration_template   # writes data/eval/v0.2/calibration/template.json

Each slot carries the item gold (question, plan, outcome, cells, result, warnings, tolerance, and the
qualified alternative where one exists), the target case and whether the targeted score is expected to
pass. The answer, evidence, plan, result and the full expected score vector are blank: an isolated
calibrator fills them in before running `calibrate.py`. The calibrator is not given the scorer source.

Items come from the dev split. Five targets have no dev item (Cisco and Oracle have no fallback concept,
no revised value and no negative value in FY2023-FY2025): those slots use the gold of a test item and are
marked `gold_source: test_gold` (question and gold only; no system output exists or is used). Two slots
(alias interpretation, ambiguous year) use calibration-only items on dev companies, built by the gold
builder and marked `gold_source: calibration_only`.
"""
import json

import yaml

from ... import config
from . import gen_qa, gold

DIR = config.EVAL_DIR / "v0.2"
OUT = DIR / "calibration" / "template.json"
VECTOR = ["final_correct", "appropriate_refusal", "evidence_complete", "plan_valid", "intent_ok", "concept",
          "period_ok", "calculation_ok"]


def _load(split):
    return {it["id"]: it for it in json.loads((DIR / f"qa_{split}.json").read_text(encoding="utf-8"))}


def _first(items, pred):
    return next(it for it in items.values() if pred(it))


def _intent(it):
    return (it["gold_plan"] or {}).get("intent")


def _calibration_item(o, cid, question, ticker, metric, fy, outcome, warnings):
    c = gold.cell(o, ticker, metric, fy)
    assert c["outcome"] == "answer", (cid, c)
    return {"id": cid, "layer": "calibration", "author": "calibration_only", "question": question,
            "gold_plan": {"intent": "fact_lookup", "metric": metric, "companies": [ticker], "periods": [f"FY{fy}"]},
            "gold_outcome": outcome, "gold_cells": gen_qa._evidence(c),
            "gold_result": {"outcome": outcome, "val": c["val"]}, "required_warnings": warnings,
            "advisory_warnings": [], "tolerance": gen_qa.tolerance(c["unit"], "fact_lookup")}


def main():
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    dev, test = _load("dev"), _load("test")
    alts = {a["item"]: a for a in json.loads((DIR / "qualified_alternatives.json").read_text(encoding="utf-8"))["items"]}
    usd = lambda it: it["gold_outcome"] == "answer" and _intent(it) == "fact_lookup" and len(it["gold_cells"]) == 1
    fact_usd = _first(dev, lambda it: usd(it) and it["gold_cells"][0]["unit"] == "USD" and it["id"] not in alts)
    fact_usd2 = _first(dev, lambda it: usd(it) and it["gold_cells"][0]["unit"] == "USD" and it["id"] not in alts
                       and it["id"] != fact_usd["id"])
    eps = _first(dev, lambda it: it["gold_outcome"] == "answer" and any(c["unit"] == "USD/shares" for c in it["gold_cells"]))
    shares = _first(dev, lambda it: it["gold_outcome"] == "answer" and any(c["unit"] == "shares" for c in it["gold_cells"]))
    pct = _first(dev, lambda it: it["gold_outcome"] == "answer" and _intent(it) == "percent_change")
    pp = _first(dev, lambda it: it["gold_outcome"] == "answer" and _intent(it) == "percentage_point_change")
    change = _first(dev, lambda it: it["gold_outcome"] == "answer" and _intent(it) in ("absolute_change", "percent_change")
                    and it["id"] != pct["id"])
    cross = [it for it in dev.values() if _intent(it) == "cross_company_comparison" and "period_mismatch" in it["required_warnings"]]
    ratio = _first(dev, lambda it: it["gold_outcome"] == "answer" and _intent(it) == "ratio")
    nr = _first(dev, lambda it: it["gold_outcome"] == "not_reported")
    uns = _first(dev, lambda it: it["gold_outcome"] == "unsupported")
    ooo = _first(dev, lambda it: it["gold_outcome"] == "out_of_ontology")
    ltd = next(it for it in dev.values() if it["id"] in alts)
    neg = _first(test, lambda it: usd(it) and it["gold_cells"][0]["value"] < 0)
    scope = _first(test, lambda it: "scope" in it["required_warnings"] and _intent(it) == "fact_lookup")
    restated = _first(test, lambda it: "restated" in it["required_warnings"] and _intent(it) == "restated_value_lookup")
    nm = [it for it in test.values() if it["gold_outcome"] == "not_meaningful"]
    alias = _calibration_item(o, "A-cal-alias-001", "What was Cisco's EPS in fiscal 2024?", "CSCO", "eps_diluted", 2024,
                              "answer", ["alias_interpretation"])
    amb = _calibration_item(o, "A-cal-year-001", "What was Cisco's revenue in 2024?", "CSCO", "revenue", 2024,
                            "ambiguous_year", ["ambiguous_year"])

    S = [  # (slot, category, target, item, system, targeted score, expected pass)
        ("N1", "numeric", "wrong unit scaling (e.g. billions written as millions)", fact_usd, "v0.1", "final_correct", False),
        ("N2", "numeric", "EPS with two decimals", eps, "v0.1", "final_correct", True),
        ("N3", "numeric", "share count", shares, "v0.1", "final_correct", True),
        ("N4", "numeric", "percent change in natural wording", pct, "v0.1", "final_correct", True),
        ("N5", "numeric", "percentage-point change in natural wording (pp / points / percentage points)", pp, "v0.1",
         "final_correct", True),
        ("N6", "numeric", "negative amount stated without loss, minus sign or parentheses", neg, "v0.1", "final_correct", False),
        ("N7", "numeric", "wrong number (plausible but outside tolerance)", fact_usd2, "v0.1", "final_correct", False),
        ("N8", "numeric", "direction contradicts the gold change", change, "v0.1", "final_correct", False),
        ("W1", "warning", "period mismatch stated in natural wording", cross[0], "v0.1", "final_correct", True),
        ("W2", "warning", "scope (fallback concept) stated", scope, "v0.1", "final_correct", True),
        ("W3", "warning", "restatement stated, current and original value", restated, "v0.1", "final_correct", True),
        ("W4", "warning", "bare EPS interpreted as diluted, stated", alias, "v0.1", "final_correct", True),
        ("W5", "warning", "bare year interpreted as a fiscal year, stated", amb, "v0.1", "final_correct", True),
        ("W6", "warning", "required period-mismatch warning missing", cross[1], "v0.1", "final_correct", False),
        ("R1", "refusal", "correct refusal, not reported", nr, "v0.1", "final_correct", True),
        ("R2", "refusal", "investment-advice question declined", uns, "v0.1", "final_correct", True),
        ("R3", "refusal", "refusal that still states a figure", ooo, "v0.1", "final_correct", False),
        ("R4", "refusal", "negative base handled: says not meaningful, no percentage", nm[0], "v0.1", "final_correct", True),
        ("R5", "refusal", "negative base: a percentage is stated anyway", nm[1], "v0.1", "final_correct", False),
        ("E1", "evidence", "complete evidence for every stated number", ratio, "v0.1", "evidence_complete", True),
        ("E2", "evidence", "an evidence item without accession or period_end", fact_usd, "v0.1", "evidence_complete", False),
        ("E3", "evidence", "a stated number that no evidence value supports", fact_usd2, "v0.1", "evidence_complete", False),
        ("S1", "structured", "v0.2 record fully correct (plan, cells, result)", ratio, "v0.2", "calculation_ok", True),
        ("S2", "structured", "plan does not validate against the schema", pct, "v0.2", "plan_valid", False),
        ("S3", "structured", "plan intent differs from gold", pct, "v0.2", "intent_ok", False),
        ("S4", "structured", "a cell uses the wrong concept", fact_usd, "v0.2", "concept", False),
        ("S5", "structured", "a cell uses the wrong period end", fact_usd2, "v0.2", "period_ok", False),
        ("S6", "structured", "result does not follow from the system's own cells", pp, "v0.2", "calculation_ok", False),
        ("L1", "long_term_debt", "noncurrent basis stated explicitly, all cells noncurrent", ltd, "v0.1", "final_correct", True),
        ("L2", "long_term_debt", "noncurrent values without saying so, or bases mixed", ltd, "v0.1", "final_correct", False),
    ]
    assert len(S) == 30 and sum(s[6] for s in S) == 15
    test_ids = {neg["id"], scope["id"], restated["id"], nm[0]["id"], nm[1]["id"]}
    slots = []
    for slot, cat, target, it, system, scored, expect in S:
        src = "test_gold" if it["id"] in test_ids else "calibration_only" if it["layer"] == "calibration" else "dev"
        slots.append({
            "slot": slot, "category": cat, "target": target,
            "targeted_score": scored, "targeted_expected": "pass" if expect else "fail",
            "gold_source": src, "item": it, "qualified_alternative": alts.get(it["id"]),
            "record": {"id": it["id"], "system": system, "answer": "", "evidence": [],
                       "plan": None if system == "v0.1" else {}, "result": None if system == "v0.1" else {}},
            "expected_scores": {k: None for k in VECTOR},
            "calibrator_note": ""})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"version": 1, "n": len(slots), "expected_pass": 15, "expected_fail": 15,
                               "vector": VECTOR, "slots": slots}, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print({s["slot"]: (s["item"]["id"], s["gold_source"]) for s in slots})


if __name__ == "__main__":
    main()
