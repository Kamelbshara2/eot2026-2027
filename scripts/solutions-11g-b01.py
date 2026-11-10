import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from solutions_io import save
PY=('Pythagorean Theorem.','a^2+b^2=c^2')
D3=('Distance in space.','d=\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}')
save('11G','b01',{
'11G-p08-9b':(1,'read from the figure',[PY,('15 is the hypotenuse; legs 9 and x.','x^2=15^2-9^2=225-81=144'),('Positive root.','x=12'),('Option 3 (C).','12')]),
'11G-p08-9c':(1,'read from the figure',[PY,('65 is the hypotenuse; legs 25 and x.','x^2=65^2-25^2=4225-625=3600'),('Positive root.','x=60'),('Option 2 (B).','60')]),
'11G-p08-10a':(1,[PY,('Legs: height 450 m and horizontal 775 m; L is the hypotenuse.','L^2=450^2+775^2=202500+600625=803125'),('Square root.','L\\approx896.17\\ \\text{m}'),('Option 1 (A).','896.17\\ \\text{m}')]),
'11G-p09-10b':(1,[PY,('Legs 12 ft and 1 ft.','L^2=12^2+1^2=145'),('Exact length.','L=\\sqrt{145}\\ \\text{ft}'),('Option 3 (C).','\\sqrt{145}')]),
'11G-p09-11a':(1,[D3,('Substitute (5, 0, 65) and (3, 0, −6).','d=\\sqrt{(5-3)^2+0^2+(65+6)^2}=\\sqrt{4+5041}'),('Evaluate.','d=\\sqrt{5045}\\approx71\\ \\text{cm}'),('Option 4 (D).','71\\ \\text{cm}')]),
'11G-p10-11b':(1,[D3,('From (0, 0, 0) to (17, −14, 23).','d=\\sqrt{17^2+(-14)^2+23^2}=\\sqrt{289+196+529}'),('Evaluate.','d=\\sqrt{1014}\\approx31.8\\ \\text{km}'),('Option 2 (B).','31.8\\ \\text{km}')]),
'11G-p10-12a':(1,'read from the figure',[('45°–45°–90° triangle: hypotenuse = leg × √2.','x=7\\sqrt2'),('Option 4 (D).','7\\sqrt2')]),
'11G-p10-12b':(1,'read from the figure',[('45°–45°–90°: x is the hypotenuse and 3√2 a leg.','x=3\\sqrt2\\cdot\\sqrt2'),('Simplify.','x=6'),('Option 3 (C).','6')]),
'11G-p11-12c':(1,'read from the figure',[('45°–45°–90°: leg 25, x is the hypotenuse.','x=25\\sqrt2'),('Decimal.','x\\approx35.36'),('Option 1 (A).','35.36')]),
'11G-p11-13a':(1,'read from the figure',[('30°–60°–90°: sides short : long : hyp = 1 : √3 : 2. The side 12 is opposite the 60° angle (long leg).','\\text{long leg}=12'),('Short leg x = long leg ÷ √3.','x=\\dfrac{12}{\\sqrt3}=4\\sqrt3'),('Hypotenuse y = 2x.','y=8\\sqrt3'),('Option 2 (B).','x=4\\sqrt3,\\ y=8\\sqrt3')]),
'11G-p11-13b':(1,'read from the figure',[('30°–60°–90°: the side 15 is opposite the 60° angle (long leg); x is the short leg.','x\\sqrt3=15'),('Short leg.','x=\\dfrac{15}{\\sqrt3}=5\\sqrt3'),('Hypotenuse y = 2x.','y=10\\sqrt3'),('Option 1 (A).','x=5\\sqrt3,\\ y=10\\sqrt3')]),
'11G-p12-14a':(1,[('The 12-ft ramp is the hypotenuse; 4° is at the ground.','\\cos4^\\circ=\\dfrac{x}{12},\\quad \\sin4^\\circ=\\dfrac{y}{12}'),('Horizontal distance.','x=12\\cos4^\\circ\\approx11.97\\ \\text{ft}'),('Height.','y=12\\sin4^\\circ\\approx0.84\\ \\text{ft}'),('Option 3 (C).','x=11.97,\\ y=0.84')]),
'11G-p12-14b':(1,'read from the figure (32 is the side opposite the 41° angle)',[('32 is opposite the 41° angle and x is adjacent: use tan.','\\tan41^\\circ=\\dfrac{32}{x}'),('Solve.','x=\\dfrac{32}{\\tan41^\\circ}\\approx36.8'),('Option 1 (A).','36.8')]),
'11G-p12-15a':(1,[('Height of the drone above Rakeem\'s eyes.','102-6=96\\ \\text{ft}'),('96 is opposite the 30° angle; the distance AB is the hypotenuse.','\\sin30^\\circ=\\dfrac{96}{AB}'),('Solve.','AB=\\dfrac{96}{0.5}=192\\ \\text{ft}'),('Option 3 (C).','192\\ \\text{ft}')]),
})
