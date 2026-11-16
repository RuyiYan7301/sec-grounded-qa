"""Part A scorer, version 2.0. Rule-based; frozen with the benchmark before the typed engine exists.

    python -m secqa.evaluation.v2.score RUN.jsonl [--split test|dev] [--paired OTHER.jsonl]

Input: one JSON record per item, the same format for v0.1 and v0.2 (v0.1 through an adapter that reads
its tool trace):

    {"id": "A-test-gen-001",
     "system": "v0.2" | "v0.1",
     "answer": "<final answer text>",
     "evidence": [{"ticker", "metric", "period", "concept", "value", "unit", "accession", "period_end"}],
     "plan": {...} | null,          # v0.2 only, validated against data/eval/v0.2/plan.schema.json
     "result": {...} | null}        # v0.2 only: the engine's computed result, e.g. {"val": 63.03}

`evidence` lists the facts the system used (v0.2: the executed plan's cells; v0.1: get_fact / compare
rows from the trace). Every score is computed from the record and the frozen gold only. Text checks
use the fixed patterns below; they are part of the frozen scorer and are not changed after any run.
"""
import json
import math
import re
import sys
from collections import Counter

from ... import agent, config

V = "2.0"
DIR = config.EVAL_DIR / "v0.2"
REFUSALS = ("out_of_ontology", "not_reported", "unsupported", "out_of_range", "unsupported_operation")
ANSWER_OUTCOMES = ("answer", "ambiguous_year")
REL_EVIDENCE = 0.006          # a stated number traces to an evidence value within 0.6% (as in v0.1)

# ---------------------------------------------------------------- frozen text patterns
FLAGS = re.I | re.S
UNAVAILABLE = re.compile(
    r"not (?:separately |explicitly )?(?:report|disclos|available|provid|present|in (?:the|my|our) (?:data|scope|ontology))"
    r"|does(?:n't| not) (?:report|disclose|provide|break out|present|have)|isn't (?:reported|disclosed|available)"
    r"|no (?:such |separate )?(?:figure|line item|value|data|reported value)|cannot (?:provide|answer|compute|give|determine)"
    r"|can't (?:provide|answer|compute|give|determine)|unable to|outside (?:the |my |our )?(?:scope|range|data|coverage)"
    r"|not (?:supported|covered|one of|part of)|out of (?:scope|range)|only (?:covers?|includes?|has|indexes)"
    r"|non-GAAP|not a (?:GAAP|reported) (?:metric|measure)"
    r"|unavailable|outside (?:the |my |our )?[\w -]{0,30}?(?:range|scope|coverage|period)", FLAGS)   # round 2, P10
ADVICE_REFUSAL = re.compile(r"(?:can(?:no|')t|do not|don't|not able to|unable to|won't) (?:give|provide|offer|make)"
                            r"[^.]{0,40}(?:advice|recommendation|prediction|forecast)|not (?:investment|financial) advice"
                            r"|cannot predict|can't predict|no forecast"
                            # calibration round 4, P10: "I can't advise whether you should buy ...; ... is unsupported"
                            r"|(?:can(?:no|')t|do not|don't|won't|not able to|unable to) (?:advise|recommend|say whether)"
                            r"|\bunsupported\b", FLAGS)
NOT_MEANINGFUL = re.compile(r"not meaningful|not a meaningful|isn't meaningful|not (?:well[- ])?defined"
                            r"|(?:negative|zero) (?:base|starting|prior)|sign change|changed sign|from a (?:loss|negative|benefit)", FLAGS)
