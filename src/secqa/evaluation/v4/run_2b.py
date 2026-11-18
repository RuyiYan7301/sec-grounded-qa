"""v0.4 generalization test, part 2b: the frozen pipeline on 160 generated questions about new companies.

    python -m secqa.evaluation.v4.run_2b                 # all 160 items  -> results/v0.4/pipeline/
    python -m secqa.evaluation.v4.run_2b --subset noise  # 40-item rerun for the noise floor

Same planner -> executor -> renderer -> frozen scorer 2.1 as evaluation/run_v2.py (its functions are reused,
not copied), with the mechanically generalized universe (universe.activate()). Only one harness change:
the fact store is built per question from the companies the plan names (a store of all 85 filers does
not fit beside the model in 16 GB). Store and SnapshotSource are per-ticker, so the facts the executor
sees are the same as with a store of every filer.

Noise subset: 40 item ids drawn with random.Random(2606) from the sorted ids, fixed here before any run.
No qualified alternatives exist for v0.4 items (the v0.2 file covers v0.2 items only).
"""
import argparse
import datetime
import hashlib
import json
import random
import time
from collections import OrderedDict

import yaml

from ... import config, universe
from ...engine import execute, llm, plan, render, resolve
from ...facts import Store
from ..run_v01 import commit
from ..run_v2 import execution_correct, scorer_result, summarize
from ..v2 import score as scorer

QA = config.EVAL_DIR / "v0.4" / "qa_gen_2606.json"
OUT = config.REPO_ROOT / "results" / "v0.4" / "pipeline"


def noise_ids(items):
    return set(random.Random(2606).sample(sorted(it["id"] for it in items), 40))


class Stores:
    """Fact stores keyed by the plan's companies; keeps a few in memory."""

    def __init__(self, keep=3):
        self.cache, self.keep = OrderedDict(), keep

    def source(self, tickers):
        key = tuple(sorted(set(tickers)))
        if key not in self.cache:
            self.cache[key] = resolve.SnapshotSource(Store(list(key)))
            while len(self.cache) > self.keep:
                self.cache.popitem(last=False)
        self.cache.move_to_end(key)
        return self.cache[key]


def run(subset=None):
    universe.activate()
    items = json.loads(QA.read_text(encoding="utf-8"))
    if subset == "noise":
        ids = noise_ids(items)
        items = [it for it in items if it["id"] in ids]
    o = yaml.safe_load((config.REPO_ROOT / "data" / "metric_ontology.yaml").read_text(encoding="utf-8"))
    stores = Stores()
    prompts_sha = hashlib.sha256((plan.system_prompt() + render.SYSTEM).encode("utf-8")).hexdigest()
    started = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for k, it in enumerate(items, 1):                  # production pass: no gold, no scorer
        log = llm.CallLog()
        t0 = time.perf_counter()
        p = plan.make_plan(it["question"], log)
        if p["status"] != "valid":
            r = {"outcome": "invalid_plan", "warnings": [], "evidence": []}
            rendered = {"answer": "", "renderer_input": None}
        else:
            src = stores.source(p["plan"].get("companies") or [])
            r = execute.execute(p["plan"], it["question"], src, o)
            rendered = render.render(it["question"], p["plan"], r, log)
        rows.append({"id": it["id"], "question": it["question"], "plan": p, "execution": r, "render": rendered,
                     "calls": log.calls, "seconds": round(time.perf_counter() - t0, 3)})
        print(k, it["id"], p["status"], r.get("outcome"), rows[-1]["seconds"], flush=True)
    gold = {it["id"]: it for it in items}              # scoring pass
    for row in rows:
        it, r = gold[row["id"]], row["execution"]
        rec = {"id": it["id"], "system": "v0.2", "answer": row["render"]["answer"],
               "evidence": [{k: e.get(k) for k in ("ticker", "metric", "concept", "value", "unit", "accession", "period_end")}
                            | {"period": e.get("fy")} for e in r.get("evidence", [])],
               "plan": row["plan"]["plan"], "result": scorer_result(r)}
        s = scorer.score_item(it, rec, None, o)
        row["score"] = {k: v for k, v in s.items() if k != "detail"} | {"detail": s["detail"]}
        row["execution_correct"] = execution_correct(it, r)
    summary = summarize(rows)
    run_info = {"test": "v0.4 2b", "questions": QA.name, "subset": subset, "commit": commit(),
                "started_utc": started.isoformat(timespec="seconds"), "model": config.DEFAULT_MODEL,
                "options": llm.OPTIONS, "planner_prompt_sha256": hashlib.sha256(plan.system_prompt().encode()).hexdigest(),
                "renderer_prompt_sha256": hashlib.sha256(render.SYSTEM.encode()).hexdigest(), "scorer_version": scorer.V,
                "schema": str(plan.SCHEMA_PATH)}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"run_{prompts_sha[:8]}_{started.strftime('%Y%m%dT%H%M%SZ')}{'_' + subset if subset else ''}.json"
    path.write_text(json.dumps({"run": run_info, "summary": summary, "items": rows}, indent=1, default=str) + "\n",
                    encoding="utf-8", newline="\n")
    print(path.name)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", choices=["noise"])
    run(ap.parse_args().subset)
