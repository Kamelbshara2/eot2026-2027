// Shared builders for a class "review pack": a 30-minute printable worksheet (bank questions, PDF)
// and a SCORM 1.2 auto-marked quiz of authored mirror questions. Used by
// scripts/build-g9g-review-pack.mjs and scripts/build-g10g-review-pack.mjs (10A1 has its own scripts).
import {readFile, writeFile, rm, mkdtemp} from 'node:fs/promises';
import {resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {execFileSync} from 'node:child_process';
import katex from 'katex';
import {translate, bidi} from '../lib/study-translate.js';

export const root = resolve(import.meta.dirname, '..');
export const tex = (s, display = false) => katex.renderToString(String(s), {throwOnError: true, displayMode: display, output: 'html'});
export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
export const near = (a, b, eps = 1e-9) => Math.abs(a - b) < eps;
export const check = (cond, msg) => { if (!cond) throw Error('Check failed: ' + msg); };
export const same = (f, g, pts = [-3, -1.5, 0.5, 2, 7]) => pts.every(t => near(f(t), g(t), 1e-7));

async function fontsCss() {
  let k = await readFile(resolve(root, 'node_modules/katex/dist/katex.min.css'), 'utf8');
  for (const m of [...k.matchAll(/src:url\(fonts\/([^)]*\.woff2)\) format\("woff2"\)[^;}]*[;}]/g)]) {
    const bytes = await readFile(resolve(root, 'node_modules/katex/dist/fonts', m[1]));
    k = k.replace(m[0], `src:url(data:font/woff2;base64,${bytes.toString('base64')}) format("woff2")${m[0].endsWith('}') ? '}' : ';'}`);
  }
  const r = (await readFile(resolve(root, 'public/fonts/NotoSansArabic-Regular.woff'))).toString('base64');
  const b = (await readFile(resolve(root, 'public/fonts/NotoSansArabic-Bold.woff'))).toString('base64');
  return `${k}\n@font-face{font-family:NA;src:url(data:font/woff;base64,${r}) format("woff");font-weight:400}@font-face{font-family:NA;src:url(data:font/woff;base64,${b}) format("woff");font-weight:700}`;
}

