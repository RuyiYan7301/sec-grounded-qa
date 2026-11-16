# Part A scorer calibration, round 3: FAILED (scorer bugs found), now development data

## Process check

- Protocol and seed committed before sampling (`f03dcd8`); Amendment 1 before any sample was written
  (`3bc9caf`); template, generator and cell exclusion committed with sha256 (`13dbd13`).
- `filled.json` by a fresh Codex session ("Codex GPT-5", 2026-11-15), committed before the run (`aa4f199`).
  Two later commits (`9058cc9`, `05b06cd`) only moved `na_ok` out of `expected_scores` to the slot level,
  after the runner refused the file; no answer, record or expected value changed (checked slot by slot).
- One run, scorer sha256 `95c3722a…` (unchanged since `2ba02ab`); the run file is the committed content
  (sha256 differs from the git blob only by line endings). Output: `runs.jsonl`, `raw_output_run1.json`.

## Result of the single run (as produced)

| Set | n | Fully matching | Record-level mismatch | Wilson 95% |
|---|---:|---:|---:|---|
| all slots | 30 | 22 | 8 (26.7%) | 14.2% – 44.4% |
| slots built from unused cells only | 26 | 19 | 7 (26.9%) | 13.7% – 46.1% |

Mismatches per score (all 30): `evidence_complete` 7, `final_correct` 1, `period_ok` 1. Targets not as
designed: P04.

## Reading of the 8 mismatches (classification by Claude, for the owner to check)

| Slots | Who is right | Why |
|---|---|---|
| **P04** | calibrator | **Scorer bug.** The cross-company difference (1.397 billion shares) is part of the gold result but was not in the scorer's gold amounts, so it was flagged as a contradiction. |
| **P08** | calibrator | **Scorer bug.** "159 basis points" was read as an amount of 159 and failed evidence completeness; the evidence check does not know percentage-point or basis-point figures. (P08 is a partially_new slot.) |
| F04, F08, F09, F10, F12 | scorer | The answers state figures no evidence supports (a mis-computed 1.5%, an estimated $30B, a projected $60B, an out-of-range $15B, a mis-computed $35M). Under the specification that makes `evidence_complete = false`; the calibrator expected true. |
| F01 | scorer | The note says the FY2023 value was put in FY2024 evidence, but the record's evidence is the unchanged FY2024 gold cell while the answer states the FY2023 figure. Scored as the record stands: evidence does not support the stated number (`evidence_complete = false`) and the evidence period is right (`period_ok = true`). |

With this classification the scorer was wrong on 2 of 30 slots (Wilson 95% 1.8% – 21.3%); on the 26
new-cell slots, 1 of 26 (0.7% – 18.9%). These are **not** reported as the scorer confirmation.

## Consequence (rule fixed before the round)

Round 3 exposed scorer bugs, so it is reported as failed, becomes development data, the bugs are fixed
with regression tests, and a fourth unseen set is needed for the confirmation.
