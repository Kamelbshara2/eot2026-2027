// Cross-origin access is allowed only from the configured public frontend origin.
export function handleCors(req,res){
 const origin=req.headers.origin;res.setHeader('Vary','Origin');
 if(origin){
  let sameHost=false;try{sameHost=new URL(origin).host===req.headers.host}catch{}
  const allowed=process.env.PUBLIC_APP_ORIGIN?.replace(/\/$/,'');
  if(!sameHost&&origin!==allowed){res.status(403).json({error:'Frontend origin is not allowed'});return true}
  res.setHeader('Access-Control-Allow-Origin',origin);
  res.setHeader('Access-Control-Allow-Methods','GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers','Content-Type, Authorization');
 }
 if(req.method==='OPTIONS'){res.status(204);res.end();return true}
 return false;
}
