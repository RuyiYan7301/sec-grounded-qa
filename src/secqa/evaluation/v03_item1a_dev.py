"""Development runs of the Item 1A v0.3 candidates (docs/item1a-v0.3-plan.md).

    python -m secqa.evaluation.v03_item1a_dev VARIANT [--model M] [--cases C ...]
    # writes results/dev/item1a_v03/<variant>_<model>_<UTC>.json, never over an earlier file

Development cases only (CSCO dev, and the v0.2 test cases, which are development data for v0.3). Each case is
scored with the frozen Part B Item 1A rules (partb_score.score_item1a) against the frozen v0.2 gold.
"""
import argparse
import datetime
import hashlib
import json
import time

import requests

from .. import config
from ..engine import item1a_v03, llm
from .run_v01 import commit
from .v2 import partb_score as ps

DEV = {"CSCO_FY2024": ("CSCO", 2023, 2024), "NVDA_FY2025": ("NVDA", 2024, 2025),
       "INTC_FY2025": ("INTC", 2024, 2025), "AVGO_FY2024": ("AVGO", 2023, 2024)}
OUT = config.REPO_ROOT / "results" / "dev" / "item1a_v03"
POOL = ("precision", "recall", "boilerplate_fpr", "subtype_agreement", "locator_complete")


def run(variant, model=None, cases=None):
    model = model or config.DEFAULT_MODEL
    loc, labels = ps.load_item1a()
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        ollama_version = requests.get(f"{config.OLLAMA_HOST}/api/version", timeout=10).json().get("version")
    except requests.RequestException:
        ollama_version = None
    per = {}
    for case in cases or DEV:
        t, y1, y2 = DEV[case]
        t0 = time.perf_counter()
        d = item1a_v03.detect(t, y1, y2, variant, log=llm.CallLog(), model=model)
        packet = {"case": case, "item1a_changes": d["item1a_changes"]}
        s = ps.score_item1a(packet, True, loc, labels)
        per[case] = {"score": s, "seconds": round(time.perf_counter() - t0, 1), "calls": d["calls"],
                     "candidates": d["candidates"], "item1a_changes": d["item1a_changes"]}
        print(case, {k: f"{s[k]['num']}/{s[k]['den']}" for k in POOL}, per[case]["seconds"], "s", flush=True)
        OUT.mkdir(parents=True, exist_ok=True)       # one file per finished case, so a dropped connection loses nothing
        (OUT / f"partial_{variant}_{model.replace(':', '-')}_{started.strftime('%Y%m%dT%H%M%SZ')}_{case}.json").write_text(
            json.dumps({"variant": variant, "model": model, "ollama_host_kind": "lan" if "192.168" in config.OLLAMA_HOST else "local",
                        "case": case} | per[case], ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    pooled = {k: {"num": sum(per[c]["score"][k]["num"] for c in per), "den": sum(per[c]["score"][k]["den"] for c in per)}
              for k in POOL}
    tests = [c for c in per if c != "CSCO_FY2024"]
    pooled_test3 = {k: {"num": sum(per[c]["score"][k]["num"] for c in tests), "den": sum(per[c]["score"][k]["den"] for c in tests)}
                    for k in POOL}
    sys_sha = hashlib.sha256(item1a_v03.system_prompts()[variant].encode()).hexdigest()
    info = {"variant": variant, "model": model, "ollama_version": ollama_version, "options": llm.OPTIONS,
            "move_min": item1a_v03.MOVE_MIN, "system_prompt_sha256": sys_sha, "commit": commit(),
            "started_utc": started.isoformat(timespec="seconds")}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{variant}_{model.replace(':', '-')}_{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps({"run": info, "pooled_4": pooled, "pooled_nvda_intc_avgo": pooled_test3,
                                "cases": per}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(path.name)
    print("pooled_4", {k: f"{v['num']}/{v['den']}" for k, v in pooled.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["v02", "diff", "quote"])
    ap.add_argument("--model")
    ap.add_argument("--cases", nargs="*")
    a = ap.parse_args()
    run(a.variant, a.model, a.cases)
