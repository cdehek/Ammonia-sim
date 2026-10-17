import {Client} from './client.mjs';import {BACKEND} from './service.mjs';import {assert,same,bits} from './values.mjs';import {probe} from './probe-client.mjs';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
export async function run(){const rows=[];
 // Binary64 and clone/transfer contract independent of physics.
 const buffer=new ArrayBuffer(48),d=new DataView(buffer);['0000000000000000','8000000000000000','7ff0000000000000','fff0000000000000','7ff8000000001234','3ff0000000000001'].forEach((h,i)=>d.setBigUint64(i*8,BigInt('0x'+h)));
 const expected=[...new Uint8Array(buffer)],begin=performance.now(),echo=await probe('echo',{values:[0,-0,Infinity,-Infinity,NaN,1+Number.EPSILON],bytes:new Uint8Array(buffer)},[buffer]);
 assert(buffer.byteLength===0,'transfer detaches copied buffer');assert(same([...echo.result.bytes],expected),'all payload bytes including NaN payload');assert(Object.is(echo.result.values[1],-0)&&Number.isNaN(echo.result.values[4]));
 rows.push({test:'binary64-clone-and-transfer',passed:true,roundtripMS:performance.now()-begin,bytes:expected,numberBits:echo.result.values.map(bits),authoritativeStateDetached:false});
 const js=await probe('jsError');assert(!js.success&&js.error.message==='B9 JS-origin error');rows.push({test:'JS-error',passed:true,response:js});
 for(const mode of ['main','worker']){
 const c=new Client(mode);let init=await c.request('initialize',{fixture:'cold'});assert(init.success);
 // Queue while synchronous advance runs. Stop is acknowledged after its commit.
 const advance=c.request('advance',{duration:.0001}),stop=c.request('stop');const [a,s]=await Promise.all([advance,stop]);assert(a.success&&s.success&&s.clock===.0001&&s.result.physicalStop===null);
 const refused=await c.request('advance',{duration:.0001});assert(!refused.success&&refused.clock===.0001);const snap=await c.request('snapshot');assert(same(a.result.state,snap.result.state));
 const queued=Array.from({length:8},()=>c.request('diagnostics'));let bounded=false;try{await c.request('diagnostics');}catch(e){bounded=e.message==='Backpressure limit';}assert(bounded,'bounded pending requests');assert((await Promise.all(queued)).every(r=>r.success),'queued diagnostics');
 const old={protocol:1,workerId:c.workerId,backendId:BACKEND,requestId:'duplicate-stop',sessionId:c.sessionId,sequence:++c.sequence,type:'stop',args:{}};
 const first=await c.send(old),duplicate=await c.send(old);assert(first.success&&same(first.result,duplicate.result));
 const bad=await c.send({...old,args:{different:true}});assert(!bad.success&&bad.error.message.includes('Duplicate'));
 const outOfOrder=await c.send({...old,requestId:'out-of-order',sequence:c.sequence+2});assert(!outOfOrder.success);
 const unknown=await c.request('unsupported-command');assert(!unknown.success);
 const invalid=await c.send({...old,requestId:'bad-version',protocol:999,sequence:c.sequence+1});assert(!invalid.success);
 const display=c.display;assert(!c.receive({...snap,sessionId:'old-session'}));assert(c.display===display,'stale session cannot render');
 // A matched late response with an older version cannot replace display.
 const lateQ={...old,requestId:'late-display',sequence:++c.sequence,type:'snapshot'};const fake={...snap,requestId:lateQ.requestId,sequence:lateQ.sequence,acceptedVersion:-1,result:{record:{seconds:-99}}};
 const late=new Promise((resolve,reject)=>{c.pending.set(lateQ.requestId,{q:lateQ,resolve,reject,start:performance.now(),timer:setTimeout(()=>{},1)});});c.receive(fake);await late;assert(c.display===display,'older version cannot render');c.sequence--;
 const equalQ={...old,requestId:'late-equal-version',sequence:c.lastDisplaySequence-1,type:'snapshot'};const equalLate=new Promise((resolve,reject)=>c.pending.set(equalQ.requestId,{q:equalQ,resolve,reject,start:performance.now(),timer:setTimeout(()=>{},1)}));c.receive({...snap,requestId:equalQ.requestId,sequence:equalQ.sequence,result:{record:{seconds:-99}}});await equalLate;assert(c.display===display,'older command cannot replace equal-version fault/record');
 // Use a separate low-level owner to test requests after dispose (client closes).
 const {service}=await import('./service.mjs'),owner=service('disposed-test','disposed-test');let seq=0;const q=type=>({protocol:1,workerId:'disposed-test',backendId:BACKEND,requestId:String(++seq),sessionId:'disposed-test',sequence:seq,type,args:{fixture:'cold'}});
 await owner(q('initialize'));await owner(q('dispose'));const after=await owner(q('snapshot'));assert(!after.success);
 const disposed=await c.dispose();assert(disposed.success);assert(!c.receive(snap));
 // Duplicate ADVANCE must not double-run, including two queued identical messages.
 const dup=new Client(mode);await dup.request('initialize',{fixture:'cold'});const dq={protocol:1,workerId:dup.workerId,backendId:BACKEND,requestId:'same-advance',sessionId:dup.sessionId,sequence:++dup.sequence,type:'advance',args:{duration:.0001}};
 const [d1,d2]=await Promise.all([dup.send(dq),dup.send(dq)]);const replay=await dup.send(dq);assert(same(d1.result,replay.result),'owner cached advance replay');assert(same(d1.result,d2.result));const ds=await dup.request('snapshot');assert(ds.clock===.0001);await dup.dispose();
 // Fresh original conditions after restart.
 const restart=new Client(mode),fresh=await restart.request('initialize',{fixture:'cold'});assert(same(fresh.result.state,init.result.state));await restart.dispose();
 // Failed construction never installs a model; then safe disposal.
 const failed=new Client(mode),f=await failed.request('initialize',{fixture:'not-supported'});assert(!f.success&&f.clock===null);assert((await failed.dispose()).success);
 rows.push({mode,test:'stop-queue-duplicate-order-stale-dispose-restart-init-error',passed:true,lastAcceptedClock:a.clock,stopAfterBoundary:s.clock,duplicateAdvanceClock:ds.clock,disposedRequest:after.error});
 }
 // Termination during pending work: unknown accepted state, never pretend rollback.
 const terminated=new Client('worker');await terminated.request('initialize',{fixture:'cold'});const known=terminated.display.seconds;const pending=terminated.request('advance',{duration:.001});terminated.terminate();let rejected=false;try{await pending;}catch{rejected=true;}assert(rejected);rows.push({test:'emergency-termination',passed:true,lastKnownAcceptedClock:known,inFlightState:'unknown/unrecoverable',solverRollbackClaim:false});
 let crash=false;try{await probe('crash');}catch(e){crash=true;}assert(crash);rows.push({test:'unexpected-worker-crash',passed:true,pendingRejected:true});
 // Actual module fetch failure, independent of numerical behavior.
 let fetchFailed=false;const w=new Worker(new URL('./missing-worker.mjs',import.meta.url),{type:'module'});await new Promise(resolve=>{const t=setTimeout(resolve,3000);w.onerror=()=>{fetchFailed=true;clearTimeout(t);resolve();};});w.terminate();assert(fetchFailed);rows.push({test:'module-fetch-failure',passed:true});
 // Pending dispose follows committed work, then termination.
 const pendingDispose=new Client('worker');await pendingDispose.request('initialize',{fixture:'warm'});const p=pendingDispose.request('advance',{duration:.0001}),dis=pendingDispose.dispose();const r=await p,dr=await dis;assert(dr.clock===r.clock);rows.push({test:'dispose-pending-advance',passed:true,acceptedClock:dr.clock});
 const {service}=await import('./service.mjs'),boundedOwner=service('bounded','bounded');let seq=0;const cq=type=>({protocol:1,workerId:'bounded',backendId:BACKEND,requestId:String(++seq),sessionId:'bounded',sequence:seq,type,args:{}});for(let i=0;i<256;i++)await boundedOwner(cq('unsupported'));const exhausted=await boundedOwner(cq('diagnostics'));assert(!exhausted.success&&exhausted.error.message==='Session response cache exhausted','finite cache');assert((await boundedOwner(cq('dispose'))).success,'dispose after exhausted cache');rows.push({test:'bounded-cache-dispose',passed:true,cachedResponses:256});
 return {passed:true,rows};
}
