#!/usr/bin/env python3
"""Calculator policy (teacher request 2026-11-11): the calculator guide appears ONLY where a calculator is really used.

USE   : outcomes whose work needs a calculator (trigonometry values, logs/e, normal areas, decimal rounding of
        roots, growth/decay, tables for graphing, distance in space, Law of Sines, ...), plus any question that asks
        for a rounded decimal answer.
HAND  : everything else (formulas, literal equations, properties, factoring/expanding, exact radicals, exact trig
        of special angles, probability with fractions, derivatives by rule, ...). Their entries become
        role 'by_hand' with no key sequences, and the booklet hides the calculator button for them.
Missing keys on a USE question are taken from its verified worked solution: a step '<numeric expression> \\approx v'
is converted to a key sequence only when the expression evaluates to v (to the shown rounding).
usage: python3 scripts/calculator-guides/calculator-policy.py [--write]
"""
import importlib.util, json, re, sys
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parents[2]
_src = (ROOT / 'scripts/calculator-guides/build-support.py').read_text()
def _grab(name):   # copy one top-level helper (def or assignment) from build-support.py without running its build
    m = re.search(r'^(def ' + name + r'\(.*?|' + name + r'=.*?)(?=^\S)', _src, re.S | re.M); return m.group(1)
class _BS: pass
bs = _BS(); _ns = {'re': re, 'ast': __import__('ast'), 'S': S, 'X': S.Symbol('X', real=True)}
for _n in ('normalize_input', 'numeric', 'operation', 'KEY_LABELS', 'input_keys'):
    _code = _grab(_n)
    if _n == 'numeric':
        _code = _code.replace("if f=='sqrt':return S.sqrt(a)", "if f=='sqrt':return S.sqrt(a)\n            if f=='ln':return S.log(a)")
        _code = _code.replace("if isinstance(n,ast.Name) and n.id in ['X','x']: return X", "if isinstance(n,ast.Name) and n.id in ['X','x']: return X\n        if isinstance(n,ast.Name) and n.id=='pi': return S.pi")
    if _n == 'input_keys': _code = _code.replace("if isinstance(n,ast.Name) and n.id in ['X','x']:return ['ALPHA','RP']", "if isinstance(n,ast.Name) and n.id in ['X','x']:return ['ALPHA','RP']\n        if isinstance(n,ast.Name) and n.id=='pi':return ['SHIFT','EXP']").replace("if f=='sqrt':return ['SQRT']+walk(n.args[0])+['RIGHT']", "if f=='sqrt':return ['SQRT']+walk(n.args[0])+['RIGHT']\n            if f=='ln':return ['LN']+walk(n.args[0])+['RP']")
    exec(_code, _ns)
for _n in ('operation', 'KEY_LABELS', 'input_keys'): setattr(bs, _n, _ns[_n])
WRITE = '--write' in sys.argv

USE = {
    '9G3': {'LO09', 'LO21', 'LO22', 'LO24', 'LO25', 'LO26'},
    '9A': {'LO24', 'LO25'},
    '10G3': {'LO10', 'LO14', 'LO16', 'LO18', 'LO19', 'LO25'},
    '10A1': {'LO18', 'LO19', 'LO20', 'LO24', 'LO25'},
    '11G': {'LO14', 'LO15', 'LO23', 'LO24'},
    '11A': {'LO05', 'LO06', 'LO21', 'LO22', 'LO24', 'LO25'},
    '12G': {'LO03', 'LO06', 'LO17', 'LO24', 'LO25'},
    '12A': {'LO01', 'LO25'},
}
# questions in a calculator outcome whose answer is exact or conceptual: solved by hand
BY_HAND = {'10G3-REV-LO19-01', '11A-Q22-added-01', '11A-Q22-added-02', '11A-Q22-added-03', '11A-Q24-empirical', '11A-Q25-trig7', '11A-Q25-trig8', '11A-Q25-trig11',
           '12G-p09-Ex1-1', '12G-p09-Ex2-1', '12G-p09-Ex1-2', '12G-p10-Ex2-1', '12G-p10-Q1-1', '12G-p10-Q2-1', '12G-p11-Q3-1', '12G-p11-Q4-1', '12G-p11-Q5-1', '12G-p11-Q6-1',
           '12G-en-Q016', '12G-en-Q017', '12G-en-Q021', '12G-en-Q022', '12G-en-Q023', '12G-en-Q024', '12G-p16-Ex2-1', '12G-p16-Ex1-1', '12G-p17-Ex2-1', '12G-p40-Ex6-1',
           '12G-en-Q108', '12G-en-Q109', '12G-en-Q110', '12G-p55-9/21-1', '12G-p56-11-1', '12G-p57-Ex5-1', '12G-p58-Q17-1'}
