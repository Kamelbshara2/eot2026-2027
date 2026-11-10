#!/usr/bin/env python3
"""Author auto-checked fill-in solution spaces for the text-based written (FRQ) questions of Grades 11 and 12.

Every blank answer is computed with sympy from the question's own numbers (or asserted against the teacher key in the bank),
so the checker never accepts or rejects a value that was typed by hand. Parts that need a drawing or an explanation stay
paper-only (reference solution shown). Blank syntax: lib/study-fill.js. Run after scripts/import-upper-grades.py.
"""
import json, math
from pathlib import Path
import sympy as S

ROOT = Path(__file__).resolve().parent.parent
x, n = S.symbols('x n')
YN = lambda a: f'[[?Yes;No|{a}]]'


def tol(v, t): return f'[[~{t}:{v}]]'
def r(v, d=4): return float(round(S.N(v, 12), d))


SPEC = {}   # question id -> list of part specs {lines|table|None, prompt?}


def put(qid, *parts): SPEC[qid] = list(parts)
def L(*lines, prompt=None, table=None): return {'lines': list(lines), 'prompt': prompt, 'table': table}
PAPER = {'lines': None, 'prompt': None, 'table': None}
def paper(prompt=None): return {'lines': None, 'prompt': prompt, 'table': None}

# ------------------------------------------------------------------ 11G
put('11G-p20-22d', L(r'\dfrac{MN}{MP}=[[3/4]]', r'\dfrac{MR}{MQ}=[[21/31]]', r'\text{Is } NR\parallel PQ\,?\ ' + YN('No')))
put('11G-p23-25b', L(r'P(\text{defective chip from Box A})=[[1/25|0.04]]', r'P(\text{both defective, with replacement})=[[1/625|0.0016]]', r'\text{Is the claim } \tfrac{1}{125} \text{ correct?}\ ' + YN('No')))
put('11G-book-p403-Q18', L(r'150\times0.02=[[3]]', prompt='Number of defective chips in Box B'),
    L(r'P=\dfrac{3}{150}\cdot\dfrac{[[2]]}{[[149]]}=' + tol('1/3725', 0.000001), r'\text{The draws are } [[?dependent;independent|dependent]]', prompt='Probability and explanation'))
put('11G-book-p403-Q19', L(r'\left(\dfrac{4}{100}\right)^2=[[1/625]]', prompt='Compare with replacement'), L(r'\dfrac{4}{100}\cdot\dfrac{3}{99}=[[1/825]]', prompt='Compare without replacement'),
    L(r'\text{Did Sunita replace the first chip?}\ ' + YN('Yes'), prompt='Conclusion'))
put('11G-Q21-added-01', L(r'\dfrac{6}{15}=\dfrac{x+1}{20}\ \Rightarrow\ x+1=[[8]]\ \Rightarrow\ x=[[7]]', prompt='Proportion and x'), L(r'\text{Scale factor ABCD}\to\text{EFGH}=[[5/2|2.5]]', prompt='Scale factor'))
put('11G-Q22-added-01', L(r'\dfrac{AD}{DB}=[[2/3]],\quad \dfrac{AE}{EC}=[[2/3]]', prompt='Compare ratios'), L(r'DE\parallel BC\,?\ ' + YN('Yes'), prompt='Conclusion with reason'))
for qid, h, ang in [('11G-Q23-added-01', 12, 35), ('11G-Q23-added-02', 14, 40)]:
    a, b = h * math.sin(math.radians(ang)), h * math.cos(math.radians(ang))
    put(qid, L(rf'\text{{Leg opposite }}{ang}^\circ=' + tol(round(a, 2), 0.011) + r'\text{ cm}', rf'\text{{Leg adjacent to }}{ang}^\circ=' + tol(round(b, 2), 0.011) + r'\text{ cm}', prompt='Two legs'),
        L(r'P=' + tol(round(h + a + b, 2), 0.011) + r'\text{ cm}', prompt='Perimeter'), L(r'A=' + tol(round(a * b / 2, 2), 0.011) + r'\text{ cm}^2', prompt='Area'))
for qid, ang, d in [('11G-Q24-added-01', 35, 35), ('11G-Q24-added-02', 40, 40), ('11G-Q24-added-03', 45, 45)]:
    h = d * math.tan(math.radians(ang)) + 1.6
    put(qid, L(rf'\tan {ang}^\circ=\dfrac{{h-[[1.6]]}}{{[[{d}]]}}', prompt='Equation'), L(r'h=' + tol(round(h, 1), 0.06) + r'\text{ m}', prompt='Height'))
