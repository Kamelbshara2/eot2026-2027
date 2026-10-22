import {requestApi} from './api-client.js';

// Student check-ins are self-reported visits, never administrator credentials.
export function createStudentStore({storage,request=requestApi,notify=()=>{}}){
 let student=null,drafts={},pending={},busy=false,retained=true;
 try{student=JSON.parse(storage.getItem('forma-student-session')||'null');if(student){const saved=JSON.parse(storage.getItem(`forma-practice-${student.id}`)||'{}');drafts=saved.drafts||{};pending=saved.pending||{}}}catch{}
 function persist(){try{if(student){storage.setItem('forma-student-session',JSON.stringify(student));storage.setItem(`forma-practice-${student.id}`,JSON.stringify({drafts,pending}))}retained=true;return true}catch{retained=false;return false}}
 async function sync(){
  if(busy||!student||!student.school)return;
  busy=true;const visit=student;
  try{
   if(!visit.synced){const r=await request('/api/student-logins',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:visit.id,name:visit.name,school:visit.school,grade:visit.grade,classroom:visit.classroom}),signal:AbortSignal.timeout(10000)});const data=await r.json();if(!r.ok||data.login?.id!==visit.id)throw Error('Visit not recorded');visit.synced=true;if(student!==visit)return;persist();notify()}
   for(const [questionId,draft] of Object.entries(pending)){
    if(student!==visit)return;
    const r=await request('/api/practice',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${visit.id}`},body:JSON.stringify({questionId,fields:draft.fields,paths:draft.paths,selected:draft.selected,...(draft.paper?.data?{paper:draft.paper}:{keepPaper:Boolean(draft.paper)})}),signal:AbortSignal.timeout(15000)});const data=await r.json();if(!r.ok||!data.saved)throw Error('Answer not recorded');if(student!==visit)return;
    if(pending[questionId]===draft){delete pending[questionId];if(drafts[questionId]===draft&&'paper'in data)draft.paper=data.paper;persist();notify()}
   }
  }catch{/* Local practice stays available; retry on the next save or reconnect. */}finally{busy=false}
 }
 return {
  current:()=>student,
  retained:()=>retained,
  start(payload){student={...payload,synced:false};drafts={};pending={};const retained=persist();notify();void sync();return {student,retained}},
  end(){if(student)try{storage.removeItem(`forma-practice-${student.id}`);storage.removeItem('forma-student-session')}catch{}student=null;drafts={};pending={};notify()},
  drafts:()=>drafts,
  remember(questionId,draft){drafts[questionId]=draft;return persist()},
  save(questionId,draft){drafts[questionId]=draft;pending[questionId]=draft;const retained=persist();notify();void sync();return retained},
  pending:questionId=>Boolean(pending[questionId]),sync
 };
}
let storage;try{storage=globalThis.sessionStorage}catch{}
export const studentStore=createStudentStore({storage,notify:()=>{if(typeof window!=='undefined')window.dispatchEvent(new Event('student-sync-changed'))}});
if(typeof window!=='undefined'){
 window.addEventListener('online',()=>void studentStore.sync());
 window.addEventListener('focus',()=>void studentStore.sync());
 setInterval(()=>{if(!document.hidden)void studentStore.sync()},30000);
 void studentStore.sync();
}
