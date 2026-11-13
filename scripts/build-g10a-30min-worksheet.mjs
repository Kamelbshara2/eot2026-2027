// Grade 10 Advanced: 30-minute mixed Term 1 review worksheet (user request, 13 Nov 2026).
// Questions come unchanged from public/data/study/10A1.json (revision-booklet textbook exercises
// not used in the printed study booklet). Every key below is checked against the bank, and the
// numeric ones are recomputed here, so the sheet can never disagree with the website.
// Run: PLAYWRIGHT_MODULE=/opt/node-tools/node_modules/playwright/index.mjs node scripts/build-g10a-30min-worksheet.mjs
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import katex from 'katex';
import {translate, bidi} from '../lib/study-translate.js';

const root = resolve(import.meta.dirname, '..');
const bank = JSON.parse(await readFile(resolve(root, 'public/data/study/10A1.json'), 'utf8'));
const tr = JSON.parse(await readFile(resolve(root, 'public/data/study/translations-ar.json'), 'utf8'));
const Q = Object.fromEntries(bank.questions.map(q => [q.id, q]));
const LO = Object.fromEntries(bank.learning_outcomes.map(o => [o.id, o]));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const tex = (s, display = false) => katex.renderToString(String(s), {throwOnError: true, displayMode: display, output: 'html'});
const deg = x => x * Math.PI / 180, r1 = x => Math.round(x * 10) / 10;

// id, minutes, key, worked line for the answer key, optional numeric recomputation
const PART_A = [
  ['G10A-REV-Q01-MCQ-05', 1, 'D', String.raw`6k^2+4k^2=10k^2,\ 2k-5k=-3k,\ +9 \Rightarrow 10k^2-3k+9`],
  ['G10A-REV-Q02-MCQ-02', 1, 'A', String.raw`24d^2-42d-20d+35=24d^2-62d+35`],
  ['G10A-REV-Q03-MCQ-02', 1, 'C', String.raw`9q(5p-3)-10(5p-3)=(9q-10)(5p-3)`],
  ['G10A-REV-Q04-MCQ-02', 1, 'C', String.raw`(-20)(-2)=40,\ -20+(-2)=-22 \Rightarrow (x-20)(x-2)`],
  ['G10A-REV-Q09-MCQ-01', 1, 'D', String.raw`C'=2.5\,(5,\,2)=(12.5,\,5)`, () => [2.5 * 5, 2.5 * 2], [12.5, 5]],
  ['G10A-REV-Q15-MCQ-04', 1, 'D', String.raw`\sqrt{3\cdot 24}=\sqrt{72}=\sqrt{36\cdot 2}=6\sqrt2`, () => Math.sqrt(72), 6 * Math.SQRT2],
  ['G10A-REV-Q12-MCQ-03', 2, 'B', String.raw`4\tfrac12\text{ ft}=4.5,\ 3\tfrac13\text{ ft}=\tfrac{10}{3};\ \tfrac{h}{100}=\tfrac{4.5}{10/3}\Rightarrow h=135\text{ ft}`, () => 100 * 4.5 / (10 / 3), 135],
  ['G10A-REV-Q14-MCQ-01', 2, 'B', String.raw`\tfrac{ST}{FG}=\tfrac{SH}{FJ}\Rightarrow \tfrac{6}{FG}=\tfrac57\Rightarrow FG=8.4`, () => 6 * 7 / 5, 8.4],
  ['G10A-REV-Q16-MCQ-03', 2, 'A', String.raw`(\sqrt5)^2+(\sqrt{12})^2=17>13=(\sqrt{13})^2\Rightarrow\text{acute}`],
  ['G10A-REV-Q17-MCQ-01', 2, 'C', String.raw`h=40\sin30^\circ=20\text{ ft}\ \ (30^\circ\text{-}60^\circ\text{-}90^\circ:\ \text{half the hypotenuse})`, () => 40 * Math.sin(deg(30)), 20],
  ['G10A-REV-Q19-MCQ-02', 2, 'D', String.raw`\tan19^\circ=\tfrac{120}{d}\Rightarrow d=\tfrac{120}{\tan19^\circ}\approx348.5\text{ ft}`, () => r1(120 / Math.tan(deg(19))), 348.5],
  ['G10A-REV-Q20-MCQ-02', 2, 'C', String.raw`A=\tfrac12(9)(11)\sin46^\circ\approx35.6\text{ yd}^2`, () => r1(0.5 * 9 * 11 * Math.sin(deg(46))), 35.6],
];
const FRQ_A = 'G10A-REV-Q21-FRQ-02', FRQ_B = 'G10A-REV-Q25-FRQ-02';