for qid, red, blue in [('11G-Q25-added-01', 4, 6), ('11G-Q25-added-02', 5, 7), ('11G-Q25-added-03', 6, 8)]:
    t = red + blue
    put(qid, L(r'\text{Without replacement the draws are }[[?dependent;independent|dependent]]', prompt='Dependence'),
        L(rf'P(\text{{both red}})=\dfrac{{{red}}}{{{t}}}\cdot\dfrac{{{red-1}}}{{{t-1}}}=[[{S.Rational(red*(red-1), t*(t-1))}]]', prompt='Without replacement'),
        L(rf'P(\text{{both red}})=\left(\dfrac{{{red}}}{{{t}}}\right)^2=[[{S.Rational(red*red, t*t)}]]', prompt='With replacement'))
for qid, N, art, mus, both in [('11G-Q26-added-01', 35, 13, 16, 6), ('11G-Q26-added-02', 40, 14, 17, 7)]:
    u = art + mus - both
    put(qid, L(rf'P(\text{{art or music}})=\dfrac{{{art}+{mus}-{both}}}{{{N}}}=[[{S.Rational(u, N)}]]', prompt='Union'), L(rf'P(\text{{neither}})=1-\dfrac{{{u}}}{{{N}}}=[[{S.Rational(N-u, N)}]]', prompt='Complement'),
        L(rf'P(\text{{art and music}})=[[{S.Rational(both, N)}]],\ \text{{so the events are mutually exclusive?}}\ ' + YN('No'), prompt='Explain overlap'))

put('11G-book-p403-Q20', L(r'P(D\cup F)=1-0.1=[[0.9]]', r'P(F)=P(D\cup F)-P(D)+P(D\cap F)=[[0.5]]', prompt='(a) Probability of flying'), L(r'P(F\mid D)=\dfrac{P(D\cap F)}{P(D)}=\dfrac{0.2}{0.6}=[[1/3]]', prompt='(b) Conditional probability of flying given driving'))

# ------------------------------------------------------------------ 11A
def expgraph(qid, fexpr, asym, lo, hi, rng):
    f = lambda v: fexpr.subs(x, v)
    ar = S.N((f(hi) - f(lo)) / (hi - lo), 10)
    choices = {'up': f'({asym}, ∞)', 'down': f'(−∞, {asym})'}
    rng_txt = choices[rng]
    put(qid, L(rf'\text{{Horizontal asymptote: }}y=[[{asym}]]', rf'\text{{y-intercept: }}f(0)=' + tol(r(f(0), 3), 0.01), prompt='Graph: key features to read from your sketch'),
        L(r'\text{Domain: }[[?ℝ;(0, ∞);[0, ∞);(−∞, 0)|ℝ]]', rf'\text{{Range: }}[[?{choices["up"]};{choices["down"]};ℝ;[{asym}, ∞)|{rng_txt}]]', prompt='Domain and range'),
        L(rf'\dfrac{{f({hi})-f({lo})}}{{{hi}-({lo})}}=' + tol(r(ar, 4), 0.001), prompt='Average rate of change'))
E = S.E
expgraph('11A-Q21-10', 3 * S.exp(x - 1) + 3, 3, -5, -2, 'up')
expgraph('11A-Q21-11', 4 * S.exp(2 * x) - 1, -1, -3, -1, 'up')
expgraph('11A-Q21-12', -2 * S.exp(x + 3) + 2, 2, -7, -4, 'down')
expgraph('11A-Q21-added-01', 2 * S.exp(x) - 3, -3, 0, 2, 'up')
expgraph('11A-Q21-added-02', 3 * S.exp(x) - 4, -4, 0, 2, 'up')

k = S.log(2) / 75381
put('11A-Q22-thorium', L(r'k=\dfrac{\ln 2}{75381}=' + tol(r(k, 10), 0.0000000005) + r'\ \text{per year}', prompt='Decay constant and model'),
    L(r'\text{Mass after 1500 years}=' + tol(r(2 * S.exp(-k * 1500), 2), 0.01) + r'\text{ g}', prompt='Remaining mass'))
k2 = S.log(2) / S.Rational('8.02')
put('11A-Q22-iodine', L(r'k=\dfrac{\ln 2}{8.02}\approx' + tol(r(k2, 3), 0.0006), r'y=a\,e^{-kt}', prompt='Decay equation'),
    L(r'\text{Mass after 20 days}=' + tol(r(15 * S.exp(-k2 * 20), 2), 0.01) + r'\text{ g}', prompt='Remaining mass'))
