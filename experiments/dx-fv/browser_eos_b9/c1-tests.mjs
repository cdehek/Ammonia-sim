import {loader} from './accepted-bundle.mjs';
import {sources,controlSources,runA2} from './c1-bundle.mjs';
import {createAdapter} from '../browser_eos_b5b_c1/adapter.mjs';
import {assert,same,diagnostic,exact} from './values.mjs';
export async function local(){
 const load=loader(),table=load('engine.js').createEngine(load('properties.json'));
 // This is deliberately synthetic. It exercises the actual C1 wrapper, not a
 // claim that table physics naturally encounters an experimental EOS refusal.
 const synthetic=createAdapter({evaluate(){throw Error('B9 synthetic EOS refusal; no physical trajectory claim');}},table);
 const failure=(...a)=>{try{synthetic.stateMVU(...(a.length?a:[.01,.003/5,5,3.5]));}catch(e){return e;}throw Error('Expected C1 refusal');};
 const original=runA2({sources,controlSources,engine:table,tableEngine:table,realFailure:()=>failure()});assert(original.passed);
 // Additional bit-exact and identity checks within THIS authoritative realm.
 const cache={};function require(name){const k=name.replace(/^\.\//,'');if(cache[k])return cache[k].exports;assert(Object.hasOwn(sources,k));const m={exports:{}};cache[k]=m;new Function('module','exports','require',sources[k])(m,m.exports,require);return m.exports;}
 const F=require('./coupled-model.cjs').createCoupledModel;
 let armed=false,before,ids;const attempts=[];
 const engine={...table,stateMVU(...a){if(armed)throw failure(...a);return table.stateMVU(...a);}};
 const accepted=s=>({spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
 const model=F(engine,{trace:true,timestepGrowth:'failure-aware'},a=>{if(armed&&a.failure){assert(same(accepted(state),before),'binary64 rollback');assert(state.cells===ids.cells&&state.energies===ids.energies&&state.ledger===ids.ledger,'rollback identities');assert(state.cells.every((c,i)=>c===ids.sections[i]),'individual cell identities');attempts.push(a);}});
 const state=model.create();model.advance(state,.0001);model.update(state,{airLoadKW:1.5});state.nextStepSeconds=.001;
 before=structuredClone(accepted(state));ids={cells:state.cells,sections:[...state.cells],energies:state.energies,ledger:state.ledger};armed=true;let error;
 try{model.advance(state,.001);}catch(e){error=e;}
 assert(error?.recordFailure&&!error.recordFailure.propertyStatesReturned,'failed record must not invent properties');assert(attempts.length===20,'20 attempts');assert(state.stop.kind==='solver'&&!state.stop.evidence.confirmed,'numerical refusal');
 attempts.forEach((a,i)=>{if(i)assert(a.trialSeconds===attempts[i-1].trialSeconds/2,'halving');});assert(same(accepted(state),before),'final exact rollback');assert(state.nextStepSeconds===.001,'proposal identity');
 return {passed:true,syntheticFault:true,actualUnchangedC1Wrapper:true,original:diagnostic(original),exactRollback:{everyRejectedTrial:true,attempts:diagnostic(attempts),allPhysicalBits:true,objectIdentityInThisRealm:true,recordRefused:diagnostic(error),lastAccepted:exact(before),stop:diagnostic(state.stop)},fullA2Qualification:false};
}
export async function run(mode='both'){
 const main=mode==='worker'?null:await local();
 if(mode==='main')return main;
 const {probe}=await import('./probe-client.mjs');const worker=await probe('c1');assert(worker.success,'worker C1 '+JSON.stringify(worker.error));
 if(main){const strip=v=>{const copy=structuredClone(v);for(const r of copy.original.rows){delete r.candidateMS;delete r.controlMS;delete r.elapsedMS;}return copy;};assert(same(strip(main),strip(worker.result)),'C1 main/worker values');}
 return {passed:true,main,worker:worker.result};
}
