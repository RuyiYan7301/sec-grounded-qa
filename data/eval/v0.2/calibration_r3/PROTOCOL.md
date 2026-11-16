# Part A scorer calibration, round 3: protocol (written before any sampling)

CALIBRATION_R3_SEED = 4041

## Items

30 new calibration-only questions on the dev companies (Cisco, Oracle), built by
`src/secqa/evaluation/v2/calibration_template_r3.py` with the seed above, gold computed by the gold
builder (`gold.py`, value policy `latest_in_snapshot`).

A fact cell is **used** if it appears anywhere in:

- `data/eval/v0.2/qa_dev.json` (every gold cell, components included);
- the round-1 and round-2 calibration templates (every gold cell of every slot item);
- `data/eval/v0.2/qualified_alternatives.json` (every alternative cell).

Cell key: `(ticker, metric, concept, period_end, value_policy, accession)`. A round-3 question may use
only unused cells; for a derived metric every component cell must be unused (a gross margin built on a
used revenue cell is not new). Questions without fact cells (refusals) must have wording and target not
used in rounds 1-2.

## Order

1. This protocol is committed before the generator runs.
2. The generator, its output (`template.json`) and the cell exclusion report are committed, with
   sha256 recorded in `manifest.json`.
3. A fresh Codex session fills `filled.json`; it may not read the scorer, its tests, rounds 1-2 or their
   reports, `results/`, or git history.
4. `filled.json` (answers, evidence, plan, result, full expected vectors) is committed before the run.
5. One run. Raw output kept.

## Outcome rules (fixed before the round)

- Differences on the boundaries defined in the specification are kept; the scorer is not changed.
- A scorer bug: the failed result is saved and reported, round 3 becomes development data, the bug is
  fixed with regression tests, and a fourth unseen set is the confirmation. Round 3 is then not called
  independent.
- Report: slots matching the expected vector, record-level mismatch rate, mismatches per score, Wilson
  95% interval.
