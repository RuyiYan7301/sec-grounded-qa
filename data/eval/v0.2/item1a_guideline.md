# Item 1A change labelling guideline (v0.2 benchmark)

You will read short pieces of the "Risk Factors" section (Item 1A) of two consecutive annual reports
(10-K) of the same company, and decide for each piece whether the change between the two years is
**material** (the disclosed risk itself changed) or **not material** (the wording changed but the risk
did not).

You do not need finance training. Read each piece on its own, decide, and move on. A piece should take
one to two minutes. Please do not look at any other labels, and do not discuss items with anyone before
you have finished; afterwards, disagreements are compared and discussed.

## What you see for each item

| Column | Meaning |
|---|---|
| company, earlier_filing, later_filing | which two reports are compared, with links if you want the full text |
| context_before / context_after | unchanged neighbouring paragraphs, only to help you understand the piece |
| EARLIER TEXT | text in the earlier report that was removed or changed (`(none: text added)` if new) |
| LATER TEXT | text in the later report that was added or changed (`(none: text removed)` if dropped) |
| closest text elsewhere in the other filing | if the text was added or removed, the most similar paragraph anywhere in the other report, when one exists. If it says the same thing, the text probably just moved |

Judge only the change between EARLIER TEXT and LATER TEXT. Do not judge whether the risk is important
for the company in general.

## Labels (write exactly one in the `label` column)

### `material_added`
A risk, or a substantive part of one, appears that was not disclosed before. Examples of substance:
a new country, regulation, export rule or sanction; a new product line, customer, supplier or
dependency; a new event (an acquisition, a lawsuit, an incident); a new quantitative fact.

### `material_removed`
A risk, or a substantive part of one, that was disclosed before is no longer disclosed anywhere.
Check the "closest text elsewhere" column first: if the same content appears there, it was not removed.

### `material_modified`
The same risk is still discussed, but what is said about it changed in substance: its scope (more or
fewer products, markets, countries), its likelihood or status ("could" became "has", a proposal became
law, a pending matter was resolved), its size (a number, a share, an amount), or the company's
exposure to it.

### `boilerplate`
The change does not alter what risk is disclosed or how large or likely it is. Typical cases:
- rewording with the same meaning ("adverse effect" → "negative impact", sentences reordered or merged)
- the text moved to another place, with or without light editing
- a date, fiscal year or cross-reference updated with no change in substance ("fiscal 2023" → "fiscal 2024"
  in an otherwise identical sentence)
- formatting, numbering, headings rephrased, list items split or joined
- a summary bullet that repeats a heading elsewhere

### `ambiguous`
Reasonable readers could disagree, or you cannot tell from the text shown. Use it honestly rather than
guessing; it is not a failure. Add a short note saying why.

## Decision order

1. Is the same content present on the other side (same paragraph, or the "closest text" says the same)?
   If yes and nothing substantive differs → `boilerplate`.
2. Does a new risk or substantive part appear? → `material_added`.
3. Does a risk or substantive part disappear from the report? → `material_removed`.
4. Same risk, but scope, status, size or exposure changed? → `material_modified`.
5. Only wording, order, dates or formatting changed? → `boilerplate`.
6. Still unsure → `ambiguous` with a note.

When a piece contains both a material change and boilerplate edits, label it by the material change.

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
   → `material_added` (a new event, the Splunk acquisition, and a new emphasis on subscription risk).

4. EARLIER: "Acquisitions may also cause us to:"
   LATER: "Acquisitions have in the past and may in the future also cause us to:"
   → `material_modified` (status: the company now says these effects have already happened, not only that they
   could). By the rules above a "could" → "has" change counts as material even when it reads like legal caution.

## What to hand back

The same spreadsheet with `label`, `confidence (1-3)` and, where useful, `note` filled in. Do not change
any other column.
