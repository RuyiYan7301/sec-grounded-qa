"""Check generated gold values against the 10-K text, independently of the fact store.

For each gold value, look for it as printed in a 10-K (millions with thousands separators,
or a two-decimal per-share figure) in the filer's 10-Ks for that fiscal year and the two
after it (later 10-Ks carry it as a comparative). Then print the surrounding text for a
random sample so a person can confirm the figure is the right line item for the right year.

    secqa verify-gold [--sample 20]
"""
import json
import random
import re

from .. import config, filings


def printed(v, unit):
    if unit == "USD/shares":
        return [f"{v:.2f}"]
    m = abs(v) / 1e6
    return [f"{m:,.0f}"]


def find(ticker, fy, s):
    hits = []
    for y in (fy, fy + 1, fy + 2):
        p = filings.text_dir() / f"{ticker}_FY{y}.txt"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r"(?<![\d,.])" + re.escape(s) + r"(?![\d]|,\d)", text):
            hits.append((y, text[max(0, m.start() - 160):m.end() + 60].replace("\n", " | ")))
    return hits


def main(n_sample=20):
    qs = json.loads((config.EVAL_DIR / "gold_test.json").read_text(encoding="utf-8"))
    checks = []
    for q in qs:
        if q["check"] != "numeric":
            continue
        tickers = q["company"].split(",")
        fys = [int(x) for x in re.findall(r"FY(\d{4})", q["period"])]
        if len(tickers) == 2:
            pairs = list(zip(tickers, fys * 2, q["gold"]))
        else:
            pairs = [(tickers[0], fy, v) for fy, v in zip(fys if len(fys) == len(q["gold"]) else fys * len(q["gold"]), q["gold"])]
        for t, fy, v in pairs:
            s = printed(v, q.get("gold_unit", "USD"))[0]
            checks.append({"id": q["id"], "ticker": t, "fy": fy, "metric": q["metric"], "val": v,
                           "printed": s, "hits": find(t, fy, s)})
    missing = [c for c in checks if not c["hits"]]
    print(f"{len(checks)} gold values; found in 10-K text: {len(checks) - len(missing)}; missing: {len(missing)}")
    for c in missing:
        print("  MISSING", c["id"], c["ticker"], f"FY{c['fy']}", c["metric"], c["printed"])
    rng = random.Random(0)
    print(f"\n--- random sample of {n_sample} for reading ---")
    for c in rng.sample([c for c in checks if c["hits"]], n_sample):
        y, ctx = c["hits"][0]
        print(f"\n[{c['id']}] {c['ticker']} FY{c['fy']} {c['metric']} = {c['printed']}  (in FY{y} 10-K, {len(c['hits'])} hits)")
        print("   ", ctx)