// ---- checks: keys match the bank, numbers recompute, written answers recompute
for (const [id, , key, , f, want] of PART_A) {
  const q = Q[id];
  if (!q || q.type !== 'mcq') throw Error(`Missing MCQ ${id}`);
  if (q.answer.correct_option_id !== key) throw Error(`${id}: sheet key ${key} ≠ bank ${q.answer.correct_option_id}`);
  if (f) { const got = f(); const ok = Array.isArray(want) ? want.every((w, i) => Math.abs(got[i] - w) < 1e-9) : Math.abs(got - want) < 1e-9; if (!ok) throw Error(`${id}: recomputed ${got} ≠ ${want}`); }
}
const sinB = 4 * Math.sin(deg(30)) / 3, B1 = Math.asin(sinB) * 180 / Math.PI, B2 = 180 - B1, C1 = 150 - B1, C2 = 150 - B2;
const c1 = 3 * Math.sin(deg(C1)) / Math.sin(deg(30)), c2 = 3 * Math.sin(deg(C2)) / Math.sin(deg(30));
const tri = {B1: Math.round(B1), C1: Math.round(C1), c1: r1(c1), B2: Math.round(B2), C2: Math.round(C2), c2: r1(c2)};
if (JSON.stringify(tri) !== JSON.stringify({B1: 42, C1: 108, c1: 5.7, B2: 138, C2: 12, c2: 1.2})) throw Error('Law of Sines recomputation changed: ' + JSON.stringify(tri));
if (!Q[FRQ_B].parts[1].answer.model_answer_and_marking.includes('c≈5.7') || !Q[FRQ_B].parts[1].answer.model_answer_and_marking.includes('c≈1.2')) throw Error('Bank model answer for Q14 changed');
if (Q[FRQ_A].parts[0].answer.math_latex.replace(/\\left|\\right|\s/g, '') !== '2(4a-5b)(4a+5b)') throw Error('Bank model answer for Q13 changed');

// ---- rendering helpers
const img = async id => {
  const a = bank.assets[id];
  const bytes = await readFile(resolve(root, 'public', a.src));
  const mime = a.src.endsWith('.svg') ? 'image/svg+xml' : 'image/png';
  return `<img class="fig" src="data:${mime};base64,${bytes.toString('base64')}" alt="${esc(a.alt_text)}">`;
};
const ar = (kind, text) => { const t = translate(tr, kind, text); return t ? `<p class="ar" lang="ar" dir="rtl">${bidi(esc(t))}</p>` : ''; };
const loTag = q => { const o = LO[q.learning_outcome_id]; return `<span class="lo">${o.id} · ${esc(o.title)}<bdi class="lo-ar" lang="ar" dir="rtl">${esc(o.title_ar)}</bdi></span>`; };

