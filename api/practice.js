import {neon} from '@neondatabase/serverless';
import {handleCors} from '../lib/cors.js';
import {getAdmin} from '../lib/admin-auth.js';
export function validateResponse(input){
 if(!input||typeof input.questionId!=='string'||input.questionId.length>150||!Array.isArray(input.fields)||input.fields.length>40||!input.fields.every(f=>f&&typeof f.label==='string'&&f.label.length<=150&&typeof f.value==='string'&&f.value.length<=10000)||!Array.isArray(input.paths)||input.paths.length>100||!input.paths.every(d=>typeof d==='string'&&d.length<=50000&&/^[MLml0-9., eE+\-]*$/.test(d))||(input.selected!==null&&(!Number.isInteger(input.selected)||input.selected<0||input.selected>20)))return null;
 if(!input.fields.some(f=>f.value.trim())&&!input.paths.length&&input.selected===null)return null;
 if(JSON.stringify(input).length>200000)return null;
 return {questionId:input.questionId,fields:input.fields,paths:input.paths,selected:input.selected};
}
export function createPracticeHandler(getSql=()=>neon(process.env.DATABASE_URL)){
 return async(req,res)=>{res.setHeader('Cache-Control','no-store');if(handleCors(req,res))return;
 if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed'})}
 if(!process.env.DATABASE_URL)return res.status(503).json({error:'Practice database unavailable'});
 try{
 if(req.method==='GET'&&await getAdmin(req,getSql)){const sql=getSql();
  const students=await sql`SELECT l.id,l.name,l.school,l.grade,l.classroom,l.created_at,(SELECT count(*)::int FROM questions q WHERE NOT q.deleted AND COALESCE(q.data->>'classroom','10G3')=l.classroom) AS question_count,count(p.question_id)::int AS saved_count,count(*) FILTER(WHERE p.correct=true)::int AS correct_count,max(p.updated_at) AS last_activity FROM student_logins l LEFT JOIN practice_responses p ON p.login_id=l.id GROUP BY l.id ORDER BY l.created_at DESC LIMIT 100`;
  const attempts=await sql`SELECT p.login_id,p.question_id,p.response,p.correct,p.updated_at,q.data->>'topic' AS topic FROM practice_responses p JOIN questions q ON q.id=p.question_id WHERE p.login_id IN (SELECT id FROM student_logins ORDER BY created_at DESC LIMIT 100) ORDER BY p.updated_at DESC LIMIT 5000`;
  return res.json({students,attempts});
 }
 const header=req.headers.authorization||'',id=header.startsWith('Bearer ')?header.slice(7):'';
 if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id))return res.status(401).json({error:'Student sign-in required'});
 const sql=getSql();const logins=await sql`SELECT id,classroom FROM student_logins WHERE id=${id}::uuid AND created_at>now()-interval '24 hours'`;if(!logins.length)return res.status(401).json({error:'Student session expired. Please sign in again.'});
 if(req.method==='GET'){const attempts=await sql`SELECT question_id,response,correct,updated_at FROM practice_responses WHERE login_id=${id}::uuid`;return res.json({attempts})}
 if(!req.headers['content-type']?.startsWith('application/json'))return res.status(415).json({error:'JSON required'});
 let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid JSON'})}
 const data=validateResponse(input);if(!data)return res.status(400).json({error:'Enter an answer before saving'});
 const rows=await sql`SELECT data FROM questions WHERE id=${data.questionId} AND NOT deleted`;if(!rows.length)return res.status(404).json({error:'Question not found'});
 const q=rows[0].data;if((q.classroom||'10G3')!==logins[0].classroom)return res.status(403).json({error:'Question belongs to another classroom'});if(q.type==='MCQ'&&(data.selected===null||data.selected>=q.options.length))return res.status(400).json({error:'Select one option'});
 const correct=q.type==='MCQ'&&Number.isInteger(q.correctIndex)?data.selected===q.correctIndex:null;
 const response={fields:data.fields,paths:data.paths,selected:data.selected};
 await sql`INSERT INTO practice_responses(login_id,question_id,response,correct) VALUES(${id}::uuid,${data.questionId},${JSON.stringify(response)}::jsonb,${correct}) ON CONFLICT(login_id,question_id) DO UPDATE SET response=EXCLUDED.response,correct=EXCLUDED.correct,updated_at=now()`;
 return res.json({saved:true,correct});
 }catch{return res.status(503).json({error:'Practice was not confirmed saved. Please retry.'})}
 }
}
export default createPracticeHandler();
