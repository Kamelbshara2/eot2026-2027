import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import katex from 'katex';
import {valid,classifyTriangle} from '../lib/validation.js';import {classroomGroups} from '../lib/classroom-navigation.js';import {rightTriangleDiagram} from '../lib/right-triangle-diagrams.js';import {worksheetPage,printableQuestion} from '../lib/print-worksheet.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),plan=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url))),qs=bank.questions.filter(q=>q.classroom==='10A1'&&q.examWeek===10),near=(a,b)=>assert(Math.abs(a-b)<1e-8*Math.max(1,Math.abs(b)));
test('10A1 Week 10 has 38 MCQs and 12 unique coordinate FRQs in the confirmed four outcomes',()=>{
 assert.equal(qs.length,50);assert.equal(qs.filter(printableQuestion).length,12);assert.equal(qs.filter(q=>q.type==='MCQ').length,38);const groups=classroomGroups('10A1',bank.questions,plan.outcomes,plan.assignments,10);assert.deepEqual(groups.map(o=>o.questions.length),[10,15,13,12]);assert.deepEqual(groups.map(o=>o.assessmentItem),['Q15','Q16','Q17','Q24']);assert.equal(new Set(qs.map(q=>q.id)).size,50);
 for(const q of qs){assert(valid(q),q.id);assert.equal(plan.assignments.filter(a=>a.question_id===q.id).length,1);for(const s of [q.prompt,q.promptAr,q.answer,q.answerAr,...q.options,...q.optionsAr])for(const m of s.matchAll(/\$([^$]+)\$/g))assert.doesNotThrow(()=>katex.renderToString(m[1],{throwOnError:true}),q.id);if(q.type==='MCQ')assert.equal(new Set(q.options).size,4)}
});
test('geometric mean exercises are preserved in Week 9 and independently assigned for Week 10',()=>{
 const mean=qs.filter(q=>q.sourcePage===165);assert.equal(mean.length,10);for(const q of mean){const old=bank.questions.find(p=>p.id===q.id.replace('w10','w9'));assert(old);assert.equal(q.correctIndex,old.correctIndex);assert.deepEqual(q.expectedValues,old.expectedValues);assert.deepEqual(q.options,old.options);assert.equal(old.examWeek,9);if(q.geometricMean)near(q.expectedValues.mean**2,q.geometricMean[0]*q.geometricMean[1])}
});
test('all twelve Pythagorean diagrams have one positive valid answer and the converse classifies the three source triples',()=>{
 const pyth=qs.filter(q=>q.rightTriangleProblem);assert.equal(pyth.length,12);const expected=[3*Math.sqrt(2),12,60,1/3,Math.sqrt(1345),Math.sqrt(663),15,51,100,13,6,16];for(const q of pyth){const p=q.rightTriangleProblem;near(p.legs[0]**2+p.legs[1]**2,p.hyp**2);near(p.choiceValues[q.correctIndex],expected[q.sourceQuestion-1]);assert(!valid({...q,correctIndex:(q.correctIndex+1)%4}))}
 const classifications=qs.filter(q=>q.triangleClassification);assert.deepEqual(classifications.map(q=>q.triangleClassification.choiceValues[q.correctIndex]),['acute','right','right']);assert.equal(classifyTriangle([1,2,3]),'not-triangle');assert.equal(classifyTriangle([2,3,4]),'obtuse');
 for(const q of qs.filter(q=>q.rightTriangleDiagram)){const html=rightTriangleDiagram(q);assert(html.includes('<svg'));assert(!/NaN|undefined/.test(html));assert(html.includes('angle-mark'))}
});
test('special-triangle answers satisfy the 30-60-90 ratios and altitude/projection relationships',()=>{
 const get=(page,n)=>qs.find(q=>q.sourcePage===page&&q.sourceQuestion===n).specialTriangle.expected;
 assert.deepEqual(get(184,19),[8,16]);assert.deepEqual(get(184,20),[10,20]);let [x,y]=get(184,21);near(x,y*Math.sqrt(3));near(2*y,15);[x,y]=get(184,22);near(x,y*Math.sqrt(3));near(y,17/2);[x,y]=get(184,23);near(x,24*Math.sqrt(3));near(y,48);[x,y]=get(184,24);near(x*Math.sqrt(3),14);near(y,2*x);
 [x,y]=get(185,33);near(x*Math.sqrt(2),13);assert.equal(y,45);[x,y]=get(185,34);near(y,6*Math.sqrt(2));near(x,6/Math.sqrt(2));assert.deepEqual(get(185,35),[3,1]);assert.deepEqual(get(185,36),[5,10]);[x,y]=get(185,37);near(y*9,(3*Math.sqrt(3))**2);near(x*x,(y+9)*9);[x,y]=get(185,38);assert.equal(x,45);near(y,12*Math.sqrt(2));assert.deepEqual(get(184,25),[20]);
 for(const q of qs.filter(q=>q.specialTriangle))assert(!valid({...q,correctIndex:(q.correctIndex+1)%4}));
});
test('3D midpoint and distance exercises retain every coordinate and exact radical answer without duplicates',()=>{
 const frqs=qs.filter(q=>q.spatial3D);assert.deepEqual(frqs.map(q=>q.sourceQuestion),Array.from({length:12},(_,i)=>i+13));const distances={19:6,20:2*Math.sqrt(3),21:1,22:Math.sqrt(17),23:Math.sqrt(39),24:Math.sqrt(31)};
 for(const q of frqs){const p=q.spatial3D;for(let i=0;i<3;i++)near(p.midpoint[i],(p.points[0][i]+p.points[1][i])/2);if(p.distance!==undefined){near(p.distance,distances[q.sourceQuestion]);near(p.distance,Math.hypot(...p.points[0].map((v,i)=>v-p.points[1][i])))}assert(!q.sourcePage);const html=worksheetPage(q);assert(html.includes('ألاستاذ كامل بشارة 0502837825'));assert(!html.includes(q.answer));assert(!/<input|<textarea/.test(html));assert(html.includes('print-spatial-page'));assert(!valid({...q,spatial3D:{...p,midpoint:[0,0,1000]}}))}
});

