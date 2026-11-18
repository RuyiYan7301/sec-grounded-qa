"""v0.4 step 2: supervised distillation of the planner (Qwen3-1.7B + LoRA), docs/v0.4-plan.md section 3.

    C:/Users/Admin/venvs/secqa-train/Scripts/python train/sft.py --out runs/sft_r16_lr2e-4 --lr 2e-4 --epochs 2

Loss on the completion (plan JSON) only. One adapter checkpoint per epoch; checkpoints are compared on the
validation split with train/eval_planner.py, never on test.
"""
import argparse
import json
import random
import time

import torch
from peft import LoraConfig, get_peft_model
from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer,
                          TrainingArguments)

from common import MODEL, ROOT, SHORT, completion_text, load_items, prompt_text

TRAIN = ROOT / "data" / "train" / "v0.4" / "sft_train.json"


def encode(tok, items, max_len=384):
    rows, cut = [], 0
    for it in items:
        p = tok(prompt_text(tok, SHORT, it["question"]), add_special_tokens=False)["input_ids"]
        c = tok(completion_text(it["target_plan"]), add_special_tokens=False)["input_ids"]
        ids = (p + c)[:max_len]
        cut += len(p) + len(c) > max_len
        rows.append({"input_ids": ids, "attention_mask": [1] * len(ids), "labels": ([-100] * len(p) + c)[:max_len]})
    print(f"{len(rows)} examples, {cut} truncated, max len {max(len(r['input_ids']) for r in rows)}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    out = ROOT / a.out
    tok = AutoTokenizer.from_pretrained(MODEL)
    items = load_items(TRAIN)
    random.Random(a.seed).shuffle(items)
    data = encode(tok, items)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda")
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(
        r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05, task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()
    args = TrainingArguments(
        output_dir=str(out), num_train_epochs=a.epochs, per_device_train_batch_size=a.batch,
        gradient_accumulation_steps=1, learning_rate=a.lr, lr_scheduler_type="cosine", warmup_ratio=0.03,
        bf16=True, logging_steps=20, save_strategy="epoch", report_to="none", seed=a.seed,
        dataloader_num_workers=0, remove_unused_columns=False)
    t0 = time.perf_counter()
    trainer = Trainer(model=model, args=args, train_dataset=data,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100))
    trainer.train()
    info = {"args": vars(a), "train_items": len(items), "seconds": round(time.perf_counter() - t0, 1),
            "gpu_peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2), "log": trainer.state.log_history}
    (out / "train_info.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k != "log"}))


if __name__ == "__main__":
    main()
