#!/usr/bin/env python3
"""Independent audit of the three study banks (public/data/study/*.json).

Checks (all computed, none copied from the generator):
  S  structure: 4 distinct options, one keyed answer, non-empty stems
  D  mathematically equivalent options (two options that are both correct / indistinguishable)
  K  keyed answer vs. independent evidence: the stem itself (expand/simplify/factor families),
     the calculator-support numeric evidence, FRQ model answers, substituted evaluations
  X  duplicated questions
Findings are written to content-imports/study-question-audit.json. Items that need a human
(geometry, graphs, proofs, prose) are counted separately and never reported as verified.
Usage: python3 scripts/audit-study-questions.py [--json-only]
"""
import json, re, sys, itertools, random
from pathlib import Path
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor, split_symbols

ROOT = Path(__file__).resolve().parent.parent
T = standard_transformations + (split_symbols, implicit_multiplication_application, convert_xor)
CLASSES = ['9G3', '10G3', '10A1']
SUP = json.loads((ROOT / 'public/data/study/calculator-support.json').read_text())['classes']

def clean(t):
    t = t.replace('\\left', '').replace('\\right', '').replace('\\,', ' ').replace('\\!', '').replace('\\;', ' ')
    t = re.sub(r'\\(?:cdot|times)', '*', t); t = t.replace('\\div', '/').replace('\\pi', 'pi').replace('−', '-')
    t = re.sub(r'\\(?:text|mathrm)\{[^}]*\}', '', t)
    t = re.sub(r'(\d)\s*j\b', r'\1*j', t)
    for _ in range(8):
        t = re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}', r'((\1)/(\2))', t)
        t = re.sub(r'\\frac(\d)(\d)', r'((\1)/(\2))', t)
        t = re.sub(r'\\sqrt\[(\d+)\]\{([^{}]*)\}', r'((\2)**(1/\1))', t)
        t = re.sub(r'\\sqrt\{([^{}]*)\}', r'sqrt(\1)', t)
        t = re.sub(r'\^\{([^{}]*)\}', r'**(\1)', t)
    t = re.sub(r'\\sqrt(\d)', r'sqrt(\1)', t)
    t = re.sub(r'\^(\d)', r'**\1', t).replace('^', '**').replace('{', '(').replace('}', ')')
    return t.strip()

def one(t):
    t = clean(t)
    if not t or re.search(r'[A-Za-z]{4,}', re.sub(r'sqrt|pi|theta', '', t)) or any(c in t for c in '<>≤≥≈∈∪∞∅'): return None
    if '=' in t: return None
    try:
        e = parse_expr(t, transformations=T, evaluate=True)
        return e if isinstance(e, sp.Basic) and not isinstance(e, (sp.Tuple,)) else None
    except Exception:
        return None

def parse(t):
    """-> list of sympy expressions (comma/quad separated pieces) or None"""
    if t is None: return None
    pieces = [p for p in re.split(r',\s*\\quad|\\quad|;', str(t)) if p.strip()]
    out = [one(p) for p in pieces]
    return out if out and all(o is not None for o in out) else None

PTS = [{}, ]
def equiv(a, b):
    if a is None or b is None or len(a) != len(b): return None
    for x, y in zip(a, b):
        d = sp.expand(x - y)
        if d == 0: continue
        syms = sorted((x.free_symbols | y.free_symbols), key=str)
        ok = True
        rnd = random.Random(7)
        for _ in range(4):
            sub = {s: sp.Rational(rnd.randint(-9, 9), rnd.randint(1, 5)) + sp.Rational(1, 7) for s in syms}
            try:
                if abs(sp.N((x - y).subs(sub))) > 1e-9: ok = False; break
            except Exception:
                return None
        if not ok: return False
    return True

def numeric(e):
    try: return float(sp.N(e[0])) if e and len(e) == 1 else None
    except Exception: return None

findings, stats = [], {}
HUMAN = {}
BASE = {c: {q['id']: q for q in json.loads((ROOT / f'content-imports/textbook-v1-inputs/{f}.json').read_text())['questions']} for c, f in (('9G3', '9g3-term1'), ('10G3', '10g3-term1'), ('10A1', '10a1-term1'))}
def add(sev, cls, qid, kind, msg):
    findings.append({'severity': sev, 'class': cls, 'id': qid, 'kind': kind, 'message': msg})

FAMILY = re.compile(r'product|simplif|expand|equivalent|which expression|distribut|standard form|factor', re.I)

