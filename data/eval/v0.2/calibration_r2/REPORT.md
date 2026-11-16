# Part A scorer calibration, round 2 (held out): FAILED, now development data

## What happened

- `filled.json` written by a fresh Codex session ("Codex GPT-5", 2026-11-15) and committed before the run
  (`1ee340b`).
- The single run **crashed**: `AttributeError: 'str' object has no attribute 'get'` in
  `evidence_complete()`. No scores were produced. Recorded in `runs.jsonl` (status `crashed`, scorer
  sha256 `d1806a1d…`, file sha256 `90b8e5e4…`); the folder stays locked against further runs.
- Cause: eight records gave `evidence` as a single object (P01, P02, P11, F13) or `null` (P09, P10, F07,
  F08) instead of a list. The record format asks for a list, but a scorer must score malformed input,
  not crash on it. This is a scorer bug.

Under the rule fixed before the round: the round is reported as failed, its 30 slots become development
data, the bug is fixed with regression tests, and a third unseen set is the confirmation. No accuracy
figure is reported from round 2.

## Fixes (all with regression tests in `tests/test_score_v2.py`)

| Found on | Fix |
|---|---|
| crash (8 slots) | records are cleaned first; evidence as one object is read as a one-item list, `null` as empty, anything else dropped; `record_format_ok` reported per item; malformed plan/result/answer never raise |
| P04, P13 | period-mismatch wording: "not aligned", "periods end on different dates" |
| P10 | refusal wording: "unavailable", "outside the covered filing range" |
| F05 | basic EPS named for a diluted-EPS question (3.70 vs 3.71 is inside the $0.01 tolerance) is wrong |
| F05, F10, F11 | scores separated: concept matched by company and metric (period falls back), period by company and period end, calculation uses the system's own metric, companies, periods and cells with the gold formula |
| regressions caught by re-checking round 1 and 2 | mixed concepts across years must still be `incorrect` (F15); a wrong intent must not also fail calculation (round 1 S3) |

## Development check after the fixes (`dev_check.json`, not a calibration run)

- round 2: 27 / 30 slots match the calibrator's expected vector.
- round 1: unchanged apart from the definitions already recorded in its report.

The three remaining round-2 differences are semantic boundaries; the scorer was **not** changed for them:

| Slot | Calibrator | Scorer | Point at issue |
|---|---|---|---|
| F09 | wrong | right | "gross margin rose by 0.3%" for a 0.3 pp change: the number is the pp value, written with a % sign |
| F10 | wrong | right | the answer's number equals the gold, but the v0.2 plan and cells used a wrong metric (concept fails) |
| F14 | wrong | right | correct answer plus an extra unsupported figure ("revenue also increased 12.0%"; evidence fails) |

Under the specification, final-answer correctness depends on the stated numbers, warnings and outcome
only; the errors in F10 and F14 are scored by concept and evidence completeness. Whether to make
final-answer correctness stricter on these points is a decision for the project owner before round 3.
