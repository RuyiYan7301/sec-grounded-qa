"""The Part A scorer, plan schema and qualified alternatives match data/eval/v0.2/scorer_lock.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scorer_lock():
    lock = json.loads((ROOT / "data" / "eval" / "v0.2" / "scorer_lock.json").read_text(encoding="utf-8"))
    for rel, sha in lock["files"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, rel


def test_scorer_version_matches_lock():
    from secqa.evaluation.v2 import score
    lock = json.loads((ROOT / "data" / "eval" / "v0.2" / "scorer_lock.json").read_text(encoding="utf-8"))
    assert score.V == lock["version"]
