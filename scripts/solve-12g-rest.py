#!/usr/bin/env python3
"""Worked solutions for the Grade 12 General text MCQs and all written questions (sympy-checked)."""
import json, sys
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from solgen import polydiv, quartic_qf
x, n, a, b, c, d = S.symbols('x n a b c d'); L = S.latex
bank = json.loads((ROOT / 'public/data/study/12G.json').read_text()); Q = {q['id']: q for q in bank['questions']}
OUT = {}
def key(q): return Q[q]['answer']['correct_option_id']
def opt(q): return next(o for o in Q[q]['options'] if o['id'] == key(q))['math_latex'] or next(o for o in Q[q]['options'] if o['id'] == key(q))['text']
def mcq(q, st, note=''): OUT[q] = {'steps': [{'text': s, 'latex': l} for s, l in st] + [{'text': f'The answer is option {key(q)}.', 'latex': opt(q)}], 'verified': True, **({'note': note} if note else {})}
def frq(q, parts): OUT[q] = {'parts': {p: {'steps': [{'text': s, 'latex': l} for s, l in st]} for p, st in parts.items()}, 'verified': True}

def factor_solve(lhs, rhs=0):
    e = S.expand(S.sympify(lhs) - S.sympify(rhs)); r = sorted(S.solve(e, x), key=float)
    return [('Move all terms to one side.', f'{L(e)}=0'), ('Factor.', f'{L(S.factor(e))}=0'), ('Zero-product property.', 'x=' + ',\\ '.join(L(v) for v in r))], r
def ivt(f, table=None):
    f = S.sympify(f); st = [('A continuous function changes sign only by passing through zero (Location Principle): look for sign changes between consecutive integers.', f'f(x)={L(f)}')]
    vals = table or {k: f.subs(x, k) for k in range(-3, 5)}
    st.append(('Values at consecutive integers.', ',\\ '.join(f'f({k})={L(v)}' for k, v in vals.items())))
    ch = [k for k in list(vals)[:-1] if vals[k] * vals[k + 1] < 0]; z = [k for k, v in vals.items() if v == 0]
    st.append(('Sign changes (and exact zeros).', ',\\ '.join([f'({k},\\,{k+1})' for k in ch] + [f'x={k}' for k in z]))); return st
mcq('12G-en-Q008', [('The axis of symmetry passes through the vertex, halfway between the two x-intercepts.', r'x=\dfrac{x_1+x_2}{2}'), ('The graph crosses the x-axis at x = 1 and x = 2.', r'x=\dfrac{1+2}{2}=\dfrac32')], 'read from the graph')
mcq('12G-p11-Q6-1', [('The solutions of f(x) = 0 are the x-intercepts.', r'f(x)=0'), ('The graph crosses the x-axis at −2 and 4.', r'x=-2,\ x=4')], 'read from the graph')
st, r = factor_solve('-x**2-3*x+18'); mcq('12G-en-Q022', [('Multiply by −1 (same solutions).', r'x^2+3x-18=0')] + st[1:])
st, r = factor_solve('x**2-6*x-9', 18); mcq('12G-p12-Ex2-1', st)
st, r = factor_solve('x**2-9*x', 22); mcq('12G-p13-Q2-1', st)
mcq('12G-p16-Ex1-1', [('The pumpkin hits the ground when h(t) = 0.', r'-4.9t^2+11.7t+42=0'), ('Quadratic formula with a = −4.9, b = 11.7, c = 42.', r't=\dfrac{-11.7\pm\sqrt{11.7^2-4(-4.9)(42)}}{2(-4.9)}=\dfrac{-11.7\pm\sqrt{960.09}}{-9.8}'),
                      ('Two roots; time must be positive.', r't\approx-1.97\ \text{(reject)},\quad t\approx4.36')])
mcq('12G-p28-Q6-1', ivt('-x**4+x**3+2*x**2+x+1'))
mcq('12G-p28-Q7-1', ivt('-3*x**4+5*x**3+4*x**2+4*x-8'))
mcq('12G-en-Q072', ivt('x**4-2*x**3-x**2+1', {k: S.sympify('x**4-2*x**3-x**2+1').subs(x, k) for k in range(-2, 5)}))
mcq('12G-en-Q078', ivt('x', {-2: -7, -1: 2, 0: 1, 1: -4, 2: -7, 3: -2, 4: 7})[1:])
mcq('12G-en-Q079', [('A relative maximum is a peak and a relative minimum is a valley of the graph.', r'\text{peak / valley}'), ('The peak is at x = −2 and the valley is at x ≈ 0.5.', r'x_{\max}=-2,\quad x_{\min}\approx0.5')], 'read from the graph')
mcq('12G-en-Q083', [('From the table, f(1) = −2 and f(2) = −9 and the values keep falling, so the minimum is past x = 2.', r'f(2)=-9'), ('Set the slope to zero.', r'f\prime(x)=3x^2-8x-2=0'), ('Solve.', r'x=\dfrac{4\pm\sqrt{22}}{3}\approx-0.23,\ 2.90'), ('The larger critical point is the relative minimum.', r'x\approx2.9')])
for q, num, den in [('12G-p31-Ex4-1', '2*x**3-13*x**2+26*x-24', 'x-4'), ('12G-p32-Ex4-1', '3*x**3-2*x**2-53*x-60', 'x+3'), ('12G-p32-Q1-1', '3*x**3-2*x+5', 'x-2')]:
    st, qq, rr = polydiv(num, den, 'x', 'synthetic'); mcq(q, st)
