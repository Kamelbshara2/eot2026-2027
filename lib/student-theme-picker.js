import {classroomLabels} from './branding.js';
import {classroomPath,classroomRoute} from './classroom-navigation.js';
export const THEME_STORAGE_KEY='math100-student-theme-v1';
export const STUDENT_THEMES=[{id:'current',name:'الحالي',color:'#153c35'},{id:'studio',name:'استوديو',color:'#2444e8'},{id:'masar',name:'مسار',color:'#063c2a'}];
export const normalizeStudentTheme=value=>STUDENT_THEMES.some(t=>t.id===value)?value:'current';
export function readStudentTheme(storage){try{return normalizeStudentTheme(storage?.getItem(THEME_STORAGE_KEY))}catch{return 'current'}}
export function saveStudentTheme(storage,value){const theme=normalizeStudentTheme(value);try{storage?.setItem(THEME_STORAGE_KEY,theme)}catch{}return theme}
export function themePickerMarkup(){return `<fieldset class="student-theme-picker" dir="rtl"><legend>اختر ثيمك · Theme</legend><div class="theme-choices">${STUDENT_THEMES.map(t=>`<label class="theme-choice" title="${t.name}"><input type="radio" name="student-theme" value="${t.id}" aria-label="ثيم ${t.name}"><span class="theme-swatch theme-swatch-${t.id}" aria-hidden="true"></span><span>${t.name}</span></label>`).join('')}</div><span class="theme-feedback" role="status" aria-live="polite"></span></fieldset>`}
export function mountStudentThemePicker({doc=document,win=window,storage}={}){
 let local=storage;if(local===undefined)try{local=win.localStorage}catch{local=null}
 const holder=doc.createElement('div');holder.innerHTML=themePickerMarkup();const picker=holder.firstElementChild;doc.querySelector('.platform-masthead').after(picker);
 const rail=doc.createElement('nav');rail.className='masar-theme-rail';rail.setAttribute('aria-label','التنقل بين الصفوف');rail.setAttribute('dir','rtl');rail.innerHTML=`<a class="masar-rail-brand" href="#/classrooms"><b>100</b><span>رياضيات<br><small>تعلّم على مسارك.</small></span></a><span class="masar-rail-label">مساحة التعلّم</span><a href="#/classrooms" class="masar-rail-home">الصفوف الدراسية</a>${['9G3','10G3','10A1'].map(id=>[id,classroomLabels[id].ar]).map(([id,title])=>`<a data-rail-classroom="${id}" href="${classroomPath(id)}"><b dir="ltr">${id}</b><span>${title}</span></a>`).join('')}<div class="masar-rail-note">كل فكرة تفهمها،<br>خطوة جديدة في مسارك.</div>`;doc.querySelector('#app').prepend(rail);
 const syncRail=()=>{const route=classroomRoute(win.location.hash);for(const a of rail.querySelectorAll('[data-rail-classroom]')){a.href=classroomPath(a.dataset.railClassroom,route.validWeek?route.examWeek:10);if(route.classroom===a.dataset.railClassroom)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')}rail.querySelector('.masar-rail-home').toggleAttribute('data-current',!route.classroom)};
 const apply=(value,announce=false)=>{const theme=normalizeStudentTheme(value);doc.body.dataset.studentTheme=theme;doc.documentElement.dataset.studentTheme=theme;for(const t of STUDENT_THEMES)doc.body.classList.toggle('theme-'+t.id,t.id===theme);for(const input of picker.querySelectorAll('input'))input.checked=input.value===theme;const meta=doc.querySelector('meta[name=theme-color]');if(meta)meta.content=STUDENT_THEMES.find(t=>t.id===theme).color;if(announce)picker.querySelector('.theme-feedback').textContent='تم اختيار ثيم '+STUDENT_THEMES.find(t=>t.id===theme).name;return theme};
 apply(readStudentTheme(local));syncRail();
 picker.addEventListener('change',e=>{if(e.target.matches('input[name=student-theme]'))apply(saveStudentTheme(local,e.target.value),true)});
 win.addEventListener('storage',e=>{if(e.key===THEME_STORAGE_KEY||e.key===null)apply(e.key===null?'current':e.newValue)});win.addEventListener('hashchange',syncRail);
 return {picker,apply:theme=>apply(saveStudentTheme(local,theme),true)};
}
