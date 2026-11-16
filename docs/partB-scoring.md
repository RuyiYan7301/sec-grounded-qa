# Part B scoring (scorer `src/secqa/evaluation/v2/partb_score.py`, version 1.0; to be locked)

Part B is a **case-study evaluation of v0.2 only**; Part A is the paired v0.1/v0.2 comparison. v0.1 may be
shown qualitatively on the cases; no structured extractor is added to it after the fact.

Packet format: `data/eval/v0.2/packet.schema.json` (draft 3; conditional rules tested in
`tests/test_packet_schema.py`, validated with the JSON Schema date format checker). Every score reads structured fields only; nothing is parsed out of prose.
A packet that fails the schema gets `packet_valid = false` and is still scored on the fields that can be
read; the scorer never crashes on malformed input.

Gold: `cases/<case>.numeric.json` (labels), `cases/provenance.json` (per-value facts and accessions),
`cases/revision_stability_controls.json`, `cases/AMD_FY2025_sga.json`, `partB/item1a_locators.json` and
`item1a/protocol_v2/gold_item1a_v2_test.csv`. Tolerances as Part A: 0.5% relative for amounts and shares,
$0.01 for EPS, 0.1 pp for ratios and pp. The three test cases are NVDA, INTC, AVGO; CSCO is dev.

Gold provenance, as it may be described: 258 case values were automatically located in their cited 10-K
texts; 16 randomly sampled contexts (seed 2027) were read by hand. All 69 revision controls have their
first-reported value located in the first-reporting filing's text.

## Packet metadata

`packet_metadata_ok` checks case, ticker, from/to fiscal year, target filing accession and filed date and
`value_policy` against the gold. If any is wrong, no item of the packet can hit the gold. Item ids must
carry the packet's case (and metric, and period for revision checks); a mismatching id is an unknown item.

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
| revision stability | revision checks have three states, `stable`, `revised`, `no_prior_observation`. False-positive rate on the **57** stable controls: reported `revised` (or an inconsistent duplicate). An omitted stable control is not a false positive; a `stable` claim must give both `first_reported` and `as_presented` with the gold accessions and equal values, otherwise it is counted under `stable_claims_without_two_sided_evidence`. The 2 `no_prior_observation` items are not scored. |
| split recast recall | of the 8 stock-split re-presentations: `status = revised`, `cause = stock_split_recast`, both facts value-correct with the gold accessions. |
| AMD accounting recast | the 2 recast SG&A cells (FY2023, FY2024 in the FY2025 10-K): `status = revised`, `cause = accounting_recast`, facts right. Micro-case, descriptive. |
| correct abstention | gold `expected_abstention` items with status `abstain` and the right `abstain_reason`. **Over-abstention** (abstain on an answerable item) counted separately. |
| scope warning | gold items flagged `scope_warning` whose packet item has `scope` in `warnings`. |
| concept change | gold `concept_change` items: status `concept_change`, no change values. The three test cases have **no** gold concept_change item; false `concept_change` claims are counted, descriptively. |
| evidence completeness | three levels on matched items: **fact-level** (packet facts with accession, filed, period end and concept matching the gold, not look-ahead), **item-level** (reported items whose fact set is exact and every fact passes), **packet-level all-pass** (every reported item passes; **N/A** for a packet with no assertion). A missing large change costs recall, not evidence. |
| silent numeric errors | count of stated numbers (facts or change fields) **of items that match a gold id** outside tolerance of the gold; a look-ahead fact with a different value adds one more. **No warning offsets an error.** Target 0. |
| unknown items | `unknown_item_count`: ids not in the gold. A false prediction in precision; no numeric accuracy is computed for them. |
| packet validity | the packet validates against the schema. |

## Item 1A (scored separately; never combined with the numeric score)

- Packets give paragraph **locators**, not benchmark unit ids: accession, section `1A`, paragraph index in
  the benchmark segmentation (`item1a.paragraphs()`), SHA-256 of the normalised paragraph text, optional
  quote. Gold locators: `partB/item1a_locators.json` (built with the same segmenter; 12 unit sides have a
  paragraph text that occurs more than once in its filing, so index **and** hash must both match).
- **Locator first, label second.** Each locator a packet item gives is mapped to a gold unit (accession,
  paragraph index and text hash must all match). If its two locators map to different units the item is
  `inconsistent`; if none maps it is unmatched. Only then is the unit's gold label consulted. The
  predicted sub-type never decides whether a change was found. Text similarity is only shown to a human
  reviewer; it never decides a score. The gold unit is a paragraph unit.
- **Locator completeness** is reported separately and judged by the gold unit type (`added` needs the
  later locator, `removed` the earlier, `modified` both), not by the predicted label: a paragraph moved
  with new substance is `material_modified` on a one-sided unit (93 test units), so the schema only
  requires at least one locator for `material_modified`.
- Several predictions on one unit with the same label fold into one; with **different labels** the unit is a
  `conflicting_duplicate` (a wrong prediction, not a hit). Unmatched and inconsistent items are wrong
  predictions.
- On all 525 test units: precision and recall on material units (any `material_*`; `ambiguous` excluded),
  boilerplate false-positive rate, sub-type agreement, locator completeness, with Wilson 95% intervals for
  precision and recall. On the 100 doubly labelled units only recall, boilerplate false-positive rate and
  sub-type agreement (precision is not defined on a subset, since unmatched predictions belong to none).

Every proportion is stored with its numerator and denominator; main precision and recall carry Wilson 95%
intervals. The three cross-year unchanged controls stay descriptive (n = 3).

## Tests

`tests/test_partb_score.py`: the reference packet built from the gold scores full marks on CSCO (dev) and
the three test cases and is schema-valid; mutations (empty packet, wrong metadata, identical and
conflicting duplicates in either order, look-ahead with equal and different values, another accession,
extra fact, warning on a wrong value, unknown and wrong-case ids, gray on an unchanged control, missing
scope warning, stable reported revised, stable without first report, omitted stable control, wrong split
cause, locators on two units, wrong sub-type, conflicting duplicate labels, unmatched locator, one-sided
locator on a modified unit, malformed packets) cost exactly what the rules above say.

## Post-freeze real-output check for Part B

Separate from the Part A 80-record audit: the three test-case packets are reviewed by hand item by item,
without the scorer's scores, and agreement with the scorer is reported per score.
