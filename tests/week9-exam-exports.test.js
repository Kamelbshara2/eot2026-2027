import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const read=name=>readFile(new URL(`../public/${name}`,import.meta.url));
const bank=JSON.parse(await read('data/questions.json'));
const plan=JSON.parse(await read('data/learning-outcomes.json'));
const manifest=JSON.parse(await read('exams/week9-exam-manifest.json'));
for(const exam of manifest.exams)test(`${exam.grade} Week 9 exam has 5 practised MCQs worth 10 marks and covers every learning outcome`,async()=>{
 assert.equal(manifest.examWeek,9);assert.equal(manifest.marks,10);assert.equal(manifest.marksPerQuestion,2);assert.equal(exam.questions.length,5);assert.equal(exam.questions.reduce((sum,q)=>sum+q.marks,0),10);
 const expected=plan.outcomes.filter(o=>o.classroom===exam.classroom&&o.examWeek===9).map(o=>o.id).sort();assert.deepEqual([...new Set(exam.questions.map(q=>q.outcomeId))].sort(),expected);
 const html=(await read(`exams/${exam.slug}.html`)).toString();assert.equal((html.match(/data-type="MCQ" data-marks="2"/g)||[]).length,5);assert.equal((html.match(/class="choice-letter"/g)||[]).length,20);assert.equal((html.match(/class="exam-page"/g)||[]).length,2);
 assert(html.includes('Math 9th Week'));assert(html.includes('Khalid bin Alwaleed School'));assert(!/question-watermark|0502837825|correctIndex|data-type="FRQ"|Teacher answer key|23\/10\/2026/.test(html));
 for(const item of exam.questions){const source=bank.questions.find(q=>q.id===item.id);assert(source);assert.equal(source.type,'MCQ');assert.equal(source.examWeek,9);assert.equal(source.classroom,exam.classroom);assert.equal(item.marks,2);assert.equal(plan.assignments.find(a=>a.question_id===source.id).outcome_id,item.outcomeId);assert.deepEqual([...item.optionOrder].sort(),[0,1,2,3]);assert.equal(item.optionOrder[item.correctIndex],source.correctIndex);assert(html.includes(`data-question-id="${item.id}"`));assert(!html.includes(source.answer))}
 const pdf=await read(`exams/${exam.slug}.pdf`);assert.equal(pdf.subarray(0,5).toString(),'%PDF-');assert(pdf.length>20000);
});
test('separate Week 9 teacher key includes all 15 source question references and a PDF',async()=>{
 const html=(await read('exams/math-9th-week-teacher-answer-keys.html')).toString();assert.equal((html.match(/class="key-row"/g)||[]).length,15);assert.equal((html.match(/class="exam-page"/g)||[]).length,3);for(const exam of manifest.exams)for(const q of exam.questions)assert(html.includes(q.id));assert(!/question-watermark|0502837825/.test(html));assert.equal((await read('exams/math-9th-week-teacher-answer-keys.pdf')).subarray(0,5).toString(),'%PDF-');
});
