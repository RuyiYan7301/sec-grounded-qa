"""Deterministic calculation and stable evidence ids.

Rules (data/metric_ontology.yaml, operations): percent change needs value(t1) > 0, otherwise
not_meaningful with the absolute change kept; a ratio needs a denominator > 0, otherwise not_meaningful;
a percentage-point change is ratio(t2) - ratio(t1) in points. Two negative values are compared by
magnitude only (direction loss_narrowed / loss_widened), never as a percentage.
"""
import hashlib
import json

LOSS_METRICS = {"gross_profit", "operating_income", "net_income", "eps_basic", "eps_diluted"}


def evidence_id(cell):
    """Stable id from the fact's content, independent of list order or run."""
    key = {k: cell.get(k) for k in ("ticker", "concept", "period_start", "period_end", "accession", "value", "unit")}
    return "ev_" + hashlib.sha256(json.dumps(key, sort_keys=True, default=str).encode()).hexdigest()[:16]


def ratio(num, den):
    if den is None or num is None or den <= 0:
        return {"outcome": "not_meaningful", "reason": "denominator not positive"}
    return {"outcome": "answer", "value": num / den * 100, "unit": "percent"}


def change(v1, v2, metric=None):
    """Absolute change, and percent change only for a positive base; magnitude-only for two negatives."""
    out = {"absolute_change": v2 - v1, "direction": "increase" if v2 > v1 else "decrease" if v2 < v1 else "no_change"}
    if v1 > 0:
        return {**out, "percent_change": (v2 - v1) / v1 * 100, "change_basis": "percent", "outcome": "answer"}
    if v1 < 0 and v2 < 0:
        noun = "loss" if metric in LOSS_METRICS else "negative_value"
        return {**out, "percent_change": None, "change_basis": "magnitude_only",
                "direction": f"{noun}_narrowed" if abs(v2) < abs(v1) else f"{noun}_widened",
                "magnitude_change_pct": abs(v2 - v1) / abs(v1) * 100, "outcome": "not_meaningful"}
    basis = "sign_change" if (v1 < 0) != (v2 < 0) and v1 != 0 and v2 != 0 else "zero_base"
    return {**out, "percent_change": None, "change_basis": basis, "outcome": "not_meaningful",
            "direction": "sign_change" if basis == "sign_change" else out["direction"]}


def pp_change(r1, r2):
    """Two ratio results (percent) -> change in percentage points."""
    if r1.get("outcome") != "answer" or r2.get("outcome") != "answer":
        return {"outcome": "not_meaningful", "reason": "a ratio is not meaningful"}
    d = r2["value"] - r1["value"]
    return {"outcome": "answer", "pp_change": d, "change_basis": "percentage_points",
            "direction": "increase" if d > 0 else "decrease" if d < 0 else "no_change"}
