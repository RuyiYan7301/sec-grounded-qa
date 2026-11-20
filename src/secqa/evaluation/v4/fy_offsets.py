"""v0.4 2c fix 1: per-filer fiscal-year label offsets (docs/v0.4-2c-plan.md).

The engine labels a fiscal year by the calendar year it ends in. A few filers name theirs differently
(Home Depot's "fiscal 2024" ended 2 February 2025). The filer's own label is the DEI fiscal-year focus on
the rows filed with each 10-K, already collected in results/v0.4/coverage/labels.json. A filer gets an
offset when at least MIN_AGREE of its 10-Ks reported since 2018 disagree with the engine label by that
same nonzero amount; one-off disagreements (CRM, 1 of 9) are left alone.

    python -m secqa.evaluation.v4.fy_offsets    # writes data/universe/fy_label_offsets.json
"""
import json
from collections import Counter

from ... import config

LABELS = config.REPO_ROOT / "results" / "v0.4" / "coverage" / "labels.json"
OUT = config.REPO_ROOT / "data" / "universe" / "fy_label_offsets.json"
SINCE = "2018-01-01"
MIN_AGREE = 5


def derive(labels):
    offsets, evidence = {}, {}
    for ticker, v in sorted(labels.items()):
        diffs = Counter(k["own_fy"] - k["engine_fy"] for k in v["tenks"]
                        if k["own_fy"] is not None and k["report_date"] >= SINCE)
        nonzero = {d: n for d, n in diffs.items() if d}
        if not nonzero:
            continue
        evidence[ticker] = {str(d): n for d, n in sorted(diffs.items())}
        d, n = max(nonzero.items(), key=lambda kv: kv[1])
        if n >= MIN_AGREE and n > diffs.get(0, 0):
            offsets[ticker] = d
    return offsets, evidence


def main():
    offsets, evidence = derive(json.loads(LABELS.read_text(encoding="utf-8")))
    OUT.write_text(json.dumps({"rule": f"own DEI fy minus engine label, 10-Ks reported since {SINCE}, "
                                       f"applied when at least {MIN_AGREE} agree and outnumber zero",
                               "offsets": offsets, "evidence": evidence}, indent=1) + "\n", encoding="utf-8")
    print(offsets, evidence)


if __name__ == "__main__":
    main()
