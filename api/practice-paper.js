import {neon} from '@neondatabase/serverless';
import {getAdmin} from '../lib/admin-auth.js';
import {handleCors} from '../lib/cors.js';
export function createPaperHandler(getSql=()=>neon(process.env.DATABASE_URL)){
 return async(req,res)=>{res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');if(handleCors(req,res))return;if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'})}if(!process.env.DATABASE_URL)return res.status(503).json({error:'Paper submission database unavailable'});
 try{const query=new URL(req.url||'/','http://localhost').searchParams;const loginId=req.query?.loginId||query.get('loginId'),questionId=req.query?.questionId||query.get('questionId');if(typeof loginId!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(loginId)||typeof questionId!=='string'||questionId.length>150)return res.status(400).json({error:'Invalid paper request'});
 const sql=getSql(),admin=await getAdmin(req,getSql),token=(req.headers.authorization||'').replace(/^Bearer /,'');if(!admin){if(token!==loginId)return res.status(401).json({error:'Student or admin sign-in required'});const own=await sql`SELECT id FROM student_logins WHERE id=${loginId}::uuid AND created_at>now()-interval '24 hours'`;if(!own.length)return res.status(401).json({error:'Student session expired'})}
 const rows=await sql`SELECT name,mime,encode(content,'base64') AS data FROM practice_uploads WHERE login_id=${loginId}::uuid AND question_id=${questionId}`;if(!rows.length)return res.status(404).json({error:'Paper answer not found'});const file=rows[0];res.setHeader('Content-Type',file.mime);res.setHeader('Content-Disposition',`attachment; filename*=UTF-8''${encodeURIComponent(file.name)}`);return res.end(Buffer.from(file.data,'base64'));
 }catch{return res.status(503).json({error:'Paper answer could not be loaded'})}}
}
export default createPaperHandler();
