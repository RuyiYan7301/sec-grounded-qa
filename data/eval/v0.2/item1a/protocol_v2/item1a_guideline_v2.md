# Item 1A change labelling guideline, v2 (v0.2 benchmark)

v2 replaces v1 (`data/eval/v0.2/item1a_guideline.md`, kept unchanged) for all labelling from protocol v2 on.
What changed and why is listed at the end. v2 was written after reading the round-1 (pilot) disagreements.

You will read short pieces of the "Risk Factors" section (Item 1A) of two consecutive annual reports
(10-K) of the same company, and decide for each piece whether the change between the two years is
**material** (the disclosed risk itself changed) or **not material** (the wording or place changed but
the risk did not).

You do not need finance training. Read each piece on its own, decide, and move on. A piece should take
one to two minutes. Please do not look at any other labels, and do not discuss items with anyone before
you have finished; afterwards, disagreements are compared and discussed.

## What you see for each item

Columns starting with **LABEL THIS** are the text you judge. Columns starting with **CONTEXT ONLY** are
there to help you understand it; never label their content.

| Column | Meaning |
|---|---|
| company, earlier_filing, later_filing | which two reports are compared, with links if you want the full text |
| position of the text to label | where the piece sits in each report (paragraph number of total) |
| CONTEXT ONLY - paragraph before / after | unchanged neighbouring paragraphs |
| **LABEL THIS - EARLIER TEXT** | text in the earlier report that was removed or changed (`(none: text added)` if new) |
| **LABEL THIS - LATER TEXT** | text in the later report that was added or changed (`(none: text removed)` if dropped) |
| CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3) | the three paragraphs of the later report whose sentences best match the EARLIER TEXT |
| CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3) | the three paragraphs of the earlier report whose sentences best match the LATER TEXT |

How to read the "where ... may be" columns. Each candidate shows a match score and its position.
The score is the share of the piece's text (by characters, sentence by sentence) that the candidate
paragraph reproduces: 1.00 means every sentence appears there verbatim. **Two unrelated paragraphs
typically score 0.30 to 0.45**, so a score in that range means "no real match"; it does not mean the
text moved there. A high score means the sentences are found in that paragraph, possibly merged with
other text. Read the candidate before relying on it: the score measures wording, not meaning. When an
item is a changed paragraph (both EARLIER and LATER TEXT shown), its paired paragraph is not repeated
among the candidates.

Judge only the change between EARLIER TEXT and LATER TEXT. Do not judge whether the risk is important
for the company in general.

## Labels (write exactly one in the `label` column)

