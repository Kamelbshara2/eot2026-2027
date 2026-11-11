#!/usr/bin/env python3
"""Independent maths re-check of MCQ keys on every class (teacher request 2026-11-11).

For questions whose statement and options are LaTeX:
  equation in one unknown + numeric/set options  -> solve; the key must equal the solution (set) and no other option may
  "simplify / expand / rewrite / factor / distribute" + expression options -> the key must be equivalent, no other option
  "evaluate" with given values in the statement -> the key must equal the value
Anything that cannot be parsed is skipped (counted). Prints KEY-WRONG and AMBIGUOUS findings for manual review.
"""
import json, re, signal, sys
from pathlib import Path
import sympy as sp
from sympy.parsing.latex import parse_latex
ROOT = Path(__file__).resolve().parent.parent
CLASSES = sys.argv[1:] or ['9G3', '9A', '10G3', '10A1', '11G', '11A', '12G', '12A']


class TO(Exception): pass


def _alarm(*_): raise TO()


signal.signal(signal.SIGALRM, _alarm)


def clean(t):
    t = str(t or '').strip().rstrip('.').replace('−', '-').replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac').replace('\\left', '').replace('\\right', '')
    t = re.sub(r'\\(?:,|;|!|quad|qquad| )', ' ', t).replace('\\displaystyle', '')
    t = re.sub(r'\\frac(\d)(\d)', r'\\frac{\1}{\2}', t)
    t = re.sub(r'\\sqrt(\d+)', r'\\sqrt{\1}', t)
    t = ''.join(c if c.startswith('\\') else c.replace('d', '\\delta ') for c in re.split(r'(\\[a-zA-Z]+)', t))   # variable d is not a differential (3dt)
    t = re.sub(r'(?<!\\)\b([a-zA-Z0-9}])\s*\(', r'\1\\cdot(', t)   # 2k(k+2): product, not a function call
    t = re.sub(r'\)\s*\(', r')\\cdot(', t)
    return t.strip()


def P(t):
    t = clean(t)
    if not t or re.search(r'\\text|\\begin|\\mathbb|\\cup|\\infty|\\lfloor|\\pm|\\le|\\ge|<|>|\\ne|\\sin|\\cos|\\tan|\\log|\\ln|\\int|\\lim|\\sum|\\prime|\'|\\sqrt\[', t): return None
    try:
        e = parse_latex(t)
        return e
    except Exception:
        return None


def P_set(t):   # "\{-6,3\}" or "x=2, x=-3" or "-6, 3"
    t = clean(t)
    t = re.sub(r'^\\\{|\\\}$', '', t)
    if re.search(r'[a-z]\s*=', t): t = ','.join(re.sub(r'^[a-z]\s*=', '', s.strip()) for s in t.split(','))
    vals = []
    for s in re.split(r',(?![^{]*\})', t):
        if not s.strip(): continue
        e = P(s)
        if e is None or e.free_symbols: return None
        vals.append(sp.nsimplify(e))
    return set(vals) if vals else None


KW_EQUIV = re.compile(r'gives the product|sum or difference|simplif|expand|rewrite|factor|distributiv|multiply|combine like|equivalent|product of the (?:binomials|polynomials)|write .* standard form', re.I)
KW_SKIP = re.compile(r'values of|deriv|integral|inverse|asymptote|domain|range|slope|intercept|vertex|graph|zero|root|tangent|limit|differen|rate|sequence|term|probab', re.I)


def check(q):
    ins = q.get('instruction') or ''; m = q.get('math_latex') or ''
    opts = q.get('options') or []
    if not m or not opts or any(not o.get('math_latex') for o in opts): return None
    key = q['answer']['correct_option_id']
    # equations in one unknown
    if m.count('=') == 1 and not KW_SKIP.search(ins) and not re.search(r'\bsolve for [a-z]\b', ins, re.I):
        l, r = (P(s) for s in m.split('='))
        if l is None or r is None: return None
        if l.is_Symbol and r.is_number: return None   # given data such as h=5
        fs = (l - r).free_symbols
        if len(fs) != 1: return None
        x = fs.pop()
        sol = sp.solveset(sp.Eq(l, r), x, sp.S.Reals)
        if not isinstance(sol, sp.FiniteSet): return None
        sol = {sp.nsimplify(v) for v in sol}
        good = []
        for o in opts:
            s = P_set(o['math_latex'])
            if s is None: return None
            single = re.search(r'which value|satisf|one solution|a solution', ins, re.I)
            if re.search(r'round|nearest|decimal', ins, re.I):
                close = lambda A, B: len(A) == len(B) and all(any(abs(float(a) - float(b)) < 0.006 for b in B) for a in A)
                if close(s, sol) or (single and len(s) == 1 and any(abs(float(next(iter(s))) - float(v)) < 0.006 for v in sol)): good.append(o['id'])
            elif s == sol or (single and len(s) == 1 and s <= sol): good.append(o['id'])
        return ('equation', good, key, str(sol))
    # expression equivalence
    if '=' not in m and KW_EQUIV.search(ins) and not KW_SKIP.search(ins):
        e = P(m)
        if e is None: return None
        good = []
        for o in opts:
            t = o['math_latex'].split('=')[-1] if re.match(r'^[a-zA-Z]\(?[a-z]?\)?\s*=', o['math_latex']) else o['math_latex']
            oe = P(t)
            if oe is None: return None
            if sp.simplify(sp.expand(oe - e)) == 0: good.append(o['id'])
        return ('equivalent', good, key, '')
    return None


def main():
    stats = {'checked': 0, 'ok': 0}; findings = []
    for c in CLASSES:
        b = json.loads((ROOT / f'public/data/study/{c}.json').read_text())
        for q in b['questions']:
            if q['type'] != 'mcq': continue
            signal.alarm(8)
            try: r = check(q)
            except Exception: r = None
            finally: signal.alarm(0)
            if r is None: continue
            kind, good, key, extra = r; stats['checked'] += 1
            if good == [key]: stats['ok'] += 1; continue
            findings.append((c, q['id'], kind, 'KEY-WRONG' if key not in good else 'AMBIGUOUS', f'key {key}, correct options {good} {extra}', q['math_latex'][:70]))
    for f in findings: print(*f, sep=" | ")
    if "--ok-ids" in sys.argv: pass
    print(stats, len(findings), 'findings')


if __name__ == '__main__':
    main()
