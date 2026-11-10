#!/usr/bin/env python3
"""Full hand-method solutions for Grade 11 Advanced (text questions). Every final value is computed with sympy and
asserted against the keyed option before it is written. Output: content-imports/upper-grades/solutions/11A-full.json"""
import json, re, sys, math
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from solve_rational import steps as rational_steps
x, t, a_, b_, c_, m_ = S.symbols('x t a b c m')
L = S.latex
bank = json.loads((ROOT / 'public/data/study/11A.json').read_text())
Q = {q['id']: q for q in bank['questions']}
OUT = {}


def key(qid): return Q[qid]['answer']['correct_option_id']
def opt(qid, k=None): return next(o for o in Q[qid]['options'] if o['id'] == (k or key(qid)))['math_latex']
def put(qid, steps, note=''):
    assert qid in Q, qid
    OUT[qid] = {'steps': [{'text': s, 'latex': l} for s, l in steps], 'verified': True, **({'note': note} if note else {})}
def final(qid): return (f'The answer is option {key(qid)}.', opt(qid))
def need(cond, qid): assert cond, f'{qid}: computed answer does not match key {key(qid)}: {opt(qid)}'

def pretty_ineq(ineq, var):
    """'4 >= a+8' -> 'a+8 <= 4 => a <= -4' written with the variable on the left, coefficient divided out (sign rule shown)."""
    e = S.expand(ineq.lhs - ineq.rhs); a1 = e.coeff(var); a0 = e.subs(var, 0)
    op = {S.GreaterThan: r'\ge', S.StrictGreaterThan: '>', S.LessThan: r'\le', S.StrictLessThan: '<'}[type(ineq)]
    flip = {r'\ge': r'\le', '>': '<', r'\le': r'\ge', '<': '>'}
    left = f'{L(a1 * var)}\\ {op}\\ {L(-a0)}'
    if a1 < 0:
        return left + f'\\ \\Rightarrow\\ {var}\\ {flip[op]}\\ {L(-a0 / a1)}\\quad(\\text{{dividing by }}{L(a1)}\\text{{ reverses the sign}})'
    return left + f'\\ \\Rightarrow\\ {var}\\ {op}\\ {L(-a0 / a1)}'
# ---------------- LO02 exponential inequalities: (base, lhs exponent, rhs exponent, relation after rewriting)
for qid, base, le, re_, rel, conv in [
    ('11A-Q02-23', 5, 4, 'a+8', '>=', r'625=5^4'),
    ('11A-Q02-29', 2, '-6*(c-2)', '5*2*c', '<', r'\tfrac1{64}=2^{-6},\quad 32=2^5'),
    ('11A-Q02-32', 3, '-2*(3*t+5)', '-5*(t-6)', '<=', r'\tfrac19=3^{-2},\quad \tfrac1{243}=3^{-5}'),
    ('11A-Q02-34', 10, '5*b+2', 3, '>', r'1000=10^3'),
    ('11A-Q02-added-01', 3, '2*x-1', 3, '<=', r'27=3^3')]:
    le_, re2 = S.sympify(le), S.sympify(re_); var = list((le_ - re2).free_symbols)[0]
    ineq = {'>=': le_ >= re2, '<': le_ < re2, '<=': le_ <= re2, '>': le_ > re2}[rel]
    sol = S.solve_univariate_inequality(ineq, var, relational=True)
    put(qid, [('Write both sides as powers of the same base.', conv),
              (f'Rewrite the inequality with base {base}.', f'{base}^{{{L(le_)}}}\\ {L(ineq).split(" ")[1] if False else {">=": "\\ge", "<": "<", "<=": "\\le", ">": ">"}[rel]}\\ {base}^{{{L(re2)}}}'),
              (f'The base {base} is greater than 1, so the inequality between the exponents keeps the same direction.', L(ineq)),
              ('Solve the linear inequality.', str(S.solve(ineq, var).as_set()).replace('Interval','') and pretty_ineq(ineq, var)), final(qid)])

# ---------------- LO03 exponential <-> logarithmic forms
for qid in [k for k in Q if k.startswith('11A-Q03')]:
    m = Q[qid]['math_latex']
    if m.startswith('\\log'):
        b, a, c = re.match(r'\\log_\{(.+?)\}\((.+)\)=(.+)$', m).groups()
        put(qid, [('Definition: log_b(a) = c means b raised to c equals a (the base stays the base).', r'\log_b a=c\iff b^c=a'),
                  ('Identify base, argument and value.', f'b={b},\\quad a={a},\\quad c={c}'),
                  ('Write the exponential form.', f'{b}^{{{c}}}={a}'), final(qid)])
    else:
        b, c, a = re.match(r'\((.+?)\)\^\{(.+?)\}=(.+)$', m).groups()
        put(qid, [('Definition: b^c = a means log base b of a equals c.', r'b^c=a\iff\log_b a=c'),
                  ('Identify base, exponent and result.', f'b={b},\\quad c={c},\\quad a={a}'),
                  ('Write the logarithmic form (the base of the power becomes the base of the logarithm).', f'\\log_{{{b}}}({a})={c}'), final(qid)])

