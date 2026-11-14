#!/usr/bin/env python3
"""Grade 11 Advanced review (user request, 14 Nov 2026). Idempotent; run after the upper-grade import,
fix-upper-content.py and apply-upper-solutions.py (it rewrites what those produce for the items below).

LO19 (reciprocal trig graphs): the imported choices were predictable and partly wrong.
  * Three choices shared one asymptote/extremum text and differed only in the period, and the period
    distractors' text did not match their own graphs (e.g. a graph with asymptotes every 2π/3 labelled
    "x = 4nπ/3"). The fourth choice ("no vertical asymptotes") can never hold for csc, sec or cot.
  * Graph file names ended in -0 for the correct choice; x-axes were numeric (−8…8), so asymptotes at
    multiples of π could not be read.
  Rebuilt: every choice is a complete, TRUE description of its own graph, made from one named mistake
  (wrong period formula, wrong function family, missed reflection). Students must check period, asymptotes
  and shape. Graphs are SVG with π-labelled ticks and dashed asymptotes. Formulas are simplified.
  11A-Q19-cot asks for x-intercepts: its key was right but its solution steps computed asymptotes.
"""
import json, math, re, shutil
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / 'public/data/study/11A.json'
TR = ROOT / 'public/data/study/translations-ar.json'
ASSET_DIR = ROOT / 'public/data/study-assets/11a'
OLD_DIR = ROOT / 'content-imports/upper-grades/superseded-11a-lo19-graphs'
d = json.loads(BANK.read_text())
tr = json.loads(TR.read_text())
Q = {q['id']: q for q in d['questions']}
changed = []

def tkey(s):
    return re.sub(r'-?\d+(?:\.\d+)?', '#', s.strip())

# ------------------------------------------------------------------ LaTeX helpers
def pi_l(c, n=False):
    """c·π (or c·nπ) for a positive Fraction c, simplified: 4nπ/3, π/2, 3nπ."""
    if c == 0: return '0'
    core = ('n' if n else '') + r'\pi'
    top = core if c.numerator == 1 else f'{c.numerator}{core}'
    return top if c.denominator == 1 else rf'\frac{{{top}}}{{{c.denominator}}}'

def fam_l(offset, step):
    return pi_l(step, True) if offset == 0 else f'{pi_l(offset)}+{pi_l(step, True)}'

def num_l(a):
    a = Fr(a)
    if a.denominator == 1: return str(a.numerator)
    return ('-' if a < 0 else '') + rf'\frac{{{abs(a.numerator)}}}{{{a.denominator}}}'

def pi_txt(c):
    """Plain text tick label for c·π (c may be negative or 0)."""
    if c == 0: return '0'
    s = '−' if c < 0 else ''; c = abs(c)
    top = 'π' if c.numerator == 1 else f'{c.numerator}π'
    return s + (top if c.denominator == 1 else f'{top}/{c.denominator}')

def func_l(F, A, B):
    a = '' if A == 1 else '-' if A == -1 else num_l(A)
    arg = 'x' if B == 1 else f'{B.numerator}x' if B.denominator == 1 else rf'\frac{{{B.numerator}}}{{{B.denominator}}}x'
    return rf'y={a}\{F} x' if B == 1 else rf'y={a}\{F}\left({arg}\right)'

PERIOD = {'csc': 2, 'sec': 2, 'cot': 1, 'tan': 1}            # period = PERIOD·π/|b|

def props(F, A, B):
    T = Fr(PERIOD[F]) / B
    asym = (Fr(0), 1 / B) if F in ('csc', 'cot') else (1 / (2 * B), 1 / B)
    p = {'T': T, 'asym': asym}
    if F in ('csc', 'sec'):
        px = Fr(0) if F == 'sec' else 1 / (2 * B)
        p['point'] = (px, Fr(A)); p['kind'] = 'minimum' if A > 0 else 'maximum'
    else:
        p['icept'] = (1 / (2 * B), 1 / B) if F == 'cot' else (Fr(0), 1 / B)
        p['dir'] = ('decreasing' if A > 0 else 'increasing') if F == 'cot' else ('increasing' if A > 0 else 'decreasing')
    return p

def desc_graph(F, A, B):
    """One property per line (a single long line was clipped on phones)."""
    p = props(F, A, B); lines = [rf'T={pi_l(p["T"])}', rf'\text{{asymptotes: }}x={fam_l(*p["asym"])}']
    if F in ('csc', 'sec'):
        px, py = p['point']
        lines += [rf'\text{{local {p["kind"]}: }}\left({pi_l(px) if px else "0"},\,{num_l(py)}\right)', rf'\text{{range: }}y\le {num_l(-abs(A))}\text{{ or }}y\ge {num_l(abs(A))}']
    else:
        lines += [rf'\text{{x-intercepts: }}x={fam_l(*p["icept"])}', rf'\text{{{p["dir"]} between asymptotes}}']
    return r'\begin{array}{l}' + r'\\[5pt] '.join(lines) + r'\end{array}'

