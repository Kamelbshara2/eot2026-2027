#!/usr/bin/env python3
"""Import the supplied Grade 9 complete question banks.

  9 Advanced : new class 9A (all 188 eligible questions)  -> public/data/study/9A.json
  9 General  : only the questions MISSING from the current 9G3 bank are appended (matched by printed page + exercise/example,
               then by identical statement) -> public/data/study/9G3.json. Existing 9G3 questions are never replaced.

usage: python3 scripts/import-grade9.py --a <9A package dir> --g <9G package dir> [--write]
Keys come from private/teacher-bank.json (answer_key inline). Options are re-lettered A-D in the given order.
"""
import json, re, shutil, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade9a_meta import META9A

ROOT = Path(__file__).resolve().parent.parent
A = Path(sys.argv[sys.argv.index('--a') + 1]); G = Path(sys.argv[sys.argv.index('--g') + 1]); WRITE = '--write' in sys.argv
LET = 'ABCD'
norm_ws = lambda s: re.sub(r'\s+', '', str(s or ''))


def conv(q, src, folder, assets, lo_local, dn, copied):
    k = q['answer_key']
    def asset(rel, alt):
        stem = 'g9-' + Path(rel).stem
        if rel not in copied:
            s = src / rel; d = ROOT / 'public' / folder / Path(rel).name
            if WRITE: d.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(s, d)
            w, h = Image.open(s).size
            assets[stem] = {'src': f'{folder}/{Path(rel).name}', 'width': w, 'height': h, 'alt_text': alt, 'source': {'bank_asset': rel, 'bank_question': q['id']}}
            copied.add(rel)
        return stem
    s = q['source']
    it = {'id': q['id'], 'learning_outcome_id': lo_local, 'type': q['type'], 'display_number': dn, 'instruction': q['prompt'], 'stem': (q['prompt'] + ' ' + q['math_latex']).strip(),
          'math_latex': q['math_latex'], 'marks': q.get('question_marks'), 'diagram_asset_ids': [asset(m, 'Original textbook figure') for m in q['media']],
          'source': {'printed_page': s.get('printed_page'), 'pdf_page': s.get('pdf_page'), 'exercise': (('Example ' if s.get('reference_kind') == 'example' else '') + str(s.get('exercise'))), 'book': s.get('id'), 'book_sha256': s.get('sha256')},
          'grade': 9, 'track': q['track'], 'source_kind': q['source_kind'], 'family_id': q['family_id'], 'difficulty': 'standard', 'skill_tags': [], 'reference_kind': s.get('reference_kind', 'exercise'),
          'bank_verification': k.get('verification')}
    if q.get('table'):   # data table given with the question -> LaTeX array (rows of the table become columns x / y)
        t = q['table']; cols = len(t['rows'])
        it['math_latex'] = '\\begin{array}{c|' + 'c' * cols + '}' + '\\\\'.join(h + '&' + '&'.join(str(r[j]) for r in t['rows']) for j, h in enumerate(t['headers'])) + '\\end{array}'
        it['stem'] = (q['prompt'] + ' ' + it['math_latex']).strip()
    if q['type'] == 'mcq':
        opts = []; letter = {}
        for j, o in enumerate(q['options']):
            letter[o['id']] = LET[j]
            op = {'id': LET[j], 'text': o.get('latex') or o.get('label') or f'Graph {LET[j]}', 'math_latex': o.get('latex', ''), 'misconception': None}
            if o.get('image'): op['image'] = asset(o['image'], f'Option {LET[j]} graph')
            opts.append(op)
        cid = letter[k['correct_option_id']]
        co = next(o for o in opts if o['id'] == cid)
        it['options'] = opts; it['answer'] = {'correct_option_id': cid, 'correct_option_text': co['math_latex'] or co['text'], 'explanation': k['solution']}
    else:
        pa = {p['part_id']: p['answer'] for p in k.get('part_answers', [])}
        parts = []
        for j, p in enumerate(q['parts']):
            prompt = re.sub(r'^[a-h]\.\s*', '', p['instruction'])
            ans = pa.get(p['id'], {})
            parts.append({'id': 'abcdefgh'[j], 'prompt': prompt, 'math_latex': '', 'marks': p.get('marks'), 'workspace': {'height_mm': 45},
                          'answer': {'model_answer_and_marking': (ans.get('text') or ('Answer: ' + ans['latex'] if ans.get('latex') else k['solution'])) if len(q['parts']) > 1 else k['solution'], 'math_latex': ans.get('latex', ''), 'bank_solution': k['solution']}})
        if len(parts) > 1: parts[0]['answer']['model_answer_and_marking'] = (parts[0]['answer']['model_answer_and_marking'] + ' ' + k['solution']).strip()
        it['parts'] = parts
    return it


def load(pkg):
    return json.loads((pkg / 'private/teacher-bank.json').read_text())['questions'], json.loads((pkg / 'data/bank.json').read_text())['learning_outcomes']