// ---------------------------------------------------------------- worksheet (PDF)
const WS_CSS = `@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,"NA",sans-serif;color:#111827;background:#e5e7eb}
[lang=ar],.ar{font-family:"NA",Arial,sans-serif}
.page{width:210mm;height:297mm;margin:0 auto 6mm;background:#fff;padding:11mm 12mm 14mm;position:relative;overflow:hidden;page-break-after:always}
.running{display:flex;justify-content:space-between;font-size:7.5pt;letter-spacing:.06em;text-transform:uppercase;color:#475569;border-bottom:1px solid #cbd5e1;padding-bottom:2mm;margin-bottom:3mm}
.foot{position:absolute;left:12mm;right:12mm;bottom:6mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#475569;border-top:1px solid #cbd5e1;padding-top:1.5mm}
.title{display:flex;justify-content:space-between;gap:6mm;align-items:flex-end}h1{font-size:19pt;margin:0;color:#0f2b46}.sub{margin:1mm 0 0;font-size:8.5pt;color:#334155}
.title-ar{text-align:right}.title-ar h2{margin:0;font-size:14pt;color:#0f2b46}.title-ar p{margin:1mm 0 0;font-size:8.5pt;color:#334155}
.fields{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:3mm;margin:3.5mm 0 3mm}.fields label{font-size:7.5pt;color:#334155;display:flex;flex-direction:column;gap:1mm}.fields span{display:block;height:8mm;border:1.2px solid #94a3b8;border-radius:1.5mm;text-align:right;padding:2mm 2mm 0;font-weight:700;color:#0f2b46}
.plan{display:grid;grid-template-columns:1fr 1fr;gap:1.5mm 4mm;background:#f1f5f9;border-left:3px solid #0f766e;padding:2.2mm 3mm;font-size:8pt;line-height:1.45}.plan [lang=ar]{display:block;font-size:7.6pt;color:#334155}
.timeline{grid-column:1/-1;display:flex;gap:1mm;margin-top:1mm}.timeline span{background:#0f766e;color:#fff;font-size:7pt;padding:.8mm 1.5mm;border-radius:1mm;text-align:center;white-space:nowrap}.timeline span.b{background:#9a3412}
.part{font-size:10.5pt;margin:3.5mm 0 2mm;color:#0f2b46;border-bottom:2px solid #0f2b46;padding-bottom:1mm}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:3mm}
.q{border:1px solid #cbd5e1;border-radius:2mm;padding:2.2mm 2.8mm;break-inside:avoid;display:flex;flex-direction:column}
.q header{display:flex;align-items:center;gap:2mm;margin-bottom:1.2mm}.num{background:#0f2b46;color:#fff;font-weight:700;font-size:9pt;min-width:6.5mm;height:6.5mm;border-radius:1.5mm;display:inline-flex;align-items:center;justify-content:center}
.lo{font-size:6.6pt;color:#475569;flex:1;line-height:1.3}.lo-ar{display:block;font-size:6.6pt}.time{font-size:6.6pt;color:#9a3412;font-weight:700;white-space:nowrap}
.stem{margin:0;font-size:9pt;line-height:1.38}.ar{margin:.6mm 0 0;font-size:8pt;line-height:1.5;color:#334155;text-align:right}
.math{margin:1mm 0;font-size:10pt}.math .katex-display{margin:.8mm 0}
.figs{text-align:center;margin:1mm 0}.fig{max-height:30mm;max-width:100%}.frq .fig{max-height:52mm}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:1.2mm 3mm;margin-top:1.2mm;font-size:9pt}.opts.wide{grid-template-columns:1fr}.opt{display:flex;align-items:center;gap:1.8mm}.opt b{display:inline-flex;width:5mm;height:5mm;border:1.2px solid #334155;border-radius:50%;align-items:center;justify-content:center;font-size:7.5pt;flex:none}
.work{margin-top:1.5mm;flex:1;min-height:9mm;border-top:1px dashed #cbd5e1;font-size:6.5pt;color:#94a3b8;padding-top:.6mm}
.frq{margin-bottom:3.5mm}.frq .stem{font-size:9.6pt}.steps-hint{font-size:7.8pt;color:#0f766e;background:#f0fdfa;border-radius:1.5mm;padding:1.2mm 2mm;margin:1mm 0}
.part-label{margin:2mm 0 .5mm;font-size:9.3pt}.m{color:#9a3412;font-weight:700;font-size:8pt}
.lines i{display:block;height:8.2mm;border-bottom:1px solid #cbd5e1}
.end{text-align:center;font-size:8pt;color:#475569;margin-top:2mm}
.keytab{width:100%;border-collapse:collapse;font-size:8.6pt}.keytab th,.keytab td{border-bottom:1px solid #e2e8f0;padding:1.6mm 2mm;text-align:left;vertical-align:middle}.kn{width:8mm;font-weight:700}.kk{width:11mm;font-weight:700;color:#0f766e;font-size:10pt}.klo{width:12mm;color:#64748b;font-size:7.5pt}
.model p{margin:1.4mm 0;font-size:9pt;line-height:1.5}.mk{color:#475569;font-size:8pt!important}.srcnote{font-size:7pt;color:#64748b;margin-top:4mm}
@media print{body{background:#fff}.page{margin:0}}`;

export async function loadBank(classroom) {
  const bank = JSON.parse(await readFile(resolve(root, `public/data/study/${classroom}.json`), 'utf8'));
  const tr = JSON.parse(await readFile(resolve(root, 'public/data/study/translations-ar.json'), 'utf8'));
  return {bank, tr, Q: Object.fromEntries(bank.questions.map(q => [q.id, q])), LO: Object.fromEntries(bank.learning_outcomes.map(o => [o.id, o]))};
}

/**
 * cfg: {classroom, slug, grade, gradeAr, partA:[{id, min, key, work, check?}], partB:[{id, minutes, parts:[{text, marks, hint?, lines}], extra?, mathOverride?}],
 *       keyB:[html], srcnote}
 */
