import {doubleExactTex,pairOptionTex} from '../lib/right-triangle-diagrams.js';
import {readFile,writeFile} from 'node:fs/promises';import {randomUUID} from 'node:crypto';
const bp=new URL('../public/data/questions.json',import.meta.url),pp=new URL('../public/data/learning-outcomes.json',import.meta.url),bank=JSON.parse(await readFile(bp)),plan=JSON.parse(await readFile(pp)),R=String.raw;
const specs=[['geometric-mean','Find the geometric mean between two numbers','إيجاد الوسط الهندسي بين عددين','165 (Q1–6, Q11–14)','Q15'],['pythagorean','Use the Pythagorean Theorem and its converse','استعمال نظرية فيثاغورس وعكسها','171 (Q7–12); 172 (Q20–22); supplied Q1–6','Q16'],['special','Use the properties of 45°–45°–90° and 30°–60°–90° triangles','استعمال خصائص المثلثات ٤٥°–٤٥°–٩٠° و٣٠°–٦٠°–٩٠°','184 (Q19–25); 185 (Q33–38)','Q17'],['spatial','Find midpoints and distances in three-dimensional coordinates','إيجاد منتصف القطعة والمسافة في الإحداثيات الثلاثية','Supplied Q13–24 (page unspecified)','Q24']];
const os=specs.map(([key,title,titleAr,bookPages,assessmentItem],i)=>{let o=plan.outcomes.find(o=>o.classroom==='10A1'&&o.examWeek===10&&o.title===title);if(!o){o={id:randomUUID(),classroom:'10A1',examWeek:10,title,titleAr,bookPages,assessmentItem,position:i+1,targetCount:5};plan.outcomes.push(o)}return {key,o}}),made=[];
function save(q,key){made.push({q,outcomeId:os.find(o=>o.key===key).o.id});return q}
function add(key,id,en,ar,answer,answerAr,meta={}){const q={id:`10a1-w10-${id}`,classroom:'10A1',examWeek:10,exam:'10A1 · 10th week practice',topic:os.find(o=>o.key===key).o.title,type:'MCQ',marks:1,difficulty:'Standard',diagram:'none',image:'',prompt:en,promptAr:ar,answer,answerAr,options:[],optionsAr:[],...meta};if(q.type==='MCQ'){const shift=made.length%4,order=Array.from({length:4},(_,i)=>(i-shift+4)%4);q.options=order.map(i=>meta.options[i]);q.optionsAr=order.map(i=>(meta.optionsAr||meta.options)[i]);q.correctIndex=shift;for(const name of ['rightTriangleProblem','triangleClassification','specialTriangle'])if(q[name]?.choiceValues)q[name]={...q[name],choiceValues:order.map(i=>q[name].choiceValues[i])};}return save(q,key)}
for(const q of bank.questions.filter(q=>q.classroom==='10A1'&&q.examWeek===9&&q.sourcePage===165))save({...structuredClone(q),id:q.id.replace('w9','w10'),examWeek:10,exam:'10A1 · 10th week practice'},'geometric-mean');
const rows=[
 [1,[3,3],3*Math.sqrt(2),'hyp',['3','3','x'],[R`3\sqrt2`,'6','9',R`\sqrt6`]],
 [2,[9,12],15,'legB',['9','x','15'],['12','6','18','24']],
 [3,[25,60],65,'legB',['25','x','65'],['60','40','90','30']],
 [4,[1/3,4/9],5/9,'legA',['x','4/9','5/9'],[R`\frac{1}{3}`,R`\frac{1}{9}`,R`\frac{4}{9}`,'1']],
 [5,[16,33],Math.sqrt(1345),'hyp',['16','33','x'],[R`\sqrt{1345}`,'49','17',R`\sqrt{833}`]],
 [6,[11,Math.sqrt(663)],28,'legB',['11','x','28'],[R`\sqrt{663}`,'17','39',R`\sqrt{905}`]],
 [7,[8,15],17,'legB',['8','x','17'],['15','9','25','12']],
 [8,[24,45],51,'hyp',['24','45','x'],['51','69','21','48']],
 [9,[28,96],100,'hyp',['28','96','x'],['100','124','68','104']],
 [10,[5,12],13,'hyp',['5','12','x'],['13','17','7','15']],
 [11,[8,6],10,'legB',['8','x','10'],['6','2','18','12']],
 [12,[12,16],20,'legB',['12','x','20'],['16','8','32','24']]
];
for(const [n,legs,hyp,unknown,labels,choices]of rows){const value=unknown==='hyp'?hyp:unknown==='legA'?legs[0]:legs[1],numeric=[value,...choices.slice(1).map(s=>s.startsWith('\\sqrt')?Math.sqrt(Number(s.match(/\d+/)[0])):s.includes('frac')?Number(s.match(/\d+/g)[0])/Number(s.match(/\d+/g)[1]):Number(s))];const explanation=unknown==='hyp'?R`$x^2=${legs[0]}^2+${legs[1]}^2$. Thus $x=${choices[0]}$.`:R`Subtract the known leg's square from the hypotenuse's square: $x^2=${hyp}^2-${unknown==='legA'?legs[1]:legs[0]}^2$. Take the positive square root: $x=${choices[0]}$.`;
 add('pythagorean',`p171-q${n}`,`Find the positive value of x in the marked right triangle. ${n===6?'The hypotenuse is 28 and the marked leg is 11. ':''}Use the Pythagorean Theorem.`,`أوجد القيمة الموجبة لـ x في المثلث القائم المعلم. ${n===6?'طول الوتر 28 وطول الضلع المعلم 11. ':''}استعمل نظرية فيثاغورس.`,explanation,`نطبق نظرية فيثاغورس: مربع الوتر يساوي مجموع مربعي الضلعين القائمين، ثم نأخذ الجذر الموجب. $x=${choices[0]}$.`,{sourcePage:171,sourceQuestion:n,options:choices.map(s=>`$${s}$`),rightTriangleDiagram:{kind:'right',legs,labels},rightTriangleProblem:{legs,hyp,unknown,choiceValues:numeric}});
}
for(const [n,sides,tex,classification]of [[20,[Math.sqrt(5),Math.sqrt(12),Math.sqrt(13)],R`\sqrt5,\sqrt{12},\sqrt{13}`,'acute'],[21,[2,Math.sqrt(8),Math.sqrt(12)],R`2,\sqrt8,\sqrt{12}`,'right'],[22,[9,40,41],'9,40,41','right']]){
 const values=[classification,...['acute','right','obtuse','not-triangle'].filter(x=>x!==classification)],names={acute:['Acute triangle','مثلث حاد الزوايا'],right:['Right triangle','مثلث قائم الزاوية'],obtuse:['Obtuse triangle','مثلث منفرج الزاوية'],'not-triangle':['Not a triangle','لا تشكل مثلثاً']};const sq=sides.map(v=>Math.round(v*v));
 add('pythagorean',`p172-q${n}`,R`Can $${tex}$ be the side lengths of a triangle? If so, classify it as acute, obtuse, or right.`,R`هل يمكن أن تكون $${tex}$ أطوال أضلاع مثلث؟ إذا كان ممكناً، فصنّفه إلى حاد أو منفرج أو قائم.`,R`The triangle inequality holds. Compare squares: $${sq[0]}+${sq[1]}${classification==='right'?'=':'>'}${sq[2]}$. The triangle is ${classification}.`,R`تتحقق متباينة المثلث. وبمقارنة المربعات: $${sq[0]}+${sq[1]}${classification==='right'?'=':'>'}${sq[2]}$؛ لذا فهو مثلث ${classification==='right'?'قائم الزاوية':'حاد الزوايا'}.`,{sourcePage:172,sourceQuestion:n,options:values.map(v=>names[v][0]),optionsAr:values.map(v=>names[v][1]),triangleClassification:{sides,choiceValues:values}});
}
const special=[
 [184,19,[8,16],['8','16'],{kind:'right',legs:[8*Math.sqrt(3),8],labels:['8√3','x','y'],angleC:60,angleA:30}],
 [184,20,[10,20],['10','20'],{kind:'right',legs:[10,10*Math.sqrt(3)],labels:['x','10√3','y'],angleC:30,angleA:60}],
 [184,21,[15*Math.sqrt(3)/2,15/2],[R`\frac{15\sqrt3}{2}`,R`\frac{15}{2}`],{kind:'right',legs:[15/2,15*Math.sqrt(3)/2],labels:['y','x','15'],angleC:30}],
 [184,22,[17*Math.sqrt(3)/2,17/2],[R`\frac{17\sqrt3}{2}`,R`\frac{17}{2}`],{kind:'right',legs:[17/2,17*Math.sqrt(3)/2],labels:['y','x','17'],angleA:60}],
 [184,23,[24*Math.sqrt(3),48],[R`24\sqrt3`,'48'],{kind:'right',legs:[24,24*Math.sqrt(3)],labels:['24','x','y'],angleC:30}],
 [184,24,[14*Math.sqrt(3)/3,28*Math.sqrt(3)/3],[R`\frac{14\sqrt3}{3}`,R`\frac{28\sqrt3}{3}`],{kind:'right',legs:[14/Math.sqrt(3),14],labels:['x','14','y'],angleA:60}],
 [185,33,[13*Math.sqrt(2)/2,45],[R`\frac{13\sqrt2}{2}`,'45^\\circ'],{kind:'square',number:33}],
 [185,34,[3*Math.sqrt(2),6*Math.sqrt(2)],[R`3\sqrt2`,R`6\sqrt2`],{kind:'special34'}],
 [185,35,[3,1],['3','1'],{kind:'special35'}],
 [185,36,[5,10],['5','10'],{kind:'special36'}],
 [185,37,[6*Math.sqrt(3),3],[R`6\sqrt3`,'3'],{kind:'special37'}],
 [185,38,[45,12*Math.sqrt(2)],['45^\\circ',R`12\sqrt2`],{kind:'square',number:38}]
];
const doubleTex=doubleExactTex;
for(const [page,n,values,t,g]of special){const [x,y]=values,choices=[values,[y,x],[2*x,y],[x,2*y]],texts=[t,[t[1],t[0]],[doubleTex(t[0]),t[1]],[t[0],doubleTex(t[1])]],ex=n===35?'Use the 30°–60°–90° ratio to get hypotenuse 4; the hypotenuse projections are 3 and 1.':n===37?'The altitude theorem gives y=(3√3)²/9=3. The hypotenuse is 12, so x²=12×9=108.':'Use the ratio 1:1:√2 for a 45°–45°–90° triangle, or 1:√3:2 for a 30°–60°–90° triangle, matching sides to the marked angles.';
 add('special',`p${page}-q${n}`,`Find x and y in the diagram. Give exact values; any variable marked ° is an angle in degrees.`,`أوجد x وy في الرسم بالقيم الدقيقة. كل متغير معلم بالرمز ° يمثل زاوية بالدرجات.`,`${ex} Therefore $x=${t[0]}$ and $y=${t[1]}$.`,R`نستعمل النسبة $1:1:\sqrt2$ للمثلث $45^\circ,45^\circ,90^\circ$ أو $1:\sqrt3:2$ للمثلث $30^\circ,60^\circ,90^\circ$، مع مطابقة الأضلاع للزوايا. النتيجة $x=${t[0]}$ و$y=${t[1]}$.`,{sourcePage:page,sourceQuestion:n,options:texts.map(([a,b])=>pairOptionTex(a,b)),rightTriangleDiagram:g,specialTriangle:{expected:values,choiceValues:choices}});
}
add('special','p184-q25',R`A 40-foot escalator makes a $30^\circ$ angle with the horizontal. How high is the second floor above the first floor?`,R`سلم كهربائي طوله 40 قدماً يصنع زاوية $30^\circ$ مع الأفقي. ما ارتفاع الطابق الثاني عن الأول؟`,R`The height is opposite $30^\circ$, so it is half the hypotenuse: $40/2=20$ feet.`,R`الارتفاع يقابل زاوية $30^\circ$، لذا يساوي نصف الوتر: $40/2=20$ قدماً.`,{sourcePage:184,sourceQuestion:25,options:['$20$ ft','$40$ ft',R`$20\sqrt3$ ft`,R`$40\sqrt3$ ft`],optionsAr:['20 قدماً','40 قدماً',R`$20\sqrt3$ قدماً`,R`$40\sqrt3$ قدماً`],rightTriangleDiagram:{kind:'right',legs:[20,20*Math.sqrt(3)],labels:['height','horizontal','40'],angleC:30},specialTriangle:{expected:[20],choiceValues:[[20],[40],[20*Math.sqrt(3)],[40*Math.sqrt(3)]]}});
const pairs=[
 [13,[[-2,-4,-4],[4,2,0]],['K(-2,-4,-4)','L(4,2,0)'],'(1,-1,-2)'],
 [14,[[-1,-3,-6],[-1,5,10]],['W(-1,-3,-6)','Z(-1,5,10)'],'(-1,1,2)'],
 [15,[[3,3,4],[5,4,13]],['R(3,3,4)','V(5,4,13)'],R`(4,\frac72,\frac{17}{2})`],
 [16,[[4,6,-8],[0,0,0]],['A(4,6,-8)','B(0,0,0)'],'(2,3,-4)'],
 [17,[[8,7,11],[2,1,8]],['C(8,7,11)','D(2,1,8)'],R`(5,4,\frac{19}{2})`],
 [18,[[-1,-7,9],[5,-1,-6]],['T(-1,-7,9)','U(5,-1,-6)'],R`(2,-4,\frac32)`],
 [19,[[-5,-2,-1],[-1,0,3]],['P(-5,-2,-1)','Q(-1,0,3)'],'(-3,-1,1)','6'],
 [20,[[1,1,1],[-1,-1,-1]],['J(1,1,1)','K(-1,-1,-1)'],'(0,0,0)',R`2\sqrt3`],
 [21,[[3/5,0,4/5],[0,0,0]],[R`F(\frac35,0,\frac45)`,'G(0,0,0)'],R`(\frac3{10},0,\frac25)`,'1'],
 [22,[[1,-1,6],[1/5,-2/5,2]],['G(1,-1,6)',R`H(\frac15,-\frac25,2)`],R`(\frac35,-\frac7{10},4)`,R`\sqrt{17}`],
 [23,[[Math.sqrt(3),2,2*Math.sqrt(2)],[-2*Math.sqrt(3),4,4*Math.sqrt(2)]],[R`B(\sqrt3,2,2\sqrt2)`,R`C(-2\sqrt3,4,4\sqrt2)`],R`(-\frac{\sqrt3}{2},3,3\sqrt2)`,R`\sqrt{39}`],
 [24,[[6*Math.sqrt(3),4,4*Math.sqrt(2)],[4*Math.sqrt(3),5,Math.sqrt(2)]],[R`S(6\sqrt3,4,4\sqrt2)`,R`T(4\sqrt3,5,\sqrt2)`],R`(5\sqrt3,\frac92,\frac{5\sqrt2}{2})`,R`\sqrt{31}`]
];
for(const [n,points,names,midTex,distTex]of pairs){const midpoint=points[0].map((v,i)=>(v+points[1][i])/2),distance=Math.hypot(...points[0].map((v,i)=>points[1][i]-v));add('spatial',`coordinate-q${n}`,R`Given $${names[0]}$ and $${names[1]}$, find ${n<19?'the coordinates of midpoint M.':'the distance between the points and the coordinates of midpoint M.'} Show the three-dimensional formula and your working.`,R`للنقطتين $${names[0]}$ و$${names[1]}$، أوجد ${n<19?'إحداثيات منتصف القطعة M.':'المسافة بينهما وإحداثيات منتصف القطعة M.'} اكتب الصيغة في الفراغ وخطوات الحل.`,R`$M=(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2},\frac{z_1+z_2}{2})=${midTex}$. ${n>=19?R`Also $d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}=${distTex}$.`:''}`,R`نأخذ متوسط كل زوج من الإحداثيات: $M=(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2},\frac{z_1+z_2}{2})=${midTex}$. ${n>=19?R`والمسافة $d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}=${distTex}$.`:''}`,{type:'FRQ',marks:n<19?3:4,sourceQuestion:n,sourceReference:'Supplied three-dimensional coordinate exercises; page unspecified. Routed to confirmed FRQ outcome Q24.',responseParts:[{label:'Formula and substitution · الصيغة والتعويض'},...(n>=19?[{label:'Exact distance · المسافة الدقيقة'}]:[]),{label:'Midpoint coordinates · إحداثيات منتصف القطعة'}],spatial3D:{points,midpoint,...(n>=19?{distance}:{})}})}
for(const {q,outcomeId}of made){const old=bank.questions.find(x=>x.id===q.id);if(old&&JSON.stringify(old)!==JSON.stringify(q))throw Error(`Preserve teacher edits: ${q.id}`);if(!old)bank.questions.push(q);if(!plan.assignments.some(a=>a.question_id===q.id))plan.assignments.push({question_id:q.id,outcome_id:outcomeId,position:Math.max(0,...plan.assignments.filter(a=>a.outcome_id===outcomeId).map(a=>a.position))+1})}
for(const {o}of os)o.targetCount=plan.assignments.filter(a=>a.outcome_id===o.id).length;plan.assignmentSeedQuestionIds=[...new Set([...(plan.assignmentSeedQuestionIds||[]),...made.map(x=>x.q.id)])];bank.exams=bank.exams.filter(e=>!(e.classroom==='10A1'&&e.examWeek===10));bank.exams.push({classroom:'10A1',examWeek:10,title:'10th week practice',questions:made.length});await writeFile(bp,JSON.stringify(bank,null,2)+'\n');await writeFile(pp,JSON.stringify(plan,null,2)+'\n');console.log(`10A1 Week 10: ${made.length} questions (${made.filter(x=>x.q.type==='MCQ').length} MCQ, ${made.filter(x=>x.q.type==='FRQ').length} FRQ); outcomes ${os.map(x=>x.o.targetCount)}.`);
