"""Calculator + written-solution support for the Grade 11/12 study banks (11G, 11A, 12G, 12A).

Adds (or replaces) only those four classes in public/data/study/calculator-support.json; the Grade 9/10 entries are untouched.
Every question gets: the outcome set-up (by hand), the ClassWiz route for the topic, the reference solution and the original
question image (shown by the UI). Key sequences are generated ONLY for numeric expressions listed in EXPRESSIONS below and are
checked in the CE X emulator by tests/calculator-support.test.js. Nothing here is a device capture.
"""
import ast, json, re, sys
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from upper_grades_meta import META

X = S.Symbol('X', real=True)
KEY_LABELS = {'LP': '(', 'RP': ')', 'ADD': '+', 'SUB': '−', 'MUL': '×', 'DIV': '÷', 'POW': 'x^□', 'RIGHT': '→', 'SQRT': '√', 'NEG': '(−)', 'EQ': '=', 'DOT': '.', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan',
              'SHIFT': 'SHIFT', 'ALPHA': 'ALPHA', 'LN': 'ln', 'EXP': '×10^□/π', 'AC': 'AC'}


def numeric(text):
    def walk(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return S.Rational(str(n.value))
        if isinstance(n, ast.Name) and n.id == 'pi': return S.pi
        if isinstance(n, ast.UnaryOp): return -walk(n.operand) if isinstance(n.op, ast.USub) else walk(n.operand)
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            return {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b, ast.Div: lambda: a / b, ast.Pow: lambda: a ** b}[type(n.op)]()
        if isinstance(n, ast.Call):
            a = walk(n.args[0]); f = n.func.id
            return {'sqrt': S.sqrt, 'ln': S.log, 'exp': S.exp}[f](a)
        raise ValueError(text)
    return walk(ast.parse(text.replace('^', '**'), mode='eval').body)


def input_keys(expr):
    def walk(n):
        if isinstance(n, ast.Constant): return ['DOT' if c == '.' else c for c in str(n.value)]
        if isinstance(n, ast.Name) and n.id == 'pi': return ['SHIFT', 'EXP']
        if isinstance(n, ast.UnaryOp): return (['NEG'] if isinstance(n.op, ast.USub) else []) + ['LP'] + walk(n.operand) + ['RP']
        if isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Pow): return ['LP'] + walk(n.left) + ['RP', 'POW'] + walk(n.right) + ['RIGHT']
            op = {ast.Add: 'ADD', ast.Sub: 'SUB', ast.Mult: 'MUL', ast.Div: 'DIV'}[type(n.op)]
            return ['LP'] + walk(n.left) + [op] + walk(n.right) + ['RP']
        if isinstance(n, ast.Call):
            f = n.func.id
            if f == 'sqrt': return ['SQRT'] + walk(n.args[0]) + ['RIGHT']
            if f == 'ln': return ['LN'] + walk(n.args[0]) + ['RP']
            if f == 'exp': return ['SHIFT', 'LN'] + walk(n.args[0]) + ['RIGHT']
        raise ValueError(expr)
    return walk(ast.parse(expr.replace('^', '**'), mode='eval').body)


def operation(expr, purpose):
    e = numeric(expr)
    assert not e.free_symbols and e.is_real, expr
    keys = ['AC'] + input_keys(expr) + ['EQ']
    return {'input': expr.replace('**', '^'), 'exact': S.latex(S.simplify(e)), 'decimal': str(S.N(e, 12)), 'purpose': purpose, 'keys': keys, 'key_labels': [KEY_LABELS.get(k, k) for k in keys]}


