import {selectQuestions,rich,bilingual,options,heading,examHeader,examFooter,writeExam} from './exam-layout.mjs';
import {blankQuadraticPlane} from '../lib/quadratic-worksheets.js';
import {similarityDiagram} from '../lib/similarity-diagram.js';
import {aaDiagram} from '../lib/aa-diagram.js';
import {frqTriangleDiagram} from '../lib/frq-triangle-diagram.js';

// A numbered, equal-unit coordinate plane. Curve equations never appear on reading graphs.
let serial=0;
function quadraticPlot(coefficients,bounds,cls,labelsEvery=1){
 const [a,b,c]=coefficients,[xmin,xmax,ymin,ymax]=bounds,u=24,left=38,top=25,w=(xmax-xmin)*u,h=(ymax-ymin)*u,right=left+w,bottom=top+h,X=x=>left+(x-xmin)*u,Y=y=>top+(ymax-y)*u,id=`exam-curve-${++serial}`;
 let grid='',labels='',path='',visible=[];
 for(let x=xmin;x<=xmax;x++){grid+=`<path d="M${X(x)} ${top}V${bottom}"/>`;if(x&&x%labelsEvery===0)labels+=`<text x="${X(x)}" y="${Y(0)+17}" text-anchor="middle">${x}</text>`}
 for(let y=ymin;y<=ymax;y++){grid+=`<path d="M${left} ${Y(y)}H${right}"/>`;if(y&&y%labelsEvery===0)labels+=`<text x="${X(0)-7}" y="${Y(y)+5}" text-anchor="end">${y}</text>`}
 for(let i=0;i<=1400;i++){const x=xmin+(xmax-xmin)*i/1400,y=a*x*x+b*x+c;path+=`${i?'L':'M'}${X(x).toFixed(2)} ${Y(y).toFixed(2)} `;if(y>=ymin&&y<=ymax)visible.push([X(x),Y(y)])}
 let arrows='';for(const [tip,near]of [[visible[0],visible[2]],[visible.at(-1),visible.at(-3)]]){if(!tip||!near)continue;const dx=tip[0]-near[0],dy=tip[1]-near[1],l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l;arrows+=`<path d="M${tip[0]-ux*9-uy*4} ${tip[1]-uy*9+ux*4}L${tip[0]} ${tip[1]}L${tip[0]-ux*9+uy*4} ${tip[1]-uy*9-ux*4}"/>`}
 return `<svg class="${cls}" viewBox="0 0 ${right+28} ${bottom+23}" role="img" aria-label="Quadratic curve on a numbered unit Cartesian grid"><defs><clipPath id="${id}"><rect x="${left}" y="${top}" width="${w}" height="${h}"/></clipPath></defs><rect x="${left}" y="${top}" width="${w}" height="${h}" fill="white" stroke="#a5b7be"/><g fill="none" stroke="#d1dce0" stroke-width=".8">${grid}</g><path d="M${left} ${Y(0)}H${right+8} M${X(0)} ${bottom}V${top-8}" stroke="#36505b" stroke-width="1.6" fill="none"/><g font-family="Arial,sans-serif" font-size="16" fill="#36505b">${labels}<text x="${right+12}" y="${Y(0)-6}">x</text><text x="${X(0)+8}" y="16">y</text><text x="${X(0)+5}" y="${Y(0)+17}">0</text></g><g clip-path="url(#${id})" fill="none" stroke="#16758c" stroke-width="2.7"><path d="${path}"/>${arrows}</g></svg>`;
}
const question=(q,n,body,cls='')=>`<section class="exam-question ${cls}" data-question-id="${q.id}" data-type="${q.type}">${heading(q,n)}${body}</section>`;
const box=(label,height='')=>`<div class="answer-box"${height?` style="min-height:${height}mm"`:''}><b>${rich(label)}</b><span></span></div>`;
const lines=n=>`<div class="working-lines">${'<i></i>'.repeat(n)}</div>`;
const blankTable=()=>`<table class="blank-table"><thead><tr><th>x</th><th>y</th></tr></thead><tbody>${Array.from({length:5},(_,i)=>`<tr${i===2?' class="axis-row"':''}><td></td><td></td></tr>`).join('')}</tbody></table>`;

