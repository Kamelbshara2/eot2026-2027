import {questionWatermark} from './watermark.js';
import {normalizeStudyMath} from './study-math.js';
import {bankMath} from './exam-bank-math.js';
import '../study-booklet.css';
import {calculatorGuide} from './calculator-guide.js';
import {renderCalculatorExamples} from './calculator-examples.js';
import {setupFloatingCalculator} from './floating-calculator.js';
import {setupQuestionWalkthrough} from './question-walkthrough.js';
import {initMathAnswerEditors} from './math-answer-editor.js';

const title = 'مذاكرة الهيكل الاختبار النهائي للفصل الاول';
const names = {'9G3':'التاسع العام','10G3':'العاشر العام','10A1':'العاشر المتقدم'};
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const math = value => bankMath(normalizeStudyMath(value));
const pair = (ar,en) => `<div class="study-ar" lang="ar" dir="rtl">${escape(ar)}</div><div class="study-en" lang="en" dir="ltr">${escape(en)}</div>`;
const href = (classroom,lo) => `#/classrooms/${classroom}/banks/term1${lo?'/outcomes/'+lo:''}`;
const cache = new Map();
export async function renderStudyBooklet({root,route,studentKey='guest'}) {
  const requestHash = location.hash, classroom = route.classroom;
  root.innerHTML = '<p role="status">جارٍ فتح الملزمة · Opening your study booklet…</p>';
  try {
    if (!cache.has(classroom)) {
      const base=import.meta.env?.BASE_URL || '/';
      const [response,supportResponse] = await Promise.all([fetch(`${base}data/study/${classroom}.json`),fetch(`${base}data/study/calculator-support.json`)]);
      if (!response.ok || !supportResponse.ok) throw Error('load');
      const bank=await response.json(), support=(await supportResponse.json()).classes[classroom];
      for(const q of bank.questions)q.calculatorSupport=support.questions[q.id];
      for(const o of bank.learning_outcomes)o.calculatorStrategy=support.outcomes[o.id].prepare;
      cache.set(classroom, bank);
    }
    if (location.hash !== requestHash) return;
    const bank = cache.get(classroom);
    const storageKey = 'study-v1-' + classroom + '-' + studentKey;
    let progress = {};
    try { progress = JSON.parse(sessionStorage.getItem(storageKey) || '{}'); } catch {}
    if (!progress || typeof progress !== 'object' || Array.isArray(progress)) progress = {};
    const header = () => `<header class="study-hero"><div><p class="study-kicker">TERM 01 / STUDY COMPANION / 2026–2027</p><h1 lang="ar" dir="rtl">${title}</h1><p>Final exam structure revision · ${escape(names[classroom])} · ${classroom}</p></div><div class="study-total"><strong>${bank.learning_outcomes.length}</strong><span>مخرج تعلم<br>Learning outcomes</span></div></header><nav class="study-classes" aria-label="الصفوف · Classes">${Object.entries(names).map(([id,name])=>`<a href="${href(id)}" ${id===classroom?'aria-current="page"':''}>${name} · ${id}</a>`).join('')}</nav>`;
    const outcome = bank.learning_outcomes.find(lo=>lo.id===route.outcomeId);
    if (route.outcomeId && !outcome) {
      root.innerHTML = `<section class="study-booklet">${header()}<p role="alert">المخرج غير موجود · Outcome unavailable</p><a href="${href(classroom)}">العودة للملزمة · Back</a></section>`;
      return;
    }
    if (!outcome) {
      root.innerHTML = `<section class="study-booklet">${header()}<div class="study-intro">${pair('رحلتك من الفكرة إلى الحل','Your path from understanding to independent practice')}<p lang="ar" dir="rtl">افهم القاعدة ← شاهد مثالًا محلولًا ← حل سؤالًا مشابهًا بمساعدة تدريجية ← راجع بقية التدريبات.</p><p lang="en" dir="ltr">Understand the rule → study a worked example → try a similar question with guided support → practise the remaining questions.</p><p class="study-subtle">مساعد موجّه بقواعد وشروح المحتوى · Content-based guided assistant</p></div><label class="study-search">ابحث عن درس أو صفحة · Find a topic or page<input type="search" id="study-search" placeholder="LO · الموضوع · page"></label><p id="study-count" role="status"></p><div class="study-grid"></div><p class="study-subtle">المصدر assessment-transfer.zip · المراجع كما وردت في الملف المرفق. الحفظ في علامة التبويب الحالية فقط.<br>References follow the supplied transfer package. Progress stays in this browser tab.</p></section>`;
      const draw = () => {
        const term = root.querySelector('#study-search').value.trim().toLowerCase();
        const filtered = bank.learning_outcomes.filter(lo => JSON.stringify([lo.id,lo.title,lo.title_ar,lo.textbook_references]).toLowerCase().includes(term));
        root.querySelector('#study-count').textContent = `${filtered.length} / ${bank.learning_outcomes.length} · الدروس / Lessons`;
        root.querySelector('.study-grid').innerHTML = filtered.map((lo,i)=>`<a class="study-topic" href="${href(classroom,lo.id)}"><span class="study-topic-top"><b>${lo.id} / ${lo.exam_slot}</b><span>${progress[lo.id]?'✓ راجعت الدرس':'ابدأ المذاكرة'}</span></span><h2 lang="en" dir="ltr">${escape(lo.title)}</h2><small>${escape(lo.textbook_references.map(r=>'p. '+r.printed_page+' · '+r.exercises_or_section).join(' / '))}</small><div class="study-topic-bottom">${lo.question_ids.length} تدريبات · ${lo.question_type.toUpperCase()}<b>افتح الدرس ←</b></div></a>`).join('') || '<p>لا توجد نتائج · No results</p>';
      };
      root.querySelector('#study-search').oninput = draw;
      draw();
      return;
    }
    const questions = outcome.question_ids.map(id => bank.questions.find(q=>q.id===id)).filter(Boolean);
    let practiceIndex = Math.min(1,questions.length-1), phase = 2, hint = 0, chosen = '', checked = false;
    const drafts = {};
    const assetBase = import.meta.env?.BASE_URL || '/';
    const guide = q => q.calculatorSupport || q.calculator?.applicable ? calculatorGuide({...q, calculator:{...q.calculator, image: (q.calculator.image || '').split('/').slice(-2).join('/')}}, `${assetBase}data/exam-banks/${{'9G3':'9g3-term1','10G3':'10g3-term1','10A1':'10a1-term1'}[classroom]}/`) : '<p class="study-subtle">لا يتوفر دليل حاسبة لهذا السؤال. · No calculator guide for this question.</p>';
    const example = questions[0];
    const options = question => question.options || [];
    const diagrams = question => (question.diagram_asset_ids || []).map(id => bank.assets[id]).filter(Boolean).map(asset => `<figure><img loading="lazy" src="${assetBase}${escape(asset.src)}" alt="${escape(asset.alt_text)}"><figcaption>${escape(asset.alt_text)}</figcaption></figure>`).join('');
    const prompt = question => `<div class="study-question-watermarked">${questionWatermark()}<p lang="ar" dir="rtl" class="study-subtle">تدريب على ${escape(outcome.title_ar)} · اقرأ المعطيات التالية.</p><div lang="en" dir="ltr"><p>${escape(question.math_latex ? question.instruction : question.stem)}</p>${question.math_latex?'<div class="study-math">'+math(question.math_latex)+'</div>':''}${diagrams(question)}${(question.parts||[]).map(part=>`<div class="study-part"><b>${escape(part.id)}.</b> ${escape(part.prompt)}${part.math_latex?'<div class="study-math">'+math(part.math_latex)+'</div>':''}</div>`).join('')}</div><small class="study-source">Reveal · p. ${escape(question.source?.printed_page)} · ${escape(question.source?.exercise)} · ${escape(question.source_kind)} · ${escape(question.id)}</small></div>`;
    const answer = question => question.type === 'mcq'
      ? `<div class="study-math">${question.answer?.correct_option_id} · ${(options(question).find(o=>o.id===question.answer?.correct_option_id)?.math_latex ? math(question.answer?.correct_option_text) : escape(question.answer?.correct_option_text))}</div><p lang="en" dir="ltr">${escape(question.answer?.explanation)}</p>`
      : (question.parts || []).map(part=>`<div class="study-answer-part"><b>${escape(part.id)}</b><p lang="en" dir="ltr">${escape(part.prompt)}</p><div class="study-math">${math(part.answer?.math_latex)}</div><p lang="en" dir="ltr">${escape(part.answer?.model_answer_and_marking)}</p></div>`).join('');
    const steps = question => `<ol class="study-steps"><li>${pair('حدّد المطلوب والمعطيات في السؤال والرسم قبل اختيار العملية.','Identify the requested quantity and the given values in the prompt and diagram.')}</li><li>${pair(outcome.rule_ar,outcome.rule_summary)}</li><li>${pair('طبّق القاعدة على معطيات هذا السؤال، ثم قارن ناتجك بالحل المرجعي أدناه.','Apply the rule to this question’s values, then compare your result with the reference solution below.')}${answer(question)}</li><li>${pair('تحقّق من الإشارات والمجال والوحدات. عوّض للتحقق إذا كانت المسألة معادلة.','Check signs, domain restrictions and units. Substitute back when the task is an equation.')}</li></ol>`;
    root.innerHTML = `<section class="study-booklet">${header()}<div class="study-toolbar"><a href="${href(classroom)}">← فهرس الملزمة · Contents</a><button id="study-print">طباعة الدرس · Print lesson</button></div><button type="button" id="open-floating-calculator" class="calculator-launch" aria-expanded="false" aria-controls="floating-calculator">Open calculator</button><section id="floating-calculator" class="floating-calculator" aria-label="Movable calculator" hidden><div class="floating-calculator-bar"><strong>Calculator · drag to move</strong><div><button type="button" id="calculator-dock-left" aria-label="Move calculator to left">◀</button><button type="button" id="calculator-dock-right" aria-label="Move calculator to right">▶</button><button type="button" id="calculator-close" aria-label="Close calculator">×</button></div></div><p>fx‑991CE X emulator: menus may differ from fx‑991EX or fx‑991ES PLUS. Verify answers on your calculator.</p><iframe class="study-calculator-frame" title="Interactive ClassWiz calculator" loading="lazy"></iframe><a href="https://github.com/magicnothief/fx991ex-emulator" target="_blank" rel="noopener noreferrer">Emulator source</a></section><details class="study-panel calculator-examples"><summary>Illustrated calculator walkthroughs</summary><p>These are worked examples, not the current question. Each frame shows the screen after the highlighted key. The fx‑991CE X emulator may differ from your calculator.</p><div id="calculator-examples" role="region" aria-label="أمثلة الحاسبة المصوّرة"><p>جارٍ تحميل الأمثلة…</p></div></details><div class="study-lesson-title"><span>${outcome.id} / ${outcome.exam_slot}</span><h2 lang="en">${escape(outcome.title)}</h2><p lang="ar" dir="rtl">${escape(outcome.title_ar)}</p></div><div class="study-rule"><span>01 / الفكرة الأساسية · THE IDEA</span>${pair(outcome.rule_ar,outcome.rule_summary)}<h3 lang="en">Calculator strategy for this outcome</h3><p lang="en" dir="ltr">${escape(outcome.calculatorStrategy)}</p></div><div class="study-columns"><article class="study-panel"><span class="study-label">02 / مثال محلول · WORKED EXAMPLE</span>${prompt(example)}${example.type==='mcq'?`<div class="study-example-options">${options(example).map(o=>`<div dir="ltr">${escape(o.id)} · ${o.math_latex?math(o.math_latex):escape(o.text)}</div>`).join('')}</div>`:''}<details id="study-example"><summary>اشرح حل المثال خطوة بخطوة · Explain this example</summary>${steps(example)}${guide(example)}</details></article><aside class="study-panel study-coach"><span class="study-label">03 / مساعد المذاكرة · STUDY COACH</span><h3 lang="ar">جرّب سؤالًا مشابهًا</h3><p lang="en">Work through a different question from this outcome.</p><label>اختر التدريب · Choose practice<select id="study-practice-select">${questions.slice(1).map((q,i)=>`<option value="${i+1}">${q.display_number} · p. ${q.source?.printed_page} · ${q.source?.exercise}</option>`).join('')}</select></label><div id="study-practice"></div><div class="study-slide-actions"><button type="button" id="practice-prev">السابق · Previous</button><button type="button" id="practice-next">التالي · Next</button></div></aside></div><section class="study-panel study-quiz" id="study-quiz"><span class="study-label">04 / اختبر فهمك · CHECK YOUR LEARNING</span><h3>اختبار المخرج</h3><p>أجب عن أسئلة الاختيار، ثم اعرض النتيجة. الأسئلة الكتابية تراجع ذاتيًا في التدريب.</p><div id="study-quiz-content"></div></section><div class="study-finish"><label><input type="checkbox" id="study-done" ${progress[outcome.id]?'checked':''}> راجعت هذا الدرس · I reviewed this lesson</label><span id="study-save" role="status"></span><a href="${href(classroom,bank.learning_outcomes[bank.learning_outcomes.indexOf(outcome)+1]?.id)}">الدرس التالي / الفهرس ← Next</a></div></section>`;
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
    if(examples.length)renderCalculatorExamples(examplesRoot,assetBase,examples);else examplesRoot.closest('details').hidden=true;
    setupFloatingCalculator(root, assetBase);
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
    function drawPractice() {
      root.querySelector('#practice-prev').disabled=practiceIndex<=1;
      root.querySelector('#practice-next').disabled=practiceIndex>=questions.length-1;
      const question = questions[practiceIndex], area = root.querySelector('#study-practice');
      const hintText = hint === 1 ? pair(outcome.rule_ar,outcome.rule_summary) :
        hint > 1 ? pair('ارجع إلى المثال المحلول وطبّق القاعدة نفسها على الأعداد والرسم الجديدين. راجع الإشارات والمقادير المتناظرة قبل الحساب.','Return to the worked example and apply the same rule to the new values and diagram. Check signs and corresponding quantities before calculating.') : '';
      area.innerHTML = `${prompt(question)}<p class="study-step-count">التدريب ${practiceIndex} من ${questions.length-1} · Practice ${practiceIndex} of ${questions.length-1}</p>
      ${phase===0?`<h4>ما المعطيات وما المطلوب؟ · What is given and required?</h4><label>ملاحظاتك · Your notes<textarea id="study-notes" rows="3" placeholder="المعطيات / Given → المطلوب / Required">${escape(drafts[question.id]?.notes || '')}</textarea></label><button id="study-next">حدّدت المعطيات، تابع · Continue</button>`:phase===1?`<h4>اختر القاعدة المناسبة · Choose the matching rule</h4><div class="study-rule-options">${[outcome,...bank.learning_outcomes.filter(lo=>lo.id!==outcome.id).slice(0,2)].sort((a,b)=>a.id.localeCompare(b.id)).map(lo=>`<button data-study-rule="${lo.id}">${pair(lo.rule_ar,lo.rule_summary)}</button>`).join('')}</div><p id="study-rule-feedback" role="status"></p>`:
      `<h4>طبّق القاعدة وأوجد الناتج · Apply the rule and solve</h4>${pair(outcome.rule_ar,outcome.rule_summary)}${question.type==='mcq'?`<fieldset><legend>اختر الناتج · Choose your result</legend>${options(question).map(o=>`<label class="study-choice"><input type="radio" name="study-choice" value="${escape(o.id)}" ${chosen===o.id?'checked':''}><span dir="ltr">${escape(o.id)} · ${o.math_latex?math(o.math_latex):escape(o.text)}</span></label>`).join('')}</fieldset><button id="study-check">تحقّق من إجابتي · Check my answer</button><div id="study-feedback" role="status"></div>`:`<p>اكتب إجابتك رياضيًا، واستخدم أدوات الكسر والقوة والجذر للمساعدة. · Write your answer and use the math tools when needed.</p>${(question.parts||[]).map((part,i)=>`<div class="study-writing math-answer-editor"><label id="math-label-${i}">${escape(part.id)} · ${escape(part.prompt)}</label><math-field data-writing="${i}" aria-labelledby="math-label-${i}" dir="ltr" math-virtual-keyboard-policy="manual"></math-field><details class="math-tools"><summary>أدوات الكتابة الرياضية · Math tools</summary><div class="math-toolbar" role="group" aria-label="Math templates"><button type="button" data-math-template="fraction" aria-label="Insert fraction">${math('\\frac{\\square}{\\square}')}<span>Fraction · كسر</span></button><button type="button" data-math-template="power" aria-label="Insert power">${math('x^{\\square}')}<span>Power · قوة</span></button><button type="button" data-math-template="root" aria-label="Insert square root">${math('\\sqrt{\\square}')}<span>Root · جذر</span></button><button type="button" data-math-template="nthroot" aria-label="Insert nth root">${math('\\sqrt[n]{x}')}<span>ⁿ√x</span></button><button type="button" data-math-template="subscript" aria-label="Insert subscript">${math('x_{n}')}<span>Subscript</span></button><button type="button" data-math-template="brackets" aria-label="Insert parentheses">( )<span>Brackets</span></button><button type="button" data-math-template="pi" aria-label="Insert pi">π</button><button type="button" data-math-template="infinity" aria-label="Insert infinity">∞</button><button type="button" data-math-template="le" aria-label="Insert less than or equal">≤</button><button type="button" data-math-template="ge" aria-label="Insert greater than or equal">≥</button><button type="button" data-math-keyboard>⌨ Math keyboard · لوحة الرياضيات</button></div><p>استخدم Tab للانتقال بين خانات الكسر أو القوة. · Use Tab to move between boxes.</p></details></div>`).join('')}<details><summary>راجع خطواتي مع الحل المرجعي · Compare with the worked solution</summary>${steps(question)}</details><p class="study-subtle">هذا التدريب المقالي للمقارنة الذاتية · Written working uses self-assessment.</p>`}`}
      ${guide(question)}<div class="study-hint-actions"><button id="study-hint">أحتاج تلميحًا · Hint</button><button id="study-help-example">اشرح المثال أولًا · Explain the example</button></div><div class="study-hint" role="status">${hintText}</div>`;
      area.querySelector('#study-notes')?.addEventListener('input', e=>{(drafts[question.id] ||= {}).notes=e.target.value;});
      initMathAnswerEditors(area, drafts, question.id);
      area.querySelector('#study-next')?.addEventListener('click',()=>{phase=1;drawPractice();});
      area.querySelectorAll('[data-study-rule]').forEach(button=>button.onclick=()=>{
        if(button.dataset.studyRule===outcome.id){phase=2;drawPractice();}
        else area.querySelector('#study-rule-feedback').innerHTML=pair('هذه القاعدة تخص فكرة أخرى. اقرأ المطلوب وقارن الرموز ثم جرّب مجددًا.','That rule belongs to a different concept. Re-read the required quantity and compare the symbols, then try again.');
      });
      const feedback = () => {
        const target = area.querySelector('#study-feedback');
        if(!target || !checked) return;
        if(!chosen){target.innerHTML=pair('اختر إجابة أولًا.','Choose an answer first.');return;}
        const correct=chosen===question.answer.correct_option_id;
        target.innerHTML=correct?pair('صحيح. راجع سبب الحل لتثبيت الفكرة.','Correct. Review why the solution works.')+steps(question):
          pair('حاول مرة أخرى. راجع القاعدة والإشارات وترتيب العمليات. يمكنك طلب تلميح أو مشاهدة المثال.','Try again. Check the rule, signs and operation order. Ask for a hint or revisit the example.');
        target.className=correct?'study-correct':'study-retry';
      };
      area.querySelectorAll('[name="study-choice"]').forEach(input=>input.onchange=()=>{chosen=input.value;(drafts[question.id] ||= {}).choice=chosen;checked=false;});
      area.querySelector('#study-check')?.addEventListener('click',()=>{checked=true;feedback();});
      area.querySelector('#study-hint').onclick=()=>{hint=Math.min(hint+1,2);const values=[pair(outcome.rule_ar,outcome.rule_summary),pair('طبّق القاعدة على معطيات السؤال الحالي، مع مراجعة الإشارات والوحدات. قارن العملية بمثال الدرس.','Apply the rule to the current values, checking signs and units. Compare the operation with the lesson example.')];area.querySelector('.study-hint').innerHTML=values[hint-1];};
      area.querySelector('#study-help-example').onclick=()=>{const details=root.querySelector('#study-example');details.open=true;details.scrollIntoView({block:'center'});};
      feedback();
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
        quizArea.innerHTML = `<div class="study-slide-nav" aria-label="أسئلة الاختبار · Quiz questions">${quizQuestions.map((item,i)=>`<button type="button" data-quiz-index="${i}" aria-label="السؤال ${i+1}${selected[i]?'، تمت الإجابة':''}" ${i===quizIndex?'aria-current="step"':''} class="${selected[i]?'is-answered':''}">${i+1}</button>`).join('')}</div><fieldset class="study-quiz-question"><legend>السؤال ${quizIndex+1} من ${quizQuestions.length}</legend>${prompt(q)}${options(q).map(o=>`<label class="study-choice"><input type="radio" name="quiz-choice" value="${escape(o.id)}" ${selected[quizIndex]===o.id?'checked':''}><span dir="ltr">${escape(o.id)} · ${o.math_latex?math(o.math_latex):escape(o.text)}</span></label>`).join('')}</fieldset><div class="study-slide-actions"><button type="button" id="quiz-prev" ${quizIndex===0?'disabled':''}>السابق · Previous</button><button type="button" id="quiz-next" ${quizIndex===quizQuestions.length-1?'disabled':''}>التالي · Next</button><button type="button" id="quiz-submit">عرض النتيجة · Show result</button></div><p role="status">${selected.filter(Boolean).length} / ${quizQuestions.length} مجاب</p>${submitted?`<div id="study-quiz-result" role="status"><h4>النتيجة: ${score} / ${quizQuestions.length}</h4><p>غير المجاب: ${selected.filter(v=>!v).length} · يمكنك تغيير الإجابات وإعادة التحقق.</p><p>${selected[quizIndex]===q.answer.correct_option_id?'إجابة صحيحة':'راجع إجابة هذا السؤال'}</p><details><summary>عرض الإجابة والشرح · Review answer</summary>${answer(q)}${guide(q)}</details></div>`:''}`;
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
