"""Adversarial and edge items for part A, chosen from the coverage report and the ontology.

Written by Claude (which also builds the system) before any typed-engine code, from the frozen
ontology only. Answerable items get their gold values from gold.py like every other item.
"""
from . import gold

# (kind, question, plan, gold outcome); plan: metric, companies, periods, intent
TEST = [
    # out of ontology
    ("out_of_ontology", "What was Nvidia's EBITDA in fiscal 2025?", None, "out_of_ontology"),
    ("out_of_ontology", "What was Intel's total debt at the end of fiscal 2024?", None, "out_of_ontology"),
    ("out_of_ontology", "How much revenue did Nvidia's Data Center segment generate in fiscal 2025?", None, "out_of_ontology"),
    ("out_of_ontology", "What was Apple's revenue in the fourth quarter of fiscal 2024?", None, "out_of_ontology"),
    ("out_of_ontology", "What was Microsoft's non-GAAP earnings per share in fiscal 2024?", None, "out_of_ontology"),
    ("out_of_ontology", "What was Broadcom's EBIT in fiscal 2024?", None, "out_of_ontology"),
    # not reported by the company
    ("not_reported", "How much goodwill did Apple carry at the end of fiscal 2023?", ("goodwill", ["AAPL"], ["FY2023"]), "not_reported"),
    ("not_reported", "How much goodwill did Apple carry at the end of fiscal 2025?", ("goodwill", ["AAPL"], ["FY2025"]), "not_reported"),
    ("not_reported", "What was Microsoft's selling, general and administrative expense in fiscal 2024?",
     ("selling_general_administrative", ["MSFT"], ["FY2024"]), "not_reported"),
    ("not_reported", "What were Intel's total liabilities at the end of fiscal 2024?", ("total_liabilities", ["INTC"], ["FY2024"]), "not_reported"),
    ("not_reported", "What was Intel's cash and cash equivalents balance at the end of fiscal 2023?",
     ("cash_and_equivalents", ["INTC"], ["FY2023"]), "not_reported"),
    ("not_reported", "What were AMD's total liabilities at the end of fiscal 2025?", ("total_liabilities", ["AMD"], ["FY2025"]), "not_reported"),
    ("not_reported", "What was Broadcom's long-term debt at the end of fiscal 2024?", ("long_term_debt", ["AVGO"], ["FY2024"]), "not_reported"),
    ("not_reported", "What was AMD's long-term debt at the end of fiscal 2024?", ("long_term_debt", ["AMD"], ["FY2024"]), "not_reported"),
    # only a fallback concept: answer with a scope warning
    ("fallback", "What was Broadcom's net income in fiscal 2025?", ("net_income", ["AVGO"], ["FY2025"]), "answer"),
    ("fallback", "What were Nvidia's capital expenditures in fiscal 2024?", ("capital_expenditures", ["NVDA"], ["FY2024"]), "answer"),
    ("fallback", "How much did Nvidia spend on capital expenditures in fiscal 2025?", ("capital_expenditures", ["NVDA"], ["FY2025"]), "answer"),
    ("fallback", "What was Broadcom's total stockholders' equity at the end of fiscal 2024?", ("stockholders_equity", ["AVGO"], ["FY2024"]), "answer"),
    ("fallback", "What was Broadcom's total stockholders' equity at the end of fiscal 2025?", ("stockholders_equity", ["AVGO"], ["FY2025"]), "answer"),
    ("fallback", "What was Nvidia's free cash flow in fiscal 2025?", ("free_cash_flow", ["NVDA"], ["FY2025"]), "answer"),
    # a near-neighbour concept is reported too and must not be used
    ("confounder", "What was Intel's net income attributable to Intel in fiscal 2024?", ("net_income", ["INTC"], ["FY2024"]), "answer"),
    ("confounder", "What was Intel's stockholders' equity attributable to Intel at the end of fiscal 2023?", ("stockholders_equity", ["INTC"], ["FY2023"]), "answer"),
    ("confounder", "What was Intel's total stockholders' equity at the end of fiscal 2025?", ("stockholders_equity", ["INTC"], ["FY2025"]), "answer"),
    ("confounder", "What was Intel's cash and cash equivalents balance at the end of fiscal 2025?",
     ("cash_and_equivalents", ["INTC"], ["FY2025"]), "answer"),
    ("confounder", "What was Nvidia's basic earnings per share in fiscal 2025?", ("eps_basic", ["NVDA"], ["FY2025"]), "answer"),
    ("confounder", "What was AMD's net cash provided by operating activities in fiscal 2025?",
     ("operating_cash_flow", ["AMD"], ["FY2025"]), "answer"),
    # unsupported requests
    ("unsupported", "Is Nvidia a good stock to buy right now?", None, "unsupported"),
    ("unsupported", "What will AMD's revenue be in fiscal 2026?", None, "unsupported"),
    ("unsupported", "Should I sell my Intel shares after its fiscal 2024 results?", None, "unsupported"),
    ("unsupported", "Is Broadcom's management doing a good job, judging by its fiscal 2024 margins?", None, "unsupported"),
    ("unsupported", "Which of these eight companies has the best long-term prospects?", None, "unsupported"),
    ("unsupported", "Predict Apple's diluted EPS for fiscal 2026.", None, "unsupported"),
    # year out of range / bare calendar year
    ("year", "What was Microsoft's net income in fiscal 2021?", None, "out_of_range"),
    ("year", "What was Apple's revenue in fiscal 2026?", None, "out_of_range"),
    ("year", "What was Nvidia's revenue in 2024?", ("revenue", ["NVDA"], ["FY2024"]), "ambiguous_year"),
    ("year", "What was Intel's revenue in 2024?", ("revenue", ["INTC"], ["FY2024"]), "answer"),
    # per-share values compared across companies
    ("cross_company_per_share", "Compare Nvidia's and AMD's diluted EPS for fiscal 2025.", None, "unsupported_operation"),
    ("cross_company_per_share", "Which had higher basic earnings per share in fiscal 2024, Apple or Microsoft?", None, "unsupported_operation"),
    # split-sensitive changes: split-adjusted values from the latest filing
    ("split", "By what percentage did Nvidia's basic EPS change from fiscal 2024 to fiscal 2025?",
     ("eps_basic", ["NVDA"], ["FY2024", "FY2025"]), "answer"),
    ("split", "By what percentage did Broadcom's diluted EPS change from fiscal 2023 to fiscal 2024?",
     ("eps_diluted", ["AVGO"], ["FY2023", "FY2024"]), "answer"),
]

