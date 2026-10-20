import {loader as control} from './control-bundle.mjs';
import {loader as candidate} from './candidate-bundle.mjs';
import {loader as dc} from './regress-control-bundle.mjs';
import {loader as dp} from './regress-candidate-bundle.mjs';
import {assert,same,exact,diagnostic,auditRecord} from '../browser_eos_b9/values.mjs';
export {same,exact};
const now=()=>performance.now();
export async function digest(v){const raw=new TextEncoder().encode(JSON.stringify(exact(v)));return [...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function probe(){
 const stack=[],out={counts:{},public:{},section:{requests:0,hits:0,misses:0},boundaries:[],properties:[],residuals:[],linear:[],solves:[],times:{},stageCount:0,trialCount:0,recordCount:0};let role=null,request=null;
 const stage=()=>stack.findLast(f=>f.label==='stage')?.id??null;
 const count=k=>out.counts[k]=(out.counts[k]||0)+1;
 const p={out,count,enter(label){const f={label,id:label==='stage'?++out.stageCount:label==='trial'?++out.trialCount:label==='record'?++out.recordCount:null,t:now()};stack.push(f);return ()=>{assert(stack.pop()===f,'scope stack');out.times[label]=(out.times[label]||0)+now()-f.t;};},
  section(hit){out.section.requests++;out.section[hit?'hits':'misses']++;},
  boundary(side,p,h,fn){const previousRole=role,previousRequest=request;role=side;request=out.boundaries.length;const row={id:request,stage:stage(),side,p,h};out.boundaries.push(row);const n=out.public.ph||0;
   try{const value=fn();row.value=value;return value;}catch(e){row.error=diagnostic(e);throw e;}finally{row.realPH=(out.public.ph||0)-n;role=previousRole;request=previousRequest;}},
  property(method,fn,args){out.public[method]=(out.public[method]||0)+1;const row={method,args,stage:stage(),role,request};out.properties.push(row);const t=now();try{const result=fn(...args);row.result=result;return result;}catch(e){row.error=diagnostic(e);throw e;}finally{out.times['property.'+method]=(out.times['property.'+method]||0)+now()-t;}}
 };globalThis.__b9c=p;return p;
}
export function setup(mode,observed=false,options={}){
 const p=observed?probe():null,load=(observed?(mode==='control'?dc:dp):(mode==='control'?control:candidate))();
 const engine=load('table-only.cjs').createTableEngine();
 if(observed){
  const linear=load('implicit.cjs'),L=linear.solveLinear;linear.solveLinear=(matrix,rhs)=>{const delta=L(matrix,rhs);p.out.linear.push({matrix,rhs,delta});return delta;};
  const implicit=load('coupled-implicit.cjs'),N=implicit.coupledNewton;
  implicit.coupledNewton=(evaluate,initial,variables,settings,work,columns)=>{
   const row={initial,variables,context:work.diagnosticContext};p.out.solves.push(row);
   try{const result=N(x=>{const end=p.enter('residual');try{const value=evaluate(x);p.out.residuals.push({x,value});return value;}finally{end();}},initial,variables,settings,work,columns);row.result=result;return result;}catch(e){row.error=diagnostic(e);throw e;}
  };
 }
 const attempts=[],model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware',...options},a=>attempts.push(a));
 return {load,engine,model,attempts,p};
}
export async function workload(mode,fixture,observed=false){
 const construction=now(),s=setup(mode,observed),constructionMS=now()-construction;
 const config=s.load('coupled-fixtures.cjs').fixture(fixture),t=now(),state=s.model.create(config),initial=s.model.record(state),initializationMS=now()-t,rows=[{state:structuredClone(state),record:initial,attempts:null}],timing=[];
 for(const duration of [.0001,.0004,.0005]){
  const a0=s.attempts.length,t=now(),record=s.model.advance(state,duration),advanceMS=now()-t;
  rows.push({state:structuredClone(state),record,attempts:structuredClone(s.attempts.slice(a0))});
  const r0=now(),snapshot=s.model.record(state),recordMS=now()-r0;assert(same(snapshot,record),'record purity');timing.push({duration,advanceMS,recordMS});
 }
 const science={rows,attempts:s.attempts},scienceHash=await digest(science),checkpointHashes=await Promise.all(rows.map(row=>digest({record:row.record,state:row.state})));
 const result={mode,fixture,observed,constructionMS,initializationMS,timing,scienceHash,checkpointHashes,audits:rows.map(r=>auditRecord(r.record)),work:{residuals:state.attemptedResidualEvaluations,corrections:state.attemptedIterations,accepted:state.acceptedSteps,rejected:state.rejectedSteps},settings:s.model.settings};
 if(observed){
  result.science=exact(science);
  result.componentHashes={};for(const key of ['residuals','linear','solves'])result.componentHashes[key]=await digest(s.p.out[key]);
  // Full per-evaluation rates/inventories are hashed above; retain raw coordinates,
  // residuals, full matrices/corrections and complete stage outcomes separately.
  s.p.out.residuals=s.p.out.residuals.map(({x,value})=>({x,residual:value.residual}));
  result.evidence=exact(s.p.out);
 }
 return result;
}
export async function regressions(mode){
 const unit=await(await import('../browser_eos_b9c/cache-unit.mjs')).run();
 const cases=[],base=setup(mode),sat=base.engine.sat(4);
 assert(Object.isFrozen(base.engine)&&Object.isFrozen(base.load('properties.json'))&&Object.isFrozen(base.load('properties.json').sat[0]),'owned table frozen');
 const scenarios=[
  {name:'flow-reversal',config:{},update:{inlet:{p:3,h:600},outlet:{p:4,h:1700}}},
  {name:'scheduled-boundary',config:{schedule:[{seconds:.0001,patch:{inlet:{p:4.2,h:550},outlet:{p:3.4,h:1650}}}]}},
  {name:'manual-boundary',config:{},update:{inlet:{p:4.2,h:550},outlet:{p:3.4,h:1650}}},
  ...[0,1,.4].map(x=>({name:'saturated-'+x,config:{inlet:{p:4,h:sat.hf+(sat.hg-sat.hf)*x},outlet:{p:4,h:sat.hf+(sat.hg-sat.hf)*x}}})),
  {name:'superheated-outlet',config:{outlet:{p:3.5,h:1700}}},
  ...[200,400].map(k=>({name:'thermal-'+k,config:{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:k,finProfileK:k,airInitialK:k,airLoadKW:0}},update:{airLoadKW:k===200?-1:1}})),
  {name:'numerical-stop',config:{},options:{maxIterations:1,maxAttempts:20}},
 ];
 for(const scenario of scenarios){
  const s=setup(mode,true,scenario.options),state=s.model.create(scenario.config),records=[s.model.record(state)];let error;
  records.push(s.model.advance(state,.0001));
  if(scenario.update&&!state.stop)records.push(s.model.update(state,scenario.update));
  const before=structuredClone(physical(state)),ids={cells:state.cells,energies:state.energies,ledger:state.ledger};
  try{records.push(s.model.advance(state,.0001));}catch(e){error=diagnostic(e);}
  if(scenario.name.startsWith('thermal-')){assert(state.stop?.kind==='domain'&&state.stop.evidence.confirmed,'thermal genuine stop');assert(same(physical(state),before),'thermal rollback');assert(state.cells===ids.cells&&state.energies===ids.energies&&state.ledger===ids.ledger,'thermal identity rollback');}
  if(scenario.name==='flow-reversal'){
   const a=records[1].fluxes.faces,b=records[2].fluxes.faces;
   assert(a[0].massKgS>0&&b[0].massKgS<0&&b.at(-1).massKgS<0,'actual reversal');
   assert(b.at(-1).energyKW===b.at(-1).massKgS*1700,'reversed outlet donor');
  }
  if(scenario.name==='scheduled-boundary')assert(state.scheduleIndex===1&&state.boundaryEvents.length===1&&state.boundaryEvents[0].seconds===.0001&&state.boundaryEvents[0].scheduled&&state.spec.fluid.inlet.p===4.2,'scheduled patch actually applied');
  if(scenario.name==='manual-boundary')assert(state.boundaryEvents.length===1&&!state.boundaryEvents[0].scheduled&&state.spec.fluid.outlet.p===3.4,'manual patch actually applied');
  if(scenario.name==='numerical-stop')assert(state.stop?.kind==='solver','numerical stop remains numerical');
  const componentHashes={};for(const key of ['residuals','linear','solves'])componentHashes[key]=await digest(s.p.out[key]);
  const metrics=s.p.out;
  const logicalBoundaryHash=await digest(metrics.boundaries.map(({realPH,...b})=>b));
  const evidence={counts:metrics.counts,public:metrics.public,section:metrics.section,stageCount:metrics.stageCount,trialCount:metrics.trialCount,logicalBoundaryHash,boundaryRequests:metrics.boundaries.length,stageRequests:metrics.boundaries.filter(b=>b.stage!==null).length,stageMisses:metrics.boundaries.filter(b=>b.stage!==null&&b.realPH===1).length,stageHits:metrics.boundaries.filter(b=>b.stage!==null&&b.realPH===0).length,thrown:metrics.properties.filter(p=>p.error).map(p=>({method:p.method,args:p.args,error:p.error}))};
  cases.push({name:scenario.name,state:structuredClone(state),records,error,attempts:s.attempts,audits:records.map(auditRecord),componentHashes,evidence});
 }
 const property=[];
 for(const p of [.3-1e-12,.3,.3+1e-12,35-1e-12,35,35+1e-12,NaN,Infinity,-Infinity,-0,0]){
  let h=500;try{const a=base.engine.sat(p);h=(a.hf+a.hg)/2;}catch{}
  property.push(propertyCase(mode,'pressure',p,h));
 }
 const a=base.engine.sat(4),hot=base.engine.statePT(4,a.T+250).h,cool=base.engine.statePT(4,a.T-30,'liquid').h;
 for(const h of [a.hf-1e-7,a.hf-1e-9,a.hf,a.hf+1e-9,a.hg-1e-9,a.hg,a.hg+1e-9,a.hg+1e-7,hot,hot+1,hot-1,cool,cool-1,cool+1,-1e9,1e9,NaN,Infinity,-0,0])property.push(propertyCase(mode,'enthalpy/phase',4,h));
 // Supported update path refuses before changing spec, accepted inventories or events.
 const invalidUpdates=[];
 for(const patch of [{inlet:{p:.3-1e-12,h:500}},{outlet:{p:35+1e-12,h:1700}},{inlet:{p:4,h:1e9}},{outlet:{p:4,h:-1e9}}]){
  const s=setup(mode),state=s.model.create({}),before=structuredClone(state);let error;
  try{s.model.update(state,patch);}catch(e){error=diagnostic(e);}assert(error&&same(state,before),'invalid update exact rollback');invalidUpdates.push({patch,error,unchanged:true});
 }
 let rejectedBackend=false;
 const cl=candidate(),unowned=cl('engine.js').createEngine(cl('properties.json'));
 try{cl('coupled-model.cjs').createCoupledModel(unowned);}catch(e){rejectedBackend=e.message==='B9C requires its owned original table engine.';}assert(rejectedBackend,'reject unowned backend');
 let missingRegion;try{base.engine.statePT(.3,base.engine.sat(.3).T-30,'liquid');}catch(e){missingRegion=diagnostic(e);}assert(missingRegion?.message==='Liquid state below the property table temperature limit.','original missing region refusal');
 return {mode,cases:exact(cases),property:exact(property),invalidUpdates:exact(invalidUpdates),missingRegion,rejectedBackend,unit,ownedTableFrozen:true,passed:true};
}
function propertyCase(mode,category,p,h){
 const s=setup(mode),thermo=s.load('thermodynamics.cjs').createThermodynamics(s.engine);let result,error;
 try{result=thermo.ph(p,h);const repeat=thermo.ph(p,h);assert(same(result,repeat),'determinism');assert(Object.values(result).every(v=>v===null||typeof v!=='object'),'flat PH shape');}catch(e){error=diagnostic(e);}
 return {category,p,h,result,error};
}
export function physical(s){return {spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps};}
export async function c1(){
 const original=await(await import('../browser_eos_b9/c1-tests.mjs')).local();
 const {c1Session}=await import('../browser_eos_b9a/c1-session.mjs'),rows=[];
 for(const scenario of ['transient','persistent','boundary','recordFailure','thermal200','thermal400']){
  const s=setup('control'),attempts=[],session=c1Session(s.engine,scenario,a=>attempts.push(a));let record,error;
  try{record=session.model.advance(session.state,.001);}catch(e){error=diagnostic(e);}
  const proof=session.proof();assert(scenario==='transient'?proof.failures===2:proof.acceptedBitsUnchanged&&proof.identityUnchanged,'C1 integrity');rows.push({scenario,proof,record,error,attempts});
 }
 return {passed:true,unchangedC1:true,original,rows};
}
