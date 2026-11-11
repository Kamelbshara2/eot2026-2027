#!/usr/bin/env python3
"""Step-by-step solutions for every Grade 9 / Grade 10 multiple-choice question (teacher request 2026-11-11).

Each step:  text (simple English) · ar (simple Arabic) · latex (the working) · why / why_ar (why this step comes now,
for stronger students). Values are computed here with sympy; the last step must equal the keyed option, otherwise
the question is reported and left unchanged. Figure-based questions use hand-read data (scripts/steps_manual_g910.py).

usage: python3 scripts/steps-grade9-10.py [--write] [--class 9G3]
"""
import importlib.util, json, math, re, sys
from pathlib import Path
import sympy as sp
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
_spec = importlib.util.spec_from_file_location('am', ROOT / 'scripts/audit-math.py'); am = importlib.util.module_from_spec(_spec)
_argv = sys.argv; sys.argv = ['x', 'none']; _spec.loader.exec_module(am); sys.argv = _argv
from steps_manual_g910 import MANUAL
L = lambda e: sp.latex(e)
WRITE = '--write' in sys.argv
ONLY = sys.argv[sys.argv.index('--class') + 1] if '--class' in sys.argv else None


SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def plain(t):   # LaTeX fragments inside a sentence -> readable text (2k, 3/4, x², √5)
    t = str(t)
    for _ in range(3): t = re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1)/(\2)', t)
    t = re.sub(r'\((-?[\w.]+)\)/\((-?[\w.]+)\)', r'\1/\2', t)
    t = re.sub(r'\^\{?(-?\d+)\}?', lambda m: m.group(1).translate(SUP), t)
    t = re.sub(r'\\sqrt\{([^{}]*)\}', r'√(\1)', t).replace('\\cdot', '·').replace('\\left', '').replace('\\right', '').replace('\\pi', 'π')
    t = re.sub(r'(\d) (?=[a-z(])', r'\1', t)
    return t.replace('{', '').replace('}', '')


def S(text, ar, latex='', why='', why_ar=''):
    d = {'text': plain(text), 'ar': plain(ar), 'latex': latex}
    if why: d['why'] = why; d['why_ar'] = why_ar
    return d


def P(t):
    e = am.P(t)
    if e is None: return None
    try: e = sp.sympify(str(e))   # canonical tree (the LaTeX parser returns nested, unevaluated sums)
    except Exception: pass
    return e.subs({s: sp.Symbol('d') for s in e.free_symbols if str(s) == 'delta'})   # audit parser renames d (not a differential)


def key_opt(q): return next(o for o in q['options'] if o['id'] == q['answer']['correct_option_id'])


def final(q, latex=None):
    o = key_opt(q)
    return S(f'So the answer is option {o["id"]}.', f'إذن الإجابة هي الخيار {o["id"]}.', latex if latex is not None else (o.get('math_latex') or ''),
             'Always compare your result with every option: a wrong sign or a missing term is a common trap.',
             'قارن ناتجك مع كل الخيارات: الإشارة الخاطئة أو الحد الناقص فخ شائع.')


def same(a, b):
    try: return sp.simplify(sp.expand(a - b)) == 0
    except Exception: return False


# ---------------- linear equations (one unknown) ----------------
def linear_steps(m):
    l, r = (P(s) for s in m.split('='))
    if l is None or r is None: return None
    fs = (l - r).free_symbols
    if len(fs) != 1: return None
    x = fs.pop(); v = str(x)
    st = []
    coeffs = [c for side in (sp.expand(l), sp.expand(r)) for c in sp.Poly(side, x).all_coeffs()]
    den = sp.ilcm(*[sp.fraction(sp.nsimplify(c))[1] for c in coeffs] or [1])
    if den != 1:
        l2, r2 = sp.expand(l * den), sp.expand(r * den)
        st.append(S(f'Multiply both sides by {den} to remove the fractions.', f'اضرب الطرفين في {den} لتتخلص من الكسور.', f'{L(l2)}={L(r2)}',
                    f'{den} is the least common denominator; whole numbers are easier and safer to work with.', f'{den} هو المضاعف المشترك الأصغر للمقامات؛ العمل بالأعداد الصحيحة أسهل وأضمن.'))
    else:
        l2, r2 = sp.expand(l), sp.expand(r)
        if (sp.srepr(l2), sp.srepr(r2)) != (sp.srepr(l), sp.srepr(r)):
            st.append(S('Remove the brackets (distribute) and combine like terms on each side.', 'فك الأقواس (التوزيع) واجمع الحدود المتشابهة في كل طرف.', f'{L(l2)}={L(r2)}',
                        'Each side must be simplified first; then the unknown appears in at most one term per side.', 'نبسّط كل طرف أولاً، فيظهر المجهول في حد واحد فقط في كل طرف.'))
    a = l2.coeff(x, 1) - r2.coeff(x, 1); c = r2.coeff(x, 0) - l2.coeff(x, 0)
    lx, rx, lc, rc = l2.coeff(x, 1) * x, r2.coeff(x, 1) * x, l2.coeff(x, 0), r2.coeff(x, 0)
    st.append(S(f'Move all {v}-terms to the left and all numbers to the right (do the opposite operation on both sides).', f'انقل حدود {v} إلى اليسار والأعداد إلى اليمين (نفّذ العملية العكسية على الطرفين).',
                f'{L(lx)}-({L(rx)})={L(rc)}-({L(lc)})\\ \\Rightarrow\\ {L(a * x) if a else "0"}={L(c)}', 'Collecting the unknown in one place leaves a one-step equation.', 'تجميع المجهول في مكان واحد يحوّل المعادلة إلى خطوة واحدة.'))
    if a == 0:
        kind = 'no solution' if c != 0 else 'all real numbers'
        st.append(S(('The unknown disappeared and the statement is false, so there is no solution.' if c != 0 else 'The unknown disappeared and the statement is always true, so every real number is a solution.'),
                    ('اختفى المجهول والعبارة خاطئة، إذن لا يوجد حل.' if c != 0 else 'اختفى المجهول والعبارة صحيحة دائماً، إذن كل الأعداد الحقيقية حلول.'),
                    '\\varnothing' if c != 0 else '\\mathbb{R}', 'When both sides have the same unknown term, compare the numbers left over.', 'عندما يتساوى حد المجهول في الطرفين نقارن الأعداد المتبقية.'))
        return st, ({'none'} if c != 0 else {'all'})
    sol = sp.nsimplify(c / a)
    st.append(S(f'Divide both sides by {L(a)}.', f'اقسم الطرفين على {L(a)}.', f'{v}={L(sol)}', f'{L(a)} is multiplying {v}; dividing undoes it.', f'العدد {L(a)} مضروب في {v}؛ القسمة تلغي الضرب.'))
    val = sp.nsimplify(l.subs(x, sol))
    st.append(S('Check: put the value back into the original equation; both sides must be equal.', 'تحقق: عوّض القيمة في المعادلة الأصلية؛ يجب أن يتساوى الطرفان.',
                f'\\text{{left}}={L(val)},\\ \\text{{right}}={L(sp.nsimplify(r.subs(x, sol)))}', 'Checking catches sign and arithmetic slips before you choose.', 'التحقق يكشف أخطاء الإشارات والحساب قبل الاختيار.'))
    return st, {sol}


def opt_value(o):
    t = o.get('math_latex') or o.get('text') or ''
    if re.search(r'no solution|varnothing|∅', t, re.I): return {'none'}
    if re.search(r'all real|mathbb|ℝ', t, re.I): return {'all'}
    s = am.P_set(t)
    return s


def H_equation(q):
    m = q.get('math_latex') or ''
    if m.count('=') != 1: return None
    r = linear_steps(m)
    if not r: return None
    st, sol = r
    ov = opt_value(key_opt(q))
    if ov is None: return None
    if ov != sol and not (len(ov) == 1 and ov <= sol):
        if not (re.search(r'round|nearest|decimal', q['instruction'], re.I) and len(sol) == 1 and 'none' not in sol and 'all' not in sol and abs(float(next(iter(ov))) - float(next(iter(sol)))) < 0.006): return False
    if re.search(r'round|nearest hundredth|decimal', q['instruction'], re.I) and len(sol) == 1 and next(iter(sol)) not in ('none', 'all'):
        v = next(iter(sol)); st.append(S('Write the value as a decimal and round to the nearest hundredth.', 'اكتب القيمة عدداً عشرياً وقرّبها لأقرب جزء من مئة.', f'{L(v)}\\approx {float(v):.2f}',
                                         'Round only at the end so earlier steps stay exact.', 'نقرّب في النهاية فقط حتى تبقى الخطوات السابقة دقيقة.'))
    return st + [final(q)]


