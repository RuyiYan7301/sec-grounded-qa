# Perplexity comparison: notes (written after scoring)

Pre-registered result (frozen Part A scorer 2.1, final_correct): Perplexity 13/30, v0.2 26/30, v0.1 14/30;
paired vs v0.2: only v0.2 right 13, only Perplexity right 0 (exact McNemar p = 0.0002); vs v0.1: 5 vs 4.

Not pre-registered, reported separately: reading the 17 Perplexity misses, three are scorer artifacts on a
right answer (the frozen scorer was built around short single-paragraph answers):
- A-test-gen-014: $1.638 billion is right; an expense-breakdown table after it triggers the contradiction rule.
- A-test-gen-070: -35.32% is right; numbers in the shown calculation trigger the contradiction rule.
- A-test-gen-024: the three values are right but sit in a table whose header says "USD millions"; the
  scorer reads "$290,437" as dollars.
With these three counted right: Perplexity 16/30. This reading is by the same assistant that built the
system and is not blind; v0.2's answers were not re-read the same way.

Perplexity's other misses, by kind:
- Policy items the frozen gold refuses (EBITDA, Data Center segment revenue, cross-company per-share
  comparison, management judgement, unsupported question): Perplexity answers them. By this benchmark's
  rules they are wrong; a general assistant is not bound by this project's ontology.
- AMD long-term debt (gold not_reported): Perplexity gives $1.721 billion "long-term debt, net of current
  portion". As with Broadcom (audit A32/A50), the gold here likely reflects a missing XBRL concept rather
  than the absence of debt; kept as frozen.
- Different concept or measure: Intel total equity $126.4 billion (includes non-controlling interests; gold
  is equity attributable to Intel, $114.3 billion); Apple long-term debt change -8.66% (a different debt
  line than the gold's -6.19%).
- Wrong figures: Intel R&D share "fell 0.2 pp" (gold +1.57 pp); Apple capex change $1.55 billion from
  rounded inputs (gold $1.512 billion, outside tolerance); Intel net income percent change on a negative
  base given as 98.58% (gold: not meaningful).
- Missing required warnings: Broadcom equity without the scope note; Apple vs AMD stock compensation
  without the fiscal-period mismatch (and without both amounts).
- One reply stopped mid-sentence (Broadcom restated EPS).

Caveat: Perplexity reads the live web, not the 2026-10-16 snapshot. Question 1 was asked signed out,
questions 2-30 signed in (free plan, default Search mode).
