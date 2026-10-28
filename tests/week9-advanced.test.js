import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
import {valid} from '../lib/validation.js';import {week9GeometryDiagram,validWeek9Geometry} from '../lib/week9-geometry.js';import {classroomGroups} from '../lib/classroom-navigation.js';import {worksheetPage} from '../lib/print-worksheet.js';import katex from 'katex';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url))),qs=bank.questions.filter(q=>q.classroom==='10A1'&&q.examWeek===9);
const q=(p,n)=>qs.find(q=>q.sourcePage===p&&q.sourceQuestion===n);
test('all 27 Grade 10 Advanced questions are bilingual FRQs routed in source order to Week 9 only',()=>{
 assert.equal(qs.length,27);assert.equal(new Set(qs.map(q=>q.id)).size,27);const groups=classroomGroups('10A1',bank.questions,seed.outcomes,seed.assignments,9);assert.deepEqual(groups.map(o=>o.questions.length),[6,11,10]);assert.deepEqual(groups[0].questions.map(q=>q.sourceQuestion),[11,12,13,14,15,16]);assert.deepEqual(groups[1].questions.map(q=>q.sourceQuestion),[1,2,3,4,5,6,7,8,9,10,11]);assert.deepEqual(groups[2].questions.map(q=>q.sourceQuestion),[1,2,3,4,5,6,11,12,13,14]);
 for(const item of qs){assert(valid(item),item.id);assert.equal(item.type,'FRQ');assert(item.promptAr&&item.answerAr);assert(item.responseParts.length);assert.equal(seed.assignments.filter(a=>a.question_id===item.id).length,1);for(const str of [item.prompt,item.promptAr,item.answer,item.answerAr])for(const m of str.matchAll(/\$([^$]+)\$/g))assert.doesNotThrow(()=>katex.renderToString(m[1],{throwOnError:true}))}
 assert.equal(classroomGroups('10A1',bank.questions,seed.outcomes,seed.assignments,8).flatMap(g=>g.questions).length,35);assert.equal(classroomGroups('10G3',bank.questions,seed.outcomes,seed.assignments,9).flatMap(g=>g.questions).length,0);
});
test('page 146 solutions respect equal intercepts, the midsegment theorem, and the confirmed half-side bracket',()=>{
 const a=q(146,11).expectedValues;assert.equal(2*a.x+1,a.x+7);assert.equal(3*a.y-8,a.y+5);
 const b=q(146,12).expectedValues;assert.equal(b.x+3,1.5*b.x+2);assert.equal(2*b.y-1,3*b.y-5);
 assert.equal(q(146,13).expectedValues.x,30/2);assert.equal(q(146,14).expectedValues.x,2*9);assert.equal(q(146,15).expectedValues.x,8);assert.equal(q(146,16).expectedValues.AC,2*10);
});
test('page 153 solutions use corresponding cevians, angle bisectors, and the stated vertex correspondence',()=>{
 for(const [n,result]of [[1,22*10.5/14],[2,33*10/15],[3,22*10/20],[4,12.6*18/12],[5,6*7/5],[6,24*10.5/14]])assert(Math.abs(Object.values(q(153,n).expectedValues)[0]-result)<1e-9);
 assert.equal(q(153,7).expectedValues.distance,Math.round(5*50/35));assert.equal(q(153,8).expectedValues.m,Math.round(20*8/12*10)/10);assert.equal(q(153,9).expectedValues.x,24*7/20);assert.equal(q(153,10).expectedValues.XC,Math.round((14-Math.sqrt(12**2-8**2))*10)/10);assert.equal(q(153,11).expectedValues.EY,Math.round((8*8/12)*10)/10);
});
test('page 165 exact geometric means and right-triangle altitude/leg identities are consistent',()=>{
 for(const item of qs.filter(q=>q.geometricMean)){assert(item.expectedValues.mean>0);assert(Math.abs(item.expectedValues.mean**2-item.geometricMean[0]*item.geometricMean[1])<1e-9)}
 let v=q(165,11).expectedValues;assert(Math.abs(v.x**2-8*23)<1e-8);assert(Math.abs(v.y**2-31*8)<1e-8);assert(Math.abs(v.z**2-31*23)<1e-8);
 v=q(165,12).expectedValues;assert(Math.abs(v.x**2-19*6)<1e-8);assert(Math.abs(v.y**2-25*6)<1e-8);assert(Math.abs(v.z**2-25*19)<1e-8);
 v=q(165,13).expectedValues;assert.equal(2*v.x,9);assert.equal(v.z,2+v.x);assert(Math.abs(v.y**2-2*v.z)<1e-8);
 v=q(165,14).expectedValues;assert.equal(v.x+v.y,20);assert.equal(20*v.y,100);assert(Math.abs(v.z**2-20*v.x)<1e-8);
});
test('21 vector diagrams validate their source and render in compact printable worksheets without response keys',()=>{
 assert.equal(qs.filter(q=>q.geometryDiagram).length,21);for(const item of qs.filter(q=>q.geometryDiagram)){assert(validWeek9Geometry(item.geometryDiagram));const visual=week9GeometryDiagram(item.geometryDiagram);assert(visual.includes('<svg'));assert(!/NaN|undefined/.test(visual));assert(!valid({...item,classroom:'10G3'}));assert(!valid({...item,examWeek:8}));assert(!valid({...item,geometryDiagram:{page:165,number:7}}));const page=worksheetPage(item,{visual});assert(page.includes('print-geometry-page'));assert(!page.includes(item.answer));assert(!page.includes('<textarea'));assert(!page.includes('<input'))}
 assert.equal(week9GeometryDiagram({page:146,number:99}),'');
});
