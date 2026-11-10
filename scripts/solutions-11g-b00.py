import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from solutions_io import save
SIM=('Similar triangles: corresponding sides are proportional.','\\dfrac{a_1}{a_2}=\\dfrac{b_1}{b_2}')
save('11G','b00',{
'11G-p02-1c':(1,[('A dilation centred at the origin multiplies both coordinates by k = ½.','(x,y)\\to\\left(\\tfrac12x,\\tfrac12y\\right)'),('Apply to each vertex.',"T\\prime(-2,-2.5),\\ R\\prime(0,3),\\ S\\prime(2,1.5)"),('Option 3 (C).',"T\\prime(-2,-2.5),\\ R\\prime(0,3),\\ S\\prime(2,1.5)")]),
'11G-p03-2a':(1,[('Scale: 4 cm on the map is 20 m, so 1 cm represents 5 m.','\\dfrac{20\\text{ m}}{4\\text{ cm}}=5\\ \\text{m/cm}'),('Map length of the round trip.','9+8+4=21\\ \\text{cm}'),('Actual distance.','21\\times5=105\\ \\text{m}=10500\\ \\text{cm}'),('Option 2 (B).','105\\ \\text{m}')]),
'11G-p03-2b':(1,[('Scale: 8 cm is 4 km, so 1 cm represents 0.5 km.','\\dfrac{4}{8}=0.5\\ \\text{km/cm}'),('Map length of the trip.','2+8+7=17\\ \\text{cm}'),('Actual distance.','17\\times0.5=8.5\\ \\text{km}'),('Option 2 (B).','8.5\\ \\text{km}')]),
'11G-p04-3a':(1,'read from the figure',[('PQ ∥ JK (arrow marks), so corresponding angles are equal.','\\angle LPQ=\\angle LJK,\\ \\angle LQP=\\angle LKJ'),('Both triangles share angle L; two equal angles give AA similarity.','\\triangle KLJ\\sim\\triangle QLP\\ \\text{(AA)}'),('Option 1 (A).','\\text{AA}')]),
'11G-p04-3b':(1,'read from the figure',[('Third angle of each right triangle.','\\angle A=180-90-44=46^\\circ,\\quad \\angle G=180-90-47=43^\\circ'),('The acute angles are 44°, 46° and 43°, 47°: no pair matches.','44^\\circ,46^\\circ\\ne43^\\circ,47^\\circ'),('Not similar: option 4 (D).','\\text{not similar}')]),
'11G-p04-4a':(1,'read from the figure',[SIM,('Corresponding sides (vertical angles at B, right angles): AC ↔ DE and BC ↔ BE.','\\dfrac{x+1}{x+5}=\\dfrac{12}{15}'),('Cross-multiply.','15x+15=12x+60\\Rightarrow x=15'),('AC = x + 1.','AC=16'),('Option 2 (B).','16')]),
'11G-p05-4b':(1,'read from the figure',[SIM,('JK ∥ MN gives JL/LM = JK/MN.','\\dfrac{x+18}{x-3}=\\dfrac{16}{4}'),('Solve.','x+18=4x-12\\Rightarrow x=10'),('JL = x + 18.','JL=28'),('Option 4 (D).','28')]),
'11G-p05-4c':(1,'read from the figure',[SIM,('HG ∥ FD with HG = 6, FD = 12: scale factor 1/2.','\\dfrac{EH}{EF}=\\dfrac{6}{12}=\\dfrac12'),('EF = EH + 9.','\\dfrac{EH}{EH+9}=\\dfrac12\\Rightarrow EH=9'),('Option 1 (A).','EH=9')]),
'11G-p05-5':(1,'read from the figure',[('Compare sides in order from shortest to longest.','\\dfrac{8}{6}=\\dfrac{12}{9}=\\dfrac{16}{12}=\\dfrac43'),('All three ratios are equal: SSS similarity.','\\text{SSS}'),('Option 2 (B).','\\text{SSS}')]),
'11G-p06-6a':(1,'read from the figure',[('Three parallel lines cut congruent segments on one transversal (marked), so they cut congruent segments on every transversal.','2x+1=x+7,\\quad 3y-8=y+5'),('Solve.','x=6,\\quad y=6.5'),('Option 2 (B).','x=6,\\ y=6.5')]),
'11G-p06-6b':(1,'read from the figure',[('The marked segment is a midsegment: it bisects both sides.','x+3=\\tfrac32x+2,\\quad 2y-1=3y-5'),('Solve.','x=2,\\quad y=4'),('Option 4 (D).','x=2,\\ y=4')]),
'11G-p06-7a':(1,'read from the figure',[('In similar triangles corresponding segments (altitude/median) are proportional to corresponding sides.','\\dfrac{MN}{XY}=\\dfrac{PF}{ZG}'),('Substitute.','\\dfrac{18}{27}=\\dfrac{x}{12}'),('Solve.','x=8'),('Option 3 (C).','x=8')]),
'11G-p07-8a':(1,[('Geometric mean of a and b is √(ab).','\\sqrt{5\\times45}'),('Simplify.','\\sqrt{225}=15'),('Option 1 (A).','15')]),
'11G-p07-8b':(1,[('Geometric mean.','\\sqrt{4\\times25}=\\sqrt{100}'),('Simplify.','10'),('Option 3 (C).','10')]),
'11G-p07-9a':(1,'read from the figure',[('Pythagorean Theorem: x is the hypotenuse, legs 3 and 3.','x^2=3^2+3^2=18'),('Take the positive square root.','x=\\sqrt{18}=3\\sqrt2'),('Option 2 (B).','3\\sqrt2')]),
})
