import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Calculator} from '../public/vendor/fx991ce/src/calc/calculator.js';
import {MODES} from '../public/vendor/fx991ce/src/calc/modes/index.js';
import {calculatorGuide} from '../lib/calculator-guide.js';
const load=async p=>JSON.parse(await readFile(new URL('../'+p,import.meta.url)));
const data=await load('public/data/study/calculator-support.json');
const run=keys=>{const c=new Calculator({modes:MODES,storage:null});c.setup.angle='deg';for(const k of keys)c.press(k);return c;};
test('every study question has outcome-specific calculator or manual reasoning support',async()=>{
 let total=0;
 for(const [id,support] of Object.entries(data.classes)){
  const bank=await load(`public/data/study/${id}.json`);
  assert.equal(Object.keys(support.questions).length,bank.questions.length);
  assert.equal(Object.keys(support.outcomes).length,bank.learning_outcomes.length);
  for(const q of bank.questions){const g=support.questions[q.id];assert.equal(g.outcome,q.learning_outcome_id);assert(g.prepare&&g.interpret&&g.solutions.length);assert(calculatorGuide({...q,calculatorSupport:g},'/').includes('Use the output in your written answer'));total++;}
 }
 assert.equal(total,1239);
});
test('generated key sequences agree with independently computed arithmetic and table values',()=>{
 let count=0;
 for(const bank of Object.values(data.classes))for(const g of Object.values(bank.questions)){
  for(const op of [...g.operations,...g.tables.flatMap(t=>t.rows.map(r=>({keys:r.keys,decimal:r.y})))]){
   const got=Number(run(op.keys).top.result?.value?.d?.toString()),expected=Number(op.decimal);
   assert(Number.isFinite(got));assert(Math.abs(got-expected)<=2e-9*Math.max(1,Math.abs(expected)),`${got} != ${expected}`);count++;
  }
 }
 assert.equal(count,763);
});
test('proportions use a working SOLVE guess and preserve forbidden denominator values',()=>{
 for(const [id,excluded,expected] of [['G9G-BOOK-Q09-MCQ-03','5',11],['G9G-BOOK-Q09-MCQ-04','3',58/3]]){
  const g=data.classes['9G3'].questions[id];const c=run(g.keys);
  assert.equal(c.top.constructor.name,'SolveResult');assert(Math.abs(Number(c.top.x.d.toString())-expected)<1e-8);
  assert(g.excluded_values.includes(excluded));assert.equal(g.initial_guess,'10');
 }
});
test('three requested curves have separate tables and reasoning-only problems do not pretend to be solved by a calculator',()=>{
 const tables=data.classes['10G3'].questions['G10G-Q23-FRQ-05'].tables;
 assert.deepEqual(tables.map(t=>t.expression),['X','X^2','X^3']);
 const proof=data.classes['10A1'].questions['G10A-BOOK-Q07-MCQ-01'];
 assert.equal(proof.role,'reasoning');assert.equal(proof.operations.length,0);
 const identity=data.classes['9G3'].questions['G9G-BOOK-Q23-FRQ-04'];
 assert.equal(identity.role,'reasoning');assert.match(identity.prepare,/One SOLVE result cannot prove/);
});
test('each question-specific TABLE sequence reaches the table screen',()=>{
 let count=0;
 for(const bank of Object.values(data.classes))for(const [id,g] of Object.entries(bank.questions))for(const table of g.tables){
  assert.equal(run(table.keys).top.constructor.name,'GridScreen',`${id}: ${table.expression}`);
  count++;
 }
 assert.equal(count,35);
});
