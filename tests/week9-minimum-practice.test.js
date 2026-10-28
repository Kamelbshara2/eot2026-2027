import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {classroomGroups} from '../lib/classroom-navigation.js';
import {mergeOutcomeSeeds} from '../lib/outcomes.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),plan=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
const made=bank.questions.filter(q=>q.examWeek===9&&q.sourceKind==='teacher-designed');
test('all ten Week 9 outcomes have at least five uniquely assigned MCQs, with aligned supplements',()=>{
 assert.equal(made.length,10);
 const expected={'10A1':[6,11,10],'10G3':[5,5,5,6],'9G3':[8,9,5]};
 for(const [classroom,counts]of Object.entries(expected)){
  const groups=classroomGroups(classroom,bank.questions,plan.outcomes,plan.assignments,9);assert.deepEqual(groups.map(o=>o.questions.length),counts);
  for(const o of groups){assert(o.questions.length>=5);assert.equal(o.targetCount,o.questions.length);assert(o.questions.every(q=>q.type==='MCQ'&&q.classroom===classroom&&q.examWeek===9));assert.equal(new Set(o.questions.map(q=>JSON.stringify([q.prompt,q.linearGraph?.coefficients,q.linearChoices?.target]))).size,o.questions.length);for(const q of o.questions)assert.equal(plan.assignments.filter(a=>a.question_id===q.id).length,1)}
 }
 for(const q of made){assert(!q.sourcePage,'Designed exercises must not claim to be numbered textbook questions');assert.equal(q.options.length,4);assert.equal(new Set(q.options).size,4);assert(plan.assignmentSeedQuestionIds.includes(q.id))}
});
test('new quadratic MCQs have exactly one complete real solution set and correct completing-square steps',()=>{
 for(const q of made.filter(q=>q.problemData?.rootChoices)){
  const {coefficients:[a,b,c],rootChoices,completion}=q.problemData;
  const discriminant=b*b-4*a*c;assert(discriminant>0);
  const roots=[(-b-Math.sqrt(discriminant))/(2*a),(-b+Math.sqrt(discriminant))/(2*a)].sort((a,b)=>a-b);
  const matches=rootChoices.map(choice=>choice.length===2&&[...choice].sort((a,b)=>a-b).every((x,i)=>Math.abs(x-roots[i])<1e-9));
  assert.equal(matches.filter(Boolean).length,1,q.id);assert(matches[q.correctIndex],q.id);
  if(completion){assert.equal(2*completion.shift,b);assert.equal(completion.rhs,completion.shift**2-c);for(const x of [-5,-1,0,2,6])assert.equal(x*x+b*x+c,(x+completion.shift)**2-completion.rhs)}
 }
 for(const q of made.filter(q=>q.squareChoices)){const {b,c,shift}=q.problemData;assert.equal(c,b*b/4);assert.equal(shift,b/2);const matches=q.squareChoices.map(([c,h])=>c===b*b/4&&2*h===b);assert.equal(matches.filter(Boolean).length,1);assert(matches[q.correctIndex])}
});
test('new constant-function choices include one horizontal line at the requested height',()=>{
 for(const q of made.filter(q=>q.classroom==='9G3')){const {target,choices}=q.linearChoices;assert.equal(target.kind,'line');assert.equal(target.m,0);const matches=choices.map(c=>c.kind==='line'&&c.m===0&&c.b===target.b);assert.equal(matches.filter(Boolean).length,1);assert(matches[q.correctIndex])}
});
test('returning browsers receive ten new assignments once and preserve teacher edits and removals',()=>{
 const originals=plan.outcomes.filter(o=>o.examWeek===9).map(o=>({...o,targetCount:({'4976444a-a131-47e4-8dfd-3a9aee82b2d8':2,'65883fee-f0d9-4fc4-98d7-69bd60ac365d':4,'43923d3e-bf8e-47e1-a2e5-e6c2a7987d78':3,'af78925a-ba6e-45ec-8cf8-91bb3304efd5':1}[o.id]??o.targetCount)}));
 const added=new Set(made.map(q=>q.id)),seen=[...plan.outcomes.map(o=>o.id),...plan.assignmentSeedQuestionIds.filter(id=>!added.has(id)).map(id=>`question:${id}`)];
 const previous={outcomes:originals,assignments:plan.assignments.filter(a=>!added.has(a.question_id)&&originals.some(o=>o.id===a.outcome_id))};
 const next=mergeOutcomeSeeds(previous,plan,seen);assert.equal(next.assignments.length-previous.assignments.length,10);for(const o of next.outcomes)assert(o.targetCount>=5);
 const removed=next.assignments.find(a=>added.has(a.question_id));const seenAfter=[...seen,...made.map(q=>`question:${q.id}`)];assert(!mergeOutcomeSeeds({...next,assignments:next.assignments.filter(a=>a!==removed)},plan,seenAfter).assignments.some(a=>a.question_id===removed.question_id));
 const teacher={...originals.find(o=>o.classroom==='10G3'),title:'Teacher custom title',targetCount:12,revision:7,lastOperation:'custom'};assert.equal(mergeOutcomeSeeds({outcomes:[teacher],assignments:[]},plan,seen).outcomes.find(o=>o.id===teacher.id).targetCount,12);
 const seeded={...originals.find(o=>o.classroom==='10G3'),revision:2,lastOperation:originals.find(o=>o.classroom==='10G3').id};assert.equal(mergeOutcomeSeeds({outcomes:[seeded],assignments:[]},plan,seen).outcomes.find(o=>o.id===seeded.id).targetCount,5);
});
