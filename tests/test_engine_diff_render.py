"""Engine diff size labels, Item 1A candidate alignment and renderer input, on hand-made fixtures."""
import json

from secqa.engine import diff, item1a_changes, render


def test_size_status_thresholds():
    assert diff.size_status("amount", 100, 112) == "large_numeric_change"
    assert diff.size_status("amount", 100, 105) == "gray_zone"
    assert diff.size_status("amount", 100, 101) == "unchanged_control"
    assert diff.size_status("amount", -100, -50) == "large_numeric_change"          # magnitude only
    assert diff.size_status("amount", -10, 5) == "large_numeric_change"             # sign change
    assert diff.size_status("ratio", 60.0, 62.5) == "large_numeric_change"          # points
    assert diff.size_status("ratio", 60.0, 61.0) == "gray_zone"
    assert diff.size_status("ratio", 60.0, 60.2) == "unchanged_control"


def test_item1a_candidates_engine_alignment():
    a = ["Unchanged risk paragraph one about suppliers and demand.",
         "We depend on a small number of customers for a large share of revenue in every region.",
         "A paragraph that was removed entirely from the later report about hedging programs."]
    b = ["Unchanged risk paragraph one about suppliers and demand.",
         "We depend on a small number of customers for a large share of revenue in every region and market.",
         "A brand new paragraph about export controls on advanced computing products."]
    c = item1a_changes.candidates(a, b)
    assert (1, 1) in c                                   # paired: same risk, edited
    assert (2, None) in c and (None, 2) in c             # removed and added
    assert all(p != (0, 0) for p in c)                   # unchanged paragraph is not a candidate


def test_item1a_norm_ignores_years_and_punctuation():
    assert item1a_changes._norm("In fiscal 2023, revenue grew.") == item1a_changes._norm("In fiscal 2024 revenue grew")


def test_renderer_input_holds_only_agreed_fields():
    result = {"outcome": "answer", "result": {"value": 1.0}, "warnings": [{"code": "scope", "detail": "x"}],
              "evidence": [{"id": "ev_1", "ticker": "CSCO", "metric": "revenue", "fy": "FY2024", "concept": "C",
                            "value": 1.0, "unit": "USD", "period_end": "2024-07-27", "accession": "a",
                            "other_values": [], "first_accession": "z"}],
              "cells": ["internal"], "intent": "fact_lookup"}
    data = render.render_input("q", {"intent": "fact_lookup"}, result)
    assert set(data) <= {"question", "plan", "execution", "display", "evidence"}
    assert set(data["execution"]) <= {"outcome", "reason", "result", "alignment", "warnings"}
    blob = json.dumps(data).lower() + render.SYSTEM.lower()
    for word in ("gold", "scorer", "regex", "final_correct", "tolerance"):
        assert word not in blob, word


def test_display_formats_amounts_by_code():
    f = render.fmt
    assert f(10123000000, "USD") == "$10,123 million"
    assert f(-1234500000, "USD") == "-$1,234.5 million"
    assert f(2866000000, "shares") == "2,866 million shares"
    assert f(3.82, "USD/shares") == "$3.82 per share"
    assert f(43.21, "percent") == "43.2%"
    assert f(-12.345, "USD", "percent_change") == "-12.3%"
    assert f(1.26, "percent", "pp_change") == "1.3 percentage points"
    assert f(None, "USD") is None


def test_display_covers_multi_value_results():
    """Multi-value results carry their unit, so every value is formatted (dev run: 10,123 million was
    written as 101.23 billion when only raw integers were shown)."""
    r = {"outcome": "answer", "result": {"values": {"FY2023": 10123000000, "FY2024": 7508000000}, "unit": "USD"},
         "evidence": []}
    d = render.render_input("q", {}, r)["display"]
    assert d == {"values": {"FY2023": "$10,123 million", "FY2024": "$7,508 million"}}
    r = {"outcome": "answer", "result": {"values": {"ORCL": 3974000000, "CSCO": 3074000000},
                                         "difference": 900000000, "unit": "USD"}, "evidence": []}
    assert render.render_input("q", {}, r)["display"]["difference"] == "$900 million"


def test_no_display_for_refusals():
    r = {"outcome": "out_of_range", "reason": "x", "evidence": []}
    assert "display" not in render.render_input("q", {}, r)


def test_where_else_finds_merged_text():
    """A removed paragraph whose sentences were merged into another paragraph scores 1.0 there."""
    from secqa.engine import item1a_changes as ic
    removed = "Our results may fluctuate. This could harm our stock price."
    later = ["Unrelated text about export controls and tariffs.",
             "Demand is uncertain. Our results may fluctuate. This could harm our stock price."]
    top = ic.where_else(removed, later)
    assert top[0]["index"] == 1 and top[0]["score"] == 1.0
    assert top[1]["score"] < 0.5
    assert [x["index"] for x in ic.where_else(removed, later, exclude=1)] == [0]
