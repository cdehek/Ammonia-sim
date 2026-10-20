export class Client {
 constructor(){
  this.session=crypto.randomUUID();this.seq=0;this.pending=new Map();this.metrics=[];this.postCosts={};this.history=[];this.latest=null;this.stale=false;this.status='new';this.closed=false;
  const start=performance.now();this.ready=new Promise((resolve,reject)=>{this.readyResolve=resolve;this.readyReject=reject;});
  const u=new URL('./worker.mjs',import.meta.url);u.searchParams.set('session',this.session);this.worker=new Worker(u,{type:'module'});this.constructMS=performance.now()-start;
  this.worker.onmessage=e=>{const handlerStart=performance.now(),r=e.data;
   if(r.kind==='ready'){this.readyMS=performance.now()-start;this.readyResolve(r);return;}
   if(r.kind==='post-cost'){this.postCosts[r.id]=r.postMS;return;}
   const p=this.pending.get(r.id);if(!p||r.session!==this.session||r.sequence!==p.q.sequence||r.type!==p.q.type)return;
   clearTimeout(p.timer);this.pending.delete(r.id);
   const accepted=this.receive(r),displayStart=performance.now();if(r.snapshot&&accepted&&document.getElementById('clock'))document.getElementById('clock').textContent=String(r.clock);const textAssignmentMS=performance.now()-displayStart;
   const roundtripMS=handlerStart-p.start,metric={type:r.type,id:r.id,roundtripMS,mainPostMS:p.postMS,dispatchToWorkerMS:r.receivedEpochMS-(performance.timeOrigin+p.start),returnDeliveryMS:performance.timeOrigin+handlerStart-r.sentEpochMS,handlerMS:performance.now()-handlerStart,textAssignmentMS,...r.timing};
   this.metrics.push(metric);p.resolve({...r,metric});
  };
  this.worker.onerror=e=>{e.preventDefault();this.lose('Worker error: '+e.message);};this.worker.onmessageerror=()=>this.lose('Worker decode failure');
 }
 receive(r){if(this.closed||r.session!==this.session||!Number.isSafeInteger(r.sequence)||r.sequence<=(this.lastSequence??0)||r.version<(this.version??0))return false;this.lastSequence=r.sequence;this.version=r.version;this.status=r.status;if(!r.success||r.status==='disposed')this.stale=!!this.latest;if(r.snapshot){this.latest=r.snapshot;this.stale=false;this.history.push(r.snapshot);this.history=this.history.slice(-8);}return true;}
 async request(type,args={},override={}){if(this.closed)throw Error('Worker lost/disposed');await this.ready;const q={protocol:1,session:this.session,id:crypto.randomUUID(),sequence:++this.seq,type,args,...override};return new Promise((resolve,reject)=>{const start=performance.now(),timer=setTimeout(()=>this.lose('External deadline; scientific result unknown'),90000);const p={q,resolve,reject,start,timer};this.pending.set(q.id,p);const t=performance.now();this.worker.postMessage(q);p.postMS=performance.now()-t;});}
 lose(reason='External worker loss; scientific result unknown'){if(this.closed)return;this.closed=true;this.worker.terminate();this.readyReject(Error(reason));for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(Error(reason));}this.pending.clear();this.status='lost';this.stale=!!this.latest;}
 async dispose(){if(this.closed)return null;const start=performance.now(),r=await this.request('dispose');this.closed=true;this.worker.terminate();r.terminateAndDisposeMS=performance.now()-start;return r;}
}
