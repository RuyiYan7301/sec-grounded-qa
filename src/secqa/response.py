"""Structured answer: what the CLI prints, the web demo shows and `--json` emits.

Built from the agent's raw result. Every field comes from the tool trace, the fact store or
the checks, not from the model's wording, so a reader can audit an answer without trusting it.
Nothing here changes what the model sees or answers.
"""
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from functools import lru_cache

from . import agent, edgar, guards, tools
from .facts import fiscal_year as _fiscal_year

# Status, from strongest to weakest. A status only claims what the checks established.
STATUS = {
    "verified": ("VERIFIED",
                 "Every number traces to an XBRL fact and every check passed. Nothing to flag."),
    "verified_with_warnings": ("VERIFIED WITH WARNINGS",
                               "Every number traces to an XBRL fact and every check passed. The warnings below "
                               "describe the data itself (for example, periods that do not line up), and the answer "
                               "mentions each one."),
    "traceable": ("TRACEABLE",
                  "Every number traces to an XBRL fact, but something is unresolved: a check failed, or the answer "
                  "does not mention one of the warnings below. Read them before using the answer."),
    "unverified": ("UNVERIFIED",
                   "Some numbers do not trace to any XBRL fact. Single mode returns the answer anyway; do not rely on it."),
    "withheld": ("WITHHELD",
                 "The draft failed verification twice, so no answer is given. The checks say why."),
}

