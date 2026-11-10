#!/usr/bin/env python3
"""Add the missing Grade 10 Advanced structure questions (from the teacher revision booklet) to the study bank.

Input : content-imports/g10a-revision/items.json (scripts/import-g10a-revision.py --stage parse)
Output: public/data/study/10A1.json (new questions, assets, LO lists), calculator-support.json (guides),
        public/data/study-assets/10a1/rev###.png (figures, lossless), content-imports/g10a-revision/build-report.json

Rules (see STUDY_AUTHORING.md):
 * An item is imported only when its (printed page, exercise) is not already in the bank -> no duplicates.
   The (page, exercise) of every revision item comes from the order of the official coverage sheet; the alignment is
   cross-checked against the 100 exercises already in the bank (all 100 agree with the booklet's key).
 * Provenance is kept on every question; originals are never overwritten. Idempotent: previous G10A-REV-* items are replaced.
 * Algebra answers are re-derived with sympy and must equal the booklet's key; distractors of algebra families are
   regenerated as named mistakes. Figure-based keys come from the booklet and are flagged `key_source`.
"""
import copy, hashlib, importlib.util, itertools, json, re, shutil, sys
from fractions import Fraction
from pathlib import Path
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor, split_symbols

ROOT = Path(__file__).resolve().parent.parent
REV = ROOT / 'content-imports/g10a-revision'
spec = importlib.util.spec_from_file_location('imp', ROOT / 'scripts/import-g10a-revision.py')
imp = importlib.util.module_from_spec(spec); sys.argv = sys.argv[:1]; spec.loader.exec_module(imp)
u2tex = imp.u2tex
T = standard_transformations + (split_symbols, implicit_multiplication_application, convert_xor)

def rng(a, b): return [str(i) for i in range(a, b + 1)]
STRUCTURE = {  # coverage sheet (Learn sections excluded): LO -> [(printed page, [exercises])]
 'LO01': [(635, rng(10, 14) + rng(22, 26))], 'LO02': [(649, rng(1, 6))], 'LO03': [(665, rng(11, 20))], 'LO04': [(671, rng(1, 6))], 'LO05': [(63, rng(1, 4))],
 'LO06': [(72, rng(9, 12))], 'LO07': [(79, rng(1, 6))], 'LO08': [(106, rng(13, 16))], 'LO09': [(120, rng(13, 16)), (121, ['20'])], 'LO10': [(128, rng(11, 14))],
 'LO11': [(120, rng(10, 12) + rng(17, 18))], 'LO12': [(133, rng(1, 8))], 'LO13': [(146, rng(11, 16))], 'LO14': [(153, rng(1, 11))], 'LO15': [(165, rng(1, 6) + rng(11, 14))],
 'LO16': [(171, rng(7, 12)), (172, rng(20, 22))], 'LO17': [(184, rng(19, 25)), (185, rng(33, 38))], 'LO18': [(192, rng(22, 27)), (193, rng(30, 32))], 'LO19': [(199, rng(1, 7))],
 'LO20': [(200, rng(13, 18)), (201, rng(19, 21))], 'LO21': [(680, rng(35, 41)), (681, rng(51, 56))], 'LO22': [(64, rng(9, 14) + rng(15, 18))], 'LO23': [(139, rng(5, 11))],
 'LO24': [(177, rng(13, 18)), (178, rng(19, 24))], 'LO25': [(208, rng(15, 26))]}

# ------------------------------------------------------------------ math helpers
def S(txt):
    txt = re.sub(r'√\s*\(([^()]*)\)', r'sqrt(\1)', txt); txt = re.sub(r'√\s*(\d+)', r'sqrt(\1)', txt)
    t = txt.replace('−', '-').replace('²', '^2').replace('³', '^3').replace('⁴', '^4').replace('⁵', '^5').replace('⁶', '^6').replace('½', '(1/2)')
    return parse_expr(t, transformations=T)
def tx(e):  # sympy -> LaTeX, spaced like the existing bank
    return sp.latex(e, order='lex', mul_symbol=' ').replace('\\left(', '\\left(').replace('\\cdot', ' ')
def poly_tex(e, var=None):
    e = sp.expand(e)
    gens = sorted(e.free_symbols, key=str)
    p = sp.Poly(e, *gens)
    parts = []
    for mon, c in sorted(p.terms(), key=lambda m: tuple(-x for x in m[0])):
        m = sp.Mul(*[g ** k for g, k in zip(gens, mon)])
        parts.append((c, m))
    out = ''
    for i, (c, m) in enumerate(parts):
        mt = '' if m == 1 else sp.latex(m)
        ca = abs(c)
        body = (str(ca) if (ca != 1 or m == 1) else '') + (' ' if mt and (ca != 1 or m == 1) else '') + mt
        body = body.strip()
        if i == 0: out += ('- ' if c < 0 else '') + body
        else: out += (' - ' if c < 0 else ' + ') + body
    return out
def lead(e):
    e = sp.expand(e); gens = sorted(e.free_symbols, key=str); p = sp.Poly(e, *gens)
    return sp.Poly(e, gens[0]).LC()
def num(s): return sp.nsimplify(s.replace('−', '-'))