# ---------------- solve for a variable (literal equations) ----------------
def H_literal(q):
    mm = re.search(r'[Ss]olve (?:the equation )?for ([a-z])', q['instruction'])
    m = q.get('math_latex') or ''
    if not mm or m.count('=') != 1: return None
    v = sp.Symbol(mm.group(1)); l, r = P(m.split('=')[0]), P(m.split('=')[1])
    if l is None or r is None: return None
    # parse_latex symbols may be distinct objects; map by name
    names = {str(s): s for s in (l - r).free_symbols}
    if mm.group(1) not in names: return None
    v = names[mm.group(1)]
    sol = sp.solve(sp.Eq(l, r), v)
    if len(sol) != 1: return None
    sol = sp.simplify(sol[0])
    ko = P(key_opt(q)['math_latex'].split('=')[-1])
    if ko is None: return None
    ko = ko.subs({s: names.get(str(s), s) for s in ko.free_symbols})
    if not same(ko, sol): return False
    num, den = sp.fraction(sp.together(l - r))
    st = []
    if den != 1:
        st.append(S(f'Multiply both sides by {L(den)} to clear the fraction.', f'اضرب الطرفين في {L(den)} لإزالة الكسر.', f'{L(sp.expand(l * den))}={L(sp.expand(r * den))}',
                    'With no fractions the term containing the variable is easy to isolate.', 'بعد إزالة الكسور يسهل عزل الحد الذي يحتوي المتغير.'))
        l, r = sp.expand(l * den), sp.expand(r * den)
    e = sp.expand(l - r); coef = e.coeff(v, 1); rest = sp.expand(-(e - coef * v))
    st.append(S(f'Keep the term with {v} on one side; move every other term to the other side.', f'أبقِ الحد الذي فيه {v} في طرف، وانقل باقي الحدود إلى الطرف الآخر.', f'{L(coef * v)}={L(rest)}',
                'Treat the other letters like numbers: undo addition/subtraction first, then multiplication.', 'عامل الحروف الأخرى كأنها أعداد: نلغي الجمع والطرح أولاً ثم الضرب.'))
    if coef != 1:
        st.append(S(f'Divide both sides by {L(coef)}.', f'اقسم الطرفين على {L(coef)}.', f'{v}={L(sp.simplify(rest / coef))}', f'{L(coef)} multiplies {v}; division undoes it.', f'{L(coef)} مضروب في {v}؛ القسمة تلغي الضرب.'))
    return st + [final(q)]


# ---------------- products / distribution / sums ----------------
def H_expand(q):
    if not re.search(r'gives the product|Distributive Property to (?:rewrite and )?simplify|sum or difference|Simplify\.?$', q['instruction']): return None
    m = q.get('math_latex') or ''
    e = P(m)
    if e is None or '=' in m: return None
    ko = P(key_opt(q)['math_latex'])
    if ko is None: return None
    res = sp.expand(e)
    if not same(ko, res): return False
    st = []
    if 'sum or difference' in q['instruction']:
        st.append(S('Remove the brackets. A minus sign in front of a bracket changes the sign of every term inside.', 'أزل الأقواس. إشارة السالب قبل القوس تغيّر إشارة كل حد داخله.', L(e),
                    'Brackets hide signs; opening them first prevents sign errors.', 'الأقواس تخفي الإشارات؛ فتحها أولاً يمنع أخطاء الإشارة.'))
        st.append(S('Group like terms (same letter and same power) and add their coefficients.', 'اجمع الحدود المتشابهة (نفس المتغير ونفس الأس) بجمع معاملاتها.', L(res),
                    'Only like terms can be combined; x² and x are different terms.', 'لا نجمع إلا الحدود المتشابهة؛ x² و x حدان مختلفان.'))
    else:
        fs = sp.Mul.make_args(sp.factor_terms(e)) if isinstance(e, sp.Mul) else [e]
        if isinstance(e, sp.Pow) and e.exp == 2:
            a, b = (sp.Add.make_args(e.base) + (0,))[:2]
            st.append(S('Use the square pattern: (a+b)² = a² + 2ab + b².', 'استخدم نمط مربع المجموع: (a+b)² = a² + 2ab + b².', f'({L(a)})^2+2({L(a)})({L(b)})+({L(b)})^2',
                        'The pattern is faster than multiplying and never forgets the middle term 2ab.', 'النمط أسرع من الضرب ولا ينسى الحد الأوسط 2ab.'))
        elif isinstance(e, sp.Mul) and sum(1 for f in sp.Mul.make_args(e) if isinstance(f, sp.Add)) == 2:
            A, B = [f for f in sp.Mul.make_args(e) if isinstance(f, sp.Add)]
            terms = [sp.Mul(a, b, evaluate=False) for a in sp.Add.make_args(A) for b in sp.Add.make_args(B)]
            st.append(S('Multiply each term of the first bracket by each term of the second (FOIL: First, Outer, Inner, Last).', 'اضرب كل حد في القوس الأول في كل حد في القوس الثاني (الأول، الخارجي، الداخلي، الأخير).',
                        '+'.join(L(sp.expand(t)) for t in terms).replace('+-', '-'), 'Every pair of terms must be multiplied once, otherwise a term is lost.', 'يجب ضرب كل زوج من الحدود مرة واحدة وإلا ضاع حد.'))
        else:
            st.append(S('Distribute: multiply the number outside by every term inside the bracket.', 'وزّع: اضرب العدد الذي خارج القوس في كل حد داخله.', L(sp.expand(e)),
                        'The Distributive Property: a(b + c) = ab + ac.', 'خاصية التوزيع: a(b + c) = ab + ac.'))
        st.append(S('Combine like terms and write the answer in standard form (highest power first).', 'اجمع الحدود المتشابهة واكتب الناتج بالصورة القياسية (الأس الأعلى أولاً).', L(res),
                    'Standard form makes it easy to compare with the options.', 'الصورة القياسية تسهّل المقارنة مع الخيارات.'))
    return st + [final(q)]


# ---------------- factoring ----------------
def H_factor(q):
    if 'complete factorisation' not in q['instruction']: return None
    m = (q.get('math_latex') or '').split('=')[-1]
    e = P(m)
    if e is None: return None
    ko = P(key_opt(q)['math_latex'])
    if ko is None or not same(ko, e): return False
    st = []
    g = sp.gcd_terms(e); content, prim = sp.factor_terms(e).as_coeff_Mul() if False else (None, None)
    gcf = sp.gcd(list(sp.Add.make_args(sp.expand(e))))
    rest = sp.expand(sp.expand(e) / gcf) if gcf != 1 else sp.expand(e)
    if gcf != 1:
        st.append(S(f'Look for the greatest common factor (GCF) of all terms: it is {L(gcf)}. Take it out.', f'ابحث عن العامل المشترك الأكبر لكل الحدود: إنه {L(gcf)}. أخرجه خارج القوس.',
                    f'{L(gcf)}\\left({L(rest)}\\right)', 'Always remove the GCF first; the bracket left over is smaller and easier to factor.', 'نخرج العامل المشترك أولاً دائماً؛ يبقى قوس أصغر وأسهل في التحليل.'))
    fr = sp.factor(rest)
    syms = sorted(rest.free_symbols, key=str)
    nterms = len(sp.Add.make_args(rest))
    if fr != rest and len(syms) == 1 and sp.degree(rest, syms[0]) == 2:
        x = syms[0]; a, b, c = [rest.coeff(x, k) for k in (2, 1, 0)]
        if b == 0 and c < 0:
            st.append(S('The bracket is a difference of two squares: a² − b² = (a − b)(a + b).', 'القوس فرق بين مربعين: a² − b² = (a − b)(a + b).', L(fr),
                        'Two square terms with a minus sign between them always split this way.', 'حدان مربعان بينهما إشارة سالب يتحللان دائماً بهذه الطريقة.'))
        else:
            st.append(S(f'Factor the trinomial: find two numbers whose product is a·c = {L(a * c)} and whose sum is b = {L(b)}.', f'حلّل ثلاثي الحدود: أوجد عددين حاصل ضربهما a·c = {L(a * c)} ومجموعهما b = {L(b)}.',
                        L(fr), 'These two numbers split the middle term, so the trinomial factors into two brackets.', 'هذان العددان يقسمان الحد الأوسط فيتحلل ثلاثي الحدود إلى قوسين.'))
    elif fr != rest and nterms == 4:
        st.append(S('Four terms: group them in pairs and take a common factor from each pair; the same bracket appears twice.', 'أربعة حدود: جمّعها في زوجين وأخرج عاملاً مشتركاً من كل زوج؛ سيظهر القوس نفسه مرتين.',
                    L(fr), 'Grouping turns a four-term polynomial into a product of two brackets.', 'التجميع يحوّل كثيرة الحدود الرباعية إلى حاصل ضرب قوسين.'))
    elif fr != rest:
        st.append(S('Factor what is left in the bracket.', 'حلّل ما تبقى داخل القوس.', L(fr), 'Keep factoring until no bracket can be factored further.', 'استمر في التحليل حتى لا يمكن تحليل أي قوس.'))
    full = sp.factor(e)
    st.append(S('Check by expanding: you must get the original expression back.', 'تحقق بالفك: يجب أن تحصل على المقدار الأصلي.', f'{L(full)}={L(sp.expand(e))}',
                '"Complete" factorisation means no bracket can be factored any further.', 'التحليل الكامل يعني أنه لا يمكن تحليل أي قوس أكثر.'))
    return st + [final(q)]


