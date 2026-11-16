"""Item 1A v0.3 held-out reference: parse labeller B (Gemini) raw replies, compute A-B agreement, write the
adjudication packet for the units where A and B disagree (docs/item1a-v0.3-plan.md).

    python -m secqa.evaluation.v03_item1a_consensus parse      # labels_gemini/labels.csv + agreement.json
    python -m secqa.evaluation.v03_item1a_consensus adjudication-packet

Parsing: each saved reply is Gemini's own copy of a CSV code block; a row is `item,hunk_id,label,confidence,
note`, and the note may hold unquoted commas, so a row is split at its first four commas only (a quoted note
is unquoted). Rows are checked against the packets: every unit exactly once, the hunk_id matching the item
number. Agreement is computed on the raw labels, before any adjudication: 5-class raw agreement and Cohen's
kappa, and material-vs-boilerplate kappa on units neither labeller called ambiguous.
"""
import collections
import csv
import json
import random
import re
import sys

from .. import config

D = config.EVAL_DIR / "v0.3" / "item1a"
LABELS = ("material_added", "material_removed", "material_modified", "boilerplate", "ambiguous")
ROW = re.compile(r"^(\d+),([A-Z]+_FY\d{4}-u\d{3}),([a-z_]+),([123]),(.*)$")
ADJ_SEED = 1117


def packet_units():
    units = {}
    for p in sorted((D / "packets").glob("packet_*_FY2026_[0-9].csv")):
        with open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                units[int(r["item"]), r["hunk_id"].split("-")[0]] = r
    return units


