"""Renderer: structured execution result -> final answer text, by the model, one call, no retry, no rewrite.

Policy (docs/engine-v0.2-decisions.md): qwen3:8b, temperature 0, one call, no tools. Input only: the
question, the validated plan, the structured execution result, the evidence items and the warnings as
semantic codes with a plain description. No scorer patterns, match words or validation results. The output
is returned exactly as the model wrote it; the prompt, the structured input and the raw output are kept.
"""
import json

from . import llm

SYSTEM = """You write the final answer to a question about companies' annual 10-K financial data.

You are given the question, a plan, and the result that code has already computed from the filings. Write a
short answer for the person who asked, in plain English.

- Use only the numbers in the result and evidence. Do not compute new figures and do not add numbers that are
  not given. Keep each number's meaning (which company, which fiscal year, which quantity).
- "display" gives each number of the result already written out with its unit (formatted by code). Use
  those strings as written; do not convert them to other units or scales.
- Say whether a change is an increase or a decrease when the result gives a direction.
- Every item in "warnings" matters to the reader: explain each one in your own words in the answer.
- If the outcome is not "answer", say plainly that the figure cannot be given and why (use the reason given),
  and give no figure for what was asked.
- Do not give investment advice or forecasts.
- Name the fiscal years and, where useful, the filing (accession) the figures come from."""


def fmt(v, unit, kind="amount"):
    """One number as text with its unit. Amounts in USD and share counts are written in millions, as the
    10-K statements present them; nothing is rounded beyond what the reader needs (0.1 million, 0.01 USD,
    0.1 percent or percentage point)."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    if kind == "percent_change":
        return f"{v:.1f}%"
    if kind == "pp_change":
        return f"{v:.1f} percentage points"
    if unit == "percent":
        return f"{v:.1f}%"
    if unit == "USD/shares":
        return f"{'-' if v < 0 else ''}${abs(v):.2f} per share"
    if unit in ("USD", "shares"):
        a = abs(v)
        if a >= 1e6:
            m = a / 1e6
            s = f"{m:,.0f}" if abs(m - round(m)) < 1e-6 else f"{m:,.1f}"
            s += " million"
        else:
            s = f"{a:,.0f}"
        sign = "-" if v < 0 else ""
        return f"{sign}${s}" if unit == "USD" else f"{sign}{s} shares"
    return f"{v:,} {unit}" if unit else f"{v:,}"


def display(result):
    """Formatted strings for every number in the execution result (same keys as the result)."""
    res = result.get("result")
    if not isinstance(res, dict):
        return None
    unit, out = res.get("unit"), {}
    for k in ("value", "difference", "absolute_change", "current", "original"):
        if k in res and fmt(res[k], unit) is not None:
            out[k] = fmt(res[k], unit)
    if isinstance(res.get("values"), dict):
        out["values"] = {k: fmt(v, unit) for k, v in res["values"].items()}
    for k, kind in (("percent_change", "percent_change"), ("magnitude_change_pct", "percent_change"),
                    ("pp_change", "pp_change")):
        if fmt(res.get(k), unit, kind) is not None:
            out[k] = fmt(res[k], unit, kind)
    return out or None


def render_input(question, plan, result):
    """The renderer's structured input: nothing else is shown to the model."""
    keep = ("outcome", "reason", "result", "alignment", "warnings")
    ev = [{k: e.get(k) for k in ("id", "ticker", "metric", "fy", "concept", "value", "unit", "period_end", "accession",
                                 "component_of")} for e in result.get("evidence", [])]
    out = {"question": question, "plan": plan, "execution": {k: result[k] for k in keep if k in result}}
    d = display(result) if result.get("outcome") == "answer" else None
    if d:
        out["display"] = d
    out["evidence"] = ev
    return out


def render(question, plan, result, log=None, model=None, post=None):
    log = log or llm.CallLog()
    data = render_input(question, plan, result)
    user = json.dumps(data, indent=1, default=str)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    kw = {"post": post} if post else {}
    text = llm.chat(msgs, "renderer", log, model=model, **kw)        # one call, no retry
    return {"answer": text, "renderer_input": data, "renderer_system": SYSTEM}