async function mcqCard(id, n, minutes) {
  const q = Q[id];
  const figs = (await Promise.all((q.diagram_asset_ids || []).map(img))).join('');
  const opts = q.options.map(o => `<div class="opt"><b>${o.id}</b><span>${o.math_latex ? tex(o.math_latex) : esc(o.text)}</span></div>`).join('');
  return `<section class="q mcq"><header><span class="num">${n}</span>${loTag(q)}<span class="time">≈ ${minutes} min · 2 marks</span></header>
<p class="stem">${esc(q.instruction)}</p>${ar('instruction', q.instruction)}
${q.math_latex ? `<div class="math">${tex(q.math_latex.replace(/\b(and|or)\b/g, '\\text{ $1 }'), true)}</div>` : ''}${figs ? `<div class="figs">${figs}</div>` : ''}
<div class="opts">${opts}</div><div class="work"><span>Working · الحل</span></div></section>`;
}

const head = (sub) => `<div class="running"><span>Math 100 · Grade 10 Advanced · Term 1</span><span>${sub}</span></div>`;
const foot = (p, total) => `<div class="foot"><span>Term 1 review worksheet · أ. كامل</span><span>${p} / ${total}</span></div>`;

const cardsA = [];
for (const [i, [id, minutes]] of PART_A.entries()) cardsA.push(await mcqCard(id, i + 1, minutes));
const qa = Q[FRQ_A], qb = Q[FRQ_B];
const total = 4;

const page1 = `<section class="page">${head('Student sheet · ورقة الطالب')}
<div class="title"><div><h1>Term 1 Review Worksheet</h1><p class="sub">Mixed outcomes · 30 minutes · calculator allowed (Casio fx-991EX, Degree mode)</p></div>
<div class="title-ar" lang="ar" dir="rtl"><h2>ورقة عمل مراجعة الفصل الأول</h2><p>مخرجات متنوعة · 30 دقيقة · الآلة الحاسبة مسموحة</p></div></div>
<div class="fields"><label>Name · الاسم<span></span></label><label>Class · الشعبة<span></span></label><label>Date · التاريخ<span></span></label><label class="score">Score · الدرجة<span>/ 44</span></label></div>
<div class="plan"><div><b>Part A</b> · 12 multiple-choice · 24 marks · <b>18 min</b><br><span lang="ar" dir="rtl">الجزء أ: 12 سؤال اختيار من متعدد · 18 دقيقة — ضع دائرة حول رمز الإجابة</span></div>
<div><b>Part B</b> · 2 written questions · 20 marks · <b>12 min</b><br><span lang="ar" dir="rtl">الجزء ب: سؤالان كتابيان · 12 دقيقة — اكتب خطوات الحل كاملة</span></div>
<div class="timeline"><span style="flex:6">Q1–6 · 6 min</span><span style="flex:12">Q7–12 · 12 min</span><span style="flex:4">Q13 · 4</span><span style="flex:8">Q14 · 8 min</span></div></div>
<h3 class="part">Part A · Multiple choice · الجزء أ</h3><div class="grid">${cardsA.slice(0, 6).join('')}</div>${foot(1, total)}</section>`;

const page2 = `<section class="page">${head('Part A continued · تابع الجزء أ')}<div class="grid">${cardsA.slice(6).join('')}</div>${foot(2, total)}</section>`;

