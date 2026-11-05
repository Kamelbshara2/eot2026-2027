import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import {renderStudentHome,draftHasAnswer} from '../lib/student-design.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),plan=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
test('student home shows actual counts for the selected week and routes each card to that classroom',()=>{
 const html=renderStudentHome({questions:bank.questions,outcomes:plan.outcomes});assert(html.includes('<b>121</b>'));assert(html.includes('<b>12</b>'));assert(!html.includes('<b>299</b>'));const cards=[...html.matchAll(/data-classroom="([^"]+)" href="([^"]+)"/g)];assert.deepEqual(cards.map(m=>m[1]),['9G3','10G3','10A1']);for(const [,id,path]of cards)assert.equal(path,`#/classrooms/${id}/weeks/10`);assert(!html.includes('scorm'));
 const earlier=renderStudentHome({questions:bank.questions,outcomes:plan.outcomes,week:9});assert(earlier.includes('<b>70</b>'));assert(!earlier.includes('<b>121</b>'));assert(earlier.includes('/9G3/weeks/9'));
});
test('loading home avoids invented question or learning-outcome statistics',()=>{const html=renderStudentHome();assert(html.includes('جاري التحميل'));assert(!html.includes('<b>121</b>'));assert(!html.includes('<b>12</b>'));assert.equal((html.match(/data-classroom=/g)||[]).length,3)});
test('outcome progress and practice navigation count real responses, including the first MCQ option and numeric zero',()=>{
 for(const d of [undefined,null,{},false,{selected:null},{selected:-1},{fields:[]},{fields:[{value:'  '}]},{paths:[]},{fields:'corrupt cache'},{fields:[null]}])assert.equal(draftHasAnswer(d),false,JSON.stringify(d));
 for(const d of [{selected:0},{selected:3},{fields:[{value:0}]},{fields:[{value:'x=4'}]},{paths:['M0 0L1 1']},{paper:{name:'solution.jpg'}}])assert.equal(draftHasAnswer(d),true,JSON.stringify(d));
});
