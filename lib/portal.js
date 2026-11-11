import {stopTermMockExam} from './term-mock-ui.js';
import {examBankRoute,examBankEntryMarkup,renderExamBank,clearExamBankSession} from './exam-bank-ui.js';
import {renderStudentHome,draftHasAnswer} from './student-design.js';
import {classroomLabels} from './branding.js';
import {adminState} from './admin-ui.js';
import {studentStore} from './student-session.js';
import {outcomeState} from './outcomes-ui.js';
import {classroomRoute,classroomGroups,outcomePath,classroomPath,examWeeks,weekLabel} from './classroom-navigation.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function updateClassroomCounts(){window.dispatchEvent(new Event('classroom-counts-changed'))}
export function mountPortal({getQuestions,printQuestions}){
 const main=document.querySelector('main'),examSections=[...main.querySelectorAll(':scope > .heading,:scope > .stats,:scope > .library')];
 const portal=document.createElement('section');portal.id='portal';main.querySelector('header').after(portal);
 document.querySelector('.brand').href='#/classrooms';
 document.querySelector('#bank').textContent='▦ Classrooms · الصفوف';
 document.querySelector('#bank').onclick=()=>location.hash='/classrooms';
 const dialog=document.createElement('dialog');dialog.id='student-dialog';dialog.innerHTML=`<form id="student-form"><div class="section-head"><h2>Enter classroom · دخول الصف</h2><button type="button" class="close" aria-label="Close">×</button></div><p>No account or password needed. Enter your name and school.</p><p lang="ar" dir="rtl">لا تحتاج إلى حساب أو كلمة مرور. أدخل اسمك واسم مدرستك فقط.</p><label>Name · اسم الطالب<input name="name" autocomplete="name" minlength="2" maxlength="100" required></label><label>School name · اسم المدرسة<input name="school" autocomplete="organization" minlength="2" maxlength="150" required></label><p class="hint">Practice starts immediately. Visits and saved answers sync with your teacher when the backend is available. Local work stays in this browser tab until you sign out or close it.<br><span lang="ar" dir="rtl">يبدأ التدريب فوراً. تُرسل الزيارة والإجابات المحفوظة للمعلم عند توفر الاتصال بقاعدة البيانات. يبقى العمل المحلي في علامة التبويب هذه حتى الخروج أو إغلاقها.</span></p><p id="student-error" role="alert"></p><button class="primary" type="submit">Enter classroom · دخول الصف</button></form>`;document.body.append(dialog);
 let activeClass=null,student=studentStore.current(),pendingDestination=null;
 const form=dialog.querySelector('form'),error=dialog.querySelector('#student-error');
 function signedIn(classroom){return student?.classroom===classroom&&typeof student?.id==='string'}
 function openSignIn(classroom,destination){activeClass=classroom;pendingDestination=destination;form.reset();error.textContent='';dialog.querySelector('h2').textContent=`دخول ${classroomLabels[classroom].ar}`;dialog.showModal()}
 function cancelEntry(){pendingDestination=null;dialog.close();location.hash='/classrooms'}
 dialog.querySelector('.close').onclick=cancelEntry;dialog.addEventListener('cancel',e=>{e.preventDefault();cancelEntry()});
 form.onsubmit=e=>{e.preventDefault();const name=form.elements.name.value.trim(),school=form.elements.school.value.trim();if(name.length<2||school.length<2){error.textContent='Enter your name and school. · أدخل اسمك واسم مدرستك.';return}
  const result=studentStore.start({id:crypto.randomUUID(),name,school,grade:Number(activeClass.match(/^\d+/)[0]),classroom:activeClass});student=result.student;dialog.close();const destination=pendingDestination;pendingDestination=null;if(destination)location.hash=destination;window.dispatchEvent(new Event('student-session-changed'));route();
 };
 function route(){
  const {classroom,outcomeId,manage,examWeek,validWeek}=classroomRoute(location.hash),termBank=examBankRoute(location.hash);
  if(!termBank?.mock)stopTermMockExam();
  const practicing=Boolean(outcomeId&&signedIn(classroom)&&!adminState.active);
  document.body.classList.toggle('practice-mode',practicing);examSections.forEach(s=>s.hidden=true);portal.hidden=false;
  document.body.classList.toggle('student-home',!classroom);
  if(!classroom){dialog.close();portal.innerHTML=renderStudentHome({questions:getQuestions(),outcomes:outcomeState.outcomes});
   portal.querySelector('#browse-classrooms').onclick=()=>{const heading=portal.querySelector('#student-classrooms-title');heading.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});heading.focus({preventScroll:true})};return}

  // Students only see the term-1 study booklet; weekly exam pages stay available to administrators.
  if(!adminState.active&&!termBank){location.replace(`#/classrooms/${classroom}/banks/term1`);return}
  if(!adminState.active&&!signedIn(classroom)){
   portal.innerHTML=`<div class="portal-heading"><a href="#/classrooms">← Classrooms · الصفوف</a><div class="eyebrow">${termBank?'TERM 1 STUDY BOOKLET':'EOT / WEEK '+examWeek}</div><h1 lang="ar" dir="rtl">أهلاً بك في صفك<span>.</span></h1><p lang="ar" dir="rtl">${classroomLabels[classroom].ar} — سجّل اسمك ومدرستك مرة واحدة لدخول الصف، ثم اختر مخرج التعلم الذي تريد التدرب عليه.</p><button class="primary" id="enter-classroom">Enter classroom · دخول الصف</button></div>`;
   const destination=termBank?location.hash.slice(1):classroomPath(classroom,examWeek).slice(1);
   portal.querySelector('#enter-classroom').onclick=()=>openSignIn(classroom,destination);
   if(dialog.open&&activeClass!==classroom)dialog.close();
   if(!dialog.open)openSignIn(classroom,destination);
   return;
  }
  if(termBank){document.body.classList.remove('practice-mode');void renderExamBank({root:portal,route:termBank,studentKey:student?.id||'admin'});return}
  if(!validWeek){portal.innerHTML=`<p>Unknown exam week · أسبوع غير متاح</p><a href="${classroomPath(classroom)}">Week 10 · الأسبوع العاشر</a>`;return}
  const tabs=`<nav class="week-tabs" aria-label="Exam week · أسبوع الاختبار">${examWeeks.map(w=>`<a href="${classroomPath(classroom,w)}" ${examWeek===w?'aria-current="page"':''}>Week ${w} · ${weekLabel(w)}</a>`).join('')}</nav>`;
  const groups=classroomGroups(classroom,getQuestions(),outcomeState.outcomes,outcomeState.assignments,examWeek);
  const selected=groups.find(g=>g.id===outcomeId),showBank=adminState.active&&(manage||selected);
  document.body.classList.toggle('practice-mode',Boolean(selected&&practicing));
  const sessionBar=`<div class="portal-session"><a href="${classroomPath(classroom,examWeek)}">← ${classroomLabels[classroom].ar} · Learning outcomes · مخرجات التعلم</a><span><b class="student-name">${esc(signedIn(classroom)?student.name:adminState.active?'Admin':'')}</b> ${signedIn(classroom)?'<button class="secondary" id="student-logout">Sign out · خروج</button>':''}</span></div>`;
  if((selected&&practicing)||showBank){portal.innerHTML=sessionBar+`${signedIn(classroom)?`<p role="status" class="student-sync-status">${student.synced?'Visit recorded for your teacher · تم تسجيل الزيارة للمعلم':'Practice available. Visit saved locally; not yet sent to your teacher. · يمكنك التدريب. الزيارة محفوظة محلياً ولم تُرسل للمعلم بعد.'}</p>`:''}`;examSections.forEach(s=>s.hidden=false)}
  else {
   const frqs=groups.flatMap(g=>g.questions).filter(q=>q.type==='FRQ'),drafts=studentStore.drafts();
   portal.innerHTML=`<div class="portal-heading"><a href="#/classrooms">← Classrooms · الصفوف</a><div class="eyebrow">${classroomLabels[classroom].en} / EOT / WEEK ${examWeek}</div><h1 lang="ar" dir="rtl">مخرجات التعلم<span>.</span></h1><p lang="ar" dir="rtl">${classroomLabels[classroom].ar} — امتحان ${weekLabel(examWeek)}</p>${signedIn(classroom)?`<p>Welcome · مرحباً ${esc(student.name)} <button class="secondary" id="student-logout">Sign out · خروج</button></p>`:''}</div>${examBankEntryMarkup(classroom)}${tabs}<div class="outcome-toolbar"><p lang="ar" dir="rtl">اختر مخرج تعلم للتدريب. الطباعة تجمع الأسئلة المقالية FRQ لجميع المخرجات فقط؛ أسئلة الاختيار من متعدد للتدريب داخل المنصة.</p><button class="primary" id="print-classroom" ${frqs.length?'':'disabled'}>Print FRQ review (${frqs.length}) · طباعة مراجعة الأسئلة المقالية</button>${adminState.active?`<a class="secondary" href="${classroomPath(classroom,examWeek)}/manage">Manage questions · إدارة الأسئلة</a>`:''}<p class="print-feedback" role="status"></p></div>${outcomeId&&!selected?'<p role="alert">This outcome is unavailable in this classroom. · مخرج التعلم غير متاح في هذا الصف.</p>':''}<div class="outcome-cards">${groups.map((g,i)=>{const written=g.questions.filter(q=>q.type==='FRQ').length,completed=g.questions.filter(q=>draftHasAnswer(drafts[q.id])).length;return `<article class="outcome-card"><div class="outcome-card-top"><span class="outcome-index">${String(i+1).padStart(2,'0')}</span><span class="eyebrow">${classroomLabels[classroom].en} / WEEK ${examWeek}</span></div><h2 lang="ar" dir="rtl">${esc(g.titleAr||g.title)}</h2><p>${esc(g.title)}</p>${g.assessmentItem?`<span class="assessment-item">EOT ${esc(g.assessmentItem)}</span>`:''}${g.bookPages?`<small>Book pages · صفحات الكتاب: ${esc(g.bookPages)}</small>`:''}<div class="outcome-counts"><span>${g.questions.length} questions · سؤال</span><span class="count-frq">${written} FRQ · كتابي</span><span class="count-mcq">${g.questions.length-written} MCQ · اختياري</span></div><div class="outcome-progress"><span lang="ar" dir="rtl">${completed?`أجبت عن ${completed} من ${g.questions.length} أسئلة`:'ابدأ أول سؤال، وخذ خطوتك الأولى'}</span><progress aria-label="Answered questions · الأسئلة المجابة" value="${completed}" max="${Math.max(1,g.questions.length)}"></progress></div><div class="outcome-card-actions">${g.questions.length?`<a class="primary" href="${outcomePath(classroom,g.id,examWeek)}">Practice this outcome · تدرّب على هذا المخرج</a>`:'<p class="awaiting-questions" lang="ar" dir="rtl">الأسئلة ستضاف قريباً · Questions coming soon</p>'}</div></article>`}).join('')}</div>${groups.length?'':'<p class="empty">Your teacher is preparing learning outcomes. · يجهّز معلمك مخرجات التعلم.</p>'}`;
   const print=async(button,questions)=>{button.disabled=true;const feedback=portal.querySelector('.print-feedback');try{await printQuestions(questions)}catch(error){if(feedback)feedback.textContent=error.message}finally{button.disabled=false}};
   portal.querySelector('#print-classroom')?.addEventListener('click',e=>print(e.currentTarget,groups.flatMap(g=>g.questions)));
  }
  portal.querySelector('#student-logout')?.addEventListener('click',()=>{clearExamBankSession(student?.id);studentStore.end();student=null;location.hash='/classrooms';window.dispatchEvent(new Event('student-session-changed'));dialog.close();route()});
 }
 window.addEventListener('student-sync-changed',()=>{student=studentStore.current();const notice=portal.querySelector('.student-sync-status');if(notice&&student?.synced)notice.textContent='Visit recorded for your teacher · تم تسجيل الزيارة للمعلم'});window.addEventListener('hashchange',route);window.addEventListener('classroom-counts-changed',route);window.addEventListener('admin-role-changed',()=>{if(adminState.active)dialog.close();route()});route();
}
