"""Item 1A change detection, v0.3 candidates (post-hoc; docs/item1a-v0.3-plan.md). v0.2 stays in
item1a_changes.py, unchanged; this module reuses its alignment, context search and locators.

Variants (chosen by name, each logged in results/dev/item1a_v03/):
- "v02": the frozen v0.2 classifier prompt and input (baseline, re-run on the same machine).
- "diff": the classifier sees a word-level diff made by code: deleted words in [-...-], inserted words in
  {+...+}, everything else identical. A one-sided candidate (added or removed paragraph) whose sentences
  reappear elsewhere in the other report (best sentence-coverage match >= MOVE_MIN) is diffed against that
  paragraph, so moved, merged or split text shows only its real edits.
- "quote": as "diff", and the classifier must first list each change it sees with its quoted words and
  whether it is substance or wording; a material label with no change marked as substance is turned into
  boilerplate by code (the rule is stated in the prompt).
"""
import difflib
import json
import re

from . import item1a_changes as v02, llm
from ..evaluation.v2 import item1a as protocol

MOVE_MIN = 0.6
LABELS = v02.LABELS

DEFS = """Labels (answer with exactly one):
- material_added: a risk, or a substantive part of a risk, appears that the earlier report did not disclose
  anywhere.
- material_removed: a risk, or a substantive part of a risk, that the earlier report disclosed is no longer
  disclosed anywhere in the later report.
- material_modified: the same risk is still disclosed, but what is said about it changed in substance: its
  scope, its likelihood or status (for example something that could happen now has happened), its size, or
  the company's exposure; or a new fact or event was added to an existing risk.
- boilerplate: wording, order, formatting, dates or cross-references changed, or text moved, but the risk
  disclosed and its scope, likelihood, size and exposure are the same.
- ambiguous: you cannot tell from the text."""

DIFF_SYSTEM = """You compare one piece of the Risk Factors section (Item 1A) of a company's annual report with
the previous year's report and decide whether the disclosed risk changed.

You get a word-level comparison made by code. Words in [-...-] were in the earlier report and are gone;
words in {+...+} are new in the later report; all other words are identical in both reports. Judge only the
marked words: ask whether they change the risk itself, or only its wording. Synonyms, reordering, a new
date or year, a renamed section or cross-reference, and a sentence split or joined are wording.

""" + DEFS + """

Return JSON: {"label": "<one label>", "reason": "<one sentence>"}"""

QUOTE_SYSTEM = """You compare one piece of the Risk Factors section (Item 1A) of a company's annual report with
the previous year's report and decide whether the disclosed risk changed.

You get a word-level comparison made by code. Words in [-...-] were in the earlier report and are gone;
words in {+...+} are new in the later report; all other words are identical in both reports. Judge only the
marked words.

First list every change you see: quote the marked words and say whether the change is "substance" (it
changes the risk's scope, likelihood or status, size or the company's exposure, or adds or drops a risk, a
fact or an event) or "wording" (synonyms, reordering, dates or years, cross-references, section names,
sentence splits, emphasis). Then give the label. A material label needs at least one change marked
"substance"; if every change is wording, the label is boilerplate.

""" + DEFS + """

Return JSON: {"changes": [{"quote": "<marked words>", "kind": "substance" or "wording"}], "label": "<one label>",
"reason": "<one sentence>"}"""


