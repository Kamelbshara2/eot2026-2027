// Grade 10 Advanced: SCORM 1.2 auto-marked quiz of MIRROR questions for the 30-minute worksheet
// (user request, 13 Nov 2026). Each item mirrors one worksheet question: same outcome, structure and
// skill, new numbers. They are authored variants (not textbook exercises). Every key and every
// distractor is recomputed below; distractors come from named mistakes.
// Output: public/worksheets/grade-10-advanced-term1-mirror-scorm12.zip (imsmanifest.xml + index.html)
// Run: node scripts/build-g10a-mirror-scorm.mjs
import {readFile, writeFile, rm, mkdtemp} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve} from 'node:path';
import {execFileSync} from 'node:child_process';
import katex from 'katex';
import {bidi} from '../lib/study-translate.js';

const root = resolve(import.meta.dirname, '..');
const tex = (s, display = false) => katex.renderToString(String(s), {throwOnError: true, displayMode: display, output: 'html'});
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const deg = x => x * Math.PI / 180, r1 = x => Math.round(x * 10) / 10, near = (a, b) => Math.abs(a - b) < 1e-9;
const check = (cond, msg) => { if (!cond) throw Error('Key check failed: ' + msg); };

// ---------- figures (inline SVG, labels only, like the originals)
const svgSimilar = `<svg viewBox="0 0 330 160" width="330" height="160" role="img" aria-label="Similar triangles ABC and XYZ with altitudes BD and YW" font-family="Arial" font-style="italic" font-size="15">
<polygon points="20,125 130,125 80,65" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/><line x1="80" y1="65" x2="80" y2="125" stroke="#db2777" stroke-width="2" stroke-dasharray="5 4"/><path d="M80 115 h10 v10" fill="none" stroke="#db2777" stroke-width="1.6"/>
<polygon points="160,145 307,145 240,65" fill="#dcfce7" stroke="#15803d" stroke-width="2"/><line x1="240" y1="65" x2="240" y2="145" stroke="#db2777" stroke-width="2" stroke-dasharray="5 4"/><path d="M240 135 h10 v10" fill="none" stroke="#db2777" stroke-width="1.6"/>
<text x="6" y="132">A</text><text x="134" y="132">C</text><text x="74" y="58">B</text><text x="74" y="143">D</text>
<text x="144" y="152">X</text><text x="310" y="152">Z</text><text x="234" y="58">Y</text><text x="234" y="160">W</text></svg>`;
const P = [30, 150], Bv = [30 + 13 * 16, 150], Cv = [30 + 8 * 16 * Math.cos(deg(52)), 150 - 8 * 16 * Math.sin(deg(52))];
const svgSAS = `<svg viewBox="0 0 280 175" width="280" height="175" role="img" aria-label="Triangle with sides 8 yd and 13 yd and included angle 52 degrees" font-family="Arial" font-size="14">
<polygon points="${P} ${Bv} ${Cv.map(v => v.toFixed(1))}" fill="#cffafe" stroke="#0e7490" stroke-width="2"/>
<path d="M${P[0] + 26} ${P[1]} A26 26 0 0 0 ${(P[0] + 26 * Math.cos(deg(52))).toFixed(1)} ${(P[1] - 26 * Math.sin(deg(52))).toFixed(1)}" fill="none" stroke="#0e7490" stroke-width="1.5"/>
<text x="${P[0] + 30}" y="${P[1] - 8}" font-weight="700">52°</text><text x="${(P[0] + Bv[0]) / 2 - 18}" y="${P[1] + 18}" font-weight="700">13 yd</text>
<text x="${((P[0] + Cv[0]) / 2 - 44).toFixed(0)}" y="${((P[1] + Cv[1]) / 2).toFixed(0)}" font-weight="700">8 yd</text></svg>`;

