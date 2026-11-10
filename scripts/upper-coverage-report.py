#!/usr/bin/env python3
"""EOT structure coverage for Grades 11-12: every learning outcome of the official coverage sheet vs the questions on the site."""
import json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
NAMES = {'11G': 'الصف 11 عام', '11A': 'الصف 11 متقدم', '12G': 'الصف 12 عام', '12A': 'الصف 12 متقدم'}
out, md = {}, ['# تقرير تغطية هيكل الاختبار — الصفان 11 و12', '',
  'المصدر: ملفات الهيكل الرسمية الأربعة (EoT1 Coverage) مقابل بيانات الموقع `public/data/study/<class>.json`. كل مخرج من الهيكل (Q1…Q26) له سؤال أو أكثر في الموقع، ونوعه (اختيار من متعدد Q1–Q20، مقالي Q21+) مطابق للهيكل.', '']
tot = collections.Counter()
for c in ['11G', '11A', '12G', '12A']:
    d = json.load(open(ROOT / f'public/data/study/{c}.json')); qs = {q['id']: q for q in d['questions']}
    md += [f'## {NAMES[c]} — {len(d["learning_outcomes"])} مخرجاً، {len(qs)} سؤالاً', '',
           '| المخرج | الهيكل | المرجع الرسمي | النوع | عدد الأسئلة | بطاقات مصوّرة | مصدر الأسئلة | تصحيح آلي للمقالي |', '|---|---|---|---|---|---|---|---|']
    out[c] = {}
    for lo in d['learning_outcomes']:
        items = [qs[i] for i in lo['question_ids']]
        cards = sum(bool(q.get('figure_in_image')) for q in items)
        kinds = collections.Counter('أصلي' if q['source_kind'] in ('review_question', 'textbook_exercise', 'textbook_mcq_conversion', 'user_authorized_graph_variant') else 'مؤلَّف' for q in items)
        auto = sum(any(p.get('blanks') for p in q['parts']) for q in items if q['type'] == 'frq') if lo['question_type'] == 'frq' else None
        md.append(f"| {lo['id']} | {lo['exam_slot']} | {lo['reference_text']} | {lo['question_type'].upper()} | {len(items)} | {cards} | أصلي {kinds['أصلي']} · مؤلَّف {kinds['مؤلَّف']} | {'—' if auto is None else f'{auto}/{len(items)}'} |")
        out[c][lo['id']] = {'slot': lo['exam_slot'], 'reference': lo['reference_text'], 'type': lo['question_type'], 'questions': len(items), 'cards': cards, 'source_mix': dict(kinds), 'auto_checked': auto}
        tot['q'] += len(items)
    md.append('')
(ROOT / 'content-imports/upper-grades/eot-coverage.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
(ROOT / 'UPPER_GRADES_COVERAGE_REPORT.md').write_text('\n'.join(md) + '\n')
print('questions', tot['q'])
