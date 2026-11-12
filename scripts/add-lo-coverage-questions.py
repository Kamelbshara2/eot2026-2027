#!/usr/bin/env python3
"""Authored questions for outcome-description parts that no existing question practised (audit 2026-11-12,
scripts/audit-lo-coverage.py). Each is labelled source_kind 'authored_lo_variant' (not a textbook item), has
bilingual steps with 'why', Arabic instruction/options, and a calculator entry (by hand, or keys checked on the
emulator by tests/calculator-support.test.js). Values are asserted here before writing. Re-running replaces them.
usage: python3 scripts/add-lo-coverage-questions.py [--write]
"""
import importlib.util, json, math, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
WRITE = '--write' in sys.argv
spec = importlib.util.spec_from_file_location('cp', ROOT / 'scripts/calculator-guides/calculator-policy.py'); cp = importlib.util.module_from_spec(spec); sys.argv, _a = ['x'], sys.argv; spec.loader.exec_module(cp); sys.argv = _a


def S(t, a, l, w, wa): return {'text': t, 'ar': a, 'latex': l, 'why': w, 'why_ar': wa}


# id: (class, LO, instruction_en, instruction_ar, math, [(option, option_ar or None)], key, explanation, steps, calculator expressions or None)
FRQ_BLANKS = {   # outcomes whose EOT slot is a written question: answer spaces (tolerance-checked where rounded)
    '11A-Q21-cov-eval': [r'\ln(e^{5})=[[5]],\quad e^{\ln 3}=[[3]]', r'\text{Value}=[[8]]'],
    '11A-Q21-cov-solve': [r'x=\ln [[7]]', r'x\approx[[~0.0001:1.9459]]'],
    '11A-Q22-cov-double': [r'e^{0.04t}=[[2]]', r't=\dfrac{\ln 2}{[[0.04]]}\approx[[~0.05:17.3]]\ \text{years}'],
    '11A-Q22-cov-rate': [r'e^{6k}=[[4]]', r'k=\dfrac{\ln 4}{[[6]]}\approx[[~0.0001:0.2310|0.231]]'],
    '12G-Q25-cov-inv90': [r'x=\mu+z\sigma=170+[[1.28]]([[8]])', r'x\approx[[~0.05:180.2]]\ \text{cm}'],
    '12G-Q25-cov-inv5': [r'x=60+([[-1.645]])(10)', r'x\approx[[~0.05:43.6]]'],
}
Q = {
 '11G-Q04-cov-sas': ('11G', 'LO04', 'In △ABC, AB = 6, AC = 8 and ∠A = 50°. In △DEF, DE = 9, DF = 12 and ∠D = 50°. Are the triangles similar? Choose the correct reason.',
   'في △ABC: AB = 6 و AC = 8 و ∠A = 50°. وفي △DEF: DE = 9 و DF = 12 و ∠D = 50°. هل المثلثان متشابهان؟ اختر السبب الصحيح.', '',
   [('Similar by SAS: 6/9 = 8/12 and the included angles are equal.', 'متشابهان بـ SAS: 6/9 = 8/12 والزاويتان المحصورتان متساويتان.'), ('Similar by SSS: all three sides are known.', 'متشابهان بـ SSS: الأضلاع الثلاثة معلومة.'),
    ('Not similar: the sides have different lengths.', 'غير متشابهين: أطوال الأضلاع مختلفة.'), ('Similar by AA: one pair of angles is equal.', 'متشابهان بـ AA: زوج واحد من الزوايا متساوٍ.')], 'A',
   'Two pairs of sides are in the same ratio 2/3 and the angles between them are equal, so SAS similarity applies.',
   [S('Compare the two pairs of sides that form the known angle.', 'قارن زوجي الأضلاع اللذين يحصران الزاوية المعلومة.', r'\tfrac{AB}{DE}=\tfrac69=\tfrac23,\quad \tfrac{AC}{DF}=\tfrac{8}{12}=\tfrac23', 'SAS needs two side ratios to be equal.', 'التشابه SAS يحتاج تساوي نسبتي ضلعين.'),
    S('Check that the equal angle is BETWEEN those sides (included angle).', 'تأكد أن الزاوية المتساوية محصورة بين هذين الضلعين.', r'\angle A=\angle D=50^\circ', 'The angle must be the included one, otherwise SAS does not apply.', 'يجب أن تكون الزاوية محصورة، وإلا لا ينطبق SAS.'),
    S('So the triangles are similar by SAS with scale factor 3/2.', 'إذن المثلثان متشابهان بـ SAS بمعامل 3/2.', r'\triangle ABC\sim\triangle DEF', 'SSS would need all three sides; AA would need two angles.', 'SSS يحتاج الأضلاع الثلاثة، و AA يحتاج زاويتين.')], None),
 '11G-Q04-cov-sss': ('11G', 'LO04', 'A triangle has sides 4, 6 and 8. A second triangle has sides 6, 9 and 12. Are they similar? Choose the correct reason.',
   'أطوال أضلاع مثلث 4 و 6 و 8، وأطوال أضلاع مثلث آخر 6 و 9 و 12. هل هما متشابهان؟ اختر السبب الصحيح.', '',
   [('Not similar: the perimeters are different.', 'غير متشابهين: المحيطان مختلفان.'), ('Similar by SSS: every ratio of corresponding sides is 3/2.', 'متشابهان بـ SSS: كل نسبة بين الأضلاع المتناظرة تساوي 3/2.'),
    ('Similar by SAS: two sides are given.', 'متشابهان بـ SAS: يوجد ضلعان معطيان.'), ('Cannot be decided without angles.', 'لا يمكن الحكم دون الزوايا.')], 'B',
   'Ordered sides give 6/4 = 9/6 = 12/8 = 3/2, so SSS similarity applies.',
   [S('Write both side lists from shortest to longest so corresponding sides match.', 'رتّب أضلاع كل مثلث من الأقصر إلى الأطول حتى تتناظر الأضلاع.', '4,6,8\\ \\text{and}\\ 6,9,12', 'Corresponding sides must be compared in the same order.', 'يجب مقارنة الأضلاع المتناظرة بالترتيب نفسه.'),
    S('Find the three ratios.', 'احسب النسب الثلاث.', r'\tfrac64=\tfrac96=\tfrac{12}{8}=\tfrac32', 'SSS needs all three ratios equal.', 'SSS يحتاج تساوي النسب الثلاث.'),
    S('All ratios are equal: similar by SSS.', 'كل النسب متساوية: متشابهان بـ SSS.', r'k=\tfrac32', 'No angles are needed when all three sides are proportional.', 'لا نحتاج الزوايا عندما تتناسب الأضلاع الثلاثة.')], None),
 '11G-Q05-cov-sas': ('11G', 'LO05', 'In △PQR, PQ = 3, QR = 5 and ∠Q = 70°. In △XYZ, XY = 6, YZ = 10 and ∠Y = 70°. Which statement is correct?',
   'في △PQR: PQ = 3 و QR = 5 و ∠Q = 70°. وفي △XYZ: XY = 6 و YZ = 10 و ∠Y = 70°. أي عبارة صحيحة؟', '',
   [('△PQR ∼ △XYZ by SAS, scale factor 2.', '△PQR ∼ △XYZ بـ SAS ومعامل التشابه 2.'), ('△PQR ∼ △XYZ by AA.', '△PQR ∼ △XYZ بـ AA.'), ('They are congruent.', 'المثلثان متطابقان.'), ('They are not similar.', 'المثلثان غير متشابهين.')], 'A',
   'PQ/XY = QR/YZ = 1/2 with the included angles Q and Y equal: SAS similarity with factor 2.',
   [S('Compare the sides around the equal angle.', 'قارن الضلعين حول الزاوية المتساوية.', r'\tfrac{XY}{PQ}=\tfrac63=2,\quad\tfrac{YZ}{QR}=\tfrac{10}{5}=2', 'The two ratios must be equal for SAS.', 'يجب أن تتساوى النسبتان لتطبيق SAS.'),
    S('The 70° angles are included between these sides, so SAS applies.', 'الزاويتان 70° محصورتان بين هذين الضلعين، فينطبق SAS.', r'\triangle PQR\sim\triangle XYZ,\ k=2', 'Equal ratios + equal included angle = SAS.', 'تساوي النسبتين + تساوي الزاوية المحصورة = SAS.')], None),
 '11G-Q07-cov-bisector': ('11G', 'LO07', 'Two triangles are similar. Corresponding sides are 6 cm and 9 cm. The angle bisector from a vertex of the smaller triangle is 4 cm. Find the corresponding angle bisector of the larger triangle.',
   'مثلثان متشابهان، فيهما ضلعان متناظران 6 سم و 9 سم. طول منصف زاوية في المثلث الأصغر 4 سم. أوجد طول منصف الزاوية المناظر في المثلث الأكبر.', '',
   [('6 cm', None), ('8.7 cm', None), ('2.7 cm', None), ('7 cm', None)], 'A', 'Corresponding angle bisectors have the same ratio as corresponding sides: 4 × 9/6 = 6 cm.',
   [S('In similar triangles, corresponding angle bisectors are in the same ratio as corresponding sides.', 'في المثلثات المتشابهة، منصفات الزوايا المتناظرة بنسبة الأضلاع المتناظرة نفسها.', r'\tfrac{b}{4}=\tfrac96', 'Every corresponding length scales by the same factor.', 'كل الأطوال المتناظرة تتغير بالمعامل نفسه.'),
    S('Solve.', 'حل.', r'b=4\cdot\tfrac32=6\ \text{cm}', 'Multiply by the scale factor 9/6 = 3/2.', 'اضرب في معامل التشابه 9/6 = 3/2.')], None),
 '11G-Q07-cov-median': ('11G', 'LO07', 'Two triangles are similar with corresponding sides 8 m and 12 m. A median of the smaller triangle is 5 m. Find the corresponding median of the larger triangle.',
   'مثلثان متشابهان فيهما ضلعان متناظران 8 م و 12 م. طول متوسط في المثلث الأصغر 5 م. أوجد طول المتوسط المناظر في المثلث الأكبر.', '',
   [('7.5 m', None), ('9 m', None), ('3.3 m', None), ('10 m', None)], 'A', 'Medians scale like the sides: 5 × 12/8 = 7.5 m.',
   [S('Corresponding medians have the same ratio as corresponding sides.', 'المتوسطات المتناظرة بنسبة الأضلاع المتناظرة.', r'\tfrac{m}{5}=\tfrac{12}{8}', 'Medians, altitudes and bisectors all scale by the same factor.', 'المتوسطات والارتفاعات والمنصفات كلها تتغير بالمعامل نفسه.'),
    S('Solve.', 'حل.', r'm=5\cdot1.5=7.5\ \text{m}', 'Multiply by the scale factor 12/8 = 1.5.', 'اضرب في معامل التشابه 12/8 = 1.5.')], None),
 '11A-Q14-cov-shape': ('11A', 'LO14', 'A data set has mean 52 and median 45. Which statement best describes the shape of the distribution?',
   'مجموعة بيانات وسطها الحسابي 52 ووسيطها 45. أي عبارة تصف شكل التوزيع بشكل أفضل؟', '',
   [('Skewed right: a few large values pull the mean above the median.', 'ملتوٍ لليمين: قيم كبيرة قليلة تسحب الوسط فوق الوسيط.'), ('Skewed left: the mean is above the median.', 'ملتوٍ لليسار: الوسط فوق الوسيط.'),
    ('Symmetric: mean and median are always equal.', 'متماثل: الوسط والوسيط متساويان دائماً.'), ('Uniform: every value is equally common.', 'منتظم: كل القيم متكررة بالقدر نفسه.')], 'A',
   'Mean > median means a tail of large values on the right: skewed right.',
   [S('Compare the mean with the median.', 'قارن الوسط بالوسيط.', '52>45', 'The mean is pulled toward a tail; the median is not.', 'الوسط ينسحب نحو الذيل، أما الوسيط فلا.'),
    S('The mean is larger, so the long tail is on the right: skewed right.', 'الوسط أكبر، فالذيل الطويل في اليمين: ملتوٍ لليمين.', r'\text{mean}>\text{median}\Rightarrow\text{skewed right}', 'Mean ≈ median → symmetric; mean < median → skewed left.', 'الوسط ≈ الوسيط ← متماثل؛ الوسط < الوسيط ← ملتوٍ لليسار.')], None),
 '11A-Q14-cov-center': ('11A', 'LO14', 'A distribution of house prices is strongly skewed right. Which measures of center and spread describe it best?',
   'توزيع أسعار منازل ملتوٍ لليمين بشدة. أي مقياسين للنزعة المركزية والتشتت يصفانه بشكل أفضل؟', '',
   [('Median and interquartile range', 'الوسيط والمدى الربيعي'), ('Mean and standard deviation', 'الوسط والانحراف المعياري'), ('Mean and range', 'الوسط والمدى'), ('Mode and standard deviation', 'المنوال والانحراف المعياري')], 'A',
   'Skewed data: use measures that resist extreme values, the median and the IQR.',
   [S('Skewed data contain extreme values in one tail.', 'البيانات الملتوية تحتوي قيماً متطرفة في أحد الذيلين.', r'\text{skewed right}', 'Extreme values pull the mean and inflate the standard deviation.', 'القيم المتطرفة تسحب الوسط وتكبّر الانحراف المعياري.'),
    S('Choose resistant measures: the median (center) and the interquartile range (spread).', 'اختر مقاييس لا تتأثر بالقيم المتطرفة: الوسيط (المركز) والمدى الربيعي (التشتت).', r'\text{median},\ \text{IQR}', 'For symmetric data the mean and standard deviation are fine.', 'للبيانات المتماثلة يصلح الوسط والانحراف المعياري.')], None),
 '11A-Q21-cov-eval': ('11A', 'LO21', 'Evaluate the expression exactly.', 'احسب قيمة العبارة بدقة.', r'\ln\left(e^{5}\right)+e^{\ln 3}',
   [('8', None), ('15', None), ('5\\ln 3', None), ('e^{8}', None)], 'A', 'ln and e^x undo each other: ln(e⁵) = 5 and e^(ln 3) = 3, so the sum is 8.',
   [S('ln and eˣ are inverse functions, so they cancel each other.', 'الدالتان ln و eˣ عكسيتان، فكل منهما تلغي الأخرى.', r'\ln(e^{a})=a,\quad e^{\ln b}=b', 'Inverse functions undo each other.', 'الدوال العكسية تلغي بعضها.'),
    S('Apply to each term and add.', 'طبّق على كل حد واجمع.', r'5+3=8', 'No calculator is needed for exact cancellations.', 'لا نحتاج الحاسبة في الإلغاء الدقيق.')], None),
 '11A-Q21-cov-solve': ('11A', 'LO21', 'Solve the equation. Round to four decimal places.', 'حل المعادلة. قرّب لأربع منازل عشرية.', r'e^{x}=7',
   [('1.9459', None), ('0.8451', None), ('1096.6332', None), ('2.6458', None)], 'A', 'Take ln of both sides: x = ln 7 ≈ 1.9459.',
   [S('Take the natural logarithm of both sides.', 'خذ اللوغاريتم الطبيعي للطرفين.', r'\ln(e^{x})=\ln 7\Rightarrow x=\ln 7', 'ln undoes e^x, which isolates x.', 'ln يلغي eˣ فيعزل x.'),
    S('Use the calculator (ln key) and round to four decimal places.', 'استخدم الحاسبة (زر ln) وقرّب لأربع منازل.', r'x=\ln 7\approx1.9459', 'log 7 ≈ 0.8451 is the common log, a different function.', 'log 7 ≈ 0.8451 هو اللوغاريتم العشري، وهو دالة مختلفة.')], ['ln(7)']),
 '11A-Q22-cov-double': ('11A', 'LO22', 'A population of 500 grows continuously at 4% per year. How many years until it doubles? Round to the nearest tenth.',
   'مجتمع عدده 500 ينمو نمواً متصلاً بمعدل 4% سنوياً. بعد كم سنة يتضاعف؟ قرّب لأقرب عُشر.', r'P(t)=500e^{0.04t}',
   [('17.3 years', 'بعد 17.3 سنة'), ('25.0 years', 'بعد 25.0 سنة'), ('12.5 years', 'بعد 12.5 سنة'), ('34.7 years', 'بعد 34.7 سنة')], 'A', 'Double means 1000 = 500e^{0.04t}, so t = ln 2 / 0.04 ≈ 17.3 years.',
   [S('Doubling means the population becomes 2 × 500 = 1000.', 'التضاعف يعني أن المجتمع يصبح 2 × 500 = 1000.', r'1000=500e^{0.04t}', 'Write the condition as an equation first.', 'اكتب الشرط كمعادلة أولاً.'),
    S('Divide by 500, then take ln of both sides.', 'اقسم على 500 ثم خذ ln للطرفين.', r'2=e^{0.04t}\Rightarrow\ln 2=0.04t', 'ln brings the exponent down.', 'ln يُنزل الأس.'),
    S('Divide by 0.04 and round.', 'اقسم على 0.04 وقرّب.', r't=\tfrac{\ln 2}{0.04}\approx17.3', 'The doubling time does not depend on the starting 500.', 'زمن التضاعف لا يعتمد على العدد الابتدائي 500.')], ['ln(2)/0.04']),
 '11A-Q22-cov-rate': ('11A', 'LO22', 'A culture grows from 200 to 800 bacteria in 6 hours. Find the growth rate k. Round to four decimal places.',
   'تنمو مزرعة بكتيريا من 200 إلى 800 خلال 6 ساعات. أوجد معدل النمو k. قرّب لأربع منازل عشرية.', r'N(t)=200e^{kt}',
   [('0.2310', None), ('0.6667', None), ('0.1155', None), ('1.3863', None)], 'A', '800 = 200e^{6k} gives e^{6k} = 4, so k = ln 4 / 6 ≈ 0.2310.',
   [S('Substitute t = 6 and N = 800.', 'عوّض t = 6 و N = 800.', r'800=200e^{6k}', 'The known point gives one equation in k.', 'النقطة المعلومة تعطي معادلة واحدة في k.'),
    S('Divide by 200 and take ln.', 'اقسم على 200 وخذ ln.', r'4=e^{6k}\Rightarrow\ln4=6k', 'Isolate the exponential before using ln.', 'اعزل الدالة الأسية قبل استخدام ln.'),
    S('Divide by 6 and round.', 'اقسم على 6 وقرّب.', r'k=\tfrac{\ln4}{6}\approx0.2310', 'A positive k means growth; a negative k would mean decay.', 'k الموجبة تعني نمواً والسالبة تعني اضمحلالاً.')], ['ln(4)/6']),
 '12G-Q25-cov-inv90': ('12G', 'LO25', 'Heights are normally distributed with mean 170 cm and standard deviation 8 cm. Find the height below which 90% of people fall. Use z = 1.28 and round to the nearest tenth.',
   'الأطوال موزعة توزيعاً طبيعياً بوسط 170 سم وانحراف معياري 8 سم. أوجد الطول الذي يقل عنه 90% من الناس. استخدم z = 1.28 وقرّب لأقرب عُشر.', '',
   [('180.2 cm', None), ('159.8 cm', None), ('178.0 cm', None), ('171.3 cm', None)], 'A', 'Inverse normal: x = μ + zσ = 170 + 1.28 × 8 = 180.24 ≈ 180.2 cm.',
   [S('90% below means the z-value with left area 0.90: z = 1.28 (given).', 'تحته 90% يعني قيمة z التي مساحتها اليسرى 0.90: z = 1.28 (معطاة).', r'z=1.28', 'Inverse problems start from an area and go back to x.', 'المسائل العكسية تبدأ من المساحة وترجع إلى x.'),
    S('Undo the z-formula: x = μ + zσ.', 'اعكس قانون z: x = μ + zσ.', r'x=170+1.28(8)\approx180.2', 'z counts standard deviations above the mean.', 'z تعدّ الانحرافات المعيارية فوق الوسط.')], ['170+1.28*8']),
 '12G-Q25-cov-inv5': ('12G', 'LO25', 'Test scores are normal with mean 60 and standard deviation 10. Find the score that cuts off the lowest 5%. Use z = −1.645 and round to the nearest tenth.',
   'درجات اختبار موزعة طبيعياً بوسط 60 وانحراف معياري 10. أوجد الدرجة التي تفصل أدنى 5%. استخدم z = −1.645 وقرّب لأقرب عُشر.', '',
   [('43.6', None), ('76.5', None), ('58.4', None), ('50.0', None)], 'A', 'x = μ + zσ = 60 − 1.645 × 10 = 43.55 ≈ 43.6.',
   [S('The lowest 5% is a left area of 0.05, so z is negative: z = −1.645.', 'أدنى 5% مساحة يسرى 0.05، فتكون z سالبة: z = −1.645.', r'z=-1.645', 'Below the mean, z must be negative.', 'تحت الوسط تكون z سالبة.'),
    S('x = μ + zσ.', 'x = μ + zσ.', r'x=60+(-1.645)(10)\approx43.6', '76.5 uses +1.645 by mistake (that is the top 5%).', '76.5 تستخدم +1.645 خطأً (أعلى 5%).')], ['60-1.645*10']),
 '12G-Q09-cov-eval1': ('12G', 'LO09', 'Evaluate the polynomial function at the given value.', 'احسب قيمة الدالة كثيرة الحدود عند القيمة المعطاة.', r'f(x)=2x^3-x^2+4,\quad f(-2)',
   [('-16', None), ('16', None), ('-8', None), ('0', None)], 'A', 'f(−2) = 2(−8) − 4 + 4 = −16.',
   [S('Substitute x = −2, keeping brackets around the negative number.', 'عوّض x = −2 مع إبقاء الأقواس حول العدد السالب.', r'f(-2)=2(-2)^3-(-2)^2+4', 'Brackets keep the sign correct when you raise to a power.', 'الأقواس تحفظ الإشارة عند الرفع لقوة.'),
    S('Powers first, then multiply, then add.', 'الأسس أولاً ثم الضرب ثم الجمع.', r'=2(-8)-4+4=-16', '(−2)² = 4 but −2² would wrongly be −4.', '(−2)² = 4 بينما −2² تعطي −4 خطأً.')], None),
 '12G-Q09-cov-eval2': ('12G', 'LO09', 'Evaluate the polynomial function at the given value.', 'احسب قيمة الدالة كثيرة الحدود عند القيمة المعطاة.', r'f(x)=x^4-3x^2+x,\quad f(2)',
   [('6', None), ('10', None), ('2', None), ('-2', None)], 'A', 'f(2) = 16 − 12 + 2 = 6.',
   [S('Substitute x = 2.', 'عوّض x = 2.', r'f(2)=2^4-3(2)^2+2', 'Replacing x by the given number turns the function into arithmetic.', 'استبدال x بالعدد المعطى يحوّل الدالة إلى حساب.'), S('Evaluate the powers, multiply, then add/subtract.', 'احسب الأسس ثم الضرب ثم الجمع والطرح.', r'=16-12+2=6', 'Order of operations matters.', 'ترتيب العمليات مهم.')], None),
 '12A-Q06-cov-comp1': ('12A', 'LO06', 'Let f(x) = √x and g(x) = x² + 5. Where is f(g(x)) continuous?', 'لتكن f(x) = √x و g(x) = x² + 5. أين تكون f(g(x)) متصلة؟', r'f(g(x))=\sqrt{x^2+5}',
   [('\\mathbb{R}', None), ('x\\ge0', None), ('x\\ge-5', None), ('x\\ne0', None)], 'A', 'g is continuous everywhere and x² + 5 ≥ 5 > 0, so √(x² + 5) is defined and continuous for all real x.',
   [S('A composition f(g(x)) is continuous where g is continuous and f is continuous at g(x).', 'التركيب f(g(x)) متصل حيث g متصلة و f متصلة عند g(x).', r'f\circ g\ \text{continuous where } g \text{ and } f(g(x)) \text{ are}', 'Check the inside function first, then the outside function at its outputs.', 'افحص الدالة الداخلية أولاً ثم الخارجية عند مخرجاتها.'),
    S('g(x) = x² + 5 is a polynomial: continuous everywhere, and its values are always ≥ 5.', 'g(x) = x² + 5 كثيرة حدود: متصلة في كل مكان وقيمها دائماً ≥ 5.', r'x^2+5\ge5>0', 'Polynomials have no breaks; knowing the outputs tells us what f receives.', 'كثيرات الحدود لا انقطاع فيها؛ ومعرفة المخرجات تخبرنا بما تستقبله f.'),
    S('√ is continuous for inputs ≥ 0, and every input here is ≥ 5, so f(g(x)) is continuous on ℝ.', 'الجذر متصل للمدخلات ≥ 0، وكل المدخلات هنا ≥ 5، إذن f(g(x)) متصلة على ℝ.', r'\mathbb{R}', 'x ≥ 0 is the domain of √x alone, not of the composition.', 'x ≥ 0 هو مجال √x وحدها وليس مجال التركيب.')], None),
 '12A-Q06-cov-comp2': ('12A', 'LO06', 'Let f(x) = 1/x and g(x) = x − 3. Where is f(g(x)) continuous?', 'لتكن f(x) = 1/x و g(x) = x − 3. أين تكون f(g(x)) متصلة؟', r'f(g(x))=\frac{1}{x-3}',
   [('x\\ne3', None), ('x\\ne0', None), ('x\\ne-3', None), ('\\mathbb{R}', None)], 'A', 'f is discontinuous only where its input is 0, i.e. g(x) = x − 3 = 0, so f(g(x)) is continuous for x ≠ 3.',
   [S('f(x) = 1/x is continuous except where its input is 0.', 'f(x) = 1/x متصلة إلا حيث يكون مدخلها صفراً.', r'\text{input}\ne0', 'Division by zero is the only break of 1/x.', 'القسمة على صفر هي الانقطاع الوحيد للدالة 1/x.'),
    S('The input is g(x) = x − 3; set it equal to 0.', 'المدخل هو g(x) = x − 3؛ ساوِه بالصفر.', r'x-3=0\Rightarrow x=3', 'The break comes from where g sends x to the bad input of f.', 'الانقطاع يأتي من حيث ترسل g العدد x إلى المدخل الممنوع في f.'),
    S('So f(g(x)) is continuous for every x except 3.', 'إذن f(g(x)) متصلة لكل x عدا 3.', r'x\ne3', 'Every other x gives a nonzero input, so there is no break.', 'كل قيمة أخرى لـ x تعطي مدخلاً غير صفري، فلا يوجد انقطاع.')], None),
}


