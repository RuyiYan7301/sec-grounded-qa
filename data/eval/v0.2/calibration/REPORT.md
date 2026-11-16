# Part A scorer calibration, round 1 (2026-11-15)

Calibrator: an isolated Codex session (recorded in `filled.json` as "Codex GPT-5"), given `INSTRUCTIONS.md`,
the template, the plan schema, the ontology and the specification; not the scorer source or its tests.
It filled all 30 slots (answers and full expected score vectors) before the first run; its build script
is `build_filled.py`. Answers and expectations were not changed after scores were seen. Runs are in
`runs.jsonl` (scorer sha256 per run).

## Run 1 (scorer `ba5f471f…`)

Targets not as designed: W6, R2. Field-level mismatches in 29 of 30 slots, sorted by cause:

| Cause | Slots | Resolution |
|---|---|---|
| **Scorer bug**: the period-mismatch pattern reused the v0.1 stem "differ", which matched "difference" | W6 | own pattern in the scorer; v0.1 system code unchanged |
| **Scorer bug**: typographic apostrophe (U+2019, "can’t") not matched by refusal patterns | R2 | answers normalised to ASCII quotes before matching |
| **Scorer bug**: "2,270.6%" split by the number reader into 2,270 and 6% | R5 (parse) | grouped decimals joined before reading numbers |
| **Scorer bug**: qualified-alternative cells carry no `metric`, so concept state could never be `qualified_alternative` | L1, L2 | alternative cells inherit the plan metric |
| Definition: `appropriate_refusal` read as "is a refusal" instead of "the refusal behaviour is right" | 26 slots | spec made explicit; scorer unchanged |
| Definition: evidence without `period_end` counted as the right period | E2 | spec: it does not; scorer unchanged |
| Definition: a gold fallback concept (`ProfitLoss`) expected as `qualified_alternative` | W2 | spec: it is `canonical`; scorer unchanged |
| Definition: `null` vs `n/a` for "does not apply" | R1, R2, R3 | runner treats them as equal (the instructions allowed both) |
| Calibrator arithmetic: 2,270.6% stated, exact change is 2,270.05% (outside 0.2 pt) | R5 (evidence) | scorer's `evidence_complete = false` is right |

Each scorer fix has a regression test in `tests/test_score_v2.py`.

## Run 2 (after the fixes)

All 30 targeted scores as designed (15 pass, 15 fail). Remaining field mismatches are only the
definition cases above (appropriate_refusal on answer items, W2 concept, E2 period, R5 evidence).

## Limits

The four fixes were made after reading these 30 slots, so run 2 is not an independent estimate of the
scorer's error rate on new wording. See the next step in the benchmark spec.
