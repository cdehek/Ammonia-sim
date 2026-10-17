import {service} from './service.mjs';
let owner=null,lastPostMS=null;
self.onmessage=async ({data})=>{
 const receivedAt=performance.timeOrigin+performance.now();
 if(!owner)owner=service(data?.workerId,data?.sessionId);
 const r=await owner(data);r.transport={workerReceivedAt:receivedAt,workerPreparedAt:performance.timeOrigin+performance.now(),previousResponsePostMS:lastPostMS};
 const t=performance.now();self.postMessage(r);lastPostMS=performance.now()-t;
};
