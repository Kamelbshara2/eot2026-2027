import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import katex from 'katex';
import {valid} from '../lib/validation.js';import {classroomGroups} from '../lib/classroom-navigation.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),plan=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url))),qs=bank.questions.filter(q=>q.classroom==='10G3'&&q.examWeek===9);
const q=(page,n,part)=>qs.find(q=>q.sourcePage===page&&q.sourceQuestion===n&&(!part||q.sourcePart===part));
test('14 bilingual Grade 10 General items follow all four Week 9 book references without touching earlier practice',()=>{
 assert.equal(qs.length,14);assert.equal(qs.filter(q=>q.type==='MCQ').length,14);assert.equal(qs.filter(q=>q.type==='FRQ').length,0);assert.deepEqual(classroomGroups('10G3',bank.questions,plan.outcomes,plan.assignments,9).map(o=>o.questions.length),[4,3,1,6]);
 for(const item of qs){assert(valid(item),item.id);assert(item.promptAr&&item.answerAr);assert.equal(plan.assignments.filter(a=>a.question_id===item.id).length,1);for(const str of [item.prompt,item.promptAr,item.answer,item.answerAr,...item.options,...item.optionsAr])for(const match of str.matchAll(/\$([^$]+)\$/g))assert.doesNotThrow(()=>katex.renderToString(match[1],{throwOnError:true}))}
 assert.equal(classroomGroups('10G3',bank.questions,plan.outcomes,plan.assignments,8).flatMap(o=>o.questions).length,48);assert.equal(classroomGroups('10A1',bank.questions,plan.outcomes,plan.assignments,9).flatMap(o=>o.questions).length,27);assert.equal(classroomGroups('9G3',bank.questions,plan.outcomes,plan.assignments,9).flatMap(o=>o.questions).length,19);
});
test('page 722 retains four self-contained MCQs, with exactly one valid option for each requested part',()=>{
 const a=q(722,29,'A');assert.equal(a.expectedValues.t,6);assert.equal(-16*a.expectedValues.t**2+576,0);assert(a.prompt.includes('576'));assert(a.prompt.includes('t\\ge0'));assert.equal(a.correctIndex,1);
 for(const item of [q(722,29,'B'),q(722,30,'A')]){const d=item.problemData;const matches=d.optionCoefficients.map(c=>c.every((v,i)=>v===d.coefficients[i]));assert.equal(matches.filter(Boolean).length,1);assert(matches[item.correctIndex])}
 const volume=q(722,30,'B');assert.equal(volume.expectedValues.V,3*(9-6)**2);assert.equal(volume.correctIndex,2);assert.equal(q(722,30,'A').diagram,'box-net');assert.equal(volume.diagram,'box-net');for(const item of qs.filter(q=>q.type==='MCQ')){assert.equal(item.options.length,4);assert.equal(item.optionsAr.length,4);assert.equal(new Set(item.options).size,4)}
});
test('page 725 Learn and all six page 729 constants satisfy the completing-the-square identity exactly',()=>{
 const items=[q(725,1),...qs.filter(q=>q.sourcePage===729)];assert.equal(q(725,1).expectedValues.c,16);assert.equal(q(725,1).sourceKind,'worked-example');assert.deepEqual(qs.filter(q=>q.sourcePage===729).map(q=>q.expectedValues.c),[169,144,90.25,72.25,6.25,42.25]);
 for(const item of items){const {b,c,shift}=item.problemData;assert.equal(c,(b/2)**2);assert.equal(shift,b/2);for(const x of [-7,-.5,0,4])assert.equal(x*x+b*x+c,(x+shift)**2)}
});
test('page 730 identifies the unique non-square, accepts the repeated root 4 and compares exact versus approximate methods correctly',()=>{
 const odd=q(730,37).problemData;assert.deepEqual(odd.coefficients.map(([a,b,c])=>Math.abs(b*b-4*a*c)<1e-12),[true,true,true,false]);assert.equal(odd.oddIndex,3);
 const repeated=q(730,38).problemData.exampleCoefficients,[a,b,c]=repeated;assert.notEqual(a,0);assert.equal(b*b-4*a*c,0);assert.equal(-b/(2*a),4);assert(q(730,38).answer.includes('a\\ne0'));
 const comparison=q(730,39).problemData;assert.equal(comparison.discriminant,53);for(const root of [(5-Math.sqrt(53))/2,(5+Math.sqrt(53))/2])assert(Math.abs(root*root-5*root-7)<1e-12);assert(q(730,39).answer.includes('(-1.14,0)'));assert(q(730,39).answer.includes('(6.14,0)'));assert(q(730,39).answer.includes('rational coefficients'));
});
