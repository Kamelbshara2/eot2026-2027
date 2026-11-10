import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SIM = ('Similar polygons: corresponding sides are proportional.', r'\dfrac{a_1}{a_2}=\dfrac{b_1}{b_2}')
def P(st): return {'parts': {'a': {'steps': [{'text': t, 'latex': l} for t, l in st]}}, 'verified': True}
a59, l59 = 5 / math.tan(math.radians(59)), 5 / math.sin(math.radians(59))
b18, h18 = 12 * math.tan(math.radians(18)), 12 / math.cos(math.radians(18))
s48, c48 = 3.5 * math.sin(math.radians(48)), 3.5 * math.cos(math.radians(48))
I = {
 '11G-p18-21a': P([SIM, ('Match corresponding sides from the figure.', r'\dfrac{x+1}{3x+1}=\dfrac{8}{20}'), ('Cross-multiply.', r'20(x+1)=8(3x+1)\Rightarrow20x+20=24x+8'), ('Solve.', r'4x=12\Rightarrow x=3')]),
 '11G-p18-21b': P([SIM, ('Match corresponding sides.', r'\dfrac{8x-1}{3x-1}=\dfrac{12}{4}=3'), ('Cross-multiply.', r'8x-1=9x-3'), ('Solve.', r'x=2')]),
 '11G-p19-21c': P([SIM, ('Match corresponding sides.', r'\dfrac23=\dfrac{x+3}{2x+2}'), ('Cross-multiply.', r'2(2x+2)=3(x+3)\Rightarrow4x+4=3x+9'), ('Solve.', r'x=5')]),
 '11G-p19-21d': P([SIM, ('Match corresponding sides.', r'\dfrac{x+5}{15}=\dfrac45'), ('Cross-multiply.', r'5(x+5)=60\Rightarrow x+5=12'), ('Solve.', r'x=7')]),
 '11G-p19-22a': P([('Triangle Proportionality: a line parallel to one side divides the other two sides proportionally.', r'\dfrac{9}{ED}=\dfrac{6}{4}'), ('Solve.', r'6\,ED=36\Rightarrow ED=6')]),
 '11G-p19-22b': P([('Parallel line: corresponding parts of the whole triangle are proportional.', r'\dfrac{AE}{AE+5}=\dfrac{12}{16}'), ('Cross-multiply.', r'16AE=12AE+60'), ('Solve.', r'4AE=60\Rightarrow AE=15')]),
 '11G-p20-22c': P([('MN = MP − NP.', r'MN=18-6=12'), ('Compare the ratios on both sides.', r'\dfrac{MN}{MP}=\dfrac{12}{18}=\dfrac23,\qquad\dfrac{MR}{MQ}=\dfrac{16}{24}=\dfrac23'), ('Equal ratios: by the converse of the Triangle Proportionality Theorem NR ∥ PQ.', r'NR\parallel PQ')]),
 '11G-p20-23a': P([('The given leg 5 is opposite the 59° angle? No — it is adjacent to the right angle and opposite the 59° angle; find the other leg with tan and the hypotenuse with sin.', r'b=\dfrac{5}{\tan59^\circ},\quad c=\dfrac{5}{\sin59^\circ}'), ('Evaluate.', f'b\\approx{a59:.2f},\\quad c\\approx{l59:.2f}'), ('Perimeter.', f'P=5+{a59:.2f}+{l59:.2f}\\approx{5 + a59 + l59:.2f}\\ \\text{{in}}'), ('Area = ½ × leg × leg.', f'A=\\tfrac12(5)({a59:.2f})\\approx{2.5 * a59:.2f}\\ \\text{{in}}^2')]),
 '11G-p21-23b': P([('Other leg with tan and hypotenuse with cos (12 is adjacent to 18°).', r'b=12\tan18^\circ,\quad c=\dfrac{12}{\cos18^\circ}'), ('Evaluate.', f'b\\approx{b18:.2f},\\quad c\\approx{h18:.2f}'), ('Perimeter.', f'P=12+{b18:.2f}+{h18:.2f}\\approx{12 + b18 + h18:.2f}\\ \\text{{cm}}'), ('Area.', f'A=\\tfrac12(12)({b18:.2f})\\approx{6 * b18:.2f}\\ \\text{{cm}}^2')]),
 '11G-p21-23c': P([('Hypotenuse 3.5 and angle 48°: legs with sin and cos.', r'a=3.5\sin48^\circ,\quad b=3.5\cos48^\circ'), ('Evaluate.', f'a\\approx{s48:.2f},\\quad b\\approx{c48:.2f}'), ('Perimeter.', f'P=3.5+{s48:.2f}+{c48:.2f}\\approx{3.5 + s48 + c48:.2f}\\ \\text{{ft}}'), ('Area.', f'A=\\tfrac12({s48:.2f})({c48:.2f})\\approx{0.5 * s48 * c48:.2f}\\ \\text{{ft}}^2')]),
 '11G-p22-24a': P([('Rise above eye level.', r'102-6=96\ \text{ft}'), ('96 is opposite the 30° angle of elevation and the line of sight is the hypotenuse.', r'\sin30^\circ=\dfrac{96}{d}'), ('Solve.', r'd=\dfrac{96}{0.5}=192\ \text{ft}')]),
 '11G-p22-24b': P([('Height is opposite the 35° angle, 200 m is adjacent.', r'\tan35^\circ=\dfrac{h}{200}'), ('Solve.', f'h=200\\tan35^\\circ\\approx{200 * math.tan(math.radians(35)):.2f}\\approx140\\ \\text{{m}}')]),
 '11G-p23-25a': P([('Box B: 2% of 150 chips are defective.', r'150\times0.02=3'), ('Without replacement the second draw depends on the first.', r'P=\dfrac{3}{150}\cdot\dfrac{2}{149}'), ('Simplify.', r'P=\dfrac{6}{22350}=\dfrac1{3725}\approx0.00027')]),
 '11G-p24-25c': P([('Probability of travelling at all.', r'P(D\cup F)=1-0.1=0.9'), ('Addition rule.', r'0.9=0.6+P(F)-0.2\Rightarrow P(F)=0.5'), ('Conditional probability.', r'P(F\mid D)=\dfrac{P(F\cap D)}{P(D)}=\dfrac{0.2}{0.6}=\dfrac13')]),
 '11G-p24-26a': P([('Not mutually exclusive: subtract the overlap.', r'P(A\cup B)=P(A)+P(B)-P(A\cap B)'), ('Counts: 5 round, 4 orange, 2 both out of 9.', r'\dfrac59+\dfrac49-\dfrac29'), ('Result.', r'\dfrac79')]),
 '11G-p24-26b': P([('Addition rule with overlap.', r'P(M\cup I)=P(M)+P(I)-P(M\cap I)'), ('Counts: 3 male, 6 international, 2 both out of 8.', r'\dfrac38+\dfrac68-\dfrac28'), ('Result.', r'\dfrac78')]),
}
I['11G-p20-23a']['parts']['a']['steps'][0]['text'] = 'The leg 5 is opposite the 59° angle: find the other leg with tan and the hypotenuse with sin.'
(ROOT / 'content-imports/upper-grades/solutions/11G-cardfrq.json').write_text(json.dumps({'class': '11G', 'items': I}, ensure_ascii=False, indent=1)); print(len(I))
