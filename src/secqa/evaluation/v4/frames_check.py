"""v0.4 generalization test, part 2a: cross-check against the SEC frames API (docs/v0.4-plan.md).

    python -m secqa.evaluation.v4.frames_check     # writes results/v0.4/frames/frames_check.json

For six metrics (revenue, operating income, net income, total assets, operating cash flow, diluted EPS),
every filer, fiscal years 2022-2024: take the concept and period the resolver chose (coverage cells.jsonl),
find the same filer, concept and period (same start and end dates) in the frames API, and compare values.
Frames choose one fact per filer and calendar period by their own rules (the latest filed, the period
closest to the calendar), so a period that is not in any frame is listed as `no_frame`, not as an error.
Agreement: relative difference <= 0.5%.
"""
import json
from collections import Counter
from datetime import date

from ... import config, edgar
from .sample_cells import CELLS

METRICS = ("revenue", "operating_income", "net_income", "total_assets", "operating_cash_flow", "eps_diluted")
YEARS = (2022, 2023, 2024)
OUT = config.REPO_ROOT / "results" / "v0.4" / "frames"
TOL = 0.005


def _frame(tag, unit, period):
    name = f"frames_{tag}_{unit.replace('/', '-')}_{period}.json"
    url = f"https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/{unit}/{period}.json"
    try:
        return edgar._cached(name, url)
    except Exception as e:  # a concept with no frame for that period (404)
        return {"error": str(e), "data": []}


def _periods(end, instant):
    """Calendar frames that could hold a period ending on `end`."""
    y = end.year
    if instant:
        return [f"CY{yy}Q{q}I" for yy in (y - 1, y) for q in (1, 2, 3, 4)]
    return [f"CY{yy}" for yy in (y - 1, y, y + 1)]


def run():
    edgar.ALLOW_FETCH = True
    from ... import universe
    filers = universe.filers()
    cells = [json.loads(x) for x in CELLS.read_text(encoding="utf-8").splitlines() if x.strip()]
    rows, n = [], Counter()
    for c in cells:
        if c["metric"] not in METRICS or c["fy"] not in YEARS or c["status"] not in ("resolved", "fallback_with_warning"):
            continue
        end = date.fromisoformat(c["period_end"])
        instant = c["metric"] == "total_assets"
        cik = filers[c["ticker"]]
        hit = None
        for p in _periods(end, instant):
            for d in _frame(c["concept"], c["unit"], p).get("data", []):
                if d["cik"] == cik and d["end"] == c["period_end"]:
                    hit = {**d, "frame": p}
                    break
            if hit:
                break
        if hit is None:
            out = "no_frame"
        else:
            rel = abs(hit["val"] - c["value"]) / max(abs(c["value"]), 1e-9)
            out = "agree" if rel <= TOL else "disagree"
        n[out] += 1
        rows.append({"ticker": c["ticker"], "metric": c["metric"], "fy": c["fy"], "concept": c["concept"],
                     "value": c["value"], "period_end": c["period_end"], "original": c["original"],
                     "result": out, "frame": hit and {k: hit[k] for k in ("frame", "val", "accn", "end")}})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frames_check.json").write_text(json.dumps({"tolerance": TOL, "counts": dict(n), "rows": rows},
                                                      indent=1), encoding="utf-8")
    print(dict(n))
    for r in rows:
        if r["result"] == "disagree":
            print("DISAGREE", r["ticker"], r["metric"], r["fy"], r["concept"], r["value"], r["frame"])


if __name__ == "__main__":
    run()
