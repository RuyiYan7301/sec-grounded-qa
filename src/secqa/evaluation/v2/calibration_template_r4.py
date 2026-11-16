"""Round-4 calibration template: 24 slots on Cisco and Oracle base cells that never appeared before.

    python -m secqa.evaluation.v2.calibration_template_r4
        # writes data/eval/v0.2/calibration_r4/{template.json, cell_exclusion.json, manifest.json}

Protocol: data/eval/v0.2/calibration_r4/PROTOCOL.md (committed before this ran). Used cells are those of
qa_dev.json, of every round-1, round-2 and round-3 calibration item, and of qualified_alternatives.json.
Base metrics only (no ratio, no percentage-point items); at most 24 new cells; at least 10 left unused.
"""
import hashlib
import json
import random

import yaml

from ... import config
from . import calibration_template_r3 as r3
from . import gen_qa, gold

SEED = 4042                      # CALIBRATION_R4_SEED, fixed in PROTOCOL.md before sampling
DIR = config.EVAL_DIR / "v0.2"
OUT = DIR / "calibration_r4"
NAME, YEARS, VECTOR, key = r3.NAME, r3.YEARS, r3.VECTOR, r3.key
MAX_NEW, MIN_LEFT = 24, 10


def used_cells():
    used = r3.used_cells()
    for s in json.loads((DIR / "calibration_r3" / "template.json").read_text(encoding="utf-8"))["slots"]:
        used |= {key(c) for c in s["item"]["gold_cells"]}
    return used


def free_base_cells(o, used):
    out = {}
    for t in r3.TICKERS:
        for m in o["metrics"]:
            for fy in YEARS:
                c = gold.cell(o, t, m, fy)
                if c["outcome"] != "answer":
                    continue
                ev = gen_qa._evidence(c)
                if not any(key(e) in used for e in ev):
                    out[(t, m, fy)] = (ev, c)
    return out


