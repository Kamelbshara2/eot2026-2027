#!/usr/bin/env python3
"""For written parts without worked steps: steps = the outcome rule + every checked blank line with its reference answer filled in.
The blank answers were computed with sympy / taken from the reviewed key, and tests prove each one is accepted by the checker."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
cls = sys.argv[1]
p = ROOT / f'public/data/study/{cls}.json'; d = json.loads(p.read_text()); LO = {l['id']: l for l in d['learning_outcomes']}
def fill(line):
    def rep(m):
        b = re.sub(r'#\w+$', '', m.group(1)); b = re.sub(r'^~[\d.]+:', '', b)
        if b.startswith('?'): return '\\text{' + b.split('|')[-1] + '}'
        b = b.split('|')[0]
        return '\\boxed{' + b + '}'
    return re.sub(r'\[\[(.+?)\]\]', rep, line)
n = 0
for q in d['questions']:
    if q['type'] != 'frq': continue
    lo = LO[q['learning_outcome_id']]
    for i, part in enumerate(q['parts']):
        if part['answer'].get('steps') or not part.get('blanks'): continue
        st = [{'text': lo['rule_summary'], 'latex': ''}] if i == 0 else []
        for ln in part['blanks'].get('lines', []): st.append({'text': 'Working:', 'latex': fill(ln)})
        if part['blanks'].get('table'):
            t = part['blanks']['table']; st.append({'text': 'Table of values (compute y for each x).', 'latex': r'\begin{array}{c|' + 'c' * len(t['xs']) + r'}x&' + '&'.join(t['xs']) + r'\\\hline y&' + '&'.join(map(str, t['ys'])) + r'\end{array}'})
        st = [s for s in st if s['latex'] or s['text']]
        if st and not st[0]['latex']: st[0]['latex'] = r'\text{method}'
        part['answer']['steps'] = st; n += 1
p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print(cls, 'parts given steps from blanks:', n)
