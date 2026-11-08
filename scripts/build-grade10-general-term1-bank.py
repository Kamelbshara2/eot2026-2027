"""Curated textbook-only selection. Rebuild: python scripts/build-grade10-general-term1-bank.py /path/to/10عام.pdf
Requires PyMuPDF and SymPy. Question data are transcribed from the specified printed pages;
only MCQ choices and model answers are added. Do not substitute generated numeric variants.
"""
from pathlib import Path
import json, hashlib, sys, re
import fitz
import sympy as S
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'public/data/exam-banks/10g3-term1'
OUT.mkdir(parents=True,exist_ok=True);(OUT/'assets').mkdir(exist_ok=True)
BOOK=Path(sys.argv[1])
PDF=fitz.open(BOOK)
assert len(PDF)==170, 'Expected the uploaded 170-page book (printed pages 569–738)'
SHA=hashlib.sha256(BOOK.read_bytes()).hexdigest()
assets={};questions=[];outcomes=[];checks=[]
letters='ABCD'
def latex(v):return S.latex(v) if isinstance(v,S.Basic) else str(v)
def source(page,ex,mcq=True):return dict(printed_page=page,pdf_page=page-568,exercise=str(ex),adaptation='mcq' if mcq else 'transcription',book_sha256=SHA)
def lo(n,title,ar,statement,rule,refs):
 o=dict(id=f'LO{n:02}',exam_slot=f'Q{n}',title=title,title_ar=ar,statement=statement,rule_summary=rule,question_type='mcq' if n<=20 else 'frq',textbook_references=[dict(printed_page=p,exercises_or_section=e) for p,e in refs],question_ids=[],question_count=0,download=f'LO{n:02}.json');outcomes.append(o);return n

def mc(n,page,ex,instruction,expr,correct,wrong,explanation,diagrams=(),verified=None,wide=False):
 # Expressions are evaluated symbolically before emission; numerical/string choices must be distinct.
 vals=[correct,*wrong];texts=[latex(v) for v in vals];assert len(vals)==4 and len(set(texts))==4,(n,ex,texts)
 if all(isinstance(v,S.Basic) for v in vals):
  assert all(S.simplify(vals[i]-vals[j])!=0 for i in range(4) for j in range(i)),(n,ex,texts)
 k=sum(q['learning_outcome_id']==f'LO{n:02}' for q in questions)+1
 shift=(n+k)%4;order=list(range(4));order=order[shift:]+order[:shift]
 opts=[dict(id=letters[i],text=texts[j],**({'math_latex':texts[j]} if not isinstance(vals[j],str) or not texts[j].startswith('TEXT:') else {})) for i,j in enumerate(order)]
 for o in opts:
  if o['text'].startswith('TEXT:'):o['text']=o['text'][5:]
 key=letters[order.index(0)]
 q=dict(id=f'G10G-Q{n:02}-MCQ-{k:02}',learning_outcome_id=f'LO{n:02}',type='mcq',display_number=f'{n}.{k}',instruction=instruction,stem=instruction+(' '+expr if expr else ''),math_latex=expr,marks=None,options=opts,answer=dict(correct_option_id=key,correct_option_text=opts[order.index(0)]['text'],explanation=explanation),diagram_asset_ids=list(diagrams),source=source(page,ex),wide=wide)
 questions.append(q)
 if verified is not None:assert verified, (n,page,ex)
 return q

def part(id,prompt,answer,marks=5,math='',solution_math='',height=25):return dict(id=id,prompt=prompt,math_latex=math,marks=marks,workspace=dict(height_mm=height),answer=dict(model_answer_and_marking=answer,math_latex=solution_math))
def fr(n,page,ex,instruction,expr,parts,diagrams=(),graph=False):
 k=sum(q['learning_outcome_id']==f'LO{n:02}' for q in questions)+1
 assert sum(p['marks'] for p in parts)==10
 q=dict(id=f'G10G-Q{n:02}-FRQ-{k:02}',learning_outcome_id=f'LO{n:02}',type='frq',display_number=f'{n}.{k}',instruction=instruction,stem=instruction+(' '+expr if expr else ''),math_latex=expr,marks=10,parts=parts,diagram_asset_ids=list(diagrams),source=source(page,ex,False),graph_workspace=graph)
 questions.append(q);return q

def crop(id,page,box,alt):
 # box is normalized to the original A4 PDF. Clip the original, without redrawing its graph.
 p=PDF[page-569];r=fitz.Rect(box[0]*p.rect.width,box[1]*p.rect.height,box[2]*p.rect.width,box[3]*p.rect.height)
 pix=p.get_pixmap(matrix=fitz.Matrix(3,3),clip=r);pix.save(OUT/f'assets/{id}.png')
 assets[id]=dict(src=f'assets/{id}.png',width=pix.width,height=pix.height,alt_text=alt,source=source(page,id,False),crop_box=list(box))
 return id

def nums(c):return [S.sympify(c+1),S.sympify(-c),S.sympify(c+2)]
x,y,a,b,c,d,g,k,m,n,p,q,r,t,u,v,w,z,h,f=S.symbols('x y a b c d g k m n p q r t u v w z h f',nonzero=True)
# Q1–Q7: literal textbook exercises, including the higher-order items specified for Q5.
lo(1,'FOIL binomial products','ضرب ثنائيي الحد','Multiply binomials by using the FOIL method.','Multiply all four pairs, then combine the two middle terms.',[(649,'1–6')])
for i,e in enumerate([(3*c-5)*(c+3),(g+10)*(2*g-5),(6*a+5)*(5*a+3),(4*x+1)*(6*x+3),(5*y-4)*(3*y-1),(6*d-5)*(4*d-7)],1):
 ans=S.expand(e);sym=next(iter(e.free_symbols));mc(1,649,i,'Find the product.',S.latex(e),ans,[ans+sym,ans-sym,ans+1],f'Use FOIL and combine like terms: {ans}.')
