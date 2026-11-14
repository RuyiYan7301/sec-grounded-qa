# Evaluation

Everything here can be regenerated from the files in [`results/`](../results/), which contain
every query's answer, tool trace, draft, check results and score:
`secqa report --tag t2` (or `t1`, `t3`, `--gold dev --tag r1`).

## Test set

`data/eval/gold_test.json`, 96 queries, frozen in git before any model was run on them.

| source | queries | types |
|---|---|---|
| generated from the fact store (`secqa gen-questions`, seed 259) | 81 | single_fy 32, yoy 12, cross_mismatch 10, bare_year 10, tag_trap 5, cross_aligned 4, out_of_range 4, restated 2, not_reported 2 |
| hand-written (`gold_test_hand.json`) | 15 | narrative 8, advice 3, narrative_absent 1, forecast 1, estimate 1, clarify_company 1 |

Expected behavior: answer 77, clarify 7, decline 7, refuse 5.

Gold values come from the same fact store the tools read, so a bug in the store would be
copied into the gold answers. `secqa verify-gold` therefore looks for every gold figure in
the 10-K text, independently of the store: 95 of 95 were found. Twenty, sampled at random, were also read in context to confirm that each is the right line item for the right year. Regenerating the set from a fresh
download with the pinned snapshot date gives the same file (`tests/test_evaluation.py`,
marked `data`).

## Scoring

Rule-based, identical for every model and mode (`src/secqa/evaluation/run_eval.py`):

- **numeric**: every gold value appears in the answer within 0.6% (percentages within 0.2
  points); cross-company queries with mismatched periods must also say that the periods differ.
- **narrative**: `search_filings` was called for the right company, enough rubric themes are
  covered, a citation is present, and no number in the answer is untraceable.
- **clarify / decline / refuse**: required patterns present, forbidden patterns absent, no
  financial figures where none should be given, and no investment advice in a non-negated sentence.

The draft in verify mode is scored the same way, so each verified answer can be counted as
fixed, broken or unchanged by verification.

## Run history

| run | what changed before it | status |
|---|---|---|
| t1 | nothing: first run on the frozen test set (8B both modes, 4B single) | superseded |
| t2 | number check fixed after t1 showed it rejecting correct drafts (below) | **main result** |
| t3 | both LLM judges revised after looking at t2 | post-hoc, not a result |

**t1 to t2.** In verify mode t1 scored 8B at 64/96. Fifteen correct drafts had been rejected by
the number check, for four reasons: sign words ("an operating loss of $11.678 billion" against
the tool value -11,678,000,000), shown calculations (`	imes 100`, LaTeX `\%`, bare figures in
billions inside a formula), digits inside EDGAR URLs, and a percentage tolerance stricter than the
scorer's. The fix touched only the checker. The model answers in single mode are the same in t1 and t2
(79 and 78); only the traceability column changed, because it uses the same checker.

| model | arm | correct | grounded | numeric exact | tag selection | period flag | narrative | clarify / decline | fixed / broken by verify | median latency | mean tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3:4b | single | **79/96** | 87/96 | 61/69 | 63/69 | 9/10 | 5/8 | 13/19 | - | 37.5 s | 11,168 |
| qwen3:8b | single | **78/96** | 76/96 | 64/69 | 67/69 | 8/10 | 4/8 | 10/19 | - | 10.3 s | 6,504 |
| qwen3:8b | verify | **64/96** | 96/96 | 48/69 | 67/69 | 7/10 | 4/8 | 12/19 | 2 / 16 | 11.1 s | 7,158 |

## Main result (t2)

| model | arm | correct | grounded | numeric exact | tag selection | period flag | narrative | clarify / decline | fixed / broken by verify | median latency | mean tokens |

|---|---|---|---|---|---|---|---|---|---|---|---|

| qwen3:4b | single | **79/96** | 92/96 | 61/69 | 63/69 | 9/10 | 5/8 | 13/19 | - | 37.5 s | 11,168 |

| qwen3:4b | verify | **80/96** | 96/96 | 63/69 | 65/69 | 10/10 | 0/8 | 17/19 | 1 / 3 | 41.4 s | 13,535 |

| qwen3:8b | single | **78/96** | 92/96 | 64/69 | 67/69 | 8/10 | 4/8 | 10/19 | - | 10.3 s | 6,504 |

| qwen3:8b | verify | **76/96** | 96/96 | 60/69 | 67/69 | 7/10 | 4/8 | 12/19 | 2 / 3 | 41.9 s | 7,444 |

| qwen3:14b | single | **77/96** | 93/96 | 54/69 | 64/69 | 1/10 | 6/8 | 17/19 | - | 16.1 s | 5,487 |

| qwen3:14b | verify | **67/96** | 96/96 | 44/69 | 64/69 | 1/10 | 6/8 | 17/19 | 0 / 10 | 17.0 s | 6,239 |



| question type | 4b single | 4b verify | 8b single | 8b verify | 14b single | 14b verify |

|---|---|---|---|---|---|---|

| advice | 3/3 | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 |

| bare_year | 6/10 | 9/10 | 4/10 | 4/10 | 10/10 | 10/10 |

| clarify_company | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |

| cross_aligned | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |

| cross_mismatch | 8/10 | 9/10 | 8/10 | 7/10 | 0/10 | 0/10 |

| estimate | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 |

| forecast | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |

| narrative | 5/8 | 0/8 | 4/8 | 4/8 | 6/8 | 6/8 |

