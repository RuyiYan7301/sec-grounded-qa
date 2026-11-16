import copy
import json
from pathlib import Path

root = Path(__file__).parent
data = json.loads((root / 'template.json').read_text(encoding='utf-8'))
data['calibrator'] = 'Codex GPT-5'
data['date'] = '2026-11-15'

def ev(item):
    out = []
    for c in item.get('gold_cells', []):
        out.append({k: v for k, v in c.items() if k != 'use'})
    return out

def scores(**kw):
    base = {k: None for k in data['vector']}
    base.update(kw)
    return base

def set_slot(slot, answer, evidence=None, plan=None, result=None, expected=None, note=''):
    s = next(x for x in data['slots'] if x['slot'] == slot)
    r = s['record']
    r['answer'] = answer
    r['evidence'] = ev(s['item']) if evidence is None else evidence
    r['plan'] = plan
    r['result'] = result
    s['expected_scores'] = expected
    s['na_ok'] = {k: True for k, v in expected.items() if v is None}
    s['calibrator_note'] = note

def v01(item):
    return None

def gold_plan(slot):
    s = next(x for x in data['slots'] if x['slot'] == slot)
    return copy.deepcopy(s['item']['gold_plan'])

def gold_result(slot):
    s = next(x for x in data['slots'] if x['slot'] == slot)
    return copy.deepcopy(s['item']['gold_result'])

