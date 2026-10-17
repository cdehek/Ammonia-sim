export function probe(type,args={},transfer=[]){return new Promise((resolve,reject)=>{
 const worker=new Worker(new URL('./probe-worker.mjs',import.meta.url),{type:'module'}),id=crypto.randomUUID();const timer=setTimeout(()=>{worker.terminate();reject(Error('Probe deadline'));},90000);
 worker.onerror=e=>{clearTimeout(timer);worker.terminate();reject(Error(e.message));};worker.onmessage=e=>{clearTimeout(timer);worker.terminate();resolve(e.data);};
 worker.postMessage({protocol:1,workerId:id,backendId:type==='c1'?'C1-table-synthetic':type==='b7'?'B7-gateA-subset':'B9-transport-test',requestId:id,sessionId:id,sequence:1,type,args},transfer);
});}
