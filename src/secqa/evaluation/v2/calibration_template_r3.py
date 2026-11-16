"""Round-3 calibration template: 30 new calibration-only questions on Cisco and Oracle cells not used before.

    python -m secqa.evaluation.v2.calibration_template_r3
        # writes data/eval/v0.2/calibration_r3/{template.json, cell_exclusion.json, manifest.json}

Protocol: data/eval/v0.2/calibration_r3/PROTOCOL.md (committed before this ran). A fact cell is used if
it appears in qa_dev.json, in the round-1 or round-2 calibration templates, or in
qualified_alternatives.json; key (ticker, metric, concept, period_end, value_policy, accession). Every cell
of a round-3 question, components of derived metrics included, must be unused, and no cell is shared
between two round-3 questions. Refusal questions have no cells; their wording and target are new.

No long-term-debt slot: every Cisco long_term_debt cell is used (dev gen-010) and Oracle does not report
the metric, so no qualified-alternative item can be built from unused cells.
"""
import hashlib
import json
import random

import yaml

from ... import config
from . import gen_qa, gold

SEED = 4041                      # CALIBRATION_R3_SEED, fixed in PROTOCOL.md before sampling
DIR = config.EVAL_DIR / "v0.2"
OUT = DIR / "calibration_r3"
POLICY = "latest_in_snapshot"
TICKERS = ("CSCO", "ORCL")
YEARS = (2023, 2024, 2025)
NAME = {"CSCO": "Cisco", "ORCL": "Oracle"}
VECTOR = ["final_correct", "appropriate_refusal", "evidence_complete", "plan_valid", "intent_ok", "concept",
          "period_ok", "calculation_ok"]


def key(c):
    return (c["ticker"], c.get("metric"), c["concept"], c["period_end"], POLICY, c["accession"])


def used_cells():
    used = set()
    for it in json.loads((DIR / "qa_dev.json").read_text(encoding="utf-8")):
        used |= {key(c) for c in it["gold_cells"]}
    for r in ("calibration", "calibration_r2"):
        for s in json.loads((DIR / r / "template.json").read_text(encoding="utf-8"))["slots"]:
            used |= {key(c) for c in s["item"]["gold_cells"]}
    plan_metric = {}
    for path in ("qa_dev.json", "qa_test.json"):
        for it in json.loads((DIR / path).read_text(encoding="utf-8")):
            if it["gold_plan"]:
                plan_metric[it["id"]] = it["gold_plan"]["metric"]
    for a in json.loads((DIR / "qualified_alternatives.json").read_text(encoding="utf-8"))["items"]:
        used |= {key({**c, "metric": plan_metric[a["item"]]}) for c in a["cells"]}
    return used


class Pool:
    """Unused cells, handed out once each."""

    def __init__(self, o, used):
        self.o, self.used, self.taken = o, used, set()

    def cells(self, t, m, fy, partial=False, allow_taken=False):
        """Evidence cells of one value if they are new. partial (Amendment 1, ratio and pp slots only):
        only the numerator must be new; the denominator may be a used cell. allow_taken: the numerator may
        already be held by another round-3 question (the second pp slot, Amendment 1)."""
        c = gold.cell(self.o, t, m, fy)
        if c["outcome"] != "answer":
            return None, c
        ev = gen_qa._evidence(c)
        check = gen_qa._evidence(c["components"][0]) if partial and "components" in c else ev
        if any(key(e) in self.used or (key(e) in self.taken and not allow_taken) for e in check):
            return None, c
        return ev, c

    def reused(self, ev):
        return [list(key(e)) for e in ev if key(e) in self.used]

    def take(self, ev):
        self.taken |= {key(e) for e in ev}


def item(iid, question, intent, metric, companies, periods, outcome, cells, result, warnings, unit):
    return {"id": iid, "layer": "calibration", "author": "calibration_only", "question": question,
            "gold_plan": {"intent": intent, "metric": metric, "companies": companies, "periods": periods},
            "gold_outcome": outcome, "gold_cells": cells, "gold_result": result, "required_warnings": warnings,
            "advisory_warnings": [], "tolerance": gen_qa.tolerance(unit, intent)}


