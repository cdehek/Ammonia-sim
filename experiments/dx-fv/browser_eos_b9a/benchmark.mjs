import {Client} from './client.mjs';import {assert,exact,same} from './values.mjs';import {compact} from './snapshot.mjs';import {heartbeat} from '../browser_eos_b9/experiment.mjs';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function render(snapshot){const t=performance.now();document.querySelector('#status').textContent=`${snapshot.status} · ${snapshot.clockSeconds} s · accepted ${snapshot.acceptedVersion}`;document.querySelector('#reading').textContent=JSON.stringify(snapshot,null,2);return performance.now()-t;}
export async function workload(mode,fixture,{engine}={}){
 const frozen=await(await fetch('../browser_eos_b9/evidence/frozen-browser-scientific-hashes.json')).json();
 const hb=heartbeat();await wait(30);const c=new Client(mode),samples=[],payloads=[];window.activeClient=c;
 const measurement=(r,type)=>({type,clock:r.clock,timing:r.timing,client:r.clientTiming,verificationMS:r.verificationMS??null,scientificHashVerifiedInsideOwner:r.scientificHashVerifiedInsideOwner??null,advanceMS:r.result?.advanceMS??null,components:r.timing.components??null,propertyCalls:r.result?.propertyCalls??null});
 const project=r=>r.result.compact??compact(r.result.record,r.result.state,{status:r.status});
 try{
 hb.phase('initialization');const init=await c.request('initialize',{fixture,scientificHash:frozen[engine][fixture][0]});assert(init.success,JSON.stringify(init.error));let snap=project(init);const renderMS=render(snap);const firstFrame=performance.now();await new Promise(requestAnimationFrame);const frameWaitMS=performance.now()-firstFrame;
 samples.push({...measurement(init,'initialize'),renderMS,frameWaitMS,creationMS:c.creationMS,firstRenderableMS:c.creationMS+init.clientTiming.roundtripMS+renderMS,firstActualFrameUpperBoundMS:c.creationMS+init.clientTiming.roundtripMS+renderMS+frameWaitMS});
 const rawPayloads=[];
 await wait(30);
 for(let i=0;i<3;i++){
 hb.phase('physics');const r=await c.request('advance',{duration:[.0001,.0004,.0005][i],scientificHash:frozen[engine][fixture][i+1]});assert(r.success,JSON.stringify(r.error));assert(r.clock===[.0001,.0005,.001][i]);samples.push(measurement(r,'advance'));rawPayloads.push({type:'advance',value:r.result});
 hb.phase('snapshot');const s=await c.request('snapshot');assert(s.success);snap=project(s);hb.phase('render');const t=performance.now(),renderMS=render(snap);await new Promise(requestAnimationFrame);samples.push({...measurement(s,'snapshot'),renderMS,nextFrameUpperBoundMS:performance.now()-t});rawPayloads.push({type:'snapshot',value:s.result});await wait(30);
 }
 hb.phase('diagnostics');const d=await c.request(mode==='A'?'diagnostics':'diagnosticsSummary',mode==='A'?{}:{version:snap.acceptedVersion});assert(d.success);samples.push(measurement(d,'diagnosticsSummary'));rawPayloads.push({type:'diagnostics',value:d.result});
 hb.phase('dispose');const disposed=await c.dispose();assert(disposed.success);samples.push(measurement(disposed,'dispose'));await wait(30);const heart=hb.end();
 // Size estimates are deliberately after timed phases, with no scientific input reconstruction.
 for(const v of rawPayloads){const t=performance.now();payloads.push({type:v.type,jsonEstimateBytes:new TextEncoder().encode(JSON.stringify(v.value)).length,serializationEstimateMS:performance.now()-t});}
 return {passed:true,mode,fixture,samples,payloads,heartbeat:heart,baselineVerifiedInsideOwner:true,diagnosticScope:mode==='A'?'complete cumulative transport':mode==='B'?'complete cumulative ownership; compact transport':'complete generation; four recent endpoint retention',browserHeap:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null};
 }finally{c.terminate();window.activeClient=null;}
}
