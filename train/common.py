"""Shared pieces for the v0.4 planner training (run in the secqa-train venv; docs/v0.4-plan.md section 3).

The prompt text is built exactly the same way at training and at inference: Qwen3 chat template, thinking
off, system message = the short instruction (or the full planner prompt for the base-model arms), user
message = the question. The completion is the plan as compact JSON followed by <|im_end|>.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("SECQA_DATA_DIR", "C:/Users/Admin/sgqa-clean/data")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

MODEL = "C:/Users/Admin/models/Qwen3-1.7B"
SHORT = "Return the typed plan for the question as one JSON object."
END = "<|im_end|>"


def system_text(kind):
    if kind == "short":
        return SHORT
    from secqa import universe
    from secqa.engine import plan
    universe.activate()
    return plan.system_prompt()


def prompt_text(tok, system, question):
    return tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": question}],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False)


def completion_text(plan):
    return json.dumps(plan) + END + "\n"


def load_items(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return d["items"] if isinstance(d, dict) else d