# real calculator work whose worked solution states the values but not the expression: expressions written here
MANUAL_OPS = {
    'G10A-REV-Q18-MCQ-03': ['5/tan(59)', '5/sin(59)'],
    '11G-Q23-added-01': ['12*sin(35)', '12*cos(35)', '(1/2)*(12*sin(35))*(12*cos(35))'],
    '11G-Q23-added-02': ['14*sin(40)', '14*cos(40)', '(1/2)*(14*sin(40))*(14*cos(40))'],
    '12A-p02-Q9-1': ['sqrt(1.5^2+(sqrt(10)/2-1)^2)', 'sqrt(1.5^2+(2-sqrt(10)/2)^2)'],
    '12A-p03-Q10-1': ['sqrt(0.5^2+(1-2/3)^2)', 'sqrt(0.5^2+(2/3-1/2)^2)'],
    '12A-p03-Q11-1': ['sqrt(2^2+4^2)', '2*sqrt(2^2+4^2)'],
    '12A-p02-Q7-1': ['sqrt((pi/4)^2+(1-sqrt(2)/2)^2)', 'sqrt((pi/4)^2+(sqrt(2)/2)^2)'], '12A-p02-Q8-1': ['sqrt((pi/2)^2+1)', '2*sqrt((pi/2)^2+1)'],
    '12A-p65-Q35-1': ['100*ln(3)'], '12A-p66-Q36-1': ['100*ln(3)'],
    '9G-Q24-p215-variant-variant': ['-(1/2)*(-2)+3', '-(1/2)*(2)+3', '-(1/2)*(4)+3'],
}
ROUNDING = re.compile(r'nearest (tenth|hundredth|thousandth|whole|degree|foot|metre|meter|yard|cent)|round|decimal place', re.I)
REASON = {
    'hand': ('This question is solved by hand: the steps are short and exact, and the method itself is what is being assessed. No calculator is needed.',
             'هذا السؤال يُحل يدوياً: الخطوات قصيرة ودقيقة، والطريقة نفسها هي المقصودة بالتقييم. لا حاجة للحاسبة.'),
}


def to_input(tex):
    """LaTeX numeric expression -> calculator input syntax understood by build-support (degrees for trig)."""
    t = tex.replace('\\left', '').replace('\\right', '').replace('\\,', '').replace('\\ ', '').replace('\\cdot', '*').replace('\\times', '*')
    t = re.sub(r'\^\\circ|°', '', t)
    t = t.replace('\\!', '')
    t = re.sub(r'\\(sin|cos|tan)\^\{-1\}', r'a\1', t)   # inverse trig (argument may be a fraction)
    t = re.sub(r'\\[dt]?frac(\d)(\d)', r'((\1)/(\2))', t)
    for _ in range(3): t = re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}', r'((\1)/(\2))', t)
    t = re.sub(r'\\ln\s*\(?([0-9.]+)\)?', r'ln(\1)', t)
    t = re.sub(r'\\sqrt\{([^{}]*)\}', r'sqrt(\1)', t)
    t = re.sub(r'\\(sin|cos|tan)\^\{-1\}\s*\(?([^()]*?)\)?(?=$|[+\-*/])', r'a\1(\2)', t)
    t = re.sub(r'\\(sin|cos|tan)\s*\(?([0-9.]+)\)?', r'\1(\2)', t)
    t = t.replace('{', '(').replace('}', ')').replace('\\pi', 'pi')
    t = re.sub(r'(?<=[0-9)])\s*(?=[(a-z])', '*', t)
    if re.search(r'[A-Za-z]', re.sub(r'a?(sin|cos|tan)|sqrt|ln|pi', '', t)): return None
    return t