# (question id) -> [(purpose, calculator expression)]. Each expression is the arithmetic that the written method reduces to.
EXPRESSIONS = {
    '11A-Q05-changebase': [('Change of base: log₂11 = ln 11 ÷ ln 2.', 'ln(11)/ln(2)')],
    '11A-Q05-added-01': [('Change of base: log₃11 = ln 11 ÷ ln 3.', 'ln(11)/ln(3)')],
    '11A-Q05-added-02': [('Change of base: log₄13 = ln 13 ÷ ln 4.', 'ln(13)/ln(4)')],
    '11A-Q05-added-03': [('Change of base: log₅15 = ln 15 ÷ ln 5.', 'ln(15)/ln(5)')],
    '11A-Q05-added-04': [('Change of base: log₆17 = ln 17 ÷ ln 6.', 'ln(17)/ln(6)')],
    '11A-Q06-ln': [('Evaluate ⅓ln 8 − ln 3 + ln 9 and compare with the single logarithm you wrote by hand.', '(1/3)*ln(8)-ln(3)+ln(9)')],
    '11A-Q06-added-01': [('Evaluate 2 ln 3 − ln 6 and compare with ln(9/6).', '2*ln(3)-ln(6)')],
    '11A-Q06-added-02': [('Evaluate 2 ln 4 − ln 7 and compare with ln(16/7).', '2*ln(4)-ln(7)')],
    '11A-Q06-added-03': [('Evaluate 2 ln 5 − ln 8 and compare with ln(25/8).', '2*ln(5)-ln(8)')],
    '11A-Q06-added-04': [('Evaluate 2 ln 6 − ln 9 and compare with ln 4.', '2*ln(6)-ln(9)')],
    '11A-Q21-10': [('Average rate of change = (f(−2) − f(−5)) / 3 for f(x)=3e^(x−1)+3.', '(3*exp(-2-1)+3-(3*exp(-5-1)+3))/(-2-(-5))')],
    '11A-Q21-11': [('Average rate of change = (f(−1) − f(−3)) / 2 for f(x)=4e^(2x)−1.', '((4*exp(2*(-1))-1)-(4*exp(2*(-3))-1))/(-1-(-3))')],
    '11A-Q21-12': [('Average rate of change = (f(−4) − f(−7)) / 3 for f(x)=−2e^(x+3)+2.', '((-2*exp(-4+3)+2)-(-2*exp(-7+3)+2))/(-4-(-7))')],
    '11A-Q22-thorium': [('Decay constant k = ln 2 ÷ half-life.', 'ln(2)/75381'), ('Remaining mass = 2·e^(−k·1500).', '2*exp(-1500*ln(2)/75381)')],
    '11A-Q22-iodine': [('Decay constant k = ln 2 ÷ 8.02 (round to the nearest thousandth in the answer).', 'ln(2)/8.02'), ('Remaining mass with the unrounded k: 15·e^(−20k).', '15*exp(-20*ln(2)/8.02)')],
    '11A-Q24-traffic': [('Standardise: z = (100000 − 98452) ÷ 10325.', '(100000-98452)/10325')],
    '11A-Q25-example': [('Arc length s = rθ = 80 × 3π/2.', '80*3*pi/2')],
    '11A-Q25-52': [('Arc length s = rθ = 100 × π/2.', '100*pi/2')],
    '11A-Q25-53': [('Arc length s = rθ = 5 × 4π/3.', '5*4*pi/3')],
}