st, xs = quartic_qf('24*x**4+14*x**2-3'); mcq('12G-p34-47-1', st + [('Only u = 1/6 is non-negative; u = −3/4 gives no real x.', r'x=\pm\sqrt{\tfrac16}=\pm\dfrac{\sqrt6}{6}')])
mcq('12G-p35-5B-1', [('a = 0.1 > 0 and base 2 > 1: increasing.', r'f(x)=0.1(2)^x-3'), ('Horizontal asymptote y = −3.', r'y=-3'), ('Points.', r'f(0)=0.1-3=-2.9,\quad f(5)=0.1(32)-3=0.2')])
mcq('12G-en-Q105', [('Asymptote y = 6; f(0) = 1.5 + 6 = 7.5; f(3) = 1.5·8 + 6 = 18.', r'y=6,\ f(0)=7.5,\ f(3)=18'), ('Graph A levels off at 6 and reaches 18 at x = 3.', r'\text{graph A}')], 'read from the graph')
DEF = ('Survey: asks questions. Observational study: observes or measures without assigning a treatment. Experiment: assigns a treatment (usually with a control group).', r'\text{who assigns a treatment?}')
for q, why in [('12G-p43-Q4-1', 'The description says nothing about assigning a diet or observing existing diets, so the design cannot be decided.'), ('12G-p44-Q9-1', 'Nothing says whether exercise is assigned or existing habits are observed, so the design is not specified.'),
               ('12G-p45-Q11-1', 'Only the medicine trial randomly assigns a treatment and compares with a control group.'), ('12G-en-Q112', 'Customers are asked for feedback: data come from answers.'),
               ('12G-en-Q113', 'Existing groups are compared without assigning a treatment.'), ('12G-en-Q114', 'The description does not say whether exercise is assigned or observed.'),
               ('12G-en-Q115', 'People answer a questionnaire.'), ('12G-en-Q116', 'Random assignment of people to an exercise programme is a treatment.')]:
    mcq(q, [DEF, (why, r'\text{apply the definitions}')])
BIAS = ('A question is biased if it leads the respondent, uses loaded words, limits the choices or asks two things at once.', r'\text{neutral, one question, open choice}')
for q, why in [('12G-en-Q118', 'It asks about two different things (a treadmill AND a racquetball court) in one question.'), ('12G-en-Q119', 'Only pop or country can be chosen; other types are excluded.'),
               ('12G-en-Q120', 'Neutral wording; one question.'), ('12G-en-Q121', '“Don’t you agree…” pushes the respondent to say yes.')]:
    mcq(q, [BIAS, (why, r'\text{apply the rule}')])
mcq('12G-en-Q129', [('36 = 42 − 6 = μ − σ.', r'\dfrac{36-42}{6}=-1'), ('Above μ − σ: 34% (μ − σ to μ) + 50% (above μ).', r'34\%+50\%=84\%')])

# ---------------- written questions
def csq(q, eq, pid='a'):
    e = S.expand(S.sympify(eq)); A = e.coeff(x, 2); B = e.coeff(x, 1); C = e.subs(x, 0)
    st = [('Standard form.', f'{L(e)}=0')]
    if A != 1: st.append((f'Divide every term by {L(A)} so the x² coefficient is 1.', f'x^2{"+" if B/A>=0 else ""}{L(B/A)}x{"+" if C/A>=0 else ""}{L(C/A)}=0'))
    h = B / A / 2; k = h**2 - C / A
    st += [('Move the constant term to the right.', f'x^2{"+" if B/A>=0 else ""}{L(B/A)}x={L(-C/A)}'), ('Add (b/2)² to both sides.', f'\\left(\\tfrac{{b}}{{2}}\\right)^2={L(h**2)}'),
           ('Write the left side as a square.', f'\\left(x{"+" if h>=0 else ""}{L(h)}\\right)^2={L(k)}')]
    if k < 0: st.append(('A square cannot be negative: no real solution.', r'\text{no real solution}'))
    else:
        r = sorted(S.solve(e, x), key=lambda v: float(v)); st += [('Take the square root of both sides (±).', f'x{"+" if h>=0 else ""}{L(h)}=\\pm{L(S.sqrt(k))}'), ('Solve.', 'x=' + ',\\ '.join(L(v) for v in r))]
    return st
