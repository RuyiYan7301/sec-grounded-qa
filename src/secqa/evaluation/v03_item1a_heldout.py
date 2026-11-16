"""Held-out Item 1A cases for v0.3 (docs/item1a-v0.3-plan.md): units, labeller packets and locators.

    python -m secqa.evaluation.v03_item1a_heldout
    # writes data/eval/v0.3/item1a/<case>.hunks.json, packets/packet_<case>_<k>.csv, item1a_locators.json

Uses the frozen v0.2 annotation code unchanged (item1a.hunks, item1a_display.row, item1a_locators): the two
new cases are only registered in gen_cases.CASES at run time, so units, display and locators are built by
exactly the code that built the v0.2 gold. Packets are split into parts of at most PART units for the
labellers, in unit order; no strata, no labels.
"""
import hashlib
import json

from .. import config
from .v2 import gen_cases, item1a, item1a_display, item1a_locators

CASES = {"MSFT_FY2026": ("MSFT", 2025, 2026, "v03_heldout"), "ORCL_FY2026": ("ORCL", 2025, 2026, "v03_heldout")}
OUT = config.EVAL_DIR / "v0.3" / "item1a"
PART = 45


def main():
    gen_cases.CASES.update(CASES)
    (OUT / "packets").mkdir(parents=True, exist_ok=True)
    manifest = {"cases": {}, "frozen_code_sha256": {
        p: hashlib.sha256((config.REPO_ROOT / p).read_bytes()).hexdigest()
        for p in ("src/secqa/evaluation/v2/item1a.py", "src/secqa/evaluation/v2/item1a_display.py",
                  "src/secqa/evaluation/v2/item1a_locators.py",
                  "data/eval/v0.2/item1a/protocol_v2/item1a_guideline_v2.md")}}
    locs = {"segmenter": "secqa.evaluation.v2.item1a.paragraphs", "normalisation": item1a.ALIGN["normalise"],
            "hash": "sha256 of the UTF-8 paragraph text as returned by the segmenter", "cases": {}}
    for case, (t, y1, y2, split) in CASES.items():
        hs = item1a.hunks(case)
        f1, f2 = gen_cases.target_filing(t, y1), gen_cases.target_filing(t, y2)
        (OUT / f"{case}.hunks.json").write_text(json.dumps(
            {"ticker": t, "from": f"FY{y1}", "to": f"FY{y2}", "split": split, "from_filing": f1, "to_filing": f2,
             "alignment": item1a.ALIGN, "hunks": hs}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        a, b = item1a_display.case_paragraphs(case)
        paras = {case: (a, b)}
        parts = []
        for k in range(0, len(hs), PART):
            path = OUT / "packets" / f"packet_{case}_{k // PART + 1}.csv"
            item1a_display.write_packet(path, [item1a_display.row(n, h, paras) for n, h in enumerate(hs[k:k + PART], k + 1)])
            parts.append({"path": path.name, "sha256": item1a_display.sha(path), "n": len(hs[k:k + PART])})
        pos = item1a_locators.unit_positions(a, b)
        assert len(pos) == len(hs), case
        units = []
        for h, (gi, gj) in zip(hs, pos):
            assert (h["before"] == ([a[gi]] if gi is not None else [])
                    and h["after"] == ([b[gj]] if gj is not None else [])), h["id"]
            u = {"id": h["id"], "type": h["type"], "split": split}
            if gi is not None:
                u["earlier"] = item1a_locators.locator(f1["accession"], a, gi)
            if gj is not None:
                u["later"] = item1a_locators.locator(f2["accession"], b, gj)
            units.append(u)
        locs["cases"][case] = {"earlier_filing": f1["accession"], "later_filing": f2["accession"],
                               "paragraphs_earlier": len(a), "paragraphs_later": len(b), "units": units}
        manifest["cases"][case] = {"units": len(hs), "earlier_filing": f1, "later_filing": f2, "packets": parts}
        print(case, len(hs), "units,", len(parts), "packets")
    (OUT / "item1a_locators.json").write_text(json.dumps(locs, indent=1, ensure_ascii=False) + "\n",
                                              encoding="utf-8", newline="\n")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8", newline="\n")


SECOND_SEED = 1116   # fixed before the sample was drawn


def second_labeller_packet():
    """50 held-out units for the optional external second labeller: item1a.sample (same strata rule as the
    v0.2 confirm sample) with SECOND_SEED, display as in v0.2. Written after the Claude labels and before any
    run; the external labeller sees no labels."""
    gen_cases.CASES.update(CASES)
    every = []
    for case in CASES:
        every += [h | {"split": "test"} for h in
                  json.loads((OUT / f"{case}.hunks.json").read_text(encoding="utf-8"))["hunks"]]
    picked = item1a.sample(every, n=50, seed=SECOND_SEED)
    paras = {c: item1a_display.case_paragraphs(c) for c in CASES}
    path = OUT / "packets" / "packet_second_labeller.csv"
    item1a_display.write_packet(path, [item1a_display.row(k, h, paras) for k, h in enumerate(picked, 1)])
    (OUT / "second_labeller_sample.json").write_text(json.dumps(
        {"seed": SECOND_SEED, "n": len(picked), "method": "item1a.sample, strata (case, stratum)",
         "packet": path.name, "packet_sha256": item1a_display.sha(path), "ids": [h["id"] for h in picked]},
        indent=1) + "\n", encoding="utf-8", newline="\n")
    print(len(picked), path.name)


if __name__ == "__main__":
    import sys
    second_labeller_packet() if sys.argv[1:] == ["--second-labeller"] else main()