export async function buildWorksheet(cfg) {
  const {bank, tr, Q, LO} = await loadBank(cfg.classroom);
  for (const a of cfg.partA) {
    const q = Q[a.id];
    check(q && q.type === 'mcq', `${a.id} is an MCQ in ${cfg.classroom}`);
    check(q.answer.correct_option_id === a.key, `${a.id}: sheet key ${a.key} = bank ${q.answer.correct_option_id}`);
    if (a.check) check(a.check(), `${a.id}: recomputation`);
  }
  for (const b of cfg.partB) check(Q[b.id] && Q[b.id].type === 'frq', `${b.id} is an FRQ`);
  const img = async id => { const a = bank.assets[id]; const bytes = await readFile(resolve(root, 'public', a.src)); return `<img class="fig" src="data:${a.src.endsWith('.svg') ? 'image/svg+xml' : 'image/png'};base64,${bytes.toString('base64')}" alt="${esc(a.alt_text)}">`; };
  const ar = text => { const t = translate(tr, 'instruction', text); return t ? `<p class="ar" lang="ar" dir="rtl">${bidi(esc(t))}</p>` : ''; };
  const loTag = q => { const o = LO[q.learning_outcome_id]; return `<span class="lo">${o.id} · ${esc(o.title)}<bdi class="lo-ar" lang="ar" dir="rtl">${esc(o.title_ar)}</bdi></span>`; };
  const mathOf = s => s.replace(/\b(and|or)\b/g, '\\text{ $1 }');
  const optHtml = o => o.math_latex ? tex('\\displaystyle ' + o.math_latex) : esc(o.text);
  const cards = [];
  for (const [i, a] of cfg.partA.entries()) {
    const q = Q[a.id];
    const figs = (await Promise.all((q.diagram_asset_ids || []).map(img))).join('');
    const wide = q.options.some(o => (o.math_latex || o.text).length > 26);
    cards.push(`<section class="q mcq"><header><span class="num">${i + 1}</span>${loTag(q)}<span class="time">≈ ${a.min} min · 2 marks</span></header>
<p class="stem">${esc(q.instruction)}</p>${ar(q.instruction)}${q.math_latex ? `<div class="math">${tex(mathOf(q.math_latex), true)}</div>` : ''}${figs ? `<div class="figs">${figs}</div>` : ''}
<div class="opts${wide ? ' wide' : ''}">${q.options.map(o => `<div class="opt"><b>${o.id}</b><span>${optHtml(o)}</span></div>`).join('')}</div><div class="work"><span>Working · الحل</span></div></section>`);
  }
  const lines = n => `<div class="lines">${'<i></i>'.repeat(n)}</div>`;
  const frqs = [];
  for (const [j, b] of cfg.partB.entries()) {
    const q = Q[b.id], marks = b.parts.reduce((s, p) => s + p.marks, 0);
    const figs = (await Promise.all((q.diagram_asset_ids || []).map(img))).join('');
    frqs.push(`<section class="q frq"><header><span class="num">${13 + j}</span>${loTag(q)}<span class="time">≈ ${b.minutes} min · ${marks} marks</span></header>
<p class="stem">${esc(q.instruction)}</p>${ar(q.instruction)}${q.math_latex ? `<div class="math">${tex(q.math_latex, true)}</div>` : ''}${figs ? `<div class="figs">${figs}</div>` : ''}
${b.parts.map((p, k) => `<p class="part-label">${b.parts.length > 1 ? `<b>(${'abcd'[k]})</b> ` : ''}${p.text} <span class="m">[${p.marks}]</span></p>${p.hint ? `<div class="steps-hint">${p.hint}</div>` : ''}${p.extra || ''}${lines(p.lines)}`).join('')}</section>`);
  }
  const minA = cfg.partA.reduce((s, a) => s + a.min, 0), minB = cfg.partB.reduce((s, b) => s + b.minutes, 0);
  check(minA + minB === 30, `time plan adds to 30 (got ${minA + minB})`);
  const marksB = cfg.partB.reduce((s, b) => s + b.parts.reduce((t, p) => t + p.marks, 0), 0), total = 24 + marksB;
  const split = cfg.firstPageCards ?? 6;
  const fastN = cfg.partA.filter(a => a.min === 1).length;
  const head = sub => `<div class="running"><span>Math 100 · ${esc(cfg.grade)} · Term 1</span><span>${sub}</span></div>`;
  const foot = (p, n) => `<div class="foot"><span>Term 1 review worksheet · أ. كامل</span><span>${p} / ${n}</span></div>`;
  const keyRows = cfg.partA.map((a, i) => `<tr><td class="kn">${i + 1}</td><td class="kk">${a.key}</td><td>${tex(a.work)}</td><td class="klo">${Q[a.id].learning_outcome_id}</td></tr>`).join('');
  const pages = [
    `<section class="page">${head('Student sheet · ورقة الطالب')}
<div class="title"><div><h1>Term 1 Review Worksheet</h1><p class="sub">${esc(cfg.grade)} · mixed outcomes · 30 minutes · calculator allowed</p></div>
<div class="title-ar" lang="ar" dir="rtl"><h2>ورقة عمل مراجعة الفصل الأول</h2><p>${esc(cfg.gradeAr)} · مخرجات متنوعة · 30 دقيقة · الآلة الحاسبة مسموحة</p></div></div>
<div class="fields"><label>Name · الاسم<span></span></label><label>Class · الشعبة<span></span></label><label>Date · التاريخ<span></span></label><label>Score · الدرجة<span>/ ${total}</span></label></div>
<div class="plan"><div><b>Part A</b> · 12 multiple-choice · 24 marks · <b>${minA} min</b><br><span lang="ar" dir="rtl">الجزء أ: 12 سؤال اختيار من متعدد · ${minA} دقيقة — ضع دائرة حول رمز الإجابة</span></div>
<div><b>Part B</b> · 2 written questions · ${marksB} marks · <b>${minB} min</b><br><span lang="ar" dir="rtl">الجزء ب: سؤالان كتابيان · ${minB} دقيقة — اكتب خطوات الحل كاملة</span></div>
<div class="timeline"><span style="flex:${fastN}">Q1–${fastN} · ${fastN} min</span><span style="flex:${minA - fastN}">Q${fastN + 1}–12 · ${minA - fastN} min</span>${cfg.partB.map((b, j) => `<span class="b" style="flex:${b.minutes}">Q${13 + j} · ${b.minutes} min</span>`).join('')}</div></div>
<h3 class="part">Part A · Multiple choice · الجزء أ</h3><div class="grid">${cards.slice(0, split).join('')}</div>FOOT</section>`,
    `<section class="page">${head('Part A continued · تابع الجزء أ')}<div class="grid">${cards.slice(split).join('')}</div>FOOT</section>`,
    `<section class="page">${head('Part B · الجزء ب')}<h3 class="part">Part B · Written questions · show all steps · الجزء ب: اكتب الخطوات كاملة</h3>${frqs.join('')}
<p class="end">End of worksheet · انتهت الورقة — check every answer if time remains.</p>FOOT</section>`,
    `<section class="page key">${head('Teacher key · مفتاح المعلم — do not print for students')}
<h3 class="part">Part A · Answers and one-line working</h3><table class="keytab"><thead><tr><th>Q</th><th>Key</th><th>Working</th><th>LO</th></tr></thead><tbody>${keyRows}</tbody></table>
<h3 class="part">Part B · Model answers and marking</h3><div class="model">${cfg.keyB.join('')}</div><p class="srcnote">${esc(cfg.srcnote)} Keys match the website.</p>FOOT</section>`,
  ].map((p, i, all) => p.replace('FOOT', foot(i + 1, all.length)));
  const html = `<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>${esc(cfg.grade)} · Term 1 review worksheet · 30 minutes</title><style>${await fontsCss()}\n${WS_CSS}</style></head><body>${pages.join('')}</body></html>`;
  const out = resolve(root, `public/worksheets/${cfg.slug}-term1-30min-worksheet`);
  await writeFile(out + '.html', html);
  const {chromium} = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setContent(html, {waitUntil: 'load'});
    await page.emulateMedia({media: 'print'});
    await page.evaluate(() => document.fonts.ready);
    const problems = await page.evaluate(() => [...document.querySelectorAll('.page')].flatMap((p, i) => {
      const bottom = p.getBoundingClientRect().bottom - 14 * 96 / 25.4;
      return [...p.querySelectorAll('.q,.part,.end,.keytab,.model,.srcnote')].filter(el => el.getBoundingClientRect().bottom > bottom + 1).map(el => `page ${i + 1}: ${el.className} overflows`);
    }));
    const broken = await page.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).length);
    if (problems.length || broken) throw Error([...problems, broken ? `${broken} broken images` : ''].join('; '));
    await page.pdf({path: out + '.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true});
  } finally { await browser.close(); }
  console.log(`Worksheet ${cfg.classroom}: 12 MCQs + ${cfg.partB.length} written, ${total} marks → ${out}.pdf`);
  return out + '.pdf';
}

