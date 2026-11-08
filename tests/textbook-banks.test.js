import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import katex from 'katex';
import {validateExamBank,examBankRoute,examBankPath,bankAssetUrl,clearExamBankSession,bankStorageKey} from '../lib/exam-bank-ui.js';
import {createTermMock,validTermMock,gradeTermMock,mockStorageKey} from '../lib/term-mock-core.js';
const read=async p=>JSON.parse(await readFile(new URL('../'+p,import.meta.url)));
for(const [classroom,folder,count,los,diagrams] of [['10A1','10a1-term1',108,25,60],['9G3','9g3-term1',126,26,16]]){
 const bank=await read(`public/data/exam-banks/${folder}/index.json`);
 test(`${classroom}: original-book provenance, complete LO downloads and labelled derived practice`,async()=>{
  assert(validateExamBank(bank));assert.equal(bank.content_version,'exam-review-v2');assert.equal(bank.questions.length,count);assert.equal(bank.learning_outcomes.length,los);
  assert.deepEqual(await read(`public/data/exam-banks/${folder}/bank.json`),bank);
  for(const [i,o] of bank.learning_outcomes.entries()){
   assert(o.question_count>=4);assert.equal(o.question_type,i<20?'mcq':'frq');assert.equal(o.exam_slot,`Q${i+1}`);
   const group=bank.questions.filter(q=>q.learning_outcome_id===o.id);assert.deepEqual((await read(`public/data/exam-banks/${folder}/${o.download}`)).questions,group);assert.equal(o.booklet_question_ids.length,4);assert(o.booklet_question_ids.every(id=>group.some(q=>q.id===id)));
   assert(o.textbook_references.every(r=>r.printed_page&&r.exercises_or_section));
   for(const q of group){assert(q.id.includes('-BOOK-')||q.parent_question_id);if(q.parent_question_id)assert(bank.questions.some(p=>p.id===q.parent_question_id));const src=q.source,part=bank.source_parts[src.book_part];assert.equal(src.book_sha256,part.sha256);assert.equal(src.pdf_page,src.printed_page-part.printed_start+1);assert(src.pdf_page>=1&&src.pdf_page<=part.pdf_pages);assert(src.exercise);assert.equal(src.adaptation,q.parent_question_id?q.source_kind:q.type==='mcq'?'mcq':'transcription')}
  }
  assert.equal(Object.keys(bank.assets).length,diagrams);
  for(const a of Object.values(bank.assets)){assert(bankAssetUrl(a.src,classroom).endsWith(a.src));assert(a.src.endsWith('.png'));assert((await readFile(new URL(`../public/data/exam-banks/${folder}/${a.src}`,import.meta.url))).length>100);assert(a.crop_box.length===4)}
 });
 test(`${classroom}: valid math, distinct choices, canonical keys and complete written rubrics`,()=>{
  const math=[];for(const q of bank.questions){if(q.math_latex)math.push(q.math_latex);if(q.type==='mcq'){assert.equal(q.options.length,4);assert.equal(new Set(q.options.map(o=>o.text)).size,4,q.id);const answer=q.options.find(o=>o.id===q.answer.correct_option_id);assert.equal(answer.text,q.answer.correct_option_text);assert(q.answer.explanation);math.push(...q.options.filter(o=>o.math_latex).map(o=>o.math_latex))}else{assert.equal(q.parts.reduce((a,p)=>a+p.marks,0),10);for(const p of q.parts){assert(p.prompt&&p.answer.model_answer_and_marking&&p.workspace.height_mm>=15);if(p.answer.math_latex)math.push(p.answer.math_latex)}}}
  for(const expr of math){assert(!/[\x00-\x1f]/.test(expr),expr);assert.doesNotThrow(()=>katex.renderToString(expr,{throwOnError:true,strict:'ignore'}),expr)}
 });
 test(`${classroom}: topic fairness, shuffled canonical grading, one hour and isolated student storage`,()=>{
  const seen=new Set();for(let i=0;i<400;i++){const s=createTermMock(bank,1000000);assert(validTermMock(s,bank));assert.equal(s.deadline-s.startedAt,3600000);assert.equal(new Set(s.ids.map(id=>bank.questions.find(q=>q.id===id).learning_outcome_id)).size,20);for(const id of s.ids){seen.add(id);s.answers[id]=bank.questions.find(q=>q.id===id).answer.correct_option_id}assert.equal(gradeTermMock(s,bank),20)}assert.equal(seen.size,bank.mcq_count);
  const key=mockStorageKey('one',bank.mock_storage_namespace),other=mockStorageKey('two',bank.mock_storage_namespace),data=new Map([[key,'attempt'],[other,'keep'],[bankStorageKey('one',classroom),'draft']]);clearExamBankSession('one',{removeItem:k=>data.delete(k)});assert(!data.has(key));assert(data.has(other));assert(!data.has(bankStorageKey('one',classroom)));assert.deepEqual(examBankRoute(examBankPath(`LO${los}`,classroom)),{classroom,outcomeId:`LO${los}`,valid:true});assert.equal(examBankRoute(examBankPath(`LO${los+1}`,classroom)).valid,false);
 });
}
test('Grade 9 original-source traps: fraction 5f/2, third root-free branch, floors and arithmetic signs',async()=>{
 const b=await read('public/data/exam-banks/9g3-term1/index.json'),q=(lo,ex)=>b.questions.find(q=>q.learning_outcome_id===lo&&q.source.exercise===ex);
 assert.equal(q('LO03','2').math_latex,'44=t-72');assert.equal(q('LO03','2').answer.correct_option_text,'116');assert.equal(q('LO20','29').math_latex,'\\frac{5f}{2}-6=19');assert.equal(q('LO20','29').answer.correct_option_text,'10');
 assert(q('LO25','1').math_latex.includes('\\frac12'));assert(q('LO25','3').math_latex.includes('\\frac13'));assert.equal(q('LO16','18d').answer.correct_option_text,'-6');assert(q('LO16','18c').math_latex.endsWith('x=9.7'));assert.equal(q('LO16','18c').answer.correct_option_text,'16');assert(q('LO23','39').parts[0].answer.math_latex.includes('q\\in'));
 assert.equal(JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url))).questions.length,299);
});
