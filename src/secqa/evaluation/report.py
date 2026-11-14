"""Comparison table of saved evaluation runs (markdown).

    secqa report                 # test set, run t2 (the pre-registered result)
    secqa report --tag t3        # test set, post-hoc run of the revised verify arm
    secqa report --gold dev --tag r1
"""
import json

from .. import config

MODELS = ["qwen3:4b", "qwen3:8b", "qwen3:14b"]
ARMS = ["single", "verify"]


def load(gold="test", tag="t2"):
    runs = {}
    for m in MODELS:
        for a in ARMS:
            p = config.RESULTS_DIR / gold / f"{a}_{m.replace(':', '_')}_all{'_' + tag if tag else ''}.json"
            if p.exists():
                runs[(m, a)] = json.loads(p.read_text(encoding="utf-8"))
    return runs


def table(runs):
    lines = ["| model | arm | correct | grounded | numeric exact | tag selection | period flag | narrative | "
             "clarify / decline | fixed / broken by verify | median latency | mean tokens |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (m, a), r in runs.items():
        s = r["summary"]
        fb = f"{s['fixed_by_verify']} / {s['broken_by_verify']}" if a == "verify" else "-"
        lines.append(f"| {m} | {a} | **{s['correct']}/{s['n']}** | {s['grounded']} | {s['numeric_exact']} | "
                     f"{s['tag_selection']} | {s['period_flag']} | {s['narrative']} | {s['behavior']} | {fb} | "
                     f"{s['median_latency_s']:.1f} s | {s['mean_tokens']:,} |")
    return "\n".join(lines)


def by_type(runs):
    types = sorted({t for r in runs.values() for t in r["summary"].get("by_type", {})})
    if not types:
        return ""
    cols = list(runs)
    lines = ["| question type | " + " | ".join(f"{m.split(':')[1]} {a}" for m, a in cols) + " |",
             "|---|" + "---|" * len(cols)]
    for t in types:
        lines.append(f"| {t} | " + " | ".join(runs[k]["summary"]["by_type"].get(t, "") for k in cols) + " |")
    return "\n".join(lines)


def main(gold="test", tag="t2"):
    runs = load(gold, tag)
    if not runs:
        print(f"no results in {config.RESULTS_DIR / gold} with tag {tag!r}")
        return ""
    out = table(runs) + "\n\n" + by_type(runs)
    print(out)
    return out
