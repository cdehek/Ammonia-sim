// Separate support-boundary contract witness; not a normal-fixture horizon run.
import fs from 'node:fs';
import {loader as candidate} from '../browser_eos_b9c/candidate-bundle.mjs';
import {loader as control} from '../browser_eos_b9c/control-bundle.mjs';
import {same,exact,assert,auditRecord,diagnostic} from '../browser_eos_b9/values.mjs';
function witness(loader){
 const load=loader(),engine=load('table-only.cjs').createTableEngine(),attempts=[];
 const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a));
 const state=model.create({sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:200,finProfileK:200,airInitialK:200,airLoadKW:0},schedule:[{seconds:.0001,patch:{airLoadKW:-1}}]});
 const initial=model.record(state),result=model.advance(state,.0002);
 assert(state.seconds===.0001&&state.acceptedSteps>0,'earlier committed progress lost');
 assert(state.stop?.kind==='domain'&&state.stop.evidence.confirmed,'genuine outward thermal domain refusal required');
 const before=structuredClone(state),again=model.advance(state,.0001);
 assert(same(before,state)&&same(again,result),'stopped state changed');
 // The sealed zero-exchange fixture is physically unchanged before the load event.
 assert(same(state.cells,state.initialCells)&&same(state.energies,state.initialEnergies),'unaccepted state leaked');
 const audit=auditRecord(result);
 const live=model.create(load('coupled-fixtures.cjs').fixture('cold')),liveBefore=structuredClone(live);let error;
 try{model.update(live,{inlet:{p:.29,h:500}});}catch(e){error=diagnostic(e);}
 assert(error&&same(live,liveBefore),'invalid update rollback changed');
 return {initial,result,state,attempts,audit,stoppedRepeatUnchanged:true,earlierAcceptedProgressPreserved:true,invalidUpdate:{error,unchanged:true}};
}
const c=witness(candidate),a=witness(control);assert(same(c,a),'A2/B9C domain contract mismatch');
fs.writeFileSync(new URL('./evidence/domain-and-rollback.json',import.meta.url),JSON.stringify({passed:true,scope:'Sealed zero-exchange exact-200K thermal support witness; no solver settings changed; not normal cold/warm progression',sameEngineAcceptedA2BitExact:true,witness:exact(c)},null,2)+'\n');
console.log('PASS: genuine domain refusal after committed 0.0001 s; exact rollback and stopped repeat; A2/B9C bit equality');
