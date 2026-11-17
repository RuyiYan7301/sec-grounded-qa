"""The web app's API: same structured answer as the CLI, figures in the answer linked to facts, input checks."""
import pytest
from conftest import call, say

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from secqa import web  # noqa: E402


@pytest.fixture
def client():
    return TestClient(web.create_app())


def test_segments_link_only_figures_that_match_a_fact():
    facts = [{"value": 123216e6}, {"value": 32972e6}]
    segs = web.segments("Apple $123,216 million; Nvidia $32.972 billion; gap $90,244 million.", facts)
    assert [s.get("fact") for s in segs if "fact" in s] == [0, 1]
    assert "".join(s["text"] for s in segs) == "Apple $123,216 million; Nvidia $32.972 billion; gap $90,244 million."


def test_meta_lists_companies_years_and_examples(client):
    m = client.get("/api/meta").json()
    assert len(m["companies"]) == 8 and m["target_years"] == m["years"][1:] and m["examples"]


def test_ask_returns_the_structured_answer_with_segments(client, fake_chat):
    fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's total revenue in fiscal 2024 was $60.922 billion.")],
              judge=lambda p: {"facts": [{"n": 1, "matches": True}]})
    r = client.post("/api/ask", json={"question": "What was Nvidia's total revenue in fiscal 2024?", "engine": "agent"})
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "verified" and d["facts"][0]["concept"] == "Revenues"
    assert any(s.get("fact") == 0 and "60.922" in s["text"] for s in d["segments"])


def test_ask_rejects_an_empty_question_without_calling_the_model(client, fake_chat):
    fc = fake_chat([])
    r = client.post("/api/ask", json={"question": "  "})
    assert r.status_code == 400 and fc.calls == []


def test_compare_checks_its_input(client):
    assert client.post("/api/compare", json={"ticker": "XYZ", "to_fy": "FY2025"}).status_code == 400
    assert client.post("/api/compare", json={"ticker": "NVDA", "to_fy": "2025"}).status_code == 400


def test_peers_checks_its_input(client):
    assert client.post("/api/peers", json={"metric": "revenue", "fy": "2024"}).status_code == 400
    assert client.post("/api/peers", json={"metric": "not_a_metric", "fy": "FY2024"}).status_code == 400


def test_meta_lists_metrics_and_which_compare_across_companies(client):
    ms = {m["id"]: m for m in client.get("/api/meta").json()["metrics"]}
    assert len(ms) == 28 and ms["revenue"]["comparable"] and not ms["eps_diluted"]["comparable"]