// ---------------------------------------------------------------- SCORM 1.2 quiz
const SC_CSS = `:root{--ink:#111827;--muted:#475569;--line:#cbd5e1;--brand:#0f2b46;--ok:#166534;--okbg:#dcfce7;--bad:#991b1b;--badbg:#fee2e2;--accent:#0f766e}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,"NA",sans-serif;color:var(--ink);background:#f1f5f9;line-height:1.45}[lang=ar]{font-family:"NA",Arial,sans-serif}
.top{position:sticky;top:0;z-index:5;background:var(--brand);color:#fff;padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.top h1{font-size:17px;margin:0}.top small{display:block;opacity:.85;font-weight:400}.timer{font:700 20px/1 Arial;background:#fff;color:var(--brand);border-radius:8px;padding:6px 10px;min-width:84px;text-align:center}.timer.low{background:#fde68a}
.wrap{max-width:860px;margin:0 auto;padding:14px 16px 90px}.intro{background:#fff;border-left:4px solid var(--accent);border-radius:8px;padding:10px 14px;font-size:14px}.intro p{margin:4px 0}.lmsnote{font-size:12px;color:var(--muted)}
.q{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}.q header{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.num{background:var(--brand);color:#fff;font-weight:700;border-radius:6px;min-width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center}.lo{flex:1;font-size:12px;color:var(--muted)}.mk{font-size:12px;font-weight:700;color:#9a3412}
.stem{margin:2px 0;font-size:16px}.ar{margin:2px 0 4px;font-size:14px;color:#334155;text-align:right}.math{font-size:17px}.fig{text-align:center;margin:4px 0}.fig svg{max-width:100%;height:auto}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}.opts.wide{grid-template-columns:1fr}@media(max-width:560px){.opts{grid-template-columns:1fr}}
.opt{display:flex;align-items:center;gap:8px;border:1.5px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer;font-size:16px;min-height:44px}
.opt input{position:absolute;opacity:0;pointer-events:none}.opt b{display:inline-flex;width:24px;height:24px;border-radius:50%;border:1.5px solid #334155;align-items:center;justify-content:center;font-size:13px;flex:none}
.opt:has(input:checked){border-color:var(--brand);background:#e0e7ff}.opt:has(input:checked) b{background:var(--brand);color:#fff}.opt:has(input:focus-visible){outline:3px solid #f59e0b}
.locked .opt.right{border-color:var(--ok);background:var(--okbg)}.locked .opt.right b{background:var(--ok);color:#fff;border-color:var(--ok)}.locked .opt.wrongpick{border-color:var(--bad);background:var(--badbg)}.locked .opt.wrongpick b{background:var(--bad);color:#fff;border-color:var(--bad)}
.fill{font-size:16px;margin:8px 0;line-height:2.2}.blank{font-size:16px;padding:6px;border:1.5px solid #64748b;border-radius:6px;text-align:center}.blank.ok,select.ok{border-color:var(--ok);background:var(--okbg)}.blank.no,select.no{border-color:var(--bad);background:var(--badbg)}
select{font-size:15px;padding:6px;border-radius:6px;border:1.5px solid #64748b;max-width:100%}.hint{font-size:12px;color:var(--muted);margin:4px 0}
.fb{margin-top:8px;font-size:14px}.fb:empty{display:none}.fb .res{font-weight:700}.fb.ok .res{color:var(--ok)}.fb.no .res{color:var(--bad)}.fb .work{background:#f8fafc;border-radius:6px;padding:6px 8px;margin-top:4px;overflow-x:auto}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;justify-content:center;align-items:center;flex-wrap:wrap}
button{font:700 16px Arial;padding:10px 20px;border-radius:8px;border:0;background:var(--accent);color:#fff;cursor:pointer;min-height:44px}button:disabled{opacity:.5;cursor:default}.answered{font-size:13px;color:var(--muted)}
.result{background:#fff;border:2px solid var(--brand);border-radius:10px;padding:12px 16px;margin:12px 0;font-size:16px}.result strong{font-size:22px}.locked .opt,.locked .blank,.locked select{pointer-events:none}`;

