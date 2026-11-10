import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
import sympy as sp
from solutions_io import save
x,t,y=sp.symbols('x t y')
def der(f,var,expect,steps,opt):
    d=sp.diff(sp.sympify(f),var); assert sp.simplify(d-sp.sympify(expect))==0,(f,d,expect); return steps+[(f'Option {opt}.',sp.latex(sp.sympify(expect)))]
def horiz(f,roots,opt,fac):
    F=sp.sympify(f); d=sp.factor(sp.diff(F,x)); r=sorted(sp.solve(sp.diff(F,x),x)); assert r==sorted(sp.sympify(roots)),(f,r)
    return [('A horizontal tangent has slope 0: solve f′(x) = 0.',"f\\prime(x)=0"),('Product Rule with (e^{kx})′ = k e^{kx}.',f"f\\prime(x)={sp.latex(d)}"),('e^{kx} is never 0, so set the other factor to 0.',fac),(f'Option {opt}.','x='+',\\ '.join(sp.latex(v) for v in r))]
save('12A','b06',{
'12A-p42-Q16-1':(1,der('4*x**2*sin(x)*sec(3*x)',x,'8*x*sin(x)*sec(3*x)+4*x**2*(cos(x)*sec(3*x)+sin(x)*sec(3*x)*tan(3*x)*3)',[('Product Rule for 4x² · (sin x sec 3x).','f\\prime=8x\\sin x\\sec3x+4x^2\\left(\\sin x\\sec3x\\right)\\prime'),('Product and Chain Rules: (sec 3x)′ = 3 sec 3x tan 3x.','\\left(\\sin x\\sec3x\\right)\\prime=\\cos x\\sec3x+\\sin x\\sec3x\\tan3x\\,(3)')],'D)')),
'12A-p43-Q29-1':(1,horiz('x*exp(-2*x)',['1/2'],'A)','1-2x=0')),
'12A-p44-Q29-1':(1,horiz('x*exp(-3*x)',['1/3'],'A)','1-3x=0')),
'12A-p44-Q30-1':(1,horiz('x**2*exp(-2*x)',[0,1],'A)','2x-2x^2=2x(1-x)=0')),
'12A-p44-Q30-2':(1,horiz('x**2*exp(-3*x)',[0,'2/3'],'A)','2x-3x^2=x(2-3x)=0')),
'12A-p45-Q20-1':(1,der('sqrt(log(x))/x',x,'(1-2*log(x))/(2*x**2*sqrt(log(x)))',[('Quotient Rule with (√(ln x))′ = 1/(2x√(ln x)).','f\\prime=\\dfrac{\\frac{1}{2x\\sqrt{\\ln x}}\\cdot x-\\sqrt{\\ln x}}{x^2}'),('Multiply top and bottom by 2√(ln x).','f\\prime=\\dfrac{1-2\\ln x}{2x^2\\sqrt{\\ln x}}')],'A)')),
'12A-p45-Q20-2':(1,der('log(sqrt(t))/t',t,'(1-log(t))/(2*t**2)',[('Simplify first: ln √t = ½ ln t.','g(t)=\\dfrac{\\ln t}{2t}'),('Quotient Rule.','g\\prime(t)=\\dfrac12\\cdot\\dfrac{\\frac1t\\cdot t-\\ln t}{t^2}=\\dfrac{1-\\ln t}{2t^2}')],'A)')),
'12A-p46-Q21-1':(1,der('exp(x)*log(x)',x,'exp(x)*(log(x)+1/x)',[('Product Rule.','h\\prime=e^x\\ln x+e^x\\cdot\\dfrac1x')],'A)')),
'12A-p46-Q21-2':(1,[('e and ln are inverse functions: e^{ln x} = x for x > 0.','f(x)=x'),('Derivative.','f\\prime(x)=1'),('Option A).','1')]),
'12A-p46-Q22-1':(1,der('2**exp(x)',x,'2**exp(x)*exp(x)*log(2)',[('(a^u)′ = a^u · ln a · u′ with u = eˣ.','h\\prime=2^{e^x}\\ln2\\cdot e^x')],'A)')),
'12A-p47-Ex8.2-1':(1,[('Differentiate both sides with respect to x (product rule on x²y²; y′ for every y).','2xy^2+2x^2y\\,y\\prime-2=-4y\\prime'),('Collect the y′ terms.','y\\prime(2x^2y+4)=2-2xy^2'),('Solve.','y\\prime=\\dfrac{1-xy^2}{x^2y+2}'),('Slope at (2, −2).','y\\prime=\\dfrac{1-2(4)}{4(-2)+2}=\\dfrac{-7}{-6}=\\dfrac76'),('Tangent line.','y+2=\\tfrac76(x-2)\\Rightarrow y=\\tfrac76x-\\tfrac{13}{3}'),('Option B).','y\\prime=\\dfrac{1-xy^2}{x^2y+2},\\ y=\\tfrac76x-\\tfrac{13}3')]),
'12A-p48-Q29a-1':(1,der('asin(x**3+1)',x,'3*x**2/sqrt(1-(x**3+1)**2)',[('(sin⁻¹u)′ = u′/√(1 − u²) with u = x³ + 1, u′ = 3x².','f\\prime=\\dfrac{3x^2}{\\sqrt{1-(x^3+1)^2}}')],'A)')),
})
