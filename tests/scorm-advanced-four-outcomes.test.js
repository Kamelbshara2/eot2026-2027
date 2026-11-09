import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {createSession,startAttempt,active,selected,grade,recordedScore,recordedAttempt,hasResponses,timing,finishAttempt,validSession,chooseState,numericAnswer,correctBlank,MAIN_MS,GRACE_MS} from '../scorm/advanced-four-outcomes/core.js';
import {reportResult} from '../scorm/advanced-four-outcomes/report.js';
const student={name:'طالب اختبار',number:'001234'},root=new URL('../',import.meta.url);
const packages=['Main','Reserve'].map(kind=>{const path=new URL(`downloads/10A1-Four-Outcomes-${kind}-15min-2tries-SCORM12.zip`,root);const files=JSON.parse(execFileSync('python',['-c',`import zipfile,json,sys,xml.etree.ElementTree as E,hashlib
with zipfile.ZipFile(sys.argv[1]) as z:
 assert z.testzip() is None
 m=E.fromstring(z.read('imsmanifest.xml'));ns={'i':'http://www.imsproject.org/xsd/imscp_rootv1p1p2','a':'http://www.adlnet.org/xsd/adlcp_rootv1p2'}
 assert m.find('i:metadata/i:schemaversion',ns).text=='1.2'
 assert m.find('.//i:resource',ns).attrib['{'+ns['a']+'}scormtype']=='sco'
 assert all(x.attrib['href'] in z.namelist() for x in m.findall('.//i:file',ns))
 assert m.find('.//a:maxtimeallowed',ns) is None
 files={n:z.read(n).decode() for n in ['assets/data.js','assets/core.js','assets/report.js','assets/exam.js','assets/exam.css','index.html','README.txt']}
 files['imageHashes']={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.png')}
 print(json.dumps(files))`,path.pathname],{encoding:'utf8',maxBuffer:5e6}));const ctx={window:{}};vm.runInNewContext(files['assets/data.js'],ctx);return {kind,files,data:JSON.parse(JSON.stringify(ctx.window.EXAM_DATA))}});
