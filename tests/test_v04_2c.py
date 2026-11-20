"""v0.4 2c fixes (docs/v0.4-2c-plan.md): fiscal-year label offsets and submissions pagination."""
from datetime import date

from secqa import edgar, facts
from secqa.evaluation.v4 import fy_offsets


def _labels(rows):
    return {"X": {"tenks": [{"report_date": d, "engine_fy": e, "own_fy": o} for d, e, o in rows]}}


def test_offset_needs_a_consistent_majority():
    many = [(f"{2018 + i}-02-01", 2018 + i, 2017 + i) for i in range(6)]
    assert fy_offsets.derive(_labels(many))[0] == {"X": -1}
    one_off = [(f"{2018 + i}-01-31", 2018 + i, 2018 + i) for i in range(8)] + [("2026-01-31", 2026, 2025)]
    assert fy_offsets.derive(_labels(one_off))[0] == {}          # CRM-like: 1 of 9
    too_few = many[:4]
    assert fy_offsets.derive(_labels(too_few))[0] == {}
    old_only = [(f"{2008 + i}-02-01", 2008 + i, 2007 + i) for i in range(6)]
    assert fy_offsets.derive(_labels(old_only))[0] == {}         # before 2018 does not count


def test_committed_offsets_are_the_three_filers():
    assert facts.label_offsets() == {"HD": -1, "JNJ": -1, "LOW": -1}


def test_fiscal_year_applies_offset_only_with_ticker():
    hd_end = date(2025, 2, 2)                                    # Home Depot's fiscal 2024
    assert facts.fiscal_year(hd_end, "0131") == 2025             # raw engine rule
    assert facts.fiscal_year(hd_end, "0131", "HD") == 2024
    jnj_end = date(2019, 12, 29)                                 # Johnson & Johnson's fiscal 2019
    assert facts.fiscal_year(jnj_end, "0103", "JNJ") == 2019
    assert facts.fiscal_year(date(2025, 1, 26), "0126", "NVDA") == 2025   # original filers unchanged
    assert facts.fiscal_year(date(2024, 9, 28), "0928", "AAPL") == 2024


def test_filing_index_reads_extra_pages(monkeypatch, tmp_path):
    main = {"filings": {"recent": {"form": ["10-K"], "reportDate": ["2025-12-31"], "accessionNumber": ["a"]},
                        "files": [{"name": "p1.json"}]}}
    page = {"form": ["10-K", "8-K"], "reportDate": ["2019-12-31", ""], "accessionNumber": ["b", "c"]}
    monkeypatch.setattr(edgar, "submissions", lambda t, refresh=False: main)
    monkeypatch.setattr(edgar, "_cached", lambda name, url, refresh=False: page)
    idx = edgar.filing_index("X")
    assert idx["accessionNumber"] == ["a", "b", "c"]
    assert idx["form"] == ["10-K", "10-K", "8-K"]


def test_filing_index_without_extra_pages_is_recent():
    sub = edgar.submissions("AAPL")
    assert edgar.filing_index("AAPL") == {k: v for k, v in sub["filings"]["recent"].items()}
