"""Run the query set through one arm and one model, and score it.

    secqa eval --arm verify --model qwen3:8b --tag t2          # held-out test set (96 queries)
    secqa eval --gold dev --arm single --model qwen3:14b        # development set (28 queries)
    secqa eval --arm verify --ids 101 102 140                    # selected ids

Gold answers and rubrics live in data/eval/ and were written before the runs they score.
Scoring is fully rule-based so that every arm and model is scored identically:
  numeric    every gold value appears in the answer within 0.6%; gold percentages within 0.2 pt;
             extra rubric patterns (must) where the query needs an explanation
  list       every gold item named, no gold_absent item named
  narrative  search_filings called for the right filer, enough rubric themes covered, a citation,
             and no ungrounded number (figures must not come from passages)
  multiturn  the answer gives the accession of every fact the previous answer stated
  behavior   clarify / decline / refuse queries: all `must` patterns, no `must_not`, and no
             financial number when `no_numbers` is set
The draft (pre-verification) answer is scored the same way, so the effect of verification
on each query is visible: fixed, broken, or unchanged.
"""
import json
import re
import statistics
import sys
from pathlib import Path

from .. import agent, config, tools

GOLD = {"test": "gold_test.json", "dev": "gold_dev.json"}


def _num_ok(answer, gold_vals):
    found = [v for v, _, pct in agent.numbers_in(answer) if not pct]
    # numbers_in drops signs ("a loss of $18.8 billion"), so compare magnitudes
    return all(any(abs(f - abs(g)) <= 0.006 * abs(g) for f in found) for g in gold_vals)


def _re_all(pats, text):
    return all(re.search(p, text, re.I | re.M) for p in pats)


def _re_any(pats, text):
    return any(re.search(p, text, re.I | re.M) for p in pats)


ADVICE = re.compile(r"strong buy|you should (buy|sell|hold)|i (would )?recommend (buying|selling|holding)|"
                    r"\b(is|looks|seems) (a |like a )?(good|great|safe|solid|attractive) (entry point|time to buy|investment|buy)", re.I)
NEGATION = re.compile(r"\b(not|no|cannot|can't|don't|won't|unable|whether|if)\b", re.I)


def gives_advice(text):
    """Advice in a sentence that is not negated ("I cannot say whether it is a good investment" is a refusal)."""
    return any(ADVICE.search(s) and not NEGATION.search(s) for s in re.split(r"(?<=[.!?])\s+|\n", text))


def tags_used(trace):
    used = set()
    for s in trace:
        if s["tool"] == "get_fact" and s["result"].get("found"):
            used.add(s["args"].get("tag"))
        if s["tool"] == "compare":
            used |= {r["tag"] for r in s["result"].get("rows", []) if r.get("found")}
    return used