lo(2,'Squares of sums and differences','مربع مجموع وفرق','Find squares of sums and differences.','(a ± b)² = a² ± 2ab + b². Do not omit the middle term.',[(653,'Learn'),(655,'Learn'),(657,'1–6')])
for i,(base,form) in enumerate([(a+10,'(a+10)(a+10)'),(b-6,'(b-6)(b-6)'),(n+7,'(n+7)^2'),(x+6,'(x+6)^2'),(8-m,'(8-m)^2'),(9-2*y,'(9-2y)^2')],1):
 ans=S.expand(base**2);sym=next(iter(base.free_symbols));mc(2,657,i,'Find the product.',form,ans,[ans+sym,ans-sym,ans+1],f'Expand both factors, including 2ab: {ans}.')
lo(3,'Sum and difference products','حاصل ضرب مجموع وفرق','Find the product of a sum and a difference.','(a+b)(a−b)=a²−b²; the middle terms cancel.',[(658,'15–20')])
for i,(left,right) in enumerate([(u,3),(b,7),(2,x),(4,x),(2*q,5*r),(3*a**2,7*b)],15):
 ans=left**2-right**2;mc(3,658,i,'Find the product.',f'({latex(left)}+{latex(right)})({latex(left)}-{latex(right)})',S.expand(ans),[S.expand(left**2+right**2),S.expand(ans+left*right),S.expand(-ans)],f'Square the first term and subtract the square of the second: {S.expand(ans)}.')
lo(4,'Factor using distribution','التحليل بخاصية التوزيع','Factor polynomials by using the Distributive Property.','Take the greatest common factor from every term; check by multiplication.',[(665,'1–6')])
for i,e in enumerate([16*t-40*y,30*v+50*x,2*k**2+4*k,5*z**2+10*z,4*a**2*b**2+2*a**2*b-10*a*b**2,5*c**2*v-15*c**2*v**2+5*c**2*v**3],1):
 ans=S.factor(e);mc(4,665,i,'Factor completely over the integers.',latex(e),ans,[S.Mul(S.Rational(1,2),ans,evaluate=False),S.Mul(2,ans,evaluate=False),-ans],f'Take out the GCF: {ans}. Expanding restores the original polynomial.')
lo(5,'Analyse monic trinomial factors','تحليل ثلاثيات الحدود ومعاملاتها','Factor trinomials of the form x² + bx + c.','For (x+r)(x+s), r+s=b and rs=c. Enumerate integer factor pairs.',[(674,'73–78')])
mc(5,674,73,'Which expression does not belong because it cannot be factored using integers?','',x**2+12*x+24,[x**2+2*x-24,x**2+11*x+24,x**2-10*x-24],'For 24, no integer factor pair sums to 12. The other three factor into integer binomials.')
mc(5,674,74,'Jamaall: (x+2)(x−8). Charles: (x−2)(x+8). Who correctly factored x²+6x−16?','', 'TEXT:Charles only',['TEXT:Jamaall only','TEXT:Both students','TEXT:Neither student'],'Charles: (x−2)(x+8)=x²+6x−16. Jamaall gets a middle term of −6x.')
for ex,expr,ans,bad,why in [(75,'x^2+kx-19',r'k\in\{-18,18\}',[r'k\in\{-20,20\}',r'k\in\{-19,19\}',r'k=18'], 'The integer factors of −19 are (1,−19) and (−1,19); the sums are −18 and 18.'),(76,'x^2+kx+14',r'k\in\{-15,-9,9,15\}',[r'k\in\{9,15\}',r'k\in\{-14,14\}',r'k\in\{-8,8\}'],'Integer pairs with product 14 give sums ±15 and ±9.'),(77,r'x^2-8x+k,\quad k>0',r'k\in\{7,12,15,16\}',[r'k\in\{7,12,15\}',r'k\in\{8,16\}',r'k\in\{1,2,3,4\}'],'Pairs of negative integers with sum −8 have products 7, 12, 15 and 16.'),(78,r'x^2-5x+k,\quad k>0',r'k\in\{4,6\}',[r'k\in\{4,5,6\}',r'k\in\{1,5\}',r'k=6'],'The negative integer pairs (−1,−4) and (−2,−3) give products 4 and 6.')]:mc(5,674,ex,'Find all values of k for which the polynomial factors using integers.',expr,ans,bad,why)
lo(6,'Factor non-monic trinomials','تحليل ثلاثيات الحدود غير الأحادية','Factor trinomials of the form ax² + bx + c.','Find two numbers with product ac and sum b; split the middle term and group.',[(672,'21–26')])
for ex,e in enumerate([5*x**2+34*x+24,2*x**2+19*x+24,4*x**2+22*x+10,4*x**2+38*x+70,2*x**2-3*x-9,4*x**2-13*x+10],21):
 ans=S.factor(e);mc(6,672,ex,'Factor completely over the integers.',latex(e),ans,[(x+4)*(5*x+6),(x+3)*(2*x+8),2*(x+1)*(2*x+5),2*(x+5)*(2*x+7),(x+3)*(2*x-3),(x-5)*(4*x-2)][ex-21:ex-20]+[-ans,ans*2],f'Split the middle term and factor by grouping: {ans}.')