DEV = [
    ("out_of_ontology", "What was Cisco's EBITDA in fiscal 2024?", None, "out_of_ontology"),
    ("not_reported", "What were Cisco's selling, general and administrative expenses in fiscal 2025?",
     ("selling_general_administrative", ["CSCO"], ["FY2025"]), "not_reported"),
    ("not_reported", "What was Oracle's cost of revenue in fiscal 2023?", ("cost_of_revenue", ["ORCL"], ["FY2023"]), "not_reported"),
    ("confounder", "What was Oracle's net income in fiscal 2025?", ("net_income", ["ORCL"], ["FY2025"]), "answer"),
    ("unsupported", "Is Oracle overvalued?", None, "unsupported"),
    ("year", "What was Cisco's revenue in fiscal 2020?", None, "out_of_range"),
]

INTENT = {1: "fact_lookup", 2: "percent_change"}


def components(o, metric):
    if metric in o["metrics"]:
        return [metric]
    a, _, b = o["derived_metrics"][metric]["formula"].split()
    return [metric, a, b]


def items(o, split):
    from .gen_qa import split_of
    out = []
    for n, (kind, question, plan, outcome) in enumerate(TEST if split == "test" else DEV, 1):
        assert not plan or all(split_of(t) == split for t in plan[1]), question
        it = {"id": f"A-{split}-adv-{n:03d}", "layer": "adversarial", "kind": kind, "author": "claude_assisted",
              "question": question, "gold_plan": None, "gold_outcome": outcome, "gold_cells": [],
              "gold_result": {"outcome": outcome}, "required_warnings": [], "advisory_warnings": [],
              "tolerance": None}
        if plan:
            metric, companies, periods = plan
            intent = INTENT[len(periods)]
            it["gold_plan"] = {"intent": intent, "metric": metric, "companies": companies, "periods": periods}
        if outcome in ("answer", "ambiguous_year"):
            from .gen_qa import _evidence, tolerance
            cells = [gold.cell(o, companies[0], metric, int(p[2:])) for p in periods]
            assert all(c["outcome"] == "answer" for c in cells), (question, [c["outcome"] for c in cells])
            it["gold_cells"] = [e for c in cells for e in _evidence(c)]
            if len(cells) == 1:
                it["gold_result"] = {"outcome": outcome, "val": cells[0]["val"]}
            else:
                it["gold_result"] = {**gold.change(cells[0]["val"], cells[1]["val"], intent)}
                if it["gold_result"]["outcome"] == "answer":
                    it["gold_result"] |= {"val": it["gold_result"]["val"] * 100, "unit": "percent"}
                it["gold_result"]["outcome"] = outcome if it["gold_result"]["outcome"] == "answer" else it["gold_result"]["outcome"]
            it["tolerance"] = tolerance(cells[0]["unit"], intent)
            if any(c.get("fallback") for c in cells):
                it["required_warnings"].append("scope")
            if outcome == "ambiguous_year":
                it["required_warnings"].append("ambiguous_year")
        elif outcome == "not_reported":
            c = gold.cell(o, companies[0], metric, int(periods[0][2:]))
            assert c["outcome"] == "not_reported", (question, c["outcome"])
        out.append(it)
    return out
