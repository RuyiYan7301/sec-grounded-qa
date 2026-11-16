# v0.2 benchmark: specification (draft, not yet frozen)

The v0.2 benchmark was specified and frozen before the typed engine was implemented. This file is
the specification; the frozen artifacts and their hashes are listed in `data/eval/v0.2/manifest.json`.
It is a prospective frozen benchmark, not a blind test: the same people who wrote it build the system.
What makes it prospective is that questions, gold answers, labels and the scorer are fixed before any
v0.2 engine code exists, and no test output is used for tuning (the dev split is used for that).

Two parts:

| Part | What it tests | Systems | Value policy |
|---|---|---|---|
| A. Numeric QA | one question, one answer | v0.1 and v0.2, paired per question | `latest_in_snapshot` |
| B. Filing-change case studies | a change packet for one target 10-K | v0.2 only | `as_of_filing` |

Everything is built from the frozen ontology (`data/metric_ontology.yaml`, sha256 recorded in the
manifest) and the snapshot `SECQA_SNAPSHOT=2026-10-16`.

---

## Part A: numeric QA

### Layers and counts (test split)

| Layer | n | How items are made |
|---|---:|---|
| Generated factual | 80 | seeded sampling of ontology cells (ticker, metric, fiscal year) and intents; fixed templates |
| Handwritten paraphrases | 40 | new sampled plans, written in natural wording: synonyms, company labels ("net sales"), interpreted aliases ("EPS") |
| Adversarial / edge | 40 | hand-selected from the coverage report and the ontology's out-of-ontology list |
| **Total** | **160** | |

Generated factual, by intent: fact_lookup 20, multi_period_lookup 8, cross_company_comparison 10
(at least 5 with fiscal-year-end mismatch), absolute_change 10, percent_change 12 (at least 3 with a
zero or negative base, gold `not_meaningful`), percentage_point_change 8, ratio 6, restated_value_lookup 6.

The snapshot has only two accounting recasts outside stock splits (AMD SG&A for FY2023 and FY2024), so
restated_value_lookup items record a `revision_cause`: both recast cells are used (`recast`), the rest
are stock-split re-presentations (`stock_split`, NVDA and AVGO). Results are reported by cause.

Warnings: `required_warnings` decide correctness (period_mismatch on cross-company items whose period
ends differ by more than 31 days, scope for fallback concepts, restated on restated_value_lookup,
alias_interpretation when the question uses an interpreted alias such as plain "EPS", ambiguous_year).
`advisory_warnings` (e.g. a value revised since first reported) are scored separately as warning recall.

Handwritten paraphrases follow the same intent mix (scaled to 40). The plans are sampled first; the
wording is written afterwards from the plan alone. Each item records its author:

| Author | n | Rules |
|---|---:|---|
| `codex_assisted` (project owner, assisted by Codex) | 12 | written before any typed-engine code; sees only the frozen ontology and the gold plan; sees no system output |
| `claude_assisted` (Claude, which also builds the system) | 28 | same rules |

The other author only checks that a question is semantically valid for its plan; no question is
reworded to suit a system. Neither set is an independent external question set.

Adversarial / edge:

| Kind | n | Gold outcome |
|---|---:|---|
| out of ontology (EBITDA, total debt, segment revenue, quarterly) | 6 | `out_of_ontology` |
| not reported (e.g. ORCL gross profit, AAPL goodwill, MSFT SG&A, INTC FY2023 cash) | 8 | `not_reported` |
| fallback concept (AVGO FY2025 net income, NVDA capex, AVGO equity) | 6 | answer + scope warning |
| near-neighbour confounders (current vs total, restricted cash, basic vs diluted) | 6 | answer with the right concept |
| unsupported (advice, forecast, open-ended judgement) | 6 | `unsupported` |
| year out of range / bare calendar year | 4 | 2 `out_of_range` (MSFT FY2021, AAPL FY2026); 1 non-calendar filer (NVDA "2024") answered with required warning `ambiguous_year` (item `gold_outcome` is `ambiguous_year`, scored as an answer that must carry the warning); 1 December-year-end filer (INTC "2024") answered with no warning |
| cross-company per-share comparison | 2 | `unsupported_operation` |
| split-sensitive EPS change (NVDA, AVGO) | 2 | split-adjusted answer + basis recorded |

