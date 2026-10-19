import {service} from './service.mjs';
const p=new URL(location.href).searchParams,run=service(p.get('sessionId'),{test:p.get('test')==='1'});
self.onmessage=async e=>{const response=await run(e.data);response.sentEpochMS=performance.timeOrigin+performance.now();self.postMessage(response);};