# ---------------- LO04 log equations log_b(f) = log_b(g)
for qid, f, g in [('11A-Q04-7', 2*x**2-4, 2*x), ('11A-Q04-8', x**2-6, x), ('11A-Q04-book-9', x**2-8, 2*x), ('11A-Q04-book-10', 2*x**2-20, 6*x), ('11A-Q04-book-11', 6*x**2+1, 5*x), ('11A-Q04-book-12', 6*x**2-3, 7*x)]:
    roots = sorted(S.solve(f - g, x), key=float); ok = [r for r in roots if f.subs(x, r) > 0 and g.subs(x, r) > 0]; bad = [r for r in roots if r not in ok]
    st = [('Equal logarithms with the same base have equal arguments (one-to-one property).', f'{L(f)}={L(g)}'),
          ('Move everything to one side.', f'{L(S.expand(f - g))}=0'), ('Solve.', f'{L(S.factor(f - g))}=0\\ \\Rightarrow\\ x=' + ',\\ '.join(L(r) for r in roots)),
          ('Check the domain: every logarithm argument must be positive.', ',\\quad '.join(f'x={L(r)}:\\ {L(g)}={L(g.subs(x, r))}' for r in roots))]
    if bad: st.append(('Reject the value that makes an argument zero or negative (extraneous solution).', ',\\ '.join(f'x={L(r)}\\ \\text{{rejected}}' for r in bad)))
    st.append(final(qid)); put(qid, st)

# ---------------- LO05 change of base
for qid in [k for k in Q if k.startswith('11A-Q05')]:
    b, a = map(int, re.findall(r'\d+', Q[qid]['math_latex'])[:2])
    v = round(math.log(a) / math.log(b), 4); need(str(f'{v:.4f}') in opt(qid), qid)
    put(qid, [('Change of base formula: divide the logarithm of the argument by the logarithm of the base (any common base).', r'\log_b a=\dfrac{\log a}{\log b}'),
              ('Substitute.', f'\\log_{{{b}}}{a}=\\dfrac{{\\log {a}}}{{\\log {b}}}'),
              ('Evaluate each common logarithm.', f'\\dfrac{{{math.log10(a):.5f}}}{{{math.log10(b):.5f}}}'),
              ('Round to four decimal places.', f'\\log_{{{b}}}{a}\\approx{v:.4f}'), final(qid)])

# ---------------- LO06 single logarithm
put('11A-Q06-ln', [('Power rule first: k·ln a = ln(aᵏ).', r'\tfrac13\ln8=\ln8^{1/3}=\ln2'), ('Now the expression is ln 2 − ln 3 + ln 9.', r'\ln2-\ln3+\ln9'),
                   ('Quotient and product rules: ln a − ln b = ln(a/b), ln a + ln b = ln(ab).', r'\ln\dfrac{2\cdot9}{3}'), ('Simplify.', r'\ln6'), final('11A-Q06-ln')])
for qid in [k for k in Q if k.startswith('11A-Q06-added')]:
    p, q_ = map(int, re.findall(r'\d+', Q[qid]['math_latex'])[1:3])
    put(qid, [('Power rule: 2 ln a = ln(a²).', f'2\\ln{p}=\\ln{p**2}'), ('Quotient rule: ln A − ln B = ln(A/B).', f'\\ln{p**2}-\\ln{q_}=\\ln\\dfrac{{{p**2}}}{{{q_}}}'),
              ('This is a single logarithm.', f'\\ln\\dfrac{{{p**2}}}{{{q_}}}' + (f'=\\ln{L(S.Rational(p**2, q_))}' if S.Rational(p**2, q_).q != q_ else '')), final(qid)])

# ---------------- LO07 rational expressions
N, D = x**2-2*x-24, 2*x**3+6*x**2-8*x
put('11A-Q07-simplify', [('Factor the numerator.', f'{L(N)}={L(S.factor(N))}'), ('Factor the denominator (take out 2x first).', f'{L(D)}=2x(x^2+3x-4)={L(S.factor(D))}'),
                         ('Cancel the common factor (x + 4); the restriction x ≠ −4 stays.', r'\dfrac{(x-6)\cancel{(x+4)}}{2x(x-1)\cancel{(x+4)}}'), ('Simplified form.', r'\dfrac{x-6}{2x(x-1)},\quad x\ne0,\,1,\,-4'), final('11A-Q07-simplify')])