// Generic client: MCQs (2 marks each) + written items made of numeric/select fields.
const CLIENT = String.raw`
(function(){
var D=JSON.parse(decodeURIComponent(escape(atob(ENC.split('').reverse().join('')))));
var MAX=D.max,LIMIT=30*60,api=null,start=Date.now(),done=false,mastery=D.mastery;
function findAPI(w){var n=0;while(w&&!w.API&&w.parent&&w.parent!==w&&n<10){w=w.parent;n++}return w&&w.API?w.API:null}
api=findAPI(window)||(window.opener?findAPI(window.opener):null);
function sv(k,v){try{if(api)api.LMSSetValue(k,String(v))}catch(e){}}
function gv(k){try{return api?api.LMSGetValue(k):''}catch(e){return ''}}
var $=function(s){return document.querySelector(s)},$$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};
if(api){try{api.LMSInitialize('')}catch(e){}var nm=gv('cmi.core.student_name');if(nm)$('#who').textContent=nm;var ms=parseFloat(gv('cmi.student_data.mastery_score'));if(ms>0)mastery=ms;
 if(gv('cmi.core.lesson_status')==='not attempted')sv('cmi.core.lesson_status','incomplete');$('#lms').textContent='Connected to your LMS · results will be recorded.';}
else $('#lms').textContent='No LMS detected · practice mode (results are not recorded).';
function state(){var s={};$$('input[type=radio]:checked').forEach(function(i){s[i.name]=i.value});$$('.blank,select.field').forEach(function(i){if(i.value)s[i.id]=i.value});return s}
function elapsed(){return prior+Math.round((Date.now()-start)/1000)}
function save(){if(done)return;sv('cmi.suspend_data',JSON.stringify({a:state(),t:elapsed()}).slice(0,4000));count()}
var saved={};try{saved=JSON.parse(gv('cmi.suspend_data')||'{}')}catch(e){}
var a=saved.a||{},prior=saved.t||0;
Object.keys(a).forEach(function(k){var r=document.querySelector('input[name="'+k+'"][value="'+a[k]+'"]');if(r)r.checked=true;var b=document.getElementById(k);if(b&&(b.classList.contains('blank')||b.classList.contains('field')))b.value=a[k]});
function count(){var n=0;D.mcq.forEach(function(q){if(document.querySelector('input[name='+q.id+']:checked'))n++});D.written.forEach(function(w){if(w.fields.some(function(f){return document.getElementById(f.id).value}))n++});$('#answered').textContent=n+' / '+(D.mcq.length+D.written.length)+' answered'}
document.addEventListener('change',save);document.addEventListener('input',count);
var tick=setInterval(function(){var left=LIMIT-elapsed();if(left<=0){$('#timer').textContent='0:00';clearInterval(tick);if(!done)submit(true);return}
 $('#timer').textContent=Math.floor(left/60)+':'+('0'+left%60).slice(-2);$('#timer').classList.toggle('low',left<=300);if(left%30===0)save()},1000);
function num(v){v=String(v||'').trim().replace(/\s+/g,'').replace(',','.').replace(/[−–]/g,'-');if(v==='')return NaN;var m=v.match(/^(-?\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)$/);return m?Number(m[1])/Number(m[2]):Number(v)}
function hms(s){function p(x,l){x=String(x);while(x.length<l)x='0'+x;return x}return p(Math.floor(s/3600),4)+':'+p(Math.floor(s%3600/60),2)+':'+p(s%60,2)}
var ix=0;function inter(id,type,resp,pat,ok,w){var p='cmi.interactions.'+ix+'.';sv(p+'id',id);sv(p+'type',type);sv(p+'student_response',resp);sv(p+'correct_responses.0.pattern',pat);sv(p+'result',ok?'correct':'wrong');sv(p+'weighting',w);ix++}
function fb(el,ok,text,work){var f=el.querySelector('.fb');f.className='fb '+(ok?'ok':'no');f.innerHTML='<span class="res">'+text+'</span>'+(work?'<div class="work">'+work+'</div>':'')}
function submit(auto){
 if(done)return;if(!auto&&!confirm('Submit your answers now? · هل تريد تسليم إجاباتك الآن؟'))return;done=true;clearInterval(tick);
 var score=0;document.body.classList.add('locked');
 D.mcq.forEach(function(q){var el=document.getElementById(q.id),pick=(document.querySelector('input[name='+q.id+']:checked')||{}).value||'',ok=pick===q.key;if(ok)score+=2;
  el.querySelectorAll('.opt').forEach(function(o){if(o.dataset.l===q.key)o.classList.add('right');else if(o.dataset.l===pick)o.classList.add('wrongpick')});
  var why=pick&&!ok&&q.why['ABCD'.indexOf(pick)]?' — '+q.why['ABCD'.indexOf(pick)]:'';
  fb(el,ok,ok?'✓ Correct · +2':'✗ '+(pick?'You chose '+pick+why:'Not answered')+' · correct answer: '+q.key,q.work);inter(q.id,'choice',pick,q.key,ok,2)});
 D.written.forEach(function(w){var el=document.getElementById(w.id),pts=0,resp=[],pat=[];
  w.fields.forEach(function(f){var inp=document.getElementById(f.id),v=inp.value,ok;
   if(f.kind==='select')ok=v===f.answer;else{var x=num(v);ok=!isNaN(x)&&Math.abs(x-f.answer)<=(f.tol||0)+1e-9}
   inp.classList.add(ok?'ok':'no');if(ok)pts+=f.pts;resp.push(v);pat.push(f.kind==='select'?f.answer:f.answer)});
  score+=pts;fb(el,pts===w.max,(pts===w.max?'✓ ':'✗ ')+pts+' / '+w.max+(w.answerText?' · '+w.answerText:''),w.work);inter(w.id,'fill-in',resp.join(';').slice(0,250),pat.join(';'),pts===w.max,w.max)});
 var pct=Math.round(score/MAX*100),pass=pct>=mastery;
 sv('cmi.core.score.raw',pct);sv('cmi.core.score.min',0);sv('cmi.core.score.max',100);sv('cmi.core.lesson_status',pass?'passed':'failed');sv('cmi.core.session_time',hms(Math.round((Date.now()-start)/1000)));
 sv('cmi.suspend_data','');sv('cmi.core.exit','');try{if(api)api.LMSCommit('')}catch(e){}
 var r=$('#result');r.hidden=false;r.innerHTML='<strong>'+score+' / '+MAX+'</strong> ('+pct+'%) · '+(pass?'Passed · ناجح':'Keep practising · واصل التدريب')+(auto?'<br>Time is up: your answers were submitted automatically.':'')+'<br><span class="lmsnote">Scroll through the questions to see the correct answers and working.</span>';
 $('#submit').disabled=true;window.scrollTo({top:0,behavior:'smooth'});window.__score={raw:score,pct:pct,pass:pass};
}
$('#submit').addEventListener('click',function(){submit(false)});
function finish(){if(api){if(!done){save();sv('cmi.core.exit','suspend');sv('cmi.core.session_time',hms(Math.round((Date.now()-start)/1000)))}try{api.LMSCommit('');api.LMSFinish('')}catch(e){}api=null}}
window.addEventListener('pagehide',finish);window.addEventListener('beforeunload',finish);count();
})();`;

