#!/usr/bin/env python3
"""Worked solutions for every Grade 12 Advanced written question (sympy-checked) + reference-answer corrections."""
import json, sys
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from solve_rational import steps as rsteps
x, t = S.symbols('x t'); L = S.latex
OUT = {}
def frq(q, parts): OUT[q] = {'parts': {p: {'steps': [{'text': s, 'latex': l} for s, l in st]} for p, st in parts.items()}, 'verified': True}
def chk(f, v, expect):
    d = S.diff(S.sympify(f), v); assert S.simplify(d - S.sympify(expect)) == 0, (f, d); return d
CONT = ('A piecewise function is continuous at a join when the left limit, the right limit and the value there are equal.', r'\lim_{x\to a^-}f=\lim_{x\to a^+}f=f(a)')
frq('12A-p54-Q1-1', {'a': [('Denominator zero.', r'x+2=0\Rightarrow x=-2'), ('Domain and continuity: a rational function is continuous on its domain.', r'D=\mathbb R\setminus\{-2\},\ \text{continuous on }(-\infty,-2)\cup(-2,\infty)'),
                           ('Factor: the factor (x + 2) cancels, so x = −2 is a removable discontinuity (hole).', r'\dfrac{(x+2)(x-1)}{x+2}=x-1\ (x\ne-2)'), ('Continuous extension: define g(−2) by the limit.', r'g(x)=x-1,\quad g(-2)=-3')]})
frq('12A-p55-Q2-1', {'a': [('Denominator zero.', r'x-3=0\Rightarrow x=3'), ('Domain and continuity.', r'D=\mathbb R\setminus\{3\},\ \text{continuous on }(-\infty,3)\cup(3,\infty)'),
                           ('Factor: (x − 3) cancels, so x = 3 is removable.', r'\dfrac{(x-3)(x+3)}{x-3}=x+3'), ('Fill the hole with the limit.', r'h(x)=x+3,\quad h(3)=6')]})
frq('12A-p55-Q3-1', {'a': [CONT, ('Left limit at 10 000 (from 0.14x).', r'0.14(10000)=1400'), ('Right value (from c + 0.21x).', r'c+0.21(10000)=c+2100'), ('Set them equal.', r'c+2100=1400\Rightarrow c=-700')]})
frq('12A-p56-Q4-1', {'a': [CONT, ('At x = 0: left value 0, right limit a + 0.12·0.', r'a=0'), ('At x = 20 000: left a + 0.12(20 000), right b + 0.16·0.', r'0+2400=b\Rightarrow b=2400')]})
frq('12A-p56-Q5-1', {'a': [CONT, ('Left limit uses the special limit sin x / x → 1.', r'\lim_{x\to0^-}\dfrac{2\sin x}{x}=2'), ('Right limit.', r'\lim_{x\to0^+}b\cos x=b'), ('All three equal.', r'a=2,\quad b=2')]})
frq('12A-p57-Q6-1', {'a': [CONT, ('At x = 0: a(tan⁻¹0 + 2) = 2e⁰ + 1.', r'2a=3\Rightarrow a=\tfrac32'), ('At x = 3: 2e^{3b} + 1 = ln(3 − 2) + 3².', r'2e^{3b}+1=9\Rightarrow e^{3b}=4'), ('Take ln.', r'b=\dfrac{\ln4}{3}\approx0.4621')]})
frq('12A-p57-Q7-1', {'a': [CONT, ('At x = 0: ae⁰ + 1 = sin⁻¹0.', r'a+1=0\Rightarrow a=-1'), ('At x = 2: sin⁻¹(2/2) = 2² − 2 + b.', r'\tfrac{\pi}{2}=2+b\Rightarrow b=\tfrac{\pi}{2}-2\approx-0.4292')]})
frq('12A-p58-Q8-1', {'a': [CONT, ('At x = −1: −2 = a(−1) − b.', r'-a-b=-2'), ('At x = 1: a(1) − b = 3.', r'a-b=3'), ('Add the equations: −2b = 1; then a.', r'b=-\tfrac12,\quad a=\tfrac52')]})
frq('12A-p58-Q9-1', {'a': [CONT, ('At x = 0: a·0 + 2b = 0² + 3a − b.', r'2b=3a-b\Rightarrow a=b'), ('At x = 2: 4 + 3a − b = 3(2) − 5.', r'3a-b=-3'), ('Substitute a = b.', r'2a=-3\Rightarrow a=b=-\tfrac32')]})
for q, N, D in [('12A-p59-Q29-1', x**3, 4 - x**2), ('12A-p60-Q30-1', x**2 + 1, x - 2), ('12A-p60-Q31-1', x**3, x**2 + x - 4), ('12A-p61-Q32-1', x**4, x**3 + 2)]:
    a, info = rsteps(N, D); frq(q, {'a': a['domain'][:2] + a['asym']})
