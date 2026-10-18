import {sources} from '../browser_eos_b9/c1-bundle.mjs';
import {createAdapter} from '../browser_eos_b5b_c1/adapter.mjs';
import {same,assert,diagnostic,exact} from './values.mjs';
const accepted=s=>({spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
export function c1Session(table,scenario,observe){
 let stage=false,armed=false,remaining=scenario==='transient'?2:Infinity,state,before,ids,failures=0;
 const refusal=createAdapter({evaluate(){if(scenario==='boundary')return {p:3500001,h:500000,T:300,s:2000,rho:20,u:480000,Q:.1};throw Error('B9A synthetic C1 property refusal; not natural trajectory evidence');}},table);
 const fail=(...args)=>{try{return refusal.stateMVU(...(args.length?args:[.01,.003/5,5,3.5]));}catch(e){return e;}};
 const persistent=['persistent','boundary','recordFailure'].includes(scenario),keys=new Set();
 const engine={...table,ph(...a){if(armed&&stage&&remaining>0){remaining--;throw fail();}return table.ph(...a);},stateMVU(...a){if(armed&&persistent&&(scenario==='recordFailure'||!keys.has(JSON.stringify(a.slice(0,3)))))throw fail(...a);return table.stateMVU(...a);}};
 const cache={};function require(n){const k=n.replace(/^\.\//,'');if(cache[k])return cache[k].exports;const m={exports:{}};cache[k]=m;assert(Object.hasOwn(sources,k));new Function('module','exports','require',sources[k])(m,m.exports,require);if(k==='coupled-implicit.cjs'){const f=m.exports.coupledNewton;m.exports.coupledNewton=(...a)=>{stage=true;try{return f(...a);}finally{stage=false;}};}return m.exports;}
 const model=require('./coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>{if(armed&&a.failure){failures++;assert(same(accepted(state),before),'STOP C1 exact rollback');assert(state.cells===ids.cells&&state.energies===ids.energies&&state.ledger===ids.ledger,'STOP C1 rollback references');assert(state.cells.every((c,i)=>c===ids.sections[i]),'STOP C1 cells');}observe(a);});
 const limit=scenario==='thermal200'?200:scenario==='thermal400'?400:null;
 state=model.create(limit?{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:0}}:{});
 model.advance(state,.0001);model.update(state,{airLoadKW:limit?(limit===200?-1:1):1.5});state.nextStepSeconds=.001;
 for(const c of state.cells)keys.add(JSON.stringify([c.massKg,c.volumeM3,c.internalEnergyKJ]));
 const record=model.record(state);before=structuredClone(accepted(state));ids={cells:state.cells,sections:[...state.cells],energies:state.energies,ledger:state.ledger};armed=true;
 return {model,state,record,proof:()=>({scenario,synthetic:!limit,failures,acceptedBitsUnchanged:same(accepted(state),before),identityUnchanged:state.cells===ids.cells&&state.energies===ids.energies&&state.ledger===ids.ledger,lastAccepted:exact(before),stop:diagnostic(state.stop),floor:model.settings.minStep,maxIterations:model.settings.maxIterations,physicalTrajectoryClaim:!!limit})};
}
