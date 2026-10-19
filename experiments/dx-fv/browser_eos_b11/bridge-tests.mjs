import {Client,DisplayState} from './preview/client.mjs';
import {BACKEND,SOURCE,INTERVALS} from './preview/snapshot.mjs';
import {format,get} from './preview/view.mjs';
import {assert,same,exact,auditRecord} from '../browser_eos_b9/values.mjs';
import {digest,physical,setup} from '../browser_eos_b9c/harness.mjs';
export function verify(s,r,state){
 assert(same(s.source,SOURCE)&&s.clockSeconds===r.seconds&&r.seconds===state.seconds,'source clock');
 assert(s.sections.length===5&&s.nodes.length===11,'five sections / eleven thermal nodes');
 for(let i=0;i<5;i++){
  const a=s.sections[i],v=r.sections[i],c=state.cells[i];
  for(const [k,value] of Object.entries({pressureBarAbsolute:v.p,temperatureC:v.T,massKg:c.massKg,internalEnergyKJ:c.internalEnergyKJ,volumeM3:c.volumeM3,enthalpyKJkg:v.h,phase:v.phase,quality:v.x,wet:v.wet,superheatK:v.superheatK}))assert(same(a[k],value),'source section '+i+' '+k);
 }
 r.nodes.forEach((n,i)=>{assert(same(s.nodes[i],{id:n.id,temperatureK:n.temperatureK,energyKJ:n.energyKJ}),'thermal node source');});
 assert(same(s.totals,r.totals)&&same(s.flows.inlet,r.fluxes.faces[0])&&same(s.flows.outlet,r.fluxes.faces.at(-1)),'totals/flow source');
 for(const key of ['massResidualKg','refrigerantEnergyResidualKJ','thermalEnergyResidualKJ','combinedEnergyResidualKJ'])assert(same(s.conservation[key],r[key]),key);
 for(const key of ['boundaryMassKg','boundaryEnthalpyKJ','airLoadKJ'])assert(same(s.conservation[key],r.ledger[key]),key);
 assert(Object.values(s.unavailable).every(v=>v===null)&&s.stop===null,'truthful unavailability');
 assert(same(s.heatTransfer.tubeRefrigerantKW,r.fluxes.tubeRefrigerant)&&same(s.heatTransfer.totalTubeRefrigerantKW,r.fluxes.tubeRefrigerant.reduce((a,b)=>a+b,0))&&same(s.heatTransfer.airLoadKW,r.fluxes.airLoad),'original heat-transfer sources');
 for(const key of ['acceptedSteps','rejectedSteps','minAcceptedStepSeconds','maxAcceptedStepSeconds','lastTimeError','lastResidual'])assert(same(s.numerics[key],r[key]),'original numerical source '+key);
 assert(same(s.numerics.nextStepSeconds,state.nextStepSeconds)&&same(s.numerics.lastAcceptedInterval,state.trace.length?state.trace.at(-1):null),'original accepted interval and proposal');
 return {passed:true,sections:5,nodes:11,allSourceFieldsExact:true,audit:auditRecord(r)};
}
function verifyDOM(s,history){
 const cells=[...window.b10.root.querySelectorAll('[data-reading]')];assert(cells.length===93,'all actual reading cells');
 cells.forEach(el=>assert(el.textContent===format(get(s,el.dataset.reading)),'render source '+el.dataset.reading));
 const rows=[...window.b10.root.querySelectorAll('#history tbody tr')];assert(rows.length===history.length,'actual history length');
 rows.forEach((row,i)=>assert(same([...row.cells].map(c=>c.textContent),[history[i].clockSeconds,history[i].acceptedVersion,history[i].sections[4].pressureBarAbsolute,history[i].totals.massKg].map(format)),'history actual accepted source'));
 return cells.length;
}
export async function science(fixture){
 const client=new Client(v=>window.b10.update(v),{test:true}),rows=[],hashes=[],details=[];
 try{
  let response=await client.request('initialize',{fixture});assert(response.success,'initialize');
  for(let i=0;i<4;i++){
   if(i){response=await client.request('advance');assert(response.success,'advance');}
   const detail=await client.request('testDetail'),{record,state}=detail.result;details.push(exact({record,state}));
   rows.push({clock:state.seconds,version:client.view.version,source:verify(client.view.snapshot,record,state),displayCells:verifyDOM(client.view.snapshot,client.view.history),work:{residuals:state.attemptedResidualEvaluations,accepted:state.acceptedSteps,rejected:state.rejectedSteps}});
   hashes.push(await digest({record,state}));
   const detached=structuredClone(client.view.snapshot);detached.sections[0].massKg=-999;
   const again=await client.request('testDetail');assert(same(again.result.state,state)&&same(again.result.record,record),'detached display cannot mutate worker');
  }
  const latest=await client.request('latest');assert(latest.success&&client.view.history.length===4,'read latest creates no trend point');
  return {fixture,rows,checkpointHashes:hashes,fullAcceptedDetails:details,attemptsHash:await digest((await client.request('testDetail')).result.attempts),passed:true,metrics:client.metrics};
 }finally{await client.dispose();}
}
export async function lifecycle(){
 const rows=[];
 for(const fixture of ['numerical','thermal200','thermal400']){
  const c=new Client(v=>window.b10.update(v),{test:true});const initialized=await c.request('initialize',{fixture});assert(initialized.success,'failure fixture initialized');const before=(await c.request('testDetail')).result,snapshot=structuredClone(c.view.snapshot);
  const refused=await c.request('advance');assert(!refused.success&&!refused.snapshot&&c.view.stale,'no successful snapshot after refusal');
  assert(same(c.view.snapshot,snapshot)&&c.view.history.length===1,'last accepted display preserved');verifyDOM(snapshot,c.view.history);assert(window.b10.root.querySelector('#status').textContent.includes('STALE'),'actual stale fault display');assert(window.b10.root.querySelector('#failed-request').textContent.includes(format(refused.requestRange.targetSeconds)),'failed request target separately displayed');const after=(await c.request('testDetail')).result;
  const reference=setup('control',false,fixture==='numerical'?{maxIterations:1,maxAttempts:20}:{});
  const k=Number(fixture.slice(7)),config=fixture==='numerical'?{}:{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:k,finProfileK:k,airInitialK:k,airLoadKW:0}},original=reference.model.create(config);
  if(fixture!=='numerical')reference.model.update(original,{airLoadKW:fixture==='thermal200'?-1:1});
  const originalRecord=reference.model.advance(original,.0001);
  assert(same(original,after.state)&&same(originalRecord,after.record),'stopped accepted state exactly matches original control including prior accepted substeps');
  if(after.state.acceptedSteps===before.state.acceptedSteps)assert(same(physical(before.state),physical(after.state))&&after.proof.wholeAdvancePhysicalUnchanged&&after.proof.wholeAdvanceIdentityUnchanged,'no-commit exact physical/identity rollback');
  assert(fixture==='numerical'?refused.status==='numerical-refusal':refused.status==='modeled-domain-stop'&&refused.fault.evidence.confirmed,'real stop classification');
  const latest=await c.request('latest');assert(!latest.success&&c.view.stale&&same(c.view.snapshot,snapshot),'failure retained on latest');
  const disposed=await c.dispose();assert(disposed.success&&disposed.status==='disposed','dispose after error');rows.push({fixture,refused:exact(refused),proof:after.proof,dispose:disposed.result});
 }
 const c=new Client(()=>{},{test:true});await c.request('initialize',{fixture:'warm'});const before=c.view.snapshot;
 const advance=c.request('advance');let duplicate;try{await c.request('advance');}catch(e){duplicate=e.message;}assert(duplicate==='Physics advance already pending','duplicate client advance refused');
 const stop=c.request('stop');const a=await advance,b=await stop;assert(a.success&&b.success&&b.status==='scheduling-stopped','stop queues after synchronous work');
 assert(!(await c.request('advance')).success,'no resume after scheduling stop');rows.push({stopDuringPending:{advanceClock:a.clockSeconds,stopClock:b.clockSeconds,duplicate,status:b.status}});await c.dispose();
 const fresh=new Client(()=>{},{test:true});await fresh.request('initialize',{fixture:'warm'});assert(same(fresh.view.snapshot.sections,before.sections)&&fresh.view.snapshot.clockSeconds===0,'fresh original restart');
 const last=structuredClone(fresh.view.snapshot);fresh.lose('Test hard worker termination');assert(fresh.view.status==='lost'&&fresh.view.stale&&same(fresh.view.snapshot,last),'lost keeps stale accepted data');rows.push({termination:true,restartOriginal:true,freshInitialization:fresh.metrics[0]});
 const interrupted=new Client(()=>{},{test:true});await interrupted.request('initialize',{fixture:'warm'});const known=structuredClone(interrupted.view.snapshot);interrupted.timeoutMS=50;
 const pending=interrupted.request('advance');interrupted.worker.terminate();let lost;try{await pending;}catch(e){lost=e.message;}
 assert(interrupted.view.status==='lost'&&interrupted.view.stale&&same(interrupted.view.snapshot,known),'actual terminated pending worker becomes lost at deadline');rows.push({actualPendingTermination:true,deadlineTestOnlyMS:50,reason:lost});
 window.b10.update(new DisplayState('new-empty-session'));assert(window.b10.root.querySelectorAll('[data-reading]').length===0&&window.b10.root.querySelector('#history').textContent==='','restart clears prior-session DOM before initialization');rows.push({newSessionClearsOldDOM:true});
 // Production reducer, with synthetic transport ordering only (no fabricated physics).
 const d=new DisplayState('ordering'),base={protocol:1,backendId:BACKEND,sessionId:'ordering',acceptedVersion:0,clockSeconds:0,status:'ready',success:true,snapshot:{...structuredClone(before),sessionId:'ordering'},type:'latest'};
 assert(d.receive({...base,sequence:1}),'initial ordering');assert(d.receive({...base,sequence:3,success:false,snapshot:null,status:'numerical-refusal',error:{message:'transport-order test'}}),'new refusal');
 assert(!d.receive({...base,sequence:2})&&d.stale&&d.status==='numerical-refusal','old equal-version snapshot cannot clear fault');
 assert(!d.receive({...base,sequence:4,sessionId:'replaced'})&&!d.receive({...base,sequence:4,acceptedVersion:-1}),'wrong session/stale version');rows.push({productionReducerOrdering:true,syntheticTransportOnly:true});
 const disposalClient=new Client(()=>{},{test:true});await disposalClient.request('initialize',{fixture:'cold'});const firstDispose=disposalClient.dispose(),secondDispose=disposalClient.dispose();assert(firstDispose===secondDispose,'duplicate disposal shares acknowledgement');let afterDispose;try{await disposalClient.request('latest');}catch(e){afterDispose=e.message;}assert(afterDispose,'commands during disposal refuse immediately');await firstDispose;assert(disposalClient.pending.size===0&&disposalClient.closed,'disposal leaves no dangling commands');rows.push({duplicateDisposal:true,commandDuringDisposalRefused:true});
 const init=window.b10.initialize('cold');let duplicateInit;try{await window.b10.initialize('warm');}catch(e){duplicateInit=e.message;}assert(duplicateInit==='Initialization already pending','duplicate initialization refuses without orphan worker');await init;await window.b10.client.dispose();rows.push({duplicateInitializationRefused:true});
 return {passed:true,rows,raw:await rawProtocol()};
}
async function rawProtocol(){
 const sessionId=crypto.randomUUID(),url=new URL('./preview/worker.mjs',import.meta.url);url.searchParams.set('sessionId',sessionId);url.searchParams.set('test','1');const w=new Worker(url,{type:'module'});let seq=0;
 const send=q=>new Promise((resolve,reject)=>{const t=setTimeout(()=>{w.terminate();reject(Error('raw worker timeout'));},30000);w.onmessage=e=>{clearTimeout(t);resolve(e.data);};w.onerror=e=>{clearTimeout(t);reject(Error(e.message));};w.postMessage(q);});
 const q=(type,args={})=>({protocol:1,backendId:BACKEND,sessionId,requestId:crypto.randomUUID(),sequence:++seq,type,args});
 try{
  assert((await send(q('initialize',{fixture:'cold'}))).success,'raw init');const command=q('advance'),a=await send(command),duplicate=await send(command);
  assert(a.success&&same(a.snapshot,duplicate.snapshot)&&same(a.result,duplicate.result),'exact duplicate replay');
  const changed=await send({...command,args:{duration:.1}});assert(!changed.success,'altered duplicate refuses');
  const wrong=await send({...q('latest'),sequence:99});assert(!wrong.success,'out of order refuses');seq--;
  const detail=await send(q('testDetail'));assert(detail.result.state.seconds===.0001,'duplicate never reexecutes');
  const stale=await send(q('advance',{expectedVersion:0}));assert(!stale.success,'stale expected version refuses');
  const disposed=await send(q('dispose'));assert(disposed.success,'raw dispose');return {passed:true,duplicateReplay:true,alteredDuplicateRefused:true,outOfOrderRefused:true,staleExpectedVersionRefused:true,clockAfterDuplicate:.0001};
 }finally{w.terminate();}
}