WARNING = {
    # Own copy of the v0.1 mismatch words, without the bare stem "differ", which also matched "difference"
    # (calibration slot W6). The v0.1 system's own pattern (agent.MISMATCH_WORDS) is not changed.
    "period_mismatch": re.compile(r"mismatch|not line up|do(?:es)? not align|don't align|different (?:fiscal )?periods?"
                                  r"|not (?:directly )?comparable|not like-for-like|cover different"
                                  r"|\bdiffer(?:s|ed|ing)?\b(?! by)|fiscal years? end(?:s|ed)? (?:on |in )?different"
                                  r"|different fiscal year|year[- ]ends? (?:differ|are different)|different year[- ]ends?"
                                  # calibration round 2, P04 / P13
                                  r"|not aligned|(?:periods?|years?) (?:end|ended|ending) on different"
                                  r"|end(?:s|ed)? on different dates", FLAGS),
    "scope": re.compile(r"scope|fallback|broader|non-?controlling|attributable|productive assets|including (?:minority|NCI)"
                        r"|different (?:concept|tag|line item)|not the same (?:concept|line)", FLAGS),
    "restated": re.compile(r"restat|recast|revis|re-?present|split[- ]adjust|adjusted for (?:the )?(?:stock )?split"
                           r"|originally reported|as first reported|first reported|differs? from (?:the )?original", FLAGS),
    "alias_interpretation": re.compile(r"(?:interpret|assum|treat|read|tak|us)\w*[^.]{0,60}diluted"
                                       r"|diluted[^.]{0,60}(?:interpret|assum|unless|rather than basic)", FLAGS),
    "ambiguous_year": re.compile(r"ambigu|calendar (?:year )?20\d\d|fiscal (?:year )?20\d\d,? (?:which )?(?:ended|ending|ends)"
                                 r"|FY ?20\d\d \((?:ended|ending)|(?:ended|ending) (?:on )?(?:January|February|late January)"
                                 r"|interpret\w*[^.]{0,40}fiscal", FLAGS),
}
NONCURRENT = re.compile(r"non-?current (?:portion|part|amount|long-term debt)|excluding (?:the )?current (?:maturities|portion)"
                        r"|excludes? (?:the )?current (?:maturities|portion)|net of (?:the )?current (?:maturities|portion)"
                        r"|LongTermDebtNoncurrent", FLAGS)
DOWN = re.compile(r"decreas|declin|fell|drop|lower|down\b|reduc|shrank|contract|narrow|−\s?\d|-\s?\$?\d|\(\$?\d", FLAGS)
UP = re.compile(r"increas|rose|grew|grow|higher|up\b|gain|rise|expan|widen|\+\s?\$?\d", FLAGS)
NEG_VALUE = re.compile(r"loss|negative|deficit|benefit|−\s?\$?\d|-\s?\$?\d|\(\$?\d", FLAGS)
BOTH = re.compile(r"\bboth\b|\beach\b|give (?:the |both )?(?:two )?(?:figures|amounts|values)|include (?:both )?(?:amounts|figures)", FLAGS)


# ---------------------------------------------------------------- gold
def load_gold(split):
    items = json.loads((DIR / f"qa_{split}.json").read_text(encoding="utf-8"))
    alts = {a["item"]: a for a in json.loads((DIR / "qualified_alternatives.json").read_text(encoding="utf-8"))["items"]}
    return {it["id"]: it for it in items}, alts


def _tol_ok(x, g, tol):
    if tol is None:
        return False
    if tol["kind"] == "relative":
        return abs(x - abs(g)) <= tol["rel"] * max(abs(g), 1e-9)
    return abs(x - abs(g)) <= tol["abs"]


def required_numbers(item, result, cells, question):
    """(value, kind) pairs the answer must state. kind: 'cell' (amount) or 'result'."""
    intent = (item["gold_plan"] or {}).get("intent")
    r = result
    out = []
    if intent in ("fact_lookup",) or item["gold_outcome"] == "ambiguous_year" and "val" in r:
        out.append((r["val"], "cell"))
    elif intent in ("multi_period_lookup", "cross_company_comparison"):
        out += [(v, "cell") for v in r["vals"]]
    elif intent == "restated_value_lookup":
        out += [(r["val"], "cell"), (r["original_val"], "cell")]
    elif intent in ("absolute_change", "percent_change", "percentage_point_change", "ratio"):
        out.append((r["val"], "result"))
        if BOTH.search(question):
            out += [(c["value"], "cell") for c in cells if c.get("use", "primary") != "component"]
    return out


