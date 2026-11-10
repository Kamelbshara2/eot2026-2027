import {readFileSync} from 'node:fs';import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import {renderStudentHome,draftHasAnswer} from '../lib/student-design.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))),plan=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
test('student home links each class card straight to the term-1 study booklet and hides exam weeks',()=>{
 const html=renderStudentHome();const cards=[...html.matchAll(/data-classroom="([^"]+)" href="([^"]+)"/g)];assert.deepEqual(cards.map(m=>m[1]),['9G3','10G3','10A1','11G','11A','12G','12A']);for(const [,id,path]of cards)assert.equal(path,`#/classrooms/${id}/banks/term1`);
 assert(!html.includes('/weeks/'));assert(!html.includes('الأسبوع'));assert(html.includes('9 عام')&&html.includes('10 عام')&&html.includes('10 متقدم')&&html.includes('11 عام')&&html.includes('12 متقدم'));assert(html.includes('ملزمة الفصل الأول'));assert(!html.includes('scorm'));
});
test('home statistics come from the booklet banks, not from exam weeks',()=>{const html=renderStudentHome();const total=['9G3','10G3','10A1','11G','11A','12G','12A'].reduce((n,c)=>n+JSON.parse(readFileSync(new URL(`../public/data/study/${c}.json`,import.meta.url))).question_count,0);assert(html.includes(`<b>${total}</b>`));assert(html.includes('<b>178</b>'));assert.equal((html.match(/data-classroom=/g)||[]).length,7)});
test('outcome progress and practice navigation count real responses, including the first MCQ option and numeric zero',()=>{
 for(const d of [undefined,null,{},false,{selected:null},{selected:-1},{fields:[]},{fields:[{value:'  '}]},{paths:[]},{fields:'corrupt cache'},{fields:[null]}])assert.equal(draftHasAnswer(d),false,JSON.stringify(d));
 for(const d of [{selected:0},{selected:3},{fields:[{value:0}]},{fields:[{value:'x=4'}]},{paths:['M0 0L1 1']},{paper:{name:'solution.jpg'}}])assert.equal(draftHasAnswer(d),true,JSON.stringify(d));
});
