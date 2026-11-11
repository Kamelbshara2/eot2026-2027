#!/usr/bin/env python3
"""Double-review fixes for the Grade 9 import (2026-11-11).

9A LO13 (p.248 ex.10-15): the textbook figure is only the grid with the parent line f(x)=x (students draw g on it).
Shown under "describe the dilation of g(x)=5x" it looked like a wrong graph of g, so the caption now says what it is.
All keys were re-checked by hand (text items) and against the figures (picture items); no key changed.
"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
p = ROOT / 'public/data/study/9A.json'; b = json.loads(p.read_text())
CAP = 'Textbook grid: the line drawn is the parent f(x) = x, not g(x) · شبكة الكتاب: الخط المرسوم هو الدالة الأم f(x) = x وليس g(x)'
n = 0
for q in b['questions']:
    if q['learning_outcome_id'] == 'LO13':
        for a in q.get('diagram_asset_ids', []): b['assets'][a]['alt_text'] = CAP; n += 1
p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':'))); print('captions', n)

# 9G3 LO11: same parent-only textbook grid as 9A LO13
g = ROOT / 'public/data/study/9G3.json'; G = json.loads(g.read_text())
for q in G['questions']:
    if q['learning_outcome_id'] == 'LO11' and re.search(r'dilation', q['instruction'], re.I):
        for a in q.get('diagram_asset_ids', []): G['assets'][a]['alt_text'] = CAP

# 9G3 LO01 (p.9 ex.16-21): "the difference of eleven and four times five" also reads as 11 - 4*5 (an option), while the key is (11-4)*5.
# Commas / "multiplied by" make the keyed grouping the only reading. Keys unchanged; textbook wording recorded.
WORDING = {
    '9G-Q01-p9-exercise-16': ('Which numerical expression represents the difference of eleven and four, multiplied by five?', 'أي عبارة عددية تمثل الفرق بين أحد عشر وأربعة، مضروباً في خمسة؟'),
    '9G-Q01-p9-exercise-17': ('Which numerical expression represents the sum of one and two, divided by twenty?', 'أي عبارة عددية تمثل مجموع واحد واثنين، مقسوماً على عشرين؟'),
    '9G-Q01-p9-exercise-18': ('Which numerical expression represents the sum of two, four and six, multiplied by eight?', 'أي عبارة عددية تمثل مجموع اثنين وأربعة وستة، مضروباً في ثمانية؟'),
    '9G-Q01-p9-exercise-19': ('Which numerical expression represents the sum of twelve and sixteen, divided by the sum of three and four?', 'أي عبارة عددية تمثل مجموع اثني عشر وستة عشر، مقسوماً على مجموع ثلاثة وأربعة؟'),
    '9G-Q01-p9-exercise-20': ('Which numerical expression represents the difference of twenty-two and six, divided by the sum of five and three?', 'أي عبارة عددية تمثل الفرق بين اثنين وعشرين وستة، مقسوماً على مجموع خمسة وثلاثة؟'),
    '9G-Q01-p9-exercise-21': ('Which numerical expression represents the sum of thirty-six and fourteen, divided by the product of two and five?', 'أي عبارة عددية تمثل مجموع ستة وثلاثين وأربعة عشر، مقسوماً على حاصل ضرب اثنين في خمسة؟'),
}
tp = ROOT / 'public/data/study/translations-ar.json'; T = json.loads(tp.read_text())
for q in G['questions']:
    if q['id'] in WORDING:
        en, ar = WORDING[q['id']]
        if q['instruction'] != en:
            q.setdefault('source', {})['original_wording'] = q['instruction']
            q['review_note'] = 'Wording clarified with a comma so the keyed grouping is the only reading.'
            q['instruction'] = q['stem'] = en
        T['instruction'][en] = ar
g.write_text(json.dumps(G, ensure_ascii=False, separators=(',', ':')))
tp.write_text(json.dumps(T, ensure_ascii=False, indent=1)); print('9G3 wording', len(WORDING))