lo(7,'Difference of squares','تحليل الفرق بين مربعين','Factor binomials that are the difference of squares.','A²−B²=(A−B)(A+B). Factor repeatedly when possible.',[(679,'1–6')])
for ex,e in enumerate([q**2-121,r**4-k**4,w**4-625,r**2-9*t**2,h**4-256,2*x**3-x**2-162*x+81],1):
 ans=S.factor(e);mc(7,679,ex,'Factor completely over the integers.',latex(e),ans,[S.Mul(2,ans,evaluate=False),S.Mul(S.Rational(1,2),ans,evaluate=False),S.factor(-e)],f'Use difference of squares, with grouping when needed: {ans}.')
# Exponents: domain statements are retained from the original exercise instructions.
lo(8,'Divide monomials','قسمة وحيدات الحد','Divide monomials using the properties of exponents.','Subtract exponents when dividing; multiply every exponent when raising a quotient to a power.',[(581,'Learn'),(583,'5–9')])
for ex,expr,ans in [(3,r'\frac{c^4d^4f^3}{c^2d^4f^3}',c**2),(5,r'(\frac{p^2t^7}{10})^3',p**6*t**21/1000),(6,r'\frac{a^7b^8c^8}{a^5bc^7}',a**2*b**7*c),(7,r'(\frac{3np^3}{7q^2})^2',9*n**2*p**6/(49*q**4)),(8,r'(\frac{2r^3t^6}{5u^9})^4',16*r**12*t**24/(625*u**36)),(9,r'(\frac{3m^5r^3}{4p^8})^4',81*m**20*r**12/(256*p**32))]:
 mc(8,583,ex,'Simplify. Assume no denominator equals zero.',expr,ans,[ans*2,ans/2,ans+1],f'Apply quotient and power rules. Simplified result: {ans}.')
lo(9,'Negative and zero exponents','الأسس السالبة والصفرية','Simplify expressions containing negative and zero exponents.','For a≠0, a⁰=1 and a⁻ⁿ=1/aⁿ. Move only factors with negative exponents.',[(587,'Learn'),(591,'11–14')])
for ex,expr,ans in [(11,r'\frac{3m^{-3}t^4p^2}{12t^4}',p**2/(4*m**3)),(12,r'(\frac{3t^6u^2v^5}{9tuv^{21}})^0',S.Integer(1)),(13,r'\frac{x^{-4}y^9}{z^{-2}}',y**9*z**2/x**4),(14,r'(-\frac{5f^9g^4h^2}{fg^2h^3})^0',S.Integer(1)),(15,r'\frac{p^4r^{-3}}{r^{-2}}',p**4/r),(16,r'-\frac{5c^2d^6}{8cd^5r^0}',-5*c*d/8)]:
 mc(9,591,ex,'Simplify using positive exponents. Assume no denominator equals zero and each zero-power base is nonzero.',expr,ans,[S.Integer(0),-ans,ans*2],f'Use zero and negative exponent rules: {ans}.')
lo(10,'Rational exponents','الأسس النسبية والجذور','Evaluate and rewrite expressions involving rational exponents.','a^(1/n) is the principal nth root of a. Evaluate the root before any other power.',[(599,'9–16')])
for ex,expr,ans in [(9,r'(\frac1{16})^{1/4}',S.Rational(1,2)),(10,r'\sqrt[5]{3125}',S.Integer(5)),(11,r'729^{1/3}',S.Integer(9)),(12,r'(\frac1{32})^{1/5}',S.Rational(1,2)),(13,r'\sqrt[6]{4096}',S.Integer(4)),(15,r'(\frac{16}{625})^{1/4}',S.Rational(2,5))]:
 mc(10,599,ex,'Evaluate.',expr,ans,[ans*2,ans/2,-ans],f'Raise {ans} to the indicated denominator of the exponent to check the radicand.')