# Numeric and warning records (v0.1: plan/result do not apply).
set_slot('N1', 'Oracle reported income tax expense of $623,000 million in FY2023.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=False, concept='canonical', period_ok=True), note='The amount is scaled as millions instead of the gold-dollar amount.')
set_slot('N2', 'Oracle basic EPS was $3.82 in fiscal 2024.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='Two-decimal EPS matches the gold within the EPS tolerance.')
set_slot('N3', 'The weighted-average diluted share count was 2,866,000,000 shares in FY2025.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The share count and unit are stated explicitly.')
set_slot('N4', 'Cisco capex increased 35.07% year over year in FY2025.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='35.07% is the FY2024-to-FY2025 percentage change.')
set_slot('N5', 'Oracle’s net margin rose by 2.74 percentage points from FY2023 to FY2024.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The answer uses percentage-point language for the margin difference.')
set_slot('N6', 'Intel net income attributable to Intel was 18,756,000,000 dollars in FY2024.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The magnitude is present but no loss, negative sign, or parentheses indicate the negative amount.')
set_slot('N7', 'Oracle’s FY2023 net income was $8.6 billion.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=False, concept='canonical', period_ok=True), note='The plausible rounded number is outside the 0.5% tolerance.')
set_slot('N8', 'Cisco’s operating expenses decreased by $1.925 billion from FY2023 to FY2024.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The magnitude is right but the direction contradicts the increase in the gold values.')
set_slot('W1', 'Cisco was higher: $19.886 billion versus Oracle’s $17.165 billion. The fiscal year ends differ, so this comparison carries a period-mismatch warning.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The answer gives both values and explicitly identifies the fiscal period-end mismatch.')
set_slot('W2', 'Broadcom’s FY2025 net income was $23.126 billion. This uses the reported ProfitLoss fallback, so scope is broader than parent-attributable net income.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='qualified_alternative', period_ok=True), note='The fallback concept and its broader scope are disclosed.')
orig = {'ticker':'AMD','metric':'selling_general_administrative','period':'FY2024','concept':'SellingGeneralAndAdministrativeExpense','value':2783000000,'unit':'USD','accession':'0000002488-25-000012','period_end':'2024-12-28'}
set_slot('W3', 'AMD originally reported $2.783 billion of FY2024 SG&A; the recast figure is now $2.735 billion.', evidence=ev(next(x for x in data['slots'] if x['slot']=='W3')['item']) + [orig], expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='Both original and current values are stated, and the accounting recast is identified.')
set_slot('W4', 'Cisco’s EPS, interpreted as diluted EPS, was $2.54 in FY2024; the filing also reports basic EPS separately.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='Bare EPS is resolved to diluted EPS and the interpretation warning is stated.')
set_slot('W5', 'Cisco’s revenue for 2024—treated here as fiscal FY2024—was $53.803 billion; the year wording is ambiguous for fiscal-year reporting.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The answer states the FY interpretation and flags the bare-year ambiguity.')
set_slot('W6', 'Oracle had $134.384 billion of assets versus Cisco’s $101.852 billion in FY2023, a $32.532 billion difference.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='The values and difference are correct, but the required period-mismatch warning is omitted.')

# Refusal records.
set_slot('R1', 'Cisco did not report SG&A as a separately available FY2025 metric in the specified filing data, so I cannot provide a figure.', evidence=[], expected=scores(final_correct=True, appropriate_refusal=True, evidence_complete=True), note='Correctly declines an unavailable metric without asserting a number.')
set_slot('R2', 'I can’t determine whether Oracle is overvalued from SEC 10-K financial-statement data; that is an investment judgment requiring market data and assumptions.', evidence=[], expected=scores(final_correct=True, appropriate_refusal=True, evidence_complete=True), note='The unsupported valuation question is declined without investment advice.')
set_slot('R3', 'Cisco EBITDA is outside the benchmark ontology, although one possible filing-derived figure would be about $15 billion; I cannot answer it reliably.', evidence=[], expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=False), note='The refusal is undermined by asserting a figure for an out-of-ontology metric.')
set_slot('R4', 'AMD’s income-tax expense changed by $727 million, but a conventional percentage change is not meaningful because the FY2023 base was negative.', expected=scores(final_correct=True, appropriate_refusal=True, evidence_complete=True, concept='canonical', period_ok=True), note='It reports the absolute change, explains the negative base, and gives no percentage.')
set_slot('R5', 'Nvidia’s income-tax expense changed by 2,270.6% from FY2023 to FY2024, even though the starting value was negative.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='A percentage is stated despite the negative base, contrary to the not-meaningful rule.')

# Evidence-focused v0.1 records.
set_slot('E1', 'Oracle’s FY2024 operating margin was 28.99%, calculated as $15.353 billion divided by $52.961 billion.', expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='canonical', period_ok=True), note='Every stated component and the resulting percentage are supported by complete evidence.')
bad_meta = ev(next(x for x in data['slots'] if x['slot']=='E2')['item']); bad_meta[0].pop('accession'); bad_meta[0].pop('period_end')
set_slot('E2', 'Oracle’s FY2023 income-tax expense was $623 million.', evidence=bad_meta, expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=False, concept='canonical', period_ok=True), note='The value is correct, but the evidence item lacks accession and period-end provenance.')
set_slot('E3', 'Oracle’s FY2023 net income was $8.6 billion.', expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=False, concept='canonical', period_ok=True), note='The stated amount is not supported by the evidence value of $8.503 billion.')

# Structured v0.2 records.
set_slot('S1', 'Oracle’s FY2024 operating margin was 28.99%.', plan=gold_plan('S1'), result=gold_result('S1'), expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, plan_valid=True, intent_ok=True, concept='canonical', period_ok=True, calculation_ok=True), note='Plan, evidence cells, answer, and computed result all agree with gold.')
p2 = gold_plan('S2'); p2['extra'] = 'invalid schema property'
set_slot('S2', 'Cisco capex rose 35.07% from FY2024 to FY2025.', plan=p2, result=gold_result('S2'), expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, plan_valid=False, intent_ok=True, concept='canonical', period_ok=True, calculation_ok=True), note='The plan has an additional forbidden property, so schema validation fails while its intent and result remain correct.')
p3 = gold_plan('S3'); p3['intent'] = 'absolute_change'
set_slot('S3', 'Cisco capex rose 35.07% from FY2024 to FY2025.', plan=p3, result=gold_result('S3'), expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, plan_valid=True, intent_ok=False, concept='canonical', period_ok=True, calculation_ok=True), note='The plan is schema-valid but declares the wrong operation intent.')
e4 = ev(next(x for x in data['slots'] if x['slot']=='S4')['item']); e4[0]['concept'] = 'IncomeTaxesPaid'
set_slot('S4', 'Oracle’s FY2023 income-tax expense was $623 million.', evidence=e4, plan=gold_plan('S4'), result=gold_result('S4'), expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, plan_valid=True, intent_ok=True, concept='incorrect', period_ok=True, calculation_ok=True), note='The numeric value is right, but the evidence concept is cash taxes paid rather than tax expense.')
e5 = ev(next(x for x in data['slots'] if x['slot']=='S5')['item']); e5[0]['period_end'] = '2022-05-31'
set_slot('S5', 'Oracle’s FY2023 net income was $8.503 billion.', evidence=e5, plan=gold_plan('S5'), result=gold_result('S5'), expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, plan_valid=True, intent_ok=True, concept='canonical', period_ok=False, calculation_ok=True), note='The evidence uses the wrong fiscal period end even though the displayed result matches gold.')
set_slot('S6', 'Oracle’s net margin increased by 2.00 percentage points from FY2023 to FY2024.', plan=gold_plan('S6'), result={'outcome':'answer','val':2.0,'unit':'pp'}, expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, plan_valid=True, intent_ok=True, concept='canonical', period_ok=True, calculation_ok=False), note='The system result does not follow from its own four evidence cells or the gold formula.')

