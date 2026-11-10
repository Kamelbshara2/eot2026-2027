// Exports one A4 PDF per classroom with every written (FRQ) question, working space, blank tables and graph paper.
// Student version: no answers. Usage: PLAYWRIGHT_MODULE=<path to playwright index.mjs> CHROMIUM_PATH=<chromium> node scripts/export-written-pdfs.mjs
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {printableQuestion} from '../lib/study-print.js';
import {watermarkCss, questionWatermark} from '../lib/watermark.js';

const {chromium} = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const files = {'9G3': ['grade-9-general', '9 عام'], '10G3': ['grade-10-general', '10 عام'], '10A1': ['grade-10-advanced', '10 متقدم']};
const katexCss = pathToFileURL(resolve('node_modules/katex/dist/katex.min.css')).href;
const base = pathToFileURL(resolve('public')).href + '/';
const css = `*{box-sizing:border-box}body{font:12.5px/1.55 Arial,'Noto Sans Arabic',sans-serif;color:#14293b;margin:0}
h1{font-size:20px;margin:0 0 4px}.meta{font-size:12px;margin:6px 0 14px;border-bottom:2px solid #153f69;padding-bottom:8px}
.lo{margin:16px 0 4px;break-after:avoid}.lo h2{font-size:15px;margin:0;border-bottom:1.5px solid #153f69;padding-bottom:3px}.lo h2 span{background:#153f69;color:#fff;border-radius:5px;padding:1px 8px;font-size:12px}
.print-q{break-inside:avoid;margin:10px 0;padding:8px 10px;border:1px solid #b9c7d0;border-radius:8px;position:relative}
.print-q>header{font-size:11px;color:#486273}.print-q>header b{background:#153f69;color:#fff;border-radius:5px;padding:1px 8px}
.print-q p{margin:4px 0}.print-part{margin:8px 0}.print-marks{color:#486273;font-size:11px}
.print-lines{border:1px solid #9fb0ba;border-radius:5px;background:repeating-linear-gradient(#fff 0 8mm,#d5dee3 8mm calc(8mm + .5px))}
.print-table{border-collapse:collapse;margin:6px 0}.print-table th,.print-table td{border:1px solid #6b7f8b;width:21mm;height:8mm;text-align:center}.print-table th{width:9mm;background:#eef3f6}
.print-graph{display:block;width:100%;max-width:118mm;margin:6px 0}figure{margin:6px 0}figure img{max-width:100%;max-height:60mm}
.study-math{overflow:hidden;padding:4px 0;font-size:15px}${watermarkCss}.question-watermark{opacity:.1!important}.question-watermark span{color:#9aa!important}`;

const browser = await chromium.launch({headless: true, executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox']});
try {
  const page = await browser.newPage();
  for (const [classroom, [slug, label]] of Object.entries(files)) {
    const bank = JSON.parse(await readFile(`public/data/study/${classroom}.json`, 'utf8'));
    const groups = bank.learning_outcomes.map(lo => ({lo, qs: lo.question_ids.map(id => bank.questions.find(q => q.id === id)).filter(q => q?.type === 'frq')})).filter(g => g.qs.length);
    const total = groups.reduce((n, g) => n + g.qs.length, 0);
    const html = `<!doctype html><html lang="ar"><head><meta charset="utf-8"><link rel="stylesheet" href="${katexCss}"><style>${css}</style></head><body>
      <h1 dir="rtl">الأسئلة المقالية — ${label} · مذاكرة الهيكل الاختبار النهائي للفصل الاول</h1>
      <p class="meta" dir="rtl">الاسم: ______________________ &nbsp; المدرسة: ______________________ &nbsp; التاريخ: ____________ &nbsp; (${total} سؤالاً)</p>
      ${groups.map(g => `<section><div class="lo"><h2><span>${esc(g.lo.id)}</span> ${esc(g.lo.title_ar)} · <small>${esc(g.lo.title)}</small></h2></div>${g.qs.map(q => `<div class="wm">${questionWatermark()}${printableQuestion(bank, q, base)}</div>`).join('')}</section>`).join('')}</body></html>`;
    const tmp = resolve(`node_modules/.written-${classroom}.html`);
    await writeFile(tmp, html);
    await page.goto(pathToFileURL(tmp).href);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForLoadState('networkidle');
    const out = resolve(`public/worksheets/${slug}-term1-written-questions.pdf`);
    await page.pdf({path: out, format: 'A4', printBackground: true, margin: {top: '12mm', bottom: '14mm', left: '11mm', right: '11mm'}, displayHeaderFooter: true,
      headerTemplate: '<span></span>', footerTemplate: `<div style="width:100%;font-size:9px;color:#556;text-align:center">Math 100 · <span class="pageNumber"></span> / <span class="totalPages"></span> · 0502837825</div>`});
    console.log(classroom, total, 'questions ->', out);
  }
} finally { await browser.close(); }
