"""v0.4 generalization test, part 2b: generated questions on the new companies (docs/v0.4-plan.md).

    python -m secqa.evaluation.v4.gen_qa_v4 --seed 2606 --out qa_gen_2606.json     # the 2b test set
    python -m secqa.evaluation.v4.gen_qa_v4 --seed 2608 --out qa_gen_2608.json     # 2c re-measure (later)

The frozen v0.2 generator (evaluation/v2/gen_qa.py) is reused unchanged: same templates, gold builder,
tolerances and warnings. Only its module-level company list, names and years are set to the v0.4 universe
(new companies only, fiscal years 2019-2025), and the intent counts are doubled to 160 items.
Multi-period questions keep the template's fixed wording (FY2023 through FY2025), so they are drawn with
those three years. gold._raw keeps one company in memory at a time (16 GB machine).
"""
import argparse
import json
import random
from functools import lru_cache

from ... import config, universe
from ..v2 import gen_qa, gold

OUT = config.EVAL_DIR / "v0.4"
MIX = {"fact_lookup": 40, "multi_period_lookup": 16, "cross_company_comparison": 20, "absolute_change": 20,
       "percent_change": 24, "percentage_point_change": 16, "ratio": 12, "restated_value_lookup": 12}
NOT_MEANINGFUL = 6


def _with_offsets(rule):
    path = config.REPO_ROOT / "data" / "universe" / "fy_label_offsets.json"
    offsets = json.loads(path.read_text(encoding="utf-8"))["offsets"] if path.exists() else {}

    def fiscal_year_of(ticker, end):
        return rule(ticker, end) + offsets.get(ticker, 0)
    return fiscal_year_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tickers", default="new", help="'new' (77 new filers) or a comma list")
    a = ap.parse_args()
    universe.activate()
    names = universe.short_names()
    tickers = [t for t in universe.filers() if t not in universe.ORIGINAL] if a.tickers == "new" else a.tickers.split(",")
    gold._raw = lru_cache(maxsize=1)(gold._raw.__wrapped__)
    # 2c fix 1: the frozen gold builder keeps its own fiscal-year rule (v0.2 manifest hash); the per-filer
    # label offsets (data/universe/fy_label_offsets.json, read directly, not through facts.py) are added here.
    gold.fiscal_year_of = _with_offsets(gold.fiscal_year_of)
    gen_qa.NAMES, gen_qa.TICKERS, gen_qa.DEV_TICKERS = {t: names[t] for t in tickers}, tickers, ()
    gen_qa.NOT_MEANINGFUL = {"test": NOT_MEANINGFUL, "handwritten": 0, "dev": 0}
    rng = random.Random(a.seed)
    gen_qa.YEARS = tuple(range(2019, 2026))
    pools7 = gen_qa.Pools()
    used = set()
    items = gen_qa.sample("test", "generated", {**MIX, "multi_period_lookup": 0}, rng, pools7, used)
    gen_qa.YEARS = (2023, 2024, 2025)
    gen_qa.NOT_MEANINGFUL = {"test": 0, "handwritten": 0, "dev": 0}
    pools3 = gen_qa.Pools.__new__(gen_qa.Pools)
    pools3.cells = {k: v for k, v in pools7.cells.items() if k[2] in gen_qa.YEARS}
    multi = gen_qa.sample("test", "generated", {k: (MIX[k] if k == "multi_period_lookup" else 0) for k in MIX},
                          rng, pools3, used)
    for i, it in enumerate(items + multi, 1):
        it["id"] = f"V4-{a.seed}-{i:03d}"
    items = items + multi
    gen_qa.interpretation_warnings(items)
    OUT.mkdir(parents=True, exist_ok=True)
    gen_qa._dump(OUT / a.out, items)
    from collections import Counter
    print(len(items), dict(Counter(i["gold_plan"]["intent"] for i in items)))
    print("companies", len({t for i in items for t in i["gold_plan"]["companies"]}))


if __name__ == "__main__":
    main()