TOPICS = [  # keyword (lower-case, in the English title) -> (route key)
    ('trigonometr', 'trig'), ('sinusoid', 'trig'), ('periodic', 'trig'), ('angles in standard', 'trig'), ('degrees, radians', 'trig'), ('right-triangle', 'trig'),
    ('logarithm', 'log'), ('change of base', 'log'), ('natural base', 'log'), ('natural logarithm', 'log'), ('exponential', 'exp'),
    ('normal', 'normal'), ('empirical', 'normal'), ('distribution', 'stats'), ('probab', 'prob'), ('sample space', 'prob'), ('counting', 'prob'), ('statistical', 'none'), ('sampling', 'none'),
    ('quadratic', 'poly'), ('discriminant', 'poly'), ('polynomial', 'poly'), ('factoring', 'poly'), ('completing', 'poly'), ('squares', 'poly'),
    ('derivative', 'deriv'), ('power rule', 'deriv'), ('product', 'deriv'), ('chain rule', 'deriv'), ('implicit', 'deriv'), ('velocity', 'deriv'), ('mean value', 'deriv'), ('rolle', 'deriv'),
    ('limit', 'limit'), ('continuity', 'limit'), ('squeeze', 'limit'), ('asymptote', 'limit'), ('infinite', 'limit'),
    ('pythagor', 'geo'), ('distance', 'geo'), ('triangle', 'geo'), ('geometric mean', 'geo'), ('dilation', 'geo'), ('polygon', 'geo'), ('similar', 'geo'),
    ('graph', 'table'), ('rational', 'table'), ('reciprocal', 'table'),
]
ROUTES = {
    'trig': ('Set the angle unit first, then use sin/cos/tan (SHIFT + key for the inverse). Keep full precision.', ['SHIFT → MENU (SETUP) → Angle Unit → Degree (or Radian for π-based arguments).', 'MENU → Calculate. Use sin, cos or tan; SHIFT + sin/cos/tan gives the inverse function.', 'Keep full precision and round only the final answer. The calculator evaluates a ratio; it does not replace the diagram reading or the written method.']),
    'log': ('Use ln for base e and ln(a) ÷ ln(b) for log base b. Check the domain by hand first.', ['MENU → Calculate. For log_b(a) enter ln(a) ÷ ln(b) (or log(a) ÷ log(b)); require a>0, b>0, b≠1.', 'ln is the key above the log keys; e^x is SHIFT then ln. To solve an exponential equation, isolate the exponential, then take logarithms.', 'Keep full precision for decay constants; show the algebra and domain restrictions in the written answer.']),
    'exp': ('Rewrite with a common base when possible; otherwise take logarithms. Use the power key for evaluations.', ['MENU → Calculate. Enter powers with the x^□ key and leave the exponent box with the → key.', 'For growth/decay y = a·bᵗ evaluate b^t after you set the model up by hand; e^x is SHIFT then ln.', 'A table of values (MENU → Table) helps you plot points; it does not draw the graph.']),
    'normal': ('Standardise z = (x−μ)/σ and read the area from the supplied table, or use Normal CD / Inverse Normal.', ['MENU → Distribution → Normal CD for an interval probability: enter lower bound, upper bound, σ and μ in the labelled fields.', 'For inverse values use Inverse Normal: enter the left-tail area, σ and μ; convert a right-tail probability to a left-tail area first.', 'When the question requires the supplied z-table, show z=(x−μ)/σ and use that table with the prescribed rounding.']),
    'stats': ('Enter the data in STATISTICS and read the mean, deviation and quartiles; describe shape from the graph yourself.', ['MENU → Statistics → 1-Variable. Enter the data, then press AC and OPTN → 1-Variable Calc.', 'Read n, x̄, σ and the quartiles; compute IQR = Q3 − Q1 by hand.', 'Shape (symmetric/skewed) is a judgement from the display, not a calculator output.']),
    'prob': ('List or count the outcomes first; use the calculator only for the arithmetic of the probabilities.', ['MENU → Calculate. Enter fractions with the fraction key; use SHIFT ÷ (nCr) and SHIFT × (nPr) for counting.', 'Multiply along tree branches (and), add between branches (or); subtract the overlap when events are not mutually exclusive.', 'Convert to a percentage only at the end; keep exact fractions while you calculate.']),
    'poly': ('Rearrange to standard form first; the Equation/Func solver gives every root to check your factorisation or formula.', ['MENU → Equation/Func → Polynomial → Degree 2 (or 3). Enter each coefficient with its sign and press =.', 'Compare each root with the factorisation you found by hand and substitute it back.', 'For an inequality use MENU → Inequality (or test one point in every interval by hand).']),
    'deriv': ('Differentiate by hand with the rules; the calculator can check a derivative value at a point.', ['MENU → Calculate. Press SHIFT then the ∫dx key to insert d/dx(f(x))|x=a; type f(x) and the value of x.', 'Use the result to check your derivative at that single point; it never replaces the rule-based working.', 'For a tangent line use y − f(a) = f′(a)(x − a).']),
    'limit': ('Decide the limit algebraically (substitute, factor, divide by the highest power); the calculator only shows the trend numerically.', ['MENU → Calculate. Type f(x) with the x variable, then press CALC and enter values such as a ± 0.001 from both sides.', 'Both one-sided trends must agree; a calculator table is evidence, not proof.', 'For limits at infinity evaluate at large values of x (for example 10⁶) to see the trend.']),
    'geo': ('Draw or read the diagram first, set up the ratio or formula by hand, then calculate.', ['MENU → Calculate. Use x², √ and the fraction key; keep exact values (S⇔D) until the final decimal.', 'Match corresponding sides before forming a proportion; check the scale factor with a second pair.', 'For lengths take the positive root only.']),
    'table': ('Read key features from the graph, or build a TABLE of values to plot and compare.', ['MENU → Table. Enter f(x) with the x variable; leave g(x) blank if it is not needed.', 'Set Start, End and Step to produce the required x-values; avoid excluded x-values of rational functions.', 'Copy x and f(x) into your table and plot the points. TABLE does not draw the graph.']),
    'none': ('This is a reasoning question: decide with the definitions, no calculation is needed.', []),
}


