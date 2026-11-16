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
    assert set(data) == {"question", "plan", "execution", "evidence"}
    assert set(data["execution"]) <= {"outcome", "reason", "result", "alignment", "warnings"}
    blob = json.dumps(data).lower() + render.SYSTEM.lower()
    for word in ("gold", "scorer", "regex", "final_correct", "tolerance"):
        assert word not in blob, word
