import {readFile,writeFile} from 'node:fs/promises';
const bankPath=new URL('../public/data/questions.json',import.meta.url),planPath=new URL('../public/data/learning-outcomes.json',import.meta.url);
const bank=JSON.parse(await readFile(bankPath)),plan=JSON.parse(await readFile(planPath));
const outcome=(classroom,page)=>plan.outcomes.find(o=>o.classroom===classroom&&o.examWeek===9&&o.bookPages.startsWith(String(page)));
const additions=[];
function add(classroom,page,number,en,ar,choices,answer,answerAr,extra={}){
 const q={id:`${classroom.toLowerCase()}-w9-designed-${page}-${number}`,classroom,examWeek:9,exam:'9th week practice',type:'MCQ',topic:outcome(classroom,page).title,difficulty:'Standard',marks:1,diagram:'none',image:'',prompt:en,promptAr:ar,options:choices,optionsAr:[...choices],correctIndex:0,answer,answerAr,sourceKind:'teacher-designed',sourceReference:`Teacher-designed supplementary practice aligned with page ${page}; not a numbered textbook question.`,...extra};
 const shift=number%4,order=Array.from({length:4},(_,i)=>(i-shift+4)%4);q.options=order.map(i=>q.options[i]);q.optionsAr=order.map(i=>q.optionsAr[i]);q.correctIndex=shift;
 if(q.linearChoices)q.linearChoices.choices=order.map(i=>q.linearChoices.choices[i]);
 if(q.squareChoices)q.squareChoices=order.map(i=>q.squareChoices[i]);
 if(q.problemData?.rootChoices)q.problemData.rootChoices=order.map(i=>q.problemData.rootChoices[i]);
 additions.push({q,outcomeId:outcome(classroom,page).id});return q;
}
for(const [i,b]of [-3,4,-2].entries()){
 const choices=[{kind:'line',m:0,b},{kind:'line',m:0,b:-b},{kind:'vertical',x:b},{kind:'line',m:1,b}];
 add('9G3',233,i+1,`Which graph represents $y=${b}$? Each grid square is 1 unit.`,`أي رسم يمثل $y=${b}$؟ كل مربع يمثل وحدة واحدة.`,choices.map(c=>c.kind==='vertical'?`$x=${c.x}$`:`$y=${c.m?`x${c.b<0?'-':'+'}${Math.abs(c.b)}`:c.b}$`),`The equation $y=${b}$ fixes the y-coordinate. Its graph is a horizontal line through $(0,${b})$, parallel to the x-axis, with slope 0.`,`المعادلة $y=${b}$ تثبت قيمة الصادات؛ لذا يمثلها مستقيم أفقي يمر بالنقطة $(0,${b})$ ويوازي محور السينات وميله صفر.`,{linearChoices:{bounds:[-5,5,-5,5],target:choices[0],choices}});
}
const sets=values=>values.map(v=>`$x=${v.join('\\text{ or }')}$`);
function roots(page,n,prompt,ar,coefficients,rootChoices,answer,answerAr,extra={}){return add('10G3',page,n,prompt,ar,sets(rootChoices),answer,answerAr,{problemData:{kind:page===722?'solve-factoring':page===730?'solve-square-root':'solve-completing-square',coefficients,rootChoices,...extra}})}
roots(722,1,'Solve $x^2-7x+12=0$ by factoring. Choose the complete solution set.','حل $x^2-7x+12=0$ بالتحليل. اختر مجموعة الحل الكاملة.',[1,-7,12],[[3,4],[-4,-3],[-3,4],[-4,3]],'$x^2-7x+12=(x-3)(x-4)$. By the Zero Product Property, $x=3$ or $x=4$.','نحلل: $x^2-7x+12=(x-3)(x-4)$. وبخاصية حاصل الضرب الصفري يكون $x=3$ أو $x=4$.');
roots(730,1,'Use the Square Root Property to solve $(x-3)^2=25$. Choose both solutions.','استعمل خاصية الجذر التربيعي لحل $(x-3)^2=25$. اختر الحلين.',[1,-6,-16],[[-2,8],[2,8],[-8,2],[-2,2]],'$x-3=\\pm5$, so $x=3\\pm5$. The two solutions are $x=-2$ and $x=8$.','$x-3=\\pm5$، ومنه $x=3\\pm5$. إذن الحلان $x=-2$ و$x=8$.');
roots(730,2,'Use the Square Root Property to solve $2x^2-18=0$. Choose the complete solution set.','استعمل خاصية الجذر التربيعي لحل $2x^2-18=0$. اختر مجموعة الحل الكاملة.',[2,0,-18],[[-3,3],[-9,9],[3],[-3]],'$2x^2=18$, so $x^2=9$ and $x=\\pm3$. Both signs are required.','$2x^2=18$، ومنه $x^2=9$، ولذلك $x=\\pm3$. يجب أخذ الإشارتين.');
roots(725,1,'Solve $x^2+6x+5=0$ by completing the square. Choose both solutions.','حل $x^2+6x+5=0$ بإكمال المربع. اختر الحلين.',[1,6,5],[[-5,-1],[1,5],[-3,3],[-5,1]],'$x^2+6x=-5$. Add $(6/2)^2=9$ to both sides: $(x+3)^2=4$. Thus $x+3=\\pm2$, giving $x=-5$ or $x=-1$.','$x^2+6x=-5$. نضيف $(6/2)^2=9$ للطرفين، فنحصل على $(x+3)^2=4$. إذن $x+3=\\pm2$، ومنه $x=-5$ أو $x=-1$.',{completion:{shift:3,rhs:4}});
roots(725,2,'Solve $x^2-4x-12=0$ by completing the square. Choose both solutions.','حل $x^2-4x-12=0$ بإكمال المربع. اختر الحلين.',[1,-4,-12],[[-2,6],[-6,2],[2,6],[-4,4]],'$x^2-4x=12$. Add $(-4/2)^2=4$ to both sides: $(x-2)^2=16$. Thus $x-2=\\pm4$, giving $x=-2$ or $x=6$.','$x^2-4x=12$. نضيف $(-4/2)^2=4$ للطرفين، فنحصل على $(x-2)^2=16$. إذن $x-2=\\pm4$، ومنه $x=-2$ أو $x=6$.',{completion:{shift:-2,rhs:16}});
for(const [number,b]of [[3,12],[4,-7]]){
 const h=b/2,c=h*h,values=[[c,h],[b*b,b],[c,-h],[b*b/16,b/4]];
 const binomial=t=>`(x${t<0?'-':'+'}${Math.abs(t)})^2`;
 add('10G3',725,number,`Which value of c and binomial square complete $x^2${b<0?'-':'+'}${Math.abs(b)}x+c$ correctly?`,`أي قيمة لـ c وصورة مربع ذي الحدين تكمل $x^2${b<0?'-':'+'}${Math.abs(b)}x+c$ بصورة صحيحة؟`,values.map(([c,h])=>`$c=${c},\\quad ${binomial(h)}$`),`Half of ${b} is ${h}. Squaring gives $c=(${h})^2=${c}$. Therefore $x^2${b<0?'-':'+'}${Math.abs(b)}x+${c}=${binomial(h)}$.`,`نصف ${b} هو ${h}، ومربعه $c=(${h})^2=${c}$. إذن $x^2${b<0?'-':'+'}${Math.abs(b)}x+${c}=${binomial(h)}$.`,{squareChoices:values,problemData:{kind:'complete-square',b,c,shift:h}});
}
for(const {q,outcomeId}of additions){const existing=bank.questions.findIndex(v=>v.id===q.id);if(existing<0)bank.questions.push(q);else if(JSON.stringify(bank.questions[existing])!==JSON.stringify(q))throw Error(`Preserve existing edits: ${q.id}`);if(!plan.assignments.some(a=>a.question_id===q.id))plan.assignments.push({question_id:q.id,outcome_id:outcomeId,position:Math.max(0,...plan.assignments.filter(a=>a.outcome_id===outcomeId).map(a=>a.position))+1})}
plan.targetCountUpdates=[{outcomeId:outcome('9G3',236).id,from:[3],to:9},{outcomeId:outcome('9G3',233).id,from:[1,2],to:5},{outcomeId:outcome('10G3',722).id,from:[2,4],to:5},{outcomeId:outcome('10G3',730).id,from:[3],to:5},{outcomeId:outcome('10G3',725).id,from:[1],to:5}];
plan.assignmentSeedQuestionIds=[...new Set([...(plan.assignmentSeedQuestionIds||[]),...additions.map(({q})=>q.id)])];
for(const o of plan.outcomes.filter(o=>o.examWeek===9)){const count=plan.assignments.filter(a=>a.outcome_id===o.id).length;if(count<5)throw Error(`Still short: ${o.id}`);o.targetCount=Math.max(o.targetCount,count)}
for(const exam of bank.exams.filter(e=>e.examWeek===9))exam.questions=bank.questions.filter(q=>q.classroom===exam.classroom&&q.examWeek===9).length;
await writeFile(bankPath,JSON.stringify(bank,null,2)+'\n');await writeFile(planPath,JSON.stringify(plan,null,2)+'\n');
console.log(`Added ${additions.length} aligned MCQs; all 10 Week 9 learning outcomes now have at least 5 questions.`);
