"""Apply the reusable exam-writing policy to the three textbook banks.
Requires sympy, antlr4-python3-runtime==4.11.1. Originals remain in textbook-v1-inputs.
"""
from pathlib import Path
import json,re,copy,hashlib,math,sys
import sympy as S
from sympy.parsing.latex import parse_latex
ROOT=Path(__file__).resolve().parent.parent
x,a,b=S.symbols('x a b')
REPORT=[]
def clean(s):
 # Source math is already valid. In particular, preserve \\ row separators.
 return s
def fixmath(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=='math_latex' and isinstance(v,str):obj[k]=clean(v)
   else:fixmath(v)
 elif isinstance(obj,list):
  for v in obj:fixmath(v)
def parse(s):
 if not s or any(k in s for k in ['begin','text','quad',',','=','circ','infty','lfloor']):return None
 try:
  e=parse_latex(clean(s).replace(chr(92)+'left','').replace(chr(92)+'right',''),strict=True)
  return e.replace(lambda v:v.is_Function and len(v.func.__name__)==1,lambda v:S.Symbol(v.func.__name__)*v.args[0])
 except Exception:return None
def fmt(e):return S.latex(e)
def validnew(v,seen):return all(S.simplify(v-w)!=0 for w in seen)
def replace_choices(q,values,reasons):
 correct=q['answer']['correct_option_id'];ids=[o['id'] for o in q['options']];wrongids=[i for i in ids if i!=correct]
 for o in q['options']:
  j=0 if o['id']==correct else wrongids.index(o['id'])+1
  o.update(text=fmt(values[j]),math_latex=fmt(values[j]),misconception=None if j==0 else reasons[j-1])
 q['answer']['correct_option_text']=next(o['text'] for o in q['options'] if o['id']==correct)
def algebra_choices(q):
 ans=parse(next(o.get('math_latex','') for o in q['options'] if o['id']==q['answer']['correct_option_id']))
 if ans is None or not ans.free_symbols:return False
 expr=parse(q.get('math_latex',''));terms=S.Add.make_args(S.sympify(S.sstr(S.expand(ans)),evaluate=True));candidates=[]
 factoring='factor' in q['instruction'].lower()
 if factoring:
  for fac in S.Mul.make_args(ans):
   if fac.is_Add:
    for t in fac.args:
     changed=ans.xreplace({fac:fac-2*t});candidates.append((changed,'Reverse a sign inside a factor.'))
  coeff,rest=ans.as_coeff_Mul()
  if coeff not in [1,-1]:candidates.append((rest,'Omit the greatest common numerical factor.'))
 else:
  for t in terms:
   candidates.extend([(S.expand(ans-t),'Omit a term when distributing or combining like terms.'),(S.expand(ans-2*t),'Reverse the sign of a term.')])
 candidates.append((-ans,'Reverse every sign instead of applying the operation to the required term.'))
 vals=[ans];reasons=[]
 for v,why in candidates:
  if validnew(v,vals):vals.append(v);reasons.append(why)
  if len(vals)==4:break
 if len(vals)==4:replace_choices(q,vals,reasons);return True
 return False

def extra(bank,lo,prompt,latex,answer,wrongs,explanation,skill,origin='concept_application',calc=None):
 o=bank['learning_outcomes'][lo-1];i=sum(q.get('source_kind') in ['concept_application','example_variant'] and q['learning_outcome_id']==o['id'] for q in bank['questions'])+1
 qid=f'{bank["classroom"]}-REV-{o["id"]}-{i:02}'
 values=[answer,*wrongs];assert len(set(values))==4
 shift=int(hashlib.sha256(qid.encode()).hexdigest()[:4],16)%4;order=list(range(4));order=order[shift:]+order[:shift]
 opts=[dict(id='ABCD'[j],text=values[k][5:] if values[k].startswith('TEXT:') else values[k],**({} if values[k].startswith('TEXT:') else dict(math_latex=values[k])),misconception=None if k==0 else 'Apply the stated rule incorrectly; compare the relevant sign, operation or condition.') for j,k in enumerate(order)]
 parent=next(q for q in bank['questions'] if q['learning_outcome_id']==o['id']);q=dict(id=qid,learning_outcome_id=o['id'],type='mcq',display_number=f'{lo}.{o["question_count"]+i}',instruction=prompt,stem=prompt+' '+latex,math_latex=latex,marks=None,options=opts,answer=dict(correct_option_id=opts[order.index(0)]['id'],correct_option_text=opts[order.index(0)]['text'],explanation=explanation),source={**parent['source'],'adaptation':origin,'exercise':f'Application of {parent["source"]["exercise"]}'},source_kind=origin,parent_question_id=parent['id'],diagram_asset_ids=[],skill_tags=[skill],difficulty='standard',calculator_expressions=calc or [])
 bank['questions'].append(q);return q

def addvariants(bk):
 c=bk['classroom'];T=lambda s:'TEXT:'+s
 if c=='9G3':
  for i,(expr,ans,bad) in enumerate([('6(99)','594',['600','599','606']),('8(102)','816',['802','808','800']),('7(49)','343',['350','349','357']),('4(198)','792',['798','800','808'])]):extra(bk,7,'Which value is obtained by using the Distributive Property?',expr,ans,bad,'Rewrite the second factor around 100 or 200, then multiply both terms.','mental-distribution','example_variant',[expr])
  for pts,answer,wrongs,why,calc in [
   (r'(0,1),\ (2,7),\ (4,13)','3',['-3',r'\frac13','6'],'Each increase of 2 in x gives 6 in y, so rate=3.',['6/2']),
   (r'(0,9),\ (2,5),\ (4,1)','-2',['2',r'-\frac12','-4'],'Each increase of 2 in x gives −4 in y, so rate=−2.',['(-4)/2']),
   (r'(-2,5),\ (0,5),\ (2,5)','0',['5','1',T('Undefined')],'The y-values do not change, so the rate is zero.',['0/2']),
   (r'(0,1),\ (1,2),\ (2,5)',T('No constant rate.'),['1','3','2'],'Successive rates 1 and 3 differ: these points do not describe a linear function.',['(2-1)/(1-0)','(5-2)/(2-1)'])]:extra(bk,8,'Which statement describes the rate of change in the listed data?',pts,answer,wrongs,why,'rate-from-data','example_variant',calc)
  for pts,answer,wrongs,why,calc in [
   (r'(1,2),\ (3,6)','2',['-2',r'\frac12','4'],'m=(6−2)/(3−1)=2.',['(6-2)/(3-1)']),
   (r'(1,5),\ (3,-1)','-3',['3',r'-\frac13','-6'],'m=(−1−5)/(3−1)=−3.',['(-1-5)/(3-1)']),
   (r'(-2,4),\ (3,4)','0',['4','1',T('Undefined')],'A horizontal line has slope zero.',['(4-4)/(3+2)']),
   (r'(2,-1),\ (2,5)',T('Undefined'),['0','6',r'\frac16'],'A vertical line gives a zero denominator; its slope is undefined.',[])]:extra(bk,15,'What is the slope of the line through the two points?',pts,answer,wrongs,why,'slope-formula','example_variant',calc)
  for lo,items in {
   11:[('For g(x)=3x relative to f(x)=x, which statement is correct?','Vertical stretch by 3.',['Vertical compression by 3.','Translation up 3.','Translation right 3.']),('For g(x)=0.4x relative to f(x)=x, which statement is correct?','Vertical compression by 0.4.',['Vertical stretch by 0.4.','Reflection only.','Translation down 0.4.'])],
   14:[('For f(x)=floor(x), which point belongs to the graph?','(−1.2, −2)',['(−1.2, −1)','(1.2, 2)','(0, 1)']),('For f(x)=floor(x), how are endpoints drawn on the step y=2?','Closed at x=2; open at x=3.',['Open at x=2; closed at x=3.','Closed at both endpoints.','Open at both endpoints.'])],
   18:[('Which equation has a horizontal graph through (0,−3)?','y=−3',['x=−3','y=−3x','y=x−3']),('What is the slope of y=8?','0',['8','1','Undefined'])]}.items():
   for p,ans,wrong in items:extra(bk,lo,p,'',T(ans),[T(w) for w in wrong],bk['learning_outcomes'][lo-1]['rule_summary'],'concept-interpretation')
  for prompt,ans,wrong,why in [('What are the next three terms?',r'-21,-24,-27',[r'-20,-22,-24',r'-15,-12,-9',r'-19,-20,-21'],'Subtract 3 repeatedly.'),('Which formula gives the nth term?',r'a_n=-3n-6',[r'a_n=-3n-9',r'a_n=3n-12',r'a_n=-6n-3'],'Use a₁+(n−1)d=−9−3(n−1).'),('What is the 11th term?','-39',['-42','-36','39'],'a₁₁=−9+10(−3)=−39.'),('Which term has value −60?','18',['17','20','21'],'Solve −3n−6=−60: n=18.')]:extra(bk,17,prompt,r'-9,-12,-15,-18,\ldots',ans,wrong,why,{'What are the next three terms?':'next-terms','Which formula gives the nth term?':'nth-term-formula','What is the 11th term?':'term-value','Which term has value −60?':'term-order'}[prompt], 'example_variant')
 elif c=='10G3':
  for lo,prompt,expr,ans,wrong,why in [
   (2,'Which identity correctly expands the square of a sum?',r'(a+b)^2',r'a^2+2ab+b^2',[r'a^2+b^2',r'a^2-2ab+b^2',r'2a+2b'],'Include both cross-products ab.'),
   (2,'Which missing term makes this identity true?',r'(x-5)^2=x^2+\square+25','-10x',['10x','-5x','-25'],'The middle term is 2·x·(−5).'),
   (8,'Which expression is equivalent when b≠0?',r'\left(\frac ab\right)^3',r'\frac{a^3}{b^3}',[r'\frac{a^3}{b}',r'\frac a{b^3}',r'\frac{3a}{3b}'],'Apply the power to numerator and denominator.'),
   (8,'Which simplified expression is correct for x≠0?',r'\frac{x^7}{x^3}','x^4',['x^{10}','x^{21}','x^{7/3}'],'Subtract exponents for equal nonzero bases.'),
   (9,'Which statement holds for every nonzero real number a?',r'a^0','1',['0','a','-1'],'The zero-exponent rule requires a≠0.'),
   (9,'Which expression uses positive exponents only? Assume x≠0.',r'x^{-4}',r'\frac1{x^4}',['-x^4','x^4',r'-\frac1{x^4}'],'A negative exponent means a reciprocal, not a negative value.'),
   (15,'Which operation isolates the square before taking square roots?',r'3(x-2)^2=27',T('Divide both sides by 3.'),[T('Subtract 3 from both sides.'),T('Take only the positive root.'),T('Subtract 2 from 27.')],'First obtain (x−2)²=9.'),
   (15,'Which pair is the complete solution set?',r'(x-2)^2=9',r'\{-1,5\}',[r'\{5\}',r'\{-5,1\}',r'\{-3,3\}'],'x−2=±3, so x=−1 or 5.'),
   (16,'What is the vertex of the translated parabola?',r'y=(x-3)^2+2','(3,2)',['(-3,2)','(3,-2)','(-3,-2)'],'For y=(x−h)²+k, the vertex is (h,k).'),
   (16,'Which translation takes y=x² to the given graph?',r'y=(x+4)^2-1',T('4 left and 1 down.'),[T('4 right and 1 down.'),T('4 left and 1 up.'),T('1 left and 4 down.')],'x+4 means h=−4; k=−1.'),
   (18,'Which description is correct relative to y=x²?',r'y=-2x^2',T('Reflection in the x-axis and vertical stretch by 2.'),[T('Reflection in the y-axis only.'),T('Vertical compression by 2.'),T('Translation down 2.')],'Negative a reflects across the x-axis; |a|>1 stretches.'),
   (18,'Which graph is wider than y=x²?', '',r'y=\frac14x^2',['y=4x^2','y=-4x^2','y=2x^2'],'If 0<|a|<1, the parabola is wider.'),
   (19,'A quadratic graph touches the x-axis at exactly one point. How many distinct real zeros does it have?','','1',['0','2','3'],'A tangent x-intercept is a repeated root, one distinct real zero.'),
   (19,'Which values solve the equation from its x-intercepts?',r'y=(x-2)(x+3)',r'\{-3,2\}',[r'\{-2,3\}',r'\{2,3\}',r'\{-3,-2\}'],'Set y=0; either factor is zero.')]:extra(bk,lo,prompt,expr,ans,wrong,why,'rule-application')
 else:
  for lo,prompt,ans,wrong,why in [
   (7,'Which condition guarantees a quadrilateral is a parallelogram?','Both pairs of opposite sides are congruent.',['Exactly one right angle.','Only one pair of opposite sides is congruent.','Its diagonals have equal length.'],'This is a sufficient parallelogram test.'),
   (7,'Which extra condition makes a quadrilateral with one pair of parallel opposite sides a parallelogram?','That same pair is congruent.',['The other pair is congruent.','One interior angle is acute.','The diagonals are congruent.'],'The SAME pair must be both parallel and congruent.'),
   (12,'Two angles of one triangle equal two angles of a second triangle. Which conclusion follows?','The triangles are similar by AA.',['The triangles must be congruent.','All corresponding sides are equal.','The triangles cannot be similar.'],'Two corresponding equal angles establish similarity, not necessarily equal size.'),
   (12,'Which information alone is insufficient to prove two triangles similar?','Only one pair of equal angles.',['Two pairs of equal angles.','All three corresponding side ratios equal.','Two corresponding side ratios equal and the included angles equal.'],'One equal angle leaves the other angles undetermined.')]:extra(bk,lo,prompt,'',T(ans),[T(v) for v in wrong],why,'theorem-conditions')
  for lengths,ans,wrong,why in [(r'\sqrt5,\sqrt{12},\sqrt{13}','Acute',['Right','Obtuse','Not a triangle'],'13<5+12, and the triangle inequality holds.'),(r'2,\sqrt8,\sqrt{12}','Right',['Acute','Obtuse','Not a triangle'],'12=4+8; the converse of Pythagoras applies.')]:extra(bk,16,'How is the triangle with these side lengths classified?',lengths,T(ans),[T(v) for v in wrong],why,'pythagorean-converse')
  for prompt,ans,wrong,why in [('A 45°–45°–90° triangle has legs of length 6. What is its hypotenuse?',r'6\sqrt2',['12','6',r'3\sqrt2'],'Hypotenuse=leg·√2.'),('A 45°–45°–90° triangle has hypotenuse 10. What is each leg?',r'5\sqrt2',[r'10\sqrt2','5','20'],'Each leg=hypotenuse/√2.')]:extra(bk,17,prompt,'',ans,wrong,why,'45-45-90')

def curated_choices(q,c):
 """Reviewed distractor families; values in each row are [key, wrong, wrong, wrong]."""
 lo=int(q['learning_outcome_id'][2:]);n=int(q['display_number'].split('.')[-1])-1
 sets={
 ('9G3',3):[['23','5','-23','14'],['116','-28','28','-116'],['-43','-79','43','79'],['22','58','-22','40']],
 ('9G3',6):[['6','30','-6',r'\frac{90}{11}'],['4',r'\frac75',r'-\frac{20}{3}','-4'],['1','-1',r'\frac7{11}',r'-\frac17'],['4','-4',r'\frac{20}{11}',r'-\frac85']],
 ('9G3',9):[['6','0','3','15'],['3','-3','12','21'],['11','1','6',r'\frac{23}{3}'],['19.33','13.33','16.33','9.00']],
 ('9G3',10):[[r'\frac{20}{a}',r'\frac{26}{a}','20a','20'],[r'\frac{18}{a}',r'-\frac{10}{a}','18a','18'],[r'\frac{24}{a}',r'\frac{14}{a}','24a','24'],[r'-\frac{35}{a}',r'-\frac{23}{a}','-35a',r'\frac{35}{a}']],
 ('9G3',15):[[r'-\frac25',r'\frac25',r'-\frac52',r'-\frac23'],['0','5','1','TEXT:Undefined'],['TEXT:Undefined','0','-6',r'-\frac16'],['-1','1',r'-\frac35',r'\frac35']],
 ('9G3',16):[['0','1','2','-2'],['2','2.4','4','1'],['16','17.4','18','8'],['-6','-4','-4.5','6']],
 ('9G3',20):[['7',r'\frac{37}{3}','21','-7'],['10',r'\frac{26}{5}','25','-10'],['-2','0','-1','-6'],['7','-7','11','21']],
 ('10G3',8):[['c^2','c^6','c^2d^8f^6','c^8'],[r'\frac{p^6t^{21}}{1000}',r'\frac{p^5t^{10}}{1000}',r'\frac{p^6t^{21}}{10}',r'\frac{p^6t^{21}}{30}'],['a^2b^7c','a^{12}b^9c^{15}','a^2b^8c','a^2b^7c^{15}'],[r'\frac{9n^2p^6}{49q^4}',r'\frac{6n^2p^6}{14q^4}',r'\frac{9n^2p^6}{7q^2}',r'\frac{9n^2p^5}{49q^4}'],[r'\frac{16r^{12}t^{24}}{625u^{36}}',r'\frac{8r^{12}t^{24}}{20u^{36}}',r'\frac{16r^7t^{10}}{625u^{13}}',r'\frac{16r^{12}t^{24}}{5u^9}'],[r'\frac{81m^{20}r^{12}}{256p^{32}}',r'\frac{12m^{20}r^{12}}{16p^{32}}',r'\frac{81m^9r^7}{256p^{12}}',r'\frac{81m^{20}r^{12}}{4p^8}']],
 ('10G3',9):[[r'\frac{p^2}{4m^3}',r'-\frac{m^3p^2}{4}',r'\frac{m^3p^2}{4}',r'\frac{p^2}{4m^3t^8}'],['1','0','-1',r'\frac{t^5u}{3v^{16}}'],[r'\frac{y^9z^2}{x^4}',r'\frac{y^9}{x^4z^2}',r'\frac{x^4y^9}{z^2}',r'-\frac{y^9z^2}{x^4}'],['1','0','-1',r'-\frac{5f^8g^2}{h}'],[r'\frac{p^4}{r}',r'\frac{p^4}{r^5}','p^4r',r'-\frac{p^4}{r}'],[r'-\frac{5cd}{8}','0',r'\frac{5cd}{8}',r'-\frac{5c^3d^{11}}8']],
 ('10G3',10):[[r'\frac12',r'-\frac12',r'\frac14','2'],['5','625','25','-5'],['9','243','27','-9'],[r'\frac12',r'\frac1{160}','2',r'-\frac12'],['4','64','8','-4'],[r'\frac25',r'\frac45',r'\frac4{25}',r'-\frac25']],
 ('10G3',12):[[r'\frac{2\sqrt2}3',r'\frac89',r'\frac{2\sqrt2}9',r'\frac{\sqrt2}3'],[r'\frac{2\sqrt{11}}3',r'\frac{44}9',r'\frac{2\sqrt{11}}9',r'\frac{\sqrt{11}}3'],[r'\frac{2\sqrt{21}}{11}',r'\frac{84}{121}',r'\frac{2\sqrt{21}}{121}',r'\frac{\sqrt{21}}{11}'],[r'\frac{\sqrt{15}}2',r'\frac{15}4',r'\frac{\sqrt{15}}4',r'\frac{\sqrt{55}}2']],
 ('10G3',13):[[r'5\sqrt7',r'9\sqrt7',r'5\sqrt{14}',r'14\sqrt7'],[r'20\sqrt2',r'10\sqrt2',r'20',r'42\sqrt2'],[r'11\sqrt5',r'3\sqrt5',r'11\sqrt{10}',r'28\sqrt5'],[r'11\sqrt6',r'7\sqrt6',r'11\sqrt{12}',r'18\sqrt6'],[r'-\sqrt5',r'\sqrt5',r'7\sqrt5',r'\sqrt{15}'],[r'3\sqrt2',r'27\sqrt2',r'9\sqrt2',r'3\sqrt{82}']],
 ('10A1',8):[['101','202','79','158'],['127','254','53','106']],
 ('10A1',14):[[r'\frac{33}2',r'\frac{88}3',r'\frac{33}4','33'],['22',r'\frac{99}2','33','11'],['11','44','22',r'\frac{11}2'],[r'\frac{120}7',r'\frac{42}5',r'\frac{60}7',r'\frac{240}7']],
 ('10A1',15):[[r'2\sqrt6','5','24',r'-2\sqrt6'],['1',r'\frac54',r'\frac52','-1']],
 ('10A1',16):[['15',r'\sqrt{353}','9','225'],['51','69','21',r'\sqrt{1449}'],['100','124','68',r'\sqrt{8432}'],['13','17','7',r'\sqrt{119}']],
 ('10A1',19):[['64','14','71','33'],['13.5','16.5','76.5','14.1'],['21','43','37','25'],['57.7','59.0','32.3','46.4']],
 ('10A1',20):[['62.3','124.6','45.3','77.0'],['41.8','83.6','51.0','29.3'],['71.5','143.1','114.5','135.0'],['19.0','38.0','40.8','45.0']]
 }
 if (c,lo) in sets and n<len(sets[c,lo]):
  vals=sets[c,lo][n];wrong=[o['id'] for o in q['options'] if o['id']!=q['answer']['correct_option_id']]
  family='Use the correct inverse operation and preserve signs on both sides.' if c=='9G3' and lo in [3,6,9,10,20] else 'Use the correct exponent rule: distinguish adding, subtracting and multiplying powers; apply powers to every factor.' if c=='10G3' and lo in [8,9] else 'Use the stated radical, ratio or geometric rule; check reciprocal, sign, squared length and units.'
  for o in q['options']:
   i=0 if o['id']==q['answer']['correct_option_id'] else wrong.index(o['id'])+1;v=vals[i];o['text']=v[5:] if v.startswith('TEXT:') else v
   if v.startswith('TEXT:'):o.pop('math_latex',None)
   else:o['math_latex']=v
   o['misconception']=None if i==0 else family
  q['answer']['correct_option_text']=next(o['text'] for o in q['options'] if o['id']==q['answer']['correct_option_id'])
 if c=='9G3' and lo==1 and n==1:
  for o in q['options']:
   if o.get('math_latex')==r'\frac{4}{6-2}':o['math_latex']=r'\frac{6+2}{4}';o['text']=o['math_latex'];o['misconception']='Use a sum where the prompt specifies a difference.'
 if c=='9G3' and lo==18 and n==3:
  for o in q['options']:
   o['text']=o['text'].replace('slope 7','slope −2/3').replace('(7,0)','(−2/3,0)')
 if c=='10G3' and lo==18:
  wrongs=[['Reflect across the x-axis and stretch by 3','Compress vertically by 1/3 without reflection','Shift down 1/3'],['Reflect across the x-axis and compress by 4/9','Compress vertically by 2/3','Stretch vertically by 9/4'],None,None,['Stretch by 2, shift left 3 and up 8','Compress by 1/2, shift right 3 and up 8','Stretch by 2, shift right 3 and down 8'],['Reflect and compress by 3/4, then shift down 5','Stretch by 4/3 without reflection, then shift down 5','Reflect and stretch by 4/3, then shift up 5']][n]
  if wrongs:
   for o,v in zip([o for o in q['options'] if o['id']!=q['answer']['correct_option_id']],wrongs):o['text']=v;o.pop('math_latex',None)

T=lambda s:'TEXT:'+s
# Calculator entries are explicit expressions, not a simulation of Casio firmware.
def calculator(q,bk):
 lo=int(q['learning_outcome_id'][2:]);c=bk['classroom'];idx=int(q['display_number'].split('.')[-1]);exprs=q.pop('calculator_expressions',[]);kind='evaluate';table=None;branches=None
 if c=='9G3' and lo==24 and q['type']=='frq':
  expr,start,end,step,ys=[('8-X',0,8,4,[8,4,0]),('10-X',0,10,5,[10,5,0]),('X/2+1',-2,2,2,[0,1,2]),('X/4-2',-4,4,4,[-3,-2,-1])][idx-1]
  table=dict(expression=expr,start=start,end=end,step=step,x=[start,start+step,end],y=ys);kind='table'
 if c=='9G3' and lo==25 and q['type']=='frq':
  data=[ [('X/2-1',3,5,1,'x>3; boundary open'),('-2X+3',1,3,1,'x≤3; boundary closed')], [('2X-5',1,3,1,'x>1; boundary open'),('4X-3',-1,1,1,'x≤1; boundary closed')], [('2X+3',-3,-1,1,'x≥−3; boundary closed'),('X/3+1',-9,-3,3,'x<−3; boundary open')], [('3X+4',1,3,1,'x≥1; boundary closed'),('X+3',-1,1,1,'x<1; boundary open')] ][idx-1]
  branches=[]
  for e,st,en,sp,cond in data:
   # Explicit branch expressions avoid relying on a calculator to enforce domains.
   expr=S.sympify(e.replace('^','**'),locals={'X':x},evaluate=True) if not re.search(r'\dX',e) else S.sympify(re.sub(r'(\d)X',r'\1*X',e).replace('^','**'),locals={'X':x})
   xs=[st,st+sp,en];branches.append(dict(expression=e,start=st,end=en,step=sp,x=xs,y=[float(expr.subs(x,v)) for v in xs],condition=cond))
  table=branches[0];kind='table'
 if c=='10G3' and lo==25 and q['type']=='frq':
  expr,start,end,step,ys=[('X^2-X-6',-1.5,2.5,1,[-2.25,-5.25,-6.25,-5.25,-2.25]),('2X^2-12X+16',1,5,1,[6,0,-2,0,6]),('4X^2-32X+60',2,6,1,[12,0,-4,0,12]),('-X^2/2+2X+6',0,4,1,[6,7.5,8,7.5,6])][idx-1]
  table=dict(expression=expr,start=start,end=end,step=step,x=[start+i*step for i in range(5)],y=ys);kind='table';q['table_after_solving']=True
 if c=='10G3' and q.get('graph_workspace'):table=dict(expression='X^2',start=-2,end=2,step=1,x=[-2,-1,0,1,2],y=[4,1,0,1,4]);kind='table'
 explicit={('10A1',15):[['sqrt(4*6)'],['sqrt((1/2)*2)'],['sqrt(8*23)','sqrt(31*8)','sqrt(31*23)'],['10^2/20','20-5','sqrt(20*15)']],('10A1',16):[['sqrt(17^2-8^2)'],['sqrt(45^2+24^2)'],['sqrt(28^2+96^2)'],['sqrt(5^2+12^2)']],('10A1',17):[['(8*sqrt(3))/sqrt(3)','2*8'],['(10*sqrt(3))/sqrt(3)','2*10'],['15*sqrt(3)/2','15/2'],['14/sqrt(3)','2*14/sqrt(3)']],('10A1',18):[['180-90-32','11/tan(32)','11/sin(32)'],['180-90-57','18*sin(57)','18*cos(57)'],['180-90-32','7*cos(32)','7*sin(32)'],['180-90-45','18','18*sqrt(2)']],('10A1',19):[['30/tan(25)'],['atan((32.5-6)/110)'],['30/tan(55)'],['atan((100-5)/60)']],('10A1',20):[['11*14*sin(54)/2'],['8.5*12*sin(125)/2'],['15*18*sin(32)/2'],['9*10*sin(155)/2']],('9G3',21):[['2+6*11'],['7-2*3'],['3^2+(2^3-8)^5'],['(2*11+3*2)/4']],('9G3',22):[['(36-2*4)/2'],['39/0.325'],['(136-55)/13.50'],['50/(10*2)']],('9G3',26):[['-3+(7-1)*(-5)'],['-2+(7-1)*5'],['-11+(7-1)*(-4)'],['-0.75+(7-1)*0.25']]}
 if not q.get('parent_question_id') and (c,lo) in explicit:exprs=explicit[(c,lo)][idx-1]
 geometry={
  6:[['11-6','10+7'],['(15-11)/(3-1)','(11-5)/(3-1)'],['(180+5-11)/3','(2*58+11)/2'],['(5+5)/(3-1)','(9-7)/(2-1)']],
  8:[['(360-110-48)/2'],['(360-36-70)/2'],['sqrt(7^2+4^2)','2*(sqrt(7^2+4^2)+sqrt(11^2+7^2))'],['sqrt(20^2+12^2)','2*(sqrt(20^2+12^2)+sqrt(28^2+12^2))']],
  9:[['(-10)/4','(-4)/4','(-8)/4'],['2*5/4','(-1)*5/4','(-6)*5/4','4*5/4','(-2)*5/4','(-5)*5/4'],['4*3/4','6*3/4','(-6)*3/4','2*3/4','(-8)*3/4'],['(-2)*3/2','6*3/2','(-1)*3/2','(-5)*3/2','3*3/2']],
  10:[['(20-8)/(24-20)'],['(12-4)/(36-32)'],['(9-4)/(4-3)'],['15*4/5-5']],
  11:[['2/1'],['3/2'],['4/6'],['3/2']],
  13:[['(7-1)/(2-1)','(8+5)/(3-1)'],['(3-2)/(1.5-1)','(5-1)/(3-2)'],['30/2'],['2*9']],
  14:[['22*5.25/7'],['33*10/15'],['22*10/20'],['12*18/12.6']]}
 if c=='10A1' and not q.get('parent_question_id') and lo in geometry:exprs=geometry[lo][idx-1]
 if c=='9G3' and not q.get('parent_question_id') and lo in [8,15,17]:
  exprs={8:[['(-3+5)/(8-11)'],['(-1+4)/(29-22)','(1+1)/(36-29)'],['10.5+(-2.25-7.5)/(-6.5)'],['10.75+(-6.5)*(9.5-10)']],15:[['(1-3)/(4+1)'],['(-5+5)/(4+2)'],['(-3)-(-3)'],['(1+4)/(0-5)']],17:[['(-12)-(-9)','(-15)-(-12)'],['15-10','25-15','40-25'],['(-5)-(-10)','0-(-5)'],['(-3)-(-5)','(-1)-(-3)']]}[lo][idx-1]
  if lo==15 and idx==3:kind='vertical'
 if c=='9G3' and q.get('parent_question_id') and lo==17:
  exprs=[[],[],['-9+(11-1)*(-3)'],['(-60+6)/(-3)']][idx-5]
 if c=='10G3' and not q.get('parent_question_id') and lo==11 and idx<=4:
  exprs=[['6*sqrt(2)*3*sqrt(6)/2'],['8*sqrt(12)*4*sqrt(8)'],['sqrt(32*14)'],['sqrt(5/6)']][idx-1]
 if c=='10G3' and lo==20:
  coefficient=[26,-24,-19,11,5,-8][idx-1];exprs=[f'({coefficient}/2)^2']
 if c=='10G3' and lo==14 and idx==1:exprs=['sqrt(576/16)']
 if c=='10G3' and lo in [14,15,17,19] and not q.get('parent_question_id') and '=' in q.get('math_latex',''):
  lhs,rhs=q['math_latex'].split('=');le,ri=parse(lhs),parse(rhs)
  if le is not None and ri is not None and (le.free_symbols|ri.free_symbols)=={x}:
   poly=S.Poly(S.expand(S.sympify(S.sstr(le-ri))),x)
   if poly.degree()==2:
    co=poly.all_coeffs();discr=S.simplify(co[1]**2-4*co[0]*co[2]);kind='quadratic';exprs=[f'({co[1]})^2-4*({co[0]})*({co[2]})']
    if discr>=0:exprs.extend([f'(-({co[1]})+sqrt({discr}))/(2*({co[0]}))',f'(-({co[1]})-sqrt({discr}))/(2*({co[0]}))'])
 if c=='10A1' and lo==25:
  A,aa,bb=[(50,34,40),(24,3,8),(125,22,15),(30,2,4)][idx-1];exprs=[f'{bb}*sin({A})/{aa}'];kind='ssa';sine=bb*math.sin(math.radians(A))/aa
  if sine<=1:
   B=math.degrees(math.asin(min(1,sine)));exprs.append(f'asin({bb}*sin({A})/{aa})')
   for candidate in [B,180-B]:
    if A+candidate<180 and not(candidate!=B and abs(candidate-B)<1e-8):exprs.extend([f'180-{A}-{candidate}',f'{aa}*sin({180-A-candidate})/sin({A})'])
 if c=='9G3' and lo==16:
  exprs=[['2*0'],['2*1'],['2*8'],['2*(-3)']][idx-1];kind='floor'
 if c=='10A1' and lo==24 and q['type']=='frq':
  exprs=[['(-2+4)/2','(-4+2)/2','(-4+0)/2'],['(3+5)/2','(3+4)/2','(4+13)/2'],['sqrt((-1+5)^2+(0+2)^2+(3+1)^2)','(-5-1)/2','(-2+0)/2','(-1+3)/2'],['sqrt((-2*sqrt(3)-sqrt(3))^2+(4-2)^2+(4*sqrt(2)-2*sqrt(2))^2)','(sqrt(3)-2*sqrt(3))/2','(2+4)/2','(2*sqrt(2)+4*sqrt(2))/2']][idx-1]
 if c=='10A1' and lo==22 and q['type']=='frq':exprs=[['360/(180-144)'],['360/(180-160)'],['(360-27)/9'],['(360-76)/4']][idx-1]
 if c=='10A1' and lo==5:exprs=[['(360-12)/6'],['(360+4)/7'],['(540-170)/5'],['(540+4)/8']][idx-1]
 if not table and not exprs:
  e=parse(q.get('math_latex',''))
  if e is not None and isinstance(e,S.Expr):
   if not e.free_symbols:exprs=[S.sstr(e)]
   elif (q['type']=='frq' or lo in ([2,4,10,12] if c=='9G3' else range(1,14))):
    kind='check';subs={s:2+i for i,s in enumerate(sorted(e.free_symbols,key=str))};exprs=[re.sub(r'\b('+ '|'.join(re.escape(str(v)) for v in subs) +r')\b',lambda m:str(subs[S.Symbol(m.group(0))]),S.sstr(e))];q['calculator_substitution']={str(s):v for s,v in subs.items()}
  if c=='9G3' and lo in [3,6,9,20] and q['type']=='mcq':kind='solve';left,right=q['math_latex'].split('=');le,ri=parse(left),parse(right);syms=le.free_symbols|ri.free_symbols;exprs=[re.sub(r'\b('+ '|'.join(re.escape(str(v)) for v in syms) +r')\b','X',S.sstr(le)+'='+S.sstr(ri))]
 if not exprs and not table:return dict(applicable=False,reason='This question assesses a mathematical rule, graph or justification. Use the worked explanation; calculator output alone is insufficient.')
 steps=[dict(title='Calculate mode',keys=['MENU','1'],text='Select Calculate. Use the (−) key for a negative number, and parentheses around fractions and negative bases.')]
 if kind=='table':steps=[dict(title='TABLE mode',keys=['MENU','9'],text='Select Table. In SETUP → Table, select f(x) only (or leave g(x) blank when prompted). fx‑991EX generates values, not a graph.'),dict(title='Enter f(X)',keys=['ALPHA','X'],text='Enter '+table['expression']+'. Use ALPHA and the key labelled X, then =.'),dict(title='Set range',keys=['='],text=f'Start {table["start"]} =; End {table["end"]} =; Step {table["step"]} =.'),dict(title='Read and plot',keys=['▼'],text='Read X and f(X), copy the pairs into the table, then plot them by hand. For a quadratic, include the vertex and two points on each side. '+table.get('condition',''))]
 else:
  if any(re.search(r'(sin|cos|tan)',e) for e in exprs):steps.append(dict(title='Degrees',keys=['SHIFT','MENU'],text='Choose Angle Unit → Degree. Keep full precision until the final rounding. Inverse sine/tangent uses SHIFT then sin/tan.'))
  if kind=='solve':
   steps.append(dict(title='Enter the equation',keys=['ALPHA','X','ALPHA','CALC'],expression=exprs[0],text='Enter the equation below in Calculate. ALPHA with the X-labelled key enters X; ALPHA CALC enters the equality sign. Do not press the ordinary = key to evaluate the equation.'))
   steps.append(dict(title='SOLVE and check',keys=['SHIFT','CALC','='],text='Press SHIFT CALC (SOLVE). When prompted for X, enter an initial value such as 0, then =. Read the solved X and check L−R≈0. Identities and contradictions require algebra.'))
  elif kind=='check':steps.append(dict(title='Numerical check',keys=['CALC'],text='Substitute '+str(q.get('calculator_substitution'))+' into the original expression and each proposed expression. Repeat with different allowed values. Matching values support a check; prove equivalence algebraically.'))
  elif kind=='quadratic':steps.append(dict(title='Check the discriminant, then both signs',keys=[],text='Rearrange to ax²+bx+c=0. Calculate b²−4ac first. A negative result means no real roots; otherwise evaluate both quadratic-formula expressions. Use the method requested by the question in your written work.'))
  elif kind=='vertical':steps.append(dict(title='Check the denominator',keys=[],text='Calculate the change in x. It is zero, so the slope is undefined; do not enter a division by zero.'))
  elif kind=='floor':steps.append(dict(title='Apply floor first',keys=[],text='Find the greatest integer ≤X−1 by reasoning, including for negative values; then enter the multiplication below. Do not round to the nearest integer.'))
  for e in ([] if kind=='solve' else exprs):steps.append(dict(title='Enter and evaluate',keys=['=','S⇔D'],expression=e,text='Enter the expression below, then =. Use S⇔D when a decimal is required.'))
  if kind=='ssa':steps.append(dict(title='Check both angles',keys=[],text='If sin B>1 there is no triangle. Otherwise test B and 180°−B; keep only A+B<180°. Do not round before finding the remaining side.'))
 if branches:
  steps.append(dict(title='Repeat for the second branch',keys=['MENU','9'],text='Enter '+branches[1]['expression']+f'; Start {branches[1]["start"]}; End {branches[1]["end"]}; Step {branches[1]["step"]}. '+branches[1]['condition']+'. TABLE ignores domain restrictions: mark open or closed boundary points yourself.'))
 return dict(branch_tables=branches,applicable=True,model='fx-991EX ClassWiz',kind=kind,steps=steps,expressions=exprs,table=table,illustration_kind='instructional_key_guide_not_firmware',instructional_only=True)

for folder in ['9g3-term1','10g3-term1','10a1-term1']:
 bk=json.loads((ROOT/f'content-imports/textbook-v1-inputs/{folder}.json').read_text());fixmath(bk);changed=0
 crop_updates=ROOT/'content-imports/reviewed-source-crops.json'
 for aid,a in json.loads(crop_updates.read_text()).get(folder,{}).items():bk['assets'][aid]=a
 for q in bk['questions']:
  q.update(grade=9 if bk['classroom']=='9G3' else 10,track='advanced' if bk['classroom']=='10A1' else 'general',source_kind='textbook_exercise',difficulty='standard',skill_tags=[bk['learning_outcomes'][int(q['learning_outcome_id'][2:])-1]['title']])
  if q['type']=='mcq':
   for o in q['options']:
    if o.get('math_latex'):o['text']=o['math_latex']
   q['answer']['correct_option_text']=next(o['text'] for o in q['options'] if o['id']==q['answer']['correct_option_id'])
   changed+=algebra_choices(q)
   ins=q['instruction'];original=ins
   ins=ins.replace('Options give y.','').replace('Options list the vertices in the stated order.','').strip()
   if 'standard form and identify the leading coefficient' in ins:ins='Which option shows the polynomial in standard form and its leading coefficient?'
   elif ins.startswith('Write a numerical expression for '):ins='Which numerical expression represents '+ins[len('Write a numerical expression for '):].rstrip('.')+'?'
   elif ins.startswith('Write a verbal expression'):ins='Which verbal expression represents the given algebraic expression?'
   elif 'slope-intercept form' in ins:ins='Which equation is equivalent to the given equation in slope-intercept form?'
   elif ins.startswith('Write an equation for the original graph'):ins='Which equation matches the graph?'
   elif ins.startswith('Write '):ins='Which option correctly represents the given information? '+ins
   elif ins.startswith('Factor '):ins='Which option is the complete factorisation of the expression?'
   elif ins.startswith('Simplify '):ins='Which option is equivalent to the expression in simplified form?'
   elif ins.startswith('Evaluate '):ins='What is the value of the given expression? '+ins
   elif ins.startswith('Find the geometric mean'):ins='What is the positive geometric mean of the two numbers?'
   elif ins.startswith('Find the slope'):ins='What is the slope of the line through the given points?'
   elif ins.startswith('Find each variable'):ins='Which values of the variables satisfy the parallelogram shown?'
   elif ins.startswith('Find all of x'):ins='Which values of x, y and z are correct, in simplest exact form?'
   elif ins.startswith('Find x and y'):ins='Which values of x and y are correct, in simplest exact form?'
   elif ins.startswith('Find the measure of each interior angle'):ins='Which option gives the interior angles in the stated vertex order?'
   elif ins.startswith('Find '):ins='Which option gives '+ins[5:].rstrip('.')+'?'
   elif ins.startswith('Solve the equation'):ins='Which option gives the complete real solution set?' if bk['classroom']=='10G3' else 'Which value satisfies the equation?'
   elif ins.startswith('Solve the proportion'):ins='Which value satisfies the proportion?'
   elif ins.startswith('Solve for '):ins=ins+' Which expression is correct?'
   if 'Options give y.' in original:
    for opt in q['options']:
     if opt.get('math_latex'):opt['math_latex']='y='+opt['math_latex'];opt['text']=opt['math_latex']
    q['answer']['correct_option_text']=next(opt['text'] for opt in q['options'] if opt['id']==q['answer']['correct_option_id'])
   q['instruction']=ins;q['stem']=ins+' '+q.get('math_latex','')
   curated_choices(q,bk['classroom'])
   for o in q['options']:
    if o['id']!=q['answer']['correct_option_id'] and not o.get('misconception'):o['misconception']='Check the operation, sign, endpoint, correspondence or theorem condition against the given information.'
 addvariants(bk)
 for q in bk['questions']:
  q['reference_kind']=q['source_kind'] if q.get('parent_question_id') else 'worked_example' if 'example' in q['source']['exercise'].lower() else 'exercise'
  q.setdefault('grade',9 if bk['classroom']=='9G3' else 10);q.setdefault('track','advanced' if bk['classroom']=='10A1' else 'general');q['calculator']=calculator(q,bk)
  if q['calculator']['applicable']:q['calculator']['image']=f'calculator/{q["id"]}.png'
 for q in bk['questions']:
  if q['calculator'].get('expressions'):q['calculator']['expressions']=[v.replace('**','^') for v in q['calculator']['expressions']]
 for o in bk['learning_outcomes']:
  group=[q for q in bk['questions'] if q['learning_outcome_id']==o['id']];o['question_ids']=[q['id'] for q in group];o['question_count']=len(group);variants=[q for q in group if q.get('parent_question_id')]
  if variants:o['booklet_question_ids']=o['booklet_question_ids'][:2]+[q['id'] for q in variants[:2]]
  o['assessment_facets']=sorted(set(t for q in group for t in q['skill_tags']));o['calculator_model']='fx-991EX ClassWiz'
 bk.update(content_version='exam-review-v2',mock_storage_namespace=folder+'-exam-review-v2',question_count=len(bk['questions']),mcq_count=sum(q['type']=='mcq' for q in bk['questions']),frq_count=sum(q['type']=='frq' for q in bk['questions']),title='Term 1 exam-style practice bank',title_ar='بنك مراجعة الفصل الأول حسب مخرجات التعلم',authored_notice='Original textbook exercises adapted to exam-style MCQs, with labelled concept applications and example variants. Written tasks retain the original textbook data. Calculator key guides use fx-991EX ClassWiz and are instructional diagrams, not a firmware emulator.',authored_notice_ar='أسئلة الكتاب بصياغة اختبارية، مع تطبيقات للقوانين وأسئلة مشابهة للأمثلة موثقة بوضوح. معطيات المقالية من الكتاب. دليل أزرار fx-991EX ClassWiz تعليمي وليس محاكيًا رسميًا.')
 out=ROOT/f'public/data/exam-banks/{folder}';(out/'calculator').mkdir(exist_ok=True)
 (out/'provenance.json').write_text(json.dumps(dict(content_version=bk['content_version'],source_parts=bk.get('source_parts'),source_sha256=bk.get('source_sha256'),selection_policy=bk['authored_notice'],questions=bk['questions'],assets=bk['assets']),ensure_ascii=False,indent=2)+'\n')
 for name in ['index.json','bank.json']:(out/name).write_text(json.dumps(bk,ensure_ascii=False,indent=2)+'\n')
 for o in bk['learning_outcomes']:
  group=[q for q in bk['questions'] if q['id'] in o['question_ids']];used={a for q in group for a in q['diagram_asset_ids']}
  (out/o['download']).write_text(json.dumps(dict(bank_metadata=dict(id=folder+'-'+o['id'],classroom=bk['classroom'],learning_outcome_id=o['id'],question_count=len(group)),learning_outcomes=[o],questions=group,assets={a:bk['assets'][a] for a in used}),ensure_ascii=False,indent=2)+'\n')
 REPORT.append(dict(classroom=bk['classroom'],questions=bk['question_count'],mcq=bk['mcq_count'],frq=bk['frq_count'],algebra_distractor_sets_rebuilt=changed,calculator_guides=sum(q['calculator']['applicable'] for q in bk['questions'])))
 print(REPORT[-1],flush=True)
(ROOT/'content-imports/review-v2-report.json').write_text(json.dumps(REPORT,indent=2)+'\n')
