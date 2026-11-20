"""Fact store built from cached XBRL companyfacts.

Three things the pilot showed and this module handles explicitly:
  1. The same fact is repeated in every later filing that shows it as a comparative.
     -> dedupe on (tag, unit, start, end).
  2. `fy`/`fp` describe the filing, not the period the fact covers.
     -> fiscal year is derived from the period end date and the filer's fiscal-year-end month.
  3. Restatements: one period can carry different values in different filings.
     -> keep every distinct value with its accession; answer with the most recently filed one
        and flag that others exist.
Facts filed after config.SNAPSHOT are ignored, so a later download gives the same store.
"""
import json
from collections import defaultdict
from datetime import date, timedelta
from functools import lru_cache

from . import config
from .edgar import FILERS, companyfacts, submissions

FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
INDEXED_FY = (2023, 2024, 2025)  # the three fiscal years in scope, per filer


def _d(s):
    return date.fromisoformat(s) if s else None


@lru_cache(maxsize=None)
def label_offsets():
    """Per-filer fiscal-year label offsets (v0.4 2c fix 1), derived from each 10-K's own DEI fiscal-year
    focus by secqa.evaluation.v4.fy_offsets. Empty when the file is absent."""
    path = config.REPO_ROOT / "data" / "universe" / "fy_label_offsets.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["offsets"]


def fiscal_year(end, fye, ticker=None):
    """Fiscal year label of a period ending on `end`, given the filer's FYE as "MMDD".

    Most filers label their fiscal year by the calendar year in which it ends
    (Nvidia FY2024 ended Jan 28 2024, Apple FY2024 ended Sep 28 2024), so the label is
    the first year Y whose fiscal year end is on or after `end`. 52/53-week years drift
    by up to a week around the nominal date, hence the 7-day tolerance.
    Quarters inherit the fiscal year they fall in: Nvidia's quarter ending Apr 2024 is FY2025.
    A few filers name their year differently (Home Depot's fiscal 2024 ended 2 Feb 2025; Johnson &
    Johnson's fiscal 2019 ended 29 Dec 2019); with `ticker` given, their own convention is applied
    from `label_offsets()`.
    """
    mm, dd = int(fye[:2]), int(fye[2:])
    for y in (end.year - 1, end.year, end.year + 1):
        if end <= date(y, mm, min(dd, 28)) + timedelta(days=7):
            return y + (label_offsets().get(ticker, 0) if ticker else 0)
    raise ValueError(end)


def _kind(start, end):
    if start is None:
        return "instant"
    days = (end - start).days
    if 350 <= days <= 380:
        return "FY"
    if 80 <= days <= 100:
        return "Q"
    if 170 <= days <= 190:
        return "H1"
    if 260 <= days <= 285:
        return "9M"
    return f"{days}d"


class Store:
    def __init__(self, tickers=None):
        self.tickers = list(tickers or FILERS)
        self.meta = {}
        self.facts = {}   # ticker -> tag -> list of deduped period records
        self.labels = {}  # ticker -> tag -> (label, description, taxonomy)
        for t in self.tickers:
            self._load(t)

    def _load(self, t):
        sub = submissions(t)
        fye = sub.get("fiscalYearEnd") or "1231"
        self.meta[t] = {"name": sub["name"], "fiscal_year_end": fye}
        cf = companyfacts(t)
        tags, labels = {}, {}
        for tax, concepts in cf["facts"].items():
            for tag, c in concepts.items():
                labels[tag] = (c.get("label") or "", c.get("description") or "", tax)
                groups = defaultdict(list)
                frames = {}
                for unit, rows in c["units"].items():
                    for r in rows:
                        key = (unit, r.get("start"), r["end"])
                        # SEC puts a period's calendar frame (e.g. CY2024) on whichever row was
                        # filed last, which can be a later proxy statement. The frame describes the
                        # period, not the filing, so read it from every row before filtering.
                        if r.get("frame"):
                            frames.setdefault(key, r["frame"])
                        if r.get("form") not in FORMS or r.get("filed", "") > config.SNAPSHOT:
                            continue
                        groups[key].append(r)
                recs = []
                for (unit, start, end), rows in groups.items():
                    s, e = _d(start), _d(end)
                    rows.sort(key=lambda r: r["filed"])
                    # Prefer the most recent annual report: 10-Q footnotes often restate a
                    # 10-K balance rounded ($90.7B for $90,678M), and "latest filed" alone
                    # would pick the rounded figure.
                    annual = [r for r in rows if r["form"].startswith("10-K")]
                    latest = (annual or rows)[-1]
                    distinct = {}
                    for r in rows:
                        if abs(r["val"] - latest["val"]) <= 0.001 * max(abs(latest["val"]), 1):
                            continue  # same value or a rounded copy of it, not a restatement
                        distinct.setdefault(r["val"], r)  # first filing that reported each value
                    recs.append({
                        "tag": tag, "taxonomy": tax, "unit": unit,
                        "start": start, "end": end, "kind": _kind(s, e),
                        "fiscal_year": fiscal_year(e, fye, t),
                        "val": latest["val"], "accn": latest["accn"], "form": latest["form"],
                        "filed": latest["filed"], "frame": frames.get((unit, start, end)),
                        "n_filings": len(rows),
                        # earliest filing that reported this period (for display; tools do not return it)
                        "first_accn": rows[0]["accn"], "first_form": rows[0]["form"], "first_filed": rows[0]["filed"],
                        "other_values": [
                            {"val": v, "accn": r["accn"], "form": r["form"], "filed": r["filed"]}
                            for v, r in distinct.items() if v != latest["val"]
                        ],
                    })
                if recs:
                    tags[tag] = recs
        self.facts[t] = tags
        self.labels[t] = labels


def in_scope(rec):
    return rec["fiscal_year"] in INDEXED_FY
