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

## Amendment 1 (2026-11-15, before any sample was written; decided by the project owner)

A first generator run stopped with "no unused cells" for the percentage-point slot and wrote nothing.
Every Cisco and Oracle revenue cell (the denominator of every ratio metric) is used, so no ratio or
percentage-point question can be built from unused cells only. For these four slots (two ratio, two
percentage-point) the **numerator** cells must be unused; the revenue denominator may be a used cell.
They are marked `cell_novelty: partially_new` with the reused cells listed. Only Cisco R&D has unused
cells in consecutive years, so both percentage-point slots use Cisco R&D intensity (FY2023→FY2024 and
FY2024→FY2025) and share the FY2024 R&D cell; this is marked too. The confirmation is reported on all 30
slots and on the 26 slots built from unused cells only. The seed is unchanged.
