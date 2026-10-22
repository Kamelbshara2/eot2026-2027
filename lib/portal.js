import {adminState} from './admin-ui.js';
import {requestApi} from './api-client.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const classes=['10A1','10G3','9G3'];
let counts={'10G3':48,'10A1':15,'9G3':0};
export function updateClassroomCounts(questions){counts=Object.fromEntries(classes.map(c=>[c,questions.filter(q=>(q.classroom||'10G3')===c).length]));window.dispatchEvent(new Event('classroom-counts-changed'))}
export function mountPortal(){
 const main=document.querySelector('main'),examSections=[...main.querySelectorAll(':scope > .heading,:scope > .stats,:scope > .library')];
 const portal=document.createElement('section');portal.id='portal';main.querySelector('header').after(portal);
 document.querySelector('.brand').href='#/classrooms';
 document.querySelector('#bank').textContent='▦ Classrooms · الصفوف';
 document.querySelector('#bank').onclick=()=>location.hash='/classrooms';
 const dialog=document.createElement('dialog');dialog.id='student-dialog';dialog.innerHTML=`<form id="student-form"><div class="section-head"><h2>Student sign-in · دخول الطالب</h2><button type="button" class="close" aria-label="Close sign-in">×</button></div><p>Enter your details to record your visit and start studying.</p><p lang="ar" dir="rtl">أدخل بياناتك لتسجيل زيارتك وبدء المراجعة.</p><label>Name · اسم الطالب<input name="name" autocomplete="name" minlength="2" maxlength="100" required></label><label>School name · اسم المدرسة<input name="school" autocomplete="organization" minlength="2" maxlength="150" required></label><label>Grade · الصف الدراسي<select name="grade" required><option value="9">Grade 9 · الصف التاسع</option><option value="10">Grade 10 · الصف العاشر</option></select></label><p class="hint">Your name, school, grade, classroom and sign-in time will be recorded for your teacher.<br><span lang="ar" dir="rtl">سيُحفظ اسمك ومدرستك وصفك ووقت دخولك ليتمكن المعلم من متابعة الزيارات.</span></p><p id="student-error" role="alert"></p><button class="primary" type="submit">Sign in · تسجيل الدخول</button></form>`;document.body.append(dialog);
 let activeClass=null,student=null,requestId=null,pendingDestination=null;
 try{student=JSON.parse(sessionStorage.getItem('forma-student-session')||'null')}catch{}
 const form=dialog.querySelector('form'),error=dialog.querySelector('#student-error'),submit=form.querySelector('[type=submit]');
 function signedIn(classroom){return student?.classroom===classroom&&typeof student?.id==='string'}
 function openSignIn(classroom,destination){activeClass=classroom;pendingDestination=destination;requestId=crypto.randomUUID();form.reset();form.elements.grade.value=classroom==='9G3'?'9':'10';error.textContent='';submit.disabled=false;dialog.showModal()}
 dialog.querySelector('.close').onclick=()=>{if(!submit.disabled)dialog.close()};dialog.addEventListener('cancel',e=>{if(submit.disabled)e.preventDefault()});
 form.onsubmit=async e=>{e.preventDefault();if(submit.disabled)return;const grade=Number(form.elements.grade.value);if(grade!==(activeClass==='9G3'?9:10)){error.textContent='Grade must match the selected classroom. · يجب أن يطابق الصف الفصل المختار.';return}
  submit.disabled=true;error.textContent='';
  try{const payload={id:requestId,name:form.elements.name.value.trim(),school:form.elements.school.value.trim(),grade,classroom:activeClass};const response=await requestApi('/api/student-logins',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(20000)});const data=await response.json().catch(()=>null);if(!response.ok||!data?.login?.id)throw Error(data?.error||'Sign-in unavailable. Please retry.');student={id:data.login.id,name:payload.name,classroom:activeClass};try{sessionStorage.setItem('forma-student-session',JSON.stringify(student))}catch{}dialog.close();window.dispatchEvent(new Event('student-session-changed'));const destination=pendingDestination;pendingDestination=null;if(destination)location.hash=destination;route();
  }catch(e){error.textContent=(e.name==='TimeoutError'?'Request timed out. Retry to confirm your sign-in.':e.message)+' · لم يتم تأكيد تسجيل الدخول، يرجى المحاولة مجدداً.'}finally{submit.disabled=false}
 };
 function route(){
  const parts=location.hash.replace(/^#\/?/,'').split('/');const classroom=parts[0]==='classrooms'&&classes.includes(parts[1])?parts[1]:null;
  const exam=['10G3','10A1'].includes(classroom)&&parts[2]==='exams'&&parts[3]==='week-8';
  examSections.forEach(s=>s.hidden=true);portal.hidden=false;
  if(!classroom){portal.innerHTML=`<div class="portal-heading"><div class="eyebrow">YOUR LEARNING SPACE · مساحة التعلم</div><h1>Choose your classroom<span>.</span></h1><p lang="ar" dir="rtl">اختر صفك الدراسي لعرض الاختبارات والمراجعات.</p></div><div class="classroom-cards">${classes.map(c=>`<a class="classroom-card" href="#/classrooms/${c}"><span class="classroom-icon">${c==='9G3'?'09':'10'}</span><h2>${c}</h2><p>${c==='9G3'?'Grade 9':'Grade 10'} · ${c==='9G3'?'الصف التاسع':'الصف العاشر'}</p><span>View exams · عرض الاختبارات ↗</span></a>`).join('')}</div>`;return}
  if(exam&&(signedIn(classroom)||adminState.active)){portal.innerHTML=`<div class="portal-session"><a href="#/classrooms/${classroom}">← ${classroom} · Back to exams · العودة للاختبارات</a><span>${esc(student?.name||'Admin')} ${signedIn(classroom)?'<button class="secondary" id="student-logout">Sign out · خروج</button>':''}</span></div>`;examSections.forEach(s=>s.hidden=false)}
  else {portal.innerHTML=`<div class="portal-heading"><a href="#/classrooms">← Classrooms · الصفوف</a><h1>${classroom}<span>.</span></h1><p>Exams & review · الاختبارات والمراجعات</p>${signedIn(classroom)?`<p>Welcome · مرحباً ${esc(student.name)} <button class="secondary" id="student-logout">Sign out · خروج</button></p>`:'<button class="secondary" id="student-login">Student sign-in · دخول الطالب</button>'}</div>${['10G3','10A1'].includes(classroom)?`<a class="exam-card" id="week8-card" href="#/classrooms/${classroom}/exams/week-8"><span class="pill">EOT · ${classroom}</span><h2>8th week exam</h2><p lang="ar" dir="rtl">امتحان الأسبوع الثامن — ${classroom}</p><span>${counts[classroom]} questions · سؤالاً &nbsp; Start review · ابدأ المراجعة ↗</span></a>`:'<div class="empty"><h2>No exams yet · لا توجد اختبارات بعد</h2><p>New exams will appear here. · ستظهر الاختبارات الجديدة هنا.</p></div>'}`;
   portal.querySelector('#student-login')?.addEventListener('click',()=>openSignIn(classroom,null));
   if(exam&&!dialog.open)openSignIn(classroom,`/classrooms/${classroom}/exams/week-8`);
  }
  portal.querySelector('#student-logout')?.addEventListener('click',()=>{student=null;try{sessionStorage.removeItem('forma-student-session')}catch{}window.dispatchEvent(new Event('student-session-changed'));location.hash=`/classrooms/${classroom}`;route()});
 }
 window.addEventListener('hashchange',route);window.addEventListener('classroom-counts-changed',route);window.addEventListener('admin-role-changed',()=>{if(adminState.active)dialog.close();route()});route();
}
