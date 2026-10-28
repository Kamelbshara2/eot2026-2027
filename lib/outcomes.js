export const classrooms=['10A1','10G3','9G3'];
export function validateOutcome(input){
 if(!input||typeof input.id!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(input.id)||!classrooms.includes(input.classroom)||!Number.isInteger(input.revision)||input.revision<0)return null;
 const examWeek=input.examWeek??8,assessmentItem=typeof input.assessmentItem==='string'?input.assessmentItem.trim():'';
 if(!Number.isInteger(examWeek)||examWeek<1||examWeek>52||assessmentItem.length>80)return null;
 const title=typeof input.title==='string'?input.title.trim():'',titleAr=typeof input.titleAr==='string'?input.titleAr.trim():'',bookPages=typeof input.bookPages==='string'?input.bookPages.trim():'';
 if(!title||title.length>300||titleAr.length>1000||bookPages.length>300||!Number.isInteger(input.targetCount)||input.targetCount<1||input.targetCount>500||!Number.isInteger(input.position)||input.position<1||input.position>1000||!Array.isArray(input.questionIds)||input.questionIds.length>500||new Set(input.questionIds).size!==input.questionIds.length||!input.questionIds.every(id=>typeof id==='string'&&id.length>0&&id.length<=150))return null;
 return {...input,title,titleAr,bookPages,examWeek,assessmentItem};
}
export function arrangeQuestions(questions,outcomes,assignments){const byId=new Map(outcomes.map(o=>[o.id,o])),links=new Map(assignments.map(a=>[a.question_id,a]));const rank=q=>{const link=links.get(q.id),outcome=byId.get(link?.outcome_id);return [outcome?.position??Number.MAX_SAFE_INTEGER,outcome?.id||'',outcome?link.position:(q.position??9999),q.id]};return [...questions].sort((a,b)=>{const x=rank(a),y=rank(b);return x[0]-y[0]||x[1].localeCompare(y[1])||x[2]-y[2]||x[3].localeCompare(y[3])})}
export function outcomeFor(questionId,outcomes,assignments){const link=assignments.find(a=>a.question_id===questionId);return outcomes.find(o=>o.id===link?.outcome_id)||null}

// Add newly published outcome IDs without replacing teacher edits or restoring seen deletions.
export function mergeOutcomeSeeds(current,seed,seenIds=[]){
 const known=new Set([...seenIds,...current.outcomes.map(o=>o.id)]),added=seed.outcomes.filter(o=>!known.has(o.id)),addedIds=new Set(added.map(o=>o.id)),assigned=new Set(current.assignments.map(a=>a.question_id));
 // Publish new questions into existing outcomes once; a seen marker preserves later teacher unassignments.
 const published=new Set((seed.assignmentSeedQuestionIds||[]).filter(id=>!seenIds.includes(`question:${id}`)));
 const outcomes=[...current.outcomes,...added].map(o=>{
  const update=(seed.targetCountUpdates||[]).find(u=>u.outcomeId===o.id),next=seed.outcomes.find(s=>s.id===o.id);
  const untouched=o.lastOperation===o.id||!o.lastOperation&&(o.revision??1)<=1;
  return update&&update.from.includes(o.targetCount)&&untouched&&next&&['title','titleAr','bookPages','position'].every(k=>o[k]===next[k])?{...o,targetCount:next.targetCount}:o;
 });
 const available=new Set(outcomes.map(o=>o.id));
 return {outcomes,assignments:[...current.assignments,...seed.assignments.filter(a=>!assigned.has(a.question_id)&&(addedIds.has(a.outcome_id)||published.has(a.question_id)&&available.has(a.outcome_id)))]};
}
