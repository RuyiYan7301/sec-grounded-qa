"""Run the Part A scorer on a filled calibration file and compare with the calibrator's expected scores.

    python -m secqa.evaluation.v2.calibrate data/eval/v0.2/calibration/filled.json

Refuses to run until every slot has an answer and a complete expected score vector, so expectations are
written before any score is seen. Every run is appended to calibration/runs.jsonl with the scorer's
sha256, so each scorer change and its re-run on all 30 slots is on record.
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

import yaml

from ... import config
from . import score

RUNS = config.EVAL_DIR / "v0.2" / "calibration" / "runs.jsonl"
SCORER = Path(score.__file__)


def check_filled(doc):
    problems = []
    for s in doc["slots"]:
        rec, exp = s["record"], s["expected_scores"]
        if not (rec.get("answer") or "").strip():
            problems.append(f"{s['slot']}: answer is empty")
        missing = [k for k in doc["vector"] if k not in exp or (exp[k] is None and not s.get("na_ok", {}).get(k))]
        if missing:
            problems.append(f"{s['slot']}: expected scores missing {missing} (use null only via na_ok)")
    return problems


def run(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = check_filled(doc)
    if problems:
        print("Not run: fill these first\n  " + "\n  ".join(problems))
        return None
    ontology = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    rows, mismatches = [], []
    for s in doc["slots"]:
        got = score.score_item(s["item"], s["record"], s.get("qualified_alternative"), ontology)
        diff = {k: {"expected": s["expected_scores"][k], "scored": got[k]} for k in doc["vector"]
                if s["expected_scores"][k] != got[k]}
        target_ok = (got[s["targeted_score"]] in (True, "canonical", "qualified_alternative")) == \
                    (s["targeted_expected"] == "pass")
        rows.append({"slot": s["slot"], "target_as_designed": target_ok, "mismatch": diff, "path": got["path"],
                     "detail": got["detail"]})
        if diff:
            mismatches.append(s["slot"])
    rep = {"at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "scorer_version": score.V, "scorer_sha256": hashlib.sha256(SCORER.read_bytes()).hexdigest(),
           "file": str(Path(path).name), "file_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
           "slots": len(rows), "slots_with_mismatch": mismatches,
           "targets_not_as_designed": [r["slot"] for r in rows if not r["target_as_designed"]]}
    RUNS.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNS, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rep) + "\n")
    print(json.dumps(rep, indent=1))
    for r in rows:
        if r["mismatch"]:
            print(r["slot"], json.dumps(r["mismatch"]), "| path", r["path"])
    return rep, rows


if __name__ == "__main__":
    run(sys.argv[1])
