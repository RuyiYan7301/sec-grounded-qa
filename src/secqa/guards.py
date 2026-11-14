"""Deterministic checks around the model: input validation before it runs, warnings after.

None of these change what the model answers (the evaluated agent is unchanged). Input
validation rejects requests the system cannot serve before any model call; warnings make
the traps visible to the person reading the answer, from the tool results rather than from
the model's wording.
"""
import re
from datetime import date

from .edgar import FILERS
from .facts import INDEXED_FY

NAMES = {"AAPL": "Apple", "NVDA": "Nvidia", "MSFT": "Microsoft", "ORCL": "Oracle", "CSCO": "Cisco",
         "AVGO": "Broadcom", "INTC": "Intel", "AMD": "AMD"}
ALIASES = {"AAPL": ["apple", "aapl"], "NVDA": ["nvidia", "nvda"], "MSFT": ["microsoft", "msft"],
           "ORCL": ["oracle", "orcl"], "CSCO": ["cisco", "csco"], "AVGO": ["broadcom", "avgo"],
           "INTC": ["intel", "intc"], "AMD": ["amd", "advanced micro devices"]}
MAX_QUESTION = 2000


class InputError(ValueError):
    """A request that is rejected before any model call."""


def warning(code, message):
    return {"code": code, "message": message}


def companies_in(text):
    low = text.lower()
    return [t for t, names in ALIASES.items() if any(re.search(r"\b" + re.escape(n) + r"\b", low) for n in names)]


def parse_fiscal_year(value):
    """'FY2024', '2024', 2024 -> 2024. None or '' -> None."""
    if value in (None, "", "Any"):
        return None
    m = re.fullmatch(r"\s*(?:FY\s*)?(\d{4})\s*", str(value), re.I)
    if not m:
        raise InputError(f"Fiscal year must look like FY2024, got {value!r}.")
    return int(m.group(1))


def check_input(question, company=None, fiscal_year=None):
    """Validate a request. Returns (ticker or None, fiscal year or None); raises InputError."""
    q = (question or "").strip()
    if not q:
        raise InputError("The question is empty.")
    if len(q) > MAX_QUESTION:
        raise InputError(f"The question is {len(q):,} characters; the limit is {MAX_QUESTION:,}.")
    ticker = None
    if company not in (None, "", "Any"):
        key = str(company).strip().upper()
        by_name = {v.upper(): k for k, v in NAMES.items()}
        ticker = key if key in FILERS else by_name.get(key)
        if ticker is None:
            raise InputError(f"{company} is not covered. Covered companies: "
                             + ", ".join(f"{NAMES[t]} ({t})" for t in FILERS) + ".")
    fy = parse_fiscal_year(fiscal_year)
    if fy is not None and fy not in INDEXED_FY:
        raise InputError(f"FY{fy} is not covered. Covered fiscal years: "
                         + ", ".join(f"FY{y}" for y in INDEXED_FY) + ".")
    return ticker, fy


def compose(question, ticker=None, fy=None):
    """Question text sent to the model, with the selected company and fiscal year made explicit."""
    q = question.strip()
    ctx = []
    if ticker and ticker not in companies_in(q):
        ctx.append(f"company: {NAMES[ticker]} ({ticker})")
    if fy and not re.search(rf"\b{fy}\b", q):
        ctx.append(f"fiscal year: FY{fy}")
    return q + (f"\n\n(Selected {'; '.join(ctx)}.)" if ctx else "")


def question_warnings(question):
    out = []
    if not companies_in(question):
        out.append(warning("no_company", "The question names none of the covered companies; "
                                         "the assistant should ask which one is meant."))
    years = sorted({int(y) for y in re.findall(r"\b(20\d\d)\b", question)} - set(INDEXED_FY))
    if years:
        out.append(warning("out_of_range", "Years outside the covered fiscal years FY2023-FY2025: "
                                           + ", ".join(map(str, years)) + "."))
    return out


MISSING = {"tag_not_used": "missing_data", "no_fact_for_period": "missing_data",
           "out_of_range": "out_of_range", "not_indexed_filer": "not_covered", "ambiguous_year": "ambiguous_year"}


def trace_warnings(trace, used_facts, hint=None):
    """Warnings derived from tool results: period mismatches, restatements, missing data, ambiguity."""
    out, seen = [], set()

    def add(code, msg):
        if (code, msg) not in seen:
            seen.add((code, msg))
            out.append(warning(code, msg))

    if hint:
        add("ambiguous_year", hint.split("Note from the system, not the user: ")[-1])
    for s in trace:
        r = s.get("result") or {}
        if s["tool"] == "compare" and r.get("period_mismatch"):
            add("period_mismatch", "Fiscal periods do not line up: " + r.get("mismatch_reason", ""))
        if r.get("found") is False and r.get("reason") in MISSING:
            code = MISSING[r["reason"]]
            # A wrong tag tried on the way to a found fact is not missing data.
            if code != "missing_data" or not used_facts:
                add(code, r.get("detail") or r["reason"])
    # Same fiscal-year label, different calendar periods. Checked on the facts the answer uses,
    # so it fires even when the model fetched each company with get_fact instead of compare.
    by_label = {}
    for f in used_facts:
        if f.get("end") and f.get("period"):
            by_label.setdefault(f["period"], {}).setdefault(f["ticker"], f["end"])
    for label, ends in by_label.items():
        days = sorted(date.fromisoformat(e) for e in ends.values())
        if len(ends) >= 2 and (days[-1] - days[0]).days > 31 and not any(c == "period_mismatch" for c, _ in seen):
            add("period_mismatch", f"{label} is a different period for each company: "
                + ", ".join(f"{t} ends {e}" for t, e in ends.items()) + ".")
    for f in used_facts:
        if f.get("other_values"):
            o = f["other_values"][0]
            add("restated", f"{f['ticker']} {f['tag']} {f['period']} was reported as {o['display']} in "
                            f"{o['form']} {o['accn']} and as {f['display']} in the later {f['form']} {f['accn']}.")
    return out
