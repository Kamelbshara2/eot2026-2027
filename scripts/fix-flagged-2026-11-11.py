#!/usr/bin/env python3
"""Teacher-reviewed fixes (2026-11-11) for the two questions left open in UPPER_GRADES_KEY_ISSUES.md.

12G-en-Q057  the boundary curve in the textbook graph is solid and the region below is shaded -> y <= -x^2+2x+6 (option A).
             Question is now typed (options as LaTeX); the original card stays as the figure.
12A-p33-Q24b-1  the card repeated Q24a ("for a = 0"). Clarified to ask h'(1) (outcome LO12, quotient rule) -> 4 (option D).
             The card is no longer shown because its wording conflicts with the clarified question; it stays recorded in source.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
S = lambda c: ROOT / f'public/data/study/{c}.json'

def edit(cls, qid, fn):
    p = S(cls); b = json.loads(p.read_text()); q = next(q for q in b['questions'] if q['id'] == qid); fn(q, b)
    p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':'))); return q

def q057(q, b):
    opts = ['y\\le -x^2+2x+6', 'y\\ge -x^2+2x+6', 'y< -x^2+2x+6', 'y\\le x^2-2x+6']
    q.update(instruction='Write a quadratic inequality for the graph.', presentation='normalized', embedded_options=False, source_kind='review_clarification',
             options=[{'id': 'ABCD'[i], 'text': o, 'math_latex': o, 'misconception': m} for i, (o, m) in enumerate(zip(opts, [None, 'Shades above the curve', 'Dashed boundary (strict) although the curve is solid', 'Parabola opening upward']))],
             review_note='Key changed C -> A after review of the figure: the boundary is solid (included) and the region below it is shaded.')
    q['stem'] = q['instruction']
    s = q['answer']['steps']; s[-1] = {'text': 'This is option A.', 'latex': 'y\\le -x^2+2x+6'}
    q['answer'].update(correct_option_id='A', correct_option_text=opts[0], steps_verified=True,
                       explanation='Vertex (1, 7) and point (0, 6) give y = −(x−1)² + 7 = −x² + 2x + 6. The curve is solid and the region below it is shaded, so y ≤ −x² + 2x + 6.')

def q24b(q, b):
    q['source']['original_card_asset'] = q['diagram_asset_ids'][0]; q['source']['original_wording'] = "Find h'(x) for a = 0 (repeats Q24a)"
    data = "f(0)=-1,\\ f(1)=-2,\\ f'(0)=-1,\\ f'(1)=3,\\quad g(0)=3,\\ g(1)=1,\\ g'(0)=-1,\\ g'(1)=-2;\\qquad h(x)=\\dfrac{x^2}{g(x)}"
    q.update(instruction="f and g are differentiable with the values given. Let h(x) = x²/g(x). Find h′(1).", math_latex=data, presentation='normalized', figure_in_image=False,
             embedded_options=False, diagram_asset_ids=[], source_kind='review_clarification',
             options=[{'id': L, 'text': v, 'math_latex': v, 'misconception': m} for L, v, m in (('A', '2', 'Uses g′(1)=+2'), ('B', '0', 'Evaluates at x = 0 instead of 1'), ('C', '6', 'Adds the terms in the numerator incorrectly'), ('D', '4', None))],
             review_note='The card asked for a = 0 again (same as Q24a). Clarified to x = 1 so the item tests a new quotient-rule value.')
    q['stem'] = q['instruction'] + ' ' + data
    q['answer'] = {'correct_option_id': 'D', 'correct_option_text': '4', 'steps_verified': True,
                   'explanation': "h′(x) = (2x·g(x) − x²·g′(x))/g(x)². At x = 1: (2·1·1 − 1·(−2))/1² = 4.",
                   'steps': [{'text': 'Quotient Rule.', 'latex': "h'(x)=\\dfrac{2x\\,g(x)-x^2\\,g'(x)}{g(x)^2}"},
                             {'text': 'Substitute x = 1, g(1) = 1, g′(1) = −2.', 'latex': "h'(1)=\\dfrac{2(1)(1)-(1)^2(-2)}{(1)^2}"},
                             {'text': 'Simplify: option D.', 'latex': "h'(1)=\\dfrac{2+2}{1}=4"}]}

a = edit('12G', '12G-en-Q057', q057); b = edit('12A', '12A-p33-Q24b-1', q24b)
cp = ROOT / 'public/data/study/calculator-support.json'; cs = json.loads(cp.read_text())
for cls, q in (('12G', a), ('12A', b)):
    e = cs['classes'][cls]['questions'][q['id']]
    e['prepare'] = e['prepare'].replace(' Read the whole question from the image (all labels, scales and options) before choosing a method.', '')
    e['solutions'] = [{'part': 'Answer', 'math': q['answer']['correct_option_text'], 'text': q['answer']['explanation'], 'answer_text': q['answer']['correct_option_text']}]
cp.write_text(json.dumps(cs, ensure_ascii=False, indent=2) + '\n')
tp = ROOT / 'public/data/study/translations-ar.json'; t = json.loads(tp.read_text())
t['instruction'].update({'Write a quadratic inequality for the graph.': 'اكتب متباينة تربيعية تمثل التمثيل البياني.',
                         'f and g are differentiable with the values given. Let h(x) = x²/g(x). Find h′(#).': 'الدالتان f وg قابلتان للاشتقاق بالقيم المعطاة. لتكن h(x) = x²/g(x). أوجد h′(#).'})
tp.write_text(json.dumps(t, ensure_ascii=False, indent=1)); print('fixed', a['id'], b['id'])
