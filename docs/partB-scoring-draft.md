# Part B scoring: draft for review (not implemented, not frozen)

Part B is a **case-study evaluation of v0.2 only**. Part A is the paired v0.1/v0.2 comparison. v0.1 may be
shown qualitatively on the cases; no structured extractor is added to it after the fact.

Packet format: `data/eval/v0.2/packet.schema.json` (draft). Every score below reads structured fields only;
nothing is parsed out of prose. A packet that fails the schema gets `packet_valid = false` and is still
scored on the fields that can be read (the scorer never crashes on malformed input).

Gold: `cases/<case>.numeric.json` (labels), `cases/provenance.json` (values, accessions, revisions),
`cases/revision_stability_controls.json`, `cases/AMD_FY2025_sga.json`, `item1a/protocol_v2/gold_item1a_v2_test.csv`.
Tolerances as Part A: 0.5% relative for amounts and shares, $0.01 for EPS, 0.1 pp for ratios and pp.

## Matching

- Numeric items match on the stable id `<case>:<metric>:numeric_change`; revision checks on
  `<case>:<metric>:<FY>:revision_control`. An id that is not in the gold is an **unknown item**: it never
  counts as a hit, and if its status is `large_numeric_change` it is a false positive.
- **Duplicates**: the first item with an id is scored; later items with the same id are counted as
  `duplicates` and ignored, so repeating a change cannot add recall. If a duplicate contradicts the first
  (different status or values outside tolerance), the item is scored as wrong (`inconsistent_duplicate`).
- An item counts as **value-correct** when every gold fact of both years (components of derived metrics
  included) appears in `facts` with the gold concept, period end and accession-or-earlier, and the value
  within tolerance; and the stated change fields agree with the gold (`percent_change` only for a positive
  base; `magnitude_only` with no percentage for two negative values).

## Scores (per case, and pooled over the three test cases; CSCO is dev)

| Score | Definition |
|---|---|
| large-change recall | gold `large_numeric_change` items whose packet item has status `large_numeric_change` **and is value-correct** / gold large items. `gray_zone` items are not in the denominator. *Detection recall* (status right, values not checked) is reported next to it. |
| large-change precision | packet items with status `large_numeric_change` whose gold label is `large_numeric_change` / packet items with that status. A `gray_zone`, `unchanged_control`, `expected_abstention` or unknown item reported as large is a false positive. |
| cross-year unchanged controls | false-positive rate on the gold `unchanged_control` items (NVDA 2, INTC 1): reported as large or gray. Descriptive only (n = 3). |
| revision stability | false-positive rate on the 59 stable revision controls: `revised = true`. |
| split recast recall | of the 8 stock-split re-presentations: `revised = true`, `cause = stock_split`, both values right. |
| AMD accounting recast | the 2 recast SG&A cells (FY2023, FY2024 in the FY2025 10-K): `revised = true`, `cause = accounting_recast`, values right. Micro-case, descriptive. |
| correct abstention | gold `expected_abstention` items with status `abstain` and the right `abstain_reason`. **Over-abstention** (abstain on an answerable item) is counted separately. |
| scope warning | gold items flagged `scope_warning`: `warnings` contains `scope`. |
| concept change | gold `concept_change` items: status `concept_change`, no change value stated. The three test cases have **no** gold concept_change item; only false `concept_change` claims can be counted (descriptive). |
| evidence completeness | every fact in the packet has accession, period end and concept, and matches the companyfacts row with that accession; and no fact is reported in a filing **after the target filing date** (look-ahead fails). |
| silent numeric errors | count of stated numbers (facts or change fields) outside tolerance of the gold with no warning on that item. Target 0. |
| packet validity | the packet validates against the schema. |

Item 1A is scored **separately** from the numeric packet; the two are never combined into one score.

## Item 1A (separate score)

- Matching: each packet `item1a_change` is mapped to the gold paragraph unit whose earlier/later text it
  best matches (the sentence-level match of `item1a_display.py`, threshold fixed before any run, proposed
  0.6). Unmatched packet items are false positives; several packet items on one unit count once.
- Precision / recall on gold `material_*` units (any material label counts as material; `ambiguous` units
  excluded from both); false-positive rate on gold `boilerplate` units. Label agreement among material
  sub-types (added / removed / modified) reported descriptively.
- Results are reported next to the gold provenance: 25 adjudicated, 75 cross-model agreed, 425 single-label
  units (precision and recall also given on the 100 doubly labelled units).

## Post-freeze real-output check for Part B

Separate from the Part A 80-record audit: the three test-case packets are reviewed by hand item by item,
without the scorer's scores, and agreement with the scorer is reported per score.

## Questions for the reviewer

1. Recall requires value-correct items (detection recall shown alongside). Agree, or recall on status only?
2. Item 1A matching by text similarity with a pre-fixed threshold (0.6), since a system cannot know the
   benchmark's unit ids. Agree, or require a paragraph locator in the packet?
3. Duplicate rule as above (first counts, contradicting duplicate makes the item wrong). Agree?
4. Look-ahead (a fact reported after the target filing) fails evidence completeness and, when its value
   differs from the as-of value, also counts as a silent numeric error. Agree?
5. Should an unchanged-control item reported as `gray_zone` count as a false positive, or only `large`?