def derive_ops(q):
    """Numeric expressions written in the verified worked solution -> calculator operations (max 3, trig/roots first)."""
    steps = list((q.get('answer') or {}).get('steps') or []) + [s for p in q.get('parts', []) for s in (p['answer'].get('steps') or [])]
    cands, seen = [], set()
    for s in steps:
        tex = (s.get('latex') or '').replace('\\dfrac', '\\frac').replace('\\left', '').replace('\\right', '')
        for seg in re.split(r'\\approx|=|\\Rightarrow|\\quad|,\\\s|\\to(?![a-z])|\\le(?![a-z])|\\ge(?![a-z])|<|>', tex):
            seg = seg.strip().strip(',')
            if not seg or not re.search(r'\d', seg) or not re.search(r'[+\-*/^]|\\frac|\\sqrt|\\cdot|\\sin|\\cos|\\tan|\(', seg): continue
            inp = to_input(seg)
            if not inp or inp in seen or re.fullmatch(r'-?[0-9.]+', inp): continue
            if re.fullmatch(r'-?\s*\(\(\d+\)/\(\d+\)\)', inp): continue   # a plain fraction is not calculator work
            if not re.search(r'sin|cos|tan|sqrt|ln|pi|\^|\.|/', inp) and len(re.findall(r'[+\-*]', inp.lstrip('-'))) <= 1: continue   # one step of whole-number arithmetic
            try: op = bs.operation(inp, 'Evaluate this expression from the worked solution, then round as the question asks.')
            except Exception: continue
            seen.add(inp)
            op['keys'] = ['AC'] + bs.input_keys(op['input']) + ['EQ']; op['key_labels'] = [bs.KEY_LABELS.get(k, k) for k in op['keys']]
            cands.append((0 if re.search(r'sin|cos|tan|sqrt|\.', inp) else 1, -len(inp), op))
    return [c[2] for c in sorted(cands, key=lambda c: (c[0], c[1]))[:3]]


def quadratic_route(q):
    """Equation mode (MENU > Equation/Func > Polynomial > degree 2) from the worked solution: 'a=.., b=.., c=..' or the
    first 'ax^2+bx+c=0' (any one letter, possibly after =>)."""
    steps = list((q.get('answer') or {}).get('steps') or []) + [s_ for p in q.get('parts', []) for s_ in (p['answer'].get('steps') or [])]
    coeffs = None
    for st in steps:
        t = (st.get('latex') or '').replace('\\,', '').replace('\\quad', ' ').replace('\\ ', ' ')
        m = re.search(r'a=(-?\d+),\s*b=(-?\d+),\s*c=(-?\d+)', t)
        if m: coeffs = [S.Integer(m.group(k)) for k in (1, 2, 3)]; break
        seg = re.split(r'\\Rightarrow', t)[-1]
        m = re.match(r'^\s*([-+0-9a-z^{}\s]+)=\s*0\s*$', seg)
        if not m: continue
        letters = set(re.findall(r'[a-z]', m.group(1)))
        if len(letters) != 1: continue
        v = S.Symbol(letters.pop())
        try: e = S.expand(S.sympify(re.sub(r'(\d)([a-z])', r'\1*\2', m.group(1).replace('^', '**').replace('{', '(').replace('}', ')')), locals={str(v): v}))
        except Exception: continue
        if S.degree(e, v) != 2: continue
        coeffs = [e.coeff(v, k) for k in (2, 1, 0)]; break
    if not coeffs: return None
    a, b, c = coeffs; x = S.Symbol('x'); e = a * x**2 + b * x + c
    keys = ['MENU', 'NEG', '2', '2'] + sum([(['NEG'] if v < 0 else []) + list(str(abs(v))) + ['EQ'] for v in (a, b, c)], []) + ['EQ']
    roots = sorted(S.solve(e, x), key=lambda r: complex(S.N(r)).real)
    return {'keys': keys, 'coefficients': [str(a), str(b), str(c)], 'polynomial': S.latex(e) + '=0', 'roots': [S.latex(r) for r in roots], 'discriminant': str(b * b - 4 * a * c)}