# ---------------------------------------------------------------- number helpers
PP = re.compile(r"(\d+(?:\.\d+)?)\s*(?:percentage[- ]points?|pp\b|ppts?\b|pts?\b|points?\b)", re.I)
SMALL = re.compile(r"(?<![\d.,])(\d{1,2}\.\d{1,4})(?![\d%])")


QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "−": "-"})
GROUPED_DECIMAL = re.compile(r"(?<![\d,])(\d{1,3}(?:,\d{3})+)(\.\d+)")


def norm(text):
    """Typographic quotes and minus to ASCII (calibration slot R2: "can’t"); "2,270.6" to "2270.6", which
    numbers_in would otherwise split into 2,270 and .6 (slot R5)."""
    text = (text or "").translate(QUOTES)
    return GROUPED_DECIMAL.sub(lambda m: m.group(1).replace(",", "") + m.group(2), text)


def _amounts(text):
    """Non-percentage numbers (magnitudes, signs dropped by numbers_in) and percentages, in raw units.
    numbers_in skips bare numbers below 32 (counts); percentage-point figures ("0.22 percentage points")
    and bare decimals ("EPS of 1.21") are added here so small results can be found."""
    nums = agent.numbers_in(norm(text))
    amounts = [v for v, _, p in nums if not p]
    pcts = [v for v, _, p in nums if p] + [float(m.group(1)) for m in PP.finditer(text)]
    amounts += [float(m.group(1)) for m in SMALL.finditer(text)]
    return amounts, pcts


BPS = re.compile(r"(\d+(?:\.\d+)?)\s*(?:basis[- ]points?|bps?\b)", re.I)


def _pps(text):
    """Percentage-point figures written as such: "0.3 percentage points", "0.3 pp", "0.3 ppts", "0.3 points",
    or basis points ("30 basis points", "30 bps" = 0.3 pp)."""
    t = norm(text)
    return [float(m.group(1)) for m in PP.finditer(t)] + [float(m.group(1)) / 100 for m in BPS.finditer(t)]


def _stated(target, kind, unit, tol, amounts, pcts, pps=()):
    if kind == "result" and unit == "pp":
        # A percentage-point change must be written in points or basis points: "rose by 0.3%" states a
        # relative change, a different quantity (rule fixed after calibration round 2, slot F09).
        return any(_tol_ok(p, target, tol) for p in pps)
    if kind == "result" and unit == "percent":
        return any(_tol_ok(p, target, tol) for p in pcts) or any(_tol_ok(a, target, tol) for a in amounts)
    if tol and tol["kind"] == "absolute":                      # EPS
        return any(_tol_ok(a, target, tol) for a in amounts)
    t = tol or {"kind": "relative", "rel": 0.005}
    return any(_tol_ok(a, target, t) for a in amounts)


def _contradicts(amounts, targets, tol):
    """A stated amount within a factor of 2 of a required amount, outside tolerance of every gold amount."""
    t = tol if tol and tol["kind"] == "relative" else {"kind": "relative", "rel": 0.005}
    big = [abs(g) for g in targets if abs(g) >= 1e5]
    for a in amounts:
        near = [g for g in big if g / 2 <= a <= g * 2]
        if near and not any(_tol_ok(a, g, t) for g in big):
            return True
    return False


BASIC = re.compile(r"\bbasic\b", re.I)
DILUTED = re.compile(r"\bdiluted\b", re.I)


FY_MENTION = re.compile(r"\b(?:FY\s?'?(\d{4}|\d{2})|fiscal(?: year)?\s+(\d{4}))\b", re.I)
# a year that names a source document, a filing date or restatement provenance, not the period of a figure
SOURCE_AFTER = re.compile(r"^\W{0,3}(?:annual report|form 10-k|10-k|10-q|filing|report\b|proxy|filed)", re.I)
SOURCE_BEFORE = re.compile(r"(?:filed|filing|reported|restated|recast|revised|published|issued|presented)\s+"
                           r"(?:in|on|with|by)\s+(?:the\s+|its\s+|a\s+)?$|(?:10-k|filing)\s+for\s+$", re.I)
