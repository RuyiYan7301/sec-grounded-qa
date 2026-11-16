# Part A audit pack (80 records, blind)

Key sha256: `8104c3542698e871f88bc2883d5ad642d04bd170f48153ba5ab0dc78d856e313`. Do not open key_sealed.json before form.csv is complete.

Judge each record against the gold: is the answer right for the person who asked (number, direction, years, required warnings; or a refusal for the right reason), and is the cited evidence complete, the right concept, the right period, and the calculation right? Write y, n or na in form.csv.

---

## A01

**Question:** By what percentage did Microsoft's total stockholders' equity change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 30.18770942135455, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2023", "value": 206223000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2024", "value": 268477000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> Microsoft's total stockholders' equity increased by **30.2%** from fiscal 2023 to fiscal 2024. The equity was **$206,223 million** at the end of fiscal 2023 and rose to **$268,477 million** by the end of fiscal 2024. These figures are based on the 10-K filings for FY2023 (accession: 0000950170-25-100235) and FY2024 (accession: 0001193125-26-323660).

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2023", "value": 206223000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2024", "value": 268477000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0001193125-26-323660"}

---

## A02

**Question:** What was Nvidia's EBITDA in fiscal 2025?

**Gold:** outcome `out_of_ontology`, result `{"outcome": "out_of_ontology"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The figure cannot be given because EBITDA is not a metric included in the provided ontology. Therefore, there is no available data to answer the question about Nvidia's EBITDA in fiscal 2025.

**Evidence cited (0):**

---

## A03

**Question:** What was Broadcom's total stockholders' equity at the end of fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 67678000000}`, required warnings `['scope']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AVGO", "concept": "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "period": "FY2024", "value": 67678000000, "unit": "USD", "period_end": "2024-11-03", "use": "fallback_with_warning"}

**Answer:**

> Broadcom's total stockholders' equity at the end of fiscal 2024 was $67.678 billion, as reported in accession number 0001730168-25-000121.

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "period": "FY2024", "value": 67678000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A04

**Question:** Has Nvidia's reported weighted-average diluted shares outstanding for fiscal 2023 been revised? Give the original and current figures.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 25070000000, "original_val": 2507000000, "original_accession": "0001045810-23-000017"}`, required warnings `['restated']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "use": "primary"}

**Answer:**

> The original figure for Nvidia's weighted-average diluted shares outstanding for fiscal 2023 was **2,507,000,000 shares** (accession number 0001045810-23-000017). The current figure is **25,070,000,000 shares** (accession number 0001045810-25-000023). The later filing revised the figure.

**Evidence cited (1):**
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}

---

## A05

**Question:** How much was Nvidia's research and development expense in FY2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 12914000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 12914000000, "unit": "USD", "period_end": "2025-01-26", "use": "primary"}

**Answer:**

> Nvidia's research and development expense in FY2025 was $12,914 million, according to the 10-K filing with accession number 0001045810-26-000021, which covers the period ending January 26, 2025.

**Evidence cited (1):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 12914000000, "unit": "USD", "period_end": "2025-01-26", "accession": "0001045810-26-000021"}

---

## A06

**Question:** What was the dollar change in Microsoft's cost of revenue between FY2023 and FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 8251000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2023", "value": 65863000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2024", "value": 74114000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> The dollar change in Microsoft's cost of revenue between FY2023 and FY2024 was an increase of $8,251 million. This change is based on the following figures:  
> - FY2023 cost of revenue: $65,863 million  
> - FY2024 cost of revenue: $74,114 million  
> 
> The data comes from Microsoft's annual filings with the SEC, specifically accession numbers 0000950170-25-100235 (FY2023) and 0001193125-26-323660 (FY2024).

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2023", "value": 65863000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2024", "value": 74114000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0001193125-26-323660"}

---

## A07

**Question:** How much goodwill did Apple carry at the end of fiscal 2023?

**Gold:** outcome `not_reported`, result `{"outcome": "not_reported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The XBRL tag for "goodwill" is not directly available for Apple (AAPL) in FY2023. The closest related tags are "Intangible Assets, Net (Excluding Goodwill)" and "Intangible Assets, Gross (Excluding Goodwill)." These tags do not include goodwill. You may need to consult the 10-K filing for more detailed information on goodwill.

**Evidence cited (0):**

---

## A08

**Question:** What was Broadcom's gross margin in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 63.03369915073487, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "GrossProfit", "period": "FY2024", "value": 32509000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}
- {"ticker": "AVGO", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 51574000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> Broadcom's gross margin in fiscal 2024 was 63.0%. This figure is derived from the gross profit of $32,509 million and revenue of $51,574 million, both reported in the fiscal year ending November 3, 2024, from the filing with accession number 0001730168-25-000121. The gross margin represents the ratio of gross profit to revenue.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "GrossProfit", "period": "FY2024", "value": 32509000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 51574000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A09

**Question:** By what percentage did Broadcom's diluted EPS change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -62.72727272727272, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2023", "value": 3.3, "unit": "USD/shares", "period_end": "2023-10-29", "use": "primary"}
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2024", "value": 1.23, "unit": "USD/shares", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> I could not verify an answer to this question against the filings, so I am not giving one. Try asking for a specific company, reported figure and fiscal year.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2023", "value": 3.3, "unit": "USD/shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2024", "value": 1.23, "unit": "USD/shares", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A10

**Question:** What was Intel's selling, general and administrative expense in each of fiscal 2023, 2024 and 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [5634000000, 5507000000, 4624000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2023", "value": 5634000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2024", "value": 5507000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2025", "value": 4624000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Intel's selling, general and administrative expense was:
> 
> - **FY2023**: $5.634 billion (accession number 0000050863-26-000011)
> - **FY2024**: $5.507 billion (accession number 0000050863-26-000011)
> - **FY2025**: $4.624 billion (accession number 0000050863-26-000011)

**Evidence cited (3):**
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2023", "value": 5634000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2024", "value": 5507000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2025", "value": 4624000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A11

**Question:** How many percentage points did Apple's net profit margin change from FY2023 to FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1.3349784943764154, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2023", "value": 96995000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2024", "value": 93736000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> The net profit margin for Apple changed by **3.26 percentage points** from FY2023 to FY2024.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2023", "value": 96995000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2024", "value": 93736000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}

---

## A12

**Question:** How much goodwill did Apple carry at the end of fiscal 2023?

**Gold:** outcome `not_reported`, result `{"outcome": "not_reported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The amount of goodwill that Apple carried at the end of fiscal 2023 could not be provided because it was not reported in the available filings.

**Evidence cited (0):**

---

## A13

**Question:** What operating margin did AMD earn in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 7.368625169672289, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "OperatingIncomeLoss", "period": "FY2024", "value": 1900000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD's operating income for fiscal 2024 was $1.900 billion, as reported in its 10-K filing (accession number 0000002488-26-000018).

**Evidence cited (1):**
- {"ticker": "AMD", "concept": "OperatingIncomeLoss", "period": "FY2024", "value": 1900000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A14

**Question:** How did Intel's R&D as a share of revenue move between FY2024 and FY2025, in percentage points?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -5.098526987050411, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 16546000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 53101000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 13774000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Intel's R&D as a share of revenue decreased by **5.1 percentage points** from FY2024 to FY2025. This change reflects a reduction in the proportion of revenue allocated to R&D expenses. The data is based on the filings with accession numbers provided.

**Evidence cited (4):**
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 16546000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 53101000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 13774000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A15

**Question:** What was AMD's stock-based compensation expense in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1407000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AMD", "concept": "ShareBasedCompensation", "period": "FY2024", "value": 1407000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD's stock-based compensation expense in fiscal 2024 was $1,407 million, as reported in its 10-K filing with the SEC (accession number 0000002488-26-000018). This figure represents the total share-based compensation expense for the fiscal year ending December 28, 2024.

**Evidence cited (1):**
- {"ticker": "AMD", "concept": "ShareBasedCompensation", "period": "FY2024", "value": 1407000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A16

**Question:** What was Nvidia's EBITDA in fiscal 2025?

**Gold:** outcome `out_of_ontology`, result `{"outcome": "out_of_ontology"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The term "EBITDA" does not correspond to any XBRL tag for Nvidia (NVDA) in the fiscal years FY2023, FY2024, or FY2025. Please clarify or provide an alternative metric.

**Evidence cited (0):**

---

## A17

**Question:** What was Broadcom's total stockholders' equity at the end of fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 67678000000}`, required warnings `['scope']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AVGO", "concept": "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "period": "FY2024", "value": 67678000000, "unit": "USD", "period_end": "2024-11-03", "use": "fallback_with_warning"}

**Answer:**

> Broadcom's total stockholders' equity at the end of fiscal 2024 was $67,678 million. This figure is based on the filing with accession number 0001730168-25-000121, which ends on November 3, 2024. The value was derived using the concept "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest."

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "period": "FY2024", "value": 67678000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A18

**Question:** Which had higher basic earnings per share in fiscal 2024, Apple or Microsoft?

**Gold:** outcome `unsupported_operation`, result `{"outcome": "unsupported_operation"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The comparison of basic earnings per share (EPS) between Apple and Microsoft for fiscal 2024 cannot be provided because cross-company comparisons for EPS are not supported. The result is based on the restriction that such comparisons are not allowed.

**Evidence cited (0):**

---

## A19

**Question:** What was Intel's net income attributable to Intel in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -18756000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> Intel's net income attributable to Intel in fiscal 2024 was **-$18.756 billion** (accession number: 0000050863-26-000011).

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}

---

## A20

**Question:** What was the year-over-year percent change in AMD's income tax expense in fiscal 2024?

**Gold:** outcome `not_meaningful`, result `{"outcome": "not_meaningful", "absolute_change": 727000000}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2023", "value": -346000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2024", "value": 381000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> The year-over-year percent change in AMD's income tax expense in fiscal 2024 cannot be provided because the change is not meaningful. This is due to a sign change in the income tax expense from a negative value of -$346 million in FY2023 to a positive value of $381 million in FY2024. The percent change calculation is not meaningful when the direction of the change (from negative to positive) alters the basis for comparison. The figures are sourced from the filings with accession numbers 0000002488-26-000018.

**Evidence cited (2):**
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2023", "value": -346000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2024", "value": 381000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A21

**Question:** What was the percentage change in Intel's net income from fiscal 2024 to fiscal 2025?

**Gold:** outcome `not_meaningful`, result `{"outcome": "not_meaningful", "absolute_change": 18489000000}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2025", "value": -267000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> The percentage change in Intel's net income from fiscal 2024 to fiscal 2025 could not be meaningfully calculated because the change is based on magnitude only, and the percent change is not provided. The net income for fiscal 2024 was a loss of $18,756 million, and for fiscal 2025, it was a loss of $2,670 million. The loss narrowed, indicating an improvement, but the percent change could not be determined from the given data. The figures are sourced from the filings with accession numbers 0000050863-26-000011.

**Evidence cited (2):**
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2025", "value": -267000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A22

**Question:** How did Apple's FY2025 net sales compare with Intel's FY2025 revenue?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [416161000000, 52853000000], "difference": 363308000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 416161000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> The tags for "net sales" and "revenue" were not found. Please use `list_concepts` to identify the correct XBRL tags for Apple and Intel before comparing.

**Evidence cited (0):**

---

## A23

**Question:** How much was AMD's weighted-average basic shares outstanding in FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1620000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AMD", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2024", "value": 1620000000, "unit": "shares", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD's weighted-average basic shares outstanding in FY2024 was **1,620,000,000 shares** (accession number: 0000002488-26-000018, form 10-K, filed on 2026-02-04).

**Evidence cited (1):**
- {"ticker": "AMD", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2024", "value": 1620000000, "unit": "shares", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A24

**Question:** Compare Microsoft's and AMD's revenue for fiscal 2023.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [211915000000, 22680000000], "difference": 189235000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 211915000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 22680000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}

**Answer:**

> The fiscal years for Microsoft and AMD do not align for FY2023. Microsoft's fiscal year ended on June 30, 2023, while AMD's fiscal year ended on December 30, 2023. 
> 
> - **Microsoft (FY2023)**: $211.915 billion (accession: 0000950170-25-100235)
> - **AMD (FY2023)**: $22.680 billion (accession: 0000002488-26-000018)

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 211915000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 22680000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000002488-26-000018"}

---

## A25

**Question:** Compare Microsoft's and AMD's revenue for fiscal 2023.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [211915000000, 22680000000], "difference": 189235000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 211915000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 22680000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}

**Answer:**

> Microsoft's revenue for fiscal 2023 was $211,915 million, while AMD's revenue for the same fiscal year was $22,680 million. Microsoft's revenue was significantly higher than AMD's by $189,235 million. However, it is important to note that the fiscal years compared end on different dates—Microsoft's fiscal year ended on June 30, 2023, while AMD's fiscal year ended on December 30, 2023. This difference in reporting periods may affect the comparability of the figures.

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 211915000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 22680000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000002488-26-000018"}

---

## A26

**Question:** How much free cash flow did Apple generate in fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 98767000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "NetCashProvidedByUsedInOperatingActivities", "period": "FY2025", "value": 111482000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2025", "value": 12715000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple generated **$98,767 million** in free cash flow for fiscal 2025. This figure is based on the company's operating cash flow of **$111,482 million** minus capital expenditures of **$12,715 million**, as reported in its Form 10-K filing for the fiscal year ending September 27, 2025. 
> 
> Note: Free cash flow is a derived metric and not a GAAP line item. Companies may define it differently, but this answer uses the standard definition of operating cash flow minus capital expenditures.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "NetCashProvidedByUsedInOperatingActivities", "period": "FY2025", "value": 111482000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2025", "value": 12715000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A27

**Question:** How did Apple's FY2025 net sales compare with Intel's FY2025 revenue?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [416161000000, 52853000000], "difference": 363308000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 416161000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Apple's FY2025 net sales were $416,161 million, while Intel's FY2025 revenue was $52,853 million. Apple's revenue was significantly higher than Intel's by $363,308 million. However, it's important to note that the fiscal years ended on different dates: Apple's fiscal year ended on September 27, 2025, while Intel's fiscal year ended on December 27, 2025, creating a 91-day gap in the reporting periods. This difference in timing may affect the comparability of the figures.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 416161000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A28

**Question:** What was Intel's gross profit in fiscal 2023?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 21711000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "GrossProfit", "period": "FY2023", "value": 21711000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}

**Answer:**

> Intel's gross profit in fiscal 2023 was $21.711 billion, as reported in filing 0000050863-26-000011.

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "GrossProfit", "period": "FY2023", "value": 21711000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000050863-26-000011"}

---

## A29

**Question:** Compare Nvidia's and Microsoft's long-term debt for fiscal 2024.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [9709000000, 44937000000], "difference": -35228000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "LongTermDebt", "period": "FY2024", "value": 9709000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2024", "value": 44937000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> Nvidia's long-term debt for fiscal 2024 was **$9,709 million**, while Microsoft's long-term debt was **$44,937 million**. The difference is **-$35,228 million**, meaning Microsoft's long-term debt is significantly higher than Nvidia's. 
> 
> However, there is a **period mismatch**: Nvidia's fiscal year ended on **January 28, 2024**, while Microsoft's fiscal year ended on **June 30, 2024**, creating a **154-day gap**. This difference in reporting dates may affect the comparability of the figures.

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "LongTermDebt", "period": "FY2024", "value": 9709000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-25-000023"}
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2024", "value": 44937000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0000950170-25-100235"}

---

## A30

**Question:** What will AMD's revenue be in fiscal 2026?

**Gold:** outcome `unsupported`, result `{"outcome": "unsupported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The question asks for a forecast, which I cannot provide. I can only report historical data from SEC filings. Please ask about AMD's revenue in a past fiscal year.

**Evidence cited (0):**

---

## A31

**Question:** What was Microsoft's long-term debt balance at the end of FY2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 43151000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2025", "value": 43151000000, "unit": "USD", "period_end": "2025-06-30", "use": "primary"}

**Answer:**

> Microsoft's long-term debt balance at the end of FY2025 was **$43.151 billion**, as reported in its 10-K filing (accession number 0001193125-26-323660).

**Evidence cited (1):**
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2025", "value": 43151000000, "unit": "USD", "period_end": "2025-06-30", "accession": "0001193125-26-323660"}

---

## A32

**Question:** What was Broadcom's long-term debt at the end of fiscal 2024?

**Gold:** outcome `not_reported`, result `{"outcome": "not_reported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The figure for Broadcom's long-term debt at the end of fiscal 2024 could not be provided because it was not reported in the available filings.

**Evidence cited (0):**

---

## A33

**Question:** What was Intel's total stockholders' equity at the end of fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 114281000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "StockholdersEquity", "period": "FY2025", "value": 114281000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Intel's total stockholders' equity at the end of fiscal 2025 was $114.281 billion, as reported in accession number 0000050863-26-000011.

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "StockholdersEquity", "period": "FY2025", "value": 114281000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A34

**Question:** How did Intel's R&D as a share of revenue move between FY2024 and FY2025, in percentage points?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -5.098526987050411, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 16546000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 53101000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 13774000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> (empty)

**Evidence cited (4):**
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 16546000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 13774000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 53101000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 52853000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A35

**Question:** How much was AMD's weighted-average basic shares outstanding in FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1620000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AMD", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2024", "value": 1620000000, "unit": "shares", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD's weighted-average basic shares outstanding in FY2024 was 1,620 million shares. This figure is based on the filing with accession number 0000002488-26-000018. The value is split-adjusted, meaning the per-share and share-count values are based on the latest filing that presents them.

**Evidence cited (1):**
- {"ticker": "AMD", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2024", "value": 1620000000, "unit": "shares", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A36

**Question:** What was Apple's cash and cash equivalents at the end of each of fiscal 2023, 2024 and 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [29965000000, 29943000000, 35934000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2023", "value": 29965000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2024", "value": 29943000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2025", "value": 35934000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple's cash and cash equivalents at the end of each fiscal year were as follows:  
> - **Fiscal 2023**: $29,965 million (as of September 30, 2023, filing accession: 0000320193-24-000123).  
> - **Fiscal 2024**: $29,943 million (as of September 28, 2024, filing accession: 0000320193-25-000079).  
> - **Fiscal 2025**: $35,934 million (as of September 27, 2025, filing accession: 0000320193-25-000079).  
> 
> There were no warnings to note.

**Evidence cited (3):**
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2023", "value": 29965000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-24-000123"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2024", "value": 29943000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2025", "value": 35934000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A37

**Question:** By how much did Nvidia's research and development expense change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1336000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2023", "value": 7339000000, "unit": "USD", "period_end": "2023-01-29", "use": "primary"}
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}

**Answer:**

> Nvidia's research and development expense increased by $1,336 million from fiscal 2023 to fiscal 2024. This represents an 18.2% increase. The data comes from the fiscal years FY2023 (accession: 0001045810-25-000023) and FY2024 (accession: 0001045810-26-000021).

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2023", "value": 7339000000, "unit": "USD", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}

---

## A38

**Question:** What basic EPS did Broadcom first report for fiscal 2023, and what figure do its filings show today?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 3.39, "original_val": 33.93, "original_accession": "0001730168-23-000096"}`, required warnings `['restated']`, tolerance `{"kind": "absolute", "abs": 0.01}`

Gold facts:
- {"ticker": "AVGO", "concept": "EarningsPerShareBasic", "period": "FY2023", "value": 3.39, "unit": "USD/shares", "period_end": "2023-10-29", "use": "primary"}

**Answer:**

> Broadcom first reported basic EPS of $33.93 per share for fiscal 2023 (accession number 0001730168-23-000096). Its current figure for FY2025 is $4.91 per share (accession number 0001730168-25-000121).

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "EarningsPerShareBasic", "period": "FY2023", "value": 3.39, "unit": "USD/shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "EarningsPerShareBasic", "period": "FY2025", "value": 4.91, "unit": "USD/shares", "period_end": "2025-11-02", "accession": "0001730168-25-000121"}

---

## A39

**Question:** What did Broadcom originally report as its weighted-average basic shares outstanding for fiscal 2023, and what is the figure now?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 4149000000, "original_val": 415000000, "original_accession": "0001730168-23-000096"}`, required warnings `['restated']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AVGO", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2023", "value": 4149000000, "unit": "shares", "period_end": "2023-10-29", "use": "primary"}

