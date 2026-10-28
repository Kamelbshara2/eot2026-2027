import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import katex from 'katex';
import {valid} from '../lib/validation.js';
import {mcqOptions} from '../lib/mcq.js';
import {linearFunctionGraph} from '../lib/linear-worksheets.js';
import {upgradeQuestion} from '../lib/content-upgrades.js';
import {printableQuestion} from '../lib/print-worksheet.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url)));
const updates=JSON.parse(await readFile(new URL('../lib/content-updates.json',import.meta.url)));
const qs=bank.questions.filter(q=>q.examWeek===9);
const numeric=tex=>{let s=tex.replaceAll('$','').replaceAll('\\ ', '').replace(/\\frac\{([\d.]+)\}\{([\d.]+)\}/g,'($1/$2)').replace(/\\sqrt\{(\d+)\}/g,'Math.sqrt($1)').replace(/\\sqrt(\d)/g,'Math.sqrt($1)').replace(/(\d)(Math\.sqrt)/g,'$1*$2');assert(/^[\d.()+*/\-Mathsqrt]+$/.test(s),tex);return Function(`return (${s})`)()};
test('all 60 Week 9 exercises are four-option MCQs with bilingual valid mathematics, and none is printable as FRQ',()=>{
 assert.equal(qs.length,60);assert.deepEqual(['10A1','10G3','9G3'].map(c=>qs.filter(q=>q.classroom===c).length),[27,14,19]);
 for(const q of qs){assert(valid(q),q.id);assert.equal(q.type,'MCQ');assert.equal(q.options.length,4);assert.equal(new Set(q.options).size,4);assert(!q.responseParts);assert(!printableQuestion(q));const html=mcqOptions(q);assert.equal((html.match(/type="radio"/g)||[]).length,4);assert(!/NaN|undefined/.test(html));for(const s of [q.prompt,q.promptAr,q.answer,q.answerAr,...q.options,...q.optionsAr])for(const m of s.matchAll(/\$([^$]+)\$/g))assert.doesNotThrow(()=>katex.renderToString(m[1],{throwOnError:true}),q.id)}
});
test('every advanced selected option agrees with the independently checked numerical model and distractors differ',()=>{
 for(const q of qs.filter(q=>q.classroom==='10A1')){
  const keys=Object.keys(q.expectedValues),choices=q.options.map(s=>s.replaceAll('$','').split(',').map(t=>numeric(t.includes('=')?t.split('=')[1]:t)));
  const matches=choices.map(v=>v.length===keys.length&&v.every((n,i)=>Math.abs(n-q.expectedValues[keys[i]])<1e-7));assert.equal(matches.filter(Boolean).length,1,q.id);assert(matches[q.correctIndex],q.id);
 }
});
test('Grade 9 graph and equation options have exactly one mathematical match and show the supplied points',()=>{
 for(const q of qs.filter(q=>q.classroom==='9G3')){
  const g=q.linearEquationChoices||q.linearChoices;assert.equal(g.choices.filter(c=>JSON.stringify(c)===JSON.stringify(g.target)).length,1,q.id);
  if(q.linearGraph){const [m,b]=q.linearGraph.coefficients;assert.deepEqual([m,b],g.target);if(q.linearGraph.showPoints){const html=linearFunctionGraph(q);for(const [x,y]of q.linearGraph.sourcePoints){assert.equal(m*x+b,y);assert(html.includes(`(${x}, ${y})`))}}}
  if(q.linearChoices){assert.equal((mcqOptions(q).match(/<svg/g)||[]).length,4);assert(!valid({...q,linearChoices:{...q.linearChoices,choices:Array(4).fill(g.target)}}))}
  else assert(!valid({...q,linearEquationChoices:{...g,choices:Array(4).fill(g.target)}}));
 }
 const square=qs.find(q=>q.squareChoices);assert(!valid({...square,correctIndex:(square.correctIndex+1)%4}));
});
test('37 original written records upgrade in place, retaining IDs, diagrams, and teacher edits',()=>{
 const conversions=updates.filter(u=>u.before.examWeek===9&&u.before.type==='FRQ'&&u.after.type==='MCQ');assert.equal(conversions.length,37);
 for(const {before,after}of conversions){assert.deepEqual(upgradeQuestion(before),after);assert.deepEqual(after,qs.find(q=>q.id===before.id));assert.deepEqual(after.geometryDiagram,before.geometryDiagram);const edited={...before,prompt:'Teacher custom question'};assert.deepEqual(upgradeQuestion(edited),edited)}
});

test('old offline Grade 9 plans receive new question assignments once, without restoring teacher unassignments',async()=>{
 const {mergeOutcomeSeeds}=await import('../lib/outcomes.js');const seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
 const originals=seed.outcomes.filter(o=>o.classroom==='9G3'&&o.examWeek===9).map(o=>({...o,targetCount:o.bookPages.startsWith('236')?3:o.bookPages.startsWith('233')?1:8}));
 const seen=seed.outcomes.map(o=>o.id);const merged=mergeOutcomeSeeds({outcomes:originals,assignments:[]},seed,seen);assert.equal(merged.assignments.length,19);assert.deepEqual(merged.outcomes.map(o=>o.targetCount),[8,9,2]);
 const removed=merged.assignments[0].question_id;const edited={...merged,assignments:merged.assignments.slice(1)};const next=mergeOutcomeSeeds(edited,seed,[...seen,...seed.assignmentSeedQuestionIds.map(id=>`question:${id}`)]);assert(!next.assignments.some(a=>a.question_id===removed));
});
