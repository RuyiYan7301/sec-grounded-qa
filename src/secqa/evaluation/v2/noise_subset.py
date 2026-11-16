"""Part A noise-floor subset: 40 test items run a second time by each system.

    python -m secqa.evaluation.v2.noise_subset      # writes data/eval/v0.2/noise_subset.json

Fixed before any v0.1 or v0.2 run on the v0.2 test split. Strata are layer x intent (generated,
handwritten) and layer x kind (adversarial): 24 strata. The 40 items are split across layers in
proportion to layer size (80/40/40 -> 20/10/10); inside a layer every stratum gets one item and the
rest goes to the largest strata by largest remainder. Items inside a stratum are drawn with SEED.
"""
import hashlib
import json
import random
from collections import Counter

from ... import config

SEED = 4040
N = 40
QA = config.EVAL_DIR / "v0.2" / "qa_test.json"
OUT = config.EVAL_DIR / "v0.2" / "noise_subset.json"


def stratum(it):
    return (it["layer"], it["kind"] if it["layer"] == "adversarial" else it["gold_plan"]["intent"])


def allocate(sizes, budget):
    take = {k: 1 for k in sizes}
    rest = budget - len(take)
    assert rest >= 0
    spare = {k: sizes[k] - 1 for k in sizes}
    total = sum(spare.values())
    quota = {k: rest * spare[k] / total for k in sizes}
    for k in sizes:
        take[k] += int(quota[k])
    left = budget - sum(take.values())
    for k in sorted(sizes, key=lambda k: (-(quota[k] - int(quota[k])), k))[:left]:
        take[k] += 1
    assert all(take[k] <= sizes[k] for k in sizes) and sum(take.values()) == budget
    return take


def main():
    items = json.loads(QA.read_text(encoding="utf-8"))
    groups = {}
    for it in items:
        groups.setdefault(stratum(it), []).append(it["id"])
    layers = Counter(it["layer"] for it in items)
    budget = {l: round(N * n / len(items)) for l, n in layers.items()}
    assert sum(budget.values()) == N
    rng = random.Random(SEED)
    picked = []
    for layer in sorted(layers):
        sizes = {k: len(v) for k, v in groups.items() if k[0] == layer}
        take = allocate(sizes, budget[layer])
        for k in sorted(sizes):
            ids = sorted(groups[k])
            picked += rng.sample(ids, take[k])
    OUT.write_text(json.dumps({
        "purpose": "noise floor: each system runs these test items a second time; run-to-run disagreement is "
                   "reported next to every v0.1/v0.2 difference",
        "fixed_before_any_run": True, "seed": SEED, "n": len(picked),
        "qa_test_sha256": hashlib.sha256(QA.read_bytes()).hexdigest(),
        "strata": "layer x intent (generated, handwritten), layer x kind (adversarial)",
        "per_layer": dict(Counter(i.split("-")[2] for i in picked)),
        "ids": sorted(picked)}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(len(picked), Counter(i.split("-")[2] for i in picked))


if __name__ == "__main__":
    main()
