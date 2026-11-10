"""Full hand-method solution for rational functions f = N/D (zeros, domain, holes, asymptotes incl. oblique by long division, intercept, graph)."""
import sympy as S
x = S.Symbol('x')
L = lambda e: S.latex(e)
P = lambda e: S.sstr(e)   # plain text inside sentences

def steps(N, D):
    N, D = S.expand(N), S.expand(D)
    g = S.gcd(N, D); n2, d2 = S.cancel(N / g), S.cancel(D / g)
    nf, df = S.factor(N), S.factor(D)
    excl = sorted([r for r in S.solve(D, x) if r.is_real], key=float)
    holes = [r for r in excl if S.simplify(g.subs(x, r)) == 0]
    va = [r for r in excl if r not in holes]
    zeros = sorted([z for z in S.solve(n2, x) if z.is_real], key=float)
    q, r = S.div(S.Poly(N, x), S.Poly(D, x)); q = q.as_expr(); r = r.as_expr()
    degN, degD = S.degree(N, x), S.degree(D, x)
    a = {'domain': [], 'zeros': [], 'asym': [], 'graph': []}
    a['domain'].append(('Factor the numerator and the denominator completely.', f'f(x)=\\dfrac{{{L(nf)}}}{{{L(df)}}}'))
    a['domain'].append(('The denominator cannot be zero: solve D(x) = 0 to find the excluded values.', f'{L(df)}=0\\ \\Rightarrow\\ x=' + ',\\ '.join(L(v) for v in excl)))
    a['domain'].append(('Domain.', '\\{x\\in\\mathbb{R}\\mid ' + ',\\ '.join(f'x\\ne {L(v)}' for v in excl) + '\\}'))
    if holes:
        for h in holes:
            a['domain'].append((f'The factor ({P(x - h)}) cancels, so x = {P(h)} is a hole, not an asymptote. Its y-value comes from the simplified function.', f'f(x)=\\dfrac{{{L(S.factor(n2))}}}{{{L(S.factor(d2))}}},\\quad x\\ne{L(h)};\\qquad y=\\dfrac{{{L(n2.subs(x, h))}}}{{{L(d2.subs(x, h))}}}={L(S.nsimplify(n2.subs(x, h) / d2.subs(x, h)))}'))
    else:
        a['domain'].append(('No factor is common to the numerator and denominator, so there is no hole.', '\\text{no hole}'))
    if zeros:
        a['zeros'].append(('Zeros: set the (simplified) numerator equal to 0. A value is a zero only if it is in the domain.', f'{L(S.factor(n2))}=0\\ \\Rightarrow\\ x=' + ',\\ '.join(L(z) for z in zeros)))
        mult = S.roots(S.Poly(n2, x))
        for z in zeros:
            if mult.get(z, 1) % 2 == 0: a['zeros'].append((f'x = {P(z)} comes from a squared factor (even multiplicity): the graph touches the x-axis there without crossing.', f'({L(x - z)})^{{{mult[z]}}}'))
    else:
        disc = S.discriminant(S.Poly(n2, x)) if S.degree(n2, x) == 2 else None
        a['zeros'].append(('Zeros: set the numerator equal to 0.', f'{L(n2)}=0'))
        if disc is not None: a['zeros'].append(('The discriminant is negative, so the numerator has no real roots: f has no real zeros (no x-intercepts).', f'b^2-4ac={L(disc)}<0'))
        else: a['zeros'].append(('This equation has no real solution, so f has no real zeros.', '\\text{no real zeros}'))
    y0 = None if D.subs(x, 0) == 0 else S.nsimplify(N.subs(x, 0) / D.subs(x, 0))
    if y0 is not None: a['zeros'].append(('y-intercept: substitute x = 0.', f'f(0)=\\dfrac{{{L(N.subs(x, 0))}}}{{{L(D.subs(x, 0))}}}={L(y0)}'))
    for v in va: a['asym'].append((f'x = {P(v)} makes the denominator zero but not the numerator: vertical asymptote.', f'x={L(v)}'))
    if degN == degD + 1:
        a['asym'].append(('The degree of the numerator is one more than the degree of the denominator, so there is an oblique (slant) asymptote and no horizontal asymptote. Use long division.', f'\\deg N={degN},\\quad \\deg D={degD}'))
        a['asym'].append(('Divide the leading terms, multiply back, subtract; repeat.', f'\\dfrac{{{L(S.LT(N, x))}}}{{{L(S.LT(D, x))}}}={L(S.LT(N, x) / S.LT(D, x))}'))
        a['asym'].append(('Result of the division (quotient + remainder/divisor).', f'\\dfrac{{{L(N)}}}{{{L(D)}}}={L(q)}' + (f'-\\dfrac{{{L(-r)}}}{{{L(D)}}}' if S.sympify(r).could_extract_minus_sign() else f'+\\dfrac{{{L(r)}}}{{{L(D)}}}')))
        a['asym'].append(('Check: divisor × quotient + remainder gives back the numerator.', f'\\left({L(D)}\\right)\\left({L(q)}\\right)' + (f'-{L(-r)}' if S.sympify(r).could_extract_minus_sign() else f'+{L(r)}') + f'={L(S.expand(D * q + r))}'))
        a['asym'].append(('As x → ±∞ the remainder fraction → 0, so the graph approaches the quotient line.', f'\\text{{Oblique asymptote: }}y={L(q)}'))
    elif degN < degD:
        a['asym'].append(('The degree of the numerator is less than the degree of the denominator: horizontal asymptote y = 0.', 'y=0'))
    elif degN == degD:
        a['asym'].append(('Equal degrees: horizontal asymptote y = ratio of leading coefficients.', f'y={L(S.LT(N, x) / S.LT(D, x))}'))
    a['graph'].append(('Draw the asymptotes as dashed lines, mark the intercepts' + (' and the hole (open circle)' if holes else '') + '.', '\\text{dashed asymptotes}'))
    for v in va:
        lv, rv = S.limit(N / D, x, v, '-'), S.limit(N / D, x, v, '+')
        a['graph'].append((f'Behaviour next to x = {P(v)}: test values on each side.', f'x\\to {L(v)}^-:\\ f(x)\\to{L(lv)},\\qquad x\\to {L(v)}^+:\\ f(x)\\to{L(rv)}'))
    a['graph'].append(('Plot a few points (TABLE on the calculator helps) on both sides of each vertical asymptote and join them, following the asymptotes.', '\\text{one branch on each side of each vertical asymptote}'))
    return a, {'excl': excl, 'holes': holes, 'va': va, 'zeros': zeros, 'q': q, 'y0': y0}
