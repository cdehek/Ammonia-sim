'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createEvaporator}=require('./evaporator.cjs'),{cases,spec,accuracyOptions}=require('./time-cases.cjs');
const direct=require(process.env.DX_FV_TIME_REFERENCE_PATH||'./time-reference.json');
const methods=['backward-euler','trapezoid','tr-bdf2'],scenarios=cases(engine);
const report={sectionCount:3,selectedMethod:'tr-bdf2',referenceMethod:'tr-bdf2 adaptive 1e-8 with trapezoid cross-check',scenarios:[],refinement:[],independentReference:{source:direct.source},failures:[],performance:[]};
function check(r){
 assert.equal(r.sectionCount,3);assert(!r.stop,JSON.stringify(r.stop));assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);
 r.sectionResiduals.forEach(v=>{assert(Math.abs(v.massKg)<1e-8);assert(Math.abs(v.energyKJ)<1e-6);});
 if(r.integration.adaptive)assert(r.lastTimeError<=1);
 r.sections.forEach(v=>{assert(Number.isFinite(v.p)&&Number.isFinite(v.h)&&Number.isFinite(v.T));assert(v.massKg>0);});return r;
}
function result(r){return {seconds:r.seconds,sections:r.sections.map(v=>({p:v.p,h:v.h,T:v.T})),terminal:r.terminal,events:r.events,massResidualKg:r.massResidualKg,energyResidualKJ:r.energyResidualKJ,steps:r.acceptedSteps,rejected:r.rejectedSteps,accuracyRejected:r.accuracyRejectedSteps,eventRejected:r.eventRejectedSteps,calls:r.attemptedResidualEvaluations,minStep:r.minAcceptedStepSeconds,maxStep:r.maxAcceptedStepSeconds};}
function run(c,method,options){
 const model=createEvaporator(engine,{method,minStep:1e-9,...options}),state=model.create(c.config),rows=[],start=performance.now();let change=0;
 for(const target of [...new Set([0,...c.samples,...c.changes.map(v=>v.seconds)])].sort((a,b)=>a-b)){
  if(target>state.seconds)check(model.advance(state,target-state.seconds));
  if(c.samples.includes(target))rows.push(result(model.record(state)));
  while(change<c.changes.length&&c.changes[change].seconds===target){const before=JSON.stringify(state.cells),ledger=JSON.stringify(state.ledger),seconds=state.seconds;model.update(state,c.changes[change++].patch);assert.equal(JSON.stringify(state.cells),before);assert.equal(JSON.stringify(state.ledger),ledger);assert.equal(state.seconds,seconds);}
 }
 const final=check(model.record(state));
 return {rows,final:result(final),elapsedMS:performance.now()-start,model,state};
}
function differences(a,b){
 const errors={pressureBar:0,enthalpyKJkg:0,temperatureK:0,eventSeconds:0};
 a.rows.forEach((row,j)=>row.sections.forEach((v,i)=>{errors.pressureBar=Math.max(errors.pressureBar,Math.abs(v.p-b.rows[j].sections[i].p));errors.enthalpyKJkg=Math.max(errors.enthalpyKJkg,Math.abs(v.h-b.rows[j].sections[i].h));errors.temperatureK=Math.max(errors.temperatureK,Math.abs(v.T-b.rows[j].sections[i].T));}));
 const events=a.final.events,ref=b.final.events;assert.equal(events.length,ref.length,'Event count must agree, including absence of spurious crossings');
 events.forEach((v,i)=>{const w=ref[i];assert.equal(v.section,w.section);assert.equal(v.boundary,w.boundary);assert.equal(v.direction,w.direction);errors.eventSeconds=Math.max(errors.eventSeconds,Math.abs(v.seconds-w.seconds));});
 return errors;
}
// Independently converged, direct-EOS continuous-time reference, not a coarse
// backward-Euler fixture. Its own Radau tolerance refinement must agree first.
const [lo,hi]=direct.runs;assert.equal(direct.sectionCount,3);assert(Math.abs(lo.terminalDryToWetSeconds-hi.terminalDryToWetSeconds)<1e-6);
lo.sections.forEach((v,i)=>{assert(Math.abs(v.h-hi.sections[i].h)<1e-4);assert(Math.abs(v.p-hi.sections[i].p)<1e-7);});
const directRun=run(scenarios[0],'tr-bdf2',{adaptive:true,...accuracyOptions(1e-7),eventStepSeconds:.0001});
report.independentReference.errors={pressureBar:0,enthalpyKJkg:0,temperatureK:0,eventSeconds:Math.abs(directRun.final.events[0].seconds-hi.terminalDryToWetSeconds)};
directRun.final.sections.forEach((v,i)=>{for(const [k,field]of [['pressureBar','p'],['enthalpyKJkg','h'],['temperatureK','T']])report.independentReference.errors[k]=Math.max(report.independentReference.errors[k],Math.abs(v[field]-hi.sections[i][field]));});
assert(report.independentReference.errors.pressureBar<.0001);assert(report.independentReference.errors.enthalpyKJkg<.02);assert(report.independentReference.errors.temperatureK<.01);assert(report.independentReference.errors.eventSeconds<.0002);
// Fixed-step temporal orders and event timing, independent of adaptive tolerance.
for(const method of methods){
 const rows=[];for(const step of [.00625,.003125,.0015625,.00078125]){const r=run(scenarios[0],method,{maxStep:step});rows.push({step,h:r.final.terminal.h,eventSeconds:r.final.events[0].seconds,calls:r.final.calls,elapsedMS:r.elapsedMS});}
 const d=rows.slice(0,-1).map((v,i)=>Math.abs(v.h-rows[i+1].h)),orders=[Math.log2(d[0]/d[1]),Math.log2(d[1]/d[2])];
 assert(orders.every(v=>v>(method==='backward-euler'?.9:1.7)&&v<(method==='backward-euler'?1.5:2.5)));
 report.refinement.push({method,rows,observedOrders:orders});
}
// Accuracy/robustness/cost comparison on exactly the same three-section cases.
for(const c of scenarios){
 const reference=run(c,'tr-bdf2',{adaptive:true,...accuracyOptions(1e-8),maxStep:.02,eventStepSeconds:.00005,minStep:1e-10});
 const cross=run(c,'trapezoid',{adaptive:true,...accuracyOptions(1e-8),maxStep:.02,eventStepSeconds:.00005,minStep:1e-10});
 const crossErrors=differences(cross,reference);assert(crossErrors.enthalpyKJkg<.01);assert(crossErrors.pressureBar<.00005);assert(crossErrors.eventSeconds<.0002);
 const comparisons=[];
 for(const method of methods)for(const tolerance of [1e-4,1e-5,1e-6]){
  const runResult=run(c,method,{adaptive:true,...accuracyOptions(tolerance)}),errors=differences(runResult,reference);
  runResult.final.events.forEach(v=>assert(v.bracketEndSeconds-v.bracketStartSeconds<=.002+1e-12));
  comparisons.push({method,relativeTolerance:tolerance,errors,...runResult.final,elapsedMS:runResult.elapsedMS});
  if(method==='tr-bdf2'&&tolerance===1e-6){assert(errors.enthalpyKJkg<.05,`${c.name}: ${JSON.stringify(errors)}`);assert(errors.pressureBar<.00005);assert(errors.temperatureK<.03);assert(errors.eventSeconds<.003);}
 }
 for(const method of methods){const errors=comparisons.filter(v=>v.method===method).map(v=>v.errors.enthalpyKJkg);if(Math.max(...errors)>1e-3)assert(errors[0]>errors[1]&&errors[1]>errors[2],c.name+' tolerance refinement '+method);}
 report.scenarios.push({name:c.name,samples:c.samples,reference:{...reference.final,rows:reference.rows,elapsedMS:reference.elapsedMS},crossCheckErrors:crossErrors,comparisons});
 console.error('Verified temporal case: '+c.name);
}
// Independently derived sealed boiling event: fixed M/V, saturated vapor density
// determines p; exact linear energy ledger determines transition time.
const sealedCase=scenarios[5],sealedState=createEvaporator(engine).create(sealedCase.config),cell=sealedState.cells[0];let left=.3,right=35;
for(let i=0;i<60;i++){const p=(left+right)/2;if(engine.sat(p).rhog>cell.massKg/cell.volumeM3)right=p;else left=p;}
const saturationPressure=(left+right)/2,threshold=cell.massKg*engine.sat(saturationPressure).hg-100*saturationPressure*cell.volumeM3,exactSeconds=(threshold-cell.internalEnergyKJ)/.1;
report.eventRefinement={exactSealedBoilingSeconds:exactSeconds,rows:[]};
for(const cap of [.008,.002,.0005]){const m=createEvaporator(engine,{adaptive:true,eventStepSeconds:cap}),s=m.create(sealedCase.config),r=check(m.advance(s,1)),event=r.events[0];assert.equal(r.integration.method,'tr-bdf2');assert(event.bracketEndSeconds-event.bracketStartSeconds<=cap+1e-12);report.eventRefinement.rows.push({eventStepSeconds:cap,seconds:event.seconds,errorSeconds:Math.abs(event.seconds-exactSeconds)});}
const timingErrors=report.eventRefinement.rows.map(v=>v.errorSeconds);assert(timingErrors[0]>timingErrors[1]&&timingErrors[1]>timingErrors[2]);assert(timingErrors[2]<.00002);
// A coarse trapezoid can oscillate through saturation; adaptive versions above
// must match the reference crossing count. Preserve this candidate limitation.
const coarse=run(scenarios[0],'trapezoid',{maxStep:.05});assert(coarse.final.events.length>directRun.final.events.length);report.coarseTrapezoid={events:coarse.final.events,terminalEnthalpy:coarse.final.terminal.h};
// Trial is uncommitted, even for the two-stage method. Coarse/two-half candidates
// cannot touch physical inventories, time, events or conservation ledgers.
const model=createEvaporator(engine,{method:'tr-bdf2',adaptive:true,...accuracyOptions(1e-6),minStep:1e-9}),state=model.create(spec()),snapshot=JSON.stringify(state);model.trial(state,.001);assert.equal(JSON.stringify(state),snapshot);
const tooTight=createEvaporator(engine,{method:'tr-bdf2',adaptive:true,...accuracyOptions(1e-9),maxStep:.5,minStep:.5}),rejected=tooTight.create(spec()),physical=JSON.stringify({cells:rejected.cells,ledger:rejected.ledger,seconds:rejected.seconds,events:rejected.events});
const rejectRow=tooTight.advance(rejected,1);assert.equal(rejectRow.stop.kind,'accuracy');assert.equal(JSON.stringify({cells:rejected.cells,ledger:rejected.ledger,seconds:rejected.seconds,events:rejected.events}),physical);assert.equal(rejectRow.acceptedSteps,0);assert(rejectRow.attemptedResidualEvaluations>0);
const frozen=JSON.stringify(rejected);tooTight.advance(rejected,1);assert.equal(JSON.stringify(rejected),frozen);report.failures.push(rejectRow.stop);
const priming=createEvaporator(engine),primed=check(priming.advance(priming.create(scenarios[2].config),120));const prior=tooTight.create({...scenarios[2].config,initial:primed.sections.map(v=>({p:v.p,h:v.h}))});check(tooTight.advance(prior,1));tooTight.update(prior,{heatKW:[4,4,4]});const priorAccepted=JSON.stringify({cells:prior.cells,ledger:prior.ledger,seconds:prior.seconds,events:prior.events});const laterRejected=tooTight.advance(prior,1);assert.equal(laterRejected.stop.kind,'accuracy');assert.equal(JSON.stringify({cells:prior.cells,ledger:prior.ledger,seconds:prior.seconds,events:prior.events}),priorAccepted);
const solver=createEvaporator(engine,{method:'tr-bdf2',adaptive:true,maxIterations:1,maxStep:.5,minStep:.5}),failed=solver.create(spec()),solverLedger=JSON.stringify(failed.ledger);const fault=solver.advance(failed,1);assert.equal(fault.stop.kind,'solver');assert.equal(fault.seconds,0);assert.equal(JSON.stringify(failed.ledger),solverLedger);assert(fault.attemptedResidualEvaluations>0);report.failures.push(fault.stop);
// Domain limits remain bounded and distinct. This test checks the existing
// property-domain exhaustion, not an arbitrary wet/level equipment trip.
const hot=model.create(spec([2,4,12])),hotRow=model.advance(hot,10);assert.equal(hotRow.stop.kind,'domain',JSON.stringify(hotRow.stop));assert(hotRow.terminal.superheatK>249);report.failures.push(hotRow.stop);assert(Math.abs(hotRow.energyResidualKJ)<1e-6);
// Validation rejects invalid tolerances; a boundary patch remains atomic.
for(const option of [{relativeTolerance:0},{eventStepSeconds:NaN},{method:'explicit'},{adaptive:'yes'}])assert.throws(()=>createEvaporator(engine,option));
const before=JSON.stringify(state);assert.throws(()=>model.update(state,{heatKW:[1,2]}));assert.equal(JSON.stringify(state),before);
// One-hour adaptive behavior including actual nonlinear-work counters. Numbers
// are host measurements, not physical-iPad performance claims.
for(const heatKW of [[6,6,6],[4,4,4]]){
 const s=model.create(spec(heatKW)),start=performance.now(),r=check(model.advance(s,3600));report.performance.push({name:heatKW[0]===6?'one-hour dry':'one-hour wet',...result(r),elapsedMS:performance.now()-start});
 assert.equal(r.terminal.wet,heatKW[0]===4);assert(r.attemptedResidualEvaluations>=r.acceptedResidualEvaluations);
}
report.passed=true;
const target=process.argv[2];if(target)fs.writeFileSync(path.resolve(target),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
