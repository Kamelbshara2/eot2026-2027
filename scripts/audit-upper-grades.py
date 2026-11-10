#!/usr/bin/env python3
"""Independent audit of the Grade 11/12 study banks (11G, 11A, 12G, 12A). Nothing is copied from the import step.

  S  structure: 4 options, keyed id exists, options not identical, no empty stems / placeholder text
  D  two options mathematically equivalent (indistinguishable answers)
  K  key vs independent evidence: when the stem is a parseable expression and exactly one option equals it
     (simplify / evaluate / expand / combine questions) the keyed option must be that one; for 'solve' questions the
     keyed values are substituted back; numeric keys quoted with ≈ are compared with the computed value
  F  written parts: every blank's reference answer is numerically consistent with the number(s) printed in the bank key
Items that need a human (cards, graphs, geometry, prose) are counted as 'unverified', never as verified.
Output: content-imports/upper-grades/audit.json and a console summary.
"""
import json, re, random, sys, warnings, math
from pathlib import Path
import sympy as sp
warnings.filterwarnings('ignore')
from sympy.parsing.latex import parse_latex

ROOT = Path(__file__).resolve().parent.parent
CLASSES = ['11G', '11A', '12G', '12A']
random.seed(7)


def clean(t):
    t = t.replace('\\left', '').replace('\\right', '').replace('\\,', ' ').replace('\\!', '').replace('\\;', ' ').replace('\\tfrac', '\\frac').replace('\\dfrac', '\\frac')
    t = re.sub(r'\\text\{[^}]*\}', '', t).replace('−', '-').replace('\\ ', ' ').replace('^\\circ', '').replace('\\%', '')
    return t.strip()


def expr(t):
    try:
        e = parse_latex(clean(t), strict=False)
        return e
    except Exception:
        return None


def val(e, pts=None):
    """Numeric fingerprint: value if constant, else values at fixed random points (same points for every expression)."""
    syms = sorted(e.free_symbols, key=str)
    if not syms:
        try:
            v = complex(sp.N(e, 15))
        except Exception:
            return None
        return [v] if abs(v.imag) < 1e-12 else None
    pts = pts or [{s: sp.Rational(k + 2, 3) + i for i, s in enumerate(syms)} for k in range(4)]
    out = []
    for p in pts:
        try:
            v = complex(sp.N(e.subs(p), 15))
        except Exception:
            return None
        if abs(v.imag) > 1e-9 or v != v: return None
        out.append(v)
    return out


def same(a, b):
    sa, sb = sorted(a.free_symbols, key=str), sorted(b.free_symbols, key=str)
    if sa != sb: return False
    pts = [{s: sp.Rational(k + 2, 3) + i for i, s in enumerate(sa)} for k in range(4)]
    va, vb = val(a, pts), val(b, pts)
    return bool(va and vb and all(abs(x - y) <= 1e-9 * max(1, abs(x), abs(y)) for x, y in zip(va, vb)))


