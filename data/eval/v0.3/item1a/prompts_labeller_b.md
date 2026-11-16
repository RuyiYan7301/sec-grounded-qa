# Labeller B (Gemini) prompts, Item 1A v0.3 held-out

The prompt of `data/eval/v0.2/item1a/protocol_v2/prompt_v2.md` (sha256 f65f689112e58663a7d562ab26c7820a4ca4b90c6afd285a590b4e5b9e22f7ce), word for word, except the item count and the item numbers of the first batch, which are set to each packet's own.

For each packet: a new Gemini chat (no saved info / memory, no Gem, no custom instructions), attach `item1a_guideline_v2.md` and that packet only, paste its prompt once, then type `continue` after each batch until the last item. Save every reply unchanged in `labels_gemini/raw_replies_<packet>.md`. Record model name and version as shown in the UI, date, and interface.

---

## packet_MSFT_FY2026_1.csv (45 items, 1-45)

```
You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 45 items (items 1-45). For each item, judge only the two columns whose names start with
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
```

---

## packet_MSFT_FY2026_2.csv (36 items, 46-81)

```
You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 36 items (items 46-81). For each item, judge only the two columns whose names start with
"LABEL THIS" (EARLIER TEXT and LATER TEXT). Columns whose names start with "CONTEXT ONLY" help you
understand the piece and show where its text may have moved; never label their content. Read the
guideline's section on match scores before using the "where ... may be" columns.

Rules:
- Use exactly one of: material_added, material_removed, material_modified, boilerplate, ambiguous.
- confidence is 1, 2 or 3 as defined in the guideline.
- note: one short sentence giving the reason (required for ambiguous; write added_claim where the
  guideline says so).
- Label every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items (items 46-55 first). After each batch, stop and wait for me to say "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,label,confidence,note
and one row per item, in item order. No other text.
```

---

## packet_ORCL_FY2026_1.csv (45 items, 1-45)

```
You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 45 items (items 1-45). For each item, judge only the two columns whose names start with
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
```

---

## packet_ORCL_FY2026_2.csv (45 items, 46-90)

```
You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 45 items (items 46-90). For each item, judge only the two columns whose names start with
"LABEL THIS" (EARLIER TEXT and LATER TEXT). Columns whose names start with "CONTEXT ONLY" help you
understand the piece and show where its text may have moved; never label their content. Read the
guideline's section on match scores before using the "where ... may be" columns.

Rules:
- Use exactly one of: material_added, material_removed, material_modified, boilerplate, ambiguous.
- confidence is 1, 2 or 3 as defined in the guideline.
- note: one short sentence giving the reason (required for ambiguous; write added_claim where the
  guideline says so).
- Label every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items (items 46-55 first). After each batch, stop and wait for me to say "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,label,confidence,note
and one row per item, in item order. No other text.
```

---

## packet_ORCL_FY2026_3.csv (35 items, 91-125)

```
You are labelling changes in the Risk Factors section (Item 1A) of consecutive 10-K reports.
The attached file item1a_guideline_v2.md is the complete labelling guideline. Follow it exactly.
The attached CSV has 35 items (items 91-125). For each item, judge only the two columns whose names start with
"LABEL THIS" (EARLIER TEXT and LATER TEXT). Columns whose names start with "CONTEXT ONLY" help you
understand the piece and show where its text may have moved; never label their content. Read the
guideline's section on match scores before using the "where ... may be" columns.

Rules:
- Use exactly one of: material_added, material_removed, material_modified, boilerplate, ambiguous.
- confidence is 1, 2 or 3 as defined in the guideline.
- note: one short sentence giving the reason (required for ambiguous; write added_claim where the
  guideline says so).
- Label every item independently. Do not skip items, do not merge items.
- Work in batches of 10 items (items 91-100 first). After each batch, stop and wait for me to say "continue".

Output for each batch: only a CSV code block with the header
item,hunk_id,label,confidence,note
and one row per item, in item order. No other text.
```
