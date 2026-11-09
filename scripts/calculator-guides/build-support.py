"""Build question-specific calculator support without changing reviewed question banks.
Requires sympy and antlr4-python3-runtime==4.11.1.
Numerical reference values are computed independently; they are not device captures.
"""
from pathlib import Path
import ast, json, re
import sympy as S
from sympy.parsing.latex import parse_latex
ROOT=Path(__file__).resolve().parents[2]
X=S.Symbol('X', real=True)

def normalize_input(text):
    return re.sub(r'(?<=[0-9)])(?=\()', '*',text).replace('**','^')

def numeric(text):
    """Restricted arithmetic parser. Trigonometric arguments/results use degrees."""
    def walk(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return S.Rational(str(n.value))
        if isinstance(n,ast.Name) and n.id in ['X','x']: return X
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)): return -walk(n.operand) if isinstance(n.op,ast.USub) else walk(n.operand)
        if isinstance(n,ast.BinOp):
            a,b=walk(n.left),walk(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):return a**b
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and len(n.args)==1:
            a=walk(n.args[0]); f=n.func.id
            if f=='sqrt':return S.sqrt(a)
            if f in ['sin','cos','tan']:return getattr(S,f)(a*S.pi/180)
            if f in ['asin','acos','atan']:return getattr(S,f)(a)*180/S.pi
        raise ValueError('Unsupported numeric input: '+text)
    return S.simplify(walk(ast.parse(text.replace('^','**'),mode='eval').body))

def latex(text):
    # Some imported math fields contain doubled command escapes.
    text=text.replace('\\\\','\\').replace('\\left','').replace('\\right','')
    e=parse_latex(text,strict=True)
    return e.replace(lambda v:v.is_Function and len(v.func.__name__)==1,lambda v:S.Symbol(v.func.__name__)*v.args[0])

def operation(expression,purpose='Evaluate this expression after setting up the mathematics.'):
    expression=normalize_input(expression)
    e=numeric(expression)
    assert not e.free_symbols and e.is_finite is not False and e.is_real is not False,expression
    return dict(input=expression.replace('**','^'),exact=S.latex(e),decimal=str(S.N(e,12)),purpose=purpose)

