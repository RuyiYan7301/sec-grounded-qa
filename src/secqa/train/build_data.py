"""v0.4 step 2 data (docs/v0.4-plan.md sections 3 and 3b): training, validation, GRPO prompts and test set 2.

    python -m secqa.train.build_data sft   --seed 2613   # data/train/v0.4/sft_{train,val}.json
    python -m secqa.train.build_data grpo  --seed 2612   # data/train/v0.4/grpo_prompts.json
    python -m secqa.train.build_data test2 --seed 2611   # data/eval/v0.4/qa_heldout_2611.json (test set 2)

Every item has the frozen generator's fields (question, gold_plan, gold_outcome, gold_result, tolerance,
required_warnings), so the executor's correctness check applies to any of them. Answer questions come from
the frozen generator (evaluation/v2/gen_qa.sample + gold.py) with its company list and template table
replaced:
  - train / validation / GRPO: train-half templates plus Claude Haiku paraphrases of them
    (data/train/v0.4/paraphrases_haiku.json); a paraphrase equal to a test-half template after
    normalisation is dropped; companies from the train or validation split only;
  - test set 2: test-half templates only, the 15 new test companies, same mix as the 2b test (160 items).
Refusal questions are made by rule on the same companies: metrics the ontology lists as out of scope,
advice / forecast / judgement requests, fiscal years outside FY2019-FY2025, and per-share values compared
across companies (the ontology does not allow cross-company comparison for per-share metrics). A share of
answer plans use cells the company does not report (gold outcome not_reported: the planner should still
write the plan; the executor reports the absence).
"""
import argparse
import json
import random
import re
from collections import Counter
from functools import lru_cache

from .. import config, universe
from ..evaluation.v2 import gen_qa, gold
from .splits import load as load_splits

DIR = config.REPO_ROOT / "data" / "train" / "v0.4"
PARA = DIR / "paraphrases_haiku.json"
MIX = {"fact_lookup": 40, "multi_period_lookup": 16, "cross_company_comparison": 20, "absolute_change": 20,
       "percent_change": 24, "percentage_point_change": 16, "ratio": 12, "restated_value_lookup": 12}
YEARS = tuple(range(2019, 2026))
SHORT_SYSTEM = "Return the typed plan for the question as one JSON object."
OUT_OF_ONTOLOGY = ["EBITDA", "adjusted EBITDA", "EBIT", "non-GAAP earnings per share", "adjusted net income",
                   "total debt", "total borrowings", "segment revenue", "backlog",
                   "remaining performance obligations", "market capitalization", "year-end share price",
                   "price-to-earnings ratio", "customer acquisition cost", "fourth-quarter revenue",
                   "third-quarter operating income", "same-store sales growth"]
PER_SHARE = ["eps_basic", "eps_diluted", "weighted_shares_basic", "weighted_shares_diluted"]
FORECAST_METRICS = ["revenue", "net_income", "eps_diluted", "operating_income", "free_cash_flow"]
REASONS = {"out_of_ontology": "The requested metric is not in the supported metric list.",
           "unsupported": "Investment advice, forecasts and opinions are not answered from filings.",
           "out_of_range": "The fiscal year is outside FY2019-FY2025.",
           "unsupported_operation": "Per-share values are not compared across companies."}
PLAN_KEYS = ("intent", "metric", "companies", "periods")


def norm(s):
    return re.sub(r"[^a-z0-9{} ]", "", s.lower()).strip()


@lru_cache(maxsize=1)
def _v02_test_questions():
    q = json.loads((config.EVAL_DIR / "v0.2" / "qa_test.json").read_text(encoding="utf-8"))
    return [norm(i["question"]) for i in q]


def _hits_v02_test(s):
    """True if the template, with any text in its placeholders, can produce a v0.2 test question."""
    pat = re.escape(norm(s))
    pat = re.sub(r"\\{\w+\\}|{\w+}", ".+", pat)
    rx = re.compile("^" + pat + "$")
    return any(rx.match(q) for q in _v02_test_questions())


