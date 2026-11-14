# Changelog

## 0.1.0 (2026-11-14)

First public release.

**System**
- XBRL fact store: deduplicates comparatives, derives fiscal year from the period end,
  keeps restatements with their filings.
- Tools: `list_concepts`, `get_fact`, `compare` (with `period_mismatch`), `filer_info`,
  `search_filings`. Every empty result says why.
- Hybrid retrieval (BM25 + sentence-transformers, reciprocal rank fusion) over Item 1A and
  Item 7 of 24 10-Ks.
- Tool-calling agent with **single** and **verify** modes. Verify runs five checks (numbers,
  re-query, period and restatement flags, concept judge, support judge), allows one
  revision, and withholds an answer that still fails.

**Engineering**
- Installable package with a `secqa` CLI: `setup`, `doctor`, `ask` (`--json`, `--trace`),
  `examples`, `app`, `eval`, `report`, `gen-questions`, `verify-gold`.
- Structured answers: status, XBRL facts with accession and filing link, retrieved passages,
  tool calls, check results, warnings.
- Deterministic input validation and warnings (`guards.py`). A period mismatch is detected
  from the facts an answer uses, even when the model did not call `compare`.
- Gradio web demo.
- Layered answer status: VERIFIED, VERIFIED WITH WARNINGS, TRACEABLE, UNVERIFIED, WITHHELD.
  An answer that leaves out a period-mismatch or restatement warning is TRACEABLE, never VERIFIED.
- Every fact names the filing its value is taken from and the filing that first reported it,
  whether it came through `get_fact` or `compare` (prior-year values come from later 10-Ks).
- EDGAR client: required User-Agent read from `.env`, rate limit, exponential backoff on
  throttling and connection errors, offline cache, snapshot date (`SECQA_SNAPSHOT`) so a
  later download rebuilds the evaluated data. Calendar frames are read from every row of a
  period, because EDGAR moves a frame to whichever filing came last (found by a clean-clone
  rebuild: a proxy statement filed after the snapshot had taken the frame from the 10-K).
- Offline test suite (trimmed real EDGAR fixture, scripted model) and GitHub Actions CI.

## Evaluation history

Development before this repository is summarized here; the results of every run are in `results/`.

- **Development set (r1).** 28 queries used while building the system.
- **Test set frozen.** 96 queries, before any model run.
- **t1.** First test run. The number check rejected correct drafts (sign words, shown
  calculations, digits in URLs, tolerance), so 8B in verify mode scored 64/96. Fixed in the
  checker only.
- **t2 (main result).** single 79 / 78 / 77, verify 80 / 76 / 67 (qwen3 4B / 8B / 14B).
  Traceability in verify mode: 96/96 for every model.
- **t3 (post-hoc).** Concept judge sees all periods of a concept; flagged sentences are
  removed and the rest re-verified before withholding. Verify: 78 / 79 / 77.
- **Fact-level period-mismatch warning (post-hoc).** Applied to the saved t2 answers, it
  flags 21 of the 24 answers that failed the mismatch rule, with 0 false alarms on the other 516.
