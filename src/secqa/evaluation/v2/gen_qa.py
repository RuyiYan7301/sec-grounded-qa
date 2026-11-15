"""Generate part A of the v0.2 benchmark (numeric QA) from the frozen ontology and the raw data.

    python -m secqa.evaluation.v2.gen_qa      # writes data/eval/v0.2/qa_{test,dev}.json + handwritten plans

Same seed, ontology and snapshot -> byte-identical files. Gold values come from gold.py (raw
companyfacts), never from the system's fact store.

Split by company: dev uses Cisco and Oracle only, test the other six, so dev and test share no
company and no cell. Items are sampled per intent from the cells of their split.
"""
import json
import random
import re

from ... import config, ontology
from . import adversarial, gold

SEED = 2602
OUT = config.EVAL_DIR / "v0.2"
YEARS = (2023, 2024, 2025)
NAMES = {"AAPL": "Apple", "NVDA": "Nvidia", "MSFT": "Microsoft", "ORCL": "Oracle", "CSCO": "Cisco",
         "AVGO": "Broadcom", "INTC": "Intel", "AMD": "AMD"}
TICKERS = list(NAMES)
RATIOS = ["gross_margin", "operating_margin", "net_margin", "rd_intensity"]
DEV_TICKERS = ("CSCO", "ORCL")

# intent -> (test generated, test handwritten, dev generated, dev handwritten)
MIX = {
    "fact_lookup":              (20, 10, 8, 1),
    "multi_period_lookup":      (8, 4, 2, 0),
    "cross_company_comparison": (10, 5, 4, 1),
    "absolute_change":          (10, 5, 4, 1),
    "percent_change":           (12, 6, 5, 1),
    "percentage_point_change":  (8, 4, 3, 1),
    "ratio":                    (6, 3, 3, 0),
    "restated_value_lookup":    (6, 3, 0, 0),   # Cisco and Oracle have no revised values
}
# percent_change items with base <= 0 (Cisco and Oracle have none in FY2023-FY2024, so dev has none)
NOT_MEANINGFUL = {"test": 3, "handwritten": 1, "dev": 0}
OWNER_SHARE = 12                                            # handwritten test plans written by the owner

T = {
    "fact_lookup": ["What was {co}'s {m} in fiscal {y}?", "Report {co}'s {m} for fiscal year {y}.",
                    "How much was {co}'s {m} in FY{y}?"],
    "fact_lookup_instant": ["What was {co}'s {m} at the end of fiscal {y}?",
                            "Report {co}'s {m} as of the end of fiscal year {y}."],
    "multi_period_lookup": ["What was {co}'s {m} in each of fiscal 2023, 2024 and 2025?",
                            "List {co}'s {m} for FY2023 through FY2025."],
    "multi_period_lookup_instant": ["What was {co}'s {m} at the end of each of fiscal 2023, 2024 and 2025?",
                                    "List {co}'s {m} at each fiscal year end from FY2023 through FY2025."],
    "cross_company_comparison": ["Compare {co}'s and {co2}'s {m} for fiscal {y}.",
                                 "Which was larger in fiscal {y}, {co}'s or {co2}'s {m}, and by how much?"],
    "absolute_change": ["By how much did {co}'s {m} change from fiscal {y1} to fiscal {y2}?",
                        "What was the dollar change in {co}'s {m} between FY{y1} and FY{y2}?"],
    "percent_change": ["By what percentage did {co}'s {m} change from fiscal {y1} to fiscal {y2}?",
                       "What was the year-over-year percent change in {co}'s {m} in fiscal {y2}?"],
    "percentage_point_change": ["By how many percentage points did {co}'s {m} change from fiscal {y1} to fiscal {y2}?",
                                "How did {co}'s {m} move between FY{y1} and FY{y2}, in percentage points?"],
    "ratio": ["What was {co}'s {m} in fiscal {y}?", "Calculate {co}'s {m} for FY{y}."],
    "restated_value_lookup": ["What did {co} originally report as its {m} for fiscal {y}, and what is the figure now?",
                              "Has {co}'s reported {m} for fiscal {y} been revised? Give the original and current figures."],
}