for qid, half, m0, t1 in [('11A-Q22-added-01', 6, 100, 18), ('11A-Q22-added-02', 8, 120, 24), ('11A-Q22-added-03', 10, 140, 30)]:
    put(qid, L(rf'k=\dfrac{{\ln 2}}{{[[{half}]]}},\qquad M(t)=[[{m0}]]\,e^{{-kt}}', prompt='Decay model'),
        L(rf'M({t1})=[[{S.Rational(m0, 2 ** (t1 // half))}]]\text{{ g}}', prompt='Remaining mass'), L(rf'\text{{Quarter remains after }}[[{2 * half}]]\text{{ days}}', prompt='Time for a fraction'))


def rational(qid, num, den, hole=None):
    f = S.cancel(num / den); q, rem = S.div(S.Poly(num, x), S.Poly(den, x))
    va = S.solve(den, x); zeros = [z for z in S.solve(num, x) if z not in va]
    slant = q.as_expr()
    y0 = S.nsimplify(num.subs(x, 0) / den.subs(x, 0)) if den.subs(x, 0) != 0 else None
    lines_z = [r'\text{Number of real zeros: }[[' + str(len(zeros)) + ']]'] if not zeros else [rf'x=[[{S.nsimplify(z)}' + ('#z' if len(zeros) > 1 else '') + ']]' for z in zeros]
    zl = r',\ '.join(lines_z) if zeros else lines_z[0]
    asym = [r'\text{Vertical asymptote: }x=[[' + str(va[0]) + ']]', r'\text{Slant asymptote: }y=[[' + str(S.simplify(slant)).replace('**', '^').replace('*', '') + ']]', r'\text{Is there a hole?}\ ' + YN('No')]
    if y0 is not None: asym.append(r'\text{y-intercept: }f(0)=[[' + str(y0) + ']]')
    put(qid, L(zl, prompt='Zeros'), L(*asym, prompt='Asymptotes and excluded points'), paper('Graph (sketch on paper using the zeros, asymptotes and intercept)'))


rational('11A-Q23-example', x**2 + 2 * x + 1, x + 4); rational('11A-Q23-11', (x - 4)**2, x + 2); rational('11A-Q23-12', (x + 3)**2, x - 5)
rational('11A-Q23-13', 6 * x**2 + 4 * x + 2, x + 2); rational('11A-Q23-14', 2 * x**2 + 7 * x, x - 2); rational('11A-Q23-15', 3 * x**2 + 8, 2 * x - 1); rational('11A-Q23-16', 2 * x**2 + 5, 3 * x + 4)
put('11A-Q23-hole', L(r'\text{Excluded values: } x=[[-4#e]],\ [[0#e]],\ [[1#e]]', r'\text{Hole at }\left(-4,\,[[-1/4]]\right)', prompt='Domain and hole'),
    L(r'\text{Zero: }x=[[6]]', r'\text{Vertical asymptotes: }x=[[0#v]],\ x=[[1#v]]', r'\text{Horizontal asymptote: }y=[[0]]', prompt='Zeros and asymptotes'), paper('Graph'))
put('11A-Q24-empirical', L(r'\text{Middle 95\%: }\left[ [[30]],\ [[54]]\right]', prompt='Middle 95%'), L(r'P(X>36)\approx' + tol(84, 0.5) + r'\%', prompt='Percentage above 36'))
put('11A-Q24-traffic', L(r'z=\dfrac{100000-98452}{10325}=' + tol(0.15, 0.006), prompt='Standardize'), L(r'P(X\ge100000)=' + tol(0.4404, 0.002), prompt='Find tail probability'))
put('11A-Q24-14', L(r'\text{Between 70 and 80: }' + tol(4.42, 0.2) + r'\%', prompt='Between 70 and 80'), L(r'\text{Over 115: }' + tol(11.12, 0.2) + r'\%', prompt='Over 115'), L(r'\text{Expected number below 75: }' + tol(1.59, 0.5), prompt='Expected number below 75'))
put('11A-Q24-book-service', L(r'z=\dfrac{30-21.3}{3.8}=' + tol(2.29, 0.01), prompt='Standardize'), L(r'P(X>30)=' + tol(1.10, 0.05) + r'\%', prompt='Upper-tail percentage'))
put('11A-Q24-added-01', L(r'x=70+8z\approx' + tol(80.3, 0.1), prompt='Inverse normal value'), L(r'P(62<X<78)=' + tol(0.6827, 0.002), prompt='Interval probability'))
put('11A-Q25-example', L(r'\text{Angle: }[[270]]^\circ=[[3\pi/2]]\text{ rad}', prompt='Angle conversion'), L(r'r=[[80]],\quad s=r\theta=' + tol(round(120 * math.pi, 2), 0.02) + r'\text{ ft}', prompt='Arc length'))
put('11A-Q25-52', L(r'\text{Angle: }[[90]]^\circ=[[\pi/2]]\text{ rad}', prompt='Angle conversion'), L(r'r=[[100]],\quad s=r\theta=' + tol(round(50 * math.pi, 2), 0.02) + r'\text{ m}', prompt='Arc length'))
put('11A-Q25-53', L(r'\text{Rotation: }[[240]]^\circ=[[4\pi/3]]\text{ rad}', prompt='Angle conversion'), L(r's=r\theta=' + tol(round(20 * math.pi / 3, 2), 0.02) + r'\text{ in}', prompt='Arc length'))
def trig(qid, amp, period, shift, direction, rng):
    put(qid, L(rf'\text{{Amplitude}}=[[{amp}]],\ \ \text{{period}}=[[{period}]],\ \ \text{{shift}}=[[{shift}]]\ [[?left;right|{direction}]]', prompt='Amplitude, period and phase shift'), paper('Graph one full period'),
        L(r'\text{Domain: }[[?ℝ;[0, ∞);[−1, 1];(0, ∞)|ℝ]]', rf'\text{{Range: }}\left[ [[-{amp}]],\ [[{amp}]]\right]', prompt='Domain and range'))
