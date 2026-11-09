import {normalizeStudyMath} from './study-math.js';
import {bankMath} from './exam-bank-math.js';
import {fillMarkup, wireFill, solvedMarkup} from './study-fill.js';
import {buildQuiz, gradeQuiz, gradeQuestion, validQuiz, quizHash, parseQuizQuery, quizPool, partBlankList, QUIZ_SIZES} from './study-quiz.js';
import '../study-booklet.css';

const BASE = import.meta.env?.BASE_URL || '/';
const title = 'مذاكرة الهيكل الاختبار النهائي للفصل الاول';
const names = {'9G3': 'التاسع العام', '10G3': 'العاشر العام', '10A1': 'العاشر المتقدم'};
const KIND = {textbook_exercise: ['تمرين من الكتاب', 'Textbook exercise'], example_variant: ['نسخة من مثال الكتاب', 'Example variant'], concept_application: ['تطبيق على المفهوم', 'Concept application']};
const SECTIONS = [
  ['idea', '١', 'الفكرة', 'The idea', 'القاعدة التي تحتاجها'],
  ['example', '٢', 'مثال محلول', 'Worked example', 'سؤال كامل مع حله وطريقة الآلة الحاسبة'],
  ['helper', '٣', 'مساعد المذاكرة', 'Study helper', 'نحلّ معًا بخطوات وتلميحات'],
  ['practice', '٤', 'تدرّب بنفسك', 'Practise', 'أسئلة بفراغات وتحقق فوري'],
  ['quiz', '٥', 'اختبر نفسك', 'Check yourself', 'اختبار قصير على هذا المخرج']
];
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const math = value => bankMath(normalizeStudyMath(value));
const pair = (ar, en) => `<div class="study-ar" lang="ar" dir="rtl">${escape(ar)}</div><div class="study-en" lang="en" dir="ltr">${escape(en)}</div>`;
const href = (classroom, lo) => `#/classrooms/${classroom}/banks/term1${lo ? '/outcomes/' + lo : ''}`;
const cache = new Map();
let uid = 0;

export async function renderStudyBooklet({root, route, studentKey = 'guest'}) {
  const requestHash = location.hash, classroom = route.classroom;
  root.innerHTML = '<p role="status">جارٍ فتح الملزمة · Opening your study booklet…</p>';
  try {
    if (!cache.has(classroom)) {
      const response = await fetch(`${BASE}data/study/${classroom}.json`);
      if (!response.ok) throw Error('load');
      cache.set(classroom, await response.json());
    }
    if (location.hash !== requestHash) return;
    const bank = cache.get(classroom);
    const byId = new Map(bank.questions.map(q => [q.id, q]));
    const progressKey = 'study-v2-' + classroom + '-' + studentKey;
    let progress = {};
    try { progress = JSON.parse(sessionStorage.getItem(progressKey) || '{}'); } catch {}
    if (!progress || typeof progress !== 'object' || Array.isArray(progress)) progress = {};
    progress.done ||= {}; progress.q ||= {}; progress.best ||= {};
    const saveProgress = () => { try { sessionStorage.setItem(progressKey, JSON.stringify(progress)); return true; } catch { return false; } };
    const ctx = {bank, byId, classroom, progress, saveProgress};
    const shell = inner => `<section class="study-booklet">${header(bank, classroom)}${inner}</section>`;

    if (route.quiz) return renderQuizRoute({root, route, ctx, shell, studentKey});
    const outcome = bank.learning_outcomes.find(lo => lo.id === route.outcomeId);
    if (route.outcomeId && !outcome) {
      root.innerHTML = shell(`<p role="alert">المخرج غير موجود · Outcome unavailable</p><a href="${href(classroom)}">العودة للملزمة · Back</a>`);
      return;
    }
    if (!outcome) return renderIndex({root, ctx, shell});
    return renderLesson({root, ctx, shell, outcome});
  } catch (error) {
    if (location.hash !== requestHash) return;
    root.innerHTML = '<p role="alert">تعذّر تحميل الملزمة · Could not load the study booklet.</p><button id="study-retry">إعادة المحاولة · Retry</button>';
    root.querySelector('#study-retry').onclick = () => renderStudyBooklet({root, route, studentKey});
  }
}

function header(bank, classroom) {
  return `<header class="study-hero"><div><p class="study-kicker">TERM 01 / STUDY COMPANION / 2026–2027</p><h1 lang="ar" dir="rtl">${title}</h1><p>Final exam structure revision · ${escape(names[classroom])} · ${classroom}</p></div><div class="study-total"><strong>${bank.learning_outcomes.length}</strong><span>مخرج تعلم<br>Learning outcomes</span></div></header><nav class="study-classes" aria-label="الصفوف · Classes">${Object.entries(names).map(([id, name]) => `<a href="${href(id)}" ${id === classroom ? 'aria-current="page"' : ''}>${name} · ${id}</a>`).join('')}</nav>`;
}

