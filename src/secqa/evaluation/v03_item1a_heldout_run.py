"""Item 1A v0.3 held-out run, once, after the v0.3 freeze (docs/item1a-v0.3-plan.md).

    python -m secqa.evaluation.v03_item1a_heldout_run SYSTEM [--model M]
    # SYSTEM: v0.2 (frozen engine.item1a_changes.detect) or v0.3 (engine.item1a_v03 "diff_small", K fixed)
    # writes results/test/item1a_v03/heldout_<system>_<model>_<UTC>.json (one file per finished case too)
    python -m secqa.evaluation.v03_item1a_heldout_run --compare RUN_V02.json RUN_V03.json

Scoring: the frozen Part B Item 1A rules (partb_score.score_item1a) against the multi-model consensus
reference (reference_item1a_v03_heldout.csv) on all 206 units, and the same scores on the high-confidence
subset (units where Claude and Gemini agreed): there, a prediction that maps to an adjudicated unit is left
out of every count. Unit-level pairing for the comparison: a unit is "flagged" by a system when a
prediction maps to it (as in the scorer); exact two-sided McNemar on boilerplate units (false flags) and on
material units (hits).
"""
import argparse
import collections
import csv
import datetime
import json
from math import comb

import requests

from .. import config
from ..engine import item1a_changes as v02, item1a_v03, llm
from .run_v01 import commit
from .v2 import partb_score as ps

D = config.EVAL_DIR / "v0.3" / "item1a"
OUT = config.REPO_ROOT / "results" / "test" / "item1a_v03"
CASES = {"MSFT_FY2026": ("MSFT", 2025, 2026), "ORCL_FY2026": ("ORCL", 2025, 2026)}
SCORES = ("precision", "recall", "boilerplate_fpr", "subtype_agreement", "locator_complete")