trig('11A-Q25-trig7', 3, '360', '45', 'right', 3); trig('11A-Q25-trig8', 2, '360', '60', 'left', 2)
trig('11A-Q25-trig9', '1/2', r'2\pi/3', r'\pi/3', 'right', 0); trig('11A-Q25-trig10', '1/2', r'2\pi/3', r'\pi/2', 'right', 0)
trig('11A-Q25-trig11', 2, '360', '90', 'left', 2); trig('11A-Q25-trig12', '1/4', '360', '30', 'right', 0)

# ------------------------------------------------------------------ 12G
put('12G-original-english-Q2', L(r'(x-[[9]])^2=[[49]]', prompt='Complete the square'), L(r'x=[[2#s]],\ [[16#s]]', prompt='Solve and check'))
put('12G-original-english-Q4', L(r'(2x-[[7]])^2=[[64]]', prompt='Complete the square'), L(r'x=[[-1/2#s]],\ [[15/2#s]]', prompt='Solve and check'))
put('12G-original-english-Q5', L(r'(5x+[[2]])^2=[[75]]', prompt='Complete the square'), L(r'5x+2=\pm[[5\sqrt{3}]]\ \Rightarrow\ x=\dfrac{-2\pm5\sqrt{3}}{5}', prompt='Solve and check'))
put('12G-original-english-Q8', L(r'(x-[[7/4]])^2=[[25/16]]', prompt='Complete the square'), L(r'x=[[1/2#s]],\ [[3#s]]', prompt='Solve and check'))
def ineq(qid, f, xs, last):
    ys = [S.nsimplify(f.subs(x, v)) for v in xs]
    put(qid, {'lines': None, 'prompt': 'Five-point table', 'table': {'xs': [str(v) for v in xs], 'ys': [str(v) for v in ys]}}, paper('Graph'), L(*last, prompt='Solution set'))