const general=selectQuestions('10G3',['10g3-quadratic-graph-03','10g3-quadratic-description-28','10g3-factoring-09','10g3-extrema-frq-2','10g3-graphing-frq-2']);
const gm={slug:'grade-10-general-math-8th-week-2026-10-23',grade:'Grade 10 General',ar:'الصف العاشر العام',count:5,marks:general.reduce((n,q)=>n+q.marks,0),pages:3};
const [g1,g2,g3,g4,g5]=general;
const wrap=(meta,page,content,cls='')=>`<section class="exam-page ${cls}">${examHeader(page,meta)}${content}${examFooter(page,meta)}</section>`;
const graphChoices=`<div class="graph-choices">${g1.transformation.choices.map(([a,h,k],i)=>`<div class="graph-choice"><span class="choice-letter">${String.fromCharCode(65+i)}</span>${quadraticPlot([a,-2*a*h,a*h*h+k],[-4,4,-3,7],'choice-plot',2)}</div>`).join('')}</div>`;
const gp1=wrap(gm,1,question(g1,1,bilingual('Which graph represents the function? All four graphs use the same scale.','أي رسم يمثل الدالة؟ الرسوم الأربعة تستخدم المقياس نفسه.')+`<div class="formula">${rich('$$g(x)=(x-1)^2$$')}</div>`+graphChoices+'<p class="small-note">Each grid square = 1 unit · كل مربع = وحدة واحدة</p>')+question(g2,2,bilingual('Describe the transformation from the parent function $f(x)=x^2$. Choose one answer.','صف التحويل من الدالة الأم $f(x)=x^2$. اختر إجابة واحدة.')+`<div class="formula">${rich('$$g(x)=2(x-3)^2+8$$')}</div>`+options(g2),'transformation-question'));
const features=[
 'Axis of symmetry · محور التماثل [1]',
 'Vertex · الرأس [1]',
 'y-intercept · التقاطع مع محور الصادات [1]',
 'Domain · المجال [1]',
 'Range · المدى [1]',
 'Maximum/minimum value and type · القيمة القصوى ونوعها [1]',
 'Left end: $x\\to-\\infty$, $y\\to$ · الطرف الأيسر [1]',
 'Right end: $x\\to+\\infty$, $y\\to$ · الطرف الأيمن [1]'
];
const featureBoxes=features.map(label=>box(label,15)).join('')+`<div class="wide">${box('Where does the extremum occur? Interpret its meaning for all function values. · أين تحدث القيمة القصوى؟ فسّر معناها لجميع قيم الدالة. [1]',25)}</div>`;
const gp2=wrap(gm,2,question(g3,3,bilingual('Solve the equation. Choose the complete solution set.','حل المعادلة. اختر مجموعة الحل الكاملة.')+`<div class="formula">${rich('$$x^2-6x=27$$')}</div>`+options(g3),'factoring-question')+question(g4,4,bilingual('Read the graph and complete all nine response boxes. Use interval notation for domain and range.','اقرأ الرسم وأكمل خانات الإجابة التسع. اكتب المجال والمدى بصيغة الفترات.')+`<div class="feature-layout"><div>${quadraticPlot(g4.graphReading.coefficients,g4.graphReading.bounds,'feature-plot')}<p class="small-note">Each grid square = 1 unit.<br><span lang="ar" dir="rtl">كل مربع = وحدة واحدة.</span></p></div><div class="feature-boxes">${featureBoxes}</div></div>`,'features-question'));
const gp3=wrap(gm,3,question(g5,5,bilingual('Solve by graphing. Complete a table with five equally spaced x-values, with the axis of symmetry in the middle row. Plot the points and draw a smooth parabola. Read the x-intercepts to find the solutions.','حل بيانياً. أكمل جدولاً لخمس قيم للسينات بفواصل متساوية، بحيث يكون محور التماثل في الصف الأوسط. مثّل النقاط وارسم قطعاً مكافئاً أملس، ثم استنتج الحلول من تقاطعاته مع محور السينات.')+`<div class="formula big">${rich('$$x^2+2x-24=0$$')}</div><p class="function-line">Function to graph / الدالة المراد رسمها: ${rich('$y=$')} ____________________________</p><div class="graph-layout"><div><h3>Table of values [2 marks]<br>جدول القيم [درجتان]</h3>${blankTable()}<p class="small-note">Middle row: axis of symmetry.<br><span lang="ar" dir="rtl">الصف الأوسط عند محور التماثل.</span></p></div><div><div class="graph-label">Plot the points and draw the parabola. [2 marks]<br><span lang="ar" dir="rtl">مثّل النقاط وارسم القطع المكافئ. [درجتان]</span></div>${blankQuadraticPlane(g5.graphing).replace('font-size="11"','font-size="14"')}<p class="small-note">Each grid square / مقياس كل مربع: x = 1, y = 5.</p></div></div><div class="intercepts">${box('x-intercept(s) · التقاطع مع محور السينات [1 mark]',22)}${box('Solution(s) · حلول المعادلة [1 mark]',22)}</div><h3>Working / calculations · خطوات الحل والحساب</h3>${lines(1)}<p class="end-note">End of exam · نهاية الاختبار</p>`,'graphing-question'),'frq-page');