The year row was clarified on 2026-11-15 to describe the four existing items (adv-033 to adv-036); no
item, count or answer changed. INTC and NVDA form a pair: a bare year is ambiguous only for a filer whose
fiscal year does not end in December.

**Dev split**: 40 items about Cisco and Oracle only; the test split covers the other six companies.
Splitting by company (not by cell) is needed because derived metrics share components: a dev gross
margin would otherwise reuse a test revenue cell. Cisco and Oracle have no negative bases and no
revised values in FY2023-FY2025, so dev has no `not_meaningful` or restated items. Only dev outputs
may be inspected while building v0.2.

### Gold for each item (illustrative values)

```json
{
  "id": "A-gen-017",
  "layer": "generated",
  "question": "...",
  "gold_plan": {"intent": "percent_change", "metric": "research_and_development",
                "companies": ["NVDA"], "periods": ["FY2024", "FY2025"]},
  "gold_outcome": "answer",
  "gold_cells": [{"ticker": "NVDA", "metric": "research_and_development", "period": "FY2024",
                  "concept": "ResearchAndDevelopmentExpense", "value": 8675000000,
                  "accession": "...", "period_end": "2024-01-28"}],
  "gold_result": {"value": 0.4888, "unit": "ratio", "formula": "(v2 - v1) / v1"},
  "required_warnings": [],
  "tolerance": {"kind": "percent_points", "abs": 0.1}
}
```

Gold values are computed by a separate gold builder that reads the raw companyfacts JSON directly,
not through the fact store or the engine, so a bug in one is not copied into the other.

### Tolerances

| Unit | Tolerance |
|---|---|
| currency, shares | 0.5% relative (stated values are rounded) |
| percent change, margins | 0.1 percentage points absolute |
| percentage-point change | 0.1 pp absolute |
| EPS | $0.01 |

### Qualified alternatives (`qualified_alternatives.json`)

Written on 2026-11-15, before the scorer and before any run, for `long_term_debt` only (test: gen-032,
gen-053, han-005, han-030; dev: gen-010). The canonical gold stays `LongTermDebt` (current plus
noncurrent portion). The balance-sheet line titled "Long-term debt" is often the noncurrent portion
only (MSFT FY2024: 44,937 vs 42,688), so:

- An answer built entirely on `LongTermDebtNoncurrent` passes final-answer correctness only if it states
  explicitly that the figure is the noncurrent portion / excludes current maturities, and its numbers
  match the pre-registered alternative cells and result within the item's tolerance.
- A noncurrent figure without that statement is wrong.
- Every cell of one answer uses the same basis. Mixing total and noncurrent across companies or years is
  wrong. (For INTC FY2023 → FY2024 the two bases even give opposite signs: +1.51% vs −1.48%.)
- A percent change on consistent noncurrent values with the right formula passes calculation correctness.
- Concept resolution is three-state: `canonical`, `qualified_alternative`, `incorrect`. The headline
  concept-resolution accuracy counts only `canonical`; `qualified_alternative` may pass final-answer
  correctness and evidence completeness but is not a canonical concept hit. Counts of each are reported.
- The alternative values come only from this file (raw companyfacts through the gold builder, same
  period end and value policy). The scorer never looks for an alternative in a system's output.

### Scores (each reported separately, per layer)

| Score | v0.1 | v0.2 | Definition |
|---|:-:|:-:|---|
| final answer correctness | ✓ | ✓ | outcome matches gold, every gold number present within tolerance, no number contradicting gold, required warnings mentioned |
| appropriate refusal | ✓ | ✓ | on refusal items: no figure asserted for the requested metric and the answer says it is unavailable / unsupported; on answer items: no refusal |
| evidence completeness | ✓ | ✓ | every stated number traces to a tool result / evidence item with accession and period |
| plan schema validity | – | ✓ | the plan validates against the JSON Schema |
| intent accuracy | – | ✓ | plan intent equals gold intent |
| concept resolution | ✓¹ | ✓ | the concept used for every cell equals the gold concept |
| period selection | ✓¹ | ✓ | the period end used for every cell equals the gold period end |
| calculation correctness | – | ✓ | given the resolved cells, the computed result equals the gold result |

