#!/usr/bin/env python3
"""Add interactive fill-in-the-blank solution templates (LaTeX) to written (FRQ) study questions.

Run AFTER the study JSON files are generated/revised:  python3 scripts/add-study-blanks.py
Idempotent: overwrites `parts[*].blanks` only. Syntax is documented in lib/study-fill.js.
Answers are computed with sympy / math wherever the data allow, so templates cannot drift from the stem.
Also applies reviewed corrections (see CORRECTIONS).
"""
import json, math, re, sys
from fractions import Fraction
from pathlib import Path
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

ROOT = Path(__file__).resolve().parent.parent
T = standard_transformations + (implicit_multiplication_application, convert_xor)
sym = lambda s: parse_expr(s, transformations=T)

def ascii_expr(e):
    s = sp.sstr(e)
    s = re.sub(r'\*\*(\d+)', r'^\1', s)
    s = re.sub(r'(?<=\d)\*(?=[a-z(])', '', s)
    s = re.sub(r'(?<=[a-z)])\*(?=[a-z(])', '', s)
    return s.replace(' ', '')

def tex_expr(e):
    return re.sub(r'\^(\d{2,})', r'^{\1}', ascii_expr(e))

def frac_txt(v):
    f = Fraction(v).limit_denominator(1000)
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'

def alt(v):
    f = Fraction(v).limit_denominator(1000)
    if f.denominator == 1: return str(f.numerator)
    d = float(f)
    return f'{f.numerator}/{f.denominator}|{d:g}'

def terms_sorted(e):
    p = sp.Poly(sp.expand(e), *sorted(e.free_symbols, key=str))
    return p.terms()

# ---------------------------------------------------------------- 10G3 polynomial families
def poly_sum(stem):
    expr = sym(stem)
    lines = []
    if re.search(r'\)-\(', stem):
        second = stem.split(')-(')[1].rstrip(')')
        lines.append(f'-({second})=[[{ascii_expr(-sym(second))}]]')
    res = sp.expand(expr)
    for mon, c in terms_sorted(res):
        gens = sorted(res.free_symbols, key=str)
        m = sp.Mul(*[g**k for g, k in zip(gens, mon)])
        label = '\\text{constant term}' if m == 1 else f'\\text{{coefficient of }}{tex_expr(m)}'
        lines.append(f'{label}:\\ [[{c}]]')
    lines.append(f'\\text{{Result}}=[[{ascii_expr(res)}]]')
    return lines

def poly_product(stem):
    m = re.match(r'^\((.+?)\)\((.+)\)$', stem)
    a, b = sym(m.group(1)), sym(m.group(2))
    lines = []
    for t in sorted(sp.Add.make_args(sp.expand(a)), key=lambda t: -sp.Poly(t, *sorted(a.free_symbols, key=str)).total_degree()):
        lines.append(f'({tex_expr(t)})({m.group(2).replace("^", "^")})=[[{ascii_expr(sp.expand(t * b))}]]')
    lines.append(f'\\text{{Sum of partial products}}=[[{ascii_expr(sp.expand(a * b))}]]')
    return lines

# ---------------------------------------------------------------- 3-D geometry
def pts_from(stem):
    s = stem.replace('\\quad', ' ').replace('\\left', '').replace('\\right', '')
    s = re.sub(r'\\sqrt\{([^{}]*)\}', r'sqrt(\1)', s)
    pts, depth, buf = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
            if depth == 1: buf = ''; continue
        if ch == ')':
            depth -= 1
            if depth == 0: pts.append(buf); continue
        if depth >= 1: buf += ch
    out = []
    for p in pts:
        comps, d, cur = [], 0, ''
        for ch in p:
            d += ch == '('; d -= ch == ')'
            if ch == ',' and d == 0: comps.append(cur); cur = ''
            else: cur += ch
        comps.append(cur)
        out.append([sym(c.strip()) for c in comps])
    return out

def mid_lines(P, Q):
    out = []
    for n, a, b in zip('xyz', P, Q):
        v = sp.nsimplify(sp.simplify((a + b) / 2))
        out.append(f'{n}_M=\\frac{{{sp.latex(a)}+({sp.latex(b)})}}{{2}}=[[{sp.sstr(v).replace("sqrt(", "sqrt(")}]]')
    return out