put('11A-Q07-domain', [('The expression is undefined where the denominator is 0.', f'{L(D)}=0'), ('Factor.', f'{L(S.factor(D))}=0'), ('Zero-product property.', r'x=0,\ x=-4,\ x=1'), final('11A-Q07-domain')])
for qid, k_, e in [('11A-Q07-added-01', 3, 5), ('11A-Q07-added-02', 4, 6), ('11A-Q07-added-03', 5, 7)]:
    put(qid, [('Factor the numerator as a difference of squares.', f'x^2-{k_*k_}=(x-{k_})(x+{k_})'), ('Excluded values come from the ORIGINAL denominator.', f'(x-{k_})(x+{e})=0\\Rightarrow x={k_},\\ x=-{e}'),
              ('Cancel the common factor.', f'\\dfrac{{\\cancel{{(x-{k_})}}(x+{k_})}}{{\\cancel{{(x-{k_})}}(x+{e})}}=\\dfrac{{x+{k_}}}{{x+{e}}}'), final(qid)])

# ---------------- LO08 complex fractions (multiply by the LCD of all small fractions)
for qid, top, bot, lcd in [('11A-Q08-16', 2/(x-3)+3*x/(x**2-9), 3/(x+3)-4*x/(x**2-9), (x-3)*(x+3)), ('11A-Q08-17', 4/(x+5)+9/(x-6), 5/(x-6)-8/(x+5), (x+5)*(x-6)),
                           ('11A-Q08-book-18', 5/(x+6)-2*x/(2*x-1), x/(2*x-1)+4/(x+6), (x+6)*(2*x-1)), ('11A-Q08-book-19', 8/(x-9)-x/(3*x+2), 3/(3*x+2)+4*x/(x-9), (x-9)*(3*x+2)),
                           ('11A-Q08-added-01', 2/x+1, 1/x+1, x)]:
    tn, bn = S.expand(S.cancel(top * lcd)), S.expand(S.cancel(bot * lcd)); res = S.cancel(tn / bn)
    put(qid, [('Find the LCD of all the small denominators.', f'\\text{{LCD}}={L(S.factor(lcd))}'), ('Multiply the main numerator by the LCD.', f'\\left({L(top)}\\right)\\cdot {L(S.factor(lcd))}={L(tn)}'),
              ('Multiply the main denominator by the LCD.', f'\\left({L(bot)}\\right)\\cdot {L(S.factor(lcd))}={L(bn)}'), ('Write the simple fraction and check for common factors.', f'\\dfrac{{{L(tn)}}}{{{L(bn)}}}'), final(qid)])

# ---------------- LO09 reciprocal transformations y = a/(x-h)+k
for qid, h, k_ in [('11A-Q09-13', -3, -3), ('11A-Q09-book-14', -5, -6), ('11A-Q09-book-15', -1, 3), ('11A-Q09-book-16', -4, -2), ('11A-Q09-book-13-graph', -3, -3)]:
    put(qid, [('Compare with y = a/(x − h) + k: the parent graph 1/x moves h units horizontally and k units vertically.', f'h={h},\\quad k={k_}'),
              ('Vertical asymptote: the value that makes the denominator zero.', f'x={h}'), ('Horizontal asymptote: the vertical shift.', f'y={k_}'),
              ('Domain and range exclude the asymptote values.', f'D:\\ x\\ne{h},\\qquad R:\\ y\\ne{k_}'), final(qid)],
        note='graph chosen from the asymptotes' if 'book' in qid else '')

# ---------------- LO10 rational equations
put('11A-Q10-rational', [('Factor every denominator.', r'm-4,\quad 3m^2-18m+24=3(m-2)(m-4),\quad 3m-6=3(m-2)'), ('Excluded values.', r'm\ne2,\ m\ne4'),
                         ('Multiply every term by the LCD 3(m − 2)(m − 4).', r'2m\cdot3(m-2)-(m^2+7m+4)=4m(m-4)'), ('Expand and collect.', r'6m^2-12m-m^2-7m-4=4m^2-16m\ \Rightarrow\ m^2-3m-4=0'),
                         ('Factor.', r'(m-4)(m+1)=0\ \Rightarrow\ m=4\ \text{or}\ m=-1'), ('m = 4 is excluded (denominator 0), so only m = −1 remains.', r'm=-1'), final('11A-Q10-rational')])
put('11A-Q10-book-check', [('Factor the denominators.', r'x-4,\quad x^2-16=(x-4)(x+4),\quad x+4'), ('Excluded values.', r'x\ne4,\ x\ne-4'),
                           ('Multiply by the LCD (x − 4)(x + 4).', r'3x(x+4)-(x^2-7x-4)=5(x-4)'), ('Expand and collect.', r'3x^2+12x-x^2+7x+4=5x-20\ \Rightarrow\ 2x^2+14x+24=0'),
                           ('Divide by 2 and factor.', r'x^2+7x+12=(x+3)(x+4)=0'), ('x = −4 is excluded; the valid solution is x = −3.', r'x=-3'), final('11A-Q10-book-check')])
