# External benchmarks: coverage check (2026-11-17)

Before running a public benchmark we checked how many of its questions fall inside this system's scope
(Apple, Microsoft, Nvidia, Oracle, Cisco, Broadcom, Intel, AMD; fiscal years 2023-2025; 28 annual GAAP metrics).

| Benchmark (public release) | Questions | About our 8 companies | Inside our scope |
|---|---|---|---|
| FinanceBench, PatronusAI/financebench (open sample) | 150 | 10 (AMD FY2015 and FY2022, Microsoft FY2016 and FY2023) | 0: the one Microsoft FY2023 question compares debt with FY2022 |
| FinRetrieval, daloopa/finretrieval (Jan 2026) | 500 | 0 | 0 |
| BIG Finance subset, RogoAI/big-finance-benchmark | 50 | 0 by company (2 matches are unrelated text) | 0 |
| Finance Agent Benchmark, vals-ai/finance_agent_benchmark | 50 | 4 (AMD guidance x2, Microsoft headcount, Oracle effective tax rate) | 0: guidance and headcount are not XBRL annual metrics; effective tax rate is not in the ontology |

So no public benchmark could be run on this system without changing its scope, and none was run. The external
comparison in the README remains the 30 seeded test questions asked to Perplexity, scored by the frozen scorer.

What this says about the system, stated as a limitation: public financial-QA benchmarks sample hundreds of companies,
quarters, guidance, segments and non-GAAP figures; this system covers 8 companies' annual GAAP figures. Widening
coverage (see the scaling notes in the project log) is what a public benchmark would test.

Files were read from the Hugging Face Hub (datasets listed above) on 2026-11-17; nothing from them is committed.