FY_RANGE = re.compile(r"(?:from|between)\s+(?:the\s+)?(FY\s?'?\d{2,4}|fiscal(?: year)?\s+\d{4})\s+(?:to|through|and|until)"
                      r"\s+(?:the\s+)?(FY\s?'?\d{2,4}|fiscal(?: year)?\s+\d{4})", re.I)


def _fy(s):
    y = int(re.search(r"\d{2,4}", s).group(0))
    return y + 2000 if y < 100 else y


def attributed_years(text):
    """Fiscal years the answer attaches to figures: 'FY2024', 'FY24', 'fiscal 2024', 'fiscal year 2024',
    minus years that name a source filing, a filing date or restatement provenance."""
    out = set()
    for m in FY_MENTION.finditer(text):
        if SOURCE_AFTER.search(text[m.end():m.end() + 25]) or SOURCE_BEFORE.search(text[max(0, m.start() - 40):m.start()]):
            continue
        out.add(_fy(m.group(0)))
    return out


def fiscal_years_ok(item, text):
    """A figure or change explicitly attributed to a fiscal year other than the gold periods is a visible
    factual error even when the number falls inside tolerance (rule after calibration round 4, F10). Source
    filings, filing dates and restatement provenance do not count. Conservative: a change whose stated
    range differs from the gold pair fails; otherwise only an answer that names fiscal years but none of
    the gold ones fails (an extra comparison year next to the gold year is not a conflict)."""
    gold = {int(p[2:]) for p in (item["gold_plan"] or {}).get("periods", [])}
    if not gold:
        return True
    intent = (item["gold_plan"] or {}).get("intent")
    if intent in ("absolute_change", "percent_change", "percentage_point_change"):
        for m in FY_RANGE.finditer(text):
            before = text[max(0, m.start() - 40):m.start()]
            if SOURCE_BEFORE.search(before):
                continue
            if {_fy(m.group(1)), _fy(m.group(2))} != gold:
                return False
    years = attributed_years(text)
    return not years or bool(years & gold)


def eps_label_ok(metric, text):
    """Basic and diluted EPS differ by cents, inside the $0.01 tolerance; an answer that names only the
    other kind is wrong even when the number is close (calibration round 2, slot F05)."""
    if metric == "eps_diluted":
        return not (BASIC.search(text) and not DILUTED.search(text))
    if metric == "eps_basic":
        return not (DILUTED.search(text) and not BASIC.search(text))
    return True


