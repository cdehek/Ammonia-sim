import {loadQualifiedEOS} from './loader.mjs';
import {bits} from '../browser_eos_b5b_c1/adapter.mjs';
const read=async p=>await(await fetch(new URL(p,import.meta.url))).json();
const pause=()=>new Promise(resolve=>setTimeout(resolve,0));
const heap=()=>performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize,limit:performance.memory.jsHeapSizeLimit}:null;
export async function performanceSamples(artifacts,engine){
 const inputs=await read('./evidence/fixed-inputs.json'),fixtures=(await read('../browser_eos_b6/evidence/historical-rejected-pt.json')).filter(r=>r.engine===engine);
 const fixed=n=>{const x=inputs.find(r=>r.key==='native-ledger-'+n).input.values;return {mode:'DU',args:[x.rho,x.u]};};
 const rows=[],initialization=[],instances={};let last=performance.now(),gaps=[];
 const timer=setInterval(()=>{const now=performance.now();gaps.push(now-last);last=now;},10);
 try{
  for(let round=0;round<5;round++)for(const id of round%2?['gateA','rebuiltB4C']:['rebuiltB4C','gateA']){
   const before=heap(),e=await loadQualifiedEOS(artifacts[id]);try{initialization.push({round,id,init:e.init,memory:e.memory(),heapBefore:before,heapAfter:heap()});}finally{e.dispose();}await pause();
  }
  for(const id of ['rebuiltB4C','gateA'])for(const fullVLE of [false,true])instances[id+':'+fullVLE]=await loadQualifiedEOS(artifacts[id],{fullVLE});
  const pt={mode:'PT',args:[350000,300]},ph={mode:'PH',args:[799999.9981754856,1624022.744737779]},liquid={mode:'PT',args:[350000,250]},mixture={mode:'PQ',args:[350000,.4]};
  const seed=instances['rebuiltB4C:false'].evaluate(pt),du={mode:'DU',args:[seed.rho,seed.u]};
  const groups=[['original-resolved-liquids',[146,151,152].map(fixed),false],['original-unresolved-endpoints',[148,162,164,165].map(fixed),false],['homogeneous-liquid',[liquid],false],['homogeneous-vapor',[pt],false],['genuine-mixture',[mixture],false],['supported-PH-PT-DU',[ph,pt,du],false],['rejected-PT',[fixtures[0].request,fixtures[3].request],false],['fresh-supported-state',[pt],true],['reused-supported-state',[pt],false]];
  for(const fullVLE of [false,true])for(let round=0;round<5;round++)for(const [group,requests,fresh]of groups)for(const id of round%2?['gateA','rebuiltB4C']:['rebuiltB4C','gateA']){
   const e=instances[id+':'+fullVLE],started=performance.now(),counts={accepted:0,rejected:0},outcomes=requests.map(()=>({accepted:0,rejected:0}));let calls=0,checksum=0,lastError=null;
   do{
    for(let i=0;i<requests.length;i++){
     try{const out=fresh?e.evaluateFresh(requests[i]):e.evaluate(requests[i]);checksum+=out.rho;counts.accepted++;outcomes[i].accepted++;}
     catch(error){counts.rejected++;outcomes[i].rejected++;lastError=error.message;}
     calls++;
    }
   }while(performance.now()-started<60);
   const elapsedMS=performance.now()-started;
   rows.push({id,fullVLE,round,group,fresh,requests:requests.map(r=>({...r,inputBits:r.args.map(bits)})),calls,counts,outcomes,elapsedMS,usPerCall:elapsedMS*1000/calls,callsPerSecond:calls*1000/elapsedMS,checksum,lastError,memory:e.memory(),heap:heap()});await pause();
  }
 }finally{for(const e of Object.values(instances))e.dispose();clearInterval(timer);}
 return {rows,initialization,heartbeatIntervalMS:10,heartbeatGapsMS:gaps,maximumHeartbeatGapMS:Math.max(...gaps),rounds:5,minimumRoundMS:60,identityHashChecksIncludedInInitialization:true,freshTimingIncludesPhaseInspection:true,heapObservationIsNotLeakProof:true,physicalSafariOrIPad:false};
}
