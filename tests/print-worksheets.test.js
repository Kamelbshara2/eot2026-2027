import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {worksheetPage,printableQuestion} from '../lib/print-worksheet.js';
import {blankQuadraticPlane,graphWorksheet} from '../lib/quadratic-worksheets.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url),'utf8'));
const seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url),'utf8'));
const frqs=bank.questions.filter(q=>q.classroom==='10G3'&&q.type==='FRQ');
test('10G3 has four extrema FRQs and six graph-solving FRQs in two separate outcomes',()=>{
 assert.equal(frqs.length,10);assert.equal(frqs.filter(q=>q.graphReading).length,4);assert.equal(frqs.filter(q=>q.graphing).length,6);
 const outcomes=seed.outcomes.filter(o=>o.position>=4&&o.classroom==='10G3'&&(o.examWeek??8)===8);assert.deepEqual(outcomes.map(o=>o.targetCount),[4,6]);
 for(const o of outcomes){const qs=seed.assignments.filter(a=>a.outcome_id===o.id).map(a=>frqs.find(q=>q.id===a.question_id));assert.equal(qs.length,o.targetCount);assert(qs.every(Boolean));}
 for(const q of frqs){assert(printableQuestion(q));assert(q.promptAr&&q.answerAr);assert.equal(q.options.length,0);assert(!q.id.startsWith('graphing-quadratic-'));}
});
test('extrema answers match the graphs, global domain/range, and both end behaviors',()=>{
 const qs=frqs.filter(q=>q.graphReading);assert.deepEqual(qs.map(q=>q.graphReading.coefficients),[[-4,0,1],[3,-6,4],[1,0,-4],[1,6,3]]);
 for(const q of qs){const [a,b,c]=q.graphReading.coefficients,h=(-b/(2*a))||0,k=a*h*h+b*h+c;assert.equal(q.marks,9);assert(q.answer.includes(a>0?`Minimum value: $${k}$`:`Maximum value: $${k}$`));assert(q.answer.includes(`at $x=${h}$`));assert(q.answer.includes('Domain: $(-\\infty,\\infty)$'));assert(q.prompt.includes('domain and range'));assert(q.answer.includes(a>0?'\\ge':'\\le'));}
});
test('page 711 equations have correct roots or no real roots, and proposed table points fit within their planes',()=>{
 const qs=frqs.filter(q=>q.graphing),solutions=[[],[-6,4],[-8],[],[-7],[1]];
 assert.deepEqual(qs.map(q=>q.graphing.coefficients),[[1,7,14],[1,2,-24],[1,16,64],[1,-5,12],[1,14,49],[1,-2,1]]);
 for(const [i,q]of qs.entries()){assert.equal(q.sourcePage,711);assert.equal(q.sourceQuestion,i+1);const g=q.graphing,[a,b,c]=g.coefficients,[xmin,xmax,ymin,ymax]=g.bounds;assert.equal(g.xs[2],-b/(2*a));for(const x of g.xs){const y=a*x*x+b*x+c;assert(x>=xmin&&x<=xmax&&y>=ymin&&y<=ymax)}for(const x of solutions[i])assert.equal(a*x*x+b*x+c,0);if(!solutions[i].length)assert(b*b-4*a*c<0);
 const online=graphWorksheet(q);assert.equal((online.match(/<tr/g)||[]).length,6);assert.equal((online.match(/<input/g)||[]).length,12);assert(!online.includes('value="'));}
});
test('paper worksheets never include keys, draft inputs or worked table values; every graphing table has five blank rows',()=>{
 for(const q of frqs){const html=worksheetPage({...q,answer:'SECRET MODEL ANSWER',answerAr:'SECRET ARABIC ANSWER'},{visual:q.graphReading?'<svg viewBox="0 0 500 465"></svg>':''});assert(!html.includes('SECRET'));assert(!/<input|<textarea|<select|<button/.test(html));assert(html.includes('Name / الاسم'));assert(html.includes('School / المدرسة'));assert(html.includes('print-working-lines'));
 if(q.graphing){assert.equal((html.match(/<tr/g)||[]).length,6);assert.equal((html.match(/<td><\/td>/g)||[]).length,10);assert(html.includes('Solutions of the equation')||html.includes('Solution(s)'));assert(html.includes('class="drawing"'));assert(/<g class="drawing"[^>]*><\/g>/.test(html))}
 else{for(const label of ['Domain','Range','Maximum/minimum','Vertex','Left end','Right end'])assert(html.includes(label));}}
});
test('empty Cartesian planes use equal physical grid-square spacing and keep curves blank',()=>{
 for(const q of frqs.filter(q=>q.graphing)){const svg=blankQuadraticPlane(q.graphing),coords=svg.match(/data-draw-bounds="([^"]+)"/)[1].split(',').map(Number),[left,top,right,bottom]=coords,[xmin,xmax,ymin,ymax]=q.graphing.bounds;assert(Math.abs((right-left)/((xmax-xmin)/q.graphing.xStep)-(bottom-top)/((ymax-ymin)/q.graphing.yStep))<1e-9);assert(svg.includes('viewBox="0 0 600 410"'));assert(svg.includes('class="drawing"'));assert(!/NaN|Infinity/.test(svg));}
});

test('every printed page bears the teacher watermark and MCQs never become worksheets',()=>{
 for(const q of bank.questions){
  if(q.type==='MCQ'){assert.equal(printableQuestion(q),false);assert.throws(()=>worksheetPage(q),/no printable FRQ/);continue}
  const html=worksheetPage(q);
  assert.equal((html.match(/class="question-watermark"/g)||[]).length,1);
  assert(html.includes('ألاستاذ كامل بشارة 0502837825'));
 }
});
