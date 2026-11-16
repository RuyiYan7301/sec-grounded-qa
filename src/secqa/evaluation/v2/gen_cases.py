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
    if v1 > 0:
        p = abs(v2 - v1) / v1 * 100
    elif v1 < 0 and v2 < 0:
        p = abs(v2 - v1) / abs(v1) * 100   # size only: no percentage change is reported
    elif v1 == 0:
        return "unchanged_control" if v2 == 0 else "large_numeric_change"
    else:
        return "large_numeric_change"      # negative to zero or positive: a sign change
    return "large_numeric_change" if p >= large else "unchanged_control" if p < control else "gray_zone"


LOSS_METRICS = {"gross_profit", "operating_income", "net_income", "eps_basic", "eps_diluted"}


def change_fields(metric, kind, v1, v2):
    """What a packet may state about a change. A percentage is given only for a positive base."""
    if kind == "ratio":
        return {"pp_change": (v2 - v1) * 100, "change_basis": "percentage_points"}
    out = {"absolute_change": v2 - v1, "percent_change": None}
    if v1 > 0:
        out |= {"percent_change": (v2 - v1) / v1 * 100, "change_basis": "percent"}
    elif v1 < 0 and v2 < 0:
        noun = "loss" if metric in LOSS_METRICS else "negative_value"
        out |= {"change_basis": "magnitude_only", "magnitude": abs(v2 - v1) / abs(v1) * 100,
                "direction": f"{noun}_narrowed" if abs(v2) < abs(v1) else f"{noun}_widened"}
    else:
        out |= {"change_basis": "sign_change" if (v1 < 0) != (v2 < 0) else "zero_base"}
    return out


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
            it |= change_fields(mid, kind, c1["val"], c2["val"])
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


def revision_controls(o):
    """Prior-year values as presented in each target 10-K vs as first reported.

    Stable values are negatives for revision detection. They are not cross-year unchanged
    controls and are scored separately (revision_false_positive_rate)."""
    rows = []
    targets = [(name, t, y1, y2) for name, (t, y1, y2, split) in CASES.items() if split == "test"]
    # AMD recast SG&A for both prior years presented in its FY2025 10-K
    targets += [("AMD_FY2025", "AMD", 2023, 2025), ("AMD_FY2025", "AMD", 2024, 2025)]
    for name, t, y1, y2 in targets:
        cutoff = target_filing(t, y2)["filed"]
        metrics = o["metrics"] if t != "AMD" else {"selling_general_administrative": o["metrics"]["selling_general_administrative"]}
        for mid, m in metrics.items():
            c = gold.cell(o, t, mid, y1, cutoff)
            if c["outcome"] != "answer":
                continue
            f = c["fact"]
            row = {"target": name, "ticker": t, "metric": mid, "period": f"FY{y1}", "concept": f["tag"],
                   "as_presented": {"val": f["val"], "accession": f["accn"], "filed": f["filed"]}}
            # The first observed annual-report row for the same concept and period, filed on or before the
            # target filing. "stable" needs a prior observation equal to the value as presented; if the first
            # observation is the target filing itself there is nothing to compare (no_prior_observation, not
            # in the stability denominator).
            first = gold._rows(t, f["tag"], y1, m["period_type"], cutoff)[0]
            row["first_reported"] = {"val": first["val"], "accession": first["accn"], "filed": first["filed"]}
            if f["earlier_values"]:
                e = f["earlier_values"][0]
                assert e["accn"] == first["accn"] and e["val"] == first["val"], (t, mid, y1)
                row["label"] = "stock_split_recast" if m.get("split_sensitive") else "accounting_recast"
            elif first["accn"] == f["accn"]:
                row["label"] = "no_prior_observation"
            else:
                assert first["val"] == f["val"], (t, mid, y1)
                row["label"] = "stable"
            rows.append(row)
    return rows


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
    rc = revision_controls(o)
    doc = {"description": "Prior-year values as presented in the target 10-K vs as first reported. "
                          "Scored separately from cross-year unchanged controls.", "value_policy": "as_of_filing",
           "items": rc}
    (OUT / "revision_stability_controls.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8",
                                                          newline="\n")
    print("revision controls", dict(Counter((r["target"], r["label"]) for r in rc)))
    for name, args in MICRO.items():
        doc = micro_case(o, *args)
        (OUT / f"{name}.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(name, doc["label"], doc["first_reported"]["val"], "->", doc["as_presented_in_target"]["val"])


if __name__ == "__main__":
    main()
