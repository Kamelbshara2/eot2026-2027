// Audio is unlocked from a student click. Playback remains subject to the LMS,
// browser autoplay/background policy and the device's sound/volume settings.
export function createFocusAlarm({enabled=false,makeContext=()=>{const Context=globalThis.AudioContext||globalThis.webkitAudioContext;return Context?new Context():null}}={}){
 let context=null,buffer=null,source=null,requested=false,disposed=false;
 const ready=()=>Boolean(enabled&&context?.state==='running'&&!disposed);
 async function arm(){if(!enabled||disposed)return false;try{context??=makeContext();if(!context)return false;if(context.state!=='running'&&context.state!=='closed'){let timeout;try{await Promise.race([context.resume(),new Promise(resolve=>{timeout=setTimeout(resolve,800)})])}finally{clearTimeout(timeout)}}if(!ready())return false;if(!buffer){const length=context.sampleRate;buffer=context.createBuffer(1,length,context.sampleRate);const samples=buffer.getChannelData(0);for(let i=0;i<length;i++){const t=i/context.sampleRate,phase=t%.3,envelope=phase<.2?Math.min(1,phase/.015,(.2-phase)/.025):0;samples[i]=.16*envelope*Math.sin(2*Math.PI*(t<.5?660:880)*t)}}return true}catch{return false}}
 async function start(){if(!enabled||disposed||!context)return false;requested=true;if(!await arm()||!requested||source)return ready();try{source=context.createBufferSource();source.buffer=buffer;source.loop=true;source.connect(context.destination);source.start();return true}catch{source=null;return false}}
 function stop(){requested=false;if(source){try{source.stop();source.disconnect()}catch{}source=null}}
 function close(){stop();disposed=true;try{context?.close()?.catch?.(()=>{})}catch{}}
 return {arm,start,stop,close,get ready(){return ready()},get playing(){return source!==null}};
}
