"""The metric ontology is consistent data, and coverage is computed from the fact store."""
import copy

from secqa import ontology, tools


def test_ontology_is_consistent():
    o = ontology.load()
    assert ontology.validate(o) == []
    assert len(o["metrics"]) >= 20


def test_validate_catches_a_confounder_that_is_also_a_candidate():
    o = copy.deepcopy(ontology.load())
    o["metrics"]["revenue"]["confounders"].append({"tag": "Revenues", "reason": "x"})
    o["derived_metrics"]["gross_margin"]["formula"] = "gross_profit / sales"
    bad = ontology.validate(o)
    assert any("both a candidate and a confounder" in b for b in bad)
    assert any("unknown metric sales" in b for b in bad)


def test_duplicate_alias_is_rejected():
    o = copy.deepcopy(ontology.load())
    o["metrics"]["cost_of_revenue"]["aliases"].append("Revenue")
    assert any("alias 'Revenue'" in b for b in ontology.validate(o))


def test_coverage_uses_priority_order_and_never_a_confounder():
    cov = ontology.coverage(tools.store())
    assert cov["revenue"]["NVDA"][2024] == ("Revenues", "primary")   # NVDA has no ASC 606 total
    for by_t in cov.values():
        for row in by_t.values():
            assert all(v is None or v[1] in ontology.USES for v in row.values())


def test_hash_ignores_line_endings(tmp_path):
    a, b = tmp_path / "a.yaml", tmp_path / "b.yaml"
    a.write_bytes(b"x: 1\ny: 2\n")
    b.write_bytes(b"x: 1\r\ny: 2\r\n")
    assert ontology.file_hash(a) == ontology.file_hash(b)
