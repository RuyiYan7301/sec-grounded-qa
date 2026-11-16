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

## Engine freeze (2026-11-16)

Tag `v0.2-engine-freeze`, set before any test-split question or test-case packet is run. From here on the
engine code and prompts below do not change for the v0.2 results; a later fix is a new version, reported
separately.

| Component | Frozen value |
|---|---|
| model | `qwen3:8b`, Ollama digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`; think false, temperature 0, num_ctx 16384 |
| planner system prompt | sha256 `9badd9e022b8b74e7aab4f7d75d034d10e265f7f5db42491c46acb56baae7fe1` (one schema repair) |
| renderer system prompt | sha256 `21237b5addad5fc82873d4cfe353c6b50f9fb8e2efd7172bcd9126cecc1d6636`; input carries a `display` field formatted by code |
| Item 1A classifier prompt | sha256 `3206c9423984597543834fb8b4926e4272145118e111c445fa77207e0eba53a8`; context = top 3 paragraphs of the other report by sentence coverage |
| scorers | Part A 2.1, Part B 1.0 (frozen with the benchmark, `v0.2-benchmark-freeze`) |

Development results at the freeze (dev split and the CSCO case only; these were used for debugging and are
not evidence of performance):

- Part A dev, 40 items: plans schema-valid 40/40; execution correct 39/40; rendered final correct 36/40
  (`results/dev/pipeline/run_61b72567_20261116T171133Z.json`).
- CSCO FY2023 -> FY2024 packet: numeric verified recall and precision 18/18, evidence 28/28, no look-ahead;
  Item 1A precision 25/45, recall 25/28, boilerplate false-positive rate 18/36, sub-type agreement 24/25
  (`results/dev/diff/CSCO_FY2024_ablation-oldprompt-newcontext_20261116T172229Z.json`, same code and prompt
  as frozen).

Known limitations carried into the test run (not fixed, to avoid further tuning on the dev data):

- The planner maps "gross margin" to `gross_profit` on one dev question; a prompt variant (10eb8ab5) did not
  fix it and added an error, and was not kept.
- Three correct refusals on the dev split are worded in ways the frozen Part A scorer does not recognise
  (scorer false negatives); they are left to the post-freeze audit, not fixed by changing wording or scorer.
- Item 1A: the classifier labels about half of the wording-only (boilerplate) changes as material. A prompt
  with the guideline v2 definitions was tried and not kept (precision 24/48).
- The dev split and CSCO do not exercise restated values, scope warnings, negative bases or splits; those
  paths are covered by fixture tests only.
