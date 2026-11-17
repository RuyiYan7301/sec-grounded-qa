# Failure analysis: the 15 typed-engine misses on the frozen test set

Run: `results/test/pipeline/run_61b72567_20261116T174624Z.json` (frozen benchmark and scorer 2.1, qwen3:8b, run once).
Score: 145/160. This note reads each of the 15 misses. It was written after the run by the person who built the
system, so it is not blind; the frozen score is not changed by it.

## Summary

| Kind | Items | Engine outcome right? | What went wrong |
|---|---|---|---|
| Refusal worded outside the scorer's patterns | 9 | yes | the plan refused for the right reason; the rendered sentence ("cannot be given", "cannot be provided", "could not be meaningfully calculated") matches none of the frozen refusal patterns |
| Scope note given, not in the scorer's words | 2 | yes | the answer names the substitute concept (`PaymentsToAcquireProductiveAssets`); the pattern looks for "productive assets" |
| Scope note incomplete | 1 | yes | the answer names `ProfitLoss` but does not say it includes non-controlling interests |
| Wrong words or figures in the rendered answer | 1 | yes | sign and two unit slips in the text; the computed result was right |
| Planner chose the wrong concept | 2 | no | "total debt" mapped to long-term debt; "EPS" read as basic, not diluted |

So 11 of the 15 are scorer or wording artifacts on a right engine outcome, and 4 are real errors (one in the
explanation, one in the rendered text, two in the plan). Read this way the engine's outcome is right on 156/160,
but that figure is a post-hoc, non-blind reading and is not the reported score; the blind model audit of 40 records
(`results/test/audit/`) found 1 scorer disagreement for this system.

## Each item

**Refusals worded outside the patterns (9).** A-test-adv-001 (EBITDA), adv-003 (segment revenue), adv-004 (a
quarter), adv-006 (EBIT): out of ontology, refused for that reason, answer "The figure cannot be given because ...".
adv-029 (sell my shares), adv-030 (is management doing a good job), adv-032 (predict EPS): unsupported, refused,
"cannot be provided". adv-037 (compare two companies' diluted EPS): the executor refused (cross-company per-share
comparison is not allowed), "cannot be provided because ... not allowed". han-025 (percent change of Intel's net
income from a loss): `not_meaningful` was right; the answer says "could not be meaningfully calculated", which the
not-meaningful pattern does not cover, and its explanation is muddled.

**Scope note not in the scorer's words (2).** adv-016, adv-017 (Nvidia capex): the engine resolved capex through
the fallback concept `PaymentsToAcquireProductiveAssets` and the answer says so, but writes the concept name as one
word, which the scope pattern ("productive assets") does not match.

**Scope note incomplete (1).** adv-015 (Broadcom net income FY2025): resolved through `ProfitLoss`; the answer names
the concept but not what makes it broader (it includes non-controlling interests). A reader could not tell the
figure is not "net income attributable to Broadcom".

**Rendered text wrong (1).** han-022 (dollar change in Intel's net income, FY2024 to FY2025): the engine computed
+$18,489 million (a loss of $18,756 million narrowing to $267 million). The answer calls it "a decrease of $18,489
million", writes the FY2024 loss as "$18,756 billion" and the FY2025 loss as "$2,670 million". The product's safety
net, added after this run, rejects text with untraced or misplaced numbers and writes the answer from the computed
result instead; the same question in the public demo shows that replacement (`data/demo/answers.json`).

**Planner concept errors (2).** adv-002 ("Intel's total debt"): planned as a lookup of long-term debt and answered
$50,011 million; total debt (current portion included) is not in the ontology, so the right outcome was a refusal.
han-040 ("Nvidia's fiscal 2023 EPS ... revised?"): planned as basic EPS; by the ontology's convention plain "EPS"
means diluted, with an `alias_interpretation` warning. The answer gives basic EPS figures with the right filings.

## What would fix each, and what it would cost

| Fix | Addresses | Cost | Risk |
|---|---|---|---|
| Write refusal and not-meaningful sentences from code templates instead of the renderer | 9 wording misses | small | none for figures; changes the answer style |
| Write the scope note from the warning (concept, what it includes) | 3 scope items | small | none |
| Safety net (already in the product): untraced or misplaced numbers replaced by an answer written from the result | the han-022 class | done | answers written by code read less naturally |
| Add "total debt" and "EPS" handling to the ontology: refuse total debt or define it; map plain EPS to diluted with the alias warning | 2 planner misses | small | needs the dev set re-run; this frozen test set cannot be used to check it |

Any of these is a change to the engine after its test run. It would need a new engine version checked on the
development set, and a fresh held-out set to report a new number.