def dist_lines(P, Q):
    out = []; total = 0; terms = []
    for n, a, b in zip('xyz', P, Q):
        d = sp.simplify(b - a); sq = sp.expand(d ** 2); total += sq; terms.append(sq)
        out.append(f'({sp.latex(b)}-({sp.latex(a)}))^2=({sp.latex(d)})^2=[[{sp.sstr(sq)}]]')
    tot = sp.simplify(total)
    out.append(f'd=\\sqrt{{[[{sp.sstr(tot)}]]}}=[[{sp.sstr(sp.sqrt(tot))}]]')
    return out

# ---------------------------------------------------------------- hand-authored blanks
OPEN = '[[?open circle;closed circle|open circle]]'
CLOSED = '[[?open circle;closed circle|closed circle]]'
SOL = lambda ans: f'[[?One solution;No solution;Infinitely many solutions|{ans}]]'
H = {}
def put(qid, part, lines=None, table=None):
    H.setdefault(qid, {})[part] = {k: v for k, v in (('lines', lines), ('table', table)) if v}

# ---- 9G3 LO21 evaluate (exact step blanks: students must show the substitution)
put('G9G-BOOK-Q21-FRQ-01', 'a', ['g+6t=2+6([[!11]])=2+[[!66]]=[[68]]'])
put('G9G-BOOK-Q21-FRQ-02', 'a', ['7-gr=7-[[!2]]([[!3]])=7-[[!6]]=[[1]]'])
put('G9G-BOOK-Q21-FRQ-03', 'a', ['r^2+(g^3-8)^5=[[!3]]^2+([[!2]]^3-8)^5=9+([[!0]])^5=[[9]]'])
put('G9G-BOOK-Q21-FRQ-04', 'a', ['(2t+3g)\\div4=(2\\cdot[[!11]]+3\\cdot[[!2]])\\div4=([[!22]]+[[!6]])\\div4=[[!28]]\\div4=[[7]]'])
# ---- 9G3 LO22 rearrange then substitute
put('G9G-BOOK-Q22-FRQ-01', 'a', ['P-[[2w|2*w]]=2\\ell', '\\ell=\\dfrac{[[P-2w]]}{[[2]]}'])
put('G9G-BOOK-Q22-FRQ-01', 'b', ['\\ell=\\dfrac{36-[[8]]}{2}=\\dfrac{[[28]]}{2}=[[14]]\\text{ m}'])
put('G9G-BOOK-Q22-FRQ-02', 'a', ['ab=[[h]]', 'b=\\dfrac{h}{[[a]]}'])
put('G9G-BOOK-Q22-FRQ-02', 'b', ['b=\\dfrac{[[39]]}{[[0.325]]}=[[120]]\\text{ times at bat}'])
put('G9G-BOOK-Q22-FRQ-03', 'a', ['c-[[p]]=13.50\\,g', 'g=\\dfrac{c-p}{[[13.50|13.5]]}'])
put('G9G-BOOK-Q22-FRQ-03', 'b', ['g=\\dfrac{136-55}{13.50}=\\dfrac{[[81]]}{13.50}=[[6]]\\text{ games}'])
put('G9G-BOOK-Q22-FRQ-04', 'a', ['h=\\dfrac{V}{[[lw|wl]]}'])
put('G9G-BOOK-Q22-FRQ-04', 'b', ['h=\\dfrac{50}{10\\cdot 2}=\\dfrac{50}{[[20]]}=[[2.5]]\\text{ m}'])
# ---- 9G3 LO23 equations
put('G9G-BOOK-Q23-FRQ-01', 'a', ['[[2r+12]]=[[4r+16]]', '[[-4]]=2r', 'r=[[-2]]', '\\text{Check: }2(-2+6)=[[8]],\\quad 4(-2+4)=[[8]]', SOL('One solution')])
put('G9G-BOOK-Q23-FRQ-02', 'a', ['[[9m-6]]=[[6m+6]]', '[[3m]]=12', 'm=[[4]]', '\\text{Check: }3(3\\cdot4-2)=[[30]],\\quad 2(3\\cdot4+3)=[[30]]', SOL('One solution')])
put('G9G-BOOK-Q23-FRQ-03', 'a', ['2x=[[2x-6]]', '0=[[-6]]\\ \\text{(false)}', SOL('No solution')])
put('G9G-BOOK-Q23-FRQ-04', 'a', ['-5(3-q)+4=[[5q-11]]', '5q-11=5q-11\\ \\text{(always true)}', SOL('Infinitely many solutions')])
# ---- 9G3 LO24 tables (x given, y computed from the equation)
put('G9G-BOOK-Q24-FRQ-01', 'a', ['y=[[8-x]]'])
put('G9G-BOOK-Q24-FRQ-02', 'a', ['y=[[10-x]]'])
put('G9G-BOOK-Q24-FRQ-04', 'a', ['y=[[x/4-2|0.25x-2]]'])
# ---- 9G3 LO25 piecewise (endpoint, slope, domain, range)
def piece(q, rows, rng_opts, rng):
    lines = []
    for cond, x0, y0, slope, circ in rows:
        lines.append(f'{cond}:\\ \\text{{slope}}=[[{slope}]],\\ \\text{{endpoint}}\\ ({x0},[[{y0}]])\\ {OPEN if circ == "open" else CLOSED}')
    lines.append('\\text{Domain: }[[?x>3;ℝ;x≥0;x≠3|ℝ]]'.replace('x>3;ℝ;x≥0;x≠3', 'ℝ;x>0;x≥0;x≠' + str(rows[0][1])))
    lines.append(f'\\text{{Range: }}[[?{";".join(rng_opts)}|{rng}]]')
    return lines