def split_of(ticker, metric=None):
    return "dev" if ticker in DEV_TICKERS else "test"


def tolerance(unit, kind):
    if kind in ("percent_change", "ratio"):
        return {"kind": "percentage_points", "abs": 0.1}
    if kind == "percentage_point_change":
        return {"kind": "percentage_points", "abs": 0.1}
    if unit == "USD/shares":
        return {"kind": "absolute", "abs": 0.01}
    return {"kind": "relative", "rel": 0.005}


def _evidence(c):
    """Gold cell for one resolved value (base or derived)."""
    if c["metric"] in ONTO["metrics"]:
        f = c["fact"]
        return [{"ticker": f["ticker"], "metric": c["metric"], "period": f"FY{f['fy']}", "concept": f["tag"],
                 "value": f["val"], "unit": f["unit"], "accession": f["accn"], "period_end": f["end"],
                 "use": c["use"]}]
    return [e for comp in c["components"] for e in _evidence(comp)]


def _phrase(metric):
    name = {**ONTO["metrics"], **ONTO["derived_metrics"]}[metric]["display_name"]
    return name if name.split()[0].isupper() else name[0].lower() + name[1:]   # keep "R&D ..." as is


def _warnings(cells):
    w = []
    if any(c.get("fallback") for c in cells):
        w.append("scope")
    return w


def _advisory(cells):
    """Warnings worth mentioning that do not decide correctness (scored separately)."""
    w = []
    for c in cells:
        for e in _evidence(c):
            f = gold.value(e["ticker"], e["concept"], int(e["period"][2:]),
                           ONTO["metrics"][e["metric"]]["period_type"])
            if f and f["earlier_values"]:
                w.append("restated")
    return sorted(set(w))


class Pools:
    """Answerable cells per split, from gold.py."""

    def __init__(self):
        self.cells = {}
        for t in TICKERS:
            for mid in list(ONTO["metrics"]) + list(ONTO["derived_metrics"]):
                for y in YEARS:
                    c = gold.cell(ONTO, t, mid, y)
                    self.cells[(t, mid, y)] = c

    def ok(self, t, mid, y, allow_fallback=False):
        c = self.cells[(t, mid, y)]
        return c["outcome"] == "answer" and (allow_fallback or not c.get("fallback"))

    def pairs(self, split, metrics):
        return [(t, mid) for t in TICKERS for mid in metrics if split_of(t) == split]


def _item(id_, layer, intent, plan, question, cells, result, unit):
    return {"id": id_, "layer": layer, "author": "template" if layer == "generated" else None,
            "question": question, "gold_plan": {"intent": intent, **plan},
            "gold_outcome": result["outcome"], "gold_cells": [e for c in cells for e in _evidence(c)],
            "gold_result": result, "required_warnings": _warnings(cells), "advisory_warnings": _advisory(cells),
            "tolerance": tolerance(unit, intent)}