// ---------- 12 mirror MCQs (mirrors worksheet Q1–Q12)
const MCQ = [
  {lo: 'LO01', title: 'Polynomial operations', en: 'Which option gives the sum?', ar: 'أيّ خيار يعطي المجموع؟', math: '(5m^{2} + 3m - 4) + (2m^{2} - 7m)',
   opts: ['7m^{2} + 10m - 4', '7m^{2} - 4m - 4', '3m^{2} - 4m - 4', '7m^{2} - 4m'], key: 'B',
   work: '5m^2+2m^2=7m^2,\\ 3m-7m=-4m,\\ -4 \\Rightarrow 7m^2-4m-4', why: ['added 3m and 7m', '', 'subtracted the m² terms', 'dropped the constant −4']},
  {lo: 'LO02', title: 'FOIL and binomial products', en: 'Which option gives the product?', ar: 'أيّ خيار يعطي حاصل الضرب؟', math: '(4x - 3)(5x - 2)',
   opts: ['20x^{2} + 6', '20x^{2} - 23x - 6', '20x^{2} - 8x + 6', '20x^{2} - 23x + 6'], key: 'D',
   work: '20x^2-8x-15x+6=20x^2-23x+6', why: ['missed the outer and inner terms', '(−3)(−2) is +6, not −6', 'kept only the outer term', '']},
  {lo: 'LO03', title: 'Factoring by grouping', en: 'Which option is the complete factorisation of the expression?', ar: 'أيّ خيار هو التحليل الكامل للتعبير؟', math: '35xy - 21y - 40x + 24',
   opts: ['(7y - 8)(5x - 3)', '(7y + 8)(5x - 3)', '(7y - 8)(5x + 3)', '(7y + 8)(5x + 3)'], key: 'A',
   work: '7y(5x-3)-8(5x-3)=(7y-8)(5x-3)', why: ['', 'sign of 8 lost when grouping', 'sign inside the common bracket', 'both signs lost']},
  {lo: 'LO04', title: 'Factoring monic trinomials', en: 'Which option is the complete factorisation of the expression?', ar: 'أيّ خيار هو التحليل الكامل للتعبير؟', math: '30 - 17x + x^{2}',
   opts: ['(x + 15)(x + 2)', '(x - 10)(x - 3)', '(x - 15)(x - 2)', '(x - 6)(x - 5)'], key: 'C',
   work: '(-15)(-2)=30,\\ -15+(-2)=-17 \\Rightarrow (x-15)(x-2)', why: ['middle term would be +17x', 'sum is −13, not −17', '', 'sum is −11, not −17']},
  {lo: 'LO09', title: 'Dilation coordinates', en: '△PQR has vertices P(2, 4), Q(4, 2) and R(6, 1). What are the coordinates of R′ after a dilation centred at the origin with scale factor 1.5?', ar: 'رؤوس △PQR هي P(2, 4) و Q(4, 2) و R(6, 1). ما إحداثيات R′ بعد تمدد مركزه نقطة الأصل ومعامله 1.5؟',
   opts: ["R'(7.5,\\ 2.5)", "R'(9,\\ 1.5)", "R'(9,\\ 1)", "R'(4,\\ 0.67)"], key: 'B',
   work: "R'=1.5\\,(6,\\,1)=(9,\\,1.5)", why: ['added 1.5 instead of multiplying', '', 'scaled only x', 'divided by 1.5']},
  {lo: 'LO15', title: 'Geometric mean', en: 'What is the positive geometric mean of 5 and 40?', ar: 'ما الوسط الهندسي الموجب للعددين 5 و 40؟',
   opts: ['10\\sqrt{2}', '22.5', '5\\sqrt{2}', '20\\sqrt{2}'], key: 'A',
   work: '\\sqrt{5\\cdot40}=\\sqrt{200}=\\sqrt{100\\cdot2}=10\\sqrt2', why: ['', 'arithmetic mean, not geometric', '√50', '√800']},
  {lo: 'LO12', title: 'AA triangle similarity', en: 'A tree casts a shadow 60 feet long. At the same time, Omar, who is 5 feet 3 inches tall, casts a shadow 3 feet 6 inches long. How tall is the tree?', ar: 'شجرة تُلقي ظلاً طوله 60 قدماً. وفي الوقت نفسه يُلقي عمر، وطوله 5 أقدام و3 بوصات، ظلاً طوله 3 أقدام و6 بوصات. ما ارتفاع الشجرة؟',
   opts: ['40\\text{ ft}', '88.3\\text{ ft}', '105\\text{ ft}', '90\\text{ ft}'], key: 'D',
   work: '5\\tfrac14\\text{ ft}=5.25,\\ 3\\tfrac12\\text{ ft}=3.5;\\ \\tfrac{h}{60}=\\tfrac{5.25}{3.5}\\Rightarrow h=90\\text{ ft}', why: ['ratio upside down', 'treated 5 ft 3 in as 5.3 and 3 ft 6 in as 3.6', 'ignored the 6 inches', '']},
  {lo: 'LO14', title: 'Parts of similar triangles', en: 'If △ABC ∼ △XYZ, BD is an altitude of △ABC, YW is an altitude of △XYZ, BC = 9, BD = 6 and YW = 8, find YZ.', ar: 'إذا كان △ABC ∼ △XYZ، وكان BD ارتفاعاً في △ABC و YW ارتفاعاً في △XYZ، وكان BC = 9 و BD = 6 و YW = 8، فأوجد YZ.', fig: svgSimilar,
   opts: ['6.75', '11', '12', '10.7'], key: 'C',
   work: '\\tfrac{BC}{YZ}=\\tfrac{BD}{YW}\\Rightarrow \\tfrac{9}{YZ}=\\tfrac68\\Rightarrow YZ=12', why: ['ratio inverted', 'added the difference 8 − 6', '', 'used 8 × 8 ÷ 6']},
  {lo: 'LO16', title: 'Pythagorean theorem and converse', en: 'How is the triangle with side lengths √6, √10 and √17 classified?', ar: 'كيف يُصنَّف المثلث الذي أطوال أضلاعه √6 و √10 و √17؟',
   opts: ['\\text{Acute}', '\\text{Right}', '\\text{Obtuse}', '\\text{Not a triangle}'], key: 'C', prose: true,
   work: '(\\sqrt6)^2+(\\sqrt{10})^2=16<17=(\\sqrt{17})^2\\Rightarrow\\text{obtuse}', why: ['16 < 17 means obtuse', 'needs 16 = 17', '', '√6 + √10 ≈ 5.61 > √17 ≈ 4.12, so it is a triangle']},
  {lo: 'LO17', title: 'Special right triangles', en: 'A 50-foot escalator makes a 30° angle with the horizontal. How high does it rise?', ar: 'سلّم متحرك طوله 50 قدماً يصنع زاوية 30° مع الأفقي. ما الارتفاع الذي يصعده؟',
   opts: ['25\\text{ ft}', '43.3\\text{ ft}', '28.9\\text{ ft}', '100\\text{ ft}'], key: 'A',
   work: 'h=50\\sin30^\\circ=25\\text{ ft}\\ \\ (\\text{side opposite }30^\\circ=\\tfrac12\\text{ hypotenuse})', why: ['', 'used the longer leg (×√3)', 'divided by √3', 'doubled instead of halving']},
  {lo: 'LO19', title: 'Angles of elevation and depression', en: 'From the top of a 90-foot lighthouse, an observer sees a boat at an angle of depression of 23°. How far is the boat from the base of the lighthouse? Round to the nearest tenth of a foot.', ar: 'من قمة منارة ارتفاعها 90 قدماً، يرى مراقب قارباً بزاوية انخفاض 23°. كم يبعد القارب عن قاعدة المنارة؟ قرّب لأقرب عُشر قدم.',
   opts: ['38.2\\text{ ft}', '212.0\\text{ ft}', '230.3\\text{ ft}', '97.8\\text{ ft}'], key: 'B',
   work: '\\tan23^\\circ=\\tfrac{90}{d}\\Rightarrow d=\\tfrac{90}{\\tan23^\\circ}\\approx212.0\\text{ ft}', why: ['multiplied by tan instead of dividing', '', 'used sin: this is the line of sight', 'used cos']},
  {lo: 'LO20', title: 'Area with two sides and an angle', en: 'Use trigonometry to find the area of the triangle to the nearest tenth.', ar: 'استخدم حساب المثلثات لإيجاد مساحة المثلث لأقرب عُشر.', fig: svgSAS,
   opts: ['32.0\\text{ yd}^{2}', '82.0\\text{ yd}^{2}', '52.0\\text{ yd}^{2}', '41.0\\text{ yd}^{2}'], key: 'D',
   work: 'A=\\tfrac12(8)(13)\\sin52^\\circ\\approx41.0\\text{ yd}^2', why: ['used cos instead of sin', 'forgot the ½', 'ignored the angle', '']},
];

