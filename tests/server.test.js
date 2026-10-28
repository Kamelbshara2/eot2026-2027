import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createApp} from '../server.mjs';
test('Railway production server serves the exam and API on one origin',async t=>{
 const server=createApp({students:async(req,res)=>res.status(201).json({studentRoute:true}),api:async(req,res)=>{if(req.method==='POST'){try{return res.json({received:JSON.parse(req.body)})}catch{return res.status(400).json({error:'Invalid JSON'})}}res.json({rows:[]})}});
 server.listen(0,'127.0.0.1');await once(server,'listening');t.after(()=>new Promise(resolve=>{server.close(resolve);server.closeAllConnections()}));const url=`http://127.0.0.1:${server.address().port}`;
 let r=await fetch(url+'/');assert.equal(r.status,200);assert(r.headers.get('content-type').includes('text/html'));const html=await r.text();assert(html.includes('منصة الرياضيات 100 مع الاستاذ كامل'));assert(html.includes('<div id="app"></div>'));
 r=await fetch(url+'/healthz');assert.deepEqual(await r.json(),{status:'ok'});
 r=await fetch(url+'/api/questions');assert.deepEqual(await r.json(),{rows:[]});
 r=await fetch(url+'/api/questions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:'offline-test'})});assert.deepEqual(await r.json(),{received:{id:'offline-test'}});
 r=await fetch(url+'/api/questions',{method:'POST',body:'invalid'});assert.equal(r.status,400);
 r=await fetch(url+'/api/student-logins',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});assert.equal(r.status,201);assert((await r.json()).studentRoute);
 r=await fetch(url+'/data/questions.json');assert.equal((await r.json()).questions.length,135);
 for(const path of ['/.env','/server.mjs','/package.json','/%2e%2e%2fpackage.json']){r=await fetch(url+path);assert.equal(r.status,404)}
 r=await fetch(url+'/',{method:'POST'});assert.equal(r.status,405);
 r=await fetch(url+'/',{method:'HEAD'});assert.equal(r.status,200);assert.equal(await r.text(),'');
});
