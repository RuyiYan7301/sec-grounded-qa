"""A tool people already use (Perplexity, web) on a seeded sample of the frozen Part A test questions.

    python -m secqa.evaluation.external_compare sample        # writes results/test/external/sample.json
    python -m secqa.evaluation.external_compare score FILE    # FILE: {"<id>": "<answer text>", ...}

Fixed before any answer was collected:
- Sample: 30 of the 160 test questions, seed 1118, stratified like the test set (15 generated, 8
  handwritten, 7 adversarial).
- Asking: each question verbatim in a new thread, default mode, nothing added; the full reply text is
  saved unchanged (raw replies kept in the same folder), with the date and the mode shown in the UI.
- Scoring: the frozen Part A scorer (2.1), final_correct only, from the answer text. The record has no plan,
  result or XBRL evidence (the tool cites web pages), so only final correctness is compared. Paired with the
  v0.2 and v0.1 test runs on the same questions (exact McNemar).
- Caveat stated with the result: the tool reads the live web, not the 2026-10-16 snapshot; a figure that
  differs because a later filing restated it would count as wrong.
"""
import json
import random
import sys
from collections import Counter
from math import comb

import yaml

from .. import config
from .v2 import score as scorer

OUT = config.REPO_ROOT / "results" / "test" / "external"
SEED, PER_LAYER = 1118, {"generated": 15, "handwritten": 8, "adversarial": 7}
V02 = config.REPO_ROOT / "results" / "test" / "pipeline" / "run_61b72567_20261116T174624Z.json"
V01 = config.REPO_ROOT / "results" / "test" / "v01" / "run_20261116T194148Z.json"


def sample():
    items = json.loads((config.EVAL_DIR / "v0.2" / "qa_test.json").read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    pick = []
    for layer, n in PER_LAYER.items():
        pool = [it for it in items if it["layer"] == layer]
        pick += rng.sample(pool, n)
    rng.shuffle(pick)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sample.json").write_text(json.dumps({"seed": SEED, "per_layer": PER_LAYER,
                                                 "items": [{"id": it["id"], "question": it["question"]} for it in pick]},
                                                indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(len(pick), "questions ->", OUT / "sample.json")


def mcnemar(b, c):
    n = b + c
    return None if not n else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def score(path):
    answers = json.loads(open(path, encoding="utf-8").read())
    ids = [x["id"] for x in json.loads((OUT / "sample.json").read_text(encoding="utf-8"))["items"]]
    gold, alts = scorer.load_gold("test")
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    ext = {}
    for i in ids:
        rec = {"id": i, "system": "external", "answer": answers.get(i, ""), "evidence": [], "plan": None, "result": None}
        ext[i] = scorer.score_item(gold[i], rec, alts.get(i), o)["final_correct"]
    v02 = {r["id"]: r["score"]["final_correct"] for r in json.loads(V02.read_text(encoding="utf-8"))["items"]}
    v01 = {r["id"]: r["score"]["final_correct"] for r in json.loads(V01.read_text(encoding="utf-8"))["items"]}
    layer = {it["id"]: it["layer"] for it in json.loads((config.EVAL_DIR / "v0.2" / "qa_test.json").read_text(encoding="utf-8"))}
    out = {"n": len(ids), "missing_answers": [i for i in ids if not answers.get(i)],
           "external_correct": sum(ext.values()), "v02_correct": sum(v02[i] for i in ids), "v01_correct": sum(v01[i] for i in ids),
           "by_layer": {L: {"n": n, "external": sum(ext[i] for i in ids if layer[i] == L),
                            "v02": sum(v02[i] for i in ids if layer[i] == L), "v01": sum(v01[i] for i in ids if layer[i] == L)}
                        for L, n in Counter(layer[i] for i in ids).items()}}
    for name, other in (("v02", v02), ("v01", v01)):
        b = sum(1 for i in ids if other[i] and not ext[i])
        c = sum(1 for i in ids if ext[i] and not other[i])
        out[f"paired_vs_{name}"] = {f"only_{name}": b, "only_external": c, "mcnemar_p": mcnemar(b, c)}
    out["per_item"] = {i: {"external": ext[i], "v02": v02[i], "v01": v01[i]} for i in ids}
    (OUT / "score.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_item"}, indent=1))


if __name__ == "__main__":
    {"sample": lambda: sample(), "score": lambda: score(sys.argv[2])}[sys.argv[1]]()
