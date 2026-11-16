"""Fiscal-period engine: range, bare-year ambiguity and cross-company alignment, as structured output.

Fiscal years are named by each filer's own calendar (the year its fiscal year ends in). Outputs are data,
not sentences: alignment, period ends, gap in days and warning codes. The 31-day tolerance for aligned
year ends follows the benchmark specification of period_mismatch, which is part of the system spec.
"""
import re
from datetime import date

from .. import edgar

COVERED = (2023, 2024, 2025)
ALIGNED_DAYS = 31


def fye(ticker):
    return edgar.submissions(ticker).get("fiscalYearEnd") or "1231"


def out_of_range(periods):
    return [p for p in periods if int(p[2:]) not in COVERED]


BARE_YEAR = re.compile(r"\b(?:in|for|during|of)\s+(20\d\d)\b", re.I)
FISCAL_WORD = re.compile(r"\b(?:fiscal|FY|calendar|CY)\s*'?(?:year\s+)?20?\d\d\b", re.I)


def bare_year_reading(question, tickers):
    """If the question names a year without saying fiscal or calendar, and some company's fiscal year does
    not end in December, the reading is ambiguous: report the reading the plan used."""
    if FISCAL_WORD.search(question or ""):
        return None
    years = BARE_YEAR.findall(question or "")
    if not years:
        return None
    off = [t for t in tickers if fye(t)[:2] != "12"]
    if not off:
        return None
    return {"code": "ambiguous_year", "years": sorted(set(years)),
            "companies_with_non_december_year_end": off,
            "detail": "the question gives a bare year; it was read as the fiscal year with that number"}


def alignment(cells):
    """cells: resolved cells of one fiscal year for several companies -> structured alignment."""
    ends = {c["ticker"]: c["period_end"] for c in cells if c and c.get("period_end")}
    if len(ends) < 2:
        return {"alignment": "single", "period_ends": ends, "gap_days": 0, "warnings": []}
    ds = sorted(date.fromisoformat(e) for e in ends.values())
    gap = (ds[-1] - ds[0]).days
    aligned = gap <= ALIGNED_DAYS
    w = [] if aligned else [{"code": "period_mismatch", "period_ends": ends, "gap_days": gap,
                             "detail": "the fiscal years compared end on different dates"}]
    return {"alignment": "aligned" if aligned else "mismatched", "period_ends": ends, "gap_days": gap, "warnings": w}
