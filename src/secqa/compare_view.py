"""Display rows for a two-10-K comparison, built from the v0.2 change packet (engine/diff.py).

Shared by the web front end (secqa web) and the Gradio demo (secqa app). Nothing here changes a value: figures,
changes and statuses come from the packet; this module only picks the year values, formats them and adds links.
"""
import difflib
import json
import re

from . import config, edgar, guards, ontology

SIZE = {"large_numeric_change": "large", "gray_zone": "moderate", "unchanged_control": "small"}
STATEMENTS = {"income_statement": "Income statement", "balance_sheet": "Balance sheet", "cash_flow": "Cash flow",
              None: "Ratios and derived"}
LABEL_1A = {"material_added": "added", "material_removed": "removed", "material_modified": "modified"}


def fmt(v, unit):
    if v is None:
        return "—"
    if unit == "percent":
        return f"{v:.1f}%"
    if unit == "shares":
        a = abs(v)
        return f"{v / 1e9:,.3f} billion shares" if a >= 1e9 else f"{v / 1e6:,.0f} million shares"
    from .tools import display
    return display(v, unit).split(" (=")[0]


def metric_value(item, fy, o):
    """The metric's value for one year from the packet's facts (derived metrics from their components)."""
    facts = [f for f in item["facts"] if f["fy"] == fy]
    if not facts:
        return None, None
    d = o["derived_metrics"].get(item["metric"])
    if not d:
        f = next((f for f in facts if not f.get("component_of")), facts[0])
        return f["value"], f["unit"]
    a, op, b = d["formula"].split()
    val = {f["metric"]: f["value"] for f in facts}
    if a not in val or b not in val:
        return None, None
    if op == "/":
        return (100 * val[a] / val[b] if val[b] else None), "percent"
    return val[a] - val[b], "USD"


def change_text(item, unit):
    if item.get("pp_change") is not None:
        return f"{item['pp_change']:+.1f} pp"
    if item.get("absolute_change") is None:
        return item.get("abstain_reason") or "—"
    s = fmt(item["absolute_change"], unit)
    s = s if s.startswith("-") else "+" + s
    return s + (f" ({item['percent_change']:+.1f}%)" if item.get("percent_change") is not None else "")


def name(mid, o):
    m = o["metrics"].get(mid) or o["derived_metrics"].get(mid) or {}
    return m.get("display_name") or mid.replace("_", " ").capitalize()


def word_diff(earlier, later):
    """Word-level segments [{op: same|added|removed, text}] between two paragraphs."""
    a, b = re.findall(r"\S+\s*", earlier or ""), re.findall(r"\S+\s*", later or "")
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append({"op": "same", "text": "".join(a[i1:i2])})
            continue
        if i2 > i1:
            out.append({"op": "removed", "text": "".join(a[i1:i2])})
        if j2 > j1:
            out.append({"op": "added", "text": "".join(b[j1:j2])})
    return out


def _ref(f):
    return {"fy": f["fy"], "concept": f["concept"], "value": f["value"], "unit": f["unit"], "accession": f["accession"],
            "filed": f.get("filed"), "url": edgar.filing_url(f["ticker"], f["accession"]), "component_of": f.get("component_of"),
            "metric": f["metric"]}


def _item1a_cache(ticker, y2):
    name = f"item1a_v03_{ticker}_FY{y2}.json"
    local = config.DATA_DIR / "ui_cache" / name
    shipped = config.DEMO_DIR / "item1a" / name          # committed copy, used when there is no local run
    return local if local.exists() or not shipped.exists() else shipped


def _with_text(detail, ticker, y1, y2):
    """The v0.3 detector records paragraph indices only; add the paragraph text from the two filings (when the
    10-K text is available), so a cached result can be shown, and shipped, without the filings."""
    cands = detail.get("candidates", [])
    if all("earlier" in c and "later" in c for c in cands):
        return detail, False
    try:
        from .evaluation.v2 import item1a as protocol
        a = protocol.paragraphs(protocol.item1a_text(ticker, y1))
        b = protocol.paragraphs(protocol.item1a_text(ticker, y2))
    except (FileNotFoundError, ImportError):
        return detail, False
    at = lambda paras, i: paras[i] if isinstance(i, int) and 0 <= i < len(paras) else None  # noqa: E731
    for c in cands:
        c["earlier"], c["later"] = at(a, c.get("earlier_index")), at(b, c.get("later_index"))
    return detail, True


def item1a_detail(ticker, y1, y2, run=False):
    """Item 1A candidates (v0.3 classifier), cached on disk after the first run; None if not run yet and run=False."""
    path = _item1a_cache(ticker, y2)
    if path.exists():
        detail, added = _with_text(json.loads(path.read_text(encoding="utf-8")), ticker, y1, y2)
        if added and path.parent.name == "ui_cache":
            path.write_text(json.dumps(detail), encoding="utf-8")
        return detail
    if not run:
        return None
    from .engine import item1a_v03
    detail, _ = _with_text(item1a_v03.detect(ticker, y1, y2, "diff_small"), ticker, y1, y2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(detail), encoding="utf-8")
    return detail