def ar_graph(F, A, B):
    p = props(F, A, B)
    if F in ('csc', 'sec'):
        return f'الدورة T، وخطوط التقارب الرأسية، و{"نقطة صغرى محلية" if p["kind"] == "minimum" else "نقطة عظمى محلية"}، والمدى (n عدد صحيح)'
    return f'الدورة T، وخطوط التقارب الرأسية، والمقاطع السينية، و{"متناقصة" if p["dir"] == "decreasing" else "متزايدة"} بين خطوط التقارب (n عدد صحيح)'

# ------------------------------------------------------------------ numeric check of every description
def fval(F, A, B, x):
    t = float(B) * x
    den = {'csc': math.sin(t), 'sec': math.cos(t), 'cot': math.sin(t), 'tan': math.cos(t)}[F]
    num = {'csc': 1.0, 'sec': 1.0, 'cot': math.cos(t), 'tan': math.sin(t)}[F]
    return float(A) * num / den if den != 0 else math.copysign(1e300, num)

def verify(F, A, B):
    p = props(F, A, B); T = float(p['T']) * math.pi; o, s = (float(v) * math.pi for v in p['asym'])
    for x in (0.31, 1.7, -2.3):
        if min(abs(((x - o) / s) - round((x - o) / s)), 1) > 0.05:
            assert abs(fval(F, A, B, x + T) - fval(F, A, B, x)) < 1e-6 * max(1, abs(fval(F, A, B, x))), (F, A, B, 'period')
            assert abs(fval(F, A, B, x + T / 2) - fval(F, A, B, x)) > 1e-6, (F, A, B, 'not a smaller period')
    for n in range(-2, 3):
        xa = o + n * s
        assert abs(fval(F, A, B, xa + 1e-7)) > 1e4 and abs(fval(F, A, B, xa - 1e-7)) > 1e4, (F, A, B, 'asymptote', n)
    if F in ('csc', 'sec'):
        px = float(p['point'][0]) * math.pi; y0 = fval(F, A, B, px)
        assert abs(y0 - float(A)) < 1e-9, (F, A, B, 'point')
        side = fval(F, A, B, px + 1e-3) - y0
        assert (side > 0) == (p['kind'] == 'minimum'), (F, A, B, 'min/max')
    else:
        io, isp = (float(v) * math.pi for v in p['icept'])
        for n in range(-2, 3):
            xi = io + n * isp; assert abs(fval(F, A, B, xi)) < 1e-9, (F, A, B, 'intercept')
            assert ((fval(F, A, B, xi + 1e-4) - fval(F, A, B, xi - 1e-4)) > 0) == (p['dir'] == 'increasing'), (F, A, B, 'direction')

