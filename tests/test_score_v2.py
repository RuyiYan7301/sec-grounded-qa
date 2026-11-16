"""Part A scorer v2.0 on synthetic answers built from the gold only (no system output is used)."""
import copy

import pytest
import yaml

from secqa import config
from secqa.evaluation.v2 import score as S

ONT = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
WARN_TEXT = {"period_mismatch": "Note that the two fiscal years end on different dates.",
             "scope": "This uses a broader fallback concept.",
             "restated": "The value was restated after it was first reported.",
             "alias_interpretation": "EPS is interpreted as diluted EPS.",
             "ambiguous_year": "I read 2024 as fiscal 2024, which ended in January 2024."}


def money(v, unit):
    a = abs(v)
    if unit and "/" in unit:
        return f"${a:.2f}"
    if unit == "shares":
        return f"{a / 1e6:,.0f} million shares"
    return f"${a / 1e9:.3f} billion"


def perfect(item, result=None, cells=None, warnings=None, extra=""):
    """A correct answer and its evidence, written from the gold."""
    o = item["gold_outcome"]
    if o in S.REFUSALS:
        text = {"unsupported": "I can't give investment advice or predictions."}.get(
            o, "That figure is not reported in the filings I can use.")
        return {"answer": text, "evidence": []}
    if o == "not_meaningful":
        return {"answer": "A percentage change is not meaningful because the base is negative.", "evidence": []}
    result = result or item["gold_result"]
    cells = cells if cells is not None else item["gold_cells"]
    warnings = item["required_warnings"] if warnings is None else warnings
    unit = result.get("unit")
    intent = item["gold_plan"]["intent"]
    parts = []
    for c in cells:
        neg = " (a loss of" if c["value"] < 0 else ""
        parts.append(f"{c['ticker']} {c['period']}: {money(c['value'], c.get('unit'))}{neg and ', a loss'}")
    if "original_val" in result:
        parts.append(f"originally reported as {money(result['original_val'], cells[0].get('unit'))}")
    if intent == "fact_lookup" and "val" in result and len(cells) > 1:     # derived metric (e.g. free cash flow)
        parts.append(f"{item['gold_plan']['metric']}: {money(result['val'], cells[0].get('unit'))}")
    if intent in ("absolute_change", "percent_change", "percentage_point_change", "ratio"):
        v = result["val"]
        word = "" if intent == "ratio" else ("decreased by " if v < 0 else "increased by ")
        if unit == "percent":
            parts.append(f"{word}{abs(v):.2f}%")
        elif unit == "pp":
            parts.append(f"{word}{abs(v):.2f} percentage points")
        else:
            parts.append(f"{word}{money(v, cells[0].get('unit'))}")
    text = "; ".join(parts) + ". " + " ".join(WARN_TEXT[w] for w in warnings) + extra
    ev = [{**c, "metric": c.get("metric")} for c in cells]
    if "original_val" in result:
        ev.append({**cells[0], "value": result["original_val"], "accession": result["original_accession"]})
    return {"answer": text, "evidence": ev}


@pytest.fixture(scope="module", params=["test", "dev"])
def gold(request):
    return S.load_gold(request.param)


def test_perfect_answers_score_correct(gold):
    items, alts = gold
    bad = []
    for i, it in items.items():
        rec = {"id": i, "system": "v0.1", **perfect(it)}
        r = S.score_item(it, rec, alts.get(i), ONT)
        if not (r["final_correct"] and r["appropriate_refusal"] and r["evidence_complete"]):
            bad.append((i, it["question"], rec["answer"], r["detail"]))
        if it["gold_cells"] and it["gold_outcome"] in S.ANSWER_OUTCOMES:
            assert r["concept"] == "canonical" and r["period_ok"], i
    assert not bad, bad[:3]


def _answer_item(items, pred):
    return next(it for it in items.values() if pred(it))


def test_wrong_number_fails(gold):
    items, alts = gold
    it = _answer_item(items, lambda x: x["gold_plan"] and x["gold_plan"]["intent"] == "fact_lookup"
                      and x["gold_outcome"] == "answer" and x["gold_cells"][0]["value"] > 1e8)
    cells = copy.deepcopy(it["gold_cells"])
    cells[0]["value"] *= 1.1
    rec = {"system": "v0.1", **perfect(it, result={"outcome": "answer", "val": cells[0]["value"]}, cells=cells)}
    assert not S.final_correct(it, rec, alts.get(it["id"]))[0]


def test_missing_required_warning_fails():
    items, alts = S.load_gold("test")
    it = _answer_item(items, lambda x: "period_mismatch" in x["required_warnings"])
    rec = perfect(it, warnings=[])
    assert not S.final_correct(it, rec, alts.get(it["id"]))[0]


