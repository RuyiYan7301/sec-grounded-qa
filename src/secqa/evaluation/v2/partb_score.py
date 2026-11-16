"""Part B scorer (change packets, v0.2 only). Structured fields only; rules in docs/partB-scoring.md.

    python -m secqa.evaluation.v2.partb_score PACKET.json [PACKET.json ...]

Numeric packet and Item 1A are scored separately and never combined. The scorer never raises on a
malformed packet: what cannot be read scores as missing, and packet_valid / packet_metadata_ok say why.
`reference_packet(case)` builds the correct packet from the gold; it exists for tests only.
"""
import collections
import json
import math
import sys

import jsonschema

from ... import config

V = "1.0"
DIR = config.EVAL_DIR / "v0.2"
CASES_DIR = DIR / "cases"
TEST_CASES = ("NVDA_FY2025", "INTC_FY2025", "AVGO_FY2024")
SIZE = ("large_numeric_change", "gray_zone", "unchanged_control")
REL, EPS_ABS, PP_ABS = 0.005, 0.01, 0.1


# ---------------------------------------------------------------- small helpers
def wilson(x, n, z=1.96):
    if not n:
        return None
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - h, 4), round(c + h, 4)]


def ratio(x, n, ci=False):
    out = {"num": x, "den": n, "value": (x / n) if n else None}
    if ci:
        out["wilson95"] = wilson(x, n)
    return out


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def close_value(got, want, unit):
    if not num(got):
        return False
    if unit and "/" in unit:
        return abs(got - want) <= EPS_ABS + 1e-9
    return abs(got - want) <= REL * max(abs(want), 1e-9)


def dicts(xs):
    return [x for x in xs if isinstance(x, dict)] if isinstance(xs, list) else []


def canon(x):
    return json.dumps(x, sort_keys=True, default=str)


# ---------------------------------------------------------------- gold
def load_gold():
    prov = json.loads((CASES_DIR / "provenance.json").read_text(encoding="utf-8"))
    cases = {}
    for name in prov["cases"]:
        doc = json.loads((CASES_DIR / f"{name}.numeric.json").read_text(encoding="utf-8"))
        items = {}
        for it, pv in zip(doc["items"], prov["cases"][name]["items"]):
            assert it["metric"] == pv["metric"]
            facts = [v for v in pv["values"] if "value" in v]
            items[it["metric"]] = {**it, "id": pv["id"], "facts": facts}
        cases[name] = {"split": doc["split"], "ticker": doc["ticker"], "from_fy": doc["from"], "to_fy": doc["to"],
                       "target": doc["target_filing"], "items": items}
    controls = collections.defaultdict(dict)
    for r in prov["revision_controls"]:
        controls[r["id"].split(":")[0]][r["id"]] = r
    for name in dict.fromkeys(r["id"].split(":")[0] for r in prov["revision_controls"]):
        if name not in cases:   # AMD micro-case: revision checks only
            t = name.split("_")[0]
            r0 = next(iter(controls[name].values()))
            cases[name] = {"split": "test", "ticker": t, "from_fy": None, "to_fy": f"FY{name[-4:]}",
                           "target": {"accession": r0["target_filing_accession"], "filed": None}, "items": {},
                           "micro": True}
    amd = json.loads((CASES_DIR / "AMD_FY2025_sga.json").read_text(encoding="utf-8"))
    cases["AMD_FY2025"]["target"]["filed"] = amd["target_filing"]["filed"]
    return {"cases": cases, "controls": controls}


def gold_direction(it):
    if it.get("direction"):
        return it["direction"]
    if it.get("change_basis") == "sign_change":
        return "sign_change"
    d = it.get("absolute_change", it.get("pp_change"))
    return "increase" if d and d > 0 else "decrease" if d and d < 0 else "no_change"


