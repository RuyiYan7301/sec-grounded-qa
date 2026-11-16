import csv, json, glob, collections, sys
base = sys.argv[1]
gpt = list(csv.DictReader(open(base + '/labels_external/gpt_labels.csv', encoding='utf-8')))
packet = list(csv.DictReader(open(base + '/second_annotator_packet.csv', encoding='utf-8-sig')))
pk = {r['hunk_id']: r for r in packet}
L = {'material_added', 'material_removed', 'material_modified', 'boilerplate', 'ambiguous'}
assert len(gpt) == 50 and len({g['hunk_id'] for g in gpt}) == 50
assert all(g['label'] in L for g in gpt)
assert [g['hunk_id'] for g in gpt] == [r['hunk_id'] for r in packet], 'order/id mismatch'
raw = {}
for f in glob.glob(base + '/labels_claude/*.json'):
    if 'self_review' in f:
        continue
    for x in json.load(open(f, encoding='utf-8')):
        raw[x['id']] = x
rev = dict(raw)
for c in json.load(open(base + '/labels_claude/self_review.json', encoding='utf-8'))['changes']:
    rev[c['id']] = dict(rev[c['id']], label=c['label'])

def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n / n
    return po, (po - pe) / (1 - pe)

coarse = lambda l: 'material' if l.startswith('material') else l
for name, C in [('raw', raw), ('after self-review', rev)]:
    a = [C[g['hunk_id']]['label'] for g in gpt]; b = [g['label'] for g in gpt]
    po, k = kappa(a, b)
    idx = [i for i in range(50) if a[i] != 'ambiguous' and b[i] != 'ambiguous']
    po3, k3 = kappa([coarse(a[i]) for i in idx], [coarse(b[i]) for i in idx])
    print(f'{name}: 5-class agree {po:.2f} kappa {k:.2f} | material-vs-boilerplate (n={len(idx)}) agree {po3:.2f} kappa {k3:.2f}')
print('Claude label counts', collections.Counter(rev[g['hunk_id']]['label'] for g in gpt))
print('GPT label counts', collections.Counter(g['label'] for g in gpt))
print('confusion (claude_reviewed, gpt):')
for k, v in sorted(collections.Counter((rev[g['hunk_id']]['label'], g['label']) for g in gpt).items()):
    print('  ', k, v)
print('DISAGREEMENTS (vs reviewed):')
for g in gpt:
    c = rev[g['hunk_id']]
    if c['label'] != g['label']:
        p = pk[g['hunk_id']]
        print(f"#{g['item']} {g['hunk_id']} claude={c['label']}({c['confidence']}) raw={raw[g['hunk_id']]['label']} gpt={g['label']}({g['confidence']}) closest={'Y' if p['closest text elsewhere in the other filing'].strip() else '-'}")
        print('   C:', c.get('note', ''))
        print('   G:', g['note'])
