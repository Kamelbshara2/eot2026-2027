import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
import sympy as sp
from solutions_io import save
x=sp.Symbol('x')
def der(f,expect,steps,opt):
    d=sp.diff(sp.sympify(f),x); assert sp.simplify(d-sp.sympify(expect))==0,(f,d,expect); return steps+[(f'Option {opt}.',sp.latex(sp.sympify(expect)))]
ROLLE=("Rolle's Theorem: if f is continuous on [a, b], differentiable on (a, b) and f(a) = f(b), then f′(c) = 0 for some c in (a, b).","f(a)=f(b)\\ \\Rightarrow\\ f\\prime(c)=0")
def rolle(f,a,b,opt,ans):
    F=sp.sympify(f); fa,fb=F.subs(x,a),F.subs(x,b); assert sp.simplify(fa-fb)==0
    cs=[c for c in sp.solve(sp.diff(F,x),x) if c.is_real and sp.N(a)<sp.N(c)<sp.N(b)]
    return [ROLLE,('Check the endpoint values (a polynomial/sine is continuous and differentiable everywhere).',f'f({sp.latex(a)})={sp.latex(fa)},\\quad f({sp.latex(b)})={sp.latex(sp.simplify(fb))}'),
            ('Solve f′(c) = 0.',f"f\\prime(x)={sp.latex(sp.diff(F,x))}=0"),('Keep only c strictly inside the interval.','c='+',\\ '.join(sp.latex(c) for c in sorted(cs,key=float))+(f'\\approx {", ".join(f"{float(c):.5f}" for c in sorted(cs,key=float))}' if any(not c.is_Rational for c in cs) else '')),(f'Option {opt}.',ans)]
save('12A','b07',{
'12A-p48-Q29b-1':(1,der('asin(sqrt(x))','1/(2*sqrt(x)*sqrt(1-x))',[('(sin⁻¹u)′ = u′/√(1 − u²) with u = √x, u′ = 1/(2√x).','f\\prime=\\dfrac{1}{\\sqrt{1-x}}\\cdot\\dfrac{1}{2\\sqrt x}=\\dfrac{1}{2\\sqrt{x(1-x)}}')],'A)')),
'12A-p49-Q31a-1':(1,der('atan(sqrt(x))','1/(2*sqrt(x)*(1+x))',[('(tan⁻¹u)′ = u′/(1 + u²) with u = √x.','f\\prime=\\dfrac{1}{1+x}\\cdot\\dfrac{1}{2\\sqrt x}')],'A)')),
'12A-p50-Q31b-1':(1,der('atan(1/x)','-1/(x**2+1)',[('(tan⁻¹u)′ = u′/(1 + u²) with u = 1/x, u′ = −1/x².','f\\prime=\\dfrac{-1/x^2}{1+1/x^2}'),('Multiply top and bottom by x².','f\\prime=\\dfrac{-1}{x^2+1}')],'A)')),
'12A-p50-Q32a-1':(1,der('sqrt(2+atan(x))','1/(2*(1+x**2)*sqrt(2+atan(x)))',[('Chain Rule: (√u)′ = u′/(2√u) with u = 2 + tan⁻¹x, u′ = 1/(1 + x²).','f\\prime=\\dfrac{1}{2\\sqrt{2+\\tan^{-1}x}}\\cdot\\dfrac{1}{1+x^2}')],'A)')),
'12A-p50-Q32b-1':(1,der('exp(atan(x))','exp(atan(x))/(1+x**2)',[('Chain Rule: (e^u)′ = e^u·u′ with u = tan⁻¹x.','f\\prime=e^{\\tan^{-1}x}\\cdot\\dfrac1{1+x^2}')],'A)')),
'12A-p51-Ex1-1':(1,rolle('x**3-3*x**2+2*x+2',0,1,'D)','c\\approx0.42265')),
'12A-p51-Ex1-2':(1,[ROLLE,('Test f(a) = f(b) for each option.','A:\\ 1\\ne5,\\quad B:\\ 0\\ne2,\\quad C:\\ 0\\ne1'),('D: sin(−π) = 0 = sin 0, and sin x is continuous and differentiable everywhere.','\\sin(-\\pi)=\\sin0=0'),('Option D).','f(x)=\\sin x\\ \\text{on}\\ [-\\pi,0]')]),
'12A-p51-Ex1-3':(1,rolle('x**4-2*x**2',-sp.sqrt(2),sp.sqrt(2),'C)','c=-1,\\ 0,\\ 1')),
'12A-p52-Q1-1':(1,rolle('x**4-2*x**2',-2,2,'b)','c=-1,\\ 1,\\ 0')),
'12A-p52-Q2-1':(1,rolle('x**2-4*x+3',1,3,'c)','c=2')),
'12A-p52-Q3-1':(1,rolle('sin(x)',0,sp.pi,'b)','c=\\dfrac{\\pi}{2}')),
'12A-p53-Q4-1':(1,[ROLLE,('Compare f(0) and f(2) for each function.','a)\\ 0=0,\\ b)\\ 1\\ne5,\\ c)\\ 0\\ne e^2-1,\\ d)\\ 0\\ne2'),('Only x² − 2x has equal endpoint values (and it is a polynomial: continuous and differentiable).','f(0)=f(2)=0'),('Option a).','f(x)=x^2-2x')]),
'12A-p53-Q5-1':(1,rolle('x**2-x+1',0,1,'b)','[0,1],\\ c=\\tfrac12')),
})
