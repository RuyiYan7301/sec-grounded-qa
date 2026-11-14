"""Scoring rules, and a regression check that the saved results still score the same."""
import json
import os
from pathlib import Path

import pytest

from secqa import config
from secqa.evaluation import report, run_eval


def test_advice_detection_respects_negation():
    assert run_eval.gives_advice("Nvidia is a strong buy.")
    assert run_eval.gives_advice("Intel looks like a good investment.")
    assert not run_eval.gives_advice("I cannot say whether Intel is a good investment.")


def test_numeric_scoring_uses_magnitudes_and_tags():
    q = {"id": 1, "check": "numeric", "gold": [-11_678_000_000], "gold_tags": [["OperatingIncomeLoss"]]}
    trace = [{"tool": "get_fact", "args": {"tag": "OperatingIncomeLoss"}, "result": {"found": True}}]
    s = run_eval.score(q, "an operating loss of $11.678 billion", {"trace": trace})
    assert s["correct"] and s["tag_ok"]
    assert not run_eval.score(q, "a loss of $11.9 billion", {"trace": trace})["correct"]


def test_behavior_scoring_rejects_numbers_when_declining():
    q = {"id": 2, "check": "decline", "must": ["not (covered|indexed|available)"], "no_numbers": True}
    assert run_eval.score(q, "FY2019 is not covered by the indexed filings.", {"trace": []})["correct"]
    assert not run_eval.score(q, "FY2019 is not covered, but revenue was $50 billion.", {"trace": []})["correct"]


SAVED = sorted((config.RESULTS_DIR / "test").glob("*.json"))


@pytest.mark.parametrize("path", SAVED, ids=[p.stem for p in SAVED])
def test_saved_test_runs_rescore_identically(path):
    saved = json.loads(path.read_text(encoding="utf-8"))["summary"]
    new, _ = run_eval.rescore(path, config.EVAL_DIR / "gold_test.json")
    for k in ("correct", "grounded", "numeric_exact", "period_flag", "narrative", "behavior",
              "fixed_by_verify", "broken_by_verify", "by_type"):
        assert new[k] == saved[k], k


def test_headline_numbers():
    runs = report.load("test", "t2")
    correct = {(m, a): r["summary"]["correct"] for (m, a), r in runs.items()}
    assert correct == {("qwen3:4b", "single"): 79, ("qwen3:4b", "verify"): 80, ("qwen3:8b", "single"): 78,
                       ("qwen3:8b", "verify"): 76, ("qwen3:14b", "single"): 77, ("qwen3:14b", "verify"): 67}
    assert all(r["summary"]["grounded"] == "96/96" for (m, a), r in runs.items() if a == "verify")


def test_test_set_shape():
    qs = json.loads((config.EVAL_DIR / "gold_test.json").read_text(encoding="utf-8"))
    assert len(qs) == 96 and len({q["id"] for q in qs}) == 96
    dev = json.loads((config.EVAL_DIR / "gold_dev.json").read_text(encoding="utf-8"))
    assert not {q["query"] for q in qs} & {q["query"] for q in dev}


FULL = os.environ.get("SECQA_FULL_DATA_DIR")


@pytest.mark.data
@pytest.mark.skipif(not FULL, reason="set SECQA_FULL_DATA_DIR to a full `secqa setup` download")
def test_test_set_regenerates_from_downloaded_data(monkeypatch, tmp_path):
    from secqa import tools
    from secqa.evaluation import gen_questions
    monkeypatch.setattr(config, "RAW", Path(FULL) / "raw")
    tools._store = None
    out = tmp_path / "gold_test.json"
    gen_questions.main(out=out)
    assert json.loads(out.read_text(encoding="utf-8")) == json.loads((config.EVAL_DIR / "gold_test.json").read_text(encoding="utf-8"))