put('G9G-BOOK-Q25-FRQ-01', 'a', piece(1, [('x>3', 3, '0.5|1/2', '1/2|0.5', 'open'), ('x\\le3', 3, '-3', '-2', 'closed')], ['[−3, ∞)', '(−3, ∞)', '(0.5, ∞)', 'ℝ'], '[−3, ∞)'))
put('G9G-BOOK-Q25-FRQ-02', 'a', piece(2, [('x>1', 1, '-3', '2', 'open'), ('x\\le1', 1, '1', '4', 'closed')], ['ℝ', '[−3, ∞)', '(−∞, 1]', '(−3, 1]'], 'ℝ'))
put('G9G-BOOK-Q25-FRQ-03', 'a', piece(3, [('x\\ge-3', -3, '-3', '2', 'closed'), ('x<-3', -3, '0', '1/3|0.333', 'open')], ['ℝ', '[−3, ∞)', '(−∞, 0)', '(−3, 0)'], 'ℝ'))
put('G9G-BOOK-Q25-FRQ-04', 'a', piece(4, [('x\\ge1', 1, '7', '3', 'closed'), ('x<1', 1, '4', '1', 'open')], ['(−∞, 4) ∪ [7, ∞)', 'ℝ', '[4, 7]', '(−∞, 7]'], '(−∞, 4) ∪ [7, ∞)'))
# ---- 9G3 LO26 arithmetic sequences
def arith(qid, a1, d):
    n = sp.Symbol('n'); f = sp.Rational(a1) + (n - 1) * sp.Rational(d)
    put(qid, 'a', [f'd=[[{alt(d)}]]', f'a_n={a1}+(n-1)\\left({d}\\right)=[[{ascii_expr(sp.expand(f))}]]'])
    put(qid, 'b', [f'a_7=[[{alt(f.subs(n, 7))}]]'])
arith('G9G-BOOK-Q26-FRQ-01', -3, -5); arith('G9G-BOOK-Q26-FRQ-02', -2, 5)
arith('G9G-BOOK-Q26-FRQ-03', -11, -4); arith('G9G-BOOK-Q26-FRQ-04', '-0.75', '0.25')

