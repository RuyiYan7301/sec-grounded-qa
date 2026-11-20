"""Deterministic execution of a validated plan -> structured result (no model call).

Output: outcome, resolved cells, result, evidence items with stable ids, and warnings as semantic codes
with a plain description. This is the renderer's input; nothing here is phrased for a scorer.
"""
import re

from . import compute, periods, resolve, scope_checks

INTENT_OP = {"fact_lookup": "lookup", "restated_value_lookup": "lookup", "multi_period_lookup": "multi_period_lookup",
             "cross_company_comparison": "cross_company_comparison", "absolute_change": "absolute_change",
             "percent_change": "percent_change", "percentage_point_change": "percentage_point_change",
             "ratio": "ratio"}


def _metric(ontology, mid):
    return ontology["metrics"].get(mid) or ontology["derived_metrics"].get(mid)


def _warn(code, detail, **extra):
    return {"code": code, "detail": detail, **extra}


def resolve_value(source, ontology, ticker, mid, fy):
    """A base or derived value -> {"status", "value", "cells", "warnings"}."""
    if mid in ontology["metrics"]:
        r = resolve.resolve(source, ontology, ticker, mid, fy)
        if r["status"] == "not_reported" and mid == "long_term_debt":      # v0.4 2c fix 5
            d = scope_checks.derived_debt(source, ontology, ticker, fy)
            if d:
                return {**d, "resolution": [r]}
        if r["status"] in ("not_reported", "ambiguous_concept"):
            return {"status": r["status"], "value": None, "cells": [], "warnings": [], "resolution": [r]}
        w = [_warn("scope", f"{mid} resolved through the fallback concept {r['cell']['concept']}",
                   concept=r["cell"]["concept"])] if r["status"] == "fallback_with_warning" else []
        w += scope_checks.warnings(source, ontology, ticker, mid, fy, r["cell"])   # v0.4 2c fixes 3-4
        return {"status": r["status"], "value": r["cell"]["value"], "cells": [r["cell"]], "warnings": w, "resolution": [r]}
    d = ontology["derived_metrics"][mid]
    a, op, b = d["formula"].split()
    ra, rb = (resolve_value(source, ontology, ticker, x, fy) for x in (a, b))
    for r in (ra, rb):
        if r["status"] in ("not_reported", "ambiguous_concept"):
            return {**r, "cells": ra["cells"] + rb["cells"]}
    cells = [{**c, "component_of": mid} for c in ra["cells"] + rb["cells"]]
    w = ra["warnings"] + rb["warnings"]
    if op == "/":
        q = compute.ratio(ra["value"], rb["value"])
        return {"status": "resolved" if q["outcome"] == "answer" else "not_meaningful",
                "value": q.get("value"), "cells": cells, "warnings": w, "unit": "percent"}
    return {"status": "resolved", "value": ra["value"] - rb["value"], "cells": cells, "warnings": w}


def interpreted_alias(question, metric):
    for a in metric.get("interpreted_aliases", []):
        if re.search(r"\b" + re.escape(a["alias"]) + r"\b", question or "") and not re.search(
                r"\b(?:diluted|basic)\b", question or "", re.I):
            return _warn("alias_interpretation", a["warning"], alias=a["alias"])
    return None