const lines = n => `<div class="lines">${'<i></i>'.repeat(n)}</div>`;
const page3 = `<section class="page">${head('Part B · الجزء ب')}
<h3 class="part">Part B · Written questions · show all steps · الجزء ب: اكتب الخطوات كاملة</h3>
<section class="q frq"><header><span class="num">13</span>${loTag(qa)}<span class="time">≈ 4 min · 10 marks</span></header>
<p class="stem">${esc(qa.instruction)} ${esc(qa.parts[0].prompt)}</p>${ar('instruction', qa.instruction)}
<div class="math">${tex(qa.math_latex, true)}</div>
<div class="steps-hint">Step 1 GCF → Step 2 pattern ${tex('A^2-B^2=(A-B)(A+B)')} → Step 3 check by expanding</div>${lines(5)}</section>
<section class="q frq"><header><span class="num">14</span>${loTag(qb)}<span class="time">≈ 8 min · 10 marks</span></header>
<p class="stem">${esc(qb.instruction)}</p>${ar('instruction', qb.instruction)}
<div class="math">${tex(qb.math_latex, true)}</div>
<p class="part-label"><b>(a)</b> ${esc(qb.parts[0].prompt)} <span class="m">[4]</span></p>
<div class="steps-hint">Compare ${tex('h=b\\sin A')} with ${tex('a')} and ${tex('b')}, then find ${tex('\\sin B=\\dfrac{b\\sin A}{a}')}</div>${lines(3)}
<p class="part-label"><b>(b)</b> ${esc(qb.parts[1].prompt)} <span class="m">[6]</span></p>
<table class="tri"><thead><tr><th></th><th>${tex('B')}</th><th>${tex('C')}</th><th>${tex('c')}</th></tr></thead>
<tbody><tr><th>Triangle 1 · المثلث 1</th><td></td><td></td><td></td></tr><tr><th>Triangle 2 · المثلث 2</th><td></td><td></td><td></td></tr></tbody></table>
${lines(4)}</section>
<p class="end">End of worksheet · انتهت الورقة — check every answer if time remains.</p>${foot(3, total)}</section>`;

const keyRows = PART_A.map(([id, , key, work], i) => `<tr><td class="kn">${i + 1}</td><td class="kk">${key}</td><td>${tex(work)}</td><td class="klo">${Q[id].learning_outcome_id}</td></tr>`).join('');
const page4 = `<section class="page key">${head('Teacher key · مفتاح المعلم — do not print for students')}
<h3 class="part">Part A · Answers and one-line working</h3>
<table class="keytab"><thead><tr><th>Q</th><th>Key</th><th>Working</th><th>LO</th></tr></thead><tbody>${keyRows}</tbody></table>
<h3 class="part">Part B · Model answers and marking</h3>
<div class="model"><p><b>13.</b> ${tex('32a^2-50b^2=2(16a^2-25b^2)=2(4a-5b)(4a+5b)')}</p>
<p class="mk">Check: ${tex('2(16a^2+20ab-20ab-25b^2)=32a^2-50b^2')}. Marks: correct method incl. GCF (5); complete factors and check (5).</p>
<p><b>14 (a).</b> ${tex('h=b\\sin A=4\\sin30^\\circ=2')}; since ${tex('h<a<b')} (2 &lt; 3 &lt; 4) there are <b>two triangles</b>. ${tex('\\sin B=\\dfrac{4\\sin30^\\circ}{3}=0.6667')}</p>
<p class="mk">Marks: correct ratio (2); number of solutions with justification (2).</p>
<p><b>14 (b).</b> ${tex(`B_1=\\sin^{-1}(0.6667)\\approx${B1.toFixed(2)}^\\circ\\approx${tri.B1}^\\circ,\\ C_1\\approx${tri.C1}^\\circ,\\ c_1=\\dfrac{3\\sin C_1}{\\sin30^\\circ}\\approx${tri.c1}`)}</p>
<p>${tex(`B_2=180^\\circ-B_1\\approx${tri.B2}^\\circ,\\ C_2\\approx${tri.C2}^\\circ,\\ c_2=\\dfrac{3\\sin C_2}{\\sin30^\\circ}\\approx${tri.c2}`)}</p>
<p class="mk">Use full-precision angles before rounding (sides to 0.1, angles to 1°). Marks: both triangles with remaining side (6).</p></div>
<p class="srcnote">Source: Grade 10 Advanced revision booklet (textbook exercises), as stored in the platform bank; none of these questions appear in the printed Term 1 study booklet. Keys match the website.</p>
${foot(4, total)}</section>`;

