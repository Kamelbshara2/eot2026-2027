#!/usr/bin/env python3
"""Merge hand-written worked solutions (content-imports/upper-grades/solutions/*.json) into the study banks (idempotent).
File format: {"class": "12G", "items": {"<question id>": {"steps": [{"text": "...", "latex": "..."}], "verified": true|false, "note": "..."}}}
`verified` = the solution was derived from the question on the card and its final answer equals the keyed option. Items with
verified=false are listed in UPPER_GRADES_SOLUTIONS_REPORT.md for teacher review (possible key or reading problem).
For written (FRQ) questions give "parts": {"a": {"steps": [...]}} instead of "steps"."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
files = sorted((ROOT / 'content-imports/upper-grades/solutions').glob('*.json'))
by = {}
for f in files:
    d = json.loads(f.read_text()); by.setdefault(d['class'], {}).update(d['items'])
rep = {}
for cls, items in by.items():
    p = ROOT / f'public/data/study/{cls}.json'; bank = json.loads(p.read_text()); n = 0; bad = []
    for q in bank['questions']:
        it = items.get(q['id'])
        if not it: continue
        if q['type'] == 'mcq':
            q['answer']['steps'] = it['steps']; q['answer']['steps_verified'] = bool(it.get('verified', True))
        else:
            for part in q['parts']:
                sp = (it.get('parts') or {}).get(part['id'])
                if sp:
                    part['answer']['steps'] = sp['steps']
                    if part['answer'].get('model_answer_and_marking', '').startswith('Included in the combined reference solution'): part['answer']['model_answer_and_marking'] = 'Worked solution for this part:'
        if not it.get('verified', True): bad.append({'id': q['id'], 'note': it.get('note', '')})
        n += 1
    missing = [k for k in items if k not in {q['id'] for q in bank['questions']}]
    assert not missing, missing
    p.write_text(json.dumps(bank, ensure_ascii=False, separators=(',', ':')))
    rep[cls] = {'applied': n, 'unverified': bad}
print(json.dumps(rep, ensure_ascii=False, indent=1))
