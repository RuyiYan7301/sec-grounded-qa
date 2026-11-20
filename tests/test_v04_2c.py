"""v0.4 2c fixes (docs/v0.4-2c-plan.md): fiscal-year label offsets and submissions pagination."""
from datetime import date

from secqa import edgar, facts
from secqa.evaluation.v4 import fy_offsets


def _labels(rows):
    return {"X": {"tenks": [{"report_date": d, "engine_fy": e, "own_fy": o} for d, e, o in rows]}}


def test_offset_needs_a_consistent_majority():
    many = [(f"{2018 + i}-02-01", 2018 + i, 2017 + i) for i in range(6)]
    assert fy_offsets.derive(_labels(many))[0] == {"X": -1}
    one_off = [(f"{2018 + i}-01-31", 2018 + i, 2018 + i) for i in range(8)] + [("2026-01-31", 2026, 2025)]
    assert fy_offsets.derive(_labels(one_off))[0] == {}          # CRM-like: 1 of 9
    too_few = many[:4]
    assert fy_offsets.derive(_labels(too_few))[0] == {}
    old_only = [(f"{2008 + i}-02-01", 2008 + i, 2007 + i) for i in range(6)]
    assert fy_offsets.derive(_labels(old_only))[0] == {}         # before 2018 does not count


def test_committed_offsets_are_the_three_filers():
    assert facts.label_offsets() == {"HD": -1, "JNJ": -1, "LOW": -1}


def test_fiscal_year_applies_offset_only_with_ticker():
    hd_end = date(2025, 2, 2)                                    # Home Depot's fiscal 2024
    assert facts.fiscal_year(hd_end, "0131") == 2025             # raw engine rule
    assert facts.fiscal_year(hd_end, "0131", "HD") == 2024
    jnj_end = date(2019, 12, 29)                                 # Johnson & Johnson's fiscal 2019
    assert facts.fiscal_year(jnj_end, "0103", "JNJ") == 2019
    assert facts.fiscal_year(date(2025, 1, 26), "0126", "NVDA") == 2025   # original filers unchanged
    assert facts.fiscal_year(date(2024, 9, 28), "0928", "AAPL") == 2024


def test_filing_index_reads_extra_pages(monkeypatch, tmp_path):
    main = {"filings": {"recent": {"form": ["10-K"], "reportDate": ["2025-12-31"], "accessionNumber": ["a"]},
                        "files": [{"name": "p1.json"}]}}
    page = {"form": ["10-K", "8-K"], "reportDate": ["2019-12-31", ""], "accessionNumber": ["b", "c"]}
    monkeypatch.setattr(edgar, "submissions", lambda t, refresh=False: main)
    monkeypatch.setattr(edgar, "_cached", lambda name, url, refresh=False: page)
    idx = edgar.filing_index("X")
    assert idx["accessionNumber"] == ["a", "b", "c"]
    assert idx["form"] == ["10-K", "10-K", "8-K"]


def test_filing_index_without_extra_pages_is_recent():
    sub = edgar.submissions("AAPL")
    assert edgar.filing_index("AAPL") == {k: v for k, v in sub["filings"]["recent"].items()}


def test_v04_gold_rule_gets_offsets_without_touching_frozen_gold():
    from secqa.evaluation.v2 import gold
    from secqa.evaluation.v4 import gen_qa_v4
    rule = gen_qa_v4._with_offsets(lambda ticker, end: 2025)
    assert rule("HD", "2025-02-02") == 2024 and rule("NVDA", "2025-01-26") == 2025
    assert gold.fiscal_year_of.__module__ == "secqa.evaluation.v2.gold"


# ---- fixes 3-5: scope warnings and the derived long-term debt sum (engine/scope_checks.py)

class _Src:
    policy = "latest_in_snapshot"

    def __init__(self, vals, end="2024-12-31"):
        self.vals, self.end = vals, end

    def cell(self, ticker, mid, metric, fy, tag):
        if tag not in self.vals:
            return None
        return {"ticker": ticker, "metric": mid, "fy": f"FY{fy}", "concept": tag, "value": self.vals[tag],
                "unit": "USD", "period_start": None, "period_end": self.end, "accession": "x", "form": "10-K",
                "filed": "2025-02-01", "other_values": []}


def _codes(vals, mid):
    from secqa import ontology
    from secqa.engine import execute
    v = execute.resolve_value(_Src(vals), ontology.load(), "X", mid, 2024)
    return v, [w["code"] for w in v["warnings"]]


def test_opex_equal_to_total_costs_is_flagged():
    gm = {"Revenues": 156_735, "OperatingIncomeLoss": 10_315, "OperatingExpenses": 146_421}
    assert _codes(gm, "operating_expenses")[1] == ["opex_is_total_costs"]
    msft = {"Revenues": 245_122, "OperatingIncomeLoss": 109_433, "OperatingExpenses": 61_575}
    assert _codes(msft, "operating_expenses")[1] == []


def test_products_only_cost_of_revenue_is_flagged():
    unh = {"Revenues": 371_622, "OperatingIncomeLoss": 32_358, "CostOfGoodsAndServicesSold": 38_770,
           "PolicyholderBenefitsAndClaimsIncurredNet": 241_894}
    v, codes = _codes(unh, "cost_of_revenue")
    assert codes == ["cost_of_revenue_partial"] and v["value"] == 38_770      # value unchanged
    no_larger = {k: x for k, x in unh.items() if k != "PolicyholderBenefitsAndClaimsIncurredNet"}
    assert _codes(no_larger, "cost_of_revenue")[1] == []
    retailer = {"Revenues": 100, "OperatingIncomeLoss": 5, "CostOfGoodsAndServicesSold": 70, "CostOfServices": 80}
    assert _codes(retailer, "cost_of_revenue")[1] == []                       # not below 50% of total costs


def test_long_term_debt_from_its_parts():
    v, codes = _codes({"LongTermDebtNoncurrent": 85_750, "LongTermDebtCurrent": 10_912}, "long_term_debt")
    assert v["status"] == "derived_sum" and v["value"] == 96_662 and codes == ["derived_sum"]
    assert [c["concept"] for c in v["cells"]] == ["LongTermDebtNoncurrent", "LongTermDebtCurrent"]
    assert _codes({"LongTermDebtNoncurrent": 1_721}, "long_term_debt")[0]["status"] == "not_reported"
    total = {"LongTermDebt": 96_700, "LongTermDebtNoncurrent": 85_750, "LongTermDebtCurrent": 10_912}
    assert _codes(total, "long_term_debt")[0]["value"] == 96_700              # a tagged total wins