# Outcome-specific manual setup and interpretation, in official bank order.
PREP={
'9G3':[
'Identify the words that determine the operation and group a whole sum or difference in parentheses before dividing.',
'Distribute the outside factor to every term. Choose allowed test values to compare the original and expanded forms.',
'Write the equation with one unknown X. Record the inverse operation you apply to both sides.',
'Isolate the requested letter algebraically. Keep all nonzero-divisor restrictions; a numerical substitution checks only one instance.',
'Identify the equality property from the structure: reversing sides, repeating an expression, or linking two equalities.',
'Distribute first if necessary and collect unknown terms on one side. Enter the original equation as a check.',
'Group the terms exactly as stated and respect multiplication before addition. Retain parentheses around negative substitutions.',
'Label the two ordered pairs consistently. Use (second y − first y)/(second x − first x). For a prediction use the resulting rate and a known value.',
'Match corresponding ratios. Keep variable denominators nonzero, then cross-multiply by hand.',
'Keep the parameter as a letter in the final formula. Choose an allowed nonzero value only for a numerical check.',
'Compare the coefficient of x with the parent y=x. Calculate sample outputs to support the stretch/compression description.',
'Isolate y first. Divide every term by its coefficient; the x coefficient is the slope and the constant is the intercept.',
'Read two exact labelled points from the graph, respecting the axis scale. Compute slope, then b=y−mx. Do not estimate unlabelled coordinates.',
'Apply the greatest-integer definition before arithmetic. Distinguish a value at an endpoint from values immediately to either side.',
'Compute Δx and Δy in the same order. If Δx is zero, stop: a vertical slope is undefined.',
'Subtract 1 from the given x, find the greatest integer no larger than that result, then multiply by 2. Rounding is not floor.',
'Compare successive differences before using an arithmetic-sequence formula. A nonconstant difference invalidates that formula.',
'Read the constant height b. A horizontal line has equation y=b and slope zero; a table can confirm its constant outputs.',
'Identify the operation and the order of the operands from the expression. Arithmetic can illustrate the operation but cannot select its wording.',
'Write each inverse operation and preserve the equality. Use SOLVE on the original equation as a check.',
'Substitute every supplied value in parentheses, then apply the order of operations.',
'Write the formula, identify the units, substitute given values, then isolate the unknown before calculating.',
'Expand and collect terms first. A contradiction and an identity must be established algebraically; SOLVE cannot classify them reliably.',
'Rearrange into y=f(x), choose the requested x values and generate the table. Transfer the pairs to a labelled graph.',
'Enter each piece separately with its own interval. Mark open/closed endpoints manually; TABLE does not enforce piecewise restrictions.',
'Identify a₁ and d, then write aₙ=a₁+(n−1)d. Substitute the requested index and keep its meaning in your answer.'
],
'10G3':[
'Expand using all four products and combine like terms. A numerical check can detect a mistake but does not prove an identity.',
'Use (a±b)²=a²±2ab+b²; include the middle term and its sign.',
'Use (a+b)(a−b)=a²−b². A calculator check should evaluate both the product and proposed difference.',
'Find the greatest common factor and divide every term by it. Expand the result by hand to prove the factorisation.',
'List integer factor pairs whose product is the constant and whose sum is the x coefficient. Calculator roots alone do not prove integer factorisation.',
'For ax²+bx+c, find integer factors of ac that add to b, split the middle term and factor by grouping.',
'Identify both squares and use a²−b²=(a−b)(a+b). Keep any greatest common factor outside.',
'Divide numerical coefficients and subtract exponents of like bases. State that each original denominator is nonzero.',
'Apply zero/negative exponent rules before evaluation. Put negative bases and fractional exponents in parentheses.',
'Interpret a rational exponent as a root followed by a power. Keep the base domain and real-root restrictions.',
'Multiply radicands and extract square factors. For geometry, set up the area or length formula first.',
'Combine compatible radicals, simplify and rationalise if required. Preserve nonzero denominators and real domains.',
'Simplify each radical, then combine only like radical terms. A decimal is a check, not the requested exact surd.',
'Translate the context or factorisation task first. For a quadratic equation, move all terms to one side and identify a, b and c.',
'Follow the requested square-root or completing-square method. Use a polynomial solver to check every root, including a repeated root.',
'Write the function as (x−h)²+k and identify (h,k). Use TABLE around x=h to confirm the vertex and symmetry.',
'Write the equation as a product equal to zero and apply the zero-product property. Never divide by the variable and lose the zero solution.',
'Identify the outside multiplier and shifts in a(x−h)²+k. If the multiplier is inside a square, square it before describing the vertical effect.',
'Roots are x-intercepts, so set y=0. Read or estimate intercepts on the graph; use Polynomial as a numerical/exact check where an equation is given.',
'For a monic quadratic, halve the x coefficient and square the result. Add the same quantity to both sides of an equation.',
'Combine like terms. When subtracting a polynomial, change the sign of every term in the second group.',
'Distribute every term and combine like terms, then check the product at allowed numerical values.',
'Identify whether powers are multiplied or raised to another power. For area square the whole side; for volume cube the whole side.',
'Read the vertex and y-intercept from the graph using its scale. Use the vertex x-coordinate for the symmetry axis and its y-coordinate for the extremum.',
'Read the vertex and another point, write y=a(x−h)²+k, and solve for a. Only then use TABLE to check the derived equation against the graph.'
],
'10A1':[
'Order polynomial terms by descending powers; identify the coefficient of the leading term separately.',
'Expand every product or use the correct special-product identity, then combine like terms.',
'Factor out a greatest common factor, or group terms to expose a shared binomial. Re-expand to verify.',
'Find two integers with the required product and sum. Re-expand the factors to prove the result.',
'Use the interior-angle sum (n−2)×180°. Set up the equation before evaluating the unknown.',
'Use the marked parallelogram property to equate opposite sides/angles or supplement adjacent angles. Solve that equation before reporting a length.',
'Use the marked sufficient condition for a parallelogram. A drawing or numerical coincidence does not prove parallelism or congruence.',
'Identify the perpendicular diagonals and equal adjacent sides of the kite. Use angle sums or the Pythagorean theorem as appropriate.',
'For a dilation about the origin multiply both coordinates by the same scale factor. Keep signs and vertex labels.',
'Match corresponding sides in the correct order, form a proportion and solve it. Check the scale factor in a second pair.',
'Divide image length by original length to find the dilation factor. Distinguish enlargement from reduction using its magnitude.',
'Identify two corresponding equal angles. Calculate a missing angle using 180° only when the given angles support it; state AA in the proof.',
'Identify corresponding proportional segments or a midsegment before setting up an equation. Do not compare noncorresponding lengths.',
'Use corresponding altitudes, medians or angle bisectors of similar triangles in the same ratio as corresponding sides.',
'Draw the altitude/right-triangle relationships, identify the correct geometric-mean equation and then take the nonnegative length.',
'Identify the longest side. For a right triangle use c²=a²+b²; for classification compare c² with a²+b² and verify a triangle exists.',
'Use the exact side ratios of 45°–45°–90° or 30°–60°–90° triangles before calculating.',
'Label opposite, adjacent and hypotenuse relative to the given angle. Set Degree mode and choose sin, cos or tan accordingly.',
'Draw the horizontal reference line and right triangle. Account for observer height before using a trigonometric ratio.',
'Use A=ab sin(C)/2 with the included angle C. Use Degree mode and keep full precision until the final unit-labelled area.',
'Choose the special-product pattern, retain common factors and expand by hand to verify.',
'Distinguish interior and exterior angles. Exterior angles total 360°; a regular polygon has equal exterior angles.',
'Prove similarity and write the ordered correspondence before forming a side proportion. Calculator arithmetic does not replace the proof.',
'Use the three coordinate averages for the midpoint and the square root of the sum of three squared differences for distance.',
'Use a/sin(A)=b/sin(B) in Degree mode. For SSA, test both B and 180°−B and retain only triangles whose angle sum is below 180°.'
]}
# Extra computations for gaps found in the original guide metadata.
EXTRA={}
def group(c,lo,entries):
    bank=json.loads((ROOT/f'public/data/study/{c}.json').read_text())
    qs=[q for q in bank['questions'] if q['learning_outcome_id']==f'LO{lo:02}' and not q.get('calculator',{}).get('applicable')]
    assert len(qs)==len(entries),(c,lo,len(qs),len(entries))
    for q,e in zip(qs,entries):EXTRA[q['id']]=e