# ---------------- exponents / radicals / evaluate ----------------
def H_simplify(q):
    if not re.search(r'^Simplify|Evaluate\.?$|equivalent to the expression in simplified form', q['instruction']): return None
    m = q.get('math_latex') or ''
    if '=' in m: return None
    e = P(m)
    if e is None: return None
    ko = P(key_opt(q)['math_latex'])
    if ko is None: return None
    res = sp.simplify(sp.powsimp(sp.radsimp(e), force=True))
    pos = {s: sp.Symbol(str(s), positive=True) for s in (e.free_symbols | ko.free_symbols)}
    if not (same(ko.subs(pos), e.subs(pos)) or sp.simplify(ko.subs(pos) - e.subs(pos)) == 0): return False
    st = []
    if '\\sqrt' in m or '^{1/' in m or '\\sqrt[' in m:
        st.append(S('Write each number under the root as (perfect power) × (what is left), e.g. 50 = 25 × 2.', 'اكتب العدد تحت الجذر في صورة (قوة كاملة) × (الباقي)، مثل 50 = 25 × 2.', L(e),
                    'A perfect square (or cube) comes out of the root as a whole number.', 'المربع الكامل (أو المكعب الكامل) يخرج من الجذر عدداً صحيحاً.'))
        st.append(S('Take the perfect powers out of the root, then combine like radicals (same number under the root).', 'أخرج القوى الكاملة من الجذر، ثم اجمع الجذور المتشابهة (نفس العدد تحت الجذر).', L(ko),
                    'Only like radicals can be added, just like like terms: 7√7 − 2√7 = 5√7.', 'نجمع الجذور المتشابهة فقط مثل الحدود المتشابهة: 7√7 − 2√7 = 5√7.'))
    else:
        st.append(S('Use the exponent rules: same base → multiply means add exponents, divide means subtract exponents, (power)^n means multiply exponents.', 'استخدم قوانين الأسس: عند الضرب نجمع الأسس، وعند القسمة نطرحها، وعند رفع قوة لقوة نضربها.',
                    L(e), 'Work with one base at a time (numbers, then each letter) so nothing is missed.', 'تعامل مع كل أساس على حدة (الأعداد ثم كل حرف) حتى لا يفوتك شيء.'))
        st.append(S('Simplify the numbers and write every exponent as positive (x⁻ⁿ = 1/xⁿ, x⁰ = 1).', 'بسّط الأعداد واكتب كل الأسس موجبة (x⁻ⁿ = 1/xⁿ و x⁰ = 1).', L(ko),
                    'Simplified form has no negative or zero exponents and no common factors left.', 'الصورة المبسطة لا تحتوي أسساً سالبة أو صفرية ولا عوامل مشتركة.'))
    return st + [final(q)]


# ---------------- slope / lines ----------------
def pts(m):
    return [(sp.nsimplify(a), sp.nsimplify(b)) for a, b in re.findall(r'\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)', m.replace('−', '-'))]


def H_slope(q):
    if not re.search(r'slope of the line through', q['instruction']): return None
    p = pts(q.get('math_latex') or '')
    if len(p) != 2: return None
    (x1, y1), (x2, y2) = p
    st = [S('Write the slope formula: m = (change in y) ÷ (change in x).', 'اكتب قانون الميل: m = (التغير في y) ÷ (التغير في x).', 'm=\\dfrac{y_2-y_1}{x_2-x_1}',
            'Slope measures how much y changes for each 1 unit of x.', 'الميل يقيس مقدار تغيّر y لكل وحدة واحدة من x.'),
          S('Substitute the two points (keep the same order on top and bottom).', 'عوّض النقطتين (بنفس الترتيب في البسط والمقام).', f'm=\\dfrac{{{L(y2)}-({L(y1)})}}{{{L(x2)}-({L(x1)})}}',
            'Mixing the order of the points on top and bottom flips the sign.', 'تبديل ترتيب النقطتين بين البسط والمقام يقلب الإشارة.')]
    if x2 == x1:
        st.append(S('The bottom is 0: division by zero is impossible, so the slope is undefined (vertical line).', 'المقام صفر: القسمة على صفر مستحيلة، إذن الميل غير معرّف (مستقيم رأسي).', '\\dfrac{%s}{0}' % L(y2 - y1),
                    'Same x-values mean the line goes straight up and down.', 'تساوي قيم x يعني أن المستقيم رأسي.'))
        ans = 'undef'
    else:
        ans = sp.nsimplify((y2 - y1) / (x2 - x1))
        st.append(S('Simplify the fraction.', 'بسّط الكسر.', f'm=\\dfrac{{{L(y2 - y1)}}}{{{L(x2 - x1)}}}={L(ans)}',
                    'A positive slope rises to the right, a negative slope falls, 0 means horizontal.', 'الميل الموجب صاعد لليمين، والسالب هابط، والصفر أفقي.'))
    t = key_opt(q).get('math_latex') or key_opt(q)['text']
    if ans == 'undef': ok = 'ndefined' in t
    else:
        kv = P(t); ok = kv is not None and same(kv, ans)
    return (st + [final(q)]) if ok else False


def H_slope_int(q):
    if not re.search(r'slope-intercept form|is the slope-intercept form', q['instruction']) or 'point' in q['instruction']: return None
    m = q.get('math_latex') or ''
    if m.count('=') != 1: return None
    l, r = P(m.split('=')[0]), P(m.split('=')[1])
    if l is None or r is None: return None
    ys = [s for s in (l - r).free_symbols if str(s) == 'y']; xs = [s for s in (l - r).free_symbols if str(s) == 'x']
    if not ys: return None
    y = ys[0]; x = xs[0] if xs else sp.Symbol('x')
    sol = sp.solve(sp.Eq(l, r), y)[0]
    kt = key_opt(q)['math_latex'].split('=')[-1]; kv = P(kt)
    if kv is None: return None
    kv = kv.subs({s: x for s in kv.free_symbols if str(s) == 'x'})
    if not same(kv, sol): return False
    e = sp.expand(l - r); cy = e.coeff(y, 1); other = sp.expand(-(e - cy * y))
    st = [S('Goal: get y alone, y = mx + b. Move the x-term and the number to the other side.', 'الهدف: عزل y بالصورة y = mx + b. انقل حد x والعدد إلى الطرف الآخر.', f'{L(cy * y)}={L(other)}',
            'Slope-intercept form shows the slope m and the y-intercept b directly.', 'صيغة الميل والمقطع تُظهر الميل m والمقطع الصادي b مباشرة.'),
          S(f'Divide every term by {L(cy)}.', f'اقسم كل حد على {L(cy)}.', f'y={L(sol)}', 'Divide every term, not only the first one.', 'نقسم كل الحدود وليس الحد الأول فقط.'),
          S('Read the slope and the y-intercept.', 'اقرأ الميل والمقطع الصادي.', f'm={L(sol.coeff(x, 1))},\\ b={L(sol.coeff(x, 0))}', 'This lets you check the option quickly.', 'يساعدك ذلك على التحقق من الخيار بسرعة.')]
    return st + [final(q)]


# ---------------- arithmetic sequences ----------------
def seq_terms(m):
    t = re.sub(r'\\ldots|\\l?dots|\\ ', ' ', m)
    out = []
    for s in t.split(','):
        s = s.strip()
        if not s: continue
        e = P(s)
        if e is None: return None
        out.append(sp.nsimplify(e))
    return out