### `material_added`
A risk proposition that is **not disclosed anywhere** in the earlier report appears in the later one.
Use it only when the earlier report has no paragraph that states this risk (check the "where the LATER
TEXT may come from" column). A risk proposition is the claim "X could (or did) harm us because of Y".

### `material_removed`
A risk proposition that was disclosed in the earlier report is **no longer disclosed anywhere** in the
later one. Check the "where the EARLIER TEXT may be" column first: if the same content appears there,
it was not removed.

### `material_modified`
The same risk is still disclosed (here or, after a move, elsewhere), but what is said about it changed
in substance:
- scope: more or fewer products, markets, countries, customers, suppliers, laws;
- status or likelihood: "could" became "has", a proposal became law, a pending matter was resolved,
  or a statement that something may happen (again, further, more) was added or dropped;
- size: a number, a share, an amount;
- exposure: how the company is affected or protected (for example insurance, hedging, contracts);
- **a new fact or event added to an existing risk** (a named acquisition, lawsuit, conflict, rule).
  Write `added_claim` in the note.

### `boilerplate`
The change does not alter what risk is disclosed or how large, likely or broad it is. Typical cases:
- rewording with the same meaning ("adverse effect" → "negative impact", sentences reordered)
- **merged, split or moved text whose content is still fully present** in the other report and whose
  risk proposition is unchanged (the "where ... may be" column shows where it went)
- a date, fiscal year or cross-reference updated with no change in substance ("fiscal 2023" → "fiscal 2024"
  in an otherwise identical sentence)
- punctuation, formatting, numbering, headings rephrased, list items split or joined
- a summary bullet that repeats a heading or risk stated elsewhere in the same report

### `ambiguous`
Reasonable readers could disagree, or you cannot tell from the text shown. Use it honestly rather than
guessing; it is not a failure. Add a short note saying why.

## Decision order

1. Read the two LABEL THIS columns. If they differ only in punctuation, formatting or wording with the
   same meaning → `boilerplate`.
2. If text was removed, merged or moved: is its content fully present elsewhere on the other side?
   - present, nothing substantive added or dropped → `boilerplate`;
   - present, but a new event, scope, status, likelihood or exposure was added or dropped → `material_modified`.
3. Is this a risk proposition that the earlier report does not state anywhere? → `material_added`.
4. Is a risk proposition gone from the later report entirely? → `material_removed`.
5. Same risk, but scope, status, likelihood, size or exposure changed, or a new fact or event was added?
   → `material_modified` (note `added_claim` for a new fact or event).
6. Only wording, order, dates or formatting changed? → `boilerplate`.
7. Still unsure → `ambiguous` with a note.

When a piece contains both a material change and boilerplate edits, label it by the material change.
When part of a removed paragraph is found elsewhere and part is not, label by the part that is not
(if that part states a risk, `material_removed` or `material_modified`; if it is only wording, `boilerplate`).

## Confidence (1-3)

1 = a guess, 2 = fairly sure, 3 = sure.

## Examples (from a company that is not in the labelled set)

These examples come from Cisco's FY2023 → FY2024 reports, which are only used for development.

1. EARLIER: "...could have an adverse effect on our operating results."
   LATER: "...could have a negative impact on our operating results."
   → `boilerplate` (same meaning, different words).

2. EARLIER: "In particular, if our model of the evolution of networking does not emerge as we believe it will..."
   LATER: "In particular, if our model of the evolution of networking, security, or observability does not emerge..."
   → `material_modified` (the scope of the strategic risk widened from networking to security and observability).

3. EARLIER: (none: text added)
   LATER: "In recent years, we have shifted our business model to deliver more recurring software and subscription
   offerings. This shift in our business model was accelerated by recent acquisitions, including our acquisition of
   Splunk in the third quarter of fiscal 2024..."
   → `material_added` if the earlier report states no risk about the shift to subscription offerings;
   `material_modified` with note `added_claim` if it does and only the Splunk acquisition is new.
   Check the "where the LATER TEXT may come from" column to decide.

4. EARLIER: "Acquisitions may also cause us to:"
   LATER: "Acquisitions have in the past and may in the future also cause us to:"
   → `material_modified` (status: the company now says these effects have already happened, not only that they
   could). By the rules above a "could" → "has" change counts as material even when it reads like legal caution.

## What to hand back

The same spreadsheet with `label`, `confidence (1-3)` and, where useful, `note` filled in. Do not change
any other column.

## Changes from v1

| Change | Reason (round-1 pilot) |
|---|---|
| LABEL THIS / CONTEXT ONLY column names | one external-model label judged a context paragraph instead of the piece (item 22) |
| top-3 "where ... may be" candidates with scores, no threshold; the v1 column showed one paragraph only from similarity 0.6 | merged or moved sentences looked deleted to a labeller who saw only the neighbouring paragraphs |
| merged / split / moved with content fully present → `boilerplate`; moved plus new substance → `material_modified` | the pilot labellers treated merges inconsistently |
| `material_added` only for a risk proposition absent from the whole earlier report; a new fact or event in an existing risk → `material_modified`, note `added_claim` | added vs modified was the second largest source of disagreement |
| "may further increase" type additions named under status or likelihood | v1 named "could → has" only; the pilot split on "have increased" → "have increased and may further increase" |
| partly found removed paragraphs: label by the part not found | not covered by v1 |
| example 3 rewritten to depend on the earlier report | under the new `material_added` rule the v1 answer is conditional |
