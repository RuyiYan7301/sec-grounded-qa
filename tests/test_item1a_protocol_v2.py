"""Item 1A annotation protocol v2 is locked: its guideline, display code, packets and prompt cannot change silently."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "eval" / "v0.2" / "item1a" / "protocol_v2"


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_protocol_hashes():
    proto = json.loads((P / "protocol.json").read_text(encoding="utf-8"))
    assert _sha(P / proto["guideline"]["path"]) == proto["guideline"]["sha256"]
    assert _sha(P / proto["external_prompt"]["path"]) == proto["external_prompt"]["sha256"]
    for key in ("display_code", "unit_code"):
        assert _sha(ROOT / proto[key]["path"]) == proto[key]["sha256"], key
    for name, spec in proto["packets"].items():
        assert _sha(P / spec["path"]) == spec["sha256"], name


def test_confirm_sample_disjoint_from_pilot():
    s = json.loads((P / "samples.json").read_text(encoding="utf-8"))
    pilot = json.loads((P.parent / "second_annotator_sample.json").read_text(encoding="utf-8"))["ids"]
    assert s["retest"]["ids"] == pilot
    assert len(s["confirm"]["ids"]) == 50 and not set(s["confirm"]["ids"]) & set(pilot)


def test_packets_carry_no_labels():
    for name in ("packet_retest.csv", "packet_confirm.csv"):
        rows = list(csv.DictReader(open(P / name, encoding="utf-8-sig")))
        assert len(rows) == 50
        assert all(not r["label"] and not r["confidence (1-3)"] and not r["note"] for r in rows)
        assert not any("stratum" in c or "claude" in c.lower() for c in rows[0])