**Answer:**

> Broadcom originally reported 415 million shares as its weighted-average basic shares outstanding for fiscal 2023, based on the filing with accession number 0001730168-23-000096. The figure has since been revised to 4,149 million shares, which is now reported in the latest filing with accession number 0001730168-25-000121. The change reflects a restatement, and the current figure is split-adjusted.

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2023", "value": 4149000000, "unit": "shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}

---

## A40

**Question:** What operating margin did AMD earn in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 7.368625169672289, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "OperatingIncomeLoss", "period": "FY2024", "value": 1900000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD earned an operating margin of 7.4% in fiscal 2024. This figure is derived from an operating income of $1,900,000,000 and revenue of $25,785,000,000 for the same period. The operating margin is calculated as operating income divided by revenue.

**Evidence cited (2):**
- {"ticker": "AMD", "concept": "OperatingIncomeLoss", "period": "FY2024", "value": 1900000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A41

**Question:** Give Nvidia's diluted share count for fiscal 2023, fiscal 2024 and fiscal 2025.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [25070000000, 24940000000, 24804000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "use": "primary"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2024", "value": 24940000000, "unit": "shares", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2025", "value": 24804000000, "unit": "shares", "period_end": "2025-01-26", "use": "primary"}

**Answer:**

> Nvidia's diluted share count for the fiscal years, including restated values, is as follows:
> 
> - **FY2023**: 200,000,000 shares (accession number: 0001045810-25-000023, filing: 10-K, filed: 2025-02-26). A restated value of 20,000,000 shares was reported in accession number: 0001045810-23-000017.
> - **FY2024**: 250,000,000 shares (accession number: 0001045810-26-000021, filing: 10-K, filed: 2026-02-25). A restated value of 25,000,000 shares was reported in accession number: 0001045810-24-000029.
> - **FY2025**: 249,000,000 shares (accession number: 0001045810-26-000021, filing: 10-K, filed: 2026-02-25). No restated value reported.

**Evidence cited (3):**
- {"ticker": "NVDA", "concept": "WeightedAverageNumberDilutedSharesOutstandingAdjustment", "period": "FY2023", "value": 200000000, "unit": "shares", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberDilutedSharesOutstandingAdjustment", "period": "FY2024", "value": 250000000, "unit": "shares", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberDilutedSharesOutstandingAdjustment", "period": "FY2025", "value": 249000000, "unit": "shares", "period_end": "2025-01-26", "accession": "0001045810-26-000021"}

---

## A42

**Question:** What did Broadcom originally report as its weighted-average basic shares outstanding for fiscal 2023, and what is the figure now?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 4149000000, "original_val": 415000000, "original_accession": "0001730168-23-000096"}`, required warnings `['restated']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AVGO", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2023", "value": 4149000000, "unit": "shares", "period_end": "2023-10-29", "use": "primary"}