def main():
    # verify computed answers
    assert abs(4 * 9 / 6 - 6) < 1e-12 and abs(5 * 12 / 8 - 7.5) < 1e-12 and math.log(7) - 1.9459 < 5e-5 and round(math.log(2) / 0.04, 1) == 17.3
    from decimal import Decimal, ROUND_HALF_UP
    half_up = lambda v, q: Decimal(str(v)).quantize(Decimal(q), rounding=ROUND_HALF_UP)
    assert round(math.log(4) / 6, 4) == 0.2310 and half_up(Decimal('170') + Decimal('1.28') * 8, '0.1') == Decimal('180.2') and half_up(Decimal('60') - Decimal('1.645') * 10, '0.1') == Decimal('43.6')
    assert 2 * (-2) ** 3 - (-2) ** 2 + 4 == -16 and 2 ** 4 - 3 * 2 ** 2 + 2 == 6
    tr = json.loads((ROOT / 'public/data/study/translations-ar.json').read_text())
    sup = json.loads((ROOT / 'public/data/study/calculator-support.json').read_text())
    banks = {}
    for qid, (c, lo, ins, ins_ar, m, opts, key, expl, steps, calc) in Q.items():
        b = banks.setdefault(c, json.loads((ROOT / f'public/data/study/{c}.json').read_text()))
        b['questions'] = [q for q in b['questions'] if q['id'] != qid]
        L = next(l for l in b['learning_outcomes'] if l['id'] == lo)
        L['question_ids'] = [i for i in L['question_ids'] if i != qid]
        options = [{'id': 'ABCD'[k], 'text': o, 'math_latex': (r'\text{' + o + '}') if a else o, 'misconception': None} for k, (o, a) in enumerate(opts)]
        for k, (o, a) in enumerate(opts):
            if a: tr['option'][re.sub(r'-?\d+(\.\d+)?', '#', o)] = re.sub(r'-?\d+(\.\d+)?', '#', a) if len(re.findall(r'-?\d+(?:\.\d+)?', o)) == len(re.findall(r'-?\d+(?:\.\d+)?', a)) else a
        tr['instruction'][re.sub(r'-?\d+(\.\d+)?', '#', ins)] = re.sub(r'-?\d+(\.\d+)?', '#', ins_ar) if len(re.findall(r'-?\d+(?:\.\d+)?', ins)) == len(re.findall(r'-?\d+(?:\.\d+)?', ins_ar)) else ins_ar
        ko = next(o for o in options if o['id'] == key)
        final = {'text': f'So the answer is option {key}.', 'ar': f'إذن الإجابة هي الخيار {key}.', 'latex': ko['math_latex'] or '', 'why': 'Always compare your result with every option.', 'why_ar': 'قارن ناتجك دائماً مع كل الخيارات.'}
        q = {'id': qid, 'learning_outcome_id': lo, 'type': 'mcq', 'display_number': f"{int(lo[2:])}.{len(L['question_ids']) + 1}", 'instruction': ins, 'stem': (ins + ' ' + m).strip(), 'math_latex': m,
             'marks': None, 'diagram_asset_ids': [], 'source': {'printed_page': None, 'pdf_page': None, 'exercise': None, 'bank_source': None},
             'grade': int(c[:2]), 'track': 'advanced' if c.endswith('A') else 'general', 'source_kind': 'authored_lo_variant', 'family_id': qid, 'difficulty': 'standard', 'skill_tags': [L['title']],
             'reference_kind': 'review', 'presentation': 'normalized', 'figure_in_image': False, 'options': options,
             'answer': {'correct_option_id': key, 'correct_option_text': ko['math_latex'] or ko['text'], 'explanation': expl, 'steps': steps + [final], 'steps_verified': True},
             'coverage_note': 'Added 2026-11-12 so every part of the outcome description is practised (scripts/audit-lo-coverage.py).'}
        if L['question_type'] == 'frq':   # keep the EOT question type of the outcome
            for k in ('options',): q.pop(k)
            q['type'] = 'frq'; ans = q.pop('answer')
            q['parts'] = [{'id': 'a', 'prompt': 'Show all steps and check your answer.', 'math_latex': '', 'marks': None, 'workspace': {'height_mm': 40},
                           'answer': {'model_answer_and_marking': expl, 'math_latex': '', 'steps': steps, 'steps_verified': True}, 'blanks': {'lines': FRQ_BLANKS[qid]}}]
        b['questions'].append(q); L['question_ids'].append(qid); L['question_count'] = len(L['question_ids'])
        if 'booklet_question_ids' in L and qid not in L['booklet_question_ids']: L['booklet_question_ids'].append(qid)
        g = {'outcome': lo, 'outcome_title': L['title'], 'source_ids': ['reviewed-bank', 'upstream-modes'], 'tables': [],
             'solutions': [{'part': 'Answer', 'math': (q['answer']['correct_option_text'] if 'answer' in q else ''), 'text': expl, 'answer_text': ''}],
             'interpret': 'Write the method, the substitution and the final answer with units. Calculator output alone does not justify the answer.'}
        if calc:
            ops = []
            for e in calc:
                op = cp.bs.operation(e, 'Evaluate this expression from the worked solution, then round as the question asks.')
                op['keys'] = ['AC'] + cp.bs.input_keys(op['input']) + ['EQ']; op['key_labels'] = [cp.bs.KEY_LABELS.get(k, k) for k in op['keys']]; ops.append(op)
            g.update(role='evaluate', use_calculator=True, operations=ops, prepare='Set up the equation by hand, then evaluate the final expression on the calculator and round as asked.',
                     setup=['MENU → Calculate. Use the ln key for natural logarithms and keep full precision until the final rounding.'])
        else:
            g.update(role='by_hand', use_calculator=False, operations=[], prepare=cp.REASON['hand'][0], prepare_ar=cp.REASON['hand'][1], setup=[])
        sup['classes'][c]['questions'][qid] = g
    for c, b in banks.items():
        for q in b['questions']:
            if q.get('coverage_note'):
                for st in (q.get('answer') or {}).get('steps', []) + [x for p in q.get('parts', []) for x in p['answer']['steps']]:
                    assert st['latex'] and st['why'], (q['id'], st['text'])
        b['question_count'] = len(b['questions']); b['mcq_count'] = sum(q['type'] == 'mcq' for q in b['questions']); b['frq_count'] = sum(q['type'] == 'frq' for q in b['questions'])
        print(c, b['question_count'])
        if WRITE: (ROOT / f'public/data/study/{c}.json').write_text(json.dumps(b, ensure_ascii=False, separators=(',', ':')))
    if WRITE:
        (ROOT / 'public/data/study/translations-ar.json').write_text(json.dumps(tr, ensure_ascii=False, indent=1))
        (ROOT / 'public/data/study/calculator-support.json').write_text(json.dumps(sup, ensure_ascii=False, indent=2) + '\n')
    print(len(Q), 'questions')


if __name__ == '__main__':
    main()