def parse():
    rows = {}
    for path in sorted((D / "labels_gemini").glob("raw_replies_*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = ROW.match(line.strip())
            if not m:
                continue
            item, hid, lab, conf, note = m.groups()
            note = note[1:-1].replace('""', '"') if len(note) >= 2 and note[0] == note[-1] == '"' else note
            if hid in rows:
                raise SystemExit(f"{hid} labelled twice ({path.name})")
            rows[hid] = {"item": int(item), "hunk_id": hid, "label": lab, "confidence": conf, "note": note,
                         "source_file": path.name}
    units = packet_units()
    want = {r["hunk_id"]: k[0] for k, r in units.items()}
    missing, extra = sorted(set(want) - set(rows)), sorted(set(rows) - set(want))
    wrong_item = [h for h, r in rows.items() if h in want and want[h] != r["item"]]
    bad = [h for h, r in rows.items() if r["label"] not in LABELS]
    assert not (missing or extra or wrong_item or bad), (missing, extra, wrong_item, bad)
    order = sorted(rows.values(), key=lambda r: (r["hunk_id"].split("-")[0], r["item"]))
    with open(D / "labels_gemini" / "labels.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "hunk_id", "label", "confidence", "note", "source_file"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(order)
    a = {r["hunk_id"]: r["label"] for r in csv.DictReader(open(D / "gold_item1a_v03_heldout.csv", encoding="utf-8"))}
    b = {r["hunk_id"]: r["label"] for r in order}
    out = {"n": len(a), "five_class": agreement(a, b, LABELS)}
    mb = {h for h in a if a[h] != "ambiguous" and b[h] != "ambiguous"}
    coarse = lambda x: "material" if x.startswith("material") else x
    out["material_vs_boilerplate"] = agreement({h: coarse(a[h]) for h in mb}, {h: coarse(b[h]) for h in mb},
                                               ("material", "boilerplate"))
    out["by_case"] = {c: agreement({h: a[h] for h in a if h.startswith(c)}, {h: b[h] for h in a if h.startswith(c)}, LABELS)
                      for c in ("MSFT_FY2026", "ORCL_FY2026")}
    out["confusion"] = {f"{x}|{y}": n for (x, y), n in sorted(collections.Counter((a[h], b[h]) for h in a).items())}
    out["disagreements"] = sorted(h for h in a if a[h] != b[h])
    (D / "agreement_claude_gemini.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in out.items() if k != "disagreements"}, indent=1))
    print("disagreements:", len(out["disagreements"]))


def agreement(a, b, cats):
    keys = sorted(a)
    n = len(keys)
    po = sum(a[k] == b[k] for k in keys) / n
    pa, pb = collections.Counter(a[k] for k in keys), collections.Counter(b[k] for k in keys)
    pe = sum(pa[c] * pb[c] for c in cats) / (n * n)
    return {"n": n, "raw_agreement": round(po, 4), "kappa": round((po - pe) / (1 - pe), 4) if pe < 1 else None}


def adjudication_packet():
    """Disagreed units only, with the two labels as 'label 1' / 'label 2' in a seeded random order; the key
    (which label came from which model) is written separately and not shown to the adjudicator."""
    agr = json.loads((D / "agreement_claude_gemini.json").read_text(encoding="utf-8"))
    a = {r["hunk_id"]: r["label"] for r in csv.DictReader(open(D / "gold_item1a_v03_heldout.csv", encoding="utf-8"))}
    b = {r["hunk_id"]: r["label"] for r in csv.DictReader(open(D / "labels_gemini" / "labels.csv", encoding="utf-8"))}
    units = {r["hunk_id"]: r for r in packet_units().values()}
    rng = random.Random(ADJ_SEED)
    rows, key = [], {}
    for k, h in enumerate(agr["disagreements"], 1):
        pair = [("claude", a[h]), ("gemini", b[h])]
        rng.shuffle(pair)
        key[h] = {"label 1": pair[0][0], "label 2": pair[1][0]}
        u = units[h]
        rows.append({"item": k, "hunk_id": h} | {c: u[c] for c in list(u)[2:] if c not in ("label", "confidence (1-3)", "note")}
                    | {"label 1": pair[0][1], "label 2": pair[1][1], "decision": "", "reason": ""})
    path = D / "adjudication" / "packet_adjudication.csv"
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (D / "adjudication" / "key_label_order.json").write_text(json.dumps({"seed": ADJ_SEED, "key": key}, indent=1) + "\n",
                                                             encoding="utf-8", newline="\n")
    print(len(rows), "units to adjudicate ->", path.name)


ADJ_ROW = re.compile(r"^(\d+),([A-Z]+_FY\d{4}-u\d{3}),(1|2|ambiguous),(.*)$")


def reference():
    """Consensus reference: A = B -> that label (high_confidence); otherwise the adjudicator's pick
    (adjudicated), or ambiguous if it picked ambiguous."""
    rows = {}
    for path in sorted((D / "adjudication").glob("raw_replies_deepseek_*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = ADJ_ROW.match(line.strip())
            if m:
                assert m.group(2) not in rows, m.group(2)
                rows[m.group(2)] = {"decision": m.group(3), "reason": m.group(4).strip('"'), "source_file": path.name}
    agr = json.loads((D / "agreement_claude_gemini.json").read_text(encoding="utf-8"))
    assert set(rows) == set(agr["disagreements"]), (set(agr["disagreements"]) ^ set(rows))
    key = json.loads((D / "adjudication" / "key_label_order.json").read_text(encoding="utf-8"))["key"]
    a = {r["hunk_id"]: r["label"] for r in csv.DictReader(open(D / "gold_item1a_v03_heldout.csv", encoding="utf-8"))}
    b = {r["hunk_id"]: r["label"] for r in csv.DictReader(open(D / "labels_gemini" / "labels.csv", encoding="utf-8"))}
    by = {"claude": a, "gemini": b}
    out, sided = [], collections.Counter()
    for h in sorted(a, key=lambda x: (x.split("-")[0], x)):
        if a[h] == b[h]:
            out.append({"hunk_id": h, "case": h.split("-")[0], "label": a[h], "source": "high_confidence",
                        "claude": a[h], "gemini": b[h], "adjudication": ""})
            continue
        d = rows[h]["decision"]
        if d == "ambiguous":
            lab, who = "ambiguous", "ambiguous"
        else:
            who = key[h][f"label {d}"]
            lab = by[who][h]
        sided[who] += 1
        out.append({"hunk_id": h, "case": h.split("-")[0], "label": lab, "source": "adjudicated",
                    "claude": a[h], "gemini": b[h], "adjudication": f"{d} ({who})"})
    path = D / "reference_item1a_v03_heldout.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    summary = {"n": len(out), "by_source": dict(collections.Counter(r["source"] for r in out)),
               "adjudicator_sided_with": dict(sided),
               "by_label": dict(collections.Counter(r["label"] for r in out)),
               "high_confidence_by_label": dict(collections.Counter(r["label"] for r in out if r["source"] == "high_confidence"))}
    (D / "reference_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    {"parse": parse, "adjudication-packet": adjudication_packet, "reference": reference}[sys.argv[1]]()