# ---------------------------------------------------------------- metadata
def metadata_ok(packet, g):
    case = packet.get("case")
    if case not in g["cases"]:
        return False, ["unknown case"]
    c = g["cases"][case]
    bad = []
    if packet.get("ticker") != c["ticker"]:
        bad.append("ticker")
    if c.get("from_fy") and packet.get("from_fy") != c["from_fy"]:
        bad.append("from_fy")
    if packet.get("to_fy") != c["to_fy"]:
        bad.append("to_fy")
    tf = packet.get("target_filing") if isinstance(packet.get("target_filing"), dict) else {}
    if tf.get("accession") != c["target"]["accession"]:
        bad.append("target_filing.accession")
    if c["target"].get("filed") and tf.get("filed") != c["target"]["filed"]:
        bad.append("target_filing.filed")
    if packet.get("value_policy") != "as_of_filing":
        bad.append("value_policy")
    return not bad, bad


# ---------------------------------------------------------------- facts
def fact_key(f):
    return (f.get("metric"), f.get("fy"), f.get("role"), f.get("component_of"))


def gold_fact_key(v):
    return (v["metric"], v["fy"], v["role"], v.get("component_of"))


def check_fact(f, gv, case):
    """(passes_evidence, value_ok, look_ahead) of one packet fact against its gold value record."""
    look_ahead = isinstance(f.get("filed"), str) and isinstance(case["target"].get("filed"), str) \
        and f["filed"] > case["target"]["filed"]
    value_ok = close_value(f.get("value"), gv["value"], gv.get("unit"))
    provenance_ok = (f.get("ticker") == case["ticker"] and f.get("concept") == gv["concept"]
                     and f.get("period_end") == gv["period_end"] and f.get("accession") == gv["reported_in_accession"]
                     and f.get("filed") == gv["filed"])
    return provenance_ok and value_ok and not look_ahead, value_ok, look_ahead


def facts_against(item_facts, gold_values, case):
    """Per-fact results and whether the packet's fact set equals the gold expected set."""
    gmap = {gold_fact_key(v): v for v in gold_values}
    seen, results = set(), []
    for f in dicts(item_facts):
        k = fact_key(f)
        gv = gmap.get(k)
        if gv is None or k in seen:
            results.append({"key": k, "known": False, "pass": False, "value_ok": False, "look_ahead": False})
            continue
        seen.add(k)
        p, v, la = check_fact(f, gv, case)
        results.append({"key": k, "known": True, "pass": p, "value_ok": v, "look_ahead": la,
                        "value": f.get("value"), "gold": gv["value"]})
    exact_set = seen == set(gmap) and all(r["known"] for r in results)
    return results, exact_set


# ---------------------------------------------------------------- numeric
def change_ok(item, git):
    """The stated change fields agree with the gold item."""
    if item.get("change_basis") != git.get("change_basis"):
        return False
    if item.get("direction") != gold_direction(git):
        return False
    if git["kind"] == "ratio":
        return num(item.get("pp_change")) and abs(item["pp_change"] - git["pp_change"]) <= PP_ABS
    scale = max(abs(git["v1"]), abs(git["v2"]), 1e-9)
    if not (num(item.get("absolute_change")) and abs(item["absolute_change"] - git["absolute_change"]) <= REL * scale):
        return False
    if git.get("percent_change") is None:
        return item.get("percent_change") is None
    return num(item.get("percent_change")) and abs(item["percent_change"] - git["percent_change"]) <= PP_ABS


def group_numeric(packet, case_name):
    groups = collections.OrderedDict()
    for it in dicts(packet.get("numeric_changes")):
        groups.setdefault(it.get("id"), []).append(it)
    out = {}
    for iid, its in groups.items():
        distinct = {canon(x) for x in its}
        out[iid] = {"item": its[0], "duplicate_count": len(its) - 1, "inconsistent": len(distinct) > 1}
    return out


