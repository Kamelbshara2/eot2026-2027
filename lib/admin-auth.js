import {createHash,randomBytes,scrypt as scryptCallback,timingSafeEqual} from 'node:crypto';
import {promisify} from 'node:util';
const scrypt=promisify(scryptCallback);
export async function hashPassword(password){const salt=randomBytes(16).toString('hex');const digest=await scrypt(password,salt,64);return `scrypt:${salt}:${digest.toString('hex')}`}
export async function verifyPassword(password,stored){const [algorithm,salt,hex]=String(stored).split(':');if(algorithm!=='scrypt'||!salt||!hex||!/^[0-9a-f]{128}$/.test(hex))return false;const actual=await scrypt(password,salt,64);return timingSafeEqual(actual,Buffer.from(hex,'hex'))}
export const tokenHash=token=>createHash('sha256').update(token).digest('hex');
export function sessionToken(req){const header=req.headers.authorization||'';return /^Bearer [a-f0-9]{64}$/.test(header)?header.slice(7):null}
export async function getAdmin(req,getSql){const token=sessionToken(req);if(!token||!process.env.DATABASE_URL)return null;const rows=await getSql()`SELECT username FROM admin_sessions WHERE token_hash=${tokenHash(token)} AND expires_at>now()`;return rows[0]||null}