def main():
    sup = json.loads((ROOT / 'public/data/study/calculator-support.json').read_text())
    report = {'use': 0, 'hand': 0, 'derived': 0, 'use_without_keys': []}
    for c, use in USE.items():
        bank = json.loads((ROOT / f'public/data/study/{c}.json').read_text()); Q = {q['id']: q for q in bank['questions']}
        LO_TITLE = {lo['id']: lo['title'] for lo in bank['learning_outcomes']}
        for qid, g in sup['classes'][c]['questions'].items():
            q = Q[qid]
            text = ' '.join([q.get('instruction', ''), q.get('stem', '')] + [p.get('prompt', '') for p in q.get('parts', [])])
            rounding = bool(ROUNDING.search(text))
            route = quadratic_route(q) if c == '12G' and g['outcome'] in ('LO03', 'LO06') else None
            if route:
                g.update(route, role='quadratic', use_calculator=True, operations=[], tables=[]); report['use'] += 1; continue
            asks = bool(re.search(r'calculator', text, re.I))   # the question itself tells students to use a calculator
            uses = asks or qid not in BY_HAND and (g['outcome'] in use or qid in MANUAL_OPS or (rounding and (g.get('operations') or derive_ops(q))))
            if not uses:
                g.update(role='by_hand', use_calculator=False, operations=[], tables=[], prepare=REASON['hand'][0], prepare_ar=REASON['hand'][1])
                g.pop('keys', None); report['hand'] += 1; continue
            g['use_calculator'] = True; report['use'] += 1
            title = LO_TITLE[g['outcome']]
            if not re.search(r'similar|proportion|ratio', title, re.I):   # drop template lines that belong to other topics
                g['setup'] = [l for l in g.get('setup', []) if not re.search(r'proportion|corresponding sides', l, re.I)]
            if g.get('role') in ('reasoning', 'manual_setup', 'by_hand'): g['role'] = 'evaluate'
            if qid in MANUAL_OPS:
                g['operations'] = []
                for e in MANUAL_OPS[qid]:
                    op = bs.operation(e, 'Evaluate this expression from the worked solution, then round as the question asks.')
                    op['keys'] = ['AC'] + bs.input_keys(op['input']) + ['EQ']; op['key_labels'] = [bs.KEY_LABELS.get(k, k) for k in op['keys']]
                    g['operations'].append(op)
            if not (g.get('operations') or g.get('tables') or g.get('keys')):
                ops = derive_ops(q)
                if ops: g['operations'] = ops; report['derived'] += 1
                else:   # no real calculator work in the verified solution: the answer is exact, so it is solved by hand
                    g.update(role='by_hand', use_calculator=False, operations=[], tables=[], prepare=REASON['hand'][0], prepare_ar=REASON['hand'][1]); g.pop('keys', None)
                    report['use'] -= 1; report['hand'] += 1; report['use_without_keys'].append(qid)
            if g.get('use_calculator') and ('pi' in ' '.join(op['input'] for op in g.get('operations', [])) or (c == '12A' and g['outcome'] == 'LO01')):
                tip = 'Enter π with SHIFT then ×10ˣ (the π key); do not type 3.14, so the result stays exact until the final rounding.'
                if tip not in g.get('setup', []): g['setup'] = g.get('setup', []) + [tip]
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in report.items()})
    print('USE but no keys:', report['use_without_keys'][:60])
    if WRITE: (ROOT / 'public/data/study/calculator-support.json').write_text(json.dumps(sup, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
