import test from 'node:test';
import assert from 'node:assert/strict';
import {createStudentStore} from './lib/student-session.js';
const visitor={id:'c0e21651-85c7-4aae-8ca1-5ff2eadfd012',name:'Student',school:'School',grade:10,classroom:'10A1'};
function memory(){const values=new Map();return {getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)}}
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
test('student enters immediately without an account while backend is unavailable; work survives refresh',async()=>{
 const storage=memory(),request=async()=>{throw Error('No backend')};
 const store=createStudentStore({storage,request});
 assert.equal(store.start(visitor).student.name,'Student');
 const answer={fields:[{label:'Working',value:'x = 5'}],paths:[],selected:null,paper:{name:'answer.pdf',type:'application/pdf',data:'data:application/pdf;base64,JVBERg=='}};
 assert.equal(store.save('q1',answer),true);
 await tick();
 assert.equal(store.current().synced,false);
 const restored=createStudentStore({storage,request});
 assert.equal(restored.current().school,'School');
 assert.deepEqual(restored.drafts().q1,answer);
 assert.equal(restored.pending('q1'),true);
});
test('reconnect registers visit before answers, retries the same UUID, and clears only confirmed saves',async()=>{
 const storage=memory(),calls=[];let online=false;
 const store=createStudentStore({storage,request:async(path,options)=>{calls.push({path,body:JSON.parse(options.body)});if(!online)throw Error('Offline');return {ok:true,json:async()=>path==='/api/student-logins'?{login:{id:visitor.id}}:{saved:true}}}});
 store.start(visitor);store.save('q1',{fields:[],paths:[],selected:2});await tick();online=true;await store.sync();
 assert.equal(store.current().synced,true);assert.equal(store.pending('q1'),false);
 assert.deepEqual(calls.map(c=>c.path),['/api/student-logins','/api/student-logins','/api/practice']);
 assert.equal(calls[0].body.id,calls[1].body.id);
 assert.equal(calls[2].body.selected,2);
});
test('failed server saves remain queued and a newer answer is not cleared by an older in-flight save',async()=>{
 let resolveSave;const request=async path=>path==='/api/student-logins'?{ok:true,json:async()=>({login:{id:visitor.id}})}:new Promise(resolve=>resolveSave=resolve);
 const store=createStudentStore({storage:memory(),request});store.start(visitor);await tick();
 store.save('q1',{selected:1});await tick();store.save('q1',{selected:3});
 resolveSave({ok:true,json:async()=>({saved:true})});await tick();
 assert.equal(store.pending('q1'),true);assert.equal(store.drafts().q1.selected,3);
});
test('quota failures do not block practice and signing out clears tab records',async()=>{
 const store=createStudentStore({storage:{getItem:()=>null,setItem:()=>{throw Error('Quota exceeded')},removeItem:()=>{}},request:async()=>{throw Error('Offline')}});
 assert.equal(store.start(visitor).retained,false);assert.equal(store.save('q1',{selected:0}),false);assert.equal(store.drafts().q1.selected,0);store.end();assert.equal(store.current(),null);
 const storage=memory(),other=createStudentStore({storage,request:async()=>{throw Error('Offline')}});other.start(visitor);other.save('q1',{selected:0});other.end();assert.equal(storage.getItem('forma-student-session'),null);assert.equal(storage.getItem(`forma-practice-${visitor.id}`),null);
});
