#!/usr/bin/env python3
"""Remove exact repeats from the Grade 9 banks (teacher request 2026-11-11: "don't repeat questions for 9 General").

An item is a repeat when it is the same equation as an earlier item (sides may be swapped or written in another order).
The six repeats are textbook p.97 exercises 1-6: they already sit in LO06 "Variables on each side" (exact fit), so the
copies the 2026-11-11 import added to LO23 are removed. LO23 is renumbered. Calculator entries are removed too.
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
REMOVE = [f'9G-Q23-p97-exercise-{n}' for n in range(1, 7)]
p = ROOT / 'public/data/study/9G3.json'; b = json.loads(p.read_text())
before = len(b['questions']); b['questions'] = [q for q in b['questions'] if q['id'] not in REMOVE]
for lo in b['learning_outcomes']:
    for k in ('question_ids', 'booklet_question_ids'):
        if k in lo: lo[k] = [i for i in lo[k] if i not in REMOVE]
    lo['question_count'] = len(lo['question_ids'])
    if lo['id'] == 'LO23':
        for n, q in enumerate([q for q in b['questions'] if q['learning_outcome_id'] == 'LO23'], 1): q['display_number'] = f'23.{n}'
b['question_count'] = len(b['questions']); b['mcq_count'] = sum(q['type'] == 'mcq' for q in b['questions']); b['frq_count'] = sum(q['type'] == 'frq' for q in b['questions'])
b['review_notes']['2026-11-11-repeats'] = 'Removed LO23 copies of textbook p.97 exercises 1-6 (same equations already practised in LO06).'
p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':')))
cp = ROOT / 'public/data/study/calculator-support.json'; cs = json.loads(cp.read_text())
for i in REMOVE: cs['classes']['9G3']['questions'].pop(i, None)
cp.write_text(json.dumps(cs, ensure_ascii=False, indent=2) + '\n')
rp = ROOT / 'content-imports/grade9/import-report.json'; r = json.loads(rp.read_text())
r['9G3']['removed_as_repeats'] = REMOVE; r['9G3']['added'] = [i for i in r['9G3']['added'] if i not in REMOVE]
rp.write_text(json.dumps(r, indent=1))
print('removed', before - b['question_count'], '→', b['question_count'], 'mcq', b['mcq_count'], 'frq', b['frq_count'])
