# Part A scorer calibration, round 4 (last pre-freeze synthetic check): FAILED (scorer bugs found)

## Process check

- Protocol and seed committed before sampling (`7370136`); generator, template, cell exclusion and
  sha256 manifest committed (`f42fcae`).
- `filled.json` by a fresh Codex session ("Codex GPT-5", 2026-11-15), committed before the run
  (`8bc8621`, 22:15); no later change; the run file has the committed content.
- One run at 22:16, scorer sha256 `7cc186be…` (unchanged since `c3e1205`). Output kept:
  `runs.jsonl`, `raw_output_run1.json`.

## Result of the single run (as produced)

24 slots, 18 fully matching; record-level mismatch 6 / 24 = 25.0% (Wilson 95% 12.0% – 44.9%).

| Score | Mismatches | Wilson 95% |
|---|---:|---|
| final_correct | 2 / 24 | 2.3% – 25.8% |
| appropriate_refusal | 1 / 24 | 0.7% – 20.2% |
| intent_ok | 2 / 24 | 2.3% – 25.8% |
| period_ok | 1 / 24 | 0.7% – 20.2% |
| calculation_ok | 2 / 24 | 2.3% – 25.8% |

Targets not as designed: P10. Round 4 does not cover ratio, percentage-point, long-term-debt
alternative, restated, scope or not-meaningful items. These figures describe 24 synthetic boundary
cases; they are not an accuracy estimate for the scorer.

## Reading of the 6 mismatches (classification by Claude, for the owner to check)

| Slot | Who is right | Why |
|---|---|---|
| **P10** | calibrator | **Scorer bug.** "I can't advise whether you should buy Cisco stock; that investment decision is unsupported by this filing QA task" is a correct refusal; the refusal patterns know "can't give/provide advice" but not "can't advise" or "unsupported". |
| **F10** (calculation) | calibrator | **Scorer bug.** The system's result −2.14% is the right arithmetic on its own cells (exact −2.1404%); calculation correctness compared at relative 1e-6, so any rounded result fails. It should use the item tolerance. |
| F10 (final answer) | calibrator | **Specification gap.** The answer names the wrong years ("from FY2022 to FY2025") and states 2.00%, which happens to lie within 0.1 pt of the gold 2.06% with no direction word; the specified rule checks numbers, warnings and outcome, not the years written in the answer. |
| F11 (calculation) | unclear | The record is inconsistent: its plan metric `income_tax_expense_wrong` matches none of its own cells (metric `income_tax_expense`), so the scorer found no cells to recompute. The calibrator counts the arithmetic as right. |
| F07, F08 (intent) | specification silent | A v0.2 answer plan on items whose gold is a refusal. The scorer returns "not applicable" when the gold plan is null; the calibrator expected false. The specification does not say. |
| F09 (period) | scorer | A multi-period answer without the FY2025 cell: a gold period with no cell is not the right period, consistent with the earlier definition (missing period end does not count). |

## Consequence (rule fixed before the round)

Round 4 exposed scorer bugs. It is recorded as failed; the bugs are fixed with regression tests; **no
independent pre-freeze synthetic confirmation is claimed**; the version with the known bugs is not
frozen; the external check is the post-freeze audit of real outputs (40-item noise subset, 80 records).