def templates(kind):
    """kind: 'train' (train half + paraphrases) or 'test' (test half only).

    Paraphrases are dropped if they equal a test-half template after normalisation, if their placeholders
    differ from the original's, or if they can produce a question of the frozen v0.2 test set (test set 1).
    """
    sp = load_splits()["templates"]
    if kind == "test":
        return {k: list(v) for k, v in sp["test"].items()}, {}
    test_norm = {norm(s) for v in sp["test"].values() for s in v}
    train_tpl = {s for v in sp["train"].values() for s in v}
    para = json.loads(PARA.read_text(encoding="utf-8"))
    dropped = Counter()

    def keep(k, e, s):
        if s in train_tpl:
            return True                     # train-half templates themselves (see plan clarification)
        why = ("test_template" if norm(s) in test_norm else
               "placeholders" if set(re.findall(r"{\w+}", s)) != set(re.findall(r"{\w+}", e["original"])) else
               "v02_test_question" if _hits_v02_test(s) else None)
        if why:
            dropped[(k, why)] += 1
        return why is None

    ans = {k: sorted({s for e in entries for s in [e["original"]] + e["paraphrases"] if keep(k, e, s)})
           for k, entries in para["answer_templates"].items()}
    ref = {k: sorted({s for e in entries for s in [e["original"]] + e["paraphrases"] if keep(k, e, s)})
           for k, entries in para["refusal_templates"].items()}
    if dropped:
        print("dropped templates", {f"{k}/{w}": n for (k, w), n in dropped.items()})
    return ans, ref


def _setup(tickers, tpl):
    names = universe.short_names()
    gold._raw = lru_cache(maxsize=1)(gold._raw.__wrapped__)
    gen_qa.NAMES, gen_qa.TICKERS, gen_qa.DEV_TICKERS = {t: names[t] for t in tickers}, list(tickers), ()
    gen_qa.T = dict(tpl)
    gen_qa.NOT_MEANINGFUL = {"test": 6, "handwritten": 0, "dev": 0}


def _answers(tickers, tpl, rng, rounds, mix=MIX, multi_fixed=False):
    """rounds x mix of answer items. Multi-period items are drawn per three-year window."""
    _setup(tickers, tpl)
    gen_qa.YEARS = YEARS
    pools = gen_qa.Pools()
    items = []
    for _ in range(rounds):
        gen_qa.YEARS = YEARS
        gen_qa.T = dict(tpl)
        gen_qa.NOT_MEANINGFUL = {"test": 6, "handwritten": 0, "dev": 0}
        items += gen_qa.sample("test", "generated", {**mix, "multi_period_lookup": 0}, rng, pools, set())
        gen_qa.NOT_MEANINGFUL = {"test": 0, "handwritten": 0, "dev": 0}
        windows = [(2023, 2024, 2025)] if multi_fixed else [(w, w + 1, w + 2) for w in range(2019, 2024)]
        per = {}
        for i in range(mix["multi_period_lookup"]):
            per[windows[i % len(windows)]] = per.get(windows[i % len(windows)], 0) + 1
        for win, n in per.items():
            gen_qa.YEARS = win
            ys = {"{y1}": str(win[0]), "{y2}": str(win[1]), "{y3}": str(win[2])}
            t2 = dict(tpl)
            for k in ("multi_period_lookup", "multi_period_lookup_instant"):
                t2[k] = [_sub(s, ys) for s in tpl[k]]
            gen_qa.T = t2
            items += gen_qa.sample("test", "generated", {k: (n if k == "multi_period_lookup" else 0) for k in mix},
                                   rng, pools, set())
    gen_qa.YEARS, gen_qa.T = YEARS, dict(tpl)
    return items, pools


def _sub(s, d):
    for k, v in d.items():
        s = s.replace(k, v)
    return s


def _not_reported(tickers, pools, tpl, rng, n):
    names = universe.short_names()
    cells = [k for k, c in pools.cells.items() if c["outcome"] == "not_reported" and k[1] in gen_qa.ONTO["metrics"]
             and k[0] in tickers]
    out = []
    for t, m, y in rng.sample(cells, min(n, len(cells))):
        inst = gen_qa.ONTO["metrics"][m]["period_type"] == "instant"
        tp = rng.choice(tpl["fact_lookup_instant" if inst else "fact_lookup"])
        out.append(_refusal_item(tp.format(co=names[t], m=gen_qa._phrase(m), y=y), "not_reported",
                                 plan={"intent": "fact_lookup", "metric": m, "companies": [t], "periods": [f"FY{y}"]}))
    return out


def _refusal_item(q, outcome, plan=None):
    return {"question": q, "layer": "rule", "gold_plan": plan, "gold_outcome": outcome, "gold_cells": [],
            "gold_result": {"outcome": outcome}, "required_warnings": [], "advisory_warnings": [], "tolerance": None}


