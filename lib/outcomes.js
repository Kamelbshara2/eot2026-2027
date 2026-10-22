export const classrooms=['10A1','10G3','9G3'];
export function validateOutcome(input){
 if(!input||typeof input.id!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(input.id)||!classrooms.includes(input.classroom)||!Number.isInteger(input.revision)||input.revision<0)return null;
 const title=typeof input.title==='string'?input.title.trim():'',titleAr=typeof input.titleAr==='string'?input.titleAr.trim():'',bookPages=typeof input.bookPages==='string'?input.bookPages.trim():'';
 if(!title||title.length>300||titleAr.length>1000||bookPages.length>300||!Number.isInteger(input.targetCount)||input.targetCount<1||input.targetCount>500||!Number.isInteger(input.position)||input.position<1||input.position>1000||!Array.isArray(input.questionIds)||input.questionIds.length>500||new Set(input.questionIds).size!==input.questionIds.length||!input.questionIds.every(id=>typeof id==='string'&&id.length>0&&id.length<=150))return null;
 return {...input,title,titleAr,bookPages};
}
export function arrangeQuestions(questions,outcomes,assignments){const byId=new Map(outcomes.map(o=>[o.id,o])),links=new Map(assignments.map(a=>[a.question_id,a]));const rank=q=>{const link=links.get(q.id),outcome=byId.get(link?.outcome_id);return [outcome?.position??Number.MAX_SAFE_INTEGER,outcome?.id||'',outcome?link.position:(q.position??9999),q.id]};return [...questions].sort((a,b)=>{const x=rank(a),y=rank(b);return x[0]-y[0]||x[1].localeCompare(y[1])||x[2]-y[2]||x[3].localeCompare(y[3])})}
export function outcomeFor(questionId,outcomes,assignments){const link=assignments.find(a=>a.question_id===questionId);return outcomes.find(o=>o.id===link?.outcome_id)||null}
