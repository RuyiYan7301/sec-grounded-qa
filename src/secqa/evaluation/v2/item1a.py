"""Part B Item 1A: candidate change units between two 10-Ks, and the second-annotator sample.

    python -m secqa.evaluation.v2.item1a          # writes data/eval/v0.2/item1a/

Alignment, in two passes over paragraphs (lines of the converted 10-K text):
  1. exact: difflib.SequenceMatcher on whole paragraphs finds the unchanged ones;
  2. inside each changed block, paragraphs are paired by a monotonic alignment that maximises the
     total character similarity of pairs with similarity >= PAIR_MIN.
Each pair is a `modified` unit, each unpaired earlier paragraph a `removed` unit, each unpaired
later paragraph an `added` unit. An added or removed paragraph that appears verbatim on the other
side is `moved`. Units are what gets labelled. The provisional strata used for sampling come from
the text alone (type, similarity, whether the text only moved); they are not labels.
"""
import csv
import difflib
import json
import random
import re
from collections import Counter

from ... import config, filings
from . import gen_cases

OUT = config.EVAL_DIR / "v0.2" / "item1a"
PAIR_MIN = 0.5
MOVED_MIN = 0.8   # an added/removed paragraph this similar to one elsewhere on the other side: moved_edited
ALIGN = {"unit": "paragraph", "min_paragraph_chars": 30, "pass1": "difflib.SequenceMatcher(autojunk=False) on paragraphs",
         "pass2": f"monotonic pairing inside changed blocks, SequenceMatcher.ratio >= {PAIR_MIN}",
         "normalise": "collapse whitespace, drop page furniture (page numbers, 'Table of Contents', running headers), join a line starting in lower case to the previous paragraph (page-break continuation)",
         "intel_section_end": "first line equal to 'Other Key Information' or 'Sales and Marketing'"}
SAMPLE_N, SAMPLE_SEED = 50, 2603
TITLE_END = ("Other Key Information", "Sales and Marketing")   # see item1a_text
FURNITURE = re.compile(r"^(table of contents|\d{1,3}|page \d+|.*\|\s*\d{4} form 10-k\s*\|\s*\d+)$", re.I)


def item1a_text(ticker, fy):
    text = (filings.text_dir() / f"{ticker}_FY{fy}.txt").read_text(encoding="utf-8")
    body = filings.split_items(text).get("1A", "")
    if len(body) < 2000:
        # Intel: section found by title. Its FY2024 10-K has no "Other Key Information" heading, so the
        # system's splitter (unchanged, v0.1 indexes it this way) runs on into sales, market risk,
        # cybersecurity and properties. The benchmark cuts at the first heading that follows the risk factors.
        body = filings.split_by_title(text, "1A")
        lines = body.split("\n")
        cut = next((k for k in range(1, len(lines)) if lines[k] in TITLE_END), len(lines))
        body = "\n".join(lines[:cut])
    return body


def paragraphs(body):
    """Paragraphs of the section. A page break splits a paragraph into two lines with page furniture
    between them; a line that starts in lower case continues the previous paragraph and is joined to it."""
    out = []
    for ln in body.split("\n"):
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln or FURNITURE.match(ln):
            continue
        if out and ln[0].islower():
            out[-1] = out[-1] + " " + ln
        else:
            out.append(ln)
    return [p for p in out if len(p) >= ALIGN["min_paragraph_chars"]]


def _sim(x, y):
    m = difflib.SequenceMatcher(None, x, y, autojunk=False)
    return m.ratio() if m.real_quick_ratio() >= PAIR_MIN and m.quick_ratio() >= PAIR_MIN else 0.0


def pair(a, b):
    """Monotonic pairing of two paragraph lists: [(i or None, j or None, sim)] in document order."""
    n, m = len(a), len(b)
    sim = [[_sim(a[i], b[j]) for j in range(m)] for i in range(n)]
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            s = sim[i][j]
            best[i][j] = max(best[i + 1][j], best[i][j + 1], best[i + 1][j + 1] + s if s >= PAIR_MIN else 0.0)
    out, i, j = [], 0, 0
    while i < n or j < m:
        if i < n and j < m and sim[i][j] >= PAIR_MIN and best[i][j] == best[i + 1][j + 1] + sim[i][j]:
            out.append((i, j, sim[i][j]))
            i, j = i + 1, j + 1
        elif i < n and (j == m or best[i][j] == best[i + 1][j]):
            out.append((i, None, 0.0))
            i += 1
        else:
            out.append((None, j, 0.0))
            j += 1
    return out


