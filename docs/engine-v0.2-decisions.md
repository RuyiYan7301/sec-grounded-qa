# v0.2 typed engine: design decisions (fixed before any engine code or dev run)

Decided by the project owner on 2026-11-16, after the benchmark freeze (`v0.2-benchmark-freeze` → `b480b35`).
The engine lives in a new package `src/secqa/engine/`; no file listed in `data/eval/v0.2/manifest.json` is
changed. It does not import `secqa.evaluation.v2.gold`, any case gold, provenance, or either scorer.

## Model and calls

- Model `qwen3:8b` through Ollama `/api/chat`, the same options as v0.1: `think: false`,
  `temperature: 0`, `num_ctx: 16384`. No automatic model switch.
- Every model call is logged with its role (planner, repair, renderer), latency and token counts where
  Ollama reports them. Both systems report model calls and latency per item.

## Planner (one repair)

- The planner returns a typed plan constrained by the frozen `data/eval/v0.2/plan.schema.json` (Ollama
  `format` = that schema). The plan is then validated with the same schema and the JSON Schema format checker.
- If the first output is not valid, **one** repair call is allowed. The repair prompt contains only the
  original question, the invalid plan and the schema validation errors: no facts, no execution results,
  no gold, no scorer feedback.
- If the repaired plan is still invalid, the item returns `invalid_plan`. No rule-based fallback and no
  silent change of the plan.
- Logged: first-pass validity, repair success, final invalid rate, calls, latency.
- The one-repair policy is fixed now. The planner prompt may be improved on the dev split; every change
  is a commit; the prompt is frozen before the test split is run.

## Renderer (one call, no rewrite)

- The final answer is written by `qwen3:8b`, temperature 0, **one call, no retry**, no tool access.
- Input only: the original question, the validated plan, the structured execution result, the evidence
  items and the warnings as semantic codes with a plain description. No scorer patterns, match words or
  validation results.
- The output is not edited afterwards (no number or warning wording is changed). The renderer prompt,
  its structured input and the raw output are saved per item.
- A missed warning, a changed number or a wrong statement by the renderer is a real end-to-end failure of
  v0.2 and counts in the main result. Structured execution metrics (plan validity, concept, period,
  calculation / execution consistency, evidence completeness) are reported alongside to show where a
  failure arose. No template answer is built for comparison with v0.1.

Wording for reports: *The intended treatment difference was the execution architecture: unconstrained
model tool use versus schema-validated planning and deterministic execution; both systems used the same
model, temperature, snapshot, questions and scorer, while model-call topology and prompts necessarily
differed.*

## Value policies

- **Part A, `latest_in_snapshot`**: the latest 10-K / 10-K/A value filed on or before the snapshot
  (`SECQA_SNAPSHOT=2026-10-16`), through the system's own data layer.
- **Part B, `as_of_filing` with the exact target accession**: a `FilingFactIndex` built only from raw
  companyfacts and submissions. The target 10-K is found independently from submissions (company, fiscal
  year, form `10-K`). Both the current-year value and the comparative-year value must come from rows with
  `accn == target_accession`. If the target filing does not present that concept and period, the item is
  `not_reported` / `abstain`; no value is filled in from another filing. The filing-date cutoff only
  prevents look-ahead and is used to find the first-reported value among qualifying 10-K rows filed
  before the target filing; it never replaces the accession rule.

## CLI

`cli.py` and `pyproject.toml` are not frozen. A new `secqa diff TICKER --from FYxxxx --to FYyyyy` is added;
the existing v0.1 commands, their behaviour and their tests stay unchanged.

## Order of work

1. engine package; 2. typed plan and schema validation; 3. metric resolver; 4. fiscal-period engine;
5. deterministic calculation and evidence ids; 6. debugging on the dev split and the CSCO case only;
7. `secqa diff`; 8. engine freeze (tag) before the test split is run; 9. the 80-record Part A audit and
the review of the three Part B packets.
