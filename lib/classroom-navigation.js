import {classrooms,arrangeQuestions,outcomeFor} from './outcomes.js';
export function classroomRoute(hash){
 const parts=hash.replace(/^#\/?/,'').split('/');
 const classroom=parts[0]==='classrooms'&&classrooms.includes(parts[1])?parts[1]:null;
 return {classroom,manage:Boolean(classroom&&parts[2]==='manage'),outcomeId:classroom&&parts[2]==='outcomes'?parts[3]||null:null};
}
export function outcomePath(classroom,id){return `#/classrooms/${classroom}/outcomes/${id}`}
export function classroomGroups(classroom,questions,outcomes,assignments){
 const scoped=outcomes.filter(o=>o.classroom===classroom).sort((a,b)=>a.position-b.position);
 const ordered=arrangeQuestions(questions.filter(q=>(q.classroom||'10G3')===classroom),scoped,assignments);
 const groups=scoped.map(o=>({...o,questions:ordered.filter(q=>outcomeFor(q.id,scoped,assignments)?.id===o.id)}));
 const remaining=ordered.filter(q=>!outcomeFor(q.id,scoped,assignments));
 if(remaining.length)groups.push({id:'unassigned',title:'Additional practice · awaiting outcome assignment',titleAr:'تدريبات إضافية — بانتظار تعيين مخرج تعلم',bookPages:'',questions:remaining});
 return groups;
}
