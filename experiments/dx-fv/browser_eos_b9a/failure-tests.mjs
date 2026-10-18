import {Client} from './client.mjs';import {assert,same,exact} from './values.mjs';
export async function run(){const original=await(await import('../browser_eos_b9/c1-tests.mjs')).run('both'),rows=[];
 for(const mode of ['B','C'])for(const scenario of ['transient','persistent','boundary','recordFailure','thermal200','thermal400']){
 const c=new Client(mode,{test:true});try{
 const init=await c.request('initialize',{fixture:'cold',c1Scenario:scenario});assert(init.success,JSON.stringify(init.error));
 const q={protocol:1,workerId:c.workerId,sessionId:c.sessionId,backendId:'accepted-A2-table',requestId:'failure-advance',sequence:++c.sequence,type:'advance',args:{duration:.001}};
 const a=await c.send(q),replay=await c.send(q);assert(same(a.result,replay.result)&&same(a.error,replay.error),'failure cache replay');assert(a.clock===replay.clock);
 if(scenario!=='transient'){const saved=structuredClone(c.lastFault);const bad=await c.send({...q,args:{duration:.002}});assert(!bad.success&&same(c.lastFault,saved),'altered duplicate cannot downgrade numerical fault');}
 const proof=await c.request('testEvidence');assert(proof.success);const p=proof.result.c1Proof;
 if(scenario==='transient'){assert(a.success&&a.clock===.0011&&!a.result.compact.lastFault);assert(p.failures===2);}
 else {assert(a.clock===init.clock&&p.acceptedBitsUnchanged&&p.identityUnchanged,'last accepted exact rollback');
 if(scenario.startsWith('thermal')){assert(a.success&&a.result.compact.status==='physical-domain-stop'&&p.stop.evidence.confirmed);}
 else {assert(p.stop.kind==='solver'&&!p.stop.evidence.confirmed&&p.failures===20);assert(p.maxIterations===30&&p.floor===1e-9);if(scenario==='recordFailure'){assert(!a.success&&a.error.recordFailure&&!a.error.recordFailure.propertyStatesReturned&&c.displayStale,'honest unavailable record');}else assert(a.success&&a.result.compact.status==='numerical-stop');}}
 const detail=await c.request('diagnosticsDetail',{version:a.acceptedVersion});assert(detail.success&&detail.result.available&&detail.acceptedVersion===a.acceptedVersion);assert(detail.result.attempts.length>0);
 const ev=detail.result.attempts.filter(a=>a.failure);for(let i=1;i<ev.length;i++)assert(ev[i].trialSeconds===ev[i-1].trialSeconds/2,'original halving');
 if(scenario==='boundary')assert(JSON.stringify(detail).includes('boundary-unresolved'),'boundary reason retained');
 if(scenario==='persistent'||scenario==='recordFailure')assert(JSON.stringify(detail).includes('inverse-recovery-failure'),'inverse reason retained');
 if(scenario!=='transient'){const stopped=await c.request('advance',{duration:.001});assert(!stopped.success&&stopped.clock===a.clock);const retained=await c.request('diagnosticsDetail',{version:a.acceptedVersion});assert(same(retained.result.attempts,detail.result.attempts)&&same(retained.result.fault,detail.result.fault),'stopped command must retain complete current fault history');}
 rows.push({mode,scenario,passed:true,response:exact(a),proof:p,diagnostics:{available:true,version:detail.result.acceptedVersion,attemptCount:detail.result.attempts.length,failureAttempts:ev.length,recordAvailable:!!detail.result.record,fault:detail.result.fault}});await c.dispose();
 }finally{c.terminate();}}
 return {passed:true,original,rows,syntheticDoesNotProveNaturalReachability:true};}
