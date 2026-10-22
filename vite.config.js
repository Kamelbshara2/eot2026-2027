import {defineConfig,loadEnv} from 'vite';
import handler from './api/questions.js';
import studentHandler from './api/student-logins.js';
import adminHandler from './api/admin.js';
import practiceHandler from './api/practice.js';
import outcomeHandler from './api/learning-outcomes.js';
import paperHandler from './api/practice-paper.js';
export default defineConfig(({mode})=>{const values=loadEnv(mode,process.cwd(),'');for(const name of ['DATABASE_URL','ADMIN_TOKEN'])if(values[name]&&!process.env[name])process.env[name]=values[name];return {base:process.env.VITE_BASE_PATH||'/',plugins:[{name:'local-question-api',configureServer(server){for(const [path,endpoint] of [['/api/questions',handler],['/api/student-logins',studentHandler],['/api/admin',adminHandler],['/api/practice',practiceHandler],['/api/learning-outcomes',outcomeHandler],['/api/practice-paper',paperHandler]])server.middlewares.use(path,async(req,res)=>{let body='';for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>4_000_000){res.statusCode=413;res.end();return}}req.body=body;res.status=code=>{res.statusCode=code;return res};res.json=value=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(value));return res};await endpoint(req,res)})}}]}});