def score_numeric(packet, g, meta_ok):
    case_name = packet.get("case")
    case = g["cases"].get(case_name, {"items": {}, "target": {}})
    gitems = case["items"]
    groups = group_numeric(packet, case_name) if meta_ok else {}
    by_metric = {}
    unknown = 0
    for iid, grp in groups.items():
        parts = iid.split(":") if isinstance(iid, str) else []
        metric = parts[1] if len(parts) == 3 else None
        if (len(parts) != 3 or parts[0] != case_name or parts[2] != "numeric_change" or metric not in gitems
                or grp["item"].get("metric") != metric):
            unknown += 1
            by_metric.setdefault(("unknown", iid), grp)
            continue
        by_metric[metric] = grp
    rows = {}
    silent = 0
    look_ahead = 0
    fact_pass = fact_total = 0
    for metric, git in gitems.items():
        grp = by_metric.get(metric)
        r = {"id": git["id"], "gold_label": git["label"], "reported": grp is not None}
        if grp:
            it = grp["item"]
            res, exact = facts_against(it.get("facts"), git["facts"], case)
            fact_total += len(res)
            fact_pass += sum(x["pass"] for x in res)
            silent += sum(1 for x in res if x["known"] and not x["value_ok"])
            la = sum(1 for x in res if x["look_ahead"])
            look_ahead += la
            silent += sum(1 for x in res if x["look_ahead"] and not x["value_ok"])   # look-ahead with a different value: once more
            status = it.get("status")
            ch_ok = git["label"] in SIZE and status in SIZE and change_ok(it, git)
            if status in SIZE and git["label"] in SIZE and not ch_ok and git.get("change_basis"):
                silent += 1     # a stated change outside tolerance of the gold change
            value_correct = (not grp["inconsistent"] and exact and all(x["pass"] for x in res)
                             and (git["label"] not in SIZE or ch_ok))
            r |= {"status": status, "inconsistent_duplicate": grp["inconsistent"],
                  "duplicate_count": grp["duplicate_count"], "facts_exact_set": exact,
                  "item_evidence_ok": exact and all(x["pass"] for x in res) and not grp["inconsistent"],
                  "value_correct": value_correct, "warnings": it.get("warnings") if isinstance(it.get("warnings"), list) else [],
                  "abstain_reason": it.get("abstain_reason")}
        rows[metric] = r
    unknown_large = sum(1 for k, grp in by_metric.items() if isinstance(k, tuple)
                        and grp["item"].get("status") == "large_numeric_change")

    def reported(r, status):
        return r["reported"] and not r.get("inconsistent_duplicate") and r.get("status") == status

    large_gold = [r for r in rows.values() if r["gold_label"] == "large_numeric_change"]
    pred_large = [r for r in rows.values() if r["reported"] and (r.get("status") == "large_numeric_change"
                                                                 or r.get("inconsistent_duplicate"))]
    n_pred = len(pred_large) + unknown_large
    v_hit = sum(1 for r in large_gold if reported(r, "large_numeric_change") and r["value_correct"])
    d_hit = sum(1 for r in large_gold if reported(r, "large_numeric_change"))
    v_tp = sum(1 for r in pred_large if r["gold_label"] == "large_numeric_change"
               and not r.get("inconsistent_duplicate") and r["value_correct"])
    d_tp = sum(1 for r in pred_large if r["gold_label"] == "large_numeric_change" and not r.get("inconsistent_duplicate"))
    controls = [r for r in rows.values() if r["gold_label"] == "unchanged_control"]
    ctrl_fp = sum(1 for r in controls if r["reported"] and r.get("status") in ("large_numeric_change", "gray_zone"))
    abst = [r for r in rows.values() if r["gold_label"] == "expected_abstention"]
    gold_reason = {m: next((o for o in gitems[m].get("outcomes", []) if o != "answer"), None) for m in gitems}
    abst_ok = sum(1 for m, r in rows.items() if r["gold_label"] == "expected_abstention" and reported(r, "abstain")
                  and r.get("abstain_reason") == gold_reason[m])
    over_abst = sum(1 for r in rows.values() if r["gold_label"] != "expected_abstention" and reported(r, "abstain"))
    scope = [m for m, git in gitems.items() if "scope_warning" in git.get("flags", [])]
    scope_ok = sum(1 for m in scope if rows[m]["reported"] and "scope" in rows[m].get("warnings", []))
    false_concept = sum(1 for r in rows.values() if r["gold_label"] != "concept_change" and reported(r, "concept_change"))
    reported_items = [r for r in rows.values() if r["reported"]]
    return {
        "verified_recall": ratio(v_hit, len(large_gold), ci=True),
        "verified_precision": ratio(v_tp, n_pred, ci=True),
        "detection_recall": ratio(d_hit, len(large_gold)),
        "detection_precision": ratio(d_tp, n_pred),
        "unchanged_control_false_positives": {"num": ctrl_fp, "den": len(controls), "descriptive": True},
        "correct_abstention": ratio(abst_ok, len(abst)),
        "over_abstention": over_abst,
        "scope_warning": ratio(scope_ok, len(scope)),
        "false_concept_change_claims": false_concept,
        "evidence_fact_level": ratio(fact_pass, fact_total),
        "evidence_item_level": ratio(sum(1 for r in reported_items if r["item_evidence_ok"]), len(reported_items)),
        "evidence_packet_all_pass": (all(r["item_evidence_ok"] for r in reported_items) if reported_items else None),
        "silent_numeric_errors": silent, "look_ahead_facts": look_ahead,
        "unknown_item_count": unknown,
        "inconsistent_duplicate_ids": sum(1 for r in rows.values() if r.get("inconsistent_duplicate")),
        "items": rows,
    }


