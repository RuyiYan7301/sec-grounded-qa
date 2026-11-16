"""Offline evaluation of the "diff_small" candidate on development data (docs/item1a-v0.3-plan.md, item 5).

    python -m secqa.evaluation.v03_item1a_small DIFF_RUN.json
    # writes results/dev/item1a_v03/diff_small_offline_<UTC>.json

Takes the "diff" run's per-candidate labels, turns to boilerplate every candidate that small_edit() marks for
K in {1..5}, rebuilds the packet and scores it with the frozen Part B Item 1A rules. No model call.
"""
import datetime
import json
import sys

from .. import config
from ..engine import item1a_changes as v02, item1a_v03
from ..evaluation.v2 import item1a as protocol
from .v03_item1a_dev import DEV, OUT, POOL
from .v2 import partb_score as ps

KS = (1, 2, 3, 4, 5)


def main(diff_run):
    run = json.loads(open(diff_run, encoding="utf-8").read())
    loc, labels = ps.load_item1a()
    res = {}
    for case, (t, y1, y2) in DEV.items():
        cands = run["cases"][case]["candidates"]
        f1, f2 = v02.target_10k(t, y1), v02.target_10k(t, y2)
        a = protocol.paragraphs(protocol.item1a_text(t, y1))
        b = protocol.paragraphs(protocol.item1a_text(t, y2))
        small = {}
        for n, c in enumerate(cands):
            i, j = c["earlier_index"], c["later_index"]
            earlier, later = (a[i] if i is not None else None), (b[j] if j is not None else None)
            if not c.get("model"):
                continue
            ctx = {"earlier_in_later": v02.where_else(earlier, b, exclude=j) if earlier else [],
                   "later_in_earlier": v02.where_else(later, a, exclude=i) if later else []}
            text, setup = item1a_v03.diff_input(earlier, later, ctx)
            if setup in ("pair", "moved"):
                words = item1a_v03.changed_words(text.split("\n\n", 1)[1])
                if not any(any(ch.isdigit() for ch in w) for w in words):
                    small[n] = len(words)
        res[case] = {}
        for k in KS:
            changes = []
            for n, c in enumerate(cands):
                lab = "boilerplate" if (n in small and small[n] <= k) else c.get("label", "")
                if not lab.startswith("material"):
                    continue
                x = {"label": lab}
                if c["earlier_index"] is not None and lab != "material_added":
                    x["earlier"] = v02.locator(f1["accession"], a, c["earlier_index"])
                if c["later_index"] is not None and lab != "material_removed":
                    x["later"] = v02.locator(f2["accession"], b, c["later_index"])
                changes.append(x)
            s = ps.score_item1a({"case": case, "item1a_changes": changes}, True, loc, labels)
            res[case][k] = {"score": {m: s[m] for m in POOL}, "turned_to_boilerplate": sum(1 for v in small.values() if v <= k)}
    pooled = {k: {m: {"num": sum(res[c][k]["score"][m]["num"] for c in res), "den": sum(res[c][k]["score"][m]["den"] for c in res)}
                  for m in POOL} for k in KS}
    out = {"diff_run": diff_run, "ks": KS, "pooled_4": pooled, "cases": res}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = OUT / f"diff_small_offline_{ts}.json"
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(path.name)
    for k in KS:
        print("K", k, {m: f"{v['num']}/{v['den']}" for m, v in pooled[k].items()})


if __name__ == "__main__":
    main(sys.argv[1])