lo(11,'Products of square roots','ضرب الجذور التربيعية','Simplify radical expressions by using the Product Property of Square Roots.','√a·√b=√(ab) for a,b≥0. Extract perfect-square factors; area uses the full formula.',[(609,'67–70')])
tri=crop('radical_triangle',609,(.705,.270,.963,.361),'Original triangle from Reveal p. 609 exercise 67; base 6√2 m and height 3√6 m.')
rect=crop('radical_rectangle',609,(.740,.360,.970,.445),'Original rectangle from Reveal p. 609 exercise 68; length 8√12 cm and width 4√8 cm.')
mc(11,609,67,'The base of a triangle is 6√2 m and its height is 3√6 m. What is its area?','',18*S.sqrt(3),[36*S.sqrt(3),18*S.sqrt(2),9*S.sqrt(3)],'A=½bh=½(6√2)(3√6)=9√12=18√3 m².',[tri])
mc(11,609,68,'A rectangle is 8√12 cm long and 4√8 cm wide. What is its area?','',128*S.sqrt(6),[64*S.sqrt(6),32*S.sqrt(6),128*S.sqrt(3)],'A=lw=32√96=128√6 cm².',[rect])
mc(11,609,69,'Use √(h·k) to find the geometric mean of 32 and 14 in simplified radical form.','',8*S.sqrt(7),[4*S.sqrt(7),16*S.sqrt(7),8*S.sqrt(14)],'√(32·14)=√448=8√7.')
mc(11,609,70,'Fernanda has paint to cover 5 square yards of a cubic prop. Use s=√(A/6). What is the longest side length, to the nearest tenth of a yard?','',S.Rational(9,10),[S.Rational(8,10),S.Rational(12,10),S.Rational(5,10)],'s=√(5/6)≈0.9128709, so the requested rounded answer is 0.9 yard.')
for ex,expr,ans in [(7,r'\sqrt5\cdot\sqrt{10}',5*S.sqrt(2)),(8,r'\sqrt{10}\cdot\sqrt{20}',10*S.sqrt(2))]:mc(11,607,ex,'Simplify.',expr,ans,[ans*2,ans/2,ans+1],f'Multiply under one radical, then extract the perfect square: {ans}.')
lo(12,'Quotients of radicals','قسمة الجذور وتبسيطها','Simplify radical expressions by using the Quotient Property of Square Roots.','√(a/b)=√a/√b for a≥0,b>0. Simplify and rationalise the denominator. For cube roots, extract cubes.',[(607,'15–18'),(608,'55–56 (cube-root extension)')])
for ex,expr,ans in [(15,r'\sqrt{\frac{192}{216}}',2*S.sqrt(2)/3),(16,r'\sqrt{\frac{88}{18}}',2*S.sqrt(11)/3),(17,r'\sqrt{\frac{84}{121}}',2*S.sqrt(21)/11),(18,r'\sqrt{\frac{75}{20}}',S.sqrt(15)/2)]:mc(12,607,ex,'Simplify.',expr,ans,[ans*2,ans/2,ans+1],f'Reduce the fraction, simplify the radical and rationalise: {ans}.')
# The coverage cites 55–56 on p.608, which are cube roots. Retain that actual root index.
mc(12,608,55,'Simplify. The denominator is nonzero.',r'\sqrt[3]{\frac{192x^7}{1029x^{10}}}',r'\frac{4}{7x}',[r'\frac{4x}{7}',r'\frac{4}{7x^3}',r'\frac{8}{7x}'],'192/1029=64/343 and x⁷/x¹⁰=1/x³, so the real cube root is 4/(7x).')
mc(12,608,56,'Simplify. The denominator is nonzero.',r'\sqrt[3]{\frac{640a^3b^8}{5ab^4}}',r'4b\sqrt[3]{2a^2b}',[r'4ab\sqrt[3]{2b}',r'8b\sqrt[3]{a^2b}',r'4b^2\sqrt[3]{2a}'],'The radicand is 128a²b⁴=64b³·2a²b. Extract the real cube root of 64b³.')
lo(13,'Add and subtract radicals','جمع الجذور وطرحها','Add and subtract radical expressions.','Simplify the radicals first; combine coefficients only when their radicands match.',[(615,'1–8')])
for ex,expr,ans in [(1,r'7\sqrt7-2\sqrt7',5*S.sqrt(7)),(2,r'3\sqrt8+7\sqrt8',20*S.sqrt(2)),(3,r'7\sqrt5+4\sqrt5',11*S.sqrt(5)),(4,r'2\sqrt6+9\sqrt6',11*S.sqrt(6)),(7,r'3\sqrt5-2\sqrt{20}',-S.sqrt(5)),(8,r'3\sqrt{50}-3\sqrt{32}',3*S.sqrt(2))]:mc(13,615,ex,'Simplify.',expr,ans,[ans*2,-ans,ans+1],f'Combine like radicals after simplifying: {ans}.')
# Q14 contains contextual factoring; use the actual numbered textbook tasks.
lo(14,'Factoring in context','تطبيق التحليل في مسائل تربيعية','Solve quadratic equations by factoring.','Set a physical model equal to the required height/volume, factor, then reject roots outside its domain.',[(722,'29–30'),(721,'15–18 (supplementary same-LO exercises)')])
mc(14,722,29,'A ballast bag is dropped from 576 ft. Its height is f(t)=−16t²+576. After how many seconds does it hit the ground?','',S.Integer(6),[S.Integer(-6),S.Integer(18),S.Integer(36)],'Set f(t)=0: −16(t−6)(t+6)=0. Time cannot be negative, so t=6 s.')
mc(14,722,'30(a)','Factor the volume expression for Catalina’s open-topped box.',r'V=3x^2-36x+108',r'3(x-6)^2',[r'3(x+6)^2',r'(3x-6)^2',r'3(x-12)^2'],'Factor out 3: 3(x²−12x+36)=3(x−6)².')
# Additional equations are literal items from the adjacent factoring exercise set.
for ex,expr,ans,bad in [(15,'x^2+9x+18=0',r'x=-6,-3',[r'x=6,3',r'x=-9,-2',r'x=0,-9']),(16,'4x^2+28x+49=0',r'x=-\frac72',[r'x=\frac72',r'x=-7',r'x=-\frac74']),(17,'-9x^2=30x+25',r'x=-\frac53',[r'x=\frac53',r'x=-\frac35',r'x=-5']),(18,'-x^2-12=-8x',r'x=2,6',[r'x=-2,-6',r'x=3,4',r'x=-3,-4'])]:mc(14,721,ex,'Solve by factoring. Check the solutions.',expr,ans,bad,'Write the equation as a product equal to zero and set each factor equal to zero.')
lo(15,'Square root and completing-square methods','الجذر التربيعي وإكمال المربع','Solve quadratic equations using the Square Root Property and by completing the square.','Isolate (x−h)²; take both square roots. Complete the square by adding (b/2)².',[(730,'37–39'),(725,'Learn'),(729,'10–12 (supplementary same-LO equations)')])
mc(15,730,37,'Which expression does not belong because it is not a perfect square trinomial?','',r'n^2+n+\frac34',[r'n^2-n+\frac14',r'n^2-\frac23n+\frac19',r'n^2+\frac13n+\frac1{36}'],'The first, third and fourth forms equal (n−½)², (n−⅓)² and (n+⅙)². For n²+n+c, c must be ¼, not ¾.')
mc(15,730,38,'Create a quadratic equation for which the only solution is 4. Choose a valid equation.','',r'(x-4)^2=0',[r'x^2-16=0',r'(x+4)^2=0',r'x^2-4=0'],'(x−4)²=0 has the repeated root x=4; x²−16=0 also has −4.')
mc(15,730,39,'For x²−5x−7=0, which comparison of completing the square, graphing and factoring is correct?','', 'TEXT:Completing the square gives exact irrational roots; graphing estimates them; integer factoring does not work.', ['TEXT:Integer factoring gives roots 7 and −1.','TEXT:Graphing always gives exact irrational roots.','TEXT:Completing the square gives only one root.'],'The discriminant is 53, not a perfect square. Completing the square gives (5±√53)/2; graphing estimates the two intercepts.',wide=True)
for ex,expr,ans,bad in [(10,'x^2+6x-16=0',r'x=2,-8',[r'x=-2,8',r'x=4,-4',r'x=-3\pm4']),(11,'x^2-2x-14=0',r'x=1\pm\sqrt{15}',[r'x=-1\pm\sqrt{15}',r'x=1\pm\sqrt{14}',r'x=2\pm\sqrt{15}']),(12,'x^2-8x-1=8',r'x=9,-1',[r'x=-9,1',r'x=4\pm\sqrt{17}',r'x=8,-1'])]:mc(15,729,ex,'Solve by completing the square.',expr,ans,bad,'Move the constant term; add (half the x-coefficient)² to both sides; take both square roots.')
lo(16,'Translations of quadratics','إزاحة الدوال التربيعية','Write a quadratic in vertex form and transform its graph.','In y=a(x−h)²+k, the vertex is (h,k). x−h shifts right; x+h shifts left.',[(699,'Learn'),(707,'3–10')])
for ex,expr,ans,bad,why in [(3,'g(x)=(x-1)^2','TEXT:Right 1 unit',['TEXT:Left 1 unit','TEXT:Up 1 unit','TEXT:Down 1 unit'],'Replacing x by x−1 shifts the parent graph right by 1.'),(4,'g(x)=x^2-8','TEXT:Down 8 units',['TEXT:Up 8 units','TEXT:Right 8 units','TEXT:Left 8 units'],'Subtracting 8 outside the square shifts down 8.'),(5,'g(x)=(x+3)^2','TEXT:Left 3 units',['TEXT:Right 3 units','TEXT:Up 3 units','TEXT:Down 3 units'],'x+3 means h=−3, so the shift is left 3.'),(6,'g(x)=x^2+7','TEXT:Up 7 units',['TEXT:Down 7 units','TEXT:Right 7 units','TEXT:Left 7 units'],'Adding 7 outside the square shifts up 7.'),(8,'g(x)=(x+5)^2-2','TEXT:Left 5 units and down 2 units',['TEXT:Right 5 units and down 2 units','TEXT:Left 5 units and up 2 units','TEXT:Right 5 units and up 2 units'],'The vertex is (−5,−2).'),(10,'g(x)=-4+(x-3)^2','TEXT:Right 3 units and down 4 units',['TEXT:Left 3 units and down 4 units','TEXT:Right 3 units and up 4 units','TEXT:Left 3 units and up 4 units'],'The vertex is (3,−4).')]:mc(16,707,ex,'Describe the translation from the parent function y=x².',expr,ans,bad,why)
lo(17,'Factoring quadratic equations','حل المعادلات التربيعية بالتحليل','Solve quadratic equations by factoring.','Write one side as zero, factor fully, and apply the zero-product property. Check every root.',[(721,'5–10')])
for ex,expr,ans,bad,why in [(5,'3b(9b-27)=0',r'b=0,3',[r'b=3',r'b=0,-3',r'b=-3,3'],'Either 3b=0 or 9b−27=0, so b=0 or 3.'),(6,'(7x+3)(2x-6)=0',r'x=-\frac37,3',[r'x=\frac37,-3',r'x=-3,3',r'x=-\frac73,3'],'Set 7x+3=0 and 2x−6=0 separately.'),(7,'b^2=-3b',r'b=0,-3',[r'b=-3',r'b=0,3',r'b=-3,3'],'b²+3b=b(b+3)=0. Do not divide by b and lose zero.'),(8,'a^2=4a',r'a=0,4',[r'a=4',r'a=0,-4',r'a=-4,4'],'a(a−4)=0, so a=0 or 4.'),(9,'x^2-6x=27',r'x=-3,9',[r'x=3,-9',r'x=3,9',r'x=-3,-9'],'x²−6x−27=(x−9)(x+3).'),(10,'a^2+11a=-18',r'a=-2,-9',[r'a=2,9',r'a=-3,-6',r'a=2,-9'],'a²+11a+18=(a+2)(a+9).')]:mc(17,721,ex,'Solve by factoring. Check the solutions.',expr,ans,bad,why)
lo(18,'Dilations and reflections of quadratics','تمدد وانعكاس الدوال التربيعية','Write quadratics in vertex form and transform their graphs.','A negative outside coefficient reflects across the x-axis; |a|>1 stretches vertically. Simplify an inside coefficient before comparing.',[(703,'Learn'),(704,'Learn'),(707,'23–26'),(708,'27–30')])
for page,ex,expr,ans,bad,why in [(707,23,r'g(x)=-\frac13x^2','TEXT:Reflect across the x-axis; vertically compress by 1/3',['TEXT:Reflect across the y-axis; stretch by 4','TEXT:Shift down 4 units','TEXT:Reflect across the x-axis; stretch by 4'],'The coefficient of x² is −⅓.'),(707,24,r'g(x)=(-\frac23x)^2','TEXT:Vertical compression by 4/9; no reflection',['TEXT:Reflect across the x-axis; stretch by 9','TEXT:Vertical stretch by 3','TEXT:Shift left 3 units'],'(−⅔x)²=(4/9)x²; squaring removes the sign. Equivalent horizontal stretch: 3/2.'),(707,25,'g(x)=-2x^2','TEXT:Reflect across the x-axis; stretch vertically by 2',['TEXT:Reflect across the y-axis only','TEXT:Compress vertically by 1/2','TEXT:Shift down 2 units'],'The outside coefficient is −2.'),(708,27,'h(x)=-7-x^2','TEXT:Reflect across the x-axis, then shift down 7',['TEXT:Reflect across the y-axis, then shift up 7','TEXT:Stretch by 7, then shift down 1','TEXT:Reflect across the x-axis, then shift up 7'],'The coefficient is −1 and the vertical shift is −7.'),(708,28,r'g(x)=2(x-3)^2+8','TEXT:Stretch vertically by 2, shift right 3 and up 8',['TEXT:Stretch vertically by 3/2, then shift up 8','TEXT:Compress vertically by 2/3, then shift down 8','TEXT:Reflect across the x-axis, then shift up 8'],'a=2, h=3 and k=8 in vertex form.'),(708,30,r'g(x)=-5-\frac43x^2','TEXT:Reflect across the x-axis, stretch by 4/3, then shift down 5',['TEXT:Reflect and stretch by 4, then shift down 5','TEXT:Compress by 1/4, then shift up 5','TEXT:Shift left 5 and down 1/4'],'The coefficient is −4/3 and the vertical shift is −5.')]:mc(18,page,ex,'Describe the graph relative to the parent y=x².',expr,ans,bad,why,wide=True)
lo(19,'Solve quadratics by graphing','حل المعادلات التربيعية بيانيًا','Solve quadratic equations by graphing.','Real solutions are the x-intercepts of the related graph; a tangent gives a repeated root; no intersection means no real solution.',[(711,'Learn'),(713,'1–6')])
for ex,expr,ans,bad,why in [(1,'x^2+7x+14=0','TEXT:No real solution',['TEXT:x = −7, −2','TEXT:x = −2, 7','TEXT:x = −3.5'],'The upward parabola has minimum 7/4>0, so it has no x-intercept.'),(2,'x^2+2x-24=0',r'x=-6,4',[r'x=6,-4',r'x=-4,6',r'x=-12,2'],'The graph crosses the x-axis at −6 and 4.'),(3,'x^2+16x+64=0',r'x=-8',[r'x=8',r'x=-8,8',r'x=-16,4'],'The graph of (x+8)² touches the x-axis at −8.'),(4,'x^2-5x+12=0','TEXT:No real solution',['TEXT:x = −3, −4','TEXT:x = 3, 4','TEXT:x = 2.5'],'The vertex is (2.5,5.75), above the x-axis.'),(5,'x^2+14x=-49',r'x=-7',[r'x=7',r'x=-7,7',r'x=-14'],'The related graph is (x+7)², tangent to the x-axis at −7.'),(6,'x^2=2x-1',r'x=1',[r'x=-1',r'x=-1,1',r'x=2'],'Bring all terms left: (x−1)²=0. The graph touches the x-axis at 1.')]:mc(19,713,ex,'Solve the equation by graphing the related quadratic function.',expr,ans,bad,why)
lo(20,'Complete the square','إكمال المربع','Solve quadratic equations by completing the square.','First make the coefficient of x² equal to 1. Add (b/2)² to form a perfect square.',[(729,'1–6')])
for ex,bv in enumerate([26,-24,-19,11,5,-8],1):
 ans=S.Rational(bv,2)**2;mc(20,729,ex,'Find c so that the trinomial is a perfect square.',f'x^2{bv:+}x+c',ans,[S.Integer(abs(bv)),ans*4,ans/4],f'c=(b/2)²=({bv}/2)²={ans}.')
