import {pack} from '../browser_eos_b5b_c1/adapter.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);};
export async function performanceSamples(loadControl,loadCandidate,fixture){
 const es={control:await loadControl('candidateB'),candidate:await loadCandidate('candidateB')},rows=[],factories=[];
 const ph={mode:'PH',args:[799999.9981754856,1624022.744737779]},s=es.candidate.evaluate(ph),du={mode:'DU',args:[s.rho,s.u]},pt={mode:'PT',args:[350000,300]};
 try{
  for(const [label,e]of Object.entries(es)){
   for(let i=0;i<8;i++){try{e.evaluate(fixture.request);}catch{}e.evaluate(pt);e.evaluate(ph);e.evaluate(du);}
   for(let i=0;i<12;i++){let t=performance.now();const state=e.module.factory('HEOS','Ammonia'),factoryMS=performance.now()-t;t=performance.now();state.delete();factories.push({label,sample:i,factoryMS,disposeMS:performance.now()-t,deleted:state.isDeleted()});}
  }
  for(let round=0;round<3;round++)for(const label of (round%2?['candidate','control']:['control','candidate'])){
   const e=es[label];for(const [group,requests]of [['PT',[pt]],['rejected-PT',[fixture.request]],['PH',[ph]],['DU',[du]],['alternating',[fixture.request,pt]]]){
    const memoryBefore=e.memory(),heapBefore=performance.memory?.usedJSHeapSize??null,t=performance.now();let calls=0,failures=0,checksum=0,firstError=null;
    do{for(const q of requests){try{checksum+=e.evaluate(q).rho;}catch(err){failures++;firstError??=String(err);if(label==='candidate')ok(!String(err).includes('Assertion failed'),'performance cleanup assertion');}calls++;}}while(performance.now()-t<35&&calls<512);
    rows.push({round,label,group,calls,failures,firstError,checksum,elapsedMS:performance.now()-t,memoryBefore,memoryAfter:e.memory(),heapBefore,heapAfter:performance.memory?.usedJSHeapSize??null});
   }
  }
  return {passed:true,rows,factories,init:Object.fromEntries(Object.entries(es).map(([k,e])=>[k,e.init])),methodology:'8 explicit warm-up sequences per variant; three interleaved 35-ms rounds, max 512 calls per sample. Full update/getters/error propagation. Timings include JS wrappers and exception diagnostics. First factory and load timings separate. No universal performance threshold.',memoryLimitations:'Linear-memory size is not live allocation count or leak proof. Chromium heap readings are coarse; WebKit heap API unavailable. Ref ownership assessed by source/ABI plus traces.'};
 }finally{es.control.dispose();es.candidate.dispose();}
}
export async function workers(fixture){
 const rows=[];
 for(const kind of ['control','candidate']){
  let ticks=0,last=performance.now(),maxGapMS=0;const t=performance.now(),timer=setInterval(()=>{const n=performance.now();maxGapMS=Math.max(maxGapMS,n-last);last=n;ticks++;},5);
  try{const result=await new Promise((resolve,reject)=>{const w=new Worker(new URL('./worker.mjs',import.meta.url),{type:'module'}),deadline=setTimeout(()=>{w.terminate();reject(Error('B6 worker deadline 30000ms'));},30000);
   w.onmessage=e=>{clearTimeout(deadline);w.terminate();resolve(e.data);};w.onerror=e=>{clearTimeout(deadline);w.terminate();reject(Error(e.message));};w.postMessage({kind,fixture});});
   rows.push({kind,result,elapsedMS:performance.now()-t,mainThreadTicks:ticks,maxGapMS});ok(result.passed,'worker status');
  }finally{clearInterval(timer);}
 }
 ok(JSON.stringify(rows[0].result.lastSupported)===JSON.stringify(rows[1].result.lastSupported),'worker supported equality');
 return {passed:true,rows,physicalIPad:false};
}
