"""Build the public demo's committed data: precomputed answers and Item 1A results (data/demo/).

    secqa demo-build            # answers every question below with the live engine, then copies Item 1A results

The public demo (SECQA_DEMO=1) serves these answers on the Ask page and runs the Companies and 10-K changes pages
live; nothing else is precomputed. Each answer is the system's real output, saved unchanged with its run date.
"""
import json
import shutil
import time
from datetime import date

from . import cli, config, response

EXTRA = [
    "What was Microsoft's operating margin in fiscal 2025?",
    "Compare Nvidia's and AMD's research and development expense for fiscal 2025.",
    "What basic EPS did Broadcom first report for fiscal 2023, and what figure do its filings show today?",
    "What was Apple's free cash flow in fiscal 2025?",
    "List Oracle's revenue for fiscal 2023 through fiscal 2025.",
    "By how many percentage points did Cisco's gross margin change from fiscal 2024 to fiscal 2025?",
    "How much did Intel's net income change from fiscal 2024 to fiscal 2025?",
    "What was Nvidia's EBITDA in fiscal 2025?",
    "What was AMD's inventory at the end of fiscal 2025?",
    "How does Microsoft describe competition in AI in its fiscal 2025 10-K?",
    "What risks does Intel describe about its foundry business in its fiscal 2025 10-K?",
    "Will Nvidia's revenue keep growing next year?",
]


def build(model=None):
    from .web import segments
    out_dir = config.DEMO_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    answers = []
    for q in [q for _, q in cli.EXAMPLES] + EXTRA:
        t0 = time.time()
        a = response.ask(q, model=model, engine="auto")
        d = a.to_dict()
        d["segments"] = segments(a.answer, d["facts"])
        answers.append(d)
        print(f"{a.status:24s} {round(time.time() - t0):4d}s  {q}", flush=True)
    (out_dir / "answers.json").write_text(json.dumps({"run_date": date.today().isoformat(), "model": model or config.DEFAULT_MODEL,
                                                      "snapshot": config.SNAPSHOT, "answers": answers}, indent=1) + "\n",
                                          encoding="utf-8", newline="\n")
    src = config.DATA_DIR / "ui_cache"
    (out_dir / "item1a").mkdir(exist_ok=True)
    n = 0
    for f in sorted(src.glob("item1a_v03_*.json")):
        shutil.copy(f, out_dir / "item1a" / f.name)
        n += 1
    print(f"{len(answers)} answers and {n} Item 1A results -> {out_dir}")
