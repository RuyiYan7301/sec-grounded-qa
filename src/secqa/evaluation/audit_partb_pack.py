"""Review packs for the post-freeze Part B check (docs/partB-scoring.md, "Post-freeze real-output check").

    python -m secqa.evaluation.audit_partb_pack PACKET.json [PACKET.json ...]
    # writes results/test/audit_partb/<case>/pack.md and blank forms numeric.csv, revisions.csv, item1a.csv

Each pack shows, for one test case, the gold and the packet side by side, item by item, with no scorer
output: numeric items per gold metric, revision checks per gold control, and every Item 1A prediction with
the text of the paragraphs its locators point to (frozen segmentation) next to the gold unit table. The
reviewer records item verdicts; audit_partb_agree.py turns them into the same scores and compares them with
the scorer. The AMD micro-case has revision checks only.
"""
import csv
import json
import sys

from .. import config
from .v2 import item1a as protocol
from .v2 import partb_score as ps

OUT = config.REPO_ROOT / "results" / "test" / "audit_partb"
NUM_FORM = ("metric", "gold_label", "reported", "status_matches_gold", "value_correct", "evidence_ok",
            "scope_warning_ok", "note")
REV_FORM = ("id", "gold_label", "reported", "status_ok", "as_presented_ok", "first_reported_ok", "cause_ok", "note")
I1A_FORM = ("pred_no", "unit_id", "material_hit", "subtype_ok", "locator_complete", "note")


def j(x):
    return json.dumps(x, ensure_ascii=False)


def short(t, n=500):
    t = " ".join((t or "").split())
    return t if len(t) <= n else t[:n] + " [...]"


def build(packet):
    case = packet["case"]
    g, (loc, labels) = ps.load_gold(), ps.load_item1a()
    d = OUT / case
    d.mkdir(parents=True, exist_ok=True)
    md = [f"# Part B review pack: {case}\n\nPacket metadata: {j({k: packet.get(k) for k in ('case', 'ticker', 'from_fy', 'to_fy', 'value_policy', 'target_filing')})}\n\n"
          f"Gold target filing: {j(g['cases'].get(case, {}).get('target'))}\n"]
    gitems = g["cases"].get(case, {}).get("items", {})
    if gitems:
        by_id = {}
        for it in packet.get("numeric_changes") or []:
            by_id.setdefault(it.get("id"), []).append(it)
        md.append("\n## 1. Numeric changes (one block per gold metric)\n")
        for m, git in gitems.items():
            gv = {k: git.get(k) for k in ("label", "kind", "v1", "v2", "absolute_change", "percent_change", "pp_change",
                                         "change_basis", "flags", "outcomes") if k in git}
            facts = [{k: f.get(k) for k in ("fy", "role", "component_of", "concept", "value", "unit", "period_end",
                                            "reported_in_accession", "filed")} for f in git["facts"]]
            md.append(f"\n### {m}\n\nGold: {j(gv)}\n\nGold facts:\n" + "".join(f"- {j(f)}\n" for f in facts))
            items = by_id.pop(git["id"], [])
            md.append(f"\nPacket items with id `{git['id']}`: {len(items)}\n" +
                      "".join(f"- {j(x)}\n" for x in items))
        if by_id:
            md.append("\n### Packet items whose id is not a gold id\n" + "".join(f"- {j(x)}\n" for v in by_id.values() for x in v))
        with open(d / "numeric.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(NUM_FORM)
            for m, git in gitems.items():
                w.writerow([m, git["label"]] + [""] * (len(NUM_FORM) - 2))
    ctr = g["controls"].get(case, {})
    if ctr:
        by_id = {}
        for rc in packet.get("revision_checks") or []:
            by_id.setdefault(rc.get("id"), []).append(rc)
        md.append("\n## 2. Revision checks (one block per gold control)\n")
        for cid, gr in ctr.items():
            gv = {k: gr.get(k) for k in ("label", "concept", "value", "unit", "period_end", "reported_in_accession",
                                         "first_reported")}
            md.append(f"\n### {cid}\n\nGold: {j(gv)}\n\nPacket items: " +
                      ("".join(f"\n- {j(x)}" for x in by_id.pop(cid, [])) or "none") + "\n")
        if by_id:
            md.append("\n### Packet revision checks whose id is not a gold id\n" + "".join(f"- {j(x)}\n" for v in by_id.values() for x in v))
        with open(d / "revisions.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(REV_FORM)
            for cid, gr in ctr.items():
                w.writerow([cid, gr["label"]] + [""] * (len(REV_FORM) - 2))
    lc = loc["cases"].get(case)
    if lc and packet.get("item1a_changes") is not None:
        paras = {"earlier": protocol.paragraphs(protocol.item1a_text(packet["ticker"], int(packet["from_fy"][2:]))),
                 "later": protocol.paragraphs(protocol.item1a_text(packet["ticker"], int(packet["to_fy"][2:])))}
        md.append("\n## 3. Item 1A\n\nGold units (id, alignment type, gold label, earlier locator, later locator, quote):\n\n"
                  "| unit | type | gold label | earlier (accession / paragraph) | later (accession / paragraph) | quote |\n|---|---|---|---|---|---|\n")
        for u in lc["units"]:
            e, lt = u.get("earlier"), u.get("later")
            q = short((lt or e or {}).get("quote"), 90).replace("|", "/")
            md.append(f"| {u['id']} | {u['type']} | {labels.get(u['id'], {}).get('label', '?')} | "
                      f"{(e['accession'] + ' / ' + str(e['paragraph_index'])) if e else '-'} | "
                      f"{(lt['accession'] + ' / ' + str(lt['paragraph_index'])) if lt else '-'} | {q} |\n")
        md.append("\nPredictions (packet order):\n")
        preds = packet["item1a_changes"]
        for n, p in enumerate(preds, 1):
            md.append(f"\n### P{n:03d}: {p.get('label')}\n\nSummary: {p.get('summary')}\n")
            for side in ("earlier", "later"):
                lx = p.get(side)
                if isinstance(lx, dict):
                    i = lx.get("paragraph_index")
                    txt = paras[side][i] if isinstance(i, int) and 0 <= i < len(paras[side]) else "(no such paragraph)"
                    md.append(f"\n{side} locator: {lx.get('accession')} / paragraph {i}\n\n> {short(txt)}\n")
        with open(d / "item1a.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(I1A_FORM)
            for n in range(1, len(preds) + 1):
                w.writerow([f"P{n:03d}"] + [""] * (len(I1A_FORM) - 1))
    (d / "pack.md").write_text("".join(md), encoding="utf-8", newline="\n")
    print(case, (d / "pack.md").stat().st_size, "bytes")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        build(json.loads(open(p, encoding="utf-8").read()))
