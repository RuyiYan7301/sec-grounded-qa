"""Shared pieces for the v0.4 planner training (run in the secqa-train venv; docs/v0.4-plan.md section 3).

The prompt text is built exactly the same way at training and at inference: Qwen3 chat template, thinking
off, system message = the short instruction (or the full planner prompt for the base-model arms), user
message = the question. The completion is the plan as compact JSON followed by <|im_end|>.
"""
import json
import os
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("SECQA_DATA_DIR", "C:/Users/Admin/sgqa-clean/data")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

MODEL = "C:/Users/Admin/models/Qwen3-1.7B"
SHORT = "Return the typed plan for the question as one JSON object."
END = "<|im_end|>"


import re

# Common names a user may type that are not the universe's short name. Written by hand, from general
# knowledge of the companies, not from any test item.
EXTRA_NAMES = {"Google": "GOOGL", "Alphabet": "GOOGL", "Facebook": "META", "Meta": "META", "J&J": "JNJ",
               "Exxon": "XOM", "ExxonMobil": "XOM", "P&G": "PG", "Procter & Gamble": "PG", "Coca-Cola": "KO",
               "Coke": "KO", "Walmart": "WMT", "Disney": "DIS", "AT&T": "T", "Verizon": "VZ", "Amazon": "AMZN",
               "Microsoft": "MSFT", "Nvidia": "NVDA", "NVIDIA": "NVDA", "Broadcom": "AVGO", "Oracle": "ORCL",
               "Cisco": "CSCO", "Salesforce": "CRM", "Lockheed": "LMT", "Raytheon": "RTX", "Philip Morris": "PM",
               "Pepsi": "PEP", "McDonald's": "MCD", "Starbucks": "SBUX", "Lilly": "LLY", "UnitedHealth": "UNH"}


@lru_cache(maxsize=1)
def _name_table():
    from secqa import universe
    names = universe.short_names()
    table = {n: t for t, n in names.items()}
    for n, t in EXTRA_NAMES.items():
        if t in names:
            table.setdefault(n, t)
    return names, sorted(table.items(), key=lambda kv: -len(kv[0]))


def company_hint(question):
    """'Companies mentioned: Boeing = BA; ...' by deterministic name and ticker matching."""
    names, table = _name_table()
    found, text = [], question
    for n, t in table:                               # longest names first
        rx = re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?:'?s)?(?![A-Za-z])", re.I if len(n) > 4 else 0)
        if rx.search(text):
            if t not in found:
                found.append(t)
            text = rx.sub(" ", text)
    for t in names:                                  # bare tickers, upper case, whole word
        if t not in found and re.search(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])", text) and len(t) > 1:
            found.append(t)
    if not found:
        return "Companies mentioned: none found."
    return "Companies mentioned: " + "; ".join(f"{names[t]} = {t}" for t in found) + "."


def system_for(kind, question):
    """System message for one question: 'short' = instruction + company hint; 'long' = full planner prompt."""
    if kind == "short":
        return SHORT + "\n" + company_hint(question)
    return system_text("long")


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
