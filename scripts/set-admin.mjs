// Read a password from stdin without printing or saving the plaintext.
import {neon} from '@neondatabase/serverless';
import {hashPassword} from '../lib/admin-auth.js';
let input='';for await(const chunk of process.stdin)input+=chunk;
const username=process.argv[2],password=input.replace(/\r?\n$/,'');
if(!username||password.length<8)throw Error('Supply a username argument and a password of at least 8 characters on stdin.');
const sql=neon(process.env.DATABASE_URL),hash=await hashPassword(password);
await sql.transaction([sql`INSERT INTO admin_users(username,password_hash) VALUES(${username},${hash}) ON CONFLICT(username) DO UPDATE SET password_hash=EXCLUDED.password_hash,failed_attempts=0,locked_until=NULL`,sql`DELETE FROM admin_sessions WHERE username=${username}`]);
console.log('Admin account configured. Plaintext password was not stored.');
