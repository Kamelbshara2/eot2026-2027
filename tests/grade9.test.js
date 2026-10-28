import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {valid,validLinearGraph,validLinearGraphing,validRateTable} from '../lib/validation.js';
import {lineSegment,linearFunctionGraph,linearGraphWorksheet,rateTable} from '../lib/linear-worksheets.js';
import {worksheetPage,printableQuestion} from '../lib/print-worksheet.js';
const bank=JSON.parse(await readFile(new URL('../public/data/questions.json',import.meta.url),'utf8'));
const seed=JSON.parse(await readFile(new URL('../public/data/learning-outcomes.json',import.meta.url),'utf8'));
const qs=bank.questions.filter(q=>q.classroom==='9G3');
test('9G3 has a distinct 25-question exam and all questions are assigned to four completed outcomes',()=>{
 assert.equal(qs.length,25);assert.equal(qs.filter(q=>q.type==='FRQ').length,8);assert.equal(qs.filter(q=>q.type==='MCQ').length,17);
 assert.equal(bank.exams.find(e=>e.classroom==='9G3').questions,25);
 const outcomes=seed.outcomes.filter(o=>o.classroom==='9G3'&&(o.examWeek??8)===8);assert.deepEqual(outcomes.map(o=>o.targetCount),[12,4,5,4]);
 for(const o of outcomes){const assigned=seed.assignments.filter(a=>a.outcome_id===o.id);assert.equal(assigned.length,o.targetCount);assert(assigned.every(a=>qs.some(q=>q.id===a.question_id)))}
 for(const q of qs){assert(valid(q),q.id);assert(q.exam.includes('9G3'));assert(q.promptAr&&q.answerAr);assert.equal(seed.assignments.filter(a=>a.question_id===q.id).length,1);if(q.type==='MCQ'){assert.equal(q.options.length,4);assert.equal(q.optionsAr.length,4);assert.equal(new Set(q.options).size,4)}}
});
test('page 125 Q11–18 isolate the requested variables with one numerically valid option each',()=>{
 const formulas=qs.filter(q=>q.literalEquation);assert.deepEqual(formulas.map(q=>q.sourceQuestion),[11,12,13,14,15,16,17,18]);
 const fixtures=[
 ['$v=\\frac{u-z}{w}$',[4,22/3,36,1/4],v=>v*3+5-17],
 ['$c=\\frac{b-x}{d}$',[-4,4,36,20/3],c=>16-c*3-4],
 ['$g=\\frac{10j+9h}{f}$',[-3,132,33,2/66],g=>2*g-9*4-10*3],
 ['$m=\\frac{p-n}{10}$',[2.4,100,-1,1],m=>10*m-17+7],
 ['$t=\\frac{3(r-v)}{2}$',[12,16/3,27,17],t=>(2/3)*t+5-13],
 ['$v=\\frac{9(z-w)}{5}$',[25/3,27,41.4,33.4],v=>(5/9)*v+4-19],
 ['$a=\\frac{x-33}{10c}$',[5.3,40,2,70/220],a=>(10*a*2-73)/11+3],
 ['$f=\\frac{6g-10}{d}$',[13,128,-3/24,8],f=>(4*f+10)/6-7]
 ];
 for(const [i,q]of formulas.entries()){const [expected,values,residual]=fixtures[i];assert.equal(q.options[q.correctIndex],expected);const matching=values.map(v=>Math.abs(residual(v))<1e-9);assert.equal(matching.filter(Boolean).length,1);assert(matching[q.correctIndex]);assert.equal(q.sourcePage,125)}
});
test('all four source rate tables are truly linear and their interpretations have the right signs and scale',()=>{
 const tables=qs.filter(q=>q.rateTable);assert.equal(tables.length,4);const expected=[1/5,-6,-2/3,3/7];
 for(const [i,q]of tables.entries()){const rows=q.rateTable.rows,rates=rows.slice(1).map(([x,y],j)=>(y-rows[j][1])/(x-rows[j][0]));assert(rates.every(r=>Math.abs(r-expected[i])<1e-9));assert(rateTable(q).includes('<table'));assert.equal(q.sourcePage,221)}
 assert.deepEqual(tables[3].rateTable.rows,[[22,-4],[29,-1],[36,2],[43,5],[50,8]]);assert(tables[3].options[tables[3].correctIndex].includes('\\frac37'));
});
test('five slope graphs have only the function line and neutral grid/axes, with three original designs',()=>{
 const graphs=qs.filter(q=>q.linearGraph);assert.equal(graphs.length,5);assert.equal(graphs.filter(q=>q.sourceKind==='original').length,3);
 const slopes=[0,3/4,-2,2/3,2];assert.deepEqual(graphs.map(q=>q.linearGraph.coefficients[0]),slopes);
 for(const q of graphs){const g=q.linearGraph,[m,b]=g.coefficients,points=lineSegment(g.coefficients,g.bounds);assert.equal(points.length,2);assert.notDeepEqual(points[0],points[1]);for(const [x,y]of points)assert(Math.abs(m*x+b-y)<1e-8);for(const [x,y]of g.sourcePoints)assert(Math.abs(m*x+b-y)<1e-8);
 const svg=linearFunctionGraph(q);assert(svg.includes('class="function-line"'));assert(!/rise-run|auxiliary|orange|yellow|#ff[0-9a-f]{4}|NaN|Infinity/.test(svg));assert(!q.prompt.includes('y='));}
});
test('four page 215 FRQs use correct linear functions, five-point tables, and blank drawable planes',()=>{
 const graphs=qs.filter(q=>q.linearGraphing);assert.deepEqual(graphs.map(q=>q.sourceQuestion),[5,6,7,8]);assert.deepEqual(graphs.map(q=>q.linearGraphing.coefficients),[[-1,8],[-1,10],[.5,1],[.25,-2]]);
 for(const q of graphs){const g=q.linearGraphing,[m,b]=g.coefficients,[xmin,xmax,ymin,ymax]=g.bounds;assert.equal(q.sourcePage,215);for(const x of g.xs)assert(x>=xmin&&x<=xmax&&m*x+b>=ymin&&m*x+b<=ymax);const online=linearGraphWorksheet(q);assert.equal((online.match(/<tr/g)||[]).length,6);assert.equal((online.match(/<input/g)||[]).length,12);assert(!online.includes('axis of symmetry'));const paper=worksheetPage(q);assert.equal((paper.match(/<td><\/td>/g)||[]).length,10);assert(!paper.includes('axis of symmetry'));assert(paper.includes('y-intercept'));}
});
test('all FRQs are printable with complete word-problem text and both parts, without leaking model keys',()=>{
 assert.equal(bank.questions.filter(printableQuestion).length,52);
 const apps=qs.filter(q=>q.responseParts);assert.deepEqual(apps.map(q=>q.sourceQuestion),[19,20,21,22]);
 for(const q of apps){assert.equal(q.responseParts.length,2);const paper=worksheetPage({...q,answer:'SECRET KEY',answerAr:'SECRET ARABIC'});assert(!paper.includes('SECRET'));assert(paper.includes('(a)'));assert(paper.includes('(b)'));assert.equal((paper.match(/class="print-answer-box /g)||[]).length,2);assert(!/<textarea|<input|<select/.test(paper));}
 assert(worksheetPage(apps[2]).includes('Thomas'));assert(worksheetPage(apps[2]).includes('136'));assert(apps[0].answer.includes('14'));assert(apps[1].answer.includes('120'));assert(apps[2].answer.includes('=6'));assert(apps[3].answer.includes('2.5'));
});
test('new diagram validators reject malformed tables, invalid planes and mismatched source points',()=>{
 assert(!validRateTable({rows:[[1,3],[1,4]]}));assert(!validRateTable({rows:[[1,'bad'],[2,3]]}));const graph=qs.find(q=>q.linearGraph).linearGraph;assert(validLinearGraph(graph));assert(!validLinearGraph({...graph,coefficients:[0,100]}));assert(!validLinearGraph({...graph,coefficients:[1,10],bounds:[-5,5,-5,5],sourcePoints:undefined}));assert(!validLinearGraph({...graph,sourcePoints:[[0,0],[1,0]]}));assert(!validLinearGraphing({coefficients:[1,0],bounds:[0,0,0,0],xs:[0,1,2,3,4],xStep:0,yStep:1}));
});
