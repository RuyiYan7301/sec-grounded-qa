"""v0.4 universe: S&P 100 non-financial filers (docs/v0.4-plan.md, section 1).

    python -m secqa.universe build      # resolve CIKs, write data/universe/filers_v0.4.json
    python -m secqa.universe download   # fetch submissions + companyfacts for every v0.4 filer

The v0.2 engine keeps its own 8 filers (edgar.FILERS); v0.4 code reads `filers()` from here.
"""
import json
import re
import sys
from datetime import date

from . import config, edgar

UNIVERSE_DIR = config.REPO_ROOT / "data" / "universe"
SOURCE = UNIVERSE_DIR / "sp100_rev1385872457.json"
MANIFEST = UNIVERSE_DIR / "filers_v0.4.json"
EXCLUDED_SECTORS = ("Financials",)
SAME_FILER = {"GOOG": "GOOGL"}  # share classes of one filer: keep one ticker
# Decided by hand after a download, reason recorded in the manifest (plan, section 1).
CIK_OVERRIDES = {
    "XOM": (34088, "company_tickers.json maps XOM to ExxonMobil Holdings Corp (CIK 2115436), a holding company "
                   "with no 10-K before the snapshot; every FY2019-FY2025 10-K is filed by Exxon Mobil Corp, CIK 34088"),
}


def _ticker_map():
    """SEC company_tickers.json (cached in data/raw with its download date)."""
    edgar.ALLOW_FETCH = True
    data = edgar._cached("company_tickers.json", "https://www.sec.gov/files/company_tickers.json")
    out = {}
    for row in data.values():
        out.setdefault(row["ticker"].upper(), set()).add(int(row["cik_str"]))
    return out


def build():
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    tmap = _ticker_map()
    filers, excluded, unresolved = {}, [], []
    for r in src["rows"]:
        sym = r["symbol"].upper()
        if r["sector"] in EXCLUDED_SECTORS:
            excluded.append({"symbol": sym, "reason": f"sector {r['sector']}"})
            continue
        if sym in SAME_FILER:
            excluded.append({"symbol": sym, "reason": f"same filer as {SAME_FILER[sym]}"})
            continue
        ciks = tmap.get(sym.replace(".", "-")) or tmap.get(sym)
        if sym in CIK_OVERRIDES:
            ciks = {CIK_OVERRIDES[sym][0]}
        if not ciks or len(ciks) != 1:
            unresolved.append({"symbol": sym, "ciks": sorted(ciks or [])})
            continue
        filers[sym] = {"cik": next(iter(ciks)), "name": r["name"], "sector": r["sector"],
                       "original": sym in edgar.FILERS}
        if sym in CIK_OVERRIDES:
            filers[sym]["cik_override"] = CIK_OVERRIDES[sym][1]
    for t, cik in edgar.FILERS.items():  # the 8 v0.2 filers must resolve to the same CIK
        if t in filers and filers[t]["cik"] != cik:
            unresolved.append({"symbol": t, "ciks": [filers[t]["cik"], cik], "note": "differs from v0.2"})
    manifest = {"source": SOURCE.name, "built": date.today().isoformat(),
                "company_tickers_json": "data/raw/company_tickers.json (SEC, cached)",
                "excluded_sectors": list(EXCLUDED_SECTORS), "n_filers": len(filers),
                "filers": filers, "excluded": excluded, "unresolved": unresolved}
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(filers)} filers, {len(excluded)} excluded, {len(unresolved)} unresolved -> {MANIFEST}")
    for u in unresolved:
        print("  unresolved:", u)


def filers():
    """ticker -> CIK for every v0.4 filer (from the committed manifest)."""
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {t: f["cik"] for t, f in m["filers"].items()}


def download(refresh=False, log=print):
    """Fetch submissions and companyfacts for every v0.4 filer into data/raw (cached, resumable)."""
    edgar.ALLOW_FETCH = True
    edgar.FILERS.update({t: c for t, c in filers().items() if t not in edgar.FILERS})
    for i, t in enumerate(filers(), 1):
        s = edgar.submissions(t, refresh)
        f = edgar.companyfacts(t, refresh)
        n = sum(len(u) for tax in f["facts"].values() for c in tax.values() for u in c["units"].values())
        log(f"{i:3d} {t:6s} {s['name'][:34]:<34s} FYE {s.get('fiscalYearEnd')}  facts={n:,}")


if __name__ == "__main__":
    {"build": build, "download": download}[sys.argv[1]]()


ORIGINAL = frozenset(edgar.FILERS)  # the 8 v0.2 filers, captured at import (before any v0.4 update)

SUFFIXES = re.compile(r"( \(Class [A-Z]\)|,? Inc\.?| Corporation| Corp\.?| \(The\)| plc| Holdings| and Company| & Company| Company| & Co\.,?)+$")
YEARS_V04 = tuple(range(2019, 2026))
SCHEMA_V04 = config.EVAL_DIR / "v0.4" / "plan.schema.json"


def short_names():
    """Plain company names for questions and the planner prompt, by one mechanical rule: the 8 v0.2 filers
    keep their v0.2 names; the others drop legal suffixes from the constituents table's name."""
    from .engine import plan
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))["filers"]
    return {t: plan.COMPANIES.get(t) or SUFFIXES.sub("", f["name"]).strip() for t, f in m.items()}


def activate():
    """Point the frozen engine at the v0.4 universe, mechanically (docs/v0.4-plan.md 2b): ticker list, names
    and covered years. Prompt wording, schema structure, executor and scorer are not changed."""
    from .engine import periods, plan
    f = filers()
    names = short_names()
    edgar.FILERS.update({t: c for t, c in f.items() if t not in edgar.FILERS})
    schema = json.loads(plan.SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["$id"] = "secqa-v0.4-plan"
    schema["oneOf"][0]["properties"]["companies"]["items"]["enum"] = list(f)
    SCHEMA_V04.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_V04.write_text(json.dumps(schema, indent=1) + "\n", encoding="utf-8")
    plan.SCHEMA_PATH = SCHEMA_V04
    plan.COMPANIES = {t: names[t] for t in f}
    plan.YEARS = tuple(f"FY{y}" for y in YEARS_V04)
    periods.COVERED = YEARS_V04
    plan.schema.cache_clear()
    plan.system_prompt.cache_clear()
