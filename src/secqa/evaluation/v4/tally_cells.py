"""v0.4 2a: tally the model review of the 200 sampled cells (results/v0.4/accuracy/review_*.csv).

    python -m secqa.evaluation.v4.tally_cells      # writes results/v0.4/accuracy/tally.json

Correct rate on answer cells with a Wilson 95% interval, by metric and sector; error list with the concept
the engine used (from key.json, which reviewers did not see); not_reported cells: share truly absent.
`cannot_verify` is reported separately and excluded from the denominator, and also counted as wrong in a
worst-case line.
"""
import csv
import json
import math
from collections import Counter, defaultdict

from ... import config, universe

DIR = config.REPO_ROOT / "results" / "v0.4" / "accuracy"


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def run():
    key = json.loads((DIR / "key.json").read_text(encoding="utf-8"))
    sector = {t: f["sector"] for t, f in
              json.loads(universe.MANIFEST.read_text(encoding="utf-8"))["filers"].items()}
    rows = []
    for p in sorted(DIR.glob("review_*.csv")):
        with open(p, encoding="utf-8", newline="") as f:
            rows += [{**r, "reviewer_file": p.name} for r in csv.DictReader(f)]
    seen = {r["id"] for r in rows}
    missing = sorted(set(key) - seen)
    ans = [r for r in rows if r["id"].startswith("A")]
    nr = [r for r in rows if r["id"].startswith("N")]
    oc = Counter(r["outcome"] for r in ans)
    verifiable = [r for r in ans if r["outcome"] != "cannot_verify"]
    k = sum(r["outcome"] == "correct" for r in verifiable)
    by_metric, by_sector = defaultdict(Counter), defaultdict(Counter)
    for r in verifiable:
        kk = key[r["id"]]
        by_metric[kk["metric"]][r["outcome"] == "correct"] += 1
        by_sector[sector[kk["ticker"]]][r["outcome"] == "correct"] += 1
    errors = [{**r, **{f"engine_{x}": key[r["id"]][x] for x in ("ticker", "metric", "fy", "concept", "use", "value")}}
              for r in ans if r["outcome"] not in ("correct",)]
    nr_oc = Counter(r["outcome"] for r in nr)
    nr_ver = [r for r in nr if r["outcome"] != "cannot_verify"]
    present = [{**r, **{f"engine_{x}": key[r["id"]][x] for x in ("ticker", "metric", "fy")}}
               for r in nr if r["outcome"] == "present"]
    out = {
        "reviewer": "Claude sub-agents (model review, not human), one per packet, no access to engine output",
        "missing_ids": missing,
        "answer": {"n": len(ans), "outcomes": dict(oc), "verifiable": len(verifiable), "correct": k,
                   "rate": round(k / len(verifiable), 3) if verifiable else None, "wilson95": wilson(k, len(verifiable)),
                   "worst_case_rate": round(k / len(ans), 3) if ans else None,
                   "by_metric": {m: [c[True], c[True] + c[False]] for m, c in sorted(by_metric.items())},
                   "by_sector": {s: [c[True], c[True] + c[False]] for s, c in sorted(by_sector.items())}},
        "not_reported": {"n": len(nr), "outcomes": dict(nr_oc),
                         "absent_rate": round(nr_oc["absent"] / len(nr_ver), 3) if nr_ver else None,
                         "wilson95": wilson(nr_oc["absent"], len(nr_ver))},
        "errors": errors, "present_but_not_reported": present,
    }
    (DIR / "tally.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("errors", "present_but_not_reported")}, indent=1))
    for e in errors:
        print("ERR", e["id"], e["outcome"], e["engine_ticker"], e["engine_metric"], e["engine_fy"], e["engine_concept"],
              e["engine_value"], "|", e["filing_value"], "|", e["line_label"], "|", e["note"])
    for e in present:
        print("PRESENT", e["id"], e["engine_ticker"], e["engine_metric"], e["engine_fy"], "|", e["filing_value"], "|",
              e["line_label"], "|", e["note"])


if __name__ == "__main__":
    run()
