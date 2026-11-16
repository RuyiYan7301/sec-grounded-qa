# Adjudicator prompt (third model family, DeepSeek), Item 1A v0.3 held-out

Written before the adjudicator sees any item. For each part: a new chat, attach `item1a_guideline_v2.md`
and that part of `packet_adjudication.csv` (as .csv.txt, rows unchanged), paste the prompt once with the
part's item count and numbers, then "continue" after each batch. Replies are saved unchanged.

---

PROMPT:

You are adjudicating labels for changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has {N} items (items {FIRST}-{LAST}). For each item, two independent labellers disagreed.
Their labels are in the columns "label 1" and "label 2"; you are not told who gave which, and the order
means nothing. Judge only the two columns whose names start with "LABEL THIS" (EARLIER TEXT and LATER
TEXT). Columns whose names start with "CONTEXT ONLY" help you understand the piece and show where its text
may have moved; never label their content. Read the guideline's section on match scores before using the
"where ... may be" columns.

Rules:
- decision: exactly one of: 1 (label 1 is right), 2 (label 2 is right), ambiguous (neither can be decided
  from the text, as the guideline defines ambiguous).
- reason: one short sentence.
- Decide every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items ({FIRST}-{FIRST10} first). After each batch, stop and wait for me to say
  "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,decision,reason
and one row per item, in item order. No other text.