**Answer:**

> I could not verify an answer to this question against the filings, so I am not giving one. Try asking for a specific company, reported figure and fiscal year.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2023", "value": 4149000000, "unit": "shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "WeightedAverageNumberOfSharesOutstandingBasic", "period": "FY2025", "value": 4712000000, "unit": "shares", "period_end": "2025-11-02", "accession": "0001730168-25-000121"}

---

## A43

**Question:** What was Intel's gross profit in fiscal 2023?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 21711000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "GrossProfit", "period": "FY2023", "value": 21711000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}

**Answer:**

> Intel's gross profit in fiscal 2023 was $21,711 million, as reported in its 10-K filing with the SEC (accession number 0000050863-26-000011). This figure represents the gross profit for the fiscal year ending December 30, 2023.

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "GrossProfit", "period": "FY2023", "value": 21711000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000050863-26-000011"}

---

## A44

**Question:** Which had higher basic earnings per share in fiscal 2024, Apple or Microsoft?

**Gold:** outcome `unsupported_operation`, result `{"outcome": "unsupported_operation"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> In fiscal 2024, Microsoft had a higher basic earnings per share of $11.86 per share compared to Apple's $6.11 per share.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "EarningsPerShareBasic", "period": "FY2024", "value": 6.11, "unit": "USD/shares", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "MSFT", "concept": "EarningsPerShareBasic", "period": "FY2024", "value": 11.86, "unit": "USD/shares", "period_end": "2024-06-30", "accession": "0001193125-26-323660"}

---

## A45

**Question:** How much did Apple's net sales go up or down from fiscal 2023 to fiscal 2024, in dollars?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 7750000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> Apple's net sales (Revenue from Contract with Customer, Excluding Assessed Tax) increased from $383.285 billion in FY2023 to $391.035 billion in FY2024.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}

---

## A46

**Question:** What was Intel's net income attributable to Intel in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -18756000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> Intel's net income attributable to Intel in fiscal 2024 was a loss of $18,756 million, as reported in its 10-K filing with the SEC (accession number 0000050863-26-000011). This figure reflects the company's financial performance for the fiscal year ending December 28, 2024.

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}

---

## A47

**Question:** By how many percentage points did AMD's R&D as a share of revenue change from fiscal 2024 to fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1.6797480725362746, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 6456000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 8091000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 34639000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> R&D as a share of revenue for AMD increased by 1.56 percentage points from FY2024 to FY2025. 
> 
> - FY2024: $6.456 billion / $25.785 billion = 24.99%  
> - FY2025: $8.091 billion / $34.639 billion = 23.36%  
> 
> Difference: 24.99% - 23.36% = 1.63 percentage points.  
> 
> (Note: The exact calculation may vary slightly due to rounding.)

**Evidence cited (4):**
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 6456000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 8091000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 34639000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000002488-26-000018"}

---

## A48

**Question:** Give Nvidia's diluted share count for fiscal 2023, fiscal 2024 and fiscal 2025.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [25070000000, 24940000000, 24804000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "use": "primary"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2024", "value": 24940000000, "unit": "shares", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2025", "value": 24804000000, "unit": "shares", "period_end": "2025-01-26", "use": "primary"}

**Answer:**

> Nvidia's diluted share count for fiscal years 2023, 2024, and 2025 was 25,070 million shares, 24,940 million shares, and 24,804 million shares, respectively. These figures are based on the latest filings and are split-adjusted. 
> 
> A warning notes that the FY2023 and FY2024 values were reported differently in earlier filings, but the current values provided are the most recent and accurate. The FY2025 value is based on the same latest filing as FY2024.

**Evidence cited (3):**
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2024", "value": 24940000000, "unit": "shares", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2025", "value": 24804000000, "unit": "shares", "period_end": "2025-01-26", "accession": "0001045810-26-000021"}

---

## A49

**Question:** By what percentage did Broadcom's total operating expenses change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 124.51962749027467, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2023", "value": 8483000000, "unit": "USD", "period_end": "2023-10-29", "use": "primary"}
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2024", "value": 19046000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> Broadcom's total operating expenses increased by 124.5% from fiscal 2023 to fiscal 2024. In fiscal 2023, operating expenses were $8,483 million, and in fiscal 2024, they rose to $19,046 million. The data comes from the filings with accession numbers 0001730168-25-000121.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2023", "value": 8483000000, "unit": "USD", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2024", "value": 19046000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A50

**Question:** What was Broadcom's long-term debt at the end of fiscal 2024?

**Gold:** outcome `not_reported`, result `{"outcome": "not_reported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> Broadcom's long-term debt at the end of fiscal 2024 was $69.847 billion, as reported in accession number 0001730168-24-000139.

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "DebtInstrumentCarryingAmount", "period": "FY2024", "value": 69847000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-24-000139"}

---

## A51

**Question:** By what percentage did Apple's gross margin dollars change from FY2024 to FY2025? Give both figures.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 8.035066940442654, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2024", "value": 180683000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2025", "value": 195201000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple's gross margin dollars increased from $180.683 billion in FY2024 to $195.201 billion in FY2025. The percentage change is calculated as follows: 
> 
> $$
> \frac{195.201 - 180.683}{180.683} \times 100 = 8.03\%
> $$
> 
> Thus, the gross margin dollars increased by 8.03%.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2024", "value": 180683000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2025", "value": 195201000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A52

**Question:** Has Nvidia's reported weighted-average diluted shares outstanding for fiscal 2023 been revised? Give the original and current figures.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 25070000000, "original_val": 2507000000, "original_accession": "0001045810-23-000017"}`, required warnings `['restated']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "use": "primary"}

**Answer:**

> Yes, Nvidia's reported weighted-average diluted shares outstanding for fiscal 2023 has been revised. The original figure was **2,507 million shares** from filing accession **0001045810-23-000017**, and the current figure is **25,070 million shares** from filing accession **0001045810-25-000023**. The revision indicates a change in the reported value, likely due to a restatement or adjustment in the accounting method. The current value is split-adjusted, meaning it reflects any stock splits or adjustments that occurred after the original filing.

**Evidence cited (1):**
- {"ticker": "NVDA", "concept": "WeightedAverageNumberOfDilutedSharesOutstanding", "period": "FY2023", "value": 25070000000, "unit": "shares", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}

---

## A53

**Question:** By how much did Nvidia's research and development expense change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1336000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2023", "value": 7339000000, "unit": "USD", "period_end": "2023-01-29", "use": "primary"}
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}

