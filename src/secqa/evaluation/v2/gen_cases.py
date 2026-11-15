"""Part B numeric gold: per-case labels for every ontology metric, from the raw data (gold.py).

    python -m secqa.evaluation.v2.gen_cases            # writes data/eval/v0.2/cases/*.numeric.json
    python -m secqa.evaluation.v2.gen_cases --sensitivity

Values are taken as of the target filing (`as_of_filing`): only 10-K rows filed on or before the
target 10-K's filing date. Size labels follow docs/benchmark-v0.2.md; they are size labels, not a
materiality judgement.
"""
import argparse
import json
from collections import Counter

from ... import config, edgar, ontology
from . import gold

OUT = config.EVAL_DIR / "v0.2" / "cases"
CASES = {
    "NVDA_FY2025": ("NVDA", 2024, 2025, "test"),
    "INTC_FY2025": ("INTC", 2024, 2025, "test"),
    "AVGO_FY2024": ("AVGO", 2023, 2024, "test"),
    "CSCO_FY2024": ("CSCO", 2023, 2024, "dev"),
}
MICRO = {"AMD_FY2025_sga": ("AMD", 2024, 2025, "selling_general_administrative")}

# (large, control) thresholds: percent for amounts, percentage points for ratios
THRESHOLDS = {"amount": (10.0, 2.0), "ratio": (2.0, 0.5)}


def target_filing(ticker, fy):
    """The original 10-K for fiscal year fy (not an amendment)."""
    r = edgar.submissions(ticker)["filings"]["recent"]
    hits = [(r["filingDate"][i], r["accessionNumber"][i]) for i, f in enumerate(r["form"])
            if f == "10-K" and r["reportDate"][i] and gold.fiscal_year_of(ticker, r["reportDate"][i]) == fy]
    filed, accn = min(hits)
    return {"accession": accn, "filed": filed, "url": edgar.filing_url(ticker, accn)}


def _tags(c):
    if "fact" in c:
        return [c["fact"]["tag"]]
    return [t for comp in c.get("components", []) for t in _tags(comp)]


def size_label(kind, v1, v2, th=THRESHOLDS):
    if kind == "ratio":
        large, control = th["ratio"]
        d = abs(v2 - v1) * 100
        return "large_numeric_change" if d >= large else "unchanged_control" if d < control else "gray_zone"
    large, control = th["amount"]
    if v1 <= 0:
        return "large_numeric_change" if (v1 < 0 <= v2 or v1 == 0 != v2 or v2 < 0 <= v1) else "gray_zone"
    p = abs(v2 - v1) / v1 * 100
    return "large_numeric_change" if p >= large else "unchanged_control" if p < control else "gray_zone"


def label_case(o, ticker, y1, y2, th=THRESHOLDS):
    cutoff = target_filing(ticker, y2)["filed"]
    items = []
    for mid in list(o["metrics"]) + list(o["derived_metrics"]):
        kind = "ratio" if o.get("derived_metrics", {}).get(mid, {}).get("unit_type") == "ratio" else "amount"
        c1, c2 = gold.cell(o, ticker, mid, y1, cutoff), gold.cell(o, ticker, mid, y2, cutoff)
        flags = []
        it = {"metric": mid, "kind": kind, "from": f"FY{y1}", "to": f"FY{y2}"}
        if c1["outcome"] != "answer" or c2["outcome"] != "answer":
            it |= {"label": "expected_abstention", "outcomes": [c1["outcome"], c2["outcome"]]}
            items.append(it)
            continue
        it |= {"v1": c1["val"], "v2": c2["val"], "concepts": [_tags(c1), _tags(c2)]}
        if c1.get("fallback") or c2.get("fallback"):
            flags.append("scope_warning")
        for c in (c1, c2):
            for comp in ([c] if "fact" in c else c.get("components", [])):
                if comp["fact"]["earlier_values"]:
                    flags.append("superseded_value")
        if _tags(c1) != _tags(c2):
            it["label"] = "concept_change"
        else:
            it["label"] = size_label(kind, c1["val"], c2["val"], th)
            if kind == "amount" and c1["val"] > 0:
                it["percent_change"] = (c2["val"] - c1["val"]) / c1["val"] * 100
            elif kind == "ratio":
                it["pp_change"] = (c2["val"] - c1["val"]) * 100
        it["flags"] = sorted(set(flags))
        items.append(it)
    return items


def micro_case(o, ticker, y1, y2, metric):
    """A prior-year value as presented in the target filing vs as first reported."""
    t = target_filing(ticker, y2)
    first = gold.cell(o, ticker, metric, y1, target_filing(ticker, y1)["filed"])
    now = gold.cell(o, ticker, metric, y1, t["filed"])
    f, n = first["fact"], now["fact"]
    return {"ticker": ticker, "metric": metric, "period": f"FY{y1}", "target_filing": t,
            "first_reported": {"val": f["val"], "accession": f["accn"], "filed": f["filed"]},
            "as_presented_in_target": {"val": n["val"], "accession": n["accn"], "filed": n["filed"]},
            "label": "superseded_value" if f["val"] != n["val"] else "unchanged"}


def sensitivity(o):
    rows = []
    for name, (t, y1, y2, _split) in CASES.items():
        for large_a, large_r in ((5, 1), (10, 2), (15, 3)):
            for control_a, control_r in ((1, 0.25), (2, 0.5), (3, 1.0)):
                th = {"amount": (large_a, control_a), "ratio": (large_r, control_r)}
                c = Counter(i["label"] for i in label_case(o, t, y1, y2, th))
                rows.append((name, f"{large_a}% / {large_r}pp", f"{control_a}% / {control_r}pp", c))
    return rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--sensitivity", action="store_true")
    a = p.parse_args(argv)
    o = ontology.load()
    if a.sensitivity:
        labels = ["large_numeric_change", "gray_zone", "unchanged_control", "concept_change", "expected_abstention"]
        print(f"{'case':12s} {'large':>11s} {'control':>12s} " + " ".join(f"{x[:12]:>12s}" for x in labels))
        for name, large, control, c in sensitivity(o):
            print(f"{name:12s} {large:>11s} {control:>12s} " + " ".join(f"{c[x]:>12d}" for x in labels))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (t, y1, y2, split) in CASES.items():
        doc = {"case": name, "split": split, "ticker": t, "from": f"FY{y1}", "to": f"FY{y2}",
               "value_policy": "as_of_filing", "target_filing": target_filing(t, y2),
               "thresholds": THRESHOLDS, "items": label_case(o, t, y1, y2)}
        (OUT / f"{name}.numeric.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(name, dict(Counter(i["label"] for i in doc["items"])))
    for name, args in MICRO.items():
        doc = micro_case(o, *args)
        (OUT / f"{name}.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(name, doc["label"], doc["first_reported"]["val"], "->", doc["as_presented_in_target"]["val"])


if __name__ == "__main__":
    main()
