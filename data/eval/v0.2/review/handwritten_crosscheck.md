# Part A handwritten items: cross-check of question vs gold plan

Rule (spec): the other author only checks that a question is semantically valid for its plan; no question is reworded to suit a system.
Verdict values: `valid`, or `invalid` with the reason. A question is never edited here; an invalid item is reported and handled by a written decision.

## A. codex_assisted items (12), checked by Claude, 2026-11-15

| id             | question                                                                                                                 | plan                                                                    | warnings        | verdict                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------- |
| A-test-han-003 | How much did Microsoft report in total liabilities for fiscal 2023?                                                      | fact_lookup · total_liabilities · MSFT · FY2023                         | -               | valid                                                                |
| A-test-han-005 | What was Microsoft's long-term debt balance at the end of FY2025?                                                        | fact_lookup · long_term_debt · MSFT · FY2025                            | -               | valid (gold affected by the long_term_debt scope question, see note) |
| A-test-han-014 | List AMD's total operating expenses for FY2023, FY2024, and FY2025.                                                      | multi_period_lookup · operating_expenses · AMD · FY2023,FY2024,FY2025   | -               | valid                                                                |
| A-test-han-016 | How did Apple's FY2025 net sales compare with Intel's FY2025 revenue?                                                    | cross_company_comparison · revenue · AAPL,INTC · FY2025                 | period_mismatch | valid; FY ends differ >31 days, period_mismatch required             |
| A-test-han-018 | Compare the total assets Nvidia and Intel reported for FY2023.                                                           | cross_company_comparison · total_assets · NVDA,INTC · FY2023            | period_mismatch | valid; period_mismatch required                                      |
| A-test-han-019 | Which company recorded more stock-based compensation in FY2025, Apple or AMD? Give both amounts.                         | cross_company_comparison · share_based_compensation · AAPL,AMD · FY2025 | period_mismatch | valid; period_mismatch required                                      |
| A-test-han-020 | By how many dollars did Apple's total operating expenses change from FY2024 to FY2025? Give both figures.                | absolute_change · operating_expenses · AAPL · FY2024,FY2025             | -               | valid                                                                |
| A-test-han-024 | How much did Nvidia's income from operations change between FY2023 and FY2024? Include both amounts.                     | absolute_change · operating_income · NVDA · FY2023,FY2024               | -               | valid (income from operations = operating_income)                    |
| A-test-han-027 | By what percentage did Apple's gross margin dollars change from FY2024 to FY2025? Give both figures.                     | percent_change · gross_profit · AAPL · FY2024,FY2025                    | -               | valid (Apple's 'gross margin' in dollars = gross_profit)             |
| A-test-han-029 | What was the percentage change in Microsoft's cost of products and services from FY2024 to FY2025? Include both amounts. | percent_change · cost_of_revenue · MSFT · FY2024,FY2025                 | -               | valid (MSFT cost of revenue = products + services)                   |
| A-test-han-031 | How many percentage points did Apple's net profit margin change from FY2023 to FY2024?                                   | percentage_point_change · net_margin · AAPL · FY2023,FY2024             | -               | valid                                                                |
| A-test-han-035 | What share of Intel's FY2024 revenue went to R&D?                                                                        | ratio · rd_intensity · INTC · FY2024                                    | -               | valid (share of revenue to R&D = rd_intensity)                       |

Note: `long_term_debt` is LongTermDebt (current plus noncurrent, frozen ontology). The balance-sheet line titled
"Long-term debt" is usually the noncurrent part only, so a literal reading can differ by more than the 0.5% tolerance
(MSFT FY2024: gold 44,937 vs balance-sheet line 42,688). Affects gen-032, gen-053, han-005, han-030. To be settled in the scorer rules before any run.

## B. claude_assisted items (28), checked by Codex-assisted review (submitted by the project owner), 2026-11-15

