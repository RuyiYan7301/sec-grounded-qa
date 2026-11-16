# Part B scoring: draft 2 for review (not implemented, not frozen)

Part B is a **case-study evaluation of v0.2 only**; Part A is the paired v0.1/v0.2 comparison. v0.1 may be
shown qualitatively on the cases; no structured extractor is added to it after the fact.

Packet format: `data/eval/v0.2/packet.schema.json` (draft 2; conditional rules tested in
`tests/test_packet_schema.py`). Every score reads structured fields only; nothing is parsed out of prose.
A packet that fails the schema gets `packet_valid = false` and is still scored on the fields that can be
read; the scorer never crashes on malformed input.

Gold: `cases/<case>.numeric.json` (labels), `cases/provenance.json` (per-value facts and accessions),
`cases/revision_stability_controls.json`, `cases/AMD_FY2025_sga.json`, `partB/item1a_locators.json` and
`item1a/protocol_v2/gold_item1a_v2_test.csv`. Tolerances as Part A: 0.5% relative for amounts and shares,
$0.01 for EPS, 0.1 pp for ratios and pp. The three test cases are NVDA, INTC, AVGO; CSCO is dev.

Gold provenance, as it may be described: 258 case values were automatically located in their cited 10-K
texts; 16 randomly sampled contexts (seed 2027) were read by hand. All 69 revision controls have their
first-reported value located in the first-reporting filing's text.

## Matching and value correctness (numeric)

- Numeric items match on the stable id `<case>:<metric>:numeric_change`; revision checks on
  `<case>:<metric>:<FY>:revision_control`. An id not in the gold is an **unknown item**: never a hit, and
  if reported as `large_numeric_change` a false prediction in precision.
- **Duplicates, by id group** (order never matters): identical items with the same id are folded into one
  and `duplicate_count` is recorded. If items with one id differ in status, values or evidence, the whole
  id is `inconsistent_duplicate`: it is not a recall hit and counts as one wrong prediction in precision.
  Repetition never adds to a denominator or to recall.
- **Expected fact set.** For each gold item the expected facts are the gold values of both years
  (components of derived metrics, with `component_of`). An item is **value-correct** only if its facts are
  exactly that set (no fact missing, no extra fact) and every fact has the gold concept, period end, value
  within tolerance, and **the gold reported-in accession**, which for every case value is the target
  filing; the change fields agree with the gold (`percent_change` only for a positive base; `magnitude_only`
  with no percentage for two negative values; `pp_change` for ratios; direction matching the gold).
- **Accession rule.** A fact from any other filing than the gold accession is not value-correct, even with
  the same value. A fact from a filing **after** the target filing date (look-ahead) fails evidence; if its
  value also differs from the as-of value it is in addition a silent numeric error. For revision checks the
  `first_reported` fact must carry the gold first-reported accession.

## Scores (per case, and pooled over the three test cases)

| Score | Definition |
|---|---|
| **verified recall** (main) | gold `large_numeric_change` items whose packet item has status `large_numeric_change` and is value-correct / gold large items. `gray_zone` items are not in the denominator. |
| **verified precision** (main) | packet items with status `large_numeric_change` whose gold label is `large_numeric_change` **and** that are value-correct / packet items with that status (inconsistent duplicates and unknown items included as wrong). A gray, unchanged, abstention or unknown item reported as large is wrong. |
| detection recall / precision (diagnostic) | the same on status labels only, values not checked. |
| cross-year unchanged controls | gold `unchanged_control` items (NVDA 2, INTC 1) reported as `large_numeric_change` **or** `gray_zone` are control false positives. An item reported `unchanged_control` with wrong numbers is not a control false positive but counts in evidence and silent errors. Descriptive only (n = 3). |
| revision stability | false-positive rate on the **57** stable controls (prior observation equal to the value as presented): `revised = true`. The 2 `no_prior_observation` items are not scored. |
| split recast recall | of the 8 stock-split re-presentations: `revised = true`, `cause = stock_split_recast`, both facts value-correct with the gold accessions. |
| AMD accounting recast | the 2 recast SG&A cells (FY2023, FY2024 in the FY2025 10-K): `revised = true`, `cause = accounting_recast`, facts right. Micro-case, descriptive. |
| correct abstention | gold `expected_abstention` items with status `abstain` and the right `abstain_reason`. **Over-abstention** (abstain on an answerable item) counted separately. |
| scope warning | gold items flagged `scope_warning` whose packet item has `scope` in `warnings`. |
| concept change | gold `concept_change` items: status `concept_change`, no change values. The three test cases have **no** gold concept_change item; false `concept_change` claims are counted, descriptively. |
| evidence completeness | reported at three levels: **fact-level** (share of packet facts with accession, filed, period end and concept that match the gold row for that accession and are not look-ahead), **item-level** (share of items whose every fact passes), and **packet-level all-pass** (every item passes). |
| silent numeric errors | count of stated numbers (facts or change fields) outside tolerance of the gold. **No warning offsets an error**: a `scope` or `concept_change` warning does not make a wrong value right. Target 0. |
| packet validity | the packet validates against the schema. |

## Item 1A (scored separately; never combined with the numeric score)

- Packets give paragraph **locators**, not benchmark unit ids: accession, section `1A`, paragraph index in
  the benchmark segmentation (`item1a.paragraphs()`), SHA-256 of the normalised paragraph text, optional
  quote. Gold locators: `partB/item1a_locators.json` (built with the same segmenter; 12 unit sides have a
  paragraph text that occurs more than once in its filing, so index **and** hash must both match).
- A gold unit is hit by a packet item when: `added` unit, the packet's later locator equals the unit's
  later locator; `removed`, the earlier locators are equal; `modified`, **both** are equal. Text
  similarity is only shown to a human reviewer as the closest unit; it never decides a score. (The gold
  unit is a paragraph unit, not a sentence.)
- Several packet items on one unit count once; packet items that hit no unit are false positives.
- Precision / recall on gold material units (any `material_*`; `ambiguous` excluded from both), false-
  positive rate on `boilerplate` units; material sub-type agreement descriptive. Reported on all 525 test
  units and on the 100 doubly labelled units (25 adjudicated, 75 cross-model agreed).

## Post-freeze real-output check for Part B

Separate from the Part A 80-record audit: the three test-case packets are reviewed by hand item by item,
without the scorer's scores, and agreement with the scorer is reported per score.