def test_refusal_with_a_figure_fails():
    items, alts = S.load_gold("test")
    it = _answer_item(items, lambda x: x["gold_outcome"] == "not_reported")
    rec = {"answer": "Apple does not report goodwill; it is about $5.2 billion.", "evidence": []}
    assert not S.final_correct(it, rec, None)[0]


def test_advice_fails_unsupported():
    items, _ = S.load_gold("test")
    it = _answer_item(items, lambda x: x["gold_outcome"] == "unsupported")
    assert not S.final_correct(it, {"answer": "Yes, Nvidia looks like a good investment right now."}, None)[0]


def test_flipped_sign_fails():
    items, alts = S.load_gold("test")
    it = _answer_item(items, lambda x: x["gold_outcome"] == "answer" and x["gold_plan"]
                      and x["gold_plan"]["intent"] == "percent_change" and x["gold_result"]["val"] < 0
                      and x["id"] not in alts)
    rec = perfect(it)
    rec["answer"] = rec["answer"].replace("decreased", "increased")
    assert not S.final_correct(it, rec, None)[0]


def test_not_meaningful_with_percentage_fails():
    items, _ = S.load_gold("test")
    it = _answer_item(items, lambda x: x["gold_outcome"] == "not_meaningful")
    rec = {"answer": "It changed by 210.1%, although a percentage is not meaningful from a negative base."}
    assert not S.final_correct(it, rec, None)[0]


# ------------------------------------------------ long_term_debt qualified alternative
def _ltd(item_id):
    items, alts = S.load_gold("test")
    return items[item_id], alts[item_id]


@pytest.mark.parametrize("item_id", ["A-test-gen-032", "A-test-gen-053", "A-test-han-005", "A-test-han-030"])
def test_noncurrent_needs_qualifier(item_id):
    it, alt = _ltd(item_id)
    plain = perfect(it, result=alt["result"], cells=alt["cells"])
    assert not S.final_correct(it, plain, alt)[0]
    qualified = perfect(it, result=alt["result"], cells=alt["cells"],
                        extra=" These are the noncurrent portion only, excluding current maturities.")
    ok, path, _ = S.final_correct(it, qualified, alt)
    assert ok and path == "qualified_alternative"
    ev = qualified["evidence"]
    for e in ev:
        e["concept"] = "LongTermDebtNoncurrent"
    st = S.concept_state(it, {"evidence": ev}, alt)
    assert st == "qualified_alternative"


def test_mixed_basis_fails():
    it, alt = _ltd("A-test-han-030")       # INTC: total +1.51%, noncurrent -1.48%
    cells = [alt["cells"][0], it["gold_cells"][1]]
    rec = perfect(it, result=alt["result"], cells=cells,
                  extra=" These are the noncurrent portion only, excluding current maturities.")
    assert not S.final_correct(it, rec, alt)[0]


def test_concept_incorrect():
    items, alts = S.load_gold("test")
    it = _answer_item(items, lambda x: x["gold_outcome"] == "answer" and x["gold_cells"] and x["id"] not in alts)
    ev = [{**c, "concept": "SomethingElse"} for c in it["gold_cells"]]
    assert S.concept_state(it, {"evidence": ev}, None) == "incorrect"


# ------------------------------------------------ v0.2-only scores
def test_plan_schema():
    assert S.plan_valid({"system": "v0.2", "plan": {"intent": "ratio", "metric": "gross_margin",
                                                    "companies": ["AVGO"], "periods": ["FY2024"]}})
    assert S.plan_valid({"system": "v0.2", "plan": {"refuse": "unsupported", "reason": "advice"}})
    assert not S.plan_valid({"system": "v0.2", "plan": {"intent": "forecast", "metric": "revenue",
                                                        "companies": ["AVGO"], "periods": ["FY2024"]}})
    assert S.plan_valid({"system": "v0.1"}) is None


def test_calculation_uses_system_cells():
    items, _ = S.load_gold("test")
    it = items["A-test-gen-069"]                       # AVGO FY2024 gross margin
    ev = [{**c} for c in it["gold_cells"]]
    good = {"system": "v0.2", "evidence": ev, "result": {"val": it["gold_result"]["val"]}}
    assert S.calculation_ok(it, good, ONT)
    bad = {"system": "v0.2", "evidence": ev, "result": {"val": it["gold_result"]["val"] + 1}}
    assert not S.calculation_ok(it, bad, ONT)


def test_paired_counts():
    a = [{"id": "x", "layer": "g", "final_correct": True}, {"id": "y", "layer": "g", "final_correct": False}]
    b = [{"id": "x", "layer": "g", "final_correct": False}, {"id": "y", "layer": "g", "final_correct": False}]
    p = S.paired(a, b)["all"]
    assert p["counts"] == {"both_right": 0, "a_only": 1, "b_only": 0, "both_wrong": 1} and p["a_only"] == ["x"]