# ------------------------------------------------------------------ SVG graph with π ticks and dashed asymptotes
def svg_graph(F, A, B, unit):
    """unit = π/b of the QUESTION's function (same window and ticks for all four choices)."""
    W, H, L, R, T_, Bm = 440, 250, 40, 12, 10, 34
    X0, X1 = -2 * float(unit) * math.pi, 2 * float(unit) * math.pi
    Ymax = max(4, math.ceil(3 * abs(float(A))))
    sx = lambda x: L + (x - X0) / (X1 - X0) * (W - L - R)
    sy = lambda y: T_ + (Ymax - y) / (2 * Ymax) * (H - T_ - Bm)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, Helvetica, sans-serif">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           f'<defs><clipPath id="c"><rect x="{L}" y="{T_}" width="{W - L - R}" height="{H - T_ - Bm}"/></clipPath></defs>']
    for k in range(-4, 5):                                          # vertical grid + π labels every half unit
        x = k * float(unit) * math.pi / 2
        out.append(f'<line x1="{sx(x):.1f}" y1="{T_}" x2="{sx(x):.1f}" y2="{H - Bm}" stroke="#e2e8f0"/>')
        out.append(f'<text x="{sx(x):.1f}" y="{H - Bm + 15}" font-size="11.5" text-anchor="middle" fill="#334155">{pi_txt(Fr(k, 2) * unit)}</text>')
    step = 1 if Ymax <= 5 else 2 if Ymax <= 10 else 3
    for y in range(-(Ymax // step) * step, Ymax + 1, step):
        out.append(f'<line x1="{L}" y1="{sy(y):.1f}" x2="{W - R}" y2="{sy(y):.1f}" stroke="#e2e8f0"/>')
        out.append(f'<text x="{L - 5}" y="{sy(y) + 4:.1f}" font-size="11" text-anchor="end" fill="#334155">{str(y).replace("-", "−")}</text>')
    out.append(f'<rect x="{L}" y="{T_}" width="{W - L - R}" height="{H - T_ - Bm}" fill="none" stroke="#94a3b8"/>')
    out.append(f'<line x1="{L}" y1="{sy(0):.1f}" x2="{W - R}" y2="{sy(0):.1f}" stroke="#334155" stroke-width="1.3"/>')
    out.append(f'<line x1="{sx(0):.1f}" y1="{T_}" x2="{sx(0):.1f}" y2="{H - Bm}" stroke="#334155" stroke-width="1.3"/>')
    out.append(f'<text x="{W - R - 8}" y="{sy(0) - 5:.1f}" font-size="13" font-style="italic">x</text><text x="{sx(0) + 5:.1f}" y="{T_ + 13}" font-size="13" font-style="italic">y</text>')
    p = props(F, A, B); o, s = (float(v) * math.pi for v in p['asym'])
    asy = [o + k * s for k in range(math.floor((X0 - o) / s) - 1, math.ceil((X1 - o) / s) + 2)]
    for xa in asy:
        if X0 - 1e-9 <= xa <= X1 + 1e-9:
            out.append(f'<line x1="{sx(xa):.1f}" y1="{T_}" x2="{sx(xa):.1f}" y2="{H - Bm}" stroke="#b91c1c" stroke-width="1.3" stroke-dasharray="6 4"/>')
    paths = []
    for a0, a1 in zip(asy, asy[1:]):
        lo, hi = max(a0, X0), min(a1, X1)
        if hi <= lo: continue
        seg, n = [], 500
        for i in range(n + 1):
            x = lo + (hi - lo) * i / n
            if abs(x - a0) < 1e-9 or abs(x - a1) < 1e-9: continue
            y = fval(F, A, B, x)
            if abs(y) <= Ymax * 1.25: seg.append(f'{sx(x):.1f},{sy(y):.1f}')
            elif seg: paths.append(seg); seg = []
        if seg: paths.append(seg)
    for sgm in paths:
        if len(sgm) > 1: out.append(f'<polyline clip-path="url(#c)" points="{" ".join(sgm)}" fill="none" stroke="#0e7490" stroke-width="2.4" stroke-linejoin="round"/>')
    out.append('</svg>')
    return '\n'.join(out)

# ------------------------------------------------------------------ the 11 LO19 items
GRAPH = {  # qid: (function, a, b)
    '11A-Q19-book-7': ('csc', Fr(1), Fr(3, 4)), '11A-Q19-book-8': ('csc', Fr(1), Fr(3)), '11A-Q19-book-9': ('csc', Fr(1, 2), Fr(1)),
    '11A-Q19-book-10': ('cot', Fr(1), Fr(2)), '11A-Q19-book-11': ('cot', Fr(1), Fr(1, 2)), '11A-Q19-book-12': ('cot', Fr(-2), Fr(1)),
    '11A-Q19-book-13': ('sec', Fr(3), Fr(1)), '11A-Q19-book-14': ('sec', Fr(1), Fr(1, 3)), '11A-Q19-book-15': ('sec', Fr(1), Fr(4)),
}
KEYS = {'11A-Q19-cot': 'B', '11A-Q19-sec': 'C', '11A-Q19-book-7': 'A', '11A-Q19-book-8': 'D', '11A-Q19-book-9': 'C', '11A-Q19-book-10': 'B',
        '11A-Q19-book-11': 'D', '11A-Q19-book-12': 'A', '11A-Q19-book-13': 'C', '11A-Q19-book-14': 'B', '11A-Q19-book-15': 'D'}
SWAP = {'csc': 'sec', 'sec': 'csc', 'cot': 'tan'}
PARENT = {'csc': 'sin', 'sec': 'cos', 'cot': 'tan'}
NAME_AR = {'csc': 'قاطع التمام', 'sec': 'القاطع', 'cot': 'ظل التمام'}

def place(qid, correct, distractors):
    """correct and distractors are (text, extra) tuples; returns options in A–D with the key at KEYS[qid]."""
    key = KEYS[qid]; slots = [L for L in 'ABCD' if L != key]
    rot = sum(map(ord, qid)) % 3; ds = distractors[rot:] + distractors[:rot]
    out = {key: correct}; out.update(zip(slots, ds))
    return [dict(id=L, **out[L]) for L in 'ABCD']

def step(text, ar, latex, why, why_ar):
    return {'text': text, 'ar': ar, 'latex': latex, 'why': why, 'why_ar': why_ar}

def final_step(L, latex):
    return step(f'So the answer is option {L}.', f'إذن الإجابة هي الخيار {L}.', latex,
                'Every choice describes a real graph; only one matches all three checks: period, asymptotes and shape.',
                'كل خيار يصف تمثيلاً حقيقياً؛ واحد فقط يطابق الفحوص الثلاثة: الدورة وخطوط التقارب والشكل.')

if OLD_DIR.exists() is False: OLD_DIR.mkdir(parents=True)
for gi, (qid, (F, A, B)) in enumerate(GRAPH.items()):
    q = Q[qid]
    Bp = 2 * B if F in ('csc', 'sec') else B / 2
    why_p = f'Used {"π" if F != "cot" else "2π"}/|b| for the period: {F} repeats every {"2π" if F != "cot" else "π"}/|b|.'
    why_f = f'These are the asymptotes of {SWAP[F]}: {F} = 1/{PARENT[F]} has no value where {PARENT[F] if F != "cot" else "sin"}(bx) = 0.'
    why_r = 'Missed the sign of a: a negative a reflects the graph in the x-axis.' if A < 0 else 'This is the reflection of the graph (a sign error): with a > 0 the graph is not reflected.'
    # The reflection distractor sometimes carries a second mistake, so the correct choice is not always the
    # "middle" one that differs from each distractor in exactly one feature.
    third = [('reflect', (F, -A, B), why_r), ('family+reflect', (SWAP[F], -A, B), why_f + ' ' + why_r), ('period+reflect', (F, -A, Bp), why_p + ' ' + why_r)][gi % 3]
    cands = [('correct', (F, A, B), None), ('period', (F, A, Bp), why_p), ('family', (SWAP[F], A, B), why_f), third]
    texts = [desc_graph(*c[1]) for c in cands]
    assert len(set(texts)) == 4, qid
    for c in cands: verify(*c[1])
    # retire the imported option images (kept outside public/ as evidence)
    for o in q['options']:
        if o.get('image') and o['image'] in d['assets'] and not o['image'].endswith(('optA', 'optB', 'optC', 'optD')):
            src = ROOT / 'public' / d['assets'][o['image']]['src']
            if src.exists(): shutil.move(str(src), OLD_DIR / src.name)
            del d['assets'][o['image']]
    unit = 1 / B
    built = []
    for (kind, params, why), text in zip(cands, texts):
        built.append({'text': text, 'math_latex': text, 'misconception': why, '_params': params})
    opts = place(qid, built[0], built[1:])
    for o in opts:
        aid = f'{qid}-opt{o["id"]}'
        (ASSET_DIR / f'{aid}.svg').write_text(svg_graph(*o.pop('_params'), unit) + '\n')
        d['assets'][aid] = {'src': f'data/study-assets/11a/{aid}.svg', 'width': 440, 'height': 250,
                            'alt_text': f'Choice {o["id"]} graph: x-axis marked in multiples of π, vertical asymptotes dashed.',
                            'source': {'adaptation': 'redrawn_for_clarity', 'reason': 'LO19 review 2026-11-14: each choice graph matches its own text; π-labelled axis'}}
        o['image'] = aid
        tr['option'][tkey(o['text'])] = ar_graph(*[c[1] for c in cands][[t for t in texts].index(o['text'])])
    key = KEYS[qid]
    q['options'] = opts
    q['math_latex'] = func_l(F, A, B)
    q['stem'] = f"{q['instruction']} {q['math_latex']}"
    q['answer']['correct_option_id'] = key
    q['answer']['correct_option_text'] = texts[0]
    p = props(F, A, B)
    absA = num_l(abs(A))
    q['answer']['explanation'] = (f'{F} = 1/{PARENT[F]}: period {"2π" if F != "cot" else "π"}/|b|, asymptotes where '
                                  f'{"sin" if F in ("csc", "cot") else "cos"}(bx) = 0; ' + ('the sign of a decides reflection.'))
    steps = [step(f'Compare with y = a·{F}(bx): read a and b.', f'قارن بالصيغة y = a·{F}(bx): حدّد a و b.', rf'a={num_l(A)},\quad b={num_l(B)}',
                  'Each number in the equation controls one feature: b the period, a the stretch and reflection.', 'كل عدد في المعادلة يتحكم بخاصية: b بالدورة، و a بالتمدد والانعكاس.'),
             step(f'{F} repeats like {PARENT[F]}: period = {"2π" if F != "cot" else "π"} ÷ |b|.', f'{NAME_AR[F]} يتكرر مثل {PARENT[F]}: الدورة = {"2π" if F != "cot" else "π"} ÷ |b|.',
                  rf'T=\dfrac{{{"2" if F != "cot" else ""}\pi}}{{{num_l(B)}}}={pi_l(p["T"])}',
                  'Dividing by |b| because a larger b squeezes the graph horizontally.', 'نقسم على |b| لأن b الأكبر يضغط التمثيل أفقياً.')]
    if F == 'csc':
        steps.append(step('csc = 1/sin is undefined where sin(bx) = 0, i.e. bx = nπ.', 'قاطع التمام = 1/جا غير معرّف حيث جا(bx) = 0، أي bx = nπ.', rf'x=\dfrac{{n\pi}}{{{num_l(B)}}}={fam_l(*p["asym"])}',
                          'A fraction with denominator 0 is undefined: that is where the vertical asymptotes are.', 'الكسر الذي مقامه صفر غير معرّف: هناك تقع خطوط التقارب الرأسية.'))
        px, py = p['point']
        steps.append(step(f'Where sin(bx) = 1 (bx = π/2) the value is a: a local {p["kind"]}.', f'حيث جا(bx) = 1 (أي bx = π/2) تكون القيمة a: {"صغرى" if A > 0 else "عظمى"} محلية.',
                          rf'\left({pi_l(px)},\,{num_l(py)}\right);\ \text{{range }}|y|\ge {absA}', 'This point decides whether the first branch after x = 0 opens up or down.', 'هذه النقطة تحدد هل الفرع الأول بعد x = 0 مفتوح لأعلى أم لأسفل.'))
    elif F == 'sec':
        steps.append(step('sec = 1/cos is undefined where cos(bx) = 0, i.e. bx = π/2 + nπ.', 'القاطع = 1/جتا غير معرّف حيث جتا(bx) = 0، أي bx = π/2 + nπ.', rf'x=\dfrac{{\pi/2+n\pi}}{{{num_l(B)}}}={fam_l(*p["asym"])}',
                          'A fraction with denominator 0 is undefined: that is where the vertical asymptotes are.', 'الكسر الذي مقامه صفر غير معرّف: هناك تقع خطوط التقارب الرأسية.'))
        steps.append(step(f'At x = 0, cos 0 = 1, so y = a: a local {p["kind"]} on the y-axis.', f'عند x = 0 يكون جتا 0 = 1، إذن y = a: {"صغرى" if A > 0 else "عظمى"} محلية على محور y.',
                          rf'\left(0,\,{num_l(A)}\right);\ \text{{range }}|y|\ge {absA}', 'The y-intercept tells you which way the middle branch opens.', 'المقطع y يبيّن اتجاه الفرع الأوسط.'))
    else:
        steps.append(step('cot = cos/sin is undefined where sin(bx) = 0, i.e. bx = nπ.', 'ظل التمام = جتا/جا غير معرّف حيث جا(bx) = 0، أي bx = nπ.', rf'x=\dfrac{{n\pi}}{{{num_l(B)}}}={fam_l(*p["asym"])}',
                          'Asymptotes come from the denominator (sin); x-intercepts come from the numerator (cos).', 'خطوط التقارب من المقام (جا)، والمقاطع السينية من البسط (جتا).'))
        steps.append(step(f'x-intercepts where cos(bx) = 0. With a {"> 0 cot falls" if A > 0 else "< 0 the graph is reflected, so it rises"} between asymptotes.',
                          f'المقاطع السينية حيث جتا(bx) = 0. ومع a {"> 0 تتناقص" if A > 0 else "< 0 ينعكس التمثيل فيتزايد"} بين خطوط التقارب.',
                          rf'x={fam_l(*p["icept"])};\ \text{{{p["dir"]}}}', 'cot always decreases unless a reflection (a < 0) turns it over.', 'ظل التمام يتناقص دائماً إلا إذا قلبه انعكاس (a < 0).'))
    steps.append(step('Check the graphs: dashed lines are the asymptotes; compare their spacing, positions and the shape of each branch.', 'افحص التمثيلات: الخطوط المتقطعة هي خطوط التقارب؛ قارن تباعدها ومواقعها وشكل كل فرع.',
                      texts[0], 'One wrong number gives a graph that looks similar, so check all three features.', 'رقم خاطئ واحد يعطي تمثيلاً مشابهاً، لذا افحص الخصائص الثلاث.'))
    steps.append(final_step(key, texts[0]))
    q['answer']['steps'] = steps; q['answer']['steps_verified'] = True
    q['review_2026_11_14'] = 'choices rebuilt: each is a true description of its own graph (period / family / reflection mistakes); π-axis graphs'
    changed.append(qid)

# ---- text-only items
TEXT = {'11A-Q19-cot': ('cot', Fr(1), Fr(1, 2), 'icept'), '11A-Q19-sec': ('sec', Fr(1), Fr(1, 3), 'asym')}
for qid, (F, A, B, ask) in TEXT.items():
    q = Q[qid]
    def short(F_, B_):
        p = props(F_, A, B_); fam = p['icept'] if ask == 'icept' else p['asym']
        return rf'T={pi_l(p["T"])};\ ' + (r'\text{x-intercepts }' if ask == 'icept' else r'\text{asymptotes }') + f'x={fam_l(*fam)}'
    cands = [((F, B), None),
             ((F, 2 * B) if F == 'sec' else (F, B / 2), f'Used {"π" if F == "sec" else "2π"}/|b| for the period.'),
             ((SWAP[F], B), 'These are the asymptotes (where sin = 0), not the x-intercepts.' if ask == 'icept' else 'These are the asymptotes of csc (where sin = 0).'),
             ((F, 1 / B), 'Multiplied by b instead of dividing.')]
    texts = [short(*c[0]) for c in cands]
    assert len(set(texts)) == 4, qid
    for c in cands: verify(c[0][0], A, c[0][1])
    opts = place(qid, {'text': texts[0], 'math_latex': texts[0], 'misconception': None},
                 [{'text': t, 'math_latex': t, 'misconception': c[1]} for t, c in zip(texts[1:], cands[1:])])
    key = KEYS[qid]
    q['options'] = opts; q['answer']['correct_option_id'] = key; q['answer']['correct_option_text'] = texts[0]
    q['math_latex'] = func_l(F, A, B); q['stem'] = f"{q['instruction']} {q['math_latex']}"
    for t in texts:
        tr['option'][tkey(t)] = 'الدورة T والمقاطع السينية (n عدد صحيح)' if ask == 'icept' else 'الدورة T وخطوط التقارب الرأسية (n عدد صحيح)'
    p = props(F, A, B)
    if F == 'cot':
        q['answer']['explanation'] = 'Period π/|b| = 2π; x-intercepts where cos(x/2) = 0: x = π + 2nπ (asymptotes, where sin(x/2) = 0, are x = 2nπ).'
        mid = [step('cot = cos/sin is zero where its numerator cos(bx) = 0, i.e. bx = π/2 + nπ.', 'ظل التمام = جتا/جا يساوي صفراً حيث بسطه جتا(bx) = 0، أي bx = π/2 + nπ.',
                    rf'\dfrac{{x}}{{2}}=\dfrac{{\pi}}{{2}}+n\pi\ \Rightarrow\ x={fam_l(*p["icept"])}', 'x-intercepts are where y = 0: a fraction is 0 when its numerator is 0.', 'المقاطع السينية حيث y = 0: الكسر يساوي صفراً عندما يكون بسطه صفراً.'),
               step('Do not confuse them with the asymptotes, where sin(bx) = 0.', 'لا تخلطها بخطوط التقارب حيث جا(bx) = 0.', r'\text{asymptotes: }x=2n\pi',
                    'Both families are spaced one period apart, so check the starting value.', 'كلتا المجموعتين متباعدتان بمقدار دورة، لذا افحص قيمة البداية.')]
    else:
        q['answer']['explanation'] = 'Period 2π/|b| = 6π; asymptotes where cos(x/3) = 0: x = 3π/2 + 3nπ.'
        mid = [step('sec = 1/cos is undefined where cos(bx) = 0, i.e. bx = π/2 + nπ.', 'القاطع = 1/جتا غير معرّف حيث جتا(bx) = 0، أي bx = π/2 + nπ.',
                    rf'\dfrac{{x}}{{3}}=\dfrac{{\pi}}{{2}}+n\pi\ \Rightarrow\ x={fam_l(*p["asym"])}', 'Multiply both sides by 3 to undo the division by 3.', 'اضرب الطرفين في 3 للتخلص من القسمة على 3.')]
    q['answer']['steps'] = [step(f'Compare with y = {F}(bx): b = {B}.', f'قارن بالصيغة y = {F}(bx): b = {B}.', rf'b={num_l(B)}', 'b controls the period.', 'b يتحكم بالدورة.'),
                            step(f'Period = {"π" if F == "cot" else "2π"} ÷ |b|.', f'الدورة = {"π" if F == "cot" else "2π"} ÷ |b|.', rf'T=\dfrac{{{"" if F == "cot" else "2"}\pi}}{{{num_l(B)}}}={pi_l(p["T"])}',
                                 'Dividing by a fraction multiplies: the graph is stretched horizontally.', 'القسمة على كسر تعني الضرب: يتمدد التمثيل أفقياً.')] + mid + [final_step(key, texts[0])]
    q['answer']['steps_verified'] = True
    q['review_2026_11_14'] = 'choices rebuilt (period / family / ×b mistakes); steps now find what the question asks'
    changed.append(qid)


# ------------------------------------------------------------------ LO20 principal values
# Keys were right, but every distractor was the key's negative, supplement or a coterminal angle, so the key was
# the "middle" choice. Now: one outside-the-principal-range angle with the same ratio, one sign error, one
# partner-function value (arcsin<->arccos, arctan<->arccot). Positions rebalanced.
INV = {'11A-Q20-book-1': ('arccos', 30, 'C'), '11A-Q20-book-2': ('arcsin', -60, 'D'), '11A-Q20-book-3': ('arccos', 120, 'A'), '11A-Q20-book-4': ('arctan', 60, 'B'),
       '11A-Q20-book-5': ('arccos', 135, 'C'), '11A-Q20-book-6': ('arctan', -45, 'D'), '11A-Q20-book-7': ('arcsin', 45, 'B'), '11A-Q20-book-8': ('arccos', 150, 'A'),
       '11A-Q20-book-9': ('arcsin', 90, 'C')}
RANGE = {'arcsin': (-90, 90), 'arccos': (0, 180), 'arctan': (-90, 90)}
RANGE_L = {'arcsin': r'[-90^\circ,\,90^\circ]', 'arccos': r'[0^\circ,\,180^\circ]', 'arctan': r'(-90^\circ,\,90^\circ)'}
def ang_l(k):
    r = Fr(k, 180)
    rad = '0' if r == 0 else ('-' if r < 0 else '') + (pi_l(abs(r)))
    return rf'{k}^\circ,\ {rad}'
def ratio(f, k):
    t = math.radians(k); return {'arcsin': math.sin(t), 'arccos': math.cos(t), 'arctan': math.tan(t) if abs(math.cos(t)) > 1e-12 else float('inf')}[f]
for qid, (f, k, key) in INV.items():
    q = Q[qid]
    lo, hi = RANGE[f]; assert lo <= k <= hi
    m = re.fullmatch(r'\\' + f + r'\((.+)\)', q['math_latex']); assert m, qid
    v = float(eval(m[1].replace('\\sqrt', 'math.sqrt').replace('sqrt3', 'sqrt(3)').replace('sqrt2', 'sqrt(2)').replace('math.sqrt3', 'math.sqrt(3)').replace('math.sqrt2', 'math.sqrt(2)')))
    assert abs(ratio(f, k) - v) < 1e-9, (qid, 'key')
    quad = {'arcsin': 180 - k, 'arccos': 360 - k, 'arctan': k + 180}[f]
    if quad == k or lo <= quad <= hi: quad = k + 360
    sign = -k if k else 180
    partner = 90 - k
    ds = []
    for val, why in [(quad, f'Same ratio, but {quad}° is outside the principal range of {f}.'), (sign, 'Sign error: check which quadrant the principal range allows.'),
                     (partner, {'arcsin': 'This is the arccos value (sine and cosine swapped).', 'arccos': 'This is the arcsin value (cosine and sine swapped).', 'arctan': 'This is the arccot value (tangent and cotangent swapped).'}[f])]:
        if val in [k] + [x for x, _ in ds]:
            val = k + 360 if k + 360 not in [x for x, _ in ds] else k - 360
            why = f'Coterminal with the answer, but {val}° is outside the principal range of {f}.'
        ds.append((val, why))
    assert len({k} | {x for x, _ in ds}) == 4, qid
    for val, _ in ds:   # every distractor is either outside the range or has a different ratio
        assert not (lo <= val <= hi and abs(ratio(f, val) - v) < 1e-9), (qid, val)
    KEYS[qid] = key
    opts = place(qid, {'text': ang_l(k), 'math_latex': ang_l(k), 'misconception': None}, [{'text': ang_l(x), 'math_latex': ang_l(x), 'misconception': w} for x, w in ds])
    q['options'] = opts; q['answer']['correct_option_id'] = key; q['answer']['correct_option_text'] = ang_l(k)
    for o in opts: tr['option'].pop(tkey(o['text']), None)
    ref = abs(k) if abs(k) <= 90 else 180 - abs(k)
    q['answer']['steps'] = [
        step(f'The principal value of {f} must lie in its restricted range.', f'القيمة الرئيسة للدالة {f} يجب أن تقع في مداها المقيّد.', rf'\{f}:\ {RANGE_L[f]}',
             'Inverse trig functions give one angle only, so each has a fixed output range.', 'الدوال المثلثية العكسية تعطي زاوية واحدة فقط، لذلك لكل منها مدى ثابت.'),
        step(f'Find the reference angle from the special triangles or the unit circle: {ref}°.', f'أوجد الزاوية المرجعية من المثلثات الخاصة أو دائرة الوحدة: {ref}°.', rf'\text{{reference angle}}={ref}^\circ',
             'The size of the ratio fixes the reference angle; its sign fixes the quadrant.', 'قيمة النسبة تحدد الزاوية المرجعية، وإشارتها تحدد الربع.'),
        step('Choose the angle with that ratio that is inside the range.', 'اختر الزاوية ذات النسبة نفسها التي تقع داخل المدى.', rf'\{f}\left({m[1]}\right)={k}^\circ',
             'Other angles with the same ratio exist, but only one is inside the principal range.', 'توجد زوايا أخرى بالنسبة نفسها، لكن واحدة فقط داخل المدى الرئيس.'),
        step('Convert to radians: multiply by π/180.', 'حوّل إلى الراديان: اضرب في π/180.', rf'{k}^\circ\times\dfrac{{\pi}}{{180}}={ang_l(k).split(chr(92) + " ", 1)[1]}',
             '180° = π radians.', '180° = π راديان.'),
        final_step(key, ang_l(k))]
    q['answer']['steps_verified'] = True
    q['review_2026_11_14'] = 'distractors rebuilt from three named mistakes; key position rebalanced'
    changed.append(qid)

# ------------------------------------------------------------------ LO01 / LO09 picture choices
# The original graphs are correct (each checked against its own function); only the presentation leaked.
# LO01: choice text "Graph A/B/C/D" did not match the choice letter, and "Graph A" was always the key.
#       Each choice now states the features of its own graph. Images are renamed by choice letter.
EXP = {  # qid: {image-suffix: (a, h, k) for y = a·2^(x+h) + k}
    '11A-Q01-added-01': {'0': (1, 0, 2), '1': (1, 0, -2), '2': (-1, 0, 2), '3': (1, 2, 0)},
    '11A-Q01-added-02': {'0': (1, 0, 3), '1': (1, 0, -3), '2': (-1, 0, 3), '3': (1, 3, 0)},
}
def exp_text(a, h, k):
    y0 = a * 2 ** h + k
    return rf'\text{{asymptote }}y={k};\ y\text{{-intercept }}(0,\,{y0});\ \text{{{"increasing" if a > 0 else "decreasing"}}}'
def rename_images(q):
    for o in q['options']:
        old = o.get('image')
        if not old or old.endswith('-opt' + o['id']): continue
        a = d['assets'].pop(old); src = ROOT / 'public' / a['src']; new = f"{q['id']}-opt{o['id']}"
        dst = src.with_name(new + src.suffix)
        if src.exists(): src.rename(dst)
        a['src'] = a['src'].rsplit('/', 1)[0] + '/' + dst.name; d['assets'][new] = a; o['image'] = new
for qid, table in EXP.items():
    q = Q[qid]
    if not q.get('review_2026_11_14'):
        for o in q['options']:
            a_, h_, k_ = table[o['image'].rsplit('-', 1)[1]]
            o['text'] = o['math_latex'] = exp_text(a_, h_, k_)
            tr['option'][tkey(o['text'])] = 'خط التقارب الأفقي، والمقطع y، والاتجاه (متزايدة أو متناقصة)'
        rename_images(q)
        key = q['answer']['correct_option_id']; q['answer']['correct_option_text'] = next(o['text'] for o in q['options'] if o['id'] == key)
        q['review_2026_11_14'] = 'choice text now states each graph\'s asymptote, y-intercept and direction (was "Graph X", key always "Graph A")'
        changed.append(qid)
    k = int(re.search(r'\+(\d)', q['math_latex'])[1])
    assert q['answer']['correct_option_text'] == exp_text(1, 0, k), qid
# LO09: tidy the printed function ("+(-6)") and rename images; the choices already match their graphs.
for qid in ['11A-Q09-book-14', '11A-Q09-book-15', '11A-Q09-book-16', '11A-Q09-book-13-graph']:
    q = Q[qid]
    if not q.get('review_2026_11_14'):
        m = re.fullmatch(r'f\(x\)=\\frac\{?(-?1)\}?\{x\+(\d)\}\+?\(?(-?\d)\)?|f\(x\)=\\frac1\{x\+(\d)\}(-\d)', q['math_latex'])
        if m and m[1]:
            a_, h_, k_ = m[1], m[2], int(m[3])
            q['math_latex'] = rf'f(x)={"-" if a_ == "-1" else ""}\frac{{1}}{{x+{h_}}}{"+" if k_ > 0 else "-"}{abs(k_)}'
        q['stem'] = f"{q['instruction']} {q['math_latex']}"
        rename_images(q)
        q['review_2026_11_14'] = 'function printed in simplest form; picture names no longer reveal the key'
        changed.append(qid)


# ------------------------------------------------------------------ polish found in the full read-through
# (all 160 keys were re-derived; none besides LO19's content needed changing)
# 1) LO06 authored items printed unreduced fractions as the key (ln(9/6)); reduce every \ln\frac{p}{q}.
from math import gcd
def red_ln(t):
    def r(m):
        p_, q_ = int(m[1]), int(m[2]); g = gcd(p_, q_); p_, q_ = p_ // g, q_ // g
        return rf'\ln({p_})' if q_ == 1 else rf'\ln\frac{{{p_}}}{{{q_}}}'
    return re.sub(r'\\ln (\d+)\b', r'\\ln(\1)', re.sub(r'\\ln\\d?frac\{(\d+)\}\{(\d+)\}', r, t))
for q in d['questions']:
    if q['id'].startswith('11A-Q06-added'):
        for o in q['options']: o['text'] = o['math_latex'] = red_ln(o['math_latex'])
        assert len({o['text'] for o in q['options']}) == 4, q['id']
        q['answer']['correct_option_text'] = next(o['text'] for o in q['options'] if o['id'] == q['answer']['correct_option_id'])
        st = q['answer']['steps']
        if len(st) >= 2: st[-1]['latex'] = q['answer']['correct_option_text']
# 2) Unneeded brackets around a positive integer base: (2)^{7} -> 2^{7}, (3)^x -> 3^x
def unbracket(t): return re.sub(r'(?<![\\\w])\((\d+)\)\^', r'\1^', t)
for q in d['questions']:
    for k in ('math_latex', 'stem'):
        if q.get(k): q[k] = unbracket(q[k])
    for o in q.get('options', []):
        if o.get('math_latex'): o['math_latex'] = unbracket(o['math_latex'])
        o['text'] = unbracket(o['text'])
    if q['type'] == 'mcq':
        q['answer']['correct_option_text'] = unbracket(q['answer']['correct_option_text'])
        for x in q['answer']['steps']: x['latex'] = unbracket(x.get('latex', ''))
# 3) Key positions: in several outcomes one letter dominated (LO04: D in 4 of 6; LO16: C in 5 of 8).
#    Swap the correct choice with another choice until each outcome's letters differ by at most one.
#    Picture choices (named by letter) and the rebuilt LO19/LO20 items are left as they are.
def relabel_steps(q, old, new):
    for x in q['answer']['steps']:
        x['text'] = re.sub(rf'\boption {old}\b', f'option {new}', x['text'])
        if x.get('ar'): x['ar'] = x['ar'].replace(f'الخيار {old}', f'الخيار {new}')
import collections
for lo in sorted({q['learning_outcome_id'] for q in d['questions']}):
    if lo in ('LO19', 'LO20'): continue
    items = [q for q in d['questions'] if q['learning_outcome_id'] == lo and q['type'] == 'mcq']
    movable = [q for q in items if not any(o.get('image') for o in q['options'])]
    for _ in range(20):
        c = collections.Counter({L: 0 for L in 'ABCD'}); c.update(q['answer']['correct_option_id'] for q in items)
        hi, lo_ = max(c, key=lambda L: (c[L], L)), min(c, key=lambda L: (c[L], L))
        if c[hi] - c[lo_] <= 1: break
        cand = [q for q in movable if q['answer']['correct_option_id'] == hi]
        if not cand: break
        q = sorted(cand, key=lambda q: q['id'])[-1]
        oi = {o['id']: o for o in q['options']}
        a, b = oi[hi], oi[lo_]
        a['id'], b['id'] = lo_, hi
        q['options'] = sorted(q['options'], key=lambda o: o['id'])
        q['answer']['correct_option_id'] = lo_
        relabel_steps(q, hi, lo_)
        q.setdefault('review_2026_11_14', 'key position rebalanced within its outcome')
        changed.append(q['id'])
# every MCQ: the key's text equals the keyed option, and the last step names the key
for q in d['questions']:
    if q['type'] != 'mcq': continue
    k = q['answer']['correct_option_id']; o = next(o for o in q['options'] if o['id'] == k)
    assert q['answer']['correct_option_text'] in (o.get('math_latex'), o['text']), q['id']
    last = q['answer']['steps'][-1]['text']
    assert re.search(rf'option {k}\b', last) or 'option' not in last, (q['id'], last)

BANK.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
TR.write_text(json.dumps(tr, ensure_ascii=False, indent=1) + '\n' if TR.read_text().startswith('{\n') else json.dumps(tr, ensure_ascii=False, separators=(',', ':')))
print('11A review: items changed this run:', len(changed))
