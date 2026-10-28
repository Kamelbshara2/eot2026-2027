import {classrooms,arrangeQuestions,outcomeFor} from './outcomes.js';
export const examWeeks=[9,8];
export const weekOf=item=>item?.examWeek??8;
export const weekLabel=week=>week===9?'الأسبوع التاسع':'الأسبوع الثامن';
export function classroomRoute(hash){
 const parts=hash.replace(/^#\/?/,'').split('/');
 const classroom=parts[0]==='classrooms'&&classrooms.includes(parts[1])?parts[1]:null;
 const explicit=parts[2]==='weeks',supported=explicit&&examWeeks.includes(Number(parts[3]));
 const offset=explicit?4:2;
 // Historic outcome/management URLs and Week 8 exam links keep their original scope.
 const examWeek=supported?Number(parts[3]):parts[2]&&parts[2]!=='weeks'?8:9;
 return {classroom,examWeek,validWeek:!explicit||Boolean(supported),manage:Boolean(classroom&&parts[offset]==='manage'),outcomeId:classroom&&parts[offset]==='outcomes'?parts[offset+1]||null:null};
}
export function classroomPath(classroom,week=9){return `#/classrooms/${classroom}/weeks/${week}`}
export function outcomePath(classroom,id,week=8){return `${classroomPath(classroom,week)}/outcomes/${id}`}
export function classroomGroups(classroom,questions,outcomes,assignments,examWeek=8){
 const scoped=outcomes.filter(o=>o.classroom===classroom&&weekOf(o)===examWeek).sort((a,b)=>a.position-b.position);
 const ordered=arrangeQuestions(questions.filter(q=>(q.classroom||'10G3')===classroom&&weekOf(q)===examWeek),scoped,assignments);
 const groups=scoped.map(o=>({...o,questions:ordered.filter(q=>outcomeFor(q.id,scoped,assignments)?.id===o.id)}));
 const remaining=ordered.filter(q=>!outcomeFor(q.id,scoped,assignments));
 if(remaining.length)groups.push({id:'unassigned',examWeek,title:'Additional practice · awaiting outcome assignment',titleAr:'تدريبات إضافية — بانتظار تعيين مخرج تعلم',bookPages:'',questions:remaining});
 return groups;
}
