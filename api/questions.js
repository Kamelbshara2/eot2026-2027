import { neon } from '@neondatabase/serverless';
import { timingSafeEqual } from 'node:crypto';
import {valid} from '../lib/validation.js';
export function authorized(header,expected){if(!expected||!header?.startsWith('Bearer '))return false;const a=Buffer.from(header.slice(7)),b=Buffer.from(expected);return a.length===b.length&&timingSafeEqual(a,b)}
export function createHandler(getSql=()=>neon(process.env.DATABASE_URL)){
return async function handler(req,res){res.setHeader('Cache-Control','no-store');if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed'})}
 if(req.method==='POST'&&!authorized(req.headers.authorization,process.env.ADMIN_TOKEN))return res.status(401).json({error:'Cloud editing key required'});
 if(!process.env.DATABASE_URL)return res.status(503).json({error:'Database not configured'});
 try{const sql=getSql();
 if(req.method==='GET'){const rows=await sql`SELECT id, data, revision, deleted FROM questions ORDER BY id`;return res.status(200).json({rows})}
 let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid JSON'})}
 if(!input||typeof input.id!=='string'||input.id.length>150||!Number.isSafeInteger(input.revision)||input.revision<0||(input.data!==null&&(!valid(input.data)||input.data.id!==input.id)))return res.status(400).json({error:'Invalid question'});
 if(Buffer.byteLength(JSON.stringify(input))>4_000_000)return res.status(413).json({error:'Question exceeds 4 MB'});
 const {id,data,revision}=input;let rows;
 if(revision===0)rows=await sql`INSERT INTO questions(id,data,revision,deleted) VALUES(${id},${JSON.stringify(data)}::jsonb,1,${data===null}) ON CONFLICT(id) DO NOTHING RETURNING id,data,revision,deleted`;
 else rows=await sql`UPDATE questions SET data=${JSON.stringify(data)}::jsonb, deleted=${data===null},revision=revision+1,updated_at=now() WHERE id=${id} AND revision=${revision} RETURNING id,data,revision,deleted`;
 if(!rows.length)return res.status(409).json({error:'Question changed on another device. Local changes retained.'});return res.status(200).json({row:rows[0]});
 }catch{return res.status(503).json({error:'Database unavailable. Local changes retained.'})}
}}
export default createHandler();
