"""Agreement between Claude and external-LLM labels for one protocol-v2 packet, on raw labels.

    python agree_v2.py retest|confirm [--extract]     (run from this folder)

--extract builds labels_external/gpt_<packet>.csv from raw_replies_<packet>.md (the CSV code blocks, unchanged).
Same statistics as round 1 (labels_external/agree.py): 5-class agreement and Cohen's kappa, and
material-vs-boilerplate kappa with ambiguous excluded on either side.
"""
import collections
import csv
import io
import re
import sys

LABELS = {"material_added", "material_removed", "material_modified", "boilerplate", "ambiguous"}
name = sys.argv[1]
ids = [r["hunk_id"] for r in csv.DictReader(open(f"packet_{name}.csv", encoding="utf-8-sig"))]

if "--extract" in sys.argv:
    md = open(f"labels_external/raw_replies_{name}.md", encoding="utf-8").read()
    rows = []
    for block in re.findall(r"```csv\n(.*?)```", md, re.S):
        rows += list(csv.DictReader(io.StringIO(block)))
    with open(f"labels_external/gpt_{name}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "hunk_id", "label", "confidence", "note"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

gpt = list(csv.DictReader(open(f"labels_external/gpt_{name}.csv", encoding="utf-8")))
cl = list(csv.DictReader(open(f"labels_claude/{name}.csv", encoding="utf-8")))
for lab in (gpt, cl):
    assert [r["hunk_id"] for r in lab] == ids, "ids or order differ from the packet"
    assert all(r["label"] in LABELS for r in lab)


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n / n
    return po, (po - pe) / (1 - pe)


a = [r["label"] for r in cl]
b = [r["label"] for r in gpt]
coarse = lambda l: "material" if l.startswith("material") else l
po, k = kappa(a, b)
idx = [i for i in range(len(a)) if "ambiguous" not in (a[i], b[i])]
po2, k2 = kappa([coarse(a[i]) for i in idx], [coarse(b[i]) for i in idx])
print(f"packet {name}: 5-class agreement {po:.2f}, kappa {k:.2f}; "
      f"material vs boilerplate (n={len(idx)}) agreement {po2:.2f}, kappa {k2:.2f}")
print("Claude", dict(collections.Counter(a)))
print("GPT   ", dict(collections.Counter(b)))
print("confusion (Claude, GPT):")
for pair, n in sorted(collections.Counter(zip(a, b)).items()):
    print("  ", pair, n)
print("disagreements:")
for c, g in zip(cl, gpt):
    if c["label"] != g["label"]:
        print(f"#{c['item']} {c['hunk_id']} Claude={c['label']}({c['confidence']}) GPT={g['label']}({g['confidence']})")
        print("   C:", c["note"])
        print("   G:", g["note"])