def build_9a():
    qs, los = load(A); assets, copied, out_q, out_lo = {}, set(), [], []
    for lo in sorted(los, key=lambda l: l['official_slot']):
        n = lo['official_slot']; lid = f'LO{n:02d}'; ta, ren, rar = META9A[n]
        ids = []
        for i, q in enumerate([q for q in qs if q['lo_id'] == lo['id'] and q['exam_eligible']], 1):
            it = conv(q, A, 'data/study-assets/9a', assets, lid, f'{n}.{i}', copied); it['skill_tags'] = [lo['title']]; out_q.append(it); ids.append(it['id'])
        refs = [{'printed_page': r['printed_page'], 'exercises_or_section': (('Example ' if r.get('kind') == 'example' else '') + str(r['exercise']))} for r in lo['references']]
        out_lo.append({'id': lid, 'exam_slot': f'Q{n}', 'title': lo['title'], 'title_ar': ta, 'statement': lo['title'], 'rule_summary': ren, 'rule_ar': rar, 'question_type': lo['type'],
                       'textbook_references': refs, 'reference_text': lo['reference'], 'question_count': len(ids), 'question_ids': ids, 'booklet_question_ids': ids, 'download': f'{lid}.json', 'calculator_model': 'fx-991EX ClassWiz'})
    data = {'id': '9a-term1-study', 'classroom': '9A', 'title': 'Grade 9 Advanced · Term 1 study booklet', 'title_ar': 'مذاكرة الهيكل · 9 متقدم', 'term': 'Term 1', 'academic_year': '2026-2027',
            'content_version': 'grade9-advanced-v1-2026-11-11', 'mock_storage_namespace': '9a-term1-study-v1', 'source_file': 'Grade9-Advanced-Complete-Question-Bank (teacher-supplied package)',
            'question_count': len(out_q), 'mcq_count': sum(q['type'] == 'mcq' for q in out_q), 'frq_count': sum(q['type'] == 'frq' for q in out_q), 'questions': out_q, 'learning_outcomes': out_lo, 'assets': assets,
            'authored_notice': 'textbook_exercise = original textbook item (MCQ options authored); example_application uses the data of a textbook example; example_variant / concept_application are declared additions.',
            'authored_notice_ar': 'تمرين من الكتاب = سؤال أصلي (خيارات الاختيار مؤلفة)؛ تطبيق على مثال يستخدم بيانات مثال الكتاب؛ النسخ وتطبيقات المفهوم إضافات معلنة.',
            'study_booklet': 'worksheets/grade-9-advanced-term1-written-questions.pdf', 'review_notes': []}
    return data


def merge_9g():
    p = ROOT / 'public/data/study/9G3.json'; bank = json.loads(p.read_text()); qs, los = load(G)
    def key_old(q):
        s = q.get('source') or {}; e = str(s.get('exercise', '')).strip()
        m = re.match(r'^Example (\d+)', e, re.I); e = ('ex' + m.group(1)) if m else (re.match(r'^(\d+[a-d]?)', e).group(1) if re.match(r'^(\d+[a-d]?)', e) else e)
        return (s.get('printed_page'), e)
    seen_ref = {(q['learning_outcome_id'], key_old(q)) for q in bank['questions']}
    seen_txt = {(q['learning_outcome_id'], norm_ws(q.get('instruction')) + norm_ws(q.get('math_latex'))) for q in bank['questions']}
    assets, copied, added, skipped = bank['assets'], set(), [], []
    los_by = {l['id']: l for l in bank['learning_outcomes']}
    for q in qs:
        if not q['exam_eligible']: continue
        lid = 'LO' + q['lo_id'][-2:]; s = q['source']
        k_ref = (lid, (s['printed_page'], ('ex' + str(s['exercise'])) if s.get('reference_kind') == 'example' else str(s['exercise'])))
        k_txt = (lid, norm_ws(q['prompt']) + norm_ws(q['math_latex']))
        if k_ref in seen_ref or (q['math_latex'] and k_txt in seen_txt):
            skipped.append(q['id']); continue
        lo = los_by[lid]; dn = f"{int(lid[2:])}.{len(lo['question_ids']) + 1}"
        it = conv(q, G, 'data/study-assets/9g3', assets, lid, dn, copied); it['skill_tags'] = [lo['title']]; it['import'] = 'grade9-general-complete-bank-2026-11-11'
        bank['questions'].append(it); lo['question_ids'].append(it['id']); lo['question_count'] = len(lo['question_ids']); added.append(it['id'])
        seen_ref.add(k_ref); seen_txt.add(k_txt)
    bank['question_count'] = len(bank['questions']); bank['mcq_count'] = sum(q['type'] == 'mcq' for q in bank['questions']); bank['frq_count'] = sum(q['type'] == 'frq' for q in bank['questions'])
    return bank, added, skipped


if __name__ == '__main__':
    a = build_9a(); g, added, skipped = merge_9g()
    print('9A', a['question_count'], a['mcq_count'], a['frq_count'], 'assets', len(a['assets']))
    print('9G3 added', len(added), 'skipped (already present)', len(skipped), 'total', g['question_count'])
    if WRITE:
        (ROOT / 'public/data/study/9A.json').write_text(json.dumps(a, ensure_ascii=False, separators=(',', ':')))
        (ROOT / 'public/data/study/9G3.json').write_text(json.dumps(g, ensure_ascii=False, separators=(',', ':')))
        d = ROOT / 'content-imports/grade9'; d.mkdir(parents=True, exist_ok=True)
        (d / 'import-report.json').write_text(json.dumps({'9A': {'questions': a['question_count']}, '9G3': {'added': added, 'skipped_already_present': skipped}}, indent=1))
        for pkg, n in ((A, '9A'), (G, '9G')): shutil.copyfile(pkg / 'audit/coverage.json', d / f'{n}-bank-coverage.json')