# Written-response topics: four actual textbook questions per idea, with all requested parts.
lo(21,'Add and subtract polynomials','جمع كثيرات الحدود وطرحها','Add and subtract polynomials.','Distribute a subtraction sign to every term; then collect like terms.',[(636,'27–34')])
for ex,e,expr in [(27,(3*c**3-c+11)-(c**2+2*c+8),'(3c^3-c+11)-(c^2+2c+8)'),(28,(z**2+z)+(z**2-11),'(z^2+z)+(z^2-11)'),(29,(2*x-2*y+1)-(3*y+4*x),'(2x-2y+1)-(3y+4x)'),(30,(4*a-5*b**2+3)+(6-2*a+3*b**2),'(4a-5b^2+3)+(6-2a+3b^2)')]:
 ans=S.expand(e);fr(21,636,ex,'Find the sum or difference.',expr,[part('a','Show your simplification.',f'Correct sign distribution and like-term collection (6 marks); simplified polynomial {ans} (4 marks).',10,solution_math=latex(ans),height=45)])
lo(22,'Multiply polynomials','ضرب كثيرات الحدود','Multiply polynomials by using the Distributive Property.','Multiply each term in the first polynomial by every term in the second; collect equal powers.',[(650,'18–23')])
for ex,e,expr in [(18,(2*y-11)*(y**2-3*y+2),'(2y-11)(y^2-3y+2)'),(19,(4*a+7)*(9*a**2+2*a-7),'(4a+7)(9a^2+2a-7)'),(20,(m**2-5*m+4)*(m**2+7*m-3),'(m^2-5m+4)(m^2+7m-3)'),(21,(x**2+5*x-1)*(5*x**2-6*x+1),'(x^2+5x-1)(5x^2-6x+1)')]:
 ans=S.expand(e);fr(22,650,ex,'Find the product.',expr,[part('a','Show all partial products and combine like terms.',f'All partial products (6 marks); correct collection of like terms (4 marks): {ans}.',10,solution_math=latex(ans),height=50)])
