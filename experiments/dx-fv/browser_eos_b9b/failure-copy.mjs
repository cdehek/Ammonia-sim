// Additional fault-path parity of accepted original versus observational copy.
// C1 classifications are tested separately with the original C1 scenario harness.
import {loader as original} from '../browser_eos_b9/accepted-bundle.mjs';
import {loader as isolated} from './diagnostic-bundle.mjs';
import {same,assert,diagnostic} from '../browser_eos_b9/values.mjs';
export function run(){
 const rows=[];
 const physical=s=>({spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
 for(const mode of ['original','isolated'])for(const scenario of ['transient','persistent','recordFailure','thermal200','thermal400']){
  const counters={};globalThis.__b9b={enter(name){counters[name]=(counters[name]||0)+1;return ()=>{};},count(name){counters[name]=(counters[name]||0)+1;},cache(){},note(){}};
  const load=mode==='original'?original():isolated(),table=load('engine.js').createEngine(load('properties.json'));
  let armed=false,inStage=false,remaining=2,before,ids,state;const attempts=[],keys=new Set(),limit=scenario==='thermal200'?200:scenario==='thermal400'?400:null;
  const refusal=()=>Object.assign(Error('B9B synthetic table property refusal; no physical-trajectory claim'),{faultKind:'solver'});
  const engine={...table,ph(...a){if(armed&&inStage&&scenario==='transient'&&remaining>0){remaining--;throw refusal();}return table.ph(...a);},stateMVU(...a){if(armed&&(scenario==='recordFailure'||scenario==='persistent'&&!keys.has(JSON.stringify(a.slice(0,3)))))throw refusal();return table.stateMVU(...a);}};
  const implicit=load('coupled-implicit.cjs'),N=implicit.coupledNewton;implicit.coupledNewton=(...a)=>{inStage=true;try{return N(...a);}finally{inStage=false;}};
  let rejected=0;const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>{if(armed&&a.failure){rejected++;assert(same(physical(state),before),'accepted-copy rollback bits');assert(state.cells===ids.cells&&state.energies===ids.energies&&state.ledger===ids.ledger&&state.cells.every((c,i)=>c===ids.sections[i]),'accepted-copy rollback references');}attempts.push(a);});
  state=model.create(limit?{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:0}}:{});
  model.advance(state,.0001);model.update(state,{airLoadKW:limit?(limit===200?-1:1):1.5});state.nextStepSeconds=.001;
  for(const c of state.cells)keys.add(JSON.stringify([c.massKg,c.volumeM3,c.internalEnergyKJ]));
  before=structuredClone(physical(state));ids={cells:state.cells,sections:[...state.cells],energies:state.energies,ledger:state.ledger};armed=true;let record,error;
  try{record=model.advance(state,.001);}catch(e){error=diagnostic(e);}
  if(scenario==='transient')assert(rejected===2&&state.seconds===.0011,'accepted-copy transient');
  else{assert(same(physical(state),before),'accepted-copy final rollback');assert(rejected===20,'accepted-copy 20 attempts');assert(limit?state.stop.kind==='domain'&&state.stop.evidence.confirmed:state.stop.kind==='solver'&&!state.stop.evidence.confirmed,'accepted-copy stop');}
  rows.push({mode,scenario,synthetic:!limit,rejected,state:structuredClone(state),record,error,attempts,counters,floor:model.settings.minStep,maxIterations:model.settings.maxIterations,exactRollback:true});
 }
 for(const scenario of ['transient','persistent','recordFailure','thermal200','thermal400']){
  const [a,b]=rows.filter(r=>r.scenario===scenario);assert(same({...a,mode:null,counters:null},{...b,mode:null,counters:null}),'accepted-copy full failure parity '+scenario);
 }
 return {passed:true,rows,notC1Qualification:true};
}
