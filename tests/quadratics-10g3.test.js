import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {mergeOutcomeSeeds} from '../lib/outcomes.js';
import {optionGraph} from '../lib/mcq.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url),'utf8'));
const seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url),'utf8'));
const targets=new Map([[3,[1,1,0]],[4,[1,0,-8]],[5,[1,-3,0]],[6,[1,0,7]],[7,[1,-2.5,0]],[8,[1,-5,-2]],[9,[1,0,6]],[10,[1,3,-4]],[23,[-1/3,0,0]],[24,[4/9,0,0]],[25,[-2,0,0]],[26,[36/25,0,0]],[27,[-1,0,-7]],[28,[2,3,8]],[29,[2/3,0,6]],[30,[-4/3,0,-5]]]);
function assigned(outcome){return seed.assignments.filter(a=>a.outcome_id===outcome.id).sort((a,b)=>a.position-b.position).map(a=>bank.questions.find(q=>q.id===a.question_id))}
test('two separate transformation EOT items each have eight graph and eight description MCQs',()=>{
 const outcomes=seed.outcomes.filter(o=>o.bookPages.startsWith('707'));assert.equal(outcomes.length,2);
 for(const [i,outcome] of outcomes.entries()){
  const qs=assigned(outcome);assert.equal(outcome.classroom,'10G3');assert.equal(outcome.targetCount,16);assert.equal(qs.length,16);
  const numbers=i?[23,24,25,26,27,28,29,30]:[3,4,5,6,7,8,9,10];
  for(const kind of ['graph','description']){const group=qs.filter(q=>q.transformation.kind===kind);assert.deepEqual(group.map(q=>q.sourceQuestion),numbers);
   for(const q of group){assert.equal(q.classroom,'10G3');assert.equal(q.sourcePage,q.sourceQuestion>=27?708:707);assert.equal(q.options.length,4);assert.equal(q.optionsAr.length,4);assert(q.promptAr&&q.answerAr);assert.deepEqual(q.transformation.target,targets.get(q.sourceQuestion));
    // Compare each option as a polynomial at multiple x values, including shifts.
    const f=([a,h,k],x)=>a*(x-h)**2+k;
    const matching=q.transformation.choices.map(c=>[-3,0,2,5].every(x=>Math.abs(f(c,x)-f(targets.get(q.sourceQuestion),x))<1e-9));assert.equal(matching.filter(Boolean).length,1);assert(matching[q.correctIndex]);
    assert(q.answer.includes(`Correct option: ${String.fromCharCode(65+q.correctIndex)}`));
    if(kind==='graph'){const svgs=q.transformation.choices.map((choice,j)=>optionGraph(choice,String.fromCharCode(65+j)));for(const svg of svgs){assert(svg.includes('viewBox="0 0 480 580"'));assert(svg.includes('unit grid'));assert(!/NaN|Infinity/.test(svg))}}
   }
  }
 }
});
test('factoring has six complete solution sets; each option has exactly one correct solution set',()=>{
 const o=seed.outcomes.find(o=>o.bookPages==='721 (Q5–10)'),qs=assigned(o);assert.equal(o.targetCount,6);assert.equal(qs.length,6);assert.deepEqual(qs.map(q=>q.sourceQuestion),[5,6,7,8,9,10]);
 const coefficients=[[27,-81,0],[14,-36,-18],[1,3,0],[1,-4,0],[1,-6,-27],[1,11,18]];
 const sets=[[[0,3],[0,-3],[3],[0,9]],[[3/7,3],[-3/7,3],[-3/7,-3],[-3,3/7]],[[0,3],[-3],[-3,0],[-3,3]],[[0,-4],[4],[-4,4],[0,4]],[[-3,9],[-9,3],[3,9],[-3,-9]],[[9,2],[-9,-2],[-9,2],[-6,-3]]];
 for(const [i,q] of qs.entries()){assert.equal(q.sourcePage,721);assert.equal(q.classroom,'10G3');assert.equal(q.type,'MCQ');assert.equal(q.options.length,4);assert.equal(new Set(q.options).size,4);assert(q.answer.includes('Check:'));const [a,b,c]=coefficients[i],match=sets[i].map(s=>s.length===2&&new Set(s).size===2&&s.every(x=>Math.abs(a*x*x+b*x+c)<1e-9));assert.equal(match.filter(Boolean).length,1);assert(match[q.correctIndex]);}
 assert.equal(qs[1].options[qs[1].correctIndex],'$x \\in \\{-\\frac{3}{7},3\\}$');
});
test('new outcome seeds reach existing browsers without replacing edits or restoring a previously seen deletion',()=>{
 const old=seed.outcomes[0],fresh=seed.outcomes.find(o=>o.examWeek===9),edited={...old,title:'Teacher edited title',revision:8};
 const current={outcomes:[edited],assignments:[{question_id:'teacher-question',outcome_id:old.id,position:1}]};
 const merged=mergeOutcomeSeeds(current,seed,seed.previousSeedIds);
 assert.equal(merged.outcomes.find(o=>o.id===old.id).title,'Teacher edited title');assert(!merged.outcomes.some(o=>o.id===seed.outcomes[1].id));assert(merged.outcomes.some(o=>o.id===fresh.id));assert.equal(merged.assignments.filter(a=>a.outcome_id===fresh.id).length,0);
 const repeated=mergeOutcomeSeeds(merged,seed,seed.outcomes.map(o=>o.id));assert.deepEqual(repeated,merged);
});
