# Review instructions (v0.4 accuracy sample, docs/v0.4-plan.md 2a)

You review cells from one packet file. For each `## <id>` section:
- Read the packet text. You may open and search the "Full 10-K text" file named in that section
  (grep / read parts of it). Do not open any other file in the repository, results, code, or other packets.
- Judge only from the filing text and the metric definition in the packet.

Answer cells (id starts with A): is the reported value the filing's figure for this metric, for the
fiscal year ending on the date given, for the consolidated company? Choose one outcome:
- `correct`: the filing prints this value (any usual scale: millions, thousands, units; EPS to the cent)
  for this metric and period, or it is an exact sum the filing itself presents.
- `wrong_value`: the filing's figure for this metric and period is a different number.
- `wrong_concept`: the number is printed, but on a line that is not this metric by the definition
  (e.g. general & administrative only when the metric is SG&A; net income including noncontrolling
  interests when the filing also shows net income attributable to the company).
- `wrong_period`: the number belongs to a different fiscal year or a quarter.
- `scope`: right line, but not the consolidated total (e.g. one segment), or materially different coverage.
- `cannot_verify`: you could not find the figure or the line in the text after searching.

Not-reported cells (id starts with N): the system says the 10-K does not report this metric for that fiscal
year. Search the income statement / balance sheet / cash flow statement and notes. Outcome:
- `absent`: the filing has no line that is this metric by the definition (a sum you would have to compute
  yourself counts as absent).
- `present`: the filing prints this metric for that year; give the value and the line label.
- `cannot_verify`.

Write a CSV with header `id,outcome,filing_value,line_label,note` (one row per id, in packet order;
filing_value as printed, with its scale, e.g. "10,042 (millions)"; note <= 25 words). Be strict and
literal; when unsure between two outcomes, pick the less favourable one and say why in the note.
