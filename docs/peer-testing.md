# Peer testing protocol

Course milestone (proposal, Check-in 3): peer testing done and feedback folded in. Written before any
session. Each session takes about 15 minutes, one tester at a time, on the author's machine.

## Setup (author)

1. `secqa doctor` passes; `secqa app` is running at http://127.0.0.1:7860 with Engine = auto.
2. A fresh copy of `docs/peer-testing-form.csv` is open for notes.
3. The tester gets only the one-paragraph intro below and the task cards; no other help unless stuck
   for more than two minutes (note when help was given).

Intro read to the tester: "This tool answers questions about the annual reports (10-K filings) of
Apple, Microsoft, Nvidia, Oracle, Cisco, Broadcom, Intel and AMD, fiscal years 2023 to 2025. It shows
where every number comes from. Please think aloud while you use it."

## Tasks (same order for every tester)

| # | Task card | What it probes |
|---|---|---|
| T1 | Find Apple's revenue in its most recent fiscal year covered, and check which filing it came from. | basic lookup, provenance |
| T2 | Compare Nvidia's and Apple's operating income for fiscal 2024. Is the comparison fair? | fiscal-period mismatch warning |
| T3 | How much did Intel's net income change from fiscal 2023 to fiscal 2024? | change calculation, negative values |
| T4 | What does Microsoft say are its main risks related to AI? | narrative path, citations |
| T5 | Ask anything you would really want to know about one of these companies. | real needs, coverage gaps |
| T6 | Try to make the tool give a wrong or made-up answer. | robustness, refusals |

## What to record per task (form columns)

- `answered_correctly` (y / n / partly, the author's judgement against the filing), `status_shown`
- `found_source` (could the tester find where the number came from without help: y / n)
- `understood_warning` (when a warning was shown, could the tester say what it means: y / n / na)
- `time_s`, `help_given` (y / n), `quote` (the tester's own words), `issue` (anything that went wrong)

## After the tasks (ask, then record in the form's last row for the tester)

1. How much would you trust a number from this tool, 1 (not at all) to 5 (fully)? Why?
2. What was confusing? (status labels, warnings, tabs, wording)
3. What is missing that would make you use it? (companies, quarters, segments, charts, export)
4. Would you use it instead of opening the 10-K or a search engine? For what?

## Reporting

- Number of testers, tasks completed, how often sources were found without help, and every issue
  found, each marked: fixed (commit), planned, or not planned (why).
- Quotes are reported without names. Testers are asked before the session whether their anonymised
  comments may appear in the course report.
- Changes made because of feedback are listed separately; any change to the engine is re-tested on
  the dev split only and does not change the frozen test results.