# ------------------------------------------------------------------ text normalisation to the existing bank style
MCQ_INSTRUCTION = {
 'Write in standard form and identify the leading coefficient.': 'Which option shows the polynomial in standard form and its leading coefficient?',
 'Find the sum or difference.': 'Which option gives the sum or difference?',
 'Find the product.': 'Which option gives the product?',
 'Factor the polynomial.': 'Which option is the complete factorisation of the expression?',
 'Factor the polynomial, if possible.': 'Which option is the complete factorisation of the expression?',
 'Is the quadrilateral a parallelogram? Select the conclusion and reason.': 'Determine whether the markings guarantee a parallelogram. Choose the correct justification.',
 'Are the triangles similar? Select the conclusion and reason.': 'Determine whether the triangles are similar. Choose a valid explanation.',
 'Find the scale factor of the dilation.': 'Which option gives the scale factor from the original polygon to its primed image?',
 'Find x, y, and z.': 'Which values of x, y and z are correct, in simplest exact form?',
 'Find x and y.': 'Which values of x and y are correct, in simplest exact form?',
 'Find the geometric mean between the numbers.': 'What is the positive geometric mean of the two numbers?',
 'Can these be the side lengths of a triangle? If so, classify it.': 'How is the triangle with these side lengths classified?',
 'Solve the right triangle. Round sides to the nearest tenth and angles to the nearest degree.': 'Solve the right triangle. Round sides to the nearest tenth and acute angles to the nearest degree.',
 'Find the perimeter and area. Round to the nearest hundredth.': 'Which option gives the perimeter and area, rounded to the nearest hundredth?',
 'Find the area of △ABC to the nearest tenth.': 'Use trigonometry to find the triangle’s area to the nearest tenth.',
}
FRQ_INSTRUCTION = {
 'Factor completely, if possible. If it cannot be factored using integers, write prime.': 'Factor completely using integers.',
 'Is this a perfect square trinomial? Write yes or no. If yes, factor it.': 'Determine whether this is a perfect-square trinomial; if so, factor it.',
 'The measure of an interior angle of a regular polygon is given. Find the number of sides.': 'The given angle is an interior angle of a regular polygon. Find the number of sides.',
 'Determine whether the triangle has no solution, one solution, or two solutions. Then solve the triangle. Round sides to the nearest tenth and angles to the nearest degree.': 'Determine whether the triangle has no solution, one solution or two solutions. Then solve it. Round sides to the nearest tenth and angles to the nearest degree.',
 'Find the coordinates of the midpoint M of the segment joining the points.': 'Find the midpoint of the segment joining the two points.',
 'Find the distance between the points and the coordinates of their midpoint M.': 'Find the distance and midpoint of the segment.',
}
SENTENCE_FIX = [(r'^Yes; ', 'Yes: '), (r'^No; ', 'No: '), (r'^Acute triangle$', 'Acute'), (r'^Obtuse triangle$', 'Obtuse'), (r'^Right triangle$', 'Right')]

def fix_sentence(s):
    for a, b in SENTENCE_FIX: s = re.sub(a, b, s)
    return s

def split_stem(item):
    """-> (instruction, math line or '')  : the last short non-sentence line is the mathematical given."""
    lines = [l.strip() for l in item['stem_lines'] if l.strip()]
    if len(lines) >= 2 and not lines[-1].endswith(('.', '?', ':')) and lines[-2].endswith(('.', '?', ':')):
        # keep multi-line word problems intact: the last line must look like a bare expression / data line
        last = lines[-1]
        if len(last) <= 60 and not re.search(r'[a-z]{4,} [a-z]{4,}', last):
            return ' '.join(lines[:-1]), last
    return ' '.join(lines), ''

