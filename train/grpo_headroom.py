"""v0.4 step 2, before GRPO: is there anything for GRPO to learn from on its prompts?

    cd train
    C:/Users/Admin/venvs/secqa-train/Scripts/python grpo_headroom.py --sft runs/sft_hint_r16_lr2e-4/checkpoint-480 --n 200

GRPO learns only from groups whose rollouts get different rewards (the advantage is reward minus the group
mean; a group with equal rewards gives zero gradient). This samples `group` completions per prompt from
the SFT checkpoint with TRL's GRPO sampling (temperature 1.0, top_p 1.0, top_k 0, thinking off, short
prompt with company hint), scores them with the GRPO reward (train/grpo.py: Rewarder), and reports the
share of prompts with mixed rewards. Prompts: a random sample (seed 2614) of the GRPO prompt set, which is
training data; no validation or test item is used.
Writes results/v0.4/planner/grpo_headroom_<tag>.json.
"""
import argparse
import json
import random
import time
from collections import Counter

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import END, MODEL, ROOT, load_items, prompt_text, system_for
from grpo import DATA, Rewarder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--batch", type=int, default=4, help="prompts per generate call")
    ap.add_argument("--tag", default="sft_hint_ck480")
    a = ap.parse_args()
    items = load_items(DATA)
    idx = sorted(random.Random(2614).sample(range(len(items)), a.n))
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, str(ROOT / a.sft)).merge_and_unload().eval()
    rew = Rewarder(items)
    torch.manual_seed(0)
    rows, t0 = [], time.perf_counter()
    for b in range(0, len(idx), a.batch):
        chunk = idx[b:b + a.batch]
        prompts = [prompt_text(tok, system_for("short", items[i]["question"]), items[i]["question"]) for i in chunk]
        enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            g = model.generate(**enc, do_sample=True, temperature=1.0, top_p=1.0, top_k=0, max_new_tokens=256,
                               num_return_sequences=a.group, pad_token_id=tok.pad_token_id)
        texts = [tok.decode(r, skip_special_tokens=False).split(END)[0].strip() for r in g[:, enc["input_ids"].shape[1]:]]
        for k, i in enumerate(chunk):
            outs = [rew.one(items[i], t) for t in texts[k * a.group:(k + 1) * a.group]]
            rs = [r for r, _ in outs]
            rows.append({"id": items[i]["id"], "gold_outcome": items[i]["gold_outcome"],
                         "intent": (items[i].get("gold_plan") or {}).get("intent"),
                         "rewards": rs, "why": [w for _, w in outs], "mixed": len(set(rs)) > 1,
                         "distinct_texts": len(set(texts[k * a.group:(k + 1) * a.group]))})
        print(f"{len(rows)}/{len(idx)} mixed so far {sum(r['mixed'] for r in rows)}", flush=True)
    n = len(rows)
    allr = [x for r in rows for x in r["rewards"]]
    by = {}
    for r in rows:
        k = r["intent"] or r["gold_outcome"]
        by.setdefault(k, [0, 0, 0.0])
        by[k][0] += r["mixed"]
        by[k][1] += 1
        by[k][2] += sum(r["rewards"]) / len(r["rewards"])
    summary = {"prompts": n, "group": a.group, "mixed_groups": sum(r["mixed"] for r in rows),
               "mixed_share": round(sum(r["mixed"] for r in rows) / n, 3),
               "all_correct_groups": sum(all(x == 1 for x in r["rewards"]) for r in rows),
               "mean_reward": round(sum(allr) / len(allr), 3),
               "rollout_outcomes": dict(Counter(w for r in rows for w in r["why"])),
               "median_distinct_texts": sorted(r["distinct_texts"] for r in rows)[n // 2],
               "by_kind_mixed_of_n_meanreward": {k: [v[0], v[1], round(v[2] / v[1], 3)] for k, v in sorted(by.items())},
               "minutes": round((time.perf_counter() - t0) / 60, 1),
               "gpu_peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
    out = ROOT / "results" / "v0.4" / "planner" / f"grpo_headroom_{a.tag}.json"
    out.write_text(json.dumps({"args": vars(a), "summary": summary, "rows": rows}, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