lo(23,'Multiplication properties of exponents','خواص ضرب القوى','Multiply monomials and simplify expressions using multiplication properties of exponents.','Add exponents in a product; multiply exponents in a power. Apply the power to the coefficient too.',[(576,'25–30'),(578,'56–58')])
fr(23,576,25,'A square field has side length 5x³y⁵. What is its area in terms of x and y?','',[part('a','Show the area calculation.', 'A=s²=(5x³y⁵)²=25x⁶y¹⁰. Square the coefficient (3), multiply each exponent by 2 (5), final expression (2).',10,solution_math='A=25x^6y^{10}',height=40)])
cube=crop('shipping_cube',576,(.423,.149,.550,.252),'Original cube-shaped shipping box, Reveal p. 576 exercise 27; side length 4m⁸n⁴.')
fr(23,576,27,'A cube-shaped shipping box has side length 4m⁸n⁴. What is its volume in terms of m and n?','',[part('a','Show the volume calculation.','V=s³=(4m⁸n⁴)³=64m²⁴n¹². Cube the coefficient (3), multiply each exponent by 3 (5), final expression (2).',10,solution_math='V=64m^{24}n^{12}',height=40)],[cube])
fr(23,578,56,'Consider the two expressions.',r'(m^p)(m^q)\quad\text{and}\quad(m^p)^q',[part('a','What must be true about p and q for the expressions to be equal? Give an example.','For positive m≠1, require p+q=pq, or (p−1)(q−1)=1 (3). Example p=q=2 (2). Without that assumption, m=1 makes both expressions equal for all defined p,q; other bases require domain care.',5,solution_math=r'p+q=pq\quad (m>0,\ m\ne1)',height=25),part('b','Assuming m, p and q are positive integers, can (mᵖ)(mᑫ) > (mᵖ)ᑫ ever be true? Explain.','Yes. Take m=2 and p=q=1: 2·2=4>2¹=2 (3). For m>1 compare exponents p+q and pq (2).',5,solution_math=r'2^1\cdot2^1=4>2^{1\cdot1}=2',height=25)])
fr(23,578,57,'For nonzero real a and b and integers m and t, simplify and explain.',r'(-\frac{a^m}{b^t})^{2t}',[part('a','Apply the power rules and explain the sign.','Since 2t is even, (−1)²ᵗ=1 (3). Multiply the numerator exponents to get 2mt (3), and denominator exponents to get 2t² (3); final quotient (1). Nonzero a,b make all integer powers defined.',10,solution_math=r'\frac{a^{2mt}}{b^{2t^2}}',height=45)])
fr(23,578,58,'Consider y=x, y=x² and y=x³.','',[part('a','For each equation, write the related expression and record the power of x.','x=x¹ (power 1), x·x=x² (power 2), x·x·x=x³ (power 3). One mark per row.',3,height=20),part('b','Graph each equation using a graphing calculator.','Correct line, upward parabola and increasing cubic through the origin. One mark per graph.',3,height=25),part('c','Classify each graph as linear or nonlinear.','y=x is linear; y=x² and y=x³ are nonlinear. One mark for all three correct.',1,height=15),part('d','Explain how to determine whether an equation, or its related expression, is linear or nonlinear without graphing.','After simplification, y=ax+b is linear (2); higher powers of x such as x² and x³ are nonlinear (1).',3,height=20)],graph=True)
lo(24,'Quadratic extrema and graph features','القيم العظمى والصغرى وخصائص المنحنى','Find and interpret maximum and minimum values of a quadratic function.','The vertex (h,k) gives the minimum k when the graph opens up and maximum k when it opens down; the axis is x=h.',[(695,'1–4')])
# These are exact clips of the book's graphs. All features are retained in the prompt.
for ex,box,axis,vertex,yint,end in [(1,(.18,.14,.355,.263),'x=0','(0,1)','(0,1)','y→−∞ as x→±∞; maximum 1'),(2,(.542,.14,.715,.263),'x=1','(1,1)','(0,4)','y→+∞ as x→±∞; minimum 1'),(3,(.18,.302,.355,.425),'x=0','(0,−4)','(0,−4)','y→+∞ as x→±∞; minimum −4'),(4,(.542,.302,.715,.425),'x=−3','(−3,−6)','(0,3)','y→+∞ as x→±∞; minimum −6')]:
 aid=crop(f'extrema_{ex}',695,box,f'Original quadratic graph, Reveal p. 695 exercise {ex}; one unit per grid square.')
 fr(24,695,ex,'Identify the axis of symmetry, vertex and y-intercept of the graph. Then describe the end behavior.','',[part('a','Axis of symmetry and vertex.',f'Axis {axis} (2); vertex {vertex} (3).',5,height=25),part('b','y-intercept and end behavior.',f'y-intercept {yint} (2); {end} (3). The extremum is the vertex y-coordinate.',5,height=25)],[aid])