def sample(split, layer, counts, rng, pools, used):
    """counts: intent -> n. `used` holds plan keys already taken (no duplicate plans across layers)."""
    base = [m for m in ONTO["metrics"]]
    currency = [m for m in base if ONTO["metrics"][m]["unit_type"] == "currency"]
    not_split = [m for m in base if not ONTO["metrics"][m].get("split_sensitive")]
    items = []

    def take(cands, n, key):
        cands = [c for c in cands if key(c) not in used]
        rng.shuffle(cands)
        out = cands[:n]
        used.update(key(c) for c in out)
        if len(out) < n:
            raise ValueError(f"{split}/{layer}: only {len(out)} of {n} candidates")
        return out

    def q(intent, **kw):
        if layer != "generated":
            return None
        tpl = T[intent]
        if kw.get("instant"):
            tpl = T[intent + "_instant"]
        kw.pop("instant", None)
        return rng.choice(tpl).format(**kw)

    n_id = [0]

    def nid():
        n_id[0] += 1
        return f"A-{split}-{layer[:3]}-{n_id[0]:03d}"

    pairs_base = pools.pairs(split, base + ["free_cash_flow"])
    # fact_lookup
    cands = [(t, m, y) for t, m in pairs_base for y in YEARS if pools.ok(t, m, y)]
    for t, m, y in take(cands, counts["fact_lookup"], lambda c: ("fact", *c)):
        c = pools.cells[(t, m, y)]
        inst = m in ONTO["metrics"] and ONTO["metrics"][m]["period_type"] == "instant"
        items.append(_item(nid(), layer, "fact_lookup", {"metric": m, "companies": [t], "periods": [f"FY{y}"]},
                           q("fact_lookup", co=NAMES[t], m=_phrase(m), y=y, instant=inst), [c],
                           {"outcome": "answer", "val": c["val"]}, c["unit"]))
    # multi_period_lookup
    cands = [(t, m) for t, m in pools.pairs(split, base) if all(pools.ok(t, m, y) for y in YEARS)]
    for t, m in take(cands, counts["multi_period_lookup"], lambda c: ("multi", *c)):
        cs = [pools.cells[(t, m, y)] for y in YEARS]
        items.append(_item(nid(), layer, "multi_period_lookup",
                           {"metric": m, "companies": [t], "periods": [f"FY{y}" for y in YEARS]},
                           q("multi_period_lookup", co=NAMES[t], m=_phrase(m),
                             instant=ONTO["metrics"][m]["period_type"] == "instant"), cs,
                           {"outcome": "answer", "vals": [c["val"] for c in cs]}, cs[0]["unit"]))
    # cross_company_comparison (per-share metrics excluded by the ontology)
    cands = []
    for m in not_split:
        ts = [t for t in TICKERS if split_of(t, m) == split]
        for i, t in enumerate(ts):
            for t2 in ts[i + 1:]:
                for y in YEARS:
                    if pools.ok(t, m, y) and pools.ok(t2, m, y):
                        cands.append((t, t2, m, y))
    picked = take(cands, counts["cross_company_comparison"], lambda c: ("cross", *c))
    for t, t2, m, y in picked:
        c1, c2 = pools.cells[(t, m, y)], pools.cells[(t2, m, y)]
        it = _item(nid(), layer, "cross_company_comparison", {"metric": m, "companies": [t, t2], "periods": [f"FY{y}"]},
                   q("cross_company_comparison", co=NAMES[t], co2=NAMES[t2], m=_phrase(m), y=y), [c1, c2],
                   {"outcome": "answer", "vals": [c1["val"], c2["val"]], "difference": c1["val"] - c2["val"]},
                   c1["unit"])
        from datetime import date
        e1, e2 = c1["fact"]["end"], c2["fact"]["end"]
        if abs((date.fromisoformat(e1) - date.fromisoformat(e2)).days) > 31:
            it["required_warnings"].append("period_mismatch")
        items.append(it)
    # two-period operations on consecutive years
    for intent, metrics in (("absolute_change", currency), ("percent_change", currency + ["eps_diluted"]),
                            ("percentage_point_change", RATIOS)):
        n = counts[intent]
        cands = [(t, m, y) for t, m in pools.pairs(split, metrics) for y in YEARS[1:]
                 if pools.ok(t, m, y - 1) and pools.ok(t, m, y)]
        chosen = []
        if intent == "percent_change":
            k = NOT_MEANINGFUL["dev" if split == "dev" else ("test" if layer == "generated" else "handwritten")]
            neg = [c for c in cands if pools.cells[(c[0], c[1], c[2] - 1)]["val"] <= 0]
            chosen = take(neg, k, lambda c, i=intent: (i, *c))
            cands = [c for c in cands if c not in neg]
            n -= k
        chosen += take(cands, n, lambda c, i=intent: (i, *c))
        for t, m, y in chosen:
            c1, c2 = pools.cells[(t, m, y - 1)], pools.cells[(t, m, y)]
            res = gold.change(c1["val"], c2["val"], intent)
            if res["outcome"] == "answer":   # percent and pp results are stated in percent units
                res["unit"] = {"absolute_change": c1["unit"], "percent_change": "percent",
                               "percentage_point_change": "pp"}[intent]
                if intent == "percent_change":
                    res["val"] *= 100
            items.append(_item(nid(), layer, intent, {"metric": m, "companies": [t], "periods": [f"FY{y - 1}", f"FY{y}"]},
                               q(intent, co=NAMES[t], m=_phrase(m), y1=y - 1, y2=y), [c1, c2], res, c1["unit"]))
    # ratio (single period)
    cands = [(t, m, y) for t, m in pools.pairs(split, RATIOS) for y in YEARS if pools.ok(t, m, y)]
    for t, m, y in take(cands, counts["ratio"], lambda c: ("ratio", *c)):
        c = pools.cells[(t, m, y)]
        items.append(_item(nid(), layer, "ratio", {"metric": m, "companies": [t], "periods": [f"FY{y}"]},
                           q("ratio", co=NAMES[t], m=_phrase(m), y=y), [c],
                           {"outcome": "answer", "val": c["val"] * 100, "unit": "percent"}, "ratio"))
    # restated_value_lookup: a value reported differently in an earlier 10-K. Every recast (non-split)
    # cell of the split is taken first; the rest are stock-split re-presentations.
    revised = [(t, m, y) for t, m in pools.pairs(split, base) for y in YEARS
               if pools.ok(t, m, y) and pools.cells[(t, m, y)]["fact"]["earlier_values"]]
    recast = [c for c in revised if c[1] in not_split]
    n = counts["restated_value_lookup"]
    chosen = take(recast, min(n, len([c for c in recast if ("restated", *c) not in used])), lambda c: ("restated", *c))
    chosen += take([c for c in revised if c[1] not in not_split], n - len(chosen), lambda c: ("restated", *c))
    for t, m, y in chosen:
        c = pools.cells[(t, m, y)]
        f = c["fact"]
        cause = "recast" if m in not_split else "stock_split"
        it = _item(nid(), layer, "restated_value_lookup",
                   {"metric": m, "companies": [t], "periods": [f"FY{y}"], "revision_cause": cause},
                   q("restated_value_lookup", co=NAMES[t], m=_phrase(m), y=y), [c],
                   {"outcome": "answer", "val": f["val"], "original_val": f["earlier_values"][0]["val"],
                    "original_accession": f["earlier_values"][0]["accn"]}, c["unit"])
        it["required_warnings"].append("restated")
        it["advisory_warnings"] = [w for w in it["advisory_warnings"] if w != "restated"]
        items.append(it)
    return items


