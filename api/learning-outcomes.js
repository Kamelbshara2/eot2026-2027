import {neon} from '@neondatabase/serverless';
import {randomUUID} from 'node:crypto';
import {getAdmin} from '../lib/admin-auth.js';
import {handleCors} from '../lib/cors.js';
import {validateOutcome} from '../lib/outcomes.js';
export async function loadOutcomeData(sql){const [outcomes,assignments]=await Promise.all([sql`SELECT id,classroom,exam_week AS "examWeek",assessment_item AS "assessmentItem",title,title_ar AS "titleAr",book_pages AS "bookPages",target_count AS "targetCount",position,revision FROM learning_outcomes WHERE NOT deleted ORDER BY classroom,position,id`,sql`SELECT a.question_id,a.outcome_id,a.position FROM outcome_questions a JOIN learning_outcomes o ON o.id=a.outcome_id WHERE NOT o.deleted ORDER BY a.outcome_id,a.position`]);return {outcomes,assignments}}
export function createOutcomeHandler(getSql=()=>neon(process.env.DATABASE_URL)){
 return async(req,res)=>{res.setHeader('Cache-Control','no-store');if(handleCors(req,res))return;if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed'})}
 try{
 if(req.method==='POST'&&!await getAdmin(req,getSql))return res.status(401).json({error:'Admin sign-in required'});
 if(!process.env.DATABASE_URL)return res.status(503).json({error:'Learning-outcome database is unavailable'});
 const sql=getSql();if(req.method==='GET')return res.json(await loadOutcomeData(sql));
 if(!req.headers['content-type']?.startsWith('application/json'))return res.status(415).json({error:'JSON required'});
 let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid JSON'})}
 const data=validateOutcome(input);if(!data)return res.status(400).json({error:'Check outcome title, pages, question count and question order.'});
 const {id,classroom,examWeek,assessmentItem,title,titleAr,bookPages,targetCount,position,revision,questionIds}=data,operation=randomUUID();
 const queries=[sql`SELECT pg_advisory_xact_lock(hashtext(${classroom}))`];
 if(input.action==='delete'){
  queries.push(sql`UPDATE learning_outcomes SET deleted=true,revision=revision+1,last_operation=${operation}::uuid WHERE id=${id}::uuid AND classroom=${classroom} AND revision=${revision} AND NOT deleted`,sql`DELETE FROM outcome_questions WHERE outcome_id=${id}::uuid AND EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${id}::uuid AND last_operation=${operation}::uuid)`);
 }else if(input.action==='save'){
  queries.push(sql`WITH requested AS (SELECT value AS id FROM jsonb_array_elements_text(${JSON.stringify(questionIds)}::jsonb)),eligible AS (SELECT 1 WHERE (SELECT count(*) FROM questions q JOIN requested r ON r.id=q.id WHERE NOT q.deleted AND COALESCE(q.data->>'classroom','10G3')=${classroom} AND COALESCE((q.data->>'examWeek')::integer,8)=${examWeek})=${questionIds.length} AND NOT EXISTS(SELECT 1 FROM outcome_questions a JOIN requested r ON r.id=a.question_id WHERE a.outcome_id<>${id}::uuid) AND ((${revision}=0 AND NOT EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${id}::uuid)) OR EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${id}::uuid AND classroom=${classroom} AND exam_week=${examWeek} AND revision=${revision} AND NOT deleted))) INSERT INTO learning_outcomes(id,classroom,exam_week,assessment_item,title,title_ar,book_pages,target_count,position,last_operation) SELECT ${id}::uuid,${classroom},${examWeek},${assessmentItem},${title},${titleAr},${bookPages},${targetCount},${position},${operation}::uuid FROM eligible ON CONFLICT(id) DO UPDATE SET assessment_item=EXCLUDED.assessment_item,title=EXCLUDED.title,title_ar=EXCLUDED.title_ar,book_pages=EXCLUDED.book_pages,target_count=EXCLUDED.target_count,position=EXCLUDED.position,last_operation=EXCLUDED.last_operation,revision=learning_outcomes.revision+1 WHERE learning_outcomes.revision=${revision} AND learning_outcomes.classroom=${classroom} AND learning_outcomes.exam_week=${examWeek} AND NOT learning_outcomes.deleted`,sql`DELETE FROM outcome_questions WHERE outcome_id=${id}::uuid AND EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${id}::uuid AND last_operation=${operation}::uuid)`,sql`INSERT INTO outcome_questions(question_id,outcome_id,position) SELECT r.value,${id}::uuid,r.ordinality::integer FROM jsonb_array_elements_text(${JSON.stringify(questionIds)}::jsonb) WITH ORDINALITY r(value,ordinality) WHERE EXISTS(SELECT 1 FROM learning_outcomes WHERE id=${id}::uuid AND last_operation=${operation}::uuid)`);
 }else return res.status(400).json({error:'Invalid action'});
 queries.push(sql`SELECT id,revision FROM learning_outcomes WHERE id=${id}::uuid AND last_operation=${operation}::uuid`);
 const result=await sql.transaction(queries);if(!result.at(-1).length)return res.status(409).json({error:'Outcome changed, or a question is unavailable, in another classroom or exam week, or already assigned elsewhere. Refresh and try again.'});
 return res.json({saved:true,...await loadOutcomeData(sql)});
 }catch{return res.status(503).json({error:'Learning-outcome changes were not confirmed saved. Please retry.'})}
 }
}
export default createOutcomeHandler();
