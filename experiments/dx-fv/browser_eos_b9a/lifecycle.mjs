import {Client} from './client.mjs';import {BACKEND,service} from './service.mjs';import {assert,same,exact} from './values.mjs';
export async function run(){const rows=[];
 // Untouched control lifecycle remains separately executable.
 const control=await(await import('../browser_eos_b9/lifecycle.mjs')).run();assert(control.passed);
 for(const mode of ['B','C']){
 const c=new Client(mode);try{
 const init=await c.request('initialize',{fixture:'cold'});assert(init.success);
 const v0=init.acceptedVersion,initial=structuredClone(init.result.compact),d0=await c.request('diagnosticsDetail',{version:v0});
 c.display.sections[0].massKg=-999;const s0=await c.request('snapshotCompact');assert(same(s0.result.compact,initial),'detached presentation');
 const d1=await c.request('diagnosticsDetail',{version:v0});assert(same(d0.result.state,d1.result.state),'presentation did not mutate authority');
 const q={protocol:1,workerId:c.workerId,backendId:BACKEND,requestId:'duplicate-advance',sessionId:c.sessionId,sequence:++c.sequence,type:'advance',args:{duration:.00001}};
 const [a,a2]=await Promise.all([c.send(q),c.send(q)]);assert(same(a.result,a2.result));const before=await c.request('diagnosticsDetail',{version:a.acceptedVersion}),countsBefore=await c.request('diagnostics');
 const replay=await c.send(q);assert(same(a.result,replay.result));const after=await c.request('diagnosticsDetail',{version:a.acceptedVersion}),countsAfter=await c.request('diagnostics');assert(same(before.result.state,after.result.state)&&same(countsBefore.result.counts,countsAfter.result.counts),'cache physics/events/property counters unchanged');
 const altered=await c.send({...q,args:{duration:.00002}});assert(!altered.success&&altered.error.message.includes('mismatch'));
 const oo=await c.send({...q,requestId:'out-of-order',sequence:c.sequence+2});assert(!oo.success);
 const stale=await c.request('advance',{duration:.00001,expectedVersion:-1});assert(!stale.success&&stale.clock===a.clock);
 for(let i=0;i<5;i++)assert((await c.request('advance',{duration:.00001})).success);
 const expired=await c.request('diagnosticsDetail',{version:v0});assert(expired.success&&!expired.result.available&&expired.result.reason==='unavailable/expired');
 const summary=await c.request('diagnosticsSummary',{version:expired.acceptedVersion});assert(summary.result.available);const current=await c.request('snapshotCompact'),display=structuredClone(c.display);
 await c.send(q);assert(same(c.display,display),'old duplicate cannot install stale display');
 const pending=Array.from({length:8},()=>c.request('diagnosticsSummary',{version:current.acceptedVersion}));let backpressure=false;try{await c.request('snapshotCompact');}catch(e){backpressure=e.message==='Backpressure limit';}assert(backpressure);await Promise.all(pending);
 const advance=c.request('advance',{duration:.00001}),stop=c.request('stop');const [ar,sr]=await Promise.all([advance,stop]);assert(ar.success&&sr.success&&sr.clock===ar.clock&&sr.result.physicalStop===null);
 const refused=await c.request('advance',{duration:.00001});assert(!refused.success&&c.displayStale);
 // Synthetic older equal-version response must not erase the latest refusal.
 const savedFault=structuredClone(c.lastFault),seq=c.lastDisplaySequence-1,fakeQ={...q,type:'snapshotCompact',requestId:'stale-equal',sequence:seq};
 const late=new Promise((resolve,reject)=>c.pending.set(fakeQ.requestId,{q:fakeQ,resolve,reject,start:performance.now(),timer:setTimeout(()=>{},1)}));c.receive({...current,sequence:seq,type:fakeQ.type,requestId:fakeQ.requestId,acceptedVersion:refused.acceptedVersion});await late;assert(same(c.lastFault,savedFault)&&c.displayStale,'older snapshot cannot erase refusal');
 assert(!c.receive({...current,sessionId:'replaced-session'}));
 const disposed=await c.dispose();assert(disposed.success&&disposed.result.retainedEvidence===0);assert(!c.receive(current));
 const restart=new Client(mode);const fresh=await restart.request('initialize',{fixture:'cold'});assert(same(fresh.result.compact,initial));await restart.dispose();
 rows.push({mode,passed:true,duplicatePhysicsNotRepeated:true,countsAndMUVAndEventsUnchanged:true,alteredDuplicateRefused:true,outOfOrderRefused:true,staleVersionRefused:true,expiration:expired.result,backpressure,stopAtBoundary:true,equalVersionFaultPreserved:true,restartInitialIdentical:true,dispose:disposed.result});
 }finally{c.terminate();}
 // Exercise exact bounded response semantics directly in the owner; no wall-clock physics.
 const owner=service('bounded','bounded',{mode});let seq=0;const q=(type,args={})=>({protocol:1,workerId:'bounded',backendId:BACKEND,sessionId:'bounded',requestId:String(++seq),sequence:seq,type,args});
 await owner(q('initialize',{fixture:'cold'}));for(let i=1;i<256;i++)assert((await owner(q('snapshotCompact'))).success);
 const exhausted=await owner(q('advance',{duration:.0001}));assert(!exhausted.success&&exhausted.clock===0&&exhausted.error.message==='Session response cache exhausted');const disposed=await owner(q('dispose'));assert(disposed.success);const after=await owner(q('snapshotCompact'));assert(!after.success);
 rows.push({mode,test:'cache-256-exhaustion',passed:true,clockNotAdvanced:exhausted.clock,dispose:disposed.result,afterDisposed:after.error});
 const doomed=new Client(mode);await doomed.request('initialize',{fixture:'cold'});const p=doomed.request('advance',{duration:.001});doomed.terminate();let rejected=false;try{await p;}catch{rejected=true;}assert(rejected);rows.push({mode,test:'terminate-pending',passed:true,inFlightState:'unknown; destroyed session; not rollback'});
 }
 return {passed:true,control,rows};}