// recompute every numeric key and named distractor
check(near(1.5 * 6, 9) && near(1.5 * 1, 1.5) && near(6 + 1.5, 7.5) && near(1 + 1.5, 2.5) && near(6 / 1.5, 4) && Math.round(1 / 1.5 * 100) / 100 === 0.67, 'Q5');
check(near(Math.sqrt(200), 10 * Math.SQRT2) && near(Math.sqrt(50), 5 * Math.SQRT2) && near(Math.sqrt(800), 20 * Math.SQRT2) && (5 + 40) / 2 === 22.5, 'Q6');
check(near(60 * 5.25 / 3.5, 90) && near(60 * 3.5 / 5.25, 40) && r1(60 * 5.3 / 3.6) === 88.3 && near(60 * 5.25 / 3, 105), 'Q7');
check(near(9 * 8 / 6, 12) && near(9 * 6 / 8, 6.75) && near(9 + 8 - 6, 11) && r1(8 * 8 / 6) === 10.7, 'Q8');
check(6 + 10 < 17 && Math.sqrt(6) + Math.sqrt(10) > Math.sqrt(17), 'Q9');
check(near(r1(50 * Math.sin(deg(30))), 25) && r1(25 * Math.sqrt(3)) === 43.3 && r1(50 / Math.sqrt(3)) === 28.9, 'Q10');
check(r1(90 / Math.tan(deg(23))) === 212 && r1(90 * Math.tan(deg(23))) === 38.2 && r1(90 / Math.sin(deg(23))) === 230.3 && r1(90 / Math.cos(deg(23))) === 97.8, 'Q11');
check(r1(0.5 * 8 * 13 * Math.sin(deg(52))) === 41 && r1(0.5 * 8 * 13 * Math.cos(deg(52))) === 32 && r1(8 * 13 * Math.sin(deg(52))) === 82 && 0.5 * 8 * 13 === 52, 'Q12');
// algebra items: check the correct option by evaluating both sides at sample points
const evals = {
  0: [(m) => (5 * m * m + 3 * m - 4) + (2 * m * m - 7 * m), (m) => 7 * m * m - 4 * m - 4],
  1: [(x) => (4 * x - 3) * (5 * x - 2), (x) => 20 * x * x - 23 * x + 6],
  3: [(x) => 30 - 17 * x + x * x, (x) => (x - 15) * (x - 2)],
};
for (const [i, [f, g]] of Object.entries(evals)) for (const t of [-3, -1, 0.5, 2, 7]) check(near(f(t), g(t)), `Q${+i + 1}`);
for (const [x, y] of [[1, 2], [-2, 3], [0.5, -4]]) check(near(35 * x * y - 21 * y - 40 * x + 24, (7 * y - 8) * (5 * x - 3)), 'Q3');
for (const q of MCQ) { check(q.opts.length === 4 && new Set(q.opts).size === 4 && 'ABCD'.includes(q.key), q.lo); }

