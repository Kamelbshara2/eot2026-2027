"""Reusable sympy-checked step generators for worked solutions (used by the card batches)."""
import sympy as sp
x = sp.Symbol('x'); u = sp.Symbol('u')
L = lambda e: sp.latex(e)
def _ex(s): return sp.sympify(s.replace('^', '**'))

def polydiv(num, den, var='x', method='long'):
    v = sp.Symbol(var); N = _ex(num).subs(x, v) if var != 'x' else _ex(num); D = _ex(den)
    q, r = sp.div(N, D, v)
    st = [('Write the dividend in descending powers (0 for any missing power).', f'\\left({L(sp.expand(N))}\\right)\\div\\left({L(D)}\\right)')]
    if method == 'synthetic':
        c = sp.solve(D, v)[0]; co = sp.Poly(N, v).all_coeffs(); row = [co[0]]
        for a in co[1:]: row.append(a + row[-1] * c)
        st.append((f'Synthetic division with the zero of the divisor, {var} = {c}: bring down, multiply by {c}, add.', f'{L(c)}\\ \\big|\\ ' + '\\ \\ '.join(map(L, co)) + '\\ \\Rightarrow\\ ' + '\\ \\ '.join(map(L, row))))
    else:
        st.append(('Divide leading terms, multiply back, subtract; repeat with the remainder.', f'\\dfrac{{{L(sp.LT(N, v))}}}{{{L(sp.LT(D, v))}}}={L(sp.LT(N, v) / sp.LT(D, v))}'))
    st.append(('Quotient and remainder.', f'q={L(sp.expand(q))},\\qquad r={L(r)}'))
    st.append(('Check: divisor × quotient + remainder = dividend.', f'\\left({L(D)}\\right)\\left({L(sp.expand(q))}\\right)+{L(r)}={L(sp.expand(D * q + r))}'))
    assert sp.expand(D * q + r - N) == 0
    return st, q, r

def quartic_qf(expr):
    """a x^4 + b x^2 + c = 0 solved with u = x^2."""
    e = sp.expand(_ex(expr)); a, b, c = [e.coeff(x, 4), e.coeff(x, 2), e.subs(x, 0)]
    qu = a * u**2 + b * u + c; us = sp.solve(qu, u); xs = sorted({s for uu in us for s in sp.solve(x**2 - uu, x) if s.is_real}, key=float)
    st = [('The equation is quadratic in x²: substitute u = x².', f'{L(qu)}=0'), ('Factor (or use the quadratic formula).', f'{L(sp.factor(qu))}=0\\ \\Rightarrow\\ u=' + ',\\ '.join(L(v) for v in us)),
          ('Return to x: x² = u, so x = ±√u (only u ≥ 0 gives real x).', ',\\quad '.join(f'x=\\pm{L(sp.sqrt(v))}' for v in us if v >= 0))]
    return st, xs

def cube_eq(expr):
    e = sp.expand(_ex(expr)); a = e.coeff(x, 3); c = e.subs(x, 0); r = sp.real_root(-c / a, 3)
    return [('Isolate x³.', f'x^3={L(-c / a)}'), ('Take the real cube root (a cube root of a negative number is negative).', f'x=\\sqrt[3]{{{L(-c / a)}}}={L(r)}'), ('Check.', f'{L(e.subs(x, r))}=0')], r