/**
 * cfg: {slug, grade, gradeAr, identifier, mastery,
 *   mcq:[{lo,title,en,ar,math?,fig?,opts[4 latex],key,work(latex),why[4]}],
 *   written:[{lo,title,en,ar,math?,fig?,body(html with [[num:id]] / [[sel:id]]),fields:[{id,kind:'num'|'select',answer,tol?,pts,options?:[[value,label]]}],work(html),hint?,answerText?}]}
 */
export async function buildScorm(cfg) {
  for (const q of cfg.mcq) check(q.opts.length === 4 && new Set(q.opts).size === 4 && 'ABCD'.includes(q.key) && q.why.length === 4 && q.why['ABCD'.indexOf(q.key)] === '', `${q.lo} options/why`);
  const written = cfg.written.map((w, j) => ({...w, id: `Q${cfg.mcq.length + 1 + j}`, max: w.fields.reduce((s, f) => s + f.pts, 0)}));
  const max = cfg.mcq.length * 2 + written.reduce((s, w) => s + w.max, 0);
  const field = (w, kind, id) => {
    const f = w.fields.find(x => x.id === id); check(f && f.kind === kind, `${w.id} field ${id}`);
    return kind === 'num' ? `<input class="blank" id="${id}" inputmode="decimal" autocomplete="off" style="width:${f.width || 4}em" aria-label="${esc(f.label || id)}">`
      : `<select class="field" id="${id}" aria-label="${esc(f.label || id)}"><option value="">— choose · اختر —</option>${f.options.map(([v, l]) => `<option value="${esc(v)}">${esc(l)}</option>`).join('')}</select>`;
  };
  const mcqHtml = cfg.mcq.map((q, i) => { const wide = q.opts.some(o => o.length > 28); return `<section class="q" id="Q${i + 1}"><header><span class="num">${i + 1}</span><span class="lo">${q.lo} · ${esc(q.title)}</span><span class="mk">2 marks</span></header>
<p class="stem">${esc(q.en)}</p><p class="ar" lang="ar" dir="rtl">${bidi(esc(q.ar))}</p>${q.math ? `<div class="math">${tex(q.math, true)}</div>` : ''}${q.fig ? `<div class="fig">${q.fig}</div>` : ''}
<div class="opts${wide ? ' wide' : ''}" role="radiogroup" aria-label="Question ${i + 1}">${q.opts.map((o, j) => { const L = 'ABCD'[j]; return `<label class="opt" data-l="${L}"><input type="radio" name="Q${i + 1}" value="${L}"><b>${L}</b><span>${tex('\\displaystyle ' + o)}</span></label>`; }).join('')}</div><div class="fb" aria-live="polite"></div></section>`; }).join('\n');
  const writtenHtml = written.map(w => `<section class="q" id="${w.id}"><header><span class="num">${w.id.slice(1)}</span><span class="lo">${w.lo} · ${esc(w.title)}</span><span class="mk">${w.max} marks</span></header>
<p class="stem">${esc(w.en)}</p><p class="ar" lang="ar" dir="rtl">${bidi(esc(w.ar))}</p>${w.math ? `<div class="math">${tex(w.math, true)}</div>` : ''}${w.fig ? `<div class="fig">${w.fig}</div>` : ''}
${w.body.replace(/\[\[(num|sel):([a-zA-Z0-9_]+)\]\]/g, (_, k, id) => field(w, k === 'num' ? 'num' : 'select', id))}${w.hint ? `<p class="hint">${w.hint}</p>` : ''}<div class="fb" aria-live="polite"></div></section>`).join('\n');
  for (const w of written) for (const f of w.fields) check(w.body.includes(`:${f.id}]]`), `${w.id}: field ${f.id} is placed`);
  const DATA = {max, mastery: cfg.mastery ?? 60,
    mcq: cfg.mcq.map((q, i) => ({id: `Q${i + 1}`, key: q.key, why: q.why, work: tex(q.work)})),
    written: written.map(w => ({id: w.id, max: w.max, work: w.work, answerText: w.answerText || '', fields: w.fields.map(({id, kind, answer, tol, pts}) => ({id, kind, answer, tol, pts}))}))};
  const encoded = Buffer.from(JSON.stringify(DATA)).toString('base64').split('').reverse().join('');
  const n = cfg.mcq.length + written.length, nm = cfg.mcq.length;
  const html = `<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(cfg.grade)} · Term 1 mirror quiz · 30 minutes</title><style>${await fontsCss()}\n${SC_CSS}</style></head><body>
<div class="top"><h1>${esc(cfg.grade)} · Term 1 mirror quiz<small><span lang="ar">اختبار أسئلة مماثلة · ${esc(cfg.gradeAr)}</span> · <span id="who"></span></small></h1><div class="timer" id="timer" role="timer" aria-label="Time remaining">30:00</div></div>
<main class="wrap"><div class="intro"><p><b>30 minutes · ${n} questions · ${max} marks.</b> Calculator allowed. Questions 1–${nm}: choose one answer (2 marks each). Questions ${nm + 1}–${n}: type your answers in the boxes (fractions like 3/4 are accepted). Answers are marked automatically when you press <b>Submit</b> or when time runs out.</p>
<p lang="ar" dir="rtl">30 دقيقة · ${n} سؤالاً · ${max} درجة. الآلة الحاسبة مسموحة. الأسئلة 1–${nm}: اختر إجابة واحدة. الأسئلة ${nm + 1}–${n}: اكتب إجابتك في المربعات (يمكن كتابة الكسور مثل 3/4). يتم التصحيح تلقائياً عند الضغط على «تسليم» أو عند انتهاء الوقت.</p>
<p class="lmsnote" id="lms"></p></div><div class="result" id="result" hidden></div>
${mcqHtml}
${writtenHtml}
</main><div class="bar"><span class="answered" id="answered"></span><button id="submit" type="button">Submit · تسليم</button></div>
<script>var ENC="${encoded}";</script><script>${CLIENT}</script></body></html>`;
  const manifest = `<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="${cfg.identifier}" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1">
      <title>${esc(cfg.grade)} - Term 1 mirror quiz (30 min)</title>
      <item identifier="ITEM-1" identifierref="RES-1" isvisible="true">
        <title>Term 1 mirror quiz - ${n} auto-marked questions</title>
        <adlcp:masteryscore>${cfg.mastery ?? 60}</adlcp:masteryscore>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
    </resource>
  </resources>
</manifest>
`;
  const stage = await mkdtemp(resolve(tmpdir(), 'scorm-'));
  await writeFile(resolve(stage, 'index.html'), html);
  await writeFile(resolve(stage, 'imsmanifest.xml'), manifest);
  const zipPath = resolve(root, `public/worksheets/${cfg.slug}-term1-mirror-scorm12.zip`);
  await rm(zipPath, {force: true});
  execFileSync('zip', ['-X', '-q', '-j', zipPath, resolve(stage, 'imsmanifest.xml'), resolve(stage, 'index.html')]);
  await rm(stage, {recursive: true, force: true});
  console.log(`SCORM 1.2 ${cfg.grade}: ${n} questions, ${max} marks → ${zipPath}`);
  return {zipPath, answers: DATA};
}
