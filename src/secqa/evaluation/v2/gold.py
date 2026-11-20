"""Gold values for the v0.2 benchmark, computed straight from the raw companyfacts JSON.

Deliberately independent of facts.Store, tools and ontology.resolve_cell: it re-implements period
selection, value versions and concept resolution from the raw rows and the frozen ontology, so a
bug in the system's data layer is not copied into the gold answers.

Value policies (see data/metric_ontology.yaml):
  latest_in_snapshot  latest 10-K / 10-K/A row filed on or before the snapshot
  as_of_filing        latest 10-K / 10-K/A row filed on or before a cutoff date (the target filing)
"""
import json
from datetime import date, timedelta
from functools import lru_cache

from ... import config, edgar

ANNUAL = ("10-K", "10-K/A")
SAME = 0.001  # relative difference below which two reported values are the same figure (rounding)


@lru_cache(maxsize=None)
def _raw(ticker):
    return edgar.companyfacts(ticker)["facts"].get("us-gaap", {})


@lru_cache(maxsize=None)
def fye(ticker):
    return edgar.submissions(ticker).get("fiscalYearEnd") or "1231"


@lru_cache(maxsize=None)
def _label_offsets():
    """v0.4 2c: per-filer label offsets read straight from the committed table (derived from each
    10-K's own DEI fiscal-year focus), not from facts.py. Empty for the 8 v0.2 filers."""
    path = config.REPO_ROOT / "data" / "universe" / "fy_label_offsets.json"
    return json.loads(path.read_text(encoding="utf-8"))["offsets"] if path.exists() else {}


def fiscal_year_of(ticker, end):
    """Fiscal year label of a period ending on `end`: the year whose nominal FYE (+7 days for
    52/53-week calendars) is the first on or after `end`, plus the filer's own label offset."""
    mm, dd = int(fye(ticker)[:2]), int(fye(ticker)[2:])
    e = date.fromisoformat(end)
    for y in (e.year - 1, e.year, e.year + 1):
        if e <= date(y, mm, min(dd, 28)) + timedelta(days=7):
            return y + _label_offsets().get(ticker, 0)
    raise ValueError(end)


def _is_fy(r):
    if "start" not in r:
        return False
    return 350 <= (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days <= 380


def _rows(ticker, tag, fy, period_type, cutoff):
    """Annual-report rows for (tag, fiscal year), filed on or before cutoff, one period only."""
    units = _raw(ticker).get(tag, {}).get("units", {})
    rows = [dict(r, unit=u) for u, rs in units.items() for r in rs
            if r.get("form") in ANNUAL and r.get("filed", "") <= cutoff
            and fiscal_year_of(ticker, r["end"]) == fy
            and (_is_fy(r) if period_type == "duration" else "start" not in r)]
    if not rows:
        return []
    # One period: for instants the fiscal-year-end balance (latest end within the year).
    end = max(r["end"] for r in rows)
    return sorted((r for r in rows if r["end"] == end), key=lambda r: (r["filed"], r["accn"]))


def value(ticker, tag, fy, period_type, cutoff=None):
    """The reported value under the cutoff, with its filing and every earlier differing value."""
    cutoff = cutoff or config.SNAPSHOT
    rows = _rows(ticker, tag, fy, period_type, cutoff)
    if not rows:
        return None
    latest = rows[-1]
    earlier = []
    for r in rows:
        if abs(r["val"] - latest["val"]) > SAME * max(abs(latest["val"]), 1) and \
                r["val"] not in [e["val"] for e in earlier]:
            earlier.append({"val": r["val"], "accn": r["accn"], "filed": r["filed"], "form": r["form"]})
    return {"ticker": ticker, "tag": tag, "fy": fy, "val": latest["val"], "unit": latest["unit"],
            "end": latest["end"], "start": latest.get("start"), "accn": latest["accn"],
            "form": latest["form"], "filed": latest["filed"], "first_accn": rows[0]["accn"],
            "first_filed": rows[0]["filed"], "earlier_values": earlier}


def resolve(ontology, ticker, metric_id, fy, cutoff=None):
    """Apply the ontology's resolution rules to one cell.

    Returns {"outcome": "answer" | "not_reported" | "ambiguous_concept", ...}; for an answer also
    "fact" (see value()), "use" (primary / fallback_with_warning) and "others" (other reported candidates)."""
    m = ontology["metrics"][metric_id]
    found = []
    for c in m["candidate_concepts"]:
        v = value(ticker, c["tag"], fy, m["period_type"], cutoff)
        if v is not None:
            found.append((c, v))
    if not found:
        return {"outcome": "not_reported", "metric": metric_id, "ticker": ticker, "fy": fy}
    primary = [(c, v) for c, v in found if c["use"] == "primary"]
    if primary and len({v["val"] for _, v in primary}) > 1:
        return {"outcome": "ambiguous_concept", "metric": metric_id, "ticker": ticker, "fy": fy,
                "others": [{"tag": c["tag"], "val": v["val"]} for c, v in found]}
    c, v = (primary or found)[0]
    return {"outcome": "answer", "metric": metric_id, "ticker": ticker, "fy": fy, "use": c["use"], "fact": v,
            "others": [{"tag": c2["tag"], "use": c2["use"], "val": v2["val"]} for c2, v2 in found if c2 is not c]}


def derived(ontology, ticker, metric_id, fy, cutoff=None):
    """Resolve a derived metric from its components. Formula is 'a / b' or 'a - b'."""
    d = ontology["derived_metrics"][metric_id]
    a, op, b = d["formula"].split()
    ra, rb = resolve(ontology, ticker, a, fy, cutoff), resolve(ontology, ticker, b, fy, cutoff)
    base = {"metric": metric_id, "ticker": ticker, "fy": fy, "formula": d["formula"], "components": [ra, rb]}
    for r in (ra, rb):
        if r["outcome"] != "answer":
            return base | {"outcome": r["outcome"]}
    va, vb = ra["fact"]["val"], rb["fact"]["val"]
    fallback = any(r["use"] != "primary" for r in (ra, rb))
    if op == "/":
        if vb <= 0:
            return base | {"outcome": "not_meaningful"}
        return base | {"outcome": "answer", "val": va / vb, "unit": "ratio", "fallback": fallback}
    return base | {"outcome": "answer", "val": va - vb, "unit": ra["fact"]["unit"], "fallback": fallback}


def cell(ontology, ticker, metric_id, fy, cutoff=None):
    """resolve() or derived(), whichever the metric is."""
    if metric_id in ontology["metrics"]:
        r = resolve(ontology, ticker, metric_id, fy, cutoff)
        if r["outcome"] == "answer":
            r |= {"val": r["fact"]["val"], "unit": r["fact"]["unit"], "fallback": r["use"] != "primary"}
        return r
    return derived(ontology, ticker, metric_id, fy, cutoff)


def change(v1, v2, kind):
    """Gold result of a two-period operation."""
    if kind == "absolute_change":
        return {"outcome": "answer", "val": v2 - v1}
    if kind == "percent_change":
        if v1 <= 0:
            return {"outcome": "not_meaningful", "absolute_change": v2 - v1}
        return {"outcome": "answer", "val": (v2 - v1) / v1}
    if kind == "percentage_point_change":
        return {"outcome": "answer", "val": (v2 - v1) * 100}
    raise ValueError(kind)
