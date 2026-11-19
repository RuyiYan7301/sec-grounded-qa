"""v0.4 step 2: GRPO on the executor's verdict, starting from the SFT checkpoint (docs/v0.4-plan.md 3b).

    cd train
    C:/Users/Admin/venvs/secqa-train/Scripts/python grpo.py --sft runs/sft_hint_r16_lr2e-4/checkpoint-480 \
        --out runs/grpo_from_ck480

Reference model = the SFT checkpoint: the SFT adapter is merged into the base weights and a fresh LoRA
(same r16/alpha32 setup) is trained on top, so TRL's reference (adapter disabled) is the SFT model, not the
base. Reward per completion (plan table in 3b, with the 2026-11-18 amendments):
    +1  execution check correct (outcome, result in tolerance, required warning codes), or correct refusal;
        for restated-value questions the plan's period set must also equal the gold set
     0  refusal plan on an answerable question
    -1  anything else: wrong answer, wrong refusal, answer where a refusal is due, invalid plan, executor error
The rendered answer is not used (one 8B call per rollout does not fit the budget). A checkpoint is saved
every 50 steps; checkpoints are compared on validation with eval_planner.py, never on test. Per-step
logs: mean reward and the rates of invalid plans, refusals on answerable prompts and executor errors
(the stop rule is a refusal-rate rise of more than 5 points over SFT on validation, checked per checkpoint).
"""
import argparse
import json
import time
from collections import Counter

import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import GRPOConfig, GRPOTrainer

from common import MODEL, ROOT, load_items, system_for

DATA = ROOT / "data" / "train" / "v0.4" / "grpo_prompts.json"
ANSWERABLE = ("answer", "not_meaningful", "ambiguous_year")


class Rewarder:
    """Plan text -> reward, using the frozen validator, executor and execution check."""

    def __init__(self, items):
        from secqa import config, universe
        import yaml
        universe.activate()
        from secqa.engine import execute, llm, plan
        from secqa.evaluation.run_v2 import execution_correct
        from secqa.evaluation.v4.run_2b import Stores
        self.items, self.execute, self.llm, self.plan, self.ok = items, execute, llm, plan, execution_correct
        self.o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
        self.stores = Stores()
        self.counts = Counter()
        self.__name__ = "executor_reward"

    def one(self, it, text):
        p = self.llm.parse_json(text)
        if p is None or self.plan.validate(p):
            return -1.0, "invalid"
        if "refuse" in p and it["gold_outcome"] in ANSWERABLE:
            return 0.0, "refused_answerable"
        try:
            src = None if "refuse" in p else self.stores.source(p.get("companies") or [])
            r = self.execute.execute(p, it["question"], src, self.o)
        except Exception:                            # noqa: BLE001  an executor crash is a -1, and counted
            return -1.0, "executor_error"
        good = self.ok(it, r)
        gp = it.get("gold_plan") or {}
        if good and gp.get("intent") == "restated_value_lookup" and set(p.get("periods") or []) != set(gp["periods"]):
            return -1.0, "extra_period"
        return (1.0, "correct") if good else (-1.0, "wrong")

    def __call__(self, prompts, completions, idx, **_):
        out = []
        for c, i in zip(completions, idx):
            text = c[0]["content"] if isinstance(c, list) else c
            r, why = self.one(self.items[i], text)
            self.counts[why] += 1
            out.append(r)
        return out


class Log(TrainerCallback):
    def __init__(self, rewarder, path):
        self.r, self.path, self.t0 = rewarder, path, time.perf_counter()

    def on_log(self, args, state, control, logs=None, **k):
        c, n = self.r.counts, max(1, sum(self.r.counts.values()))
        row = {"step": state.global_step, "min": round((time.perf_counter() - self.t0) / 60, 1),
               "reward": logs.get("reward"), "kl": logs.get("kl"),
               **{f"rate_{k}": round(v / n, 3) for k, v in sorted(c.items())}}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        self.r.counts.clear()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft", required=True, help="SFT adapter directory (relative to the repo root)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--accum", type=int, default=4, help="prompts per optimizer step")
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--max-completion", type=int, default=256)
    ap.add_argument("--limit", type=int, help="first N prompts only (smoke test)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data", default=str(DATA.relative_to(ROOT)), help="prompt file, relative to the repo root")
    a = ap.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    items = load_items(ROOT / a.data)[:a.limit]
    ds = Dataset.from_list([{"prompt": [{"role": "system", "content": system_for("short", it["question"])},
                                        {"role": "user", "content": it["question"]}], "idx": i}
                            for i, it in enumerate(items)])
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(base, str(ROOT / a.sft)).merge_and_unload()   # reference = SFT
    rewarder = Rewarder(items)
    cfg = GRPOConfig(
        output_dir=str(out), num_train_epochs=a.epochs, per_device_train_batch_size=a.group,
        num_generations=a.group, gradient_accumulation_steps=a.accum, max_completion_length=a.max_completion,
        temperature=1.0, learning_rate=a.lr, beta=0.04, bf16=True, gradient_checkpointing=True,
        logging_steps=1, save_strategy="steps", save_steps=50, report_to="none", seed=a.seed,
        chat_template_kwargs={"enable_thinking": False}, remove_unused_columns=False)
    trainer = GRPOTrainer(
        model=model, processing_class=tok, reward_funcs=rewarder, args=cfg, train_dataset=ds,
        peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                               target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]),
        callbacks=[Log(rewarder, out / "reward_log.jsonl")])
    t0 = time.perf_counter()
    trainer.train()
    info = {"args": vars(a), "prompts": len(items), "seconds": round(time.perf_counter() - t0, 1),
            "gpu_peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
    (out / "train_info.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps(info))


if __name__ == "__main__":
    main()
