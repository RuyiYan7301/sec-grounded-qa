"""v0.4 generalization test, part 2a: coverage of the frozen ontology + resolver on the v0.4 universe.

    python -m secqa.evaluation.v4.coverage      # writes results/v0.4/coverage/{cells.jsonl,labels.json,summary.json}

Frozen code only: facts.Store, resolve.SnapshotSource, resolve.resolve and the frozen ontology. Nothing is
fixed here; this records what the v0.2 rules do on companies and years they were not built on.

Per (company, metric, fiscal year) cell: the resolver's status (resolved / fallback_with_warning /
ambiguous_concept / not_reported), or `no_10k` when the company filed no 10-K for that fiscal year before
the snapshot. Fiscal years are the engine's labels (facts.fiscal_year: the calendar year the fiscal year
ends in). labels.json compares that label with each 10-K's own fiscal-year focus (DEI `fy` on the filing's
current-period rows), because companies do not all name their fiscal years the same way.
"""
import json
from collections import Counter, defaultdict
from datetime import date

from ... import config, edgar, facts, ontology, universe
from ...engine import resolve

YEARS = range(2019, 2026)
OUT = config.REPO_ROOT / "results" / "v0.4" / "coverage"


def _pages(ticker):
    """The submissions file's `recent` block holds only the latest ~1,000 filings; older ones are in
    extra pages listed under filings.files (fetched and cached like the main file)."""
    sub = edgar.submissions(ticker)
    pages = [sub["filings"]["recent"]]
    edgar.ALLOW_FETCH = True
    for f in sub["filings"].get("files", []):
        pages.append(edgar._cached(f"submissions_{ticker}_{f['name']}", f"https://data.sec.gov/submissions/{f['name']}"))
    return pages


def _tenks(ticker, fye):
    """10-K filings before the snapshot: accession -> (report date, engine FY label)."""
    out = {}
    for r in _pages(ticker):
        for i, form in enumerate(r["form"]):
            if form == "10-K" and r["reportDate"][i] and r["filingDate"][i] <= config.SNAPSHOT:
                end = date.fromisoformat(r["reportDate"][i])
                out[r["accessionNumber"][i]] = (r["reportDate"][i], facts.fiscal_year(end, fye))
    return out


def _own_labels(ticker, tenks):
    """Each 10-K's own fiscal-year focus, read from companyfacts rows filed with it (DEI fy, mode)."""
    seen = defaultdict(Counter)
    for tax in edgar.companyfacts(ticker)["facts"].values():
        for c in tax.values():
            for rows in c["units"].values():
                for x in rows:
                    if x.get("accn") in tenks and x.get("form") == "10-K" and x.get("end") == tenks[x["accn"]][0]:
                        if x.get("fy"):
                            seen[x["accn"]][x["fy"]] += 1
    return {a: seen[a].most_common(1)[0][0] if seen[a] else None for a in tenks}


def run():
    onto = ontology.load()
    filers = universe.filers()
    edgar.FILERS.update({t: c for t, c in filers.items() if t not in edgar.FILERS})
    OUT.mkdir(parents=True, exist_ok=True)
    labels, n = {}, Counter()
    with open(OUT / "cells.jsonl", "w", encoding="utf-8") as f:
        for t in filers:
            store = facts.Store([t])
            fye = store.meta[t]["fiscal_year_end"]
            tenks = _tenks(t, fye)
            own = _own_labels(t, tenks)
            labels[t] = {"fiscal_year_end": fye, "original": t in universe.ORIGINAL,
                         "tenks": [{"accession": a, "report_date": d, "engine_fy": fy, "own_fy": own[a]}
                                   for a, (d, fy) in sorted(tenks.items(), key=lambda kv: kv[1][0])]}
            have = {fy for _, fy in tenks.values()}
            src = resolve.SnapshotSource(store)
            for mid in onto["metrics"]:
                for y in YEARS:
                    if y not in have:
                        row = {"ticker": t, "metric": mid, "fy": y, "status": "no_10k"}
                    else:
                        r = resolve.resolve(src, onto, t, mid, y)
                        c = r["cell"] or {}
                        row = {"ticker": t, "metric": mid, "fy": y, "status": r["status"],
                               "concept": c.get("concept"), "use": c.get("use"), "value": c.get("value"),
                               "unit": c.get("unit"), "period_end": c.get("period_end"),
                               "accession": c.get("accession"), "n_other_values": len(c.get("other_values") or []),
                               "candidates_found": [x["concept"] for x in r["others"] + r["alternates"]]}
                    row["original"] = t in universe.ORIGINAL
                    f.write(json.dumps(row) + "\n")
                    n[(row["original"], row["status"])] += 1
            print(f"{t:6s} FYE {fye}  10-Ks {len(tenks)}", flush=True)
    (OUT / "labels.json").write_text(json.dumps(labels, indent=1), encoding="utf-8")
    summary = {"snapshot": config.SNAPSHOT, "years": [min(YEARS), max(YEARS)],
               "counts": {f"{'original' if o else 'new'}:{s}": k for (o, s), k in sorted(n.items())}}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    run()
