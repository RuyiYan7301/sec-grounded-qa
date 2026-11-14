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
        "What was the total revenue?", "Nvidia (NVDA)", "FY2024", "verify", "qwen3:8b")
    assert ">VERIFIED<" in status and "$60.922 billion" in answer
    assert "NVDA" in facts[0][0] and "Revenues" in facts[0][0] and "index.htm" in facts[0][2] and "First reported" in facts[0][3]
    assert [row[1] for row in trace] == ["list_concepts", "get_fact"]
    assert raw["question"].endswith("(Selected company: Nvidia (NVDA); fiscal year: FY2024.)")


def test_run_shows_input_errors_without_calling_the_model(fake_chat):
    fc = fake_chat([])
    status, *_ = app.run("", "Any", "Any", "verify", "qwen3:8b")
    assert "Input error" in status and fc.calls == []