def H_sequence(q):
    ins = q['instruction']
    if not re.search(r'sequence is arithmetic|next three terms|th term\?|formula gives the nth term|Which term has value', ins): return None
    terms = seq_terms(q.get('math_latex') or '')
    if not terms or len(terms) < 3: return None
    d = [b - a for a, b in zip(terms, terms[1:])]
    st = [S('Subtract each term from the next one to find the differences.', 'اطرح كل حد من الحد الذي يليه لتجد الفروق.', ',\\ '.join(f'{L(b)}-({L(a)})={L(b - a)}' for a, b in zip(terms, terms[1:])),
            'An arithmetic sequence adds the same number (the common difference d) every time.', 'المتتابعة الحسابية يُضاف فيها العدد نفسه (الأساس d) في كل مرة.')]
    if len(set(d)) != 1:
        st.append(S('The differences are not all equal, so the sequence is NOT arithmetic.', 'الفروق غير متساوية، إذن المتتابعة ليست حسابية.', '\\text{differences not equal}',
                    'One unequal difference is enough to say "not arithmetic".', 'فرق واحد غير متساوٍ يكفي للحكم بأنها ليست حسابية.'))
        return st + [final(q)]
    dd = d[0]
    st.append(S(f'All differences are equal, so it is arithmetic with d = {L(dd)}.', f'كل الفروق متساوية، إذن المتتابعة حسابية والأساس d = {L(dd)}.', f'd={L(dd)}',
                'A constant difference — not a constant ratio — is what makes a sequence arithmetic.', 'الفرق الثابت (وليس النسبة الثابتة) هو ما يجعل المتتابعة حسابية.'))
    a1 = terms[0]; n = sp.Symbol('n'); an = sp.expand(a1 + (n - 1) * dd)
    if 'next three' in ins:
        nx = [terms[-1] + dd * k for k in (1, 2, 3)]
        st.append(S('Keep adding d to the last term.', 'استمر في إضافة d إلى آخر حد.', ',\\ '.join(L(v) for v in nx), 'Each new term = previous term + d.', 'كل حد جديد = الحد السابق + d.'))
    if re.search(r'formula|th term\?|term has value', ins):
        st.append(S('Use the nth-term formula aₙ = a₁ + (n − 1)d and simplify.', 'استخدم قانون الحد النوني aₙ = a₁ + (n − 1)d وبسّط.', f'a_n={L(a1)}+(n-1)({L(dd)})={L(an)}',
                    'a₁ is the first term; we add d one time fewer than the term number.', 'a₁ هو الحد الأول؛ ونضيف d عدداً من المرات أقل من رتبة الحد بواحد.'))
        mm = re.search(r'(\d+)th term', ins)
        if mm:
            k = int(mm.group(1)); st.append(S(f'Substitute n = {k}.', f'عوّض n = {k}.', f'a_{{{k}}}={L(an.subs(n, k))}', 'Substitute only after the formula is simplified.', 'نعوّض بعد تبسيط القانون.'))
        mm = re.search(r'value\s*[−-](\d+)', ins)
        if mm:
            target = -int(mm.group(1)); k = sp.solve(sp.Eq(an, target), n)[0]
            st.append(S(f'Set the formula equal to {target} and solve for n.', f'ساوِ القانون بـ {target} وحل المعادلة لإيجاد n.', f'{L(an)}={target}\\ \\Rightarrow\\ n={L(k)}',
                        'n must be a positive whole number (a position in the list).', 'يجب أن تكون n عدداً صحيحاً موجباً (رتبة في القائمة).'))
    return st + [final(q)]


# ---------------- step (floor) functions ----------------
def H_floor_eval(q):
    m = q.get('math_latex') or ''
    mm = re.search(r'f\(x\)=(.*?),\\quad x=(-?[\d.]+)', m)
    if not mm or 'lfloor' not in m: return None
    expr = mm.group(1).replace('\\lfloor', 'floor(').replace('\\rfloor', ')')
    x = sp.Symbol('x'); xv = sp.nsimplify(mm.group(2))
    inner = re.search(r'floor\((.*?)\)', expr).group(1)
    iv = sp.nsimplify(P(inner).subs({s: xv for s in P(inner).free_symbols}))
    fl = sp.floor(iv)
    outside = expr.replace(f'floor({inner})', 'F')
    res = P(outside.replace('F', f'({fl})')) if outside != 'F' else fl
    kv = P(key_opt(q)['math_latex'])
    if kv is None or not same(kv, res): return False
    return [S(f'Substitute x = {mm.group(2)} into the inside of the brackets first.', f'عوّض x = {mm.group(2)} داخل القوسين أولاً.', f'{L(P(inner))}\\to {L(iv)}',
              'The greatest-integer brackets act on the inside value, so it must be found first.', 'دالة أكبر عدد صحيح تعمل على القيمة الداخلية، لذا نحسبها أولاً.'),
            S('Take the greatest integer that is less than or equal to that value (go DOWN on the number line, also for negatives).', 'خذ أكبر عدد صحيح أصغر من القيمة أو يساويها (انزل على خط الأعداد، حتى للسالب).',
              f'\\lfloor {L(iv)}\\rfloor={fl}', 'For negatives going down means more negative: ⌊−1.4⌋ = −2, not −1.', 'للأعداد السالبة النزول يعني أكثر سالبية: ⌊−1.4⌋ = −2 وليس −1.'),
            S('Finish the rest of the formula (multiply / add).', 'أكمل باقي القانون (الضرب / الجمع).', f'f({mm.group(2)})={L(res)}', 'Outside operations come after the bracket is evaluated.', 'العمليات الخارجية تأتي بعد حساب القوس.'),
            final(q)]


# ---------------- inequalities (9A LO11/LO12) ----------------
def H_inequality(q):
    if not re.search(r'Solve the inequality', q['instruction']): return None
    m = q.get('math_latex') or ''
    mm = re.search(r'(\\le|\\ge|<|>)', m)
    if not mm: return None
    op = mm.group(1); l, r = P(m[:mm.start()]), P(m[mm.end():])
    if l is None or r is None: return None
    fs = (l - r).free_symbols
    if len(fs) != 1: return None
    x = fs.pop(); e = sp.expand(l - r); a = e.coeff(x, 1); c = -e.coeff(x, 0)
    if a == 0: return None
    flip = a < 0
    nop = {'<': '>', '>': '<', '\\le': '\\ge', '\\ge': '\\le'}[op] if flip else op
    b = sp.nsimplify(c / a)
    st = [S(f'Move the {x}-terms to one side and the numbers to the other, like an equation.', f'انقل حدود {x} إلى طرف والأعداد إلى الطرف الآخر كما في المعادلة.', f'{L(a * x)}{op}{L(c)}',
            'Adding or subtracting the same amount never changes the inequality sign.', 'جمع أو طرح العدد نفسه لا يغيّر إشارة المتباينة.'),
          S(f'Divide both sides by {L(a)}.' + (' Because it is negative, reverse the inequality sign.' if flip else ''), f'اقسم الطرفين على {L(a)}.' + (' ولأنه سالب اعكس إشارة المتباينة.' if flip else ''),
            f'{x}{nop}{L(b)}', 'Multiplying or dividing by a negative number reverses the order of numbers, so the sign flips.' if flip else 'Dividing by a positive number keeps the sign the same.',
            'الضرب أو القسمة على عدد سالب يعكس ترتيب الأعداد فتنقلب الإشارة.' if flip else 'القسمة على عدد موجب لا تغيّر الإشارة.'),
          S('Graph it: ' + ('closed circle (included)' if 'e' in nop else 'open circle (not included)') + f' at {L(b)}, shade ' + ('right' if '>' in nop or 'ge' in nop else 'left') + '.',
            'مثّلها: ' + ('دائرة مغلقة (مشمولة)' if 'e' in nop else 'دائرة مفتوحة (غير مشمولة)') + f' عند {L(b)}، وظلّل ' + ('يميناً' if '>' in nop or 'ge' in nop else 'يساراً') + '.',
            f'\\{{{x}\\mid {x}{nop}{L(b)}\\}}', '≤ and ≥ include the endpoint (closed); < and > do not (open).', '≤ و ≥ تشمل نقطة الحد (مغلقة)، و < و > لا تشملها (مفتوحة).')]
    kt = key_opt(q).get('math_latex') or key_opt(q)['text']
    if not (str(b).replace('-', '−') in kt.replace('-', '−') or L(b) in kt): return False
    return st + [final(q)]


