"""Run the Part A scorer on a filled calibration file and compare with the calibrator's expected scores.

    python -m secqa.evaluation.v2.calibrate data/eval/v0.2/calibration/filled.json

Refuses to run until every slot has an answer and a complete expected score vector, so expectations are
written before any score is seen. Every run is appended to runs.jsonl next to the filled file (full output in raw_output_run<n>.json) with the scorer's
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
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    runs = path.parent / "runs.jsonl"              # each round keeps its runs next to its filled file
    if doc.get("single_run") and runs.exists() and runs.read_text(encoding="utf-8").strip():
        print(f"Not run: {runs} already has a run and this round allows one run only.")
        return None
    problems = check_filled(doc)
    if problems:
        print("Not run: fill these first\n  " + "\n  ".join(problems))
        return None
    ontology = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    rows, mismatches = [], []
    for s in doc["slots"]:
        got = score.score_item(s["item"], s["record"], s.get("qualified_alternative"), ontology)
        same = lambda e, g: e == g or (e is None and g == "n/a")   # INSTRUCTIONS allowed both for "does not apply"
        diff = {k: {"expected": s["expected_scores"][k], "scored": got[k]} for k in doc["vector"]
                if not same(s["expected_scores"][k], got[k])}
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
    with open(runs, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rep) + "\n")
    n = len(runs.read_text(encoding="utf-8").strip().splitlines())
    raw = path.parent / f"raw_output_run{n}.json"     # full per-slot output, saved as produced
    raw.write_text(json.dumps({"report": rep, "rows": rows}, indent=1, ensure_ascii=False, default=str) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(rep, indent=1))
    for r in rows:
        if r["mismatch"]:
            print(r["slot"], json.dumps(r["mismatch"]), "| path", r["path"])
    return rep, rows


if __name__ == "__main__":
    run(sys.argv[1])
