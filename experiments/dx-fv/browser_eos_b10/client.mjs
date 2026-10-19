import {BACKEND,SOURCE} from './snapshot.mjs';
export class DisplayState{
 constructor(sessionId){this.sessionId=sessionId;this.sequence=0;this.version=null;this.snapshot=null;this.status='initializing';this.stale=false;this.history=[];this.fault=null;this.clockSeconds=null;this.failureRange=null;this.currentStateKnown=true;}
 receive(r){
  if(r.protocol!==1||r.sessionId!==this.sessionId||r.backendId!==BACKEND||r.sequence<=this.sequence||(this.version!==null&&r.acceptedVersion!==null&&r.acceptedVersion<this.version))return false;
  if(r.snapshot&&(r.snapshot.sessionId!==this.sessionId||r.snapshot.backendId!==BACKEND||r.snapshot.acceptedVersion!==r.acceptedVersion||r.snapshot.clockSeconds!==r.clockSeconds))return false;
  this.sequence=r.sequence;this.version=r.acceptedVersion;this.status=r.status;this.clockSeconds=r.clockSeconds;
  if(!r.success){this.failureRange=r.requestRange;this.stale=!!this.snapshot;this.fault=r.fault||r.error;return true;}
  if(r.snapshot){this.snapshot=r.snapshot;this.failureRange=null;this.stale=false;this.fault=null;if(!this.history.some(s=>s.acceptedVersion===r.snapshot.acceptedVersion)){this.history.push(r.snapshot);this.history=this.history.slice(-8);}}
  if(r.status==='disposed')this.stale=!!this.snapshot;
  return true;
 }
}
export class Client{
 constructor(onchange=()=>{},{test=false,timeoutMS=30000}={}){
  this.sessionId=crypto.randomUUID();this.view=new DisplayState(this.sessionId);this.sequence=0;this.pending=new Map();this.onchange=onchange;this.metrics=[];this.closed=false;this.timeoutMS=timeoutMS;
  const u=new URL('./worker.mjs',import.meta.url);u.searchParams.set('sessionId',this.sessionId);if(test)u.searchParams.set('test','1');
  this.worker=new Worker(u,{type:'module'});this.worker.onmessage=e=>this.receive(e.data);this.worker.onerror=e=>{e.preventDefault();this.lose(e.message||'Worker error');};this.worker.onmessageerror=()=>this.lose('Worker communication decode failure');
 }
 receive(r){
  if(!r.source||Object.keys(SOURCE).some(k=>r.source[k]!==SOURCE[k])){this.lose('Scientific source identity mismatch');return false;}
  const p=this.pending.get(r.requestId);if(!p||r.sessionId!==this.sessionId||r.backendId!==BACKEND||r.type!==p.q.type||r.sequence!==p.q.sequence)return false;
  clearTimeout(p.timer);this.pending.delete(r.requestId);const received=performance.now();r.delivery={roundtripMS:received-p.start,transferAndDispatchMS:performance.timeOrigin+received-r.sentEpochMS};this.metrics.push({type:r.type,timing:r.timing,delivery:r.delivery});
  if(this.metrics.length>512)this.metrics.shift();this.view.receive(r);this.onchange(this.view);p.resolve(r);return true;
 }
 request(type,args={}){
  if(this.closed||this.disposing&&type!=='dispose')return Promise.reject(Error('Lost, disposing or disposed session'));
  if(this.pending.size>=8)return Promise.reject(Error('Pending command limit'));
  if(type==='advance'&&[...this.pending.values()].some(p=>p.q.type==='advance'))return Promise.reject(Error('Physics advance already pending'));
  const q={protocol:1,backendId:BACKEND,sessionId:this.sessionId,requestId:crypto.randomUUID(),sequence:++this.sequence,type,args};
  return new Promise((resolve,reject)=>{const start=performance.now(),timer=setTimeout(()=>this.lose('Worker deadline; in-flight state unknown'),this.timeoutMS);this.pending.set(q.requestId,{q,start,timer,resolve,reject});if(type==='advance'){this.view.status='pending';this.onchange(this.view);}this.worker.postMessage(q);});
 }
 lose(reason){if(this.closed)return;this.closed=true;this.worker.terminate();for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(Error(reason));}this.pending.clear();this.view.status='lost';this.view.currentStateKnown=false;this.view.stale=!!this.view.snapshot;this.view.fault={message:reason};this.onchange(this.view);}
 dispose(){if(this.disposal)return this.disposal;if(this.closed)return Promise.resolve();this.disposing=true;this.disposal=(async()=>{const r=await this.request('dispose');this.closed=true;this.worker.terminate();return r;})();return this.disposal;}
}
