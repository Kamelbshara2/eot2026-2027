// Server-side validation; browser uploads never become executable HTML/SVG.
export const PAPER_LIMIT=2*1024*1024;
export function validatePaper(value){
 if(!value||typeof value.name!=='string'||!value.name.trim()||value.name.length>180||!['image/png','image/jpeg','image/webp','application/pdf'].includes(value.type)||!Number.isInteger(value.size)||value.size<1||value.size>PAPER_LIMIT||typeof value.data!=='string')return null;
 const prefix=`data:${value.type};base64,`;if(!value.data.startsWith(prefix))return null;const base64=value.data.slice(prefix.length);if(base64.length>Math.ceil(PAPER_LIMIT/3)*4||(base64.length%4!==0||!/^[A-Za-z0-9+/]*={0,2}$/.test(base64)))return null;
 const bytes=Buffer.from(base64,'base64');if(bytes.length!==value.size)return null;
 const signature=value.type==='application/pdf'?bytes.subarray(0,5).toString()==='%PDF-':value.type==='image/png'?bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])):value.type==='image/jpeg'?bytes[0]===255&&bytes[1]===216&&bytes[2]===255:bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP';
 return signature?{name:value.name.trim().replace(/[\\/\x00-\x1f\x7f]/g,'_'),type:value.type,size:value.size,base64}:null;
}