// ------------------------------------------------------------------ shared question pieces
const diagrams = (bank, q) => (q.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(a => `<figure><img loading="lazy" src="${BASE}${escape(a.src)}" alt="${escape(a.alt_text)}"><figcaption>${escape(a.alt_text)}</figcaption></figure>`).join('');
const sourceChip = q => { const [ar, en] = KIND[q.source_kind] || KIND.textbook_exercise; return `<span class="q-chip q-chip-${escape(q.source_kind)}" title="${en}">${ar}</span>`; };
const sourceRef = q => `<span class="q-ref">Reveal · p. ${escape(q.source?.printed_page)} · ${escape(q.source?.exercise)}</span>`;

function promptHtml(bank, q) {
  return `<div class="q-prompt" lang="en" dir="ltr"><p>${escape(q.math_latex ? q.instruction : q.stem)}</p>${q.math_latex ? `<div class="study-math">${math(q.math_latex)}</div>` : ''}${diagrams(bank, q)}${(q.parts || []).map(part => `<div class="q-part-prompt"><b>${escape(part.id)}.</b> ${escape(part.prompt)}${part.math_latex ? `<div class="study-math">${math(part.math_latex)}</div>` : ''}</div>`).join('')}</div>`;
}

function solutionHtml(q) {
  if (q.type === 'mcq') {
    const opt = q.options.find(o => o.id === q.answer.correct_option_id);
    return `<div class="solution-mcq"><b>${escape(q.answer.correct_option_id)}</b> <span dir="ltr">${opt?.math_latex ? math(q.answer.correct_option_text) : escape(q.answer.correct_option_text)}</span><p lang="en" dir="ltr">${escape(q.answer.explanation)}</p></div>`;
  }
  return q.parts.map(part => `<div class="solution-part"><b>${escape(part.id)}.</b>${part.blanks ? solvedMarkup(part.blanks) : (part.answer?.math_latex ? `<div class="study-math">${math(part.answer.math_latex)}</div>` : '')}<p lang="en" dir="ltr">${escape(part.answer?.model_answer_and_marking)}</p></div>`).join('');
}

const calcImage = g => g.image ? `${BASE}${g.image.replace(/^assets\//, 'data/exam-banks/')}` : '';
function calculatorHtml(q, open = false) {
  const g = q.calculator;
  if (!g?.applicable) return `<details class="q-tool q-calc q-calc-none"><summary><span class="q-tool-icon" aria-hidden="true">⌗</span>الآلة الحاسبة · Calculator</summary><p lang="ar" dir="rtl">هذا السؤال يعتمد على قاعدة أو رسم أو تبرير، والحاسبة وحدها لا تكفي. اتبع الحل المرجعي، ويمكنك استخدام الحاسبة لفحص الأعداد فقط.</p><p lang="en" dir="ltr" class="study-subtle">No calculator route: the justification, graph or rule is the solution.</p></details>`;
  const tables = g.table ? (g.branch_tables || [g.table]).map(t => `<table class="calculator-table"><caption>جدول القيم الناتج · Table results ${escape(t.condition || '')}</caption><tr><th>X</th>${t.x.map(v => `<td>${escape(v)}</td>`).join('')}</tr><tr><th>f(X)</th>${t.y.map(v => `<td>${escape(v)}</td>`).join('')}</tr></table>`).join('') : '';
  const lead = g.kind === 'check' ? 'للتحقق العددي: عوّض قيمة مسموحة في الطرفين؛ تساوي الناتجين دعم لا برهان.' : g.kind === 'table' ? 'MENU ← Table: ينتج قيمًا للدالة ولا يرسم المنحنى؛ ارسم النقاط بنفسك.' : g.kind === 'solve' ? 'للحل العددي: تأكد من أن الناتج يحقق المعادلة الأصلية.' : 'اتبع التسلسل ثم قارن الناتج بالحل المرجعي.';
  return `<details class="q-tool q-calc" ${open ? 'open' : ''}><summary><span class="q-tool-icon" aria-hidden="true">⌗</span>الحل بالآلة الحاسبة · ${escape(g.model)}</summary><p lang="ar" dir="rtl" class="calc-lead">${lead} <span class="study-subtle">تأكد أن الزوايا على Degree عند الحاجة.</span></p><ol class="calc-steps">${g.steps.map(s => `<li><b>${escape(s.title)}</b><div class="calculator-keys" dir="ltr">${s.keys.map(k => `<kbd>${escape(k)}</kbd>`).join('')}</div><p lang="en" dir="ltr">${escape(s.text)}</p>${s.expression ? `<code dir="ltr">${escape(String(s.expression).replaceAll('**', '^'))}</code>` : ''}</li>`).join('')}</ol>${tables}${g.image ? `<details class="calc-image"><summary>عرض مخطط الأزرار · Key diagram</summary><img loading="lazy" src="${escape(calcImage(g))}" alt="Key guide for question ${escape(q.display_number)}"></details>` : ''}<p class="study-subtle">مخطط تعليمي للأزرار وليس صورة من الحاسبة · Instructional key guide, not an official Casio emulator.</p></details>`;
}

// ------------------------------------------------------------------ interactive question card
function answerArea(bank, q, id) {
  if (q.type === 'mcq') {
    return `<fieldset class="q-choices"><legend class="sr-only">اختر الإجابة · Choose</legend>${q.options.map(o => `<label class="q-choice"><input type="radio" name="${id}" value="${escape(o.id)}"><span class="q-opt-id" dir="ltr">${escape(o.id)}</span><span class="q-opt" dir="ltr">${o.math_latex ? math(o.math_latex) : escape(o.text)}</span></label>`).join('')}</fieldset>`;
  }
  const parts = q.parts.map(part => {
    if (!part.blanks) return `<div class="q-paper"><b>${escape(part.id)}.</b> <span lang="ar" dir="rtl">اكتب الحل على ورقة (${part.workspace?.height_mm ? 'مساحة العمل ' + part.workspace.height_mm + ' مم' : 'حسب المطلوب'}) ثم قارنه بالحل المرجعي.</span></div>`;
    const {html} = fillMarkup(part.blanks, `${id}-${part.id}`);
    return `<div class="q-fill" data-part="${escape(part.id)}"><div class="q-fill-label"><b>${escape(part.id)}.</b> <span lang="ar" dir="rtl">أكمل الفراغات بخطوات الحل</span> · <span lang="en">Complete the working</span></div>${html}</div>`;
  }).join('');
  return parts;
}

// Mounts checking behaviour; returns {check(), values(), setValues(), done()}
function mountAnswer(el, bank, q, onResult) {
  if (q.type === 'mcq') {
    return {
      check() { const v = el.querySelector('input:checked')?.value; if (!v) return {empty: true}; const ok = v === q.answer.correct_option_id; el.querySelectorAll('.q-choice').forEach(l => { const i = l.querySelector('input'); l.classList.toggle('is-right', ok && i.checked); l.classList.toggle('is-wrong', !ok && i.checked); }); return {all: ok, correct: ok ? 1 : 0, total: 1}; },
      values: () => el.querySelector('input:checked')?.value || '',
      setValues(v) { const i = el.querySelector(`input[value="${CSS.escape(v || '')}"]`); if (i) i.checked = true; },
      reveal() { const i = el.querySelector(`input[value="${CSS.escape(q.answer.correct_option_id)}"]`); if (i) { i.checked = true; i.closest('.q-choice').classList.add('is-right'); } },
      reset() { el.querySelectorAll('input').forEach(i => { i.checked = false; }); el.querySelectorAll('.q-choice').forEach(l => l.classList.remove('is-right', 'is-wrong')); }
    };
  }
  const fills = q.parts.filter(p => p.blanks).map(part => {
    const box = el.querySelector(`.q-fill[data-part="${CSS.escape(part.id)}"] .fill-box`);
    const parsed = fillMarkup(part.blanks, 'x').parsed;
    return {part, wire: wireFill(box, parsed, onResult || (() => {}))};
  });
  return {
    check() { if (!fills.length) return {empty: true}; const rs = fills.map(f => f.wire.check()); const total = rs.reduce((s, r) => s + r.total, 0), correct = rs.reduce((s, r) => s + r.correct, 0); return {all: correct === total, correct, total, empty: fills.every(f => f.wire.values().every(v => !v))}; },
    values: () => Object.fromEntries(fills.map(f => [f.part.id, f.wire.values()])),
    setValues(v) { fills.forEach(f => f.wire.setValues(v?.[f.part.id])); },
    reveal() { fills.forEach(f => f.wire.reveal()); },
    reset() { fills.forEach(f => f.wire.reset()); }
  };
}

function hintHtml(outcome, level) {
  if (level === 1) return `<p class="hint-tag">تلميح ١ · القاعدة</p>${pair(outcome.rule_ar, outcome.rule_summary)}`;
  return `<p class="hint-tag">تلميح ٢ · الخطة</p>${pair('اكتب المعطيات، ثم طبّق القاعدة على الأعداد الجديدة، وراقب الإشارات والوحدات. قارن مع المثال المحلول في الأعلى.', 'List the givens, apply the rule to the new values and watch signs and units. Compare with the worked example above.')}`;
}

function questionCard(ctx, outcome, q, {index, role = 'practice'} = {}) {
  const id = 'qc' + (++uid);
  const done = ctx.progress.q[q.id];
  return {
    id,
    html: `<article class="q-card q-${role}" id="${id}" data-qid="${escape(q.id)}"><header class="q-head"><span class="q-num">${escape(q.display_number)}</span>${sourceChip(q)}${sourceRef(q)}<span class="q-done" ${done ? '' : 'hidden'} title="أنجزت هذا السؤال">✓</span></header>
      <div class="q-block q-question"><span class="q-label">السؤال · QUESTION</span>${promptHtml(ctx.bank, q)}</div>
      <div class="q-block q-answer"><span class="q-label">إجابتك · YOUR ANSWER</span>${answerArea(ctx.bank, q, id)}
        <div class="q-actions"><button type="button" class="btn-primary" data-act="check">تحقّق · Check</button><button type="button" data-act="hint">تلميح · Hint</button><button type="button" data-act="reveal">أظهر الحل · Show answer</button><button type="button" data-act="reset">مسح · Clear</button></div>
        <div class="q-feedback" role="status" aria-live="polite"></div><div class="q-hint" role="note"></div></div>
      <details class="q-tool q-solution"><summary><span class="q-tool-icon" aria-hidden="true">✓</span>الحل المرجعي · Reference solution</summary>${solutionHtml(q)}</details>
      ${calculatorHtml(q)}</article>`,
    mount() {
      const el = document.getElementById(id); if (!el) return;
      const mcq = q.type === 'mcq', fb = el.querySelector('.q-feedback'), hintEl = el.querySelector('.q-hint');
      let hints = 0;
      const area = mountAnswer(el.querySelector('.q-answer'), ctx.bank, q);
      const markDone = () => { ctx.progress.q[q.id] = true; ctx.saveProgress(); el.querySelector('.q-done').hidden = false; el.dispatchEvent(new CustomEvent('q-done', {bubbles: true})); };
      el.querySelector('[data-act=check]').onclick = () => {
        const r = area.check();
        if (r.empty) { fb.className = 'q-feedback'; fb.innerHTML = pair(mcq ? 'اختر إجابة أولًا.' : 'اكتب في فراغ واحد على الأقل (الأسئلة الورقية فقط لا تُصحَّح هنا).', mcq ? 'Choose an answer first.' : 'Fill at least one blank (paper-only parts are not auto-checked).'); return; }
        if (r.all) { fb.className = 'q-feedback is-right'; fb.innerHTML = pair('صحيح! راجع الحل المرجعي لتثبيت الفكرة.', 'Correct! Open the reference solution to lock in the idea.') + (mcq ? `<p lang="en" dir="ltr">${escape(q.answer.explanation)}</p>` : ''); markDone(); }
        else { fb.className = 'q-feedback is-wrong'; fb.innerHTML = pair(mcq ? 'ليست الإجابة الصحيحة. راجع القاعدة والإشارات، ثم جرّب مجددًا أو اطلب تلميحًا.' : `${r.correct} من ${r.total} فراغات صحيحة. الفراغات الحمراء تحتاج مراجعة.`, mcq ? 'Not quite. Check the rule and signs, then try again or ask for a hint.' : `${r.correct} of ${r.total} blanks correct. Red blanks need another look.`); }
      };
      el.querySelector('[data-act=hint]').onclick = () => { hints = Math.min(2, hints + 1); hintEl.innerHTML = hintHtml(outcome, hints); };
      el.querySelector('[data-act=reveal]').onclick = () => { area.reveal?.(); fb.className = 'q-feedback'; fb.innerHTML = pair('هذا هو الحل — حاول شرحه بنفسك بصوت مسموع.', 'Here is the solution — try explaining each step aloud.'); el.querySelector('.q-solution').open = true; };
      el.querySelector('[data-act=reset]').onclick = () => { area.reset(); fb.className = 'q-feedback'; fb.textContent = ''; hintEl.textContent = ''; hints = 0; };
    }
  };
}

// ------------------------------------------------------------------ index
function builderHtml(ctx, selected = []) {
  const {bank, classroom} = ctx;
  const sel = new Set(selected);
  return `<section class="quiz-builder" aria-labelledby="qb-title"><div class="qb-head"><span class="study-label">QUIZ BUILDER · منشئ الاختبار</span><h2 id="qb-title" lang="ar" dir="rtl">اصنع اختبارًا على مخرجات التعلم</h2><p lang="ar" dir="rtl" class="study-subtle">اختر مخرجًا أو أكثر، وعدد الأسئلة؛ تُوزَّع الأسئلة بالتساوي بين المخرجات، وتُخلط الخيارات في كل مرة.</p></div>
    <form id="quiz-form"><div class="qb-actions"><button type="button" data-qb="all">تحديد الكل</button><button type="button" data-qb="none">إلغاء التحديد</button><span id="qb-count" class="study-subtle" role="status"></span></div>
    <div class="qb-los">${bank.learning_outcomes.map(lo => { const n = quizPool(bank, {los: [lo.id]}).length; return `<label class="qb-lo ${n ? '' : 'is-empty'}"><input type="checkbox" name="lo" value="${lo.id}" ${sel.has(lo.id) ? 'checked' : ''} ${n ? '' : 'disabled'}><span><b>${lo.id}</b> ${escape(lo.title_ar)}<small>${n} أسئلة جاهزة${ctx.progress.best[lo.id] != null ? ` · أفضل نتيجة ${ctx.progress.best[lo.id]}%` : ''}</small></span></label>`; }).join('')}</div>
    <div class="qb-options"><label>عدد الأسئلة · Questions<select name="n">${QUIZ_SIZES.map(n => `<option value="${n}" ${n === 10 ? 'selected' : ''}>${n}</option>`).join('')}</select></label><label>نوع الأسئلة · Type<select name="mix"><option value="all">متنوعة · Mixed</option><option value="mcq">اختيار من متعدد · MCQ</option><option value="frq">كتابية بفراغات · Written (blanks)</option></select></label><label class="qb-check"><input type="checkbox" name="t"> بمؤقت · Timed</label><button type="submit" class="btn-primary">ابدأ الاختبار · Start quiz</button></div></form></section>`;
}

function mountBuilder(root, ctx) {
  const form = root.querySelector('#quiz-form'); if (!form) return;
  const count = () => { const los = [...form.querySelectorAll('[name=lo]:checked')].map(i => i.value); const mix = form.elements.mix.value; const pool = los.length ? quizPool(ctx.bank, {los, mix}).length : 0; root.querySelector('#qb-count').textContent = los.length ? `${los.length} مخرجات · ${pool} سؤالًا متاحًا` : 'اختر مخرجًا واحدًا على الأقل'; return {los, pool, mix}; };
  form.addEventListener('change', count); count();
  form.querySelectorAll('[data-qb]').forEach(b => b.onclick = () => { form.querySelectorAll('[name=lo]:not(:disabled)').forEach(i => { i.checked = b.dataset.qb === 'all'; }); count(); });
  form.onsubmit = e => { e.preventDefault(); const {los, pool, mix} = count(); if (!los.length || !pool) { root.querySelector('#qb-count').textContent = 'لا توجد أسئلة مطابقة؛ غيّر الاختيار.'; return; } const n = Number(form.elements.n.value); location.hash = quizHash(ctx.classroom, los, n, mix) + (form.elements.t.checked ? '&t=1' : ''); };
}

function renderIndex({root, ctx, shell}) {
  const {bank, classroom, progress} = ctx;
  const legend = `<ol class="study-flow" aria-label="مكونات الدرس · Lesson parts">${SECTIONS.map(([k, n, ar, en, tip]) => `<li class="flow-${k}"><span class="flow-n" aria-hidden="true">${n}</span><b>${ar}</b><small>${en}</small><span class="flow-tip" lang="ar" dir="rtl">${tip}</span></li>`).join('')}</ol>`;
  root.innerHTML = shell(`<div class="study-intro">${pair('رحلتك من الفكرة إلى الحل المستقل', 'Your path from understanding to independent practice')}${legend}<p class="study-subtle" lang="ar" dir="rtl">${escape(bank.authored_notice_ar || '')}</p></div>
    ${builderHtml(ctx)}
    <label class="study-search"><span>ابحث عن درس أو صفحة · Find a topic or page</span><input id="study-search" type="search" placeholder="LO · الموضوع · page"></label><p id="study-count" role="status"></p><div class="study-grid"></div>
    <p class="study-subtle">المراجع كما وردت في الملف المرفق؛ الحفظ في علامة التبويب هذه فقط. References follow the supplied transfer package. Progress stays in this browser tab.</p>`);
  mountBuilder(root, ctx);
  const draw = () => {
    const term = root.querySelector('#study-search').value.trim().toLowerCase();
    const filtered = bank.learning_outcomes.filter(lo => JSON.stringify([lo.id, lo.title, lo.title_ar, lo.textbook_references]).toLowerCase().includes(term));
    root.querySelector('#study-count').textContent = `${filtered.length} / ${bank.learning_outcomes.length} · الدروس / Lessons`;
    root.querySelector('.study-grid').innerHTML = filtered.map(lo => {
      const total = lo.question_ids.length, done = lo.question_ids.filter(id => progress.q[id]).length, best = progress.best[lo.id];
      return `<a class="study-topic" href="${href(classroom, lo.id)}"><span class="study-topic-top"><b>${lo.id} / ${lo.exam_slot}</b><span>${progress.done[lo.id] ? '✓ راجعت الدرس' : done ? 'قيد المذاكرة' : 'ابدأ المذاكرة'}</span></span><h2 lang="ar" dir="rtl">${escape(lo.title_ar)}</h2><p lang="en">${escape(lo.title)}</p><small>${escape(lo.textbook_references.map(r => 'p. ' + r.printed_page + ' · ' + r.exercises_or_section).join(' / '))}</small><div class="topic-meter" role="img" aria-label="${done} من ${total}"><i style="width:${total ? Math.round(done / total * 100) : 0}%"></i></div><div class="study-topic-bottom"><span>${done}/${total} · ${lo.question_type.toUpperCase()}${best != null ? ` · اختبار ${best}%` : ''}</span><span>افتح الدرس ←</span></div></a>`;
    }).join('');
  };
  root.querySelector('#study-search').oninput = draw; draw();
}

// ------------------------------------------------------------------ lesson
function renderLesson({root, ctx, shell, outcome}) {
  const {bank, byId, classroom, progress} = ctx;
  const questions = outcome.question_ids.map(id => byId.get(id)).filter(Boolean);
  const example = questions[0], helperPool = questions.slice(1), practice = questions.slice(2);
  const index = bank.learning_outcomes.indexOf(outcome), next = bank.learning_outcomes[index + 1], prev = bank.learning_outcomes[index - 1];
  const cards = practice.map((q, i) => questionCard(ctx, outcome, q, {index: i}));
  const quizReady = quizPool(bank, {los: [outcome.id]}).length;
  const sec = (key, body, extra = '') => { const [k, n, ar, en, tip] = SECTIONS.find(s => s[0] === key); return `<section class="lesson-sec sec-${k}" id="sec-${k}" aria-labelledby="h-${k}"><header class="sec-head"><span class="sec-n" aria-hidden="true">${n}</span><div><h3 id="h-${k}" lang="ar" dir="rtl">${ar}</h3><p class="sec-en">${en} · <span lang="ar" dir="rtl">${tip}</span></p></div>${extra}</header>${body}</section>`; };
  const doneCount = () => questions.filter(q => progress.q[q.id]).length;
  root.innerHTML = shell(`<div class="study-toolbar"><a href="${href(classroom)}">← فهرس الملزمة · Contents</a><button type="button" id="study-print">طباعة الدرس · Print</button></div>
    <div class="study-lesson-title"><span>${outcome.id} / ${outcome.exam_slot}</span><h2 lang="ar" dir="rtl">${escape(outcome.title_ar)}</h2><p lang="en">${escape(outcome.title)}</p><div class="lesson-progress"><div class="topic-meter"><i id="lp-bar" style="width:${Math.round(doneCount() / questions.length * 100)}%"></i></div><span id="lp-text">${doneCount()} / ${questions.length} · أنجزت</span></div></div>
    <nav class="lesson-nav" aria-label="أقسام الدرس · Lesson sections">${SECTIONS.map(([k, n, ar]) => `<a href="#sec-${k}" data-sec="${k}" class="nav-${k}"><span>${n}</span>${ar}</a>`).join('')}</nav>
    ${sec('idea', `<div class="idea-card">${pair(outcome.rule_ar, outcome.rule_summary)}</div>`)}
    ${sec('example', `<div class="example-card"><div class="q-meta">${sourceChip(example)}${sourceRef(example)}<span class="q-num">${escape(example.display_number)}</span></div>
      <div class="q-block q-question"><span class="q-label">السؤال · QUESTION</span>${promptHtml(bank, example)}</div>
      <div class="q-block q-solved"><span class="q-label">الحل · SOLUTION</span>${solutionHtml(example)}</div>
      ${calculatorHtml(example, true)}</div>`)}
    ${sec('helper', helperPool.length ? `<div class="helper-card"><label class="helper-pick">اختر السؤال · Choose a question<select id="study-practice-select">${helperPool.map((q, i) => `<option value="${i}">${escape(q.display_number)} · p. ${escape(q.source?.printed_page)} · ${escape(q.source?.exercise)}</option>`).join('')}</select></label><div id="study-practice"></div></div>` : '<p class="study-subtle">لا توجد أسئلة إضافية.</p>')}
    ${sec('practice', practice.length ? `<p lang="ar" dir="rtl" class="sec-note">أجب في الفراغات ثم اضغط «تحقّق». «الحل المرجعي» و«الآلة الحاسبة» أسفل كل سؤال.</p><div class="q-list">${cards.map(c => c.html).join('')}</div>` : '<p class="study-subtle">لا توجد أسئلة تدريب إضافية.</p>')}
    ${sec('quiz', quizReady ? `<div class="quiz-cta"><p lang="ar" dir="rtl">اختبار قصير من ${Math.min(quizReady, 5)} أسئلة على هذا المخرج، بخيارات مخلوطة وتصحيح فوري ومراجعة للأخطاء.</p><div class="cta-row"><a class="btn-primary" href="${quizHash(classroom, [outcome.id], Math.min(5, QUIZ_SIZES.find(n => n >= Math.min(quizReady, 5)) || 5), 'all')}">ابدأ اختبار هذا المخرج · Start quiz</a><a href="${href(classroom)}">اختبار متعدد المخرجات · Multi-outcome quiz</a></div>${progress.best[outcome.id] != null ? `<p class="study-subtle">أفضل نتيجة لك: ${progress.best[outcome.id]}%</p>` : ''}</div>` : '<p class="study-subtle">لا يوجد اختبار آلي لهذا المخرج (أسئلته ورقية).</p>')}
    <div class="study-finish"><label><input type="checkbox" id="study-done" ${progress.done[outcome.id] ? 'checked' : ''}> راجعت هذا الدرس · I reviewed this lesson</label><span id="study-save" role="status"></span>${prev ? `<a href="${href(classroom, prev.id)}">→ السابق</a>` : ''}<a href="${href(classroom, next?.id)}">${next ? 'الدرس التالي ←' : 'الفهرس ←'}</a></div>`);
  root.querySelector('#study-print').onclick = () => window.print();
  root.querySelector('#study-done').onchange = event => { progress.done[outcome.id] = event.target.checked; root.querySelector('#study-save').textContent = ctx.saveProgress() ? 'تم الحفظ في هذه التبويبة · Saved in this tab' : 'تعذّر الحفظ · Could not save'; };
  cards.forEach(c => c.mount());
  root.addEventListener('q-done', () => { const d = doneCount(); root.querySelector('#lp-bar').style.width = Math.round(d / questions.length * 100) + '%'; root.querySelector('#lp-text').textContent = `${d} / ${questions.length} · أنجزت`; });
  const nav = [...root.querySelectorAll('.lesson-nav a')];
  nav.forEach(a => a.addEventListener('click', e => { e.preventDefault(); root.querySelector(a.getAttribute('href')).scrollIntoView({behavior: 'smooth', block: 'start'}); }));
  if ('IntersectionObserver' in window) { const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) nav.forEach(a => a.toggleAttribute('aria-current', a.dataset.sec === en.target.id.slice(4))); }), {rootMargin: '-30% 0px -60% 0px'}); root.querySelectorAll('.lesson-sec').forEach(s => io.observe(s)); }
  if (helperPool.length) mountHelper(root, ctx, outcome, helperPool);
}