const done=(s,d,score=10)=>{const a=active(s);a.answers=selected(a,d).map((q,i)=>score>=2*(i+1)?q.correctIndex:null);a.blanks=d.frq.blanks.map((b,i)=>score===10?String(b.answer):'');s.attempts[s.attempts.length-1]=finishAttempt(a,d,a.t+10000);s.seq++;return s};
for(const {kind,files,data} of packages){
 test(`${kind}: packaged sources, local original images, fonts and blueprint are complete`,()=>{
  for(const file of ['core.js','report.js','exam.js'])assert.equal(files['assets/'+file],fs.readFileSync(new URL('scorm/advanced-four-outcomes/'+file,root),'utf8'));
  assert.equal(data.pools.length,4);assert.equal(data.frq.blanks.length,5);assert.deepEqual(data.frq.blanks.map(b=>b.marks),[.25,.25,.25,.25,1]);assert.equal(data.mainSeconds,900);assert.equal(data.graceSeconds,120);assert.equal(data.maxAttempts,2);assert.equal(data.totalMarks,10);assert(files['assets/exam.css'].includes('data:font/woff2;base64,'));assert(!/(src|href)="https?:/i.test(files['index.html']+files['assets/data.js']));
  const images=JSON.parse(fs.readFileSync(new URL('public/data/exam-banks/10a1-four-outcomes-assessment/source-images.json',root)));for(const image of Object.values(images))assert.equal(files.imageHashes[image.src],image.sha256);
  for(const q of [...data.pools.flatMap(p=>p.questions),data.frq])assert(files.imageHashes[q.image]);
  assert(!files['assets/data.js'].includes('explanationHTML'));assert(files['README.txt'].includes('ONE outer SCORM attempt'));
 });
 test(`${kind}: every form covers the four confirmed LOs, scores 10, and a second try differs in all four pools`,()=>{
  const expected=new Set(JSON.parse(fs.readFileSync(new URL('public/data/learning-outcomes.json',root))).outcomes.filter(o=>o.classroom==='10A1'&&o.examWeek===10).map(o=>o.id));let allOrders=new Set();const seen=data.pools.map(()=>new Set());
  for(let i=0;i<250;i++){let s=startAttempt(createSession(data,student),data,1000000);assert(validSession(s,data));const a=active(s);assert.equal(grade(a,data),0);assert.deepEqual(new Set([...selected(a,data).map(q=>q.outcomeId),data.frq.outcomeId]),expected);selected(a,data).forEach((q,j)=>{seen[j].add(q.id);assert.deepEqual([...a.options[j]].sort(),[0,1,2,3]);a.answers[j]=q.correctIndex});assert.equal(grade(a,data),8);a.blanks=data.frq.blanks.map(b=>String(b.answer));assert.equal(grade(a,data),10);allOrders.add(a.order.join(','));s=done(s,data);s=startAttempt(s,data,1020000);assert(active(s).ids.every((id,j)=>id!==s.attempts[0].ids[j]));s=done(s,data,6);assert.equal(recordedScore(s,data),10);assert.throws(()=>startAttempt(s,data,1040000));assert(validSession(s,data));assert(new TextEncoder().encode(JSON.stringify(s)).length<4096)}
  assert(allOrders.size>10);for(const [i,p]of data.pools.entries())assert.equal(seen[i].size,p.questions.length);
 });
 test(`${kind}: one immutable deadline, grace exactly at 15:00, auto-submit cutoff exactly 17:00`,()=>{
  const s=startAttempt(createSession(data,student),data,1000000),a=active(s);assert.equal(MAIN_MS,900000);assert.equal(GRACE_MS,120000);assert.deepEqual(timing(a,a.t),{remaining:900,grace:false,expired:false});assert.deepEqual(timing(a,a.mainEnd),{remaining:120,grace:true,expired:false});assert.deepEqual(timing(a,a.deadline-1),{remaining:1,grace:true,expired:false});assert.deepEqual(timing(a,a.deadline),{remaining:0,grace:true,expired:true});const loaded=JSON.parse(JSON.stringify(s));assert.equal(active(loaded).deadline,a.deadline);const f=finishAttempt(a,data,a.deadline+99999,'timeout');assert.equal(f.end,a.deadline);assert.deepEqual(finishAttempt(f,data,a.deadline+999999),f);
 });
 test(`${kind}: maximum two tries, saved-state validation and failed-save recovery do not create a new try`,()=>{
  let s=startAttempt(createSession(data,student),data,1000000);assert.throws(()=>startAttempt(s,data,1000001));const old=structuredClone(s);s.seq++;active(s).blanks[0]='-3';assert.equal(chooseState(old,s,data).seq,s.seq);assert.equal(chooseState(s,old,data).seq,s.seq);for(const a of [{...active(s),deadline:active(s).deadline+1},{...active(s),answers:[4,null,null,null]},{...active(s),order:[0,0,2,3]},{...active(s),blanks:['1/0']},{...active(s),score:10,finished:true,end:1000001,reason:'submitted'}])assert(!validSession({...s,attempts:[a]},data));assert.throws(()=>chooseState({...s,p:'wrong'},s,data));s=done(s,data,8);s=startAttempt(s,data,1020000);s=done(s,data,10);assert.equal(recordedScore(s,data),8);
 });
 test(`${kind}: SCORM reports the first answered score with canonical shuffled grading and retries writes safely`,()=>{
  let s=done(startAttempt(createSession(data,student),data,1000000),data,8);s=done(startAttempt(s,data,1020000),data,6);const values={},calls=[];let failure=true;const lms={set:(k,v)=>{calls.push(k);if(failure&&k==='cmi.core.score.raw')return false;values[k]=String(v);return true},commit:()=>true};assert(!reportResult(lms,s,data,10000).ok);assert(!('cmi.core.lesson_status' in values));failure=false;assert(reportResult(lms,s,data,10000).ok);assert.equal(values['cmi.core.score.raw'],'80');assert.equal(values['cmi.core.score.max'],'100');assert.equal(values['cmi.core.lesson_status'],'completed');assert.equal(JSON.parse(values['cmi.suspend_data']).attempts.length,2);assert.equal(values['cmi.interactions.9.student_response'],'001234');assert.equal(values['cmi.interactions.19.student_response'],'001234');assert.equal(values['cmi.interactions.0.correct_responses.0.pattern'],String.fromCharCode(65+s.attempts[0].options[0].indexOf(selected(s.attempts[0],data)[0].correctIndex)));assert(!reportResult({...lms,commit:()=>false},s,data,10000).ok);
 });
}
test('main and reserve identities are independent and written keys use all original 3D coordinates',()=>{assert.notEqual(packages[0].data.id,packages[1].data.id);assert.deepEqual(packages[0].data.frq.blanks.map(b=>b.answer),[-3,-1,1,36,6]);assert.deepEqual(packages[1].data.frq.blanks.map(b=>b.answer),[0,0,0,12,Math.sqrt(12)]);for(const {data}of packages)assert(data.pools.every(p=>p.questions.every(q=>q.id!==data.frq.practiceId)))});
test('short answers accept fractions, Arabic digits and decimals without executable input',()=>{for(const [s,n]of [['٧/٥',1.4],['٨٫٤',8.4],['3/4',.75],['0018',18],['−٣',-3]])assert(correctBlank(s,n));for(const s of ['', '1/0','2+4','alert(1)','0x10','Infinity','1e3','sqrt(2)'])assert.equal(numericAnswer(s),null)});

test('the complete practice bank retains all 50 source exercises and corrects Q21 against the original book',()=>{
 const bank=JSON.parse(fs.readFileSync(new URL('public/data/exam-banks/10a1-four-outcomes-assessment/bank.json',root)));
 assert.equal(bank.practiceQuestions.length,50);assert.equal(bank.practiceQuestions.filter(q=>q.type==='MCQ').length,38);assert.equal(bank.practiceQuestions.filter(q=>q.type==='FRQ').length,12);
 assert.deepEqual(bank.outcomes.map(o=>bank.practiceQuestions.filter(q=>q.outcomeId===o.id).length),[10,15,13,12]);
 assert.equal(new Set(bank.practiceQuestions.map(q=>q.id)).size,50);assert.equal(bank.pools.reduce((n,p)=>n+p.questions.length,0),20);
 for(const q of bank.practiceQuestions.filter(q=>q.type==='MCQ')){assert.equal(q.optionHTML.length,4);assert.equal(new Set(q.optionHTML).size,4);assert(q.correctIndex>=0&&q.correctIndex<4)}
 const q21=bank.practiceQuestions.find(q=>q.id.endsWith('coordinate-q21'));assert.deepEqual(q21.spatial3D.points[1],[0,3,0]);assert.deepEqual(q21.spatial3D.midpoint,[.3,1.5,.4]);assert.equal(q21.spatial3D.distance,Math.sqrt(10));
 for(const q of bank.practiceQuestions.filter(q=>q.type==='FRQ')){const p=q.spatial3D;p.midpoint.forEach((v,i)=>assert(Math.abs(v-(p.points[0][i]+p.points[1][i])/2)<1e-9));if(p.distance!==undefined)assert(Math.abs(p.distance-Math.hypot(...p.points[0].map((v,i)=>v-p.points[1][i])))<1e-9)}
});
test('two written working steps plus final answer sum to exactly two marks, with independent partial credit and rounding',()=>{
 for(const {data}of packages){const s=startAttempt(createSession(data,student),data,1000000),a=active(s);let sum=0;
 for(let i=0;i<5;i++){a.blanks[i]=String(data.frq.blanks[i].answer);sum+=data.frq.blanks[i].marks;assert.equal(grade(a,data),sum)}
 assert.equal(sum,2);assert.equal(data.frq.blanks.filter(b=>b.groupTitleHTML).length,3);
 const values={};const lms={set:(k,v)=>{values[k]=String(v);return true},commit:()=>true};s.attempts[0]=finishAttempt(a,data,a.t+1);assert(reportResult(lms,s,data,1).ok);assert.equal(values['cmi.core.exit'],'suspend');assert.equal(values['cmi.core.score.raw'],'20');
 }
 assert(correctBlank('3.46',Math.sqrt(12),.005));assert(!correctBlank('3.45',Math.sqrt(12),.005));
});

for(const {kind,data}of packages)test(`${kind}: first grade is retained, including zero with answers; only an empty first submission uses try 2`,()=>{
 for(const mode of ['mcq-wrong','written-wrong','whitespace','empty']){
  let s=startAttempt(createSession(data,student),data,1000000);const a=active(s);
  if(mode==='mcq-wrong')a.answers[0]=(selected(a,data)[0].correctIndex+1)%4;
  if(mode==='written-wrong')a.blanks[0]='not a number';
  if(mode==='whitespace')a.blanks.fill('  ');
  assert.equal(grade(a,data),0);s.attempts[0]=finishAttempt(a,data,a.t+1000);s.seq++;
  s=done(startAttempt(s,data,1020000),data,10);
  const empty=mode==='empty'||mode==='whitespace';assert.equal(hasResponses(s.attempts[0]),!empty);assert.equal(recordedScore(s,data),empty?10:0);assert.equal(recordedAttempt(s).n,empty?2:1);
  const values={};assert(reportResult({set:(k,v)=>{values[k]=String(v);return true},commit:()=>true},s,data,10000).ok);assert.equal(values['cmi.core.score.raw'],empty?'100':'0');assert.equal(JSON.parse(values['cmi.comments']).countedAttempt,empty?2:1);
  assert.equal(recordedScore(JSON.parse(JSON.stringify(s)),data),empty?10:0);
 }
 let s=done(startAttempt(createSession(data,student),data,1000000),data,6);s=done(startAttempt(s,data,1020000),data,10);assert.equal(recordedScore(s,data),6);
});
