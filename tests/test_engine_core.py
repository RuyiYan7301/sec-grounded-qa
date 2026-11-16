"""Engine resolver, period engine, calculation and executor on hand-made fixtures (no dev or test data)."""
import pytest

from secqa.engine import compute, execute, periods, resolve

ONT = {
    "metrics": {
        "revenue": {"display_name": "Revenue", "period_type": "duration", "allowed_operations":
                    ["lookup", "multi_period_lookup", "cross_company_comparison", "absolute_change", "percent_change", "ratio"],
                    "candidate_concepts": [{"tag": "A", "priority": 1, "use": "primary"},
                                           {"tag": "B", "priority": 2, "use": "primary"},
                                           {"tag": "F", "priority": 3, "use": "fallback_with_warning"}]},
        "gross_profit": {"display_name": "Gross profit", "period_type": "duration",
                         "allowed_operations": ["lookup", "absolute_change", "percent_change", "ratio"],
                         "candidate_concepts": [{"tag": "GP", "priority": 1, "use": "primary"}]},
        "eps_diluted": {"display_name": "Diluted EPS", "period_type": "duration", "split_sensitive": True,
                        "allowed_operations": ["lookup", "absolute_change", "percent_change"],
                        "interpreted_aliases": [{"alias": "EPS", "warning": "EPS read as diluted EPS"}],
                        "candidate_concepts": [{"tag": "EPSD", "priority": 1, "use": "primary"}]},
    },
    "derived_metrics": {"gross_margin": {"display_name": "Gross margin", "formula": "gross_profit / revenue", "unit_type": "ratio",
                                         "allowed_operations": ["lookup", "percentage_point_change"]}},
}


class FakeSource:
    policy = "latest_in_snapshot"

    def __init__(self, table):
        self.table = table          # (ticker, tag, fy) -> value

    def cell(self, ticker, mid, metric, fy, tag):
        v = self.table.get((ticker, tag, fy))
        if v is None:
            return None
        end = {"X": f"{fy}-12-31", "Y": f"{fy}-06-30"}[ticker]
        return {"ticker": ticker, "metric": mid, "fy": f"FY{fy}", "concept": tag, "value": v, "unit": "USD",
                "period_start": None, "period_end": end, "accession": f"0000000000-{fy % 100:02d}-000001",
                "form": "10-K", "filed": f"{fy + 1}-02-01", "value_policy": self.policy, "other_values": []}


def res(table, mid="revenue", t="X", fy=2024):
    return resolve.resolve(FakeSource(table), ONT, t, mid, fy)


def test_one_primary_resolved():
    assert res({("X", "A", 2024): 10})["status"] == "resolved"


def test_same_value_primaries_keep_alternates():
    r = res({("X", "A", 2024): 10, ("X", "B", 2024): 10})
    assert r["status"] == "resolved" and r["cell"]["concept"] == "A" and [a["concept"] for a in r["alternates"]] == ["B"]


def test_different_primaries_are_ambiguous():
    r = res({("X", "A", 2024): 10, ("X", "B", 2024): 11})
    assert r["status"] == "ambiguous_concept" and r["cell"] is None


def test_primary_wins_over_fallback():
    r = res({("X", "B", 2024): 10, ("X", "F", 2024): 9})
    assert r["status"] == "resolved" and r["cell"]["concept"] == "B" and [o["concept"] for o in r["others"]] == ["F"]


def test_fallback_only():
    assert res({("X", "F", 2024): 9})["status"] == "fallback_with_warning"


def test_not_reported():
    assert res({})["status"] == "not_reported"


def test_change_rules():
    assert compute.change(100, 120)["percent_change"] == pytest.approx(20)
    z = compute.change(0, 5)
    assert z["percent_change"] is None and z["outcome"] == "not_meaningful" and z["absolute_change"] == 5
    n = compute.change(-200, -50, "net_income")
    assert n["percent_change"] is None and n["change_basis"] == "magnitude_only" and n["direction"] == "loss_narrowed"
    s = compute.change(-10, 30)
    assert s["change_basis"] == "sign_change" and s["percent_change"] is None
    assert compute.ratio(5, 0)["outcome"] == "not_meaningful" and compute.ratio(5, -2)["outcome"] == "not_meaningful"
    assert compute.pp_change({"outcome": "answer", "value": 60.0}, {"outcome": "answer", "value": 62.5})["pp_change"] == pytest.approx(2.5)


