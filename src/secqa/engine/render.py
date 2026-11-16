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
- State amounts with units, e.g. "$12.3 billion" or "2,866 million shares"; per-share amounts in dollars and
  cents; percentages and percentage points as given.
- Say whether a change is an increase or a decrease when the result gives a direction.
- Every item in "warnings" matters to the reader: explain each one in your own words in the answer.
- If the outcome is not "answer", say plainly that the figure cannot be given and why (use the reason given),
  and give no figure for what was asked.
- Do not give investment advice or forecasts.
- Name the fiscal years and, where useful, the filing (accession) the figures come from."""


def render_input(question, plan, result):
    """The renderer's structured input: nothing else is shown to the model."""
    keep = ("outcome", "reason", "result", "alignment", "warnings")
    ev = [{k: e.get(k) for k in ("id", "ticker", "metric", "fy", "concept", "value", "unit", "period_end", "accession",
                                 "component_of")} for e in result.get("evidence", [])]
    return {"question": question, "plan": plan, "execution": {k: result[k] for k in keep if k in result},
            "evidence": ev}


def render(question, plan, result, log=None, model=None, post=None):
    log = log or llm.CallLog()
    data = render_input(question, plan, result)
    user = json.dumps(data, indent=1, default=str)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    kw = {"post": post} if post else {}
    text = llm.chat(msgs, "renderer", log, model=model, **kw)        # one call, no retry
    return {"answer": text, "renderer_input": data, "renderer_system": SYSTEM}
