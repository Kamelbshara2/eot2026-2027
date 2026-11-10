import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
import sympy as sp
from solutions_io import save
x,w=sp.symbols('x w')
INV=('Inverse-function derivative: if g = f⁻¹ and f(a) = b, then g′(b) = 1 / f′(a).','g\\prime(b)=\\dfrac1{f\\prime(a)}')
def inv(f,b,opt,expect):
    F=sp.sympify(f); a=[k for k in range(-6,7) if F.subs(x,k)==b][0]; d=sp.diff(F,x); fa=sp.simplify(d.subs(x,a)); g=1/fa
    assert g==sp.sympify(expect),(f,g)
    return [INV,(f'Find a with f(a) = {b} (try small integers).',f'f({a})={sp.latex(F.subs(x,a))}\\ \\Rightarrow\\ a={a}'),('Differentiate f.',f"f\\prime(x)={sp.latex(d)}"),(f'Evaluate at a = {a}.',f"f\\prime({a})={sp.latex(fa)}"),('Reciprocal.',f"g\\prime({b})={sp.latex(g)}"),(f'Option {opt}.',sp.latex(g))]
CH=('Chain Rule.','\\dfrac{d}{dx}f(u(x))=f\\prime(u(x))\\,u\\prime(x)')
def der(f,var,expect,steps,opt):
    d=sp.diff(sp.sympify(f),var); assert sp.simplify(d-sp.sympify(expect))==0,(f,d); return steps+[(f'Option {opt}.',sp.latex(sp.sympify(expect)))]
save('12A','b05',{
'12A-p34-Q24c-1':(1,[('Quotient Rule for x²/g(x).','h\\prime(x)=\\dfrac{2x\\,g(x)-x^2g\\prime(x)}{g(x)^2}'),('At x = 1 (g(1) = 1, g′(1) = −2).','h(1)=\\dfrac{1}{1}=1,\\quad h\\prime(1)=\\dfrac{2(1)(1)-(1)(-2)}{1^2}=4'),('Tangent line.','y-1=4(x-1)\\Rightarrow y=4x-3'),('Option A).','y=4x-3')]),
'12A-p34-Q31-1':(1,[CH,('h′(1) = f′(g(1))·g′(1) with g(1) = 2.','h\\prime(1)=f\\prime(2)\\cdot g\\prime(1)'),('Substitute f′(2) = 3, g′(1) = −2.','h\\prime(1)=3(-2)=-6'),('Option B).','-6')]),
'12A-p35-Q34-1':(1,[('Symmetry about x = a means f(a + h) = f(a − h).','f(a+h)=f(a-h)'),('Differentiate with respect to h.','f\\prime(a+h)=-f\\prime(a-h)'),('So f′ is symmetric about the point (a, 0) (point symmetry).','(a,\\ 0)'),('Option A).','(a,0)')]),
'12A-p36-Q35a-1':(1,[CH,('Outer f, inner x³ with derivative 3x².','\\dfrac{d}{dx}f(x^3)=f\\prime(x^3)\\cdot3x^2'),('Option A).','3f\\prime(x^3)\\,x^2')]),
'12A-p36-Q35b-1':(1,[CH,('Outer u², inner f(x).','\\dfrac{d}{dx}[f(x)]^2=2f(x)\\,f\\prime(x)'),('Option A).','2f(x)f\\prime(x)')]),
'12A-p36-Q35c-1':(1,[CH,('Outer f, inner f(x).','\\dfrac{d}{dx}f(f(x))=f\\prime(f(x))\\,f\\prime(x)'),('Option B).','f\\prime(f(x))f\\prime(x)')]),
'12A-p37-Q36a-1':(1,[CH,('Inner √x has derivative 1/(2√x).','\\dfrac{d}{dx}f(\\sqrt x)=f\\prime(\\sqrt x)\\cdot\\dfrac1{2\\sqrt x}'),('Option D).','\\dfrac{f\\prime(\\sqrt x)}{2\\sqrt x}')]),
'12A-p37-Q36b-1':(1,[CH,('Outer √u has derivative 1/(2√u); inner f(x).','\\dfrac{d}{dx}\\sqrt{f(x)}=\\dfrac{f\\prime(x)}{2\\sqrt{f(x)}}'),('Option A).','\\dfrac{f\\prime(x)}{2\\sqrt{f(x)}}')]),
'12A-p37-Q36c-1':(1,[CH,('Inner x·f(x) needs the Product Rule.','\\dfrac{d}{dx}[xf(x)]=f(x)+xf\\prime(x)'),('Combine.','\\dfrac{d}{dx}f(xf(x))=f\\prime(xf(x))\\,(f(x)+xf\\prime(x))'),('Option D).','f\\prime(xf(x))(f(x)+xf\\prime(x))')]),
'12A-p38-Q17-1':(1,inv('x**3+4*x-1',-1,'B)','1/4')),
'12A-p38-Q18-1':(1,inv('x**5+4*x-2',-2,'C)','1/4')),
'12A-p39-Q19-1':(1,inv('x**5+3*x**3+x',5,'C)','1/15')),
'12A-p39-Q20-1':(1,inv('x**3+2*x+1',-2,'C)','1/5')),
'12A-p39-Q21-1':(1,inv('sqrt(x**3+2*x+4)',2,'B)','2')),
'12A-p40-Q22-1':(1,inv('sqrt(x**5+4*x**3+3*x+1)',3,'A)','3/10')),
'12A-p41-Q11-1':(1,der('1/sin(4*x)',x,'-4*cos(4*x)/sin(4*x)**2',[('Write as a power.','f(x)=(\\sin4x)^{-1}'),('Chain Rule: power, then sine, then 4x.','f\\prime(x)=-(\\sin4x)^{-2}\\cdot\\cos4x\\cdot4')],'D)')),
'12A-p41-Q12-1':(1,der('w**2*sec(3*w)**2',w,'2*w*sec(3*w)**2+6*w**2*sec(3*w)**2*tan(3*w)',[('Product Rule: (w²)′·sec²3w + w²·(sec²3w)′.','2w\\sec^23w+w^2\\cdot\\dfrac{d}{dw}\\sec^23w'),('Chain Rule: (sec²u)′ = 2 sec u · sec u tan u · u′ with u = 3w.','\\dfrac{d}{dw}\\sec^23w=2\\sec3w\\cdot\\sec3w\\tan3w\\cdot3=6\\sec^23w\\tan3w')],'A)')),
'12A-p42-Q14-1':(1,[('Factor out 4 and use sin²θ + cos²θ = 1.','f(x)=4(\\sin^23x+\\cos^23x)=4'),('The derivative of a constant is 0.','f\\prime(x)=0'),('Option B).','0')]),
'12A-p42-Q15-1':(1,der('tan(sqrt(x**2+1))',x,'sec(sqrt(x**2+1))**2*x/sqrt(x**2+1)',[CH,('Outer tan u → sec²u; inner √(x²+1) → x/√(x²+1).','f\\prime(x)=\\sec^2\\!\\left(\\sqrt{x^2+1}\\right)\\cdot\\dfrac{2x}{2\\sqrt{x^2+1}}')],'C)')),
})