# Qualified long-term-debt alternatives.
alt = [
 {'ticker':'CSCO','metric':'long_term_debt','period':'FY2023','concept':'LongTermDebtNoncurrent','value':6658000000,'unit':'USD','accession':'0000858877-24-000017','period_end':'2023-07-29'},
 {'ticker':'CSCO','metric':'long_term_debt','period':'FY2024','concept':'LongTermDebtNoncurrent','value':19621000000,'unit':'USD','accession':'0000858877-25-000111','period_end':'2024-07-27'},
 {'ticker':'CSCO','metric':'long_term_debt','period':'FY2025','concept':'LongTermDebtNoncurrent','value':22861000000,'unit':'USD','accession':'0000858877-26-000132','period_end':'2025-07-26'},
]
set_slot('L1', 'Cisco’s noncurrent long-term debt, excluding current maturities, was $6.658 billion at FY2023 end, $19.621 billion at FY2024 end, and $22.861 billion at FY2025 end.', evidence=alt, expected=scores(final_correct=True, appropriate_refusal=False, evidence_complete=True, concept='qualified_alternative', period_ok=True), note='All cells use the registered noncurrent basis and the answer explicitly qualifies it.')
set_slot('L2', 'Cisco long-term debt was $6.658 billion in FY2023, $19.621 billion in FY2024, and $22.861 billion in FY2025.', evidence=alt, expected=scores(final_correct=False, appropriate_refusal=False, evidence_complete=True, concept='qualified_alternative', period_ok=True), note='The alternative noncurrent basis is used without saying it excludes current maturities.')

for s in data['slots']:
    if any(v is None and not s.get('na_ok', {}).get(k, False) for k, v in s['expected_scores'].items()):
        raise ValueError(f"incomplete expected scores: {s['slot']}")
    if not s['calibrator_note']:
        raise ValueError(f"missing note: {s['slot']}")

# Post-run corrections are notes only: the first-run answers and expectations remain unchanged.
answer_slots = {'N1','N2','N3','N4','N5','N6','N7','N8','W1','W2','W3','W4','W5','W6','E1','E2','E3','S1','S2','S3','S4','S5','S6','L1','L2'}
corrections = {
    **{k: 'Corrected note after first run: under the specification, an answer item with no refusal should receive appropriate_refusal=true; the original expectation above is retained for the first run.' for k in answer_slots},
    'W2': 'Corrected note after first run: ProfitLoss is the item gold cell concept, so the human concept label is canonical here; the original expectation above is retained for the first run.',
    'E2': 'Corrected note after first run: without period_end provenance, period selection cannot be verified and should be false; the original expectation above is retained for the first run.',
    'R5': 'Corrected note after first run: because the negative-base percentage is not a meaningful reportable result, its evidence completeness should be false; the original expectation above is retained for the first run.',
}
for s in data['slots']:
    if s['slot'] in corrections:
        s['calibrator_note_correction'] = corrections[s['slot']]
(root / 'filled.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
