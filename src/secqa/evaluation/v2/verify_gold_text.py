"""Part A gold audit: is each gold cell's value printed in the 10-K it is attributed to?

    python -m secqa.evaluation.v2.verify_gold_text                 # writes results/v0.2/gold_text_audit.json
    python -m secqa.evaluation.v2.verify_gold_text --fetch-cited   # first downloads cited 10-Ks with no text

Independent of the gold builder: it reads only the gold items, the cached submissions index (accession ->
fiscal-year text file) and the converted 10-K text. A value counts as found when one of its usual printed
forms (in millions or thousands with thousands separators, the raw number, or for per-share values the
two-decimal amount) appears in the text as a whole token. Not found does not mean wrong: a value may be
printed only in a table the text conversion split, or be a sum of printed lines. Those are listed for
reading. Context lines are saved for a fixed-seed sample of found cells, to be read by hand.
"""
import json
import random
import re

from ... import config, edgar, filings

QA = [config.EVAL_DIR / "v0.2" / f for f in ("qa_test.json", "qa_dev.json")]
OUT = config.REPO_ROOT / "results" / "v0.2" / "gold_text_audit.json"
SAMPLE_SEED, SAMPLE_N = 2026, 20


def _all_10k(ticker):
    """Every original 10-K in the cached submissions index, filed on or before the snapshot."""
    from datetime import date

    from ...facts import fiscal_year
    s = edgar.submissions(ticker)
    r, fye = s["filings"]["recent"], s.get("fiscalYearEnd") or "1231"
    return [{"ticker": ticker, "fiscal_year": fiscal_year(date.fromisoformat(r["reportDate"][i]), fye),
             "form": "10-K", "accn": r["accessionNumber"][i], "doc": r["primaryDocument"][i]}
            for i, form in enumerate(r["form"])
            if form == "10-K" and r["reportDate"][i] and r["filingDate"][i] <= config.SNAPSHOT]


def accession_files():
    """accession -> converted text file name, for every 10-K whose text is on disk (indexed FY2023-FY2025,
    plus any cited filing fetched with --fetch-cited)."""
    m = {}
    for p in (config.RAW).glob("submissions_*.json"):
        t = p.stem.split("_", 1)[1]
        for f in _all_10k(t):
            name = f"{t}_FY{f['fiscal_year']}.txt"
            if (filings.text_dir() / name).exists():
                m[f["accn"]] = name
    return m


def fetch_cited():
    """Download and convert the 10-Ks that gold cells cite but that have no text on disk (e.g. FY2026
    10-Ks, the latest in the snapshot). Uses the project's EDGAR client (declared User-Agent from
    SEC_USER_AGENT, rate limit, cache) and the same HTML-to-text conversion as the indexed filings."""
    cited = {c["accession"]: c["ticker"] for path in QA for it in json.loads(path.read_text(encoding="utf-8"))
             for c in it["gold_cells"]}
    have = accession_files()
    edgar.ALLOW_FETCH = True
    got = []
    for accn, t in sorted(cited.items()):
        if accn in have:
            continue
        f = next((x for x in _all_10k(t) if x["accn"] == accn), None)
        if f is None:
            print("not an original 10-K in the snapshot:", t, accn)
            continue
        filings.fetch_text(f)
        got.append((t, accn, f"{t}_FY{f['fiscal_year']}.txt"))
    for g in got:
        print("fetched", *g)
    return got


def forms(value, unit):
    v = float(value)
    out = set()
    if unit and "share" in unit.lower() and "/" in unit:          # per-share (USD/shares)
        out.add(f"{abs(v):.2f}")
        return out
    a = abs(v)
    for div in (1e6, 1e3, 1):
        x = a / div
        if abs(x - round(x)) < 1e-9 and x >= 1:
            out.add(f"{int(round(x)):,}")
        elif div == 1e6:
            out.add(f"{x:,.1f}")                                 # e.g. 1,234.5 million in prose
    return out


def find(text, s):
    return [m.start() for m in re.finditer(r"(?<![\d,.])" + re.escape(s) + r"(?![\d,]|\.\d)", text)]


def main():
    files = accession_files()
    texts = {}
    rows = []
    seen = set()
    for path in QA:
        for it in json.loads(path.read_text(encoding="utf-8")):
            for c in it["gold_cells"]:
                key = (c["accession"], c["concept"], c["period_end"], c["value"])
                if key in seen:
                    continue
                seen.add(key)
                name = files.get(c["accession"])
                r = {"item": it["id"], "ticker": c["ticker"], "metric": c.get("metric"), "period": c.get("period"),
                     "concept": c["concept"], "value": c["value"], "unit": c.get("unit"),
                     "accession": c["accession"], "file": name}
                if not name:
                    # The cited filing (here: FY2026 10-Ks, latest in the snapshot) has no converted text.
                    # Proxy: is the same value printed in an indexed 10-K of the same filer? This checks the
                    # number, not that it appears in the cited filing.
                    r["status"] = "no_text_for_accession"
                    for fy in (2025, 2024, 2023):
                        alt = f"{c['ticker']}_FY{fy}.txt"
                        if alt not in texts and (filings.text_dir() / alt).exists():
                            texts[alt] = (filings.text_dir() / alt).read_text(encoding="utf-8")
                        if alt in texts and any(find(texts[alt], s) for s in forms(c["value"], c.get("unit"))):
                            r["status"], r["proxy_file"] = "found_in_other_10K_of_filer", alt
                            break
                else:
                    if name not in texts:
                        texts[name] = (filings.text_dir() / name).read_text(encoding="utf-8")
                    t = texts[name]
                    hits = {s: find(t, s) for s in forms(c["value"], c.get("unit"))}
                    hits = {s: h for s, h in hits.items() if h}
                    r["status"] = "found" if hits else "not_found"
                    if hits:
                        s, h = next(iter(sorted(hits.items())))
                        line_start = t.rfind("\n", 0, h[0]) + 1
                        line_end = t.find("\n", h[0])
                        r["match"] = s
                        r["context"] = t[max(line_start, h[0] - 200):line_end if line_end > 0 else None][:400]
                rows.append(r)
    found = [r for r in rows if r["status"] == "found"]
    sample = random.Random(SAMPLE_SEED).sample(found, min(SAMPLE_N, len(found)))
    summary = {s: sum(r["status"] == s for r in rows)
               for s in ("found", "found_in_other_10K_of_filer", "no_text_for_accession", "not_found")}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"cells": len(rows), "summary": summary,
                               "not_found": [r for r in rows if r["status"] != "found"],
                               "context_sample_seed": SAMPLE_SEED,
                               "context_sample": sample}, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(len(rows), summary)


if __name__ == "__main__":
    import sys
    if "--fetch-cited" in sys.argv:
        fetch_cited()
    main()