// ---------- written items (mirrors worksheet Q13–Q14), auto-marked by blanks
for (const [m, n] of [[1, 1], [2, -3], [0.5, 4]]) check(near(18 * m * m - 98 * n * n, 2 * (3 * m - 7 * n) * (3 * m + 7 * n)), 'Q13');
const A = 40, a = 5, b = 7, h = b * Math.sin(deg(A)), sinB = b * Math.sin(deg(A)) / a;
const B1 = Math.asin(sinB) * 180 / Math.PI, B2 = 180 - B1, C1 = 180 - A - B1, C2 = 180 - A - B2;
const c1 = a * Math.sin(deg(C1)) / Math.sin(deg(A)), c2 = a * Math.sin(deg(C2)) / Math.sin(deg(A));
check(h < a && a < b, 'Q14 two solutions');
const T = {B1: Math.round(B1), C1: Math.round(C1), c1: r1(c1), B2: Math.round(B2), C2: Math.round(C2), c2: r1(c2)};
check(JSON.stringify(T) === JSON.stringify({B1: 64, C1: 76, c1: 7.5, B2: 116, C2: 24, c2: 3.2}), 'Q14 values ' + JSON.stringify(T));

// ---------- data sent to the page (keys lightly encoded: casual-peek deterrent only)
const DATA = {
  mcq: MCQ.map((q, i) => ({id: `Q${i + 1}`, lo: q.lo, key: q.key, why: q.why, work: tex(q.work)})),
  q13: {gcf: 2, p: [3, 7, 3, 7], work: tex('18m^2-98n^2=2(9m^2-49n^2)=2(3m-7n)(3m+7n)')},
  q14: {count: 'two', tri: [[T.B1, T.C1, T.c1], [T.B2, T.C2, T.c2]],
    work: tex(`h=b\\sin A=7\\sin40^\\circ\\approx${h.toFixed(2)};\\ h<a<b\\Rightarrow\\text{two triangles};\\ \\sin B=\\tfrac{7\\sin40^\\circ}{5}\\approx${sinB.toFixed(4)}`) + '<br>' +
      tex(`B_1\\approx${B1.toFixed(2)}^\\circ\\approx${T.B1}^\\circ,\\ C_1\\approx${T.C1}^\\circ,\\ c_1=\\tfrac{5\\sin C_1}{\\sin40^\\circ}\\approx${T.c1}`) + '<br>' +
      tex(`B_2=180^\\circ-B_1\\approx${T.B2}^\\circ,\\ C_2\\approx${T.C2}^\\circ,\\ c_2=\\tfrac{5\\sin C_2}{\\sin40^\\circ}\\approx${T.c2}`)},
};
const encoded = Buffer.from(JSON.stringify(DATA)).toString('base64').split('').reverse().join('');

// ---------- markup
const mcqHtml = MCQ.map((q, i) => `<section class="q" id="Q${i + 1}" data-type="mcq"><header><span class="num">${i + 1}</span><span class="lo">${q.lo} · ${esc(q.title)}</span><span class="mk">2 marks</span></header>
<p class="stem">${esc(q.en)}</p><p class="ar" lang="ar" dir="rtl">${bidi(esc(q.ar))}</p>${q.math ? `<div class="math">${tex(q.math, true)}</div>` : ''}${q.fig ? `<div class="fig">${q.fig}</div>` : ''}
<div class="opts" role="radiogroup" aria-label="Question ${i + 1}">${q.opts.map((o, j) => { const L = 'ABCD'[j]; return `<label class="opt" data-l="${L}"><input type="radio" name="Q${i + 1}" value="${L}"><b>${L}</b><span>${tex(o)}</span></label>`; }).join('')}</div>
<div class="fb" aria-live="polite"></div></section>`).join('\n');