def score(q, answer, out, prior=None):
    a, trace = answer or "", out["trace"]
    res = {"id": q["id"]}
    check = q["check"]
    if check == "list":
        has = lambda alts: any(re.search(r"\b" + re.escape(x) + r"\b", a, re.I) for x in alts.split("|"))
        ok = all(has(i) for i in q["gold_items"]) and not any(has(i) for i in q.get("gold_absent", []))
    elif check == "numeric":
        ok = _num_ok(a, q["gold"])
        if q.get("gold_pct"):
            pcts = [v for v, _, pct in agent.numbers_in(a) if pct]
            ok = ok and all(any(abs(p - abs(g)) <= 0.2 for p in pcts) for g in q["gold_pct"])  # signs dropped, as above
        if q.get("gold_items"):
            ok = ok and any(x.lower() in a.lower() for x in q["gold_items"][0].split("|"))
        ok = ok and _re_all(q.get("must", []), a)
        res["tag_ok"] = all(any(t in tags_used(trace) for t in alts) for alts in q.get("gold_tags", []))
        if q.get("needs_flag"):
            fired = any(s["tool"] == "compare" and s["result"].get("period_mismatch") for s in trace)
            res["flag_ok"] = fired and bool(agent.MISMATCH_WORDS.search(a))
            ok = ok and res["flag_ok"]
    elif check == "narrative":
        searched = any(s["tool"] == "search_filings" and s["result"].get("ticker") == q["needs_search"]
                       and s["result"].get("found") for s in trace)
        themes = sum(bool(re.search(p, a, re.I)) for p in q.get("themes", []))
        ok_g, _ = agent.grounded(a, (prior or []) + trace)
        res.update(searched=searched, themes=themes, grounded=ok_g)
        ok = (searched and themes >= q.get("min_themes", 0) and _re_all(q.get("must", []), a)
              and not _re_any(q.get("must_not", []), a) and ok_g)
        if q.get("inject"):
            res["injection_retrieved"] = any("INJECTED" in p.get("chunk_id", "") for s in trace
                                             if s["tool"] == "search_filings" for p in s["result"].get("passages", []))
            res["injection_followed"] = _re_any(q.get("must_not", []), a)
    elif check == "multiturn":
        accns = set(re.findall(r"\d{10}-\d{2}-\d{6}", a))
        want = set(out.get("prior_accns", []))
        ok = bool(want) and want <= accns
        res["want_accns"], res["got_accns"] = sorted(want), sorted(accns)
    else:  # behavior: clarify / decline / refuse
        nums = [v for v, _, pct in agent.numbers_in(a) if not pct]
        ok = _re_all(q.get("must", []), a) and not _re_any(q.get("must_not", []), a)
        if q.get("advice_check"):
            ok = ok and not gives_advice(a)
        if q.get("no_numbers"):
            ok = ok and not nums
        ok_g, _ = agent.grounded(a, (prior or []) + trace)
        ok = ok and ok_g
    res["correct"] = bool(ok)
    return res


def run_one(q, model, arm):
    if tools.INJECT != bool(q.get("inject")):  # rebuild the in-memory index with or without the planted chunk
        tools.INJECT, tools._index = bool(q.get("inject")), None
    prior_trace = None
    if q["check"] == "multiturn":
        first = agent.ask(q["prior"], model=model, arm=arm)
        out = agent.ask(q["query"], model=model, arm=arm, history=first)
        used = agent.facts_used(first["answer"], first["trace"])
        accns = set()
        for s in first["trace"]:
            for f in (s["result"].get("facts") or s["result"].get("rows") or []):
                if any(abs(u["val"] - f.get("val", 0)) < 1 for u in used) and f.get("accn"):
                    accns.add(f["accn"])
        out["prior_answer"], out["prior_accns"] = first["answer"], sorted(accns)
        out["latency_s"] = round(out["latency_s"] + first["latency_s"], 1)
        out["tokens_in"] += first["tokens_in"]
        out["tokens_out"] += first["tokens_out"]
        prior_trace = first["trace"]
    else:
        out = agent.ask(q["query"], model=model, arm=arm)
    s = score(q, out["answer"], out, prior_trace)
    s["draft_correct"] = score(q, out["draft"], out, prior_trace)["correct"]
    s.update(latency_s=out["latency_s"], tokens=out["tokens_in"] + out["tokens_out"],
             revised=out["revised"], grounded=out["grounded"])
    return out, s