**Answer:**

> The research and development expense for Nvidia increased from $7.339 billion in FY2023 to $8.675 billion in FY2024. 
> 
> - FY2023: $7.339 billion (accession 0001045810-25-000023)
> - FY2024: $8.675 billion (accession 0001045810-26-000021)

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2023", "value": 7339000000, "unit": "USD", "period_end": "2023-01-29", "accession": "0001045810-25-000023"}
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}

---

## A54

**Question:** What was AMD's stock-based compensation expense in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 1407000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AMD", "concept": "ShareBasedCompensation", "period": "FY2024", "value": 1407000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> AMD's stock-based compensation expense in fiscal 2024 was $1.407 billion, as reported in its 10-K filing (accession number 0000002488-26-000018).

**Evidence cited (1):**
- {"ticker": "AMD", "concept": "ShareBasedCompensation", "period": "FY2024", "value": 1407000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}

---

## A55

**Question:** Compare Nvidia's and Microsoft's long-term debt for fiscal 2024.

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [9709000000, 44937000000], "difference": -35228000000}`, required warnings `['period_mismatch']`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "LongTermDebt", "period": "FY2024", "value": 9709000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2024", "value": 44937000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> _NVDA FY2024 Long-term Debt (Noncurrent): $8.459 billion (accession 0001045810-25-000023).  
> _MSFT FY2024 Long-term Debt (Noncurrent): $42.688 billion (accession 0000950170-25-100235).

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "LongTermDebtNoncurrent", "period": "FY2024", "value": 8459000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-25-000023"}
- {"ticker": "MSFT", "concept": "LongTermDebtNoncurrent", "period": "FY2024", "value": 42688000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0000950170-25-100235"}

---

## A56

**Question:** Calculate Nvidia's R&D as a share of revenue for FY2024.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 14.239519385443684, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "NVDA", "concept": "Revenues", "period": "FY2024", "value": 60922000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}

**Answer:**

> Nvidia's R&D as a share of revenue for FY2024 was 14.2%. This is calculated by dividing the R&D expense of $8,675,000,000 by the revenue of $60,922,000,000. The figures are from the filing with accession number 0001045810-26-000021, which covers the fiscal year ending January 28, 2024.

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}
- {"ticker": "NVDA", "concept": "Revenues", "period": "FY2024", "value": 60922000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}

---

## A57

**Question:** How many percentage points did Apple's net profit margin change from FY2023 to FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1.3349784943764154, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2023", "value": 96995000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2024", "value": 93736000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> Apple's net profit margin decreased by **1.3 percentage points** from FY2023 to FY2024. This change is based on the data from the filings with accession numbers provided. The net margin is calculated as net income divided by revenue, and the decrease indicates a lower proportion of revenue converted into net profit in FY2024 compared to FY2023.

**Evidence cited (4):**
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2023", "value": 96995000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "NetIncomeLoss", "period": "FY2024", "value": 93736000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}

---

## A58

**Question:** How much was Nvidia's research and development expense in FY2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 12914000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 12914000000, "unit": "USD", "period_end": "2025-01-26", "use": "primary"}

**Answer:**

> Nvidia's research and development expense in FY2025 was $12.914 billion, as reported in accession number 0001045810-26-000021.

**Evidence cited (1):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 12914000000, "unit": "USD", "period_end": "2025-01-26", "accession": "0001045810-26-000021"}

---

## A59

**Question:** By how much did Apple's capital expenditures change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1512000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2023", "value": 10959000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2024", "value": 9447000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> None of the listed XBRL tags for Apple (AAPL) directly measure "capital expenditures." Please clarify or provide the exact term you're referring to.

**Evidence cited (0):**

---

## A60

**Question:** What basic EPS did Broadcom first report for fiscal 2023, and what figure do its filings show today?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 3.39, "original_val": 33.93, "original_accession": "0001730168-23-000096"}`, required warnings `['restated']`, tolerance `{"kind": "absolute", "abs": 0.01}`