# ---------------- quadratics (10G3) ----------------
def H_complete_square(q):
    if 'completing the square' not in q['instruction'] or '=' not in (q.get('math_latex') or ''): return None
    l, r = (P(s) for s in q['math_latex'].split('='))
    x = list((l - r).free_symbols)[0]; e = sp.expand(l - r); b = e.coeff(x, 1); c = e.coeff(x, 0)
    h = b / 2; rhs = h ** 2 - c
    sols = sp.solve(e, x)
    st = [S('Move the constant to the right side.', 'انقل العدد الثابت إلى الطرف الأيمن.', f'{L(x**2 + b*x)}={L(-c)}', 'Leave room on the left to build a perfect square.', 'نترك مكاناً في اليسار لبناء مربع كامل.'),
          S(f'Add (b/2)² = ({L(h)})² = {L(h**2)} to both sides.', f'أضف (b/2)² = ({L(h)})² = {L(h**2)} إلى الطرفين.', f'{L(x**2 + b*x + h**2)}={L(rhs)}',
            'Adding (b/2)² makes the left side a perfect square trinomial; adding to both sides keeps the balance.', 'إضافة (b/2)² تجعل الطرف الأيسر مربعاً كاملاً، وإضافتها للطرفين تحافظ على التوازن.'),
          S('Write the left side as a square.', 'اكتب الطرف الأيسر في صورة مربع.', f'({L(x + h)})^2={L(rhs)}', 'x² + bx + (b/2)² = (x + b/2)².', 'x² + bx + (b/2)² = (x + b/2)².'),
          S('Take the square root of both sides (remember ±), then isolate x.', 'خذ الجذر التربيعي للطرفين (تذكر ±)، ثم اعزل x.', f'{x}={L(-h)}\\pm{L(sp.sqrt(rhs))}\\ \\Rightarrow\\ {x}=' + ',\\ '.join(L(s) for s in sols),
            'Both the positive and negative roots square to the same number, so there are two solutions.', 'الجذر الموجب والسالب مربعهما واحد، لذلك يوجد حلان.')]
    return st + [final(q)]


def H_perfect_c(q):
    if 'perfect square' not in q['instruction'] or 'gives c' not in q['instruction']: return None
    e = sp.expand(P(q['math_latex'].replace('+c', '').replace('c', '')))
    x = [s for s in e.free_symbols if str(s) == 'x'][0]; b = e.coeff(x, 1); c = (b / 2) ** 2
    kv = P(key_opt(q)['math_latex'])
    if kv is None or not same(kv, c): return False
    return [S('Take half of the coefficient of x.', 'خذ نصف معامل x.', f'\\dfrac{{b}}{{2}}=\\dfrac{{{L(b)}}}{{2}}={L(b/2)}', 'A perfect square (x + k)² has middle term 2kx, so k = b/2.', 'المربع الكامل (x + k)² حده الأوسط 2kx، إذن k = b/2.'),
            S('Square it.', 'ربّعه.', f'c=\\left({L(b/2)}\\right)^2={L(c)}', 'The last term of (x + k)² is k².', 'الحد الأخير في (x + k)² هو k².'), final(q)]


def H_factor_solve(q):
    if 'Solve by factoring' not in q['instruction']: return None
    m = q.get('math_latex') or ''
    if m.count('=') != 1: return None
    l, r = (P(s) for s in m.split('='))
    e = sp.expand(l - r); x = list(e.free_symbols)[0]; f = sp.factor(e); sols = sorted(set(sp.solve(e, x)))
    ko = am.P_set(key_opt(q)['math_latex'])
    if ko is None or ko != set(sols): return False
    st = []
    if r != 0: st.append(S('Move everything to one side so the equation equals 0.', 'انقل كل الحدود إلى طرف واحد لتصبح المعادلة = 0.', f'{L(e)}=0', 'The zero-product property only works when one side is 0.', 'خاصية الضرب الصفري تعمل فقط عندما يكون أحد الطرفين صفراً.'))
    st += [S('Factor the expression.', 'حلّل المقدار.', f'{L(f)}=0', 'A product is easier to solve than a sum.', 'حاصل الضرب أسهل في الحل من المجموع.'),
           S('Set each factor equal to 0 and solve.', 'ساوِ كل عامل بالصفر وحل.', ',\\ '.join(f'{x}={L(s)}' for s in sols), 'If a·b = 0 then a = 0 or b = 0 (zero-product property).', 'إذا كان a·b = 0 فإن a = 0 أو b = 0 (خاصية الضرب الصفري).'),
           S('Check each solution in the original equation.', 'تحقق من كل حل في المعادلة الأصلية.', ',\\ '.join(f'{L(l.subs(x, s))}={L(r.subs(x, s))}' for s in sols), 'A lost factor (like a common factor x) loses a solution; checking catches it.', 'إهمال عامل (مثل x المشترك) يضيّع حلاً؛ التحقق يكشف ذلك.')]
    return st + [final(q)]


def H_no_real(q):
    if 'complete real solution set' not in q['instruction']: return None
    m = q.get('math_latex') or ''
    if m.count('=') != 1: return None
    l, r = (P(s) for s in m.split('='))
    e = sp.expand(l - r); x = list(e.free_symbols)[0]; a, b, c = [e.coeff(x, k) for k in (2, 1, 0)]
    D = b * b - 4 * a * c; sols = [s for s in sp.solve(e, x) if s.is_real]
    kt = key_opt(q).get('math_latex') or key_opt(q)['text']
    if D < 0 and not re.search(r'[Nn]o real', kt): return False
    st = [S('Write the equation in the form ax² + bx + c = 0 and read a, b, c.', 'اكتب المعادلة على الصورة ax² + bx + c = 0 واقرأ a و b و c.', f'a={L(a)},\\ b={L(b)},\\ c={L(c)}', 'The discriminant uses exactly these three numbers.', 'المميز يستخدم هذه الأعداد الثلاثة بالضبط.'),
          S('Find the discriminant b² − 4ac.', 'احسب المميز b² − 4ac.', f'({L(b)})^2-4({L(a)})({L(c)})={L(D)}', 'Its sign tells how many real solutions exist before solving.', 'إشارته تخبرنا بعدد الحلول الحقيقية قبل الحل.')]
    if D < 0: st.append(S('The discriminant is negative, so there is no real solution.', 'المميز سالب، إذن لا يوجد حل حقيقي.', '\\varnothing', 'The square root of a negative number is not real.', 'الجذر التربيعي لعدد سالب ليس عدداً حقيقياً.'))
    else: st.append(S('Solve with the quadratic formula or factoring.', 'حلّ بالقانون العام أو بالتحليل.', ',\\ '.join(f'{x}={L(s)}' for s in sols), 'D > 0 gives two solutions, D = 0 gives one.', 'المميز الموجب يعطي حلين، والصفر يعطي حلاً واحداً.'))
    return st + [final(q)]


def H_transform(q):
    if not re.search(r'translation from the parent function y=x²|graph relative to the parent y=x²|translation of g\(x\) relative to the parent f\(x\)=\|x\||dilation relative to the parent function f\(x\)=x|For g\(x\)=[\d.]+x relative', q['instruction']): return None
    m = q.get('math_latex') or ''
    if not m and 'For g(x)' in q['instruction']: m = re.search(r'g\(x\)=[\d.]+x', q['instruction']).group(0)
    rhs = m.split('=')[-1]
    is_abs = '|' in m or '\\left|' in m
    parent = '|x|' if is_abs else ('x^2' if 'x²' in q['instruction'] else 'x')
    st = [S(f'Compare g(x) with the parent y = {parent}. Write g in the form a·f(x − h) + k.', f'قارن g(x) بالدالة الأم y = {parent}. اكتب g على الصورة a·f(x − h) + k.', f'g(x)={rhs}',
            'Each of a, h and k controls one change, so reading them one by one avoids mixing them up.', 'كل من a و h و k يتحكم في تغيير واحد، وقراءتها واحداً واحداً تمنع الخلط.'),
          S('Inside the function: x − h moves the graph RIGHT h; x + h moves it LEFT h. Outside: + k moves UP, − k moves DOWN.', 'داخل الدالة: x − h تنقل المنحنى يميناً h، و x + h تنقله يساراً h. خارجها: + k لأعلى و − k لأسفل.', '',
            'The inside change works opposite to its sign because it changes x before the function acts.', 'التغيير الداخلي يعمل عكس إشارته لأنه يغيّر x قبل تطبيق الدالة.'),
          S('Multiplying by a: |a| > 1 stretches, 0 < |a| < 1 compresses, a negative a reflects in the x-axis.', 'الضرب في a: إذا كان |a| > 1 تمدد، وإذا كان 0 < |a| < 1 انكماش، و a السالبة انعكاس حول محور x.', '',
            'a multiplies every y-value, so it changes the height, not the left-right position.', 'a تضرب كل قيم y فتغيّر الارتفاع لا الموقع الأفقي.')]
    return st + [final(q)]


