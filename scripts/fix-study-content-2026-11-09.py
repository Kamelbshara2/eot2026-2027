#!/usr/bin/env python3
"""Reviewed content fixes found by scripts/audit-study-questions.py + manual review (2026-11-09).

G10G-Q05-MCQ-01 and G10G-Q15-MCQ-01 ("which expression does NOT belong") lost their valid distractors when the
generic distractor pass ran: after it, all four options were non-factorable (Q05.1) or none was a perfect square
(Q15.1), so the keyed answer was not uniquely correct. The textbook-import options are restored; the key letter is
unchanged. Every restored option is verified here with sympy before it is written. Idempotent.
"""
import json, sys
from pathlib import Path
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
T = standard_transformations + (implicit_multiplication_application, convert_xor)

ROOT = Path(__file__).resolve().parent.parent
x, n = sp.symbols('x n')

FIX = {
    'G10G-Q05-MCQ-01': {
        'options': [('A', 'x^{2} + 11 x + 24', 'Choose a pair that sums to 11 only by guessing; 3 and 8 do work, so this one factors.'),
                    ('B', 'x^{2} - 10 x - 24', 'Sign slip on the middle term; -12 and 2 do work, so this one factors.'),
                    ('C', 'x^{2} + 12 x + 24', None),
                    ('D', 'x^{2} + 2 x - 24', 'Check the sum of the pair: 6 and -4 do work, so this one factors.')],
        'key': 'C', 'check': 'factorable_except_key',
        'explanation': 'x²+12x+24: no integer pair has product 24 and sum 12 (the discriminant 48 is not a perfect square). The other three factor into integer binomials: (x+3)(x+8), (x−12)(x+2), (x+6)(x−4).',
        'support_math': 'x^{2} + 12 x + 24'},
    'G10G-Q15-MCQ-01': {
        'options': [('A', 'n^{2} + n + \\frac{3}{4}', None),
                    ('B', 'n^{2} - n + \\frac{1}{4}', 'Perfect square: (n − 1/2)².'),
                    ('C', 'n^{2} - \\frac{2}{3} n + \\frac{1}{9}', 'Perfect square: (n − 1/3)².'),
                    ('D', 'n^{2} + \\frac{1}{3} n + \\frac{1}{36}', 'Perfect square: (n + 1/6)².')],
        'key': 'A', 'check': 'square_except_key',
        'explanation': 'B, C and D equal (n−1/2)², (n−1/3)² and (n+1/6)². For n²+n+c to be a perfect square c must be (1/2)² = 1/4, not 3/4, so A does not belong.',
        'support_math': 'n^{2} + n + \\frac{3}{4}'},
}

def tex(s):
    s = s.replace('\\frac{', '(').replace('}{', ')/(').replace('^{2}', '**2').replace('^{', '**(')
    s = s.replace('}', ')').replace('{', '(').replace(' ', '')
    return parse_expr(s, local_dict={'x': x, 'n': n}, transformations=T)

def verify(spec):
    ok = []
    for oid, text, _ in spec['options']:
        e = tex(text)
        v = x if 'x' in text else n
        if spec['check'] == 'factorable_except_key':
            fl = sp.factor_list(e)[1]; ok.append((oid, len(fl) == 2 or any(m > 1 for _, m in fl)))
        else:
            sq = sp.Poly(e, v)
            disc = sp.simplify(sq.coeffs()[1] ** 2 - 4 * sq.coeffs()[0] * sq.coeffs()[2]) if sq.degree() == 2 and len(sq.coeffs()) == 3 else 1
            ok.append((oid, disc == 0))
    good = [o for o, f in ok if f]; bad = [o for o, f in ok if not f]
    assert bad == [spec['key']] and len(good) == 3, f'verification failed: {ok}'
    return ok

def patch(node, changed):
    if isinstance(node, dict):
        if node.get('id') in FIX and isinstance(node.get('options'), list):
            spec = FIX[node['id']]
            node['options'] = [dict(id=oid, text=text, math_latex=text, **({'misconception': mc} if mc else {})) for oid, text, mc in spec['options']]
            ans = node.setdefault('answer', {})
            ans['correct_option_id'] = spec['key']; ans['correct_option_text'] = next(t for o, t, _ in spec['options'] if o == spec['key']); ans['explanation'] = spec['explanation']
            changed.append(node['id'])
        for sol in node.get('solutions', []) if node.get('outcome') and node.get('role') else []:
            pass
        for v in node.values(): patch(v, changed)
    elif isinstance(node, list):
        for v in node: patch(v, changed)

def main():
    for spec in FIX.values(): verify(spec)
    files = ['public/data/study/10G3.json'] + [f'public/data/exam-banks/10g3-term1/{n}.json' for n in ('index', 'bank', 'LO05', 'LO15', 'provenance')]
    for f in files:
        p = ROOT / f; d = json.loads(p.read_text()); changed = []
        patch(d, changed)
        p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')) if f.endswith('study/10G3.json') else json.dumps(d, ensure_ascii=False, indent=2))
        print(f, sorted(set(changed)) or '-')
    # calculator support text for the two items
    p = ROOT / 'public/data/study/calculator-support.json'; d = json.loads(p.read_text())
    for qid, spec in FIX.items():
        g = d['classes']['10G3']['questions'][qid]
        for sol in g['solutions']: sol['math'] = spec['support_math']; sol['text'] = spec['explanation']
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