def refusal(iid, question, outcome, plan=None):
    return {"id": iid, "layer": "calibration", "author": "calibration_only", "question": question,
            "gold_plan": plan, "gold_outcome": outcome, "gold_cells": [], "gold_result": {"outcome": outcome},
            "required_warnings": [], "advisory_warnings": [], "tolerance": None}


def novelty(it, reused):
    it["cell_novelty"] = "partially_new" if reused else "new"
    if reused:
        it["reused_cells"] = reused
    return it


def build(o, pool, rng):
    base = [m for m in o["metrics"] if m not in ("long_term_debt",)]
    ratios = [m for m, d in o["derived_metrics"].items() if d["formula"].split()[1] == "/"]
    out = {}

    def pick(kind, cands, make):
        rng.shuffle(cands)
        for cand in cands:
            got = make(*cand)
            if got:
                out[kind] = got
                return
        raise RuntimeError(f"no unused cells for {kind}")

    def fact(t, m, fy, kind_id, q, intent="fact_lookup", outcome="answer", warnings=(), partial=False):
        ev, c = pool.cells(t, m, fy, partial=partial)
        if not ev:
            return None
        reused = pool.reused(ev)
        pool.take(ev)
        val = c["val"] * 100 if intent == "ratio" else c["val"]
        unit = "percent" if intent == "ratio" else None
        res = {"outcome": outcome, "val": val} | ({"unit": unit} if unit else {})
        return novelty(item(kind_id, q, intent, m, [t], [f"FY{fy}"], outcome, ev, res, list(warnings), c["unit"]),
                       reused)

    def two(t, m, kind_id, intent, q, partial=False, allow_taken=False, first_years=(2023, 2024)):
        for y1 in first_years:
            e1, c1 = pool.cells(t, m, y1, partial=partial, allow_taken=allow_taken)
            e2, c2 = pool.cells(t, m, y1 + 1, partial=partial, allow_taken=allow_taken)
            if e1 and e2 and not {key(e) for e in e1} & {key(e) for e in e2}:
                reused = pool.reused(e1 + e2)
                shared = [list(key(e)) for e in e1 + e2 if key(e) in pool.taken and key(e) not in pool.used]
                pool.take(e1 + e2)
                if intent == "percentage_point_change":
                    res = {"outcome": "answer", "val": (c2["val"] - c1["val"]) * 100, "unit": "pp"}
                elif intent == "percent_change":
                    r = gold.change(c1["val"], c2["val"], intent)
                    res = {**r, "val": r["val"] * 100, "unit": "percent"} if r["outcome"] == "answer" else r
                else:
                    res = {"outcome": "answer", "val": c2["val"] - c1["val"], "unit": c1["unit"]}
                it = item(kind_id, q.format(co=NAME[t], m=gen_qa._phrase(m), y1=y1, y2=y1 + 1), intent, m, [t],
                          [f"FY{y1}", f"FY{y1 + 1}"], res["outcome"], e1 + e2, res, [], c1["unit"])
                it = novelty(it, reused)
                if shared:
                    it["shared_with_other_round3_question"] = shared
                return it
        return None

    def three(t, m, kind_id):
        evs, vals, unit = [], [], None
        for fy in YEARS:
            e, c = pool.cells(t, m, fy)
            if not e:
                return None
            evs.append(e)
            vals.append(c["val"])
            unit = c["unit"]
        flat = [x for e in evs for x in e]
        if len({key(x) for x in flat}) != len(flat):
            return None
        pool.take(flat)
        return item(kind_id, f"List {NAME[t]}'s {gen_qa._phrase(m)} for fiscal 2023, 2024 and 2025.",
                    "multi_period_lookup", m, [t], [f"FY{y}" for y in YEARS], "answer", flat,
                    {"outcome": "answer", "vals": vals}, [], unit)

    def cross(m, fy, kind_id):
        e1, c1 = pool.cells("CSCO", m, fy)
        e2, c2 = pool.cells("ORCL", m, fy)
        if not (e1 and e2):
            return None
        pool.take(e1 + e2)
        return item(kind_id, f"Compare Cisco's and Oracle's {gen_qa._phrase(m)} for fiscal {fy}.",
                    "cross_company_comparison", m, ["CSCO", "ORCL"], [f"FY{fy}"], "answer", e1 + e2,
                    {"outcome": "answer", "vals": [c1["val"], c2["val"]], "difference": c1["val"] - c2["val"]},
                    ["period_mismatch"], c1["unit"])

    ty = [(t, m, fy) for t in TICKERS for m in base for fy in YEARS]
    tm = [(t, m) for t in TICKERS for m in base]
    usd = [x for x in ty if x[1] not in ("eps_basic", "eps_diluted", "weighted_shares_basic", "weighted_shares_diluted")]
    # scarcest first (Amendment 1): only Cisco R&D has new numerator cells in consecutive years
    pick("pp", [(t, m) for t in TICKERS for m in ratios],
         lambda t, m: two(t, m, "A-cal3-pp", "percentage_point_change",
                          "By how many percentage points did {co}'s {m} change from fiscal {y1} to fiscal {y2}?",
                          partial=True))
    pick("pp_b", [(t, m) for t in TICKERS for m in ratios],
         lambda t, m: two(t, m, "A-cal3-pp-b", "percentage_point_change",
                          "How did {co}'s {m} move from fiscal {y1} to fiscal {y2}?", partial=True, allow_taken=True,
                          first_years=(2024,)))      # the other year pair; shares only the FY2024 numerator
    pick("ratio", [(t, m, fy) for t in TICKERS for m in ratios for fy in YEARS],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-ratio", f"What was {NAME[t]}'s {gen_qa._phrase(m)} in fiscal {fy}?",
                               intent="ratio", partial=True))
    pick("ratio_b", [(t, m, fy) for t in TICKERS for m in ratios for fy in YEARS],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-ratio-b", f"Calculate {NAME[t]}'s {gen_qa._phrase(m)} for fiscal {fy}.",
                               intent="ratio", partial=True))
    pick("fact_a", list(usd), lambda t, m, fy: fact(t, m, fy, "A-cal3-fact-a",
                                                     f"What was {NAME[t]}'s {gen_qa._phrase(m)} in fiscal {fy}?"))
    pick("fact_b", list(usd), lambda t, m, fy: fact(t, m, fy, "A-cal3-fact-b",
                                                     f"How much {gen_qa._phrase(m)} did {NAME[t]} report for fiscal {fy}?"))
    pick("fact_c", list(usd), lambda t, m, fy: fact(t, m, fy, "A-cal3-fact-c",
                                                     f"Give {NAME[t]}'s fiscal {fy} {gen_qa._phrase(m)}."))
    pick("eps", [(t, "eps_diluted", fy) for t in TICKERS for fy in YEARS],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-eps", f"What was {NAME[t]}'s diluted earnings per share in fiscal {fy}?"))
    pick("alias", [(t, "eps_diluted", fy) for t in TICKERS for fy in YEARS],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-alias", f"What was {NAME[t]}'s EPS in fiscal {fy}?",
                               warnings=["alias_interpretation"]))
    pick("year", [(t, m, fy) for t, m, fy in usd if m in ("revenue", "net_income", "operating_income", "total_assets")],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-year", f"What was {NAME[t]}'s {gen_qa._phrase(m)} in {fy}?",
                               outcome="ambiguous_year", warnings=["ambiguous_year"]))
    pick("multi", list(tm), lambda t, m: three(t, m, "A-cal3-multi"))
    pick("multi_b", list(tm), lambda t, m: three(t, m, "A-cal3-multi-b"))
    pick("cross", [(m, fy) for m in base for fy in YEARS], lambda m, fy: cross(m, fy, "A-cal3-cross"))
    pick("cross_b", [(m, fy) for m in base for fy in YEARS], lambda m, fy: cross(m, fy, "A-cal3-cross-b"))
    pick("abs", list(tm), lambda t, m: two(t, m, "A-cal3-abs", "absolute_change",
                                           "By how much did {co}'s {m} change from fiscal {y1} to fiscal {y2}?"))
    pick("abs_b", list(tm), lambda t, m: two(t, m, "A-cal3-abs-b", "absolute_change",
                                             "What was the dollar change in {co}'s {m} between fiscal {y1} and {y2}?"))
    pick("pct", list(tm), lambda t, m: two(t, m, "A-cal3-pct", "percent_change",
                                           "What was the percent change in {co}'s {m} from fiscal {y1} to fiscal {y2}?"))
    pick("pct_b", list(tm), lambda t, m: two(t, m, "A-cal3-pct-b", "percent_change",
                                             "By what percentage did {co}'s {m} change from fiscal {y1} to {y2}?"))
    pick("fcf", [(t, "free_cash_flow", fy) for t in TICKERS for fy in YEARS],
         lambda t, m, fy: fact(t, m, fy, "A-cal3-fcf", f"How much free cash flow did {NAME[t]} generate in fiscal {fy}?"))
    out["not_reported"] = refusal("A-cal3-notrep", "What was Oracle's total liabilities at the end of fiscal 2025?",
                                  "not_reported", {"intent": "fact_lookup", "metric": "total_liabilities",
                                                   "companies": ["ORCL"], "periods": ["FY2025"]})
    out["ontology"] = refusal("A-cal3-ooo", "What was Cisco's revenue from its Networking product category in fiscal 2025?",
                              "out_of_ontology")
    out["forecast"] = refusal("A-cal3-forecast", "What will Oracle's revenue be in fiscal 2027?", "unsupported")
    out["range"] = refusal("A-cal3-range", "What was Oracle's operating income in fiscal 2021?", "out_of_range")
    return out