Gold facts:
- {"ticker": "AVGO", "concept": "EarningsPerShareBasic", "period": "FY2023", "value": 3.39, "unit": "USD/shares", "period_end": "2023-10-29", "use": "primary"}

**Answer:**

> Broadcom first reported a basic EPS of $33.93 per share for fiscal 2023 in its filing dated December 14, 2023 (accession: 0001730168-23-000096). However, the filings now show a revised basic EPS of $3.39 per share, which is significantly lower. This change indicates a restatement, and the current figure is split-adjusted based on the latest filing (accession: 0001730168-25-000121). The difference between the original and current values is due to a restatement, which may reflect adjustments in accounting or share counts.

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "EarningsPerShareBasic", "period": "FY2023", "value": 3.39, "unit": "USD/shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}

---

## A61

**Question:** What will AMD's revenue be in fiscal 2026?

**Gold:** outcome `unsupported`, result `{"outcome": "unsupported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The figure cannot be given because the question refers to a fiscal year (FY2026) outside the covered range of FY2023 to FY2025. No data is available for FY2026.

**Evidence cited (0):**

---

## A62

**Question:** Calculate Nvidia's R&D as a share of revenue for FY2024.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 14.239519385443684, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}
- {"ticker": "NVDA", "concept": "Revenues", "period": "FY2024", "value": 60922000000, "unit": "USD", "period_end": "2024-01-28", "use": "primary"}

**Answer:**

> Nvidia's R&D expense for FY2024 was $8.675 billion, and its revenue was $60.922 billion. R&D as a share of revenue is $8.675 billion / $60.922 billion = 14.24%.

**Evidence cited (2):**
- {"ticker": "NVDA", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 8675000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}
- {"ticker": "NVDA", "concept": "Revenues", "period": "FY2024", "value": 60922000000, "unit": "USD", "period_end": "2024-01-28", "accession": "0001045810-26-000021"}

---

## A63

**Question:** By how many percentage points did AMD's R&D as a share of revenue change from fiscal 2024 to fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1.6797480725362746, "unit": "pp"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 6456000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 8091000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 34639000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> AMD's R&D as a share of revenue decreased by **1.7 percentage points** from fiscal 2024 to fiscal 2025. This change is based on the following data:
> 
> - In fiscal 2024, R&D expenses were $6,456 million, and revenue was $25,785 million.
> - In fiscal 2025, R&D expenses were $8,091 million, and revenue was $34,639 million.
> 
> The calculation shows a decrease in R&D intensity as a share of revenue.

**Evidence cited (4):**
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2024", "value": 6456000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 25785000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "ResearchAndDevelopmentExpense", "period": "FY2025", "value": 8091000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2025", "value": 34639000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000002488-26-000018"}

---

## A64

**Question:** What was the year-over-year percent change in AMD's income tax expense in fiscal 2024?

**Gold:** outcome `not_meaningful`, result `{"outcome": "not_meaningful", "absolute_change": 727000000}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2023", "value": -346000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2024", "value": 381000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}

