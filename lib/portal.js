import {adminState} from './admin-ui.js';
import {studentStore} from './student-session.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const classes=['10A1','10G3','9G3'];
let counts={'10G3':38,'10A1':35,'9G3':0};
export function updateClassroomCounts(questions){counts=Object.fromEntries(classes.map(c=>[c,questions.filter(q=>(q.classroom||'10G3')===c).length]));window.dispatchEvent(new Event('classroom-counts-changed'))}
export function mountPortal(){
 const main=document.querySelector('main'),examSections=[...main.querySelectorAll(':scope > .heading,:scope > .stats,:scope > .library')];
 const portal=document.createElement('section');portal.id='portal';main.querySelector('header').after(portal);
 document.querySelector('.brand').href='#/classrooms';
 document.querySelector('#bank').textContent='▦ Classrooms · الصفوف';
 document.querySelector('#bank').onclick=()=>location.hash='/classrooms';
 const dialog=document.createElement('dialog');dialog.id='student-dialog';dialog.innerHTML=`<form id="student-form"><div class="section-head"><h2>Start practice · ابدأ التدريب</h2><button type="button" class="close" aria-label="Close">×</button></div><p>No account or password needed. Enter your name and school.</p><p lang="ar" dir="rtl">لا تحتاج إلى حساب أو كلمة مرور. أدخل اسمك واسم مدرستك فقط.</p><label>Name · اسم الطالب<input name="name" autocomplete="name" minlength="2" maxlength="100" required></label><label>School name · اسم المدرسة<input name="school" autocomplete="organization" minlength="2" maxlength="150" required></label><p class="hint">Practice starts immediately. Visits and saved answers sync with your teacher when the backend is available. Local work stays in this browser tab until you sign out or close it.<br><span lang="ar" dir="rtl">يبدأ التدريب فوراً. تُرسل الزيارة والإجابات المحفوظة للمعلم عند توفر الاتصال بقاعدة البيانات. يبقى العمل المحلي في علامة التبويب هذه حتى الخروج أو إغلاقها.</span></p><p id="student-error" role="alert"></p><button class="primary" type="submit">Start practice · ابدأ التدريب</button></form>`;document.body.append(dialog);
 let activeClass=null,student=studentStore.current(),pendingDestination=null;
 const form=dialog.querySelector('form'),error=dialog.querySelector('#student-error');
 function signedIn(classroom){return student?.classroom===classroom&&typeof student?.id==='string'}
 function openSignIn(classroom,destination){activeClass=classroom;pendingDestination=destination;form.reset();error.textContent='';dialog.showModal()}
 dialog.querySelector('.close').onclick=()=>dialog.close();
 form.onsubmit=e=>{e.preventDefault();const name=form.elements.name.value.trim(),school=form.elements.school.value.trim();if(name.length<2||school.length<2){error.textContent='Enter your name and school. · أدخل اسمك واسم مدرستك.';return}
  const result=studentStore.start({id:crypto.randomUUID(),name,school,grade:activeClass==='9G3'?9:10,classroom:activeClass});student=result.student;dialog.close();window.dispatchEvent(new Event('student-session-changed'));const destination=pendingDestination;pendingDestination=null;if(destination)location.hash=destination;route();
 };
 function route(){
  const parts=location.hash.replace(/^#\/?/,'').split('/');const classroom=parts[0]==='classrooms'&&classes.includes(parts[1])?parts[1]:null;
  const exam=['10G3','10A1'].includes(classroom)&&parts[2]==='exams'&&parts[3]==='week-8';
  document.body.classList.toggle('practice-mode',exam&&signedIn(classroom)&&!adminState.active);examSections.forEach(s=>s.hidden=true);portal.hidden=false;
  if(!classroom){portal.innerHTML=`<div class="portal-heading"><div class="eyebrow">YOUR LEARNING SPACE · مساحة التعلم</div><h1>Choose your classroom<span>.</span></h1><p lang="ar" dir="rtl">اختر صفك الدراسي لعرض الاختبارات والمراجعات.</p></div><div class="classroom-cards">${classes.map(c=>`<a class="classroom-card" href="#/classrooms/${c}"><span class="classroom-icon">${c==='9G3'?'09':'10'}</span><h2>${c}</h2><p>${c==='9G3'?'Grade 9':'Grade 10'} · ${c==='9G3'?'الصف التاسع':'الصف العاشر'}</p><span>View exams · عرض الاختبارات ↗</span></a>`).join('')}</div>`;return}
  if(exam&&(signedIn(classroom)||adminState.active)){portal.innerHTML=`<div class="portal-session"><a href="#/classrooms/${classroom}">← ${classroom} · Back to exams · العودة للاختبارات</a><span><b class="student-name">${esc(student?.name||'Admin')}</b> ${signedIn(classroom)?'<button class="secondary" id="student-logout">Sign out · خروج</button>':''}</span></div>${signedIn(classroom)?`<p role="status" class="student-sync-status">${student.synced?'Visit recorded for your teacher · تم تسجيل الزيارة للمعلم':'Practice available. Visit saved locally; not yet sent to your teacher. · يمكنك التدريب. الزيارة محفوظة محلياً ولم تُرسل للمعلم بعد.'}</p>`:''}`;examSections.forEach(s=>s.hidden=false)}
  else {portal.innerHTML=`<div class="portal-heading"><a href="#/classrooms">← Classrooms · الصفوف</a><h1>${classroom}<span>.</span></h1><p>Exams & review · الاختبارات والمراجعات</p>${signedIn(classroom)?`<p>Welcome · مرحباً ${esc(student.name)} <button class="secondary" id="student-logout">Sign out · خروج</button></p>`:'<button class="secondary" id="student-login">Student sign-in · دخول الطالب</button>'}</div>${['10G3','10A1'].includes(classroom)?`<a class="exam-card" id="week8-card" href="#/classrooms/${classroom}/exams/week-8"><span class="pill">EOT · ${classroom}</span><h2>8th week exam</h2><p lang="ar" dir="rtl">امتحان الأسبوع الثامن — ${classroom}</p><span>${counts[classroom]} questions · سؤالاً &nbsp; Start review · ابدأ المراجعة ↗</span></a>`:'<div class="empty"><h2>No exams yet · لا توجد اختبارات بعد</h2><p>New exams will appear here. · ستظهر الاختبارات الجديدة هنا.</p></div>'}`;
   portal.querySelector('#student-login')?.addEventListener('click',()=>openSignIn(classroom,null));
   if(exam&&!dialog.open)openSignIn(classroom,`/classrooms/${classroom}/exams/week-8`);
  }
  portal.querySelector('#student-logout')?.addEventListener('click',()=>{studentStore.end();student=null;location.hash=`/classrooms/${classroom}`;window.dispatchEvent(new Event('student-session-changed'));dialog.close();route()});
 }
 window.addEventListener('student-sync-changed',()=>{student=studentStore.current();const notice=portal.querySelector('.student-sync-status');if(notice&&student?.synced)notice.textContent='Visit recorded for your teacher · تم تسجيل الزيارة للمعلم'});window.addEventListener('hashchange',route);window.addEventListener('classroom-counts-changed',route);window.addEventListener('admin-role-changed',()=>{if(adminState.active)dialog.close();route()});route();
}