lo(25,'Write a quadratic from its graph','كتابة الدالة التربيعية من الرسم','Write quadratic equations using Standard Form.','Read the zeros r,s, write y=a(x−r)(x−s), then use another point to find a. Expand to y=ax²+bx+c.',[(722,'31–34')])
for ex,box,formula,why in [(31,(.092,.545,.265,.667),'y=x^2-x-6','Zeros −2 and 3 give y=a(x+2)(x−3). The y-intercept −6 gives a=1.'),(32,(.455,.545,.628,.667),'y=2x^2-12x+16','Zeros 2 and 4 give y=a(x−2)(x−4). The vertex (3,−2) gives a=2.'),(33,(.092,.702,.265,.826),'y=4x^2-32x+60','Zeros 3 and 5 give y=a(x−3)(x−5). The vertex (4,−4) gives a=4.'),(34,(.455,.702,.628,.826),r'y=-\frac12x^2+2x+6','Zeros −2 and 6 give y=a(x+2)(x−6). The vertex (2,8) gives a=−½.')]:
 aid=crop(f'quadratic_graph_{ex}',722,box,f'Original quadratic graph, Reveal p. 722 exercise {ex}.')
 fr(25,722,ex,'Write a quadratic function for the given graph. Give the equation in standard form.','',[part('a','Show how you find the equation.',why+' Correct reading of two graph features (4), coefficient a (3), expanded standard form (3).',10,solution_math=formula,height=60)],[aid])