const advanced=selectQuestions('10A1',['10a1-similar-polygons-13','10a1-aa-similarity-2','10a1-similar-triangles-frq-5']);
const am={slug:'grade-10-advanced-math-8th-week-2026-10-23',grade:'Grade 10 Advanced',ar:'الصف العاشر المتقدم',count:3,marks:advanced.reduce((n,q)=>n+q.marks,0),pages:2};
const [a1,a2,a3]=advanced;
const ap1=wrap(am,1,question(a1,1,bilingual('The polygons are similar. Find the value of $x$. Match the corresponding sides using the angle markings.','المضلعان متشابهان. أوجد قيمة $x$، وحدد الأضلاع المتناظرة باستعمال علامات الزوايا.')+similarityDiagram(a1.similarityDiagram)+options(a1),'polygon-question')+question(a2,2,bilingual('Are the triangles similar? Choose the correct conclusion and reason. Use only the given information.','هل المثلثان متشابهان؟ اختر الاستنتاج والتعليل الصحيحين اعتماداً على المعطيات فقط.')+aaDiagram(a2.aaDiagram).replace('viewBox="0 0 1000 400"','viewBox="0 0 1000 320"')+options(a2),'aa-question'));
const ap2=wrap(am,2,question(a3,3,bilingual('Identify the similar triangles, state the vertex correspondence, and explain why they are similar. Then find $x$ using a proportion. Show your working.','حدد المثلثين المتشابهين وتناظر الرؤوس، وفسّر سبب تشابههما، ثم أوجد $x$ باستعمال التناسب موضحاً خطوات الحل.')+frqTriangleDiagram(a3.frqDiagram).replace('viewBox="0 0 1000 390"','viewBox="70 0 550 370"')+`<div class="triangle-responses"><div class="two-boxes">${box('(a) Similarity statement / vertex correspondence · عبارة التشابه وتناظر الرؤوس [1 mark]',27)}${box('(b) Reason for similarity · سبب التشابه [1 mark]',27)}</div><div class="proportion-box">${box('(c) Write a proportion and solve it. · اكتب تناسباً وحلّه. [2 marks]',37)}</div>${box('(d) Final value of $x$ · القيمة النهائية لـ $x$ [1 mark]',22)}</div><p class="end-note">End of exam · نهاية الاختبار</p>`,'triangle-question'));

const extraCss=`
.small-note{font-size:8pt;line-height:1.7;color:#40536b;margin:2mm 0}.exam-question h3{font-size:9pt;line-height:1.6;margin:2mm 0}.formula{margin:1mm 0 2mm}
.graph-choices{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3mm}.graph-choice{border:.6pt solid #b4c4cf;border-radius:2mm;padding:2mm 1mm;text-align:center}.graph-choice>.choice-letter{margin:0 auto 1mm}.choice-plot{width:100%;height:auto;display:block}
.transformation-question{margin-top:4mm}.transformation-question .option{font-size:8.5pt;min-height:23mm}.transformation-question .option-ar{font-size:8.3pt}
.factoring-question .options{grid-template-columns:repeat(4,1fr)}.factoring-question .option{padding:2mm 1.5mm}.factoring-question .option-ar{font-size:7.3pt}.factoring-question .choice-letter{width:4.5mm;height:4.5mm;font-size:7pt}
.features-question{margin-top:4mm}.feature-layout{display:grid;grid-template-columns:83mm 97mm;gap:6mm;align-items:start;margin-top:3mm}.feature-plot{width:83mm;height:auto;display:block}.feature-boxes{display:grid;grid-template-columns:1fr 1fr;gap:2mm}.feature-boxes .answer-box{padding:1.5mm 2mm;border-radius:1.5mm;font-size:7.7pt}.feature-boxes .answer-box>span{min-height:7mm}.feature-boxes .wide{grid-column:1/-1}.feature-boxes .wide .answer-box>span{min-height:12mm}
.graphing-question .bilingual{font-size:9.5pt}.graphing-question .graph-layout{margin-top:2mm}.function-line{font-size:9pt;line-height:1.7;margin:3mm 0}.axis-row td{border-top:1.1pt solid #5c748a;border-bottom:1.1pt solid #5c748a}.working-lines i{display:block;height:7mm;border-bottom:.4pt solid #bec9d2}.graphing-question .small-note{font-size:7.8pt}.graphing-question .plot-plane{width:132mm;margin-left:auto;margin-right:auto}
.similarity-figure,.aa-figure,.frq-triangle-figure{margin:2mm auto}.similarity-figure{width:136mm}.aa-figure{width:140mm}.similarity-figure svg,.aa-figure svg,.frq-triangle-figure svg{display:block;width:100%;height:auto}.similarity-figure figcaption,.aa-figure figcaption{display:none}.polygon-question .options{grid-template-columns:repeat(4,1fr)}.polygon-question .option{min-height:11mm}.aa-question{margin-top:3mm}.aa-question .option{font-size:8.2pt;min-height:22mm;align-items:flex-start}.aa-question .option-ar{font-size:8pt}.aa-question .choice-letter{margin-top:1mm}
.triangle-question{margin-top:4mm}.triangle-question .bilingual{font-size:10pt}.frq-triangle-figure{width:108mm;margin:4mm auto}.frq-triangle-figure figcaption{font-size:8pt;text-align:center;margin-top:1mm}.two-boxes{display:grid;grid-template-columns:1fr 1fr;gap:5mm}.proportion-box{margin:4mm 0}.triangle-responses{margin-top:4mm}.triangle-question .answer-box{font-size:9pt}
`;
await writeExam(gm,[gp1,gp2,gp3],extraCss);
await writeExam(am,[ap1,ap2],extraCss);