// Step-by-step helper: understand -> choose the rule -> apply with blanks / choices
function mountHelper(root, ctx, outcome, pool) {
  const select = root.querySelector('#study-practice-select'), area = root.querySelector('#study-practice');
  const state = {i: 0, phase: 0, notes: '', rule: false};
  const draw = () => {
    const q = pool[state.i];
    const steps = ['فهم السؤال', 'اختيار القاعدة', 'الحل'];
    const rules = [outcome, ...ctx.bank.learning_outcomes.filter(l => l.id !== outcome.id).slice(0, 2)].sort((a, b) => a.id.localeCompare(b.id));
    area.innerHTML = `<ol class="helper-steps" aria-label="خطوات المساعد">${steps.map((s, k) => `<li class="${k === state.phase ? 'is-now' : k < state.phase ? 'is-past' : ''}"><span>${k + 1}</span>${s}</li>`).join('')}</ol>
      <div class="q-block q-question"><span class="q-label">السؤال · QUESTION</span>${promptHtml(ctx.bank, q)}</div>
      <div class="q-block q-helper"><span class="q-label">المساعد · HELPER</span>${state.phase === 0 ? `<h4>ما المعطيات وما المطلوب؟ · What is given and required?</h4><textarea id="h-notes" rows="3" placeholder="المعطيات ← المطلوب · Given → Required">${escape(state.notes)}</textarea><button type="button" id="h-next" class="btn-primary">حدّدتُ المعطيات، تابع · Continue</button>`
        : state.phase === 1 ? `<h4>اختر القاعدة المناسبة · Choose the matching rule</h4><div class="study-rule-options">${rules.map(lo => `<button type="button" data-rule="${lo.id}"><span lang="ar" dir="rtl">${escape(lo.rule_ar)}</span><small lang="en" dir="ltr">${escape(lo.rule_summary)}</small></button>`).join('')}</div><div id="h-rule-fb" role="status"></div>`
        : `<h4>طبّق القاعدة وأوجد الناتج · Apply the rule</h4>${pair(outcome.rule_ar, outcome.rule_summary)}<div id="h-card"></div>`}
        <div class="q-actions"><button type="button" id="h-example">اشرح المثال أولًا · See the example</button></div></div>`;
    area.querySelector('#h-example').onclick = () => root.querySelector('#sec-example').scrollIntoView({behavior: 'smooth'});
    area.querySelector('#h-next')?.addEventListener('click', () => { state.notes = area.querySelector('#h-notes').value; state.phase = 1; draw(); });
    area.querySelectorAll('[data-rule]').forEach(b => b.onclick = () => { if (b.dataset.rule === outcome.id) { state.phase = 2; draw(); } else area.querySelector('#h-rule-fb').innerHTML = pair('هذه القاعدة تخص فكرة أخرى. اقرأ المطلوب وقارن الرموز ثم جرّب مجددًا.', 'That rule belongs to a different concept. Re-read the required quantity and compare the symbols, then try again.'); });
    if (state.phase === 2) {
      const card = questionCard(ctx, outcome, q, {role: 'helper'});
      const host = area.querySelector('#h-card'); host.innerHTML = card.html; card.mount();
      host.querySelector('.q-head').remove(); host.querySelector('.q-question').remove();
    }
  };
  select.onchange = () => { state.i = Number(select.value); state.phase = 0; state.notes = ''; draw(); };
  draw();
}

