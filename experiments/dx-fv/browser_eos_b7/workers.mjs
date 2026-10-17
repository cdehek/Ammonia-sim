export async function workers(artifacts,engine){
 const rows=[];let last=performance.now(),gaps=[];
 const timer=setInterval(()=>{const now=performance.now();gaps.push(now-last);last=now;},10);
 try{
  for(const id of ['rebuiltB4C','gateA']){
   const started=performance.now(),worker=new Worker(new URL('./worker.mjs',import.meta.url),{type:'module'});
   try{
    const result=await new Promise((resolve,reject)=>{
     const deadline=setTimeout(()=>reject(Error('B7 worker deadline')),120000);
     worker.onmessage=e=>{clearTimeout(deadline);resolve(e.data);};worker.onerror=e=>{clearTimeout(deadline);reject(Error(e.message));};worker.postMessage({identity:artifacts[id],engine});
    });
    if(!result.passed)throw Error(result.message);
    rows.push({id,latencyMS:performance.now()-started,result});
   }finally{worker.terminate();}
  }
 }finally{clearInterval(timer);}
 return {passed:true,rows,heartbeatIntervalMS:10,heartbeatGapsMS:gaps,maximumHeartbeatGapMS:Math.max(...gaps),desktopBrowserOnly:true};
}
