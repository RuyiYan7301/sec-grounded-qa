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
        for ia in m.get("interpreted_aliases", []):
            if not ia.get("warning"):
                bad.append(f"{mid}: interpreted alias {ia['alias']!r} has no warning")
        for a in m["aliases"] + [ia["alias"] for ia in m.get("interpreted_aliases", [])]:
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
    for mid, m in metrics.items():
        if m.get("split_sensitive") and "cross_company_comparison" in m["allowed_operations"]:
            bad.append(f"{mid}: split-sensitive metrics are not compared across companies")
    for mid, d in derived.items():
        for name in re.findall(r"[a-z_]+", d["formula"]):
            if name not in metrics:
                bad.append(f"{mid}: formula uses unknown metric {name}")
    return bad


def _annual(rec, period_type):
    return rec["kind"] == ("FY" if period_type == "duration" else "instant")


def resolve_cell(store, ticker, metric, year):
    """How the resolution rules settle one (company, metric, fiscal year) cell, from the store.

    Returns None (not reported) or a dict:
      status      ok | alternates | fallback | ambiguous_concept
      tag, use, val    the chosen candidate (None when ambiguous)
      others      every other reported candidate with its value
    Only values reported in a 10-K count. Instants are taken at fiscal-year end: the latest
    instant within the fiscal year."""
    kind = "FY" if metric["period_type"] == "duration" else "instant"
    found = []
    for c in metric["candidate_concepts"]:
        recs = [r for r in store.facts[ticker].get(c["tag"], []) if r["fiscal_year"] == year and r["kind"] == kind and r["form"].startswith("10-K")]
        if recs:
            r = max(recs, key=lambda r: r["end"])
            found.append({"tag": c["tag"], "use": c["use"], "val": r["val"]})
    if not found:
        return None
    primary = [f for f in found if f["use"] == "primary"]
    if not primary:
        chosen, status = found[0], "fallback"
    elif len({f["val"] for f in primary}) > 1:
        return {"status": "ambiguous_concept", "tag": None, "use": None, "others": found}
    else:
        chosen, status = primary[0], ("alternates" if len(primary) > 1 else "ok")
    return {"status": status, "tag": chosen["tag"], "use": chosen["use"], "val": chosen["val"],
            "others": [f for f in found if f is not chosen]}


def coverage(store, o=None):
    """metric -> ticker -> fiscal year -> resolve_cell(...)."""
    o = o or load()
    return {mid: {t: {y: resolve_cell(store, t, m, y) for y in o["fiscal_years"]} for t in store.tickers}
            for mid, m in o["metrics"].items()}


SYMBOL = {None: "-", "ok": "P", "alternates": "A", "fallback": "f", "ambiguous_concept": "X"}


def summary(cov):
    """Count of cells per status (None = not reported)."""
    counts = dict.fromkeys(SYMBOL, 0)
    for by_t in cov.values():
        for row in by_t.values():
            for v in row.values():
                counts[v and v["status"]] += 1
    return counts


def report(out=print, validate_only=False):
    o = load()
    problems = validate(o)
    out(f"ontology v{o['version']} ({o['status']})")
    out(f"sha256 {file_hash()}")
    out(f"{len(o['metrics'])} base metrics, {len(o.get('derived_metrics', {}))} derived")
    if problems:
        out("\nproblems:\n" + "\n".join(f"  - {x}" for x in problems))
    else:
        out("structure: ok")
    if validate_only:
        return not problems
    from . import tools
    store = tools.store()
    cov = coverage(store, o)
    years = o["fiscal_years"]
    out(f"\ncoverage, {len(store.tickers)} filers x FY{years[0]}-FY{years[-1]}")
    out("  P primary   A primary, other primaries agree   f fallback only (answer carries a warning)")
    out("  X candidates disagree (ambiguous_concept)   - not reported\n")
    out(f"{'metric':30s} " + " ".join(f"{t:>5s}" for t in store.tickers))
    for mid, by_t in cov.items():
        cells = ["".join(SYMBOL[v and v["status"]] for v in by_t[t].values()) for t in store.tickers]
        out(f"{mid:30s} " + " ".join(f"{c:>5s}" for c in cells))
    c = summary(cov)
    total = sum(c.values())
    used = c["ok"] + c["alternates"]
    out(f"\n{used}/{total} primary ({used / total:.0%}; {c['alternates']} with agreeing alternates), "
        f"{c['fallback']} fallback only, {c['ambiguous_concept']} ambiguous, {c[None]} not reported")
    shadowed = [(mid, t, y, v) for mid, by_t in cov.items() for t, row in by_t.items() for y, v in row.items()
                if v and v["status"] in ("ok", "alternates") and any(x["use"] != "primary" for x in v["others"])]
    differ = [(mid, t, y, v) for mid, t, y, v in shadowed
              if any(x["use"] != "primary" and x["val"] != v["val"] for x in v["others"])]
    if shadowed:
        out(f"\n{len(shadowed)} cells use the primary while a fallback is also reported (recorded in evidence); "
            f"{len(differ)} of them differ in value:")
        for mid, t, y, v in differ:
            fb = "; ".join(f"{x['tag']} {x['val']:,.0f}" for x in v["others"] if x["use"] != "primary")
            out(f"  {mid} {t} FY{y}: {v['tag']} {v['val']:,.0f} used; {fb}")
    return not problems
