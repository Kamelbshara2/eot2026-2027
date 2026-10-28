import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {classroomRoute,classroomGroups,classroomPath,outcomePath,weekOf} from '../lib/classroom-navigation.js';
import {validateOutcome,mergeOutcomeSeeds} from '../lib/outcomes.js';
import {valid} from '../lib/validation.js';
const seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url)));
test('Week 9 plans capture all ten screenshot rows, including repeated topics and exact references, with correctly scoped questions',()=>{
 const expected={'10A1':[['Q13','146 (Q11–16)'],['Q14','153 (Q1–11)'],['Q15','165 (Q1–6, Q11–14)']],'9G3':[['Q12','235 (Q1–8)'],['Q13','236 (Q37–39)'],['Q18','233 (Example 6 · مثال 6)']],'10G3':[['Q14','722 (Q29 & Q30)'],['Q15','730 (Q37–39)'],['Q15','725 (Learn · تعلّم)'],['Q20','729 (Q1–6)']]};
 assert.equal(seed.outcomes.filter(o=>o.examWeek===9).length,10);
 for(const [classroom,refs]of Object.entries(expected)){
  const groups=classroomGroups(classroom,bank.questions,seed.outcomes,seed.assignments,9);
  assert.deepEqual(groups.map(o=>[o.assessmentItem,o.bookPages]),refs);
  for(const o of groups){assert.equal(o.questions.length,classroom==='9G3'?0:o.targetCount);assert(o.titleAr&&o.title);assert(validateOutcome({...o,revision:0,questionIds:[]}));assert.equal(seed.assignments.filter(a=>a.outcome_id===o.id).length,o.questions.length)}
 }
 assert.equal(bank.questions.filter(q=>weekOf(q)===8).length,108);assert.equal(bank.questions.filter(q=>weekOf(q)===9).length,41);
});
test('route week selection preserves legacy Week 8 links and keeps explicit week scopes',()=>{
 assert.equal(classroomRoute('#/classrooms/10G3').examWeek,9);
 assert.equal(classroomRoute('#/classrooms/10G3/exams/week-8').examWeek,8);
 assert.equal(classroomRoute('#/classrooms/10G3/outcomes/old').examWeek,8);
 const selected=classroomRoute(outcomePath('10A1','new-id',9));assert.equal(selected.examWeek,9);assert.equal(selected.outcomeId,'new-id');assert.equal(selected.validWeek,true);
 assert.equal(classroomRoute(classroomPath('9G3',8)+'/manage').manage,true);
 assert.equal(classroomRoute('#/classrooms/10G3/weeks/99/outcomes/new-id').validWeek,false);
});
test('new questions and unassigned practice are isolated by classroom and exam week',()=>{
 const outcome=seed.outcomes.find(o=>o.classroom==='10G3'&&o.examWeek===9);
 const newQuestion={...bank.questions.find(q=>q.classroom==='10G3'),id:'new-week9',examWeek:9};
 assert(valid(newQuestion));assert(!valid({...newQuestion,examWeek:'9'}));
 const assignments=[...seed.assignments,{question_id:newQuestion.id,outcome_id:outcome.id,position:1}];
 const all=[...bank.questions,newQuestion,{...newQuestion,id:'other-class',classroom:'10A1'}];
 const scoped=classroomGroups('10G3',all,seed.outcomes,assignments,9).flatMap(o=>o.questions);assert.equal(scoped.length,15);assert(scoped.some(q=>q.id==='new-week9'));assert(scoped.every(q=>q.classroom==='10G3'&&q.examWeek===9));
 assert.equal(classroomGroups('10G3',all,seed.outcomes,assignments,8).flatMap(o=>o.questions).length,48);
 const extra=classroomGroups('10A1',all,seed.outcomes,assignments,9).find(o=>o.id==='unassigned');assert.deepEqual(extra.questions.map(q=>q.id),['other-class']);
});
test('Week 9 seeds reach old browsers while preserving teacher edits and earlier deletions',()=>{
 const first=seed.outcomes[0],oldIds=seed.outcomes.filter(o=>weekOf(o)===8).map(o=>o.id);
 const current={outcomes:[{...first,title:'Teacher edit',revision:7}],assignments:[]};
 const merged=mergeOutcomeSeeds(current,seed,oldIds);
 assert.equal(merged.outcomes.find(o=>o.id===first.id).title,'Teacher edit');assert.equal(merged.outcomes.filter(o=>o.examWeek===9).length,10);
 assert.equal(merged.outcomes.filter(o=>weekOf(o)===8).length,1);
 assert.deepEqual(mergeOutcomeSeeds(merged,seed,seed.outcomes.map(o=>o.id)),merged);
 const planned=seed.outcomes.find(o=>o.examWeek===9);for(const examWeek of [0,53,'9'])assert.equal(validateOutcome({...planned,examWeek,questionIds:[]}),null);
});
