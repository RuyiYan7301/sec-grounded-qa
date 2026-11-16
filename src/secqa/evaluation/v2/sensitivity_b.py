"""Part B threshold sensitivity table: display only.

    python -m secqa.evaluation.v2.sensitivity_b     # writes results/v0.2/partB_threshold_sensitivity.{json,md}

The pre-registered thresholds stay 10% (amounts: currency, shares, EPS) and 2 pp (ratios); this table only
shows how the size labels of each case would move at 5% / 10% / 15% and at 1 / 2 / 3 pp, so it is visible
whether the chosen cut happens to sit at a convenient place. It is never used to change the thresholds.

- The amount threshold acts only on amount items, the pp threshold only on ratio items; the control cut
  (2% / 0.5 pp) is held fixed.
- Negative bases keep the magnitude-only size, with no percentage (gen_cases.size_label).
- Labels that do not depend on size (expected_abstention, concept_change) are counted once and do not move.
- Read from the committed case files, so the table matches the gold exactly.
"""
import json
from collections import Counter

from ... import config
from . import gen_cases

CASES_DIR = config.EVAL_DIR / "v0.2" / "cases"
OUT = config.REPO_ROOT / "results" / "v0.2"
SIZE = ("large_numeric_change", "gray_zone", "unchanged_control")
AMOUNT_CUTS, RATIO_CUTS = (5.0, 10.0, 15.0), (1.0, 2.0, 3.0)
CONTROL = {"amount": gen_cases.THRESHOLDS["amount"][1], "ratio": gen_cases.THRESHOLDS["ratio"][1]}


def table():
    rows = []
    for name in gen_cases.CASES:
        doc = json.loads((CASES_DIR / f"{name}.numeric.json").read_text(encoding="utf-8"))
        fixed = Counter(i["label"] for i in doc["items"] if i["label"] not in SIZE)
        sized = [i for i in doc["items"] if i["label"] in SIZE]
        for kind, cuts in (("amount", AMOUNT_CUTS), ("ratio", RATIO_CUTS)):
            items = [i for i in sized if i["kind"] == kind]
            for cut in cuts:
                th = dict(gen_cases.THRESHOLDS)
                th[kind] = (cut, CONTROL[kind])
                c = Counter(gen_cases.size_label(kind, i["v1"], i["v2"], th) for i in items)
                prereg = cut == gen_cases.THRESHOLDS[kind][0]
                if prereg:   # the committed labels must be reproduced at the pre-registered cut
                    assert c == Counter(i["label"] for i in items), (name, kind)
                rows.append({"case": name, "split": doc["split"], "kind": kind,
                             "large_cut": f"{cut:g}%" if kind == "amount" else f"{cut:g} pp",
                             "pre_registered": prereg, "n_items": len(items), **{k: c[k] for k in SIZE}})
        rows.append({"case": name, "split": doc["split"], "kind": "not size-based", "large_cut": "-",
                     "pre_registered": True, "n_items": sum(fixed.values()), **dict(fixed)})
    return rows


def main():
    rows = table()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "partB_threshold_sensitivity.json").write_text(json.dumps(
        {"note": "display only; the pre-registered thresholds (10% amounts, 2 pp ratios; controls 2% / 0.5 pp) "
                 "are not changed by this table", "rows": rows}, indent=1) + "\n", encoding="utf-8", newline="\n")
    lines = ["# Part B threshold sensitivity (display only)", "",
             "Pre-registered: 10% for amounts, 2 pp for ratios; control cut fixed at 2% / 0.5 pp. "
             "This table is not used to change them. Negative bases are sized by magnitude only.", "",
             "| case | split | kind | large cut | n | large | gray | unchanged | other labels |",
             "|---|---|---|---|---:|---:|---:|---:|---|"]
    for r in rows:
        other = ", ".join(f"{k} {v}" for k, v in r.items() if k not in
                          ("case", "split", "kind", "large_cut", "pre_registered", "n_items", *SIZE) and v)
        cut = f"**{r['large_cut']}**" if r["pre_registered"] and r["kind"] != "not size-based" else r["large_cut"]
        lines.append(f"| {r['case']} | {r['split']} | {r['kind']} | {cut} | {r['n_items']} | "
                     f"{r.get('large_numeric_change', '')} | {r.get('gray_zone', '')} | {r.get('unchanged_control', '')} | {other} |")
    (OUT / "partB_threshold_sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
