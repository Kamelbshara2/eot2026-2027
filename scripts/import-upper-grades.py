#!/usr/bin/env python3
"""Import the Grade 11/12 (General + Advanced) Term-1 question bank into the study booklet format.

usage: python3 scripts/import-upper-grades.py --src <extracted Math-Question-Banks dir> [--write]

Input  : data/bank.json (questions, options, media), private/answer-keys.json (keys), assets/ (original cards + plots)
Output : public/data/study/{11G,11A,12G,12A}.json, public/data/study-assets/<class>/..., content-imports/upper-grades/*
Rules  : original source cards are kept untouched; the bank's own classification (source_kind) is preserved;
         duplicates flagged by the bank (exam_eligible=false) are NOT shown; option ids are re-lettered A-D.
"""
import json, re, shutil, sys, hashlib
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upper_grades_meta import META

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[sys.argv.index('--src') + 1])
WRITE = '--write' in sys.argv
LETTERS = 'ABCD'
CLASS_LABEL = {'11G': ('Grade 11 General', '11 عام'), '11A': ('Grade 11 Advanced', '11 متقدم'),
               '12G': ('Grade 12 General', '12 عام'), '12A': ('Grade 12 Advanced', '12 متقدم')}
CARD_INSTRUCTION = 'Study the full question in the image, then choose the matching answer.'
CARD_FRQ = 'Complete every part of the question shown in the image. Write your working in the space below.'


def pdf_pages(ref):
    """Reference text -> [{printed_page, exercises_or_section}] (best effort, kept verbatim as text)."""
    out = []
    for chunk in re.split(r';\s*', ref):
        m = re.match(r'^(?:Reveal|Bridge|Arabic)?\s*(\d+)(?:[–/\-]\d+)?(?:\s*/\s*Arabic\s*\d+)?,?\s*(.*)$', chunk.strip())
        if m: out.append({'printed_page': int(m.group(1)), 'exercises_or_section': m.group(2) or 'Section'})
        else: out.append({'printed_page': None, 'exercises_or_section': chunk.strip()})
    return out


