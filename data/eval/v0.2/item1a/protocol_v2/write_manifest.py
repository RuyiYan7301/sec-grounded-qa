"""Writes data/eval/v0.2/item1a/manifest_item1a.json: sha256 of every Item 1A file and of its code.

    python data/eval/v0.2/item1a/protocol_v2/write_manifest.py     (run from the repository root)
"""
import collections
import csv
import hashlib
import json
import pathlib
import subprocess

root = pathlib.Path(".")
d = root / "data/eval/v0.2/item1a"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {p.relative_to(d).as_posix(): sha(p) for p in sorted(d.rglob("*"))
         if p.is_file() and p.name != "manifest_item1a.json"}
code = ["src/secqa/evaluation/v2/item1a.py", "src/secqa/evaluation/v2/item1a_display.py",
        "src/secqa/evaluation/v2/item1a_rest_packet.py"]
gold = list(csv.DictReader(open(d / "protocol_v2/gold_item1a_v2_test.csv", encoding="utf-8")))
m = {
    "benchmark": "secqa-v0.2, part B Item 1A",
    "frozen_on": "2026-11-15",
    "git_commit_before_freeze": subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip(),
    "scope": "Item 1A only. Part A QA and part B numeric are not frozen by this file; "
             "data/eval/v0.2/manifest.json is written when they are.",
    "protocol": "protocol_v2/protocol.json (locked before any v2 label)",
    "reliability": {
        "claim": "cross-model agreement (Claude vs ChatGPT, model reported by the owner as '5.6 sol'); "
                 "not independent human annotation",
        "reported_figure": "confirm packet only: raw agreement 0.76, Cohen's kappa 0.63 (bootstrap 95% CI 0.46-0.80), "
                           "material-vs-boilerplate kappa 0.78 on 46 non-ambiguous units",
        "not_reported_as_result": ["round-1 pilot (kappa 0.39, protocol v1)",
                                   "retest (kappa 0.56, pilot units after protocol repair)",
                                   "dev (no agreement computed)"],
    },
    "gold": {
        "path": "protocol_v2/gold_item1a_v2_test.csv", "n": len(gold),
        "by_source": dict(collections.Counter(r["source"] for r in gold)),
        "by_label": dict(collections.Counter(r["label"] for r in gold)),
        "built_by": "protocol_v2/build_gold.py from labels_claude/v2_raw_all_test.csv, labels_external/gpt_*.csv, "
                    "adjudication/adjudication_log.csv",
        "note": "claude_v2_single units have one labeller only",
    },
    "dev_labels": {"path": "protocol_v2/labels_claude/dev.csv", "n": 66, "use": "implementation and debugging only"},
    "archive_v1": "labels_claude/, item1a_guideline (v1, in data/eval/v0.2/), second_annotator_* and labels_external/ "
                  "(round 1) are kept unchanged as protocol history",
    "rule": "test gold and test packets do not change after this point; system outputs on the test units are not "
            "used to change rules or labels",
    "code": {c: sha(root / c) for c in code},
    "files": files,
}
(d / "manifest_item1a.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(len(files), "files", m["git_commit_before_freeze"])