const num = (id, w = 4.2, ph = '') => `<input class="blank" id="${id}" inputmode="decimal" autocomplete="off" style="width:${w}em" placeholder="${ph}" aria-label="${id}">`;
const q13 = `<section class="q" id="Q13" data-type="q13"><header><span class="num">13</span><span class="lo">LO21 · Special-product factorization</span><span class="mk">10 marks</span></header>
<p class="stem">Factor completely using integers. Fill in each box.</p><p class="ar" lang="ar" dir="rtl">حلّل تحليلاً كاملاً باستخدام الأعداد الصحيحة. اكتب العدد المناسب في كل مربع.</p>
<div class="math">${tex('18m^{2} - 98n^{2}', true)}</div>
<p class="fill">Step 1 · GCF = ${num('q13g', 3)}</p>
<p class="fill">Step 2 · ${tex('18m^2-98n^2=')} ${'<span class="gcfecho">□</span>'}( ${num('q13a', 3)}${tex('m')} − ${num('q13b', 3)}${tex('n')} )( ${num('q13c', 3)}${tex('m')} + ${num('q13d', 3)}${tex('n')} )</p>
<p class="hint">GCF 2 marks · each correct coefficient 2 marks</p><div class="fb" aria-live="polite"></div></section>`;
const q14 = `<section class="q" id="Q14" data-type="q14"><header><span class="num">14</span><span class="lo">LO25 · Law of Sines and the ambiguous case</span><span class="mk">10 marks</span></header>
<p class="stem">Determine whether the triangle has no solution, one solution or two solutions. Then solve it. Round sides to the nearest tenth and angles to the nearest degree.</p>
<p class="ar" lang="ar" dir="rtl">حدّد هل للمثلث لا حلّ أم حلّ واحد أم حلّان، ثم حُلّه. قرّب الأضلاع لأقرب عُشر والزوايا لأقرب درجة.</p>
<div class="math">${tex('A=40^\\circ,\\quad a=5,\\quad b=7', true)}</div>
<p class="fill"><b>(a)</b> Number of triangles · عدد المثلثات [4 marks]
<select id="q14n"><option value="">— choose —</option><option value="none">No solution · لا حلّ</option><option value="one">One triangle · مثلث واحد</option><option value="two">Two triangles · مثلثان</option></select></p>
<p class="fill"><b>(b)</b> Fill in every possible triangle (leave row 2 empty if there is only one) [6 marks · 1 each]</p>
<table class="tri"><thead><tr><th></th><th>${tex('B')} (°)</th><th>${tex('C')} (°)</th><th>${tex('c')}</th></tr></thead><tbody>
<tr><th>Triangle 1</th><td>${num('t1B')}</td><td>${num('t1C')}</td><td>${num('t1c')}</td></tr>
<tr><th>Triangle 2</th><td>${num('t2B')}</td><td>${num('t2C')}</td><td>${num('t2c')}</td></tr></tbody></table>
<p class="hint">Angles accepted within ±1°, sides within ±0.1 · the two triangles may be entered in either order</p><div class="fb" aria-live="polite"></div></section>`;

