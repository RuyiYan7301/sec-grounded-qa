# Human audit: 25 of the 80 blind records

Seeded sample (seed 2611) of the blind Part A audit pack. Same records, same rules as pack.md. No system name, no plan, no scorer output. Fill form_human.csv (y / n / na per column, note when anything is n or close). Do not open key_sealed.json, form_model_judge.csv or agreement_model_judge.json before the form is complete.

Judge each record against the gold: is the answer right for the person who asked (number, direction, years, required warnings; or a refusal for the right reason), is the cited evidence complete, the right concept and period, and is the calculation right? Each record takes about one minute.

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

## A07

**Question:** How much goodwill did Apple carry at the end of fiscal 2023?

**Gold:** outcome `not_reported`, result `{"outcome": "not_reported"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The XBRL tag for "goodwill" is not directly available for Apple (AAPL) in FY2023. The closest related tags are "Intangible Assets, Net (Excluding Goodwill)" and "Intangible Assets, Gross (Excluding Goodwill)." These tags do not include goodwill. You may need to consult the 10-K filing for more detailed information on goodwill.

**Evidence cited (0):**

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

## A16

**Question:** What was Nvidia's EBITDA in fiscal 2025?

**Gold:** outcome `out_of_ontology`, result `{"outcome": "out_of_ontology"}`, required warnings `[]`, tolerance `null`

Gold facts:

**Answer:**

> The term "EBITDA" does not correspond to any XBRL tag for Nvidia (NVDA) in the fiscal years FY2023, FY2024, or FY2025. Please clarify or provide an alternative metric.

**Evidence cited (0):**

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
