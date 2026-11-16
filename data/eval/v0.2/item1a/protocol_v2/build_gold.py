"""Final Item 1A v2 gold for the 525 test units, built from raw files that are never edited.

    python build_gold.py          (run from this folder)

label source, per unit:
  cross_model_agreed : retest/confirm unit where Claude v2 and ChatGPT gave the same raw label
  adjudicated        : retest/confirm unit where they differed; label from adjudication/adjudication_log.csv
  claude_v2_single   : one of the other 425 units; Claude v2 raw label only (no second labeller)
`ambiguous` stays a label; it is excluded from precision and recall, as the spec says.
"""
import collections
import csv

LABELS = {"material_added", "material_removed", "material_modified", "boilerplate", "ambiguous"}


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


claude = {r["hunk_id"]: r for r in read("labels_claude/v2_raw_all_test.csv")}
gpt = {}
for name in ("retest", "confirm"):
    for r in read(f"labels_external/gpt_{name}.csv"):
        gpt[r["hunk_id"]] = r
adj = {r["hunk_id"]: r for r in read("adjudication/adjudication_log.csv")}

assert len(claude) == 525
for hid, r in adj.items():
    assert r["claude_label"] == claude[hid]["label"] and r["gpt_label"] == gpt[hid]["label"], hid
assert set(adj) == {h for h in gpt if gpt[h]["label"] != claude[h]["label"]}, "every disagreement adjudicated, nothing else"

rows = []
for hid in sorted(claude):
    c = claude[hid]
    if hid in adj:
        label, source = adj[hid]["final_label"], "adjudicated"
    elif hid in gpt:
        label, source = c["label"], "cross_model_agreed"
    else:
        label, source = c["label"], "claude_v2_single"
    assert label in LABELS
    rows.append({"hunk_id": hid, "case": hid.split("-")[0], "label": label, "source": source,
                 "packet": c["packet"]})

with open("gold_item1a_v2_test.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print("units", len(rows))
print("by source", dict(collections.Counter(r["source"] for r in rows)))
print("labels", dict(collections.Counter(r["label"] for r in rows)))
