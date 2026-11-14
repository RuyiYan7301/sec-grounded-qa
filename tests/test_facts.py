from datetime import date

import pytest

from secqa import config, facts


@pytest.mark.parametrize("end, fye, fy", [
    ("2024-01-28", "0128", 2024),   # Nvidia FY2024 ended in January 2024
    ("2024-09-28", "0928", 2024),   # Apple FY2024 ended in September 2024
    ("2024-10-27", "0128", 2025),   # Nvidia Q3 FY2025
    ("2024-11-03", "1101", 2024),   # Broadcom 53-week year runs past its nominal year end
    ("2024-12-28", "1228", 2024),   # Intel
    ("2025-06-30", "0630", 2025),   # Microsoft
])
def test_fiscal_year_from_period_end(end, fye, fy):
    assert facts.fiscal_year(date.fromisoformat(end), fye) == fy


@pytest.mark.parametrize("start, end, kind", [
    (None, "2024-01-28", "instant"),
    ("2023-01-30", "2024-01-28", "FY"),
    ("2024-04-29", "2024-07-28", "Q"),
    ("2024-01-29", "2024-07-28", "H1"),
    ("2023-01-30", "2023-10-29", "9M"),
])
def test_period_kind(start, end, kind):
    assert facts._kind(date.fromisoformat(start) if start else None, date.fromisoformat(end)) == kind


def test_store_dedupes_comparatives():
    s = facts.Store(["NVDA"])
    fy24 = [r for r in s.facts["NVDA"]["Revenues"] if r["kind"] == "FY" and r["fiscal_year"] == 2024]
    assert len(fy24) == 1                 # one record although several 10-Ks repeat it
    assert fy24[0]["n_filings"] >= 2
    assert fy24[0]["val"] == 60_922_000_000
    assert fy24[0]["end"] == "2024-01-28"


def test_store_keeps_restatements():
    s = facts.Store(["AMD"])
    rec = next(r for r in s.facts["AMD"]["SellingGeneralAndAdministrativeExpense"]
               if r["kind"] == "FY" and r["fiscal_year"] == 2024)
    assert rec["val"] == 2_735_000_000    # recast value from the later 10-K
    assert [o["val"] for o in rec["other_values"]] == [2_783_000_000]


def test_snapshot_drops_later_filings(monkeypatch):
    full = facts.Store(["NVDA"])
    monkeypatch.setattr(config, "SNAPSHOT", "2025-01-01")
    early = facts.Store(["NVDA"])
    assert all(r["filed"] <= "2025-01-01" for recs in early.facts["NVDA"].values() for r in recs)
    assert sum(map(len, early.facts["NVDA"].values())) < sum(map(len, full.facts["NVDA"].values()))
