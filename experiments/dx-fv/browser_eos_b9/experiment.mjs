import {Client} from './client.mjs';
import {assert,same,exact,auditRecord,diagnostic} from './values.mjs';
export const times=[0,.0001,.0005,.001];
function render(r,mode){const t=performance.now();const status=document.querySelector('#status'),reading=document.querySelector('#reading');if(status)status.textContent=`${mode} · accepted-A2-table · accepted clock ${r.seconds} s`;if(reading)reading.textContent=JSON.stringify({clockSeconds:r.seconds,lastAcceptedSteps:r.acceptedSteps,sectionTemperaturesK:r.sections.map(s=>s.T+273.15),thermalTemperaturesK:r.nodes.map(n=>({id:n.id,K:n.temperatureK})),inventory:r.totals,fault:r.stop,qualification:'Bounded table-backed architecture research'},null,2);return performance.now()-t;}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
export function heartbeat(){let phase='idle',last=performance.now(),frameLast=last;const gaps=[],frames=[],longTasks=[],spans=[];let phaseStart=last;
 const timer=setInterval(()=>{const now=performance.now();gaps.push({phaseAtCallback:phase,start:last,end:now,ms:now-last});last=now;},10);
 let raf;const frame=t=>{frames.push({phaseAtCallback:phase,start:frameLast,end:t,ms:t-frameLast});frameLast=t;raf=requestAnimationFrame(frame);};raf=requestAnimationFrame(frame);
 let observer;try{observer=new PerformanceObserver(list=>longTasks.push(...list.getEntries().map(e=>({phase,ms:e.duration,start:e.startTime}))));observer.observe({entryTypes:['longtask']});}catch{}
 return {phase:p=>{const now=performance.now();spans.push({phase,start:phaseStart,end:now});phaseStart=now;phase=p;window.workPhase=p;},end:()=>{spans.push({phase,start:phaseStart,end:performance.now()});clearInterval(timer);cancelAnimationFrame(raf);observer?.disconnect();return {gaps,frames,spans,longTasks,longTaskAPI:!!observer};}};
}
export async function workload(mode,fixture,{observe=true,engine=null}={}){
 const hb=heartbeat();await wait(30);const client=new Client(mode),rows=[],samples=[];
 try{
 hb.phase('initialization');const initial=await client.request('initialize',{fixture});assert(initial.success,'initialization '+JSON.stringify(initial.error));
 const firstRenderMS=render(initial.result.record,mode);rows.push(initial.result);samples.push({type:'initialize',timing:initial.timing,client:initial.clientTiming,importMS:initial.result.importMS,factoryMS:initial.result.factoryMS,constructionMS:initial.result.constructionMS,firstRenderMS,firstRenderableMS:initial.clientTiming.roundtripMS+client.creationMS+firstRenderMS});
 await wait(30);
 for(let i=1;i<times.length;i++){
 hb.phase('physics');const reply=await client.request('advance',{duration:times[i]-times[i-1]});assert(reply.success,'advance '+JSON.stringify(reply.error));assert(!reply.result.record.stop,'unexpected physics stop');assert(reply.clock===times[i],'clock');
 rows.push(reply.result);samples.push({type:'advance',clock:reply.clock,timing:reply.timing,client:reply.clientTiming,advanceMS:reply.result.advanceMS,propertyCalls:reply.result.propertyCalls});
 hb.phase('snapshot');const snap=await client.request('snapshot');assert(snap.success&&same(snap.result.record,reply.result.record),'record purity');hb.phase('render');const renderMS=render(snap.result.record,mode);samples.push({type:'snapshot',recordMS:snap.result.recordMS,renderMS,timing:snap.timing,client:snap.clientTiming,recordJSONEstimateBytes:new TextEncoder().encode(JSON.stringify(snap.result.record)).byteLength});
 await wait(30);
 }
 hb.phase('diagnostics');const diag=await client.request('diagnostics');assert(diag.success);const disposed=await client.dispose();assert(disposed.success);
 await wait(30);const audits=rows.map(r=>auditRecord(r.record));
 const science=rows.map(r=>({record:r.record,state:r.state,attempts:r.attempts??null}));
 let baselineVerified=null;if(engine){const baseline=await(await fetch(new URL('./evidence/frozen-browser-scientific-hashes.json',import.meta.url))).json();for(let i=0;i<science.length;i++){const raw=new TextEncoder().encode(JSON.stringify(exact({record:science[i].record,state:science[i].state}))),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(v=>v.toString(16).padStart(2,'0')).join('');assert(hash===baseline[engine][fixture][i],'STOP: timed-run scientific baseline mismatch');}baselineVerified=true;}
 return {mode,fixture,baselineVerified,science,records:rows.map(r=>r.record),audits,samples,diagnostics:diag.result,disposed:disposed.result,heartbeat:hb.end(),exactEvidenceUTF8Bytes:science.map(v=>new TextEncoder().encode(JSON.stringify(exact(v))).byteLength)};
 }finally{client.terminate();}
}
export async function parity(){const results=[];
 for(const fixture of ['cold','warm']){
 const main=await workload('main',fixture),worker=await workload('worker',fixture);
 assert(same(main.science,worker.science),'STOP: scientific parity mismatch '+fixture);
 assert(same(main.diagnostics.counts,worker.diagnostics.counts),'property call parity');assert(same(main.diagnostics.attempts,worker.diagnostics.attempts),'stage/probe/line-search parity');
 results.push({fixture,exactParity:true,main,worker});
 }
 return {passed:true,results};
}
export async function benchmark(){const rounds=[];
 for(let round=0;round<3;round++){
 for(const mode of (round%2?['worker','main']:['main','worker'])){
 // Driver reloads the page for each mode block in the outer runner when requested.
 for(const fixture of ['cold','warm'])for(const temperature of ['cold-session','warm-restart']){
 const r=await workload(mode,fixture);rounds.push({round,temperature,...r});
 }
 }
 }
 return {passed:true,rounds};
}
export async function run(stage,args={}){
 if(stage==='parity')return parity();
 if(stage==='workload')return workload(args.mode,args.fixture,{engine:args.engine});
 if(stage==='lifecycle')return (await import('./lifecycle.mjs')).run();
 if(stage==='b7')return (await import('./b7-subset.mjs')).run();
 if(stage==='c1timed'){const hb=heartbeat();await wait(30);hb.phase('C1-sequence');const t=performance.now(),result=await (await import('./c1-tests.mjs')).run(args.mode),elapsedMS=performance.now()-t;await wait(30);return {passed:true,elapsedMS,heartbeat:hb.end(),result};}
 if(stage==='c1')return (await import('./c1-tests.mjs')).run(args.mode);
 throw Error('Unknown B9 stage');
}
