"""Answer a question with the v0.2 typed engine and return the same structured Answer the CLI and web demo show.

planner (typed plan, schema-validated, one repair) -> deterministic execution -> renderer (one call). Facts,
warnings and the step trace come from the engine's structured output, never from the rendered wording. A
number in the rendered answer that matches no evidence value or computed result is reported as a check
failure and lowers the status, so a renderer slip is visible to the reader.
"""
import json
import time
from functools import lru_cache

import yaml

from . import config, edgar, guards, response
from .engine import execute, llm, plan, render, resolve
from .facts import Store

REFUSALS = {"out_of_ontology", "not_reported", "unsupported", "out_of_range", "unsupported_operation",
            "not_meaningful", "invalid_plan", "ambiguous_concept"}


@lru_cache(maxsize=1)
def _engine():
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    return o, resolve.SnapshotSource(Store())


def _result_numbers(result):
    out = []

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            out.append(float(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(result)
    return out


def untraced_numbers(answer, ex):
    """Numbers in the rendered answer that match no evidence value and no computed result (magnitudes; values
    may be written in millions or billions; percentages may be a result or a ratio of two evidence values)."""
    from .agent import numbers_in
    vals = [abs(e["value"]) for e in ex.get("evidence", []) if isinstance(e.get("value"), (int, float))]
    vals += [abs(v) for v in _result_numbers(ex.get("result"))]
    cands = vals + [v / 1e6 for v in vals] + [v / 1e9 for v in vals]
    bad = []
    for v, raw, pct in numbers_in(answer):
        if pct:
            ok = any(abs(v - c) <= 0.15 for c in vals) or any(
                b and abs(abs(100 * (a - b) / b) - v) <= 0.15 or b and abs(100 * a / b - v) <= 0.15
                for a in vals for b in vals)
        else:
            ok = any(abs(v - c) <= 0.006 * max(c, 1) for c in cands)
        if not ok:
            bad.append(raw)
    return bad


def _fact(e):
    fy, first_fy = response._filing_fy(e["ticker"], e["accession"]), response._filing_fy(e["ticker"], e.get("first_accession") or e["accession"])
    same = (e.get("first_accession") or e["accession"]) == e["accession"]
    prov = (f"Reported in the {response._name(e.get('form', '10-K'), fy, e.get('filed', ''))}." if same else
            f"{e['fy']} value as shown in the {response._name(e.get('form', '10-K'), fy, e.get('filed', ''))}, the latest "
            f"annual report that includes it. First reported in the "
            f"{response._name('10-K', first_fy, e.get('first_filed', ''))}"
            + ("; revised since (see warnings)." if e.get("other_values") else "; unchanged since."))
    from .tools import display
    return response.Fact(
        ticker=e["ticker"], concept=e["concept"], label=e.get("metric") or e["concept"], period=e["fy"],
        value=e["value"], unit=e["unit"], display=display(e["value"], e["unit"]), period_end=e["period_end"],
        accession=e["accession"], form=e.get("form", "10-K"), filed=e.get("filed", ""), filing_fiscal_year=fy,
        url=edgar.filing_url(e["ticker"], e["accession"]), first_accession=e.get("first_accession") or e["accession"],
        first_form="10-K", first_filed=e.get("first_filed") or e.get("filed", ""), first_filing_fiscal_year=first_fy,
        provenance=prov, restated=False)


def ask(question, model=None, post=None, route_why=None, route_calls=()):
    """question already validated and composed by response.ask."""
    o, src = _engine()
    log = llm.CallLog()
    t0 = time.perf_counter()
    kw = {"post": post} if post else {}
    p = plan.make_plan(question, log, model=model, **kw)
    steps = [response.ToolCall(tool="plan", args={"question": question}, ok=p["status"] == "valid",
                               summary=json.dumps(p["plan"]) if p["plan"] else "invalid plan after one repair")]
    if p["status"] != "valid":
        ex = {"outcome": "invalid_plan", "reason": "the question could not be turned into a valid plan",
              "evidence": [], "warnings": []}
        answer = ("I could not turn this question into a plan I can execute, so I am not giving an answer. "
                  "Try naming the company, the figure and the fiscal year.")
    else:
        ex = execute.execute(p["plan"], question, src, o)
        steps.append(response.ToolCall(tool="execute", args={}, ok=ex["outcome"] == "answer",
                                       summary=f"outcome {ex['outcome']}; {len(ex.get('evidence', []))} evidence items; "
                                               f"warnings: {', '.join(w['code'] for w in ex.get('warnings', [])) or 'none'}"))
        answer = render.render(question, p["plan"], ex, log, model=model, **kw)["answer"]
        steps.append(response.ToolCall(tool="render", args={}, ok=True, summary=f"{len(answer)} characters"))
    warns = [guards.warning(w["code"], w.get("detail", "")) for w in ex.get("warnings", [])]
    for w in warns:
        pat = response.MENTIONED.get(w["code"])
        w["mentioned_in_answer"] = None if pat is None else bool(pat.search(answer))
    bad = untraced_numbers(answer, ex) if ex["outcome"] == "answer" else []
    checks = [f"number not traced to evidence or result: {b}" for b in bad]
    if ex["outcome"] != "answer":
        status = "verified"            # no figure is given; the answer states why
    elif bad:
        status = "unverified"
    elif any(w["mentioned_in_answer"] is False for w in warns):
        status = "traceable"
    else:
        status = "verified_with_warnings" if warns else "verified"
    calls = list(route_calls) + log.calls
    if route_why:
        steps.insert(0, response.ToolCall(tool="route", args={}, ok=True, summary=route_why))
    return response.Answer(
        question=question, answer=answer, status=status, model=model or config.DEFAULT_MODEL, mode="typed",
        facts=[_fact(e) for e in ex.get("evidence", [])], sources=[], tool_calls=steps,
        checks=checks, warnings=warns, grounded=not bad, ungrounded_numbers=bad, draft=None,
        latency_s=round(time.perf_counter() - t0, 1), llm_calls=len(calls),
        tokens=sum((c["prompt_tokens"] or 0) + (c["output_tokens"] or 0) for c in calls))