def build():
    rng = random.Random(SEED)
    pools = Pools()
    used = set()
    out = {}
    for split in ("test", "dev"):
        col = 0 if split == "test" else 2
        gen = sample(split, "generated", {k: v[col] for k, v in MIX.items()}, rng, pools, used)
        hand = sample(split, "handwritten", {k: v[col + 1] for k, v in MIX.items()}, rng, pools, used)
        adv = adversarial.items(ONTO, split)
        out[split] = gen + hand + adv
    # handwritten test plans: OWNER_SHARE written by the owner, stratified by intent order
    hand = [i for i in out["test"] if i["layer"] == "handwritten"]
    owner = set(i["id"] for i in random.Random(SEED + 1).sample(hand, OWNER_SHARE))
    for i in out["test"] + out["dev"]:
        if i["layer"] == "handwritten":
            i["author"] = "codex_assisted" if i["id"] in owner else "claude_assisted"
    return out


INSTRUCTIONS = [
    "Write one natural-language question per plan, in the 'question' field. Leave everything else unchanged.",
    "Use only this file and data/metric_ontology.yaml. Do not look at any system output or gold value.",
    "Vary the wording: synonyms from aliases_allowed, the company's own line-item names, informal phrasing.",
    "The question must ask for exactly the plan: same company or companies, metric, fiscal years and operation.",
    "Say 'fiscal' (or FY) for the year; a bare calendar year changes the intended answer.",
    "If you use an interpreted alias (for example plain 'EPS'), keep it: the gold then requires the interpretation warning.",
    "Write these before any typed-engine code exists. Questions are not reworded later to suit a system.",
]
INTENT_WORDS = {
    "fact_lookup": "one value for one fiscal year",
    "multi_period_lookup": "the value in each of the listed fiscal years",
    "cross_company_comparison": "the value for each company in the same fiscal year, compared",
    "absolute_change": "the change in amount from the first to the second fiscal year",
    "percent_change": "the percentage change from the first to the second fiscal year",
    "percentage_point_change": "the change in percentage points from the first to the second fiscal year",
    "ratio": "the ratio for one fiscal year",
    "restated_value_lookup": "the originally reported figure and the current figure for that fiscal year",
}