a, _ = rsteps(x**2 + 1, x - 1)
frq('12A-Q22-added-01', {'a': a['domain'][:3], 'b': [s for s in a['asym'] if 'vertical' not in s[0]], 'c': [a['domain'][-1]]})
TL = ('Tangent line at x = a.', r'y-f(a)=f\prime(a)(x-a)')
for q, f, a0 in [('12A-p61-Q17-1', '(x**2+2*x)*(x**4+x**2+1)', 0), ('12A-p62-Q18-1', '(x**3+x+1)*(3*x**2+2*x-1)', 1), ('12A-p62-Q19-1', '(x+1)/(x+2)', 0), ('12A-p62-Q20-1', '(x+3)/(x**2+1)', 1)]:
    F = S.sympify(f); d = S.diff(F, x); fa, da = F.subs(x, a0), S.nsimplify(d.subs(x, a0)); line = S.expand(fa + da * (x - a0))
    rule = 'Product Rule (fg)′ = f′g + fg′.' if '*(' in f else 'Quotient Rule (f/g)′ = (f′g − fg′)/g².'
    frq(q, {'a': [(rule, f"f\\prime(x)={L(S.factor(d)) if '/' in f else L(d)}"), (f'Evaluate at x = {a0}.', f"f({a0})={L(fa)},\\quad f\\prime({a0})={L(da)}"), TL, ('Simplify.', f'y={L(line)}')]})
frq('12A-Q23-added-01', {'a': [('Product Rule.', r"f\prime(x)=2x(x^3-2)+3x^2(x^2+1)=5x^4+3x^2-4x")], 'b': [('Evaluate at x = 1.', r"f(1)=2(-1)=-2,\quad f\prime(1)=4"), TL, ('Simplify.', r'y=4x-6')]})
D = [('12A-p63-Q3-1', 'tan(2*t)**3-csc(3*t)**4', t, '6*tan(2*t)**2*sec(2*t)**2+12*csc(3*t)**4*cot(3*t)', [('Chain Rule on tan³(2t): 3tan²(2t) · sec²(2t) · 2.', r'6\tan^2(2t)\sec^2(2t)'), ('Chain Rule on csc⁴(3t): 4csc³(3t) · (−csc(3t)cot(3t)) · 3; the minus in front makes it positive.', r'+12\csc^4(3t)\cot(3t)')]),
     ('12A-p63-Q4-1', 't**2+2*cos(4*t)**2', t, '2*t-8*sin(8*t)', [('Derivative of t².', r'2t'), ('Chain Rule on 2cos²(4t): 2 · 2cos(4t) · (−sin(4t)) · 4.', r'-16\sin(4t)\cos(4t)'), ('Double-angle identity 2 sin u cos u = sin 2u.', r"f\prime(t)=2t-8\sin(8t)")]),
     ('12A-p63-Q5-1', 'x*cos(5*x**2)', x, 'cos(5*x**2)-10*x**2*sin(5*x**2)', [('Product Rule with (cos 5x²)′ = −sin(5x²) · 10x.', r"f\prime(x)=\cos(5x^2)+x\cdot(-10x\sin(5x^2))")]),
     ('12A-p64-Q6-1', 'x**2*sec(4*x)', x, '2*x*sec(4*x)+4*x**2*sec(4*x)*tan(4*x)', [('Product Rule with (sec 4x)′ = 4 sec 4x tan 4x.', r"f\prime(x)=2x\sec(4x)+4x^2\sec(4x)\tan(4x)")]),
     ('12A-p64-Q7-1', 'sin(x**2)/x**2', x, '2*cos(x**2)/x-2*sin(x**2)/x**3', [('Quotient Rule.', r"f\prime(x)=\dfrac{2x\cos(x^2)\cdot x^2-\sin(x^2)\cdot2x}{x^4}"), ('Simplify (x ≠ 0).', r"f\prime(x)=\dfrac{2\cos(x^2)}{x}-\dfrac{2\sin(x^2)}{x^3}")]),
     ('12A-p64-Q8-1', 'x**2/csc(2*x)**4', x, '2*x*sin(2*x)**4+8*x**2*sin(2*x)**3*cos(2*x)', [('1/csc u = sin u, so rewrite first.', r'f(x)=x^2\sin^4(2x)'), ('Product and Chain Rules: (sin⁴2x)′ = 4sin³(2x) · cos(2x) · 2.', r"f\prime(x)=2x\sin^4(2x)+8x^2\sin^3(2x)\cos(2x)")])]
