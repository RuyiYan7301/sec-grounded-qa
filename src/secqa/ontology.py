"""Metric ontology: loading, structural checks, and coverage against the fact store.

The ontology itself is data (data/metric_ontology.yaml). This module does not resolve questions;
it only checks that the file is consistent and reports which metrics each filer actually reports.
"""
import hashlib
import re

import yaml

from . import config

PATH = config.REPO_ROOT / "data" / "metric_ontology.yaml"
PERIOD_TYPES = {"duration", "instant"}
UNIT_TYPES = {"currency", "per_share", "shares", "ratio"}
USES = {"primary", "fallback_with_warning"}


def load(path=PATH):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def file_hash(path=PATH):
    """sha256 of the file with line endings normalised, so a Windows checkout hashes the same."""
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def validate(o):
    """List of problems; empty means the ontology is consistent."""
    bad, ops = [], set(o["operations"])
    metrics, derived = o["metrics"], o.get("derived_metrics", {})
    alias_owner = {}
    for mid, m in {**metrics, **derived}.items():
        for a in m["aliases"]:
            key = a.lower()
            if key in alias_owner:
                bad.append(f"alias {a!r} used by both {alias_owner[key]} and {mid}")
            alias_owner[key] = mid
        for op in m["allowed_operations"]:
            if op not in ops:
                bad.append(f"{mid}: unknown operation {op}")
        if m.get("review", {}).get("status") not in {"draft", "reviewed", "confirmed"}:
            bad.append(f"{mid}: review.status missing")
    for mid, m in metrics.items():
        if m["period_type"] not in PERIOD_TYPES:
            bad.append(f"{mid}: period_type {m['period_type']}")
        if m["unit_type"] not in UNIT_TYPES:
            bad.append(f"{mid}: unit_type {m['unit_type']}")
        cands = [c["tag"] for c in m["candidate_concepts"]]
        if [c["priority"] for c in m["candidate_concepts"]] != list(range(1, len(cands) + 1)):
            bad.append(f"{mid}: priorities must be 1..n in order")
        if m["candidate_concepts"][0]["use"] != "primary":
            bad.append(f"{mid}: first candidate must be primary")
        for c in m["candidate_concepts"]:
            if c["use"] not in USES:
                bad.append(f"{mid}: use {c['use']}")
        for c in m["confounders"]:
            if c["tag"] in cands:
                bad.append(f"{mid}: {c['tag']} is both a candidate and a confounder")
            if not c.get("reason"):
                bad.append(f"{mid}: confounder {c['tag']} has no reason")
    for mid, d in derived.items():
        for name in re.findall(r"[a-z_]+", d["formula"]):
            if name not in metrics:
                bad.append(f"{mid}: formula uses unknown metric {name}")
    return bad


def _annual(rec, period_type):
    return rec["kind"] == ("FY" if period_type == "duration" else "instant")


def coverage(store, o=None):
    """metric -> ticker -> fiscal year -> (tag, use) of the candidate that would be chosen, or None.

    Instants are taken at fiscal-year end: the latest instant within the fiscal year."""
    o = o or load()
    years = o["fiscal_years"]
    out = {}
    for mid, m in o["metrics"].items():
        out[mid] = {}
        for t in store.tickers:
            row = {}
            for y in years:
                row[y] = None
                for c in m["candidate_concepts"]:
                    recs = [r for r in store.facts[t].get(c["tag"], [])
                            if r["fiscal_year"] == y and _annual(r, m["period_type"])]
                    if recs:
                        row[y] = (c["tag"], c["use"])
                        break
            out[mid][t] = row
    return out


def summary(cov):
    """(cells with a primary concept, cells with only a fallback, empty cells)."""
    cells = [v for by_t in cov.values() for row in by_t.values() for v in row.values()]
    primary = sum(1 for v in cells if v and v[1] == "primary")
    fallback = sum(1 for v in cells if v and v[1] != "primary")
    return primary, fallback, len(cells) - primary - fallback


def report(out=print):
    from . import tools
    o = load()
    problems = validate(o)
    store = tools.store()
    cov = coverage(store, o)
    years = o["fiscal_years"]
    out(f"ontology v{o['version']} ({o['status']}), sha256 {file_hash()[:12]}")
    out(f"{len(o['metrics'])} base metrics, {len(o.get('derived_metrics', {}))} derived, "
        f"{len(store.tickers)} filers x FY{years[0]}-FY{years[-1]}")
    out("  legend: P primary concept  f fallback (answer carries a warning)  - not reported\n")
    out(f"{'metric':30s} " + " ".join(f"{t:>5s}" for t in store.tickers))
    for mid, by_t in cov.items():
        cells = []
        for t in store.tickers:
            cells.append(f"{''.join('-' if v is None else 'P' if v[1] == 'primary' else 'f' for v in by_t[t].values()):>5s}")
        out(f"{mid:30s} " + " ".join(cells))
    p, f, n = summary(cov)
    total = p + f + n
    out(f"\ncoverage: {p}/{total} primary ({p / total:.0%}), {f} fallback, {n} not reported")
    if problems:
        out("\nproblems:\n" + "\n".join(f"  - {x}" for x in problems))
    return not problems
