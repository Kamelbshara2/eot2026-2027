"""Hand-read step solutions for Grade 9/10 questions whose data is in a figure or in words (used by steps-grade9-10.py).
Every number here was read from the question/figure and checked against the key during the 2026-11-11 audit
(AUDIT_2026-11-11.md). Each step: text (simple English), ar (simple Arabic), latex, why / why_ar (why this step comes now)."""
import math


def S(text, ar, latex='', why='', why_ar=''):
    d = {'text': text, 'ar': ar, 'latex': latex}
    if why: d['why'] = why; d['why_ar'] = why_ar
    return d


r1 = lambda v: f'{v:.1f}'
deg = lambda v: math.degrees(v)
sin = lambda a: math.sin(math.radians(a)); cos = lambda a: math.cos(math.radians(a)); tan = lambda a: math.tan(math.radians(a))

# ---------- words <-> symbols ----------
KEYWORDS = S('Underline the key words: sum → +, difference → −, product/times → ×, quotient/divided by → ÷.', 'ضع خطاً تحت الكلمات المفتاحية: مجموع ← +، فرق ← −، حاصل ضرب ← ×، ناتج قسمة/مقسوم على ← ÷.', '',
             'Each key word tells you which operation to write.', 'كل كلمة مفتاحية تحدد العملية التي نكتبها.')


def words(answer, grouping_en, grouping_ar):
    return [KEYWORDS,
            S(grouping_en, grouping_ar, '', '"The sum of A and B" is one quantity, so it goes in brackets (or above a fraction bar) before the next operation acts on it.',
              '"مجموع A و B" كمية واحدة، فنضعها بين قوسين (أو فوق خط الكسر) قبل أن تؤثر عليها العملية التالية.'),
            S('Write the expression.', 'اكتب العبارة.', answer, 'Read your expression back in words to check it says the same thing.', 'اقرأ عبارتك بالكلمات للتأكد من أنها تقول المعنى نفسه.')]


def verbal(expr, reading_en, reading_ar):
    return [S('Identify the operations and their order in the expression (powers first, then × and ÷, then + and −).', 'حدّد العمليات وترتيبها في العبارة (الأسس أولاً، ثم × و ÷، ثم + و −).', expr,
              'Words must describe the same order of operations, otherwise they describe a different expression.', 'يجب أن تصف الكلمات ترتيب العمليات نفسه، وإلا وصفت عبارة مختلفة.'),
            S(reading_en, reading_ar, '', 'Power words: squared = ², cubed = ³, fourth power = ⁴. "Twice a" = 2a.', 'كلمات الأسس: تربيع = ²، تكعيب = ³، القوة الرابعة = ⁴. "مثلا a" = 2a.')]


def sentence(answer, map_en, map_ar):
    return [KEYWORDS, S(map_en, map_ar, '', '"is", "is the same as", "equals" become the = sign.', 'الكلمات "يساوي"، "هو نفسه" تصبح إشارة =.'),
            S('Write the equation.', 'اكتب المعادلة.', answer, 'Check: read the equation back as a sentence.', 'تحقق: اقرأ المعادلة كجملة.')]


def prop(name_en, name_ar, rule, latex):
    return [S(f'Compare the two sides of the statement: {name_en.lower()} says {rule}.', f'قارن طرفي العبارة: خاصية {name_ar} تقول {rule}.', latex,
              'Reflexive: a = a. Symmetric: if a = b then b = a. Transitive: if a = b and b = c then a = c.', 'الانعكاس: a = a. التماثل: إذا a = b فإن b = a. التعدي: إذا a = b و b = c فإن a = c.'),
            S(f'So the property is the {name_en}.', f'إذن الخاصية هي خاصية {name_ar}.', '', 'Match the pattern, not the numbers.', 'طابق النمط لا الأعداد.')]


def distrib(n, base, d, sign, value):
    op = '+' if sign > 0 else '-'
    return [S(f'Write the awkward number as a friendly number {op} a small number: {base} {op} {d}.', f'اكتب العدد الصعب كعدد سهل {op} عدد صغير: {base} {op} {d}.', rf'{n}({base}{op}{d})',
              'Numbers like 100 or 50 are easy to multiply mentally.', 'الأعداد مثل 100 و 50 سهلة الضرب ذهنياً.'),
            S('Distribute: multiply the outside number by BOTH parts.', 'وزّع: اضرب العدد الخارجي في الجزأين كليهما.', rf'{n}({base}){op}{n}({d})={n * base}{op}{n * d}',
              'a(b ± c) = ab ± ac; forgetting to multiply the small part is the usual mistake.', 'a(b ± c) = ab ± ac؛ نسيان ضرب الجزء الصغير خطأ شائع.'),
            S('Add or subtract.', 'اجمع أو اطرح.', f'={value}', '', '')]


def line_graph(p1, p2, m, b, eq):
    return [S(f'Read two clear points from the graph: {p1} and {p2}.', f'اقرأ نقطتين واضحتين من الرسم: {p1} و {p2}.', '', 'Points on grid corners give exact values.', 'النقاط عند تقاطعات الشبكة تعطي قيماً دقيقة.'),
            S('Find the slope: rise ÷ run.', 'أوجد الميل: الارتفاع ÷ المسافة الأفقية.', rf'm={m}', 'Going right, up is positive rise and down is negative rise.', 'عند التحرك يميناً: الصعود ارتفاع موجب والهبوط سالب.'),
            S('Read the y-intercept b (where the line crosses the y-axis).', 'اقرأ المقطع الصادي b (حيث يقطع المستقيم محور y).', rf'b={b}', 'b is the y-value when x = 0.', 'b هو قيمة y عندما x = 0.'),
            S('Write y = mx + b.', 'اكتب y = mx + b.', eq, '', '')]


def ineq_graph(pt, closed, right, ans):
    return [S(f'Look at the circle at {pt}: it is ' + ('filled (closed), so the endpoint is included: use ≤ or ≥.' if closed else 'empty (open), so the endpoint is not included: use < or >.'),
              f'انظر إلى الدائرة عند {pt}: إنها ' + ('مغلقة (مظللة)، أي أن نقطة الحد مشمولة: نستخدم ≤ أو ≥.' if closed else 'مفتوحة، أي أن نقطة الحد غير مشمولة: نستخدم < أو >.'), '',
              'The circle type decides whether the inequality includes "equal to".', 'نوع الدائرة يحدد هل تشمل المتباينة "يساوي".'),
            S('The shading goes ' + ('right: numbers greater than the endpoint.' if right else 'left: numbers less than the endpoint.'), 'التظليل ' + ('نحو اليمين: أعداد أكبر من نقطة الحد.' if right else 'نحو اليسار: أعداد أصغر من نقطة الحد.'),
              ans, 'Right on a number line means larger.', 'اليمين على خط الأعداد يعني أكبر.')]


def abs_graph(h, k, ans):
    return [S(f'Find the vertex (the sharp corner) of the V: ({h}, {k}).', f'أوجد رأس الشكل V (الزاوية الحادة): ({h}, {k}).', '', 'For f(x) = |x − h| + k the vertex is (h, k).', 'في الدالة f(x) = |x − h| + k يكون الرأس (h, k).'),
            S('The V opens up with slopes ±1, so a = 1. Put h inside with the opposite sign and k outside.', 'الشكل V مفتوح لأعلى بميل ±1، إذن a = 1. ضع h داخل القيمة المطلقة بإشارة معاكسة و k خارجها.',
              ans, 'Moving right by h means x − h inside; moving up by k means + k outside.', 'الانتقال يميناً بمقدار h يعني x − h بالداخل، والانتقال لأعلى بمقدار k يعني + k بالخارج.')]


def angles(n, eq, x, values):
    total = (n - 2) * 180
    return [S(f'The polygon has {n} sides, so its interior angles add to (n − 2)·180° = {total}°.', f'للمضلع {n} أضلاع، إذن مجموع زواياه الداخلية (n − 2)·180° = {total}°.', rf'({n}-2)\cdot180^\circ={total}^\circ',
              'Any polygon splits into n − 2 triangles of 180°.', 'أي مضلع ينقسم إلى n − 2 مثلثات كل منها 180°.'),
            S('Add all the angle expressions and set the sum equal to the total.', 'اجمع كل تعابير الزوايا وساوِ المجموع بالمجموع الكلي.', eq, 'This gives one equation in x.', 'هذا يعطي معادلة واحدة في x.'),
            S('Solve for x.', 'حل لإيجاد x.', rf'x={x}', '', ''),
            S('Substitute x into each expression, in the stated vertex order.', 'عوّض x في كل تعبير بترتيب الرؤوس المذكور.', values, 'Check: the angles should add to the total.', 'تحقق: يجب أن يكون مجموع الزوايا هو المجموع الكلي.')]


def simple(*rows):
    return [S(*r) for r in rows]


def pyth(a, b, c, which):
    return [S('In a right triangle: (leg)² + (leg)² = (hypotenuse)². The hypotenuse is opposite the right angle.', 'في المثلث القائم: (ضلع)² + (ضلع)² = (الوتر)². الوتر يقابل الزاوية القائمة.', 'a^2+b^2=c^2',
              'Decide first which side is the hypotenuse: it changes the equation.', 'حدّد الوتر أولاً لأنه يغيّر المعادلة.'),
            S('Substitute the known sides.', 'عوّض الأضلاع المعلومة.', which, '', ''),
            S('Recognise the Pythagorean triple (or take the square root).', 'تعرّف على ثلاثية فيثاغورس (أو خذ الجذر).', rf'{a},\ {b},\ {c}', 'Common triples: 3-4-5, 5-12-13, 8-15-17, 7-24-25 and their multiples.', 'الثلاثيات الشائعة: 3-4-5، 5-12-13، 8-15-17، 7-24-25 ومضاعفاتها.')]


def trig_area(a, b, C, label):
    A = 0.5 * a * b * sin(C)
    return [S(f'Find two sides and the angle BETWEEN them: {a} and {b} with included angle {C}°.', f'حدّد ضلعين والزاوية المحصورة بينهما: {a} و {b} والزاوية {C}°.', label,
              'The formula needs the included angle (between the two sides).', 'القانون يحتاج الزاوية المحصورة بين الضلعين.'),
            S('Use Area = ½·a·b·sin C.', 'استخدم المساحة = ½·a·b·sin C.', rf'A=\tfrac12({a})({b})\sin{C}^\circ', 'b·sin C is the height of the triangle, so this is ½·base·height.', 'b·sin C هو ارتفاع المثلث، فالقانون هو ½ × القاعدة × الارتفاع.'),
            S('Calculate (calculator in degree mode) and round to the nearest tenth.', 'احسب (الحاسبة على وضع الدرجات) وقرّب لأقرب عُشر.', rf'A\approx{A:.1f}', 'Round only at the end.', 'نقرّب في النهاية فقط.')]


def tri_angle_C(A, B):
    return S(f'Find the third angle first: 180° − {A}° − {B}° = {180 - A - B}°.', f'أوجد الزاوية الثالثة أولاً: 180° − {A}° − {B}° = {180 - A - B}°.', rf'C={180 - A - B}^\circ', 'The angle between the two known sides is needed.', 'نحتاج الزاوية المحصورة بين الضلعين المعلومين.')


