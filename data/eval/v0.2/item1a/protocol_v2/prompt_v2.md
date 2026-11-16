# External-model labelling, protocol v2

Two runs, each in its **own new chat** (no memory, no custom instructions), in this order:
1. `packet_retest.csv`  — the 50 pilot units (protocol-repair retest)
2. `packet_confirm.csv` — 50 new units (confirmation sample)

Attach to each chat `item1a_guideline_v2.md` and that run's packet only. Send the prompt below once,
then "continue" after each batch. Save every reply unchanged (copy the whole reply) in
`labels_external/raw_replies_<run>.md`.

Record for each run:
- model name and version (as shown in the UI):
- date:
- interface (ChatGPT web / API):
- memory and custom instructions off: yes / no

---

PROMPT (copy verbatim):

You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 50 items. For each item, judge only the two columns whose names start with
"LABEL THIS" (EARLIER TEXT and LATER TEXT). Columns whose names start with "CONTEXT ONLY" help you
understand the piece and show where its text may have moved; never label their content. Read the
guideline's section on match scores before using the "where ... may be" columns.

Rules:
- Use exactly one of: material_added, material_removed, material_modified, boilerplate, ambiguous.
- confidence is 1, 2 or 3 as defined in the guideline.
- note: one short sentence giving the reason (required for ambiguous; write added_claim where the
  guideline says so).
- Label every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items (items 1-10 first). After each batch, stop and wait for me to say "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,label,confidence,note
and one row per item, in item order. No other text.
