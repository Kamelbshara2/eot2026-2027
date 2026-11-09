import {readFile,writeFile} from 'node:fs/promises';
import {Calculator} from '../../public/vendor/fx991ce/src/calc/calculator.js';
import {MODES} from '../../public/vendor/fx991ce/src/calc/modes/index.js';
const data=JSON.parse(await readFile(new URL('../../public/data/study/calculator-support.json',import.meta.url)));
const report={arithmetic:0,tableValues:0,quadratics:0,solve:0,failed:[]};
const close=(a,b)=>Number.isFinite(a)&&Math.abs(a-b)<=2e-9*Math.max(1,Math.abs(b));
function run(keys){const c=new Calculator({modes:MODES,storage:null});c.setup.angle='deg';c.setup.eqComplex=false;for(const k of keys)c.press(k);return c;}
function value(c){return Number(c.top.result?.value?.d?.toString());}
for(const bank of Object.values(data.classes))for(const [id,g] of Object.entries(bank.questions)){
 try{
  for(const [index,op] of g.operations.entries()){
   const c=run(op.keys), got=value(c),expected=Number(op.decimal);
   if(!close(got,expected))report.failed.push({id,index,input:op.input,got:String(got),expected,screen:c.top.constructor.name});
   report.arithmetic++;
  }
  for(const t of g.tables)for(const row of t.rows){const got=value(run(row.keys));if(!close(got,Number(row.y)))report.failed.push({id,table:t.expression,x:row.x,got});report.tableValues++;}
  if(g.role==='quadratic'){
   const c=run(g.keys);const [a,b,d]=g.coefficients.map(Number);const roots=c.top.items?.slice(0,Number(g.discriminant)===0?1:2).map(x=>Number(x.value?.d?.toString()));
   if(Number(g.discriminant)<0){if(c.top.constructor.name!=='Message')report.failed.push({id,screen:c.top.constructor.name});}
   else if(!roots?.length || roots.some(x=>!close(a*x*x+b*x+d,0)))report.failed.push({id,roots,screen:c.top.constructor.name});
   report.quadratics++;
  }
  if(g.role==='solve'){
   const c=run(g.keys);const got=Number(c.top.x?.d?.toString());
   const expected=g.checks.map(x=>x.x); // These generated examples all have rational roots.
   const rational=s=>{const m=/^(-?)\\frac\{(\d+)\}\{(\d+)\}$/.exec(s);return m?(m[1]?-1:1)*Number(m[2])/Number(m[3]):Number(s);};
   if(c.top.constructor.name!=='SolveResult'||!expected.some(x=>close(got,rational(x))))report.failed.push({id,got,expected,screen:c.top.constructor.name});
   report.solve++;
  }
 }catch(e){report.failed.push({id,error:e.message});}
}
await writeFile(new URL('../../content-imports/calculator-key-validation.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));if(report.failed.length)process.exitCode=1;
