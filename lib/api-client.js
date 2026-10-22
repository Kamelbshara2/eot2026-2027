const env=import.meta.env||{};
export function resolveApiUrl(path,{baseUrl=env.VITE_API_BASE_URL||'',appBase=env.BASE_URL||'/'}={}){
 if(!path.startsWith('/api/'))throw Error('Invalid API path');
 if(!baseUrl){if(appBase!=='/')throw Error('The student sign-in backend is not connected yet. Please contact your teacher.');return path}
 const url=new URL(baseUrl);
 if(url.username||url.password||url.search||url.hash||!['https:','http:'].includes(url.protocol)||url.protocol==='http:'&&!['localhost','127.0.0.1'].includes(url.hostname))throw Error('Invalid public backend URL');
 return url.origin+path;
}
export const requestApi=(path,options)=>fetch(resolveApiUrl(path),options);