// ---------- fonts + KaTeX CSS (self-contained package: works offline inside any LMS)
let katexCss = await readFile(resolve(root, 'node_modules/katex/dist/katex.min.css'), 'utf8');
for (const m of [...katexCss.matchAll(/src:url\(fonts\/([^)]*\.woff2)\) format\("woff2"\)[^;}]*[;}]/g)]) {
  const bytes = await readFile(resolve(root, 'node_modules/katex/dist/fonts', m[1]));
  katexCss = katexCss.replace(m[0], `src:url(data:font/woff2;base64,${bytes.toString('base64')}) format("woff2")${m[0].endsWith('}') ? '}' : ';'}`);
}
const arR = (await readFile(resolve(root, 'public/fonts/NotoSansArabic-Regular.woff'))).toString('base64');
const css = `@font-face{font-family:NA;src:url(data:font/woff;base64,${arR}) format("woff")}
:root{--ink:#111827;--muted:#475569;--line:#cbd5e1;--brand:#0f2b46;--ok:#166534;--okbg:#dcfce7;--bad:#991b1b;--badbg:#fee2e2;--accent:#0f766e}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,"NA",sans-serif;color:var(--ink);background:#f1f5f9;line-height:1.45}
[lang=ar]{font-family:"NA",Arial,sans-serif}
.top{position:sticky;top:0;z-index:5;background:var(--brand);color:#fff;padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.top h1{font-size:17px;margin:0}.top small{display:block;opacity:.85;font-weight:400}.timer{font:700 20px/1 Arial;background:#fff;color:var(--brand);border-radius:8px;padding:6px 10px;min-width:84px;text-align:center}.timer.low{background:#fde68a}
.wrap{max-width:860px;margin:0 auto;padding:14px 16px 90px}
.intro{background:#fff;border-left:4px solid var(--accent);border-radius:8px;padding:10px 14px;font-size:14px}.intro p{margin:4px 0}
.lmsnote{font-size:12px;color:var(--muted)}
.q{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}
.q header{display:flex;align-items:center;gap:8px;margin-bottom:6px}.num{background:var(--brand);color:#fff;font-weight:700;border-radius:6px;min-width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center}
.lo{flex:1;font-size:12px;color:var(--muted)}.mk{font-size:12px;font-weight:700;color:#9a3412}
.stem{margin:2px 0;font-size:16px}.ar{margin:2px 0 4px;font-size:14px;color:#334155;text-align:right}.math{font-size:17px}.fig{text-align:center;margin:4px 0}.fig svg{max-width:100%;height:auto}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}@media(max-width:560px){.opts{grid-template-columns:1fr}}
.opt{display:flex;align-items:center;gap:8px;border:1.5px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer;font-size:16px;min-height:44px}
.opt input{position:absolute;opacity:0;pointer-events:none}.opt b{display:inline-flex;width:24px;height:24px;border-radius:50%;border:1.5px solid #334155;align-items:center;justify-content:center;font-size:13px;flex:none}
.opt:has(input:checked){border-color:var(--brand);background:#e0e7ff}.opt:has(input:checked) b{background:var(--brand);color:#fff}.opt:has(input:focus-visible){outline:3px solid #f59e0b}
.locked .opt.right{border-color:var(--ok);background:var(--okbg)}.locked .opt.right b{background:var(--ok);color:#fff;border-color:var(--ok)}.locked .opt.wrongpick{border-color:var(--bad);background:var(--badbg)}.locked .opt.wrongpick b{background:var(--bad);color:#fff;border-color:var(--bad)}
.fill{font-size:16px;margin:8px 0}.blank{font-size:16px;padding:6px;border:1.5px solid #64748b;border-radius:6px;text-align:center}.blank.ok{border-color:var(--ok);background:var(--okbg)}.blank.no{border-color:var(--bad);background:var(--badbg)}
select{font-size:15px;padding:6px;border-radius:6px}.gcfecho{display:inline-block;min-width:1.2em;text-align:center;font-weight:700}
.tri{border-collapse:collapse;margin:6px 0}.tri th,.tri td{border:1px solid var(--line);padding:6px 8px;text-align:center}.tri tbody th{text-align:left;font-weight:600;background:#f8fafc}
.hint{font-size:12px;color:var(--muted);margin:4px 0}
.fb{margin-top:8px;font-size:14px}.fb:empty{display:none}.fb .res{font-weight:700}.fb.ok .res{color:var(--ok)}.fb.no .res{color:var(--bad)}.fb .work{background:#f8fafc;border-radius:6px;padding:6px 8px;margin-top:4px;overflow-x:auto}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;justify-content:center;align-items:center;flex-wrap:wrap}
button{font:700 16px Arial;padding:10px 20px;border-radius:8px;border:0;background:var(--accent);color:#fff;cursor:pointer;min-height:44px}button:disabled{opacity:.5;cursor:default}
.answered{font-size:13px;color:var(--muted)}
.result{background:#fff;border:2px solid var(--brand);border-radius:10px;padding:12px 16px;margin:12px 0;font-size:16px}.result strong{font-size:22px}
.locked .opt,.locked .blank,.locked select{pointer-events:none}`;

