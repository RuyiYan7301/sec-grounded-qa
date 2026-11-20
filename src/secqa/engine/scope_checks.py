"""v0.4 2c fixes 3-5 (docs/v0.4-2c-plan.md): scope warnings and one derived value, outside the frozen ontology.

3. opex_is_total_costs: a resolved operating_expenses value within 0.5% of revenue minus operating income is
   the filer's total operating costs (cost of sales included when the filer has any: GM, CAT), so it is not
   comparable with filers whose operating expenses exclude cost of sales. Amended from the plan's
   `opex_includes_cost_of_sales` (which also required a tagged cost-of-revenue concept) after a sweep of all
   85 filers, before any fresh sample: GM tags no us-gaap cost line, so the plan's rule missed it, and UNP and
   BKNG have no cost of sales, so that wording would be wrong for them.
4. cost_of_revenue_partial: a cost_of_revenue resolved through CostOfGoodsAndServicesSold that is below 50% of
   revenue minus operating income, for a filer that tags a larger benefit or service cost line (UNH: products
   only, medical costs are separate).
5. derived_sum: long_term_debt with no total concept but both LongTermDebtNoncurrent and LongTermDebtCurrent at
   the same balance date is reported as their sum, with a note naming both facts.

Values are never changed by 3 and 4: the tag is the filer's own; the answer carries the warning.
"""
from . import resolve

OPEX_TOL = 0.005
PARTIAL_COST = 0.5
LARGER_COST_TAGS = ("PolicyholderBenefitsAndClaimsIncurredNet", "PolicyholderBenefitsAndClaimsIncurredHealthCare",
                    "BenefitsLossesAndExpenses", "CostOfServices")
DEBT_PARTS = ("LongTermDebtNoncurrent", "LongTermDebtCurrent")


def _base(source, ontology, ticker, mid, fy):
    """Every reported candidate value of a base metric (ambiguous candidates included)."""
    m = ontology["metrics"][mid]
    return [x["value"] for c in resolve.candidates(m)
            if (x := source.cell(ticker, mid, m, fy, c["tag"])) is not None]


def _total_costs(source, ontology, ticker, fy):
    """Revenue minus operating income, for each reported revenue candidate; [] when either is missing."""
    oi = _base(source, ontology, ticker, "operating_income", fy)
    return [rev - oi[0] for rev in _base(source, ontology, ticker, "revenue", fy)] if oi else []


def warnings(source, ontology, ticker, mid, fy, cell):
    if mid == "operating_expenses":
        if any(t > 0 and abs(cell["value"] - t) <= OPEX_TOL * t
               for t in _total_costs(source, ontology, ticker, fy)):
            return [{"code": "opex_is_total_costs",
                     "detail": "this operating expenses line equals revenue minus operating income: it is the filer's "
                               "total operating costs, including cost of sales if the filer has any, and is not "
                               "comparable with operating expenses that exclude cost of sales"}]
    if mid == "cost_of_revenue" and cell["concept"] == "CostOfGoodsAndServicesSold":
        m = ontology["metrics"][mid]
        larger = [t for t in LARGER_COST_TAGS
                  if (x := source.cell(ticker, mid, m, fy, t)) is not None and x["value"] > cell["value"]]
        if larger and any(t > 0 and cell["value"] < PARTIAL_COST * t for t in _total_costs(source, ontology, ticker, fy)):
            return [{"code": "cost_of_revenue_partial",
                     "detail": f"{cell['concept']} covers part of the filer's costs; {larger[0]} is tagged separately "
                               "and is larger", "concept": larger[0]}]
    return []


def derived_debt(source, ontology, ticker, fy):
    """long_term_debt from its two parts, or None."""
    m = ontology["metrics"]["long_term_debt"]
    parts = [source.cell(ticker, "long_term_debt", m, fy, t) for t in DEBT_PARTS]
    if any(p is None for p in parts) or len({(p["period_end"], p["unit"]) for p in parts}) > 1:
        return None
    cells = [{**p, "use": "derived_part", "component_of": "long_term_debt"} for p in parts]
    return {"status": "derived_sum", "value": sum(p["value"] for p in parts), "cells": cells,
            "warnings": [{"code": "derived_sum", "detail": f"no total long-term debt is tagged; reported as "
                          f"{DEBT_PARTS[0]} + {DEBT_PARTS[1]} at {parts[0]['period_end']}",
                          "concepts": list(DEBT_PARTS)}]}
