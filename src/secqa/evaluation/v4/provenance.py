"""Secondary final-correct count for v0.4: frozen scorer 2.1 with earlier-reported values exempted.

The frozen slot-based contradiction check reads an earlier-reported value quoted as provenance ("restated
from an earlier report of $12,483 million") as a contradiction (docs/v0.4-generalization.md, 2b). This
module does not change the scorer. It masks such quotes in the answer text and then calls the frozen
`score_item` unchanged. A number is masked only when both hold:
  - it equals (relative 0.5%) an earlier value recorded in the execution result itself: the `earlier`
    values of a `restated` warning, or a cell's `other_values`; and
  - its sentence contains a provenance cue (earlier, originally, previously, first reported, restated
    from, revised from, prior/earlier/original filing or report).
So a number the renderer invents, or a current value attached to the wrong year, is never masked.
The frozen count stays the primary result; this count is reported next to it as secondary.
"""
import re

from ... import agent
from ..v2 import score as scorer

CUE = re.compile(r"\b(?:earlier|originally|original|previously|previous|first reported|initially|"
                 r"restated from|revised from|recast from|prior filing|prior report)\b", re.I)
SENTENCE = re.compile(r"(?<=[.;\n])\s+")


def earlier_values(execution):
    vals = set()
    for w in execution.get("warnings", []) or []:
        for rv in w.get("revisions", []) or []:
            for e in rv.get("earlier", []) or []:
                if isinstance(e.get("val"), (int, float)):
                    vals.add(float(e["val"]))
    for c in execution.get("cells", []) or []:
        for e in c.get("other_values", []) or []:
            if isinstance(e.get("val"), (int, float)):
                vals.add(float(e["val"]))
    return vals


def mask(answer, execution):
    """(masked text, number of masked figures)."""
    earlier = [abs(v) for v in earlier_values(execution) if abs(v) >= 1e5]
    if not earlier or not answer:
        return answer, 0
    text = scorer.norm(answer)
    out, n = [], 0
    for sent in SENTENCE.split(text):
        if CUE.search(sent):
            for v, raw, pct in agent.numbers_in(sent):
                if not pct and any(abs(abs(v) - e) <= 0.005 * e for e in earlier):
                    sent = sent.replace(raw, "[earlier value]", 1)
                    n += 1
        out.append(sent)
    return " ".join(out), n


def score_item(item, rec, execution, ontology):
    """Frozen score_item on the masked answer; adds `provenance_masked` (count). Restated-value questions
    are not masked: there the original value is a required number, and the frozen check already treats it
    as gold (`original_val`)."""
    if (item.get("gold_plan") or {}).get("intent") == "restated_value_lookup":
        masked, n = rec.get("answer"), 0
    else:
        masked, n = mask(rec.get("answer"), execution)
    s = scorer.score_item(item, dict(rec, answer=masked), None, ontology)
    s["provenance_masked"] = n
    return s