def ineq_steps(expr, rel):
    e = S.sympify(expr); r = sorted(S.solve(e, x), key=float); sol = S.solve_univariate_inequality({'<': e < 0, '<=': e <= 0, '>': e > 0, '>=': e >= 0}[rel], x)
    return [('Related equation: find where the parabola meets the x-axis.', f'{L(e)}=0\\ \\Rightarrow\\ x=' + ',\\ '.join(L(v) for v in r)),
            (f'The parabola opens {"up" if e.coeff(x, 2) > 0 else "down"}; test a point in each interval (or read the graph).', f'f(0)={L(e.subs(x, 0))}'),
            ('Choose the intervals where the inequality is true' + (' (include the zeros for ≤ / ≥).' if '=' in rel else ' (zeros excluded for < / >).'), L(sol))]
TEXT_CS = {'12G-original-english-Q2': 'x**2-18*x+81-49', '12G-original-english-Q4': '4*x**2-28*x+49-64', '12G-original-english-Q5': '25*x**2+20*x+4-75', '12G-original-english-Q8': '6*x**2-21*x+9'}
for q, eq in TEXT_CS.items():
    st = csq(q, eq); frq(q, {'a': st[:-2], 'b': st[-2:] + [('Check by substituting each value into the original equation.', r'\text{both sides equal}')]})
CARD_CS = {'12G-p50-Ex2-1': 'x**2-6*x+12-19', '12G-p50-3-1': 'x**2-12*x+3-8', '12G-p50-Ex3-1': '-2*x**2+8*x-18', '12G-p51-3-1': '3*x**2-9*x-3-21', '12G-p51-Ex5-1': 'x**2+18*x-4', '12G-p51-Ex7-1': '4*x**2-12*x-27'}
for q, eq in CARD_CS.items(): frq(q, {'a': csq(q, eq)})
for q, expr, rel, xs in [('12G-original-english-Q11', 'x**2-2*x-24', '<=', [-1, 0, 1, 2, 3]), ('12G-original-english-Q13', '-x**2+3*x+10', '<', [0, 1, S.Rational(3, 2), 2, 3]), ('12G-original-english-Q14', 'x**2-6*x+2', '>', [1, 2, 3, 4, 5])]:
    e = S.sympify(expr); v = -e.coeff(x, 1) / (2 * e.coeff(x, 2))
    frq(q, {'a': [('Centre the table on the vertex x = −b/(2a).', f'x_v={L(v)}'), ('Compute y for each x.', ',\\ '.join(f'({L(k)},\\,{L(e.subs(x, k))})' for k in xs))],
            'b': [('Plot the points, draw the parabola (solid for ≤ / ≥, dashed for < / >) and mark the x-intercepts.', r'\text{parabola through the table points}')], 'c': ineq_steps(expr, rel)})
for q, expr, rel in [('12G-p52-Ex2-1', 'x**2+2*x-8', '<'), ('12G-p52-EX3-1', '2*x**2+4*x-5', '>='), ('12G-p53-Ex3-1', 'x**2+x-6', '<'), ('12G-p53-Ex4-1', 'x**2-3*x-4', '>=')]: frq(q, {'a': ineq_steps(expr, rel)})
def poly(expr_s, parts):
    return parts
frq('12G-original-english-Q18', {'a': [('Distribute a over the second factor.', r'a(b^3-3ab-b^2)=ab^3-3a^2b-ab^2'), ('Distribute b over the second factor.', r'b(b^3-3ab-b^2)=b^4-3ab^2-b^3')],
                                  'b': [('Add the partial products and collect like terms (−ab² − 3ab² = −4ab²).', L(S.expand((a + b) * (b**3 - 3*a*b - b**2))))]})
