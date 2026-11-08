"""Independent symbolic/structural audit; reports coverage rather than claiming a proof of all prose."""
from pathlib import Path
import json,re,math,itertools
import sympy as S
from sympy.parsing.latex import parse_latex
ROOT=Path(__file__).resolve().parent.parent

def parse(s):
 if not s or any(k in s for k in ['begin','text','quad',',','=','circ','infty','lfloor']):return None
 try:
  e=parse_latex(s.replace('\\left','').replace('\\right',''),strict=True)
  return e.replace(lambda v:v.is_Function and len(v.func.__name__)==1,lambda v:S.Symbol(v.func.__name__)*v.args[0])
 except Exception:return None
counts=dict(option_pairs_checked=0,original_keys_compared=0,expression_keys_proved=0,table_cells_checked=0);issues=[]
for folder in ['9g3-term1','10g3-term1','10a1-term1']:
 b=json.loads((ROOT/f'public/data/exam-banks/{folder}/index.json').read_text());old={q['id']:q for q in json.loads((ROOT/f'content-imports/textbook-v1-inputs/{folder}.json').read_text())['questions']}
 for q in b['questions']:
  if q['type']=='mcq':
   options=[(o['id'],parse(o.get('math_latex',''))) for o in q['options']]
   for (ia,a),(ib,bb) in itertools.combinations(options,2):
    if a is not None and bb is not None:
     counts['option_pairs_checked']+=1
     if S.simplify(a-bb)==0:issues.append(f'{q["id"]}: equivalent choices {ia}/{ib}')
   answer=next(o for o in q['options'] if o['id']==q['answer']['correct_option_id']);ans=parse(answer.get('math_latex',''))
   original=old.get(q['id'])
   if original:
    oldans=parse(next(o.get('math_latex','') for o in original['options'] if o['id']==original['answer']['correct_option_id']))
    if ans is not None and oldans is not None:
     counts['original_keys_compared']+=1
     if S.simplify(ans-oldans)!=0:issues.append(f'{q["id"]}: revised answer differs from original')
   expr=parse(q.get('math_latex',''))
   if expr is not None and ans is not None and any(t in q['instruction'].lower() for t in ['simplified form','complete factorisation','the product?','sum or difference?','value of the given expression']):
    if isinstance(expr,S.Expr) and isinstance(ans,S.Expr):
     counts['expression_keys_proved']+=1
     diff=S.simplify(S.powdenest(expr-ans,force=True))
     if diff!=0:issues.append(f'{q["id"]}: expression/key mismatch {diff}')
  guide=q['calculator']
  if guide.get('table'):
   for t in guide.get('branch_tables') or [guide['table']]:
    x=S.Symbol('X');expr=S.sympify(re.sub(r'(\d)X',r'\1*X',t['expression']).replace('^','**'),locals={'X':x})
    assert len(t['x'])==len(t['y'])
    for i,(xx,yy) in enumerate(zip(t['x'],t['y'])):
     assert abs(xx-(t['start']+i*t['step']))<1e-8
     counts['table_cells_checked']+=1
     if abs(float(expr.subs(x,xx))-yy)>1e-8:issues.append(f'{q["id"]}: invalid table value')
report=dict(checks=counts,issues=issues,limitations='Symbolic checks cover parseable scalar expressions. Geometry, prose, graph readings and rubrics also require source review; this audit does not certify those automatically.')
(ROOT/'content-imports/reviewed-math-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert not issues
