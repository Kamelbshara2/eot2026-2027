// Printable sheet of every written (FRQ) question with suitable working space, graph paper and blank tables.
import {normalizeStudyMath} from './study-math.js';
import {bankMath} from './exam-bank-math.js';
import {questionWatermark} from './watermark.js';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const math = v => bankMath(normalizeStudyMath(v));

export function graphPaper([xmin, xmax, ymin, ymax], S = 16) {
  const w = (xmax - xmin) * S, h = (ymax - ymin) * S, X = x => (x - xmin) * S, Y = y => (ymax - y) * S;
  let g = '';
  for (let x = xmin; x <= xmax; x++) g += `<path d="M${X(x)} 0V${h}" stroke="#c4cfd6" stroke-width=".6"/>`;
  for (let y = ymin; y <= ymax; y++) g += `<path d="M0 ${Y(y)}H${w}" stroke="#c4cfd6" stroke-width=".6"/>`;
  let t = '';
  for (let x = xmin; x <= xmax; x++) if (x && x % 2 === 0) t += `<text x="${X(x)}" y="${Y(0) + 11}" text-anchor="middle">${x}</text>`;
  for (let y = ymin; y <= ymax; y++) if (y && y % 2 === 0) t += `<text x="${X(0) - 3}" y="${Y(y) + 3}" text-anchor="end">${y}</text>`;
  return `<svg class="print-graph" viewBox="-14 -6 ${w + 28} ${h + 24}" role="img" aria-label="Blank graph paper"><g>${g}</g><path d="M0 ${Y(0)}H${w}M${X(0)} 0V${h}" stroke="#1f3b4d" stroke-width="1.4"/><g font-size="9" font-family="Arial" fill="#1f3b4d">${t}<text x="${w + 6}" y="${Y(0) + 11}">x</text><text x="${X(0) + 4}" y="6">y</text></g></svg>`;
}
// blank number line (integer ticks) for inequality answers
export function numberLinePaper([lo, hi]) {
  const U = Math.min(34, 560 / (hi - lo)), w = (hi - lo) * U, X = x => x * U - lo * U;
  let t = '';
  for (let x = lo; x <= hi; x++) t += `<path d="M${X(x)} 12V24" stroke="#1f3b4d"/>` + ((hi - lo) <= 18 || x % 2 === 0 ? `<text x="${X(x)}" y="38" text-anchor="middle">${x}</text>` : '');
  return `<svg class="print-numberline" viewBox="-16 0 ${w + 32} 44" role="img" aria-label="Blank number line"><path d="M-12 18H${w + 12}" stroke="#1f3b4d" stroke-width="1.4"/><path d="M-14 18l8 -5v10zM${w + 14} 18l-8 -5v10z" fill="#1f3b4d"/><g font-size="10" font-family="Arial" fill="#1f3b4d">${t}</g></svg>`;
}
const blankTable = (n = 3) => `<table class="print-table"><tr><th>x</th>${'<td></td>'.repeat(n)}</tr><tr><th>y</th>${'<td></td>'.repeat(n)}</tr></table>`;
// value table from the question (x given, y left blank); the endpoint column is marked
const givenTable = t => `<table class="print-table">${t.caption ? `<caption>${t.caption_tex ? math(t.caption_tex) + ' ' : ''}${esc(t.caption)}</caption>` : ''}<tr><th>x</th>${t.xs.map((x, i) => `<td>${esc(x)}${i === t.end ? '<small> (endpoint)</small>' : ''}</td>`).join('')}</tr><tr><th>y</th>${'<td></td>'.repeat(t.xs.length)}</tr></table>`;
const lines = mm => `<div class="print-lines" style="height:${Math.max(42, Math.round(mm * 1.8))}mm"></div>`;

export function printableQuestion(bank, q, base = '/') {
  const figs = (q.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(a => `<figure><img src="${base}${esc(a.src)}" alt="${esc(a.alt_text)}"></figure>`).join('');
  const parts = q.parts.map(part => `<div class="print-part"><p><b>${esc(part.id)}.</b> ${esc(part.prompt)}${part.marks ? ` <span class="print-marks">(${part.marks})</span>` : ''}</p>${part.math_latex ? `<div class="study-math">${math(part.math_latex)}</div>` : ''}${(part.blanks?.tables || []).map(givenTable).join('')}${part.plot ? (part.plot.kind === 'line' ? blankTable(Math.max(3, part.plot.min_points)) : '') + graphPaper(part.plot.bounds) : ''}${part.numberline ? numberLinePaper(part.numberline.bounds) : ''}${lines(part.workspace?.height_mm || 30)}</div>`).join('');
  return `<article class="print-q"><header><b>${esc(q.display_number)}</b> <span>${esc(q.learning_outcome_id)} · ${q.source?.printed_page ? 'Reveal p. ' + esc(q.source.printed_page) + ' · ' : ''}${esc(q.source?.exercise)}</span></header><p lang="en" dir="ltr">${esc(q.math_latex ? q.instruction : q.stem)}</p>${q.math_latex ? `<div class="study-math">${math(q.math_latex)}</div>` : ''}${figs}${parts}</article>`;
}

const PDF = {'9G3': 'grade-9-general', '9A': 'grade-9-advanced', '10G3': 'grade-10-general', '10A1': 'grade-10-advanced', '11G': 'grade-11-general', '11A': 'grade-11-advanced', '12G': 'grade-12-general', '12A': 'grade-12-advanced'};
export function renderPrintSheet({root, bank, classroom, backHref, base = '/'}) {
  const groups = bank.learning_outcomes.map(lo => ({lo, qs: lo.question_ids.map(id => bank.questions.find(q => q.id === id)).filter(q => q?.type === 'frq')})).filter(g => g.qs.length);
  const total = groups.reduce((n, g) => n + g.qs.length, 0);
  root.innerHTML = `<section class="study-booklet print-sheet"><div class="study-toolbar no-print"><a href="${backHref}">← الملزمة · Booklet</a><button type="button" id="print-now" class="btn-primary">طباعة كل الأسئلة المقالية (${total}) · Print</button><a class="btn-primary" href="${base}worksheets/${PDF[classroom]}-term1-written-questions.pdf" download>تحميل PDF · Download PDF</a><span class="study-subtle">A4 · مساحات كتابة وأوراق رسم وجداول فارغة</span></div>
   <header class="print-head"><h1 lang="ar" dir="rtl">الأسئلة المقالية — ${esc(bank.title_ar || '')}</h1><p>الاسم: ____________________ &nbsp; المدرسة: ____________________ &nbsp; التاريخ: __________</p></header>
   ${groups.map(g => `<section class="print-lo"><h2><span>${esc(g.lo.id)}</span> ${esc(g.lo.title_ar)} · <small lang="en">${esc(g.lo.title)}</small></h2>${g.qs.map(q => `<div class="study-question-watermarked">${questionWatermark()}${printableQuestion(bank, q, base)}</div>`).join('')}</section>`).join('')}</section>`;
  root.querySelector('#print-now').onclick = () => window.print();
}