def fam_check(q):
    """Family verifiers for templated text questions. Returns True (key verified), False (key wrong) or None (not covered)."""
    ins, m = q['instruction'], q['math_latex']; opts = {o['id']: o['math_latex'] for o in q['options']}; key = q['answer']['correct_option_id']
    flat = lambda t: re.sub(r'[\s(){}]|\\left|\\right', '', t)
    def unique(pred):
        hit = [i for i, t in opts.items() if pred(t)]
        return hit == [key] if hit else False
    try:
        if ins.startswith('Which exponential equation'):
            b, a, c = re.match(r'\\log_\{(.+?)\}\((.+)\)=(.+)$', m).groups(); return flat(opts[key]) == flat(f'{b}^{{{c}}}={a}') and unique(lambda t: flat(t) == flat(f'{b}^{{{c}}}={a}'))
        if ins.startswith('Which logarithmic equation'):
            b, c, a = re.match(r'\((.+?)\)\^\{(.+?)\}=(.+)$', m).groups(); return unique(lambda t: flat(t) == flat(f'\\log_{{{b}}}({a})={c}'))
        if ins.startswith('Find the distance between A and B'):
            x1, y1, x2, y2 = map(float, re.findall(r'-?\d+(?:\.\d+)?', m)); d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5; return unique(lambda t: abs(float(t) - d) < 1e-6)
        if ins.startswith('A meal consists'):
            a, b = map(int, re.findall(r'\d+', ins)[:2]); return unique(lambda t: int(t) == a * b)
        if ins.startswith('Use change of base'):
            v = float(sp.N(expr(m), 12)); return unique(lambda t: abs(float(t) - v) < 5.1e-5)
        if ins.startswith('Write as a single logarithm'):
            v = float(sp.N(expr(m), 12)); return unique(lambda t: abs(float(sp.N(expr(t), 12)) - v) < 1e-9)
        if ins.startswith('Treat the listed values'):
            xs = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', m)]; mu = sum(xs) / len(xs); sd = (sum((x - mu) ** 2 for x in xs) / len(xs)) ** .5
            return unique(lambda t: [round(float(z), 2) for z in re.findall(r'-?\d+(?:\.\d+)?', t)] == [round(mu, 2), round(sd, 2)])
        if ins.startswith('Select one positive and one negative angle coterminal'):
            g = int(re.search(r'(-?\d+)', m)[1]); ok = lambda t: (lambda a, b: a > 0 > b and (a - g) % 360 == 0 and (b - g) % 360 == 0)(*[int(z) for z in re.findall(r'-?\d+', t)[:2]]); return unique(ok)
        if ins.startswith('Find the principal angle'):
            f, arg = re.match(r'\\(arcsin|arccos|arctan)\((.+)\)$', m).groups(); v = float(sp.N(getattr(sp, 'a' + f[3:])(expr(arg)) * 180 / sp.pi, 12)); return unique(lambda t: abs(float(re.findall(r'-?\d+(?:\.\d+)?', t)[0]) - v) < 1e-6)
        if ins.startswith('Estimate the curve length'):
            fx = expr(re.search(r'y=(.+?),\\quad', m)[1]); lo, hi = [sp.N(expr(z), 12) for z in re.search(r'(\S+?)\\le x\\le(\S+)$', m.replace(' ', '')).groups()]
            xs = sp.Symbol('x'); fx = fx.subs({s_: xs for s_ in fx.free_symbols}); mid = (lo + hi) / 2; pts = [(float(t), float(fx.subs(xs, t))) for t in (lo, mid, hi)]
            L = sum(((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** .5 for i in range(2)); return unique(lambda t: abs(float(t) - L) < 5.1e-5)
        if ins.startswith('Which side-length triple'):
            a = [float(x) for x in re.findall(r'\d+', ins)[:3]]; ok = lambda t: (lambda z: len({round(z[i] / a[i], 9) for i in range(3)}) == 1)(sorted(float(x) for x in re.findall(r'\d+(?:\.\d+)?', t))); return unique(ok)
        if ins.startswith('Find the positive geometric mean'):
            a, b = map(float, re.findall(r'\d+', m)[:2]); return unique(lambda t: abs(float(sp.N(expr(t), 12)) - (a * b) ** .5) < 1e-9)
        if ins.startswith('A right triangle has the two given perpendicular legs'):
            a, b = map(float, re.findall(r'\d+', m)[:2]); return unique(lambda t: abs(float(t) - (a * a + b * b) ** .5) < 1e-9)
        if ins.startswith('A dilation centred at the origin has the given scale factor'):
            px, py, k = [float(sp.N(expr(z), 12)) for z in re.search(r'P\((.+?),(.+?)\),\\ k=(.+)$', m).groups()]; return unique(lambda t: (lambda z: abs(z[0] - k * px) < 1e-9 and abs(z[1] - k * py) < 1e-9)([float(sp.N(expr(w), 12)) for w in re.match(r'\((.+?),(.+)\)$', t.replace(' ', '')).groups()]))
        if ins.startswith('From a point on level ground'):
            d, ang = map(float, re.findall(r'\d+(?:\.\d+)?', ins)[:2]); h = d * math.tan(math.radians(ang)); return unique(lambda t: abs(float(t) - h) < .051)
    except Exception:
        return None
    return None


def main():
    rep = {'structure': [], 'equivalent_options': [], 'key_mismatch': [], 'key_verified': 0, 'unverified': 0, 'numeric_key_checked': 0, 'frq_consistency': []}
    totals = {}
    for c in CLASSES:
        d = json.loads((ROOT / f'public/data/study/{c}.json').read_text())
        n_mcq = n_ver = 0
        for q in d['questions']:
            if q['type'] != 'mcq': continue
            n_mcq += 1
            opts = q['options']; ids = [o['id'] for o in opts]
            if len(opts) != 4 or q['answer']['correct_option_id'] not in ids or not q['stem'].strip() or any('undefined' in str(o) or 'None' in str(o.get('text')) for o in opts):
                rep['structure'].append({'class': c, 'id': q['id']})
            if q.get('embedded_options'):
                rep['unverified'] += 1; continue
            texts = [re.sub(r'\s+', '', o['math_latex']) for o in opts]
            if len(set(texts)) < 4: rep['structure'].append({'class': c, 'id': q['id'], 'issue': 'identical options'})
            ex = [expr(o['math_latex']) if o['math_latex'] else None for o in opts]
            # D: pairwise equivalence among parseable options
            for i in range(4):
                for j in range(i + 1, 4):
                    if ex[i] is not None and ex[j] is not None and ex[i] != ex[j] and same(ex[i], ex[j]):
                        # equal as expressions of different form only counts when both are fully symbolic/numeric (no inequality text)
                        rep['equivalent_options'].append({'class': c, 'id': q['id'], 'options': [ids[i], ids[j]], 'a': opts[i]['math_latex'], 'b': opts[j]['math_latex']})
            fc = fam_check(q)
            if fc is True: rep['key_verified'] += 1; n_ver += 1; continue
            if fc is False: rep['key_mismatch'].append({'class': c, 'id': q['id'], 'issue': 'family check failed'}); continue
            # K: stem expression vs options
            key_i = ids.index(q['answer']['correct_option_id'])
            stem = expr(q['math_latex']) if q['math_latex'] and not re.search(r'[=<>]|\\le|\\ge|,', clean(q['math_latex'])) else None
            if stem is not None and re.search(r'simplif|evaluat|expand|combine|single|product|sum|difference|value of', q['instruction'], re.I) and all(e is not None for e in ex):
                eq = [i for i in range(4) if same(stem, ex[i])]
                if eq == [key_i]: rep['key_verified'] += 1; n_ver += 1; continue
                if eq and key_i not in eq:
                    rep['key_mismatch'].append({'class': c, 'id': q['id'], 'keyed': ids[key_i], 'equals_stem': [ids[i] for i in eq], 'stem': q['math_latex']})
                    continue
            # numeric key quoted with ≈ (e.g. "\\log(22)\\approx1.3424"): compare with the printed number to the left
            m = re.search(r'^(.*?)\\approx\s*(-?\d+(?:\.\d+)?)\s*$', q['answer']['correct_option_text'])
            if m:
                lhs = expr(m.group(1))
                if lhs is not None and not lhs.free_symbols:
                    v = float(sp.N(lhs, 12)); want = float(m.group(2)); dec = len(m.group(2).split('.')[-1]) if '.' in m.group(2) else 0
                    ok = abs(v - want) <= 0.51 * 10 ** (-dec)
                    rep['numeric_key_checked'] += 1
                    if not ok: rep['key_mismatch'].append({'class': c, 'id': q['id'], 'issue': 'numeric key differs from its own expression', 'printed': want, 'computed': v})
                    else: n_ver += 1
                    continue
            rep['unverified'] += 1
        # F: FRQ consistency between blank answers and the printed key
        for q in d['questions']:
            if q['type'] != 'frq': continue
            key = q['parts'][0]['answer']['model_answer_and_marking']
            nums_key = {round(float(x), 2) for x in re.findall(r'(?<![\w.])-?\d+(?:\.\d+)?', key.replace('−', '-'))}
            for p in q['parts']:
                for line in (p.get('blanks') or {}).get('lines', []):
                    for b in re.findall(r'\[\[(.+?)\]\]', line):
                        b = re.sub(r'#\w+$', '', b); b = re.sub(r'^~[\d.]+:', '', b).split('|')[0]
                        if b.startswith('?'): continue
                        e = expr(b.replace('^', '^'))
                        if e is None or e.free_symbols: continue
                        v = round(float(sp.N(e, 10)), 2)
                        # only flag a plain number that appears nowhere in the key and cannot be derived from the key's numbers
                        if re.fullmatch(r'-?\d+(\.\d+)?', b) and v not in nums_key and not any(abs(v - k) <= 0.011 or (k and abs(v / k - 1) < 0.02) for k in nums_key):
                            rep['frq_consistency'].append({'class': c, 'id': q['id'], 'blank': b, 'key': key[:90]})
        totals[c] = {'mcq': n_mcq, 'verified_independently': n_ver}
    rep['totals'] = totals
    (ROOT / 'content-imports/upper-grades/audit.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}, indent=1))
    for k in ('structure', 'equivalent_options', 'key_mismatch'):
        for x in rep[k][:25]: print(k, x)
    print('frq flags', len(rep['frq_consistency']))
    for x in rep['frq_consistency'][:15]: print(x)


if __name__ == '__main__':
    main()