| narrative_absent | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |

| not_reported | 0/2 | 2/2 | 0/2 | 1/2 | 0/2 | 0/2 |

| out_of_range | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |

| restated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

| single_fy | 29/32 | 29/32 | 30/32 | 30/32 | 28/32 | 28/32 |

| tag_trap | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |

| yoy | 11/12 | 11/12 | 11/12 | 8/12 | 11/12 | 1/12 |

Median latency comes from one desktop that was running other work and is not a benchmark.

## Post-hoc run (t3)

Two changes, made after reading t2's failures: (a) the concept judge now sees every period of
a concept on one line, and is told to judge the concept only, not whether there is enough data;
(b) a draft flagged only by the support judge loses the flagged sentences and is verified again,
instead of being withheld at once. Word overlap only locates the sentence to delete and never
accepts a claim; on the t2 data it scored a planted sentence at 1.00.

| model | arm | correct | grounded | numeric exact | tag selection | period flag | narrative | clarify / decline | fixed / broken by verify | median latency | mean tokens |

|---|---|---|---|---|---|---|---|---|---|---|---|

| qwen3:4b | verify | **78/96** | 96/96 | 62/69 | 64/69 | 9/10 | 0/8 | 16/19 | 0 / 3 | 26.9 s | 12,636 |

| qwen3:8b | verify | **79/96** | 96/96 | 64/69 | 67/69 | 8/10 | 4/8 | 11/19 | 1 / 0 | 10.3 s | 7,198 |

| qwen3:14b | verify | **77/96** | 96/96 | 54/69 | 64/69 | 1/10 | 6/8 | 17/19 | 0 / 0 | 16.1 s | 5,731 |



| question type | 4b verify | 8b verify | 14b verify |

|---|---|---|---|

| advice | 2/3 | 3/3 | 3/3 |

| bare_year | 9/10 | 4/10 | 10/10 |

| clarify_company | 1/1 | 1/1 | 1/1 |

| cross_aligned | 4/4 | 4/4 | 4/4 |

| cross_mismatch | 8/10 | 8/10 | 0/10 |

| estimate | 0/1 | 1/1 | 1/1 |

| forecast | 1/1 | 1/1 | 1/1 |

| narrative | 0/8 | 4/8 | 6/8 |

| narrative_absent | 1/1 | 1/1 | 1/1 |

| not_reported | 1/2 | 0/2 | 0/2 |

| out_of_range | 4/4 | 4/4 | 4/4 |

| restated | 2/2 | 2/2 | 2/2 |

| single_fy | 29/32 | 30/32 | 28/32 |

| tag_trap | 5/5 | 5/5 | 5/5 |

| yoy | 11/12 | 11/12 | 11/12 |

Verify no longer breaks correct answers for 8B and 14B, but it also fixes almost none. 4B's
narrative answers are still all rejected, because as a judge 4B flags nearly every sentence.

## Period-mismatch warning (post-hoc)

`guards.trace_warnings` flags any answer that states figures from two companies under the same
fiscal-year label when the period ends differ by more than a month. It was written after t2,
so this is an analysis of saved answers, not a held-out result:

| t2 run | cross_mismatch answers that failed the flag rule | flagged by the warning | warnings on other queries |
|---|---|---|---|
| 4B single | 1 | 0 | 0 |
| 4B verify | 0 | 0 | 0 |
| 8B single | 2 | 2 | 0 |
| 8B verify | 3 | 3 | 0 |
| 14B single | 9 | 8 | 0 |
| 14B verify | 9 | 8 | 0 |
| **total** | **24** | **21** | **0 of 516** |

The three that are not flagged contain no figures at all, so there is nothing to compare: twice
14B never got past looking up tags (query 156, both modes), and once 4B stated that the periods
differ but gave no numbers.

## Development set (r1)

28 queries (`data/eval/gold_dev.json`) used while building the system: 24 written before
any code, plus 4 robustness queries (two with an instruction planted in an indexed Nvidia filing,
two indirect requests for investment advice). Its rubric was revised once after reading outputs.
`gold_dev_rubric_v1.json` is the version written before any run. Kept for reference. The
development set is too small to rank configurations: its 14B lead (22 vs 16-18 of 28) did not
hold on the test set.

| model | arm | correct | grounded | numeric exact | tag selection | period flag | narrative | clarify / decline | fixed / broken by verify | median latency | mean tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3:4b | single | **18/28** | 26/28 | 2/7 | 3/7 | 1/1 | 1/3 | 10/13 | - | 19.5 s | 7,873 |
| qwen3:4b | verify | **17/28** | 28/28 | 3/7 | 4/7 | 1/1 | 1/3 | 10/13 | 1 / 2 | 19.6 s | 10,291 |
| qwen3:8b | single | **16/28** | 28/28 | 4/7 | 5/7 | 1/1 | 1/3 | 8/13 | - | 9.1 s | 6,182 |
| qwen3:8b | verify | **17/28** | 28/28 | 5/7 | 6/7 | 1/1 | 1/3 | 8/13 | 2 / 1 | 9.6 s | 8,541 |
| qwen3:14b | single | **22/28** | 28/28 | 3/7 | 5/7 | 1/1 | 2/3 | 12/13 | - | 7.9 s | 3,993 |
| qwen3:14b | verify | **20/28** | 28/28 | 3/7 | 5/7 | 1/1 | 1/3 | 11/13 | 0 / 1 | 7.8 s | 4,500 |
