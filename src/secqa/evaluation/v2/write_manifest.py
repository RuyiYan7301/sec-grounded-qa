"""Overall freeze manifest of the v0.2 benchmark.

    python -m secqa.evaluation.v2.write_manifest            # writes data/eval/v0.2/manifest.json
    python -m secqa.evaluation.v2.write_manifest --check    # recomputes every hash and reports mismatches

Hash rule: files under data/eval/v0.2/item1a/ are stored byte for byte (.gitattributes -text) and hashed
as they are; every other file is stored as text with LF line endings, so CRLF is normalised to LF before
hashing. With that rule a checkout on any platform reproduces the hashes.

Raw inputs (companyfacts, submissions, converted 10-K texts) are not in the repository; their hashes are
recorded from the data directory used to build the benchmark, so a rebuild can show it used the same data.
"""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from ... import config

ROOT = config.REPO_ROOT
EVAL = config.EVAL_DIR / "v0.2"
OUT = EVAL / "manifest.json"
CODE = sorted([*(p.relative_to(ROOT).as_posix() for p in (ROOT / "src/secqa/evaluation/v2").glob("*.py")),
               # the Part A scorer imports these v0.1 modules (numbers_in, gives_advice): frozen with it
               "src/secqa/agent.py", "src/secqa/evaluation/run_eval.py", "src/secqa/ontology.py",
               "data/metric_ontology.yaml", "data/metric_ontology.lock.json", ".gitattributes",
               "docs/benchmark-v0.2.md", "docs/partB-scoring.md",
               # audits written by verify_gold_text, partb_provenance and sensitivity_b
               *(p.relative_to(ROOT).as_posix() for p in (ROOT / "results/v0.2").glob("*") if p.is_file())])


def file_sha(path):
    b = Path(path).read_bytes()
    rel = Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    if not rel.startswith("data/eval/v0.2/item1a/"):
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def eval_files():
    return sorted(p for p in EVAL.rglob("*") if p.is_file() and p != OUT)


def raw_inputs():
    raw = config.RAW
    files = sorted([*raw.glob("companyfacts_*.json"), *raw.glob("submissions_*.json"),
                    *(raw / "filings").glob("*.txt")])
    return {p.relative_to(raw).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def counts():
    qa_t = json.loads((EVAL / "qa_test.json").read_text(encoding="utf-8"))
    qa_d = json.loads((EVAL / "qa_dev.json").read_text(encoding="utf-8"))
    b = {}
    for name in ("NVDA_FY2025", "INTC_FY2025", "AVGO_FY2024", "CSCO_FY2024"):
        doc = json.loads((EVAL / "cases" / f"{name}.numeric.json").read_text(encoding="utf-8"))
        b[name] = {"split": doc["split"], **Counter(i["label"] for i in doc["items"])}
    rc = json.loads((EVAL / "cases" / "revision_stability_controls.json").read_text(encoding="utf-8"))["items"]
    return {"A_test": dict(Counter(i["layer"] for i in qa_t)), "A_dev": len(qa_d),
            "A_noise_subset": len(json.loads((EVAL / "noise_subset.json").read_text(encoding="utf-8"))["ids"]),
            "B_numeric": b, "B_revision_controls": dict(Counter(r["label"] for r in rc)),
            "item1a_test_units": 525, "item1a_dev_units": 66}


def build():
    head = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, cwd=ROOT).strip()
    lock = lambda p: json.loads((EVAL / p).read_text(encoding="utf-8"))
    return {
        "benchmark": "secqa-v0.2",
        "frozen_on": "2026-11-15",
        "git_commit_before_manifest": head,
        "snapshot": config.SNAPSHOT,
        "hash_rule": "sha256; files under data/eval/v0.2/item1a/ byte for byte, all others with CRLF normalised to LF",
        "statement": ("Prospective frozen benchmark, not a blind test: questions, gold answers, labels and both scorers "
                      "are fixed before any v0.2 engine code exists, and no test output is used for tuning."),
        "scorers": {"part_a": {"version": lock("scorer_lock.json")["version"], "lock": "scorer_lock.json"},
                    "part_b": {"version": lock("partB/partB_lock.json")["version"], "lock": "partB/partB_lock.json"},
                    "item1a_gold": {"manifest": "item1a/manifest_item1a.json"}},
        "reliability_and_checks": {
            "scorer_calibration": "rounds 1-4 synthetic: development and defect discovery only, never reported as accuracy",
            "external_checks_after_freeze": ["Part A: 80 real outputs (40-item noise subset x v0.1, v0.2), judged without scores",
                                             "Part B: the three test-case packets reviewed by hand"],
            "item1a_reliability": "cross-model agreement on the confirm sample: kappa 0.63 (95% CI 0.46-0.80); not human annotation",
            "gold_text_audits": ["Part A: 227/227 gold cells located in the cited accession's 10-K text",
                                 "Part B: 258 case values, 69 revision controls (as presented and first reported), "
                                 "2 micro-case values automatically located; 16 randomly sampled contexts (seed 2027) read by hand"]},
        "counts": counts(),
        "code": {p: file_sha(ROOT / p) for p in CODE},
        "files": {p.relative_to(ROOT).as_posix(): file_sha(p) for p in eval_files()},
        "raw_inputs_sha256": raw_inputs(),
    }


def check():
    m = json.loads(OUT.read_text(encoding="utf-8"))
    bad = [p for p, h in {**m["code"], **m["files"]}.items() if not (ROOT / p).exists() or file_sha(ROOT / p) != h]
    extra = [p.relative_to(ROOT).as_posix() for p in eval_files() if p.relative_to(ROOT).as_posix() not in m["files"]]
    raw = raw_inputs() if config.RAW.exists() else {}
    raw_bad = [k for k, h in m["raw_inputs_sha256"].items() if raw and raw.get(k) != h]
    print(f"code+files {len(m['code']) + len(m['files'])}, mismatched {len(bad)}, unlisted {len(extra)}, "
          f"raw inputs checked {len(raw)}, raw mismatched {len(raw_bad)}")
    for p in bad + extra + raw_bad:
        print("  ", p)
    return not (bad or extra or raw_bad)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    m = build()
    OUT.write_text(json.dumps(m, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(len(m["code"]), "code files,", len(m["files"]), "eval files,", len(m["raw_inputs_sha256"]), "raw inputs")
