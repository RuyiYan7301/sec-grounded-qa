# Item 1A change detection, v0.3 (post-hoc work after the v0.2 freeze)

Written before any v0.3 method is tried. The frozen v0.2 engine, benchmark, scorers and test results are
not changed; v0.3 is reported separately as post-hoc work.

## Why

On the v0.2 test cases the Item 1A classifier marks many wording-only (boilerplate) changes as material:
boilerplate FPR 30/54 (NVDA), 19/73 (INTC), 70/121 (AVGO); precision 50/82, 50/71, 76/151. The numeric
change engine is not touched.

## Data

- **Development** (all of it may be looked at freely, and is reported as development data only): CSCO
  FY2023→FY2024 (dev gold), and NVDA FY2024→FY2025, INTC FY2024→FY2025, AVGO FY2023→FY2024 (the 525 v0.2
  test units; their results have been seen, so they are development data for v0.3).
- **Held-out test**: two new company-year pairs never used for Item 1A labelling or tuning, chosen below
  before any label or run exists for them. Gold is made with the frozen v0.2 annotation protocol:
  - units: `src/secqa/evaluation/v2/item1a.py` (unchanged; sha256 recorded in protocol_v2/protocol.json);
  - display: `src/secqa/evaluation/v2/item1a_display.py` (unchanged), guideline `item1a_guideline_v2.md`
    (unchanged);
  - labeller: fresh Claude sub-agents given only the guideline and one packet, as in v0.2; labels are
    written before any v0.3 or v0.2 run on these pairs, and committed with their sha256;
  - optional second labeller: ChatGPT with `prompt_v2.md`, run by the project author on a seeded sample;
    if done, agreement is reported as cross-model agreement, not human annotation.
  - The gold is Claude-labelled and v0.3 is developed with Claude's help; this is a known limitation and is
    stated with every held-out figure.

## Held-out reference: multi-model consensus (added 2026-11-16, before any held-out run)

The reference is made by model families other than the system's (the system is qwen3:8b), none of which
sees system outputs or scores:

1. **Labeller A, Claude**: the five packets above (done, `labels_claude/`, committed before any run).
2. **Labeller B, Gemini** (ChatGPT was planned but had no credit): the same five packets, each in its own new chat (memory and custom
   instructions off), guideline v2 and `prompt_v2.md` verbatim except the item counts (`prompts_labeller_b.md`), run by the project author; raw replies
   saved unchanged, model name and date recorded. Replaces the 50-unit second-labeller sample
   (`packet_second_labeller.csv` is kept but not used).
3. **Agreement**: 5-class raw agreement and Cohen's kappa, and material-vs-boilerplate kappa, on all 206
   units, computed on the raw labels before any adjudication.
4. **Adjudicator, a third model family** (not Claude, not Gemini, not Qwen): only for units where A and B
   disagree. It sees the guideline, the unit as displayed in the packet, and the two labels as "label 1"
   and "label 2" in random order (no model names), and picks one of them or `ambiguous`.
5. **Reference labels**: agreed units take the agreed label (`high confidence`); disagreed units take the
   adjudicated label (`adjudicated`). Units adjudicated `ambiguous` are left out of material and
   boilerplate sets, as in the v0.2 scoring.
6. **Reporting**: every held-out figure is given on the full consensus reference and, separately, on the
   high-confidence (A = B) subset. It is called a **multi-model consensus evaluation**, not human
   validation. Raw labels of every model, the agreement and the adjudication log are kept.

If labeller B or the adjudicator is not available, the held-out result is reported against the Claude
labels only and called a single-model reference.

## Systems

- **v0.2** (frozen `item1a_changes.py` at tag `v0.2-engine-freeze`), qwen3:8b.
- **v0.3** (the method chosen on development data), qwen3:8b.
- **v0.3 with qwen3:14b**, as a reference only (how much a bigger model adds); never the reported system.
Same Ollama version and options for all; each runs once on the held-out pairs after the v0.3 freeze.

## Metrics (held-out, pooled over the two pairs, scored with the frozen Part B Item 1A rules)

- **Primary**: boilerplate false-positive rate, v0.3 vs v0.2 on the same units (paired; exact McNemar on
  boilerplate units flagged by one system and not the other).
- **Guard**: material recall of v0.3 not more than 5 percentage points below v0.2's. If the guard fails, the
  result is reported as "FPR lower at a recall cost", not as an improvement.
- **Secondary**: precision with Wilson 95% intervals, sub-type agreement, locator completeness, model calls
  and time.

## Development procedure

- Candidate methods (tried on development data, each logged with its numbers, kept or not):
  1. word-level diff shown to the classifier (deleted and inserted words marked by code);
  2. the classifier first quotes each substantive change, and may only answer material if it quotes one;
  3. moved paragraphs: an added and a removed paragraph that are near copies of each other are classified
     as one pair (the same check the v0.2 context step already computes);
  4. combinations of the above.
  5. (added 2026-11-16 after reading v0.2 errors on development data, before any v0.3 result) "diff_small":
     as "diff", but a candidate whose code diff (pair, or one-sided against its matched paragraph) changes
     at most K words in total and no word containing a digit is boilerplate without a model call. K is
     chosen on development data from {1, 2, 3, 4, 5} by the same selection rule, and fixed before the
     held-out run. Evaluated offline on the "diff" run's model outputs (same labels for every candidate
     the rule does not touch).
- Selection rule on development data, pooled over the four cases: lowest boilerplate FPR among the
  candidates whose recall is within 5 pp of v0.2's on the same cases.
- Every variant tried is kept in `results/dev/item1a_v03/` with its prompt hash; nothing is dropped.
- v0.3 is frozen (tag) before the held-out pairs are run.

## Held-out pairs

Rule: companies outside the development data (so not NVDA, INTC, AVGO, CSCO), the latest fiscal year
pair available in the snapshot. Unit counts of all candidates were looked at (MSFT FY26 81, ORCL FY26 125,
AMD FY25 122, AAPL FY25 75), no labels or runs. Chosen:

- **MSFT FY2025→FY2026**: 81 units (46 modified, 26 added, 9 removed), filings 0000950170-25-100235 →
  0001193125-26-323660.
- **ORCL FY2025→FY2026**: 125 units (57 modified, 60 added, 8 removed), filings 0000950170-25-087926 →
  0001193125-26-277521.

Built by `src/secqa/evaluation/v03_item1a_heldout.py` with the frozen v0.2 unit, display and locator code
(hashes in `data/eval/v0.3/item1a/manifest.json`, equal to those in protocol_v2/protocol.json). Labeller
packets: 5 parts of at most 45 units, in unit order. Each part is labelled by its own fresh Claude
sub-agent that sees only the guideline and that part, output columns as in v0.2
(item, hunk_id, label, confidence, note).
