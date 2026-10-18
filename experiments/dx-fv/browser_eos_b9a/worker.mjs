import {service} from './service.mjs';import {verifyHash} from './verification.mjs';
let owner=null,lastPostMS=null;const params=new URL(import.meta.url).searchParams,mode=params.get('mode')??'B';
self.onmessage=async({data})=>{const receivedAt=performance.timeOrigin+performance.now();try{
 if(!owner)owner=service(data?.workerId,data?.sessionId,{mode,test:params.get('test')==='1'});
 const r=await owner(data);
 if(mode==='A'&&data.args?.scientificHash&&r.success&&r.result.state&&r.result.record){const t=performance.now();await verifyHash({record:r.result.record,state:r.result.state},data.args.scientificHash);r.verificationMS=performance.now()-t;r.scientificHashVerifiedInsideOwner=true;}
 r.transport={workerReceivedAt:receivedAt,workerPreparedAt:performance.timeOrigin+performance.now(),previousResponsePostMS:lastPostMS};const t=performance.now();self.postMessage(r);lastPostMS=performance.now()-t;
 }catch(e){setTimeout(()=>{throw e;},0);}};