def word_diff(a, b):
    """Earlier text a, later text b -> one string with [-deleted-] and {+inserted+} runs."""
    x, y = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(" ".join(x[i1:i2]))
        if op in ("delete", "replace"):
            out.append("[-" + " ".join(x[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            out.append("{+" + " ".join(y[j1:j2]) + "+}")
    return " ".join(out)


def diff_input(earlier, later, ctx):
    """The text the diff variants classify, and how the candidate was set up."""
    if earlier and later:
        return "kind: changed paragraph\n\n" + word_diff(earlier, later), "pair"
    if earlier:
        best = (ctx["earlier_in_later"] or [None])[0]
        if best and best["score"] >= MOVE_MIN:
            return ("kind: paragraph removed here; its sentences reappear elsewhere in the later report "
                    f"(match {best['score']:.2f}). Comparison with that later paragraph:\n\n"
                    + word_diff(earlier, best["text"])), "moved"
        return "kind: paragraph removed, not found elsewhere in the later report\n\n[-" + earlier + "-]", "removed"
    best = (ctx["later_in_earlier"] or [None])[0]
    if best and best["score"] >= MOVE_MIN:
        return ("kind: paragraph added here; its sentences were already elsewhere in the earlier report "
                f"(match {best['score']:.2f}). Comparison with that earlier paragraph:\n\n"
                + word_diff(best["text"], later)), "moved"
    return "kind: paragraph added, not found elsewhere in the earlier report\n\n{+" + later + "+}", "added"


SMALL_MAX = None   # K for "diff_small"; set from development data before the held-out run


def changed_words(diff_text):
    """Words inside [-...-] and {+...+} runs of a word_diff output."""
    return [w for run in re.findall(r"\[-(.*?)-\]|\{\+(.*?)\+\}", diff_text, flags=re.S) for part in run for w in part.split()]


def small_edit(earlier, later, ctx, k):
    """True if the diff the "diff" variant would show is a pair or a moved paragraph, changes at most k words,
    and no changed word contains a digit."""
    text, setup = diff_input(earlier, later, ctx)
    if setup not in ("pair", "moved"):
        return False
    words = changed_words(text.split("\n\n", 1)[1])
    return len(words) <= k and not any(any(ch.isdigit() for ch in w) for w in words)


def classify(variant, earlier, later, ctx, log, model=None):
    if variant == "diff_small":
        if small_edit(earlier, later, ctx, SMALL_MAX):
            return {"label": "boilerplate", "reason": f"code diff changes at most {SMALL_MAX} words, no numbers",
                    "rule": "small_edit", "setup": diff_input(earlier, later, ctx)[1], "raw": None}
        variant = "diff"
    if variant == "v02":
        prompt = (f"EARLIER TEXT: {earlier or '(none: text added)'}\n\nLATER TEXT: {later or '(none: text removed)'}"
                  + v02._context("CONTEXT ONLY - where the EARLIER TEXT may be in the later report", ctx["earlier_in_later"])
                  + v02._context("CONTEXT ONLY - where the LATER TEXT may come from in the earlier report",
                                 ctx["later_in_earlier"]))
        system, setup = v02.CLASSIFY, "v02"
    else:
        prompt, setup = diff_input(earlier, later, ctx)
        system = DIFF_SYSTEM if variant == "diff" else QUOTE_SYSTEM
    text = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    "item1a_classifier", log, model=model, fmt="json")
    out = llm.parse_json(text) or {}
    lab = out.get("label") if out.get("label") in LABELS else "ambiguous"
    rule = None
    if variant == "quote" and lab.startswith("material"):
        ch = out.get("changes") if isinstance(out.get("changes"), list) else []
        if not any(isinstance(c, dict) and c.get("kind") == "substance" for c in ch):
            lab, rule = "boilerplate", "no change marked substance"
    return {"label": lab, "reason": out.get("reason"), "rule": rule, "setup": setup, "raw": text}


def system_prompts():
    return {"v02": v02.CLASSIFY, "diff": DIFF_SYSTEM, "quote": QUOTE_SYSTEM}


def detect(ticker, y1, y2, variant, log=None, model=None):
    """Same output shape as item1a_changes.detect (item1a_changes with locators, candidates kept)."""
    log = log or llm.CallLog()
    f1, f2 = v02.target_10k(ticker, y1), v02.target_10k(ticker, y2)
    a = protocol.paragraphs(protocol.item1a_text(ticker, y1))
    b = protocol.paragraphs(protocol.item1a_text(ticker, y2))
    found = []
    for i, j in v02.candidates(a, b):
        earlier, later = (a[i] if i is not None else None), (b[j] if j is not None else None)
        c = {"earlier_index": i, "later_index": j}
        if earlier and later and v02._norm(earlier) == v02._norm(later):
            c |= {"label": "boilerplate", "reason": "punctuation, spacing or year numbers only", "model": False}
        else:
            ctx = {"earlier_in_later": v02.where_else(earlier, b, exclude=j) if earlier else [],
                   "later_in_earlier": v02.where_else(later, a, exclude=i) if later else []}
            c |= classify(variant, earlier, later, ctx, log, model) | {"model": True}
        found.append(c)
    changes = []
    for c in found:
        lab = c.get("label", "")
        if not lab.startswith("material"):
            continue
        x = {"label": lab, "summary": c.get("reason") or ""}
        if c["earlier_index"] is not None and lab != "material_added":
            x["earlier"] = v02.locator(f1["accession"], a, c["earlier_index"])
        if c["later_index"] is not None and lab != "material_removed":
            x["later"] = v02.locator(f2["accession"], b, c["later_index"])
        if "earlier" in x or "later" in x:
            changes.append(x)
    return {"earlier_filing": f1, "later_filing": f2, "candidates": found, "item1a_changes": changes,
            "calls": log.summary()}