# An entry is (role, purpose, numeric expressions). Chosen values are labelled explicitly.
group('9G3',1,[('calculation','After translating the wording, evaluate the grouped expression.',[e]) for e in ['(3+7)/2','(6-2)/4','3*(4+9)','18/(2+7)']])
group('9G3',4,[('numerical_check',p,e) for p,e in [
 ('Illustrative check only: choose u=11, z=3, w=2; v=(u−z)/w. Substitute v back into vw+z.',['(11-3)/2','4*2+3']),
 ('Illustrative check only: choose b=11, x=3, d=2; c=(b−x)/d. Substitute c back into b−cd.',['(11-3)/2','11-4*2']),
 ('Illustrative check only: choose f=2, h=2, j=1. Check g=(9h+10j)/f in fg−9h.',['(9*2+10)/2','2*14-9*2']),
 ('Illustrative check only: choose p=9, n=4. Check m=(p−n)/10 in 10m−p.',['(9-4)/10','10*(1/2)-9'])]])
group('9G3',5,[('reasoning','Arithmetic illustrates the equal values, but you must name the property from its structure.',e) for e in [['4+17'],[],['9+7'],['6+2','4+4']]])
group('9G3',10,[('numerical_check','Illustrative check only: set a=2, calculate the proposed x, then substitute in the original equation.',e) for e in [['20/2','2*10+3'],['18/2','2*9-14'],['24/2','2*12-5'],['-35/2','6+2*(-35/2)']]])
group('9G3',11,[('numerical_check','Compare g(1) with the parent f(1)=1. Then justify the dilation from the coefficient, not from a single test point.',[e]) for e in ['5*1','(1/3)*1','(3/2)*1','(3/4)*1','3*1','0.4*1']])
group('9G3',12,[('calculation','Divide the x coefficient and constant by the y coefficient after rearranging. The two results are slope m and intercept b.',e) for e in [['10/2','12/2'],['-12/4','16/4'],['5/15','-30/15'],['-6/(-3)','-18/(-3)']]])
group('9G3',13,[('manual_setup','Read two exact points from this graph. Calculate (y₂−y₁)/(x₂−x₁), then y₁−m×x₁. Use the results as m and b in y=mx+b; verify another point.',[]) for _ in range(4)])
group('9G3',14,[('reasoning','Use the floor definition and endpoint inequalities. Calculator rounding cannot determine the correct open/closed endpoints.',[]) for _ in range(6)])
group('9G3',15,[('calculation','Compute Δx first; it is zero, so stop before division and write “undefined slope”.',['2-2','5-(-1)'])])
group('9G3',17,[('calculation','The common difference is −3; add it repeatedly to −18.',['-18-3','-21-3','-24-3']),('numerical_check','Derive aₙ=−9+(n−1)(−3) by hand. Check the first and second terms of −3n−6.',['-3*1-6','-3*2-6'])])
group('9G3',18,[('manual_setup','Read or identify the constant b. In TABLE enter the constant alone for f(X); every output will equal b. Write y=b and slope 0.',[]) for _ in range(6)])
group('9G3',19,[('reasoning','Translate the operation into words, preserving operand order. Evaluating a chosen value cannot establish the correct wording.',[]) for _ in range(4)])
group('9G3',23,[('solve','Use X for the original variable; show the algebraic steps and substitute the solution back into both sides.',['2*(X+6)=4*(X+4)']),('solve','Use X for m; show the distribution and collection of terms before your final answer.',['3*(3*X-2)=2*(3*X+3)']),('reasoning','Simplify 2x=2x−6 to 0=−6: no solution. A failed SOLVE is not a proof of no solution.',[]),('reasoning','Expand the left side to 5q−11, identical to the right for every real q. One SOLVE result cannot prove an identity.',[])])
group('10G3',2,[('calculation','The middle term is 2×x×(−5). Calculate its coefficient; retain x in the written term.',['2*(-5)'])])
group('10G3',5,[('numerical_check','For the candidate x²+12x+24 calculate its discriminant. It is not a perfect square, so this monic integer polynomial has no integer roots. Compare all listed candidates.', ['12^2-4*24']),('numerical_check','At x=1 the original is −9. Evaluate both proposed factorisations; one fails. Expand the other by hand to prove it.', ['1+6-16','(1+2)*(1-8)','(1-2)*(1+8)']),('calculation','List negative integer pairs summing to −8; calculate each product. Include all products and justify that the list is exhaustive.',['(-1)*(-7)','(-2)*(-6)','(-3)*(-5)','(-4)*(-4)']),('calculation','List negative integer pairs summing to −5 and calculate both positive products.',['(-1)*(-4)','(-2)*(-3)'])])
group('10G3',8,[('numerical_check','Illustrative check only: set a=2, b=3 and compare the original and proposed form. The power-of-a-quotient rule supplies the proof.',['(2/3)^3','2^3/3^3'])])
group('10G3',11,[('calculation','Use the square-root key on each factor. Write the exact simplified surd rather than only a decimal.',['sqrt(5)*sqrt(10)'])])
group('10G3',13,[('calculation','Evaluate the original expression. Simplify the radicands and combine like radicals by hand to obtain the exact form.',[e]) for e in ['7*sqrt(7)-2*sqrt(7)','3*sqrt(8)+7*sqrt(8)','7*sqrt(5)+4*sqrt(5)','2*sqrt(6)+9*sqrt(6)','3*sqrt(5)-2*sqrt(20)']])
group('10G3',14,[('numerical_check','First factor out 3 by hand. At x=2 compare the original with 3(x−6)²; re-expand for proof.',['3*2^2-36*2+108','3*(2-6)^2'])])
group('10G3',15,[('calculation','For n²+n+c a perfect square requires c=(1/2)². Compare with 3/4.',['(1/2)^2']),('quadratic','A repeated root 4 is obtained from (x−4)²=0, or x²−8x+16=0.',['1','-8','16']),('quadratic','Use coefficients 1, −5, −7. The discriminant 53 is not a perfect square; retain the exact radical answer.',['1','-5','-7']),('calculation','Divide both sides by 3 before taking square roots; the calculator confirms the quotient, not the choice of algebraic operation.',['27/3']),('quadratic','Expand and rearrange to x²−4x−5=0, or use x−2=±3 by hand.',['1','-4','-5'])])
# Tables confirm transformations at and around the known vertex; never claim that these machines plot graphs.
group('10G3',16,[('function_check','Read h and k from vertex form. Check f(h−1), f(h), f(h+1) in TABLE; the middle pair is the vertex.',[e,str(h)]) for e,h in [('(X-1)^2',1),('X^2-8',0),('(X+3)^2',-3),('X^2+7',0),('(X+5)^2-2',-5),('-4+(X-3)^2',3),('(X-3)^2+2',3),('(X+4)^2-1',-4)]])
group('10G3',17,[('quadratic','Rename the unknown as x on the calculator. Expand and rearrange; keep the zero root where present. Then show factorisation in the written answer.',list(map(str,co))) for co in [(27,-81,0),(1,3,0),(1,-4,0),(1,11,18)]])
group('10G3',18,[('function_check','Use the table to compare sample outputs with the parent y=x². Explain the sign, scale and shift algebraically.',[e,str(h)]) for e,h in [('-X^2/3',0),('(-2*X/3)^2',0),('-2*X^2',0),('-7-X^2',0),('2*(X-3)^2+8',3),('-5-4*X^2/3',0),('-2*X^2',0),('X^2/4',0)]])
group('10G3',19,[('reasoning','A graph touching the x-axis once has one distinct real zero. Repeated-root behaviour is a conceptual conclusion; no coefficients are given to enter.',[]),('quadratic','Set y=0 and expand (x−2)(x+3) to x²+x−6. Check both intercepts.',['1','1','-6'])])
group('10G3',23,[('calculation','Square the side: square 5 and multiply each exponent by 2; attach x⁶y¹⁰ to the coefficient.',['5^2','3*2','5*2']),('calculation','Cube the side: cube 4 and multiply each exponent by 3; attach m²⁴n¹² to the coefficient.',['4^3','8*3','4*3']),('numerical_check','For the equality example use m=2,p=q=2. For the strict inequality example use m=2,p=q=1. Prove the general condition by comparing exponents.',['(2^2)*(2^2)','(2^2)^2','(2^1)*(2^1)','(2^1)^1'])])
group('10G3',24,[('manual_setup','Read the vertex (h,k) and intercept from this graph; write x=h as the axis and k as the extremum. A table needs an equation that you must first derive from the graph. Do not infer an equation from the picture shape alone.',[]) for _ in range(4)])
group('10A1',7,[('reasoning','Read the actual parallel/congruent markings and apply a sufficient parallelogram test. Calculator values cannot prove a marking or create a missing condition.',[]) for _ in range(6)])
group('10A1',12,[('reasoning','Use the marked angle pair and the vertical-angle theorem; state the two angle correspondences and conclude AA.',[]),('calculation','Use the given angles to find the third angle, then write the AA correspondence.',['180-42-98']),('reasoning','Only one known angle pair is insufficient for AA. A calculator cannot supply a missing angle.',[]),('calculation','Compute the missing angle in each triangle, then identify the matching angle sets.',['180-87-41','180-52-41']),('reasoning','Two corresponding equal angle pairs prove AA similarity, not necessarily congruence.',[]),('reasoning','One equal angle pair is insufficient; no calculator computation can establish the second pair.',[])])
group('10A1',16,[('calculation','Compare the square of the longest side with the sum of the other squares; 13<17 implies acute. Confirm the triangle inequality.',['13','5+12','sqrt(5)+sqrt(12)']),('calculation','Compare c²=12 with 2²+(√8)². Equality gives a right triangle.',['12','2^2+8'])])
group('10A1',17,[('calculation','In a 45°–45°–90° triangle the hypotenuse is leg×√2. Keep the exact surd.',['6*sqrt(2)']),('calculation','Each equal leg is hypotenuse/√2. Rationalise the exact result.',['10/sqrt(2)'])])
group('10A1',23,[('calculation',p,[e]) for p,e in [('After proving AA and matching vertices, 8/4=10/x gives x=10×4/8.','10*4/8'),('After proving AA, 12/18=8/x gives x=8×18/12.','8*18/12'),('Verify the common ratio 9/4=6.75/3, then use x=5×9/4.','5*9/4'),('After proving AA, 4/x=8/6 gives x=4×6/8.','4*6/8')]])

