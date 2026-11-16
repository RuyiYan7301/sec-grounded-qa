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


@pytest.mark.parametrize("text", ["fell 0.22 pp", "fell 0.22 ppt", "fell 0.22 ppts", "fell 0.22 pts", "fell 0.22 points",
                                  "fell 0.22 percentage points", "fell 0.22 percentage-points"])
def test_percentage_point_wordings(text):
    _, pcts = S._amounts(text)
    assert 0.22 in pcts, (text, pcts)


def test_no_control_characters_in_scorer():
    src = (config.REPO_ROOT / "src" / "secqa" / "evaluation" / "v2" / "score.py").read_bytes()
    assert not any(b < 32 and b not in (9, 10, 13) for b in src)


# ------------------------------------------------ regressions found by the calibration run (2026-11-15)
def test_curly_apostrophe_refusal():
    items, _ = S.load_gold("dev")
    it = items["A-dev-adv-005"]
    ans = "I can\u2019t determine whether Oracle is overvalued from 10-K data; that is an investment judgment."
    assert S.final_correct(it, {"answer": ans}, None)[0]


def test_difference_is_not_a_period_mismatch_warning():
    assert not S.WARNING["period_mismatch"].search("Oracle had more assets, a $32.5 billion difference.")
    assert S.WARNING["period_mismatch"].search("Their fiscal years differ, so the periods do not align.")


def test_grouped_decimal_percentage():
    _, pcts = S._amounts("changed by 2,270.6% from FY2023")
    assert 2270.6 in pcts and 6.0 not in pcts


def test_alternative_concept_state_with_metric_in_evidence():
    items, alts = S.load_gold("dev")
    it, alt = items["A-dev-gen-010"], alts["A-dev-gen-010"]
    ev = [{**c, "metric": "long_term_debt"} for c in alt["cells"]]
    assert S.concept_state(it, {"evidence": ev}, alt) == "qualified_alternative"


# ------------------------------------------------ malformed records (calibration round 2 crashed on these)
MALFORMED = [
    lambda r: {**r, "evidence": r["evidence"][0] if r["evidence"] else {}},   # single object, not a list
    lambda r: {**r, "evidence": None},
    lambda r: {**r, "evidence": "see filing"},
    lambda r: {**r, "evidence": ["see filing"] + r["evidence"]},
    lambda r: {**r, "system": "v0.2", "plan": "fact_lookup revenue", "result": [1, 2]},
    lambda r: {**r, "answer": None},
]


@pytest.mark.parametrize("bend", range(len(MALFORMED)))
def test_malformed_records_never_crash(bend):
    items, alts = S.load_gold("dev")
    for i, it in items.items():
        rec = {"id": i, "system": "v0.1", **perfect(it)}
        r = S.score_item(it, MALFORMED[bend](rec), alts.get(i), ONT)
        assert r["record_format_ok"] is False, (i, bend)


def test_single_object_evidence_is_still_read():
    items, alts = S.load_gold("dev")
    it = items["A-dev-gen-008"]
    rec = perfect(it)
    rec["evidence"] = rec["evidence"][0]
    r = S.score_item(it, rec, None, ONT)
    assert r["final_correct"] and r["evidence_complete"] and r["concept"] == "canonical" and not r["record_format_ok"]


def test_unreadable_evidence_fails_completeness():
    items, _ = S.load_gold("dev")
    it = items["A-dev-gen-008"]
    rec = perfect(it)
    rec["evidence"] = ["see filing"]
    assert not S.score_item(it, rec, None, ONT)["evidence_complete"]


# ------------------------------------------------ regressions from calibration round 2 (development data)
@pytest.mark.parametrize("text", ["The fiscal periods are not aligned.",
                                  "Their FY2024 periods end on different dates (May 31 and July 27)."])
def test_more_period_mismatch_wordings(text):
    assert S.WARNING["period_mismatch"].search(text)


def test_out_of_range_unavailable_wording():
    items, _ = S.load_gold("dev")
    it = items["A-dev-adv-006"]
    ans = "Cisco FY2020 is outside the covered filing range, so the revenue figure is unavailable."
    assert S.final_correct(it, {"answer": ans}, None)[0]