def test_evidence_id_is_stable_and_content_based():
    c = {"ticker": "X", "concept": "A", "period_start": None, "period_end": "2024-12-31", "accession": "a", "value": 1, "unit": "USD"}
    assert compute.evidence_id(c) == compute.evidence_id(dict(reversed(list(c.items()))))
    assert compute.evidence_id(c) != compute.evidence_id({**c, "value": 2})


def test_alignment_structured():
    a = periods.alignment([{"ticker": "X", "period_end": "2024-12-31"}, {"ticker": "Y", "period_end": "2024-06-30"}])
    assert a["alignment"] == "mismatched" and a["gap_days"] == 184 and a["warnings"][0]["code"] == "period_mismatch"
    b = periods.alignment([{"ticker": "X", "period_end": "2024-12-28"}, {"ticker": "Y", "period_end": "2024-12-31"}])
    assert b["alignment"] == "aligned" and not b["warnings"]


def test_execute_ratio_and_pp():
    src = FakeSource({("X", "GP", 2023): 60, ("X", "A", 2023): 100, ("X", "GP", 2024): 66, ("X", "A", 2024): 110})
    r = execute.execute({"intent": "ratio", "metric": "gross_margin", "companies": ["X"], "periods": ["FY2024"]}, "q", src, ONT)
    assert r["outcome"] == "answer" and r["result"]["value"] == pytest.approx(60.0) and len(r["evidence"]) == 2
    p = execute.execute({"intent": "percentage_point_change", "metric": "gross_margin", "companies": ["X"],
                         "periods": ["FY2023", "FY2024"]}, "q", src, ONT)
    assert p["result"]["pp_change"] == pytest.approx(0.0)


def test_execute_refusals_and_guards():
    src = FakeSource({})
    assert execute.execute({"refuse": "unsupported", "reason": "advice"}, "q", src, ONT)["outcome"] == "unsupported"
    assert execute.execute({"intent": "fact_lookup", "metric": "ebitda", "companies": ["X"], "periods": ["FY2024"]},
                           "q", src, ONT)["outcome"] == "out_of_ontology"
    assert execute.execute({"intent": "fact_lookup", "metric": "revenue", "companies": ["X"], "periods": ["FY2021"]},
                           "q", src, ONT)["outcome"] == "out_of_range"
    assert execute.execute({"intent": "cross_company_comparison", "metric": "eps_diluted", "companies": ["X", "Y"],
                            "periods": ["FY2024"]}, "q", src, ONT)["outcome"] == "unsupported_operation"
    assert execute.execute({"intent": "fact_lookup", "metric": "revenue", "companies": ["X"], "periods": ["FY2024"]},
                           "q", src, ONT)["outcome"] == "not_reported"


def test_execute_percent_change_negative_base():
    src = FakeSource({("X", "GP", 2023): -5, ("X", "GP", 2024): 10})
    r = execute.execute({"intent": "percent_change", "metric": "gross_profit", "companies": ["X"],
                         "periods": ["FY2023", "FY2024"]}, "q", src, ONT)
    assert r["outcome"] == "not_meaningful" and r["result"]["absolute_change"] == 15 and r["result"]["percent_change"] is None


def test_execute_fallback_and_alias_warnings():
    src = FakeSource({("X", "F", 2024): 9, ("X", "EPSD", 2024): 1.2})
    r = execute.execute({"intent": "fact_lookup", "metric": "revenue", "companies": ["X"], "periods": ["FY2024"]}, "q", src, ONT)
    assert [w["code"] for w in r["warnings"]] == ["scope"]
    e = execute.execute({"intent": "fact_lookup", "metric": "eps_diluted", "companies": ["X"], "periods": ["FY2024"]},
                        "What was X's EPS in fiscal 2024?", src, ONT)
    assert "alias_interpretation" in [w["code"] for w in e["warnings"]]
    e2 = execute.execute({"intent": "fact_lookup", "metric": "eps_diluted", "companies": ["X"], "periods": ["FY2024"]},
                         "What was X's diluted EPS in fiscal 2024?", src, ONT)
    assert "alias_interpretation" not in [w["code"] for w in e2["warnings"]]
