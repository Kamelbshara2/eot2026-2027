#!/usr/bin/env python3
"""Teacher request 2026-11-11: every 9 General piecewise written question gets two value tables (one per piece) to fill,
with the piece's endpoint as the 3rd point. Points are taken from the plot spec (the same pieces the graph checks);
inner points are the nearest whole-number x with a whole-number y. The endpoint y is computed with the piece's own formula
(open circle: computed but not included)."""
import json
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp
ROOT = Path(__file__).resolve().parent.parent
p = ROOT / 'public/data/study/9G3.json'; b = json.loads(p.read_text())
x = sp.Symbol('x')
fmt = lambda v: str(v.numerator) if v.denominator == 1 else f'{v.numerator}/{v.denominator}|{float(v):g}'
done = []
for q in b['questions']:
    if q['type'] != 'frq': continue
    for part in q['parts']:
        pl = part.get('plot')
        if not pl or pl.get('kind') != 'piecewise': continue
        tables, steps = [], []
        for k, pc in enumerate(pl['pieces'], 1):
            m, c, x0 = Fr(pc['m']).limit_denominator(12), Fr(pc['b']).limit_denominator(12), Fr(pc['x0']).limit_denominator(12)
            d = 1 if pc['side'] == 'right' else -1   # nearest whole-number x inside the interval with a whole-number y
            inner = [x0 + d * k for k in range(1, 30) if (m * (x0 + d * k) + c).denominator == 1][:2]
            xs = (inner if d > 0 else inner[::-1]) + [x0]
            ys = [m * v + c for v in xs]
            rel = ('\\ge ' if pc['closed'] else '>') if pc['side'] == 'right' else ('\\le ' if pc['closed'] else '<')
            expr = sp.Rational(m.numerator, m.denominator) * x + sp.Rational(c.numerator, c.denominator)
            cap_tex = f'{sp.latex(expr)},\\ x{rel}{x0}'
            tables.append({'caption': f'Piece {k} · الجزء {k}', 'caption_tex': cap_tex, 'xs': [str(v) for v in xs], 'ys': [fmt(v) for v in ys], 'end': 2})
            row = ' & '.join(str(v) for v in xs); yrow = ' & '.join(sp.latex(sp.Rational(v.numerator, v.denominator)) for v in ys)
            steps.append({'text': f'Table for piece {k}: two points inside its interval, then the endpoint x = {x0} as the 3rd point ('
                                  + ('closed: it belongs to this piece).' if pc['closed'] else 'open: compute it, but draw an open circle).'),
                          'latex': f'{cap_tex}\\qquad\\begin{{array}}{{c|ccc}}x&{row}\\\\ y&{yrow}\\end{{array}}'})
        part['blanks'] = {**part.get('blanks', {}), 'tables': tables}
        part['blanks'].setdefault('lines', [])
        a = part['answer']; a['steps'] = steps + [s_ for s_ in a.get('steps', []) if not s_['text'].startswith('Table for piece')]
        done.append(q['id'])
p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':'))); print(len(done), done)
