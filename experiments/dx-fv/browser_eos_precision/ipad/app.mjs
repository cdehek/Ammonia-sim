const el=id=>document.getElementById(id);let record={schema:1,experimental:true,physicalIPadQualification:false,started:new Date().toISOString(),userAgent:navigator.userAgent,secureContext:isSecureContext,crossOriginIsolated,visibility:document.visibilityState,errors:[],offlinePreparation:null};
let worker,timer,running=false;
function show(text){el('status').textContent=text;el('results').textContent=JSON.stringify(record,null,2);}
window.addEventListener('error',e=>{record.errors.push({kind:'page',message:e.message});show('Page error recorded.');});
window.addEventListener('unhandledrejection',e=>{record.errors.push({kind:'promise',message:String(e.reason)});show('Promise error recorded.');});
el('offline').onclick=async()=>{try{
 if(!isSecureContext||!navigator.serviceWorker)throw Error('Offline restart requires a secure origin and Service Worker support. LAN HTTP does not qualify.');
 const r=await navigator.serviceWorker.register('./sw.js',{scope:'./'});await navigator.serviceWorker.ready;
 if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));
 const manifest=await (await fetch('./manifest.json')).json(),checks=[];
 for(const asset of manifest.runtimeAssets){const response=await fetch(asset);if(!response.ok)throw Error('Offline asset missing: '+asset);const data=await response.arrayBuffer(),expected=manifest.assets[asset];
  const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data)),x=>x.toString(16).padStart(2,'0')).join('');
  if(expected&&sha!==expected.sha256)throw Error('Asset digest mismatch: '+asset);checks.push({asset,bytes:data.byteLength,sha256:sha});}
 record.offlinePreparation={scope:r.scope,controller:!!navigator.serviceWorker.controller,checks,preparedAt:new Date().toISOString(),networkDisabledReloadTest:'Not performed by this button; record manually after a fresh offline restart.'};show('Assets verified and cached. Export this record, then test a fresh offline restart.');
}catch(e){record.errors.push({kind:'offline',message:String(e)});show('Offline preparation failed.');}};
el('run').onclick=async()=>{if(running)return;running=true;el('run').disabled=true;worker?.terminate();record={...record,device:el('device').value,operatorOS:el('os').value,requestedVersion:el('version').value,runStarted:new Date().toISOString(),onlineFlag:navigator.onLine,visibilityAtRun:document.visibilityState,jsHeapIfExposed:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null};
 const times=[],visibility=[];let last=performance.now();timer=setInterval(()=>{const now=performance.now();times.push(now-last);visibility.push(document.visibilityState);last=now;},50);
 worker=new Worker('./worker.mjs',{type:'module'});worker.onmessage=({data})=>{
  if(data.type==='progress'){show(data.message);return;}
  clearInterval(timer);running=false;el('run').disabled=false;
  record.workerResponsiveness={ticks:times.length,nominalIntervalMS:50,maxGapMS:Math.max(0,...times),medianGapMS:times.length?times.slice().sort((a,b)=>a-b)[Math.floor(times.length/2)]:null,hiddenTicks:visibility.filter(s=>s!=='visible').length,note:'Timers across startup and the whole bounded worker test; not a touch-latency or OS-memory measurement.'};
  if(data.type==='result'){record.result=data.result;show('Tests complete. Export evidence. Precision failures are preserved.');}
  else{record.errors.push({kind:'worker',message:data.error});show('Worker test failed; export the evidence.');}
  worker.terminate();
 };
 worker.onerror=e=>{clearInterval(timer);running=false;el('run').disabled=false;record.errors.push({kind:'worker-runtime',message:e.message});show('Worker runtime error.');worker.terminate();};
 worker.postMessage({version:record.requestedVersion});show('Worker starting…');
};
el('export').onclick=()=>{record.device=el('device').value;record.operatorOS=el('os').value;const blob=new Blob([JSON.stringify(record,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`ammonia-eos-precision-${record.requestedVersion||'startup'}-${Date.now()}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
window.ipadResearch={getRecord:()=>record,run:()=>el('run').click(),prepareOffline:()=>el('offline').click(),isRunning:()=>running};show('Ready. Prepare offline assets before disconnecting the network.');
