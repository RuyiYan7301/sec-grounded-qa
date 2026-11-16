# Part A scorer calibration: instructions for the calibrator

You are calibrating a rule-based scorer for a numeric question-answering benchmark on SEC 10-K filings.
Work in a fresh session. **Do not open `src/secqa/evaluation/v2/score.py`, `tests/test_score_v2.py` or
any file under `results/`**, and do not search the repository for the scorer's patterns. You may read
this file, `template.json`, `data/eval/v0.2/plan.schema.json`, `data/metric_ontology.yaml` and
`docs/benchmark-v0.2.md` (the specification).

## Task

1. Copy `template.json` to `filled.json` in this folder.
2. For each of the 30 slots, write a **record** that a real system could plausibly produce, in natural
   wording, so that the slot's `target` happens and the `targeted_score` comes out as
   `targeted_expected` (15 slots pass, 15 fail). Vary wording, number formats and sentence structure as
   real systems do; do not copy phrasing between slots.
3. For each slot, fill **every** entry of `expected_scores` with what a careful human grader would give
   under the specification (`docs/benchmark-v0.2.md`, Part A: Scores, Qualified alternatives, Scorer),
   not what you guess the scorer does. Use `true` / `false`, and for `concept` one of `canonical`,
   `qualified_alternative`, `incorrect`, `n/a`. A score that does not apply is `null`; mark it in
   `na_ok`, e.g. `"na_ok": {"plan_valid": true}` (plan, intent and calculation apply to `v0.2` records
   only; concept and period do not apply to refusals). Add a one-line `calibrator_note` per slot.
4. Only after every slot is filled, run:

       python -m secqa.evaluation.v2.calibrate data/eval/v0.2/calibration/filled.json

   (from the repository root, with `PYTHONPATH=src`). It refuses to run while any slot is incomplete.
5. Do not change answers or expectations after seeing scores. If you made a mistake, add a corrected
   copy of that slot's note explaining it; the first run is kept in `runs.jsonl`.

## Record format

    {"id": "<item id>", "system": "v0.1" | "v0.2",
     "answer": "<final answer text>",
     "evidence": [{"ticker": "CSCO", "metric": "revenue", "period": "FY2024", "concept": "...",
                   "value": 53803000000, "unit": "USD", "accession": "...", "period_end": "2024-07-27"}],
     "plan": {...} | null,      # v0.2 only; see plan.schema.json
     "result": {...} | null}    # v0.2 only; the engine's computed result, e.g. {"val": 22.3} or {"vals": [...]}

`evidence` is what the system used. A correct record normally copies the gold cells (from `item`) into
evidence; for the evidence and structured slots, change exactly what the target says. Percentages and
margins are in percent (63.03 means 63.03%).

## Provenance

Record in `filled.json` at top level: `"calibrator": "<tool and model>", "date": "YYYY-MM-DD"`.
Five slots use the gold of test items (`gold_source: test_gold`); only their questions and gold are
used, no system output. Two use calibration-only items on dev companies.