def _refusals(tickers, ans_tpl, ref_tpl, rng, n_each):
    names = universe.short_names()
    co = lambda: names[rng.choice(tickers)]
    out = []
    for _ in range(n_each):
        out.append(_refusal_item(rng.choice(ref_tpl["out_of_ontology"]).format(
            co=co(), x=rng.choice(OUT_OF_ONTOLOGY), y=rng.choice(YEARS)), "out_of_ontology"))
    kinds = ["unsupported_advice", "unsupported_forecast", "unsupported_judgement"]
    for i in range(n_each):
        k = kinds[i % 3]
        out.append(_refusal_item(rng.choice(ref_tpl[k]).format(
            co=co(), y=rng.choice(YEARS), yf=rng.choice([2026, 2027, 2028]),
            m=gen_qa._phrase(rng.choice(FORECAST_METRICS))), "unsupported"))
    bad_years = list(range(2010, 2019)) + [2026, 2027]
    for i in range(n_each):
        m = rng.choice([m for m in gen_qa.ONTO["metrics"] if m not in PER_SHARE])
        inst = gen_qa.ONTO["metrics"][m]["period_type"] == "instant"
        if i % 2 == 0:
            q = rng.choice(ans_tpl["fact_lookup_instant" if inst else "fact_lookup"]).format(
                co=co(), m=gen_qa._phrase(m), y=rng.choice(bad_years))
        else:
            y = rng.choice([2011, 2014, 2016, 2018, 2027])
            q = rng.choice(ans_tpl["absolute_change"]).format(co=co(), m=gen_qa._phrase(m), y1=y - 1, y2=y)
        out.append(_refusal_item(q, "out_of_range"))
    for _ in range(n_each):
        a, b = rng.sample(tickers, 2)
        out.append(_refusal_item(rng.choice(ref_tpl["cross_company_per_share"]).format(
            co=names[a], co2=names[b], m=gen_qa._phrase(rng.choice(PER_SHARE)), y=rng.choice(YEARS)),
            "unsupported_operation"))
    return out


def target(it):
    """The plan the planner should write for an item (schema keys only)."""
    if it["gold_plan"]:
        return {k: it["gold_plan"][k] for k in PLAN_KEYS}
    return {"refuse": it["gold_outcome"], "reason": REASONS[it["gold_outcome"]]}


def _finish(items, prefix, rng):
    rng.shuffle(items)
    seen, out = set(), []
    for it in items:
        if it["question"] in seen:
            continue
        seen.add(it["question"])
        it["id"] = f"{prefix}-{len(out) + 1:05d}"
        it["target_plan"] = target(it)
        out.append(it)
    return out


def make(tickers, rng, rounds, prefix, refusal_share=0.15, nr_share=0.05):
    ans_tpl, ref_tpl = templates("train")
    answers, pools = _answers(tickers, ans_tpl, rng, rounds)
    n = len(answers)
    nr = _not_reported(tickers, pools, ans_tpl, rng, int(n * nr_share))
    ref = _refusals(tickers, ans_tpl, ref_tpl, rng, int(n * refusal_share / 4))
    return _finish(answers + nr + ref, prefix, rng)


def _write(path, items, meta):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"meta": meta, "items": items}, indent=1, default=str), encoding="utf-8")
    c = Counter((it["gold_plan"] or {}).get("intent") or it["gold_outcome"] for it in items)
    print(path.name, len(items), dict(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["sft", "grpo", "test2"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--rounds", type=int, default=20)
    a = ap.parse_args()
    universe.activate()
    sp = load_splits()["companies"]
    rng = random.Random(a.seed)
    meta = {"seed": a.seed, "what": a.what, "system_prompt": SHORT_SYSTEM, "plan": "docs/v0.4-plan.md section 3"}
    if a.what == "sft":
        _write(DIR / "sft_train.json", make(sp["train"], rng, a.rounds, "SFT"), {**meta, "companies": "train"})
        _write(DIR / "sft_val.json", make(sp["validation"], rng, 2, "VAL"), {**meta, "companies": "validation"})
    elif a.what == "grpo":
        _write(DIR / "grpo_prompts.json", make(sp["train"], rng, 6, "GRPO"), {**meta, "companies": "train"})
    else:
        tpl, _ = templates("test")
        items, _ = _answers(sp["test_new"], tpl, rng, 1, multi_fixed=True)
        for i, it in enumerate(items, 1):
            it["id"] = f"H-{a.seed}-{i:03d}"
            it["target_plan"] = target(it)
        _write(config.EVAL_DIR / "v0.4" / f"qa_heldout_{a.seed}.json", items,
               {**meta, "companies": "test_new", "templates": "test half"})


if __name__ == "__main__":
    main()
