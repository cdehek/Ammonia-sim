// Compact B13 failure contract, replayed through original A2, B9C and observations.
import fs from'node:fs';import{loader as candidate}from'../browser_eos_b9c/candidate-bundle.mjs';import{loader as control}from'../browser_eos_b9c/control-bundle.mjs';
import{instrument}from'./instrument.mjs';import{same,exact,assert,auditRecord,diagnostic}from'../browser_eos_b9/values.mjs';
const noop=()=>()=>{};
globalThis.__b9c={enter:noop,count(){},section(){},boundary(side,p,h,fn){return fn();},property(method,fn,args){return fn(...args);}};
globalThis.__b14={enter:noop,column:noop,matrix(){},temporal(){},controller(){},committed(){},probe(){}};
const observed=(await import('data:text/javascript;base64,'+Buffer.from(instrument().src).toString('base64'))).loader;
function witness(loader){
 const load=loader(),engine=load('table-only.cjs').createTableEngine(),attempts=[];
 const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a));
 const state=model.create({sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:200,finProfileK:200,airInitialK:200,airLoadKW:0},schedule:[{seconds:.0001,patch:{airLoadKW:-1}}]});
 const initial=model.record(state),result=model.advance(state,.0002);
 assert(state.seconds===.0001&&state.acceptedSteps>0,'earlier committed progress lost');assert(state.stop?.kind==='domain'&&state.stop.evidence.confirmed,'genuine domain refusal');
 const before=structuredClone(state),again=model.advance(state,.0001);assert(same(before,state)&&same(again,result),'stopped state changed');
 assert(same(state.cells,state.initialCells)&&same(state.energies,state.initialEnergies),'unaccepted state leaked');const audit=auditRecord(result);
 const live=model.create(load('coupled-fixtures.cjs').fixture('cold')),liveBefore=structuredClone(live);let error;
 try{model.update(live,{inlet:{p:.29,h:500}});}catch(e){error=diagnostic(e);}assert(error&&same(live,liveBefore),'invalid update rollback');
 return{initial,result,state,attempts,audit,stoppedRepeatUnchanged:true,earlierAcceptedProgressPreserved:true,invalidUpdate:{error,unchanged:true}};
}
const c=witness(candidate),a=witness(control),o=witness(observed);assert(same(c,a)&&same(c,o),'domain/failure equivalence');
console.log(JSON.stringify({passed:true,scope:'Separately labeled exact-boundary thermal-domain witness, B13 inputs unchanged',canonicalA2B9CObservedBitExact:true,witness:exact(c),resource:process.resourceUsage()}));