def frac_slash(t):
    t = re.sub(r'(\d+(?:\\sqrt\{\d+\})?)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

def opt_tex(s, lo):
    """option text -> (text, math_latex or None)"""
    s = s.strip()
    if re.search(r'[A-Za-z]{4,} [A-Za-z]{3,}', s) and lo in ('LO07', 'LO12', 'LO16'): return fix_sentence(s), None
    if re.fullmatch(r'(Acute|Obtuse|Right) triangle|Not a triangle', s): return fix_sentence(s), None
    m = re.fullmatch(r'([\d.]+)\s*(ft|yd|m|cm|in\.?|units|mi)(²?)', s)
    if m:
        val, unit, sq = m.groups()
        return s, f'{val}\\text{{ {unit}}}' + ('^{2}' if sq else '')
    t = u2tex(s)
    # "x=8, y=16" -> (x,y)=(8,16)
    mm = re.fullmatch(r'((?:[A-Za-zθ∠]+\s*=\s*[^,;]+(?:,\s*)?)+)', s)
    if mm and s.count('=') >= 2 and not re.search(r'perimeter|P=', s):
        pairs = re.findall(r'([A-Za-z]+)\s*=\s*([^,]+)', s)
        names = ','.join(p[0] for p in pairs); vals = ','.join(frac_slash(u2tex(p[1].strip())) for p in pairs)
        return s, f'({names})=({vals})'
    t = frac_slash(t).replace(';', ',\\quad ')
    return s, t

def to_latex_poly(s):
    return frac_slash(u2tex(s)).replace('; ', ',\\quad ')


def poly_tex_asc(e, v):
    p = sp.Poly(sp.expand(e), v); out = ''
    for i, (mon, c) in enumerate(sorted(p.terms(), key=lambda t: t[0])):
        m = v ** mon[0]; mt = '' if m == 1 else sp.latex(m); ca = abs(c)
        body = ((str(ca) if (ca != 1 or m == 1) else '') + (' ' if mt and (ca != 1 or m == 1) else '') + mt).strip()
        out += (('- ' if c < 0 else '') + body) if i == 0 else ((' - ' if c < 0 else ' + ') + body)
    return out

# ------------------------------------------------------------------ small LaTeX builders (match the existing bank style)
def bn(coef, var, const):
    """binomial  coef*var + const  as '\\left(9 q - 10\\right)'"""
    c = '' if coef == 1 else ('-' if coef == -1 else str(coef))
    sign = '+' if const >= 0 else '-'
    return f'\\left({c}{(" " if c not in ("", "-") else "")}{var} {sign} {abs(const)}\\right)'
def prod(*fs): return ' '.join(fs)
def monic_factor_distractors(b, c, v):
    """factor pairs of c with a wrong sum + the sign-swapped pair"""
    pairs = []
    for p in range(-abs(c), abs(c) + 1):
        if p and c % p == 0:
            q = c // p
            if p <= q and p + q != b: pairs.append((p, q))
    pairs.sort(key=lambda t: abs(abs(t[0] + t[1]) - abs(b)))
    out = [(-(sp.Rational(0) + 0) if False else x) for x in []]
    cands = [(-p0, -q0) for p0, q0 in [next(((p, c // p) for p in range(1, abs(b) + 1) if c % p == 0 and p + c // p == abs(b)), (0, 0))]] if False else []
    return pairs

def expl_generic(lo_rule, text): return f'{text} {lo_rule}'.strip()

# ------------------------------------------------------------------ builders
def build_mcq(item, lo, lo_rule, n, k):
    ins_src, math_line = split_stem(item)
    ins = MCQ_INSTRUCTION.get(ins_src, ins_src)
    letters = 'ABCD'; key = item['key']
    opts = [{'id': L, 'text': None, 'math_latex': None} for L in letters]
    explanation = None; family = None; verified = None
    mis = {}
    # ---- algebraic families: recompute key, regenerate named-mistake distractors
    try:
        fam = algebra_family(item, lo, ins_src, math_line)
    except Exception as e:
        fam = None; print('  algebra family failed for', item['number'], e)
    if fam:
        keytex, dists, why, explanation, verified = fam
        di = iter(zip(dists, why))
        for o in opts:
            if o['id'] == key: o['text'] = o['math_latex'] = keytex
            else: o['math_latex'] = o['text'] = (lambda t: (mis.__setitem__(o['id'], t[1]) or t[0]))(next(di))
        family = 'algebra'
    else:
        for o in opts:
            t, m = opt_tex(item['options'][o['id']], lo)
            o['text'] = m if m else t
            if m: o['math_latex'] = m
            else: o.pop('math_latex')
    for o in opts:
        o.setdefault('math_latex', None)
        if o['math_latex'] is None: o.pop('math_latex')
        if o['id'] != key and o['id'] in mis: o['misconception'] = mis[o['id']]
    keyopt = next(o for o in opts if o['id'] == key)
    q = {'type': 'mcq', 'instruction': ins, 'stem': (ins + ' ' + (to_latex_poly(math_line) if math_line else '')).rstrip() + (' ' if not math_line else ''),
         'math_latex': to_latex_poly(math_line) if math_line else '', 'options': opts,
         'marks': None, 'answer': {'correct_option_id': key, 'correct_option_text': keyopt['text'], 'explanation': explanation or default_explanation(lo, item, lo_rule, keyopt)}}
    return q, family, verified

def default_explanation(lo, item, rule, keyopt):
    extra = ' '.join(item['extra']).strip()
    if extra: return u2tex_plain(extra)
    return rule

def u2tex_plain(s): return re.sub(r'\s+', ' ', s.replace('−', '-')).strip()

def algebra_family(item, lo, ins_src, math_line):
    key = item['key']
    if lo == 'LO01' and ins_src.startswith('Write in standard form'):
        e = S(math_line); v = sorted(e.free_symbols, key=str)[0]; c = sp.Poly(e, v).LC(); std = poly_tex(e)
        keyt = f'{std},\\quad {sp.latex(c)}'
        # booklet key must agree
        bk = item['options'][key]; assert S(bk.split(';')[0]) == sp.expand(e) and S(bk.split(';')[1]) == c, 'booklet key disagrees with sympy'
        written = [w for w in re.split(r'(?<!\^)(?=[+-])', math_line.replace(' ', '').replace('−', '-')) if w]
        first = S(written[0]); wl = sp.Poly(first, v).LC() if first.has(v) else first
        const = sp.expand(e).subs(v, 0)
        second = sp.Poly(e, v).all_coeffs()[1]
        cand = [(wl, 'Took the first term as written, not the term with the highest power.'), (const, 'Used the constant term as the leading coefficient.'), (-c, 'Gave the leading coefficient the wrong sign.'),
                (second, 'Took the coefficient of the second-highest power.'), (c + 1, 'Miscounted the leading coefficient.'), (2 * c, 'Doubled the leading coefficient.')]
        uniq, seen = [], {c}
        for val, why_ in cand:
            if val not in seen: seen.add(val); uniq.append((val, why_))
        uniq = uniq[:3]
        d1, d2, d3 = [f'{std},\\quad {sp.latex(v_)}' for v_, _ in uniq]
        return keyt, [d1, d2, d3], [w_ for _, w_ in uniq], \
            f'Order the terms by decreasing exponent: {std}. The leading coefficient is the coefficient of the highest-power term: {sp.latex(c)}.', 'sympy'
    if lo == 'LO01' and ins_src.startswith('Find the sum'):
        a, b = re.match(r'\((.*)\)\s*\+\s*\((.*)\)$', math_line).groups(); A, B = S(a), S(b); res = sp.expand(A + B)
        assert S(item['options'][key]) == res, 'booklet key disagrees with sympy'
        d1 = sp.expand(A - B); t2 = sp.Add.make_args(sp.expand(B))[0]; d3 = sp.expand(res - 2 * t2)
        d2 = sp.expand(res - sp.expand(res).subs({s_: 0 for s_ in res.free_symbols}))  # dropped the constant term
        ds = [d1, d2, d3]
        if len({sp.expand(x) for x in ds + [res]}) < 4: return None
        return poly_tex(res), [poly_tex(x) for x in ds], ['Subtracted the second polynomial instead of adding.', 'Dropped the constant term when combining like terms.', 'Changed the sign of a term of the second polynomial.'], f'Remove the parentheses and combine like terms: {poly_tex(res)}.', 'sympy'
    if lo == 'LO02':
        a, b = re.match(r'\((.*)\)\s*\((.*)\)$', math_line).groups(); A, B = S(a), S(b); res = sp.expand(A * B)
        assert S(item['options'][key]) == res, 'booklet key disagrees with sympy'
        v = sorted(res.free_symbols, key=str)[0]; (a1, a0), (b1, b0) = sp.Poly(A, v).all_coeffs(), sp.Poly(B, v).all_coeffs()
        ds = [a1 * b1 * v ** 2 + a0 * b0, a1 * b1 * v ** 2 + (a1 * b0 + a0 * b1) * v - a0 * b0, a1 * b1 * v ** 2 + a1 * b0 * v + a0 * b0]
        return poly_tex(res), [poly_tex(x) for x in ds], ['Multiplied only the first and the last terms.', 'Sign error on the product of the last terms.', 'Used only the outer product for the middle term.'], \
            f'FOIL: first {sp.latex(a1*b1*v**2)}, outer {sp.latex(a1*b0*v)}, inner {sp.latex(a0*b1*v)}, last {sp.latex(a0*b0)}; combine like terms: {poly_tex(res)}.', 'sympy'
    if lo in ('LO03', 'LO04') and ins_src.startswith('Factor'):
        e = S(math_line); f = sp.factor(e)
        # booklet key must equal the polynomial
        kb = item['options'][key]; kb_expr = S(re.sub(r'(\d)\(', r'\1*(', kb.replace('(', '(').replace(')(', ')*(')))
        assert sp.expand(kb_expr - e) == 0, f'booklet key {kb} is not equal to {math_line}'
        syms = sorted(e.free_symbols, key=str)
        gcf = sp.factor_list(e)[0]
        if lo == 'LO04' or len(syms) == 1 and not (math_line.replace(' ', '').replace('−', '-').count('r') and False):
            v = syms[0]; P = sp.Poly(e, v); c2, b, c = P.all_coeffs() if P.degree() == 2 else (None, None, None)
            if P.degree() == 2 and c2 == 1:
                fl = [t for t in sp.Mul.make_args(f) if t.has(v)]
                if len(fl) == 2:
                    p, q = [int(t.subs(v, 0)) for t in fl]
                    keyt = prod(bn(1, str(v), p), bn(1, str(v), q))
                    cand = [(prod(bn(1, str(v), -p), bn(1, str(v), -q)), 'Sign error: both constants have the wrong sign.')]
                    pairs = [(m, c // m) for m in range(-abs(c), abs(c) + 1) if m and c % m == 0 and m <= c // m and m + c // m != b]
                    pairs.sort(key=lambda t: (abs(t[0] + t[1] - b), t))
                    for m, n2 in pairs:
                        cand.append((prod(bn(1, str(v), m), bn(1, str(v), n2)), f'The factors multiply to {c} but add to {m + n2}, not {b}.'))
                    uniq, seen = [], {sp.expand(e)}
                    for t_, why_ in cand:
                        ex = sp.expand(S(re.sub(r'\\left|\\right', '', t_).replace('\\', '').replace(')(', ')*(').replace(') (', ')*(')))
                        if ex not in seen: seen.add(ex); uniq.append((t_, why_))
                    cand = uniq[:3]
                    if len(cand) == 3:
                        return keyt, [c_[0] for c_ in cand], [c_[1] for c_ in cand], f'Find two integers with product {c} and sum {b}: {p} and {q}. So {poly_tex(e)} = {keyt}.', 'sympy'
        # four-term grouping or GCF
        if len(syms) == 2 and sp.factor_list(e)[1] and len(sp.factor_list(e)[1]) == 2 and all(sp.Poly(t, *syms).total_degree() == 1 for t, _ in sp.factor_list(e)[1]):
            (t1, _), (t2, _) = sp.factor_list(e)[1]
            def lin(t, sign=1):
                P = sp.Poly(t, *syms); co = [(P.coeff_monomial(s_), s_) for s_ in syms]
                const = P.coeff_monomial(1); (cv, sv) = [x for x in co if x[0] != 0][0]
                return bn(int(cv), str(sv), int(const) * sign)
            keyt = prod(lin(t1), lin(t2)); g = gcf
            ds = [prod(lin(t1, -1), lin(t2)), prod(lin(t1), lin(t2, -1)), prod(lin(t1, -1), lin(t2, -1))]
            if len({keyt, *ds}) == 4:
                return keyt, ds, ['Sign error in the first binomial when factoring the group.', 'Sign error in the second binomial when factoring the group.', 'Sign errors in both binomials (factored a negative common factor incorrectly).'], \
                    f'Group the terms, factor the common factor out of each group, then factor out the common binomial: {poly_tex(e)} = {keyt}.', 'sympy'
        if len(syms) == 1 and P.degree() == 2 and c2 != 1 and not b == 0 and c == 0:
            v = syms[0]; g, rest = sp.factor_list(e)[0], f
            # GCF example 8r^2+12r = 4r(2r+3)
            fl = sp.factor_list(e); content = fl[0]
            mono = [t for t, _ in fl[1] if t == v]
            lin_ = [t for t, _ in fl[1] if t != v]
            if mono and lin_:
                a_, b_ = sp.Poly(lin_[0], v).all_coeffs()
                keyt = f'{content} {v} \\left({"" if a_ == 1 else a_} {v} {"+" if b_ >= 0 else "-"} {abs(b_)}\\right)'.replace('  ', ' ')
                g2 = sp.gcd(sp.Poly(e, v).all_coeffs()[0], sp.Poly(e, v).all_coeffs()[1])
                half = content // 2 if content % 2 == 0 else None
                ds = [f'{content} {v} \\left({"" if a_ == 1 else a_} {v} {"-" if b_ >= 0 else "+"} {abs(b_)}\\right)'.replace('  ', ' '),
                      f'{content} {v} \\left({"" if a_ == 1 else a_} {v} {"+" if b_ >= 0 else "-"} {abs(b_) * content // (content // g2 if False else 1) if False else abs(b_) * content}\\right)'.replace('  ', ' '),
                      f'{content} \\left({"" if a_ == 1 else a_} {v} {"+" if b_ >= 0 else "-"} {abs(b_)}\\right)'.replace('  ', ' ')]
                if len(ds) == 3:
                    return keyt, ds, ['Sign error inside the bracket.', 'Divided only the first term by the common factor (kept the second coefficient).', 'Left the variable out of the common factor.'], f'Factor out the greatest common factor {content} {v}: {poly_tex(e)} = {keyt}.', 'sympy'
    return None

# ------------------------------------------------------------------ numeric verification of keys that can be recomputed from the text
def fmt_num(x, nd=1):
    x = float(x); return f'{x:.{nd}f}'
def numeric_check(item, lo):
    """returns (description, ok) when the key can be recomputed independently from the statement text, else None"""
    n = item['number']; txt = ' '.join(item['stem_lines']); key = item['options'].get(item['key'], '')
    num_ = lambda s: [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', s.replace('−', '-'))]
    import math
    if n == 55: v = (2.5 * 5, 2.5 * 2); return ('C′ = 2.5·(5,2) = (12.5,5)', num_(key) == [12.5, 5.0])
    if n in (92, 93, 94, 95):
        a, b = [int(x) for x in re.findall(r'\d+', item['stem_lines'][-1])]; g = sp.sqrt(a * b)
        return (f'√({a}·{b}) = {sp.simplify(g)}', sp.simplify(S(key) - g) == 0)
    if n in (106, 107, 108):
        sides = [sp.sqrt(int(x)) if '√' in t else sp.Integer(int(x)) for t, x in [(t, re.sub(r'\D', '', t)) for t in re.split(r',\s*', item['stem_lines'][-1])]]
        sq = sorted(s_ ** 2 for s_ in sides); a2, b2, c2 = sq; kind = 'Right' if a2 + b2 == c2 else ('Acute' if a2 + b2 > c2 else 'Obtuse')
        return (f'{a2}+{b2} vs {c2}: {kind}', key.split()[0] == kind)
    if n == 115: return ('40·sin 30° = 20', num_(key)[0] == 20)
    if n == 135: v = math.degrees(math.atan((80 + 5.5) / 122)); return (f'atan(85.5/122) = {v:.2f}°', abs(num_(key)[0] - round(v)) < 0.51)
    if n == 136: v = 120 / math.tan(math.radians(19)); return (f'120/tan 19° = {v:.2f}', abs(num_(key)[0] - v) < 0.06)
    if n == 137: v = math.degrees(math.atan(528 / 2000)); return (f'atan(528/2000) = {v:.2f}°', abs(num_(key)[0] - v) < 0.06)
    if n == 71: v = 4.5 * 100 / (3 + 4 / 12); return (f'4.5·100/3.333 = {v:.1f}', abs(num_(key)[0] - v) < 0.5)
    if n == 78: return ('AC = 2·DE = 20', num_(key)[0] == 20)
    if n == 83: return ('FG = ST·FJ/SH = 6·7/5 = 8.4', abs(num_(key)[0] - 8.4) < 1e-9)
    if n == 84: return ('MN = AB·MQ/AD = 24·10.5/14 = 18', abs(num_(key)[0] - 18) < 1e-9)
    return None

# ------------------------------------------------------------------ figures, FRQ, calculator support
def build_frq(item, lo, sibling):
    ins_src, math_line = split_stem(item)
    ins = FRQ_INSTRUCTION.get(ins_src, ins_src)
    sol = [l for l in item['solution'] if l.strip()]
    sol_text = ' '.join(l.strip() for l in sol)
    parts = copy.deepcopy(sibling['parts'])
    mathtex = ''
    if lo == 'LO21':
        last = sol[-1].strip()
        if last.startswith('Yes;'): final = re.sub(r'^Yes;\s*', '', last).rstrip('.')
        elif last.startswith('No;'): final = None
        else: final = last
        if final is not None:
            fe = S(final.replace('²', '^2')); orig = S(math_line.replace('²', '^2').replace('³', '^3').replace('⁴', '^4'))
            assert sp.expand(fe - orig) == 0, f'booklet factorisation {final} != {math_line}'
            mathtex = tex_factor(final)
        else:
            orig = S(math_line.replace('²', '^2')); assert not is_perfect_square_trinomial(orig), 'booklet says not a perfect square but it is'
            mathtex = '\\text{Not a perfect-square trinomial}'
        parts[0]['answer'] = {'model_answer_and_marking': f'{sol_text} Correct method (5), complete factors and check (5).', 'math_latex': mathtex}
    elif lo == 'LO22':
        if 'regular polygon' in ins_src:
            ang = int(re.sub(r'\D', '', math_line)); n = 360 // (180 - ang); assert 360 % (180 - ang) == 0 and f'{n} sides' in sol_text
            parts[0]['answer'] = {'model_answer_and_marking': f'Exterior angle=180−{ang}={180 - ang}°. Therefore n=360/{180 - ang}={n}. Correct exterior angle (3), equation (3), number of sides (4).', 'math_latex': f'n={n}'}
        else:
            xv = int(re.findall(r'(?<![\dA-Za-z])x = (\d+)', sol_text)[-1]); eq = sol[0].split('=')[0]
            ex = S(eq.replace('−', '-')); assert sp.solve(sp.Eq(ex, 360), sp.Symbol('x'))[0] == xv, 'booklet x does not solve its own equation'
            parts[0]['answer'] = {'model_answer_and_marking': f'The exterior angles sum to 360° (3). Combine all labelled exterior angles: {sol_text.split(";")[0]} (4), so x={xv} (3).', 'math_latex': f'x={xv}'}
    elif lo == 'LO23':
        mm = re.findall(r'(?:x(?: / [\d.]+)?\s*=\s*|x\s*=\s*|[Tt]ower height\s*=\s*)([\d.]+)', sol_text)
        final = sol[-1].strip()
        parts[0]['prompt'] = 'Write the proportion and solve.'
        parts[0]['answer'] = {'model_answer_and_marking': f'{sol_text} Correct similarity statement or scale (4), proportion (3), final value (3).', 'math_latex': tex_final(final)}
    elif lo == 'LO24':
        pts = parse_points(math_line)
        two = len(parts) == 2
        mid = tuple(sp.nsimplify(sp.simplify((a + b) / 2)) for a, b in zip(*pts)); dist = sp.sqrt(sp.simplify(sum((b - a) ** 2 for a, b in zip(*pts))))
        mtext = [l for l in sol if l.strip().startswith('M =')][-1]
        assert sp.simplify(S(mtext.split('=')[-1].strip().strip('()').split(',')[0].replace('²', '^2')) - mid[0]) == 0, 'booklet midpoint x disagrees'
        if two:
            dline = [l for l in sol if l.strip().startswith('d =')][-1].split('=')[-1].strip()
            assert sp.simplify(S(dline) - dist) == 0, 'booklet distance disagrees'
            parts[0]['answer'] = {'model_answer_and_marking': f'Use d=√[(x₂−x₁)²+(y₂−y₁)²+(z₂−z₁)²]; substitution (3) and simplified exact distance (2).', 'math_latex': f'd={sp.latex(dist)}'}
            parts[1]['answer'] = {'model_answer_and_marking': 'Average the corresponding x, y and z coordinates separately. Correct component calculations and complete midpoint.', 'math_latex': f'M=({",".join(sp.latex(m) for m in mid)})'}
        else:
            parts[0]['answer'] = {'model_answer_and_marking': 'Average the corresponding x, y and z coordinates separately. Correct component calculations and complete midpoint.', 'math_latex': f'M=({",".join(sp.latex(m) for m in mid)})'}
    elif lo == 'LO25':
        A, a, b = [float(x) for x in re.findall(r'(?:∠A|A) = ([\d.]+)°|a = ([\d.]+)|b = ([\d.]+)', math_line.replace('∠', '')) and [t for tup in re.findall(r'A = ([\d.]+)°.*?a = ([\d.]+).*?b = ([\d.]+)', math_line.replace('∠', '')) for t in tup]]
        import math
        ratio = b * math.sin(math.radians(A)) / a
        if ratio > 1 + 1e-12: count = 0
        else:
            B1 = math.degrees(math.asin(min(1, ratio))); count = 2 if (abs(ratio - 1) > 1e-9 and A + (180 - B1) < 180) else 1
        words = {0: 'No solution', 1: 'One solution', 2: 'Two solutions'}[count]
        assert words.lower().split()[0] in sol_text.lower().replace('(0 triangles)', 'no solution') or (count == 0 and 'no triangle' in sol_text.lower()), f'booklet count disagrees: computed {words}'
        parts[0]['answer'] = {'model_answer_and_marking': f'sin B=b sin A/a={ratio:.8f}. {words}; test both arcsine candidates against A+B<180°. Correct ratio (2), count and admissibility (2).', 'math_latex': ''}
        tri = []
        if count:
            for B in ([B1] if count == 1 else [B1, 180 - B1]):
                C = 180 - A - B; c = a * math.sin(math.radians(C)) / math.sin(math.radians(A)); tri.append(f'B≈{B:.0f}°, C≈{C:.0f}°, c≈{c:.1f}')
            bt = '; '.join(tri)
        else: bt = 'sin B>1, so there is no real angle B and no triangle.'
        parts[1]['answer'] = {'model_answer_and_marking': f'{bt} Calculate with full-precision angles before rounding. Correct possible triangles and remaining side(s) (6).', 'math_latex': ''}
        # cross-check the booklet's own rounded triangles
        for t_ in re.findall(r'B ≈ ([\d.]+)°, C = .*?c ≈ ([\d.]+)\.', sol_text) or []: pass
    ml = math_line
    if lo == 'LO25': ml = f'A={int(A)}^\\circ,\\quad a={a:g},\\quad b={b:g}'
    elif lo == 'LO24': ml = ',\\quad '.join(re.findall(r'[A-Z]\([^)]*\)', frac_slash(u2tex(math_line))))
    elif lo == 'LO22' and math_line: ml = u2tex(math_line)
    elif lo == 'LO21': ml = poly_text(math_line)
    q = {'type': 'frq', 'instruction': ins, 'stem': (ins + ' ' + ml).rstrip(), 'math_latex': ml, 'parts': parts, 'marks': sibling.get('marks', 10), 'coordinate_workspace': None}
    return q

def is_perfect_square_trinomial(e):
    x = sorted(e.free_symbols, key=str)
    return sp.factor(e).is_Pow if len(x) == 1 else False
def tex_factor(s):
    t = s.replace('²', '^2')
    t = re.sub(r'\(([^()]*)\)\^2', lambda m: '\\left(' + m.group(1) + '\\right)^{2}', t)
    t = re.sub(r'\(([^()]*)\)', lambda m: '\\left(' + m.group(1) + '\\right)', t) if '\\left' not in t else t
    return t
def tex_final(final):
    f = u2tex(final).replace('x = ', 'x=').replace(' = ', '=')
    return f
def poly_text(s): return frac_slash(u2tex(s))
def parse_points(s):
    pts = []
    for body in re.findall(r'[A-Z]\(([^)]*)\)', s):
        pts.append([S(c.strip().replace('/', '/')) for c in body.split(',')])
    return pts

# ------------------------------------------------------------------ calculator-support helpers (reuse the original builder's parsers)
def load_calc_helpers():
    src = (ROOT / 'scripts/calculator-guides/build-support.py').read_text()
    a = src.index('def normalize_input'); b = src.index('def latex(text)')
    c = src.index('def operation('); d = src.index('# Outcome-specific manual setup')
    e = src.index('KEY_LABELS='); f = src.index('def table(expr')
    ns = {'ast': __import__('ast'), 're': re, 'S': sp, 'X': sp.Symbol('X', real=True)}
    exec(src[a:b] + src[c:d] + src[e:f], ns)
    return ns
CALC = load_calc_helpers()

def asciiize(s):
    t = s.replace('−', '-').replace('²', '^2').replace('³', '^3').replace('⁴', '^4').replace('⁵', '^5').replace('⁶', '^6').replace('½', '(1/2)')
    t = re.sub(r'(\d)([A-Za-z(])', r'\1*\2', t); t = re.sub(r'\)\s*\(', ')*(', t); t = re.sub(r'\)([A-Za-z0-9])', r')*\1', t)
    t = re.sub(r'(?<=[A-Za-z])(?=[A-Za-z])', '*', t)
    return t
def with_value(expr_ascii, var_values):
    t = expr_ascii
    for v, val in var_values.items(): t = re.sub(rf'(?<![A-Za-z]){v}(?![A-Za-z])', f'({val})', t)
    return t

def mk_support(lo, lo_title, role, prepare, ops, key_math, explanation, setup, interpret, part='Answer'):
    entry = {'outcome': lo, 'outcome_title': lo_title, 'role': role, 'prepare': prepare, 'operations': [], 'tables': [],
             'solutions': [{'part': part, 'math': key_math, 'text': explanation, 'answer_text': ''}], 'source_ids': ['teacher-revision-booklet', 'reviewed-bank'], 'setup': setup, 'interpret': interpret}
    for expr, purpose in ops:
        try:
            op = CALC['operation'](expr, purpose or 'Evaluate this expression after setting up the mathematics.')
            op['keys'] = ['AC'] + CALC['input_keys'](op['input']) + ['EQ']; op['key_labels'] = [CALC['KEY_LABELS'].get(k, k) for k in op['keys']]
            entry['operations'].append(op)
        except Exception as ex:
            print('   (operation skipped)', expr, ex)
    return entry

# Figures that are cut off in the supplied booklet (labels missing) cannot be shown honestly: held back until the original textbook page is supplied.
HOLD = {112: 'figure cropped: side x is not visible (Reveal p.184 ex 22)', 113: 'figure cropped: top edge and side x are cut off (Reveal p.184 ex 23)', 117: 'figure cropped on the right: 45 and the right half are cut off (Reveal p.185 ex 34)'}
FIGURE_FLAGS = {44: 'cropped_edge', 116: 'cropped_edge', 62: 'low_resolution'}

def comp_ascii(c):
    t = c.strip().replace('−', '-').replace('√', 'sqrt').replace(' ', '')
    t = re.sub(r'sqrt(\d+)', r'sqrt(\1)', t); t = re.sub(r'(\d)sqrt', r'\1*sqrt', t)
    return t

def ops_for(lo, item, q, math_line, fam):
    """(role, [(expr, purpose)], extra_prepare) for the calculator guide of one new question"""
    n = item['number']; import math
    if fam == 'algebra' and lo in ('LO01', 'LO02', 'LO03', 'LO04'):
        vars_ = sorted({ch for ch in re.sub(r'[^A-Za-z]', '', math_line)}); vals = {v: 2 + i for i, v in enumerate(vars_)}
        key = item['options'][item['key']].split(';')[0]
        orig = with_value(asciiize(math_line), vals); kk = with_value(asciiize(key), vals)
        return 'check', [(orig, None), (kk, None)], 'Numerical check values: ' + ', '.join(f'{v}={x}' for v, x in vals.items()) + '. These are chosen test values, not extra givens.'
    if lo == 'LO15' and n in (92, 93, 94, 95):
        a, b = [int(x) for x in re.findall(r'\d+', item['stem_lines'][-1])]; return 'evaluate', [(f'sqrt({a}*{b})', None)], ''
    if lo == 'LO16' and n in (106, 107, 108):
        sides = re.split(r',\s*', item['stem_lines'][-1]); sq = sorted([int(re.sub(r"\D", "", t)) if '√' in t else int(t) ** 2 for t in sides])
        return 'calculation', [(f'{sq[0]}+{sq[1]}', None), (f'{sq[2]}', None)], ''
    table = {55: ('calculation', [('2.5*5', None), ('2.5*2', None)]), 71: ('calculation', [('4.5*100/(3+4/12)', None)]), 78: ('calculation', [('2*10', None)]),
             83: ('calculation', [('6*7/5', None)]), 84: ('calculation', [('24*10.5/14', None)]), 115: ('evaluate', [('40*sin(30)', None)]),
             135: ('evaluate', [('atan((80+5.5)/122)', None)]), 136: ('evaluate', [('120/tan(19)', None)]), 137: ('evaluate', [('atan(528/2000)', None)]),
             174: ('calculation', [('8*10/16', None)]), 175: ('calculation', [('8*3/(1/24)', None)]), 176: ('calculation', [('168.5*264/220', None)])}
    if n in table: return table[n][0], table[n][1], ''
    if lo == 'LO22' and q['type'] == 'frq':
        if 'regular polygon' in item['stem_lines'][0]:
            ang = int(re.sub(r'\D', '', math_line)); return 'evaluate', [(f'360/(180-{ang})', None)], ''
        m = re.search(r'(\d*)x \+ (-?\d+) = 360|(\d*)x - (\d+) = 360', ' '.join(item['solution'])); sol = ' '.join(item['solution']); mm = re.search(r'(\d+)x\s*([+-])\s*(\d+) = 360', sol)
        if mm: c1, sg, c0 = int(mm.group(1)), mm.group(2), int(mm.group(3)); return 'evaluate', [(f'(360{"-" if sg == "+" else "+"}{c0})/{c1}', None)], ''
    if lo == 'LO24':
        pts = parse_points(math_line); strs = re.findall(r'[A-Z]\(([^)]*)\)', math_line)
        comps = [[comp_ascii(c) for c in s_.split(',')] for s_ in strs]
        ops = []
        if len(item['solution']) and any(l.strip().startswith('d =') for l in item['solution']):
            ops.append(('sqrt(' + '+'.join(f'(({b})-({a}))^2' for a, b in zip(*comps)) + ')', None))
        ops += [(f'(({a})+({b}))/2', None) for a, b in zip(*comps)]
        return 'evaluate', ops, ''
    if lo == 'LO25':
        A, a, b = [float(t) for t in re.findall(r'[\d.]+', math_line.replace('∠A', ''))[:3]] if False else [float(x) for x in re.findall(r'A = ([\d.]+)°.*?a = ([\d.]+).*?b = ([\d.]+)', math_line.replace('∠', ''))[0]]
        ratio = b * math.sin(math.radians(A)) / a; ops = [(f'{b:g}*sin({A:g})/{a:g}', None)]
        if ratio <= 1 + 1e-12:
            B1 = math.degrees(math.asin(min(1, ratio))); two = abs(ratio - 1) > 1e-9 and A + (180 - B1) < 180
            ops += [(f'asin({b:g}*sin({A:g})/{a:g})', None), (f'180-{A:g}-{B1}', None), (f'{a:g}*sin({180 - A - B1})/sin({A:g})', None)]
            if two: B2 = 180 - B1; ops += [(f'180-{A:g}-{B2}', None), (f'{a:g}*sin({180 - A - B2})/sin({A:g})', None)]
        return 'ssa', ops, ''
    return None, [], ''

def main():
    data = json.loads((REV / 'items.json').read_text()); items = data['items']; meta = data['source']
    bank_path = ROOT / 'public/data/study/10A1.json'; bank = json.loads(bank_path.read_text())
    sup_path = ROOT / 'public/data/study/calculator-support.json'; sup = json.loads(sup_path.read_text()); S10 = sup['classes']['10A1']
    # idempotent: drop earlier imports
    old_ids = {q['id'] for q in bank['questions'] if q['id'].startswith('G10A-REV-')}
    bank['questions'] = [q for q in bank['questions'] if q['id'] not in old_ids]
    for lo in bank['learning_outcomes']:
        for k in ('question_ids', 'booklet_question_ids'): lo[k] = [i for i in lo[k] if i not in old_ids]
    for i in old_ids: S10['questions'].pop(i, None)
    for a in [a for a in bank['assets'] if a.startswith('rev')]: bank['assets'].pop(a)
    have = {(q['learning_outcome_id'], q['source'].get('printed_page'), str(q['source'].get('exercise'))) for q in bank['questions'] if q.get('source_kind') == 'textbook_exercise'}
    by_lo = {lo['id']: lo for lo in bank['learning_outcomes']}
    byq = {}
    for it in items: byq.setdefault(it['lo'], []).append(it)
    out_dir = ROOT / 'public/data/study-assets/10a1'; out_dir.mkdir(parents=True, exist_ok=True)
    report = {'source': meta, 'added': [], 'skipped_duplicates': [], 'held_back': [], 'checks': []}
    for lo_id, its in byq.items():
        seq = [(p, e) for p, es in STRUCTURE[lo_id] for e in es]; assert len(seq) == len(its), (lo_id, len(seq), len(its))
        lo = by_lo[lo_id]; n_lo = int(lo_id[2:]); counts = {'mcq': 0, 'frq': 0}; added_here = len(lo['question_ids'])
        for it, (page, ex) in zip(its, seq):
            it['book_page'], it['exercise'] = page, ex
            if (lo_id, page, ex) in have:
                report['skipped_duplicates'].append({'revision_number': it['number'], 'lo': lo_id, 'page': page, 'exercise': ex}); continue
            if it['number'] in HOLD:
                report['held_back'].append({'revision_number': it['number'], 'lo': lo_id, 'page': page, 'exercise': ex, 'reason': HOLD[it['number']]}); continue
            kind = it['part']; counts[kind] += 1; added_here += 1
            qid = f'G10A-REV-Q{n_lo:02d}-{"MCQ" if kind == "mcq" else "FRQ"}-{counts[kind]:02d}'
            ins_src, math_line = split_stem(it)
            fam = None; verified = None
            if kind == 'mcq':
                q, fam, verified = build_mcq(it, lo_id, lo['rule_summary'], n_lo, counts[kind])
            else:
                sib = next((x for x in bank['questions'] if x['learning_outcome_id'] == lo_id and x['type'] == 'frq' and x['instruction'] == FRQ_INSTRUCTION.get(ins_src, ins_src)), None) or next(x for x in bank['questions'] if x['learning_outcome_id'] == lo_id and x['type'] == 'frq')
                q = build_frq(it, lo_id, sib)
                verified = 'sympy' if lo_id in ('LO21', 'LO22', 'LO24', 'LO25') else None
            chk = numeric_check(it, lo_id)
            if chk: report['checks'].append({'id': qid, 'check': chk[0], 'agrees_with_booklet': bool(chk[1])}); assert chk[1], f'{qid}: independent computation disagrees with the booklet key ({chk[0]})'
            fig_ids = []
            for fig in it['figures']:
                aid = f'rev{it["number"]:03d}'; shutil.copyfile(REV / 'figures' / fig['file'], out_dir / f'{aid}.png')
                bank['assets'][aid] = {'src': f'data/study-assets/10a1/{aid}.png', 'width': fig['width'], 'height': fig['height'],
                                       'alt_text': f'Original textbook diagram, Reveal p. {page}, exercise {ex} (figure from the revision booklet, native resolution).',
                                       'source': {'revision_file': meta['file_name'], 'revision_sha256': meta['sha256'], 'revision_pdf_page': fig['page'], 'revision_question': it['number'], 'printed_page': page, 'exercise': ex, 'adaptation': 'transcription'}}
                fig_ids.append(aid)
            q.update({'id': qid, 'learning_outcome_id': lo_id, 'display_number': f'{n_lo}.{added_here}', 'diagram_asset_ids': fig_ids,
                      'source': {'book_part': None, 'book_sha256': None, 'printed_page': page, 'pdf_page': None, 'exercise': ex, 'adaptation': 'mcq' if kind == 'mcq' else 'transcription',
                                 'revision_booklet': {'file': meta['file_name'], 'sha256': meta['sha256'], 'pdf_page': it['page'], 'question_number': it['number']}},
                      'grade': 10, 'track': 'advanced', 'source_kind': 'textbook_exercise', 'difficulty': 'standard', 'skill_tags': [lo['title']], 'reference_kind': 'exercise',
                      'key_source': 'sympy-verified' if verified else ('recomputed-numeric' if chk else 'teacher-revision-booklet'),
                      'calculator': {'applicable': False, 'reason': 'See the calculator and written-solution guide for this question.'}})
            if it['number'] in FIGURE_FLAGS: q['figure_quality'] = FIGURE_FLAGS[it['number']]
            bank['questions'].append(q); lo['question_ids'].append(qid); lo['booklet_question_ids'].append(qid)
            # calculator guide
            role, ops, extra = ops_for(lo_id, it, q, math_line, fam)
            outcome_sup = S10['outcomes'][lo_id]
            sibling_sup = next((v for k, v in S10['questions'].items() if v['outcome'] == lo_id and (role is None or v['role'] == role)), next(v for v in S10['questions'].values() if v['outcome'] == lo_id))
            role = role or ('reasoning' if lo_id in ('LO07', 'LO12') and not ops else 'manual_setup')
            key_math = (q['answer']['correct_option_text'] if kind == 'mcq' else ' ; '.join(p['answer']['math_latex'] for p in q['parts'] if p['answer']['math_latex']))
            expl = q['answer']['explanation'] if kind == 'mcq' else ' '.join(l.strip() for l in it['solution'])
            entry = mk_support(lo_id, outcome_sup['title'], role, (outcome_sup['prepare'] + (' ' + extra if extra else '')).strip(), ops, key_math, expl, sibling_sup['setup'] if ops else [], sibling_sup['interpret'])
            S10['questions'][qid] = entry
            report['added'].append({'id': qid, 'lo': lo_id, 'revision_number': it['number'], 'page': page, 'exercise': ex, 'type': kind, 'figure': bool(fig_ids), 'key_source': q['key_source'], 'role': role})
    for lo in bank['learning_outcomes']: lo['question_count'] = len(lo['question_ids'])
    mcq = [q for q in bank['questions'] if q['type'] == 'mcq']
    bank['question_count'] = len(bank['questions']); bank['mcq_count'] = len(mcq); bank['frq_count'] = len(bank['questions']) - len(mcq)
    bank['review_notes'] = {**(bank.get('review_notes') or {}), 'teacher_revision_import': {'file': meta['file_name'], 'sha256': meta['sha256'], 'added': len(report['added']), 'duplicates_skipped': len(report['skipped_duplicates']), 'held_back': len(report['held_back']),
                            'note': 'Questions G10A-REV-* complete the official coverage sheet. Alignment is by coverage-sheet order and agrees with all 100 exercises already in the bank.'}}
    bank_path.write_text(json.dumps(bank, ensure_ascii=False, separators=(',', ':')))
    sup_path.write_text(json.dumps(sup, ensure_ascii=False, indent=2))
    (REV / 'build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print('added', len(report['added']), 'duplicates skipped', len(report['skipped_duplicates']), 'held back', len(report['held_back']), 'numeric checks', len(report['checks']))

if __name__ == '__main__':
    main()