# These parameter questions require integer-factor sums, not arbitrary substitution.
EXTRA['G10G-Q05-MCQ-03']=('calculation','Enumerate integer pairs with product −19. Their sums are the possible k values; include both sign arrangements.',['1-19','-1+19'])
EXTRA['G10G-Q05-MCQ-04']=('calculation','Enumerate integer pairs with product 14, including both-positive and both-negative pairs. Their sums are all possible k values.',['1+14','2+7','-1-14','-2-7'])

KEY_LABELS={'LP':'(','RP':')','ADD':'+','SUB':'−','MUL':'×','DIV':'÷','POW':'x^□','RIGHT':'→','SQRT':'√','NEG':'(−)','EQ':'=','DOT':'.','SIN':'sin','COS':'cos','TAN':'tan','CALC':'CALC','SHIFT':'SHIFT','ALPHA':'ALPHA'}
def input_keys(expr):
    def walk(n):
        if isinstance(n,ast.Constant):
            return ['DOT' if c=='.' else c for c in str(n.value)]
        if isinstance(n,ast.Name) and n.id in ['X','x']:return ['ALPHA','RP']
        if isinstance(n,ast.UnaryOp):return (['NEG'] if isinstance(n.op,ast.USub) else [])+['LP']+walk(n.operand)+['RP']
        if isinstance(n,ast.BinOp):
            if isinstance(n.op,ast.Pow):return ['LP']+walk(n.left)+['RP','POW']+walk(n.right)+['RIGHT']
            op={ast.Add:'ADD',ast.Sub:'SUB',ast.Mult:'MUL',ast.Div:'DIV'}[type(n.op)]
            return ['LP']+walk(n.left)+[op]+walk(n.right)+['RP']
        if isinstance(n,ast.Call):
            f=n.func.id
            if f=='sqrt':return ['SQRT']+walk(n.args[0])+['RIGHT']
            return (['SHIFT'] if f.startswith('a') else [])+[f[-3:].upper()]+walk(n.args[0])+['RP']
        raise ValueError(expr)
    return walk(ast.parse(expr.replace('^','**'),mode='eval').body)

