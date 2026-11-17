"""Change packet for one target 10-K: `secqa diff TICKER --from FYxxxx --to FYyyyy`.

Numeric items: every ontology metric for the two fiscal years, values from FilingFactIndex (exact target
accession, as_of_filing), size labels by the pre-registered thresholds of the system spec (10% / 2 pp large,
2% / 0.5 pp control). Revision checks: every base metric's prior-year value as presented in the target
filing against the first 10-K that reported it. Item 1A: engine.item1a_changes. Output follows the frozen
packet schema. During development only the CSCO dev case is run (decision record).
"""
import json

from .. import ontology
from . import compute, execute, item1a_changes, resolve

SCHEMA_VERSION = "packet-0.2-draft3"
AMOUNT = (10.0, 2.0)       # large, control: percent
RATIO = (2.0, 0.5)         # large, control: percentage points


def size_status(kind, v1, v2):
    if kind == "ratio":
        d = abs(v2 - v1)
        return "large_numeric_change" if d >= RATIO[0] else "unchanged_control" if d < RATIO[1] else "gray_zone"
    if v1 > 0:
        p = abs(v2 - v1) / v1 * 100
    elif v1 < 0 and v2 < 0:
        p = abs(v2 - v1) / abs(v1) * 100
    elif v1 == 0:
        return "unchanged_control" if v2 == 0 else "large_numeric_change"
    else:
        return "large_numeric_change"
    return "large_numeric_change" if p >= AMOUNT[0] else "unchanged_control" if p < AMOUNT[1] else "gray_zone"


def fact(cell, role, ticker):
    return {"ticker": ticker, "metric": cell["metric"], "component_of": cell.get("component_of"), "fy": cell["fy"],
            "role": role, "value": cell["value"], "unit": cell["unit"], "concept": cell["concept"],
            "period_start": cell.get("period_start"), "period_end": cell["period_end"],
            "accession": cell["accession"], "filed": cell["filed"]}


def numeric_item(case, o, idx, ticker, mid, y1, y2):
    m = o["metrics"].get(mid) or o["derived_metrics"][mid]
    kind = "ratio" if m.get("unit_type") == "ratio" else "amount"
    r1, r2 = (execute.resolve_value(idx, o, ticker, mid, y) for y in (y1, y2))
    item = {"id": f"{case}:{mid}:numeric_change", "metric": mid, "warnings": []}
    for r in (r1, r2):
        if r["status"] in ("not_reported", "ambiguous_concept"):
            return {**item, "status": "abstain", "abstain_reason": r["status"], "facts": [], "absolute_change": None,
                    "percent_change": None, "pp_change": None, "change_basis": None, "direction": None}
    facts = [fact(c, "comparative_year", ticker) for c in r1["cells"]] + [fact(c, "current_year", ticker) for c in r2["cells"]]
    warn = []
    if any(w["code"] == "scope" for w in r1["warnings"] + r2["warnings"]):
        warn.append("scope")
    if any(c.get("first_reported") and c["first_reported"]["value"] != c["value"] for c in r1["cells"] + r2["cells"]):
        warn.append("superseded_value")
    concepts1 = sorted(c["concept"] for c in r1["cells"])
    concepts2 = sorted(c["concept"] for c in r2["cells"])
    if concepts1 != concepts2:
        return {**item, "status": "concept_change", "abstain_reason": None, "facts": facts,
                "warnings": sorted(set(warn + ["concept_change"])), "absolute_change": None, "percent_change": None,
                "pp_change": None, "change_basis": None, "direction": None}
    if r1["status"] == "not_meaningful" or r2["status"] == "not_meaningful":
        return {**item, "status": "abstain", "abstain_reason": "ambiguous_concept", "facts": [], "absolute_change": None,
                "percent_change": None, "pp_change": None, "change_basis": None, "direction": None}
    v1, v2 = r1["value"], r2["value"]
    status = size_status(kind, v1, v2)          # ratio values are in percent, so differences are in points
    if kind == "ratio":
        pp = compute.pp_change({"outcome": "answer", "value": v1}, {"outcome": "answer", "value": v2})
        return {**item, "status": status, "abstain_reason": None, "facts": facts, "warnings": warn,
                "absolute_change": None, "percent_change": None, "pp_change": pp["pp_change"],
                "change_basis": "percentage_points", "direction": pp["direction"]}
    ch = compute.change(v1, v2, mid)
    return {**item, "status": status, "abstain_reason": None, "facts": facts, "warnings": warn,
            "absolute_change": ch["absolute_change"], "percent_change": ch["percent_change"], "pp_change": None,
            "change_basis": ch["change_basis"], "direction": ch["direction"]}


def revision_check(case, o, idx, ticker, mid, y1):
    m = o["metrics"][mid]
    r = resolve.resolve(idx, o, ticker, mid, y1)
    if r["status"] not in ("resolved", "fallback_with_warning"):
        return None
    c = r["cell"]
    ap = fact(c, "prior_year_as_presented", ticker)
    fr = c.get("first_reported")
    if not fr or fr["accession"] == c["accession"]:
        status, frf, cause = "no_prior_observation", None, None
    else:
        frf = {**ap, "role": "first_reported", "value": fr["value"], "accession": fr["accession"], "filed": fr["filed"]}
        if fr["value"] == c["value"]:
            status, cause = "stable", None
        else:
            status, cause = "revised", ("stock_split_recast" if m.get("split_sensitive") else "accounting_recast")
    return {"id": f"{case}:{mid}:FY{y1}:revision_control", "metric": mid, "period": f"FY{y1}", "as_presented": ap,
            "first_reported": frf, "status": status, "cause": cause}


def build_packet(ticker, y1, y2, item1a=True, log=None, item1a_method="v0.3"):
    o = ontology.load()
    case = f"{ticker}_FY{y2}"
    idx = resolve.FilingFactIndex(ticker, y2)
    p = {"schema_version": SCHEMA_VERSION, "case": case, "system": "v0.2", "ticker": ticker,
         "from_fy": f"FY{y1}", "to_fy": f"FY{y2}", "value_policy": "as_of_filing",
         "target_filing": {"accession": idx.target_accession, "filed": idx.target_filed},
         "numeric_changes": [numeric_item(case, o, idx, ticker, mid, y1, y2)
                             for mid in list(o["metrics"]) + list(o["derived_metrics"])],
         "revision_checks": [x for x in (revision_check(case, o, idx, ticker, mid, y1) for mid in o["metrics"]) if x],
         "item1a_changes": []}
    detail = None
    if item1a:
        if item1a_method == "v0.3":     # frozen at tag v0.3-item1a-freeze (word diff, small edits skip the model)
            from . import item1a_v03
            detail = item1a_v03.detect(ticker, y1, y2, "diff_small", log=log)
        else:
            detail = item1a_changes.detect(ticker, y1, y2, log=log)
        detail["item1a_method"] = item1a_method   # the packet schema is frozen; the method is recorded here
        p["item1a_changes"] = detail["item1a_changes"]
    return p, detail


def main(args):
    y1, y2 = int(args.from_fy[2:]), int(args.to_fy[2:])
    p, detail = build_packet(args.ticker.upper(), y1, y2, item1a=not args.no_item1a,
                             item1a_method=getattr(args, "item1a_method", "v0.3"))
    text = json.dumps(p, indent=1)
    if args.out:
        open(args.out, "w", encoding="utf-8", newline="\n").write(text + "\n")
        if detail is not None:
            open(args.out.replace(".json", ".item1a_candidates.json"), "w", encoding="utf-8", newline="\n").write(
                json.dumps(detail, indent=1) + "\n")
    else:
        print(text)
    return 0
