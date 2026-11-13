// Grade 10 General (10G3) review pack (user request, 13 Nov 2026):
//  1) 30-minute worksheet PDF from the bank, teacher key on page 4. Part A uses questions not in the
//     printed study booklet; the written outcomes have no unused bank questions, so Part B reuses two
//     booklet written questions (stated on the key page).
//  2) SCORM 1.2 auto-marked quiz of authored MIRROR questions (same outcome and structure, new numbers)
// Run: PLAYWRIGHT_MODULE=/opt/node-tools/node_modules/playwright/index.mjs node scripts/build-g10g-review-pack.mjs
import {buildWorksheet, buildScorm, tex, near, check, same} from './review-pack-lib.mjs';

const S = Math.sqrt;
await buildWorksheet({
  classroom: '10G3', slug: 'grade-10-general', grade: 'Grade 10 General', gradeAr: 'الصف العاشر عام',
  partA: [
    {id: 'G10G-Q13-MCQ-04', min: 1, key: 'D', work: '2\\sqrt6+9\\sqrt6=(2+9)\\sqrt6=11\\sqrt6', check: () => near(2 * S(6) + 9 * S(6), 11 * S(6))},
    {id: 'G10G-Q11-MCQ-06', min: 1, key: 'D', work: '\\sqrt{10\\cdot20}=\\sqrt{200}=\\sqrt{100\\cdot2}=10\\sqrt2', check: () => near(S(10) * S(20), 10 * S(2))},
    {id: 'G10G-Q10-MCQ-04', min: 1, key: 'C', work: '\\left(\\tfrac1{32}\\right)^{1/5}=\\tfrac{1}{\\sqrt[5]{32}}=\\tfrac12', check: () => near((1 / 32) ** 0.2, 0.5)},
    {id: 'G10G-Q09-MCQ-05', min: 1, key: 'C', work: 'p^4r^{-3-(-2)}=p^4r^{-1}=\\tfrac{p^4}{r}', check: () => same(r => 2 ** 4 * r ** -3 / r ** -2, r => 2 ** 4 / r, [1.5, 2, 3, 7])},
    {id: 'G10G-Q02-MCQ-05', min: 1, key: 'B', work: '(8-m)^2=64-16m+m^2', check: () => same(m => (8 - m) ** 2, m => m * m - 16 * m + 64)},
    {id: 'G10G-Q03-MCQ-05', min: 1, key: 'A', work: '(2q)^2-(5r)^2=4q^2-25r^2', check: () => same(q => (2 * q + 5 * 3) * (2 * q - 5 * 3), q => 4 * q * q - 25 * 9)},
    {id: 'G10G-Q08-MCQ-04', min: 2, key: 'A', work: '\\tfrac{3^2n^2(p^3)^2}{7^2(q^2)^2}=\\tfrac{9n^2p^6}{49q^4}', check: () => near((3 * 2 * 1.5 ** 3 / (7 * 1.2 ** 2)) ** 2, 9 * 4 * 1.5 ** 6 / (49 * 1.2 ** 4))},
    {id: 'G10G-Q04-MCQ-05', min: 2, key: 'D', work: '\\text{GCF}=2ab:\\ 2ab(2ab+a-5b)', check: () => same(a => 4 * a * a * 9 + 2 * a * a * 3 - 10 * a * 9, a => 2 * a * 3 * (2 * a * 3 + a - 15))},
    {id: 'G10G-Q06-MCQ-05', min: 2, key: 'B', work: '2(-9)=-18=(-6)(3):\\ 2x^2-6x+3x-9=(x-3)(2x+3)', check: () => same(x => 2 * x * x - 3 * x - 9, x => (x - 3) * (2 * x + 3))},
    {id: 'G10G-Q15-MCQ-05', min: 2, key: 'A', work: 'x^2-2x+1=14+1\\Rightarrow(x-1)^2=15\\Rightarrow x=1\\pm\\sqrt{15}', check: () => [1 + S(15), 1 - S(15)].every(x => near(x * x - 2 * x - 14, 0))},
    {id: 'G10G-Q16-MCQ-06', min: 2, key: 'C', work: '(x-3)^2-4:\\ h=3\\ (\\text{right }3),\\ k=-4\\ (\\text{down }4)'},
    {id: 'G10G-Q17-MCQ-05', min: 2, key: 'C', work: 'x^2-6x-27=0\\Rightarrow(x-9)(x+3)=0\\Rightarrow x=9,\\,-3', check: () => [9, -3].every(x => x * x - 6 * x === 27)},
  ],
  partB: [
    {id: 'G10G-Q22-FRQ-01', minutes: 6, parts: [{text: 'Show all partial products and combine like terms.', marks: 10, hint: 'Multiply 2y by every term, then −11 by every term → line up like terms → combine', lines: 7}]},
    {id: 'G10G-Q24-FRQ-02', minutes: 6, parts: [{text: 'Axis of symmetry and vertex.', marks: 5, lines: 2}, {text: 'y-intercept and end behavior.', marks: 5, hint: 'End behavior: what happens to y as x → +∞ and as x → −∞?', lines: 2}]},
  ],
  keyB: [
    `<p><b>13.</b> ${tex('2y^3-6y^2+4y-11y^2+33y-22=2y^3-17y^2+37y-22')}</p><p class="mk">Marks: all six partial products (6); like terms combined correctly (4).</p>`,
    `<p><b>14 (a).</b> Axis of symmetry ${tex('x=1')} (2); vertex ${tex('(1,\\,1)')} (3).</p>`,
    `<p><b>14 (b).</b> y-intercept ${tex('(0,\\,4)')} (2); as ${tex('x\\to\\pm\\infty')}, ${tex('y\\to+\\infty')}; minimum value 1 (3).</p>`,
  ],
  srcnote: 'Source: Grade 10 General textbook exercises from the platform bank. Part A questions are not in the printed Term 1 study booklet; Part B uses two booklet written questions because the bank has no other written questions for these outcomes.',
});
check(same(y => (2 * y - 11) * (y * y - 3 * y + 2), y => 2 * y ** 3 - 17 * y * y + 37 * y - 22), 'Q13 key');
check([0, 1, 2].map(x => 3 * (x - 1) ** 2 + 1).join() === '4,1,4', 'Q14 graph reading (vertex (1,1), y-intercept 4)');