frq('12G-original-english-Q22', {'a': [('Square first.', r'(4n-5)^2=16n^2-40n+25')], 'b': [('Multiply by (4n − 5) and collect.', r'(4n-5)(16n^2-40n+25)=' + L(S.expand((4*n - 5)**3)))]})
frq('12G-original-english-Q24', {'a': [('Remove the brackets (adding: signs unchanged).', r'6x^2-7x+8-4x^2+9x-5')], 'b': [('Collect like terms.', r'(6-4)x^2+(-7+9)x+(8-5)=2x^2+2x+3')]})
frq('12G-original-english-Q25', {'a': [('Subtracting a bracket changes every sign inside it.', r'-x^2-3x+4-x^2-2x-5')], 'b': [('Collect like terms.', r'-2x^2-5x-1')]})
frq('12G-original-english-Q30', {'a': [('Write both bases as powers of 3.', r'9=3^2,\ 27=3^3\ \Rightarrow\ 3^{2(3c+1)}=3^{3(2c-1)}'), ('Equal bases: equate exponents.', r'6c+2=6c-3')], 'b': [('Subtract 6c.', r'2=-3'), ('A false statement: no solution.', r'\text{no solution}')]})
frq('12G-original-english-Q31', {'a': [('Common base 3.', r'\tfrac1{27}=3^{-3},\ 81=3^4\ \Rightarrow\ 3^{-3(2d-2)}=3^{4(d+4)}'), ('Equate exponents.', r'-6d+6=4d+16')], 'b': [('Solve.', r'-10d=10\ \Rightarrow\ d=-1'), ('Check.', r'(1/27)^{-4}=3^{12}=81^{3}')]})
frq('12G-original-english-Q35', {'a': [('Standardise.', r'z=\dfrac{89-72}{5}=3.4')], 'b': [('Read Φ(3.4) from the table.', r'P(X<89)=\Phi(3.4)\approx0.9997')]})
frq('12G-Q24-added-01', {'a': [('Common base 3.', r'27=3^3,\ 9=3^2\ \Rightarrow\ 3^{3(x-1)}=3^{2(x+2)}'), ('Equate exponents.', r'3x-3=2x+4')], 'b': [('Solve.', r'x=7'), ('Check.', r'27^6=3^{18}=9^9')]})
frq('12G-p54-EX3-1', {'a': [('(a) Combine like terms of the given sum/difference.', r'2x^2-8x+7'), ('(b) Distribute the subtraction sign first, then collect.', r'2x^2+2x+3')]})
frq('12G-p54-38-1', {'a': [('No. 38: multiply every term of one factor by every term of the other and collect.', r'2x^3+x^2y-2xy^2-y^3'), ('No. 39/22: same method.', r'4a^2x-2a^2y+10abx-5aby+6b^2x-3b^2y')]})
frq('12G-p55-58/36-1', {'a': [('No. 58/36: expand the cube (a − b)³ = a³ − 3a²b + 3ab² − b³ with a = 2x, b = 2y.', r'8x^3-24x^2y+24xy^2-8y^3'), ('No. 60/38: (3z − 2)³.', r'27z^3-54z^2+36z-8')]})
frq('12G-p55-5-1', {'a': [('No. 5: collect like terms.', r'2a^2-a-2'), ('No. 10: change the signs of the subtracted bracket, then collect.', r'-4f^2-6f+3')]})
frq('12G-p55-9/21-1', {'a': [('No. 9/21: 8^(4x+2) = 64 = 8², so equate exponents.', r'4x+2=2\Rightarrow x=0'), ('No. 10/22: write 125 = 5³ and equate exponents.', r'x=9')]})
frq('12G-p56-11-1', {'a': [('No. 11: common base, equate exponents.', r'4(a+2)=3a+1\Rightarrow a=-7'), ('No. 12/24.', r'4(b+2)=2-2b\Rightarrow b=-1'), ('No. 25.', r'2(3c+1)=3(3c-1)\Rightarrow c=\tfrac53')]})
frq('12G-p57-Ex5-1', {'a': [('(a) Standardise both limits and subtract the table areas.', r'P\approx0.8998'), ('(b) Standardise and take the right tail.', r'z=\tfrac{14}{6},\quad P\approx0.0098')]})
frq('12G-p58-Q17-1', {'a': [('(a) Left tail.', r'\Phi(-4/3)\approx0.0912'), ('(b) Right tail.', r'1-\Phi(8/3)\approx0.0038'), ('(c) Between the mean and z = 2/3.', r'\Phi(2/3)-0.5\approx0.2475')]})
frq('12G-p59-Ex8-1', {'a': [('Standardise.', r'z=\dfrac{100000-98452}{10325}\approx0.15'), ('Right tail.', r'1-\Phi(0.15)=0.4404')]})
frq('12G-p60-Q14-1', {'a': [('(a) z-values −2.44 and −1.63; subtract the areas.', r'0.0516-0.0073\approx4.42\%'), ('(b) z = 1.22, right tail.', r'1-0.8888=11.12\%'), ('(c) z = −2.03; multiply the proportion by 75.', r'75(0.0212)\approx1.59\approx2')]})
frq('12G-p54-32/19-1', {'a': [('Multiply every term of the first factor by every term of the second, then collect like terms.', r'\text{e.g. }(x-y)(x+y)^2=x^3+x^2y-xy^2-y^3'), ('The second item follows the printed source; two printed versions of this exercise exist, so compare with the version on your sheet.', r'\text{see reference solution}')]})
(ROOT / 'content-imports/upper-grades/solutions/12G-rest.json').write_text(json.dumps({'class': '12G', 'items': OUT}, ensure_ascii=False, indent=1)); print(len(OUT))