def H_quadratic(q):
    m = q.get('math_latex') or ''
    if m.count('=') != 1: return None
    l, r = (P(t) for t in m.split('='))
    if l is None or r is None: return None
    fs = (l - r).free_symbols
    if len(fs) != 1: return None
    x = fs.pop(); e = sp.expand(l - r)
    if sp.degree(e, x) != 2: return None
    sols = sorted(set(s_ for s_ in sp.solve(e, x) if s_.is_real))
    ko = am.P_set(key_opt(q)['math_latex'])
    if ko is None or (ko != set(sols) and not (len(ko) == 1 and ko <= set(sols) and re.search(r'which value|satisf', q['instruction'], re.I))): return False
    if isinstance(l, sp.Pow) and l.exp == 2 and r.is_number:
        k = sp.sqrt(r)
        st = [S('The left side is already a square, so take the square root of both sides. Write ± because two numbers have this square.', 'الطرف الأيسر مربع، فخذ الجذر التربيعي للطرفين. اكتب ± لأن هناك عددين لهما هذا المربع.',
                f'{L(l.base)}=\\pm{L(k)}', 'Square-rooting undoes squaring; forgetting ± loses one solution.', 'الجذر يلغي التربيع؛ نسيان ± يضيّع أحد الحلين.'),
              S('Solve the two simple equations.', 'حل المعادلتين البسيطتين.', ',\\ '.join(f'{x}={L(v)}' for v in sols), 'Each sign gives one value of x.', 'كل إشارة تعطي قيمة لـ x.')]
    else:
        f = sp.factor(e)
        st = [S('Move all terms to one side so the equation equals 0.', 'انقل كل الحدود إلى طرف واحد لتصبح المعادلة = 0.', f'{L(e)}=0', 'Standard form ax² + bx + c = 0 is needed to factor or use the formula.', 'الصورة القياسية ax² + bx + c = 0 ضرورية للتحليل أو القانون العام.'),
              S('Factor (or use the quadratic formula) and set each factor equal to 0.', 'حلّل (أو استخدم القانون العام) وساوِ كل عامل بالصفر.', f'{L(f)}=0\\ \\Rightarrow\\ ' + ',\\ '.join(f'{x}={L(v)}' for v in sols),
                'If a product is 0, at least one factor is 0.', 'إذا كان حاصل الضرب صفراً فأحد العوامل على الأقل صفر.')]
    st.append(S('Check by substituting each value into the original equation.', 'تحقق بالتعويض بكل قيمة في المعادلة الأصلية.', ',\\ '.join(f'{L(l.subs(x, v))}={L(r.subs(x, v))}' for v in sols), 'Both values must make the two sides equal.', 'يجب أن تجعل كل قيمة الطرفين متساويين.'))
    return st + [final(q)]


def H_proportion(q):
    m = q.get('math_latex') or ''
    if m.count('=') != 1 or '\\frac' not in m or not re.search(r'proportion|Solve\. Round', q['instruction']): return None
    l, r = (P(t) for t in m.split('='))
    if l is None or r is None: return None
    fs = (l - r).free_symbols
    if len(fs) != 1: return None
    x = fs.pop(); a, b = sp.fraction(sp.together(l)); c, d = sp.fraction(sp.together(r))
    lhs, rhs = sp.expand(a * d), sp.expand(b * c)
    sol = sp.solve(sp.Eq(lhs, rhs), x)
    if len(sol) != 1: return None
    v = sp.nsimplify(sol[0]); ko = am.P_set(key_opt(q)['math_latex'])
    if ko is None: return None
    ok = ko == {v} or (len(ko) == 1 and abs(float(next(iter(ko))) - float(v)) < 0.006)
    if not ok: return False
    st = [S('Cross-multiply: (top left) × (bottom right) = (bottom left) × (top right).', 'اضرب ضرباً تبادلياً: (بسط الأيسر) × (مقام الأيمن) = (مقام الأيسر) × (بسط الأيمن).', f'{L(a)}\\cdot({L(d)})=({L(b)})\\cdot {L(c)}',
            'In a proportion a/b = c/d the cross products are equal, which removes the fractions in one move.', 'في التناسب a/b = c/d يتساوى حاصلا الضرب التبادلي، فتزول الكسور بخطوة واحدة.'),
          S('Distribute and simplify both sides.', 'وزّع وبسّط الطرفين.', f'{L(lhs)}={L(rhs)}', 'Now it is an ordinary linear equation.', 'أصبحت معادلة خطية عادية.'),
          S(f'Solve for {x}.', f'حل المعادلة لإيجاد {x}.', f'{x}={L(v)}' + (f'\\approx {float(v):.2f}' if v.q != 1 else ''), 'Isolate the unknown: collect terms, then divide.', 'اعزل المجهول: اجمع الحدود ثم اقسم.'),
          S('Check that no denominator becomes 0 for this value.', 'تأكد أن أي مقام لا يساوي صفراً عند هذه القيمة.', ',\\ '.join(f'{L(t)}={L(t.subs(x, v))}' for t in (b, d) if t.free_symbols), 'A value that makes a denominator 0 is not allowed.', 'القيمة التي تجعل المقام صفراً مرفوضة.')]
    return st + [final(q)]


def H_abs_ineq(q):
    m = q.get('math_latex') or ''
    mm = re.match(r'^\|(.+)\|\s*(\\le|\\ge|<|>)\s*(-?\d+)$', m.replace('\\left', '').replace('\\right', ''))
    if not mm: return None
    inner, op, k = P(mm.group(1)), mm.group(2), int(mm.group(3))
    x = list(inner.free_symbols)[0]; kt = key_opt(q).get('math_latex') or ''
    st = [S('Look at the number on the right first.', 'انظر أولاً إلى العدد في الطرف الأيمن.', f'|{L(inner)}|{op}{k}', 'An absolute value is a distance, so it is never negative.', 'القيمة المطلقة مسافة، فلا تكون سالبة أبداً.')]
    if k < 0:
        less = op in ('<', '\\le')
        st.append(S('A distance cannot be less than a negative number: no solution.' if less else 'A distance is always greater than a negative number: every real number works.',
                    'المسافة لا تكون أقل من عدد سالب: لا يوجد حل.' if less else 'المسافة دائماً أكبر من العدد السالب: كل الأعداد الحقيقية حلول.', '\\varnothing' if less else '\\mathbb{R}',
                    'Check the sign of the right side before doing any algebra.', 'افحص إشارة الطرف الأيمن قبل أي عمليات.'))
        ok = ('emptyset' in kt or 'varnothing' in kt) if less else 'mathbb' in kt
        return (st + [final(q)]) if ok else False
    if op in ('<', '\\le'):
        lo = sp.solve(sp.Eq(inner, -k), x)[0]; hi = sp.solve(sp.Eq(inner, k), x)[0]; lo, hi = min(lo, hi), max(lo, hi)
        st += [S(f'"Less than" means "between": write it as a compound "and" inequality.', 'عبارة "أقل من" تعني "بين": اكتبها متباينة مركبة بـ "و".', f'-{k}{op}{L(inner)}{op}{k}', 'The distance from 0 is smaller than k, so the expression lies between −k and k.', 'المسافة عن الصفر أقل من k، فالمقدار يقع بين −k و k.'),
               S('Do the same operation on all three parts to isolate the variable.', 'نفّذ العملية نفسها على الأجزاء الثلاثة لعزل المتغير.', f'{L(lo)}{op}{x}{op}{L(hi)}', 'Whatever is done to the middle must be done to both ends.', 'ما نفعله للوسط نفعله للطرفين.')]
        want = f'{L(lo)}, {L(hi)}'
    else:
        a = sp.solve(sp.Eq(inner, -k), x)[0]; b = sp.solve(sp.Eq(inner, k), x)[0]; a, b = min(a, b), max(a, b)
        flip = {'>': '<', '\\ge': '\\le'}[op]
        st += [S('"Greater than" means "outside": split into two inequalities joined by "or".', 'عبارة "أكبر من" تعني "خارج": قسّمها إلى متباينتين بينهما "أو".', f'{L(inner)}{flip}-{k}\\ \\text{{or}}\\ {L(inner)}{op}{k}', 'The distance from 0 is more than k, so the expression is beyond −k or beyond k.', 'المسافة عن الصفر أكبر من k، فالمقدار أبعد من −k أو أبعد من k.'),
               S('Solve each inequality.', 'حل كل متباينة.', f'{x}{flip}{L(a)}\\ \\text{{or}}\\ {x}{op}{L(b)}', 'Two separate rays, one on each side.', 'شعاعان منفصلان، كل منهما في جهة.')]
        want = f'{L(a)}' 
    ok = all(str(v).replace('-', '-') in kt.replace(' ', '').replace('\\left', '').replace('\\right', '') for v in (re.findall(r'-?\d+', want)))
    return (st + [S('Write the solution in interval notation and graph it.', 'اكتب الحل بترميز الفترات ومثّله.', kt, 'Square brackets [ ] include the endpoint (≤, ≥); round brackets ( ) do not.', 'القوس [ ] يشمل نقطة الحد (≤، ≥)، والقوس ( ) لا يشملها.'), final(q)]) if ok else False


