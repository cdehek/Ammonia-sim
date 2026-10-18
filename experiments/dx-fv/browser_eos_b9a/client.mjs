import {BACKEND,service} from './service.mjs';
import {same} from './values.mjs';
export class Client{
 constructor(mode='B',{test=false}={}){this.mode=mode;this.sessionId=crypto.randomUUID();this.workerId=crypto.randomUUID();this.sequence=0;this.pending=new Map();this.active=true;this.lastVersion=-1;this.lastDisplaySequence=-1;this.display=null;this.creationStart=performance.now();
 {const url=new URL('./worker.mjs',import.meta.url);url.searchParams.set('mode',mode);if(test)url.searchParams.set('test','1');this.worker=new Worker(url,{type:'module'});this.worker.onmessage=e=>this.receive(e.data);this.worker.onerror=e=>this.lose('Worker crash: '+e.message);this.worker.onmessageerror=()=>this.lose('Worker messageerror');}
 
 this.creationMS=performance.now()-this.creationStart;}
 request(type,args={}){if(!this.active)return Promise.reject(Error('Session lost/disposed'));if(this.pending.size>=8)return Promise.reject(Error('Backpressure limit'));
 const q={protocol:1,workerId:this.workerId,backendId:BACKEND,requestId:crypto.randomUUID(),sessionId:this.sessionId,sequence:++this.sequence,type,args};
 return this.send(q);}
 send(q){if(!this.active)return Promise.reject(Error('Session lost/disposed'));const prior=this.pending.get(q.requestId);if(prior)return same(prior.q,q)?prior.promise:Promise.reject(Error('Pending duplicate ID mismatch'));let entry;const promise=new Promise((resolve,reject)=>{entry={q,resolve,reject,start:performance.now()};entry.timer=setTimeout(()=>this.lose('Request deadline; in-flight acceptance unknown'),30000);this.pending.set(q.requestId,entry);
 const post=performance.now();if(this.worker)this.worker.postMessage(q);else this.owner(structuredClone(q)).then(r=>this.receive(structuredClone(r))).catch(e=>this.lose(String(e)));entry.postMS=performance.now()-post;});entry.promise=promise;return promise;}
 receive(r){if(!this.active||r.sessionId!==this.sessionId||r.workerId!==this.workerId||r.backendId!==BACKEND||r.protocol!==1)return false;
 const p=this.pending.get(r.requestId);if(!p||p.q.sequence!==r.sequence||p.q.type!==r.type)return false;
 clearTimeout(p.timer);this.pending.delete(r.requestId);
 const handling=performance.now(),receivedAt=performance.timeOrigin+handling;
 const newer=r.acceptedVersion>this.lastVersion||(r.acceptedVersion===this.lastVersion&&r.sequence>=this.lastDisplaySequence);
 if(newer){const v=r.result?.compact??r.result?.record;
 if(v&&r.success){this.display=v;this.displayStale=false;this.lastFault=v.lastFault??v.stop??null;this.lastVersion=r.acceptedVersion;this.lastDisplaySequence=r.sequence;}
 if(!r.success||r.fault){this.lastFault=r.fault??r.error;this.displayStale=true;this.lastVersion=r.acceptedVersion??this.lastVersion;this.lastDisplaySequence=r.sequence;}
 }
 p.resolve({...r,clientTiming:{roundtripMS:performance.now()-p.start,postMS:p.postMS,handlingMS:performance.now()-handling,workerCreationMS:this.creationMS,workerTransport:r.transport??null,requestDispatchUpperBoundMS:r.transport?r.transport.workerReceivedAt-(performance.timeOrigin+p.start):null,queueUpperBoundMS:r.transport?r.transport.workerPreparedAt-r.transport.workerReceivedAt-r.timing.serviceMS:null,responseDispatchUpperBoundMS:r.transport?receivedAt-r.transport.workerPreparedAt:null}});return true;}
 lose(reason){if(!this.active)return;this.active=false;this.lostReason=reason;this.displayStale=true;for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(Error(reason));}this.pending.clear();this.worker?.terminate();this.worker=null;this.owner=null;}
 terminate(){this.lose('Session terminated; only last received accepted state known');}
 async dispose(){try{return await this.request('dispose');}finally{this.lose('Session disposed');}}
}
