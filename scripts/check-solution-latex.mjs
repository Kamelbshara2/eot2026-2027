import fs from 'node:fs';
import {bankMath} from '../lib/exam-bank-math.js';
import {normalizeStudyMath} from '../lib/study-math.js';
let n=0,bad=[];
for(const c of ['9G3','10G3','10A1','11G','11A','12G','12A']){
 const d=JSON.parse(fs.readFileSync(`../public/data/study/${c}.json`));
 const all=[];
 for(const q of d.questions){
  for(const s of q.answer?.steps||[]) all.push([q.id,s.latex]);
  for(const p of q.parts||[]) for(const s of p.answer?.steps||[]) all.push([q.id,s.latex]);
  for(const o of q.options||[]) if(o.math_latex) all.push([q.id,o.math_latex]);
 }
 for(const [id,l] of all){ if(!l) continue; n++; const h=bankMath(normalizeStudyMath(l)); if(/katex-error|ParseError/.test(h)) bad.push([c,id,l.slice(0,90)]); }
}
console.log('rendered',n,'errors',bad.length); console.log(bad.slice(0,30).map(b=>b.join(' | ')).join('\n'));
