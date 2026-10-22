import {neon} from '@neondatabase/serverless';
import {randomBytes} from 'node:crypto';
import {handleCors} from '../lib/cors.js';
import {getAdmin,sessionToken,tokenHash,verifyPassword} from '../lib/admin-auth.js';
export function createAdminHandler(getSql=()=>neon(process.env.DATABASE_URL)){
 return async(req,res)=>{res.setHeader('Cache-Control','no-store');if(handleCors(req,res))return;
 if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return res.status(405).json({error:'Method not allowed'})}
 if(!process.env.DATABASE_URL)return res.status(503).json({error:'Admin sign-in backend is unavailable'});
 try{
 const sql=getSql();if(req.method==='GET'){const user=await getAdmin(req,getSql);return user?res.json({admin:true,username:user.username}):res.status(401).json({admin:false})}
 if(!req.headers['content-type']?.startsWith('application/json'))return res.status(415).json({error:'JSON required'});
 let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid JSON'})}
 if(!input||JSON.stringify(input).length>2048)return res.status(400).json({error:'Invalid login request'});
 if(input.action==='logout'){const token=sessionToken(req);if(token)await sql`DELETE FROM admin_sessions WHERE token_hash=${tokenHash(token)}`;return res.json({admin:false})}
 const username=typeof input.username==='string'?input.username.trim():'',password=input.password;
 if(!username||username.length>100||typeof password!=='string'||password.length>256)return res.status(400).json({error:'Enter your username and password'});
 const users=await sql`SELECT username,password_hash,locked_until>now() AS locked FROM admin_users WHERE username=${username}`;
 const user=users[0];if(user?.locked)return res.status(429).json({error:'Too many attempts. Please try again in 15 minutes.'});
 if(!user||!await verifyPassword(password,user.password_hash)){if(user)await sql`UPDATE admin_users SET failed_attempts=failed_attempts+1,locked_until=CASE WHEN failed_attempts+1>=5 THEN now()+interval '15 minutes' ELSE NULL END WHERE username=${username}`;return res.status(401).json({error:'Incorrect username or password'})}
 await sql`UPDATE admin_users SET failed_attempts=0,locked_until=NULL WHERE username=${username}`;
 const token=randomBytes(32).toString('hex');await sql`INSERT INTO admin_sessions(token_hash,username,expires_at) VALUES(${tokenHash(token)},${username},now()+interval '8 hours')`;
 return res.json({admin:true,username,token});
 }catch{return res.status(503).json({error:'Admin sign-in could not be confirmed. Please try again.'})}
 }
}
export default createAdminHandler();
