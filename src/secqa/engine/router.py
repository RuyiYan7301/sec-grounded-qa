"""Route a question to the typed engine (figures) or to the v0.1 agent (filing text).

Rules, in order:
1. The question names none of the covered companies -> agent: it asks back which company is meant, and says
   so when a company is not covered.
2. One model call (temperature 0, JSON) decides "numeric" or "narrative". Questions that ask for investment
   advice, a forecast or an estimate count as numeric: the typed engine refuses them with a stated reason.
   A question that needs both figures and filing text is narrative (the agent has both kinds of tools).
3. A reply that cannot be read falls back to numeric.
"""
from .. import guards
from . import llm

SYSTEM = """You route one question about companies' annual 10-K filings to the part of a system that can answer it.

- "numeric": the question asks for a reported financial figure (revenue, income, EPS, assets, cash flow and the
  like), a change or growth rate, a margin or ratio, or a comparison of such figures, for one or more companies
  and fiscal years. Also numeric: requests for investment advice, forecasts, estimates or valuation, and figures
  the filings may not report.
- "narrative": the question asks what the filing says in words: risk factors, strategy, business description,
  management's explanation of results, segments or products described in text, legal proceedings. If a
  question needs both figures and an explanation from the text, it is narrative.

Return JSON: {"route": "numeric" or "narrative", "reason": "<one short sentence>"}"""


def route(question, log=None, model=None, post=None):
    """{"route": "typed" | "agent", "why": str}"""
    if not guards.companies_in(question):
        return {"route": "agent", "why": "no covered company named; the agent asks which one is meant"}
    log = log or llm.CallLog()
    kw = {"post": post} if post else {}
    text = llm.chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
                    "router", log, model=model, fmt="json", **kw)
    out = llm.parse_json(text) or {}
    if out.get("route") == "narrative":
        return {"route": "agent", "why": "narrative: " + str(out.get("reason") or "")}
    return {"route": "typed", "why": ("numeric: " + str(out.get("reason") or "")) if out.get("route") == "numeric"
            else "unreadable router reply; defaulting to the typed engine"}