for cls in CLASSES:
    d = json.loads((ROOT / f'public/data/study/{cls}.json').read_text())
    S = SUP[cls]['questions']
    st = stats[cls] = dict(questions=len(d['questions']), mcq=0, frq=0, structure_ok=0, option_pairs=0, key_verified_stem=0, key_verified_calc=0,
                          frq_verified=0, needs_human=0, errors=0, warnings=0)
    seen = {}
    for q in d['questions']:
        qid = q['id']; sup = S.get(qid, {})
        key = (q['stem'].strip(), json.dumps([o['text'] for o in q.get('options', [])]), json.dumps(q.get('diagram_asset_ids')), q.get('math_latex'))
        if key in seen: add('warning', cls, qid, 'X-duplicate', f'identical stem and options to {seen[key]}')
        seen[key] = qid
        if not q['stem'].strip(): add('error', cls, qid, 'S-empty-stem', 'empty stem')
        verified = False
        b = BASE[cls].get(qid)
        if b and q['type'] == 'mcq' and b['type'] == 'mcq':
            ka = next(o for o in q['options'] if o['id'] == q['answer']['correct_option_id']); kb = next((o for o in b['options'] if o['id'] == b['answer']['correct_option_id']), None)
            r = equiv(parse(ka.get('math_latex') or ka['text']), parse(kb.get('math_latex') or kb['text'])) if kb else None
            if r is False: add('error', cls, qid, 'R-key-changed', f'keyed answer differs from the baseline import: now {ka["text"]!r}, before {kb["text"]!r}')
            elif r is None and kb and ka['text'].replace(' ', '') != kb['text'].replace(' ', ''): st['needs_human'] += 0; add('info', cls, qid, 'R-key-unparsed-change', f'could not compare: now {ka["text"]!r}, before {kb["text"]!r}')
            st['baseline_compared'] = st.get('baseline_compared', 0) + 1
        if q['type'] == 'mcq':
            st['mcq'] += 1
            ids = [o['id'] for o in q['options']]
            texts = [o['text'].strip() for o in q['options']]
            if len(q['options']) != 4 or sorted(ids) != ['A', 'B', 'C', 'D']: add('error', cls, qid, 'S-options', f'option ids {ids}')
            elif q['answer']['correct_option_id'] not in ids: add('error', cls, qid, 'S-key-missing', 'keyed option does not exist')
            elif len(set(t.replace(' ', '') for t in texts)) != 4: add('error', cls, qid, 'S-duplicate-text', 'two options have identical text')
            else: st['structure_ok'] += 1
            key_opt = next((o for o in q['options'] if o['id'] == q['answer']['correct_option_id']), None)
            if key_opt and key_opt['text'] != q['answer'].get('correct_option_text'): add('warning', cls, qid, 'S-key-text', 'answer.correct_option_text differs from keyed option text')
            P = {o['id']: parse(o.get('math_latex') or o['text']) for o in q['options']}
            # D: equivalent options
            for a, b in itertools.combinations(ids, 2):
                st['option_pairs'] += 1
                if equiv(P[a], P[b]) is True:
                    kind = 'D-equivalent-to-key' if q['answer']['correct_option_id'] in (a, b) else 'D-equivalent-distractors'
                    add('error' if 'key' in kind else 'warning', cls, qid, kind, f'options {a} and {b} are mathematically equal: {texts[ids.index(a)]}  ==  {texts[ids.index(b)]}')
            # K1: stem family
            stem_e = parse(q.get('math_latex')) if q.get('math_latex') else None
            if stem_e and FAMILY.search(q['instruction']) and key_opt and P.get(key_opt['id']):
                eq = [i for i in ids if equiv(P[i], stem_e) is True]
                if len(eq) == 1 and eq[0] == key_opt['id']: st['key_verified_stem'] += 1; verified = True
                elif len(eq) == 1: add('error', cls, qid, 'K-key-vs-stem', f'only option {eq[0]} equals the stem expression but the key is {key_opt["id"]}')
                elif len(eq) == 0 and not re.search(r'factor|standard form|leading', q['instruction'], re.I):
                    add('warning', cls, qid, 'K-no-option-equals-stem', 'no option is algebraically equal to the stem expression')
            # K3: equations -- the keyed value must satisfy the stem equation and the distractors must not
            ml = q.get('math_latex') or ''
            if key_opt and '=' in ml and not any(c in ml for c in '<>') and re.search(r'satisfies|Solve|solution', q['instruction'], re.I):
                sides = [one(x) for x in ml.replace('\\quad', ' ').split('=')]
                if len(sides) == 2 and all(x is not None for x in sides):
                    fs = sorted(sides[0].free_symbols | sides[1].free_symbols, key=str)
                    m = re.search(r'Solve for ([a-z])', q['instruction'])
                    var = sp.Symbol(m.group(1)) if m else (fs[0] if len(fs) == 1 else None)
                    if var is not None:
                        try:
                            sol = sp.solve(sp.Eq(sides[0], sides[1]), var)
                            rounding = re.search(r'nearest hundredth', q['instruction'], re.I)
                            hits = []
                            for oid in ids:
                                po = P.get(oid)
                                if not po or len(po) != 1: continue
                                if m:      # literal equation: option is an expression for var
                                    ok = any(sp.simplify(po[0] - sv) == 0 for sv in sol)
                                else:
                                    ok = abs(sp.N(sides[0].subs(var, po[0]) - sides[1].subs(var, po[0]))) < (0.006 if rounding else 1e-9) if not (sides[0].subs(var, po[0]).free_symbols) else False
                                if ok: hits.append(oid)
                            if hits == [key_opt['id']]: st['key_verified_eq'] = st.get('key_verified_eq', 0) + 1; verified = True
                            elif hits: add('error', cls, qid, 'K-equation', f'options satisfying the equation {ml}: {hits}, but key is {key_opt["id"]}')
                            elif P.get(key_opt['id']) and all(P[i] for i in ids): add('error', cls, qid, 'K-equation', f'no option satisfies {ml}; key is {key_opt["id"]} ({key_opt["text"]})')
                        except Exception:
                            pass
            # K7: solution sets of equations; K8: "values of k" for integer factoring
            def numset(txt):
                body = re.sub(r'^[a-z]\s*(=|\\in)\s*', '', txt.strip()).replace('\\{', '').replace('\\}', '').replace('{', '').replace('}', '') if '\\frac' not in txt else None
                if body is None:
                    inner = re.sub(r'^[a-z]\s*(=|\\in)\s*', '', txt.strip()).replace('\\{', '').replace('\\}', '')
                    parts = re.split(r',(?![^{]*\})', inner)
                else:
                    parts = body.split(',')
                vals = [one(x) for x in parts if x.strip()]
                return set(vals) if vals and all(v is not None for v in vals) else None
            if key_opt and ml and re.search(r'Solve by factoring|complete real solution set|complete solution set', q['instruction'], re.I) and '=' in ml and 'k' not in ml:
                sides = [one(x) for x in ml.split('=')]
                if len(sides) == 2 and all(x is not None for x in sides):
                    fs = sorted((sides[0].free_symbols | sides[1].free_symbols), key=str)
                    if len(fs) == 1:
                        truth = set(sp.solve(sp.Eq(sides[0], sides[1]), fs[0]))
                        truth = {t for t in truth if t.is_real}
                        got = {i: numset(next(o['text'] for o in q['options'] if o['id'] == i)) for i in ids}
                        if all(v is not None for v in got.values()):
                            hits = [i for i in ids if {sp.nsimplify(x) for x in got[i]} == {sp.nsimplify(x) for x in truth}]
                            if hits == [key_opt['id']]: st['key_verified_solution_set'] = st.get('key_verified_solution_set', 0) + 1; verified = True
                            else: add('error', cls, qid, 'K-solution-set', f'solutions of {ml} = {sorted(truth, key=str)}; options matching: {hits}; key {key_opt["id"]}')
            if key_opt and ml and re.search(r'values of k', q['instruction'], re.I):
                m1 = re.match(r'x\^2([+-]\d*)x([+-]\d+),?\\?quad?', ml.replace(' ', '').replace('kx', 'KX')) if False else None
                a = re.match(r'^x\^2\+kx([+-]\d+)$', ml.replace(' ', '')); b = re.match(r'^x\^2([+-]\d+)x\+k,\\quadk>0$', ml.replace(' ', ''))
                truth = None
                if a:
                    c = int(a.group(1)); truth = {p_ + c // p_ for p_ in range(-abs(c), abs(c) + 1) if p_ and c % p_ == 0}
                elif b:
                    bb = int(b.group(1)); truth = {p_ * (-bb - p_) for p_ in range(-60, 61) if p_ * (-bb - p_) > 0}
                if truth is not None:
                    got = {i: numset(next(o['text'] for o in q['options'] if o['id'] == i)) for i in ids}
                    hits = [i for i in ids if got[i] is not None and {int(x) for x in got[i]} == truth]
                    if hits == [key_opt['id']]: st['key_verified_k_values'] = st.get('key_verified_k_values', 0) + 1; verified = True
                    else: add('error', cls, qid, 'K-k-values', f'k-values for {ml} are {sorted(truth)}; options matching {hits}; key {key_opt["id"]}')
            # K5: slope through two points
            if key_opt and re.search(r'slope of the line through', q['instruction'], re.I):
                pts = re.findall(r'\(\s*(-?[\d./\\a-z{}]+)\s*,\s*(-?[\d./\\a-z{}]+)\s*\)', ml.replace('\\ ', ''))
                if len(pts) >= 2:
                    try:
                        (x1, y1), (x2, y2) = [(one(a), one(b)) for a, b in pts[:2]]
                        if sp.simplify(x2 - x1) == 0:
                            sl = 'undefined'; hits = [i for i in ids if re.search(r'undefined|no slope', next(o['text'] for o in q['options'] if o['id'] == i), re.I)]
                        else:
                            sl = sp.nsimplify((y2 - y1) / (x2 - x1))
                            hits = [i for i in ids if P.get(i) and equiv(P[i], [sl]) is True]
                        if hits == [key_opt['id']]: st['key_verified_slope'] = st.get('key_verified_slope', 0) + 1; verified = True
                        else: add('error', cls, qid, 'K-slope', f'slope of {ml} is {sl}; options equal to it: {hits}; key {key_opt["id"]}')
                    except Exception: pass
            # K6: arithmetic-sequence formulas -- options a_n = ... must reproduce the listed terms
            if key_opt and re.search(r'formula gives the nth term', q['instruction'], re.I):
                terms = [one(t) for t in re.split(r',', re.sub(r'\\ldots|\\dots', '', ml)) if t.strip()]
                if terms and all(t is not None for t in terms):
                    nn = sp.Symbol('n'); good = []
                    for i in ids:
                        body = next(o['text'] for o in q['options'] if o['id'] == i).split('=', 1)[-1]
                        f = one(body)
                        if f is not None and all(sp.simplify(f.subs(sp.Symbol('n'), k + 1) - terms[k]) == 0 for k in range(len(terms))): good.append(i)
                    if good == [key_opt['id']]: st['key_verified_sequence'] = st.get('key_verified_sequence', 0) + 1; verified = True
                    else: add('error', cls, qid, 'K-sequence', f'options reproducing {ml}: {good}; key {key_opt["id"]}')
            # K4: "complete factorisation" -- the key must be fully factored (no further factor possible)
            if key_opt and re.search(r'complete factori[sz]ation', q['instruction'], re.I) and stem_e and P.get(key_opt['id']):
                K = P[key_opt['id']][0]
                try:
                    full = sp.factor_list(sp.expand(K))[1]
                    shown = sp.Mul.make_args(K)
                    nonconst = [f for f in shown if f.free_symbols]
                    if sp.simplify(K - stem_e[0]) != 0: add('error', cls, qid, 'K-factor-not-equal', f'keyed factorisation {key_opt["text"]} != {q["math_latex"]}')
                    elif len(nonconst) < sum(m for _, m in full) and not any(f.is_Pow for f in nonconst): add('error', cls, qid, 'K-factor-incomplete', f'keyed factorisation {key_opt["text"]} can be factored further')
                    else: st['key_verified_factor'] = st.get('key_verified_factor', 0) + 1; verified = True
                except Exception:
                    pass
            # K2: calculator evidence (final numeric result)
            ops = sup.get('operations') or []
            if key_opt and ops and sup.get('role') in ('evaluate', 'calculation'):
                ex = parse(ops[-1].get('exact')); ko = P.get(key_opt['id'])
                nearest = re.search(r'nearest (tenth|hundredth|whole|integer)', q['stem'], re.I)
                pure = ex and ko and not any(e.free_symbols for e in ex + ko)
                if pure and nearest:
                    dp = {'tenth': 1, 'hundredth': 2, 'whole': 0, 'integer': 0}[nearest.group(1).lower()]
                    a, b = numeric(ex), numeric(ko)
                    if a is not None and b is not None:
                        if abs(round(a, dp) - b) < 10 ** -(dp + 3): st['key_verified_calc'] += 1; verified = True
                        else: add('error', cls, qid, 'K-key-vs-calculator', f'calculator evidence {ops[-1]["input"]} = {a:.6g} -> rounds to {round(a, dp)} but keyed option is {key_opt["text"]}')
                elif not pure: pass
                elif ex and ko and equiv(ex, ko) is False: add('error', cls, qid, 'K-key-vs-calculator', f'calculator evidence {ops[-1]["input"]} = {ops[-1]["exact"]} but keyed option is {key_opt["text"]}')
                elif ex and ko and equiv(ex, ko) is True:
                    others = [i for i in ids if i != key_opt['id'] and equiv(P[i], ex) is True]
                    if others: add('error', cls, qid, 'K-two-correct', f'options {others} also equal the computed value {ops[-1]["exact"]}')
                    else: st['key_verified_calc'] += 1; verified = True
            if key_opt and len(ops) >= 2 and sup.get('role') in ('check', 'function_check') and 'misc' not in q['id']:
                a, b = parse(ops[0]['exact']), parse(ops[1]['exact'])
                if equiv(a, b) is False: add('error', cls, qid, 'K-check-mismatch', f'numeric check: original {ops[0]["exact"]} vs keyed option {ops[1]["exact"]}')
                elif equiv(a, b) is True and not verified: st['key_verified_calc'] += 1; verified = True
        else:
            st['frq'] += 1
            for part in q['parts']:
                ml = part.get('answer', {}).get('math_latex')
                sols = sup.get('solutions') or []
                if ml and sols:
                    pe = parse(ml)
                    for sol in sols:
                        se = parse(sol.get('math'))
                        if pe and se and equiv(pe, se) is False: add('error', cls, qid, 'K-frq-vs-calculator-solution', f'part {part["id"]}: answer {ml} != support solution {sol.get("math")}')
                        elif pe and se and equiv(pe, se): verified = True
            # substituted evaluation  e.g. "Evaluate if g=2, r=3, and t=11."
            m = re.search(r'if ([a-z]=-?\d+(?:, (?:and )?[a-z]=-?\d+)*)', q['instruction'])
            if m and q.get('math_latex') and q['parts'][0].get('answer', {}).get('math_latex'):
                sub = {sp.Symbol(k): sp.Rational(v) for k, v in re.findall(r'([a-z])=(-?\d+)', m.group(1))}
                e = one(q['math_latex']); a = parse(q['parts'][0]['answer']['math_latex'])
                if e is not None and a is not None:
                    v = sp.simplify(e.subs(sub))
                    if sp.simplify(v - a[0]) != 0: add('error', cls, qid, 'K-frq-evaluation', f'{q["math_latex"]} at {dict((str(k), int(w)) for k, w in sub.items())} = {v}, but the answer is {q["parts"][0]["answer"]["math_latex"]}')
                    else: verified = True
            # polynomial expansion / factoring families (stem vs answer)
            if q.get('math_latex') and re.search(r'product|sum or difference|Factor|perfect-square', q['instruction'], re.I) and not verified:
                e = parse(q['math_latex']); a = parse(q['parts'][0].get('answer', {}).get('math_latex'))
                if e and a:
                    r = equiv(e, a)
                    if r is False: add('error', cls, qid, 'K-frq-vs-stem', f'answer {q["parts"][0]["answer"]["math_latex"]} is not equal to the stem {q["math_latex"]}')
                    elif r: verified = True
            if verified: st['frq_verified'] += 1
        if not verified:
            st['needs_human'] += 1
            why = 'diagram_or_graph' if q.get('diagram_asset_ids') or re.search(r'graph|diagram|markings|shown', q['instruction'], re.I) else 'justification_or_prose' if re.search(r'justif|explain|describe|statement|property|choose the|which of|why|match|similar|classified', q['instruction'], re.I) else 'algebra_not_parsed' if q['type'] == 'mcq' else 'written_answer'
            HUMAN.setdefault(cls, {}).setdefault(why, []).append(qid)
    st['errors'] = sum(1 for f in findings if f['class'] == cls and f['severity'] == 'error')
    st['warnings'] = sum(1 for f in findings if f['class'] == cls and f['severity'] == 'warning')

out = {'generated': '2026-11-09', 'needs_human': {c: {k: v for k, v in d.items()} for c, d in HUMAN.items()}, 'script': 'scripts/audit-study-questions.py', 'stats': stats, 'findings': findings,
       'limitations': 'Computed equivalence covers parseable algebraic/numeric content. Geometry, graph reading, prose and proofs are listed as needs_human and are NOT certified.'}
(ROOT / 'content-imports/study-question-audit.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(stats, indent=1))
for f in findings: print(f['severity'].upper(), f['class'], f['id'], f['kind'], '|', f['message'][:200])