def reference():
    loc = json.loads((D / "item1a_locators.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(D / "reference_item1a_v03_heldout.csv", encoding="utf-8")))
    labels = {r["hunk_id"]: {"label": r["label"], "source": r["source"]} for r in rows}
    return loc, labels


def unit_hits(packet, loc):
    """{unit id: [predicted labels]} plus counts of unmatched and inconsistent predictions (scorer rules)."""
    case = loc["cases"][packet["case"]]
    side_map = {(s, u[s]["accession"], u[s]["paragraph_index"], u[s]["text_sha256"]): u["id"]
                for u in case["units"] for s in ("earlier", "later") if s in u}
    hits, unmatched, inconsistent = collections.defaultdict(list), 0, 0
    for p in packet["item1a_changes"]:
        got = {side_map.get((s, p[s]["accession"], p[s]["paragraph_index"], p[s]["text_sha256"]))
               for s in ("earlier", "later") if isinstance(p.get(s), dict)} - {None}
        if not got:
            unmatched += 1
        elif len(got) > 1:
            inconsistent += 1
        else:
            hits[next(iter(got))].append(p["label"])
    return hits, unmatched, inconsistent


def subset_scores(packet, loc, labels, keep):
    """Scorer rules restricted to the units in `keep`; predictions on other units are left out."""
    units = {u["id"]: u for u in loc["cases"][packet["case"]]["units"]}
    hits, unmatched, inconsistent = unit_hits(packet, loc)
    hits = {u: l for u, l in hits.items() if u in keep}
    conflicting = {u for u, l in hits.items() if len(set(l)) > 1}
    ok = set(hits) - conflicting
    material = {u for u in keep if labels[u]["label"].startswith("material")}
    boiler = {u for u in keep if labels[u]["label"] == "boilerplate"}
    mat_hits = ok & material
    need = {"added": ("later",), "removed": ("earlier",), "modified": ("earlier", "later")}
    loc_ok = 0
    for u in mat_hits:
        p = next(x for x in packet["item1a_changes"] if x["label"] == hits[u][0] and any(
            isinstance(x.get(s), dict) and x[s]["paragraph_index"] == units[u].get(s, {}).get("paragraph_index")
            for s in ("earlier", "later")))
        loc_ok += all(isinstance(p.get(s), dict) for s in need[units[u]["type"]])
    r = lambda x, n: {"num": x, "den": n, "wilson95": ps.wilson(x, n)}
    return {"precision": r(len(mat_hits), len(ok) + len(conflicting)),   # unmatched predictions cannot be placed in a subset
            "recall": r(len(mat_hits), len(material)),
            "boilerplate_fpr": r(len((ok | conflicting) & boiler), len(boiler)),
            "subtype_agreement": r(sum(hits[u][0] == labels[u]["label"] for u in mat_hits), len(mat_hits)),
            "locator_complete": r(loc_ok, len(mat_hits)),
            "unmatched_predictions_not_counted": unmatched, "inconsistent_predictions_not_counted": inconsistent}


def run(system, model=None):
    model = model or config.DEFAULT_MODEL
    loc, labels = reference()
    hc = {u for u, v in labels.items() if v["source"] == "high_confidence"}
    started = datetime.datetime.now(datetime.timezone.utc)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    try:
        ollama_version = requests.get(f"{config.OLLAMA_HOST}/api/version", timeout=10).json().get("version")
    except requests.RequestException:
        ollama_version = None
    OUT.mkdir(parents=True, exist_ok=True)
    per = {}
    for case, (t, y1, y2) in CASES.items():
        log = llm.CallLog()
        if system == "v0.2":
            d = v02.detect(t, y1, y2, log=log, model=model)
        else:
            d = item1a_v03.detect(t, y1, y2, "diff_small", log=log, model=model)
        packet = {"case": case, "item1a_changes": d["item1a_changes"]}
        full = ps.score_item1a(packet, True, loc, labels)
        per[case] = {"full": {k: full[k] for k in SCORES} | {k: full[k] for k in ("unmatched_predictions", "inconsistent_locators")},
                     "high_confidence": subset_scores(packet, loc, labels, hc & {u["id"] for u in loc["cases"][case]["units"]}),
                     "calls": d["calls"], "item1a_changes": d["item1a_changes"], "candidates": d["candidates"]}
        (OUT / f"partial_{system}_{model.replace(':', '-')}_{stamp}_{case}.json").write_text(
            json.dumps(per[case], ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(case, {k: f"{full[k]['num']}/{full[k]['den']}" for k in SCORES}, flush=True)
    pooled = {view: {k: {"num": sum(per[c][view][k]["num"] for c in per), "den": sum(per[c][view][k]["den"] for c in per)}
                     for k in SCORES} for view in ("full", "high_confidence")}
    for view in pooled.values():
        for v in view.values():
            v["wilson95"] = ps.wilson(v["num"], v["den"])
    info = {"system": system, "model": model, "ollama_version": ollama_version, "options": llm.OPTIONS,
            "small_max": item1a_v03.SMALL_MAX if system == "v0.3" else None, "commit": commit(),
            "started_utc": started.isoformat(timespec="seconds"),
            "reference": "reference_item1a_v03_heldout.csv (multi-model consensus)"}
    path = OUT / f"heldout_{system}_{model.replace(':', '-')}_{stamp}.json"
    path.write_text(json.dumps({"run": info, "pooled": pooled, "cases": per}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    print(path.name)
    for view, v in pooled.items():
        print(view, {k: f"{x['num']}/{x['den']}" for k, x in v.items()})


def mcnemar(b, c):
    n = b + c
    return None if not n else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def compare(p2, p3):
    loc, labels = reference()
    a, b = json.loads(open(p2, encoding="utf-8").read()), json.loads(open(p3, encoding="utf-8").read())
    out = {"v0.2": p2, "v0.3": p3}
    for view, keep_src in (("full", None), ("high_confidence", "high_confidence")):
        flag = {}
        for name, run_ in (("v0.2", a), ("v0.3", b)):
            s = set()
            for case in CASES:
                hits, _, _ = unit_hits({"case": case, "item1a_changes": run_["cases"][case]["item1a_changes"]}, loc)
                s |= set(hits)
            flag[name] = s
        units = [u for u in labels if keep_src is None or labels[u]["source"] == keep_src]
        boiler = [u for u in units if labels[u]["label"] == "boilerplate"]
        material = [u for u in units if labels[u]["label"].startswith("material")]
        only2 = sum(u in flag["v0.2"] and u not in flag["v0.3"] for u in boiler)
        only3 = sum(u in flag["v0.3"] and u not in flag["v0.2"] for u in boiler)
        hit2 = sum(u in flag["v0.2"] and u not in flag["v0.3"] for u in material)
        hit3 = sum(u in flag["v0.3"] and u not in flag["v0.2"] for u in material)
        out[view] = {"boilerplate_units": len(boiler),
                     "false_flag_only_v02": only2, "false_flag_only_v03": only3, "mcnemar_p_boilerplate": mcnemar(only2, only3),
                     "material_units": len(material),
                     "hit_only_v02": hit2, "hit_only_v03": hit3, "mcnemar_p_material": mcnemar(hit2, hit3),
                     "v02": a["pooled"][view], "v03": b["pooled"][view]}
    path = OUT / f"comparison_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("system", nargs="?", choices=["v0.2", "v0.3"])
    ap.add_argument("--model")
    ap.add_argument("--compare", nargs=2)
    a = ap.parse_args()
    compare(*a.compare) if a.compare else run(a.system, a.model)