# ---- 10G3 polynomial / exponent families built from the stem (see main loop)
put('G10G-Q23-FRQ-01', 'a', ['A=(5x^3y^5)^2=[[25]]\\,x^{[[6]]}\\,y^{[[10]]}'])
put('G10G-Q23-FRQ-02', 'a', ['V=(4m^8n^4)^3=[[64]]\\,m^{[[24]]}\\,n^{[[12]]}'])
put('G10G-Q23-FRQ-03', 'a', ['(m^p)(m^q)=m^{[[p+q]]}', '(m^p)^q=m^{[[pq]]}', '\\text{Equal when } p+q=[[pq]]'])
put('G10G-Q23-FRQ-03', 'b', ['m=2,\\ p=q=1:\\ 2\\cdot2=[[4]],\\quad 2^{1\\cdot1}=[[2]]', '\\text{Can }(m^p)(m^q)>(m^p)^q\\text{ happen?}\\ [[?Yes;No|Yes]]'])
put('G10G-Q23-FRQ-04', 'a', ['(-1)^{2t}=[[1]]', '(a^m)^{2t}=a^{[[2mt]]}', '(b^t)^{2t}=b^{[[2t^2|2tt]]}'])
put('G10G-Q23-FRQ-05', 'a', ['x=x^{[[1]]},\\quad x\\cdot x=x^{[[2]]},\\quad x\\cdot x\\cdot x=x^{[[3]]}'])
put('G10G-Q23-FRQ-05', 'c', ['y=x:\\ [[?linear;nonlinear|linear]]', 'y=x^2:\\ [[?linear;nonlinear|nonlinear]]', 'y=x^3:\\ [[?linear;nonlinear|nonlinear]]'])
UP = 'y→+∞ as x→±∞'; DOWN = 'y→−∞ as x→±∞'
def reading(qid, axis, vx, vy, yi, end, ext):
    put(qid, 'a', [f'\\text{{Axis of symmetry: }}x=[[{axis}]]', f'\\text{{Vertex: }}([[{vx}]],\\ [[{vy}]])'])
    put(qid, 'b', [f'y\\text{{-intercept: }}(0,\\ [[{yi}]])', f'\\text{{End behaviour: }}[[?{UP};{DOWN}|{end}]]', f'[[?maximum;minimum|{ext}]]\\ \\text{{value}}=[[{vy}]]'])
reading('G10G-Q24-FRQ-01', 0, 0, 1, 1, DOWN, 'maximum'); reading('G10G-Q24-FRQ-02', 1, 1, 1, 4, UP, 'minimum')
reading('G10G-Q24-FRQ-03', 0, 0, -4, -4, UP, 'minimum'); reading('G10G-Q24-FRQ-04', -3, -3, -6, 3, UP, 'minimum')
def quad(qid, z1, z2, known, std):
    sg = lambda z: f'+{-z}' if z < 0 else f'-{z}'
    x0, y0 = known
    den = (x0 - z1) * (x0 - z2)
    a = Fraction(y0, den)
    sub = f'a({x0}{sg(z1)})({x0}{sg(z2)})'
    head = f'\\text{{Use the y-intercept }}(0,[[{y0}]])' if x0 == 0 else f'\\text{{Use the vertex }}([[{x0}]],\\ [[{y0}]])'
    put(qid, 'a', [f'y=a(x[[{sg(z1)}#z]])(x[[{sg(z2)}#z]])', f'{head}:\\quad [[{y0}]]={sub}=[[{den}]]\\,a', f'a=[[{alt(a)}]]', f'y=[[{std}]]'])
quad('G10G-Q25-FRQ-01', -2, 3, (0, -6), 'x^2-x-6'); quad('G10G-Q25-FRQ-02', 2, 4, (3, -2), '2x^2-12x+16')
quad('G10G-Q25-FRQ-03', 3, 5, (4, -4), '4x^2-32x+60'); quad('G10G-Q25-FRQ-04', -2, 6, (2, 8), '-x^2/2+2x+6|-0.5x^2+2x+6')

# ---- 10A1
put('G10A-BOOK-Q21-FRQ-01', 'a', ['\\text{Common factor}=[[8]]', '-72p^2+8x^2=8([[-9p^2+x^2]])', '=8([[x-3p#f]])([[x+3p#f]])'])
put('G10A-BOOK-Q21-FRQ-02', 'a', ['\\text{Common factor}=[[4]]', '16b^2-100=4([[4b^2-25]])', '=4([[2b-5#f]])([[2b+5#f]])'])
put('G10A-BOOK-Q21-FRQ-03', 'a', ['\\sqrt{9z^2}=[[3z]],\\quad \\sqrt1=[[1]]', '2\\cdot(3z)\\cdot1=[[6z]]\\ \\Rightarrow\\ \\text{middle term matches? }[[?yes;no|yes]]', '9z^2-6z+1=([[3z-1]])^2'])
put('G10A-BOOK-Q21-FRQ-04', 'a', ['\\sqrt{36x^2}=[[6x]],\\quad \\sqrt{25}=[[5]]', '2\\cdot(6x)\\cdot5=[[60x]]\\ \\Rightarrow\\ \\text{middle term matches? }[[?yes;no|yes]]', '36x^2-60x+25=([[6x-5]])^2'])
for qid, a in (('G10A-BOOK-Q22-FRQ-01', 144), ('G10A-BOOK-Q22-FRQ-02', 160)):
    e = 180 - a
    put(qid, 'a', [f'\\text{{exterior angle}}=180^\\circ-{a}^\\circ=[[{e}]]^\\circ', f'n=\\dfrac{{360}}{{[[{e}]]}}=[[{360 // e}]]'])
