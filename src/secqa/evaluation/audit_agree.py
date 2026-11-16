"""Scorer-hand agreement on the Part A audit (written before the hand judging; see audit_pack.py).

    python -m secqa.evaluation.audit_agree [FORM.csv [OUT.json]]
    # reads results/test/audit/<FORM> (default form.csv) and key_sealed.json, writes <OUT> (default agreement.json)

Per system: on final_correct, scorer false positives (scorer right, hand wrong) and false negatives (scorer
wrong, hand right), as counts and as rates with Wilson 95% intervals, over all audited records and over
the records the scorer marked right / wrong; the same agreement for each structured score where both give
a y/n verdict (na on either side is left out). The automated results are not changed and no corrected
score for the 160 items is computed from this.
"""
import csv
import hashlib
import json
import sys

from .. import config
from .v2.partb_score import wilson

D = config.REPO_ROOT / "results" / "test" / "audit"


def yn(v):
    v = (v or "").strip().lower()
    return True if v in ("y", "yes", "1", "true") else False if v in ("n", "no", "0", "false") else None


def scorer_view(s):
    concept = {"canonical": True, "qualified_alternative": True, "incorrect": False}.get(s["concept"])
    return {"final_correct": s["final_correct"], "evidence_complete": s["evidence_complete"], "concept_ok": concept,
            "period_ok": s["period_ok"], "calculation_ok": s["calculation_ok"],
            "refusal_appropriate": s["appropriate_refusal"] if s["path"] in ("refusal", "not_meaningful") else None}


def rate(x, n):
    return {"num": x, "den": n, "value": round(x / n, 4) if n else None, "wilson95": wilson(x, n)}


def main(form_name="form.csv", out_name="agreement.json"):
    key_text = (D / "key_sealed.json").read_text(encoding="utf-8")
    pack = json.loads((D / "pack.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(key_text.encode("utf-8")).hexdigest() == pack["key_sha256"], "key changed after packing"
    k = json.loads(key_text)
    runs = {s: {r["id"]: r for r in json.loads(open(p, encoding="utf-8").read())["items"]} for s, p in k["runs"].items()}
    with open(D / form_name, encoding="utf-8") as f:
        form = {r["audit_id"]: r for r in csv.DictReader(f)}
    missing = [a for a in k["key"] if yn(form.get(a, {}).get("final_correct")) is None]
    assert not missing, f"final_correct not filled in for {missing}"
    out = {}
    for system in ("v0.2", "v0.1"):
        rows = [(a, scorer_view(runs[system][m["item_id"]]["score"]), form[a]) for a, m in k["key"].items()
                if m["system"] == system]
        fp = [a for a, s, h in rows if s["final_correct"] and not yn(h["final_correct"])]
        fn = [a for a, s, h in rows if not s["final_correct"] and yn(h["final_correct"])]
        pos = sum(s["final_correct"] for _, s, _ in rows)
        per = {}
        for f in ("evidence_complete", "concept_ok", "period_ok", "calculation_ok", "refusal_appropriate"):
            pairs = [(bool(s[f]), yn(h[f])) for _, s, h in rows if s[f] is not None and yn(h[f]) is not None]
            per[f] = {"compared": len(pairs), "agree": sum(x == y for x, y in pairs),
                      "scorer_yes_hand_no": sum(x and not y for x, y in pairs),
                      "scorer_no_hand_yes": sum(y and not x for x, y in pairs)}
        out[system] = {"n": len(rows), "scorer_final_correct": pos,
                       "hand_final_correct": sum(bool(yn(h["final_correct"])) for _, _, h in rows),
                       "final_correct_disagreement": rate(len(fp) + len(fn), len(rows)),
                       "scorer_false_positive": rate(len(fp), len(rows)), "scorer_false_negative": rate(len(fn), len(rows)),
                       "false_positive_among_scorer_right": rate(len(fp), pos),
                       "false_negative_among_scorer_wrong": rate(len(fn), len(rows) - pos),
                       "fp_ids": sorted(fp), "fn_ids": sorted(fn), "per_score": per}
    (D / out_name).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