// ---- CSS: embedded KaTeX + Arabic fonts so the PDF is self-contained
let katexCss = await readFile(resolve(root, 'node_modules/katex/dist/katex.min.css'), 'utf8');
for (const m of [...katexCss.matchAll(/src:url\(fonts\/([^)]*\.woff2)\) format\("woff2"\)[^;}]*[;}]/g)]) {
  const bytes = await readFile(resolve(root, 'node_modules/katex/dist/fonts', m[1]));
  katexCss = katexCss.replace(m[0], `src:url(data:font/woff2;base64,${bytes.toString('base64')}) format("woff2")${m[0].endsWith('}') ? '}' : ';'}`);
}
const arR = (await readFile(resolve(root, 'public/fonts/NotoSansArabic-Regular.woff'))).toString('base64');
const arB = (await readFile(resolve(root, 'public/fonts/NotoSansArabic-Bold.woff'))).toString('base64');
const css = `@font-face{font-family:NA;src:url(data:font/woff;base64,${arR}) format("woff");font-weight:400}@font-face{font-family:NA;src:url(data:font/woff;base64,${arB}) format("woff");font-weight:700}
@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,"NA",sans-serif;color:#111827;background:#e5e7eb}
[lang=ar],.ar{font-family:"NA",Arial,sans-serif}
.page{width:210mm;height:297mm;margin:0 auto 6mm;background:#fff;padding:11mm 12mm 14mm;position:relative;overflow:hidden;page-break-after:always}
.running{display:flex;justify-content:space-between;font-size:7.5pt;letter-spacing:.06em;text-transform:uppercase;color:#475569;border-bottom:1px solid #cbd5e1;padding-bottom:2mm;margin-bottom:3mm}
.foot{position:absolute;left:12mm;right:12mm;bottom:6mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#475569;border-top:1px solid #cbd5e1;padding-top:1.5mm}
.title{display:flex;justify-content:space-between;gap:6mm;align-items:flex-end}h1{font-size:19pt;margin:0;color:#0f2b46}.sub{margin:1mm 0 0;font-size:8.5pt;color:#334155}
.title-ar{text-align:right}.title-ar h2{margin:0;font-size:14pt;color:#0f2b46}.title-ar p{margin:1mm 0 0;font-size:8.5pt;color:#334155}
.fields{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:3mm;margin:3.5mm 0 3mm}.fields label{font-size:7.5pt;color:#334155;display:flex;flex-direction:column;gap:1mm}.fields span{display:block;height:8mm;border:1.2px solid #94a3b8;border-radius:1.5mm;text-align:right;padding:2mm 2mm 0;font-weight:700;color:#0f2b46}
.plan{display:grid;grid-template-columns:1fr 1fr;gap:1.5mm 4mm;background:#f1f5f9;border-left:3px solid #0f766e;padding:2.2mm 3mm;font-size:8pt;line-height:1.45}.plan [lang=ar]{display:block;font-size:7.6pt;color:#334155}
.timeline{grid-column:1/-1;display:flex;gap:1mm;margin-top:1mm}.timeline span{background:#0f766e;color:#fff;font-size:7pt;padding:.8mm 1.5mm;border-radius:1mm;text-align:center;white-space:nowrap}.timeline span:nth-child(n+3){background:#9a3412}
.part{font-size:10.5pt;margin:3.5mm 0 2mm;color:#0f2b46;border-bottom:2px solid #0f2b46;padding-bottom:1mm}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:3mm}
.q{border:1px solid #cbd5e1;border-radius:2mm;padding:2.2mm 2.8mm;break-inside:avoid;display:flex;flex-direction:column}
.q header{display:flex;align-items:center;gap:2mm;margin-bottom:1.2mm}.num{background:#0f2b46;color:#fff;font-weight:700;font-size:9pt;min-width:6.5mm;height:6.5mm;border-radius:1.5mm;display:inline-flex;align-items:center;justify-content:center}
.lo{font-size:6.6pt;color:#475569;flex:1;line-height:1.3}.lo-ar{display:block;font-size:6.6pt}.time{font-size:6.6pt;color:#9a3412;font-weight:700;white-space:nowrap}
.stem{margin:0;font-size:9pt;line-height:1.38}.ar{margin:.6mm 0 0;font-size:8pt;line-height:1.5;color:#334155;text-align:right}
.math{margin:1mm 0;font-size:10pt}.math .katex-display{margin:.8mm 0}
.figs{text-align:center;margin:1mm 0}.fig{max-height:27mm;max-width:100%}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:1.2mm 3mm;margin-top:1.2mm;font-size:9pt}.opt{display:flex;align-items:center;gap:1.8mm}.opt b{display:inline-flex;width:5mm;height:5mm;border:1.2px solid #334155;border-radius:50%;align-items:center;justify-content:center;font-size:7.5pt;flex:none}
.work{margin-top:1.5mm;flex:1;min-height:9mm;border-top:1px dashed #cbd5e1;font-size:6.5pt;color:#94a3b8;padding-top:.6mm}
.frq{margin-bottom:3.5mm}.frq .stem{font-size:9.6pt}.steps-hint{font-size:7.8pt;color:#0f766e;background:#f0fdfa;border-radius:1.5mm;padding:1.2mm 2mm;margin:1mm 0}
.part-label{margin:2mm 0 .5mm;font-size:9.3pt}.m{color:#9a3412;font-weight:700;font-size:8pt}
.lines i{display:block;height:8.2mm;border-bottom:1px solid #cbd5e1}
table.tri{border-collapse:collapse;margin:2mm 0;width:72%;font-size:9pt}.tri th,.tri td{border:1.2px solid #94a3b8;padding:1.8mm 2.5mm;text-align:center}.tri td{height:9mm;width:22%}.tri tbody th{text-align:left;font-weight:600;font-size:8.2pt;background:#f8fafc}
.end{text-align:center;font-size:8pt;color:#475569;margin-top:2mm}
.keytab{width:100%;border-collapse:collapse;font-size:8.6pt}.keytab th,.keytab td{border-bottom:1px solid #e2e8f0;padding:1.6mm 2mm;text-align:left;vertical-align:middle}.kn{width:8mm;font-weight:700}.kk{width:11mm;font-weight:700;color:#0f766e;font-size:10pt}.klo{width:12mm;color:#64748b;font-size:7.5pt}
.model p{margin:1.4mm 0;font-size:9pt;line-height:1.5}.mk{color:#475569;font-size:8pt!important}.srcnote{font-size:7pt;color:#64748b;margin-top:4mm}
@media print{body{background:#fff}.page{margin:0}}`;

