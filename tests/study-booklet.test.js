import {normalizeStudyMath} from '../lib/study-math.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import katex from 'katex';

for (const [classroom,count] of [['9G3',26],['10G3',25],['10A1',25]]) {
 test(classroom+' booklet contains complete source questions, bilingual rules, usable media and valid math',()=>{
  const b=JSON.parse(fs.readFileSync(new URL('../public/data/study/'+classroom+'.json',import.meta.url)));
  assert.equal(b.learning_outcomes.length,count);
  const ids=new Set(b.questions.map(q=>q.id));
  for(const lo of b.learning_outcomes) {
   assert(lo.rule_ar && lo.rule_summary);
   assert(lo.question_ids.length>=2);
   for(const id of lo.question_ids) assert(ids.has(id));
  }
  for(const q of b.questions) {
   for(const asset of q.diagram_asset_ids||[]) assert(fs.existsSync(new URL('../public/'+b.assets[asset].src,import.meta.url)));
   const formulas=[q.math_latex,...(q.options||[]).map(o=>o.math_latex),...(q.parts||[]).map(p=>p.answer?.math_latex)];
   for(const formula of formulas.filter(Boolean)) katex.renderToString(normalizeStudyMath(formula),{throwOnError:true,strict:'ignore'});
   if(q.type==='mcq')assert(q.options.some(o=>o.id===q.answer.correct_option_id));
   else assert(q.parts.every(p=>p.answer?.model_answer_and_marking));
  }
 });
}