¹ For v0.1 read from the tool trace (the tags and periods it called `get_fact` / `compare` with).

### Scorer (`src/secqa/evaluation/v2/score.py`, version 2.0, draft until frozen)

Both systems are scored from the same record per item: final answer text, the evidence facts used
(ticker, metric, period, concept, value, accession, period end), and for v0.2 the plan (validated
against `data/eval/v0.2/plan.schema.json`) and the engine's computed result. v0.1 records are built
from its tool trace by an adapter. Rules, all fixed in code before any run:

- *Required numbers* by intent: fact lookup the value; multi-period and cross-company every value;
  restated lookup the current and the originally reported value; changes and ratios the result, plus
  the component amounts when the question asks for both ("both", "each", "give … figures").
- *Number matching* uses the item tolerance; signs are not read from numbers, so a negative change needs
  a decrease word or a minus sign, a positive change must not be described only as a decrease, and a
  negative amount needs "loss", "negative", a minus sign or parentheses.
- *Contradiction*: a stated amount within a factor of 2 of a gold amount but outside tolerance of every
  gold amount of the item makes the answer wrong.
- *Warnings*: each required warning is matched by a fixed pattern (`WARNING` in the scorer).
- *Refusal items*: an unavailable / unsupported statement (fixed patterns), no currency or share figure,
  and for advice questions no advice. *not_meaningful*: says so and states no percentage.
- *Evidence completeness*: every evidence item has accession and period end; every stated amount is an
  evidence value (or a difference of two, at any of the usual scales); every percentage is a ratio,
  change or difference of ratios of evidence values.
- *Concept resolution* (three states, see qualified alternatives), *period selection* (period end of each
  gold cell), *calculation correctness* (v0.2: the gold formula applied to the system's own cells
  reproduces its result).

