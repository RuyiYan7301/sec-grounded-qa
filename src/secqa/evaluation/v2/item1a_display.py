"""Part B Item 1A, annotation protocol v2: what the labeller is shown. Display only.

    python -m secqa.evaluation.v2.item1a_display      # writes data/eval/v0.2/item1a/protocol_v2/

The gold unit stays the paragraph-level change unit of `item1a.py` (same ids, same text); nothing here
changes units, strata or labels. Round 1 (pilot) showed that an annotator who sees only the two
neighbouring paragraphs cannot tell a deleted sentence from one merged into another paragraph. v2
therefore shows, for each side of a unit, the three paragraphs of the *other* filing where its
sentences most likely went (or came from), with a score and the paragraph position. No threshold
hides a candidate.

Score of a candidate paragraph P for unit text T: split T into sentences; for each sentence take its
best SequenceMatcher ratio against the sentences of P; the score is the character-weighted mean.
1.0 means every sentence of T appears verbatim in P.

Two packets, labelled with the same guideline (v2) and the same display:
  retest:  the 50 pilot units (protocol-repair retest; its agreement is not the confirmation result,
           because the v2 rules were written after reading the pilot disagreements);
  confirm: 50 new test units, stratified like the pilot with a new seed, excluding the pilot units.
"""
import csv
import difflib
import hashlib
import json
import re

from ... import config
from . import gen_cases, item1a

OUT = config.EVAL_DIR / "v0.2" / "item1a" / "protocol_v2"
TOP_K = 3
CONFIRM_SEED = 1115          # chosen before the confirmation sample was drawn; recorded in protocol.json
SENT_SPLIT = re.compile(r"(?<=[.;:!?])\s+(?=[A-Z(\"“•])")
DISPLAY = {"unit": "unchanged: item1a.py paragraph units",
           "candidates": f"top {TOP_K} paragraphs of the other filing, no threshold",
           "score": "character-weighted mean over unit sentences of the best SequenceMatcher(autojunk=False).ratio "
                    "against the candidate paragraph's sentences",
           "sentence_split": SENT_SPLIT.pattern,
           "modified_units": "the paired paragraph is excluded from the candidates (it is already shown as the other side)"}


def sentences(p):
    return [s for s in SENT_SPLIT.split(p) if s.strip()]


def _ratio(x, y):
    m = difflib.SequenceMatcher(None, x, y, autojunk=False)
    if m.real_quick_ratio() < 0.3 or m.quick_ratio() < 0.3:
        return 0.0
    return m.ratio()


def candidates(text, other, exclude=None, k=TOP_K):
    """[(score, index, paragraph)] for the k best paragraphs of `other` (list of paragraphs)."""
    sents = sentences(text)
    w = [len(s) for s in sents]
    other_s = [sentences(p) for p in other]
    scored = []
    for j, ps in enumerate(other_s):
        if exclude is not None and j == exclude:
            continue
        best = [max((_ratio(s, t) for t in ps), default=0.0) for s in sents]
        scored.append((sum(b * x for b, x in zip(best, w)) / sum(w), j, other[j]))
    scored.sort(key=lambda r: (-r[0], r[1]))
    return scored[:k]


def fmt(cands, n_other, which):
    if not cands:
        return ""
    return "\n\n".join(f"[{r}] match {s:.2f} | {which} filing, paragraph {j + 1} of {n_other}\n{p}"
                       for r, (s, j, p) in enumerate(cands, 1))


def case_paragraphs(case):
    t, y1, y2, _ = gen_cases.CASES[case]
    return item1a.paragraphs(item1a.item1a_text(t, y1)), item1a.paragraphs(item1a.item1a_text(t, y2))


def position(par, lst):
    try:
        return lst.index(par)
    except ValueError:
        return None


def row(k, h, paras):
    a, b = paras[h["case"]]
    t, y1, y2, _ = gen_cases.CASES[h["case"]]
    f1, f2 = gen_cases.target_filing(t, y1), gen_cases.target_filing(t, y2)
    before, after = "\n".join(h["before"]), "\n".join(h["after"])
    ia = position(h["before"][0], a) if h["before"] else None
    ib = position(h["after"][0], b) if h["after"] else None
    # the filing text must reproduce the frozen units exactly, or the positions and candidates are wrong
    assert (ia is not None) == bool(h["before"]) and (ib is not None) == bool(h["after"]), h["id"]
    pos = []
    if ia is not None:
        pos.append(f"earlier filing paragraph {ia + 1} of {len(a)}")
    if ib is not None:
        pos.append(f"later filing paragraph {ib + 1} of {len(b)}")
    return {
        "item": k, "hunk_id": h["id"], "company": t,
        "earlier_filing": f"FY{y1} 10-K, filed {f1['filed']}, {f1['url']}",
        "later_filing": f"FY{y2} 10-K, filed {f2['filed']}, {f2['url']}",
        "position of the text to label": "; ".join(pos),
        "CONTEXT ONLY - paragraph before (unchanged)": h["context_before"],
        "LABEL THIS - EARLIER TEXT (removed or changed)": before or "(none: text added)",
        "LABEL THIS - LATER TEXT (added or changed)": after or "(none: text removed)",
        "CONTEXT ONLY - paragraph after (unchanged)": h["context_after"],
        "CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)":
            fmt(candidates(before, b, exclude=ib), len(b), "later") if before else "",
        "CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)":
            fmt(candidates(after, a, exclude=ia), len(a), "earlier") if after else "",
        "label": "", "confidence (1-3)": "", "note": "",
    }


def write_packet(path, rows):
    longest = max(len(v) for r in rows for v in map(str, r.values()))
    assert longest < 32000, f"cell too long for Excel: {longest}"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:   # BOM so Excel opens it as UTF-8
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    every = []
    for case in gen_cases.CASES:
        every += json.loads((item1a.OUT / f"{case}.hunks.json").read_text(encoding="utf-8"))["hunks"]
    by_id = {h["id"]: h for h in every}
    pilot_ids = json.loads((item1a.OUT / "second_annotator_sample.json").read_text(encoding="utf-8"))["ids"]
    rest = [h for h in every if h["id"] not in set(pilot_ids)]
    confirm = item1a.sample(rest, n=item1a.SAMPLE_N, seed=CONFIRM_SEED)
    assert not set(h["id"] for h in confirm) & set(pilot_ids)
    paras = {c: case_paragraphs(c) for c in gen_cases.CASES}
    out = {}
    for name, units in (("retest", [by_id[i] for i in pilot_ids]), ("confirm", confirm)):
        path = OUT / f"packet_{name}.csv"
        write_packet(path, [row(k, h, paras) for k, h in enumerate(units, 1)])
        out[name] = {"path": path.name, "sha256": sha(path), "n": len(units), "ids": [h["id"] for h in units]}
        print(name, len(units), path.name)
    (OUT / "samples.json").write_text(json.dumps(
        {"retest": {"source": "item1a/second_annotator_sample.json (pilot, seed 2603)", **out["retest"]},
         "confirm": {"seed": CONFIRM_SEED, "excludes": "the 50 pilot units", "strata": "item1a.sample, same as pilot",
                     **out["confirm"]},
         "display": DISPLAY}, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