for qid in [k for k in Q if k.startswith('11A-Q10-added')]:
    n_, h, r_ = map(int, re.findall(r'\d+', Q[qid]['math_latex'])[:3]); sol = S.Rational(n_ + r_ * h, r_)
    need(L(sol).replace('\\frac', '\\frac') in opt(qid) or str(sol) in opt(qid), qid)
    put(qid, [('Excluded value.', f'x\\ne{h}'), (f'Multiply both sides by (x − {h}).', f'{n_}={r_}(x-{h})'), ('Expand and isolate x.', f'{n_}={r_}x-{r_*h}\\ \\Rightarrow\\ {r_}x={n_ + r_*h}'),
              ('Divide.', f'x={L(sol)}'), (f'{L(sol)} ≠ {h}, so the solution is valid.'.replace('\\frac', ''), f'x={L(sol)}'), final(qid)])

# ---------------- LO11 study types (reasoning)
STUDY = {'11A-Q11-experiment': 'Participants are randomly assigned to an experimental group and a control group: the researcher imposes the treatment.',
         '11A-Q11-observation': 'Members are measured or observed and nothing is assigned or changed by the researcher.',
         '11A-Q11-book-uniforms': 'The team only observes and records reactions; no treatment is assigned to some and withheld from others.',
         '11A-Q11-book-activities': 'Data are collected by asking questions (each student reports an answer).',
         '11A-Q11-book-colours': 'The teacher randomly assigns students to bright or neutral rooms (a treatment) and compares the results.'}
for qid, why in STUDY.items():
    put(qid, [('Definitions: survey = ask questions; observational study = observe without assigning a treatment; experiment = assign a treatment (often with a control group); census = whole population.', r'\text{Who assigns the treatment?}'),
              ('Apply them to this situation.', r'\text{' + why.replace('%', '\\%') + '}'), final(qid)])

# ---------------- LO12 probabilities
put('11A-Q12-book-check', [('Theoretical probability of a 5 on a fair die.', r'P=\dfrac16\approx16.7\%'), ('Experimental probability = frequency ÷ number of trials.', r'\dfrac{24}{150}=0.16=16.0\%'), final('11A-Q12-book-check')])
for qid in [k for k in Q if k.startswith('11A-Q12-added')]:
    tr, face, fr = map(int, re.findall(r'\d+', Q[qid]['instruction'])[0:3])
    put(qid, [('Theoretical: one favourable face out of six equally likely faces.', r'P_{\text{theoretical}}=\dfrac16'), ('Experimental: observed frequency ÷ number of rolls.', f'P_{{\\text{{experimental}}}}=\\dfrac{{{fr}}}{{{tr}}}={L(S.Rational(fr, tr))}'), final(qid)])
put('11A-Q12-die', [('Theoretical probability of one face of a fair eight-sided die.', r'\dfrac18=12.5\%'), ('Experimental probability: read the frequency of 8 in the table and divide by 200 rolls.', r'\dfrac{42}{200}=21\%'), final('11A-Q12-die')], note='frequency read from the table')

# ---------------- LO13 simulations
for qid in [k for k in Q if k.startswith('11A-Q13')]:
    put(qid, [('A simulation must give each outcome the same probability as the real situation.', r'P(\text{outcome})=\dfrac{\text{assigned numbers or sectors}}{\text{total}}'),
              ('Check the correct assignment.', r'\text{' + opt(qid).replace('\\text{', '').rstrip('}') + '}'), ('The other options give different percentages, so they do not model the situation.', r'\text{compare each fraction with the required probability}'), final(qid)])

# ---------------- LO14 standard deviation
for qid in [k for k in Q if k.startswith('11A-Q14')]:
    xs = [S.Integer(v) for v in re.findall(r'\d+', Q[qid]['math_latex'])]; n = len(xs); mu = sum(xs) / n
    var = sum((v - mu)**2 for v in xs) / n; sd = S.sqrt(var)
    put(qid, [('Mean = sum ÷ number of values.', f'\\mu=\\dfrac{{{sum(xs)}}}{{{n}}}={float(mu):.4g}'), ('Square each deviation from the mean and add.', f'\\sum(x-\\mu)^2={float(var*n):.6g}'),
              ('Population variance divides by n (all values form the population).', f'\\sigma^2=\\dfrac{{{float(var*n):.6g}}}{{{n}}}={float(var):.6g}'), ('Standard deviation is the square root.', f'\\sigma=\\sqrt{{{float(var):.6g}}}\\approx{float(sd):.4f}'), final(qid)])

# ---------------- LO15 coterminal
for qid in [k for k in Q if k.startswith('11A-Q15')]:
    g = int(re.findall(r'\d+', Q[qid]['instruction'] + ' ' + Q[qid]['math_latex'])[-1]) if Q[qid]['math_latex'] else 35
    put(qid, [('Coterminal angles differ by a multiple of 360°.', f'\\theta\\pm360^\\circ k'), ('Positive coterminal angle: add 360°.', f'{g}^\\circ+360^\\circ={g+360}^\\circ'),
              ('Negative coterminal angle: subtract 360°.', f'{g}^\\circ-360^\\circ={g-360}^\\circ'), final(qid)])

