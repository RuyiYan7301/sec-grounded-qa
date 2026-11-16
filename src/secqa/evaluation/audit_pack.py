"""Blind pack for the post-freeze Part A audit (docs/benchmark-v0.2.md, "External check").

    python -m secqa.evaluation.audit_pack V02_RUN V01_RUN
    # writes results/test/audit/pack.json, pack.md, form.csv and key_sealed.json

The 80 records are the test-run outputs of both systems on the 40 noise-subset questions (fixed before any
run). They are shuffled with a fixed seed and given audit ids A01..A80. The pack shows, per record, the
question, the gold (outcome, result, gold facts, required warnings, tolerance), the answer and the evidence
the system cited, in one common format. It shows no system name, no plan, no scorer output. The key
(audit id -> system, item id) is written to key_sealed.json; its sha256 is printed in the pack so the key
can be committed after the judging without being changed. The audit measures scorer-hand agreement only;
the automated results are kept as they are and no corrected score is computed from it.
"""
import csv
import hashlib
import json
import random
import sys

from .. import config

SEED = 8080
OUT = config.REPO_ROOT / "results" / "test" / "audit"
EV_KEYS = ("ticker", "concept", "period", "value", "unit", "period_end", "accession")
FORM = ("audit_id", "final_correct", "refusal_appropriate", "evidence_complete", "concept_ok", "period_ok",
        "calculation_ok", "warnings_ok", "note")


def v02_evidence(row):
    return [{"ticker": e.get("ticker"), "concept": e.get("concept"), "period": e.get("fy"), "value": e.get("value"),
             "unit": e.get("unit"), "period_end": e.get("period_end"), "accession": e.get("accession")}
            for e in row["execution"].get("evidence", [])]


def v01_evidence(row):
    return [{k: e.get(k) for k in EV_KEYS} for e in row["record"]["evidence"]]


def gold_view(it):
    return {"gold_outcome": it["gold_outcome"], "gold_result": it["gold_result"],
            "gold_facts": [{k: c.get(k) for k in ("ticker", "concept", "period", "value", "unit", "period_end", "use")}
                           for c in it.get("gold_cells", [])],
            "required_warnings": it["required_warnings"], "tolerance": it.get("tolerance")}


def main(v02_path, v01_path):
    ids = json.loads((config.EVAL_DIR / "v0.2" / "noise_subset.json").read_text(encoding="utf-8"))["ids"]
    gold = {it["id"]: it for it in json.loads((config.EVAL_DIR / "v0.2" / "qa_test.json").read_text(encoding="utf-8"))}
    a = {r["id"]: r for r in json.loads(open(v02_path, encoding="utf-8").read())["items"]}
    b = {r["id"]: r for r in json.loads(open(v01_path, encoding="utf-8").read())["items"]}
    recs = [("v0.2", i, a[i]["render"]["answer"], v02_evidence(a[i])) for i in ids] + \
           [("v0.1", i, b[i]["answer"], v01_evidence(b[i])) for i in ids]
    random.Random(SEED).shuffle(recs)
    key, pack = {}, []
    for n, (system, i, answer, ev) in enumerate(recs, 1):
        aid = f"A{n:02d}"
        key[aid] = {"system": system, "item_id": i}
        pack.append({"audit_id": aid, "question": gold[i]["question"], "gold": gold_view(gold[i]),
                     "answer": answer, "evidence": ev})
    OUT.mkdir(parents=True, exist_ok=True)
    key_text = json.dumps({"seed": SEED, "runs": {"v0.2": v02_path, "v0.1": v01_path}, "key": key}, indent=1) + "\n"
    (OUT / "key_sealed.json").write_text(key_text, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(key_text.encode("utf-8")).hexdigest()
    (OUT / "pack.json").write_text(json.dumps({"key_sha256": sha, "records": pack}, indent=1) + "\n",
                                   encoding="utf-8", newline="\n")
    md = [f"# Part A audit pack (80 records, blind)\n\nKey sha256: `{sha}`. Do not open key_sealed.json before "
          "form.csv is complete.\n\nJudge each record against the gold: is the answer right for the person who "
          "asked (number, direction, years, required warnings; or a refusal for the right reason), and is the "
          "cited evidence complete, the right concept, the right period, and the calculation right? Write y, "
          "n or na in form.csv.\n"]
    for p in pack:
        g = p["gold"]
        md.append(f"\n---\n\n## {p['audit_id']}\n\n**Question:** {p['question']}\n\n"
                  f"**Gold:** outcome `{g['gold_outcome']}`, result `{json.dumps(g['gold_result'])}`, "
                  f"required warnings `{g['required_warnings']}`, tolerance `{json.dumps(g['tolerance'])}`\n\n"
                  "Gold facts:\n" + "".join(f"- {json.dumps(c)}\n" for c in g["gold_facts"]) +
                  f"\n**Answer:**\n\n> " + (p["answer"] or "(empty)").strip().replace("\n", "\n> ") + "\n\n"
                  f"**Evidence cited ({len(p['evidence'])}):**\n" +
                  "".join(f"- {json.dumps(e)}\n" for e in p["evidence"][:25]) +
                  (f"- ... {len(p['evidence']) - 25} more in pack.json\n" if len(p["evidence"]) > 25 else ""))
    (OUT / "pack.md").write_text("".join(md), encoding="utf-8", newline="\n")
    with open(OUT / "form.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FORM)
        for p in pack:
            w.writerow([p["audit_id"]] + [""] * (len(FORM) - 1))
    print(len(pack), "records; key sha256", sha)


if __name__ == "__main__":
    main(*sys.argv[1:3])
