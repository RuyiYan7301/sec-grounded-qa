"""Gold paragraph locators for the Item 1A units, for scoring packets without benchmark unit ids.

    python -m secqa.evaluation.v2.item1a_locators   # writes data/eval/v0.2/partB/item1a_locators.json

A locator names one paragraph of one filing: accession, section "1A", paragraph index (0-based) in the
segmentation of item1a.paragraphs(), and the SHA-256 of the normalised paragraph text (UTF-8 of the
paragraph exactly as item1a.paragraphs() returns it: whitespace collapsed, page furniture dropped,
page-break continuations joined). The frozen Item 1A files are read, not changed.

Matching rule for packets (docs/partB-scoring-draft.md): an `added` unit matches on its later locator, a
`removed` unit on its earlier locator, a `modified` unit only when both match. Similarity is used only to
show a reviewer the closest unit; it never decides a score.
"""
import hashlib
import json

from ... import config
from . import gen_cases, item1a, item1a_display

OUT = config.EVAL_DIR / "v0.2" / "partB" / "item1a_locators.json"
SECTION = "1A"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def locator(accession, paras, i):
    text = paras[i]
    return {"accession": accession, "section": SECTION, "paragraph_index": i, "text_sha256": sha(text),
            "text_unique_in_filing": paras.count(text) == 1, "quote": text[:200]}


def unit_positions(a, b):
    """(earlier index or None, later index or None) per unit, in unit order: the same two-pass alignment as
    item1a.hunks(), kept here because the frozen module does not return indices. Some paragraph texts occur
    more than once in a filing (repeated headings), so the index, not the text, identifies the paragraph."""
    import difflib
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        for pi, pj, _sim in item1a.pair(a[i1:i2], b[j1:j2]):
            out.append((None if pi is None else i1 + pi, None if pj is None else j1 + pj))
    return out


def main():
    out = {"segmenter": "secqa.evaluation.v2.item1a.paragraphs", "normalisation": item1a.ALIGN["normalise"],
           "hash": "sha256 of the UTF-8 paragraph text as returned by the segmenter", "cases": {}}
    for case, (t, y1, y2, split) in gen_cases.CASES.items():
        a, b = item1a_display.case_paragraphs(case)
        f1, f2 = gen_cases.target_filing(t, y1), gen_cases.target_filing(t, y2)
        hunks = json.loads((item1a.OUT / f"{case}.hunks.json").read_text(encoding="utf-8"))["hunks"]
        pos = unit_positions(a, b)
        assert len(pos) == len(hunks), case
        units = []
        for h, (gi, gj) in zip(hunks, pos):
            # the re-run alignment must reproduce the frozen unit texts exactly
            assert (h["before"] == ([a[gi]] if gi is not None else [])
                    and h["after"] == ([b[gj]] if gj is not None else [])), h["id"]
            u = {"id": h["id"], "type": h["type"], "split": split}
            if gi is not None:
                u["earlier"] = locator(f1["accession"], a, gi)
            if gj is not None:
                u["later"] = locator(f2["accession"], b, gj)
            units.append(u)
        dup = sum(a.count(p) > 1 for p in set(a)) + sum(b.count(p) > 1 for p in set(b))
        out["cases"][case] = {"earlier_filing": f1["accession"], "later_filing": f2["accession"],
                              "paragraphs_earlier": len(a), "paragraphs_later": len(b),
                              "duplicate_paragraph_texts": dup, "units": units}
        print(case, len(units), "units;", len(a), "/", len(b), "paragraphs; duplicate texts", dup)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
