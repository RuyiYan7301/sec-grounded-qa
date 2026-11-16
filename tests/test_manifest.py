"""The overall v0.2 freeze manifest matches the repository (code and eval files)."""
import json

from secqa.evaluation.v2 import write_manifest as W


def test_manifest_hashes():
    m = json.loads(W.OUT.read_text(encoding="utf-8"))
    for rel, sha in {**m["code"], **m["files"]}.items():
        assert W.file_sha(W.ROOT / rel) == sha, rel


def test_no_unlisted_eval_files():
    m = json.loads(W.OUT.read_text(encoding="utf-8"))
    assert {p.relative_to(W.ROOT).as_posix() for p in W.eval_files()} == set(m["files"])