ineq('12G-original-english-Q11', x**2 - 2 * x - 24, [-1, 0, 1, 2, 3], [r'\text{Solution: }\left[ [[-4]],\ [[6]]\right]'])
ineq('12G-original-english-Q13', -x**2 + 3 * x + 10, [0, 1, S.Rational(3, 2), 2, 3], [r'x<[[-2]]\ \text{or}\ x>[[5]]'])
ineq('12G-original-english-Q14', x**2 - 6 * x + 2, [1, 2, 3, 4, 5], [r'x<[[3-\sqrt{7}]]\ \text{or}\ x>[[3+\sqrt{7}]]'])
put('12G-original-english-Q18', L(r'a(b^3-3ab-b^2)=[[ab^3-3a^2b-ab^2]]', r'b(b^3-3ab-b^2)=[[b^4-3ab^2-b^3]]', prompt='Expand'), L(r'(a+b)(b^3-3ab-b^2)=[[-3a^2b+ab^3-4ab^2+b^4-b^3]]', prompt='Combine like terms'))
put('12G-original-english-Q22', L(r'(4n-5)^2=[[16n^2-40n+25]]', prompt='Expand'), L(r'(4n-5)^3=[[64n^3-240n^2+300n-125]]', prompt='Combine like terms'))
put('12G-original-english-Q24', L(r'x^2:\ 6-4=[[2]],\quad x:\ -7+9=[[2]],\quad \text{constants: }8-5=[[3]]', prompt='Expand'), L(r'[[2x^2+2x+3]]', prompt='Combine like terms'))
put('12G-original-english-Q25', L(r'-(x^2+2x+5)=[[-x^2-2x-5]]', prompt='Expand'), L(r'[[-2x^2-5x-1]]', prompt='Combine like terms'))
put('12G-original-english-Q30', L(r'3^{2(3c+1)}=3^{3(2c-1)}:\quad [[6c+2]]=[[6c-3]]', prompt='Common base'), L(r'\text{Solution:}\ [[?c=0;c=1;No solution|No solution]]', prompt='Solve and check'))
put('12G-original-english-Q31', L(r'-3(2d-2)=[[-6d+6]],\quad 4(d+4)=[[4d+16]]', prompt='Common base'), L(r'd=[[-1]]', prompt='Solve and check'))
put('12G-original-english-Q35', L(r'z=\dfrac{89-72}{5}=[[3.4]]', prompt='Standardize'), L(r'P(X<89)=' + tol(0.9997, 0.0002), prompt='Normal probability'))
put('12G-Q24-added-01', L(r'3(x-1)=[[3x-3]],\quad 2(x+2)=[[2x+4]]', prompt='Common base'), L(r'x=[[7]]', prompt='Solve linear equation'))

# ------------------------------------------------------------------ 12A
for qid, p0 in [('12A-p65-Q35-1', 200), ('12A-p66-Q36-1', 500)]:
    put(qid, L(rf'P(t)=[[{p0}]]\cdot[[3]]^{{t}}', r'100\,\dfrac{P\prime(t)}{P(t)}=100\ln 3\approx' + tol(109.86, 0.01) + r'\%\text{ per day}'))
put('12A-p68-Q37-1', L(r"c\prime(t)=\dfrac{[[900e^{-10t}]]}{(9e^{-10t}+2)^2},\quad \text{so } c\prime(t) \text{ is } [[?positive;negative;zero|positive]]", r'\text{Upper bound: } c(t)<[[5]],\qquad \lim_{t\to\infty}c(t)=[[5]]'))
put('12A-Q22-added-01', L(r'x\ne[[1]],\quad \text{vertical asymptote }x=[[1]]', prompt='Domain and vertical asymptote'), L(r'x^2+1=(x-1)([[x+1]])+[[2]],\quad \text{oblique asymptote }y=[[x+1]]', prompt='Division and oblique asymptote'), L(r'\text{Is there a hole?}\ ' + YN('No'), prompt='Holes'))
put('12A-Q23-added-01', L(r"f\prime(x)=[[5x^4+3x^2-4x]]", prompt='Product Rule derivative'), L(r"f(1)=[[-2]],\quad f\prime(1)=[[4]],\quad y=[[4x-6]]", prompt='Tangent line'))
put('12A-Q25-added-01', L(r"P\prime(t)=[[120]]e^{0.3t}", prompt='Derivative'), L(r'100\dfrac{P\prime}{P}=[[30]]\%\text{ per day}', prompt='Percentage rate'), L(r'T=\dfrac{\ln 2}{0.3}\approx' + tol(2.31, 0.01) + r'\text{ days}', prompt='Doubling time'))


def main():
    import importlib.util
    sp = importlib.util.spec_from_file_location('card', ROOT / 'scripts/upper_card_frq.py'); cm = importlib.util.module_from_spec(sp); sp.loader.exec_module(cm)
    for qid, lines in cm.CARD.items(): SPEC[qid] = [L(*lines)]
    done = 0
    for cls in ['11G', '11A', '12G', '12A']:
        p = ROOT / f'public/data/study/{cls}.json'; d = json.loads(p.read_text()); byid = {q['id']: q for q in d['questions']}
        for qid, specs in SPEC.items():
            if qid not in byid: continue
            q = byid[qid]
            assert len(q['parts']) == len(specs), (qid, len(q['parts']), len(specs))
            for part, spec in zip(q['parts'], specs):
                if spec.get('prompt'): part['prompt'] = spec['prompt']
                part.pop('blanks', None)
                if spec.get('lines'): part['blanks'] = {'lines': spec['lines']}
                if spec.get('table'): part['blanks'] = {'lines': [r'\text{Complete the table of values.}'], 'table': spec['table']}
            q['answer_check'] = 'auto-fill'
            done += 1
        p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    print('authored', done, 'of', len(SPEC))


if __name__ == '__main__':
    main()
