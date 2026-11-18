"""v0.4 generalization test, part 2a: the accuracy samples and their review packets (docs/v0.4-plan.md).

    python -m secqa.evaluation.v4.sample_cells sample    # draw the samples -> results/v0.4/accuracy/sample.json
    python -m secqa.evaluation.v4.sample_cells packets   # fetch the 10-Ks, write review packets

Samples (new companies only, FY2019-FY2025, from results/v0.4/coverage/cells.jsonl):
  answer cells (resolved or fallback_with_warning): 150, random.Random(2604), at least 5 per metric and the
  rest in proportion to each metric's answer cells (largest remainder);
  not_reported cells: 50, random.Random(2605), simple random sample.
The sample file is written and committed before any packet is read.

Packets carry what a reader needs and nothing about how the engine chose: the metric's definition from the
frozen ontology (name, statement, aliases, what it is not), the value in the usual printed forms, and the
10-K lines around each place the value is printed. Concept tags are kept out of the packet (they are in a
separate key file used only to tally results).
"""
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date

from ... import config, edgar, facts, filings, ontology, universe
from ..v2.verify_gold_text import find, forms
from .coverage import _pages

ROOT = config.REPO_ROOT / "results" / "v0.4"
CELLS = ROOT / "coverage" / "cells.jsonl"
OUT = ROOT / "accuracy"
N_ANSWER, MIN_PER_METRIC, SEED_ANSWER = 150, 5, 2604
N_NOT_REPORTED, SEED_NR = 50, 2605
ANSWER = ("resolved", "fallback_with_warning")


def _cells():
    return [json.loads(x) for x in CELLS.read_text(encoding="utf-8").splitlines() if x.strip()]


def _key(c):
    return (c["ticker"], c["metric"], c["fy"])