def plan_sheet(items, author):
    """What a question author may see: the plan, in words, and nothing else."""
    rows = []
    for i in items:
        p = i["gold_plan"]
        m = {**ONTO["metrics"], **ONTO["derived_metrics"]}[p["metric"]]
        rows.append({"id": i["id"], "intent": p["intent"], "asks_for": INTENT_WORDS[p["intent"]],
                     "metric": p["metric"], "metric_name": m["display_name"],
                     "aliases_allowed": m["aliases"] + [a["alias"] for a in m.get("interpreted_aliases", [])],
                     "companies": [f"{NAMES[t]} ({t})" for t in p["companies"]], "periods": p["periods"],
                     "question": ""})
    return {"author": author, "instructions": INSTRUCTIONS, "plans": rows}


def _dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


ONTO = ontology.load()


PLAN_KEYS = ("intent", "metric", "companies", "periods")


def merge_questions(items, sheet):
    """Copy written questions from a plan sheet into the items. A plan that changed since the
    question was written is an error: the question would no longer match its gold."""
    by_id = {i["id"]: i for i in items}
    for row in sheet["plans"]:
        if not row["question"]:
            continue
        it = by_id[row["id"]]
        fresh = plan_sheet([it], sheet["author"])["plans"][0]
        if any(fresh[k] != row[k] for k in PLAN_KEYS):
            raise ValueError(f"{row['id']}: plan changed after its question was written")
        it["question"] = row["question"].strip()


def interpretation_warnings(items):
    """An answer item whose question uses an interpreted alias (e.g. plain 'EPS') requires the
    alias_interpretation warning. Plain aliases containing it ('diluted EPS') do not count."""
    for it in items:
        if not it["question"] or not it["gold_plan"] or it["gold_outcome"] != "answer":
            continue
        m = {**ONTO["metrics"], **ONTO["derived_metrics"]}[it["gold_plan"]["metric"]]
        text = it["question"].lower()
        for a in sorted(m["aliases"], key=len, reverse=True):
            text = re.sub(rf"\b{re.escape(a.lower())}\b", " ", text)
        if any(re.search(rf"\b{re.escape(ia['alias'].lower())}\b", text) for ia in m.get("interpreted_aliases", [])):
            if "alias_interpretation" not in it["required_warnings"]:
                it["required_warnings"].append("alias_interpretation")


def _load_sheet(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main():
    out = build()
    hand = [i for i in out["test"] + out["dev"] if i["layer"] == "handwritten"]
    sheets = {}
    for author, name in (("codex_assisted", "handwritten_plans_owner.json"),
                         ("claude_assisted", "handwritten_plans_claude.json")):
        fresh = plan_sheet([i for i in hand if i["author"] == author], author)
        old = _load_sheet(OUT / name)
        if old:  # keep questions already written; never overwrite them with blanks
            merge_questions(hand, old)
            written = {r["id"]: r["question"] for r in old["plans"]}
            for r in fresh["plans"]:
                r["question"] = written.get(r["id"], "")
        sheets[name] = fresh
    interpretation_warnings(out["test"] + out["dev"])
    _dump(OUT / "qa_test.json", out["test"])
    _dump(OUT / "qa_dev.json", out["dev"])
    for name, sheet in sheets.items():
        _dump(OUT / name, sheet)
    missing = [i["id"] for i in hand if not i["question"]]
    print(f"handwritten questions written: {len(hand) - len(missing)}/{len(hand)}")
    from collections import Counter
    for split, items in out.items():
        print(split, len(items), dict(Counter(i["layer"] for i in items)))
        print("  ", dict(Counter((i["gold_plan"] or {}).get("intent", i.get("kind")) for i in items)))
    return out


if __name__ == "__main__":
    main()