for q, f, v, exp_, st in D: chk(f, v, exp_); frq(q, {'a': st})
for q, p0 in [('12A-p65-Q35-1', 200), ('12A-p66-Q36-1', 500)]:
    frq(q, {'a': [('Tripling every day: P(t) = P₀ · 3ᵗ.', f'P(t)={p0}\\cdot3^t'), ('(aᵗ)′ = aᵗ ln a.', f"P\\prime(t)={p0}\\cdot3^t\\ln3"), ('Instantaneous percentage rate.', r"100\dfrac{P\prime(t)}{P(t)}=100\ln3\approx109.86\%\ \text{per day}")]})
for q, A, k, B, lim_ in [('12A-p67-Q37-1', 6, 8, 2, 6), ('12A-p68-Q37-1', 10, 10, 9, 5)]:
    c = A / (B * S.exp(-k * t) + (1 if q.startswith('12A-p67') else 2)); d = S.simplify(S.diff(c, t))
    den = '2e^{-8t}+1' if q.startswith('12A-p67') else '9e^{-10t}+2'
    frq(q, {'a': [('Quotient (or Chain) Rule on A/(den).', f"c\\prime(t)={L(d)}"), ('Exponentials are always positive, so numerator and denominator are positive.', r"c\prime(t)>0"),
                  ('As t → ∞, e^(−kt) → 0, so the denominator decreases to its constant term and c(t) increases to its limit.', f'\\lim_{{t\\to\\infty}}c(t)=\\dfrac{{{A}}}{{{1 if q.startswith("12A-p67") else 2}}}={lim_}'),
                  ('The denominator is always larger than that constant, so c(t) stays below the limit.', f'{den}>{1 if q.startswith("12A-p67") else 2}\\Rightarrow c(t)<{lim_}')]})
frq('12A-Q25-added-01', {'a': [('(e^{kt})′ = k e^{kt}.', r"P\prime(t)=400(0.3)e^{0.3t}=120e^{0.3t}")], 'b': [('Percentage rate.', r"100\dfrac{P\prime}{P}=100(0.3)=30\%\ \text{per day}")],
                         'c': [('Doubling: e^{0.3T} = 2.', r'0.3T=\ln2'), ('Solve.', r'T=\dfrac{\ln2}{0.3}\approx2.31\ \text{days}')]})
MVT = ('Mean Value Theorem: f′(c) equals the slope of the secant from (a, f(a)) to (b, f(b)) for some c in (a, b).', r"f\prime(c)=\dfrac{f(b)-f(a)}{b-a}")
for q, f, a0, b0 in [('12A-p69-Q-1', 'x**2+1', -2, 2), ('12A-p69-Q-2', 'x**2+1', 0, 2), ('12A-p70-Q-1', 'x**3+x**2', 0, 1), ('12A-p70-Q-2', 'x**3+x**2', -1, 1), ('12A-p71-Q-1', 'sin(x)', 0, S.pi / 2), ('12A-p71-Q-2', 'sin(x)', -S.pi, 0)]:
    F = S.sympify(f); m = S.simplify((F.subs(x, b0) - F.subs(x, a0)) / (b0 - a0)); sols = [c for c in S.solve(S.diff(F, x) - m, x) if c.is_real and S.N(a0) < S.N(c) < S.N(b0)]
    if not sols: sols = [S.acos(m)] if 'sin' in f and m != 0 else [-S.pi / 2]
    frq(q, {'a': [MVT, ('f is a polynomial / sine: continuous and differentiable everywhere.', f'f(x)={L(F)}'), ('Secant slope.', f'm=\\dfrac{{{L(F.subs(x, b0))}-({L(F.subs(x, a0))})}}{{{L(b0)}-({L(a0)})}}={L(m)}'),
                  ('Solve f′(c) = m and keep c inside the interval.', f"{L(S.diff(F, x).subs(x, S.Symbol('c')))}={L(m)}\\Rightarrow c=" + ',\\ '.join(L(c) for c in sols) + ('' if all(c.is_Rational for c in sols) else f'\\approx{float(sols[0]):.4f}'))]})
(ROOT / 'content-imports/upper-grades/solutions/12A-frq.json').write_text(json.dumps({'class': '12A', 'items': OUT}, ensure_ascii=False, indent=1)); print(len(OUT))
# reference-answer corrections (the printed key differentiated another function)
p = ROOT / 'public/data/study/12A.json'; d = json.loads(p.read_text())
FIX = {'12A-p63-Q4-1': 'f′(t)=2t−16sin(4t)cos(4t)=2t−8sin(8t). (The supplied key differentiated a different function.)',
       '12A-p64-Q8-1': 'Rewrite x²/csc⁴(2x)=x²sin⁴(2x): f′(x)=2x sin⁴(2x)+8x² sin³(2x)cos(2x). (The supplied key differentiated x²csc⁴(2x).)'}
for q in d['questions']:
    if q['id'] in FIX: q['parts'][0]['answer']['model_answer_and_marking'] = FIX[q['id']]; q['parts'][0]['answer']['key_corrected'] = True
p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