def main():
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    used = used_cells()
    pool = Pool(o, used)
    items = build(o, pool, random.Random(SEED))
    for it in items.values():
        it.setdefault("cell_novelty", "new")
    for it in items.values():
        overlap = {key(c) for c in it["gold_cells"]} & used
        if it.get("cell_novelty") == "partially_new":
            assert it["gold_plan"]["intent"] in ("ratio", "percentage_point_change"), it["id"]
            assert all(k[1] == "revenue" for k in overlap), (it["id"], overlap)     # only the denominator
        else:
            assert not overlap, it["id"]
    S = [  # (slot, item kind, system, target, targeted score, expected pass)
        ("P01", "fact_a", "v0.1", "amount stated in millions with a thousands separator", "final_correct", True),
        ("P02", "eps", "v0.1", "diluted EPS named as diluted, two decimals", "final_correct", True),
        ("P03", "multi", "v0.1", "three fiscal-year values in a bulleted list", "final_correct", True),
        ("P04", "cross", "v0.1", "comparison with the fiscal-year-end difference explained in a full sentence", "final_correct", True),
        ("P05", "abs", "v0.1", "absolute change with the direction stated in words", "final_correct", True),
        ("P06", "pct", "v0.1", "percent change with both year values", "final_correct", True),
        ("P07", "ratio", "v0.1", "ratio as a percentage with one or two decimals", "final_correct", True),
        ("P08", "pp", "v0.1", "percentage-point change written in basis points", "final_correct", True),
        ("P09", "alias", "v0.1", "bare EPS read as diluted, and the reading stated", "final_correct", True),
        ("P10", "year", "v0.1", "bare year read as the fiscal year, and the reading stated", "final_correct", True),
        ("P11", "not_reported", "v0.1", "metric the filer does not report, declined", "final_correct", True),
        ("P12", "forecast", "v0.1", "forecast question declined without a projection", "final_correct", True),
        ("P13", "ratio_b", "v0.2", "v0.2 record fully correct for a ratio", "calculation_ok", True),
        ("P14", "multi_b", "v0.2", "v0.2 record fully correct for a multi-period lookup", "calculation_ok", True),
        ("P15", "fcf", "v0.1", "derived free cash flow with its components, every number traceable", "evidence_complete", True),
        ("F01", "fact_b", "v0.1", "value of a different fiscal year stated as the requested year", "final_correct", False),
        ("F02", "cross_b", "v0.1", "cross-company comparison without the fiscal-year-end warning", "final_correct", False),
        ("F03", "abs_b", "v0.1", "absolute change with the right magnitude and the wrong direction", "final_correct", False),
        ("F04", "pct_b", "v0.1", "percent change off by more than the tolerance", "final_correct", False),
        ("F05", "pp_b", "v0.1", "percentage-point change written as a percent ('rose by 0.3%')", "final_correct", False),
        ("F06", "alias", "v0.1", "bare EPS answered with basic EPS, named as basic", "final_correct", False),
        ("F07", "year", "v0.1", "bare year answered without stating how the year was read", "final_correct", False),
        ("F08", "ontology", "v0.1", "out-of-ontology metric declined but an estimate is still given", "final_correct", False),
        ("F09", "forecast", "v0.1", "forecast question answered with a projected figure", "final_correct", False),
        ("F10", "range", "v0.1", "out-of-range year answered as if it were available", "final_correct", False),
        ("F11", "pct", "v0.2", "v0.2 plan with the wrong intent", "intent_ok", False),
        ("F12", "abs", "v0.2", "v0.2 result that does not follow from its own cells", "calculation_ok", False),
        ("F13", "fact_c", "v0.1", "an evidence item with an empty period_end", "evidence_complete", False),
        ("F14", "fact_c", "v0.1", "answer states two different values for the same figure", "final_correct", False),
        ("F15", "multi", "v0.1", "a stated number that no evidence value supports", "evidence_complete", False),
    ]
    assert len(S) == 30 and sum(s[5] for s in S) == 15
    slots = []
    for slot, kind, system, target, scored, expect in S:
        it = items[kind]
        slots.append({"slot": slot, "target": target, "targeted_score": scored,
                      "targeted_expected": "pass" if expect else "fail", "gold_source": "calibration_only",
                      "item": it, "qualified_alternative": None,
                      "record": {"id": it["id"], "system": system, "answer": "", "evidence": [],
                                 "plan": None if system == "v0.1" else {}, "result": None if system == "v0.1" else {}},
                      "expected_scores": {k: None for k in VECTOR}, "calibrator_note": ""})
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = OUT / "template.json"
    tpl.write_text(json.dumps({"version": 3, "round": 3, "single_run": True, "seed": SEED, "n": 30,
                               "expected_pass": 15, "expected_fail": 15, "vector": VECTOR, "slots": slots},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    excl = OUT / "cell_exclusion.json"
    new_cells = sorted({key(c) for it in items.values() for c in it["gold_cells"]})
    excl.write_text(json.dumps({"key": ["ticker", "metric", "concept", "period_end", "value_policy", "accession"],
                                "used_before": len(used), "used_before_cells": sorted(used),
                                "round3_cells": new_cells,
                                "overlap_with_used": sorted(set(new_cells) & used),
                                "partially_new_items": [it["id"] for it in items.values()
                                                        if it["cell_novelty"] == "partially_new"],
                                "questions": len(items)}, indent=1) + "\n", encoding="utf-8", newline="\n")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    gen = config.REPO_ROOT / "src" / "secqa" / "evaluation" / "v2" / "calibration_template_r3.py"
    (OUT / "manifest.json").write_text(json.dumps({
        "seed": SEED, "protocol": {"path": "PROTOCOL.md", "sha256": sha(OUT / "PROTOCOL.md")},
        "generator": {"path": "src/secqa/evaluation/v2/calibration_template_r3.py", "sha256": sha(gen)},
        "template": {"path": "template.json", "sha256": sha(tpl)},
        "cell_exclusion": {"path": "cell_exclusion.json", "sha256": sha(excl)}}, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    print(len(items), "questions;", len(new_cells), "new cells; excluded", len(used), "used cells")
    for k, it in items.items():
        print(f"  {k:13s} {it['id']:18s} {it['question']}")


if __name__ == "__main__":
    main()