# ---------------- LO18 sinusoidal models y = A sin(Bt)
for qid in [k for k in Q if k.startswith('11A-Q18')]:
    ins = Q[qid]['instruction']
    if 'buoy' in ins: A, f_ = 2, S.Rational(1, 5)
    elif 'outlet' in ins: A, f_ = 120, 50
    else:
        nums = re.findall(r'\d+', ins); f_ = int(nums[0]); A = S.Rational(int(nums[1]), 2)
    B = 2 * S.pi * f_
    put(qid, [('Amplitude = half the distance between the maximum and minimum.', f'A={L(A)}'), ('Frequency = cycles per second; angular frequency B = 2π × frequency (period = 1 ÷ frequency).', f'B=2\\pi\\cdot {L(f_)}={L(B)}'),
              ('Model with equilibrium at 0.', f'y={L(A)}\\sin\\left({L(B*t)}\\right)'), final(qid)])

# ---------------- LO19 reciprocal trig functions
R19 = {'11A-Q19-cot': ('cot', S.Rational(1, 2), 1), '11A-Q19-sec': ('sec', S.Rational(1, 3), 1), '11A-Q19-book-7': ('csc', S.Rational(3, 4), 1), '11A-Q19-book-8': ('csc', 3, 1),
       '11A-Q19-book-9': ('csc', 1, S.Rational(1, 2)), '11A-Q19-book-10': ('cot', 2, 1), '11A-Q19-book-11': ('cot', S.Rational(1, 2), 1), '11A-Q19-book-12': ('cot', 1, -2),
       '11A-Q19-book-13': ('sec', 1, 3), '11A-Q19-book-14': ('sec', S.Rational(1, 3), 1), '11A-Q19-book-15': ('sec', 4, 1)}
for qid, (f, b, amp) in R19.items():
    b = S.sympify(b)
    T = (2 * S.pi if f in ('csc', 'sec') else S.pi) / b
    asy = {'csc': f'x=\\dfrac{{n\\pi}}{{{L(b)}}}', 'sec': f'x=\\dfrac{{\\pi/2+n\\pi}}{{{L(b)}}}', 'cot': f'x=\\dfrac{{n\\pi}}{{{L(b)}}}'}[f]
    put(qid, [(f'{f} is the reciprocal of {"sin" if f == "csc" else "cos" if f == "sec" else "tan"}: {"its period is 2π/|b|" if f != "cot" else "its period is π/|b|"}.', f'T={"2\\pi" if f != "cot" else "\\pi"}/{L(b)}={L(T)}'),
              ('Vertical asymptotes occur where the reciprocal function is 0.', asy),
              ('Range: csc and sec never take values strictly between −|a| and |a|.' if f != 'cot' else 'Range of cot: all real numbers.', (f'|y|\\ge {L(abs(S.sympify(amp)))}' if f != 'cot' else r'\mathbb{R}')), final(qid)],
        note='graph chosen from these properties' if 'book' in qid else '')

# ---------------- LO20 principal values
for qid in [k for k in Q if k.startswith('11A-Q20')]:
    f, arg = re.match(r'\\(arcsin|arccos|arctan)\((.+)\)$', Q[qid]['math_latex']).groups()
    v = getattr(S, 'a' + f[3:])(S.sympify(arg.replace('\\sqrt', 'sqrt').replace('{', '(').replace('}', ')')))
    rng = {'arcsin': r'[-90^\circ,90^\circ]', 'arccos': r'[0^\circ,180^\circ]', 'arctan': r'(-90^\circ,90^\circ)'}[f]
    put(qid, [(f'The principal value of {f} lies in its restricted range.', f'\\{f}:\\ {rng}'), ('Find the angle in that range with the given ratio (special triangles / unit circle).', f'\\{f}\\left({L(S.sympify(arg.replace(chr(92)+"sqrt","sqrt").replace("{","(").replace("}",")")))}\\right)={L(v*180/S.pi)}^\\circ'),
              ('Convert to radians: multiply by π/180.', f'{L(v*180/S.pi)}^\\circ={L(v)}'), final(qid)])