// ---------------------------------------------------------------- mirror quiz
// W14 graph: y = −2(x + 1)² + 3, drawn on a numbered grid
const f = x => -2 * (x + 1) ** 2 + 3, X0 = -5, X1 = 4, Y0 = -5, Y1 = 5, U = 26, PAD = 22;
const px = x => PAD + (x - X0) * U, py = y => PAD + (Y1 - y) * U;
const xs = []; for (let x = -1 - S(4); x <= -1 + S(4) + 1e-9; x += 0.05) xs.push(x); // y ≥ −5 inside the grid
const pathD = xs.map((x, i) => `${i ? 'L' : 'M'}${px(x).toFixed(1)} ${py(f(x)).toFixed(1)}`).join(' ');
let grid = '';
for (let x = X0; x <= X1; x++) grid += `<line x1="${px(x)}" y1="${py(Y0)}" x2="${px(x)}" y2="${py(Y1)}" stroke="#cbd5e1"/>`;
for (let y = Y0; y <= Y1; y++) grid += `<line x1="${px(X0)}" y1="${py(y)}" x2="${px(X1)}" y2="${py(y)}" stroke="#cbd5e1"/>`;
let ticks = '';
for (let x = X0 + 1; x < X1; x++) if (x) ticks += `<text x="${px(x)}" y="${py(0) + 15}" text-anchor="middle" font-size="11" fill="#475569">${String(x).replace('-', '−')}</text>`;
for (let y = Y0 + 1; y < Y1; y++) if (y) ticks += `<text x="${px(0) - 5}" y="${py(y) + 4}" text-anchor="end" font-size="11" fill="#475569">${String(y).replace('-', '−')}</text>`;
const W = 2 * PAD + (X1 - X0) * U, H = 2 * PAD + (Y1 - Y0) * U;
const svgParabola = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Graph of a parabola on a coordinate grid" font-family="Arial">
<rect width="100%" height="100%" fill="#fff"/>${grid}
<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#111827"/></marker>
<marker id="pc" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#0e7490"/></marker></defs>
<line x1="${px(X0) - 6}" y1="${py(0)}" x2="${px(X1) + 8}" y2="${py(0)}" stroke="#111827" stroke-width="1.5" marker-start="url(#ah)" marker-end="url(#ah)"/>
<line x1="${px(0)}" y1="${py(Y0) + 6}" x2="${px(0)}" y2="${py(Y1) - 8}" stroke="#111827" stroke-width="1.5" marker-start="url(#ah)" marker-end="url(#ah)"/>
<text x="${px(X1) + 6}" y="${py(0) + 16}" font-size="14" font-style="italic">x</text><text x="${px(0) + 6}" y="${py(Y1) - 4}" font-size="14" font-style="italic">y</text><text x="${px(0) - 13}" y="${py(0) + 15}" font-size="12" font-style="italic">O</text>${ticks}
<path d="${pathD}" fill="none" stroke="#0e7490" stroke-width="3" marker-start="url(#pc)" marker-end="url(#pc)"/></svg>`;
check(f(-1) === 3 && f(0) === 1 && f(-2) === 1 && f(1) === -5, 'W14 parabola values');

// mirror MCQ checks
check(same(n => (7 - n) ** 2, n => n * n - 14 * n + 49), 'M5');
check(same(x => (3 * x + 8) * (3 * x - 8), x => 9 * x * x - 64), 'M6');
check(same(x => 6 * x * x * 2 + 9 * x * 4 - 3 * x * 2, x => 3 * x * 2 * (2 * x + 3 * 2 - 1)), 'M8'); // y = 2
check(same(x => 3 * x * x + 5 * x - 2, x => (3 * x - 1) * (x + 2)), 'M9');
check(near(S(6) * S(15), 3 * S(10)), 'M2');
check(near((1 / 81) ** 0.25, 1 / 3), 'M3');
check(same(n => 2 ** 5 * n ** -4 / n ** -1, n => 2 ** 5 / n ** 3, [1.5, 2, 3]), 'M4');
check([2 + S(13), 2 - S(13)].every(x => near(x * x - 4 * x - 9, 0)), 'M10');
check([-7, 3].every(x => x * x + 4 * x === 21), 'M12');
check(near((2 * 1.5 * 2 ** 4 / (5 * 1.2 ** 3)) ** 3, 8 * 1.5 ** 3 * 2 ** 12 / (125 * 1.2 ** 9)), 'M7');
check(same(x => (3 * x - 4) * (x * x + 2 * x - 5), x => 3 * x ** 3 + 2 * x * x - 23 * x + 20), 'W13');

await buildScorm({
  slug: 'grade-10-general', grade: 'Grade 10 General', gradeAr: 'الصف العاشر عام', identifier: 'G10G_TERM1_MIRROR_QUIZ_30MIN',
  mcq: [
    {lo: 'LO13', title: 'Add and subtract radicals', en: 'Simplify.', ar: 'بسّط.', math: '5\\sqrt3+8\\sqrt3',
     opts: ['13\\sqrt6', '40\\sqrt3', '13\\sqrt3', '3\\sqrt3'], key: 'C', work: '(5+8)\\sqrt3=13\\sqrt3', why: ['added the radicands', 'multiplied the coefficients', '', 'subtracted']},
    {lo: 'LO11', title: 'Products of square roots', en: 'Simplify.', ar: 'بسّط.', math: '\\sqrt6\\cdot\\sqrt{15}',
     opts: ['9\\sqrt{10}', '3\\sqrt{10}', '\\sqrt{21}', '90'], key: 'B', work: '\\sqrt{90}=\\sqrt{9\\cdot10}=3\\sqrt{10}', why: ['took 9 out instead of √9 = 3', '', 'added under the root', 'forgot the square root']},
    {lo: 'LO10', title: 'Rational exponents', en: 'Evaluate.', ar: 'احسب.', math: '\\left(\\frac{1}{81}\\right)^{1/4}',
     opts: ['3', '\\frac{1}{324}', '-\\frac{1}{3}', '\\frac{1}{3}'], key: 'D', work: '\\tfrac{1}{\\sqrt[4]{81}}=\\tfrac13', why: ['inverted the fraction', 'multiplied 81 by 4', 'a fourth root of a positive number is positive', '']},
    {lo: 'LO09', title: 'Negative and zero exponents', en: 'Which option is equivalent to the expression in simplified form?', ar: 'أيّ خيار يكافئ التعبير في أبسط صورة؟', math: '\\frac{m^5n^{-4}}{n^{-1}}',
     opts: ['\\frac{m^5}{n^5}', '\\frac{m^5}{n^3}', 'm^5n^3', '-\\frac{m^5}{n^3}'], key: 'B', work: 'm^5n^{-4-(-1)}=m^5n^{-3}=\\tfrac{m^5}{n^3}', why: ['added the exponents instead of subtracting', '', 'sign of the exponent', 'a negative exponent does not make the value negative']},
    {lo: 'LO02', title: 'Squares of sums and differences', en: 'Which option gives the product?', ar: 'أيّ خيار يعطي حاصل الضرب؟', math: '(7-n)^2',
     opts: ['n^2-14n-49', '49-14n', 'n^2-14n+49', 'n^2+49'], key: 'C', work: '(7-n)^2=49-14n+n^2', why: ['(−n)² is +n² and 7² is +49', 'dropped the n² term', '', 'forgot the middle term −14n']},
    {lo: 'LO03', title: 'Sum and difference products', en: 'Which option gives the product?', ar: 'أيّ خيار يعطي حاصل الضرب؟', math: '(3x+8)(3x-8)',
     opts: ['9x^2+64', '9x^2-64', '9x^2-48x-64', '3x^2-64'], key: 'B', work: '(3x)^2-8^2=9x^2-64', why: ['sign of the last term', '', 'the middle terms cancel', 'did not square the 3']},
    {lo: 'LO08', title: 'Divide monomials', en: 'Simplify. Assume no denominator equals zero.', ar: 'بسّط. افترض أن المقام لا يساوي صفراً.', math: '\\left(\\frac{2ab^4}{5c^3}\\right)^3',
     opts: ['\\frac{6a^3b^{12}}{15c^9}', '\\frac{8a^3b^{7}}{125c^{6}}', '\\frac{8a^3b^{12}}{125c^9}', '\\frac{8a^3b^{12}}{5c^9}'], key: 'C', work: '\\tfrac{2^3a^3(b^4)^3}{5^3(c^3)^3}=\\tfrac{8a^3b^{12}}{125c^9}', why: ['multiplied the numbers by 3 instead of cubing', 'added 3 to the exponents', '', 'did not cube the 5']},
    {lo: 'LO04', title: 'Factor using distribution', en: 'Which option is the complete factorisation of the expression?', ar: 'أيّ خيار هو التحليل الكامل للتعبير؟', math: '6x^2y+9xy^2-3xy',
     opts: ['3xy(2x+3y)', 'xy(6x+9y-3)', '3xy(2x+3y+1)', '3xy(2x+3y-1)'], key: 'D', work: '\\text{GCF}=3xy:\\ 3xy(2x+3y-1)', why: ['lost the −1 term', 'the common factor 3 is still inside', 'sign of the last term', '']},
    {lo: 'LO06', title: 'Factor non-monic trinomials', en: 'Which option is the complete factorisation of the expression?', ar: 'أيّ خيار هو التحليل الكامل للتعبير؟', math: '3x^2+5x-2',
     opts: ['(3x-1)(x+2)', '(3x+1)(x-2)', '(3x-2)(x+1)', '(3x+2)(x-1)'], key: 'A', work: '3(-2)=-6=6\\cdot(-1):\\ 3x^2+6x-x-2=(3x-1)(x+2)', why: ['', 'gives 3x² − 5x − 2', 'gives 3x² + x − 2', 'gives 3x² − x − 2']},
    {lo: 'LO15', title: 'Square root and completing-square methods', en: 'Solve by completing the square.', ar: 'حلّ بإكمال المربع.', math: 'x^2-4x-9=0',
     opts: ['x=-2\\pm\\sqrt{13}', 'x=2\\pm3', 'x=2\\pm\\sqrt{13}', 'x=4\\pm\\sqrt{13}'], key: 'C', work: 'x^2-4x+4=9+4\\Rightarrow(x-2)^2=13\\Rightarrow x=2\\pm\\sqrt{13}', why: ['sign of half the x-coefficient', 'forgot to add 4 to both sides', '', 'did not halve −4']},
    {lo: 'LO16', title: 'Translations of quadratics', en: 'Describe the translation from the parent function y = x².', ar: 'صف الانسحاب من الدالة الأم y = x².', math: 'g(x)=(x+2)^2+5',
     opts: ['\\text{Right 2 units and up 5 units}', '\\text{Left 2 units and up 5 units}', '\\text{Left 2 units and down 5 units}', '\\text{Right 2 units and down 5 units}'], key: 'B', work: '(x-(-2))^2+5:\\ h=-2\\ (\\text{left }2),\\ k=5\\ (\\text{up }5)', why: ['x + 2 moves left, not right', '', '+5 moves up', 'both directions reversed']},
    {lo: 'LO17', title: 'Factoring quadratic equations', en: 'Solve by factoring.', ar: 'حلّ بالتحليل.', math: 'x^2+4x=21',
     opts: ['x=7,\\,-3', 'x=-7,\\,-3', 'x=7,\\,3', 'x=-7,\\,3'], key: 'D', work: 'x^2+4x-21=0\\Rightarrow(x+7)(x-3)=0\\Rightarrow x=-7,\\,3', why: ['signs swapped', 'both signs negative', 'both signs positive', '']},
  ],
  written: [
    {lo: 'LO22', title: 'Multiply polynomials', en: 'Find the product. Write the coefficients of the answer in the boxes.', ar: 'أوجد حاصل الضرب. اكتب معاملات الناتج في المربعات.', math: '(3x-4)(x^2+2x-5)',
     body: `<p class="fill">[[num:w13a]] ${tex('x^3+')} [[num:w13b]] ${tex('x^2+')} [[num:w13c]] ${tex('x+')} [[num:w13d]]</p>`,
     fields: [{id: 'w13a', kind: 'num', answer: 3, pts: 2, label: 'coefficient of x cubed'}, {id: 'w13b', kind: 'num', answer: 2, pts: 2, label: 'coefficient of x squared'},
       {id: 'w13c', kind: 'num', answer: -23, pts: 3, label: 'coefficient of x'}, {id: 'w13d', kind: 'num', answer: 20, pts: 3, label: 'constant'}],
     hint: 'Type a negative number with a minus sign, e.g. −23 · x³: 2 · x²: 2 · x: 3 · constant: 3 marks',
     work: tex('3x^3+6x^2-15x-4x^2-8x+20=3x^3+2x^2-23x+20'), answerText: '3x³ + 2x² − 23x + 20'},
    {lo: 'LO24', title: 'Quadratic extrema and graph features', en: 'Use the graph. Identify the axis of symmetry, vertex and y-intercept. Then describe the end behavior.', ar: 'استخدم التمثيل البياني. حدّد محور التماثل والرأس والمقطع y، ثم صف سلوك طرفي التمثيل.', fig: svgParabola,
     body: `<p class="fill">Axis of symmetry: ${tex('x=')} [[num:w14ax]]</p><p class="fill">Vertex: ( [[num:w14vx]] , [[num:w14vy]] )</p><p class="fill">y-intercept: ( 0 , [[num:w14yi]] )</p>