| id | question | plan | warnings | verdict |
|---|---|---|---|---|
| A-test-han-001 | What did Apple spend in total operating expenses in fiscal 2024? | fact_lookup · operating_expenses · AAPL · FY2024 | - | valid |
| A-test-han-002 | How much stock-based compensation did Microsoft record in fiscal 2025? | fact_lookup · share_based_compensation · MSFT · FY2025 | - | valid |
| A-test-han-004 | What was Nvidia's diluted weighted average share count for fiscal 2023? | fact_lookup · weighted_shares_diluted · NVDA · FY2023 | - | valid |
| A-test-han-006 | How many basic weighted average shares did Intel have outstanding in fiscal 2025? | fact_lookup · weighted_shares_basic · INTC · FY2025 | - | valid |
| A-test-han-007 | How much free cash flow did Apple generate in fiscal 2025? | fact_lookup · free_cash_flow · AAPL · FY2025 | - | valid; the answer must state the project's FCF definition |
| A-test-han-008 | What was the value of Nvidia's inventories at the end of fiscal 2024? | fact_lookup · inventory · NVDA · FY2024 | - | valid |
| A-test-han-009 | How much inventory did Intel carry on its balance sheet at the close of fiscal 2024? | fact_lookup · inventory · INTC · FY2024 | - | valid |
| A-test-han-010 | What was Apple's basic weighted average share count in fiscal 2025? | fact_lookup · weighted_shares_basic · AAPL · FY2025 | - | valid |
| A-test-han-011 | Show Broadcom's gross profit for each fiscal year from 2023 to 2025. | multi_period_lookup · gross_profit · AVGO · FY2023,FY2024,FY2025 | - | valid |
| A-test-han-012 | Give Nvidia's diluted share count for fiscal 2023, fiscal 2024 and fiscal 2025. | multi_period_lookup · weighted_shares_diluted · NVDA · FY2023,FY2024,FY2025 | - | valid; 'diluted share count' is the ontology alias of weighted-average diluted shares |
| A-test-han-013 | What operating profit did Broadcom report in FY2023, FY2024 and FY2025? | multi_period_lookup · operating_income · AVGO · FY2023,FY2024,FY2025 | - | valid; operating profit = operating income |
| A-test-han-015 | Who earned more in fiscal 2024, Apple or Microsoft? Give each company's net income. | cross_company_comparison · net_income · AAPL,MSFT · FY2024 | period_mismatch | valid; period_mismatch required |
| A-test-han-017 | Put Apple's total assets next to AMD's for fiscal 2023. | cross_company_comparison · total_assets · AAPL,AMD · FY2023 | period_mismatch | valid; period_mismatch required |
| A-test-han-021 | How much did Apple's net sales go up or down from fiscal 2023 to fiscal 2024, in dollars? | absolute_change · revenue · AAPL · FY2023,FY2024 | - | valid; net sales = revenue |
| A-test-han-022 | What was the dollar change in Intel's net income between fiscal 2024 and fiscal 2025? | absolute_change · net_income · INTC · FY2024,FY2025 | - | valid |
| A-test-han-023 | How many dollars of revenue did Intel gain or lose from FY2023 to FY2024? | absolute_change · revenue · INTC · FY2023,FY2024 | - | valid |
| A-test-han-025 | What was the percentage change in Intel's net income from fiscal 2024 to fiscal 2025? | percent_change · net_income · INTC · FY2024,FY2025 | - | valid; negative base, gold not_meaningful, no ordinary percentage |
| A-test-han-026 | By what percent did Apple's total assets grow or shrink between the end of fiscal 2024 and the end of fiscal 2025? | percent_change · total_assets · AAPL · FY2024,FY2025 | - | valid |
| A-test-han-028 | How fast did Microsoft's revenue grow from fiscal 2023 to fiscal 2024, in percent? | percent_change · revenue · MSFT · FY2023,FY2024 | - | valid |
| A-test-han-030 | By what percentage did Intel's long-term debt change from the end of FY2023 to the end of FY2024? | percent_change · long_term_debt · INTC · FY2023,FY2024 | - | valid; long_term_debt qualified-alternative rule applies |
| A-test-han-032 | How many percentage points did Apple's gross margin percentage move from fiscal 2023 to fiscal 2024? | percentage_point_change · gross_margin · AAPL · FY2023,FY2024 | - | valid |
| A-test-han-033 | Did Intel's R&D as a percentage of revenue rise or fall from fiscal 2023 to fiscal 2024, and by how many percentage points? | percentage_point_change · rd_intensity · INTC · FY2023,FY2024 | - | valid |
| A-test-han-034 | What was the percentage-point change in Microsoft's R&D intensity from FY2023 to FY2024? | percentage_point_change · rd_intensity · MSFT · FY2023,FY2024 | - | valid |
| A-test-han-036 | What operating margin did AMD earn in fiscal 2024? | ratio · operating_margin · AMD · FY2024 | - | valid |
| A-test-han-037 | What was Microsoft's gross margin percentage for fiscal 2025? | ratio · gross_margin · MSFT · FY2025 | - | valid |
| A-test-han-038 | Nvidia's diluted share count for fiscal 2024: what was it in the original filing, and what is it now? | restated_value_lookup · weighted_shares_diluted · NVDA · FY2024 | restated | valid; original filing vs latest_in_snapshot |
| A-test-han-039 | What basic EPS did Broadcom first report for fiscal 2023, and what figure do its filings show today? | restated_value_lookup · eps_basic · AVGO · FY2023 | restated | valid; split-adjusted latest_in_snapshot value |
| A-test-han-040 | Was Nvidia's fiscal 2023 EPS later revised? Give the originally reported and the current figures. | restated_value_lookup · eps_diluted · NVDA · FY2023 | restated,alias_interpretation | valid; bare EPS read as diluted EPS, alias_interpretation required |


Result: 40 of 40 handwritten items valid for their gold plan; no question edited.
