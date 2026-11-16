"""Part B Item 1A, protocol v2: packet for the test units not in the retest or confirm packets.

    python -m secqa.evaluation.v2.item1a_rest_packet    # writes protocol_v2/packet_rest.csv, rest_packet.json

Uses the locked display (`item1a_display.row`) unchanged, so these rows show exactly what the retest and
confirm rows show. The order is shuffled with a fixed seed so no labeller sees a case in document order.
These labels complete the v2 gold; they are not part of any agreement figure.
"""
import hashlib
import json
import random

from . import gen_cases, item1a, item1a_display as d

SEED = 4250


def main():
    every = []
    for case in gen_cases.CASES:
        every += json.loads((item1a.OUT / f"{case}.hunks.json").read_text(encoding="utf-8"))["hunks"]
    s = json.loads((d.OUT / "samples.json").read_text(encoding="utf-8"))
    done = set(s["retest"]["ids"]) | set(s["confirm"]["ids"])
    rest = [h for h in every if h["split"] == "test" and h["id"] not in done]
    random.Random(SEED).shuffle(rest)
    paras = {c: d.case_paragraphs(c) for c in gen_cases.CASES}
    path = d.OUT / "packet_rest.csv"
    d.write_packet(path, [d.row(k, h, paras) for k, h in enumerate(rest, 1)])
    (d.OUT / "rest_packet.json").write_text(json.dumps({
        "packet": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "n": len(rest),
        "seed": SEED, "selection": "all test units not in retest or confirm", "display": "item1a_display.row (locked)",
        "ids": [h["id"] for h in rest]}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("rest", len(rest))


if __name__ == "__main__":
    main()