# ---------------------------------------------------------------- per-item score
def final_correct(item, rec, alt):
    """(correct, path, detail). path: canonical | qualified_alternative | refusal | not_meaningful."""
    a = norm(rec.get("answer"))
    outcome = item["gold_outcome"]
    amounts, pcts = _amounts(a)
    if outcome in REFUSALS:
        financial = [x for x in amounts if x >= 1000]
        ok = bool(UNAVAILABLE.search(a) or (outcome == "unsupported" and ADVICE_REFUSAL.search(a))) and not financial
        if outcome == "unsupported":
            from ..run_eval import gives_advice
            ok = ok and not gives_advice(a)
        return ok, "refusal", {"financial_numbers": financial[:5]}
    if outcome == "not_meaningful":
        ok = bool(NOT_MEANINGFUL.search(a)) and not pcts
        return ok, "not_meaningful", {"percentages": pcts[:5]}
    paths = [("canonical", item["gold_result"], item["gold_cells"], item["required_warnings"])]
    if alt:
        paths.append(("qualified_alternative", alt["result"], alt["cells"], alt["required_warnings"]))
    detail = {}
    for name, result, cells, warnings in paths:
        if name == "qualified_alternative" and not NONCURRENT.search(a):
            detail[name] = "noncurrent basis not stated"
            continue
        unit = result.get("unit")
        tol = item["tolerance"] if name == "canonical" else alt["tolerance"]
        req = required_numbers(item, result, cells, item["question"])
        missing = [g for g, k in req if not _stated(g, k, unit, tol, amounts, pcts, _pps(a))]
        others = [c["value"] for c in cells] + [g for g, _ in req]
        if name == "qualified_alternative" or alt:
            # same basis: an answer on one basis must not also state the other basis's amounts
            other_cells = (alt["cells"] if name == "canonical" else item["gold_cells"])
            mixed = [c["value"] for c in other_cells
                     if any(_tol_ok(x, c["value"], {"kind": "relative", "rel": 0.005}) for x in amounts)
                     and not any(abs(c["value"] - o) <= 0.005 * abs(o) for o in others)]
        else:
            mixed = []
        gold_amounts = [g for g, k in req if not (k == "result" and unit in ("percent", "pp"))]
        # every amount in the gold result counts as gold, also when the question does not require it,
        # e.g. the difference of a cross-company comparison (calibration round 3, slot P04)
        gold_amounts += [result[k] for k in ("difference", "absolute_change", "original_val")
                         if isinstance(result.get(k), (int, float))]
        if unit not in ("percent", "pp") and isinstance(result.get("val"), (int, float)):
            gold_amounts.append(result["val"])
        contra = _contradicts(amounts, gold_amounts + [c["value"] for c in cells], tol)
        warn_missing = [w for w in warnings if not WARNING[w].search(a)]
        sign_ok = True
        intent = (item["gold_plan"] or {}).get("intent")
        if intent in ("absolute_change", "percent_change", "percentage_point_change") and "val" in result:
            if result["val"] < 0:
                sign_ok = bool(DOWN.search(a))
            elif result["val"] > 0:
                sign_ok = not DOWN.search(a) or bool(UP.search(a))
        neg_ok = all(NEG_VALUE.search(a) for g, k in req if k == "cell" and g < 0)
        label_ok = eps_label_ok((item["gold_plan"] or {}).get("metric"), a)
        years_ok = fiscal_years_ok(item, a)
        ok = (not missing and not contra and not mixed and not warn_missing and sign_ok and neg_ok and label_ok
              and years_ok)
        detail[name] = {"missing": missing, "contradiction": contra, "mixed_basis": mixed,
                        "warnings_missing": warn_missing, "sign_ok": sign_ok, "negative_stated": neg_ok,
                        "eps_label_ok": label_ok, "fiscal_years_ok": years_ok}
        if ok:
            return True, name, detail
    return False, "canonical", detail


def appropriate_refusal(item, rec, correct, path):
    a = norm(rec.get("answer"))
    if item["gold_outcome"] in REFUSALS:
        return path == "refusal" and correct
    if item["gold_outcome"] == "not_meaningful":
        return not (UNAVAILABLE.search(a) and not NOT_MEANINGFUL.search(a))
    amounts, pcts = _amounts(a)
    return not (UNAVAILABLE.search(a) and not amounts and not pcts)


def evidence_of(rec):
    """(items, format_ok). The record format is a list of objects. A single object is read as a one-item
    list and a missing or null field as an empty list, but both are reported as format_ok = False;
    any other shape, and any entry that is not an object, is dropped (calibration round 2: a single
    object made the scorer iterate its keys and crash)."""
    ev = rec.get("evidence")
    if ev is None:
        return [], False
    if isinstance(ev, dict):
        return [ev], False
    if not isinstance(ev, list):
        return [], False
    items = [e for e in ev if isinstance(e, dict)]
    return items, len(items) == len(ev)


def _evidence_unreadable(rec):
    """Evidence that cannot be read as facts at all: a scalar or string, or a list with non-object entries."""
    ev = rec.get("evidence")
    return not isinstance(ev, (list, dict, type(None))) or (isinstance(ev, list) and not evidence_of(rec)[1])


def record_format_ok(rec):
    return evidence_of(rec)[1] and isinstance(rec.get("answer"), str)


def _evidence_values(ev):
    vals = [e["value"] for e in ev if isinstance(e.get("value"), (int, float))]
    return vals


