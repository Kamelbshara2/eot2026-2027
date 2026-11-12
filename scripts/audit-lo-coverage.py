#!/usr/bin/env python3
"""Outcome-description coverage audit (teacher request 2026-11-12).

For every learning outcome, each meaningful word of its EOT description (title) - an action such as graph/solve/
identify, or one item of a list such as 'polynomial, rational and trigonometric' or 'AA, SSS and SAS' - must occur in
at least one question of that outcome (instruction, statement, maths, options, parts, worked steps). Graphing actions
also count interactive graphs/number lines and figure-based graph options.
Prints the gaps; exit code 1 if any. usage: python3 scripts/audit-lo-coverage.py [--json out.json]
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CLASSES = ['9G3', '9A', '10G3', '10A1', '11G', '11A', '12G', '12A']
STOP = set('a an the of and or to in on with for from by using use its their into at as is are be one more than both each given two three containing word words other its it that this functions function'.split())
ALIASES = {   # description word -> words/patterns that show it is practised
    'graph': r'graph|plot|sketch|number line|numberline|shade', 'graphs': r'graph|plot|sketch', 'graphing': r'graph|plot|table of values',
    'solve': r'solv|solution', 'solving': r'solv|solution', 'identify': r'identif|which|determine|classif|choose|name', 'write': r'write|equation|express',
    'evaluate': r'evaluat|find|value|calculat', 'find': r'find|value|calculat|determin', 'simplify': r'simplif', 'factor': r'factor', 'factoring': r'factor',
    'construct': r'construct|write|create|find', 'create': r'create|write|construct', 'apply': r'apply|use|find|solve|evaluat', 'translate': r'translat|represent|sentence|verbal|which equation',
    'convert': r'convert|rewrite|write .* form|exponential form|logarithmic form', 'interpret': r'interpret|mean|describe|explain|what does', 'describe': r'describ|explain|which statement',
    'estimate': r'estimat|approximat|≈', 'classify': r'classif|which type|identify the type|survey|experiment|observational', 'represent': r'represent|list|table|tree|sample space',
    'analyse': r'analy|describe|determine', 'analyze': r'analy|describe|determine', 'sketch': r'sketch|graph', 'determine': r'determin|find|which|whether',
    'compare': r'compar|which is|greater|less', 'design': r'design|simulat|spinner', 'state': r'state|find|domain|range|which', 'read': r'read|graph|shown|figure',
    'properties': r'propert|rule|law', 'property': r'propert|rule|law', 'rules': r'rule|law', 'laws': r'law|rule|limit of', 'applications': r'application|word problem|real|cost|height|distance|speed|population|money|\$',
    'application': r'application|cost|height|distance|speed|population|\$', 'context': r'context|cost|height|distance|area|ball|bag|\$|ft|m\b', 'equations': r'equation|=', 'equation': r'equation|=',
    'inequalities': r'inequalit|<|>|\\le|\\ge', 'inequality': r'inequalit|<|>|\\le|\\ge', 'expressions': r'expression|simplif|evaluat', 'expression': r'expression|simplif|evaluat',
    'variables': r'variable|[a-z]\s*=', 'variable': r'variable|[a-z]\s*=', 'sides': r'side|leg|hypotenuse', 'angles': r'angle|°', 'angle': r'angle|°', 'points': r'point|\(-?\d', 'point': r'point|\(-?\d',
    'algebraically': r'factor|simplif|substitut|algebra|\\frac', 'graphically': r'graph|figure|shown|plot', 'products': r'product|multiply|×|\\cdot|\)\(', 'quotients': r'quotient|divide|\\frac',
    'monic': r'x\^\{?2\}?\s*[+-]', 'trinomials': r'trinomial|x\^\{?2\}?.*[+-].*[+-]', 'trinomial': r'trinomial|x\^\{?2\}?.*[+-].*[+-]', 'binomial': r'binomial|\)\s*\(', 'polynomials': r'polynomial|x\^', 'polynomial': r'polynomial|x\^',
    'sequences': r'sequence|term', 'sequence': r'sequence|term', 'arithmetic': r'arithmetic|common difference|d\s*=', 'nth': r'n\s*th|a_n|aₙ|nth|formula', 'term': r'term|a_', 'formula': r'formula|a_n|=',
    'specific': r'solve for|for [a-z]\b', 'center': r'center|centre|mean|median', 'spread': r'spread|standard deviation|range|iqr|σ', 'shape': r'shape|skew|symmetric|normal',
    'distribution': r'distribution|normal|data', 'probabilities': r'probabilit|P\(', 'probability': r'probabilit|P\(', 'experimental': r'experimental|trial|simulat|times', 'theoretical': r'theoretical|probabilit',
    'events': r'event|P\(', 'dependent': r'dependent|without replacement|given', 'independent': r'independent|with replacement|P\(A\)\s*\\?c?d?o?t?\s*P', 'exclusive': r'exclusive|or|P\(A\s*(∪|\\cup|or)',
    'conditional': r'conditional|given|\|', 'mutually': r'mutually|exclusive', 'counting': r'counting|ways|choices', 'fundamental': r'fundamental|ways|choices|multiply', 'principle': r'principle|ways|choices',
    'statistical': r'survey|experiment|observational|study', 'studies': r'survey|experiment|observational|study', 'types': r'type|survey|experiment|observational|classif', 'simulations': r'simulat|spinner|random', 'simulation': r'simulat|spinner|random',
    'standard': r'standard|position|initial side|terminal|form', 'position': r'position|terminal|initial|quadrant', 'ratios': r'ratio|sin|cos|tan', 'ratio': r'ratio|sin|cos|tan|:', 'values': r'value|evaluat|find|=',
    'periodic': r'period|amplitude|cycle', 'sinusoidal': r'sin|cos|amplitude|period|midline', 'trigonometric': r'sin|cos|tan|sec|csc|cot|trig', 'inverse': r'inverse|\^\{-1\}|arc|swap|⁻¹', 'reciprocal': r'reciprocal|\\frac\{1\}|1/x|\\frac\{[a-z0-9]\}\{x|csc|sec|cot',
    'transformations': r'transform|translat|shift|stretch|reflect|dilat', 'translations': r'translat|shift|left|right|up|down', 'dilations': r'dilat|stretch|compress|scale', 'reflections': r'reflect',
    'exponential': r'exponential|\^x|\^\{x|e\^|\^t|\^\{t', 'growth': r'growth|grow|increas|tripl|doubl|\^t', 'decay': r'decay|half-life|decreas|depreciat', 'logarithmic': r'log|ln', 'logarithms': r'log|ln', 'logarithm': r'log|ln',
    'natural': r'ln|e\^|\\ln|natural', 'base': r'base|log_', 'change': r'change|log_|\\ln', 'rational': r'rational|\\frac\{[^}]*x', 'complex': r'complex|\\frac\{\\frac|\\dfrac\{\\dfrac', 'fractions': r'fraction|\\frac',
    'oblique': r'oblique|slant', 'asymptotes': r'asymptote', 'asymptote': r'asymptote', 'holes': r'hole', 'horizontal': r'horizontal|y\s*=\s*-?\d', 'vertical': r'vertical|x\s*=\s*-?\d', 'normal': r'normal|z|empirical|σ|μ', 'areas': r'area|percent|%|P\(',
    'degrees': r'degree|°', 'radians': r'radian|\\pi|π', 'arc': r'arc', 'length': r'length|L\s*=|distance', 'phase': r'phase|shift', 'shift': r'shift|translat|left|right',
    'limits': r'lim|limit', 'limit': r'lim|limit', 'infinite': r'\\infty|∞|infinit', 'infinity': r'\\infty|∞|infinit', 'continuity': r'continu', 'compositions': r'compos|f\(g|\\circ',
    'velocity': r'velocit|speed|m/s|ft/s', 'average': r'average|mean|\\frac\{f\(', 'instantaneous': r'instantan|derivative|at t', 'derivative': r'derivative|\'|prime|d/dx|\\frac\{d', 'derivatives': r'derivative|\'|prime|d/dx|\\frac\{d',
    'implicit': r'implicit|dy/dx|y\'', 'differentiation': r'derivative|differentiat|prime|\'', 'squeeze': r'squeeze|sandwich', 'theorem': r'theorem|squeeze|rolle|mean value|pythag', 'hypotheses': r'hypothes|continuous|differentiable|condition',
    'similar': r'similar|∼|~|scale', 'similarity': r'similar|∼|~|AA|SSS|SAS', 'polygons': r'polygon|quadrilateral|pentagon|triangle', 'triangles': r'triangle|△', 'triangle': r'triangle|△',
    'bisectors': r'bisector|bisect', 'altitudes': r'altitude|height', 'medians': r'median', 'corresponding': r'corresponding|similar|∼', 'proportional': r'proportion|ratio|parallel|midsegment', 'proportions': r'proportion|ratio|=\\frac|\\frac\{.*\}=\\frac', 'parts': r'segment|part|midsegment|parallel',
    'geometric': r'geometric|√|\\sqrt', 'mean': r'mean|√|\\sqrt|average', 'pythagorean': r'pythag|a\^2\s*\+\s*b\^2|hypotenuse|²\s*\+', 'converse': r'converse|classif|acute|obtuse|right triangle', 'distance': r'distance|√', 'midpoint': r'midpoint',
    'space': r'space|\(\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*\)|z', 'elevation': r'elevation', 'depression': r'depression', 'perimeter': r'perimeter|P\s*=', 'area': r'area|A\s*=', 'sines': r'sin', 'ambiguous': r'ambiguous|two triangles|SSA|no triangle|one triangle',
    'case': r'case|SSA|triangle', 'special': r'special|45|30|60|√2|√3|\\sqrt\{?2|\\sqrt\{?3', 'right': r'right|90|hypotenuse', 'interior': r'interior|angle sum|\(n-2\)|180', 'exterior': r'exterior|360',
    'kites': r'kite', 'parallelograms': r'parallelogram', 'tests': r'test|guarantee|condition|prove', 'coordinates': r'coordinat|\(-?\d', 'scale': r'scale|factor|k\s*=', 'factors': r'factor|k\s*=|scale',
    'gcf': r'gcf|common factor|greatest common', 'grouping': r'group|four terms|\)\s*\(.*\)\s*\(', 'distribution ': r'distribut', 'difference': r'difference|-|−', 'squares': r'square|\^2|²', 'sums': r'sum|\+', 'sum': r'sum|\+',
    'special-product': r'special|square|difference of', 'factorization': r'factor', 'extrema': r'extrem|maximum|minimum|vertex', 'features': r'vertex|axis|intercept|zero|maximum|minimum|domain|range', 'characteristics': r'vertex|axis|intercept|zero|maximum|minimum|domain|range|symmetry',
    'zeros': r'zero|root|x-intercept|=\s*0', 'maxima': r'maxim', 'minima': r'minim', 'relative': r'relative|local', 'power': r'power|\^', 'end': r'end behavio|\\to\s*\\?infty|x\s*\\to', 'behavior': r'behavio|\\to', 'behaviour': r'behavio|\\to',
    'long': r'long division|divide|quotient', 'synthetic': r'synthetic', 'division': r'divi|quotient|remainder', 'discriminant': r'discriminant|b\^2\s*-\s*4ac|b²', 'nature': r'nature|real|imaginary|complex|how many', 'roots': r'root|solution|zero',
    'quadratic': r'quadratic|x\^\{?2|x²', 'quadratics': r'quadratic|x\^\{?2|x²', 'complete': r'complet', 'completing': r'complet', 'square': r'square|\^2|²', 'formula ': r'formula', 'two': r'two|2',
    'empirical': r'empirical|68|95|99.7', 'sampling': r'sampl', 'biased': r'bias', 'questions': r'question|survey', 'add': r'add|\+|sum', 'subtract': r'subtract|-|−', 'multiply': r'multipl|×|\\cdot|\)\(',
    'operations': r'add|subtract|multipl|\+|-', 'measures': r'measure|angle|°', 'sample': r'sample', 'spaces': r'space|outcome|list|tree',
    'numerical': r'numerical|\d', 'verbal': r'verbal|words|sentence|which expression', 'distributive': r'distribut', 'equality': r'equal|=|propert', 'rearrange': r'solve for|rearrang|for [a-z]\b', 'formulas': r'formula|solve for',
    'proportion': r'proportion|\\frac\{.*\}=\\frac', 'multi-step': r'.', 'parameters': r'a\\ne|a≠|parameter|ax', 'slope': r'slope|m\s*=|rise', 'slope-intercept': r'slope-intercept|y\s*=\s*mx|y=.*x', 'intercept': r'intercept', 'intercepts': r'intercept',
    'linear': r'linear|y\s*=|x\s*\+|rate', 'rate': r'rate|slope|per', 'constant': r'constant|horizontal|y\s*=\s*-?\d', 'step': r'step|floor|lfloor|greatest integer', 'piecewise': r'piecewise|cases', 'piecewise-defined': r'piecewise|cases',
    'identities': r'identit|all real|\\mathbb\{R\}|ℝ', 'contradictions': r'contradict|no solution|\\varnothing|∅', 'table': r'table|array', 'parallel': r'parallel', 'perpendicular': r'perpendicular', 'lines': r'line|y\s*=',
    'point-slope': r'point-slope|y\s*-\s*\(?-?\d', 'relations': r'relation|\{\(', 'inverses': r'inverse|swap', 'absolute': r'absolute|\|', 'compound': r'compound|and|or|<.*<', 'and': r'and', 'arguments': r'arithmetic|justif|reason|because|differences',
    'nth term': r'nth|a_n', 'foil': r'\)\s*\(|\\left\(.*\\right\)\s*\\left\(', 'monomials': r'monomial|\^', 'exponents': r'exponent|\^', 'negative': r'negative|\^\{-|⁻', 'zero': r'zero|\^0|\^\{0\}', 'rational exponents': r'\^\{\d/|\\frac\{1\}\{\d\}\}', 'roots ': r'√|\\sqrt',
    'completing-square': r'complet|\(b/2\)|perfect square', 'complete': r'complet|\(b/2\)|perfect square', 'multiplication': r'multipl|product|\\cdot|×', 'dilation': r'dilat|scale factor|k\s*=',
    'right-triangle': r'right|hypotenuse|90', 'trigonometry': r'sin|cos|tan', 'law': r'law|\\frac\{\w\}\{\\sin|/\s*sin|sin\s*[A-C]', 'sss': r'SSS|three side|side ratios|all three', 'sas': r'SAS|included angle',
    'non-mutually': r'non-mutually|not mutually|overlap|both|P\(A\s*(and|∩|\\cap)', 'algebraic': r'algebra|\\frac\{[^}]*[a-z]', 'involving': r'.', 'definition': r'definition|three conditions|f\(a\)|lim',
    'arc': r'arc|curve length|segments', 'analyze': r'analy|behavio|zero|degree|turning|maximum|minimum|end', 'expression': r'expression|x\^', 'quadratic ': r'quadratic',
    'radicals': r'radical|√|\\sqrt', 'methods': r'method|complet|square root|factor', 'reasoning': r'reason|justif|explain|because|why|whether', 'solving': r'solv',
}


# Reviewed 2026-11-12: the word is practised, only written in another form (symbol, maths or picture).
REVIEWED = {
    ('9G3', 'LO03', 'addition'): 'equations x + a = b written with +', ('9G3', 'LO03', 'subtraction'): 'equations x − a = b written with −',
    ('9A', 'LO07', 'interpret'): 'slope, intercept and zero read from graphs', ('9A', 'LO08', 'apply'): 'every item applies a translation', ('9A', 'LO08', 'value'): 'absolute value written |x|',
    ('9A', 'LO09', 'solutions'): 'solution sets read from number-line graphs', ('9A', 'LO11', 'linear'): 'linear inequalities in symbols', ('9A', 'LO11', 'operation'): 'multi-step inequalities',
    ('9A', 'LO12', 'value'): 'absolute value written |x|', ('9A', 'LO13', 'apply'): 'every item applies a dilation', ('9A', 'LO15', 'identify'): 'options identify the parallel/perpendicular equations',
    ('9A', 'LO19', 'value'): 'absolute value written |x|', ('9A', 'LO20', 'form'): 'answers in y = mx + b form', ('9A', 'LO21', 'distribution'): 'equations with brackets a(x + b) solved by distributing',
    ('10G3', 'LO01', 'binomial'): 'products (ax + b)(cx + d)', ('10G3', 'LO02', 'differences'): '(a − b)² items', ('10G3', 'LO04', 'distribution'): 'GCF factoring is distribution reversed',
    ('10G3', 'LO05', 'analyse'): 'which values of k / which trinomial factors', ('10G3', 'LO06', 'non-monic'): 'trinomials 5x² + …, 2x² + …', ('10G3', 'LO10', 'rational'): 'exponents 1/4, 1/3, 1/5 and n-th roots',
    ('10G3', 'LO24', 'quadratic'): 'quadratic graphs in the figures', ('10A1', 'LO06', 'properties'): 'opposite sides/angles, bisecting diagonals', ('10A1', 'LO14', 'parts'): 'altitudes, medians, bisectors of similar triangles',
    ('10A1', 'LO22', 'reasoning'): 'angle-sum reasoning items', ('11G', 'LO21', 'properties'): 'proportional sides, scale factor', ('11A', 'LO06', 'base'): 'e is the natural base (e^x, ln)',
    ('11A', 'LO17', 'properties'): 'period, amplitude, midline', ('11A', 'LO21', 'base'): 'e is the natural base (e^x, ln)', ('12A', 'LO02', 'graphically'): 'three graph cards',
    ('12A', 'LO04', 'laws'): 'sum/product/quotient limit laws in the steps', ('12A', 'LO04', 'rational'): '0/0 rational limits factored', ('12A', 'LO21', 'applications'): 'piecewise continuity applications',
}


def corpus(q):
    parts = [q.get('instruction', ''), q.get('stem', ''), q.get('math_latex', '')]
    for o in q.get('options', []): parts += [o.get('text', ''), o.get('math_latex', '')]
    for p in q.get('parts', []): parts += [p.get('prompt', ''), json.dumps(p.get('blanks', {}), ensure_ascii=False), (p.get('answer') or {}).get('model_answer_and_marking', '')]
    for s in ((q.get('answer') or {}).get('steps') or []) + [s for p in q.get('parts', []) for s in ((p.get('answer') or {}).get('steps') or [])]: parts += [s.get('text', ''), s.get('latex', '')]
    feats = []
    if any(p.get('plot') or p.get('numberline') for p in q.get('parts', [])) or any(o.get('image') for o in q.get('options', [])): feats.append('graph plot number line')
    return ' '.join(map(str, parts + feats))


def main():
    gaps = []
    for c in CLASSES:
        b = json.loads((ROOT / f'public/data/study/{c}.json').read_text()); Q = {q['id']: q for q in b['questions']}
        for lo in b['learning_outcomes']:
            text = ' '.join(corpus(Q[i]) for i in lo['question_ids'] if i in Q)
            words = [w for w in re.findall(r"[a-z][a-z'\-–]+", lo['title'].lower()) if w not in STOP and len(w) > 2]
            for w in dict.fromkeys(words):
                pat = ALIASES.get(w, re.escape(w[:-1] if w.endswith('s') and len(w) > 4 else w))
                if not re.search(pat, text, re.I) and (c, lo['id'], w) not in REVIEWED: gaps.append({'class': c, 'lo': lo['id'], 'title': lo['title'], 'missing': w, 'questions': len(lo['question_ids'])})
    for g in gaps: print(f"{g['class']:5} {g['lo']} {g['title'][:60]:60} missing: {g['missing']}")
    print(len(gaps), 'gaps')
    if '--json' in sys.argv: Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(gaps, indent=1))
    sys.exit(1 if gaps else 0)


if __name__ == '__main__':
    main()
