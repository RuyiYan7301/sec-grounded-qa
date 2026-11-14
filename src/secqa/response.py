"""Structured answer: what the CLI prints, the web demo shows and `--json` emits.

Built from the agent's raw result. Every field comes from the tool trace or the checks,
not from the model's wording, so a reader can audit an answer without trusting it.
"""
import json
import re
from dataclasses import asdict, dataclass, field

from . import agent, edgar, guards

STATUS_TEXT = {
    "verified": "All checks passed: every number traces to an XBRL fact, and the concept, period and text checks found no problem.",
    "unverified": "Checks found problems (single-pass mode returns the answer anyway; see checks).",
    "withheld": "The draft failed verification twice, so no answer is given.",
}


@dataclass
class Fact:
    ticker: str
    concept: str
    label: str
    period: str
    value: float
    unit: str
    display: str
    period_end: str
    accession: str
    form: str
    filed: str
    url: str
    restated: bool = False


@dataclass
class Source:
    citation: str
    chunk_id: str
    accession: str
    url: str
    excerpt: str


@dataclass
class ToolCall:
    tool: str
    args: dict
    ok: bool
    summary: str


@dataclass
class Answer:
    question: str
    answer: str
    status: str
    model: str
    mode: str
    facts: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    grounded: bool = True
    ungrounded_numbers: list = field(default_factory=list)
    draft: str | None = None
    latency_s: float = 0.0
    llm_calls: int = 0
    tokens: int = 0

    @property
    def status_text(self):
        return STATUS_TEXT[self.status]

    def to_dict(self):
        return asdict(self) | {"status_text": self.status_text}

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, default=str)


def _facts(answer, trace):
    """Facts from get_fact/compare results whose value is stated in the answer, with their filing."""
    used = agent.facts_used(answer, trace)
    out = []
    for u in used:
        rec = None
        for s in trace:
            r = s["result"]
            rows = r.get("facts", []) if s["tool"] == "get_fact" and r.get("found") else r.get("rows", []) if s["tool"] == "compare" else []
            for f in rows:
                vals = [f.get("val")] + [o["val"] for o in f.get("other_values", [])]
                tk = r.get("ticker") or f.get("ticker")
                if tk == u["ticker"] and u["val"] in vals:
                    other = next((o for o in f.get("other_values", []) if o["val"] == u["val"]), None)
                    rec = {**f, **(other or {}), "unit": f.get("unit"), "end": f.get("end"),
                           "other_values": f.get("other_values", []) if other is None else []}
                    break
            if rec:
                break
        if rec is None:
            continue
        accn = rec.get("accn", "")
        out.append({"fact": Fact(ticker=u["ticker"], concept=u["tag"], label=u["label"], period=u["period"] or "",
                                 value=u["val"], unit=rec.get("unit") or "", display=rec.get("display") or "",
                                 period_end=rec.get("end") or "", accession=accn, form=rec.get("form", ""),
                                 filed=rec.get("filed", ""), url=edgar.filing_url(u["ticker"], accn) if accn else "",
                                 restated=u["restated_value"]),
                    "other_values": rec.get("other_values", []), "tag": u["tag"], "ticker": u["ticker"],
                    "period": u["period"], "end": rec.get("end"), "display": rec.get("display"), "form": rec.get("form", ""), "accn": accn})
    return out


def _sources(trace):
    seen, out = set(), []
    for s in trace:
        if s["tool"] != "search_filings":
            continue
        for p in s["result"].get("passages", []):
            if p["chunk_id"] in seen:
                continue
            seen.add(p["chunk_id"])
            m = re.search(r"accession (\S+)", p["source"])
            accn = m.group(1) if m else ""
            tk = p["chunk_id"].split("-")[0]
            text = re.sub(r"</?filing_excerpt>", "", p["text"]).strip()
            out.append(Source(citation=p["source"], chunk_id=p["chunk_id"], accession=accn,
                              url=edgar.filing_url(tk, accn) if accn and tk in edgar.FILERS else "", excerpt=text))
    return out


def _summary(tool, args, res):
    if res.get("error"):
        return res["error"]
    if res.get("found") is False:
        return f"{res.get('reason')}: {res.get('detail', '')}".strip(": ")
    if tool == "list_concepts":
        return f"{len(res['candidates'])} candidate tags: " + ", ".join(c["tag"] for c in res["candidates"][:4])
    if tool == "get_fact":
        f = res["facts"][0]
        return f"{res['ticker']} {res['tag']} {res['period']} = {f['display']} (ends {f['end']}, {f['form']} {f['accn']})"
    if tool == "compare":
        rows = "; ".join(f"{r['ticker']} {r.get('display', r.get('reason'))}" for r in res["rows"])
        return rows + ("  [period mismatch]" if res.get("period_mismatch") else "")
    if tool == "search_filings":
        return f"{len(res['passages'])} passages"
    if tool == "filer_info":
        return ", ".join(f"{f['ticker']} FYE {f['fiscal_year_end_mmdd']}" for f in res["filers"])
    return "ok"


def build(raw, question=None, extra_warnings=()):
    trace = raw["trace"]
    answer = raw["answer"]
    if answer == agent.FALLBACK:
        status = "withheld"
    elif raw["final_problems"]:
        status = "unverified"
    else:
        status = "verified"
    facts = _facts(answer, trace)
    warns = list(extra_warnings) + guards.trace_warnings(trace, facts, raw.get("hint"))
    if not raw["grounded"]:
        warns.append(guards.warning("ungrounded_numbers", "Numbers not found in any tool result: "
                                    + ", ".join(raw["ungrounded_numbers"])))
    return Answer(
        question=question or raw["question"], answer=answer, status=status, model=raw["model"], mode=raw["arm"],
        facts=[f["fact"] for f in facts], sources=_sources(trace),
        tool_calls=[ToolCall(tool=s["tool"], args=s["args"], ok=not s["result"].get("error") and s["result"].get("found", True) is not False,
                             summary=_summary(s["tool"], s["args"], s["result"])) for s in trace],
        checks=list(raw["final_problems"]),
        warnings=warns, grounded=raw["grounded"], ungrounded_numbers=raw["ungrounded_numbers"],
        draft=raw["draft"] if raw.get("revised") else None, latency_s=raw["latency_s"],
        llm_calls=raw["llm_calls"], tokens=raw["tokens_in"] + raw["tokens_out"])


def ask(question, company=None, fiscal_year=None, model=None, mode="verify"):
    """Validate, answer, and return a structured Answer. Raises guards.InputError for bad input."""
    ticker, fy = guards.check_input(question, company, fiscal_year)
    q = guards.compose(question, ticker, fy)
    raw = agent.ask(q, model=model, arm=mode)
    return build(raw, question=q, extra_warnings=guards.question_warnings(q))
