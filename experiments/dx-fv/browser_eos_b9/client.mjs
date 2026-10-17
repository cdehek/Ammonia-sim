import {BACKEND,service} from './service.mjs';
import {same} from './values.mjs';
export class Client{
 constructor(mode){this.mode=mode;this.sessionId=crypto.randomUUID();this.workerId=crypto.randomUUID();this.sequence=0;this.pending=new Map();this.active=true;this.lastVersion=-1;this.lastDisplaySequence=-1;this.display=null;this.creationStart=performance.now();
 if(mode==='worker'){this.worker=new Worker(new URL('./worker.mjs',import.meta.url),{type:'module'});this.worker.onmessage=e=>this.receive(e.data);this.worker.onerror=e=>this.lose('Worker crash: '+e.message);this.worker.onmessageerror=()=>this.lose('Worker messageerror');}
 else this.owner=service(this.workerId,this.sessionId);
 this.creationMS=performance.now()-this.creationStart;}
 request(type,args={}){if(!this.active)return Promise.reject(Error('Session lost/disposed'));if(this.pending.size>=8)return Promise.reject(Error('Backpressure limit'));
 const q={protocol:1,workerId:this.workerId,backendId:BACKEND,requestId:crypto.randomUUID(),sessionId:this.sessionId,sequence:++this.sequence,type,args};
 return this.send(q);}
 send(q){if(!this.active)return Promise.reject(Error('Session lost/disposed'));const prior=this.pending.get(q.requestId);if(prior)return same(prior.q,q)?prior.promise:Promise.reject(Error('Pending duplicate ID mismatch'));let entry;const promise=new Promise((resolve,reject)=>{entry={q,resolve,reject,start:performance.now()};entry.timer=setTimeout(()=>this.lose('Request deadline; in-flight acceptance unknown'),30000);this.pending.set(q.requestId,entry);
 const post=performance.now();if(this.worker)this.worker.postMessage(q);else this.owner(structuredClone(q)).then(r=>this.receive(structuredClone(r))).catch(e=>this.lose(String(e)));entry.postMS=performance.now()-post;});entry.promise=promise;return promise;}
 receive(r){if(!this.active||r.sessionId!==this.sessionId||r.workerId!==this.workerId||r.backendId!==BACKEND||r.protocol!==1)return false;
 const p=this.pending.get(r.requestId);if(!p||p.q.sequence!==r.sequence||p.q.type!==r.type)return false;
 clearTimeout(p.timer);this.pending.delete(r.requestId);
 const handling=performance.now(),receivedAt=performance.timeOrigin+handling;if(r.success&&r.result?.record&&(r.acceptedVersion>this.lastVersion||(r.acceptedVersion===this.lastVersion&&r.sequence>=this.lastDisplaySequence))){this.display=r.result.record;this.lastVersion=r.acceptedVersion;this.lastDisplaySequence=r.sequence;}
 p.resolve({...r,clientTiming:{roundtripMS:performance.now()-p.start,postMS:p.postMS,handlingMS:performance.now()-handling,workerCreationMS:this.creationMS,workerTransport:r.transport??null,requestDispatchUpperBoundMS:r.transport?r.transport.workerReceivedAt-(performance.timeOrigin+p.start):null,queueUpperBoundMS:r.transport?r.transport.workerPreparedAt-r.transport.workerReceivedAt-r.timing.serviceMS:null,responseDispatchUpperBoundMS:r.transport?receivedAt-r.transport.workerPreparedAt:null}});return true;}
 lose(reason){if(!this.active)return;this.active=false;this.lostReason=reason;for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(Error(reason));}this.pending.clear();this.worker?.terminate();this.worker=null;this.owner=null;}
 terminate(){this.lose('Session terminated; only last received accepted state known');}
 async dispose(){try{return await this.request('dispose');}finally{this.lose('Session disposed');}}
}
