# Part A scorer calibration, round 2 (held out): instructions for the calibrator

You are writing a held-out check of a rule-based scorer for a numeric question-answering benchmark on
SEC 10-K filings. Work in a **fresh session** with no memory of earlier calibration work.

## Do not open or search

- `src/secqa/evaluation/v2/score.py`, `tests/test_score_v2.py`, `src/secqa/evaluation/v2/calibration_template.py`
- anything under `data/eval/v0.2/calibration/` (round 1: answers, report, runs)
- anything under `results/`
- the git history (`git log`, `git show`, `git diff` of earlier commits)

You may read: this file, `template.json` in this folder, `data/eval/v0.2/plan.schema.json`,
`data/metric_ontology.yaml`, `data/eval/v0.2/qualified_alternatives.json` and `docs/benchmark-v0.2.md`
(the specification; grade by it).

## Task

1. Copy `template.json` to `filled.json` in this folder. Add at top level
   `"calibrator": "<tool and model>", "date": "YYYY-MM-DD"`.
2. For each of the 30 slots write a **record** a real system could plausibly produce, in natural and
   varied wording, so that the slot's `target` happens and its `targeted_score` comes out as
   `targeted_expected` (15 pass, 15 fail). Slots whose target is a correct answer must be correct in
   every respect the specification checks; slots with an error must contain exactly that error.
3. Fill **every** entry of `expected_scores` with what a careful human grader would give under the
   specification (Part A: Scores, Qualified alternatives, Scorer, including the definitions listed
   there), not what you guess a program does. `true` / `false`; for `concept` one of `canonical`,
   `qualified_alternative`, `incorrect`, `n/a`. A score that does not apply is `null`, marked in
   `na_ok`, e.g. `"na_ok": {"plan_valid": true}`. One-line `calibrator_note` per slot.
4. **Commit before running**: from the repository root run
   `git add data/eval/v0.2/calibration_r2/filled.json && git commit -m "Calibration round 2: filled before run"`.
5. Run **once**:

       PYTHONPATH=src python -m secqa.evaluation.v2.calibrate data/eval/v0.2/calibration_r2/filled.json

   The runner refuses an incomplete file and refuses a second run in this folder. It writes
   `runs.jsonl` and `raw_output_run1.json` here. Commit both unchanged.
6. Do not edit answers or expectations after the run. Do not fix anything. Report what the run printed.

## Record format

    {"id": "<item id>", "system": "v0.1" | "v0.2",
     "answer": "<final answer text>",
     "evidence": [{"ticker": "CSCO", "metric": "revenue", "period": "FY2024", "concept": "...",
                   "value": 53803000000, "unit": "USD", "accession": "...", "period_end": "2024-07-27"}],
     "plan": {...} | null,      # v0.2 only; must follow plan.schema.json unless the slot targets an invalid plan
     "result": {...} | null}    # v0.2 only; the engine's computed result, e.g. {"val": 22.3} or {"vals": [...]}

`evidence` is what the system used; a correct record normally copies the gold cells from `item`. For
evidence and structured slots, change exactly what the target says. Percentages and margins are in
percent (63.03 means 63.03%); percentage-point changes are in points.
