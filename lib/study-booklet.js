import {questionWatermark} from './watermark.js';
import {classroomLabels} from './branding.js';
import {normalizeStudyMath} from './study-math.js';
import {bankMath} from './exam-bank-math.js';
import '../study-booklet.css';
import {calculatorGuide} from './calculator-guide.js';
import {renderCalculatorExamples} from './calculator-examples.js';
import {setupFloatingCalculator} from './floating-calculator.js';
import {setupQuestionWalkthrough} from './question-walkthrough.js';
import {initMathAnswerEditors} from './math-answer-editor.js';
import {modeBadge,ribbonMarkup,windowMarkup,setupExampleWindow} from './study-window.js';
import {fillMarkup,parseBlanks,wireFill} from './study-fill.js';
import {plotMarkup,wirePlot} from './study-plot.js';
import {renderStudyMock,stopStudyMock} from './study-mock.js';
import {renderPrintSheet} from './study-print.js';
import {translate,bidi} from './study-translate.js';
import {optionBody} from './study-option.js';

const title = 'مذاكرة الهيكل الاختبار النهائي للفصل الاول';
const names = Object.fromEntries(['9G3','10G3','10A1','11G','11A','12G','12A'].map(id=>[id,classroomLabels[id].ar]));
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const math = value => bankMath(normalizeStudyMath(value));
const pair = (ar,en) => `<div class="study-ar" lang="ar" dir="rtl">${escape(ar)}</div><div class="study-en" lang="en" dir="ltr">${escape(en)}</div>`;
const href = (classroom,lo) => `#/classrooms/${classroom}/banks/term1${lo?'/outcomes/'+lo:''}`;
const cache = new Map();
export async function renderStudyBooklet({root,route,studentKey='guest'}) {
  const requestHash = location.hash, classroom = route.classroom;
  if (!route.mock) stopStudyMock();
  root.innerHTML = '<p role="status">جارٍ فتح الملزمة · Opening your study booklet…</p>';
  try {
    if (!cache.has(classroom)) {
      const base=import.meta.env?.BASE_URL || '/';
      const [response,supportResponse] = await Promise.all([fetch(`${base}data/study/${classroom}.json`),fetch(`${base}data/study/calculator-support.json`)]);
      if (!response.ok || !supportResponse.ok) throw Error('load');
      const bank=await response.json(), support=(await supportResponse.json()).classes[classroom];
      for(const q of bank.questions)q.calculatorSupport=support.questions[q.id];
      for(const o of bank.learning_outcomes)o.calculatorStrategy=support.outcomes[o.id].prepare;
      try { const tr = await fetch(`${base}data/study/translations-ar.json`); if (tr.ok) bank.translations = await tr.json(); } catch {}
      cache.set(classroom, bank);
    }
    if (location.hash !== requestHash) return;
    const bank = cache.get(classroom);
    const siteBase = import.meta.env?.BASE_URL || '/';
    if (route.mock) return renderStudyMock({root, bank, studentKey, backHref: href(classroom), base: siteBase});
    if (route.print) return renderPrintSheet({root, bank, classroom, backHref: href(classroom), base: siteBase});
    const storageKey = 'study-v1-' + classroom + '-' + studentKey;
    let progress = {};
    try { progress = JSON.parse(sessionStorage.getItem(storageKey) || '{}'); } catch {}
    if (!progress || typeof progress !== 'object' || Array.isArray(progress)) progress = {};
    const header = () => `<header class="study-hero"><div><p class="study-kicker">TERM 01 / STUDY COMPANION / 2026–2027</p><h1 lang="ar" dir="rtl">${title}</h1><p>Final exam structure revision · ${escape(names[classroom])}</p></div><div class="study-total"><strong>${bank.learning_outcomes.length}</strong><span>مخرج تعلم<br>Learning outcomes</span></div></header><nav class="study-classes" aria-label="الصفوف · Classes">${Object.entries(names).map(([id,name])=>`<a href="${href(id)}" ${id===classroom?'aria-current="page"':''}>${name}</a>`).join('')}</nav>`;
    const outcome = bank.learning_outcomes.find(lo=>lo.id===route.outcomeId);
    if (route.outcomeId && !outcome) {
      root.innerHTML = `<section class="study-booklet">${header()}<p role="alert">المخرج غير موجود · Outcome unavailable</p><a href="${href(classroom)}">العودة للملزمة · Back</a></section>`;
      return;
    }
    if (!outcome) {
      root.innerHTML = `<section class="study-booklet">${header()}<div class="study-intro">${pair('رحلتك من الفكرة إلى الحل','Your path from understanding to independent practice')}<p lang="ar" dir="rtl">افهم القاعدة ← شاهد مثالًا محلولًا ← حل سؤالًا مشابهًا بمساعدة تدريجية ← راجع بقية التدريبات.</p><p lang="en" dir="ltr">Understand the rule → study a worked example → try a similar question with guided support → practise the remaining questions.</p><p class="study-subtle">مساعد موجّه بقواعد وشروح المحتوى · Content-based guided assistant</p></div><div class="study-cta"><a class="study-cta-card cta-mock" href="${href(classroom)}/mock"><b>اختبار تجريبي</b><span>20 سؤالًا · ساعة واحدة · سؤال لكل مخرج</span></a><a class="study-cta-card cta-print" href="${href(classroom)}/print"><b>طباعة الأسئلة المقالية</b><span>مع مساحات كتابة وأوراق رسم</span></a></div><label class="study-search">ابحث عن درس أو صفحة · Find a topic or page<input type="search" id="study-search" placeholder="LO · الموضوع · page"></label><p id="study-count" role="status"></p><div class="study-grid"></div><p class="study-subtle">المصدر assessment-transfer.zip · المراجع كما وردت في الملف المرفق. الحفظ في علامة التبويب الحالية فقط.<br>References follow the supplied transfer package. Progress stays in this browser tab.</p></section>`;
      const draw = () => {
        const term = root.querySelector('#study-search').value.trim().toLowerCase();
        const filtered = bank.learning_outcomes.filter(lo => JSON.stringify([lo.id,lo.title,lo.title_ar,lo.textbook_references]).toLowerCase().includes(term));
        root.querySelector('#study-count').textContent = `${filtered.length} / ${bank.learning_outcomes.length} · الدروس / Lessons`;
        root.querySelector('.study-grid').innerHTML = filtered.map((lo,i)=>`<a class="study-topic" href="${href(classroom,lo.id)}"><span class="study-topic-top"><b>${lo.id} / ${lo.exam_slot}</b><span>${progress[lo.id]?'✓ راجعت الدرس':'ابدأ المذاكرة'}</span></span><h2 lang="en" dir="ltr">${escape(lo.title)}</h2><small>${escape(lo.textbook_references.map(r=>(r.printed_page?'p. '+r.printed_page+' · ':'')+r.exercises_or_section).join(' / '))}</small><div class="study-topic-bottom">${lo.question_ids.length} تدريبات · ${lo.question_type.toUpperCase()}<b>افتح الدرس ←</b></div></a>`).join('') || '<p>لا توجد نتائج · No results</p>';
      };
      root.querySelector('#study-search').oninput = draw;
      draw();
      return;
    }
    const questions = outcome.question_ids.map(id => bank.questions.find(q=>q.id===id)).filter(Boolean);
    let practiceIndex = 0, phase = 2, hint = 0, chosen = '', checked = false;
    const drafts = {};
    const assetBase = import.meta.env?.BASE_URL || '/';
    const guide = q => q.calculatorSupport || q.calculator?.applicable ? calculatorGuide({...q, calculator:{...q.calculator, image: (q.calculator?.image || '').split('/').slice(-2).join('/')}, figures: (q.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(a => ({src: `${assetBase}${a.src}`, alt: a.alt_text}))}, `${assetBase}data/exam-banks/${{'9G3':'9g3-term1','10G3':'10g3-term1','10A1':'10a1-term1'}[classroom] || ''}/`) : '<p class="study-subtle">لا يتوفر دليل حاسبة لهذا السؤال. · No calculator guide for this question.</p>';
    const example = questions[0];
    const options = question => question.options || [];
    const diagrams = question => (question.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(asset => `<figure><img loading="lazy" src="${assetBase}${escape(asset.src)}" alt="${escape(asset.alt_text)}"><figcaption>${escape(asset.alt_text)}</figcaption></figure>`).join('');
    const trans = (kind, text) => translate(bank.translations, kind, text);
    const KIND_AR = {textbook_exercise: 'تمرين من الكتاب', example_variant: 'نسخة من مثال', concept_application: 'تطبيق على المفهوم', review_question: 'سؤال من هيكل المراجعة', authored_lo_variant: 'سؤال مؤلَّف على المخرج', textbook_mcq_conversion: 'تمرين من الكتاب بصيغة اختيار', example_application: 'تطبيق على مثال', exercise_conversion: 'تمرين محوَّل', review_clarification: 'سؤال مراجعة موضَّح', review_rephrasing: 'سؤال مراجعة بصياغة جديدة', cross_outcome_rephrasing: 'سؤال بصياغة جديدة', user_authorized_graph_variant: 'رسم بديل معتمد'};
    const prompt = question => {
      const parts = question.parts || [], arMain = trans('instruction', question.instruction);
      const arParts = parts.map(part => ({id: part.id, text: trans('part', part.prompt)})).filter(x => x.text);
      return `<div class="q-frame study-question-watermarked">${questionWatermark()}<div class="q-frame-head"><b>السؤال ${escape(question.display_number)}</b><span>${escape(KIND_AR[question.source_kind] || '')} · ${question.source?.printed_page?'Reveal p. '+escape(question.source.printed_page)+' · ':''}${escape(question.source?.exercise)}</span></div>
      <div class="q-frame-en" lang="en" dir="ltr"><p class="q-main">${escape(question.math_latex ? question.instruction : question.stem)}</p>${question.math_latex ? `<div class="study-math">${math(question.math_latex)}</div>` : ''}${parts.map(part => `<div class="q-frame-part"><b>${escape(part.id)}.</b> ${escape(part.prompt)}${part.math_latex ? `<div class="study-math">${math(part.math_latex)}</div>` : ''}</div>`).join('')}</div>
      ${diagrams(question)}${question.figure_quality ? '<p class="q-fig-note" lang="ar" dir="rtl">ملاحظة: هذا الشكل من ملزمة المراجعة ' + (question.figure_quality === 'low_resolution' ? 'بدقة منخفضة' : 'مقصوص الحواف قليلاً') + '، وسيُستبدل بقصاصة الكتاب الأصلية.</p>' : ''}${arMain || arParts.length ? `<div class="q-frame-ar" lang="ar" dir="rtl"><span class="q-frame-tag">الترجمة</span>${arMain ? `<p>${bidi(escape(arMain))}</p>` : ''}${arParts.map(x => `<p><b>${escape(x.id)}.</b> ${bidi(escape(x.text))}</p>`).join('')}</div>` : ''}</div>`;
    };
    const optAr = o => { const a = o.math_latex ? '' : trans('option', o.text); return a ? `<small class="opt-ar" lang="ar" dir="rtl">${bidi(escape(a))}</small>` : ''; };
    const answer = question => question.type === 'mcq'
      ? `<div class="study-math">${question.answer?.correct_option_id} · ${(options(question).find(o=>o.id===question.answer?.correct_option_id)?.math_latex ? math(question.answer?.correct_option_text) : escape(question.answer?.correct_option_text))}</div><p lang="en" dir="ltr">${escape(question.answer?.explanation)}</p>`
      : (question.parts || []).map(part=>`<div class="study-answer-part"><b>${escape(part.id)}</b><p lang="en" dir="ltr">${escape(part.prompt)}</p><div class="study-math">${math(part.answer?.math_latex)}</div><p lang="en" dir="ltr">${escape(part.answer?.model_answer_and_marking)}</p></div>`).join('');
    const steps = question => `<ol class="study-steps"><li>${pair('حدّد المطلوب والمعطيات في السؤال والرسم قبل اختيار العملية.','Identify the requested quantity and the given values in the prompt and diagram.')}</li><li>${pair(outcome.rule_ar,outcome.rule_summary)}</li><li>${pair('طبّق القاعدة على معطيات هذا السؤال، ثم قارن ناتجك بالحل المرجعي أدناه.','Apply the rule to this question’s values, then compare your result with the reference solution below.')}${answer(question)}</li><li>${pair('تحقّق من الإشارات والمجال والوحدات. عوّض للتحقق إذا كانت المسألة معادلة.','Check signs, domain restrictions and units. Substitute back when the task is an equation.')}</li></ol>`;
    root.innerHTML = `<section class="study-booklet">${header()}<div class="study-toolbar"><a href="${href(classroom)}">← فهرس الملزمة · Contents</a><button id="study-print">طباعة الدرس · Print lesson</button></div>${ribbonMarkup()}${windowMarkup({rule:`<div class="study-rule ew-rule"><span>الفكرة الأساسية · THE IDEA</span>${pair(outcome.rule_ar,outcome.rule_summary)}<h3 lang="en">Calculator strategy for this outcome</h3><p lang="en" dir="ltr">${escape(outcome.calculatorStrategy)}</p></div>`,demos:`<details class="study-panel calculator-examples" open><summary>Illustrated calculator walkthroughs</summary><p>These are worked examples, not the current question. Each frame shows the screen after the highlighted key. The fx‑991CE X emulator may differ from your calculator.</p><div id="calculator-examples" role="region" aria-label="أمثلة الحاسبة المصوّرة"><p>جارٍ تحميل الأمثلة…</p></div></details>`,question:prompt(example),badge:modeBadge(example),manual:steps(example),calculator:guide(example).replace('<details class="calculator-guide','<details open class="calculator-guide')})}<section id="floating-calculator" class="floating-calculator" aria-label="Movable calculator" hidden><div class="floating-calculator-bar"><strong>Calculator · drag to move</strong><div><button type="button" id="calculator-dock-left" aria-label="Move calculator to left">◀</button><button type="button" id="calculator-dock-right" aria-label="Move calculator to right">▶</button><button type="button" id="calculator-close" aria-label="Close calculator">×</button></div></div><p>fx‑991CE X emulator: menus may differ from fx‑991EX or fx‑991ES PLUS. Verify answers on your calculator.</p><iframe class="study-calculator-frame" title="Interactive ClassWiz calculator" loading="lazy"></iframe><a href="https://github.com/magicnothief/fx991ex-emulator" target="_blank" rel="noopener noreferrer">Emulator source</a></section><div class="study-lesson-title"><span>${outcome.id} / ${outcome.exam_slot}</span><h2 lang="en">${escape(outcome.title)}</h2><p lang="ar" dir="rtl">${escape(outcome.title_ar)}</p></div><div class="study-columns"><aside class="study-panel study-coach"><label class="q-pick">أسئلة الهيكل · Structure questions<select id="study-practice-select">${questions.map((q,i)=>`<option value="${i}">${q.display_number} · ${q.source?.printed_page ? 'p. ' + q.source.printed_page + ' · ' : ''}${q.source?.exercise ?? ''}${q.type === 'frq' ? ' · FRQ' : ''}</option>`).join('')}</select></label><div id="study-practice"></div><div class="study-slide-actions"><button type="button" id="practice-prev">السابق · Previous</button><button type="button" id="practice-next">التالي · Next</button></div></aside></div><section class="study-panel study-quiz" id="study-quiz"><span class="study-label">اختبر فهمك · CHECK YOUR LEARNING</span><h3>اختبار المخرج</h3><p>أجب عن أسئلة الاختيار، ثم اعرض النتيجة. الأسئلة الكتابية تراجع ذاتيًا في التدريب.</p><div id="study-quiz-content"></div></section><div class="study-finish"><label><input type="checkbox" id="study-done" ${progress[outcome.id]?'checked':''}> راجعت هذا الدرس · I reviewed this lesson</label><span id="study-save" role="status"></span><a href="${href(classroom,bank.learning_outcomes[bank.learning_outcomes.indexOf(outcome)+1]?.id)}">الدرس التالي / الفهرس ← Next</a></div></section>`;
    setupQuestionWalkthrough(root, assetBase);
    root._calculatorGuideController?.abort();
    root._calculatorGuideController = new AbortController();
    root.addEventListener('click', event => {
      const button = event.target.closest('[data-guide-target], [data-guide-open-calculator]');
      if (!button || !root.contains(button)) return;
      if (button.hasAttribute('data-guide-open-calculator')) {
        const launch = root.querySelector('#open-floating-calculator');
        if (launch?.getAttribute('aria-expanded') !== 'true') launch?.click();
      } else {
        const guide = button.closest('.calculator-support');
        const section = guide?.querySelector(`[data-guide-section="${button.dataset.guideTarget}"]`);
        (section || guide?.querySelector('[data-guide-section="prepare"]'))?.scrollIntoView({block:'center',behavior:'smooth'});
      }
    }, {signal:root._calculatorGuideController.signal});
    const modes=new Set(questions.map(q=>q.calculatorSupport?.role));
    const examples=['quadratic','linear','table'].filter(id=>id==='quadratic'?modes.has('quadratic'):id==='linear'?modes.has('solve'):modes.has('table')||modes.has('function_check'));
    const examplesRoot=root.querySelector('#calculator-examples');
    if(examples.length)renderCalculatorExamples(examplesRoot,assetBase,examples);else{examplesRoot.closest('details').hidden=true;root.querySelector('#ew-tab-demos').hidden=true;root.querySelector('#open-calculator-demos').hidden=true;}
    setupFloatingCalculator(root, assetBase);
    setupExampleWindow(root);
    root.querySelector('#study-print').onclick = () => window.print();
    root.querySelector('#study-done').onchange = event => {
      progress[outcome.id] = event.target.checked;
      try { sessionStorage.setItem(storageKey,JSON.stringify(progress)); root.querySelector('#study-save').textContent='تم الحفظ في هذه التبويبة · Saved in this tab'; }
      catch { root.querySelector('#study-save').textContent='تعذّر الحفظ · Could not save'; }
    };
    root.querySelector('#study-practice-select').onchange = event => {
      practiceIndex=Number(event.target.value); phase=2;hint=0;chosen=drafts[questions[practiceIndex].id]?.choice || '';checked=false;drawPractice();
    };
    const changePractice = index => { const select=root.querySelector('#study-practice-select'); select.value=String(index); select.dispatchEvent(new Event('change')); };
    root.querySelector('#practice-prev').onclick=()=>changePractice(practiceIndex-1);
    root.querySelector('#practice-next').onclick=()=>changePractice(practiceIndex+1);
    const interactiveHtml = question => (question.parts||[]).map(part=>{
      if(!part.blanks&&!part.plot)return '';
      const id=`ip-${question.id}-${part.id}`;
      return `<div class="q-fill" data-part="${escape(part.id)}"><div class="q-fill-label"><b>${escape(part.id)}.</b> ${escape(part.prompt)} · <span lang="ar" dir="rtl">أكمل الفراغات</span></div>${part.blanks?`${fillMarkup(part.blanks,id).html}<div class="q-fill-actions"><button type="button" data-fill="check" class="btn-primary">تحقّق · Check</button><button type="button" data-fill="reveal">أظهر الحل · Show</button><button type="button" data-fill="reset">مسح · Clear</button></div><div class="q-fill-feedback" role="status" aria-live="polite"></div>`:''}${part.plot?plotMarkup(part.plot,id+'-plot'):''}</div>`;
    }).join('');
    const mountInteractive = (area,question) => area.querySelectorAll('.q-fill').forEach(box=>{
      const part=question.parts.find(p=>p.id===box.dataset.part), saved=((drafts[question.id] ||= {}).fill ||= {});
      if(part.blanks){
        const fb=box.querySelector('.q-fill-feedback'), w=wireFill(box.querySelector('.fill-box'),parseBlanks(part.blanks),()=>{saved[part.id]=w.values();});
        if(saved[part.id])w.setValues(saved[part.id]);
        box.querySelector('[data-fill=check]').onclick=()=>{const r=w.check();fb.className='q-fill-feedback '+(r.all?'is-right':'is-wrong');fb.textContent=r.all?'صحيح! جميع الفراغات صحيحة · All blanks correct.':`${r.correct} من ${r.total} فراغات صحيحة؛ راجع الأحمر · ${r.correct} of ${r.total} blanks correct.`;};
        box.querySelector('[data-fill=reveal]').onclick=()=>{w.reveal();saved[part.id]=w.values();fb.className='q-fill-feedback';fb.textContent='هذا هو الحل المرجعي · Reference working shown.';};
        box.querySelector('[data-fill=reset]').onclick=()=>{w.reset();delete saved[part.id];fb.textContent='';fb.className='q-fill-feedback';};
      }
      if(part.plot)wirePlot(box.querySelector('.plot-box'),part.plot);
    });
    function drawPractice() {
      root.querySelector('#practice-prev').disabled=practiceIndex<=0;
      root.querySelector('#practice-next').disabled=practiceIndex>=questions.length-1;
      const question = questions[practiceIndex], area = root.querySelector('#study-practice');
      area.innerHTML = `${prompt(question)}<div class="q-answer-box">${question.type==='mcq'?`<fieldset><legend class="sr-only">اختر الإجابة · Choose</legend>${options(question).map(o=>`<label class="study-choice"><input type="radio" name="study-choice" value="${escape(o.id)}" ${chosen===o.id?'checked':''}><span class="opt-wrap"><span dir="ltr">${escape(o.id)} · ${optionBody(o,math,escape,assetBase,bank.assets)}</span>${optAr(o)}</span></label>`).join('')}</fieldset><button id="study-check" class="btn-primary">تحقّق · Check</button><div id="study-feedback" role="status"></div>`:`${interactiveHtml(question)}${(question.parts||[]).map((part,i)=>(part.blanks||part.plot)?'':`<div class="study-writing math-answer-editor"><label id="math-label-${i}">${escape(part.id)}. إجابتك · Your answer</label><math-field data-writing="${i}" aria-labelledby="math-label-${i}" dir="ltr" math-virtual-keyboard-policy="manual"></math-field><details class="math-tools"><summary>أدوات الكتابة الرياضية · Math tools</summary><div class="math-toolbar" role="group" aria-label="Math templates"><button type="button" data-math-template="fraction" aria-label="Insert fraction">${math('\\frac{\\square}{\\square}')}<span>Fraction · كسر</span></button><button type="button" data-math-template="power" aria-label="Insert power">${math('x^{\\square}')}<span>Power · قوة</span></button><button type="button" data-math-template="root" aria-label="Insert square root">${math('\\sqrt{\\square}')}<span>Root · جذر</span></button><button type="button" data-math-template="nthroot" aria-label="Insert nth root">${math('\\sqrt[n]{x}')}<span>ⁿ√x</span></button><button type="button" data-math-template="subscript" aria-label="Insert subscript">${math('x_{n}')}<span>Subscript</span></button><button type="button" data-math-template="brackets" aria-label="Insert parentheses">( )<span>Brackets</span></button><button type="button" data-math-template="pi" aria-label="Insert pi">π</button><button type="button" data-math-template="infinity" aria-label="Insert infinity">∞</button><button type="button" data-math-template="le" aria-label="Insert less than or equal">≤</button><button type="button" data-math-template="ge" aria-label="Insert greater than or equal">≥</button><button type="button" data-math-keyboard>⌨ Math keyboard · لوحة الرياضيات</button></div><p>استخدم Tab للانتقال بين خانات الكسر أو القوة. · Use Tab to move between boxes.</p></details></div>`).join('')}`}</div>
      <div class="q-help-bar" role="group" aria-label="مساعدة عند الطلب · Help on request"><button type="button" data-help="hint">💡 تلميح · Hint</button><button type="button" data-help="solution">✓ طريقة الحل · Solution</button><button type="button" data-help="calc">⌗ الحل بالحاسبة · Calculator</button><button type="button" data-help="example">✎ المثال · Example</button></div><div class="q-help-panel" role="region" aria-live="polite" hidden></div>`;
      initMathAnswerEditors(area, drafts, question.id);
      mountInteractive(area, question);
      const feedback = () => {
        const target = area.querySelector('#study-feedback');
        if(!target || !checked) return;
        if(!chosen){target.innerHTML=pair('اختر إجابة أولًا.','Choose an answer first.');return;}
        const correct=chosen===question.answer.correct_option_id;
        target.innerHTML=correct?pair('صحيح! أحسنت.','Correct!'):pair('ليست الإجابة الصحيحة، حاول مرة أخرى. يمكنك طلب تلميح.','Not quite. Try again; you can ask for a hint.');
        target.className=correct?'study-correct':'study-retry';
      };
      area.querySelectorAll('[name="study-choice"]').forEach(input=>input.onchange=()=>{chosen=input.value;(drafts[question.id] ||= {}).choice=chosen;checked=false;});
      area.querySelector('#study-check')?.addEventListener('click',()=>{checked=true;feedback();});
      // hints, the solution method and the calculator route appear only when requested
      const panel=area.querySelector('.q-help-panel'); let openKind='';
      const helpContent={
        hint:()=>{hint=Math.min(hint+1,2);return `<h4>تلميح ${hint} من 2 · Hint ${hint} of 2</h4>${hint===1?pair(outcome.rule_ar,outcome.rule_summary):pair('طبّق القاعدة على معطيات هذا السؤال مع مراجعة الإشارات والوحدات، وقارن مع المثال.','Apply the rule to this question’s values, checking signs and units; compare with the example.')}${hint<2?'<p class="study-subtle">اضغط «تلميح» مرة أخرى لتلميح إضافي.</p>':''}`;},
        solution:()=>`<h4>طريقة الحل · Solution method</h4>${steps(question)}`,
        calc:()=>`${modeBadge(question)}${guide(question).replace('<details class="calculator-guide','<details open class="calculator-guide')}`
      };
      area.querySelectorAll('[data-help]').forEach(button=>button.onclick=()=>{
        const kind=button.dataset.help;
        if(kind==='example'){const w=root.querySelector('#example-window');if(w.hidden)root.querySelector('#open-example-window').click();return;}
        if(openKind===kind&&kind!=='hint'){panel.hidden=true;openKind='';area.querySelectorAll('[data-help]').forEach(b=>b.removeAttribute('aria-pressed'));return;}
        panel.innerHTML=helpContent[kind]();panel.hidden=false;openKind=kind;
        area.querySelectorAll('[data-help]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      });
    }
    drawPractice();
    const quizQuestions = questions.filter(q => q.type === 'mcq' && q.options?.length && q.answer?.correct_option_id);
    const quizArea = root.querySelector('#study-quiz-content');
    if (!quizQuestions.length) quizArea.innerHTML = '<p>هذا المخرج كتابي. استخدم حقول المحاولة وقارن كل جزء بالحل المرجعي؛ لا يوجد تصحيح آلي لهذا المخرج بعد.</p>';
    else {
      let quizIndex = 0;
      const selected = Array(quizQuestions.length).fill('');
      let submitted = false;
      const drawQuiz = () => {
        const q = quizQuestions[quizIndex];
        const score = quizQuestions.filter((item,i)=>selected[i]===item.answer.correct_option_id).length;
        quizArea.innerHTML = `<div class="study-slide-nav" aria-label="أسئلة الاختبار · Quiz questions">${quizQuestions.map((item,i)=>`<button type="button" data-quiz-index="${i}" aria-label="السؤال ${i+1}${selected[i]?'، تمت الإجابة':''}" ${i===quizIndex?'aria-current="step"':''} class="${selected[i]?'is-answered':''}">${i+1}</button>`).join('')}</div><fieldset class="study-quiz-question"><legend>السؤال ${quizIndex+1} من ${quizQuestions.length}</legend>${prompt(q)}${options(q).map(o=>`<label class="study-choice"><input type="radio" name="quiz-choice" value="${escape(o.id)}" ${selected[quizIndex]===o.id?'checked':''}><span class="opt-wrap"><span dir="ltr">${escape(o.id)} · ${optionBody(o,math,escape,assetBase,bank.assets)}</span>${optAr(o)}</span></label>`).join('')}</fieldset><div class="study-slide-actions"><button type="button" id="quiz-prev" ${quizIndex===0?'disabled':''}>السابق · Previous</button><button type="button" id="quiz-next" ${quizIndex===quizQuestions.length-1?'disabled':''}>التالي · Next</button><button type="button" id="quiz-submit">عرض النتيجة · Show result</button></div><p role="status">${selected.filter(Boolean).length} / ${quizQuestions.length} مجاب</p>${submitted?`<div id="study-quiz-result" role="status"><h4>النتيجة: ${score} / ${quizQuestions.length}</h4><p>غير المجاب: ${selected.filter(v=>!v).length} · يمكنك تغيير الإجابات وإعادة التحقق.</p><p>${selected[quizIndex]===q.answer.correct_option_id?'إجابة صحيحة':'راجع إجابة هذا السؤال'}</p><details><summary>عرض الإجابة والشرح · Review answer</summary>${answer(q)}${guide(q)}</details></div>`:''}`;
        quizArea.querySelectorAll('[data-quiz-index]').forEach(button=>button.onclick=()=>{quizIndex=Number(button.dataset.quizIndex);drawQuiz()});
        quizArea.querySelectorAll('[name="quiz-choice"]').forEach(input=>input.onchange=()=>{selected[quizIndex]=input.value;submitted=false;drawQuiz()});
        quizArea.querySelector('#quiz-prev').onclick=()=>{quizIndex--;drawQuiz()};
        quizArea.querySelector('#quiz-next').onclick=()=>{quizIndex++;drawQuiz()};
        quizArea.querySelector('#quiz-submit').onclick=()=>{submitted=true;drawQuiz()};
      };
      drawQuiz();
    }
  } catch (error) {
    if(location.hash!==requestHash)return;
    root.innerHTML='<p role="alert">تعذّر تحميل الملزمة · Could not load the study booklet.</p><button id="study-retry">إعادة المحاولة · Retry</button>';
    root.querySelector('#study-retry').onclick=()=>renderStudyBooklet({root,route,studentKey});
  }
}