# Warnings the answer itself should mention, and how to tell that it did.
MENTIONED = {
    "period_mismatch": agent.MISMATCH_WORDS,
    "restated": re.compile(r"restat|recast|revis|originally|previously reported|earlier (?:filing|report)|"
                           r"later (?:filing|report)|first reported|adjusted", re.I),
    "ambiguous_year": re.compile(r"fiscal or calendar|calendar or fiscal|which (?:one|period|year)|clarify|\?", re.I),
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
    accession: str                     # filing the value is taken from
    form: str
    filed: str
    filing_fiscal_year: int | None     # fiscal year that filing covers
    url: str
    first_accession: str               # filing that first reported this period
    first_form: str
    first_filed: str
    first_filing_fiscal_year: int | None
    provenance: str                    # which filing the value comes from, in one sentence
    restated: bool = False             # True: this is an earlier reported value, since revised


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
    def status_label(self):
        return STATUS[self.status][0]

    @property
    def status_text(self):
        return STATUS[self.status][1]

    def to_dict(self):
        return asdict(self) | {"status_label": self.status_label, "status_text": self.status_text}

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------- filing provenance

@lru_cache(maxsize=None)
def _filings(ticker):
    """accession -> fiscal year the filing covers, from the cached filing list."""
    sub = edgar.submissions(ticker)
    r, fye = sub["filings"]["recent"], sub.get("fiscalYearEnd") or "1231"
    return {accn: _fiscal_year(date.fromisoformat(rd), fye) if rd else None
            for accn, rd in zip(r["accessionNumber"], r["reportDate"])}


def _filing_fy(ticker, accn):
    try:
        return _filings(ticker).get(accn)
    except FileNotFoundError:
        return None


def _name(form, fy, filed):
    return f"{'FY' + str(fy) + ' ' if fy else ''}{form} filed {filed}"


def _provenance(period, rec, src, restated_value, fy, first_fy):
    if restated_value:
        return f"Earlier reported value, from the {_name(src['form'], fy, src['filed'])}. Later filings report a different figure."
    here = _name(rec["form"], fy, rec["filed"])
    if rec["accn"] == rec["first_accn"]:
        return f"Reported in the {here}."
    text = f"{period} value as shown in the {here}, the latest annual report that includes it"
    if fy and fy > rec["fiscal_year"]:
        text += " (as a prior-year comparative)"
    text += f". First reported in the {_name(rec['first_form'], first_fy, rec['first_filed'])}"
    return text + ("; revised since (see warnings)." if rec["other_values"] else "; unchanged since.")


def _period_end(u, trace):
    """Period end of the tool result the answer's value came from."""
    for s in trace:
        r = s["result"]
        if s["tool"] == "get_fact" and r.get("found"):
            rows = [(r["ticker"], r["tag"], f) for f in r["facts"]]
        elif s["tool"] == "compare":
            rows = [(f["ticker"], f["tag"], f) for f in r.get("rows", []) if f.get("found")]
        else:
            continue
        for tk, tag, f in rows:
            vals = [f["val"]] + [o["val"] for o in f.get("other_values", [])]
            if tk == u["ticker"] and tag == u["tag"] and u["val"] in vals:
                return f["end"]
    return None


def _facts(answer, trace):
    """Facts whose value the answer states, each with the filing it comes from.

    The record is looked up in the fact store by (ticker, tag, period end), so a value that came
    through compare() gets the same filing details as one that came through get_fact()."""
    out = []
    for u in agent.facts_used(answer, trace):
        end = _period_end(u, trace)
        recs = [x for x in tools.store().facts.get(u["ticker"], {}).get(u["tag"], [])
                if x["end"] == end and (x["val"] == u["val"] or any(o["val"] == u["val"] for o in x["other_values"]))]
        if not recs:
            continue
        rec = next((x for x in recs if x["kind"] in ("FY", "instant")), recs[0])
        restated_value = rec["val"] != u["val"]
        src = {**rec, **next(o for o in rec["other_values"] if o["val"] == u["val"])} if restated_value else rec
        fy, first_fy = _filing_fy(u["ticker"], src["accn"]), _filing_fy(u["ticker"], rec["first_accn"])
        display = tools.display(u["val"], rec["unit"])
        fact = Fact(ticker=u["ticker"], concept=u["tag"], label=u["label"], period=u["period"] or "", value=u["val"],
                    unit=rec["unit"], display=display, period_end=rec["end"], accession=src["accn"], form=src["form"],
                    filed=src["filed"], filing_fiscal_year=fy, url=edgar.filing_url(u["ticker"], src["accn"]),
                    first_accession=rec["first_accn"], first_form=rec["first_form"], first_filed=rec["first_filed"], first_filing_fiscal_year=first_fy,
                    provenance=_provenance(u["period"] or "", rec, src, restated_value, fy, first_fy),
                    restated=restated_value)
        out.append({"fact": fact, "ticker": u["ticker"], "tag": u["tag"], "period": u["period"], "end": rec["end"],
                    "display": display, "form": src["form"], "accn": src["accn"],
                    "other_values": [] if restated_value else
                    [{**o, "display": tools.display(o["val"], rec["unit"])} for o in rec["other_values"]]})
    return out


# ---------------------------------------------------------------- sources and trace

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
        rows = "; ".join(f"{r['ticker']} {r.get('display', r.get('reason'))}" + (f" (ends {r['end']})" if r.get("end") else "")
                         for r in res["rows"])
        return rows + ("  [period mismatch]" if res.get("period_mismatch") else "")
    if tool == "search_filings":
        return f"{len(res['passages'])} passages"
    if tool == "filer_info":
        return ", ".join(f"{f['ticker']} FYE {f['fiscal_year_end_mmdd']}" for f in res["filers"])
    return "ok"


# ---------------------------------------------------------------- assembly

def _status(withheld, raw, warns):
    if withheld:
        return "withheld"
    if not raw["grounded"]:
        return "unverified"
    if raw["final_problems"] or any(w["mentioned_in_answer"] is False for w in warns):
        return "traceable"
    return "verified_with_warnings" if warns else "verified"


def build(raw, question=None, extra_warnings=()):
    trace, answer = raw["trace"], raw["answer"]
    withheld = answer == agent.FALLBACK
    facts = [] if withheld else _facts(answer, trace)
    warns = list(extra_warnings) + guards.trace_warnings(trace, facts, raw.get("hint"))
    if not raw["grounded"]:
        warns.append(guards.warning("ungrounded_numbers", "Numbers not found in any tool result: "
                                    + ", ".join(raw["ungrounded_numbers"])))
    for w in warns:  # does the answer itself tell the reader about this?
        pat = MENTIONED.get(w["code"])
        w["mentioned_in_answer"] = None if pat is None or withheld else bool(pat.search(answer))
    return Answer(
        question=question or raw["question"], answer=answer, status=_status(withheld, raw, warns),
        model=raw["model"], mode=raw["arm"], facts=[f["fact"] for f in facts], sources=_sources(trace),
        tool_calls=[ToolCall(tool=s["tool"], args=s["args"],
                             ok=not s["result"].get("error") and s["result"].get("found", True) is not False,
                             summary=_summary(s["tool"], s["args"], s["result"])) for s in trace],
        checks=list(raw["final_problems"]), warnings=warns, grounded=raw["grounded"],
        ungrounded_numbers=raw["ungrounded_numbers"], draft=raw["draft"] if raw.get("revised") else None,
        latency_s=raw["latency_s"], llm_calls=raw["llm_calls"], tokens=raw["tokens_in"] + raw["tokens_out"])


def ask(question, company=None, fiscal_year=None, model=None, mode="verify"):
    """Validate, answer, and return a structured Answer. Raises guards.InputError for bad input."""
    ticker, fy = guards.check_input(question, company, fiscal_year)
    q = guards.compose(question, ticker, fy)
    raw = agent.ask(q, model=model, arm=mode)
    return build(raw, question=q, extra_warnings=guards.question_warnings(q))