def evidence_complete(rec):
    """Every stated amount traces to an evidence item that carries accession and period_end; every
    percentage is a ratio, change or difference of ratios of evidence values."""
    ev, _ = evidence_of(rec)
    if _evidence_unreadable(rec):
        return False
    if any(not e.get("accession") or not e.get("period_end") for e in ev):
        return False
    vals = _evidence_values(ev)
    mags = [abs(v) for v in vals]
    scaled = mags + [m / 1e9 for m in mags] + [m / 1e6 for m in mags]
    a = norm(rec.get("answer"))
    # Percentage-point and basis-point figures are differences of ratios, not amounts; they are traced as
    # such and removed before the remaining numbers are read (calibration round 3, slot P08).
    for p in _pps(a):
        if not _pct_traceable(p, vals):
            return False
    a = BPS.sub(" ", PP.sub(" ", a))
    for v, raw, pct in agent.numbers_in(a):
        if pct:
            if not _pct_traceable(v, vals):
                return False
            continue
        cands = scaled if not re.search(r"[$a-z]", raw, re.I) else mags
        derived = [abs(x - y) for x in vals for y in vals if x != y]
        if not any(abs(v - t) <= REL_EVIDENCE * max(t, 1) for t in cands + derived + [d / 1e9 for d in derived]
                   + [d / 1e6 for d in derived]):
            return False
    return True


def _pct_traceable(p, vals, tol=0.2):
    big = [v for v in vals if v]
    ratios = [100 * x / y for x in big for y in big if x != y]
    changes = [100 * (x - y) / abs(y) for x in big for y in big if x != y]
    pp = [r1 - r2 for r1 in ratios for r2 in ratios if r1 != r2] if len(big) <= 8 else []
    return any(abs(abs(c) - p) <= tol for c in ratios + changes + pp)


def concept_state(item, rec, alt):
    """canonical | qualified_alternative | incorrect | n/a, from the evidence cells matched to gold cells."""
    gc = item["gold_cells"]
    if not gc:
        return "n/a"
    ev, _ = evidence_of(rec)

    plan_metric = (item["gold_plan"] or {}).get("metric")

    def matches(cells):
        # Each gold cell is compared with the system's cell for the same company, metric and period; if the
        # system has no cell for that period (a wrong period, scored by period_ok), with its cells for the
        # same company and metric (calibration round 2, F11). Every compared cell must use the concept, so a
        # list that mixes concepts across years is not a match (round 2, F15).
        for c in cells:
            want = c.get("metric", plan_metric)       # alternative cells carry no metric (round 1, L1, L2)
            same = [e for e in ev if e.get("ticker") == c["ticker"] and (e.get("metric") or want) == want]
            here = [e for e in same if e.get("period") == c["period"]] or same
            if not here or not all(e.get("concept") == c["concept"] for e in here):
                return False
        return True

    if matches(gc):
        return "canonical"
    if alt and matches(alt["cells"]):
        return "qualified_alternative"
    return "incorrect"


def period_ok(item, rec):
    gc = item["gold_cells"]
    if not gc:
        return None
    ev, _ = evidence_of(rec)
    # matched on company and period end only, so a wrong metric is scored by concept, not here
    # (calibration round 2, slots F05, F10)
    return all(any(e.get("ticker") == c["ticker"] and e.get("period_end") == c["period_end"] for e in ev)
               for c in gc)


def plan_valid(rec):
    if rec.get("system") != "v0.2":
        return None
    import jsonschema
    schema = json.loads((DIR / "plan.schema.json").read_text(encoding="utf-8"))
    try:
        jsonschema.validate(rec.get("plan"), schema)
        return True
    except jsonschema.ValidationError:
        return False


def intent_ok(item, rec):
    """v0.2 only. Answer items: plan intent equals gold intent. Refusal items (rule after calibration round
    4, F07/F08): a refusal plan with the right reason passes; a lookup, comparison or calculation plan, or a
    refusal for another reason (e.g. not_reported passed off as unsupported advice), fails. For
    not_reported the gold lookup plan is also right, since a planner cannot know before execution that a
    filer does not report the line. Whether the final answer refuses is scored by appropriate_refusal."""
    if rec.get("system") != "v0.2":
        return None
    plan = rec.get("plan") if isinstance(rec.get("plan"), dict) else {}
    outcome = item["gold_outcome"]
    if outcome in REFUSALS:
        if "refuse" in plan:
            return plan["refuse"] == outcome
        return outcome == "not_reported" and bool(item["gold_plan"]) and plan.get("intent") == item["gold_plan"]["intent"]
    if not item["gold_plan"]:
        return None
    return plan.get("intent") == item["gold_plan"]["intent"]