const html = `<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>Grade 10 Advanced · Term 1 review worksheet · 30 minutes</title><style>${katexCss}\n${css}</style></head><body>${page1}${page2}${page3}${page4}</body></html>`;
const out = resolve(root, 'public/worksheets/grade-10-advanced-term1-30min-worksheet');
await writeFile(out + '.html', html);

// ---- PDF export with page-bound checks
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.setContent(html, {waitUntil: 'load'});
  await page.emulateMedia({media: 'print'});
  await page.evaluate(() => document.fonts.ready);
  const problems = await page.evaluate(() => [...document.querySelectorAll('.page')].flatMap((p, i) => {
    const bottom = p.getBoundingClientRect().bottom - 14 * 96 / 25.4; // keep clear of the footer band
    return [...p.querySelectorAll('.q,.part,.end,.keytab,.model,.srcnote')].filter(el => el.getBoundingClientRect().bottom > bottom + 1).map(el => `page ${i + 1}: ${el.className} overflows`);
  }));
  const broken = await page.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).length);
  if (problems.length || broken) throw Error([...problems, broken ? `${broken} broken images` : ''].join('; '));
  await page.pdf({path: out + '.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true});
} finally { await browser.close(); }
console.log(`Worksheet: 12 MCQs + 2 written questions (30 min), 3 student pages + 1 teacher key page → ${out}.pdf`);