const CLIENT = String.raw`
(function(){
var D=JSON.parse(decodeURIComponent(escape(atob(ENC.split('').reverse().join('')))));
var MAX=44,LIMIT=30*60,api=null,start=Date.now(),done=false,mastery=60;
function findAPI(w){var n=0;while(w&&!w.API&&w.parent&&w.parent!==w&&n<10){w=w.parent;n++}return w&&w.API?w.API:null}
api=findAPI(window)||(window.opener?findAPI(window.opener):null);
function sv(k,v){try{if(api)api.LMSSetValue(k,String(v))}catch(e){}}
function gv(k){try{return api?api.LMSGetValue(k):''}catch(e){return ''}}
var $=function(s){return document.querySelector(s)},$$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};
if(api){try{api.LMSInitialize('')}catch(e){}var nm=gv('cmi.core.student_name');if(nm)$('#who').textContent=nm;var ms=parseFloat(gv('cmi.student_data.mastery_score'));if(ms>0)mastery=ms;
 if(gv('cmi.core.lesson_status')==='not attempted')sv('cmi.core.lesson_status','incomplete');$('#lms').textContent='Connected to your LMS · results will be recorded.';}
else $('#lms').textContent='No LMS detected · practice mode (results are not recorded).';
// restore saved answers (suspend_data)
function state(){var s={};$$('input[type=radio]:checked').forEach(function(i){s[i.name]=i.value});$$('.blank').forEach(function(i){if(i.value)s[i.id]=i.value});var n=$('#q14n');if(n.value)s.q14n=n.value;return s}
function save(){if(done)return;var s=JSON.stringify({a:state(),t:elapsed()});sv('cmi.suspend_data',s.slice(0,4000));count()}
var saved={};try{saved=JSON.parse(gv('cmi.suspend_data')||'{}')}catch(e){}
var a=saved.a||{},prior=saved.t||0;
Object.keys(a).forEach(function(k){var r=document.querySelector('input[name="'+k+'"][value="'+a[k]+'"]');if(r)r.checked=true;var b=document.getElementById(k);if(b&&b.classList.contains('blank'))b.value=a[k];if(k==='q14n')$('#q14n').value=a[k]});
function elapsed(){return prior+Math.round((Date.now()-start)/1000)}
function count(){var n=0;for(var i=1;i<=12;i++)if(document.querySelector('input[name=Q'+i+']:checked'))n++;if($('#q13g').value||$('#q13a').value)n++;if($('#q14n').value)n++;$('#answered').textContent=n+' / 14 answered';}
document.addEventListener('change',save);document.addEventListener('input',function(e){if(e.target.id==='q13g')$('.gcfecho').textContent=e.target.value||'□';count()});
var tick=setInterval(function(){var left=LIMIT-elapsed();if(left<=0){$('#timer').textContent='0:00';clearInterval(tick);if(!done)submit(true);return}
 $('#timer').textContent=Math.floor(left/60)+':'+('0'+left%60).slice(-2);$('#timer').classList.toggle('low',left<=300);if(left%30===0)save()},1000);
function n(id){var v=(document.getElementById(id).value||'').trim().replace(',', '.').replace('−','-');return v===''?NaN:Number(v)}
function hms(s){function p(x,l){x=String(x);while(x.length<l)x='0'+x;return x}return p(Math.floor(s/3600),4)+':'+p(Math.floor(s%3600/60),2)+':'+p(s%60,2)}
var ix=0;function inter(id,type,resp,pat,ok,w){var p='cmi.interactions.'+ix+'.';sv(p+'id',id);sv(p+'type',type);sv(p+'student_response',resp);sv(p+'correct_responses.0.pattern',pat);sv(p+'result',ok?'correct':'wrong');sv(p+'weighting',w);ix++}
function fb(el,ok,text,work){var f=el.querySelector('.fb');f.className='fb '+(ok?'ok':'no');f.innerHTML='<span class="res">'+text+'</span>'+(work?'<div class="work">'+work+'</div>':'')}
function submit(auto){
 if(done)return;if(!auto&&!confirm('Submit your answers now? · هل تريد تسليم إجاباتك الآن؟'))return;done=true;clearInterval(tick);
 var score=0;document.body.classList.add('locked');
 D.mcq.forEach(function(q,i){var el=document.getElementById(q.id),pick=(document.querySelector('input[name='+q.id+']:checked')||{}).value||'',ok=pick===q.key;if(ok)score+=2;
  el.querySelectorAll('.opt').forEach(function(o){if(o.dataset.l===q.key)o.classList.add('right');else if(o.dataset.l===pick)o.classList.add('wrongpick')});
  var why=pick&&!ok&&q.why['ABCD'.indexOf(pick)]?' — '+q.why['ABCD'.indexOf(pick)]:'';
  fb(el,ok,ok?'✓ Correct · +2':'✗ '+(pick?'You chose '+pick+why:'Not answered')+' · correct answer: '+q.key,q.work);inter(q.id,'choice',pick,q.key,ok,2)});
 // Q13
 var g=n('q13g'),ps=['q13a','q13b','q13c','q13d'].map(n),s13=0,el13=document.getElementById('Q13');
 if(g===D.q13.gcf){s13+=2;$('#q13g').classList.add('ok')}else $('#q13g').classList.add('no');
 ps.forEach(function(v,i){var id=['q13a','q13b','q13c','q13d'][i];if(v===D.q13.p[i]){s13+=2;document.getElementById(id).classList.add('ok')}else document.getElementById(id).classList.add('no')});
 score+=s13;fb(el13,s13===10,(s13===10?'✓ ':'✗ ')+s13+' / 10',D.q13.work);inter('Q13','fill-in',[g].concat(ps).join(','),'2,3,7,3,7',s13===10,10);
 // Q14
 var el14=document.getElementById('Q14'),s14=0,cnt=$('#q14n').value;if(cnt===D.q14.count){s14+=4;$('#q14n').style.background='#dcfce7'}else $('#q14n').style.background='#fee2e2';
 var rows=[['t1B','t1C','t1c'],['t2B','t2C','t2c']],got=rows.map(function(r){return r.map(n)}),tol=[1,1,0.1];
 function rowPts(gr,tr){return gr.reduce(function(s,v,j){return s+(Math.abs(v-tr[j])<=tol[j]+1e-9?1:0)},0)}
 var straight=rowPts(got[0],D.q14.tri[0])+rowPts(got[1],D.q14.tri[1]),swapped=rowPts(got[0],D.q14.tri[1])+rowPts(got[1],D.q14.tri[0]),order=swapped>straight?[1,0]:[0,1];
 rows.forEach(function(r,i){r.forEach(function(id,j){var ok=Math.abs(got[i][j]-D.q14.tri[order[i]][j])<=tol[j]+1e-9;document.getElementById(id).classList.add(ok?'ok':'no');if(ok)s14++})});
 score+=s14;fb(el14,s14===10,(s14===10?'✓ ':'✗ ')+s14+' / 10 · two triangles: B≈'+D.q14.tri[0][0]+'°, C≈'+D.q14.tri[0][1]+'°, c≈'+D.q14.tri[0][2]+' and B≈'+D.q14.tri[1][0]+'°, C≈'+D.q14.tri[1][1]+'°, c≈'+D.q14.tri[1][2],D.q14.work);
 inter('Q14','fill-in',cnt+';'+got.map(function(r){return r.join(',')}).join(';'),'two;64,76,7.5;116,24,3.2',s14===10,10);
 var pct=Math.round(score/MAX*100),pass=pct>=mastery;
 sv('cmi.core.score.raw',pct);sv('cmi.core.score.min',0);sv('cmi.core.score.max',100);sv('cmi.core.lesson_status',pass?'passed':'failed');sv('cmi.core.session_time',hms(Math.round((Date.now()-start)/1000)));
 sv('cmi.suspend_data','');sv('cmi.core.exit','');try{if(api)api.LMSCommit('')}catch(e){}
 var r=$('#result');r.hidden=false;r.innerHTML='<strong>'+score+' / '+MAX+'</strong> ('+pct+'%) · '+(pass?'Passed · ناجح':'Keep practising · واصل التدريب')+(auto?'<br>Time is up: your answers were submitted automatically. · انتهى الوقت وسُلّمت إجاباتك تلقائياً.':'')+'<br><span class="lmsnote">Scroll through the questions to see the correct answers and working. · راجع الأسئلة لترى الإجابات الصحيحة وطريقة الحل.</span>';
 $('#submit').disabled=true;window.scrollTo({top:0,behavior:'smooth'});window.__score={raw:score,pct:pct,pass:pass};
}
$('#submit').addEventListener('click',function(){submit(false)});
function finish(){if(api){if(!done){save();sv('cmi.core.exit','suspend');sv('cmi.core.session_time',hms(Math.round((Date.now()-start)/1000)))}try{api.LMSCommit('');api.LMSFinish('')}catch(e){}api=null}}
window.addEventListener('pagehide',finish);window.addEventListener('beforeunload',finish);count();
})();`;

