// Optional property subset only: never an EOS-backed A2 campaign.
import {loadQualifiedEOS} from '../browser_eos_b7/loader.mjs';
import {createAdapter} from '../browser_eos_b5b_c1/adapter.mjs';
import {loader} from './accepted-bundle.mjs';
import {assert,same,exact,diagnostic} from './values.mjs';
const read=async path=>{const r=await fetch(new URL(path,import.meta.url));assert(r.ok,'fixture fetch '+path);return r.json();};
export async function local(){
 const artifacts=await read('../browser_eos_b7/evidence/artifacts-with-diagnostics.json'),inputs=await read('../browser_eos_b7/evidence/fixed-inputs.json');
 const engine=/Chrome/.test(navigator.userAgent)?'chromium':'webkit';
 const historical=await read('../browser_eos_b7/evidence/activation-'+engine+'.json');
 const failures=(await read('../browser_eos_b5/evidence/original-failures.json')).rows.filter(r=>r.runtime===engine);
 const pt=(await read('../browser_eos_b6/evidence/historical-rejected-pt.json')).find(r=>r.engine===engine);
 const load=loader(),guard=load('engine.js').createEngine(load('properties.json')),rows=[];
 for(const fullVLE of [false,true]){
 const opts={fullVLE,events:[]},e=await loadQualifiedEOS(artifacts.gateA,opts),adapter=createAdapter(e,guard),states=[];
 const baseline=opts.runtimeStatus();
 try{
 const ph=e.evaluate({mode:'PH',args:[350000,500000]}),V=.003/5,M=ph.rho*V,U_kJ=M*(ph.h/1000)-100*(ph.p/1e5)*V;
 const du=e.evaluate({mode:'DU',args:[M/V,(U_kJ/M)*1000]}),sat=e.evaluate({mode:'SAT',args:[350000,0]}),mix={...e.evaluate({mode:'PQ',args:[350000,.4]}),phase:e.state.keyed_output(e.module.parameters.iPhase)};
 assert(Math.abs(du.p-ph.p)<=.1&&Math.abs(du.h-ph.h)<=.1&&Math.abs(du.T-ph.T)<=1e-4,'original canonical limits');assert(mix.Q>=0&&mix.Q<=1&&mix.phase===6,'genuine coexistence');
 // Actual complete adapter operations as distinct from raw finite returns.
 const supported={ph:adapter.ph(3.5,500),du:adapter.stateMVU(M,V,U_kJ,3.5),sat:adapter.sat(3.5)};
 states.push({test:'supported-PH-DU-saturation-coexistence',passed:true,ph,du,sat,mix,supported,inventory:{M,V,U_kJ}});
 if(fullVLE){
 const old=historical.result.rows.find(r=>r.base==='gateA'&&r.fullVLE).normal;
 for(const n of [146,151,152]){const f=inputs.find(r=>r.key==='native-ledger-'+n),x=f.input.values,raw={...e.evaluate({mode:'DU',args:[x.rho,x.u]}),phase:e.state.keyed_output(e.module.parameters.iPhase)};
 const expected=old.find(r=>r.key===f.key).reused.state.values;assert(same(raw,expected),'qualified liquid original bits '+n);assert(raw.phase===0&&raw.Q===10000,'original homogeneous liquid sentinel');
 states.push({test:'qualified-Gate-A-liquid',key:f.key,input:f.input,raw,originalQualificationOnly:true,completeBackendQualification:false});}
 const f=inputs.find(r=>r.key==='native-ledger-148');let err;try{e.evaluate({mode:'DU',args:[f.input.values.rho,f.input.values.u]});}catch(z){err=diagnostic(z);}assert(err,'expected unresolved endpoint refusal');states.push({test:'unresolved-endpoint',key:f.key,input:f.input,error:err,scientificallyQualified:false});
 }else{
 const f=failures[0],x=f.fixedInput.values;let error;try{adapter.stateMVU(x.M,x.V,x.U_kJ,35);}catch(z){error=diagnostic(z);}assert(error?.faultKind==='solver'&&error.evidence.propertyFailure.reason==='boundary-unresolved','historical boundary refusal');states.push({test:'historical-35bar-C1-refusal',key:f.fixedKey,input:f.fixedInput,error,physicalTrajectoryExit:'unproved'});
 }
 const before={...opts.runtimeStatus(),stack:e.stackPointer()};let native;try{e.evaluate(pt.request);}catch(z){native=diagnostic(z);}assert(native?.nativeException?.cleanup==='generated-begin/end-catch','native owned exception');
 const after={...opts.runtimeStatus(),stack:e.stackPointer()};assert(before.uncaught===after.uncaught&&before.observedCatchDepth===after.observedCatchDepth&&before.stack===after.stack,'native stack/catch bookkeeping');
 const supportedAfter=e.evaluate({mode:'PH',args:[350000,500000]});assert(same(ph,supportedAfter),'supported after rejected PT');states.push({test:'actual-native-PT-error-supported-followup',request:pt.request,native,before:{uncaught:before.uncaught,observedCatchDepth:before.observedCatchDepth},after:{uncaught:after.uncaught,observedCatchDepth:after.observedCatchDepth},stackDelta:after.stack-before.stack,supportedAfter});
 // Clearly injected dispatch to a real native PT refusal, through actual C1.
 const injected=createAdapter({evaluate(q){return q.mode==='DU'?e.evaluate(pt.request):e.evaluate(q);}},guard);let error;try{injected.stateMVU(M,V,U_kJ,3.5);}catch(z){error=diagnostic(z);}assert(error?.faultKind==='solver'&&error.evidence.propertyFailure.physicalTrajectoryExit==='unproved','C1 native fault transport');
 states.push({test:'C1-actual-PT-dispatch-injection',syntheticDispatch:true,trueNativeRequest:pt.request,error,naturalPlantReachabilityProved:false});
 const final=opts.runtimeStatus();assert(final.uncaught===baseline.uncaught&&final.observedCatchDepth===baseline.observedCatchDepth,'catch baseline');
 rows.push({fullVLE,identity:artifacts.gateA,init:e.init,memory:e.memory(),baseline,final,states,exceptionEvents:opts.events.map(v=>({kind:v.kind,stage:v.stage,referenceCount:v.header?.referenceCount,caught:v.header?.caught,rethrown:v.header?.rethrown,uncaught:v.uncaught,observedCatchDepth:v.observedCatchDepth}))});
 }finally{e.dispose();}
 }
 // Disposal/restart plus real failed WASM fetch and identity refusal.
 const restarted=await loadQualifiedEOS(artifacts.gateA);try{assert(same(restarted.evaluate({mode:'PH',args:[350000,500000]}),rows[0].states[0].ph),'restart state');}finally{restarted.dispose();}
 let fetchError;try{await loadQualifiedEOS(artifacts.gateA,{wasmURL:'../browser_eos_b9/missing.wasm'});}catch(e){fetchError=diagnostic(e);}assert(fetchError?.message.includes('HTTP 404'),'WASM fetch failure');
 return {passed:true,engine,qualification:'EXPERIMENTAL COOLPROP — NOT SCIENTIFICALLY QUALIFIED as complete backend',rows,restart:true,failedFetch:fetchError,noDPInvoked:true,noA2Campaign:true};
}
export async function run(){const main=await local();const {probe}=await import('./probe-client.mjs');const worker=await probe('b7');assert(worker.success,'B7 worker '+JSON.stringify(worker.error));
 const scientific=v=>v.rows.map(r=>({fullVLE:r.fullVLE,states:r.states.map(s=>{const x=structuredClone(s);delete x.before;delete x.after;return x;})}));assert(same(scientific(main),scientific(worker.result)),'B7 main/worker exact scientific subset');return {passed:true,exactMainWorkerSubset:true,main,worker:worker.result};}
