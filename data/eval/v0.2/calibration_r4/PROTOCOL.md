# Part A scorer calibration, round 4: protocol (written before any sampling)

CALIBRATION_R4_SEED = 4042

Round 4 is the last pre-freeze synthetic confirmation. It is a limited-scope check on unseen synthetic
boundary cases; it is not an accuracy estimate for the scorer as a whole. A separate post-freeze check
of real system outputs (below) is reported on its own.

## Items

- 24 slots, 12 expected to pass, 12 expected to fail, built by
  `src/secqa/evaluation/v2/calibration_template_r4.py` with the seed above.
- Only **base** fact cells of Cisco and Oracle that never appeared before: not in `qa_dev.json`, not in
  any cell of the round-1, round-2 or round-3 calibration items, not in `qualified_alternatives.json`.
  Cell key `(ticker, metric, concept, period_end, value_policy, accession)`. No derived metric, so no
  ratio and no percentage-point items: round 4 does **not** cover those branches, and the report says so.
- At most 24 new cells are used; at least 10 unused cells are left untouched.
- Refusal questions (no cells) use wording and targets not used in rounds 1-3.

## Order

1. This protocol is committed before the generator runs.
2. Generator, `template.json`, cell exclusion report and `manifest.json` (sha256) are committed.
3. A fresh Codex session fills `filled.json`; it may not read the scorer, its tests, the dev-check
   script, rounds 1-3 or their reports, `results/`, or git history.
4. `filled.json` (answers, evidence, plan, result, full expected vectors) is committed before the run.
5. One run; raw output kept.

## Outcome rules (fixed before the round)

- Report record-level and per-score mismatches, with Wilson 95% intervals; no extrapolation to the
  scorer as a whole.
- Differences on the boundaries defined in the specification are kept; the scorer is not changed.
- If round 4 exposes a scorer bug: record round 4 as failed; fix the bug with regression tests; no claim
  of an independent pre-freeze synthetic confirmation is made; the version with the known bug is not
  frozen; the external check is the post-freeze real-output audit.

## Post-freeze real-output audit (fixed now, run after the systems)

- Items: the 40-item noise subset already fixed in `data/eval/v0.2/noise_subset.json`; no new sample.
- Records: for each item, one designated run output of v0.1 and one of v0.2 (80 records).
- Judged by hand / Codex-assisted review without seeing the scorer's scores, per record: final answer,
  refusal, evidence, concept, period, calculation, warning.
- Compared with the frozen scorer: record-level agreement, agreement per dimension, false positives and
  false negatives, Wilson 95% intervals.
- Scorer problems found there do not change the frozen results; any corrected analysis is labelled
  post hoc.
