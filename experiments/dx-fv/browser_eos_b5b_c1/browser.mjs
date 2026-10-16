import {createAdapter,errorJSON,pack,bits} from './adapter.mjs';
import {createAdapter as historicalAdapter} from '../browser_eos_backend/adapter.mjs';
import {loadEOS} from '../browser_eos_b4c/loader.mjs';
import {run as historicalReplay} from '../browser_eos_b5b/browser.mjs';
const ok=(v,m)=>{if(!v)throw Error(m||'assertion');};
const equal=(a,b,m)=>ok(JSON.stringify(a)===JSON.stringify(b),m||'exact equality');
const decode=x=>{const d=new DataView(new ArrayBuffer(8));d.setBigUint64(0,BigInt('0x'+x));return d.getFloat64(0);};
export async function run(args){
 const control=await historicalReplay(args);
 const em={exports:{}};new Function('module','exports',args.engine)(em,em.exports);const guard=em.exports.createEngine(args.table);
 const eos=await loadEOS('candidateB'),adapter=createAdapter(eos,guard),rows=[],matrix=[],falseAcceptance=[];
 function replay(input){const calls=[],a=createAdapter({evaluate(q){const s=eos.evaluate(q);calls.push({request:q,raw:pack(s)});return s;}},guard);
  let state=null,error=null;try{state=pack(a.stateMVU(input.M,input.V,input.U_kJ,35));}catch(e){error=errorJSON(e);}
  return {input:pack(input),calls,state,error};}
 try{
  for(const f of args.fixtures){const input=Object.fromEntries(Object.entries(f.fixedInput.bits).map(([k,v])=>[k,decode(v)])),c=control.rows.find(r=>r.key===f.fixedKey),r={key:f.fixedKey,id:f.id,...replay(input)};
   equal(r.calls[0].raw,c.raw,'raw DU unchanged');ok(!r.state&&r.error?.faultKind==='solver');const diag=r.error.evidence.propertyFailure;
   ok(diag.reason==='boundary-unresolved'&&diag.physicalTrajectoryExit==='unproved');equal(diag.rawCoordinates,c.raw);
   equal(pack(eos.evaluate({mode:'PH',args:f.originalPHInput})),c.originatingRawPH,'PH bits unchanged');
   equal(pack(adapter.ph(f.originalPHInput[0]/1e5,f.originalPHInput[1]/1000)),c.originatingAdapterPH);
   const s=r.calls[0].raw.values,ph=c.originatingRawPH.values;
   r.canonical={p:s.p-f.originalPHInput[0],h:s.h-f.originalPHInput[1],T:s.T-ph.T};
   r.normalizedResiduals={mass:Math.abs((s.rho-input.rho)*input.V)/Math.max(.01,input.M),energy:Math.abs((s.u-input.u)*input.M/1000)/Math.max(1,Math.abs(input.U_kJ))};
   ok(Math.abs(r.canonical.p)<=.1&&Math.abs(r.canonical.h)<=.1&&Math.abs(r.canonical.T)<=1e-4);ok(r.normalizedResiduals.mass<=1e-11&&r.normalizedResiduals.energy<=1e-11);
   rows.push(r);
  }
  for(const c of control.falseAcceptance){const r={key:c.key,id:c.id,...replay(c.input.values)};equal(r.calls[0].raw,c.raw);equal(r.state,c.adapter);ok(r.state&&!r.error);
   r.qualificationBlocker='Historical inward-recovery mathematical outside hazard unchanged; no runtime certificate';falseAcceptance.push(r);}
  for(const c of control.matrix){const r={id:c.id,request:c.request,...replay(c.input.values)};
   equal(r.calls[0].raw,c.raw);if(c.error){ok(!r.state&&r.error);ok(r.error.evidence.propertyFailure.physicalTrajectoryExit==='unproved');}else equal(r.state,c.adapter);
   try{r.PH=pack(adapter.ph(c.request.values.p/1e5,c.request.values.h/1000));}catch(e){r.PHError=errorJSON(e);}
   if(c.request.values.p>3500000){ok(!r.PH&&r.PHError?.evidence.propertyFailure.reason==='explicit-unsupported-input');}
   if(c.adapterPH)equal(r.PH,c.adapterPH);else ok(r.PHError);matrix.push(r);
  }
  const cachedInput=rows[0].input.values;
  const realFailure=()=>{try{adapter.stateMVU(cachedInput.M,cachedInput.V,cachedInput.U_kJ,35);}catch(e){return e;}throw Error('expected refused fixture');};
  const historicalFailure=()=>{try{historicalAdapter(eos,guard).stateMVU(cachedInput.M,cachedInput.V,cachedInput.U_kJ,35);}catch(e){return e;}throw Error('expected historical refusal');};
  const mod={exports:{}};new Function('module','exports',args.a2Tests)(mod,mod.exports);
  const a2=mod.exports.runA2({sources:args.sources,controlSources:args.controlSources,engine:adapter,tableEngine:guard,realFailure,historicalFailure});
  // Exact error details survive explicit worker serialization and async throws.
  let asyncError;try{await Promise.resolve().then(()=>{throw realFailure();});}catch(e){asyncError=errorJSON(e);}equal(asyncError,errorJSON(realFailure()));
  // Alternating refused/reused supported calls; no stale error can affect success.
  const supported=control.matrix.find(r=>r.id==='B5-sweep-15').input.values;
  const historical=historicalAdapter(eos,guard),expected=pack(historical.stateMVU(supported.M,supported.V,supported.U_kJ,35));
  const memoryBefore=eos.memory(),heapBefore=performance.memory?.usedJSHeapSize??null;
  for(let i=0;i<40;i++){ok(realFailure().faultKind==='solver');equal(pack(adapter.stateMVU(supported.M,supported.V,supported.U_kJ,35)),expected);}
  const fresh=await loadEOS('candidateB');let freshResult;
  try{const a=createAdapter(fresh,guard);let e;try{a.stateMVU(cachedInput.M,cachedInput.V,cachedInput.U_kJ,35);}catch(x){e=errorJSON(x);}equal(e,errorJSON(realFailure()));
   freshResult=pack(a.stateMVU(supported.M,supported.V,supported.U_kJ,35));equal(freshResult,expected);}finally{fresh.dispose();}
  const perf=[];
  for(let round=0;round<5;round++)for(const [label,a]of (round%2? [['candidate',adapter],['control',historical]]:[['control',historical],['candidate',adapter]]))for(const [group,input]of [['success',supported],['rejected',cachedInput]]){
   const start=performance.now();let count=0,errors=0,checksum=0;
   do{try{checksum+=a.stateMVU(input.M,input.V,input.U_kJ,35).rho;}catch(e){errors++;}count++;}while(performance.now()-start<40&&count<1000);
   perf.push({round,label,group,count,errors,checksum,elapsedMS:performance.now()-start,memoryBytes:eos.memory()});
  }
  const workerStart=performance.now();let responsiveTicks=0;const responsiveTimer=setInterval(()=>responsiveTicks++,5);
  const worker=await new Promise((resolve,reject)=>{const w=new Worker(new URL('./worker.mjs',import.meta.url),{type:'module'}),t=setTimeout(()=>{w.terminate();reject(Error('worker deadline'));},30000);
   w.onmessage=e=>{if(e.data.ping){w.postMessage({...args,fixtures:args.fixtures.slice(0,1),supported});return;}clearTimeout(t);w.terminate();resolve(e.data);};w.onerror=e=>{clearTimeout(t);w.terminate();reject(Error(e.message));};});
  clearInterval(responsiveTimer);worker.elapsedMS=performance.now()-workerStart;worker.mainThreadTicks=responsiveTicks;
  ok(worker.passed);equal(worker.error,errorJSON(realFailure()));equal(worker.state,expected);
  // Existing focused PH / phase / signed finite-difference / cache controls.
  const {investigate}=await import('../browser_eos_b2/phase.mjs');
  const focusedControl=investigate(eos,args.focusedRequests),focusedCandidate=investigate({...eos,evaluate:q=>eos.evaluate(q)},args.focusedRequests);
  equal(focusedControl,focusedCandidate,'focused raw properties unchanged');
  const focusedAdapter=[];
  for(const q of focusedCandidate.rows)for(const [sample,z]of [['base',q.base],...q.probes.map(p=>[p.axis+':'+p.step,p.output])]){
   if(!z)continue;const p=z.p/1e5,h=z.h/1000,V=.003/5,M=z.state.rho*V,U_kJ=M*h-100*p*V;
   const a=pack(adapter.ph(p,h)),b=pack(historical.ph(p,h));equal(a,b,'focused PH adapter identity');
   let candidate,control;try{candidate={state:pack(adapter.stateMVU(M,V,U_kJ,p))};}catch(e){candidate={error:errorJSON(e)};}
   try{control={state:pack(historical.stateMVU(M,V,U_kJ,p))};}catch(e){control={error:errorJSON(e)};}
   equal(!!candidate.state,!!control.state);if(candidate.state)equal(candidate.state,control.state);else ok(candidate.error.evidence.propertyFailure.physicalTrajectoryExit==='unproved');
   const raw=eos.evaluate({mode:'DU',args:[M/V,(U_kJ/M)*1000]});
   focusedAdapter.push({id:q.id,sample,input:pack({M,V,U_kJ}),PH:a,candidate,control,raw:pack(raw),canonical:{p:raw.p-z.p,h:raw.h-z.h,T:raw.T-z.state.T}});
  }
  const {lifecycle}=await import('../browser_eos_b4c/lifecycle.mjs');
  // Only the established supported B4B PT cache control; rejected-PT cleanup
  // remains a separate issue and is deliberately not repaired here.
  const cache=lifecycle(eos,args.focusedRequests.filter(q=>q.id==='B1-vapor-regression'));
  return {passed:true,control,rows,matrix,falseAcceptance,a2,focused:focusedCandidate,asyncError,worker,
   focusedAdapter,cache,lifecycle:{alternations:40,freshReusedExact:true,memoryBefore,memoryAfter:eos.memory(),heapBefore,heapAfter:performance.memory?.usedJSHeapSize??null},perf,capabilities:eos.capabilities};
 }catch(error){return {passed:false,error:String(error),stack:error.stack,control,rows,matrix,falseAcceptance,a2Partial:error.a2Partial??null};}
 finally{eos.dispose();}
}