def sample():
    cells = sorted((c for c in _cells() if not c["original"]), key=_key)
    by_metric = defaultdict(list)
    for c in cells:
        if c["status"] in ANSWER:
            by_metric[c["metric"]].append(c)
    metrics = sorted(by_metric)
    total = sum(len(v) for v in by_metric.values())
    rest = N_ANSWER - MIN_PER_METRIC * len(metrics)
    exact = {m: rest * len(by_metric[m]) / total for m in metrics}
    quota = {m: MIN_PER_METRIC + int(exact[m]) for m in metrics}
    for m in sorted(metrics, key=lambda m: (-(exact[m] - int(exact[m])), m))[:N_ANSWER - sum(quota.values())]:
        quota[m] += 1
    rng = random.Random(SEED_ANSWER)
    answer = [c for m in metrics for c in rng.sample(by_metric[m], quota[m])]
    nr_pool = [c for c in cells if c["status"] == "not_reported"]
    not_reported = random.Random(SEED_NR).sample(nr_pool, N_NOT_REPORTED)
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for i, c in enumerate(answer, 1):
        items.append({"id": f"A{i:03d}", "kind": "answer", **c})
    for i, c in enumerate(not_reported, 1):
        items.append({"id": f"N{i:03d}", "kind": "not_reported", **c})
    doc = {"plan": "docs/v0.4-plan.md section 2a", "seeds": {"answer": SEED_ANSWER, "not_reported": SEED_NR},
           "quota": quota, "pool": {"answer": total, "not_reported": len(nr_pool)}, "items": items}
    (OUT / "sample.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"{len(answer)} answer cells, {len(not_reported)} not_reported cells; quota {quota}")


# ---------------------------------------------------------------- packets

def _docs(ticker):
    """accession -> (primary document, report date, form) over every submissions page."""
    out = {}
    for r in _pages(ticker):
        for i, a in enumerate(r["accessionNumber"]):
            out[a] = (r["primaryDocument"][i], r["reportDate"][i], r["form"][i])
    return out


def _text(ticker, accn, doc):
    path = filings.text_dir() / "v04" / f"{ticker}_{accn}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    cik = edgar.FILERS[ticker]
    html = edgar.get_text(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace('-', '')}/{doc}")
    text = filings.html_to_text(html)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def _definition(onto, mid):
    m = onto["metrics"][mid]
    lines = [f"Metric: {m['display_name']} ({m['statement'].replace('_', ' ')}, "
             f"{'for the fiscal year' if m['period_type'] == 'duration' else 'at fiscal year end'})",
             f"Also called: {', '.join(m.get('aliases', []))}"]
    for c in m.get("confounders", []):
        lines.append(f"Not the same as: {c['tag']} ({c.get('reason', '')})")
    if m.get("consolidated_required"):
        lines.append("Must be the consolidated total for the whole company.")
    return "\n".join(lines)


def _context(lines, idx, before=4, after=2):
    lo, hi = max(0, idx - before), min(len(lines), idx + after + 1)
    return "\n".join(("> " if i == idx else "  ") + lines[i][:220] for i in range(lo, hi))


KEYWORDS = {
    "revenue": ["revenue", "net sales", "total sales"], "cost_of_revenue": ["cost of", "costs of"],
    "gross_profit": ["gross"], "research_and_development": ["research", "development"],
    "selling_general_administrative": ["selling", "administrative"],
    "operating_expenses": ["operating expenses", "costs and expenses", "total expenses"],
    "operating_income": ["operating income", "income from operations", "operating profit", "operating loss"],
    "net_income": ["net income", "net earnings", "net loss"], "inventory": ["inventor"],
    "long_term_debt": ["long-term debt", "long term debt", "borrowings", "notes"],
    "total_liabilities": ["total liabilities"], "cash_and_equivalents": ["cash and cash equivalents", "cash and equivalents"],
    "goodwill": ["goodwill"], "capital_expenditures": ["property", "capital expenditure", "purchases of"],
    "share_based_compensation": ["stock-based", "share-based", "stock based", "equity-based"],
    "weighted_shares_diluted": ["diluted"], "weighted_shares_basic": ["basic"], "eps_basic": ["basic"],
    "eps_diluted": ["diluted"],
}


def packets():
    onto = ontology.load()
    filers = universe.filers()
    edgar.FILERS.update({t: c for t, c in filers.items() if t not in edgar.FILERS})
    edgar.ALLOW_FETCH = True
    labels = json.loads((ROOT / "coverage" / "labels.json").read_text(encoding="utf-8"))
    items = json.loads((OUT / "sample.json").read_text(encoding="utf-8"))["items"]
    docs_cache, packs, keys = {}, [], {}
    for it in items:
        t = it["ticker"]
        docs = docs_cache.setdefault(t, _docs(t))
        if it["kind"] == "answer":
            accn = it["accession"]
        else:  # the 10-K for that fiscal year (engine label)
            accn = next(k["accession"] for k in labels[t]["tenks"] if k["engine_fy"] == it["fy"])
        doc, report_date, form = docs[accn]
        text = _text(t, accn, doc)
        lines = text.split("\n")
        name = edgar.submissions(t)["name"]
        head = [f"## {it['id']}", f"Company: {name} ({t})",
                f"Fiscal year: the fiscal year ending {it.get('period_end') or report_date}",
                f"Filing read: {form} {accn}, period of report {report_date}",
                f"Full 10-K text (search it): {(filings.text_dir() / 'v04' / f'{t}_{accn}.txt').as_posix()}",
                _definition(onto, it["metric"])]
        if it["kind"] == "answer":
            v, unit = it["value"], it["unit"]
            shown = sorted(forms(v, unit))
            head.append(f"Value the system reports: {v:,} {unit}"
                        + (f" (printed forms searched: {', '.join(shown)})" if shown else ""))
            hits = []
            for s in shown:
                for pos in find(text, s):
                    hits.append(text.count("\n", 0, pos))
            hits = sorted(set(hits))[:4]
            head.append(f"Lines where the value is printed ({len(hits)} shown):" if hits else
                        "The value was not found printed in this filing's text (it may be a sum, or in a table "
                        "the text conversion split). Lines with the metric's words are shown instead.")
        else:
            head.append("The system says this item is NOT REPORTED in this 10-K for this fiscal year. "
                        "Lines with the metric's words are shown.")
            hits = []
        if not hits:
            words = KEYWORDS.get(it["metric"], [onto["metrics"][it["metric"]]["display_name"].lower()])
            cand = [i for i, ln in enumerate(lines) if any(w in ln.lower() for w in words) and re.search(r"\d", ln)]
            hits = cand[:10]
        body = "\n\n".join(_context(lines, i) for i in hits)
        packs.append("\n".join(head) + "\n\n```\n" + body + "\n```\n")
        keys[it["id"]] = {k: it.get(k) for k in ("ticker", "metric", "fy", "status", "concept", "use", "value",
                                                  "unit", "accession")}
        print(it["id"], t, it["metric"], it["fy"], len(hits), flush=True)
    rng = random.Random(2604)
    order = list(range(len(packs)))
    rng.shuffle(order)                              # mix answer and not_reported cells across reviewers
    n = 4
    for b in range(n):
        part = [packs[i] for i in order[b::n]]
        (OUT / f"packet_{b + 1}.md").write_text("\n".join(part), encoding="utf-8")
    (OUT / "key.json").write_text(json.dumps(keys, indent=1), encoding="utf-8")


if __name__ == "__main__":
    {"sample": sample, "packets": packets}[sys.argv[1]]()
