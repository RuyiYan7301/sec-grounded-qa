"""Metric resolver: (company, metric, fiscal year) -> one value with its provenance, by the ontology rules.

Statuses: resolved | fallback_with_warning | ambiguous_concept | not_reported (decisions, step 3).
Rules (data/metric_ontology.yaml, resolution_rules): only 10-K / 10-K/A rows; one primary -> use it;
several primaries with the same value -> highest priority, others kept as `alternates`; several primaries
with different values -> ambiguous_concept (never a silent choice); primary and fallback -> primary, the
fallback recorded; only fallbacks -> highest-priority fallback with a scope warning (fallbacks with
different values -> ambiguous_concept); confounders and extension concepts are never used.

Two value sources, never the gold builder:
  SnapshotSource   Part A, latest_in_snapshot, through the system's fact store (facts.Store)
  FilingFactIndex  Part B, as_of_filing with the exact target accession, from raw companyfacts and
                   submissions only; a value must come from a row with accn == target accession
"""
from datetime import date

from .. import edgar, facts

ANNUAL = ("10-K", "10-K/A")


def candidates(metric):
    return sorted(metric["candidate_concepts"], key=lambda c: c.get("priority", 99))


def settle(found):
    """found: [(candidate, cell)] in priority order -> (status, chosen cell or None, alternates, others)."""
    if not found:
        return "not_reported", None, [], []
    primary = [(c, x) for c, x in found if c["use"] == "primary"]
    pool = primary or found
    if len({x["value"] for _, x in pool}) > 1:
        return "ambiguous_concept", None, [], [x for _, x in found]
    chosen = pool[0][1]
    alternates = [x for _, x in pool[1:]]
    others = [x for c, x in found if (c, x) not in pool]
    return ("resolved" if primary else "fallback_with_warning"), chosen, alternates, others


def _period_ok(kind, period_type):
    return kind == ("FY" if period_type == "duration" else "instant")


class SnapshotSource:
    """latest_in_snapshot through facts.Store (dedupes repeats, keeps every distinct value)."""

    policy = "latest_in_snapshot"

    def __init__(self, store):
        self.store = store

    def cell(self, ticker, metric_id, metric, fy, tag):
        recs = [r for r in self.store.facts.get(ticker, {}).get(tag, [])
                if r["fiscal_year"] == fy and _period_ok(r["kind"], metric["period_type"]) and r["form"] in ANNUAL
                and r["taxonomy"] == "us-gaap"]
        if not recs:
            return None
        r = max(recs, key=lambda r: r["end"])     # instants: the fiscal-year-end balance
        return {"ticker": ticker, "metric": metric_id, "fy": f"FY{fy}", "concept": tag, "value": r["val"],
                "unit": r["unit"], "period_start": r["start"], "period_end": r["end"], "accession": r["accn"],
                "form": r["form"], "filed": r["filed"], "value_policy": self.policy,
                "first_accession": r["first_accn"], "first_filed": r["first_filed"],
                "other_values": r["other_values"]}


class FilingFactIndex:
    """as_of_filing with the exact target accession, from raw companyfacts and submissions only."""

    policy = "as_of_filing"

    def __init__(self, ticker, target_fy):
        self.ticker = ticker
        sub = edgar.submissions(ticker)
        self.fye = sub.get("fiscalYearEnd") or "1231"
        r = sub["filings"]["recent"]
        hits = sorted((r["filingDate"][i], r["accessionNumber"][i]) for i, f in enumerate(r["form"])
                      if f == "10-K" and r["reportDate"][i]
                      and facts.fiscal_year(date.fromisoformat(r["reportDate"][i]), self.fye) == target_fy)
        if not hits:
            raise LookupError(f"no original 10-K for {ticker} FY{target_fy}")
        self.target_filed, self.target_accession = hits[0]
        self.raw = edgar.companyfacts(ticker)["facts"].get("us-gaap", {})

    def _rows(self, tag, fy, period_type):
        out = []
        for unit, rows in self.raw.get(tag, {}).get("units", {}).items():
            for x in rows:
                if x.get("form") not in ANNUAL or not x.get("end"):
                    continue
                e = date.fromisoformat(x["end"])
                s = date.fromisoformat(x["start"]) if x.get("start") else None
                if facts.fiscal_year(e, self.fye) != fy or not _period_ok(facts._kind(s, e), period_type):
                    continue
                out.append({**x, "unit": unit})
        return out

    def cell(self, ticker, metric_id, metric, fy, tag):
        rows = [x for x in self._rows(tag, fy, metric["period_type"]) if x["accn"] == self.target_accession]
        if not rows:
            return None            # not presented in the target filing: never filled in from another one
        r = max(rows, key=lambda x: x["end"])
        earlier = [x for x in self._rows(tag, fy, metric["period_type"])
                   if x["filed"] < self.target_filed and x["end"] == r["end"] and x.get("start") == r.get("start")]
        first = min(earlier, key=lambda x: (x["filed"], x["accn"])) if earlier else None
        return {"ticker": ticker, "metric": metric_id, "fy": f"FY{fy}", "concept": tag, "value": r["val"],
                "unit": r["unit"], "period_start": r.get("start"), "period_end": r["end"],
                "accession": r["accn"], "form": r["form"], "filed": r["filed"], "value_policy": self.policy,
                "first_reported": ({"value": first["val"], "accession": first["accn"], "filed": first["filed"]}
                                   if first else None)}


def resolve(source, ontology, ticker, metric_id, fy):
    """One base metric cell -> {"status", "cell", "alternates", "others", "interpreted"}."""
    m = ontology["metrics"][metric_id]
    found = []
    for c in candidates(m):
        x = source.cell(ticker, metric_id, m, fy, c["tag"])
        if x is not None:
            found.append((c, {**x, "use": c["use"]}))
    status, chosen, alternates, others = settle(found)
    return {"metric": metric_id, "ticker": ticker, "fy": f"FY{fy}", "status": status, "cell": chosen,
            "alternates": alternates, "others": others}
