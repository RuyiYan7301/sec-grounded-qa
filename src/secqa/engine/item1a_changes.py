"""Item 1A change detection for change packets (Part B), done by the engine itself.

Coordinates: the section text and paragraph segmentation are the frozen protocol's (item1a.item1a_text,
item1a.paragraphs), so paragraph indices and text hashes mean the same thing as in the scorer. Nothing else
from the benchmark is used: no hunks, no unit pairing, no locator file, no labels, gold or adjudication.

Steps (engine's own): 1. unchanged paragraphs by difflib on the paragraph lists; 2. inside each changed block,
pairs by word-trigram Jaccard similarity (>= PAIR_MIN), leftovers are added or removed; 3. an added or
removed paragraph with a close match elsewhere (>= MOVED_MIN) is shown to the classifier with that match;
4. a pair whose texts differ only in punctuation, spacing or year numbers is boilerplate without a model
call; 5. every other candidate gets one classification call (qwen3:8b, temperature 0) with high-level
label definitions only. Only material candidates go into the packet, with their own paragraph locators.
"""
import difflib
import hashlib
import re
from datetime import date

from .. import edgar, facts
from ..evaluation.v2 import item1a as protocol  # coordinate system only: item1a_text, paragraphs
from . import llm

PAIR_MIN, MOVED_MIN = 0.4, 0.7
LABELS = ("material_added", "material_removed", "material_modified", "boilerplate", "ambiguous")
CLASSIFY = """You compare one piece of the Risk Factors section (Item 1A) of a company's annual report with
the previous year's report and decide whether the disclosed risk changed.

Labels (answer with exactly one):
- material_added: a risk, or a substantive part of a risk, appears that the earlier report did not disclose
  anywhere.
- material_removed: a risk, or a substantive part of a risk, that the earlier report disclosed is no longer
  disclosed anywhere in the later report.
- material_modified: the same risk is still disclosed, but what is said about it changed in substance: its
  scope, its likelihood or status (for example something that could happen now has happened), its size, or
  the company's exposure; or a new fact or event was added to an existing risk.
- boilerplate: wording, order, formatting, dates or cross-references changed, or text moved, but the risk
  disclosed and its scope, likelihood, size and exposure are the same.
- ambiguous: you cannot tell from the text.

Return JSON: {"label": "<one label>", "reason": "<one sentence>"}"""


def target_10k(ticker, fy):
    """The original 10-K for a fiscal year, from submissions (accession, filed)."""
    sub = edgar.submissions(ticker)
    fye = sub.get("fiscalYearEnd") or "1231"
    r = sub["filings"]["recent"]
    hits = sorted((r["filingDate"][i], r["accessionNumber"][i]) for i, f in enumerate(r["form"])
                  if f == "10-K" and r["reportDate"][i]
                  and facts.fiscal_year(date.fromisoformat(r["reportDate"][i]), fye) == fy)
    filed, accn = hits[0]
    return {"accession": accn, "filed": filed}


def _trigrams(text):
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 3]) for i in range(max(len(w) - 2, 1))}


def jaccard(a, b):
    ta, tb = _trigrams(a), _trigrams(b)
    return len(ta & tb) / len(ta | tb) if ta | tb else 1.0


def _norm(text):
    t = re.sub(r"\b(?:19|20)\d\d\b", "", text.lower())
    return re.sub(r"[^a-z]+", "", t)


def locator(accession, paras, i):
    return {"accession": accession, "section": "1A", "paragraph_index": i,
            "text_sha256": hashlib.sha256(paras[i].encode("utf-8")).hexdigest()}


def candidates(a, b):
    """[(earlier index | None, later index | None)] for every changed paragraph, engine's own alignment."""
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        left, right = list(range(i1, i2)), list(range(j1, j2))
        scores = sorted(((jaccard(a[i], b[j]), i, j) for i in left for j in right), reverse=True)
        used_i, used_j = set(), set()
        for s, i, j in scores:
            if s < PAIR_MIN:
                break
            if i in used_i or j in used_j:
                continue
            used_i.add(i)
            used_j.add(j)
            out.append((i, j))
        out += [(i, None) for i in left if i not in used_i] + [(None, j) for j in right if j not in used_j]
    return sorted(out, key=lambda p: (p[0] if p[0] is not None else -1, p[1] if p[1] is not None else -1))


def closest(text, paras):
    best = max(range(len(paras)), key=lambda k: jaccard(text, paras[k]), default=None)
    return (best, jaccard(text, paras[best])) if best is not None else (None, 0.0)


def detect(ticker, y1, y2, log=None, classify=True, model=None, post=None):
    log = log or llm.CallLog()
    f1, f2 = target_10k(ticker, y1), target_10k(ticker, y2)
    a = protocol.paragraphs(protocol.item1a_text(ticker, y1))
    b = protocol.paragraphs(protocol.item1a_text(ticker, y2))
    found = []
    for i, j in candidates(a, b):
        earlier, later = (a[i] if i is not None else None), (b[j] if j is not None else None)
        c = {"earlier_index": i, "later_index": j, "earlier": earlier, "later": later}
        if earlier and later and _norm(earlier) == _norm(later):
            c |= {"label": "boilerplate", "reason": "punctuation, spacing or year numbers only", "model": False}
        else:
            other = None
            if earlier and not later:
                k, s = closest(earlier, b)
                other = {"side": "later", "index": k, "similarity": round(s, 3), "text": b[k]} if s >= MOVED_MIN else None
            elif later and not earlier:
                k, s = closest(later, a)
                other = {"side": "earlier", "index": k, "similarity": round(s, 3), "text": a[k]} if s >= MOVED_MIN else None
            c["closest_elsewhere"] = other
            if classify:
                prompt = (f"EARLIER TEXT: {earlier or '(none: text added)'}\n\nLATER TEXT: {later or '(none: text removed)'}"
                          + (f"\n\nCLOSEST PARAGRAPH ELSEWHERE IN THE {other['side'].upper()} REPORT: {other['text']}" if other else ""))
                kw = {"post": post} if post else {}
                text = llm.chat([{"role": "system", "content": CLASSIFY}, {"role": "user", "content": prompt}],
                                "item1a_classifier", log, model=model, fmt="json", **kw)
                out = llm.parse_json(text) or {}
                lab = out.get("label") if out.get("label") in LABELS else "ambiguous"
                c |= {"label": lab, "reason": out.get("reason"), "model": True, "raw": text}
        found.append(c)
    changes = []
    for c in found:
        lab = c.get("label", "")
        if not lab.startswith("material"):
            continue
        x = {"label": lab, "summary": c.get("reason") or ""}
        if c["earlier_index"] is not None and lab != "material_added":
            x["earlier"] = locator(f1["accession"], a, c["earlier_index"])
        if c["later_index"] is not None and lab != "material_removed":
            x["later"] = locator(f2["accession"], b, c["later_index"])
        if "earlier" in x or "later" in x:
            changes.append(x)
    return {"earlier_filing": f1, "later_filing": f2, "paragraphs": [len(a), len(b)], "candidates": found,
            "item1a_changes": changes, "calls": log.summary()}