<p class="fill">End behavior · سلوك الطرفين: [[sel:w14end]]</p><p class="fill">The vertex is a · الرأس قيمة: [[sel:w14mm]]</p>`,
     fields: [{id: 'w14ax', kind: 'num', answer: -1, pts: 2, label: 'axis of symmetry'}, {id: 'w14vx', kind: 'num', answer: -1, pts: 1, label: 'vertex x'}, {id: 'w14vy', kind: 'num', answer: 3, pts: 2, label: 'vertex y'},
       {id: 'w14yi', kind: 'num', answer: 1, pts: 2, label: 'y-intercept'},
       {id: 'w14end', kind: 'select', answer: 'down', pts: 2, label: 'end behavior', options: [['up', 'As x → ±∞, y → +∞'], ['down', 'As x → ±∞, y → −∞'], ['updown', 'As x → −∞, y → +∞; as x → +∞, y → −∞'], ['downup', 'As x → −∞, y → −∞; as x → +∞, y → +∞']]},
       {id: 'w14mm', kind: 'select', answer: 'max', pts: 1, label: 'maximum or minimum', options: [['max', 'Maximum · قيمة عظمى'], ['min', 'Minimum · قيمة صغرى']]}],
     hint: 'Axis 2 · vertex 3 · y-intercept 2 · end behavior 2 · maximum/minimum 1',
     work: tex('\\text{Axis } x=-1;\\ \\text{vertex }(-1,\\,3);\\ y\\text{-intercept }(0,\\,1);\\ x\\to\\pm\\infty \\Rightarrow y\\to-\\infty;\\ \\text{maximum } 3'), answerText: 'x = −1; vertex (−1, 3); y-intercept (0, 1); y → −∞ both ends; maximum 3'},
  ],
});
