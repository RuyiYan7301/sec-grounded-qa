"""Typed planning: question -> plan, constrained and validated by the frozen plan schema, one repair.

Policy (docs/engine-v0.2-decisions.md): the planner output is constrained with Ollama `format` = the frozen
data/eval/v0.2/plan.schema.json and validated with the same schema. If invalid, ONE repair call whose prompt
holds only the question, the invalid plan and the schema errors. Still invalid -> `invalid_plan`; no
rule-based fallback, no silent change. The planner prompt describes only the ontology, the covered companies
and years, and the plan format; it contains no facts, no gold and nothing from the scorers.
"""
import json
from functools import lru_cache

import jsonschema

from .. import config, ontology
from . import llm

SCHEMA_PATH = config.EVAL_DIR / "v0.2" / "plan.schema.json"
COMPANIES = {"AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "ORCL": "Oracle", "CSCO": "Cisco",
             "AVGO": "Broadcom", "INTC": "Intel", "AMD": "AMD"}
YEARS = ("FY2023", "FY2024", "FY2025")
MAX_REPAIRS = 1          # fixed before any dev run


@lru_cache(maxsize=1)
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate(plan):
    """Schema errors of a plan (empty list = valid)."""
    v = jsonschema.Draft202012Validator(schema(), format_checker=jsonschema.FormatChecker())
    return [f"{'/'.join(map(str, e.absolute_path)) or '(plan)'}: {e.message}" for e in v.iter_errors(plan)]


def _metric_lines(o):
    """Metric ids, names, aliases and allowed operations, all read from the frozen ontology."""
    rows = []
    for group in ("metrics", "derived_metrics"):
        for mid, m in o[group].items():
            al = ", ".join(m.get("aliases", [])[:6])
            ops = ", ".join(m.get("allowed_operations", []))
            formula = f" = {m['formula']}" if "formula" in m else ""
            rows.append(f"- {mid}: {m['display_name']}{formula}" + (f" (also: {al})" if al else "")
                        + (f"; ops: {ops}" if ops else ""))
    return "\n".join(rows)


def _out_of_ontology_lines(o):
    """Taken verbatim from the frozen ontology, not chosen by looking at questions."""
    return "\n".join(f"- {x['name']}: {x['reason']}" for x in o.get("out_of_ontology", []))


@lru_cache(maxsize=1)
def system_prompt():
    o = ontology.load()
    companies = ", ".join(f"{t} ({n})" for t, n in COMPANIES.items())
    return f"""You turn one question about annual 10-K financial data into a plan. You do not answer it.

Return one JSON object, nothing else. Two forms:

1. An answer plan:
   {{"intent": ..., "metric": ..., "companies": [...], "periods": [...]}}
   optional "assumptions": [short strings] for any reading you had to choose.
2. A refusal plan:
   {{"refuse": ..., "reason": "short explanation"}}

Intents:
- fact_lookup: one value of a metric for one company and one fiscal year
- multi_period_lookup: one value per fiscal year, several years, one company
- cross_company_comparison: the same metric for two companies in one fiscal year, including questions that
  ask which of the two is larger or smaller
- absolute_change: change in amount between two fiscal years, one company (periods in time order)
- percent_change: percent change between two fiscal years, one company (periods in time order)
- percentage_point_change: change of a ratio in percentage points between two fiscal years
- ratio: the value of a ratio metric (a metric below whose formula divides one metric by another, such as a
  margin) for one fiscal year. Use the ratio metric's own id, never its numerator or denominator; the
  engine computes the formula.
- restated_value_lookup: a value as originally reported versus as reported now

Metrics (use the id on the left):
{_metric_lines(o)}

Companies (use the ticker): {companies}
Fiscal years covered: {", ".join(YEARS)}. Write periods as "FY2024". A fiscal year is named by the company's
own fiscal calendar. If the question gives only a bare year (e.g. "in 2024"), use the fiscal year with that
number and record the reading in "assumptions".

Not covered by the metric list (the ontology's own out-of-ontology list):
{_out_of_ontology_lines(o)}

Refusal reasons:
- out_of_ontology: the question asks for a metric that is not in the metric list above
- not_reported: only if you know the company does not report this line; otherwise plan the lookup
- unsupported: investment advice, forecasts, or open-ended judgement
- out_of_range: a fiscal year outside {YEARS[0]}-{YEARS[-1]}
- unsupported_operation: the intent is not among the metric's allowed operations (listed as "ops")
"""


def repair_prompt(question, plan_text, errors):
    """Only the question, the invalid plan and the schema errors (decision record)."""
    return (f"Question: {question}\n\nYour plan:\n{plan_text}\n\nIt does not match the plan schema:\n"
            + "\n".join(f"- {e}" for e in errors[:20])
            + "\n\nReturn a corrected plan as one JSON object, nothing else.")


def make_plan(question, log=None, model=None, post=None):
    """{"plan": dict | None, "status": "valid" | "invalid_plan", "attempts": [...], "first_pass_valid": bool}"""
    log = log or llm.CallLog()
    kw = {"post": post} if post else {}
    msgs = [{"role": "system", "content": system_prompt()}, {"role": "user", "content": question}]
    text = llm.chat(msgs, "planner", log, model=model, fmt=schema(), **kw)
    plan = llm.parse_json(text)
    errors = validate(plan) if plan is not None else ["(plan): not a JSON object"]
    attempts = [{"raw": text, "errors": errors}]
    first = not errors
    for _ in range(MAX_REPAIRS):
        if not errors:
            break
        rmsgs = [{"role": "system", "content": system_prompt()},
                 {"role": "user", "content": repair_prompt(question, text, errors)}]
        text = llm.chat(rmsgs, "repair", log, model=model, fmt=schema(), **kw)
        plan = llm.parse_json(text)
        errors = validate(plan) if plan is not None else ["(plan): not a JSON object"]
        attempts.append({"raw": text, "errors": errors})
    return {"plan": plan if not errors else None, "status": "valid" if not errors else "invalid_plan",
            "attempts": attempts, "first_pass_valid": first, "repaired": (not first) and not errors}