# ---------------------------------------------------------------- revision checks
def score_revisions(packet, g, meta_ok):
    case_name = packet.get("case")
    gold = g["controls"].get(case_name, {})
    groups = collections.OrderedDict()
    for rc in dicts(packet.get("revision_checks")) if meta_ok else []:
        groups.setdefault(rc.get("id"), []).append(rc)
    stable_fp = split_ok = recast_ok = 0
    stable_claim_without_evidence = 0
    silent = 0
    unknown = 0
    for iid, rcs in groups.items():
        if iid not in gold:
            unknown += 1
            continue
        gr = gold[iid]
        inconsistent = len({canon(x) for x in rcs}) > 1
        rc = rcs[0]
        st = rc.get("status")
        ap = rc.get("as_presented") if isinstance(rc.get("as_presented"), dict) else {}
        fr = rc.get("first_reported") if isinstance(rc.get("first_reported"), dict) else None
        ap_ok = (ap.get("accession") == gr["reported_in_accession"] and close_value(ap.get("value"), gr["value"], gr.get("unit"))
                 and ap.get("concept") == gr["concept"] and ap.get("period_end") == gr["period_end"])
        gfr = gr.get("first_reported")
        fr_ok = bool(fr and gfr and fr.get("accession") == gfr["accession"]
                     and close_value(fr.get("value"), gfr["value"], gr.get("unit")))
        if ap and not close_value(ap.get("value"), gr["value"], gr.get("unit")):
            silent += 1
        if fr and gfr and not close_value(fr.get("value"), gfr["value"], gr.get("unit")):
            silent += 1
        if gr["label"] == "stable" and (st == "revised" or inconsistent):
            stable_fp += 1
        if st == "stable" and not (ap_ok and fr_ok and close_value(fr.get("value") if fr else None, ap.get("value") or 0, gr.get("unit"))):
            stable_claim_without_evidence += 1
        if not inconsistent and st == "revised" and ap_ok and fr_ok:
            if gr["label"] == "stock_split_recast" and rc.get("cause") == "stock_split_recast":
                split_ok += 1
            if gr["label"] == "accounting_recast" and rc.get("cause") == "accounting_recast":
                recast_ok += 1
    n_stable = sum(1 for r in gold.values() if r["label"] == "stable")
    return {
        "revision_stability_false_positives": ratio(stable_fp, n_stable),
        "split_recast_recall": ratio(split_ok, sum(1 for r in gold.values() if r["label"] == "stock_split_recast")),
        "accounting_recast_recall": ratio(recast_ok, sum(1 for r in gold.values() if r["label"] == "accounting_recast")),
        "stable_claims_without_two_sided_evidence": stable_claim_without_evidence,
        "no_prior_observation_items_not_scored": sum(1 for r in gold.values() if r["label"] == "no_prior_observation"),
        "silent_numeric_errors": silent, "unknown_item_count": unknown,
    }


