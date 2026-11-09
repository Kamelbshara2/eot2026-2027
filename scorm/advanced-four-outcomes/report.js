import {grade,recordedScore,recordedAttempt,selected,correctBlank,scormTime} from './core.js';
export function reportResult(lms,s,data,elapsed){const raw=JSON.stringify(s);if(new TextEncoder().encode(raw).length>4096)return {ok:false,detailsAccepted:false};let ok=true,detailsAccepted=true;
 // Suspend after try 1 so the next LMS launch retains the same session for try 2.
 for(const [k,v]of Object.entries({'cmi.suspend_data':raw,'cmi.core.score.min':0,'cmi.core.score.max':100,'cmi.core.score.raw':recordedScore(s,data)*10,'cmi.core.session_time':scormTime(elapsed),'cmi.core.exit':s.attempts.length<2?'suspend':''}))if(!lms.set(k,v))ok=false;
 const interaction=(i,values)=>{for(const [suffix,value]of Object.entries(values))if(!lms.set(`cmi.interactions.${i}.${suffix}`,value))detailsAccepted=false};
 for(const a of s.attempts.filter(a=>a.finished)){
  selected(a,data).forEach((q,i)=>{const chosen=a.options[i].indexOf(a.answers[i]);interaction((a.n-1)*(data.frq.blanks.length+5)+i,{id:`try${a.n}-${q.id}`,type:'choice',weighting:2,'objectives.0.id':q.outcomeId,'correct_responses.0.pattern':String.fromCharCode(65+a.options[i].indexOf(q.correctIndex)),student_response:chosen<0?'':String.fromCharCode(65+chosen),result:a.answers[i]===q.correctIndex?'correct':'wrong'})});
  data.frq.blanks.forEach((b,i)=>interaction((a.n-1)*(data.frq.blanks.length+5)+4+i,{id:`try${a.n}-${data.frq.id}-${b.id}`,type:'fill-in',weighting:b.marks,'objectives.0.id':data.frq.outcomeId,'correct_responses.0.pattern':String(b.answer),student_response:a.blanks[i],result:correctBlank(a.blanks[i],b.answer,b.tolerance)?'correct':'wrong'}));
  interaction((a.n-1)*(data.frq.blanks.length+5)+4+data.frq.blanks.length,{id:`try${a.n}-student-number`,type:'fill-in',weighting:0,student_response:s.student.number,result:'neutral'});
 }
 if(!lms.set('cmi.comments',JSON.stringify({classroom:data.classroom,week:data.week,studentNumber:s.student.number,name:s.student.name,scorePolicy:'first-answered-attempt',countedAttempt:recordedAttempt(s)?.n||null,marks:recordedScore(s,data),outOf:10,tries:s.attempts.filter(a=>a.finished).map(a=>({n:a.n,score:grade(a,data),reason:a.reason,focusWarnings:a.warnings,questions:a.ids,order:a.order}))})))detailsAccepted=false;
 if(ok&&!lms.set('cmi.core.lesson_status','completed'))ok=false;
 if(!lms.commit())ok=false;
 return {ok,detailsAccepted};
}