def hunks(case):
    t, y1, y2, split = gen_cases.CASES[case]
    a, b = paragraphs(item1a_text(t, y1)), paragraphs(item1a_text(t, y2))
    sa, sb = set(a), set(b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        for pi, pj, sim in pair(a[i1:i2], b[j1:j2]):
            gi = None if pi is None else i1 + pi
            gj = None if pj is None else j1 + pj
            before = [a[gi]] if gi is not None else []
            after = [b[gj]] if gj is not None else []
            kind = "modified" if before and after else "removed" if before else "added"
            moved = (kind == "removed" and before[0] in sb) or (kind == "added" and after[0] in sa)
            # An added or removed paragraph may reappear, edited, elsewhere in the other filing (a
            # reorganised section). The closest paragraph anywhere on the other side is shown to the annotator.
            nearest = None
            if kind != "modified" and not moved:
                text, other = (before[0], b) if kind == "removed" else (after[0], a)
                score, best = max(((_sim(text, o), o) for o in other), default=(0.0, None))
                if score >= MOVED_MIN:
                    nearest = {"text": best, "similarity": round(score, 3)}
            stratum = ("moved" if moved else "moved_edited" if nearest else kind if kind != "modified" else
                       "modified_high_sim" if sim >= 0.9 else "modified_mid_sim" if sim >= 0.7 else "modified_low_sim")
            ctx_b = a[gi - 1] if gi else (a[i1 - 1] if i1 else "")
            ctx_a = b[gj + 1] if gj is not None and gj + 1 < len(b) else (b[j2] if j2 < len(b) else "")
            out.append({"id": f"{case}-u{len(out) + 1:03d}", "case": case, "split": split, "type": kind,
                        "stratum": stratum, "similarity": round(sim, 3),
                        "words": len(" ".join(before + after).split()),
                        "context_before": ctx_b, "before": before, "after": after, "context_after": ctx_a,
                        "nearest_on_other_side": nearest})
    return out


def sample(all_hunks, n=SAMPLE_N, seed=SAMPLE_SEED):
    """Stratified by (case, stratum); every non-empty stratum of every test case gets at least one hunk,
    the rest is allocated in proportion to stratum size."""
    test = [h for h in all_hunks if h["split"] == "test"]
    groups = {}
    for h in test:
        groups.setdefault((h["case"], h["stratum"]), []).append(h)
    rng = random.Random(seed)
    for g in groups.values():
        rng.shuffle(g)
    take = {k: 1 for k in groups}
    rest = n - len(take)
    weights = {k: len(v) - 1 for k, v in groups.items()}
    total = sum(weights.values())
    for k in sorted(groups, key=lambda k: -weights[k]):
        extra = min(round(rest * weights[k] / total), len(groups[k]) - take[k]) if total else 0
        take[k] += extra
    keys = sorted(groups)
    while sum(take.values()) > n:
        k = max(keys, key=lambda k: take[k])
        take[k] -= 1
    while sum(take.values()) < n:
        k = max((k for k in keys if take[k] < len(groups[k])), key=lambda k: len(groups[k]) - take[k])
        take[k] += 1
    picked = [h for k in keys for h in groups[k][:take[k]]]
    rng.shuffle(picked)   # the annotator sees no case or stratum order
    return picked


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    every = []
    for case, (t, y1, y2, split) in gen_cases.CASES.items():
        hs = hunks(case)
        every += hs
        src = {"ticker": t, "from": f"FY{y1}", "to": f"FY{y2}", "split": split,
               "from_filing": gen_cases.target_filing(t, y1), "to_filing": gen_cases.target_filing(t, y2),
               "alignment": ALIGN}
        (OUT / f"{case}.hunks.json").write_text(json.dumps({**src, "hunks": hs}, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8", newline="\n")
        print(case, len(hs), dict(Counter(h["stratum"] for h in hs)))
    picked = sample(every)
    (OUT / "second_annotator_sample.json").write_text(
        json.dumps({"seed": SAMPLE_SEED, "n": len(picked), "ids": [h["id"] for h in picked]}, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    # Annotator packet: text, source and blank label columns only. No strata, no labels.
    rows = []
    for k, h in enumerate(picked, 1):
        t, y1, y2, _ = gen_cases.CASES[h["case"]]
        f1, f2 = gen_cases.target_filing(t, y1), gen_cases.target_filing(t, y2)
        rows.append({"item": k, "hunk_id": h["id"], "company": t,
                     "earlier_filing": f"FY{y1} 10-K, filed {f1['filed']}, {f1['url']}",
                     "later_filing": f"FY{y2} 10-K, filed {f2['filed']}, {f2['url']}",
                     "context_before (unchanged)": h["context_before"],
                     "EARLIER TEXT (removed or changed)": "\n".join(h["before"]) or "(none: text added)",
                     "LATER TEXT (added or changed)": "\n".join(h["after"]) or "(none: text removed)",
                     "context_after (unchanged)": h["context_after"],
                     "closest text elsewhere in the other filing": (h["nearest_on_other_side"] or {}).get("text", ""),
                     "label": "", "confidence (1-3)": "", "note": ""})
    path = OUT / "second_annotator_packet.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:   # BOM so Excel opens it as UTF-8
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("sample", len(picked), dict(Counter((h["case"], h["stratum"]) for h in picked)))


if __name__ == "__main__":
    main()
