import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const {questions}=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url)));
const {outcomes,assignments}=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url)));
for(const [classroom,slug,mcqs,frqs]of [['9G3','grade-9-general',3,1],['10G3','grade-10-general',3,2],['10A1','grade-10-advanced',2,1]]){
 test(`${classroom} exam covers every assigned outcome once, retains question types and exports without a watermark`,async()=>{
  const base=`../public/exams/${slug}-math-8th-week-2026-10-23`;
  const html=await readFile(new URL(base+'.html',import.meta.url),'utf8');
  const entries=[...html.matchAll(/data-question-id="([^"]+)" data-type="(MCQ|FRQ)"/g)];
  assert.equal(entries.length,mcqs+frqs);assert.equal(new Set(entries.map(m=>m[1])).size,entries.length);
  const expected=outcomes.filter(o=>o.classroom===classroom).map(o=>o.id).sort();
  const actual=entries.map(([,id,type])=>{const q=questions.find(q=>q.id===id);assert(q);assert.equal(q.classroom,classroom);assert.equal(q.type,type);assert(!html.includes(q.answer));return assignments.find(a=>a.question_id===id)?.outcome_id}).sort();
  assert.deepEqual(actual,expected);assert.equal(entries.filter(m=>m[2]==='MCQ').length,mcqs);assert.equal(entries.filter(m=>m[2]==='FRQ').length,frqs);
  assert(!/question-watermark|0502837825|<input|<textarea|correctIndex/.test(html));
  assert(html.includes('Khalid bin Alwaleed School'));assert(html.includes('23/10/2026'));assert(html.includes('Math 8th Week'));assert(html.includes('data:font/woff2;base64,'));
  const pdf=await readFile(new URL(base+'.pdf',import.meta.url));assert.equal(pdf.subarray(0,5).toString(),'%PDF-');assert(pdf.length>20000);
 });
}
