"""The frozen Item 1A files (labels, adjudication, gold, packets, code) match manifest_item1a.json."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "eval" / "v0.2" / "item1a"


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_manifest_hashes():
    m = json.loads((D / "manifest_item1a.json").read_text(encoding="utf-8"))
    for rel, h in m["files"].items():
        assert _sha(D / rel) == h, rel
    for rel, h in m["code"].items():
        assert _sha(ROOT / rel) == h, rel


def test_gold_complete():
    gold = list(csv.DictReader(open(D / "protocol_v2" / "gold_item1a_v2_test.csv", encoding="utf-8")))
    assert len(gold) == 525 == len({g["hunk_id"] for g in gold})
    assert sum(g["source"] == "adjudicated" for g in gold) == 25
