"""v0.4 step 2: plan with a local Qwen3 model (base or + LoRA adapter) and check the plans by execution.

    C:/Users/Admin/venvs/secqa-train/Scripts/python train/eval_planner.py --data data/train/v0.4/sft_val.json \
        --adapter runs/sft_r16_lr2e-4/checkpoint-240 --prompt short --out results/v0.4/planner/val_sft_ep1.json

Greedy decoding, thinking off. A plan that fails the v0.4 schema gets the same one repair call as the frozen
8B planner (plan.repair_prompt). Valid plans are executed by the frozen executor, and execution correctness
is the frozen check (run_v2.execution_correct). Reports plan validity, plan exact match against the
generator's gold plan, execution correct, refusal rate on answerable items, latency, GPU peak memory.
Final correct (with the 8B renderer and scorer) is computed separately for the test runs.
"""
import argparse
import json
import time
from collections import Counter

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import END, MODEL, ROOT, load_items, prompt_text, system_text

from secqa import config, universe  # noqa: E402  (common.py puts src on the path)


def target_of(it):
    from secqa.train.build_data import target
    return it.get("target_plan") or target(it)


def same_plan(p, t):
    if p is None:
        return False
    if "refuse" in t:
        return p.get("refuse") == t["refuse"]
    return all(p.get(k) == t.get(k) for k in ("intent", "metric", "companies", "periods"))


def generate(model, tok, prompts, max_new=256, batch=16):
    outs, times = [], []
    for i in range(0, len(prompts), batch):
        chunk = prompts[i:i + batch]
        enc = tok(chunk, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        t0 = time.perf_counter()
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=max_new, do_sample=False, temperature=None, top_p=None,
                               top_k=None, pad_token_id=tok.pad_token_id)
        dt = (time.perf_counter() - t0) / len(chunk)
        for row in g[:, enc["input_ids"].shape[1]:]:
            outs.append(tok.decode(row, skip_special_tokens=False).split(END)[0].strip())
            times.append(dt)
    return outs, times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--prompt", choices=["short", "long"], default="short")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--batch", type=int, default=16)
    a = ap.parse_args()
    universe.activate()
    from secqa.engine import execute, llm, plan
    from secqa.evaluation.run_v2 import execution_correct
    from secqa.evaluation.v4.run_2b import Stores
    import yaml

    items = load_items(ROOT / a.data)[:a.limit]
    system = system_text(a.prompt)
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda")
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(ROOT / a.adapter))
    model.eval()
    torch.cuda.reset_peak_memory_stats()
    raw, secs = generate(model, tok, [prompt_text(tok, system, it["question"]) for it in items], batch=a.batch)
    plans, status, repaired = [], [], []
    need = []
    for i, (it, text) in enumerate(zip(items, raw)):
        p = llm.parse_json(text)
        errs = plan.validate(p) if p is not None else ["not JSON"]
        plans.append(p if not errs else None)
        status.append("valid" if not errs else "invalid")
        repaired.append(False)
        if errs:
            need.append((i, plan.repair_prompt(it["question"], text, errs)))
    if need:                                         # one repair call, as the frozen planner
        rtexts, rsecs = generate(model, tok, [prompt_text(tok, system, r) for _, r in need], batch=a.batch)
        for (i, _), text, s in zip(need, rtexts, rsecs):
            p = llm.parse_json(text)
            errs = plan.validate(p) if p is not None else ["not JSON"]
            secs[i] += s
            if not errs:
                plans[i], status[i], repaired[i] = p, "valid", True
            raw[i] = raw[i] + "\n---repair---\n" + text
    gpu_peak = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    del model
    torch.cuda.empty_cache()
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    stores = Stores()
    rows = []
    for it, text, p, st, rep, s in zip(items, raw, plans, status, repaired, secs):
        if p is None:
            r = {"outcome": "invalid_plan", "warnings": [], "evidence": []}
        else:
            src = None if "refuse" in p else stores.source(p.get("companies") or [])
            r = execute.execute(p, it["question"], src, o)
        t = target_of(it)
        rows.append({"id": it["id"], "question": it["question"], "raw": text, "plan": p, "status": st,
                     "repaired": rep, "target_plan": t, "plan_match": same_plan(p, t),
                     "outcome": r.get("outcome"), "execution_correct": execution_correct(it, r),
                     "seconds": round(s, 3)})
    answerable = [r for r, it in zip(rows, items) if it["gold_outcome"] in ("answer", "not_meaningful", "ambiguous_year")]
    refusal_outcomes = {"out_of_ontology", "unsupported", "out_of_range", "unsupported_operation", "invalid_plan"}
    n = len(rows)
    summary = {"items": n, "plan_valid": sum(r["status"] == "valid" for r in rows),
               "repaired": sum(r["repaired"] for r in rows),
               "plan_match": sum(r["plan_match"] for r in rows),
               "execution_correct": sum(r["execution_correct"] for r in rows),
               "answerable": len(answerable),
               "refused_answerable": sum(r["outcome"] in refusal_outcomes for r in answerable),
               "median_seconds_per_plan_batched": sorted(secs)[n // 2], "gpu_peak_gb": gpu_peak,
               "by_kind": {k: [sum(r["execution_correct"] for r, it in zip(rows, items) if kind(it) == k),
                               sum(1 for it in items if kind(it) == k)] for k in sorted({kind(it) for it in items})}}
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"args": vars(a), "summary": summary, "items": rows}, indent=1, default=str),
                   encoding="utf-8")
    print(json.dumps(summary, indent=1))


def kind(it):
    return (it.get("gold_plan") or {}).get("intent") or it["gold_outcome"]


if __name__ == "__main__":
    main()
