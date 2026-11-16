"""Part B scorer, packet schema and Part B gold match data/eval/v0.2/partB/partB_lock.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "data" / "eval" / "v0.2" / "partB" / "partB_lock.json").read_text(encoding="utf-8"))


def test_partb_lock_hashes():
    for rel, sha in LOCK["files"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, rel


def test_partb_scorer_version():
    from secqa.evaluation.v2 import partb_score
    assert partb_score.V == LOCK["version"]
