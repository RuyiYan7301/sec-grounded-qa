"""Reviewer-scorer agreement on the Part B review (written before the review; see audit_partb_pack.py).

    python -m secqa.evaluation.audit_partb_agree [--suffix S] PACKET.json [PACKET.json ...]
    # reads results/test/audit_partb/<case>/{numeric,revisions,item1a}<S>.csv, writes .../<case>/agreement<S>.json

For each case the reviewer's item verdicts are turned into the scores of docs/partB-scoring.md (same
definitions; packet statuses and labels are read from the packet itself) and set next to the scorer's
scores. Item by item: numeric items against the scorer's per-metric rows; Item 1A predictions by the gold
unit the reviewer found against the unit the locator maps to (accession, paragraph index and text hash).
Nothing is changed in the scorer or the automated results.
"""
import collections
import csv
import json
import sys

from .. import config
from .v2 import partb_score as ps

D = config.REPO_ROOT / "results" / "test" / "audit_partb"


def yn(v):
    v = (v or "").strip().lower()
    return True if v in ("y", "yes") else False if v in ("n", "no") else None


def rows(path, key):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def frac(x, n):
    return {"num": x, "den": n}


def numeric(packet, form, sc):
    g = ps.load_gold()["cases"][packet["case"]]["items"]
    st = {}
    for it in packet.get("numeric_changes") or []:
        st.setdefault(it.get("metric"), it.get("status"))
    large = [m for m, gi in g.items() if gi["label"] == "large_numeric_change"]
    pred_large = [m for m in g if st.get(m) == "large_numeric_change"]
    rv = {"verified_recall": frac(sum(yn(form[m]["value_correct"]) is True and st.get(m) == "large_numeric_change"
                                      for m in large), len(large)),
          "verified_precision": frac(sum(m in large and yn(form[m]["value_correct"]) is True for m in pred_large),
                                     len(pred_large)),
          "evidence_item_level": frac(sum(yn(form[m]["evidence_ok"]) is True for m in g if yn(form[m]["reported"])),
                                      sum(bool(yn(form[m]["reported"])) for m in g))}
    per = collections.Counter()
    diff = []
    for m, r in sc["items"].items():
        for f_rev, f_sc in (("reported", "reported"), ("value_correct", "value_correct"), ("evidence_ok", "item_evidence_ok")):
            h = yn(form[m][f_rev])
            s = r.get(f_sc)
            if h is None or s is None:
                continue
            per[f_rev + ("_agree" if h == bool(s) else "_disagree")] += 1
            if h != bool(s):
                diff.append({"metric": m, "field": f_rev, "scorer": bool(s), "reviewer": h, "note": form[m]["note"]})
    return {"reviewer": rv, "scorer": {k: {"num": sc[k]["num"], "den": sc[k]["den"]} for k in rv},
            "item_agreement": dict(per), "item_disagreements": diff}


def revisions(packet, form, sc):
    gold = ps.load_gold()["controls"][packet["case"]]
    lab = {k: v["label"] for k, v in gold.items()}
    ok = lambda r, *fs: all(yn(r[f]) is True for f in fs)
    rv = {"revision_stability_false_positives": frac(sum(1 for k, r in form.items() if lab[k] == "stable"
                                                        and yn(r["reported"]) and yn(r["status_ok"]) is False),
                                                     sum(1 for v in lab.values() if v == "stable")),
          "split_recast_recall": frac(sum(1 for k, r in form.items() if lab[k] == "stock_split_recast"
                                          and ok(r, "reported", "status_ok", "as_presented_ok", "first_reported_ok", "cause_ok")),
                                      sum(1 for v in lab.values() if v == "stock_split_recast")),
          "accounting_recast_recall": frac(sum(1 for k, r in form.items() if lab[k] == "accounting_recast"
                                               and ok(r, "reported", "status_ok", "as_presented_ok", "first_reported_ok", "cause_ok")),
                                           sum(1 for v in lab.values() if v == "accounting_recast"))}
    return {"reviewer": rv, "scorer": {k: {"num": sc[k]["num"], "den": sc[k]["den"]} for k in rv}}


def item1a(packet, form, sc):
    loc, labels = ps.load_item1a()
    units = {u["id"]: u for u in loc["cases"][packet["case"]]["units"]}
    side_map = {(s, u[s]["accession"], u[s]["paragraph_index"], u[s]["text_sha256"]): u["id"]
                for u in units.values() for s in ("earlier", "later") if s in u}
    preds = packet.get("item1a_changes") or []
    mapping_agree, mapping_diff = 0, []
    by_unit = collections.defaultdict(list)
    none = 0
    for n, p in enumerate(preds, 1):
        pid = f"P{n:03d}"
        hit = {side_map.get((s, p[s].get("accession"), p[s].get("paragraph_index"), p[s].get("text_sha256")))
               for s in ("earlier", "later") if isinstance(p.get(s), dict)} - {None}
        scorer_unit = next(iter(hit)) if len(hit) == 1 else ("conflict" if hit else "none")
        rev_unit = (form[pid]["unit_id"] or "").strip() or "none"
        if rev_unit == scorer_unit:
            mapping_agree += 1
        else:
            mapping_diff.append({"pred": pid, "scorer_unit": scorer_unit, "reviewer_unit": rev_unit, "note": form[pid]["note"]})
        if rev_unit in units:
            by_unit[rev_unit].append((p.get("label"), form[pid]))
        else:
            none += 1
    material = {u for u in units if labels.get(u, {}).get("label", "").startswith("material")}
    boiler = {u for u in units if labels.get(u, {}).get("label") == "boilerplate"}
    conflicting = {u for u, ps_ in by_unit.items() if len({l for l, _ in ps_}) > 1}
    hits = set(by_unit) - conflicting
    mat_hits = {u for u in hits if yn(by_unit[u][0][1]["material_hit"]) is True}
    rv = {"precision": frac(len(mat_hits), len(hits) + len(conflicting) + none),
          "recall": frac(len(mat_hits), len(material)),
          "boilerplate_fpr": frac(len((hits | conflicting) & boiler), len(boiler)),
          "subtype_agreement": frac(sum(yn(by_unit[u][0][1]["subtype_ok"]) is True for u in mat_hits), len(mat_hits)),
          "locator_complete": frac(sum(yn(by_unit[u][0][1]["locator_complete"]) is True for u in mat_hits), len(mat_hits))}
    return {"reviewer": rv, "scorer": {k: {"num": sc[k]["num"], "den": sc[k]["den"]} for k in rv},
            "prediction_mapping": {"agree": mapping_agree, "of": len(preds), "disagreements": mapping_diff},
            "reviewer_material_hits_not_material_in_gold": sorted(mat_hits - material)}


def main(paths, suffix=""):
    out = {}
    for p in paths:
        packet = json.loads(open(p, encoding="utf-8").read())
        case, d = packet["case"], D / packet["case"]
        sc = ps.score_packet(packet)
        res = {"packet": p}
        f = rows(d / f"numeric{suffix}.csv", "metric")
        if f:
            res["numeric"] = numeric(packet, f, sc["numeric"])
        f = rows(d / f"revisions{suffix}.csv", "id")
        if f:
            res["revisions"] = revisions(packet, f, sc["revisions"])
        f = rows(d / f"item1a{suffix}.csv", "pred_no")
        if f and sc["item1a"].get("scored"):
            res["item1a"] = item1a(packet, f, sc["item1a"])
        (d / f"agreement{suffix}.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
        out[case] = res
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:]
    suf = ""
    if args[:1] == ["--suffix"]:
        suf, args = args[1], args[2:]
    main(args, suf)