# Human-readable explanations use mathematical typography, not SymPy/Python operators.
superdigits=str.maketrans('0123456789-','⁰¹²³⁴⁵⁶⁷⁸⁹⁻')
def readable(text):return re.sub(r'\*\*(-?\d+)',lambda m:m.group(1).translate(superdigits),text).replace('*','·')
for item in questions:
 if item['type']=='mcq':item['answer']['explanation']=readable(item['answer']['explanation'])
 else:
  for itempart in item['parts']:itempart['answer']['model_answer_and_marking']=readable(itempart['answer']['model_answer_and_marking'])
# Finalise per-LO downloadable banks and machine-readable selection/provenance.
for o in outcomes:
 group=[q for q in questions if q['learning_outcome_id']==o['id']];o['question_ids']=[q['id'] for q in group];o['question_count']=len(group)
 assert len(group)==(6 if o['question_type']=='mcq' else 5 if o['id']=='LO23' else 4),(o['id'],len(group))
 selected={5:[1,2,4,5],8:[1,2,3,5],10:[0,1,4,5],13:[0,1,4,5],14:[0,1,2,5],15:[0,1,2,4],16:[0,1,4,5],18:[0,1,3,4],19:[0,1,2,5]}.get(int(o['exam_slot'][1:]),list(range(5 if o['id']=='LO23' else 4)))
 o['booklet_question_ids']=[group[i]['id'] for i in selected]
assert len(questions)==141
provenance=dict(book=dict(upload_name=BOOK.name,sha256=SHA,pdf_pages=170,printed_pages='569–738',printed_to_pdf_offset=-568),coverage=dict(file='grade10-general-coverage.pdf',question_slots=25,official_minutes=150,official_marks=100),policy='Only exercises from the uploaded textbook are used. Numerical data and required mathematical tasks are retained; MCQ options and explanatory solutions are added. Supplementary same-outcome book exercises are explicitly identified in LO references. Practice marks and 60-minute timing are not official exam settings.',selection_basis='Prioritise explicitly cited exercises, misconception checks, and complementary representations. No prediction or probability claim about the actual government final exam.',learning_outcomes=outcomes,questions=questions)
notice='Questions selected only from the uploaded Reveal textbook. MCQ options and model solutions are added for practice. FRQ rubrics use 10 practice marks, not official slot weights. The 60-minute mock is a practice format, not the official 150-minute final exam.'
bank=dict(id='10g3-term1',classroom='10G3',title='Term 1 textbook question bank',title_ar='بنك أسئلة الفصل الأول من الكتاب',term=1,academic_year='2026–2027',source_sha256=SHA,source_file='provenance.json',question_count=141,mcq_count=120,frq_count=21,learning_outcomes=outcomes,assets=assets,questions=questions,authored_notice=notice,authored_notice_ar='الأسئلة من كتاب Reveal المرفق فقط، مع إضافة خيارات ونماذج إجابة للتدريب. درجات المقالية تدريبية ولا تمثل أوزان الاختبار الرسمي. الاختبار التجريبي مدته ساعة؛ مدة الاختبار الرسمي في الهيكل 150 دقيقة.',study_booklet='worksheets/grade-10-general-term1-study-booklet.pdf',review_notes={})
for name,data in [('index.json',bank),('bank.json',bank),('provenance.json',provenance)]: (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
for o in outcomes:
 group=[q for q in questions if q['learning_outcome_id']==o['id']];used={i for q in group for i in q['diagram_asset_ids']}
 (OUT/o['download']).write_text(json.dumps(dict(bank_metadata=dict(id='10g3-term1-'+o['id'],classroom='10G3',learning_outcome_id=o['id'],question_count=len(group)),learning_outcomes=[o],questions=group,assets={i:assets[i] for i in used}),ensure_ascii=False,indent=2)+'\n')
(ROOT/'content-imports/grade10-general-term1-selection.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print(f'10G3: {len(questions)} textbook questions, {len(outcomes)} LOs, {len(assets)} original clipped diagrams; book SHA256 {SHA}')