MANUAL = {
    # ---------------- 9 General ----------------
    'G9G-BOOK-Q01-MCQ-01': words(r'\frac{3+7}{2}', '"The sum of 3 and 7" comes first, then it is divided by 2: put 3 + 7 on top.', '"مجموع 3 و 7" يأتي أولاً ثم يُقسم على 2: ضع 3 + 7 في البسط.'),
    'G9G-BOOK-Q01-MCQ-02': words(r'\frac{6-2}{4}', '"The difference of 6 and 2" is found first, then divided by 4.', '"الفرق بين 6 و 2" يُحسب أولاً ثم يُقسم على 4.'),
    'G9G-BOOK-Q01-MCQ-03': words(r'3(4+9)', '"The product of 3 and the sum": 3 multiplies the whole sum, so the sum goes in brackets.', '"حاصل ضرب 3 في المجموع": العدد 3 يضرب المجموع كله، فنضع المجموع بين قوسين.'),
    'G9G-BOOK-Q01-MCQ-04': words(r'\frac{18}{2+7}', '18 is divided by the whole sum, so 2 + 7 goes in the denominator.', 'العدد 18 مقسوم على المجموع كله، فنضع 2 + 7 في المقام.'),
    '9G-Q01-p9-exercise-15': words(r'\frac{10}{4\cdot5}', 'Ten is divided by the whole product, so 4·5 is the denominator.', 'العشرة مقسومة على حاصل الضرب كله، فيكون 4·5 في المقام.'),
    '9G-Q01-p9-exercise-16': words(r'(11-4)5', 'The comma shows the difference 11 − 4 is finished first, then multiplied by 5.', 'الفاصلة تبيّن أن الفرق 11 − 4 يُحسب أولاً ثم يُضرب في 5.'),
    '9G-Q01-p9-exercise-17': words(r'\frac{1+2}{20}', 'The comma shows the sum 1 + 2 is finished first, then divided by 20.', 'الفاصلة تبيّن أن المجموع 1 + 2 يُحسب أولاً ثم يُقسم على 20.'),
    '9G-Q01-p9-exercise-18': words(r'(2+4+6)8', 'The comma shows the sum of the three numbers is finished first, then multiplied by 8.', 'الفاصلة تبيّن أن مجموع الأعداد الثلاثة يُحسب أولاً ثم يُضرب في 8.'),
    '9G-Q01-p9-exercise-19': words(r'\frac{12+16}{3+4}', 'Each sum is one quantity: the first sum on top, the second sum on the bottom.', 'كل مجموع كمية واحدة: المجموع الأول في البسط والثاني في المقام.'),
    '9G-Q01-p9-exercise-20': words(r'\frac{22-6}{5+3}', 'The difference on top, the sum on the bottom.', 'الفرق في البسط والمجموع في المقام.'),
    '9G-Q01-p9-exercise-21': words(r'\frac{36+14}{2\cdot5}', 'The sum on top, the product on the bottom.', 'المجموع في البسط وحاصل الضرب في المقام.'),
    'G9G-BOOK-Q05-MCQ-01': prop('Symmetric Property', 'التماثل', 'the two sides can swap places', r'4+17=21\Rightarrow21=4+17'),
    'G9G-BOOK-Q05-MCQ-02': prop('Reflexive Property', 'الانعكاس', 'any quantity equals itself', r'x+3=x+3'),
    'G9G-BOOK-Q05-MCQ-03': prop('Symmetric Property', 'التماثل', 'the two sides can swap places', r'16=9+7\Rightarrow9+7=16'),
    'G9G-BOOK-Q05-MCQ-04': prop('Transitive Property', 'التعدي', 'two quantities equal to the same middle quantity are equal', r'6+2=4+4,\ 4+4=8\Rightarrow6+2=8'),
    '9G-Q05-p31-exercise-5': prop('Symmetric Property', 'التماثل', 'swap the two sides exactly', r'23+14=37\Rightarrow37=23+14'),
    '9G-Q05-p31-exercise-6': prop('Transitive Property', 'التعدي', 'a + 5 equals both b + 3 and 12, so b + 3 = 12', r'b+3=a+5=12'),
    '9G-Q05-p31-exercise-7': prop('Symmetric Property', 'التماثل', 'swap the two sides exactly', r'34=19+15\Rightarrow19+15=34'),
    '9G-Q05-p31-exercise-8': prop('Reflexive Property', 'الانعكاس', 'a quantity equals itself, written the same way', r'b+5+12=b+5+12'),
    '9G-Q05-p31-exercise-9': simple(('Read the toll for Exit 8 → Exit 15 from the table; the reverse trip Exit 15 → Exit 8 uses the same road.', 'اقرأ رسوم الرحلة من المخرج 8 إلى 15 من الجدول؛ الرحلة العكسية من 15 إلى 8 على الطريق نفسه.', '', 'Same road, same toll, opposite direction.', 'الطريق نفسه والرسوم نفسها والاتجاه معاكس.'),
                                    ('If toll(8→15) = toll(15→8), we can also write toll(15→8) = toll(8→15): this is the Symmetric Property.', 'إذا كانت رسوم (8←15) = رسوم (15←8)، يمكن كتابة رسوم (15←8) = رسوم (8←15): هذه خاصية التماثل.', r'a=b\Rightarrow b=a', 'Swapping the sides of an equality is symmetry.', 'تبديل طرفي المساواة هو التماثل.')),
    'G9G-BOOK-Q07-MCQ-01': distrib(5, 100, 1, -1, 495), 'G9G-BOOK-Q07-MCQ-02': distrib(4, 1000, 2, 1, 4008), 'G9G-BOOK-Q07-MCQ-04': distrib(7, 50, 1, 1, 357),
    'G9G-BOOK-Q07-MCQ-03': simple(('Round 51 to the friendly number 50 and multiply.', 'قرّب 51 إلى العدد السهل 50 واضرب.', r'7(50)=350', 'Estimating means using a nearby friendly number.', 'التقدير يعني استخدام عدد قريب سهل.'),
                                  ('51 is a little more than 50, so 7(51) is a little more than 350.', '51 أكبر قليلاً من 50، إذن 7(51) أكبر قليلاً من 350.', r'7(51)>350', 'Rounding down makes the estimate smaller than the true value.', 'التقريب للأسفل يجعل التقدير أصغر من القيمة الحقيقية.')),
    '9G3-REV-LO07-01': distrib(6, 100, 1, -1, 594), '9G3-REV-LO07-02': distrib(8, 100, 2, 1, 816), '9G3-REV-LO07-03': distrib(7, 50, 1, -1, 343), '9G3-REV-LO07-04': distrib(4, 200, 2, -1, 792),
    'G9G-BOOK-Q08-MCQ-01': simple(('Find the change in x and the change in y between neighbouring rows.', 'أوجد التغير في x والتغير في y بين الصفوف المتجاورة.', r'\Delta x=-3,\ \Delta y=+2\ \text{(every row)}', 'A table is linear when these changes keep the same ratio.', 'يكون الجدول خطياً عندما تبقى نسبة التغيرين ثابتة.'),
                                  ('Rate of change = Δy ÷ Δx.', 'معدل التغير = Δy ÷ Δx.', r'\dfrac{2}{-3}=-\dfrac23', 'The same rate in every row means linear.', 'المعدل نفسه في كل صف يعني أنها خطية.')),
    'G9G-BOOK-Q08-MCQ-02': simple(('Find Δx and Δy for each pair of neighbouring rows.', 'أوجد Δx و Δy لكل صفين متجاورين.', r'\Delta x=7;\ \Delta y=3,2,3,2', 'Linear needs a constant rate.', 'الخطية تحتاج معدلاً ثابتاً.'),
                                  ('The rates alternate 3/7 and 2/7, so the function is not linear.', 'المعدلات تتبادل بين 3/7 و 2/7، إذن الدالة ليست خطية.', r'\tfrac37\ne\tfrac27', 'One different rate is enough to say "not linear".', 'معدل واحد مختلف يكفي للحكم بأنها ليست خطية.')),
    'G9G-BOOK-Q08-MCQ-03': simple(('Find the pattern from the complete rows: x goes down by 0.5 while y goes up by 3.25.', 'أوجد النمط من الصفوف الكاملة: x تنقص 0.5 بينما y تزيد 3.25.', r'10.5\to10:\ 7.5\to10.75', 'A linear table changes by the same amounts every row.', 'الجدول الخطي يتغير بالمقدار نفسه في كل صف.'),
                                  ('Work backwards: before 11 comes 11.5, and before 11.5 comes 12.', 'ارجع للخلف: قبل 11 يأتي 11.5، وقبل 11.5 يأتي 12.', r'x_1=12', 'Check: y goes −2.25 → 1 → 4.25 → 7.5, adding 3.25 each time.', 'تحقق: y تمر بـ −2.25 ← 1 ← 4.25 ← 7.5 بزيادة 3.25 في كل مرة.')),
    'G9G-BOOK-Q08-MCQ-04': simple(('From the complete rows: when x decreases by 0.5, y increases by 3.25.', 'من الصفوف الكاملة: عندما تنقص x بمقدار 0.5 تزيد y بمقدار 3.25.', r'10.5\to10:\ 7.5\to10.75', 'The same change must continue for a linear table.', 'يجب أن يستمر التغير نفسه في الجدول الخطي.'),
                                  ('Apply it once more from x = 10 to x = 9.5.', 'طبّقه مرة أخرى من x = 10 إلى x = 9.5.', r'10.75+3.25=14', '', '')),
    'G9G-BOOK-Q13-MCQ-01': line_graph('(0, −3)', '(2, 1)', r'\tfrac{1-(-3)}{2-0}=2', '-3', 'y=2x-3'),
    'G9G-BOOK-Q13-MCQ-02': line_graph('(0, 2)', '(2, −4)', r'\tfrac{-4-2}{2-0}=-3', '2', 'y=2-3x'),
    'G9G-BOOK-Q13-MCQ-03': line_graph('(0, −1)', '(2, −3)', r'\tfrac{-3-(-1)}{2-0}=-1', '-1', 'y=-x-1'),
    'G9G-BOOK-Q13-MCQ-04': line_graph('(0, −8)', '(4, 4)', r'\tfrac{4-(-8)}{4-0}=3', '-8', 'y=3x-8'),
    'G9G-BOOK-Q14-MCQ-01': simple(('⌊x⌋ = n on each interval n ≤ x < n + 1.', '⌊x⌋ = n على كل فترة n ≤ x < n + 1.', r'\lfloor x\rfloor=n\ \text{on}\ [n,n+1)', 'The greatest-integer function is constant on each step.', 'دالة أكبر عدد صحيح ثابتة على كل درجة.'),
                                  ('Multiplying by 3 makes each step 3 times as high: y = 3n on [n, n + 1).', 'الضرب في 3 يجعل كل درجة أعلى 3 مرات: y = 3n على [n, n + 1).', r'f(x)=3n\ \text{on}\ [n,n+1)', 'A number outside multiplies the y-values only.', 'العدد الخارجي يضرب قيم y فقط.')),
    'G9G-BOOK-Q14-MCQ-04': simple(('Every real x can be put in, so the domain is ℝ.', 'يمكن تعويض أي عدد حقيقي x، إذن المجال ℝ.', r'D=\mathbb R', '', ''),
                                  ('⌊x⌋ gives integers n, and 3⌊x⌋ gives 3n: the range is the multiples of 3.', '⌊x⌋ تعطي أعداداً صحيحة n، و 3⌊x⌋ تعطي 3n: المدى هو مضاعفات 3.', r'R=\{3n:n\in\mathbb Z\}', 'The output is always 3 times an integer.', 'الناتج دائماً 3 أمثال عدد صحيح.')),
    'G9G-BOOK-Q14-MCQ-02': simple(('Set ⌊−x⌋ = n: this means n ≤ −x < n + 1.', 'ضع ⌊−x⌋ = n: أي n ≤ −x < n + 1.', r'n\le -x<n+1', 'Start from the definition of the floor function.', 'نبدأ من تعريف دالة أكبر عدد صحيح.'),
                                  ('Multiply by −1 and reverse both signs: −n − 1 < x ≤ −n.', 'اضرب في −1 واعكس الإشارتين: −n − 1 < x ≤ −n.', r'(-n-1,-n]', 'Multiplying an inequality by a negative number reverses it, so the closed end moves to the right.', 'الضرب في عدد سالب يعكس المتباينة، فتنتقل النهاية المغلقة إلى اليمين.')),
    'G9G-BOOK-Q14-MCQ-03': simple(('⌊x⌋ = n on [n, n + 1).', '⌊x⌋ = n على [n, n + 1).', r'\lfloor x\rfloor=n', '', ''),
                                  ('Multiply by −2: each step is at height −2n, still on [n, n + 1).', 'اضرب في −2: كل درجة على ارتفاع −2n، وما زالت على [n, n + 1).', r'g(x)=-2n\ \text{on}\ [n,n+1)', 'Multiplying outside changes heights, not the intervals.', 'الضرب الخارجي يغيّر الارتفاعات لا الفترات.')),
    '9G-Q14-p263-variant-v1': simple(('Set x − 2 = the integer part: ⌊x − 2⌋ = n when n ≤ x − 2 < n + 1.', 'ضع ⌊x − 2⌋ = n عندما n ≤ x − 2 < n + 1.', r'n\le x-2<n+1', '', ''),
                                     ('Add 2: the step y = n sits on [n + 2, n + 3). Domain ℝ, range ℤ.', 'أضف 2: الدرجة y = n تقع على [n + 2, n + 3). المجال ℝ والمدى ℤ.', r'[n+2,n+3)', 'Subtracting 2 inside shifts every step 2 units right.', 'طرح 2 بالداخل ينقل كل درجة وحدتين لليمين.')),
    '9G-Q14-p263-variant-v2': simple(('⌊x⌋ = n on [n, n + 1).', '⌊x⌋ = n على [n, n + 1).', r'\lfloor x\rfloor=n', '', ''),
                                     ('Then 2⌊x⌋ + 1 = 2n + 1: every step is an odd number. Domain ℝ, range {2n + 1}.', 'إذن 2⌊x⌋ + 1 = 2n + 1: كل درجة عدد فردي. المجال ℝ والمدى {2n + 1}.', r'y=2n+1\ \text{on}\ [n,n+1)', 'Outside operations change heights only.', 'العمليات الخارجية تغيّر الارتفاعات فقط.')),
    '9G3-REV-LO14-01': simple(('For each option compute ⌊x⌋ and compare with y.', 'لكل خيار احسب ⌊x⌋ وقارنه مع y.', r'\lfloor -1.2\rfloor=-2', 'For negative numbers, the floor goes DOWN to the next integer.', 'للأعداد السالبة، نذهب لأسفل إلى العدد الصحيح التالي.'),
                              ('(−1.2, −2) matches; the others do not (⌊0⌋ = 0, ⌊1.2⌋ = 1).', '(−1.2, −2) يطابق؛ والباقي لا (⌊0⌋ = 0، ⌊1.2⌋ = 1).', '', '', '')),
    '9G3-REV-LO14-02': simple(('y = 2 when 2 ≤ x < 3.', 'y = 2 عندما 2 ≤ x < 3.', r'\lfloor x\rfloor=2\iff2\le x<3', '', ''),
                              ('≤ gives a closed dot at x = 2; < gives an open dot at x = 3.', '≤ تعطي نقطة مغلقة عند x = 2؛ و < تعطي نقطة مفتوحة عند x = 3.', '', 'At x = 3 the value jumps to 3, so 3 is not on the step y = 2.', 'عند x = 3 تقفز القيمة إلى 3، فلا تنتمي x = 3 للدرجة y = 2.')),
    'G9G-BOOK-Q18-MCQ-01': simple(('The line is horizontal, so every point has the same y-value.', 'المستقيم أفقي، إذن كل نقاطه لها قيمة y نفسها.', '', 'A horizontal line is y = constant.', 'المستقيم الأفقي معادلته y = ثابت.'), ('Read where it crosses the y-axis: y = −4.', 'اقرأ أين يقطع محور y: y = −4.', r'y=-4', '', '')),
    'G9G-BOOK-Q18-MCQ-02': simple(('The line is horizontal, so every point has the same y-value.', 'المستقيم أفقي، إذن كل نقاطه لها قيمة y نفسها.', '', 'A horizontal line is y = constant.', 'المستقيم الأفقي معادلته y = ثابت.'), ('Read where it crosses the y-axis: y = 8.', 'اقرأ أين يقطع محور y: y = 8.', r'y=8', '', '')),
    'G9G-BOOK-Q18-MCQ-03': simple(('y = 7 has no x: y is 7 for every x.', 'y = 7 لا تحتوي x: قيمة y تساوي 7 لكل x.', r'y=7', 'A constant y-value draws a horizontal line.', 'قيمة y الثابتة ترسم مستقيماً أفقياً.'), ('It crosses the y-axis at (0, 7).', 'يقطع محور y عند (0, 7).', '(0,7)', '', '')),
    'G9G-BOOK-Q18-MCQ-04': simple(('y = −2/3 has no x: y is −2/3 for every x.', 'y = −2/3 لا تحتوي x: قيمة y تساوي −2/3 لكل x.', r'y=-\tfrac23', 'A constant y-value draws a horizontal line.', 'قيمة y الثابتة ترسم مستقيماً أفقياً.'), ('It crosses the y-axis at (0, −2/3).', 'يقطع محور y عند (0, −2/3).', r'(0,-\tfrac23)', '', '')),
    '9G3-REV-LO18-01': simple(('A horizontal line has the form y = constant.', 'المستقيم الأفقي على الصورة y = ثابت.', '', 'x = c would be vertical.', 'x = c يكون رأسياً.'), ('Through (0, −3) the constant is −3.', 'يمر بالنقطة (0, −3) فالثابت −3.', r'y=-3', '', '')),
    '9G3-REV-LO18-02': simple(('y = 8 is a horizontal line.', 'y = 8 مستقيم أفقي.', r'y=8', '', ''), ('Moving along it, y never changes, so rise = 0 and the slope is 0.', 'عند التحرك عليه لا تتغير y، فالارتفاع 0 والميل 0.', r'm=\tfrac{0}{\text{run}}=0', 'Horizontal: slope 0; vertical: slope undefined.', 'الأفقي ميله 0 والرأسي ميله غير معرّف.')),
    '9G-Q18-p233-example-6': simple(('y = 2 is a horizontal line 2 units above the x-axis.', 'y = 2 مستقيم أفقي فوق محور x بوحدتين.', r'y=2', '', ''), ('Choose the graph with a horizontal line through (0, 2): Graph A.', 'اختر الرسم الذي فيه مستقيم أفقي يمر بـ (0, 2): الرسم A.', '', 'Graph B is y = −2; the others are slanted.', 'الرسم B هو y = −2، والباقي مائل.')),
    '9G-Q18-p236-exercise-23': simple(('Solve for y: 2y = 8 − 5x, so y = 4 − 2.5x.', 'حل لإيجاد y: 2y = 8 − 5x، إذن y = 4 − 2.5x.', r'y=-\tfrac52x+4', 'Slope-intercept form shows the slope and intercept.', 'صيغة الميل والمقطع تُظهر الميل والمقطع.'),
                                      ('Look for a falling line through (0, 4) that crosses the x-axis at 1.6: Graph B.', 'ابحث عن مستقيم هابط يمر بـ (0, 4) ويقطع محور x عند 1.6: الرسم B.', r'(0,4),\ (1.6,0)', 'Graph A has the right slope but intercept −4.', 'الرسم A له الميل الصحيح لكن مقطعه −4.')),
    '9G-Q18-p236-exercise-24': simple(('Solve for y: 9y = 27 − 4x, so y = 3 − 4x/9.', 'حل لإيجاد y: 9y = 27 − 4x، إذن y = 3 − 4x/9.', r'y=-\tfrac49x+3', '', ''),
                                      ('Look for a gently falling line through (0, 3): Graph A.', 'ابحث عن مستقيم هابط ببطء يمر بـ (0, 3): الرسم A.', '(0,3)', 'Graph D falls too but crosses at (0, −3).', 'الرسم D هابط لكنه يقطع عند (0, −3).')),
    '9G-Q18-p236-exercise-27': simple(('Divide by 7: y = 3.', 'اقسم على 7: y = 3.', r'21=7y\Rightarrow y=3', '', ''), ('Horizontal line 3 units above the x-axis: Graph B.', 'مستقيم أفقي فوق محور x بثلاث وحدات: الرسم B.', '', 'Graph A is y = −3.', 'الرسم A هو y = −3.')),
    '9G-Q18-p236-exercise-28': simple(('Solve for y: 3y = 2x + 6, so y = (2/3)x + 2.', 'حل لإيجاد y: 3y = 2x + 6، إذن y = (2/3)x + 2.', r'y=\tfrac23x+2', '', ''), ('Rising line through (0, 2): Graph A.', 'مستقيم صاعد يمر بـ (0, 2): الرسم A.', '(0,2)', 'Graph B rises too but crosses at (0, −2).', 'الرسم B صاعد لكنه يقطع عند (0, −2).')),
    'G9G-BOOK-Q19-MCQ-01': verbal(r'4q', 'A number next to a letter means multiply: "the product of 4 and q".', 'العدد بجانب الحرف يعني الضرب: "حاصل ضرب 4 في q".'),
    'G9G-BOOK-Q19-MCQ-02': verbal(r'\tfrac18y', '(1/8)·y is "one eighth of y".', '(1/8)·y هو "ثُمن y".'),
    'G9G-BOOK-Q19-MCQ-03': verbal(r'15+r', '+ is "the sum of 15 and r".', 'إشارة + تعني "مجموع 15 و r".'),
    'G9G-BOOK-Q19-MCQ-04': verbal(r'w-24', 'w − 24 is "24 less than w" (24 is taken away from w).', 'w − 24 تعني "أقل من w بمقدار 24" (نطرح 24 من w).'),
    '9G-Q19-p18-exercise-5': verbal(r'3x^2', 'The power acts on x only, then multiply by 3: "three times the square of x".', 'الأس يؤثر على x فقط ثم نضرب في 3: "ثلاثة أمثال مربع x".'),
    '9G-Q19-p18-exercise-6': verbal(r'\frac{r^4}{9}', 'r is raised to the 4th power, then divided by 9: "the fourth power of r divided by nine".', 'نرفع r للقوة الرابعة ثم نقسم على 9: "القوة الرابعة لـ r مقسومة على تسعة".'),
    '9G-Q19-p18-exercise-7': verbal(r'2a+6', 'Twice a, then add 6: "six more than twice a".', 'مثلا a ثم نضيف 6: "ستة أكثر من مثلي a".'),
    '9G-Q19-p18-exercise-8': verbal(r'r^4\cdot t^3', 'Two powers multiplied: "the product of the fourth power of r and the cube of t".', 'قوتان مضروبتان: "حاصل ضرب القوة الرابعة لـ r في مكعب t".'),
    '9G-Q19-p18-exercise-9': verbal(r'25+6x^2', 'Square x, multiply by 6, add to 25: "the sum of 25 and six times the square of x".', 'ربّع x ثم اضرب في 6 ثم أضف إلى 25: "مجموع 25 وستة أمثال مربع x".'),
    '9G-Q19-p18-exercise-10': verbal(r'6f^2+5f', 'Two products added: "the sum of six times f squared and five times f".', 'حاصلا ضرب مجموعان: "مجموع ستة أمثال مربع f وخمسة أمثال f".'),
    '9G-Q19-p18-exercise-11': verbal(r'\frac{3a^5}{2}', 'a to the 5th, times 3, then divided by 2: "three times the fifth power of a, divided by two".', 'a للقوة الخامسة ثم في 3 ثم نقسم على 2: "ثلاثة أمثال القوة الخامسة لـ a مقسومة على اثنين".'),
    '9G-Q19-p18-exercise-12': verbal(r'9(a^2-1)', 'The bracket is one quantity (a² − 1) multiplied by 9: "nine times the difference of a squared and one".', 'القوس كمية واحدة (a² − 1) مضروبة في 9: "تسعة أمثال الفرق بين مربع a وواحد".'),
    # ---------------- 9 Advanced ----------------
    '9A-Q02-p71-exercise-1': sentence('3m+2=18', '"Three times a number m" = 3m; "two added to" it = 3m + 2; "is the same as 18" = 18.', '"ثلاثة أمثال العدد m" = 3m؛ "أضيف إليه اثنان" = 3m + 2؛ "يساوي 18" = 18.'),
    '9A-Q02-p71-exercise-2': sentence('5(x+3)=12', '"The sum of x and three" = (x + 3); "the product of five and" that sum = 5(x + 3).', '"مجموع x وثلاثة" = (x + 3)؛ "حاصل ضرب خمسة في" هذا المجموع = 5(x + 3).'),
    '9A-Q02-p71-exercise-3': sentence(r'\frac{24}{x}=14-2x', '"The quotient of 24 and x" = 24/x; "14 minus 2 times x" = 14 − 2x.', '"ناتج قسمة 24 على x" = 24/x؛ "14 مطروحاً منه مثلا x" = 14 − 2x.'),
    '9A-Q02-p71-exercise-4': sentence('85-9y=7(4+y)', '"9y subtracted from 85" = 85 − 9y (order matters); "seven times the sum of four and y" = 7(4 + y).', '"9y مطروحة من 85" = 85 − 9y (الترتيب مهم)؛ "سبعة أمثال مجموع أربعة و y" = 7(4 + y).'),
    '9A-Q02-p71-variant-variant': sentence('2(n+5)-4=18', '"The sum of n and five" = (n + 5); "twice" it = 2(n + 5); "four less than" that = 2(n + 5) − 4.', '"مجموع n وخمسة" = (n + 5)؛ "مثلاه" = 2(n + 5)؛ "أقل منه بأربعة" = 2(n + 5) − 4.'),
    '9A-Q04-p106-exercise-19': simple(('The temperature T may be 15° away from 400° in either direction: |T − 400| = 15.', 'قد تبتعد درجة الحرارة T عن 400 بمقدار 15 في أي اتجاه: |T − 400| = 15.', r'|T-400|=15', 'Absolute value measures distance from the set value.', 'القيمة المطلقة تقيس البعد عن القيمة المضبوطة.'),
                                      ('Split into two equations: T − 400 = 15 or T − 400 = −15.', 'قسّمها إلى معادلتين: T − 400 = 15 أو T − 400 = −15.', r'T=415\ \text{or}\ T=385', 'A distance of 15 can be above or below.', 'البعد 15 قد يكون فوق أو تحت.')),
    '9A-Q04-p106-exercise-20': simple(('Support p may be 5 points away from 38: |p − 38| = 5.', 'قد يبتعد التأييد p عن 38 بمقدار 5 نقاط: |p − 38| = 5.', r'|p-38|=5', '', ''), ('Solve both cases.', 'حل الحالتين.', r'p=43\ \text{or}\ p=33', 'Subtract and add the margin.', 'اطرح وأضف هامش الخطأ.')),
    '9A-Q04-p106-exercise-21': simple(('One standard deviation means a distance of 5.3 from the mean 20.9: |s − 20.9| = 5.3.', 'انحراف معياري واحد يعني بعداً قدره 5.3 عن الوسط 20.9: |s − 20.9| = 5.3.', r'|s-20.9|=5.3', '', ''),
                                      ('One deviation: 20.9 ± 5.3 → [15.6, 26.2]. Two deviations: 20.9 ± 10.6 → [10.3, 31.5].', 'انحراف واحد: 20.9 ± 5.3 ← [15.6, 26.2]. انحرافان: 20.9 ± 10.6 ← [10.3, 31.5].', r'[15.6,\,26.2],\ [10.3,\,31.5]', 'Two deviations = twice the distance, 2 × 5.3 = 10.6.', 'انحرافان = ضعف البعد، 2 × 5.3 = 10.6.')),
    '9A-Q04-p106-exercise-22': simple(('Read the graph: "finding new resources for Earth" = 21%.', 'اقرأ الرسم: "إيجاد موارد جديدة للأرض" = 21%.', '21\\%', '', ''),
                                      ('Apply the ±3% margin: 18% to 24%.', 'طبّق هامش ±3%: من 18% إلى 24%.', r'21\%\pm3\%', 'The margin of error gives the possible range.', 'هامش الخطأ يعطي المدى الممكن.'),
                                      ('Multiply by 40 million students.', 'اضرب في 40 مليون طالب.', r'0.18\times40=7.2,\ 0.24\times40=9.6\ \text{million}', 'Percent of a total = decimal × total.', 'النسبة من الكل = العدد العشري × الكل.')),
    '9A-Q04-p106-exercise-23': simple(('Change 8 ounces to pounds: 8 ÷ 16 = 0.5 lb.', 'حوّل 8 أونصات إلى أرطال: 8 ÷ 16 = 0.5 رطل.', r'\tfrac{8}{16}=0.5', 'Both numbers must be in the same unit.', 'يجب أن يكون العددان بالوحدة نفسها.'),
                                      ('|w − 35| = 0.5, so w = 34.5 or 35.5 lb.', '|w − 35| = 0.5، إذن w = 34.5 أو 35.5 رطل.', r'|w-35|=0.5', '', '')),
    '9A-Q05-p227-exercise-50': simple(('Points (0, 1) and (2, 5).', 'النقطتان (0, 1) و (2, 5).', r'm=\tfrac{5-1}{2-0}', 'Slope = rise ÷ run.', 'الميل = الارتفاع ÷ المسافة الأفقية.'), ('Simplify.', 'بسّط.', 'm=2', '', '')),
    '9A-Q05-p227-exercise-51': simple(('Points (0, 0) and (3, 1).', 'النقطتان (0, 0) و (3, 1).', r'm=\tfrac{1-0}{3-0}', 'Slope = rise ÷ run.', 'الميل = الارتفاع ÷ المسافة الأفقية.'), ('Simplify.', 'بسّط.', r'm=\tfrac13', '', '')),
    '9A-Q05-p227-exercise-52': simple(('Points (0, 1) and (1, −2).', 'النقطتان (0, 1) و (1, −2).', r'm=\tfrac{-2-1}{1-0}', 'Slope = rise ÷ run.', 'الميل = الارتفاع ÷ المسافة الأفقية.'), ('Simplify; the line falls, so the slope is negative.', 'بسّط؛ المستقيم هابط فالميل سالب.', 'm=-3', '', '')),
    '9A-Q07-p236-exercise-37': line_graph('(0, −3)', '(2, 1)', r'\tfrac{1-(-3)}{2}=2', '-3', 'y=2x-3'),
    '9A-Q07-p236-exercise-37-intercept': simple(('The y-intercept is where the line crosses the y-axis (x = 0).', 'المقطع الصادي هو نقطة تقاطع المستقيم مع محور y (عندما x = 0).', '(0,-3)', '', ''), ('So b = −3.', 'إذن b = −3.', 'b=-3', '', '')),
    '9A-Q07-p236-exercise-37-zero': simple(('The line is y = 2x − 3; it crosses the x-axis where y = 0.', 'المستقيم y = 2x − 3؛ يقطع محور x عندما y = 0.', '0=2x-3', 'Every point on the x-axis has y = 0.', 'كل نقطة على محور x لها y = 0.'), ('Solve.', 'حل.', r'x=\tfrac32', '', '')),
    '9A-Q07-p236-exercise-38': line_graph('(0, 2)', '(2, −4)', r'\tfrac{-4-2}{2}=-3', '2', 'y=2-3x'),
    '9A-Q07-p236-exercise-39': line_graph('(0, −1)', '(2, −3)', r'\tfrac{-3-(-1)}{2}=-1', '-1', 'y=-x-1'),
    '9A-Q09-p347-exercise-7': ineq_graph('−1', False, False, 'x<-1'), '9A-Q09-p347-exercise-8': ineq_graph('−6', False, True, 'x>-6'), '9A-Q09-p347-exercise-9': ineq_graph('5', False, False, 'x<5'),
    '9A-Q09-p347-exercise-10': ineq_graph('1', True, False, r'x\le1'), '9A-Q09-p347-exercise-11': ineq_graph('−5', True, True, r'x\ge-5'), '9A-Q09-p347-exercise-12': ineq_graph('−6', True, False, r'x\le-6'),
    '9A-Q11-p352-example-2': simple(('Translate: "the opposite of a number divided by two" = −x/2; "minus seventeen" = − 17; "is less than seven" = < 7.', 'ترجم: "معكوس عدد مقسوماً على اثنين" = −x/2؛ "مطروحاً منه سبعة عشر" = − 17؛ "أقل من سبعة" = < 7.', r'-\tfrac x2-17<7', '', ''),
                                    ('Add 17 to both sides.', 'أضف 17 إلى الطرفين.', r'-\tfrac x2<24', '', ''),
                                    ('Multiply by −2 and reverse the sign.', 'اضرب في −2 واعكس الإشارة.', r'x>-48', 'Multiplying by a negative number reverses an inequality.', 'الضرب في عدد سالب يعكس المتباينة.'),
                                    ('Graph: open circle at −48, shade right.', 'التمثيل: دائرة مفتوحة عند −48 وتظليل لليمين.', '', '', '')),
    '9A-Q11-p354-exercise-18': simple(('Distribute the right side.', 'وزّع الطرف الأيمن.', '2y+4>6+2y', '', ''), ('Subtract 2y from both sides.', 'اطرح 2y من الطرفين.', '4>6', 'When the variable disappears, judge the statement that is left.', 'عندما يختفي المتغير نحكم على العبارة المتبقية.'),
                                      ('4 > 6 is false for every y, so there is no solution.', '4 > 6 خاطئة لكل قيم y، إذن لا يوجد حل.', r'\varnothing', '', '')),
    '9A-Q11-p354-exercise-19': simple(('Distribute both sides.', 'وزّع الطرفين.', '6-3b<10-3b+18', '', ''), ('Add 3b to both sides.', 'أضف 3b إلى الطرفين.', '6<28', 'When the variable disappears, judge the statement that is left.', 'عندما يختفي المتغير نحكم على العبارة المتبقية.'),
                                      ('6 < 28 is always true, so every real number is a solution.', '6 < 28 صحيحة دائماً، إذن كل الأعداد الحقيقية حلول.', r'\mathbb R', '', '')),
    '9A-Q17-p259-example-1': simple(('Piece 1: 2x + 4 for x ≤ 1. At x = 1: 2(1) + 4 = 6, closed dot (≤), and it goes to the LEFT with slope 2.', 'الجزء 1: 2x + 4 عندما x ≤ 1. عند x = 1: 2(1) + 4 = 6، نقطة مغلقة (≤)، ويمتد لليسار بميل 2.', '(1,6)\\ \\text{closed}', 'Each piece is drawn only on its own interval.', 'كل جزء يُرسم على فترته فقط.'),
                                    ('Piece 2: −x + 3 for x > 1. At x = 1: −1 + 3 = 2, open dot (>), going RIGHT with slope −1.', 'الجزء 2: −x + 3 عندما x > 1. عند x = 1: −1 + 3 = 2، نقطة مفتوحة (>)، ويمتد لليمين بميل −1.', '(1,2)\\ \\text{open}', '', ''),
                                    ('Domain: every x is covered → ℝ. Range: piece 1 gives y ≤ 6, piece 2 gives y < 2 → (−∞, 6].', 'المجال: كل x مغطاة ← ℝ. المدى: الجزء 1 يعطي y ≤ 6، والجزء 2 يعطي y < 2 ← (−∞, 6].', r'D=\mathbb R,\ R=(-\infty,6]', 'The range is the union of the y-values of both pieces.', 'المدى هو اتحاد قيم y للجزأين.')),
    '9A-Q17-p259-example-1-boundary': simple(('At x = 1 use the piece whose condition includes 1: x ≤ 1.', 'عند x = 1 استخدم الجزء الذي يشمل شرطه العدد 1: x ≤ 1.', r'1\le1\ \checkmark', 'Only one piece may be used at the boundary.', 'نستخدم جزءاً واحداً فقط عند الحد.'), ('f(1) = 2(1) + 4 = 6, so the point is (1, 6).', 'f(1) = 2(1) + 4 = 6، إذن النقطة (1, 6).', '(1,6)', '', '')),
    '9A-Q17-p259-example-1-evaluate1': simple(('x = 1 satisfies x ≤ 1, so use 2x + 4.', 'x = 1 تحقق x ≤ 1، فنستخدم 2x + 4.', '', 'Check the condition before substituting.', 'افحص الشرط قبل التعويض.'), ('f(1) = 2(1) + 4 = 6.', 'f(1) = 2(1) + 4 = 6.', 'f(1)=6', '', '')),
    '9A-Q17-p259-example-1-evaluate2': simple(('x = 2 satisfies x > 1, so use −x + 3.', 'x = 2 تحقق x > 1، فنستخدم −x + 3.', '', 'Check the condition before substituting.', 'افحص الشرط قبل التعويض.'), ('f(2) = −2 + 3 = 1.', 'f(2) = −2 + 3 = 1.', 'f(2)=1', '', '')),
    '9A-Q17-p259-example-1-evaluate3': simple(('x = −1 satisfies x ≤ 1, so use 2x + 4.', 'x = −1 تحقق x ≤ 1، فنستخدم 2x + 4.', '', 'Check the condition before substituting.', 'افحص الشرط قبل التعويض.'), ('f(−1) = 2(−1) + 4 = 2.', 'f(−1) = 2(−1) + 4 = 2.', 'f(-1)=2', '', '')),
    '9A-Q18-p261-example-2': simple(('⌊x + 1⌋ = n when n ≤ x + 1 < n + 1.', '⌊x + 1⌋ = n عندما n ≤ x + 1 < n + 1.', r'n\le x+1<n+1', '', ''),
                                    ('Subtract 1: the step y = n is on [n − 1, n). Domain ℝ, range ℤ.', 'اطرح 1: الدرجة y = n على [n − 1, n). المجال ℝ والمدى ℤ.', r'[n-1,n)', 'Adding 1 inside shifts every step 1 unit left.', 'إضافة 1 بالداخل تنقل كل درجة وحدة لليسار.')),
    '9A-Q19-p269-example-4': abs_graph(1, 0, r'g(x)=|x-1|'), '9A-Q19-p269-example-5': abs_graph(-2, -5, r'g(x)=|x+2|-5'), '9A-Q19-p277-exercise-7': abs_graph(-2, 0, r'f(x)=|x+2|'),
    '9A-Q19-p277-exercise-8': abs_graph(-1, -2, r'f(x)=|x+1|-2'), '9A-Q19-p277-exercise-9': abs_graph(0, -3, r'f(x)=|x|-3'), '9A-Q19-p277-exercise-10': abs_graph(-5, 0, r'f(x)=|x+5|'),
    '9A-Q19-p277-exercise-11': abs_graph(0, 1, r'f(x)=|x|+1'), '9A-Q19-p277-exercise-12': abs_graph(4, -2, r'f(x)=|x-4|-2'),
    # ---------------- 10 General ----------------
    'G10G-Q05-MCQ-01': simple(('For x² + bx + c we need two integers with product c and sum b. Test each option.', 'في x² + bx + c نحتاج عددين صحيحين حاصل ضربهما c ومجموعهما b. اختبر كل خيار.', '', 'If no such pair exists, it cannot be factored over the integers.', 'إذا لم يوجد هذا الزوج فلا يمكن التحليل بأعداد صحيحة.'),
                              ('x² + 12x + 24: factor pairs of 24 sum to 25, 14, 11, 10 — never 12.', 'x² + 12x + 24: أزواج عوامل 24 مجموعها 25، 14، 11، 10 ولا تعطي 12.', r'1\cdot24,\ 2\cdot12,\ 3\cdot8,\ 4\cdot6', 'The others work: (x+3)(x+8), (x−12)(x+2), (x+6)(x−4).', 'الباقي يتحلل: (x+3)(x+8)، (x−12)(x+2)، (x+6)(x−4).')),
    'G10G-Q05-MCQ-02': simple(('Expand each answer and compare with x² + 6x − 16.', 'افرد كل إجابة وقارنها مع x² + 6x − 16.', '', 'Expanding is the quickest way to check a factorisation.', 'الفك أسرع طريقة للتحقق من التحليل.'),
                              ('(x + 2)(x − 8) = x² − 6x − 16 ✗; (x − 2)(x + 8) = x² + 6x − 16 ✓.', '(x + 2)(x − 8) = x² − 6x − 16 ✗؛ (x − 2)(x + 8) = x² + 6x − 16 ✓.', r'(x-2)(x+8)=x^2+6x-16', 'Jamaall has the right numbers with the wrong signs.', 'جمال لديه الأعداد الصحيحة بإشارات خاطئة.')),
    'G10G-Q05-MCQ-03': simple(('k must be the sum of two integers whose product is −19.', 'يجب أن يكون k مجموع عددين صحيحين حاصل ضربهما −19.', '', '(x + p)(x + q) = x² + (p + q)x + pq.', '(x + p)(x + q) = x² + (p + q)x + pq.'),
                              ('19 is prime: pairs (1, −19) and (−1, 19).', '19 عدد أولي: الزوجان (1, −19) و (−1, 19).', r'k=-18\ \text{or}\ 18', '', '')),
    'G10G-Q05-MCQ-04': simple(('k must be the sum of two integers whose product is 14.', 'يجب أن يكون k مجموع عددين صحيحين حاصل ضربهما 14.', '', '', ''),
                              ('Pairs: 1·14, 2·7 and their negatives → sums ±15, ±9.', 'الأزواج: 1·14 و 2·7 وسالباتها ← المجاميع ±15 و ±9.', r'k\in\{-15,-9,9,15\}', 'Do not forget the negative pairs.', 'لا تنسَ الأزواج السالبة.')),
    'G10G-Q05-MCQ-05': simple(('Need two positive integers with sum 8 (since −p − q = −8) and product k > 0.', 'نحتاج عددين صحيحين موجبين مجموعهما 8 وحاصل ضربهما k > 0.', '', '', ''),
                              ('Pairs (1,7), (2,6), (3,5), (4,4) give k = 7, 12, 15, 16.', 'الأزواج (1,7)، (2,6)، (3,5)، (4,4) تعطي k = 7، 12، 15، 16.', r'k\in\{7,12,15,16\}', 'Include (4, 4): a repeated factor is allowed.', 'لا تنسَ (4, 4): العامل المكرر مسموح.')),
    'G10G-Q05-MCQ-06': simple(('Need two positive integers with sum 5 and product k > 0.', 'نحتاج عددين صحيحين موجبين مجموعهما 5 وحاصل ضربهما k > 0.', '', '', ''), ('Pairs (1, 4), (2, 3) give k = 4, 6.', 'الزوجان (1, 4)، (2, 3) يعطيان k = 4، 6.', r'k\in\{4,6\}', '', '')),
    'G10G-Q11-MCQ-01': simple(('Area of a triangle = ½ × base × height.', 'مساحة المثلث = ½ × القاعدة × الارتفاع.', r'A=\tfrac12(6\sqrt2)(3\sqrt6)', '', ''), ('Multiply numbers and roots separately.', 'اضرب الأعداد معاً والجذور معاً.', r'=9\sqrt{12}', '√a·√b = √(ab).', '√a·√b = √(ab).'),
                              ('Simplify √12 = 2√3.', 'بسّط √12 = 2√3.', r'=18\sqrt3', '', '')),
    'G10G-Q11-MCQ-02': simple(('Area of a rectangle = length × width.', 'مساحة المستطيل = الطول × العرض.', r'(8\sqrt{12})(4\sqrt8)=32\sqrt{96}', '√a·√b = √(ab).', '√a·√b = √(ab).'), ('Simplify √96 = 4√6.', 'بسّط √96 = 4√6.', r'32\cdot4\sqrt6=128\sqrt6', 'Take out the largest perfect square: 96 = 16 × 6.', 'أخرج أكبر مربع كامل: 96 = 16 × 6.')),
    'G10G-Q11-MCQ-03': simple(('Geometric mean = √(h·k).', 'الوسط الهندسي = √(h·k).', r'\sqrt{32\cdot14}=\sqrt{448}', '', ''), ('Simplify: 448 = 64 × 7.', 'بسّط: 448 = 64 × 7.', r'8\sqrt7', '', '')),
    'G10G-Q11-MCQ-04': simple(('Substitute A = 5 into s = √(A/6).', 'عوّض A = 5 في s = √(A/6).', r's=\sqrt{\tfrac56}', '', ''), ('Calculate and round to the nearest tenth.', 'احسب وقرّب لأقرب عُشر.', r'\approx0.913\approx0.9=\tfrac{9}{10}', '', '')),
    'G10G-Q12-MCQ-05': simple(('Simplify inside the root first: 192/1029 = 64/343 and x⁷/x¹⁰ = 1/x³.', 'بسّط ما تحت الجذر أولاً: 192/1029 = 64/343 و x⁷/x¹⁰ = 1/x³.', r'\sqrt[3]{\tfrac{64}{343x^3}}', 'Cancelling first makes the cube root easy.', 'الاختصار أولاً يسهّل الجذر التكعيبي.'),
                              ('Take cube roots: ∛64 = 4, ∛343 = 7, ∛x³ = x.', 'خذ الجذور التكعيبية: ∛64 = 4، ∛343 = 7، ∛x³ = x.', r'\tfrac{4}{7x}', '', '')),
    'G10G-Q12-MCQ-06': simple(('Simplify inside: 640/5 = 128, a³/a = a², b⁸/b⁴ = b⁴.', 'بسّط بالداخل: 640/5 = 128، a³/a = a²، b⁸/b⁴ = b⁴.', r'\sqrt[3]{128a^2b^4}', '', ''),
                              ('Take out perfect cubes: 128 = 64·2 and b⁴ = b³·b.', 'أخرج المكعبات الكاملة: 128 = 64·2 و b⁴ = b³·b.', r'4b\sqrt[3]{2a^2b}', 'Only cubes come out of a cube root.', 'تخرج المكعبات الكاملة فقط من الجذر التكعيبي.')),
    'G10G-Q14-MCQ-01': simple(('The bag hits the ground when height = 0.', 'يصل الكيس إلى الأرض عندما يكون الارتفاع = 0.', r'-16t^2+576=0', '', ''), ('Solve: t² = 36.', 'حل: t² = 36.', r't=\pm6', '', ''), ('Time cannot be negative, so t = 6 s.', 'الزمن لا يكون سالباً، إذن t = 6 ث.', 't=6', 'Reject solutions that make no sense in the situation.', 'نرفض الحلول التي لا معنى لها في الموقف.')),
    'G10G-Q15-MCQ-01': simple(('A perfect square trinomial x² + bx + c needs c = (b/2)².', 'ثلاثي الحدود المربع الكامل x² + bx + c يحتاج c = (b/2)².', r'c=\left(\tfrac b2\right)^2', '', ''),
                              ('n² + n + 3/4: (1/2)² = 1/4 ≠ 3/4. The other three pass the test.', 'n² + n + 3/4: (1/2)² = 1/4 ≠ 3/4. الخيارات الأخرى تحقق الشرط.', r'\tfrac14\ne\tfrac34', '', '')),
    'G10G-Q15-MCQ-02': simple(('"Only solution 4" means x − 4 must be the only factor, repeated.', '"الحل الوحيد 4" يعني أن x − 4 هو العامل الوحيد مكرراً.', r'(x-4)^2=0', 'A squared factor gives one repeated root.', 'العامل المربع يعطي جذراً مكرراً واحداً.'),
                              ('Check the others: x² − 16 = 0 gives ±4; (x + 4)² gives −4; x² − 4 gives ±2.', 'افحص الباقي: x² − 16 = 0 تعطي ±4؛ (x + 4)² تعطي −4؛ x² − 4 تعطي ±2.', '', '', '')),
    'G10G-Q15-MCQ-03': simple(('Discriminant: 25 + 28 = 53, not a perfect square, so the roots are irrational.', 'المميز: 25 + 28 = 53 وليس مربعاً كاملاً، فالجذور غير نسبية.', r'b^2-4ac=53', 'Irrational roots cannot be found by integer factoring.', 'الجذور غير النسبية لا تُوجد بالتحليل بأعداد صحيحة.'),
                              ('Completing the square gives the exact values (5 ± √53)/2; a graph only estimates them.', 'إكمال المربع يعطي القيم الدقيقة (5 ± √53)/2؛ الرسم يعطي تقديراً فقط.', r'x=\tfrac{5\pm\sqrt{53}}2', '', '')),
    'G10G-Q17-MCQ-01': simple(('The product is 0, so a factor is 0.', 'حاصل الضرب صفر، إذن أحد العوامل صفر.', r'3b=0\ \text{or}\ 9b-27=0', 'Zero-product property.', 'خاصية الضرب الصفري.'), ('Solve each.', 'حل كلاً منهما.', 'b=0,\\ b=3', 'Do not divide by b: that loses b = 0.', 'لا تقسم على b لأن ذلك يضيّع b = 0.')),
    '10G3-REV-LO02-01': simple(('Write (a + b)² as (a + b)(a + b) and multiply.', 'اكتب (a + b)² على صورة (a + b)(a + b) واضرب.', r'a^2+ab+ab+b^2', '', ''), ('Combine the middle terms.', 'اجمع الحدين الأوسطين.', 'a^2+2ab+b^2', 'The middle term 2ab is the most forgotten part.', 'الحد الأوسط 2ab أكثر جزء يُنسى.')),
    '10G3-REV-LO02-02': simple(('(x − 5)² = x² − 2(5)x + 25.', '(x − 5)² = x² − 2(5)x + 25.', 'x^2-10x+25', 'Middle term = 2 × (first) × (second), with the sign of the bracket.', 'الحد الأوسط = 2 × الأول × الثاني بإشارة القوس.'), ('The missing term is −10x.', 'الحد الناقص −10x.', '-10x', '', '')),
    '10G3-REV-LO08-01': simple(('A power of a quotient: raise the top and the bottom to the power.', 'قوة ناتج قسمة: ارفع البسط والمقام للقوة.', r'\left(\tfrac ab\right)^3=\tfrac{a^3}{b^3}', '', '')),
    '10G3-REV-LO08-02': simple(('Same base divided: subtract the exponents.', 'قسمة أساسات متساوية: اطرح الأسس.', r'x^{7-3}=x^4', '', '')),
    '10G3-REV-LO09-01': simple(('Any nonzero number to the power 0 is 1.', 'أي عدد غير صفري مرفوع للقوة 0 يساوي 1.', r'a^0=1', 'aⁿ/aⁿ = a⁰ and also = 1.', 'aⁿ/aⁿ = a⁰ وتساوي أيضاً 1.')),
    '10G3-REV-LO09-02': simple(('A negative exponent means "one over".', 'الأس السالب يعني "واحد على".', r'x^{-4}=\tfrac1{x^4}', 'The sign of the value does not change; only the position.', 'إشارة القيمة لا تتغير؛ يتغير موقعها فقط.')),
    '10G3-REV-LO15-01': simple(('The square (x − 2)² is multiplied by 3. Undo that first.', 'المربع (x − 2)² مضروب في 3. نلغي ذلك أولاً.', r'(x-2)^2=9', 'Isolate the square before taking the root.', 'نعزل المربع قبل أخذ الجذر.')),
    '10G3-REV-LO16-01': simple(('Vertex form y = (x − h)² + k has vertex (h, k).', 'في صيغة الرأس y = (x − h)² + k يكون الرأس (h, k).', '(h,k)=(3,2)', 'Inside sign is opposite: x − 3 → h = 3.', 'الإشارة بالداخل معاكسة: x − 3 ← h = 3.')),
    '10G3-REV-LO16-02': simple(('x + 4 = x − (−4): shift 4 left. − 1 outside: shift 1 down.', 'x + 4 = x − (−4): انسحاب 4 يساراً. و − 1 بالخارج: انسحاب 1 لأسفل.', r'h=-4,\ k=-1', '', '')),
    '10G3-REV-LO18-01': simple(('a = −2: the minus reflects in the x-axis; |a| = 2 > 1 stretches vertically by 2.', 'a = −2: السالب يعكس حول محور x؛ و |a| = 2 > 1 تمدد رأسي بمعامل 2.', 'a=-2', '', '')),
    '10G3-REV-LO18-02': simple(('A graph is wider when 0 < |a| < 1 (vertical compression).', 'يكون المنحنى أعرض عندما 0 < |a| < 1 (انكماش رأسي).', r'|a|=\tfrac14<1', 'Smaller |a| means y grows more slowly.', 'كلما صغرت |a| نمت y أبطأ.')),
    '10G3-REV-LO19-01': simple(('Each x-intercept is a real zero. Touching at one point means one distinct zero (a double root).', 'كل مقطع سيني صفر حقيقي. التماس في نقطة واحدة يعني صفراً واحداً مميزاً (جذراً مكرراً).', '1', '', '')),
    '10G3-REV-LO19-02': simple(('Set y = 0: (x − 2)(x + 3) = 0.', 'ضع y = 0: (x − 2)(x + 3) = 0.', '', 'Zeros are the x-intercepts.', 'الأصفار هي المقاطع السينية.'), ('x = 2 or x = −3.', 'x = 2 أو x = −3.', r'\{-3,2\}', '', '')),
    # ---------------- 10 Advanced: polygons, quadrilaterals ----------------
    'G10A-BOOK-Q05-MCQ-01': angles(4, r'x+(2x+5)+x+(2x+7)=360', 58, r'(Q,R,S,T)=(121,58,123,58)^\circ'),
    'G10A-BOOK-Q05-MCQ-02': angles(4, r'(3x-6)+(x+10)+x+(2x-8)=360', 52, r'(J,K,L,M)=(150,62,52,96)^\circ'),
    'G10A-BOOK-Q05-MCQ-03': angles(5, r'90+90+(2x-20)+x+(2x+10)=540', 74, r'(A,B,C,D,E)=(90,90,128,74,158)^\circ'),
    'G10A-BOOK-Q05-MCQ-04': angles(5, r'(x-8)+(3x-11)+(x+8)+x+(2x+7)=540', 68, r'(U,V,W,Y,Z)=(60,193,76,68,143)^\circ'),
    'G10A-BOOK-Q06-MCQ-01': simple(('The diagonals of a parallelogram bisect each other: each diagonal is cut into two equal halves.', 'قطرا متوازي الأضلاع ينصّف كل منهما الآخر: كل قطر ينقسم إلى نصفين متساويين.', '', 'This property links the labelled pieces of the same diagonal.', 'هذه الخاصية تربط القطعتين المعلّمتين على القطر نفسه.'),
                                   ('Diagonal BD: x + 6 = 11 → x = 5. Diagonal AC: y − 7 = 10 → y = 17.', 'القطر BD: x + 6 = 11 ← x = 5. القطر AC: y − 7 = 10 ← y = 17.', '(x,y)=(5,17)', '', '')),
    'G10A-BOOK-Q06-MCQ-02': simple(('Opposite sides of a parallelogram are equal.', 'الأضلاع المتقابلة في متوازي الأضلاع متساوية.', '', '', ''),
                                   ('a + 15 = 3a + 11 → a = 2; 3b + 5 = b + 11 → b = 3.', 'a + 15 = 3a + 11 ← a = 2؛ 3b + 5 = b + 11 ← b = 3.', '(a,b)=(2,3)', 'Write one equation for each pair of opposite sides.', 'اكتب معادلة لكل زوج من الأضلاع المتقابلة.')),
    'G10A-BOOK-Q06-MCQ-03': simple(('Consecutive angles of a parallelogram add to 180°.', 'الزاويتان المتتاليتان في متوازي الأضلاع مجموعهما 180°.', r'(x-5)+(2x+11)=180\Rightarrow x=58', 'Consecutive angles are same-side interior angles between parallel sides.', 'الزوايا المتتالية زوايا داخلية في جهة واحدة بين ضلعين متوازيين.'),
                                   ('Opposite angles are equal: 2y = 2x + 11 = 127.', 'الزوايا المتقابلة متساوية: 2y = 2x + 11 = 127.', r'y=\tfrac{127}{2}', '', '')),
    'G10A-BOOK-Q06-MCQ-04': simple(('The diagonals bisect each other.', 'القطران ينصّف كل منهما الآخر.', '', '', ''), ('3y − 5 = y + 5 → y = 5; 2z + 7 = z + 9 → z = 2.', '3y − 5 = y + 5 ← y = 5؛ 2z + 7 = z + 9 ← z = 2.', '(y,z)=(5,2)', '', '')),
    'G10A-BOOK-Q07-MCQ-01': simple(('The same pair of opposite sides is marked parallel AND congruent.', 'الزوج نفسه من الأضلاع المتقابلة معلّم متوازياً ومتطابقاً.', '', 'One pair both parallel and congruent is a parallelogram test.', 'زوج واحد متوازٍ ومتطابق هو أحد شروط متوازي الأضلاع.'), ('So yes, it is a parallelogram.', 'إذن نعم، هو متوازي أضلاع.', '', '', '')),
    'G10A-BOOK-Q07-MCQ-02': simple(('Both pairs of opposite angles are marked congruent.', 'زوجا الزوايا المتقابلة معلّمان متطابقين.', '', 'Both pairs of opposite angles congruent is a parallelogram test.', 'تطابق زوجي الزوايا المتقابلة شرط لمتوازي الأضلاع.'), ('So yes, it is a parallelogram.', 'إذن نعم، هو متوازي أضلاع.', '', '', '')),
    'G10A-BOOK-Q07-MCQ-03': simple(('Only one pair of opposite sides is marked congruent; nothing else is marked.', 'زوج واحد فقط من الأضلاع المتقابلة معلّم متطابقاً، ولا شيء غيره.', '', 'One congruent pair alone also fits other shapes (e.g. an isosceles trapezoid).', 'زوج متطابق واحد يناسب أشكالاً أخرى (مثل شبه المنحرف متساوي الساقين).'), ('Not enough information.', 'المعلومات غير كافية.', '', '', '')),
    'G10A-BOOK-Q07-MCQ-04': simple(('One pair is marked parallel, the OTHER pair is marked congruent.', 'زوج معلّم متوازياً، والزوج الآخر معلّم متطابقاً.', '', 'An isosceles trapezoid has exactly these markings, so it is not guaranteed.', 'شبه المنحرف متساوي الساقين له هذه العلامات نفسها، فلا يوجد ضمان.'), ('Not enough information.', 'المعلومات غير كافية.', '', '', '')),
    'G10A-BOOK-Q08-MCQ-01': simple(('In a kite the angles between the two pairs of unequal sides are equal: ∠Q = ∠S.', 'في الطائرة الورقية الزاويتان بين زوجي الأضلاع غير المتساوية متساويتان: ∠Q = ∠S.', '', '', ''),
                                   ('Angles add to 360°: 2∠Q = 360 − 110 − 48 = 202.', 'مجموع الزوايا 360°: 2∠Q = 360 − 110 − 48 = 202.', r'\angle Q=101^\circ', '', '')),
    'G10A-BOOK-Q08-MCQ-02': simple(('In a kite ∠B = ∠D (the angles between unequal sides).', 'في الطائرة الورقية ∠B = ∠D.', '', '', ''), ('2∠D = 360 − 36 − 70 = 254.', '2∠D = 360 − 36 − 70 = 254.', r'\angle D=127^\circ', '', '')),
    'G10A-BOOK-Q08-MCQ-03': simple(('The diagonals of a kite are perpendicular, so each side is a hypotenuse.', 'قطرا الطائرة الورقية متعامدان، فكل ضلع وتر لمثلث قائم.', '', '', ''),
                                   ('BC = √(7² + 4²) = √65; AB = √(11² + 7²) = √170.', 'BC = √(7² + 4²) = √65؛ AB = √(11² + 7²) = √170.', r'BC=\sqrt{65}', '', ''),
                                   ('A kite has two pairs of equal sides: P = 2√170 + 2√65.', 'للطائرة زوجان من الأضلاع المتساوية: P = 2√170 + 2√65.', r'P\approx42.2', 'Round at the end.', 'نقرّب في النهاية.')),
    'G10A-BOOK-Q08-MCQ-04': simple(('Right triangles from the perpendicular diagonals: RH = √(20² + 12²) = √544 = 4√34.', 'مثلثات قائمة من القطرين المتعامدين: RH = √(20² + 12²) = √544 = 4√34.', r'RH=4\sqrt{34}', '', ''),
                                   ('RS = √(28² + 12²) = √928. P = 2(4√34 + √928).', 'RS = √(28² + 12²) = √928. P = 2(4√34 + √928).', r'P\approx107.6', '', '')),
    # dilations and similarity
    'G10A-BOOK-Q09-MCQ-01': simple(('A dilation centred at the origin multiplies both coordinates by k = 1/4.', 'التمدد حول نقطة الأصل يضرب الإحداثيين في k = 1/4.', r'(x,y)\to(kx,ky)', '', ''), ('Apply to each vertex.', 'طبّق على كل رأس.', r"F'(-\tfrac52,1),\ G'(-1,1),\ H'(-1,-2)", '', '')),
    'G10A-BOOK-Q09-MCQ-02': simple(('Multiply both coordinates by k = 5/4.', 'اضرب الإحداثيين في k = 5/4.', r'(x,y)\to(\tfrac54x,\tfrac54y)', '', ''), ('Apply to each vertex.', 'طبّق على كل رأس.', r"X'(\tfrac52,-\tfrac54),\ Y'(-\tfrac{15}2,5),\ Z'(-\tfrac52,-\tfrac{25}4)", '', '')),
    'G10A-BOOK-Q09-MCQ-03': simple(('Multiply both coordinates by k = 3/4.', 'اضرب الإحداثيين في k = 3/4.', r'(x,y)\to(\tfrac34x,\tfrac34y)', '', ''), ('Apply to each vertex.', 'طبّق على كل رأس.', r"M'(3,\tfrac92),\ N'(-\tfrac92,\tfrac32),\ P'(0,-6)", '', '')),
    'G10A-BOOK-Q09-MCQ-04': simple(('Multiply both coordinates by k = 3/2.', 'اضرب الإحداثيين في k = 3/2.', r'(x,y)\to(\tfrac32x,\tfrac32y)', '', ''), ('Apply to each vertex.', 'طبّق على كل رأس.', r"R'(-3,9),\ S'(0,-\tfrac32),\ T'(-\tfrac{15}2,\tfrac92)", '', '')),
    'G10A-REV-Q09-MCQ-01': simple(('Dilation from the origin: multiply both coordinates of C by 2.5.', 'التمدد من الأصل: اضرب إحداثيي C في 2.5.', r"C(5,2)\to C'(12.5,5)", 'Only point C is asked for.', 'المطلوب النقطة C فقط.')),
    'G10A-BOOK-Q10-MCQ-01': simple(('Match corresponding sides using the marked angles: WJ ↔ SR, JC ↔ RP.', 'طابق الأضلاع المتناظرة بالزوايا المعلّمة: WJ ↔ SR، JC ↔ RP.', '', 'Sides between matching angles correspond.', 'الأضلاع بين الزوايا المتناظرة متناظرة.'),
                                   ('Set the ratios equal: (x + 1)/8 = (3x + 1)/20.', 'ساوِ النسب: (x + 1)/8 = (3x + 1)/20.', r'20(x+1)=8(3x+1)', '', ''), ('Solve.', 'حل.', 'x=3', '', '')),
    'G10A-BOOK-Q10-MCQ-02': simple(('Corresponding sides: MP ↔ WZ and PR ↔ ZV.', 'الأضلاع المتناظرة: MP ↔ WZ و PR ↔ ZV.', '', '', ''), ('(8x − 1)/12 = (3x − 1)/4.', '(8x − 1)/12 = (3x − 1)/4.', r'4(8x-1)=12(3x-1)', '', ''), ('Solve.', 'حل.', 'x=2', '', '')),
    'G10A-BOOK-Q10-MCQ-03': simple(('Corresponding sides: SB ↔ JH (2 ↔ 3) and BP ↔ HT.', 'الأضلاع المتناظرة: SB ↔ JH (2 ↔ 3) و BP ↔ HT.', '', '', ''), ('(x + 3)/(2x + 2) = 2/3.', '(x + 3)/(2x + 2) = 2/3.', r'3(x+3)=2(2x+2)', '', ''), ('Solve.', 'حل.', 'x=5', '', '')),
    'G10A-BOOK-Q10-MCQ-04': simple(('Corresponding sides: CD ↔ WY (4 ↔ 5) and AC ↔ YQ.', 'الأضلاع المتناظرة: CD ↔ WY (4 ↔ 5) و AC ↔ YQ.', '', '', ''), ('(x + 5)/15 = 4/5.', '(x + 5)/15 = 4/5.', r'x+5=12', '', ''), ('Solve.', 'حل.', 'x=7', '', '')),
    'G10A-BOOK-Q11-MCQ-01': simple(('Compare a side of the image with the matching side of the original: J′K′ = 4, JK = 2.', 'قارن ضلعاً في الصورة بالضلع المناظر في الأصل: J′K′ = 4 و JK = 2.', r'k=\tfrac{4}{2}', 'k = image ÷ original.', 'k = الصورة ÷ الأصل.'), ('k = 2 (enlargement).', 'k = 2 (تكبير).', 'k=2', '', '')),
    'G10A-BOOK-Q11-MCQ-02': simple(('Compare distances from the origin: G(0, 2) → G′(0, 3).', 'قارن البعد عن الأصل: G(0, 2) ← G′(0, 3).', r'k=\tfrac32', 'k = image ÷ original.', 'k = الصورة ÷ الأصل.')),
    'G10A-BOOK-Q11-MCQ-03': simple(('Compare matching points: B(6, 3) → B′(4, 2).', 'قارن النقاط المتناظرة: B(6, 3) ← B′(4, 2).', r'k=\tfrac46=\tfrac23', 'k < 1 means a reduction.', 'k < 1 يعني تصغيراً.')),
    'G10A-BOOK-Q11-MCQ-04': simple(('Compare matching points: R(−4, 1) → R′(−6, 1.5).', 'قارن النقاط المتناظرة: R(−4, 1) ← R′(−6, 1.5).', r'k=\tfrac{-6}{-4}=\tfrac32', '', '')),
    'G10A-REV-Q11-MCQ-01': simple(('Compare one arm of the logo in the image with the same arm in the original.', 'قارن ذراعاً في صورة الشعار بالذراع نفسه في الأصل.', r'k=\tfrac{5}{2}=2.5', 'k = image length ÷ original length.', 'k = طول الصورة ÷ طول الأصل.')),
    'G10A-BOOK-Q12-MCQ-01': simple(('The marked angles ∠F and ∠J are equal, and the vertical angles at H are equal.', 'الزاويتان المعلّمتان ∠F و ∠J متساويتان، والزاويتان المتقابلتان بالرأس عند H متساويتان.', '', 'Two pairs of equal angles is enough (AA).', 'زوجان من الزوايا المتساوية يكفيان (AA).'), ('Similar by AA.', 'متشابهان بـ AA.', '', '', '')),
    'G10A-BOOK-Q12-MCQ-02': simple(('Find the missing angles: S-T-R: 180 − 42 − 98 = 40; U-V-W: 180 − 98 − 40 = 42.', 'أوجد الزوايا الناقصة: 180 − 42 − 98 = 40؛ 180 − 98 − 40 = 42.', '', 'Always complete the triangle before comparing.', 'أكمل زوايا المثلث دائماً قبل المقارنة.'), ('Both have 42°, 98°, 40°: similar by AA.', 'لكليهما 42° و 98° و 40°: متشابهان بـ AA.', '', '', '')),
    'G10A-BOOK-Q12-MCQ-03': simple(('Only the vertical angles at C are known to be equal.', 'الزاويتان المتقابلتان بالرأس عند C فقط معلوم تساويهما.', '', 'AA needs two pairs; one pair is not enough.', 'AA تحتاج زوجين؛ زوج واحد لا يكفي.'), ('Not enough information.', 'المعلومات غير كافية.', '', '', '')),
    'G10A-BOOK-Q12-MCQ-04': simple(('Third angles: 180 − 87 − 41 = 52 and 180 − 52 − 41 = 87.', 'الزوايا الثالثة: 180 − 87 − 41 = 52 و 180 − 52 − 41 = 87.', '', '', ''), ('Both triangles are 87°, 41°, 52°: similar by AA.', 'كلا المثلثين زواياه 87° و 41° و 52°: متشابهان بـ AA.', '', '', '')),
    'G10A-REV-Q12-MCQ-01': simple(('Third angles: 180 − 90 − 60 = 30 and 180 − 90 − 30 = 60.', 'الزوايا الثالثة: 180 − 90 − 60 = 30 و 180 − 90 − 30 = 60.', '', '', ''), ('Both are 30°, 60°, 90°: similar.', 'كلاهما 30° و 60° و 90°: متشابهان.', '', '', '')),
    'G10A-REV-Q12-MCQ-02': simple(('Order the sides and compare ratios: 8/10 = 0.8, 9/12 = 0.75, 15/20 = 0.75.', 'رتّب الأضلاع وقارن النسب: 8/10 = 0.8، 9/12 = 0.75، 15/20 = 0.75.', '', 'SSS similarity needs all three ratios equal.', 'التشابه SSS يحتاج تساوي النسب الثلاث.'), ('The ratios differ, so not similar.', 'النسب مختلفة، إذن غير متشابهين.', '', '', '')),
    'G10A-REV-Q12-MCQ-03': simple(('Same time of day → similar triangles: height/shadow is the same.', 'الوقت نفسه ← مثلثان متشابهان: الارتفاع/الظل ثابت.', r'\tfrac{h}{100}=\tfrac{4.5}{3\tfrac13}', 'Convert feet-and-inches: 4 ft 6 in = 4.5 ft, 3 ft 4 in = 3⅓ ft.', 'حوّل الأقدام والبوصات: 4 قدم 6 بوصات = 4.5 قدم، 3 قدم 4 بوصات = 3⅓ قدم.'), ('Solve.', 'حل.', r'h=135\ \text{ft}', '', '')),
    'G10A-REV-Q12-MCQ-04': simple(('Similar triangles: lighthouse 48 ↔ shadow x; Maya 6 ↔ shadow 8.', 'مثلثان متشابهان: المنارة 48 ↔ الظل x؛ مايا 6 ↔ الظل 8.', r'\tfrac{48}{x}=\tfrac68\Rightarrow x=64', '', ''), ('Maya stands 8 ft from the shadow end: y = 64 − 8 = 56.', 'تقف مايا على بعد 8 أقدام من نهاية الظل: y = 64 − 8 = 56.', 'y=56', '', '')),
    'G10A-BOOK-Q13-MCQ-01': simple(('Three parallel lines cut congruent segments on one transversal, so they cut congruent segments on every transversal.', 'ثلاثة مستقيمات متوازية تقطع قطعاً متطابقة على قاطع، فتقطع قطعاً متطابقة على كل قاطع.', '', '', ''),
                                   ('2x + 1 = x + 7 → x = 6; 3y − 8 = y + 5 → y = 13/2.', '2x + 1 = x + 7 ← x = 6؛ 3y − 8 = y + 5 ← y = 13/2.', r'(6,\tfrac{13}2)', '', '')),
    'G10A-BOOK-Q13-MCQ-02': simple(('Tick marks show a midpoint, so the two halves are equal: 2y − 1 = 3y − 5 → y = 4.', 'العلامات تبين نقطة منتصف، فالنصفان متساويان: 2y − 1 = 3y − 5 ← y = 4.', '', '', ''),
                                   ('A line through a midpoint parallel to a side bisects the other side: x + 3 = (3/2)x + 2 → x = 2.', 'المستقيم المار بمنتصف ضلع موازياً لضلع آخر ينصّف الضلع الثالث: x + 3 = (3/2)x + 2 ← x = 2.', '(x,y)=(2,4)', '', '')),
    'G10A-BOOK-Q13-MCQ-03': simple(('A midsegment is half the third side.', 'القطعة المنتصفة نصف الضلع الثالث.', r'x=\tfrac12(30)=15', 'It joins two midpoints and is parallel to the third side.', 'تصل بين منتصفي ضلعين وتوازي الضلع الثالث.')),
    'G10A-BOOK-Q13-MCQ-04': simple(('JH is a midsegment, so JH = ½ LM.', 'JH قطعة منتصفة، إذن JH = ½ LM.', r'9=\tfrac12x', '', ''), ('Solve.', 'حل.', 'x=18', '', '')),
    'G10A-REV-Q13-MCQ-01': simple(('JH joins midpoints, so it is half of LM; LM = 2 × 8 = 16.', 'JH تصل بين منتصفين، فهي نصف LM؛ LM = 2 × 8 = 16.', r'x=\tfrac12(16)=8', '', '')),
    'G10A-REV-Q13-MCQ-02': simple(('The third side is twice the midsegment.', 'الضلع الثالث ضعف القطعة المنتصفة.', r'AC=2(10)=20', '', '')),
    'G10A-BOOK-Q14-MCQ-01': simple(('In similar triangles, corresponding altitudes have the same ratio as the sides.', 'في المثلثات المتشابهة، الارتفاعات المتناظرة لها نسبة الأضلاع نفسها.', r'\tfrac{x}{22}=\tfrac{10.5}{14}', '', ''), ('Solve.', 'حل.', r'x=\tfrac{33}{2}', '', '')),
    'G10A-BOOK-Q14-MCQ-02': simple(('Medians are in the same ratio as corresponding sides (15 ↔ 10).', 'المتوسطات بنسبة الأضلاع المتناظرة (15 ↔ 10).', r'\tfrac{x}{33}=\tfrac{10}{15}', '', ''), ('Solve.', 'حل.', 'x=22', '', '')),
    'G10A-BOOK-Q14-MCQ-03': simple(('Altitudes 20 ↔ 10 are in the same ratio as the sides 22 ↔ x.', 'الارتفاعان 20 ↔ 10 بنسبة الضلعين 22 ↔ x.', r'\tfrac{x}{22}=\tfrac{10}{20}', '', ''), ('Solve.', 'حل.', 'x=11', '', '')),
    'G10A-BOOK-Q14-MCQ-04': simple(('Medians 12 ↔ x are in the same ratio as sides 12.6 ↔ 18.', 'المتوسطان 12 ↔ x بنسبة الضلعين 12.6 ↔ 18.', r'\tfrac{x}{12}=\tfrac{18}{12.6}', '', ''), ('Solve.', 'حل.', r'x=\tfrac{120}{7}', '', '')),
    'G10A-REV-Q14-MCQ-01': simple(('Altitude ratio = side ratio.', 'نسبة الارتفاعين = نسبة الضلعين.', r'\tfrac{ST}{FG}=\tfrac{SH}{FJ}\Rightarrow\tfrac6{FG}=\tfrac57', '', ''), ('Solve.', 'حل.', 'FG=8.4', '', '')),
    'G10A-REV-Q14-MCQ-02': simple(('Altitude ratio = side ratio.', 'نسبة الارتفاعين = نسبة الضلعين.', r'\tfrac{AB}{MN}=\tfrac{AD}{MQ}\Rightarrow\tfrac{24}{MN}=\tfrac{14}{10.5}', '', ''), ('Solve.', 'حل.', 'MN=18', '', '')),
    'G10A-REV-Q14-MCQ-03': simple(('The two triangles are similar, so their altitudes (distances to the intersection) have the ratio of the sides.', 'المثلثان متشابهان، فارتفاعاهما (البعد عن التقاطع) بنسبة الأضلاع.', r'\tfrac{d}{5}=\tfrac{50}{35}', '', ''), ('Solve and round.', 'حل وقرّب.', r'd\approx7\ \text{yd}', '', '')),
    'G10A-REV-Q14-MCQ-04': simple(('An angle bisector divides the opposite side in the ratio of the adjacent sides.', 'منصف الزاوية يقسم الضلع المقابل بنسبة الضلعين المجاورين.', r'\tfrac{m}{26}=\tfrac{8}{12}', '', ''), ('Solve and round.', 'حل وقرّب.', r'm\approx17.3', '', '')),
    'G10A-REV-Q14-MCQ-05': simple(('Angle-bisector ratio.', 'نسبة منصف الزاوية.', r'\tfrac{20}{24}=\tfrac{7}{x}', '', ''), ('Solve.', 'حل.', 'x=8.4', '', '')),
    'G10A-REV-Q14-MCQ-06': simple(('In △ABC use the right triangle with BX = 8, AB = 12: AX = √(12² − 8²) ≈ 8.94.', 'في △ABC استخدم المثلث القائم BX = 8، AB = 12: AX = √(12² − 8²) ≈ 8.94.', r'AX=\sqrt{80}', '', ''), ('XC = 14 − 8.94.', 'XC = 14 − 8.94.', r'XC\approx5.1\ \text{cm}', '', '')),
    'G10A-REV-Q14-MCQ-07': simple(('Scale factor from ABC to DEF: DE/AB = 8/12.', 'معامل التشابه من ABC إلى DEF: DE/AB = 8/12.', r'k=\tfrac23', '', ''), ('EY = k × BX.', 'EY = k × BX.', r'EY=\tfrac23(8)\approx5.3\ \text{cm}', 'Altitudes scale by the same factor.', 'الارتفاعات تتغير بالمعامل نفسه.')),
    'G10A-BOOK-Q15-MCQ-03': simple(('Altitude to the hypotenuse: x = √(8·23) (geometric mean of the two segments).', 'الارتفاع على الوتر: x = √(8·23) (الوسط الهندسي للقطعتين).', r'x=\sqrt{184}=2\sqrt{46}', '', ''),
                                   ('Each leg = √(adjacent segment × whole hypotenuse 31).', 'كل ضلع = √(القطعة المجاورة × الوتر كله 31).', r'y=\sqrt{8\cdot31}=2\sqrt{62},\ z=\sqrt{23\cdot31}=\sqrt{713}', '', '')),
    'G10A-BOOK-Q15-MCQ-04': simple(('Leg 10 is next to segment y: 10² = y·20 → y = 5, so x = 15.', 'الضلع 10 مجاور للقطعة y: 10² = y·20 ← y = 5، إذن x = 15.', '', '', ''), ('z = √(15·20) = 10√3.', 'z = √(15·20) = 10√3.', r'(15,5,10\sqrt3)', '', '')),
    'G10A-REV-Q15-MCQ-05': simple(('Segments 19 and 6: x = √(19·6) = √114.', 'القطعتان 19 و 6: x = √(19·6) = √114.', '', '', ''), ('y = √(6·25) = 5√6, z = √(19·25) = 5√19.', 'y = √(6·25) = 5√6، z = √(19·25) = 5√19.', r'(\sqrt{114},5\sqrt6,5\sqrt{19})', '', '')),
    'G10A-REV-Q15-MCQ-06': simple(('Altitude 3 = √(2·x) → x = 4.5; z = 2 + 4.5 = 6.5.', 'الارتفاع 3 = √(2·x) ← x = 4.5؛ z = 2 + 4.5 = 6.5.', '', '', ''), ('y = √(2·6.5) = √13.', 'y = √(2·6.5) = √13.', r'(4.5,\sqrt{13},6.5)', '', '')),
    # Pythagoras and classification
    'G10A-BOOK-Q16-MCQ-01': pyth(8, 15, 17, r'x^2+8^2=17^2'), 'G10A-BOOK-Q16-MCQ-02': pyth(24, 45, 51, r'x^2=24^2+45^2'), 'G10A-BOOK-Q16-MCQ-03': pyth(28, 96, 100, r'x^2=28^2+96^2'),
    'G10A-BOOK-Q16-MCQ-04': pyth(5, 12, 13, r'x^2=5^2+12^2'), 'G10A-REV-Q16-MCQ-01': pyth(6, 8, 10, r'x^2+8^2=10^2'), 'G10A-REV-Q16-MCQ-02': pyth(12, 16, 20, r'x^2+12^2=20^2'),
    '10A1-REV-LO16-01': simple(('Square the sides: 5, 12, 13. Compare the two smaller with the largest.', 'ربّع الأضلاع: 5، 12، 13. قارن مجموع الأصغرين بالأكبر.', r'5+12=17>13', 'Bigger than c² → acute; equal → right; smaller → obtuse.', 'أكبر من c² ← حاد؛ يساوي ← قائم؛ أصغر ← منفرج.'), ('So it is acute.', 'إذن هو حاد.', '', '', '')),
    'G10A-REV-Q16-MCQ-03': simple(('Square the sides: 5, 12, 13.', 'ربّع الأضلاع: 5، 12، 13.', r'5+12=17>13', 'Bigger than c² → acute.', 'أكبر من c² ← حاد.'), ('Acute.', 'حاد.', '', '', '')),
    '10A1-REV-LO16-02': simple(('Square the sides: 4, 8, 12.', 'ربّع الأضلاع: 4، 8، 12.', r'4+8=12', 'Equal → right triangle (converse of Pythagoras).', 'التساوي ← مثلث قائم (عكس فيثاغورس).'), ('Right.', 'قائم.', '', '', '')),
    'G10A-REV-Q16-MCQ-04': simple(('Square the sides: 4, 8, 12.', 'ربّع الأضلاع: 4، 8، 12.', r'4+8=12', 'Equal → right triangle.', 'التساوي ← مثلث قائم.'), ('Right.', 'قائم.', '', '', '')),
    'G10A-REV-Q16-MCQ-05': simple(('Square: 81 + 1600 = 1681 = 41².', 'ربّع: 81 + 1600 = 1681 = 41².', r'9^2+40^2=41^2', 'Equal → right triangle.', 'التساوي ← مثلث قائم.'), ('Right.', 'قائم.', '', '', '')),
    # special right triangles
    '10A1-REV-LO17-01': simple(('In a 45°-45°-90° triangle the hypotenuse is leg × √2.', 'في المثلث 45°-45°-90° الوتر = الضلع × √2.', r'6\sqrt2', '', '')),
    '10A1-REV-LO17-02': simple(('Leg = hypotenuse ÷ √2.', 'الضلع = الوتر ÷ √2.', r'\tfrac{10}{\sqrt2}=5\sqrt2', 'Rationalise: multiply top and bottom by √2.', 'أنطِق المقام: اضرب البسط والمقام في √2.')),
    'G10A-REV-Q17-MCQ-01': simple(('The escalator is the hypotenuse (40); the height is opposite 30°.', 'السلم المتحرك هو الوتر (40)؛ والارتفاع يقابل الزاوية 30°.', '', 'In a 30°-60°-90° triangle the side opposite 30° is half the hypotenuse.', 'في المثلث 30°-60°-90° الضلع المقابل لـ 30° نصف الوتر.'), ('Height = 40 ÷ 2.', 'الارتفاع = 40 ÷ 2.', r'20\ \text{ft}', '', '')),
    'G10A-BOOK-Q17-MCQ-01': simple(('30°-60°-90°: short leg x (opposite 30°), long leg x√3, hypotenuse 2x.', '30°-60°-90°: الضلع القصير x (يقابل 30°)، الطويل x√3، الوتر 2x.', '', 'Identify which side is given first.', 'حدّد أولاً أي ضلع معطى.'), ('Long leg 8√3 = x√3 → x = 8; hypotenuse y = 16.', 'الضلع الطويل 8√3 = x√3 ← x = 8؛ الوتر y = 16.', '(8,16)', '', '')),
    'G10A-BOOK-Q17-MCQ-02': simple(('10√3 is the long leg (next to 30°): short leg x = 10, hypotenuse y = 20.', '10√3 هو الضلع الطويل (المجاور لـ 30°): الضلع القصير x = 10، والوتر y = 20.', '(10,20)', '', '')),
    'G10A-BOOK-Q17-MCQ-03': simple(('Hypotenuse 15: short leg y = 15/2, long leg x = (15/2)√3.', 'الوتر 15: الضلع القصير y = 15/2، والطويل x = (15/2)√3.', r'(\tfrac{15\sqrt3}2,\tfrac{15}2)', '', '')),
    'G10A-BOOK-Q17-MCQ-04': simple(('14 is opposite 60° (long leg): short leg x = 14/√3 = 14√3/3; hypotenuse y = 2x = 28√3/3.', '14 يقابل 60° (الضلع الطويل): القصير x = 14/√3 = 14√3/3؛ الوتر y = 2x = 28√3/3.', r'(\tfrac{14\sqrt3}3,\tfrac{28\sqrt3}3)', '', '')),
    'G10A-REV-Q17-MCQ-02': simple(('A square cut by a diagonal makes 45°-45°-90° triangles: side = 13/√2 = 13√2/2, y = 45°.', 'قطر المربع يكوّن مثلثات 45°-45°-90°: الضلع = 13/√2 = 13√2/2، و y = 45°.', r'(\tfrac{13\sqrt2}2,45^\circ)', '', '')),
    'G10A-REV-Q17-MCQ-03': simple(('Big triangle: leg 2√3 next to 30° → other leg 2. The segment x = 2√3·cos30° = 3; y = 2·cos60° = 1.', 'المثلث الكبير: الضلع 2√3 مجاور لـ 30° ← الآخر 2. القطعة x = 2√3·cos30° = 3؛ y = 2·cos60° = 1.', '(3,1)', '', '')),
    'G10A-REV-Q17-MCQ-04': simple(('Each 5√2 is a hypotenuse of a 45°-45°-90° triangle, so each leg is 5.', 'كل 5√2 وتر لمثلث 45°-45°-90°، فكل ضلع 5.', 'x=5', '', ''), ('y is two legs: 5 + 5 = 10.', 'y يتكون من ضلعين: 5 + 5 = 10.', '(5,10)', '', '')),
    'G10A-REV-Q17-MCQ-05': simple(('Altitude 3√3 is opposite 30° in the lower triangle: x = 2·3√3 = 6√3.', 'الارتفاع 3√3 يقابل 30° في المثلث السفلي: x = 2·3√3 = 6√3.', '', '', ''), ('In the top triangle 3√3 is opposite 60°: y = 3√3/√3 = 3.', 'في المثلث العلوي 3√3 يقابل 60°: y = 3√3/√3 = 3.', r'(6\sqrt3,3)', '', '')),
    'G10A-REV-Q17-MCQ-06': simple((r'A square’s diagonal makes 45° with the sides: x = 45°.', 'قطر المربع يصنع 45° مع الأضلاع: x = 45°.', '', '', ''), ('Diagonal = side × √2 = 12√2.', 'القطر = الضلع × √2 = 12√2.', r'(45^\circ,12\sqrt2)', '', '')),
    # right-triangle trigonometry
    'G10A-BOOK-Q18-MCQ-01': simple(('Missing angle: 90 − 32 = 58°.', 'الزاوية الناقصة: 90 − 32 = 58°.', r'\angle G=58^\circ', '', ''), ('From H: GF = 11 is opposite. FH = 11/tan32°, GH = 11/sin32°.', 'من H: GF = 11 مقابل. FH = 11/tan32° و GH = 11/sin32°.', r'FH\approx17.6,\ GH\approx20.8', 'SOH-CAH-TOA: pick the ratio that uses the known side.', 'اختر النسبة المثلثية التي تستخدم الضلع المعلوم.')),
    'G10A-BOOK-Q18-MCQ-02': simple(('∠W = 90 − 57 = 33°.', '∠W = 90 − 57 = 33°.', '', '', ''), ('Hypotenuse 18: WX = 18 sin57°, XZ = 18 cos57°.', 'الوتر 18: WX = 18 sin57° و XZ = 18 cos57°.', r'WX\approx15.1,\ XZ\approx9.8', '', '')),
    'G10A-BOOK-Q18-MCQ-03': simple(('∠R = 90 − 32 = 58°.', '∠R = 90 − 32 = 58°.', '', '', ''), ('Hypotenuse 7: ST = 7 cos32°, RT = 7 sin32°.', 'الوتر 7: ST = 7 cos32° و RT = 7 sin32°.', r'ST\approx5.9,\ RT\approx3.7', '', '')),
    'G10A-BOOK-Q18-MCQ-04': simple(('∠N = 90 − 45 = 45°, so the legs are equal: QM = 18.', '∠N = 90 − 45 = 45°، فالضلعان متساويان: QM = 18.', '', '', ''), ('Hypotenuse QN = 18√2.', 'الوتر QN = 18√2.', r'QN\approx25.5', '', '')),
    'G10A-REV-Q18-MCQ-01': simple(('KL = √(22² − 8²).', 'KL = √(22² − 8²).', r'KL=\sqrt{22^2-8^2}\approx20.5', '', ''), ('∠J = cos⁻¹(8/22) ≈ 69°, ∠K = 21°.', '∠J = cos⁻¹(8/22) ≈ 69° و ∠K = 21°.', r'\angle J=\cos^{-1}(8/22)\approx69^\circ', 'Use the inverse ratio to find an angle.', 'استخدم النسبة العكسية لإيجاد الزاوية.')),
    'G10A-REV-Q18-MCQ-02': simple(('Hypotenuse 12, ∠B = 25°: AC = 12 sin25°, BC = 12 cos25°.', 'الوتر 12، ∠B = 25°: AC = 12 sin25° و BC = 12 cos25°.', r'AC=12\sin25^\circ\approx5.1,\ BC=12\cos25^\circ\approx10.9', '', ''), ('∠A = 65°.', '∠A = 65°.', '', '', '')),
    'G10A-REV-Q18-MCQ-03': simple(('Leg 5 is opposite 59°: other leg = 5/tan59° ≈ 3.00, hypotenuse = 5/sin59° ≈ 5.83.', 'الضلع 5 يقابل 59°: الضلع الآخر = 5/tan59° ≈ 3.00 والوتر = 5/sin59° ≈ 5.83.', r'\tfrac{5}{\tan59^\circ}\approx3.00,\ \tfrac{5}{\sin59^\circ}\approx5.83', '', ''),
                                  ('P = 5 + 3.00 + 5.83, A = ½·5·3.00.', 'المحيط = 5 + 3.00 + 5.83، المساحة = ½·5·3.00.', r'P\approx13.84,\ A\approx7.51', '', '')),
    'G10A-REV-Q18-MCQ-04': simple(('12 is the leg next to 18°: other leg = 12 tan18° ≈ 3.90, hypotenuse = 12/cos18° ≈ 12.62.', '12 هو الضلع المجاور لـ 18°: الآخر = 12 tan18° ≈ 3.90 والوتر = 12/cos18° ≈ 12.62.', r'12\tan18^\circ\approx3.90,\ \tfrac{12}{\cos18^\circ}\approx12.62', 'Read which side the label sits on before choosing the ratio.', 'اقرأ على أي ضلع يقع الرقم قبل اختيار النسبة.'),
                                  ('P = 12 + 3.90 + 12.62, A = ½·12·3.90.', 'المحيط = 12 + 3.90 + 12.62، المساحة = ½·12·3.90.', r'P\approx28.52,\ A\approx23.39', '', '')),
    'G10A-REV-Q18-MCQ-05': simple(('Hypotenuse 3.5, angle 48°: legs 3.5 cos48° ≈ 2.34 and 3.5 sin48° ≈ 2.60.', 'الوتر 3.5 والزاوية 48°: الضلعان 3.5 cos48° ≈ 2.34 و 3.5 sin48° ≈ 2.60.', r'3.5\cos48^\circ\approx2.34,\ 3.5\sin48^\circ\approx2.60', '', ''),
                                  ('P = 3.5 + 2.34 + 2.60, A = ½·2.34·2.60.', 'المحيط = 3.5 + 2.34 + 2.60، المساحة = ½·2.34·2.60.', r'P\approx8.44,\ A\approx3.05', '', '')),
    'G10A-BOOK-Q19-MCQ-01': simple(('Draw the right triangle: height 30 opposite 25°, distance d adjacent.', 'ارسم المثلث القائم: الارتفاع 30 يقابل 25°، والمسافة d مجاورة.', r'\tan25^\circ=\tfrac{30}{d}', 'tan links opposite and adjacent.', 'الظل يربط المقابل بالمجاور.'), ('Solve.', 'حل.', r'd=\tfrac{30}{\tan25^\circ}\approx64\ \text{m}', '', '')),
    'G10A-BOOK-Q19-MCQ-02': simple(('Height above eye level: 32.5 − 6 = 26.5 ft.', 'الارتفاع فوق مستوى العين: 32.5 − 6 = 26.5 قدم.', '', 'Angles of elevation are measured from eye level.', 'زوايا الارتفاع تُقاس من مستوى العين.'), ('θ = tan⁻¹(26.5/110).', 'θ = tan⁻¹(26.5/110).', r'\theta\approx13.5^\circ', '', '')),
    'G10A-BOOK-Q19-MCQ-03': simple(('Height 30 is opposite 55°, foot distance d is adjacent.', 'الارتفاع 30 يقابل 55°، والمسافة d مجاورة.', r'\tan55^\circ=\tfrac{30}{d}', '', ''), ('Solve.', 'حل.', r'd\approx21\ \text{ft}', '', '')),
    'G10A-BOOK-Q19-MCQ-04': simple(('Height above eye level: 100 − 5 = 95 m.', 'الارتفاع فوق مستوى العين: 100 − 5 = 95 م.', '', '', ''), ('θ = tan⁻¹(95/60).', 'θ = tan⁻¹(95/60).', r'\theta\approx57.7^\circ', '', '')),
    'G10A-REV-Q19-MCQ-01': simple(('Total height of her eyes: 80 + 5.5 = 85.5 ft; horizontal distance 122 ft.', 'ارتفاع عينيها: 80 + 5.5 = 85.5 قدم؛ والمسافة الأفقية 122 قدم.', '', 'The angle of depression equals the angle of elevation from the fountain.', 'زاوية الانخفاض تساوي زاوية الارتفاع من النافورة.'), ('θ = tan⁻¹(85.5/122).', 'θ = tan⁻¹(85.5/122).', r'\theta\approx35^\circ', '', '')),
    'G10A-REV-Q19-MCQ-02': simple(('Height 120 is opposite 19° (angle of depression = angle at the plane).', 'الارتفاع 120 يقابل 19° (زاوية الانخفاض = الزاوية عند الطائرة).', r'\tan19^\circ=\tfrac{120}{d}', '', ''), ('Solve.', 'حل.', r'd\approx348.5\ \text{ft}', '', '')),
    'G10A-REV-Q19-MCQ-03': simple(('Opposite 528, adjacent 2000.', 'المقابل 528 والمجاور 2000.', r'\theta=\tan^{-1}\tfrac{528}{2000}', '', ''), ('Calculate.', 'احسب.', r'\theta\approx14.8^\circ', '', '')),
    'G10A-BOOK-Q20-MCQ-01': trig_area(11, 14, 54, r'a=11,\ b=14,\ C=54^\circ'), 'G10A-BOOK-Q20-MCQ-02': trig_area(8.5, 12, 125, r'a=8.5,\ b=12,\ C=125^\circ'),
    'G10A-BOOK-Q20-MCQ-03': trig_area(15, 18, 32, r'a=15,\ b=18,\ C=32^\circ'), 'G10A-BOOK-Q20-MCQ-04': trig_area(9, 10, 155, r'a=9,\ b=10,\ C=155^\circ'),
    'G10A-REV-Q20-MCQ-01': trig_area(7, 5, 35, r'a=7,\ b=5,\ C=35^\circ'), 'G10A-REV-Q20-MCQ-02': trig_area(9, 11, 46, r'a=9,\ b=11,\ C=46^\circ'),
    'G10A-REV-Q20-MCQ-03': [tri_angle_C(96, 48)] + trig_area(8, 14, 36, r'a=8,\ b=14,\ C=36^\circ'),
    'G10A-REV-Q20-MCQ-04': [tri_angle_C(37, 30)] + trig_area(7, 9, 113, r'a=7,\ b=9,\ C=113^\circ'),
    'G10A-REV-Q20-MCQ-05': [tri_angle_C(75, 53)] + trig_area(15, 18, 52, r'a=15,\ b=18,\ C=52^\circ'),
    # logical conditions
    '10A1-REV-LO07-01': simple(('Recall the tests: both pairs of opposite sides congruent, both pairs of opposite angles congruent, diagonals bisect each other, or one pair parallel and congruent.', 'تذكّر الشروط: تطابق زوجي الأضلاع المتقابلة، أو زوجي الزوايا المتقابلة، أو تنصيف القطرين، أو زوج متوازٍ ومتطابق.', '', '', ''), ('Only "both pairs of opposite sides are congruent" is one of them.', 'فقط "تطابق زوجي الأضلاع المتقابلة" من بينها.', '', '', '')),
    '10A1-REV-LO07-02': simple(('One pair is parallel. If THE SAME pair is also congruent, the shape is a parallelogram.', 'زوج متوازٍ. إذا كان الزوج نفسه متطابقاً أيضاً فالشكل متوازي أضلاع.', '', 'The other pair congruent could be an isosceles trapezoid.', 'تطابق الزوج الآخر قد يعطي شبه منحرف متساوي الساقين.')),
    '10A1-REV-LO12-01': simple(('Two pairs of equal angles: the third pair is equal too (angle sum 180°).', 'زوجان من الزوايا المتساوية: الزوج الثالث متساوٍ أيضاً (مجموع الزوايا 180°).', '', '', ''), ('So the triangles are similar by AA (same shape, not necessarily the same size).', 'إذن المثلثان متشابهان بـ AA (الشكل نفسه وليس بالضرورة الحجم نفسه).', '', '', '')),
    '10A1-REV-LO12-02': simple(('AA needs two pairs of angles; SSS needs three side ratios; SAS needs two ratios and the included angle.', 'AA تحتاج زوجين من الزوايا؛ SSS تحتاج ثلاث نسب؛ SAS تحتاج نسبتين والزاوية المحصورة.', '', '', ''), ('One pair of equal angles alone is not enough.', 'زوج واحد من الزوايا وحده لا يكفي.', '', '', '')),
    'G10A-REV-Q07-MCQ-01': simple(('Both pairs of opposite sides are marked congruent.', 'زوجا الأضلاع المتقابلة معلّمان متطابقين.', '', 'This is a parallelogram test.', 'هذا شرط لمتوازي الأضلاع.'), ('Yes.', 'نعم.', '', '', '')),
    'G10A-REV-Q07-MCQ-02': simple(('Each diagonal is marked as cut into two equal halves: the diagonals bisect each other.', 'كل قطر معلّم بأنه مقسوم إلى نصفين متساويين: القطران ينصّف كل منهما الآخر.', '', 'Bisecting diagonals is a parallelogram test.', 'تنصيف القطرين شرط لمتوازي الأضلاع.'), ('Yes.', 'نعم.', '', '', '')),
}