def _formula(o, metric):
    d = o["derived_metrics"].get(metric)
    return d["formula"].split() if d else None


def calculation_ok(item, rec, ontology):
    """Given the system's own plan and its own resolved cells, does its result follow from them by the
    formula of its plan's intent and metric? Wrong metric or wrong period are scored elsewhere (concept,
    period_ok); this only checks the arithmetic (calibration round 2, slots F10, F11). The system's cells
    are taken per company and metric in period order, whatever periods it resolved."""
    if rec.get("system") != "v0.2" or item["gold_outcome"] not in ANSWER_OUTCOMES:
        return None
    # The gold intent fixes the formula (spec: "the computed result equals the gold result" given the cells);
    # metric, companies and periods are the system's own, so a wrong metric or period is not scored twice.
    # A wrong intent is scored by intent_ok only (round 1, S3).
    sp = rec.get("plan") if isinstance(rec.get("plan"), dict) else {}
    gp = item["gold_plan"] or {}
    plan = sp if all(k in sp for k in ("metric", "companies", "periods")) else gp
    res = rec.get("result") or {}
    ev = evidence_of(rec)[0]
    metric, intent = plan.get("metric"), gp.get("intent")

    def series(t, m):
        return [e.get("value") for e in sorted((e for e in ev if e.get("ticker") == t and e.get("metric") == m),
                                               key=lambda e: str(e.get("period_end") or e.get("period")))]

    def cell(t, i):
        f = _formula(ontology, metric)
        if not f:
            s = series(t, metric)
            return s[i] if i < len(s) else None
        xs, ys = series(t, f[0]), series(t, f[2])
        if i >= len(xs) or i >= len(ys) or xs[i] is None or ys[i] is None:
            return None
        return xs[i] / ys[i] * 100 if f[1] == "/" else xs[i] - ys[i]

    try:
        vals = [cell(t, i) for t in plan["companies"] for i in range(len(plan["periods"]))]
        if any(v is None for v in vals):
            return False
        if intent == "absolute_change":
            want = vals[1] - vals[0]
        elif intent == "percent_change":
            want = None if vals[0] <= 0 else (vals[1] - vals[0]) / vals[0] * 100
        elif intent == "percentage_point_change":
            want = vals[1] - vals[0]
        elif intent in ("ratio", "fact_lookup", "restated_value_lookup"):
            want = vals[0]
        # A computed result may be rounded for display; it is compared with the item tolerance, the same one
        # final-answer correctness uses (calibration round 4, F10: -2.14 for -2.1404 failed at 1e-6).
        tol = item.get("tolerance") or {"kind": "relative", "rel": 0.005}

        def close(g, w):
            if not isinstance(g, (int, float)):
                return False
            if tol["kind"] == "relative":
                return abs(g - w) <= tol["rel"] * max(abs(w), 1e-9)
            return abs(g - w) <= tol["abs"]

        if intent not in ("absolute_change", "percent_change", "percentage_point_change", "ratio", "fact_lookup",
                          "restated_value_lookup"):
            got = res.get("vals")
            return isinstance(got, list) and len(got) == len(vals) and all(close(g, w) for g, w in zip(got, vals))
        got = res.get("val")
        if want is None:
            return res.get("outcome") == "not_meaningful"
        return close(got, want)
    except (KeyError, TypeError, ZeroDivisionError):
        return False


def clean(rec):
    """A record in the documented shape, never raising: a non-string answer becomes "", a plan or result
    that is not an object becomes null (an invalid plan then fails plan_valid). format_ok says whether
    the input already had the documented shape."""
    rec = rec if isinstance(rec, dict) else {}
    ok = record_format_ok(rec)
    out = dict(rec)
    if not isinstance(out.get("answer"), str):
        out["answer"] = ""
    for k in ("plan", "result"):
        if out.get(k) is not None and not isinstance(out[k], dict):
            ok = False
            out[k] = {"_invalid": out[k]} if k == "plan" else None
    return out, ok


