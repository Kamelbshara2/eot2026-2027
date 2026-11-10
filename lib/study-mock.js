// Practice mock exam: 20 multiple-choice questions (one per learning outcome, drawn from the exam-structure bank),
// 60 minutes. Leaving the browser (tab switch, another app) blurs the page and hides the questions until return.
import {createTermMock, validTermMock, finishTermMock, gradeTermMock, mockRemaining, mockStorageKey, MOCK_QUESTION_COUNT, MOCK_DURATION_MS} from './term-mock-core.js';
import {questionWatermark} from './watermark.js';
import {normalizeStudyMath} from './study-math.js';
import {bankMath} from './exam-bank-math.js';
import {optionBody} from './study-option.js';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const math = v => bankMath(normalizeStudyMath(v));
const fmt = sec => `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
const LETTERS = ['A', 'B', 'C', 'D'];
let dispose = null;
export const stopStudyMock = () => { dispose?.(); dispose = null; };

// Pure helper (tested): focus guard state machine.
export function createFocusGuard(now = () => Date.now()) {
  let awaySince = null; const s = {leaves: 0, awayMs: 0};
  return {
    state: s, away: () => awaySince !== null,
    leave() { if (awaySince === null) { awaySince = now(); s.leaves++; } },
    back() { if (awaySince !== null) { s.awayMs += now() - awaySince; awaySince = null; } }
  };
}

export function renderStudyMock({root, bank, studentKey, backHref, base = '/', storage}) {
  stopStudyMock();
  if (storage === undefined) { try { storage = sessionStorage; } catch { storage = null; } }
  const key = mockStorageKey(studentKey, 'study-' + bank.id), byId = new Map(bank.questions.map(q => [q.id, q]));
  const wall = Date.now(), mono = performance.now(), now = () => Math.max(Date.now(), wall + performance.now() - mono);
  let state = null;
  try { const raw = storage?.getItem(key); if (raw) { const s = JSON.parse(raw); if (validTermMock(s, bank)) state = s; } } catch {}
  const rnd = () => { const a = new Uint32Array(1); crypto.getRandomValues(a); return a[0] / 4294967296; };
  const save = () => { try { storage?.setItem(key, JSON.stringify(state)); } catch {} };
  const guard = createFocusGuard(now);
  if (state?.guard) Object.assign(guard.state, state.guard);
  let timer = null;

  const diagrams = q => (q.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(a => `<figure><img src="${base}${esc(a.src)}" alt="${esc(a.alt_text)}"></figure>`).join('');
  const stem = q => `<div class="mock-stem" lang="en" dir="ltr"><p>${esc(q.math_latex ? q.instruction : q.stem)}</p>${q.math_latex ? `<div class="study-math">${math(q.math_latex)}</div>` : ''}${diagrams(q)}</div>`;

  function start() {
    root.innerHTML = `<section class="study-booklet mock-start"><div class="study-toolbar"><a href="${backHref}">← الملزمة · Booklet</a></div><div class="study-panel"><span class="study-label">MOCK EXAM · اختبار تجريبي</span><h2 lang="ar" dir="rtl">اختبار تجريبي على مخرجات الهيكل</h2>
      <ul class="mock-rules" lang="ar" dir="rtl"><li><b>${MOCK_QUESTION_COUNT} سؤالًا</b> اختيار من متعدد، سؤال واحد لكل مخرج تعلم من أسئلة الهيكل.</li><li>المدة <b>${MOCK_DURATION_MS / 60000} دقيقة</b>، ويُسلَّم الاختبار تلقائيًا عند انتهاء الوقت.</li><li>إذا غادرت المتصفح (تغيير التبويب أو فتح برنامج آخر) <b>تُحجب الأسئلة</b> وتصبح الصفحة ضبابية حتى تعود، ويُسجَّل عدد المغادرات.</li><li>لا تظهر الإجابات إلا بعد التسليم. المحاولة محفوظة في هذا التبويب فقط.</li></ul>
      <button type="button" id="mock-begin" class="btn-primary">ابدأ الاختبار · Start</button><p id="mock-error" role="alert"></p></div></section>`;
    root.querySelector('#mock-begin').onclick = () => {
      try { state = createTermMock(bank, Date.now(), rnd); state.guard = guard.state; save(); run(); }
      catch { root.querySelector('#mock-error').textContent = 'تعذّر إنشاء الاختبار · Could not build the exam.'; }
    };
  }

  function run() {
    if (state.finished) return result();
    const q = () => byId.get(state.ids[state.index]);
    root.innerHTML = `<section class="study-booklet mock-run"><div class="mock-shell"><div class="mock-content">
      <div class="mock-top"><strong>اختبار تجريبي · Mock exam</strong><span id="mock-timer" role="timer" class="quiz-timer">--:--</span><button type="button" id="mock-submit">تسليم · Submit</button></div>
      <nav class="study-slide-nav" id="mock-nav" aria-label="الأسئلة"></nav><div id="mock-q" class="study-panel"></div>
      <div class="study-slide-actions"><button type="button" id="mock-prev">السابق</button><button type="button" id="mock-next" class="btn-primary">التالي</button></div><p id="mock-away" class="study-subtle"></p></div>
      <div class="mock-cover" role="alert" hidden><div><h2 lang="ar" dir="rtl">الاختبار متوقف عرضه</h2><p lang="ar" dir="rtl">غادرت نافذة المتصفح. عد إلى هذه الصفحة لمتابعة الاختبار؛ الوقت لا يتوقف.</p></div></div></div></section>`;
    const content = root.querySelector('.mock-content'), cover = root.querySelector('.mock-cover');
    const draw = () => {
      const question = q(), order = state.options[question.id];
      root.querySelector('#mock-nav').innerHTML = state.ids.map((id, i) => `<button type="button" data-i="${i}" ${i === state.index ? 'aria-current="step"' : ''} class="${state.answers[id] ? 'is-answered' : ''}" aria-label="سؤال ${i + 1}${state.answers[id] ? '، تمت الإجابة' : ''}">${i + 1}</button>`).join('');
      root.querySelector('#mock-q').innerHTML = `<div class="study-question-watermarked">${questionWatermark()}<p class="study-label">السؤال ${state.index + 1} من ${state.ids.length}</p>${stem(question)}<fieldset class="study-quiz-question"><legend class="sr-only">الخيارات</legend>${order.map((oid, k) => { const o = question.options.find(x => x.id === oid); return `<label class="study-choice"><input type="radio" name="mock-choice" value="${esc(oid)}" ${state.answers[question.id] === oid ? 'checked' : ''}><span dir="ltr">${LETTERS[k]} · ${optionBody(o, math, esc, base, bank.assets)}</span></label>`; }).join('')}</fieldset></div>`;
      root.querySelector('#mock-prev').disabled = state.index === 0;
      root.querySelector('#mock-next').disabled = state.index === state.ids.length - 1;
      root.querySelectorAll('[name=mock-choice]').forEach(i => i.onchange = () => { state.answers[question.id] = i.value; save(); draw(); });
      root.querySelectorAll('#mock-nav [data-i]').forEach(b => b.onclick = () => { state.index = Number(b.dataset.i); save(); draw(); });
    };
    root.querySelector('#mock-prev').onclick = () => { state.index--; save(); draw(); };
    root.querySelector('#mock-next').onclick = () => { state.index++; save(); draw(); };
    const finish = reason => { dispose?.(); state = finishTermMock(state, bank, Date.now(), reason); state.guard = {...guard.state}; save(); result(); };
    root.querySelector('#mock-submit').onclick = () => { const left = state.ids.filter(id => !state.answers[id]).length; if (!left || confirm(`${left} أسئلة بلا إجابة. تسليم الاختبار؟`)) finish('submitted'); };
    const tick = () => { const left = mockRemaining(state, now()); root.querySelector('#mock-timer').textContent = fmt(left); if (!left) finish('timeout'); };
    // ---- focus guard ----
    const hide = () => { guard.leave(); state.guard = {...guard.state}; save(); content.setAttribute('aria-hidden', 'true'); content.inert = true; root.classList.add('mock-away'); cover.hidden = false; };
    const show = () => { guard.back(); state.guard = {...guard.state}; save(); content.removeAttribute('aria-hidden'); content.inert = false; root.classList.remove('mock-away'); cover.hidden = true; root.querySelector('#mock-away').textContent = `مرات المغادرة: ${guard.state.leaves}`; };
    const onVis = () => (document.hidden ? hide() : (document.hasFocus() ? show() : null));
    const onBlur = () => hide();
    const onFocus = () => { if (!document.hidden) show(); };
    const stopCopy = e => { if (root.contains(e.target)) e.preventDefault(); };
    document.addEventListener('visibilitychange', onVis); window.addEventListener('blur', onBlur); window.addEventListener('focus', onFocus); window.addEventListener('pagehide', onBlur);
    document.addEventListener('copy', stopCopy); document.addEventListener('contextmenu', stopCopy);
    if (document.hidden) hide();
    draw(); tick(); timer = setInterval(() => { if (!root.querySelector('.mock-run')) { dispose?.(); return; } tick(); }, 1000);
    dispose = () => { clearInterval(timer); document.removeEventListener('visibilitychange', onVis); window.removeEventListener('blur', onBlur); window.removeEventListener('focus', onFocus); window.removeEventListener('pagehide', onBlur); document.removeEventListener('copy', stopCopy); document.removeEventListener('contextmenu', stopCopy); };
  }

  function result() {
    const score = state.score ?? gradeTermMock(state, bank), g = state.guard || guard.state;
    const rows = state.ids.map((id, i) => {
      const q = byId.get(id), mine = state.answers[id], right = q.answer.correct_option_id, lo = bank.learning_outcomes.find(l => l.id === q.learning_outcome_id);
      const text = oid => { const o = q.options.find(x => x.id === oid); return o ? optionBody(o, math, esc, base, bank.assets) : '<em>بلا إجابة</em>'; };
      return `<article class="study-panel mock-review ${mine === right ? 'is-right' : 'is-wrong'}"><span class="study-label">${i + 1} · ${esc(q.learning_outcome_id)} · ${esc(lo?.title_ar || '')} · ${mine === right ? '✓ صحيح' : '✗ خطأ'}</span>${stem(q)}<p dir="ltr"><b>إجابتك:</b> ${text(mine)}</p>${mine === right ? '' : `<p dir="ltr"><b>الصحيح:</b> ${text(right)}</p>`}<p lang="en" dir="ltr">${esc(q.answer.explanation)}</p><a href="${backHref}/outcomes/${esc(q.learning_outcome_id)}">راجع الدرس ${esc(q.learning_outcome_id)} ←</a></article>`;
    }).join('');
    root.innerHTML = `<section class="study-booklet"><div class="study-toolbar"><a href="${backHref}">← الملزمة</a></div><div class="study-panel mock-result"><span class="study-label">النتيجة · RESULT</span><h2>${score} / ${state.ids.length}</h2><p lang="ar" dir="rtl">${state.reason === 'timeout' ? 'انتهى الوقت وتم التسليم تلقائيًا. ' : ''}مرات مغادرة المتصفح: <b>${g.leaves}</b>${g.leaves ? ` (≈ ${Math.round(g.awayMs / 1000)} ثانية)` : ''}.</p><div class="study-slide-actions"><button type="button" id="mock-again" class="btn-primary">اختبار جديد · New mock</button><button type="button" id="mock-print">طباعة</button></div></div>${rows}</section>`;
    root.querySelector('#mock-again').onclick = () => { try { storage?.removeItem(key); } catch {} state = null; guard.state.leaves = 0; guard.state.awayMs = 0; start(); };
    root.querySelector('#mock-print').onclick = () => window.print();
  }

  if (state) run(); else start();
}