put('G10A-BOOK-Q22-FRQ-03', 'a', ['[[9x+27]]=360', '9x=[[333]]', 'x=[[37]]'])
put('G10A-BOOK-Q22-FRQ-04', 'a', ['[[4x+76]]=360', '4x=[[284]]', 'x=[[71]]'])
put('G10A-BOOK-Q23-FRQ-01', 'a', ['\\triangle IHJ\\sim\\triangle [[!LKJ]]', '8x=[[40]]', 'x=[[5]]'])
put('G10A-BOOK-Q23-FRQ-02', 'a', ['\\triangle ABE\\sim\\triangle [[!DCE]]', '12x=[[144]]', 'x=[[12]]'])
put('G10A-BOOK-Q23-FRQ-03', 'a', ['\\triangle UVW\\sim\\triangle [[!RTS]]', 'k=\\dfrac94=[[2.25]]', 'x=5\\times[[2.25]]=[[11.25|45/4]]'])
put('G10A-BOOK-Q23-FRQ-04', 'a', ['\\triangle MNL\\sim\\triangle [[!KJL]]', '8x=[[24]]', 'x=[[3]]'])

def triangle(qid, A, a, b):
    ratio = b * math.sin(math.radians(A)) / a
    if ratio > 1 + 1e-12:
        put(qid, 'a', [f'\\sin B=\\dfrac{{b\\sin A}}{{a}}=[[~0.001:{ratio:.4f}]]', '\\text{Is }\\sin B\\le 1?\\ [[?yes;no|no]]', '[[?No solution;One solution;Two solutions|No solution]]'])
        put(qid, 'b', ['[[?a triangle exists;no triangle exists|no triangle exists]]'])
        return
    B1 = math.degrees(math.asin(min(1, ratio))); cands = [B1]
    if abs(ratio - 1) > 1e-9 and A + (180 - B1) < 180: cands.append(180 - B1)
    n = len(cands); word = {1: 'One solution', 2: 'Two solutions'}[n]
    put(qid, 'a', [f'\\sin B=\\dfrac{{b\\sin A}}{{a}}=[[~0.001:{ratio:.4f}]]', f'[[?No solution;One solution;Two solutions|{word}]]'])
    lines = []
    for i, B in enumerate(cands, 1):
        C = 180 - A - B; c = a * math.sin(math.radians(C)) / math.sin(math.radians(A))
        lines.append(f'B_{{{i}}}=[[~0.5:{B:.0f}]]^\\circ,\\ C_{{{i}}}=[[~0.5:{C:.0f}]]^\\circ,\\ c_{{{i}}}=[[~0.06:{c:.1f}]]')
    if n == 1 and abs(ratio - 1) > 1e-9:
        B2 = 180 - B1
        lines.append(f'\\text{{Other candidate: }}B_2=180^\\circ-B_1=[[~0.5:{B2:.0f}]]^\\circ,\\ A+B_2=[[~0.5:{A + B2:.0f}]]^\\circ\\ [[?Valid triangle;Rejected (sum ≥ 180°)|Rejected (sum ≥ 180°)]]')
    put(qid, 'b', lines)
triangle('G10A-BOOK-Q25-FRQ-01', 50, 34, 40); triangle('G10A-BOOK-Q25-FRQ-02', 24, 3, 8)
triangle('G10A-BOOK-Q25-FRQ-03', 125, 22, 15); triangle('G10A-BOOK-Q25-FRQ-04', 30, 2, 4)