def table(expr,xs,condition=''):
    normalized=re.sub(r'(\d)X',r'\1*X',expr)
    e=numeric(normalized)
    return dict(expression=normalized,start=xs[0],end=xs[-1],step=xs[1]-xs[0],condition=condition,rows=[dict(x=str(x),y=str(S.N(e.subs(X,S.Rational(str(x))),12)),exact=S.latex(S.simplify(e.subs(X,S.Rational(str(x)))))) for x in xs])

SOURCES=[
 dict(id='upstream-modes',title='fx991ex-emulator: equation, table and SOLVE source',url='https://github.com/magicnothief/fx991ex-emulator/tree/2c26421/src/calc',scope='Implementation inspected and key sequences tested. CE X simulation, not a certification of physical EX or ES PLUS behaviour.'),
 dict(id='casio-ex',title='Casio fx-570EX / fx-991EX user guide',url='https://support.casio.com/global/en/calc/manual/fx-991EX_en/',scope='Official reference link. Live access was blocked by this environment; not used as a newly verified source.'),
 dict(id='reviewed-bank',title='Repository question bank and worked marking keys',url='',scope='Original prompts, reference solutions and diagrams preserved. Numerical checks do not validate every source diagram or theorem proof.')]
report={'coverage':{},'issues':[],'sources':SOURCES}
result={'version':1,'sources':SOURCES,'classes':{}}
for classroom in PREP:
    bank=json.loads((ROOT/f'public/data/study/{classroom}.json').read_text())
    assert len(PREP[classroom])==len(bank['learning_outcomes'])
    outcomes={o['id']:{'title':o['title'],'prepare':PREP[classroom][i]} for i,o in enumerate(bank['learning_outcomes'])}
    guides={}
    for q in bank['questions']:
        g=q.get('calculator',{}); role=g.get('kind','reasoning');exprs=g.get('expressions',[])
        purpose=outcomes[q['learning_outcome_id']]['prepare']
        supplement=EXTRA.get(q['id'])
        if supplement:role,purpose,exprs=supplement
        elif not g.get('applicable'):raise ValueError('Missing review '+q['id'])
        guide={'outcome':q['learning_outcome_id'],'outcome_title':outcomes[q['learning_outcome_id']]['title'],'role':role,'prepare':purpose,'operations':[],'tables':[],'solutions':[], 'source_ids':['reviewed-bank','upstream-modes']}
        if q.get('answer'):
            option=next(o for o in q['options'] if o['id']==q['answer']['correct_option_id'])
            guide['solutions']=[dict(part='Answer',math=option.get('math_latex',''),text=q['answer'].get('explanation',''),answer_text='' if option.get('math_latex') else option.get('text',''))]
        else:
            guide['solutions']=[dict(part=p['id'],math=p.get('answer',{}).get('math_latex',''),text=p.get('answer',{}).get('model_answer_and_marking','')) for p in q.get('parts',[])]
        guide['setup']=['Use Calculate mode (MENU → Calculate on ClassWiz). Clear the previous entry with AC.','Use the (−) key for a negative number, √ for a square root, and the power key for an exponent. The → key exits a root or exponent template.','Keep exact values during the calculation. Use S⇔D to compare with a decimal; round only the final answer.']
        guide['interpret']='Read the computed value with its variable and units. Show the formula and substitution in your written solution, then compare with the worked answer below.'
        if role in ['reasoning','manual_setup']:
            guide['setup']=[]
            guide['interpret']='State the property, correspondence, domain or graph feature explicitly. Calculator output alone does not justify this answer.'
        if role in ['check','numerical_check']:
            guide['interpret']='Matching values provide a numerical check only. Write the algebraic identity or theorem steps to justify the general result.'
        if role=='check':
            subs={S.Symbol(k):S.Rational(str(v)) for k,v in q.get('calculator_substitution',{}).items()}
            if subs:
                guide['prepare']+=' Numerical check values: '+', '.join(f'{k}={v}' for k,v in subs.items())+'. These are chosen test values, not extra givens.'
                try:
                    original_expression=latex(q['math_latex'])
                    answer_expression=latex(guide['solutions'][0]['math'].split(',')[0])
                    original=original_expression.subs(subs)
                    answer=answer_expression.subs(subs)
                    if not original.free_symbols and not answer.free_symbols:
                        if S.simplify(original-answer)!=0:report['issues'].append({'question':q['id'],'issue':'Original and reference answer do not match at check values'})
                        guide['comparison']={'original':S.latex(S.simplify(original)),'answer':S.latex(S.simplify(answer)),'equal':S.simplify(original-answer)==0}
                        # Replace a generated substitution expression only with its parsed source value, preserving explicit parentheses.
                        pattern=r'\b('+ '|'.join(re.escape(str(v)) for v in subs) +r')\b'
                        exprs=[re.sub(pattern,lambda m:'('+str(subs[S.Symbol(m[0])])+')',S.sstr(e)).replace('**','^') for e in [original_expression,answer_expression]]
                except Exception as e:report['issues'].append({'question':q['id'],'issue':'Symbolic comparison unavailable: '+type(e).__name__})
        if role=='quadratic':
            if supplement: co=[S.Rational(v) for v in exprs]
            else:
                m=re.fullmatch(r'\((-?\d+)\)\^2-4\*\((-?\d+)\)\*\((-?\d+)\)',exprs[0]);assert m
                co=[S.Rational(m[2]),S.Rational(m[1]),S.Rational(m[3])]
            a,b,c=co; polynomial=a*X**2+b*X+c; roots=S.solve(polynomial,X)
            guide['keys']=['MENU','NEG','2','2']+sum([input_keys(str(v))+['EQ'] for v in co],[])+['EQ']
            guide['coefficients']=[str(v) for v in co];guide['polynomial']=S.latex(polynomial)+'=0'
            guide['roots']=[S.latex(v) for v in roots];guide['root_decimals']=[str(S.N(v,12)) for v in roots]
            guide['discriminant']=str(b*b-4*a*c)
            guide['setup']=['Rearrange all terms to ax²+bx+c=0. Identify a, b and c including their signs.','ClassWiz: MENU → Equation/Func → 2: Polynomial → 2: Degree 2.','Enter a = '+str(a)+'; press =. Enter b = '+str(b)+'; press =. Enter c = '+str(c)+'; press =.','View the roots with =. A repeated root may appear once. If the discriminant is negative, there are no real roots; complex-root display depends on settings.']
            guide['interpret']='Write all valid roots in the original variable. Substitute them into the original equation. If the question requests factoring, completing the square or graphing, show that method in your working.'
            exprs=[]
        elif role=='solve':
            guide['equation']=exprs[0];lhs,rhs=exprs[0].split('=');le,ri=numeric(lhs),numeric(rhs)
            roots=S.solve(le-ri,X);guide['roots']=[S.latex(r) for r in roots if S.simplify(le.subs(X,r)-ri.subs(X,r))==0]
            guess='10' if q['id'] in ['G9G-BOOK-Q09-MCQ-03','G9G-BOOK-Q09-MCQ-04'] else '0'
            guide['initial_guess']=guess
            guide['excluded_values']=[S.latex(v) for v in set(S.solve(S.denom(le),X)+S.solve(S.denom(ri),X))]
            guide['keys']=input_keys(lhs)+['ALPHA','CALC']+input_keys(rhs)+['SHIFT','CALC']+input_keys(guess)+['EQ','EQ']
            guide['checks']=[dict(x=S.latex(r),left=S.latex(le.subs(X,r)),right=S.latex(ri.subs(X,r))) for r in roots]
            guide['setup']=['Use Calculate mode. Use X in place of the problem’s unknown, and enter both sides of the equation.','Use ALPHA then CALC for the equality sign inside the equation; the ordinary = key evaluates an entry.','Press SHIFT then CALC (SOLVE). For this example enter the initial guess '+guess+' and confirm. A different guess can fail or converge differently; never use a zero denominator.','Read X and the L−R residual. For these linear/rational equations check the result in the original equation and reject forbidden denominators.']
            guide['interpret']='Write the solution in the original variable. Include your inverse-operation or cross-multiplication steps and the substitution check; a SOLVE display is not the full written solution.'
            exprs=[]
        elif role in ['table','function_check']:
            if role=='function_check':
                expr,h=exprs;h=float(h);guide['tables']=[table(expr,[h-2,h-1,h,h+1,h+2])]
            elif q.get('graph_workspace'):
                guide['tables']=[table(e,[-2,-1,0,1,2]) for e in ['X','X^2','X^3']]
                guide['prepare']+=' The task requests graphing-calculator plots. ClassWiz provides values only; use a graphing tool if a plotted device output is required.'
            else:
                for t in g.get('branch_tables') or [g['table']]:
                    generated=table(t['expression'],t['x'],t.get('condition',''))
                    for row,expected in zip(generated['rows'],t['y']):assert abs(float(row['y'])-expected)<1e-8,(q['id'],row,expected)
                    guide['tables'].append(generated)
            guide['setup']=['ClassWiz: MENU → Table. Choose f(x) only in Table settings, or leave g(x) blank when prompted.','Enter the function using the X-labelled key. Use parentheses around fractional coefficients and powers. Confirm with =.','Enter Start, End and Step shown in the table below; confirm each entry and generate the table.','Copy each (x,f(x)) pair accurately. Plot by hand on the requested axes and label the scale. For piecewise functions enforce the interval and endpoint conditions yourself.']
            guide['interpret']='Use the pairs to support the graph, vertex, symmetry or transformation. A finite table does not prove the full domain, range, asymptote or end behaviour.'
            exprs=[]
        if role=='vertical':guide['interpret']='A zero change in x makes the slope undefined; a division error is not a numerical slope.'
        if role=='floor':guide['prepare']+=' Compute floor(x−1) manually first; for negative inputs floor moves towards −∞, not towards zero.'
        if role=='ssa':guide['interpret']='Read the angle in degrees. Test B and 180°−B, keep only A+B<180°, then calculate the remaining angle and side for each valid triangle.'
        if any(re.search(r'(sin|cos|tan)',e) for e in exprs):guide['setup'].insert(1,'Set Angle Unit to Degree before using sin, cos, tan or their inverse functions. SHIFT followed by sin/cos/tan selects the inverse.')
        for e in exprs:
            op=operation(e,guide['prepare'] if supplement else 'Evaluate the prepared expression. Relate it to the formula and worked solution below.')
            op['keys']=['AC']+input_keys(op['input'])+['EQ']
            op['key_labels']=[KEY_LABELS.get(k,k) for k in op['keys']]
            guide['operations'].append(op)
        for t in guide['tables']:
            t['keys']=['MENU','9']+input_keys(t['expression'])+['EQ','EQ']+input_keys(str(t['start']))+['EQ']+input_keys(str(t['end']))+['EQ']+input_keys(str(t['step']))+['EQ','EQ']
            for row in t['rows']:
                expr=t['expression'].replace('X','('+row['x']+')')
                row['keys']=['AC']+input_keys(expr)+['EQ']
        guides[q['id']]=guide
    assert len(guides)==len(bank['questions'])
    result['classes'][classroom]={'outcomes':outcomes,'questions':guides}
    from collections import Counter
    report['coverage'][classroom]={'outcomes':len(outcomes),'questions':len(guides),'roles':dict(Counter(g['role'] for g in guides.values()))}
(ROOT/'public/data/study/calculator-support.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'content-imports/calculator-support-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
