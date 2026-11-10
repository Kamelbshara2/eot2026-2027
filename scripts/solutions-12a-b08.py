import sys, math; sys.path.insert(0,__import__('os').path.dirname(__file__))
import sympy as sp
from solutions_io import save
x,t=sp.symbols('x t')
def der(f,expect,steps,opt,v=x):
    d=sp.diff(sp.sympify(f),v); assert sp.simplify(d-sp.sympify(expect))==0 or abs(float((d-sp.sympify(expect)).subs(v,sp.Rational(3,10))))<1e-9,(f,d,expect); return steps+[(f'Option {opt}.',sp.latex(sp.sympify(expect)))]
def arc(f,a,b,opt,expect):
    F=sp.sympify(f); m=(a+b)/2; P=[(p,F.subs(x,p)) for p in (a,m,b)]
    segs=[sp.sqrt((P[i+1][0]-P[i][0])**2+(P[i+1][1]-P[i][1])**2) for i in range(2)]; Lt=sum(segs); assert abs(float(Lt)-float(sp.sympify(expect)))<6e-5,(f,float(Lt))
    return [('Split [a, b] into two equal parts and join the three points on the curve with straight segments.',f'x={sp.latex(a)},\\ {sp.latex(m)},\\ {sp.latex(b)}'),
            ('Points on the curve.',',\\ '.join(f'\\left({sp.latex(p)},\\,{sp.latex(sp.nsimplify(q))}\\right)' for p,q in P)),
            ('Length of each segment with the distance formula √(Δx² + Δy²).',',\\quad '.join(f'{float(s):.4f}' for s in segs)),
            ('Add the two lengths.',f'L\\approx{float(Lt):.4f}'),(f'Option {opt}.',sp.latex(sp.sympify(expect)) if not isinstance(expect,str) or '.' not in expect else expect)]