PLOTS = {
    'G9G-BOOK-Q24-FRQ-01': {'kind': 'line', 'bounds': [-12, 12, -12, 12], 'line': {'m': -1, 'b': 8}, 'min_points': 3},
    'G9G-BOOK-Q24-FRQ-02': {'kind': 'line', 'bounds': [-12, 12, -12, 12], 'line': {'m': -1, 'b': 10}, 'min_points': 3},
    'G9G-BOOK-Q24-FRQ-03': {'kind': 'line', 'bounds': [-12, 12, -12, 12], 'line': {'m': 0.5, 'b': 1}, 'min_points': 3},
    'G9G-BOOK-Q24-FRQ-04': {'kind': 'line', 'bounds': [-12, 12, -12, 12], 'line': {'m': 0.25, 'b': -2}, 'min_points': 3},
    'G9G-BOOK-Q25-FRQ-01': {'kind': 'piecewise', 'bounds': [-6, 10, -6, 8], 'pieces': [{'m': 0.5, 'b': -1, 'x0': 3, 'side': 'right', 'closed': False}, {'m': -2, 'b': 3, 'x0': 3, 'side': 'left', 'closed': True}]},
    'G9G-BOOK-Q25-FRQ-02': {'kind': 'piecewise', 'bounds': [-6, 8, -8, 8], 'pieces': [{'m': 2, 'b': -5, 'x0': 1, 'side': 'right', 'closed': False}, {'m': 4, 'b': -3, 'x0': 1, 'side': 'left', 'closed': True}]},
    'G9G-BOOK-Q25-FRQ-03': {'kind': 'piecewise', 'bounds': [-8, 6, -6, 8], 'pieces': [{'m': 2, 'b': 3, 'x0': -3, 'side': 'right', 'closed': True}, {'m': 1 / 3, 'b': 1, 'x0': -3, 'side': 'left', 'closed': False}]},
    'G9G-BOOK-Q25-FRQ-04': {'kind': 'piecewise', 'bounds': [-6, 6, -4, 12], 'pieces': [{'m': 3, 'b': 4, 'x0': 1, 'side': 'right', 'closed': True}, {'m': 1, 'b': 3, 'x0': 1, 'side': 'left', 'closed': False}]},
}

CORRECTIONS = {
    # sin B = 4*sin30/2 = 1 exactly -> ONE (right) triangle, not two identical ones
    'G10A-BOOK-Q25-FRQ-04': {
        'a': 'sin B=b sin A/a=1.00000000. Exactly one solution (a right angle at B): the second arcsine candidate 180°−90° repeats the same triangle. Correct ratio (2), count and admissibility (2).',
        'b': 'B=90°, C=60°, c≈3.5 (one triangle only). Calculate with full-precision angles before rounding. Correct triangle and remaining side (6).',
    },
}

def process(classroom):
    path = ROOT / 'public/data/study' / f'{classroom}.json'
    d = json.loads(path.read_text())
    n = 0
    for q in d['questions']:
        if q['type'] != 'frq': continue
        spec = dict(H.get(q['id'], {}))
        if q['id'].startswith('G10G-Q21-FRQ'):
            spec['a'] = {'lines': poly_sum(q['math_latex'])}
        if q['id'].startswith('G10G-Q22-FRQ'):
            spec['a'] = {'lines': poly_product(q['math_latex'])}
        if q['id'].startswith('G10A-BOOK-Q24-FRQ'):
            P = pts_from(q['math_latex'])
            if q['id'].endswith(('01', '02')):
                spec['a'] = {'lines': mid_lines(*P)}
            else:
                spec['a'] = {'lines': dist_lines(*P)}; spec['b'] = {'lines': mid_lines(*P)}
        for part in q['parts']:
            part.pop('blanks', None); part.pop('plot', None)
            if q['id'] in PLOTS: part['plot'] = PLOTS[q['id']]
            b = spec.get(part['id'])
            if b: part['blanks'] = b; n += 1
            fix = CORRECTIONS.get(q['id'], {}).get(part['id'])
            if fix: part['answer']['model_answer_and_marking'] = fix
    path.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    return n

if __name__ == '__main__':
    for c in ('9G3', '10G3', '10A1'):
        print(c, process(c), 'parts with blanks')
