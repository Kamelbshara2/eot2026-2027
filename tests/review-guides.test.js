import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {calculatorGuide} from '../lib/calculator-guide.js';
const load=async p=>JSON.parse(await readFile(new URL('../'+p,import.meta.url)));
for(const folder of ['9g3-term1','10g3-term1','10a1-term1']){
 const bank=await load(`public/data/exam-banks/${folder}/index.json`),baseline=await load(`content-imports/textbook-v1-inputs/${folder}.json`);
 test(`${folder}: original FRQs and givens are preserved; revisions have traceable parents`,()=>{
  for(const original of baseline.questions){const q=bank.questions.find(q=>q.id===original.id);assert(q);assert.equal(q.math_latex,original.math_latex);assert.deepEqual(q.diagram_asset_ids,original.diagram_asset_ids);if(q.type==='frq'){assert.deepEqual(q.parts,original.parts);assert.equal(q.instruction,original.instruction)}}
  for(const q of bank.questions.filter(q=>q.parent_question_id)){assert(['concept_application','example_variant'].includes(q.source_kind));assert(baseline.questions.some(p=>p.id===q.parent_question_id&&p.learning_outcome_id===q.learning_outcome_id));assert.equal(q.diagram_asset_ids.length,0)}
 });
 test(`${folder}: calculator guides are model-specific, safe to embed, and separate from mock questions`,async()=>{
  for(const q of bank.questions){const g=q.calculator;if(!g.applicable){assert.equal(calculatorGuide(q,'/bank/'),'');continue}assert.equal(g.model,'fx-991EX ClassWiz');assert.equal(g.illustration_kind,'instructional_key_guide_not_firmware');assert(g.steps.every(s=>s.title&&s.text&&Array.isArray(s.keys)));assert(g.steps[0].keys.includes('MENU'));assert(!JSON.stringify(g).includes('ES PLUS'));const html=calculatorGuide(q,'/bank/');assert(html.startsWith('<details'));assert(html.includes('not an official Casio emulator'));await access(new URL(`../public/data/exam-banks/${folder}/${g.image}`,import.meta.url));if(g.table){const tables=g.branch_tables||[g.table];for(const t of tables){assert.equal(t.x.length,q.grade===10?5:3);assert.equal(t.y.length,t.x.length);assert(t.y.every(Number.isFinite))}}}
  const mock=await readFile(new URL('../lib/term-mock-ui.js',import.meta.url),'utf8');assert(!mock.includes('calculatorGuide('));
 });
 test(`${folder}: provenance downloads reflect the active revision`,async()=>{const p=await load(`public/data/exam-banks/${folder}/provenance.json`);assert.equal(p.content_version,bank.content_version);assert.deepEqual(p.questions,bank.questions);assert.deepEqual(p.assets,bank.assets)});
}
test('calculator helper escapes imported text and rejects external illustration URLs',()=>{
 const q={display_number:'<script>',calculator:{applicable:true,model:'<img>',image:'https://example.org/x.png',steps:[{title:'<script>',keys:['<b>'],text:'<svg/onload=alert(1)>',expression:'<iframe>'}]}};
 const html=calculatorGuide(q,'/');assert(!html.includes('<script>'));assert(!html.includes('<img'));assert(!html.includes('<iframe>'));assert(html.includes('&lt;script&gt;'));
});
