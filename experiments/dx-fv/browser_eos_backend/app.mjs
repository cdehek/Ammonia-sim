const el=id=>document.getElementById(id);let record=null;
el('run').onclick=async()=>{
 el('run').disabled=true;el('export').disabled=true;el('status').textContent='Running in worker…';
 const started=new Date().toISOString(),gaps=[];let previous=performance.now();
 const timer=setInterval(()=>{const now=performance.now();gaps.push(now-previous);previous=now;},50);
 const worker=new Worker('./worker.mjs',{type:'module'});
 try{
  const inputs=await (await fetch('../browser_eos_precision/inputs.json')).json();
  const {requests}=await (await fetch('../browser_eos/inputs.json')).json();
  const result=await new Promise((resolve,reject)=>{worker.onmessage=e=>resolve(e.data);worker.onerror=e=>reject(Error(e.message));worker.postMessage({build:el('build').value,inputs,requests});});
  record={started,finished:new Date().toISOString(),deviceLabel:el('device').value,userAgent:navigator.userAgent,
   physicalDeviceMustBeConfirmedByOperator:true,visibility:document.visibilityState,navigatorOnline:navigator.onLine,
   workerMaxTimerGapMS:Math.max(0,...gaps),result};
  el('status').textContent=JSON.stringify({ok:result.ok,build:result.build,init:result.performance?.init,linearMemory:result.performance?.linearMemory,error:result.error,workerMaxTimerGapMS:record.workerMaxTimerGapMS},null,2);
 }catch(err){record={started,failed:new Date().toISOString(),error:String(err)};el('status').textContent=String(err);}
 finally{clearInterval(timer);worker.terminate();el('run').disabled=false;el('export').disabled=false;}
};
el('export').onclick=()=>{
 const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)+'\n'],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='ammonia-b1-'+Date.now()+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
el('offline').onclick=async()=>{
 try{
  const manifest=await (await fetch('./offline-manifest.json',{cache:'no-store'})).json();
  for(const [path,hash] of Object.entries(manifest)){
   const response=await fetch(path,{cache:'no-store'});if(!response.ok)throw Error(path+' HTTP '+response.status);
   const bytes=await response.arrayBuffer(),digest=await crypto.subtle.digest('SHA-256',bytes);
   const actual=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');if(actual!==hash)throw Error('Hash mismatch: '+path);
  }
  await navigator.serviceWorker.register('./sw.js');await navigator.serviceWorker.ready;
  if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));
  el('status').textContent='All asset hashes verified; service worker controls this page. Disconnect the network and stop the static origin, then reopen this exact URL.';
 }catch(err){el('status').textContent='Offline preparation failed: '+String(err);}
};
