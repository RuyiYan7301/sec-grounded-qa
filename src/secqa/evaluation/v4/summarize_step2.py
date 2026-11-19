"""v0.4 step 2: tables and paired tests over the render runs of every arm (plan 3d, amendment 2026-11-19).

    python -m secqa.evaluation.v4.summarize_step2      # -> results/v0.4/step2/summary.json, prints tables

Primary: frozen final correct. Exact McNemar on B0-B1, B1-S, S-R, R-T, Holm-corrected within each test
set; the same on the secondary (provenance) count. Groups: intent (gold plan intent or gold outcome);
test set 1 also by layer, and generated items by template half.
"""
import json
import math
from collections import defaultdict

from ... import config
from .run_step2 import OUT, load, template_half

ARMS = ["B0", "B1", "S", "Sfree", "Slong", "R", "T"]
PAIRS = [("B0", "B1"), ("B1", "S"), ("S", "R"), ("R", "T")]


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def group_of(it):
    if it.get("layer") in ("handwritten", "adversarial"):
        return it["layer"]
    return "generated_" + (template_half(it["question"]) or "unknown") + "_half"


def main():
    out = {}
    for s in ("t1", "t2"):
        items = {it["id"]: it for it in load(s)}
        runs = {}
        for a in ARMS:
            p = OUT / s / f"run_{a}.json"
            if p.exists():
                runs[a] = {r["id"]: r for r in json.loads(p.read_text(encoding="utf-8"))["items"]}
        res = {"items": len(items), "arms": {}, "pairs": {}}
        for a, rows in runs.items():
            summ = json.loads((OUT / s / f"run_{a}.json").read_text(encoding="utf-8"))["summary"]
            fc = sum(r["score"]["final_correct"] for r in rows.values())
            by_intent, by_group = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
            for i, r in rows.items():
                it = items[i]
                k = (it.get("gold_plan") or {}).get("intent") or it["gold_outcome"]
                by_intent[k][0] += r["score"]["final_correct"]
                by_intent[k][1] += 1
                if s == "t1":
                    g = group_of(it)
                    by_group[g][0] += r["score"]["final_correct"]
                    by_group[g][1] += 1
            res["arms"][a] = {"final_correct": fc, "wilson95": wilson(fc, len(rows)),
                              "final_correct_provenance": summ["final_correct_provenance"],
                              "execution_correct": summ["execution_correct"], "plan_valid": summ["plan_valid"],
                              "refused_answerable": [summ["refused_answerable"], summ["answerable"]],
                              "silent_wrong": summ["silent_wrong"],
                              "restated_plans_extra_period": summ["restated_plans_extra_period"],
                              "median_plan_seconds": summ["median_plan_seconds"],
                              "by_intent": dict(sorted(by_intent.items())), "by_group": dict(sorted(by_group.items()))}
        for key in ("final_correct", "final_correct_provenance"):
            ps, rows_out = [], []
            for x, y in PAIRS:
                if x in runs and y in runs:
                    get = (lambda r: r["score"]["final_correct"]) if key == "final_correct" else (lambda r: r["final_correct_provenance"])
                    b = sum(get(runs[x][i]) and not get(runs[y][i]) for i in items)
                    c = sum(not get(runs[x][i]) and get(runs[y][i]) for i in items)
                    ps.append(mcnemar_exact(b, c))
                    rows_out.append({"pair": f"{x} vs {y}", f"only_{x}": b, f"only_{y}": c, "p_exact": ps[-1]})
            for r, q in zip(rows_out, holm(ps)):
                r["p_holm"] = q
            res["pairs"][key] = rows_out
        out[s] = res
    path = OUT / "summary.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for s, res in out.items():
        print(f"\n== {s} ({res['items']} items)")
        print("arm    final  wilson        prov  exec  valid refused_ans silent extra_per med_s")
        for a, v in res["arms"].items():
            print(f"{a:6} {v['final_correct']:5}  {str(v['wilson95']):13} {v['final_correct_provenance']:4}  "
                  f"{v['execution_correct']:4}  {v['plan_valid']:5} {str(v['refused_answerable']):11} "
                  f"{v['silent_wrong']:6} {v['restated_plans_extra_period']:9} {v['median_plan_seconds']}")
        for key, rows in res["pairs"].items():
            print(key, json.dumps(rows))
        if s == "t1":
            for a, v in res["arms"].items():
                print(a, v["by_group"])
    print(path)


if __name__ == "__main__":
    main()
