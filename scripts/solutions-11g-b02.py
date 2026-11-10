import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from solutions_io import save
DEP=('Dependent events (no replacement): multiply, reducing the totals after each draw.','P(A\\cap B)=P(A)\\cdot P(B\\mid A)')
save('11G','b02',{
'11G-p13-15b':(1,[('The height a is opposite the 35° angle; 200 m is adjacent.','\\tan35^\\circ=\\dfrac{a}{200}'),('Solve.','a=200\\tan35^\\circ\\approx140.04'),('Nearest metre: option 1 (A).','140\\ \\text{m}')]),
'11G-p13-16a':(1,[('List every (Saturday, Sunday) pair; each day can be black (B) or red (R).','2\\times2=4\\ \\text{outcomes}'),('Sample space.','S=\\{RR,\\ RB,\\ BR,\\ BB\\}'),('Option 1 (A).','S=\\{RR,RB,BR,BB\\}')]),
'11G-p13-16b':(1,[('Two projects, each red (R) or yellow (Y): 2 × 2 outcomes.','2\\times2=4'),('Organised list.','S=\\{RY,\\ RR,\\ YR,\\ YY\\}'),('Option 3 (C).','S=\\{RY,RR,YR,YY\\}')]),
'11G-p14-17a':(1,[('A die has six equally likely faces.','S=\\{1,2,3,4,5,6\\}'),('Option 1 (A).','\\{1,2,3,4,5,6\\}')]),
'11G-p14-17b':(1,[('Prime numbers from 1 to 6 (1 is not prime).','\\{2,3,5\\}'),('Option 2 (B).','\\{2,3,5\\}')]),
'11G-p17-20a':(1,[('The four games are independent, each won with probability ½.','P=\\left(\\tfrac12\\right)^4'),('Evaluate.','P=\\tfrac1{16}'),('Option 2 (B).','\\tfrac1{16}')]),
'11G-p17-20b':(1,[('Number of ways to draw 4 of 6 names.','\\binom64=15'),('Ways to get all 3 directors and 1 of 3 assistants.','\\binom33\\binom31=3'),('Probability.','P=\\dfrac{3}{15}=\\dfrac15'),('Option 2 (B).','\\tfrac15')]),
'11G-p18-20c':(1,[DEP,('13 hearts in 52 cards; one fewer each time.','P=\\dfrac{13}{52}\\cdot\\dfrac{12}{51}\\cdot\\dfrac{11}{50}=\\dfrac{1716}{132600}'),('As a percentage.','P\\approx0.0129=1.29\\%'),('Option 4 (D).','1.29\\%')]),
'11G-p16-19a':(1,[DEP,('5 of 10 slices are mushroom; after Tessa takes one, 4 of 9 remain.','P=\\dfrac5{10}\\cdot\\dfrac49=\\dfrac{20}{90}'),('Simplify.','P=\\dfrac29'),('Option 3 (C).','\\tfrac29')]),
'11G-p16-19b':(1,[DEP,('5 of 20 got all correct; choose 3 without replacement.','P=\\dfrac5{20}\\cdot\\dfrac4{19}\\cdot\\dfrac3{18}=\\dfrac{60}{6840}'),('Simplify.','P=\\dfrac1{114}'),('Option 1 (A).','\\tfrac1{114}')]),
})
