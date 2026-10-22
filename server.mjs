import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import questionsHandler from './api/questions.js';

const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.woff':'font/woff','.woff2':'font/woff2','.ttf':'font/ttf','.ico':'image/x-icon'};
export function createApp({root=resolve('dist'),api=questionsHandler}={}){
 return createServer(async(req,res)=>{
  res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');
  res.status=code=>{res.statusCode=code;return res};res.json=value=>{res.setHeader('Content-Type','application/json; charset=utf-8');res.end(JSON.stringify(value));return res};
  try{
   const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
   if(path==='/healthz'){res.setHeader('Cache-Control','no-store');return res.json({status:'ok'})}
   if(path==='/api/questions'||path==='/api/questions/'){
    let size=0,body=[];
    for await(const chunk of req){size+=chunk.length;if(size>4_000_000){res.status(413).json({error:'Question exceeds 4 MB'});return}body.push(chunk)}
    req.body=Buffer.concat(body).toString('utf8');return await api(req,res);
   }
   if(!['GET','HEAD'].includes(req.method)){res.setHeader('Allow','GET, HEAD');return res.status(405).json({error:'Method not allowed'})}
   const file=resolve(root,'.'+(path==='/'?'/index.html':path));
   if(!file.startsWith(root+sep))return res.status(404).json({error:'Not found'});
   let info;try{info=await stat(file)}catch{return res.status(404).json({error:'Not found'})}
   if(!info.isFile())return res.status(404).json({error:'Not found'});
   const bytes=await readFile(file);res.setHeader('Content-Type',types[extname(file)]||'application/octet-stream');res.setHeader('Content-Length',bytes.length);res.setHeader('Cache-Control',path.startsWith('/assets/')?'public, max-age=31536000, immutable':'no-cache');res.end(req.method==='HEAD'?undefined:bytes);
  }catch(error){if(!res.headersSent)res.status(error instanceof URIError?400:500).json({error:error instanceof URIError?'Invalid URL':'Request failed'});else res.end()}
 });
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 await stat(resolve('dist/index.html'));
 const port=Number(process.env.PORT||3000);const server=createApp();server.listen(port,'0.0.0.0',()=>console.log(`Forma listening on port ${port}`));
 for(const signal of ['SIGTERM','SIGINT'])process.on(signal,()=>{server.close(()=>process.exit(0));setTimeout(()=>process.exit(1),10000).unref()});
}
