"""Paired v0.1 / v0.2 comparison on the Part A test split, by layer, with the noise floor.

    python -m secqa.evaluation.compare_test V02_RUN V01_RUN V02_NOISE V01_NOISE
    # writes results/test/comparison/comparison_<UTC>.json

Primary: per layer, the 2x2 table of final_correct (v0.2 x v0.1) on the same questions. Secondary: exact
two-sided McNemar p on the discordant pairs. Noise floor: for each system, the share of the noise-subset
questions whose final_correct differs between the test run and the second run of that subset.
"""
import datetime
import json
import sys
from math import comb

from .. import config


def load(p):
    d = json.loads(open(p, encoding="utf-8").read())
    return d["run"], {r["id"]: r for r in d["items"]}


def mcnemar_exact(b, c):
    n = b + c
    if not n:
        return None
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def table(ids, a, b):
    t = {"both": 0, "v02_only": 0, "v01_only": 0, "neither": 0}
    off = {"v02_only": [], "v01_only": []}
    for i in ids:
        x, y = a[i]["score"]["final_correct"], b[i]["score"]["final_correct"]
        cell = "both" if x and y else "v02_only" if x else "v01_only" if y else "neither"
        t[cell] += 1
        if cell in off:
            off[cell].append(i)
    t |= {"n": len(ids), "v02_correct": t["both"] + t["v02_only"], "v01_correct": t["both"] + t["v01_only"],
          "mcnemar_exact_p": mcnemar_exact(t["v02_only"], t["v01_only"]),
          "v02_only_ids": off["v02_only"], "v01_only_ids": off["v01_only"]}
    return t


def flips(test, noise):
    ids = sorted(noise)
    changed = [i for i in ids if test[i]["score"]["final_correct"] != noise[i]["score"]["final_correct"]]
    return {"n": len(ids), "final_correct_flips": len(changed), "ids": changed,
            "test_run_correct": sum(test[i]["score"]["final_correct"] for i in ids),
            "noise_run_correct": sum(noise[i]["score"]["final_correct"] for i in ids)}


def main(v02, v01, v02n, v01n):
    (r2, a), (r1, b), (_, an), (_, bn) = load(v02), load(v01), load(v02n), load(v01n)
    assert set(a) == set(b), "the two runs must cover the same questions"
    layer = {i: a[i]["score"]["layer"] for i in a}
    out = {"inputs": {"v02": v02, "v01": v01, "v02_noise": v02n, "v01_noise": v01n},
           "all": table(sorted(a), a, b),
           "by_layer": {L: table(sorted(i for i in a if layer[i] == L), a, b) for L in sorted(set(layer.values()))},
           "noise_floor": {"v02": flips(a, an), "v01": flips(b, bn)}}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = config.REPO_ROOT / "results" / "test" / "comparison" / f"comparison_{ts}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(path.name)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