def execute(plan, question, source, ontology):
    if "refuse" in plan:
        return {"outcome": plan["refuse"], "reason": plan.get("reason"), "cells": [], "evidence": [], "warnings": []}
    intent, mid, comps, pers = plan["intent"], plan["metric"], plan["companies"], plan["periods"]
    m = _metric(ontology, mid)
    if m is None:
        return {"outcome": "out_of_ontology", "reason": f"{mid} is not in the ontology", "cells": [], "evidence": [], "warnings": []}
    if periods.out_of_range(pers):
        return {"outcome": "out_of_range", "reason": f"covered fiscal years are FY{periods.COVERED[0]}-FY{periods.COVERED[-1]}",
                "cells": [], "evidence": [], "warnings": []}
    # In the ontology, computing a ratio metric (gross margin, ...) is a lookup of that derived metric; the
    # "ratio" operation on a base metric means it may serve as a ratio component.
    op = "lookup" if intent == "ratio" and m.get("unit_type") == "ratio" else INTENT_OP[intent]
    if op not in m.get("allowed_operations", []):
        return {"outcome": "unsupported_operation", "reason": f"{intent} is not allowed for {mid}",
                "cells": [], "evidence": [], "warnings": []}
    warnings = []
    if "formula" in m:   # the ontology: the formula of a derived metric is shown in every answer
        warnings.append(_warn("derived_metric_definition", f"{m['display_name']} = {m['formula']}"
                              + (f"; {m['review']['notes']}" if m.get("review", {}).get("notes") else ""),
                              informational=True))
    for w in (interpreted_alias(question, m), periods.bare_year_reading(question, comps)):
        if w:
            warnings.append(w)
    values = {}
    for t in comps:
        for p in pers:
            values[(t, p)] = resolve_value(source, ontology, t, mid, int(p[2:]))
    cells = [c for v in values.values() for c in v["cells"]]
    for v in values.values():
        warnings += [w for w in v["warnings"] if w not in warnings]
    bad = [v for v in values.values() if v["status"] in ("not_reported", "ambiguous_concept")]
    base = {"intent": intent, "metric": mid, "companies": comps, "periods": pers, "cells": cells,
            "evidence": [{"id": compute.evidence_id(c), **c} for c in cells], "warnings": warnings}
    if bad:
        return {**base, "outcome": bad[0]["status"]}
    vals = [values[(t, p)]["value"] for t in comps for p in pers]
    if any(v["status"] == "not_meaningful" for v in values.values()):
        return {**base, "outcome": "not_meaningful", "result": {"reason": "a ratio denominator is not positive"}}
    if any(c.get("other_values") for c in cells):
        warnings.append(_warn("restated", "a value used was reported differently in an earlier filing",
                              revisions=[{"concept": c["concept"], "fy": c["fy"], "current": c["value"],
                                          "earlier": c["other_values"]} for c in cells if c.get("other_values")]))
    if m.get("split_sensitive") and source.policy == "latest_in_snapshot":
        latest = max(cells, key=lambda c: c["filed"])
        warnings.append(_warn("split_adjusted", "per-share and share-count values are on the share basis of the "
                              "latest filing that presents them (split-adjusted)", basis_accession=latest["accession"]))
    # the unit of the values in the result: a ratio metric is in percent, a base metric in its cells' unit
    unit = "percent" if intent == "ratio" or m.get("unit_type") == "ratio" else cells[0]["unit"]
    if intent == "cross_company_comparison":
        al = periods.alignment([values[(t, pers[0])]["cells"][0] if values[(t, pers[0])]["cells"] else None for t in comps])
        warnings += al["warnings"]
        return {**base, "outcome": "answer", "alignment": al,
                "result": {"values": dict(zip(comps, vals)), "difference": vals[0] - vals[1], "unit": unit}}
    if intent in ("fact_lookup", "ratio"):
        return {**base, "outcome": "answer", "result": {"value": vals[0], "unit": unit}}
    if intent == "multi_period_lookup":
        return {**base, "outcome": "answer", "result": {"values": dict(zip(pers, vals)), "unit": unit}}
    if intent == "restated_value_lookup":
        c = cells[0]
        earlier = sorted(c.get("other_values") or [], key=lambda x: x["filed"])
        orig = earlier[0] if earlier else None
        if orig:
            warnings.append(_warn("restated", "the value now reported differs from the value first reported"))
        return {**base, "outcome": "answer",
                "result": {"unit": unit, "current": c["value"], "current_accession": c["accession"],
                           "original": orig["val"] if orig else c["value"],
                           "original_accession": orig["accn"] if orig else c.get("first_accession"),
                           "revised": bool(orig)}}
    if intent == "percentage_point_change":
        r = compute.pp_change({"outcome": "answer", "value": vals[0]}, {"outcome": "answer", "value": vals[1]})
        return {**base, "outcome": r["outcome"], "result": r}
    ch = {**compute.change(vals[0], vals[1], mid), "unit": unit}
    if intent == "absolute_change":
        return {**base, "outcome": "answer", "result": {**ch, "outcome": "answer"}}
    return {**base, "outcome": ch["outcome"], "result": ch}       # percent_change
