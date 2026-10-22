import {handleCors} from '../lib/cors.js';
import {neon} from '@neondatabase/serverless';
import {getAdmin} from '../lib/admin-auth.js';
export function validateStudent(input){
 if(!input||typeof input!=='object')return null;
 const {id,classroom,grade}=input;
 const name=typeof input.name==='string'?input.name.trim():'';
 const school=typeof input.school==='string'?input.school.trim():'';
 if(typeof id!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)||!['10A1','10G3','9G3'].includes(classroom)||grade!==(classroom==='9G3'?9:10)||name.length<2||name.length>100||school.length<2||school.length>150||/[\x00-\x1f\x7f]/.test(name+school))return null;
 return {id,name,school,grade,classroom};
}
export function createStudentHandler(getSql=()=>neon(process.env.DATABASE_URL)){
 return async(req,res)=>{
  res.setHeader('Cache-Control','no-store');if(handleCors(req,res))return;
  if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed'})}
  if(req.method==='GET'){try{if(!await getAdmin(req,getSql))return res.status(401).json({error:'Admin sign-in required'})}catch{return res.status(503).json({error:'Admin authorization unavailable'})}}
  let student;
  if(req.method==='POST'){
   if(!req.headers['content-type']?.toLowerCase().startsWith('application/json'))return res.status(415).json({error:'JSON required'});
   let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid JSON'})}
   if(Buffer.byteLength(JSON.stringify(input)??'')>8192)return res.status(413).json({error:'Sign-in data too large'});
   student=validateStudent(input);if(!student)return res.status(400).json({error:'Enter a valid name, school, grade and classroom.'});
  }
  if(!process.env.DATABASE_URL)return res.status(503).json({error:'Sign-in database is not configured. Please contact your teacher.'});
  try{
   const sql=getSql();
   if(req.method==='GET'){const rows=await sql`SELECT id,name,school,grade,classroom,created_at FROM student_logins ORDER BY created_at DESC LIMIT 100`;return res.json({logins:rows})}
   const {id,name,school,grade,classroom}=student;
   const rows=await sql`INSERT INTO student_logins(id,name,school,grade,classroom) VALUES(${id}::uuid,${name},${school},${grade},${classroom}) ON CONFLICT(id) DO UPDATE SET id=EXCLUDED.id WHERE student_logins.name=EXCLUDED.name AND student_logins.school=EXCLUDED.school AND student_logins.grade=EXCLUDED.grade AND student_logins.classroom=EXCLUDED.classroom RETURNING id,created_at`;
   if(!rows.length)return res.status(409).json({error:'Sign-in request changed. Close the form and try again.'});
   return res.status(201).json({login:rows[0]});
  }catch{return res.status(503).json({error:'Your sign-in was not confirmed. Please retry when the database is available.'})}
 }
}
export default createStudentHandler();