def route_for(title):
    t = title.lower()
    for kw, r in TOPICS:
        if kw in t: return r
    return 'geo'


def main():
    sup_path = ROOT / 'public/data/study/calculator-support.json'
    sup = json.loads(sup_path.read_text())
    report = {}
    for cls in ['11G', '11A', '12G', '12A']:
        bank = json.loads((ROOT / f'public/data/study/{cls}.json').read_text())
        outcomes, guides, ops = {}, {}, 0
        for lo in bank['learning_outcomes']:
            r = route_for(lo['title'])
            tip, steps = ROUTES[r]
            outcomes[lo['id']] = {'title': lo['title'], 'prepare': f"{lo['rule_summary']} {tip}", 'route': r}
        for q in bank['questions']:
            lo = outcomes[q['learning_outcome_id']]; route = lo['route']
            card = q.get('figure_in_image')
            role = 'manual_setup' if card else ('reasoning' if route == 'none' else 'check' if q['id'] in EXPRESSIONS else 'reasoning')
            _, steps = ROUTES[route]
            if q['type'] == 'mcq':
                a = q['answer']; opt = next(o for o in q['options'] if o['id'] == a['correct_option_id'])
                sols = [{'part': 'Answer', 'math': opt.get('math_latex') or '', 'text': a['explanation'], 'answer_text': '' if opt.get('math_latex') else (opt.get('text') or f"Option {a['correct_option_id']}")}]
            else:
                sols = [{'part': p['id'], 'math': p['answer'].get('math_latex', ''), 'text': p['answer']['model_answer_and_marking'], 'answer_text': ''} for p in q['parts']]
            prepare = lo['prepare']
            if card: prepare += ' Read the whole question from the image (all labels, scales and options) before choosing a method.'
            g = {'outcome': q['learning_outcome_id'], 'outcome_title': lo['title'], 'role': role, 'prepare': prepare, 'operations': [], 'tables': [], 'solutions': sols,
                 'source_ids': ['reviewed-bank', 'upstream-modes'], 'setup': steps,
                 'interpret': 'Write the method, the substitution and the final answer with units. Calculator output alone does not justify the answer.' if role != 'check' else 'Matching values give a numerical check only; show the algebraic steps in your written solution.'}
            for purpose, expr in EXPRESSIONS.get(q['id'], []):
                g['operations'].append(operation(expr, purpose)); ops += 1
            guides[q['id']] = g
        assert len(guides) == len(bank['questions'])
        sup['classes'][cls] = {'outcomes': outcomes, 'questions': guides}
        report[cls] = {'outcomes': len(outcomes), 'questions': len(guides), 'operations': ops}
    sup_path.write_text(json.dumps(sup, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