def build(ticker, to_fy, item1a="cached"):
    """item1a: 'cached' (use a saved run if there is one), 'run' (run the model if needed), or 'off'."""
    from .engine import diff
    o = ontology.load()
    y2 = int(str(to_fy).upper().removeprefix("FY"))
    y1 = y2 - 1
    p, _ = diff.build_packet(ticker, y1, y2, item1a=False)
    f1, f2 = f"FY{y1}", f"FY{y2}"
    order = list(SIZE)
    metrics = []
    for it in p["numeric_changes"]:
        v1, u1 = metric_value(it, f1, o)
        v2, u2 = metric_value(it, f2, o)
        u = u1 or u2
        m = o["metrics"].get(it["metric"]) or {}
        metrics.append({
            "id": it["metric"], "name": name(it["metric"], o), "statement": STATEMENTS.get(m.get("statement")),
            "unit": u, "v1": v1, "v2": v2, "v1_display": fmt(v1, u), "v2_display": fmt(v2, u),
            "change_display": change_text(it, u), "absolute_change": it.get("absolute_change"),
            "percent_change": it.get("percent_change"), "pp_change": it.get("pp_change"),
            "direction": it.get("direction"), "size": SIZE.get(it["status"], it["status"]),
            "rank": order.index(it["status"]) if it["status"] in order else 9,
            "warnings": [w if isinstance(w, str) else w.get("code") for w in it.get("warnings", [])], "abstain_reason": it.get("abstain_reason"),
            "facts": [_ref(f) for f in it["facts"]]})
    revisions = []
    for r in p["revision_checks"]:
        first, now = r.get("first_reported") or {}, r.get("as_presented") or {}
        u = first.get("unit") or now.get("unit")
        revisions.append({
            "metric": r["metric"], "name": name(r["metric"], o), "period": r["period"], "status": r["status"],
            "cause": (r.get("cause") or "").replace("_", " ") or None,
            "first": {"display": fmt(first.get("value"), u), **(_ref(first) if first else {})} if first else None,
            "now": {"display": fmt(now.get("value"), u), **(_ref(now) if now else {})} if now else None})
    revisions.sort(key=lambda r: r["status"] != "revised")
    detail = None if item1a == "off" else item1a_detail(ticker, y1, y2, run=item1a == "run")
    paras = None
    if detail is not None:
        paras = []
        for c in detail.get("candidates", []):
            lab = LABEL_1A.get(str(c.get("label")))
            if not lab:
                continue
            paras.append({"label": lab, "reason": c.get("reason") or "", "earlier": c.get("earlier"), "later": c.get("later"),
                          "earlier_index": c.get("earlier_index"), "later_index": c.get("later_index"),
                          "diff": word_diff(c["earlier"], c["later"]) if lab == "modified" and c.get("earlier") and c.get("later") else None})
    tf = p["target_filing"]
    return {
        "ticker": ticker, "company": guards.NAMES.get(ticker, ticker), "from_fy": f1, "to_fy": f2,
        "target_filing": {"accession": tf["accession"], "filed": tf["filed"], "url": edgar.filing_url(ticker, tf["accession"])},
        "summary": {"large": sum(m["size"] == "large" for m in metrics),
                    "revised": sum(r["status"] == "revised" for r in revisions),
                    "item1a": None if paras is None else len(paras)},
        "metrics": metrics, "revisions": revisions, "item1a": paras,
        "item1a_method": "v0.3 (word diff; edits of at most five words with no numbers skip the model)"}


# ---------------------------------------------------------------- one metric across the eight companies

ALIGNED_DAYS = 31


def metrics_list():
    o = ontology.load()
    out = []
    for mid, m in list(o["metrics"].items()) + list(o["derived_metrics"].items()):
        out.append({"id": mid, "name": m.get("display_name") or mid, "statement": STATEMENTS.get(m.get("statement")),
                    "comparable": "cross_company_comparison" in m.get("allowed_operations", [])})
    return out


def peers(metric, fy):
    """One metric for one fiscal year at every company, each value from the typed engine (no model call), with the
    period it covers so the reader sees when fiscal years do not line up."""
    from datetime import date

    from .edgar import FILERS
    from .engine import execute
    from .typed_answer import _engine
    o, src = _engine()
    m = o["metrics"].get(metric) or o["derived_metrics"].get(metric)
    if m is None:
        raise KeyError(f"unknown metric {metric}")
    rows = []
    for t in FILERS:
        ex = execute.execute({"intent": "fact_lookup", "metric": metric, "companies": [t], "periods": [fy]}, "", src, o)
        cells = ex.get("cells") or []
        c = next((x for x in cells if x.get("period_start")), cells[0] if cells else {})
        val = (ex.get("result") or {}).get("value") if ex["outcome"] == "answer" else None
        unit = (ex.get("result") or {}).get("unit") or c.get("unit")
        days = None
        if c.get("period_start") and c.get("period_end"):
            days = (date.fromisoformat(c["period_end"]) - date.fromisoformat(c["period_start"])).days + 1
        rows.append({
            "ticker": t, "company": guards.NAMES.get(t, t), "outcome": ex["outcome"], "value": val, "unit": unit,
            "display": fmt(val, unit if unit != "percent" else "percent") if val is not None else None,
            "period_start": c.get("period_start"), "period_end": c.get("period_end"), "days": days,
            "weeks53": bool(days and days > 367),
            "warnings": [w["code"] for w in ex.get("warnings", []) if w["code"] != "derived_metric_definition"],
            "facts": [_ref({**x, "ticker": t}) for x in cells]})
    ends = [date.fromisoformat(r["period_end"]) for r in rows if r["period_end"]]
    gap = (max(ends) - min(ends)).days if ends else 0
    return {"metric": metric, "name": m.get("display_name") or metric, "fy": fy,
            "unit_type": m.get("unit_type"), "formula": m.get("formula"),
            "comparable": "cross_company_comparison" in m.get("allowed_operations", []),
            "aligned": gap <= ALIGNED_DAYS, "gap_days": gap,
            "earliest_end": min(ends).isoformat() if ends else None, "latest_end": max(ends).isoformat() if ends else None,
            "rows": rows}