def main():
    bank = json.loads((SRC / 'data/bank.json').read_text())
    keys = {k['question_id']: k for k in json.loads((SRC / 'private/answer-keys.json').read_text())}
    report = {'classes': {}}
    for cls in ['11G', '11A', '12G', '12A']:
        en, ar = CLASS_LABEL[cls]
        los = sorted([l for l in bank['learning_outcomes'] if l['class_id'] == cls], key=lambda l: l['official_slot'])
        qs_all = [q for q in bank['questions'] if q['class_id'] == cls]
        folder = f'data/study-assets/{cls.lower()}'
        assets, out_los, out_qs, copied = {}, [], [], set()

        def asset(rel, alt, q):
            stem = Path(rel).stem
            if rel not in copied:
                src = SRC / rel
                dst = ROOT / 'public' / folder / Path(rel).name
                if WRITE:
                    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dst)
                copied.add(rel)
                w, h = Image.open(src).size
                assets[stem] = {'src': f'{folder}/{Path(rel).name}', 'width': w, 'height': h, 'alt_text': alt,
                                'source': {'bank_asset': rel, 'bank_question': q['id'], 'adaptation': 'original_source_crop' if '/questions/' in rel else 'bank_plot'}}
            return stem

        for lo in los:
            n = lo['official_slot']; lid = f'LO{n:02d}'
            title_ar, rule_en, rule_ar = META[cls][n]
            qs = [q for q in qs_all if q['lo_id'] == lo['id'] and q['exam_eligible'] and not q['duplicate_of']]
            ids, mcq_n, frq_n = [], 0, 0
            for i, q in enumerate(qs, 1):
                k = keys[q['id']]
                dn = f'{n}.{i}'
                figs = [asset(m, 'Original question image' if '/questions/' in m else 'Graph supplied with the question', q) for m in q['media']]
                card = q['presentation'] == 'source_card'
                item = {'id': q['id'], 'learning_outcome_id': lid, 'type': q['type'], 'display_number': dn,
                        'instruction': CARD_INSTRUCTION if (card and q['type'] == 'mcq') else (CARD_FRQ if card else q['prompt']),
                        'stem': '', 'math_latex': q['math_latex'] if not card else '', 'marks': q['question_marks'],
                        'diagram_asset_ids': figs, 'source': {'printed_page': None, 'pdf_page': (q['source'] or {}).get('pdf_page'), 'exercise': (q['source'] or {}).get('exercise'), 'bank_source': (q['source'] or {}).get('id')},
                        'grade': q['grade'], 'track': q['track'], 'source_kind': q['source_kind'], 'family_id': q['family_id'],
                        'difficulty': 'standard', 'skill_tags': [lo['title']], 'reference_kind': 'review', 'presentation': q['presentation'], 'figure_in_image': card}
                item['stem'] = (item['instruction'] + ' ' + item['math_latex']).strip()
                if q['type'] == 'mcq':
                    mcq_n += 1
                    order = q['options']; letter = {o['id']: LETTERS[j] for j, o in enumerate(order)}
                    opts = []
                    for j, o in enumerate(order):
                        if q['embedded_options']:
                            sl = str(o.get('source_label', LETTERS[j]))
                            op = {'id': LETTERS[j], 'text': (f'Option {sl} in the image' if sl.isdigit() else f'Option {sl.lower()}) in the image'), 'math_latex': '', 'misconception': None}
                        else:
                            op = {'id': LETTERS[j], 'text': o['latex'], 'math_latex': o['latex'], 'misconception': o.get('distractor_rationale')}
                        if o.get('image'):
                            op['image'] = asset(o['image'], f'Graph {LETTERS[j]}', q)
                        opts.append(op)
                    cid = letter[k['correct_option_id']] if k['correct_option_id'] in letter else k['correct_option_id']
                    assert cid in LETTERS[:len(opts)], (q['id'], cid)
                    ctext = next(o['math_latex'] or o['text'] for o in opts if o['id'] == cid)
                    sol = k['solution']
                    if 'not transcribed' in sol:
                        sol = 'Reviewed answer key. A written step-by-step solution has not been transcribed for this source card; use the lesson rule and the calculator guide.'
                    item['options'] = opts
                    item['answer'] = {'correct_option_id': cid, 'correct_option_text': ctext, 'explanation': sol}
                    item['embedded_options'] = bool(q['embedded_options'])
                else:
                    frq_n += 1
                    parts = []
                    for j, p in enumerate(q['parts']):
                        pid = 'abcdefgh'[j]
                        generic = p['instruction'] == 'Complete all parts shown in the source question.'
                        parts.append({'id': pid, 'prompt': 'Complete all parts of the question.' if generic else p['instruction'], 'math_latex': '', 'marks': p.get('marks'),
                                      'workspace': {'height_mm': 60 if generic else 40},
                                      'answer': {'model_answer_and_marking': k['solution'] if j == 0 else f'Included in the combined reference solution for part {parts[0]["id"]}.', 'math_latex': ''}})
                    item['parts'] = parts
                    item['marks'] = None
                ids.append(q['id']); out_qs.append(item)
            refs = pdf_pages(lo['reference'])
            out_los.append({'id': lid, 'exam_slot': f'Q{n}', 'title': lo['title'], 'title_ar': title_ar, 'statement': lo['title'], 'rule_summary': rule_en, 'rule_ar': rule_ar,
                            'question_type': lo['type'], 'textbook_references': refs, 'reference_text': lo['reference'], 'question_count': len(ids), 'question_ids': ids, 'booklet_question_ids': ids,
                            'download': f'{lid}.json', 'calculator_model': 'fx-991EX ClassWiz'})
        data = {'id': f'{cls.lower()}-term1-study', 'classroom': cls, 'title': f'{en} · Term 1 study booklet', 'title_ar': f'مذاكرة الهيكل · {ar}', 'term': 'Term 1', 'academic_year': '2026-2027',
                'content_version': 'upper-grades-v2-2026-11-10', 'mock_storage_namespace': f'{cls.lower()}-term1-study-v1', 'source_file': 'Math-Question-Banks v2 (teacher-supplied package)',
                'question_count': len(out_qs), 'mcq_count': sum(q['type'] == 'mcq' for q in out_qs), 'frq_count': sum(q['type'] == 'frq' for q in out_qs),
                'questions': out_qs, 'learning_outcomes': out_los, 'assets': assets,
                'authored_notice': 'Source-card questions are original images from the supplied review/textbook pages. Questions with source_kind authored_lo_variant, example_application, exercise_conversion or textbook_mcq_conversion were written for this bank and are labelled as such.',
                'authored_notice_ar': 'أسئلة البطاقات صور أصلية من صفحات المراجعة والكتاب. الأسئلة ذات التصنيف authored_lo_variant أو example_application أو exercise_conversion أو textbook_mcq_conversion مؤلَّفة لهذا البنك وموسومة بذلك.',
                'study_booklet': f'worksheets/grade-{cls[:2]}-{"general" if cls[2] == "G" else "advanced"}-term1-written-questions.pdf', 'review_notes': []}
        report['classes'][cls] = {'outcomes': len(out_los), 'questions': len(out_qs), 'mcq': data['mcq_count'], 'frq': data['frq_count'], 'assets': len(assets),
                                  'min_per_outcome': min(l['question_count'] for l in out_los), 'cards': sum(1 for q in out_qs if q['presentation'] == 'source_card')}
        if WRITE:
            (ROOT / f'public/data/study/{cls}.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps(report, indent=1))
    if WRITE:
        d = ROOT / 'content-imports/upper-grades'; d.mkdir(parents=True, exist_ok=True)
        (d / 'import-report.json').write_text(json.dumps(report, indent=1))
        shutil.copyfile(SRC / 'audit/coverage.csv', d / 'bank-coverage.csv')
        shutil.copyfile(SRC / 'audit/corrections.json', d / 'bank-corrections.json')


if __name__ == '__main__':
    main()