Definitions made explicit after calibration run 1 (the scorer already behaved this way; the
calibrator's expectations differed because the text was ambiguous):

- `appropriate_refusal` is a score of the *behaviour*, true when the behaviour is right: on refusal
  items, refused correctly; on answer items, did **not** refuse. It is not a flag for "this is a refusal".
- `period_ok` needs the period end on the evidence; an evidence item without `period_end` does not
  count as the right period.
- `qualified_alternative` exists only for the cells listed in `qualified_alternatives.json`. A fallback
  concept that is the gold concept (e.g. AVGO FY2025 `ProfitLoss`, `use: fallback_with_warning`) is
  `canonical`; its scope is checked by the required `scope` warning.
- "Does not apply" is `null` or `n/a`; both mean the same.

Tests (`tests/test_score_v2.py`) build answers from the gold only: a correct answer for every test and
dev item scores correct, and wrong numbers, missing warnings, refusals with figures, advice, flipped
signs, percentages on a negative base, unqualified or mixed long-term-debt bases each fail.

Boundary rules (fixed by the project owner after calibration round 2, before round 3):

- A percentage-point result must be written in points or basis points ("0.3 percentage points",
  "0.3 pp", "0.3 ppts", "0.3 points", "30 basis points", "30 bps"). "Rose by 0.3%" states a relative
  change, a different quantity, and is wrong.
- Final-answer correctness judges only the answer the user sees. A wrong plan metric whose answer still
  states the right numbers is `final_correct = true` and `concept = incorrect`; intent, period and
  calculation are scored on their own. Only when the wrong concept also makes the stated numbers, basis
  or wording wrong is the final answer wrong too.
- An extra figure that no evidence supports makes `evidence_complete = false`. It makes the final
  answer wrong only if it contradicts the gold or a required conclusion.

Calibration of the text patterns. No test-split system output is read before the freeze.

- **Round 1, development calibration** (`data/eval/v0.2/calibration/`): 30 slots written by an isolated
  Codex session; four scorer bugs found and fixed, so it is development data.
- **Round 2, failed confirmation attempt** (`data/eval/v0.2/calibration_r2/`): 30 held-out slots; the
  single run crashed on malformed evidence (a scorer bug). Reported as failed, demoted to development
  data, bug fixed with regression tests. No accuracy figure is taken from it.
- **Scorer confirmation**: only the last calibration set that took no part in any fix is reported as
  the scorer confirmation (match count, record-level mismatch rate, mismatches per score, Wilson 95%
  interval). If a round exposes a scorer bug it is reported as failed, demoted, fixed, and a new unseen
  set follows; differences on the boundaries defined above are kept and do not change the scorer.

After the runs, a fixed-seed sample of scored test answers per system is checked by hand and the
scorer–hand disagreement rate is reported; the scorer is not changed after the freeze.

Paired reporting: a 2×2 table per layer (v0.1 right/wrong × v0.2 right/wrong) on final answer
correctness, with the item ids in each off-diagonal cell. McNemar's exact test is given as a
secondary statistic only.

Shared conditions: same model (`qwen3:8b`), temperature 0, snapshot, questions, scorer and output
constraints. v0.1 is run from tag `v0.1.0` in verify mode. The only difference is free tool calls
vs a validated typed plan executed by code. A full comparison takes about 4-6 hours (both systems).

Noise floor: a stratified subset of 40 test items (fixed in the manifest before any run) is run a
second time by each system. The run-to-run disagreement rate on that subset is reported next to every
v0.1/v0.2 difference; a difference smaller than the noise floor is not claimed.

---

## Part B: filing-change case studies

| Case | From → to | Target filing |
|---|---|---|
| NVDA | FY2024 → FY2025 | FY2025 10-K |
| INTC | FY2024 → FY2025 | FY2025 10-K |
| AVGO | FY2023 → FY2024 (VMware acquisition) | FY2024 10-K |
| micro-case: AMD SG&A | FY2024 value superseded in the FY2025 10-K | FY2025 10-K |
| dev case: CSCO | FY2023 → FY2024 (Splunk acquisition) | FY2024 10-K |

The AMD 10-K/A (filed 2026-02-04) is described as it is; no general amendment detection is claimed.
Only the CSCO dev case may be inspected while building v0.2. Three cases are a case-study
evaluation; no claim of generality across companies.

### Numeric gold (per case)

All 23 base and 5 derived metrics for the two fiscal years, `as_of_filing` (only values filed on or
before the target filing date). Each item gets one label, by a fixed rule written before labelling.
These are size labels, not a materiality judgement.

Size rule, applied only when both years resolve to the same concept and unit:

| Metric kind | `large_numeric_change` | `gray_zone` | `unchanged_control` |
|---|---|---|---|
| currency, shares, EPS, base > 0 | \|percent change\| ≥ 10% | 2% to 10% | < 2% |
| ratio (margins, R&D intensity) | \|change\| ≥ 2 pp | 0.5 to 2 pp | < 0.5 pp |
| both values < 0 | magnitude \|v2 − v1\| / \|v1\| ≥ 10% | 2% to 10% | < 2% |
| sign change, or base 0 | always | – | base 0 and unchanged |

`gray_zone` items are not scored: reporting or omitting them is accepted.

When both values are negative the magnitude is used for the size label only. The packet may state the
two values, the absolute change and the direction (`loss_narrowed` / `loss_widened`, or
`negative_value_narrowed` / `_widened` for non-earnings metrics), with `percent_change: null` and
`change_basis: magnitude_only`; it never states a percentage. Example: "Net loss narrowed from $18.756B
to $0.267B, an absolute improvement of $18.489B. A conventional percentage change is not meaningful
because the base value is negative."

Cross-year `unchanged_control` items are scarce in these cases (NVDA 2, INTC 1, AVGO 0): the numeric
no-change false-positive rate is descriptive only. It is not padded with other kinds of negatives.

### Revision stability controls (`revision_stability_controls.json`)

Each prior-year value as presented in the target 10-K, compared with the value first reported. These
test whether the system reports a revision where there is none; they are not cross-year controls.

| Group | n | Score |
|---|---:|---|
| stable (NVDA 19, INTC 22, AVGO 18) | 59 | revision_false_positive_rate |
| stock-split re-presentation (NVDA 4, AVGO 4) | 8 | split_recast_recall |
| accounting recast (AMD SG&A FY2023, FY2024, in the FY2025 10-K) | 2 | accounting_recast_recall (micro-case, descriptive) |

Cause classification (stock split vs accounting recast) is reported on the 10 revised values.

Other labels (take precedence over the size rule):

| Label | Rule |
|---|---|
| `concept_change` | the resolved concept differs between the two years; must be reported as a definition warning, not as a value change |
| `expected_abstention` | a component is not_reported or ambiguous_concept |
| `scope_warning` | resolved only through a fallback concept |
| `superseded_value` | a prior-year value in the target filing differs from the value first reported |

Before freezing, the label counts per case are published at 5% / 10% / 15% and 1 / 2 / 3 pp, so it
is visible whether the chosen thresholds happen to sit at a convenient cut.

### Item 1A gold (per case)

Unit of labelling: a changed paragraph unit, from a deterministic two-pass alignment of the two
Item 1A sections (`src/secqa/evaluation/v2/item1a.py`, parameters recorded in the manifest):

1. paragraphs are compared exactly (`difflib.SequenceMatcher(autojunk=False)`) to find unchanged ones;
2. inside each changed block, paragraphs are paired by a monotonic alignment maximising similarity
   (pairs need similarity ≥ 0.5). A pair is a `modified` unit; an unpaired paragraph is `removed` or `added`.

Before alignment, page furniture is dropped and a line that starts in lower case is joined to the
previous paragraph (page-break continuation). An added or removed paragraph that has a paragraph with
similarity ≥ 0.8 elsewhere on the other side is shown with that text (`moved_edited`). Sentence-level
blocks were tried first and rejected: whole rewritten sections became single blocks of up to 4,800 words.

Intel's section is found by title; its FY2024 10-K has no "Other Key Information" heading, so the
benchmark ends the section at the first "Other Key Information" or "Sales and Marketing" line. The
system's own splitter is unchanged (v0.1 indexes the longer section).

Every unit gets one label:

| Label | Meaning |
|---|---|
| `material_added` / `material_removed` / `material_modified` | a risk is introduced, dropped, or its substance changes (new jurisdiction, new restriction, new dependency, changed magnitude) |
| `boilerplate` | reordering, renumbering, date or cross-reference updates, rewording with the same substance |
| `ambiguous` | reasonable readers could disagree; excluded from precision and recall, reported separately |

Labels follow a written guideline (`data/eval/v0.2/item1a_guideline.md`). The labeller also builds the
system, so 50 test units, sampled with a fixed seed before any system output exists and stratified
by case and by a text-only provisional stratum (added, removed, moved, moved_edited, modified at high /
mid / low similarity; at least one per non-empty stratum), are labelled independently by a second
annotator, a classmate who has not seen the system or its outputs. The annotator gets the guideline
and a spreadsheet with the two texts, neighbouring context and the filing sources, and no labels.
Both annotators' raw labels are saved first; raw agreement and Cohen's kappa are computed on them;
only then are disagreements adjudicated and logged. Examples in the guideline come from the Cisco dev case.

How the first set of labels was made: all 525 test units and 66 dev units were labelled by Claude
(five parallel Claude sub-agents, one per case or half-case), each given only the guideline and its
batch of unit texts, with no strata, sample membership or other labels. The raw label files are kept
unchanged in `labels_claude/`. Claude's own review before seeing any second-annotator label is logged
separately (`labels_claude/self_review.json`): 5 added/removed units whose risk paragraph exists,
edited, elsewhere in the other filing were changed to `material_modified`. For the annotator the
closest paragraph on the other side is shown from similarity 0.6 (display only; strata still use 0.8).

**What was actually done (supersedes the "second annotator, a classmate" plan above).** No human second
annotator has labelled yet. The checks so far are cross-model agreement between Claude and an external
LLM (ChatGPT); they are not independent human annotation and are not reported as such.

- *Round 1, pilot (protocol v1).* ChatGPT labelled the 50-unit sample from the v1 packet and guideline
  (`labels_external/`: prompt, transcribed replies, labels, `agreement_round1.txt`). Against Claude's
  labels: 5-class agreement 0.54, Cohen's kappa 0.39; material vs boilerplate (ambiguous excluded, n = 47)
  agreement 0.62, kappa 0.33. 18 of the 23 disagreements were Claude `boilerplate` vs ChatGPT material.
  Causes found by reading them: the packet hid where merged or moved sentences went (Claude's labellers
  had seen the whole case, the packet showed only neighbours); one ChatGPT label judged a context paragraph
  (item 22, a comma change labelled `material_removed`); the guideline did not separate added from modified
  or name "may further increase"; and some real judgement differences (Claude was lenient on item 31 under
  the v1 rules; item 30 adds the VMware Merger). The model version of this run was not recorded at the time.
  The pilot result is kept as is.
- *Protocol v2* (`item1a/protocol_v2/`, locked in `protocol.json`, hashes asserted by
  `tests/test_item1a_protocol_v2.py`). Units, ids and round-1 files are unchanged. The packet marks
  **LABEL THIS** and **CONTEXT ONLY** columns and shows, for each side, the top 3 paragraphs of the other
  filing by sentence-level match, with score and position and no threshold
  (`src/secqa/evaluation/v2/item1a_display.py`, display only). Guideline v2 adds the merge / move and
  added-vs-modified rules (its last section lists each change and the pilot item behind it).
- *Two v2 packets.* `retest`: the 50 pilot units. Because the v2 rules were written after reading their
  disagreements, this only tests whether the repair works and is reported as a protocol-repair retest.
  `confirm`: 50 new test units drawn with the same stratification and a new seed (1115), excluding the
  pilot units; its agreement is the confirmation result. Both are labelled from the same packet by fresh
  Claude sub-agents (guideline and packet only) and by ChatGPT (new chat per packet, `prompt_v2.md`).
  Agreement is computed on raw labels before adjudication, and no rule changes after it is computed.
- The full 525-unit gold was labelled under v1 with whole-case context. If v2 is kept, it is relabelled
  under v2 before the benchmark freeze; the v1 files stay as they are.

### Scores (per case and pooled)

- numeric: recall and precision on `large_numeric_change`, false-positive rate on `unchanged_control`,
  `concept_change` reported as a definition warning
- evidence completeness: every packet item carries accession, concept, period, value policy and formula
- correct abstention on `expected_abstention` items; scope warning present on `scope_warning` items
- silent numeric errors: any packet number that is wrong and carries no warning (target 0)
- Item 1A: recall and precision on material hunks, false-positive rate on boilerplate hunks

---

## Freeze manifest (`data/eval/v0.2/manifest.json`)

```json
{
  "benchmark": "secqa-v0.2",
  "frozen_on": "YYYY-MM-DD",
  "git_commit": "...",
  "snapshot": "2026-10-16",
  "ontology": {"path": "data/metric_ontology.yaml", "sha256": "..."},
  "fact_store_sha256": "... (hash of the canonical JSON dump of the store)",
  "generator": {"path": "src/secqa/evaluation/v2/gen_qa.py", "sha256": "...", "seed_test": 0, "seed_dev": 0},
  "gold_builder": {"path": "...", "sha256": "..."},
  "scorer": {"path": "...", "version": "2.0", "sha256": "..."},
  "alignment": {"sentence_split": "...", "min_sentence_chars": 30, "sha256": "..."},
  "files": {"qa_test.json": "sha256", "qa_dev.json": "sha256", "cases/NVDA_FY2025.json": "sha256"},
  "counts": {"A_test": {"generated": 80, "handwritten": 40, "adversarial": 40}, "A_dev": 40,
             "B": {"NVDA": {"numeric": 28, "item1a_hunks": 0}}},
  "pass_criteria": "see docs/benchmark-v0.2.md, section Scores"
}
```

A test asserts every hash in the manifest, so a frozen file cannot change silently.