test('every displayed two-variable option agrees with its numerical values after exact radical simplification',()=>{
 const number=tex=>{let s=tex.replaceAll('^\\circ','').replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g,'(($1)/($2))').replace(/\\sqrt([23])/g,'Math.sqrt($1)').replace(/(\d)(Math\.sqrt)/g,'$1*$2');assert(/^[0-9.+\-*/()Mathsqrt]+$/.test(s),tex);return Function(`return (${s})`)()};
 for(const q of qs.filter(q=>q.specialTriangle?.expected.length===2))q.options.forEach((text,i)=>{assert(text.includes('\\begin{gathered}'));const s=text.slice(text.indexOf('x=')+2,text.indexOf('\\end{gathered}')),values=s.split('\\\\y=').map(number);assert.equal(values.length,2);values.forEach((v,j)=>near(v,q.specialTriangle.choiceValues[i][j]))});
});

test('the 10A1 printed spatial review has twelve distinct written questions and excludes MCQ exercises',async()=>{
 const base='../public/worksheets/grade-10-advanced-week10-spatial-frq-review',html=await readFile(new URL(base+'.html',import.meta.url),'utf8'),ids=[...html.matchAll(/data-question-id="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,12);assert.equal(new Set(ids).size,12);assert(ids.every(id=>qs.some(q=>q.id===id&&q.type==='FRQ')));assert(html.includes('ألاستاذ كامل بشارة 0502837825'));assert(!/<input|<textarea/.test(html));assert.equal((await readFile(new URL(base+'.pdf',import.meta.url))).subarray(0,5).toString(),'%PDF-');
});