def test_basic_eps_for_a_diluted_question_fails():
    items, _ = S.load_gold("dev")
    it = items["A-dev-gen-004"]                           # Oracle diluted EPS FY2024, gold 3.71
    assert not S.final_correct(it, {"answer": "Oracle's basic EPS was $3.70 in FY2024."}, None)[0]
    assert S.final_correct(it, {"answer": "Oracle's diluted EPS was $3.71 in FY2024 (basic: $3.82)."}, None)[0]


def test_scores_are_separated():
    """Wrong metric: concept fails, period does not. Wrong period: period fails, concept does not."""
    items, _ = S.load_gold("dev")
    it = items["A-dev-gen-008"]
    cell = dict(it["gold_cells"][0])
    wrong_metric = {"evidence": [{**cell, "metric": "revenue", "concept": "Revenues"}]}
    assert S.concept_state(it, wrong_metric, None) == "incorrect" and S.period_ok(it, wrong_metric)
    wrong_period = {"evidence": [{**cell, "period": "FY2024", "period_end": "2024-05-31"}]}
    assert S.concept_state(it, wrong_period, None) == "canonical" and not S.period_ok(it, wrong_period)


def test_calculation_uses_the_systems_own_plan_and_cells():
    items, _ = S.load_gold("dev")
    it = items["A-dev-gen-028"]                           # Cisco gross margin FY2023 (ratio)
    cells = [dict(c) for c in it["gold_cells"]]
    gp = next(c for c in cells if c["metric"] == "gross_profit")["value"]
    rev = next(c for c in cells if c["metric"] == "revenue")["value"]
    plan = {"intent": "ratio", "metric": "gross_margin", "companies": ["CSCO"], "periods": ["FY2023"]}
    rec = {"system": "v0.2", "plan": plan, "evidence": cells, "result": {"val": gp / rev * 100}}
    assert S.calculation_ok(it, rec, ONT)
    shifted = [{**c, "period": "FY2022", "period_end": "2022-07-30"} for c in cells]   # wrong period, same arithmetic
    assert S.calculation_ok(it, {**rec, "evidence": shifted}, ONT)


def test_mixed_concepts_across_years_are_incorrect():
    items, alts = S.load_gold("dev")
    it, alt = items["A-dev-gen-010"], alts["A-dev-gen-010"]
    ev = [dict(it["gold_cells"][0]), {**alt["cells"][1], "metric": "long_term_debt"}, dict(it["gold_cells"][2])]
    assert S.concept_state(it, {"evidence": ev}, alt) == "incorrect"


def test_wrong_intent_does_not_fail_calculation():
    items, _ = S.load_gold("dev")
    it = items["A-dev-gen-020"]                           # percent change
    plan = {**it["gold_plan"], "intent": "absolute_change"}
    rec = {"system": "v0.2", "plan": plan, "evidence": [dict(c) for c in it["gold_cells"]],
           "result": {"val": it["gold_result"]["val"]}}
    assert S.calculation_ok(it, rec, ONT) and not S.intent_ok(it, rec)


# ------------------------------------------------ percentage points must be written as points (rule after round 2, F09)
def _pp_item():
    items, _ = S.load_gold("dev")
    return items["A-dev-gen-025"]


@pytest.mark.parametrize("unit_text", ["{v:.2f} percentage points", "{v:.2f} pp", "{v:.2f} ppts", "{v:.2f} points",
                                       "{b:.0f} basis points", "{b:.0f} bps"])
def test_pp_written_in_points_or_bps_passes(unit_text):
    it = _pp_item()
    v = it["gold_result"]["val"]
    word = "rose" if v > 0 else "fell"
    ans = f"Cisco's gross margin {word} by " + unit_text.format(v=abs(v), b=abs(v) * 100) + "."
    assert S.final_correct(it, {"answer": ans}, None)[0], ans


def test_pp_written_as_percent_fails():
    it = _pp_item()
    v = it["gold_result"]["val"]
    word = "rose" if v > 0 else "fell"
    assert not S.final_correct(it, {"answer": f"Cisco's gross margin {word} by {abs(v):.2f}%."}, None)[0]