def H_point_slope(q):
    if 'point-slope form' not in q['instruction']: return None
    p = pts(q['math_latex'])
    if len(p) != 2: return None
    (x1, y1), (x2, y2) = p; m = sp.nsimplify((y2 - y1) / (x2 - x1))
    kt = key_opt(q)['math_latex']
    if not re.search(r'=\s*' + re.escape(L(m)) + r'\\bigl', kt.replace(' ', '')) and L(m) not in kt: return False
    return [S('Find the slope from the two points.', 'أوجد الميل من النقطتين.', f'm=\\dfrac{{{L(y2)}-({L(y1)})}}{{{L(x2)}-({L(x1)})}}={L(m)}', 'Point-slope form needs the slope and one point.', 'صيغة النقطة والميل تحتاج الميل ونقطة واحدة.'),
            S('Use the first point (x₁, y₁) in y − y₁ = m(x − x₁).', 'استخدم النقطة الأولى (x₁, y₁) في y − y₁ = m(x − x₁).', f'y-({L(y1)})={L(m)}\\bigl(x-({L(x1)})\\bigr)', 'Keep the brackets so the signs of negative coordinates stay correct.', 'أبقِ الأقواس حتى تبقى إشارات الإحداثيات السالبة صحيحة.'),
            final(q)]


def line_from(m, pt):
    x = sp.Symbol('x'); b = sp.nsimplify(pt[1] - m * pt[0]); return sp.expand(m * x + b), b


def H_par_perp(q):
    ins = q['instruction']
    if not re.search(r'parallel|perpendicular', ins) or not re.search(r'slope-intercept', ins): return None
    m = q['math_latex']; x = sp.Symbol('x'); y = sp.Symbol('y')
    pt = pts(m) or pts(ins)
    if not pt: return None
    pt = pt[0]
    eq = m.split(',\\quad')[-1] if '\\quad' in m else m
    l, r = (P(t) for t in eq.split('='))
    sub = {s: (x if str(s) == 'x' else y) for s in (l - r).free_symbols}
    giv = sp.solve(sp.Eq(l.subs(sub), r.subs(sub)), y)[0]; mg = sp.nsimplify(giv.coeff(x, 1))
    lines = []
    st = [S('Write the given line as y = mx + b and read its slope.', 'اكتب المستقيم المعطى على الصورة y = mx + b واقرأ ميله.', f'y={L(giv)}\\ \\Rightarrow\\ m={L(mg)}', 'Parallel and perpendicular lines are decided by slopes only.', 'التوازي والتعامد يتحددان بالميل فقط.')]
    want = []
    if 'parallel' in ins:
        f, b = line_from(mg, pt); want.append(f)
        st.append(S(f'Parallel: same slope m = {L(mg)}. Substitute the point ({L(pt[0])}, {L(pt[1])}) into y = mx + b to find b.', f'التوازي: الميل نفسه m = {L(mg)}. عوّض النقطة ({L(pt[0])}, {L(pt[1])}) في y = mx + b لإيجاد b.',
                    f'{L(pt[1])}={L(mg)}({L(pt[0])})+b\\Rightarrow b={L(b)}\\Rightarrow y={L(f)}', 'Parallel lines rise at the same rate, so they never meet.', 'المستقيمات المتوازية لها معدل الصعود نفسه فلا تلتقي.'))
    if 'perpendicular' in ins:
        mp = -1 / mg; f, b = line_from(mp, pt); want.append(f)
        st.append(S(f'Perpendicular: negative reciprocal slope m = {L(mp)}. Substitute the point to find b.', f'التعامد: الميل هو المقلوب السالب m = {L(mp)}. عوّض النقطة لإيجاد b.',
                    f'{L(pt[1])}={L(mp)}({L(pt[0])})+b\\Rightarrow b={L(b)}\\Rightarrow y={L(f)}', 'Perpendicular slopes multiply to −1: flip the fraction and change the sign.', 'حاصل ضرب ميلي المتعامدين −1: اقلب الكسر وغيّر الإشارة.'))
    kt = key_opt(q)['math_latex']; parts = [t.split('=')[-1] for t in re.split(r',\\quad', kt)]
    kv = [P(t) for t in parts]
    if any(v is None for v in kv): return None
    kv = [v.subs({s: x for s in v.free_symbols}) for v in kv]
    if len(kv) != len(want) or not all(same(a, b) for a, b in zip(kv, want)): return False
    return st + [final(q)]


def H_inverse(q):
    if 'inverse of the given relation' not in q['instruction']: return None
    return [S('To find the inverse, swap x and y in every ordered pair.', 'لإيجاد العلاقة العكسية بدّل x و y في كل زوج مرتب.', '(x,\\,y)\\to(y,\\,x)', 'The inverse undoes the relation: inputs become outputs and outputs become inputs.', 'العكسية تلغي العلاقة: المدخلات تصبح مخرجات والعكس.'),
            S('Swap each pair; do not change any sign.', 'بدّل كل زوج دون تغيير أي إشارة.', key_opt(q)['math_latex'], 'Changing signs gives a reflection, not the inverse.', 'تغيير الإشارات يعطي انعكاساً لا العلاقة العكسية.'), final(q)]


def H_line_points(q):
    ins = q['instruction']; m = q.get('math_latex') or ''
    x = sp.Symbol('x')
    if 'given slope through the given point' in ins:
        mm = re.search(r'm=(.+?),\\quad P=\((-?\d+), (-?\d+)\)', m)
        mv = P(mm.group(1)); pt = (int(mm.group(2)), int(mm.group(3))); f, b = line_from(mv, pt)
        kv = P(key_opt(q)['math_latex'])
        if kv is None or not same(kv.subs({s: x for s in kv.free_symbols}), f): return False
        return [S('Start with y = mx + b and put in the slope.', 'ابدأ بالصيغة y = mx + b وعوّض الميل.', f'y={L(mv)}x+b', 'Only b is unknown now.', 'أصبح المجهول هو b فقط.'),
                S('Substitute the point to find b.', 'عوّض النقطة لإيجاد b.', f'{pt[1]}={L(mv)}({pt[0]})+b\\Rightarrow b={L(b)}', 'The point lies on the line, so its coordinates satisfy the equation.', 'النقطة تقع على المستقيم فإحداثياتها تحقق المعادلة.'),
                S('Write the equation.', 'اكتب المعادلة.', f'y={L(f)}', '', ''), final(q)]
    if 'given point is on the line' in ins:
        p = pts(m)[0]; rhs = P(m.split('y=')[-1]); val = sp.nsimplify(rhs.subs({s: p[0] for s in rhs.free_symbols}))
        return [S(f'Substitute x = {p[0]} into the equation.', f'عوّض x = {p[0]} في المعادلة.', f'y={L(rhs.subs({s: sp.UnevaluatedExpr(p[0]) for s in rhs.free_symbols}))}={L(val)}', 'A point is on a line exactly when its coordinates make the equation true.', 'تقع النقطة على المستقيم عندما تحقق إحداثياتها المعادلة.'),
                S(f'Compare with the point\'s y-value {p[1]}.', f'قارن بالإحداثي y للنقطة وهو {p[1]}.', f'{L(val)}' + ('=' if val == p[1] else '\\ne') + f'{p[1]}', 'Equal → on the line; not equal → not on the line.', 'التساوي يعني أنها على المستقيم، وعدمه يعني أنها ليست عليه.'), final(q)]
    if 'another point on the line' in ins:
        (x1, y1), (x2, y2) = pts(m); mv = sp.nsimplify((y2 - y1) / (x2 - x1))
        ko = pts(key_opt(q)['math_latex'])[0]
        if (ko[1] - y1) * (x2 - x1) != (y2 - y1) * (ko[0] - x1): return False
        return [S('Find the slope (rise over run) between the two points.', 'أوجد الميل (الارتفاع ÷ المسافة الأفقية) بين النقطتين.', f'm=\\dfrac{{{y2}-({y1})}}{{{x2}-({x1})}}={L(mv)}', 'Every pair of points on a line has the same slope.', 'كل زوج نقاط على المستقيم له الميل نفسه.'),
                S('Keep stepping with the same rise and run from a known point.', 'استمر بالخطوات نفسها (الارتفاع والمسافة الأفقية) من نقطة معلومة.', f'({x2},{y2})\\to({x2 + (x2 - x1)},{y2 + (y2 - y1)})\\to\\dots', 'Adding the same run and rise stays on the line.', 'إضافة المسافة والارتفاع نفسيهما تبقينا على المستقيم.'),
                S(f'Check the option point ({ko[0]}, {ko[1]}): its slope from ({x1}, {y1}) is also {L(mv)}.', f'تحقق من نقطة الخيار ({ko[0]}, {ko[1]}): ميلها من ({x1}, {y1}) يساوي أيضاً {L(mv)}.', f'\\dfrac{{{ko[1]}-({y1})}}{{{ko[0]}-({x1})}}={L(mv)}', 'Same slope from a point on the line ⇒ on the same line.', 'الميل نفسه من نقطة على المستقيم يعني أنها على المستقيم نفسه.'), final(q)]
    return None