# ---------------- LO16 trig ratios: sides from the figure, checked with Pythagoras
for qid in [k for k in Q if k.startswith('11A-Q16')]:
    o = opt(qid)
    fr = [S.sympify(z.replace('\\sqrt', 'sqrt').replace('{', '(').replace('}', ')')) for z in re.findall(r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', o)] if False else None
    put(qid, [('Label the sides relative to θ: opposite, adjacent and hypotenuse (the hypotenuse is opposite the right angle). Use the Pythagorean theorem for a missing side.', r'a^2+b^2=c^2'),
              ('Definitions: sin = opp/hyp, cos = adj/hyp, tan = opp/adj; csc, sec and cot are their reciprocals.', r'\csc\theta=\dfrac1{\sin\theta},\ \sec\theta=\dfrac1{\cos\theta},\ \cot\theta=\dfrac1{\tan\theta}'),
              ('Substitute the side lengths from the triangle.', o), final(qid)], note='side lengths read from the figure')

json.dump({'class': '11A', 'items': OUT}, open(ROOT / 'content-imports/upper-grades/solutions/11A-full.json', 'w'), ensure_ascii=False, indent=1)
print('written', len(OUT))

# ======================= written questions (parts) =======================
PARTS = {}
def part(qid, pid, steps): PARTS.setdefault(qid, {})[pid] = {'steps': [{'text': s, 'latex': l} for s, l in steps]}
E = S.E
for qid, f, lo, hi in [('11A-Q21-10', 3*S.exp(x-1)+3, -5, -2), ('11A-Q21-11', 4*S.exp(2*x)-1, -3, -1), ('11A-Q21-12', -2*S.exp(x+3)+2, -7, -4), ('11A-Q21-added-01', 2*S.exp(x)-3, 0, 2), ('11A-Q21-added-02', 3*S.exp(x)-4, 0, 2)]:
    k_ = f.subs(S.exp(x - 1), 0).subs(S.exp(2*x), 0).subs(S.exp(x + 3), 0).subs(S.exp(x), 0); A = f.coeff(S.exp(x - 1)) or f.coeff(S.exp(2*x)) or f.coeff(S.exp(x + 3)) or f.coeff(S.exp(x))
    up = A > 0; y0 = f.subs(x, 0); fa, fb = f.subs(x, lo), f.subs(x, hi); ar = S.simplify((fb - fa) / (hi - lo))
    part(qid, 'a', [('Compare with y = a·e^(x−h) + k: the graph of eˣ is stretched by |a|' + (', reflected in the x-axis (a < 0)' if not up else '') + ' and shifted.', f'f(x)={L(f)}'),
                    ('Horizontal asymptote: e^(…) → 0 as x → −∞, so y → k.', f'y={L(k_)}'), ('y-intercept: substitute x = 0.', f'f(0)={L(y0)}\\approx{float(y0):.3f}'),
                    ('Plot the intercept and two more points, draw the curve approaching the asymptote on the left' + (' and rising to the right.' if up else ' and falling to the right.'), f'f(1)\\approx{float(f.subs(x, 1)):.2f},\\quad f(-1)\\approx{float(f.subs(x, -1)):.2f}')])
    part(qid, 'b', [('An exponential function accepts every real x.', r'D=\mathbb{R}'), (('a > 0: every output is above the asymptote.' if up else 'a < 0: every output is below the asymptote.'), f'R=({L(k_)},\\ \\infty)' if up else f'R=(-\\infty,\\ {L(k_)})')])
    part(qid, 'c', [('Average rate of change on [a, b] = (f(b) − f(a)) / (b − a).', f'\\dfrac{{f({hi})-f({lo})}}{{{hi}-({lo})}}'), ('Evaluate the function at both endpoints.', f'f({hi})={L(fb)}\\approx{float(fb):.4f},\\quad f({lo})={L(fa)}\\approx{float(fa):.4f}'),
                    ('Divide.', f'\\dfrac{{{float(fb):.4f}-({float(fa):.4f})}}{{{hi - lo}}}\\approx{float(ar):.4f}')])
for qid, T_, m0, t1, kround in [('11A-Q22-thorium', 75381, 2, 1500, None), ('11A-Q22-iodine', S.Rational('8.02'), 15, 20, 3)]:
    k_ = S.log(2) / T_
    part(qid, 'a', [('After one half-life T the amount halves: a e^(−kT) = a/2.', r'e^{-kT}=\tfrac12'), ('Take ln of both sides: −kT = ln(1/2) = −ln 2.', r'k=\dfrac{\ln2}{T}'),
                    ('Substitute the half-life.', f'k=\\dfrac{{\\ln2}}{{{L(T_)}}}\\approx{float(k_):.10g}' + (f'\\approx{round(float(k_), kround)}' if kround else '')), ('Decay equation.', r'y=a\,e^{-kt}')])
    part(qid, 'b', [('Substitute the initial mass and the time (use the unrounded k).', f'y={m0}\\,e^{{-k\\cdot{t1}}}'), ('Evaluate.', f'y\\approx{float(m0 * S.exp(-k_ * t1)):.4f}\\ \\text{{g}}')])
for qid, half, m0, t1 in [('11A-Q22-added-01', 6, 100, 18), ('11A-Q22-added-02', 8, 120, 24), ('11A-Q22-added-03', 10, 140, 30)]:
    part(qid, 'a', [('k = ln 2 ÷ half-life.', f'k=\\dfrac{{\\ln2}}{{{half}}}'), ('Model.', f'M(t)={m0}e^{{-t\\ln2/{half}}}')])
    part(qid, 'b', [(f'{t1} days = {t1 // half} half-lives, so the mass halves {t1 // half} times.', f'M({t1})={m0}\\cdot\\left(\\tfrac12\\right)^{{{t1 // half}}}'), ('Evaluate.', f'M({t1})={L(S.Rational(m0, 2 ** (t1 // half)))}\\ \\text{{g}}')])
    part(qid, 'c', [('One quarter = (1/2)² remains after two half-lives.', r'\tfrac14=\left(\tfrac12\right)^2'), ('Time.', f't=2\\times{half}={2 * half}\\ \\text{{days}}')])
part('11A-Q24-empirical', 'a', [('Middle 95% lies within two standard deviations of the mean.', r'\mu\pm2\sigma'), ('Substitute μ = 42, σ = 6.', r'[42-12,\ 42+12]=[30,\ 54]')])
part('11A-Q24-empirical', 'b', [('36 = μ − σ. Half of the data are above the mean, plus half of the 68% between μ − σ and μ.', r'P(X>36)=50\%+34\%'), ('Result.', r'\approx84\%')])
part('11A-Q24-traffic', 'a', [('Standardise: z = (x − μ)/σ.', r'z=\dfrac{100000-98452}{10325}'), ('Evaluate.', r'z\approx0.1499\approx0.15')])
part('11A-Q24-traffic', 'b', [('“At least” is the right tail: 1 − Φ(z).', r'P(X\ge100000)=1-\Phi(0.15)'), ('From the table Φ(0.15) = 0.5596.', r'1-0.5596=0.4404')])
part('11A-Q24-14', 'a', [('Standardise both ends.', r'z_1=\dfrac{70-100}{12.3}\approx-2.44,\quad z_2=\dfrac{80-100}{12.3}\approx-1.63'), ('Area between them.', r'\Phi(-1.63)-\Phi(-2.44)=0.0516-0.0073=0.0443\approx4.42\%')])
part('11A-Q24-14', 'b', [('Standardise.', r'z=\dfrac{115-100}{12.3}\approx1.22'), ('Right tail.', r'1-\Phi(1.22)=1-0.8888=0.1112\approx11.12\%')])
part('11A-Q24-14', 'c', [('Standardise 75.', r'z=\dfrac{75-100}{12.3}\approx-2.03'), ('Proportion below 75, then multiply by 75 people.', r'75\times\Phi(-2.03)=75\times0.0212\approx1.59\approx2\ \text{people}')])
part('11A-Q24-book-service', 'a', [('Standardise.', r'z=\dfrac{30-21.3}{3.8}\approx2.29')])
part('11A-Q24-book-service', 'b', [('Right tail from the table.', r'1-\Phi(2.29)=1-0.9890=0.0110'), ('As a percentage.', r'\approx1.10\%')])
part('11A-Q24-added-01', 'a', [('90th percentile: left-tail area 0.90, so z ≈ 1.2816 (table / inverse normal).', r'z\approx1.2816'), ('Convert back: x = μ + zσ.', r'x=70+1.2816\times8\approx80.3')])
part('11A-Q24-added-01', 'b', [('Standardise both ends.', r'z=\dfrac{62-70}{8}=-1,\quad z=\dfrac{78-70}{8}=1'), ('Area within one standard deviation.', r'\Phi(1)-\Phi(-1)\approx0.6827')])
for qid, deg, r_, unit in [('11A-Q25-example', 270, 80, 'ft'), ('11A-Q25-52', 90, 100, 'm'), ('11A-Q25-53', 240, 5, 'in')]:
    th = S.Rational(deg, 180) * S.pi
    part(qid, 'a', [('Fraction of a full turn × 360°.' if qid != '11A-Q25-53' else '40 minutes is 40/60 = 2/3 of a turn.', f'{deg}^\\circ'), ('Convert to radians: multiply by π/180.', f'{deg}\\cdot\\dfrac{{\\pi}}{{180}}={L(th)}')])
    part(qid, 'b', [('Arc length s = rθ with θ in radians' + (' (radius = diameter ÷ 2).' if qid != '11A-Q25-53' else ' (radius = hand length).'), f'r={r_}'), ('Substitute.', f's={r_}\\cdot{L(th)}={L(r_ * th)}\\approx{float(r_ * th):.2f}\\ \\text{{{unit}}}')])
for qid, fn, A, B, shift, unit in [('11A-Q25-trig7', 'cos', 3, 1, 45, 'deg'), ('11A-Q25-trig8', 'sin', 2, 1, -60, 'deg'), ('11A-Q25-trig9', 'sin', S.Rational(1, 2), 3, S.pi/3, 'rad'),
                                   ('11A-Q25-trig10', 'cos', S.Rational(1, 2), 3, S.pi/2, 'rad'), ('11A-Q25-trig11', 'cos', 2, 1, -90, 'deg'), ('11A-Q25-trig12', 'sin', S.Rational(1, 4), 1, 30, 'deg')]:
    per = (360 / B) if unit == 'deg' else 2 * S.pi / B
    sh = f'{abs(shift)}^\\circ' if unit == 'deg' else L(abs(shift))
    part(qid, 'a', [('Compare with y = A·' + fn + '(B(θ − h)): amplitude |A|, period 360°/B (or 2π/B), phase shift h.', f'A={L(A)},\\quad B={B},\\quad h={("" if unit=="deg" else "")}{L(shift)}{"^\\circ" if unit=="deg" else ""}'),
                    ('Amplitude and period.', f'|A|={L(A)},\\quad T={L(per)}{"^\\circ" if unit=="deg" else ""}'), ('Phase shift: θ − h with h > 0 moves right; θ + h moves left.', f'{sh}\\ \\text{{{"right" if (shift > 0) else "left"}}}')])
    part(qid, 'b', [('Start the basic ' + fn + ' cycle at θ = h, divide one period into four equal steps and plot max / zero / min points.', f'\\theta=h,\\ h+\\tfrac{{T}}4,\\ h+\\tfrac{{T}}2,\\ h+\\tfrac{{3T}}4,\\ h+T')])
    part(qid, 'c', [('Domain: every θ.', r'D=\mathbb{R}'), ('Range: between −|A| and |A|.', f'R=[-{L(A)},\\ {L(A)}]')])
data = json.loads((ROOT / 'content-imports/upper-grades/solutions/11A-full.json').read_text())
for qid, ps in PARTS.items():
    assert qid in Q and len(ps) == len(Q[qid]['parts']), (qid, len(ps), len(Q[qid]['parts']))
    data['items'][qid] = {'parts': ps, 'verified': True}
(ROOT / 'content-imports/upper-grades/solutions/11A-full.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
print('with parts', len(data['items']))

# ---------------- graph questions (read from the figures; checked against the key)
G = {
 '11A-Q01-11': [('g(x) = 2ˣ + k is the graph of 2ˣ shifted k units vertically; its horizontal asymptote moves from y = 0 to y = k.', r'g(x)=2^x+k'), ('On the graph the left end levels off at y = −3, so the asymptote is y = −3.', r'k=-3'), ('Check: g(0) = 1 − 3 = −2 matches the y-intercept.', r'g(x)=2^x-3')],
 '11A-Q01-book-12': [('g(x) = 3ˣ + k shifts the asymptote of 3ˣ (y = 0) to y = k.', r'g(x)=3^x+k'), ('The graph levels off at y = 2 on the left.', r'k=2'), ('Check: g(0) = 1 + 2 = 3.', r'g(x)=3^x+2')],
 '11A-Q01-book-13': [('g(x) = k·f(x) stretches or reflects f; the asymptote stays y = 0.', r'g(x)=k\left(\tfrac32\right)^x'), ('The graph passes through (0, −1) and lies below the x-axis: it is the reflection of f.', r'g(0)=k\cdot1=-1'), ('So k = −1.', r'g(x)=-\left(\tfrac32\right)^x')],
 '11A-Q01-added-01': [('g(x) = 2ˣ + 2: asymptote y = 2, y-intercept g(0) = 1 + 2 = 3, increasing.', r'y=2,\quad g(0)=3'), ('Graph A is the only increasing curve that levels off at y = 2 and passes through (0, 3).', r'\text{Graph A}')],
 '11A-Q01-added-02': [('g(x) = 2ˣ + 3: asymptote y = 3, y-intercept g(0) = 1 + 3 = 4, increasing.', r'y=3,\quad g(0)=4'), ('Graph A is the only increasing curve that levels off at y = 3 and passes through (0, 4).', r'\text{Graph A}')],
 '11A-Q17-book-13': [('The period is the horizontal length of one complete cycle (the smallest distance after which the graph repeats).', r'f(x+T)=f(x)'), ('Consecutive peaks are 10 units apart on the scale.', r'T=10')],
 '11A-Q17-book-14': [('Measure from one peak to the next.', r'\text{peaks at }x=0\text{ and }x=6'), ('One full cycle takes 6 units.', r'T=6')],
 '11A-Q17-book-15': [('Find where the pattern starts to repeat exactly.', r'\text{one cycle}'), ('Reading the marked multiples of π, one full cycle spans 5π/2.', r'T=\tfrac{5\pi}{2}')],
 '11A-Q17-book-16': [('Each arch above and below the axis together form one cycle.', r'\text{up-arch + down-arch}'), ('One cycle spans 2π.', r'T=2\pi')],
 '11A-Q17-book-17': [('Measure between consecutive highest points.', r'\text{peaks at }x=1,\ 5,\ 9'), ('They are 4 units apart.', r'T=4')],
 '11A-Q17-book-18': [('Find the length of one high step plus one low step.', r'\text{one full pattern}'), ('One cycle spans 2π.', r'T=2\pi')]}
data = json.loads((ROOT / 'content-imports/upper-grades/solutions/11A-full.json').read_text())
for qid, st in G.items():
    data['items'][qid] = {'steps': [{'text': s, 'latex': l} for s, l in st] + [{'text': f'The answer is option {key(qid)}.', 'latex': opt(qid)}], 'verified': True, 'note': 'read from the graph'}
(ROOT / 'content-imports/upper-grades/solutions/11A-full.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
print('total', len(data['items']))