# ---------------------------------------------------------------- Item 1A
def load_item1a():
    import csv
    loc = json.loads((DIR / "partB" / "item1a_locators.json").read_text(encoding="utf-8"))
    test = {r["hunk_id"]: r for r in csv.DictReader(open(DIR / "item1a" / "protocol_v2" / "gold_item1a_v2_test.csv",
                                                         encoding="utf-8"))}
    dev = {r["hunk_id"]: {"label": r["label"], "source": "claude_v2_single"}
           for r in csv.DictReader(open(DIR / "item1a" / "protocol_v2" / "labels_claude" / "dev.csv", encoding="utf-8"))}
    labels = {**{k: {"label": v["label"], "source": v["source"]} for k, v in test.items()}, **dev}
    return loc, labels


def score_item1a(packet, meta_ok, loc, labels):
    case = loc["cases"].get(packet.get("case"))
    if not case or not meta_ok:
        return {"scored": False}
    side_map = {}
    units = {u["id"]: u for u in case["units"]}
    for u in case["units"]:
        for side in ("earlier", "later"):
            if side in u:
                lx = u[side]
                side_map[(side, lx["accession"], lx["paragraph_index"], lx["text_sha256"])] = u["id"]
    preds = collections.defaultdict(list)
    unmatched = inconsistent_loc = 0
    for p in dicts(packet.get("item1a_changes")):
        hit = set()
        for side in ("earlier", "later"):
            lx = p.get(side) if isinstance(p.get(side), dict) else None
            if lx:
                k = (side, lx.get("accession"), lx.get("paragraph_index"), lx.get("text_sha256"))
                if k in side_map:
                    hit.add(side_map[k])
        if not hit:
            unmatched += 1
        elif len(hit) > 1:
            inconsistent_loc += 1
        else:
            preds[next(iter(hit))].append(p)
    material = {i for i in units if labels.get(i, {}).get("label", "").startswith("material")}
    boiler = {i for i in units if labels.get(i, {}).get("label") == "boilerplate"}
    hits, conflicting = set(), set()
    subtype_ok = locator_complete = 0
    for uid, ps in preds.items():
        if len({p.get("label") for p in ps}) > 1:
            conflicting.add(uid)
            continue
        hits.add(uid)
        if uid in material:
            subtype_ok += ps[0].get("label") == labels[uid]["label"]
            need = {"added": ("later",), "removed": ("earlier",), "modified": ("earlier", "later")}[units[uid]["type"]]
            locator_complete += all(isinstance(ps[0].get(s), dict) for s in need)
    n_pred = len(hits) + len(conflicting) + unmatched + inconsistent_loc
    mat_hits = hits & material

    def subset(ids):
        m, b = material & ids, boiler & ids
        return {"recall": ratio(len(mat_hits & m), len(m)), "boilerplate_fpr": ratio(len((hits | conflicting) & b), len(b)),
                "subtype_agreement": ratio(sum(1 for u in mat_hits & m if preds[u][0].get("label") == labels[u]["label"]),
                                           len(mat_hits & m))}
    double = {i for i in units if labels.get(i, {}).get("source") in ("adjudicated", "cross_model_agreed")}
    return {"scored": True, "precision": ratio(len(mat_hits), n_pred, ci=True),
            "recall": ratio(len(mat_hits), len(material), ci=True),
            "boilerplate_fpr": ratio(len((hits | conflicting) & boiler), len(boiler)),
            "subtype_agreement": ratio(subtype_ok, len(mat_hits)),
            "locator_complete": ratio(locator_complete, len(mat_hits)),
            "unmatched_predictions": unmatched, "inconsistent_locators": inconsistent_loc,
            "conflicting_duplicate_units": len(conflicting),
            "doubly_labelled_subset": subset(double) if double else None}


# ---------------------------------------------------------------- packet
SCHEMA = None


def packet_valid(packet):
    global SCHEMA
    if SCHEMA is None:
        SCHEMA = json.loads((DIR / "packet.schema.json").read_text(encoding="utf-8"))
    return not any(True for _ in jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
                   .iter_errors(packet))


