"""Part B per-value provenance and text verification.

    python -m secqa.evaluation.v2.partb_provenance
        # writes data/eval/v0.2/cases/provenance.json and results/v0.2/partB_provenance_audit.json

For every value behind a Part B label (both years of every case item, components of derived metrics,
every revision-stability control, the AMD micro-case) it records where the value comes from and checks
it in the converted 10-K text of the accession it is reported in. The committed case files and their
labels are not changed.

Status per value:
  verified_in_text                     the value is printed in the text of its reported-in 10-K
  accession_verified_text_not_located  the companyfacts row (accession, value, period) exists, but the value
                                       was not found in the converted text; reason given
A value is never called fully verified unless it is found in the text.
"""
import json

from ... import config, edgar, ontology
from . import gen_cases, gold
from . import verify_gold_text as vt

CASES_DIR = config.EVAL_DIR / "v0.2" / "cases"
OUT = CASES_DIR / "provenance.json"
AUDIT = config.REPO_ROOT / "results" / "v0.2" / "partB_provenance_audit.json"
POLICY = "as_of_filing"


class Text:
    def __init__(self):
        self.files = vt.accession_files()
        self.cache = {}

    def check(self, accn, value, unit):
        name = self.files.get(accn)
        if not name:
            return "accession_verified_text_not_located", "no converted text for this accession (not an indexed original 10-K)"
        if name not in self.cache:
            self.cache[name] = (vt.filings.text_dir() / name).read_text(encoding="utf-8")
        t = self.cache[name]
        if any(vt.find(t, s) for s in vt.forms(value, unit)):
            return "verified_in_text", name
        return "accession_verified_text_not_located", f"value not found in {name} in any usual printed form"


def _row_exists(ticker, tag, fact):
    """The companyfacts row behind a value: same accession, value and period end."""
    units = gold._raw(ticker).get(tag, {}).get("units", {})
    return any(r.get("accn") == fact["accn"] and r.get("val") == fact["val"] and r.get("end") == fact["end"]
               for rs in units.values() for r in rs)


def base_record(o, ticker, metric, fy, role, target, txt, cutoff):
    r = gold.resolve(o, ticker, metric, fy, cutoff)
    if r["outcome"] != "answer":
        return {"ticker": ticker, "metric": metric, "fy": f"FY{fy}", "role": role, "outcome": r["outcome"]}
    f = r["fact"]
    assert _row_exists(ticker, f["tag"], f), (ticker, metric, fy)
    rec = {"ticker": ticker, "metric": metric, "fy": f"FY{fy}", "role": role, "value": f["val"], "unit": f["unit"],
           "concept": f["tag"], "use": r["use"], "period_start": f.get("start"), "period_end": f["end"],
           "reported_in_accession": f["accn"], "filed": f["filed"], "target_filing_accession": target["accession"],
           "value_policy": POLICY, "companyfacts_row": "verified"}
    if f["earlier_values"]:
        e = f["earlier_values"][0]
        split = o["metrics"][metric].get("split_sensitive")
        rec["revision"] = {"first_reported_accession": f["first_accn"], "first_filed": f["first_filed"],
                           "original_value": e["val"], "later_value": f["val"],
                           "cause": "stock_split" if split else "accounting_recast"}
    rec["text_status"], rec["text_detail"] = txt.check(f["accn"], f["val"], f["unit"])
    return rec


def value_records(o, ticker, metric, fy, role, target, txt, cutoff):
    if metric in o["metrics"]:
        return [base_record(o, ticker, metric, fy, role, target, txt, cutoff)]
    a, _, b = o["derived_metrics"][metric]["formula"].split()
    return [{**x, "component_of": metric} for m in (a, b)
            for x in value_records(o, ticker, m, fy, role, target, txt, cutoff)]


def main():
    o = ontology.load()
    txt = Text()
    out = {"value_policy": POLICY, "cases": {}, "revision_controls": [], "micro_cases": {}}
    for name, (t, y1, y2, split) in gen_cases.CASES.items():
        doc = json.loads((CASES_DIR / f"{name}.numeric.json").read_text(encoding="utf-8"))
        target = doc["target_filing"]
        cutoff = target["filed"]
        items = []
        for it in doc["items"]:
            vals = (value_records(o, t, it["metric"], y1, "comparative_year", target, txt, cutoff)
                    + value_records(o, t, it["metric"], y2, "current_year", target, txt, cutoff))
            items.append({"id": f"{name}:{it['metric']}:numeric_change", "metric": it["metric"],
                          "label": it["label"], "values": vals})
        out["cases"][name] = {"split": split, "target_filing": target, "items": items}
    rc = json.loads((CASES_DIR / "revision_stability_controls.json").read_text(encoding="utf-8"))["items"]
    for r in rc:
        t = r["ticker"]
        y2 = 2025 if r["target"] in ("NVDA_FY2025", "INTC_FY2025", "AMD_FY2025") else 2024
        target = gen_cases.target_filing(t, y2)
        rec = base_record(o, t, r["metric"], int(r["period"][2:]), "prior_year_as_presented", target, txt, target["filed"])
        rec["id"] = f"{r['target']}:{r['metric']}:{r['period']}:revision_control"
        rec["label"] = r["label"]
        if "first_reported" in r:
            fr = r["first_reported"]
            st, det = txt.check(fr["accession"], fr["val"], rec.get("unit"))
            rec["first_reported"] = {"value": fr["val"], "accession": fr["accession"], "filed": fr["filed"],
                                     "text_status": st, "text_detail": det}
        out["revision_controls"].append(rec)
    for name in gen_cases.MICRO:
        doc = json.loads((CASES_DIR / f"{name}.json").read_text(encoding="utf-8"))
        rows = {}
        for k in ("first_reported", "as_presented_in_target"):
            v = doc[k]
            st, det = txt.check(v["accession"], v["val"], "USD")
            rows[k] = {**v, "text_status": st, "text_detail": det}
        out["micro_cases"][name] = {"label": doc["label"], "target_filing": doc["target_filing"], **rows}
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")

    def statuses():
        for c in out["cases"].values():
            for it in c["items"]:
                for v in it["values"]:
                    if "text_status" in v:
                        yield "case", v
        for r in out["revision_controls"]:
            yield "revision_control", r
            if "first_reported" in r:
                yield "revision_control_first_reported", r["first_reported"]
        for m in out["micro_cases"].values():
            for k in ("first_reported", "as_presented_in_target"):
                yield "micro_case", m[k]

    summary, not_located = {}, []
    for kind, v in statuses():
        summary.setdefault(kind, {}).setdefault(v["text_status"], 0)
        summary[kind][v["text_status"]] += 1
        if v["text_status"] != "verified_in_text":
            not_located.append({"kind": kind, **{k: v.get(k) for k in ("ticker", "metric", "fy", "value", "accession",
                                                                    "reported_in_accession", "text_detail")}})
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps({"summary": summary, "not_located": not_located}, indent=1) + "\n",
                     encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))
    for n in not_located:
        print("  ", n)


if __name__ == "__main__":
    edgar.ALLOW_FETCH = False
    main()