def main():
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    used = used_cells()
    free = free_base_cells(o, used)
    rng = random.Random(SEED)
    taken = set()

    def avail(*tmf):
        return all(x in free and x not in taken for x in tmf)

    def choose(cands):
        cands = [c for c in cands if avail(*c)]
        assert cands, "no candidate"
        pick = rng.choice(sorted(cands))
        taken.update(pick)
        return pick

    ph = gen_qa._phrase
    amounts = [k for k in free if k[1] not in ("eps_basic", "eps_diluted", "weighted_shares_basic", "weighted_shares_diluted")]
    items = {}

    def one(kid, tmf, q, outcome="answer", warnings=()):
        ev, c = free[tmf]
        t, m, fy = tmf
        return r3.item(kid, q, "fact_lookup", m, [t], [f"FY{fy}"], outcome, ev, {"outcome": outcome, "val": c["val"]},
                       list(warnings), c["unit"])

    def pair(kid, t, m, y1, intent, q):
        (e1, c1), (e2, c2) = free[(t, m, y1)], free[(t, m, y1 + 1)]
        if intent == "percent_change":
            r = gold.change(c1["val"], c2["val"], intent)
            res = {**r, "val": r["val"] * 100, "unit": "percent"} if r["outcome"] == "answer" else r
        else:
            res = {"outcome": "answer", "val": c2["val"] - c1["val"], "unit": c1["unit"]}
        return r3.item(kid, q.format(co=NAME[t], m=ph(m), y1=y1, y2=y1 + 1), intent, m, [t], [f"FY{y1}", f"FY{y1 + 1}"],
                       res["outcome"], e1 + e2, res, [], c1["unit"])

    # multi-period first (needs three years of one metric), then pairs, then single cells
    multi_c =[(t, m) for (t, m, fy) in sorted(free) if fy == 2023 and all(avail((t, m, y)) for y in YEARS)]
    t, m = rng.choice(sorted(set(multi_c)))
    taken.update((t, m, y) for y in YEARS)
    evs = [free[(t, m, y)] for y in YEARS]
    items["multi"] = r3.item("A-cal4-multi", f"What were {NAME[t]}'s {ph(m)} in fiscal 2023, 2024 and 2025?",
                             "multi_period_lookup", m, [t], [f"FY{y}" for y in YEARS], "answer",
                             [x for e, _ in evs for x in e], {"outcome": "answer", "vals": [c["val"] for _, c in evs]},
                             [], evs[0][1]["unit"])
    cross_c =sorted({(m2, fy) for (t2, m2, fy) in free if t2 == "CSCO" and ("ORCL", m2, fy) in free})
    cross_c = [x for x in cross_c if avail(("CSCO",) + x, ("ORCL",) + x)]
    cm, cfy = rng.choice(cross_c)
    taken.update({("CSCO", cm, cfy), ("ORCL", cm, cfy)})
    (e1, c1), (e2, c2) = free[("CSCO", cm, cfy)], free[("ORCL", cm, cfy)]
    items["cross"] = r3.item("A-cal4-cross", f"How did Cisco's {ph(cm)} compare with Oracle's in fiscal {cfy}?",
                             "cross_company_comparison", cm, ["CSCO", "ORCL"], [f"FY{cfy}"], "answer", e1 + e2,
                             {"outcome": "answer", "vals": [c1["val"], c2["val"]], "difference": c1["val"] - c2["val"]},
                             ["period_mismatch"], c1["unit"])
    pairs = sorted({(t2, m2, fy) for (t2, m2, fy) in amounts if fy < 2025 and (t2, m2, fy + 1) in free})
    for kid, intent, q in [("abs", "absolute_change", "How much did {co}'s {m} change between fiscal {y1} and fiscal {y2}?"),
                           ("pct", "percent_change", "What was the year-over-year change, in percent, of {co}'s {m} in fiscal {y2}?")]:
        cands = [p for p in pairs if avail(p, (p[0], p[1], p[2] + 1))]
        t2, m2, y1 = rng.choice(cands)
        taken.update({(t2, m2, y1), (t2, m2, y1 + 1)})
        items[kid] = pair(f"A-cal4-{kid}", t2, m2, y1, intent, q)
    sh = sorted(k for k in free if k[1] in ("weighted_shares_basic", "weighted_shares_diluted") and k[2] < 2025
                and (k[0], k[1], k[2] + 1) in free)
    sh = [p for p in sh if avail(p, (p[0], p[1], p[2] + 1))]
    t2, m2, y1 = rng.choice(sh)
    taken.update({(t2, m2, y1), (t2, m2, y1 + 1)})
    items["pct_shares"] = pair("A-cal4-pct-shares", t2, m2, y1, "percent_change",
                               "By what percent did {co}'s {m} change from fiscal {y1} to fiscal {y2}?")
    eps_b = choose([(k,) for k in free if k[1] == "eps_basic"])[0]
    items["eps"] = one("A-cal4-eps", eps_b, f"What was {NAME[eps_b[0]]}'s basic earnings per share for fiscal {eps_b[2]}?")
    eps_d = choose([(k,) for k in free if k[1] == "eps_diluted"])[0]
    items["alias"] = one("A-cal4-alias", eps_d, f"What was {NAME[eps_d[0]]}'s EPS for fiscal {eps_d[2]}?",
                         warnings=["alias_interpretation"])
    yr = choose([(k,) for k in amounts if k[1] in ("net_income", "total_assets", "operating_cash_flow", "cost_of_revenue")])[0]
    items["year"] = one("A-cal4-year", yr, f"How much {ph(yr[1])} did {NAME[yr[0]]} report in {yr[2]}?",
                        outcome="ambiguous_year", warnings=["ambiguous_year"])
    for kid, q in [("fact_a", "What was {co}'s {m} in fiscal {y}?"), ("fact_b", "Tell me {co}'s {m} for fiscal year {y}."),
                   ("fact_c", "What {m} did {co} report for fiscal {y}?")]:
        k = choose([(x,) for x in amounts])[0]
        items[kid] = one(f"A-cal4-{kid}", k, q.format(co=NAME[k[0]], m=ph(k[1]), y=k[2]))
    items["not_reported"] = r3.refusal("A-cal4-notrep", "What was Oracle's gross profit in fiscal 2024?", "not_reported",
                                       {"intent": "fact_lookup", "metric": "gross_profit", "companies": ["ORCL"],
                                        "periods": ["FY2024"]})
    items["ontology"] = r3.refusal("A-cal4-ooo", "What was Oracle's cloud services and license support revenue in fiscal 2025?",
                                   "out_of_ontology")
    items["advice"] = r3.refusal("A-cal4-advice", "Should I buy Cisco stock this year?", "unsupported")
    items["range"] = r3.refusal("A-cal4-range", "What was Cisco's revenue in fiscal 2022?", "out_of_range")
    for it in items.values():
        it["cell_novelty"] = "new"
        assert not ({key(c) for c in it["gold_cells"]} & used), it["id"]
    new_cells = sorted({key(c) for it in items.values() for c in it["gold_cells"]})
    assert len(new_cells) <= MAX_NEW and len(free) - len(taken) >= MIN_LEFT, (len(new_cells), len(free) - len(taken))

    S = [  # (slot, item, system, target, targeted score, expected pass)
        ("P01", "fact_a", "v0.1", "amount in billions with three decimals", "final_correct", True),
        ("P02", "eps", "v0.1", "basic EPS named as basic, two decimals", "final_correct", True),
        ("P03", "multi", "v0.1", "three fiscal-year values in running prose", "final_correct", True),
        ("P04", "cross", "v0.1", "both values, their difference and the fiscal-year-end warning", "final_correct", True),
        ("P05", "abs", "v0.1", "absolute change with both year values and the direction", "final_correct", True),
        ("P06", "pct", "v0.1", "percent change with two decimals", "final_correct", True),
        ("P07", "alias", "v0.1", "bare EPS read as diluted, reading stated", "final_correct", True),
        ("P08", "year", "v0.1", "bare year read as the fiscal year, reading stated", "final_correct", True),
        ("P09", "not_reported", "v0.1", "metric the filer does not report, declined", "final_correct", True),
        ("P10", "advice", "v0.1", "investment question declined without advice", "final_correct", True),
        ("P11", "pct_shares", "v0.2", "v0.2 record fully correct for a percent change of a share count", "calculation_ok", True),
        ("P12", "fact_b", "v0.1", "every stated number traceable, answer with a short source line", "evidence_complete", True),
        ("F01", "fact_c", "v0.1", "amount rounded so far that it is outside tolerance", "final_correct", False),
        ("F02", "cross", "v0.1", "comparison without the fiscal-year-end warning", "final_correct", False),
        ("F03", "abs", "v0.1", "absolute change with the wrong direction", "final_correct", False),
        ("F04", "pct", "v0.1", "percent change computed on the later year as base", "final_correct", False),
        ("F05", "alias", "v0.1", "bare EPS answered with basic EPS, named as basic", "final_correct", False),
        ("F06", "year", "v0.1", "bare year answered without saying how the year was read", "final_correct", False),
        ("F07", "ontology", "v0.1", "out-of-ontology segment figure estimated instead of declined", "final_correct", False),
        ("F08", "range", "v0.1", "out-of-range year answered with a figure", "final_correct", False),
        ("F09", "multi", "v0.1", "multi-period answer that leaves out one year", "final_correct", False),
        ("F10", "pct_shares", "v0.2", "v0.2 cells from the wrong fiscal years", "period_ok", False),
        ("F11", "fact_a", "v0.2", "v0.2 cell resolved to a wrong concept", "concept", False),
        ("F12", "fact_b", "v0.1", "an evidence item with an empty accession", "evidence_complete", False),
    ]
    assert len(S) == 24 and sum(s[5] for s in S) == 12
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
    tpl.write_text(json.dumps({"version": 4, "round": 4, "single_run": True, "seed": SEED, "n": 24, "expected_pass": 12,
                               "expected_fail": 12, "vector": VECTOR,
                               "not_covered": ["ratio", "percentage_point_change", "long_term_debt qualified alternative",
                                               "restated", "scope", "not_meaningful"],
                               "slots": slots}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    excl = OUT / "cell_exclusion.json"
    left = sorted(set(free) - taken)
    excl.write_text(json.dumps({"key": ["ticker", "metric", "concept", "period_end", "value_policy", "accession"],
                                "used_before": len(used), "round4_cells": new_cells,
                                "overlap_with_used": sorted(set(new_cells) & used),
                                "unused_base_cells_left": [list(x) for x in left]}, indent=1) + "\n",
                    encoding="utf-8", newline="\n")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    gen = config.REPO_ROOT / "src" / "secqa" / "evaluation" / "v2" / "calibration_template_r4.py"
    (OUT / "manifest.json").write_text(json.dumps({
        "seed": SEED, "protocol": {"path": "PROTOCOL.md", "sha256": sha(OUT / "PROTOCOL.md")},
        "generator": {"path": "src/secqa/evaluation/v2/calibration_template_r4.py", "sha256": sha(gen)},
        "template": {"path": "template.json", "sha256": sha(tpl)},
        "cell_exclusion": {"path": "cell_exclusion.json", "sha256": sha(excl)}}, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    print(len(items), "questions;", len(new_cells), "new cells;", len(left), "unused base cells left")
    for k, it in items.items():
        print(f"  {k:13s} {it['id']:18s} {it['question']}")


if __name__ == "__main__":
    main()
