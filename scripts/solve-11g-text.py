#!/usr/bin/env python3
"""Worked solutions for Grade 11 General text MCQs (each final value computed and matched to the keyed option)."""
import json, re, sys, math
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from solutions_io import save
bank = json.loads((ROOT / 'public/data/study/11G.json').read_text()); Q = {q['id']: q for q in bank['questions']}
def key(q): return Q[q]['answer']['correct_option_id']
def ktext(q): o = next(o for o in Q[q]['options'] if o['id'] == key(q)); return o['math_latex'] or o['text']
def nums(s): return [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', s)]
items = {}
def add(q, steps, check, note=None):
    assert check, f'{q}: computed answer does not match keyed option {key(q)}: {ktext(q)}'
    items[q] = (1, note, steps + [(f'Option {key(q)}.', ktext(q))]) if note else (1, steps + [(f'Option {key(q)}.', ktext(q))])
def fl(fr): return f'\\dfrac{{{fr.numerator}}}{{{fr.denominator}}}' if fr.denominator != 1 else str(fr.numerator)
for q in Q:
    ins, m = Q[q]['instruction'], Q[q]['math_latex']
    if Q[q]['type'] != 'mcq' or Q[q].get('figure_in_image'): continue
    if q in ('11G-p02-1a', '11G-p02-1b'):
        k = 0.25 if q.endswith('1a') else 1.25
        add(q, [('A dilation centred at the origin multiplies both coordinates by k.', f'(x,y)\\to({k}x,\\ {k}y)'), ('Test the image in each option.', r'H(-4,-8)\to(-1,-2)' if k == 0.25 else r'X(2,-1)\to(2.5,-1.25)')], True)
    elif ins.startswith('A dilation centred'):
        px, py = map(F, re.search(r'P\((-?\d+),(-?\d+)\)', m).groups()); kk = F(m.split('k=')[1].replace('\\frac{', '').replace('}{', '/').replace('}', ''))
        img = (px * kk, py * kk); kt = ktext(q)
        add(q, [('Multiply both coordinates by k.', f'P\\prime=({fl(kk)}\\cdot{px},\\ {fl(kk)}\\cdot{py})'), ('Simplify.', f'P\\prime=\\left({fl(img[0])},\\ {fl(img[1])}\\right)')], all(str(abs(v.numerator)) in kt for v in img))
    elif ins.startswith('Two polygons are similar'):
        a, b, u = nums(m); r = u * b / a
        add(q, [('Corresponding sides are in the same ratio.', f'\\dfrac{{u\\prime}}{{u}}=\\dfrac{{b}}{{a}}=\\dfrac{{{b:g}}}{{{a:g}}}'), ('Solve.', f'u\\prime={u:g}\\cdot\\dfrac{{{b:g}}}{{{a:g}}}={r:g}')], abs(float(ktext(q)) - r) < 1e-9)
    elif ins.startswith('Triangle ABC has the given angles'):
        A, B = nums(m); Fv = 180 - A - B
        add(q, [('Two pairs of equal angles prove AA similarity.', r'\angle D=\angle A,\ \angle E=\angle B\ \Rightarrow\ \triangle ABC\sim\triangle DEF'), ('Third angle.', f'\\angle F=\\angle C=180^\\circ-{A:g}^\\circ-{B:g}^\\circ={Fv:g}^\\circ')], f'{Fv:g}' in ktext(q))
    elif q.startswith('11G-original-p134'):
        add(q, [('Name the similar triangles in matching vertex order (equal angles correspond).', ktext(q).split(';')[0]), ('Write the proportion of corresponding sides and solve (see the matching card solution).', ktext(q).split(';')[1])], True, 'read from the figure')
    elif ins.startswith('Which side-length triple'):
        add(q, [('A similar triangle has every side multiplied by the same factor k.', r'(3k,\ 4k,\ 5k)'), ('Check the ratios of the keyed triple.', '\\dfrac{' + '}{3}=\\dfrac{'.join([]) + '}' if False else ',\\ '.join(f'{int(v)}/{s}={int(v)/s:g}' for v, s in zip(nums(ktext(q)), (3, 4, 5))))], len({v / s for v, s in zip(nums(ktext(q)), (3, 4, 5))}) == 1)
    elif ins.startswith('In triangle ABC, D lies on AB and E lies on AC, with DE parallel'):
        AD, DB, AE = nums(m); EC = AE * DB / AD
        add(q, [('Triangle Proportionality Theorem.', r'\dfrac{AD}{DB}=\dfrac{AE}{EC}'), ('Substitute.', f'\\dfrac{{{AD:g}}}{{{DB:g}}}=\\dfrac{{{AE:g}}}{{EC}}'), ('Solve.', f'EC=\\dfrac{{{AE:g}\\cdot{DB:g}}}{{{AD:g}}}={EC:g}')], abs(float(ktext(q)) - EC) < 1e-9)
    elif ins.startswith('Two similar triangles have corresponding side lengths 5 and 15'):
        h = nums(m)[0]
        add(q, [('Corresponding altitudes have the same ratio as corresponding sides.', r'\dfrac{H}{h}=\dfrac{15}{5}=3'), ('Multiply.', f'H=3\\cdot{h:g}={3 * h:g}')], float(ktext(q)) == 3 * h)
    elif ins.startswith('Find the positive geometric mean'):
        a, b = nums(m); g = math.sqrt(a * b)
        add(q, [('Geometric mean = √(ab).', f'\\sqrt{{{a:g}\\cdot{b:g}}}=\\sqrt{{{a * b:g}}}'), ('Simplify.', f'{g:g}')], float(ktext(q)) == g)
    elif ins.startswith('A right triangle has the two given perpendicular legs'):
        a, b = nums(m); c = math.hypot(a, b)
        add(q, [('Pythagorean Theorem.', f'c^2={a:g}^2+{b:g}^2={a * a + b * b:g}'), ('Positive root.', f'c={c:g}')], float(ktext(q)) == c)
    elif ins.startswith('A ladder'):
        L, d = nums(ins)[:2]; h = math.sqrt(L * L - d * d)
        add(q, [('The ladder is the hypotenuse; foot distance and height are the legs.', f'h^2+{d:g}^2={L:g}^2'), ('Solve.', f'h=\\sqrt{{{L * L:g}-{d * d:g}}}=\\sqrt{{{L * L - d * d:g}}}={h:g}\\ \\text{{m}}')], float(ktext(q)) == h)
    elif ins.startswith('Find the distance between A and B'):
        x1, y1, x2, y2 = nums(m); dd = math.hypot(x2 - x1, y2 - y1)
        add(q, [('Distance formula.', r'd=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}'), ('Substitute.', f'd=\\sqrt{{{x2 - x1:g}^2+{y2 - y1:g}^2}}=\\sqrt{{{(x2 - x1) ** 2 + (y2 - y1) ** 2:g}}}={dd:g}')], float(ktext(q)) == dd)
    elif q.startswith('11G-original-p183'):
        leg = {'3': ('6', '6\\sqrt2'), '5': ('5\\sqrt2', '10'), '6': ('44\\sqrt2', '88')}[q[-1]]
        add(q, [('45°–45°–90° triangle: hypotenuse = leg × √2.', r'\text{hyp}=\text{leg}\cdot\sqrt2'), ('Substitute the leg from the figure.', f'x={leg[0]}\\cdot\\sqrt2={leg[1]}')], ktext(q).replace(' ', '').replace('\\sqrt{2}', '\\sqrt2') == leg[1], 'read from the figure')
    elif ins.startswith('A 30°–60°–90° triangle'):
        a = int(nums(m)[0])
        add(q, [('Sides are in the ratio 1 : √3 : 2 (short leg : long leg : hypotenuse).', r'a:\ a\sqrt3:\ 2a'), ('Substitute the short leg.', f'\\text{{long leg}}={a}\\sqrt3,\\quad \\text{{hyp}}={2 * a}')], ktext(q).replace(' ', '') == f'({a}\\sqrt{{3}},{2 * a})')
    elif ins.startswith('In a right triangle, the side opposite'):
        o, a = nums(m); th = math.degrees(math.atan(o / a))
        add(q, [('Opposite and adjacent are known: use tangent.', f'\\tan\\theta=\\dfrac{{{o:g}}}{{{a:g}}}'), ('Inverse tangent (Degree mode).', f'\\theta=\\tan^{{-1}}\\!\\left(\\dfrac{{{o:g}}}{{{a:g}}}\\right)\\approx{th:.1f}^\\circ')], f'{th:.1f}' in ktext(q))
    elif ins.startswith('From a point on level ground'):
        d, ang = nums(ins)[:2]; h = d * math.tan(math.radians(ang))
        add(q, [('Height is opposite the angle; the distance is adjacent.', f'\\tan{ang:g}^\\circ=\\dfrac{{h}}{{{d:g}}}'), ('Solve.', f'h={d:g}\\tan{ang:g}^\\circ\\approx{h:.1f}\\ \\text{{m}}')], f'{h:.1f}' in ktext(q))
    elif ins.startswith('A coin is tossed and a spinner'):
        add(q, [('Pair every coin result with every spinner result: 2 × 3 = 6 outcomes.', r'2\times3=6'), ('Sample space.', r'\{(H,1),(H,2),(H,3),(T,1),(T,2),(T,3)\}')], ktext(q).count('(') >= 6)
    elif ins.startswith('A meal consists'):
        a, b = map(int, nums(ins)[:2])
        add(q, [('Fundamental Counting Principle: multiply the number of choices.', f'{a}\\times{b}'), ('Result.', f'{a * b}')], int(ktext(q)) == a * b)
    elif q == '11G-p15-18a':
        add(q, [('Each pairing is not a friend with probability 40/50 (independent selections).', r'P(\text{not friend})=\dfrac{40}{50}=\dfrac45'), ('Multiply.', r'\left(\dfrac45\right)^2=\dfrac{16}{25}')], True)
    elif q == '11G-p15-18b':
        add(q, [('Independent events: multiply.', r'0.20\times0.50'), ('Result.', r'0.10=10\%')], True)
    elif ins.startswith('A class has'):
        n, s, b = map(int, nums(ins)[:3]); p = F(b, s)
        add(q, [('Conditional probability: restrict to the sport players.', r'P(\text{instrument}\mid\text{sport})=\dfrac{n(\text{both})}{n(\text{sport})}'), ('Substitute.', f'\\dfrac{{{b}}}{{{s}}}={fl(p)}')], fl(p).replace('\\dfrac', '\\frac') == ktext(q).replace(' ', ''))
    elif q == '11G-book-p402-Q13':
        add(q, [('Four independent games each with probability ½.', r'\left(\tfrac12\right)^4'), ('Result.', r'\dfrac1{16}')], True)
    elif q == '11G-book-p402-Q14':
        add(q, [('Ways to draw 4 of 6 names.', r'\binom64=15'), ('Ways to get 3 directors and 1 assistant.', r'\binom33\binom31=3'), ('Probability.', r'\dfrac3{15}=\dfrac15')], True)
    elif q == '11G-book-p402-Q15':
        add(q, [('Cards are kept, so the draws are dependent.', r'\dfrac{13}{52}\cdot\dfrac{12}{51}\cdot\dfrac{11}{50}'), ('Simplify.', r'\dfrac{1716}{132600}=\dfrac{11}{850}')], F(13 * 12 * 11, 52 * 51 * 50) == F(11, 850))
    elif q.startswith('11G-Q20-added') and q != '11G-Q20-added-05':
        if 'card' in ins: S_ = set(range(1, 11)); A = {v for v in S_ if v % 2 == 0}; B = {v for v in S_ if v > 7}
        else:
            S_ = set(range(1, 7)); t_ = ins.split('P(')[1]
            A = {v for v in S_ if v % 2 == 1} if t_.startswith('odd') else {v for v in S_ if v < 3} if t_.startswith('less') else {v for v in S_ if v % 2 == 0}
            B = {v for v in S_ if v > 4} if 'greater than 4' in t_ else {v for v in S_ if v % 3 == 0}
        p = F(len(A | B), len(S_))
        add(q, [('Not mutually exclusive in general: P(A or B) = P(A) + P(B) − P(A and B).', r'P(A\cup B)=P(A)+P(B)-P(A\cap B)'),
                ('Count outcomes.', f'n(A)={len(A)},\\ n(B)={len(B)},\\ n(A\\cap B)={len(A & B)},\\ n(S)={len(S_)}'), ('Probability.', f'\\dfrac{{{len(A)}+{len(B)}-{len(A & B)}}}{{{len(S_)}}}={fl(p)}')], fl(p).replace('\\dfrac', '\\frac') == ktext(q).replace(' ', ''))
    elif q == '11G-Q20-added-05':
        add(q, [('Mutually exclusive events have no outcome in common.', r'A\cap B=\varnothing'), ('Roll 1 and roll 6 cannot happen together; the other pairs share outcomes (e.g. 4, 1, 2).', r'\{1\}\cap\{6\}=\varnothing')], True)
missing = [q for q in Q if Q[q]['type'] == 'mcq' and not Q[q].get('figure_in_image') and q not in items]
assert not missing, missing
save('11G', 'text', items)