def score_item(item, rec, alt, ontology):
    rec, format_ok = clean(rec)
    correct, path, detail = final_correct(item, rec, alt)
    return {"id": item["id"], "layer": item["layer"], "system": rec.get("system"),
            "record_format_ok": format_ok,
            "final_correct": correct, "path": path,
            "appropriate_refusal": appropriate_refusal(item, rec, correct, path),
            "evidence_complete": evidence_complete(rec),
            "plan_valid": plan_valid(rec), "intent_ok": intent_ok(item, rec),
            "concept": concept_state(item, rec, alt), "period_ok": period_ok(item, rec),
            "calculation_ok": calculation_ok(item, rec, ontology), "detail": detail}


# ---------------------------------------------------------------- run-level
def score_run(records, split="test"):
    import yaml
    gold, alts = load_gold(split)
    ontology = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in records}
    missing = sorted(set(gold) - set(by_id))
    rows = [score_item(gold[i], by_id.get(i, {"id": i, "answer": ""}), alts.get(i), ontology) for i in sorted(gold)]
    return rows, missing


def summary(rows):
    out = {}
    for layer in sorted({r["layer"] for r in rows}) + ["all"]:
        rs = [r for r in rows if layer == "all" or r["layer"] == layer]
        s = {"n": len(rs)}
        for k in ("final_correct", "appropriate_refusal", "evidence_complete", "plan_valid", "intent_ok",
                  "period_ok", "calculation_ok"):
            vals = [r[k] for r in rs if r[k] is not None]
            s[k] = f"{sum(vals)}/{len(vals)}" if vals else None
        c = Counter(r["concept"] for r in rs if r["concept"] != "n/a")
        s["concept_canonical"] = f"{c['canonical']}/{sum(c.values())}" if c else None
        s["concept_states"] = dict(c)
        s["qualified_alternative_answers"] = sum(r["path"] == "qualified_alternative" for r in rs)
        out[layer] = s
    return out


def paired(rows_a, rows_b):
    """2x2 per layer on final_correct, off-diagonal ids, McNemar exact two-sided p (secondary)."""
    a = {r["id"]: r for r in rows_a}
    b = {r["id"]: r for r in rows_b}
    out = {}
    for layer in sorted({r["layer"] for r in rows_a}) + ["all"]:
        ids = [i for i in sorted(a) if i in b and (layer == "all" or a[i]["layer"] == layer)]
        cells = {"both_right": [], "a_only": [], "b_only": [], "both_wrong": []}
        for i in ids:
            x, y = a[i]["final_correct"], b[i]["final_correct"]
            cells["both_right" if x and y else "a_only" if x else "b_only" if y else "both_wrong"].append(i)
        n01, n10 = len(cells["b_only"]), len(cells["a_only"])
        n = n01 + n10
        p = min(1.0, 2 * sum(math.comb(n, k) for k in range(0, min(n01, n10) + 1)) / 2 ** n) if n else 1.0
        out[layer] = {"counts": {k: len(v) for k, v in cells.items()}, "a_only": cells["a_only"],
                      "b_only": cells["b_only"], "mcnemar_exact_p": p}
    return out


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--split", default="test")
    ap.add_argument("--paired")
    args = ap.parse_args(argv)
    load = lambda p: [json.loads(ln) for ln in open(p, encoding="utf-8") if ln.strip()]
    rows, missing = score_run(load(args.run), args.split)
    rep = {"scorer_version": V, "split": args.split, "missing_records": missing, "summary": summary(rows), "items": rows}
    if args.paired:
        rows_b, _ = score_run(load(args.paired), args.split)
        rep["paired"] = paired(rows, rows_b)
    print(json.dumps(rep["summary"], indent=1))
    return rep


if __name__ == "__main__":
    main(sys.argv[1:])