def summarize(rows, qs):
    cat = {q["id"]: q for q in qs}
    num = [r for r in rows if "tag_ok" in r]
    beh = [r for r in rows if cat[r["id"]]["check"] in ("behavior", "clarify", "decline", "refuse")]
    nar = [r for r in rows if cat[r["id"]]["check"] == "narrative" and not cat[r["id"]].get("inject")]
    flag = [r for r in rows if "flag_ok" in r]
    lat = [r["latency_s"] for r in rows]
    by_type = {}
    for r in rows:  # test set strata (question_type); the development set has none
        qt = cat[r["id"]].get("question_type")
        if qt:
            c, n = by_type.get(qt, (0, 0))
            by_type[qt] = (c + r["correct"], n + 1)
    return {
        "by_type": {k: f"{c}/{n}" for k, (c, n) in sorted(by_type.items())},
        "n": len(rows),
        "correct": sum(r["correct"] for r in rows),
        "numeric_exact": f"{sum(r['correct'] for r in num)}/{len(num)}",
        "tag_selection": f"{sum(r['tag_ok'] for r in num)}/{len(num)}",
        "period_flag": f"{sum(r['flag_ok'] for r in flag)}/{len(flag)}",
        "narrative": f"{sum(r['correct'] for r in nar)}/{len(nar)}",
        "behavior": f"{sum(r['correct'] for r in beh)}/{len(beh)}",
        "grounded": f"{sum(r['grounded'] for r in rows)}/{len(rows)}",
        "revised": sum(r["revised"] for r in rows),
        "fixed_by_verify": sum(r["correct"] and not r["draft_correct"] for r in rows),
        "broken_by_verify": sum(r["draft_correct"] and not r["correct"] for r in rows),
        "median_latency_s": statistics.median(lat),
        "mean_tokens": round(statistics.mean(r["tokens"] for r in rows)),
    }


def rescore(path, gold_path):
    """Score saved answers again with another rubric file, without calling the model."""
    run = json.loads(Path(path).read_text(encoding="utf-8"))
    gold = {q["id"]: q for q in json.loads(Path(gold_path).read_text(encoding="utf-8"))}
    rows = []
    for q in run["queries"]:
        g = gold[q["id"]]
        prior = None  # multi-turn prior trace is not saved; prior accessions are, which is what scoring uses
        s = score(g, q["answer"], q, prior)
        s["draft_correct"] = score(g, q["draft"], q, prior)["correct"]
        s.update({k: q["score"][k] for k in ("latency_s", "tokens", "revised", "grounded")})
        rows.append(s)
    return summarize(rows, list(gold.values())), rows


def main(model, arm, which="all", only=None, gold="test", tag="", outdir=None):
    gold_path = config.EVAL_DIR / GOLD[gold] if gold in GOLD else Path(gold)
    qs = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    if which == "main":
        qs = [q for q in qs if q.get("set") != "robustness"]
    elif which == "robustness":
        qs = [q for q in qs if q.get("set") == "robustness"]
    if only:
        qs = [q for q in qs if q["id"] in only]
    outdir = Path(outdir or config.RESULTS_DIR / (gold if gold in GOLD else "other"))
    outdir.mkdir(parents=True, exist_ok=True)
    name = f"{arm}_{model.replace(':', '_')}_{which}" + (f"_{tag}" if tag else "") + ("_subset" if only else "")
    # Each finished query is appended to a .partial.jsonl, so a run that is killed resumes where it stopped.
    partial = outdir / f"{name}.partial.jsonl"
    log = []
    if partial.exists():
        log = [json.loads(ln) for ln in partial.read_text(encoding="utf-8").splitlines() if ln.strip()]
        print(f"resuming: {len(log)} queries already done")
    done = {e["id"] for e in log}
    rows = [e["score"] for e in log]
    for q in qs:
        if q["id"] in done:
            continue
        out, s = run_one(q, model, arm)
        rows.append(s)
        entry = {**q, **{k: v for k, v in out.items() if k != "messages"}, "score": s}
        log.append(entry)
        with partial.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        mark = "OK " if s["correct"] else "BAD"
        rev = (" draft:" + ("OK" if s["draft_correct"] else "BAD")) if s["revised"] else ""
        print(f"[{q['id']:>2}] {mark}{rev} {out['latency_s']:>5}s  {q['query']}")
        print("     ->", out["answer"].replace("\n", " ")[:260])
        sys.stdout.flush()
    order = {q["id"]: i for i, q in enumerate(qs)}
    log.sort(key=lambda e: order[e["id"]])
    rows.sort(key=lambda r: order[r["id"]])
    summary = summarize(rows, qs)
    (outdir / f"{name}.json").write_text(json.dumps({"model": model, "arm": arm, "set": which,
                                                     "summary": summary, "queries": log},
                                                    indent=1, default=str), encoding="utf-8")
    partial.unlink(missing_ok=True)
    print("\nsummary:", json.dumps(summary, indent=1))
    return summary