const html = `<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Grade 10 Advanced · Term 1 mirror quiz · 30 minutes</title><style>${katexCss}\n${css}</style></head><body>
<div class="top"><h1>Grade 10 Advanced · Term 1 mirror quiz<small><span lang="ar">اختبار أسئلة مماثلة · الصف العاشر متقدم</span> · <span id="who"></span></small></h1><div class="timer" id="timer" role="timer" aria-label="Time remaining">30:00</div></div>
<main class="wrap"><div class="intro"><p><b>30 minutes · 14 questions · 44 marks.</b> Calculator allowed (Degree mode). Questions 1–12: choose one answer (2 marks each). Questions 13–14: type numbers in the boxes. Answers are marked automatically when you press <b>Submit</b> or when time runs out.</p>
<p lang="ar" dir="rtl">30 دقيقة · 14 سؤالاً · 44 درجة. الآلة الحاسبة مسموحة (وضع الدرجات). الأسئلة 1–12: اختر إجابة واحدة. السؤالان 13–14: اكتب الأعداد في المربعات. يتم التصحيح تلقائياً عند الضغط على «تسليم» أو عند انتهاء الوقت.</p>
<p class="lmsnote" id="lms"></p></div><div class="result" id="result" hidden></div>
${mcqHtml}
${q13}
${q14}
</main><div class="bar"><span class="answered" id="answered"></span><button id="submit" type="button">Submit · تسليم</button></div>
<script>var ENC="${encoded}";</script><script>${CLIENT}</script></body></html>`;

const manifest = `<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="G10A_TERM1_MIRROR_QUIZ_30MIN" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG-G10A">
    <organization identifier="ORG-G10A">
      <title>Grade 10 Advanced - Term 1 mirror quiz (30 min)</title>
      <item identifier="ITEM-G10A-QUIZ" identifierref="RES-G10A-QUIZ" isvisible="true">
        <title>Term 1 mirror quiz - 14 auto-marked questions</title>
        <adlcp:masteryscore>60</adlcp:masteryscore>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-G10A-QUIZ" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
    </resource>
  </resources>
</manifest>
`;

const stage = await mkdtemp(resolve(tmpdir(), 'scorm-g10a-'));
await writeFile(resolve(stage, 'index.html'), html);
await writeFile(resolve(stage, 'imsmanifest.xml'), manifest);
const zipPath = resolve(root, 'public/worksheets/grade-10-advanced-term1-mirror-scorm12.zip');
await rm(zipPath, {force: true});
execFileSync('zip', ['-X', '-q', '-j', zipPath, resolve(stage, 'imsmanifest.xml'), resolve(stage, 'index.html')]);
await rm(stage, {recursive: true, force: true});
console.log(`SCORM 1.2 package: ${zipPath} (12 MCQs + 2 auto-marked written items, 44 marks, mastery 60%)`);