// ------------------------------------------------------------------ quiz
const quizKey = (classroom, studentKey) => `study-quiz-${classroom}-${studentKey}`;
function loadQuiz(ctx, studentKey, sig) { try { const s = JSON.parse(sessionStorage.getItem(quizKey(ctx.classroom, studentKey)) || 'null'); if (s?.sig === sig && validQuiz(s.quiz, ctx.bank)) return s.quiz; } catch {} return null; }
function saveQuiz(ctx, studentKey, sig, quiz) { try { sessionStorage.setItem(quizKey(ctx.classroom, studentKey), JSON.stringify({sig, quiz})); } catch {} }

function renderQuizRoute({root, route, ctx, shell, studentKey}) {
  const {bank, byId, classroom, progress} = ctx;
  const cfg = parseQuizQuery(route.query);
  if (!cfg.los.length) { root.innerHTML = shell(builderHtml(ctx)); mountBuilder(root, ctx); return; }
  let sig = route.query, timerId = null;
  let quiz = loadQuiz(ctx, studentKey, sig);
  if (!quiz) {
    quiz = buildQuiz(bank, {los: cfg.los, count: cfg.count, mix: cfg.mix});
    if (!quiz.ids.length) { root.innerHTML = shell(`<p role="alert">لا توجد أسئلة مطابقة · No matching questions.</p><a href="${href(classroom)}">← الملزمة</a>`); return; }
    if (cfg.timed) { const mins = Math.ceil(quiz.ids.reduce((s, id) => s + (byId.get(id).type === 'mcq' ? 1.5 : 4), 0)); quiz.deadline = quiz.startedAt + mins * 60000; }
    saveQuiz(ctx, studentKey, sig, quiz);
  }
  const persist = () => saveQuiz(ctx, studentKey, sig, quiz);
  let current = 0, areas = {};
  const stop = () => { if (timerId) { clearInterval(timerId); timerId = null; } };
  const finish = () => { stop(); quiz.finished = true; quiz.finishedAt = Date.now(); const r = gradeQuiz(quiz, bank); for (const [lo, v] of Object.entries(r.los)) { const p = Math.round(v.score / v.max * 100); progress.best[lo] = Math.max(progress.best[lo] ?? 0, p); } ctx.saveProgress(); persist(); drawResult(); };
  const collect = () => { const id = quiz.ids[current], a = areas[id]; if (a) { quiz.answers[id] = a.values(); persist(); } };

  function drawQuestion() {
    const id = quiz.ids[current], q = byId.get(id), lo = bank.learning_outcomes.find(l => l.id === q.learning_outcome_id);
    const order = q.type === 'mcq' ? quiz.options[id].map(oid => q.options.find(o => o.id === oid)) : null;
    const shown = order ? {...q, options: order.map((o, i) => ({...o, id: o.id}))} : q;
    const unanswered = quiz.ids.filter(k => !gradeQuestion(byId.get(k), quiz.answers[k]).answered).length;
    root.innerHTML = shell(`<div class="study-toolbar"><a href="${href(classroom)}">← الملزمة</a><span class="quiz-title">اختبار المخرجات: ${escape(cfg.los.join(' · '))}</span><span id="quiz-timer" class="quiz-timer" ${quiz.deadline ? '' : 'hidden'} role="timer"></span></div>
      <div class="quiz-run"><div class="quiz-bar" role="progressbar" aria-valuemin="1" aria-valuemax="${quiz.ids.length}" aria-valuenow="${current + 1}"><i style="width:${(current + 1) / quiz.ids.length * 100}%"></i></div>
      <nav class="quiz-dots" aria-label="الأسئلة">${quiz.ids.map((k, i) => `<button type="button" data-go="${i}" class="${i === current ? 'is-now' : ''} ${gradeQuestion(byId.get(k), quiz.answers[k]).answered ? 'is-answered' : ''}" aria-label="سؤال ${i + 1}">${i + 1}</button>`).join('')}</nav>
      <article class="q-card q-quiz"><header class="q-head"><span class="q-num">${current + 1} / ${quiz.ids.length}</span><span class="q-chip">${escape(lo?.title_ar || '')}</span></header>
      <div class="q-block q-question"><span class="q-label">السؤال · QUESTION</span>${promptHtml(bank, q)}</div>
      <div class="q-block q-answer"><span class="q-label">إجابتك · YOUR ANSWER</span>${answerArea(bank, shown, 'qz')}</div></article>
      <div class="quiz-nav"><button type="button" id="qz-prev" ${current === 0 ? 'disabled' : ''}>→ السابق</button>${current < quiz.ids.length - 1 ? '<button type="button" id="qz-next" class="btn-primary">التالي ←</button>' : '<button type="button" id="qz-finish" class="btn-primary">إنهاء وتصحيح · Finish</button>'}<span class="study-subtle">${unanswered ? `${unanswered} بلا إجابة` : 'كل الأسئلة مجابة'}</span></div></div>`);
    const a = mountAnswer(root.querySelector('.q-answer'), bank, shown, () => collect());
    areas = {[id]: a};
    a.setValues(quiz.answers[id]);
    root.querySelector('.q-answer').addEventListener('change', collect);
    const go = i => { collect(); current = i; drawQuestion(); };
    root.querySelector('#qz-prev').onclick = () => go(current - 1);
    root.querySelector('#qz-next')?.addEventListener('click', () => go(current + 1));
    root.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(Number(b.dataset.go)));
    root.querySelector('#qz-finish')?.addEventListener('click', () => { collect(); const left = quiz.ids.filter(k => !gradeQuestion(byId.get(k), quiz.answers[k]).answered).length; if (!left || confirm(`${left} أسئلة بلا إجابة. إنهاء الاختبار؟`)) finish(); });
    if (quiz.deadline) tick();
  }
  function tick() {
    stop();
    const el = () => root.querySelector('#quiz-timer');
    const update = () => { const left = Math.max(0, Math.ceil((quiz.deadline - Date.now()) / 1000)); const t = el(); if (t) t.textContent = `⏱ ${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`; if (!left) { collect(); finish(); } };
    update(); timerId = setInterval(() => { if (!document.body.contains(root.querySelector('.quiz-run'))) { stop(); return; } update(); }, 1000);
  }

  function drawResult() {
    const r = gradeQuiz(quiz, bank);
    const loRows = Object.entries(r.los).map(([lo, v]) => { const t = bank.learning_outcomes.find(l => l.id === lo), p = Math.round(v.score / v.max * 100); return `<li><a href="${href(classroom, lo)}"><b>${lo}</b> ${escape(t.title_ar)}</a><div class="topic-meter ${p < 60 ? 'is-low' : ''}"><i style="width:${p}%"></i></div><span>${+v.score.toFixed(1)} / ${v.max}</span></li>`; }).join('');
    const review = quiz.ids.map((id, i) => {
      const q = byId.get(id), res = r.per[i], mine = quiz.answers[id];
      let yours = '';
      if (q.type === 'mcq') { const o = q.options.find(x => x.id === mine); yours = o ? `<span dir="ltr"><b>${escape(o.id)}</b> · ${o.math_latex ? math(o.math_latex) : escape(o.text)}</span>` : '<em>بلا إجابة</em>'; }
      else yours = q.parts.filter(p => p.blanks).map(p => `<div class="review-part"><b>${escape(p.id)}.</b> ${(mine?.[p.id] || []).map(v => `<code>${escape(v || '—')}</code>`).join(' ')}</div>`).join('');
      return `<article class="q-card review ${res.correct ? 'is-right' : 'is-wrong'}"><header class="q-head"><span class="q-num">${i + 1}</span><span class="q-chip">${res.correct ? '✓ صحيح' : res.score > 0 ? `جزئي ${Math.round(res.score * 100)}%` : '✗ خطأ'}</span>${sourceRef(q)}</header><div class="q-block q-question"><span class="q-label">السؤال · QUESTION</span>${promptHtml(bank, q)}</div><div class="q-block"><span class="q-label">إجابتك · YOURS</span>${yours}</div><details class="q-tool q-solution" ${res.correct ? '' : 'open'}><summary><span class="q-tool-icon" aria-hidden="true">✓</span>الحل المرجعي · Reference solution</summary>${solutionHtml(q)}</details>${calculatorHtml(q)}<p><a href="${href(classroom, q.learning_outcome_id)}">راجع الدرس ${q.learning_outcome_id} ←</a></p></article>`;
    }).join('');
    root.innerHTML = shell(`<div class="study-toolbar"><a href="${href(classroom)}">← الملزمة</a></div><section class="quiz-result"><div class="result-score" role="status"><strong>${r.percent}%</strong><span>${+r.score.toFixed(1)} / ${r.max}</span></div><div><h2 lang="ar" dir="rtl">${r.percent >= 80 ? 'ممتاز! أنت جاهز لهذه المخرجات' : r.percent >= 60 ? 'جيد — راجع الأسئلة الخاطئة' : 'تحتاج مزيدًا من المذاكرة — ابدأ بالمثال المحلول'}</h2><ul class="result-los">${loRows}</ul><div class="cta-row"><button type="button" id="qz-retry-wrong" class="btn-primary" ${r.wrongIds.length ? '' : 'disabled'}>أعد الأسئلة الخاطئة فقط (${r.wrongIds.length})</button><button type="button" id="qz-again">اختبار جديد بالمخرجات نفسها</button><button type="button" id="qz-print">طباعة</button></div></div></section><h3 lang="ar" dir="rtl" class="review-title">مراجعة الأسئلة</h3><div class="q-list">${review}</div>`);
    root.querySelector('#qz-print').onclick = () => window.print();
    root.querySelector('#qz-again').onclick = () => { quiz = buildQuiz(bank, {los: cfg.los, count: cfg.count, mix: cfg.mix}); sig = route.query; persist(); current = 0; drawQuestion(); };
    root.querySelector('#qz-retry-wrong').onclick = () => { quiz = buildQuiz(bank, {los: cfg.los, count: r.wrongIds.length, mix: 'all', onlyIds: r.wrongIds}); persist(); current = 0; drawQuestion(); };
  }
  if (quiz.finished) drawResult(); else drawQuestion();
}
