"""The metric ontology is consistent data, and the resolution rules are applied to the fact store."""
import copy
import json

import pytest

from secqa import cli, ontology, tools


@pytest.fixture
def onto():
    return copy.deepcopy(ontology.load())


def test_ontology_is_consistent(onto):
    assert ontology.validate(onto) == []
    assert len(onto["metrics"]) >= 20


def test_frozen_ontology_matches_its_lock(onto):
    lock = json.loads((ontology.PATH.parent / "metric_ontology.lock.json").read_text(encoding="utf-8"))
    if onto["status"] == "frozen":
        assert ontology.file_hash() == lock["sha256"], "frozen ontology was edited; bump the version instead"


def test_validate_catches_inconsistencies(onto):
    onto["metrics"]["revenue"]["confounders"].append({"tag": "Revenues", "reason": "x"})
    onto["derived_metrics"]["gross_margin"]["formula"] = "gross_profit / sales"
    onto["metrics"]["eps_basic"]["allowed_operations"].append("cross_company_comparison")
    onto["metrics"]["cost_of_revenue"]["aliases"].append("Revenue")
    onto["metrics"]["eps_diluted"]["interpreted_aliases"][0]["warning"] = ""
    bad = ontology.validate(onto)
    for text in ("both a candidate and a confounder", "unknown metric sales", "split-sensitive",
                 "alias 'Revenue'", "has no warning"):
        assert any(text in b for b in bad), text


def test_interpreted_alias_cannot_shadow_a_plain_alias(onto):
    onto["metrics"]["eps_basic"]["aliases"].append("EPS")
    assert any("alias 'EPS'" in b for b in ontology.validate(onto))


class FakeStore:
    tickers = ["X"]

    def __init__(self, facts):
        self.facts = {"X": {tag: [{"fiscal_year": 2024, "kind": "FY", "end": "2024-12-31", "val": v, "form": "10-K"}]
                            for tag, v in facts.items()}}


def metric(*cands):
    return {"period_type": "duration",
            "candidate_concepts": [{"tag": t, "use": u, "priority": i} for i, (t, u) in enumerate(cands, 1)]}


M = metric(("A", "primary"), ("B", "primary"), ("F", "fallback_with_warning"))


@pytest.mark.parametrize("facts, status, tag", [
    ({}, None, None),
    ({"B": 5}, "ok", "B"),
    ({"A": 5, "B": 5}, "alternates", "A"),              # same value: highest priority, others recorded
    ({"A": 5, "B": 6}, "ambiguous_concept", None),      # different values: never picked silently
    ({"F": 5}, "fallback", "F"),
    ({"A": 5, "F": 7}, "ok", "A"),                      # primary wins; the fallback is recorded
])
def test_resolution_rules(facts, status, tag):
    cell = ontology.resolve_cell(FakeStore(facts), "X", M, 2024)
    if status is None:
        assert cell is None
        return
    assert (cell["status"], cell["tag"]) == (status, tag)
    assert {o["tag"] for o in cell["others"]} == set(facts) - {tag}


def test_value_seen_only_in_a_10q_does_not_count():
    store = FakeStore({"A": 5})
    store.facts["X"]["A"][0]["form"] = "10-Q"
    assert ontology.resolve_cell(store, "X", M, 2024) is None


def test_coverage_on_fixture_store():
    cov = ontology.coverage(tools.store())
    assert cov["revenue"]["NVDA"][2024]["tag"] == "Revenues"   # NVDA has no ASC 606 total


def test_validate_only_needs_no_data(monkeypatch, capsys):
    monkeypatch.setattr(tools, "store", lambda: pytest.fail("validate-only must not load data"))
    assert cli.main(["ontology", "--validate-only"]) == 0
    assert "structure: ok" in capsys.readouterr().out


def test_hash_ignores_line_endings(tmp_path):
    a, b = tmp_path / "a.yaml", tmp_path / "b.yaml"
    a.write_bytes(b"x: 1\ny: 2\n")
    b.write_bytes(b"x: 1\r\ny: 2\r\n")
    assert ontology.file_hash(a) == ontology.file_hash(b)