def score_packet(packet, g=None, item1a_gold=None):
    g = g or load_gold()
    loc, labels = item1a_gold or load_item1a()
    packet = packet if isinstance(packet, dict) else {}
    ok, bad = metadata_ok(packet, g)
    return {"scorer_version": V, "case": packet.get("case"), "packet_valid": packet_valid(packet),
            "packet_metadata_ok": ok, "metadata_errors": bad,
            "numeric": score_numeric(packet, g, ok), "revisions": score_revisions(packet, g, ok),
            "item1a": score_item1a(packet, ok, loc, labels)}


# ---------------------------------------------------------------- reference packet (tests only)
def reference_packet(case_name, g=None, item1a_gold=None):
    """The correct packet, built from the gold. For tests and mutation tests only."""
    g = g or load_gold()
    loc, labels = item1a_gold or load_item1a()
    c = g["cases"][case_name]
    p = {"schema_version": "packet-0.2-draft3", "case": case_name, "system": "v0.2", "ticker": c["ticker"],
         "from_fy": c["from_fy"] or "FY2024", "to_fy": c["to_fy"], "value_policy": "as_of_filing",
         "target_filing": {"accession": c["target"]["accession"], "filed": c["target"]["filed"]},
         "numeric_changes": [], "revision_checks": [], "item1a_changes": []}

    def fact(v, role=None):
        return {"ticker": c["ticker"], "metric": v["metric"], "component_of": v.get("component_of"), "fy": v["fy"],
                "role": role or v["role"], "value": v["value"], "unit": v["unit"], "concept": v["concept"],
                "period_start": v.get("period_start"), "period_end": v["period_end"],
                "accession": v["reported_in_accession"], "filed": v["filed"]}

    for m, it in c["items"].items():
        x = {"id": it["id"], "metric": m, "warnings": ["scope"] if "scope_warning" in it.get("flags", []) else []}
        if it["label"] == "expected_abstention":
            reason = next(o for o in it["outcomes"] if o != "answer")
            x |= {"status": "abstain", "abstain_reason": reason, "facts": [], "absolute_change": None,
                  "percent_change": None, "pp_change": None, "change_basis": None, "direction": None}
        else:
            x |= {"status": it["label"], "abstain_reason": None, "facts": [fact(v) for v in it["facts"]],
                  "change_basis": it.get("change_basis"), "direction": gold_direction(it),
                  "absolute_change": it.get("absolute_change"), "percent_change": it.get("percent_change"),
                  "pp_change": it.get("pp_change")}
        p["numeric_changes"].append(x)
    for iid, r in g["controls"].get(case_name, {}).items():
        ap = fact({**r, "fy": r["fy"], "reported_in_accession": r["reported_in_accession"]}, "prior_year_as_presented")
        fr = r.get("first_reported")
        frf = None if not fr or r["label"] == "no_prior_observation" else {
            **ap, "role": "first_reported", "value": fr["value"], "accession": fr["accession"], "filed": fr["filed"]}
        status = {"stable": "stable", "no_prior_observation": "no_prior_observation"}.get(r["label"], "revised")
        p["revision_checks"].append({"id": iid, "metric": r["metric"], "period": r["fy"], "as_presented": ap,
                                     "first_reported": frf, "status": status,
                                     "cause": r["label"] if status == "revised" else None})
    lc = loc["cases"].get(case_name)
    if lc:
        for u in lc["units"]:
            lab = labels.get(u["id"], {}).get("label", "")
            if lab.startswith("material"):
                q = {"label": lab}
                for side in ("earlier", "later"):
                    if side in u and not (lab == "material_added" and side == "earlier") \
                            and not (lab == "material_removed" and side == "later"):
                        q[side] = {k: u[side][k] for k in ("accession", "section", "paragraph_index", "text_sha256")}
                p["item1a_changes"].append(q)
    return p


def main(paths):
    g, ig = load_gold(), load_item1a()
    out = [score_packet(json.loads(open(p, encoding="utf-8").read()), g, ig) for p in paths]
    for r in out:
        print(json.dumps({k: v for k, v in r.items() if k not in ("numeric",)} | {"numeric": {
            k: v for k, v in r["numeric"].items() if k != "items"}}, indent=1))
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
