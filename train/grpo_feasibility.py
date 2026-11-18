"""v0.4 step 2 feasibility gate (docs/v0.4-plan.md section 3b): can GRPO on Qwen3-1.7B + LoRA run on this
machine (RTX 5070 12 GB, 16 GB RAM), and how fast?

    C:/Users/Admin/venvs/secqa-train/Scripts/python train/grpo_feasibility.py --steps 50 --group 8 --prompt long

Dummy task: questions are made-up strings (no benchmark item is used); reward is 1 if the completion parses
as a JSON object, else 0. Only memory and speed are measured, never accuracy. The `long` prompt is the
v0.4 planner prompt (about 2.6k tokens), `short` is a one-line instruction (what a trained planner could
use). Writes results/v0.4/feasibility/grpo_<prompt>_g<group>.json.
"""
import argparse
import json
import random
import threading
import time
from pathlib import Path

import psutil
import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import TrainerCallback
from trl import GRPOConfig, GRPOTrainer

ROOT = Path(__file__).resolve().parents[1]
MODEL = "C:/Users/Admin/models/Qwen3-1.7B"
LONG = (ROOT / "data" / "eval" / "v0.4" / "planner_prompt_v04.txt").read_text(encoding="utf-8")
SHORT = "Return the typed plan for the question as one JSON object."
WORDS = ["revenue", "net income", "inventory", "goodwill", "R&D", "operating income", "capex", "diluted EPS"]
COS = ["Amgen", "Pfizer", "Boeing", "Caterpillar", "Netflix", "PepsiCo", "Chevron", "Walmart"]


def dummy(n, system, seed=0):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        q = f"What was {rng.choice(COS)}'s {rng.choice(WORDS)} in fiscal {rng.randint(2019, 2025)}?"
        rows.append({"prompt": [{"role": "system", "content": system}, {"role": "user", "content": q}]})
    return Dataset.from_list(rows)


def reward_json(completions, **_):
    out = []
    for c in completions:
        text = c[0]["content"] if isinstance(c, list) else c
        try:
            out.append(1.0 if isinstance(json.loads(text.strip().strip("`").removeprefix("json")), dict) else 0.0)
        except ValueError:
            out.append(0.0)
    return out


class Peak:
    def __init__(self):
        self.rss, self.sys_used, self.stop = 0, 0, False
        self.t = threading.Thread(target=self.loop, daemon=True)

    def loop(self):
        p = psutil.Process()
        while not self.stop:
            self.rss = max(self.rss, p.memory_info().rss)
            vm = psutil.virtual_memory()
            self.sys_used = max(self.sys_used, vm.total - vm.available)
            time.sleep(0.5)


class StepTimer(TrainerCallback):
    def __init__(self):
        self.times, self.t0 = [], None

    def on_step_begin(self, *a, **k):
        self.t0 = time.perf_counter()

    def on_step_end(self, *a, **k):
        self.times.append(time.perf_counter() - self.t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--prompt", choices=["long", "short"], default="long")
    ap.add_argument("--max-completion", type=int, default=384)
    a = ap.parse_args()
    peak = Peak()
    peak.t.start()
    torch.cuda.reset_peak_memory_stats()
    cfg = GRPOConfig(
        output_dir=str(ROOT / "results" / "v0.4" / "feasibility" / "tmp"), max_steps=a.steps,
        per_device_train_batch_size=a.group, num_generations=a.group, gradient_accumulation_steps=1,
        max_completion_length=a.max_completion, temperature=1.0, learning_rate=1e-5, beta=0.04, bf16=True,
        gradient_checkpointing=True, logging_steps=5, save_strategy="no", report_to="none",
        chat_template_kwargs={"enable_thinking": False},
    )
    timer = StepTimer()
    trainer = GRPOTrainer(
        model=MODEL, reward_funcs=reward_json, args=cfg,
        train_dataset=dummy(a.steps * a.group, LONG if a.prompt == "long" else SHORT),
        peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                               target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]),
        callbacks=[timer],
    )
    t0 = time.perf_counter()
    trainer.train()
    peak.stop = True
    st = sorted(timer.times[2:]) or timer.times      # first steps include warm-up
    out = {"prompt": a.prompt, "group": a.group, "steps": a.steps, "max_completion": a.max_completion,
           "seconds_total": round(time.perf_counter() - t0, 1),
           "sec_per_step_median": round(st[len(st) // 2], 2),
           "gpu_peak_allocated_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
           "gpu_peak_reserved_gb": round(torch.cuda.max_memory_reserved() / 2**30, 2),
           "process_rss_peak_gb": round(peak.rss / 2**30, 2), "system_ram_used_peak_gb": round(peak.sys_used / 2**30, 2),
           "torch": torch.__version__, "device": torch.cuda.get_device_name(0),
           "log_tail": trainer.state.log_history[-3:]}
    path = ROOT / "results" / "v0.4" / "feasibility" / f"grpo_{a.prompt}_g{a.group}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "log_tail"}, indent=1))


if __name__ == "__main__":
    main()
