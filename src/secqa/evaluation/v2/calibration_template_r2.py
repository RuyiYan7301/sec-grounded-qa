"""Round-2 (held-out) calibration template for the Part A scorer: 30 dev slots, 15 pass, 15 fail.

    python -m secqa.evaluation.v2.calibration_template_r2   # writes data/eval/v0.2/calibration_r2/template.json

Rules (set by the project owner before this template was made): new dev records, different questions and
error types from round 1 where the dev split allows; written by a fresh Codex session that does not see
the scorer, its tests, or anything from round 1; answers, evidence, plan, result and the full expected
vector are fixed before the single run; the raw output is kept. If the run exposes a scorer bug, this
round is reported as failed, becomes development data, and a third unseen set is the confirmation.

Only dev items are used. 23 of the 40 dev items were not used in round 1; two targets have a single dev
item and reuse a round-1 item with a different error: the advice question (A-dev-adv-005) and the
long-term-debt item (A-dev-gen-010).
"""
import json

from ... import config

DIR = config.EVAL_DIR / "v0.2"
OUT = DIR / "calibration_r2" / "template.json"
VECTOR = ["final_correct", "appropriate_refusal", "evidence_complete", "plan_valid", "intent_ok", "concept",
          "period_ok", "calculation_ok"]

SLOTS = [  # (slot, item, system, target, targeted score, expected pass)
    ("P01", "A-dev-gen-008", "v0.1", "amount written with an abbreviated scale (e.g. '$9.86bn')", "final_correct", True),
    ("P02", "A-dev-han-001", "v0.1", "amount written out in full dollars with thousands separators", "final_correct", True),
    ("P03", "A-dev-gen-009", "v0.1", "all three fiscal-year values listed in one sentence", "final_correct", True),
    ("P04", "A-dev-gen-013", "v0.1", "period mismatch stated in words different from 'mismatch'", "final_correct", True),
    ("P05", "A-dev-gen-018", "v0.1", "absolute change with both year values and an increase/decrease verb", "final_correct", True),
    ("P06", "A-dev-gen-020", "v0.1", "percent change rounded to one decimal, still within tolerance", "final_correct", True),
    ("P07", "A-dev-gen-028", "v0.1", "margin stated as a percentage in a full sentence", "final_correct", True),
    ("P08", "A-dev-gen-026", "v0.1", "percentage-point change written with 'points'", "final_correct", True),
    ("P09", "A-dev-adv-003", "v0.1", "not-reported metric declined in plain wording", "final_correct", True),
    ("P10", "A-dev-adv-006", "v0.1", "fiscal year outside the covered range declined", "final_correct", True),
    ("P11", "A-dev-adv-004", "v0.1", "near-neighbour concept: the right net income line reported", "final_correct", True),
    ("P12", "A-dev-gen-021", "v0.2", "v0.2 record fully correct for a percent change (plan, cells, result)", "calculation_ok", True),
    ("P13", "A-dev-han-002", "v0.2", "v0.2 record fully correct for a cross-company comparison", "calculation_ok", True),
    ("P14", "A-dev-gen-029", "v0.1", "answer formatted as a small markdown table, every number traceable", "evidence_complete", True),
    ("P15", "A-dev-gen-010", "v0.1", "long-term debt on the canonical basis (current plus noncurrent)", "final_correct", True),
    ("F01", "A-dev-gen-009", "v0.1", "multi-period list that omits one of the requested years", "final_correct", False),
    ("F02", "A-dev-gen-014", "v0.1", "cross-company values attributed to the wrong companies (swapped)", "final_correct", False),
    ("F03", "A-dev-gen-022", "v0.1", "percent change computed on the wrong base year", "final_correct", False),
    ("F04", "A-dev-gen-016", "v0.1", "absolute change with the right magnitude but the wrong direction", "final_correct", False),
    ("F05", "A-dev-gen-004", "v0.1", "basic EPS given when diluted EPS was asked", "final_correct", False),
    ("F06", "A-dev-han-002", "v0.1", "cross-company comparison without the required period-mismatch warning", "final_correct", False),
    ("F07", "A-dev-adv-006", "v0.1", "out-of-range year declined but a nearby year's figure is offered instead", "final_correct", False),
    ("F08", "A-dev-adv-005", "v0.1", "valuation question answered with an investment opinion", "final_correct", False),
    ("F09", "A-dev-gen-025", "v0.1", "percentage-point change reported as a relative percent change", "final_correct", False),
    ("F10", "A-dev-han-004", "v0.2", "v0.2 plan resolves the wrong metric, so the cells use a wrong concept", "concept", False),
    ("F11", "A-dev-han-005", "v0.2", "v0.2 cells taken from the wrong fiscal year", "period_ok", False),
    ("F12", "A-dev-han-003", "v0.2", "v0.2 plan missing a required field", "plan_valid", False),
    ("F13", "A-dev-gen-005", "v0.1", "an evidence item with an empty accession", "evidence_complete", False),
    ("F14", "A-dev-gen-023", "v0.1", "answer adds a number that no evidence supports", "evidence_complete", False),
    ("F15", "A-dev-gen-010", "v0.1", "long-term debt list mixing total and noncurrent values", "final_correct", False),
]


def main():
    dev = {it["id"]: it for it in json.loads((DIR / "qa_dev.json").read_text(encoding="utf-8"))}
    alts = {a["item"]: a for a in json.loads((DIR / "qualified_alternatives.json").read_text(encoding="utf-8"))["items"]}
    assert len(SLOTS) == 30 and sum(s[5] for s in SLOTS) == 15
    slots = []
    for slot, iid, system, target, scored, expect in SLOTS:
        it = dev[iid]
        slots.append({
            "slot": slot, "target": target, "targeted_score": scored,
            "targeted_expected": "pass" if expect else "fail", "gold_source": "dev",
            "item": it, "qualified_alternative": alts.get(iid),
            "record": {"id": iid, "system": system, "answer": "", "evidence": [],
                       "plan": None if system == "v0.1" else {}, "result": None if system == "v0.1" else {}},
            "expected_scores": {k: None for k in VECTOR}, "calibrator_note": ""})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"version": 2, "round": 2, "single_run": True, "n": 30, "expected_pass": 15,
                               "expected_fail": 15, "vector": VECTOR, "slots": slots}, indent=1, ensure_ascii=False)
                   + "\n", encoding="utf-8", newline="\n")
    print(len(slots), "slots;", len({s[1] for s in SLOTS}), "distinct dev items")


if __name__ == "__main__":
    main()