def H_rate_table(q):
    m = q.get('math_latex') or ''; ins = q['instruction']
    if not re.search(r'rate of change|linear function', ins): return None
    if 'array' in m:
        rows = re.findall(r'(x|y)&([^\\]+?)(?:\\\\|\\end)', m)
        if len(rows) != 2: return None
        xs = [sp.nsimplify(v) for v in rows[0][1].split('&')]; ys = [sp.nsimplify(v) for v in rows[1][1].split('&')]
        P_ = list(zip(xs, ys))
    else:
        P_ = pts(m)
    if len(P_) < 3: return None
    rates = [sp.nsimplify((b[1] - a[1]) / (b[0] - a[0])) for a, b in zip(P_, P_[1:])]
    st = [S('For each pair of neighbouring points find (change in y) ÷ (change in x).', 'لكل نقطتين متتاليتين احسب (التغير في y) ÷ (التغير في x).', ',\\ '.join(f'\\dfrac{{{L(b[1])}-({L(a[1])})}}{{{L(b[0])}-({L(a[0])})}}={L(r)}' for (a, b), r in zip(zip(P_, P_[1:]), rates)),
            'A function is linear exactly when this rate is the same everywhere.', 'تكون الدالة خطية عندما يكون هذا المعدل ثابتاً في كل مكان.')]
    if len(set(rates)) == 1: st.append(S(f'All rates are equal, so the function is linear with rate of change {L(rates[0])}.', f'كل المعدلات متساوية، إذن الدالة خطية ومعدل تغيرها {L(rates[0])}.', f'\\text{{rate}}={L(rates[0])}', 'The constant rate is the slope of the line.', 'المعدل الثابت هو ميل المستقيم.'))
    else: st.append(S('The rates are different, so the function is not linear.', 'المعدلات مختلفة، إذن الدالة ليست خطية.', '\\text{not constant}', 'One different rate is enough.', 'معدل واحد مختلف يكفي.'))
    return st + [final(q)]


def H_standard_form(q):
    if 'standard form and its leading' not in q['instruction']: return None
    e = P(q['math_latex']); v = list(e.free_symbols)[0]; pl = sp.Poly(sp.expand(e), v)
    lc = pl.LC(); kt = key_opt(q)['math_latex']
    if not kt.replace(' ', '').endswith(str(lc)): return False
    return [S('Find the exponent of each term.', 'حدّد أس كل حد.', ',\\ '.join(f'{L(t)}:\\ {sp.degree(t, v)}' for t in sp.Add.make_args(sp.expand(e))), 'Standard form orders terms by their exponents.', 'الصورة القياسية ترتب الحدود حسب أسسها.'),
            S('Write the terms from the highest exponent to the lowest.', 'اكتب الحدود من الأس الأكبر إلى الأصغر.', L(pl.as_expr()), 'The first term then shows the degree.', 'عندها يُظهر الحد الأول درجة كثيرة الحدود.'),
            S(f'The leading coefficient is the number in front of the first term: {lc}.', f'المعامل الرئيس هو العدد أمام الحد الأول: {lc}.', f'\\text{{leading coefficient}}={lc}', 'Include the sign: −y³ has leading coefficient −1.', 'انتبه للإشارة: معامل −y³ هو −1.'), final(q)]


def H_geo_mean(q):
    if 'positive geometric mean' not in q['instruction']: return None
    nums = [P(t) for t in re.split(r'\\quad\\text\{and\}\\quad|\s+and\s+', q['math_latex'])]
    if len(nums) != 2 or any(n is None for n in nums): return None
    g = sp.sqrt(nums[0] * nums[1]); kv = P(key_opt(q)['math_latex'])
    if kv is None or not same(kv, g): return False
    return [S('The geometric mean of a and b is √(a·b).', 'الوسط الهندسي للعددين a و b هو √(a·b).', f'\\sqrt{{{L(nums[0])}\\cdot {L(nums[1])}}}', 'It is the number x with a/x = x/b.', 'هو العدد x الذي يحقق a/x = x/b.'),
            S('Multiply, then simplify the root.', 'اضرب ثم بسّط الجذر.', f'\\sqrt{{{L(nums[0] * nums[1])}}}={L(g)}', 'Take out the largest perfect square factor.', 'أخرج أكبر عامل مربع كامل.'), final(q)]


def H_nroot(q):
    m = q.get('math_latex') or ''
    mm = re.match(r'^\\sqrt\[(\d+)\]\{(\d+)\}$', m)
    if not mm or not q['instruction'].startswith('Evaluate'): return None
    n, a = int(mm.group(1)), int(mm.group(2)); r = sp.root(a, n)
    kv = P(key_opt(q)['math_latex'])
    if kv is None or kv != r: return False
    return [S(f'Ask: which number multiplied by itself {n} times gives {a}?', f'اسأل: ما العدد الذي إذا ضُرب في نفسه {n} مرات يعطي {a}؟', f'{L(r)}^{{{n}}}={a}', 'The n-th root undoes raising to the n-th power.', 'الجذر النوني يلغي الرفع للقوة n.'),
            S('So the root equals that number.', 'إذن الجذر يساوي هذا العدد.', f'\\sqrt[{n}]{{{a}}}={L(r)}', 'Check by raising your answer to the power n.', 'تحقق برفع إجابتك للقوة n.'), final(q)]


HANDLERS = [H_proportion, H_abs_ineq, H_point_slope, H_par_perp, H_inverse, H_line_points, H_rate_table, H_standard_form, H_geo_mean, H_nroot, H_literal, H_inequality, H_complete_square, H_perfect_c, H_factor_solve, H_no_real, H_quadratic, H_equation, H_factor, H_expand, H_simplify, H_slope, H_slope_int, H_sequence, H_floor_eval, H_transform]


def main():
    report = {'done': 0, 'manual': 0, 'mismatch': [], 'unhandled': []}
    for c in [ONLY] if ONLY else ['9G3', '9A', '10G3', '10A1']:
        p = ROOT / f'public/data/study/{c}.json'; b = json.loads(p.read_text())
        for q in b['questions']:
            if q['type'] != 'mcq': continue
            if q['id'] in MANUAL:
                q['answer']['steps'] = MANUAL[q['id']] + [final(q)]; q['answer']['steps_verified'] = True; report['manual'] += 1; continue
            res = None
            for h in HANDLERS:
                try: res = h(q)
                except Exception as ex: res = None
                if res is not None: break
            if res is False: report['mismatch'].append(q['id']); continue
            if not res: report['unhandled'].append(q['id']); continue
            q['answer']['steps'] = res; q['answer']['steps_verified'] = True; report['done'] += 1
        if WRITE: p.write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':')))
    print('generated', report['done'], 'manual', report['manual'], 'mismatch', len(report['mismatch']), 'unhandled', len(report['unhandled']))
    print('MISMATCH', report['mismatch'])
    Path(ROOT / 'content-imports/steps-g910-unhandled.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
