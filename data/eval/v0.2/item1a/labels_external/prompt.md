# External-model labelling run (Item 1A, 50-unit sample)

Record before starting:
- model name and version (as shown in the UI):
- date: 2026-11-15
- interface (ChatGPT web / API):
- new chat, no custom instructions / memory: yes / no

Attach to the chat: `item1a_guideline.md` and `second_annotator_packet.csv` (the blank packet, no labels).
Send the prompt below once; then send "continue" for each next batch. Save every raw reply unchanged
in `raw_replies.md`, and the combined result as `gpt_labels.csv`.

---

PROMPT (copy verbatim):

You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 50 items. For each item, compare EARLIER TEXT with LATER TEXT, using the context
columns and the "closest text elsewhere in the other filing" column as the guideline says.

Rules:
- Use exactly one of: material_added, material_removed, material_modified, boilerplate, ambiguous.
- confidence is 1, 2 or 3 as defined in the guideline.
- note: one short sentence giving the reason (required for ambiguous).
- Label every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items (items 1-10 first). After each batch, stop and wait for me to say "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,label,confidence,note
and one row per item, in item order. No other text.
