"""The web demo's handler: same structured answer, rendered into the tabs."""
import pytest
from conftest import call, say

pytest.importorskip("gradio")
from secqa import app  # noqa: E402


def test_app_builds():
    assert app.build() is not None


def test_run_fills_every_panel(fake_chat):
    fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's total revenue in fiscal 2024 was $60.922 billion.")],
              judge=lambda p: {"facts": [{"n": 1, "matches": True}]})
    status, answer, warnings, facts, trace, sources, checks, draft, raw = app.run(
        "What was the total revenue?", "Nvidia (NVDA)", "FY2024", "agent", "verify", "qwen3:8b")
    assert ">VERIFIED<" in status and "$60.922 billion" in answer
    assert "NVDA" in facts[0][0] and "Revenues" in facts[0][0] and "index.htm" in facts[0][2] and "First reported" in facts[0][3]
    assert [row[1] for row in trace] == ["list_concepts", "get_fact"]
    assert raw["question"].endswith("(Selected company: Nvidia (NVDA); fiscal year: FY2024.)")


def test_run_shows_input_errors_without_calling_the_model(fake_chat):
    fc = fake_chat([])
    status, *_ = app.run("", "Any", "Any", "auto", "verify", "qwen3:8b")
    assert "Input error" in status and fc.calls == []


def test_compare_helpers_format_values_and_changes():
    o = {"metrics": {"revenue": {"display_name": "Revenue"}},
         "derived_metrics": {"gross_margin": {"display_name": "Gross margin", "formula": "gross_profit / revenue"}}}
    rev = {"metric": "revenue", "facts": [{"fy": "FY2024", "value": 60922000000, "unit": "USD", "component_of": None}]}
    assert app._metric_value(rev, "FY2024", o) == (60922000000, "USD")
    gm = {"metric": "gross_margin", "facts": [
        {"fy": "FY2025", "metric": "gross_profit", "value": 75.0, "unit": "USD", "component_of": "gross_margin"},
        {"fy": "FY2025", "metric": "revenue", "value": 100.0, "unit": "USD", "component_of": "gross_margin"}]}
    assert app._metric_value(gm, "FY2025", o) == (75.0, "percent")
    assert app._fmt(75.0, "percent") == "75.0%" and app._fmt(24690000000, "shares") == "24.690 billion shares"
    assert app._change({"absolute_change": 69575000000, "percent_change": 114.2}, "USD") == "+$69.575 billion (+114.2%)"
    assert app._change({"pp_change": -4.31}, "percent") == "-4.3 pp"


def test_compare_needs_a_company():
    assert "Choose a company" in app.compare("Any", "FY2025", False)[0]
