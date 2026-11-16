"""Development check: score a calibration file that is no longer held out (round 1, and round 2 after it
failed) with the current scorer. Not a calibration run: it writes dev_check.json next to the file and
never touches runs.jsonl.

    python -m secqa.evaluation.v2.calibration_dev_check data/eval/v0.2/calibration_r2/filled.json
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

import yaml

from ... import config
from . import score


def main(path):
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    ont = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    same = lambda e, g: e == g or (e is None and g == "n/a")
    rows, per_field = [], collections.Counter()
    for s in doc["slots"]:
        got = score.score_item(s["item"], s["record"], s.get("qualified_alternative"), ont)
        diff = {k: [s["expected_scores"][k], got[k]] for k in doc["vector"] if not same(s["expected_scores"][k], got[k])}
        per_field.update(diff.keys())
        rows.append({"slot": s["slot"], "mismatch": diff, "record_format_ok": got["record_format_ok"]})
    out = {"kind": "development check, not a calibration run",
           "scorer_sha256": hashlib.sha256(Path(score.__file__).read_bytes()).hexdigest(),
           "file": path.name, "slots": len(rows), "slots_matching": sum(not r["mismatch"] for r in rows),
           "mismatch_by_field": dict(per_field), "rows": rows}
    (path.parent / "dev_check.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(path.parent.name, "matching", out["slots_matching"], "/", len(rows), dict(per_field))
    for r in rows:
        if r["mismatch"]:
            print("  ", r["slot"], r["mismatch"])


if __name__ == "__main__":
    main(sys.argv[1])
