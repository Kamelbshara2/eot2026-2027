#!/usr/bin/env python3
"""Reviewed corrections applied AFTER scripts/import-upper-grades.py (idempotent). Each fix is listed in UPPER_GRADES_REVIEW.md."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
p = ROOT / 'public/data/study/11G.json'; d = json.loads(p.read_text()); n = 0
for q in d['questions']:
    if q['id'].startswith('11G-Q09-added'):                      # imported explanation ended with a stray "=5k"
        m = re.search(r'a=(\d+),\\?\s*b=(\d+)', q['math_latex']); a, b = int(m[1]), int(m[2]); c2 = a * a + b * b; r = round(c2 ** 0.5); assert r * r == c2
        q['answer']['explanation'] = f'c=√(a²+b²)=√({a}²+{b}²)=√{c2}={r}.'; n += 1
p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print('fixed', n)