**Answer:**

> I could not verify an answer to this question against the filings, so I am not giving one. Try asking for a specific company, reported figure and fiscal year.

**Evidence cited (2):**
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2024", "value": 381000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000002488-26-000018"}
- {"ticker": "AMD", "concept": "IncomeTaxExpenseBenefit", "period": "FY2023", "value": -346000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000002488-26-000018"}

---

## A65

**Question:** What was Intel's total stockholders' equity at the end of fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 114281000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "StockholdersEquity", "period": "FY2025", "value": 114281000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Intel's total stockholders' equity at the end of fiscal 2025 was $114,281 million, as reported in its filing with accession number 0000050863-26-000011.

**Evidence cited (1):**
- {"ticker": "INTC", "concept": "StockholdersEquity", "period": "FY2025", "value": 114281000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A66

**Question:** What was Apple's cash and cash equivalents at the end of each of fiscal 2023, 2024 and 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [29965000000, 29943000000, 35934000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2023", "value": 29965000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2024", "value": 29943000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2025", "value": 35934000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple's cash and cash equivalents at the end of each fiscal year were:
> 
> - **FY2023**: $29.965 billion (accession: 0000320193-24-000123)
> - **FY2024**: $29.943 billion (accession: 0000320193-25-000079)
> - **FY2025**: $35.934 billion (accession: 0000320193-25-000079)

**Evidence cited (3):**
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2023", "value": 29965000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-24-000123"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2024", "value": 29943000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "CashAndCashEquivalentsAtCarryingValue", "period": "FY2025", "value": 35934000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A67

**Question:** What was Broadcom's gross margin in fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 63.03369915073487, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "GrossProfit", "period": "FY2024", "value": 32509000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}
- {"ticker": "AVGO", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 51574000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> Broadcom's gross profit in fiscal 2024 was $32.509 billion, as reported in accession number 0001730168-25-000121.

**Evidence cited (1):**
- {"ticker": "AVGO", "concept": "GrossProfit", "period": "FY2024", "value": 32509000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A68

**Question:** How much did Apple's net sales go up or down from fiscal 2023 to fiscal 2024, in dollars?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 7750000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> Apple's net sales increased by $7,750 million from fiscal 2023 to fiscal 2024. The revenue for fiscal 2023 was $383,285 million, and for fiscal 2024, it was $391,035 million, according to the filings with accession numbers 0000320193-25-000079.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 383285000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 391035000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}

---

## A69

**Question:** What was Apple's revenue in fiscal 2026?

**Gold:** outcome `out_of_range`, result `{"outcome": "out_of_range"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The figure cannot be given because Apple's fiscal 2026 data is not available in the covered period of FY2023 to FY2025.

**Evidence cited (0):**

---

## A70

**Question:** By what percentage did Broadcom's diluted EPS change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -62.72727272727272, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2023", "value": 3.3, "unit": "USD/shares", "period_end": "2023-10-29", "use": "primary"}
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2024", "value": 1.23, "unit": "USD/shares", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> Broadcom's diluted EPS decreased by 62.7% from fiscal 2023 to fiscal 2024. The diluted EPS for fiscal 2023 was $3.30 per share, and for fiscal 2024, it was $1.23 per share. The data comes from the latest filing (accession 0001730168-25-000121). A warning notes that the 2023 value was reported differently in an earlier filing (accession 0001730168-23-000096), and the results are split-adjusted based on the latest filing.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2023", "value": 3.3, "unit": "USD/shares", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "EarningsPerShareDiluted", "period": "FY2024", "value": 1.23, "unit": "USD/shares", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A71

**Question:** What was the percentage change in Intel's net income from fiscal 2024 to fiscal 2025?

**Gold:** outcome `not_meaningful`, result `{"outcome": "not_meaningful", "absolute_change": 18489000000}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2025", "value": -267000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> The percentage change in Intel's net income from fiscal 2024 to fiscal 2025 is calculated as follows:
> 
> - FY2024 Net Income: -$18.756 billion
> - FY2025 Net Income: -$267 million
> 
> Percentage change = ((-267 - (-18756)) / -18756) * 100 = 99.86% increase.

**Evidence cited (2):**
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2024", "value": -18756000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "NetIncomeLoss", "period": "FY2025", "value": -267000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}

---

## A72

**Question:** By how much did Apple's capital expenditures change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": -1512000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2023", "value": 10959000000, "unit": "USD", "period_end": "2023-09-30", "use": "primary"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2024", "value": 9447000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}

**Answer:**

> Apple's capital expenditures decreased by $1,512 million from fiscal 2023 to fiscal 2024. This represents a 13.8% decrease. The data comes from the fiscal years FY2023 and FY2024 filings.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2023", "value": 10959000000, "unit": "USD", "period_end": "2023-09-30", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2024", "value": 9447000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}

---

## A73

**Question:** What was Apple's revenue in fiscal 2026?

**Gold:** outcome `out_of_range`, result `{"outcome": "out_of_range"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The question refers to a fiscal year that is outside the range of FY2023 to FY2025. I cannot provide data for FY2026.

**Evidence cited (0):**

---

## A74

**Question:** By what percentage did Apple's gross margin dollars change from FY2024 to FY2025? Give both figures.

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 8.035066940442654, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2024", "value": 180683000000, "unit": "USD", "period_end": "2024-09-28", "use": "primary"}
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2025", "value": 195201000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple's gross margin dollars increased by 8.0% from FY2024 to FY2025. In FY2024, the gross profit was $180,683 million, and in FY2025, it was $195,201 million.

**Evidence cited (2):**
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2024", "value": 180683000000, "unit": "USD", "period_end": "2024-09-28", "accession": "0000320193-25-000079"}
- {"ticker": "AAPL", "concept": "GrossProfit", "period": "FY2025", "value": 195201000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A75

**Question:** What was the dollar change in Microsoft's cost of revenue between FY2023 and FY2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 8251000000, "unit": "USD"}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2023", "value": 65863000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "MSFT", "concept": "CostOfGoodsAndServicesSold", "period": "FY2024", "value": 74114000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> I could not verify an answer to this question against the filings, so I am not giving one. Try asking for a specific company, reported figure and fiscal year.

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2023", "value": 211915000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "MSFT", "concept": "RevenueFromContractWithCustomerExcludingAssessedTax", "period": "FY2024", "value": 245122000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0001193125-26-323660"}

---

## A76

**Question:** By what percentage did Microsoft's total stockholders' equity change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 30.18770942135455, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2023", "value": 206223000000, "unit": "USD", "period_end": "2023-06-30", "use": "primary"}
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2024", "value": 268477000000, "unit": "USD", "period_end": "2024-06-30", "use": "primary"}

**Answer:**

> The percentage change in Microsoft's total stockholders' equity from FY2023 to FY2024 is calculated as follows:
> 
> - FY2023: $206.223 billion
> - FY2024: $268.477 billion
> 
> $$
> \text{Percentage Change} = \left( \frac{268.477 - 206.223}{206.223} \right) \times 100 = 30.23\%
> $$
> 
> Thus, Microsoft's total stockholders' equity increased by **30.23%** from FY2023 to FY2024.

**Evidence cited (2):**
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2023", "value": 206223000000, "unit": "USD", "period_end": "2023-06-30", "accession": "0000950170-25-100235"}
- {"ticker": "MSFT", "concept": "StockholdersEquity", "period": "FY2024", "value": 268477000000, "unit": "USD", "period_end": "2024-06-30", "accession": "0001193125-26-323660"}

---

## A77

**Question:** By what percentage did Broadcom's total operating expenses change from fiscal 2023 to fiscal 2024?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 124.51962749027467, "unit": "percent"}`, required warnings `[]`, tolerance `{"kind": "percentage_points", "abs": 0.1}`

Gold facts:
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2023", "value": 8483000000, "unit": "USD", "period_end": "2023-10-29", "use": "primary"}
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2024", "value": 19046000000, "unit": "USD", "period_end": "2024-11-03", "use": "primary"}

**Answer:**

> The percentage change in Broadcom's total operating expenses from fiscal 2023 to fiscal 2024 is calculated as follows:
> 
> - FY2023: $8.483 billion
> - FY2024: $19.046 billion
> 
> Percentage change = ((19.046 - 8.483) / 8.483) * 100 = 124.56%.

**Evidence cited (2):**
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2023", "value": 8483000000, "unit": "USD", "period_end": "2023-10-29", "accession": "0001730168-25-000121"}
- {"ticker": "AVGO", "concept": "OperatingExpenses", "period": "FY2024", "value": 19046000000, "unit": "USD", "period_end": "2024-11-03", "accession": "0001730168-25-000121"}

---

## A78

**Question:** What was Microsoft's long-term debt balance at the end of FY2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 43151000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2025", "value": 43151000000, "unit": "USD", "period_end": "2025-06-30", "use": "primary"}

**Answer:**

> Microsoft's long-term debt balance at the end of FY2025 was $43,151 million, as reported in its 10-K filing with the SEC (accession number 0001193125-26-323660). The figure reflects the debt balance as of June 30, 2025.

**Evidence cited (1):**
- {"ticker": "MSFT", "concept": "LongTermDebt", "period": "FY2025", "value": 43151000000, "unit": "USD", "period_end": "2025-06-30", "accession": "0001193125-26-323660"}

---

## A79

**Question:** How much free cash flow did Apple generate in fiscal 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "val": 98767000000}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "AAPL", "concept": "NetCashProvidedByUsedInOperatingActivities", "period": "FY2025", "value": 111482000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}
- {"ticker": "AAPL", "concept": "PaymentsToAcquirePropertyPlantAndEquipment", "period": "FY2025", "value": 12715000000, "unit": "USD", "period_end": "2025-09-27", "use": "primary"}

**Answer:**

> Apple generated $5.991 billion in free cash flow in fiscal 2025 (CY2025), as reported in accession number 0000320193-25-000079.

**Evidence cited (1):**
- {"ticker": "AAPL", "concept": "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect", "period": "FY2025", "value": 5991000000, "unit": "USD", "period_end": "2025-09-27", "accession": "0000320193-25-000079"}

---

## A80

**Question:** What was Intel's selling, general and administrative expense in each of fiscal 2023, 2024 and 2025?

**Gold:** outcome `answer`, result `{"outcome": "answer", "vals": [5634000000, 5507000000, 4624000000]}`, required warnings `[]`, tolerance `{"kind": "relative", "rel": 0.005}`

Gold facts:
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2023", "value": 5634000000, "unit": "USD", "period_end": "2023-12-30", "use": "primary"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2024", "value": 5507000000, "unit": "USD", "period_end": "2024-12-28", "use": "primary"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2025", "value": 4624000000, "unit": "USD", "period_end": "2025-12-27", "use": "primary"}

**Answer:**

> Intel's selling, general, and administrative expense was $5,634 million in fiscal 2023, $5,507 million in fiscal 2024, and $4,624 million in fiscal 2025. These figures are sourced from the respective annual filings for each fiscal year.

**Evidence cited (3):**
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2023", "value": 5634000000, "unit": "USD", "period_end": "2023-12-30", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2024", "value": 5507000000, "unit": "USD", "period_end": "2024-12-28", "accession": "0000050863-26-000011"}
- {"ticker": "INTC", "concept": "SellingGeneralAndAdministrativeExpense", "period": "FY2025", "value": 4624000000, "unit": "USD", "period_end": "2025-12-27", "accession": "0000050863-26-000011"}
