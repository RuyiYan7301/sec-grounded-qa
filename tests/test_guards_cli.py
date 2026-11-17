import json

import pytest
import requests
from conftest import call, say

from secqa import cli, guards


@pytest.mark.parametrize("company, fy, expect", [
    ("NVDA", "FY2024", ("NVDA", 2024)),
    ("nvidia", "2024", ("NVDA", 2024)),
    (None, None, (None, None)),
    ("Any", "Any", (None, None)),
])
def test_check_input_accepts(company, fy, expect):
    assert guards.check_input("What was revenue?", company, fy) == expect


@pytest.mark.parametrize("question, company, fy, msg", [
    ("", None, None, "empty"),
    ("x" * 3000, None, None, "limit"),
    ("Revenue?", "Tesla", None, "not covered"),
    ("Revenue?", "NVDA", "FY2019", "FY2019 is not covered"),
    ("Revenue?", "NVDA", "next year", "must look like"),
])
def test_check_input_rejects(question, company, fy, msg):
    with pytest.raises(guards.InputError, match=msg):
        guards.check_input(question, company, fy)


def test_compose_adds_selected_context_only_when_missing():
    assert guards.compose("What was revenue?", "NVDA", 2024) == \
        "What was revenue?\n\n(Selected company: Nvidia (NVDA); fiscal year: FY2024.)"
    assert guards.compose("What was Nvidia's revenue in fiscal 2024?", "NVDA", 2024) == \
        "What was Nvidia's revenue in fiscal 2024?"


def test_question_warnings():
    codes = [w["code"] for w in guards.question_warnings("What was revenue in fiscal 2019?")]
    assert codes == ["no_company", "out_of_range"]
    assert guards.question_warnings("What was Apple's revenue in fiscal 2024?") == []


def test_cli_ask_json(fake_chat, capsys):
    fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's total revenue in fiscal 2024 was $60.922 billion.")],
              judge=lambda p: {"facts": [{"n": 1, "matches": True}]})
    assert cli.main(["ask", "--example", "1", "--json", "--engine", "agent"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "verified" and out["facts"][0]["concept"] == "Revenues"
    assert out["tool_calls"][1]["summary"].startswith("NVDA Revenues FY2024 = $60.922 billion")


def test_cli_ask_human_readable_with_trace(fake_chat, capsys):
    fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's total revenue in fiscal 2024 was $60.922 billion.")])
    assert cli.main(["ask", "Nvidia revenue?", "--fy", "FY2024", "--mode", "single", "--trace", "--engine", "agent"]) == 0
    out = capsys.readouterr().out
    assert "Status: VERIFIED" in out and "XBRL facts used" in out and "Tool calls:" in out


def test_cli_input_error_exit_code(capsys):
    assert cli.main(["ask", "Revenue?", "--company", "Tesla"]) == 2
    assert "not covered" in capsys.readouterr().err


def test_cli_reports_ollama_down(monkeypatch, capsys):
    def refuse(*a, **k):
        raise requests.ConnectionError("refused")
    monkeypatch.setattr(cli.requests, "get", refuse)
    monkeypatch.setattr("secqa.agent.requests.post", refuse)
    assert cli.main(["ask", "What was Apple's revenue in fiscal 2024?", "--engine", "agent"]) == 3
    assert "ollama serve" in capsys.readouterr().err
    from secqa.engine import llm as engine_llm

    def down(*a, **k):
        raise engine_llm.OllamaUnavailable("Cannot reach Ollama. Start it with `ollama serve`.")
    monkeypatch.setattr(engine_llm, "chat", down)
    assert cli.main(["ask", "What was Apple's revenue in fiscal 2024?"]) == 3     # auto: the router call fails
    assert "ollama serve" in capsys.readouterr().err
    assert cli.main(["doctor"]) == 3
    out = capsys.readouterr().out
    assert "[FAIL] Ollama" in out and "[ok  ] XBRL facts: 8/8" in out


def test_doctor_ready_with_model(monkeypatch, capsys):
    monkeypatch.setattr(cli, "ollama_models", lambda: ["qwen3:8b"])
    monkeypatch.setattr(cli, "data_status", lambda: {"filers": 8, "of": 8, "filings": 24, "index": True})
    assert cli.doctor("qwen3:8b") is True
    assert not cli.doctor("qwen3:14b")
    assert "ollama pull qwen3:14b" in capsys.readouterr().out


def test_examples_listed(capsys):
    assert cli.main(["examples"]) == 0
    assert capsys.readouterr().out.count("\n") == len(cli.EXAMPLES)