IMP=('Implicit differentiation: differentiate both sides with respect to x; every y-term gets a factor y′.','\\dfrac{d}{dx}y^n=ny^{n-1}y\\prime')
save('12A','b08',{
'12A-p02-Q7-1':(1,arc('cos(x)',0,sp.pi/2,'A','1.8950')),
'12A-p02-Q8-1':(1,arc('sin(x)',0,sp.pi,'A','3.7242')),
'12A-p02-Q9-1':(1,arc('sqrt(x+1)',0,3,'D','3.1660')),
'12A-p03-Q10-1':(1,arc('1/x',1,2,'C','1.1280')),
'12A-p03-Q11-1':(1,arc('x**2+1',-2,2,'B','8.9443')),
'12A-p03-Q12-1':(1,arc('x**3+2',-1,1,'C','2*sqrt(2)')),
'12A-p04-Q23-1':(1,[('Find both one-sided limits at x = −1.','x\\to-1'),('Left: 2x + 1.','\\lim_{x\\to-1^-}(2x+1)=-1'),('Right: the constant 3.','\\lim_{x\\to-1^+}3=3'),('−1 ≠ 3, so the two-sided limit does not exist.','\\text{does not exist}'),('Option D.','\\text{DNE}')]),
'12A-Q02-added-01':(1,[('0/0: factor the difference of squares.','\\dfrac{(x-3)(x+3)}{x-3}=x+3'),('Substitute x = 3.','3+3=6'),('Option C.','6')]),
'12A-Q03-added-01':(1,[('Bound sin(1/x).','-1\\le\\sin\\tfrac1x\\le1'),('Multiply by x² ≥ 0.','-x^2\\le x^2\\sin\\tfrac1x\\le x^2'),('Both bounds → 0, so the limit is 0 (Squeeze Theorem).','0'),('Option B.','0')]),
'12A-p12-Q2-1':(1,[('Continuity at 2 means the limit (from either side) equals f(2).','f(2)=\\lim_{x\\to2}f(x)'),('The given one-sided limit therefore equals f(2).','f(2)=5'),('Option C.','5')]),
'12A-p17-Q21b-1':(1,der('sqrt(t**2+8*t)','(2*t+8)/(2*sqrt(t**2+8*t))',[('Velocity = derivative of position (Chain Rule).',"s\\prime(t)=\\dfrac{2t+8}{2\\sqrt{t^2+8t}}"),('At t = 2.',"s\\prime(2)=\\dfrac{12}{2\\sqrt{20}}=\\dfrac{6}{2\\sqrt5}=\\dfrac{3}{\\sqrt5}")],'C',t)),
'12A-p20-Q2-1':(1,'read from the graph',[('A cubic with a local maximum and a local minimum has two turning points, where f′ = 0.','f\\prime=0\\ \\text{twice}'),('The derivative of a cubic is a quadratic; f rises, falls, then rises, so f′ is +, −, +.','+,\\ -,\\ +'),('So f′ is an upward-opening parabola with two distinct x-intercepts: option C.','\\text{option C}')]),
'12A-p28-Q10-1':(1,der('3*t**pi-2*t**(13/10)','3*pi*t**(pi-1)-26*t**(3/10)/10',[('Power Rule works for any real exponent, including π.','\\dfrac{d}{dt}t^{r}=rt^{r-1}'),('Term by term.',"3\\pi t^{\\pi-1}-2(1.3)t^{0.3}=3\\pi t^{\\pi-1}-2.6t^{0.3}")],'A',t)),
'12A-p29-Q12-1':(1,der('(4*x**2-x+3)/sqrt(x)','6*sqrt(x)-1/(2*sqrt(x))-3/(2*x**(3/2))',[('Divide each term by x^(1/2).','f(x)=4x^{3/2}-x^{1/2}+3x^{-1/2}'),('Power Rule.','f\\prime(x)=6x^{1/2}-\\tfrac12x^{-1/2}-\\tfrac32x^{-3/2}')],'C')),
'12A-p35-Q32-1':(1,[('Chain Rule.','h\\prime(2)=f\\prime(g(2))\\cdot g\\prime(2)'),('g(2) = 3.','h\\prime(2)=f\\prime(3)\\cdot g\\prime(2)'),('Substitute.','(-3)(4)=-12'),('Option C.','-12')]),
'12A-p35-Q33-1':(1,[('Even: f(−x) = f(x). Differentiate with the Chain Rule.','-f\\prime(-x)=f\\prime(x)\\Rightarrow f\\prime\\ \\text{odd}'),('Odd: f(−x) = −f(x). Differentiate.','-f\\prime(-x)=-f\\prime(x)\\Rightarrow f\\prime\\ \\text{even}'),('Option D.','\\text{even}\\to\\text{odd},\\ \\text{odd}\\to\\text{even}')]),
'12A-p40-Q9-1':(1,der('sin(3*t)*sec(3*t)','3*sec(3*t)**2',[('Simplify first: sin u · sec u = tan u.','f(t)=\\tan3t'),('Chain Rule.','f\\prime(t)=3\\sec^23t')],'A',t)),
'12A-p40-Q10-1':(1,[('cos u · sec u = 1 wherever defined.','f(t)=\\sqrt{1}=1'),('A constant has derivative 0.','f\\prime(t)=0'),('Option B.','0')]),
'12A-p41-Q13-1':(1,der('2*sin(2*x)*cos(2*x)','4*cos(4*x)',[('Double-angle identity 2 sin u cos u = sin 2u.','f(x)=\\sin4x'),('Chain Rule.','f\\prime(x)=4\\cos4x')],'C')),
'12A-p43-Q17-1':(1,der('sin(cos(sqrt(x**3+2*x**2)))**3','-3*(3*x**2+4*x)*sin(cos(sqrt(x**3+2*x**2)))**2*cos(cos(sqrt(x**3+2*x**2)))*sin(sqrt(x**3+2*x**2))/(2*sqrt(x**3+2*x**2))',[('Chain Rule layer by layer: (·)³ → sin → cos → √ → x³+2x².','3\\sin^2(\\cdot)\\cdot\\cos(\\cdot)\\cdot(-\\sin\\sqrt{\\cdot})\\cdot\\dfrac{3x^2+4x}{2\\sqrt{x^3+2x^2}}')],'B')),
'12A-p43-Q18-1':(1,der('tan(sin(x**3+2*x)**2)**4','8*(3*x**2+2)*tan(sin(x**3+2*x)**2)**3*sec(sin(x**3+2*x)**2)**2*sin(x**3+2*x)*cos(x**3+2*x)',[('Chain Rule layer by layer: (·)⁴ → tan → (·)² → sin → x³+2x.','4\\tan^3(\\cdot)\\sec^2(\\cdot)\\cdot2\\sin(\\cdot)\\cos(\\cdot)\\cdot(3x^2+2)')],'D')),
'12A-Q16-added-01':(1,der('3**(2*x+1)','2*log(3)*3**(2*x+1)',[('(a^u)′ = a^u ln a · u′ with u = 2x + 1.','f\\prime=3^{2x+1}\\ln3\\cdot2')],'C')),
'12A-p47-Q22-1':(1,der('exp(x)/2**x','(E/2)**x*(1-log(2))',[('Write as one power.','\\dfrac{e^x}{2^x}=\\left(\\dfrac e2\\right)^x'),('(aˣ)′ = aˣ ln a, and ln(e/2) = 1 − ln 2.','f\\prime=\\left(\\dfrac e2\\right)^x(1-\\ln2)')],'B')),
'12A-Q18-added-01':(1,[IMP,('Differentiate.','2x+2y\\,y\\prime=0'),('Solve.','y\\prime=-\\dfrac xy'),('Option B.','-\\dfrac xy')]),
'12A-Q18-added-02':(1,[IMP,('Differentiate (product rule on xy).','2x+y+xy\\prime+2yy\\prime=0'),('Collect y′.','y\\prime(x+2y)=-(2x+y)'),('Option C.','y\\prime=-\\dfrac{2x+y}{x+2y}')]),
'12A-Q18-added-03':(1,[IMP,('Product rule.','y+xy\\prime=0'),('Solve.','y\\prime=-\\dfrac yx'),('Option B.','-\\dfrac yx')]),
'12A-Q18-added-04':(1,[IMP,('Differentiate.','3x^2+3y^2y\\prime=0'),('Solve.','y\\prime=-\\dfrac{x^2}{y^2}'),('Option D.','-\\dfrac{x^2}{y^2}')]),
'12A-p49-Q30a-1':(1,der('acos(x**2+x)','-(2*x+1)/sqrt(1-(x**2+x)**2)',[('(cos⁻¹u)′ = −u′/√(1 − u²) with u = x² + x.','f\\prime=-\\dfrac{2x+1}{\\sqrt{1-(x^2+x)^2}}')],'A')),
'12A-p49-Q30b-1':(1,[('(cos⁻¹u)′ = −u′/√(1 − u²) with u = 2/x, u′ = −2/x².','f\\prime=-\\dfrac{-2/x^2}{\\sqrt{1-(2/x)^2}}'),('The two negatives cancel.','f\\prime=\\dfrac{2}{x^2\\sqrt{1-(2/x)^2}}'),('Option D.','\\dfrac{2}{x^2\\sqrt{1-(2/x)^2}}')]),
})
