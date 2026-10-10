'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {fixture,cases,geometry,heatInputs,numericalOptions}=require('./spatial-fixtures.cjs'),{run,temporalDifference}=require('./spatial-runner.cjs'),{delta}=require('./spatial-observables.cjs'),{createEvaporator}=require('./evaporator.cjs'),H=require('./hydraulics.cjs');
const reference=require(process.env.DX_FV_SPATIAL_REFERENCE_PATH||'./spatial-reference.json');
const report={schemaVersion:1,meshes:[3,5],method:'adaptive tr-bdf2',geometry,contracts:{},scenarios:[],extended:[],independentReference:{source:reference.source,steady:[],startup:[]},limits:{massResidualKg:1e-8,energyResidualKJ:1e-6,temporalEnthalpyKJkg:.05,temporalPressureBar:.00005,temporalTemperatureK:.03,temporalEventSeconds:.003},spatialConvergenceEstablished:false};
const near=(a,b,t)=>assert(Math.abs(a-b)<t,`${a} vs ${b}`);
function checkRow(r,expectedDomain=false){
 assert([3,5].includes(r.sectionCount));if(expectedDomain){assert.equal(r.stop?.kind,'domain');assert(r.terminal.superheatK>249.99);}else assert(!r.stop,JSON.stringify(r.stop));
 assert(Math.abs(r.massResidualKg)<report.limits.massResidualKg);assert(Math.abs(r.energyResidualKJ)<report.limits.energyResidualKJ);r.sectionResiduals.forEach(v=>{assert(Math.abs(v.massKg)<report.limits.massResidualKg);assert(Math.abs(v.energyKJ)<report.limits.energyResidualKJ);});
 near(r.profile.reduce((s,v)=>s+v.massKg,0),r.totals.massKg,1e-12);near(r.profile.reduce((s,v)=>s+v.energyKJ,0),r.totals.internalEnergyKJ,1e-9);
 near(r.pressureDrop.faces.reduce((s,v)=>s+v.pressureDropBar,0),r.pressureDrop.imposedTotalBar,1e-10);
 r.sections.forEach(v=>{assert(v.massKg>0);assert(Number.isFinite(v.p)&&Number.isFinite(v.h)&&Number.isFinite(v.T));});
}
function checkRun(r,domain=false){checkRow(r.initial);r.rows.forEach(v=>checkRow(v));checkRow(r.final,domain);}
function compact(r){return {seconds:r.final.seconds,terminal:r.final.terminal,steps:r.final.steps,rejected:r.final.rejected,iterations:r.final.iterations,calls:r.final.calls,minStep:r.final.minStep,maxStep:r.final.maxStep,massResidualKg:r.final.massResidualKg,energyResidualKJ:r.final.energyResidualKJ,stop:r.final.stop,elapsedMS:r.elapsedMS};}
// A homogeneous fluid provides an analytic resistance invariant independent of
// mesh locations/donor differences. No extra local restriction at internal faces.
const physicalLength=geometry.totalVolumeM3/(Math.PI*geometry.diameterM**2/4),homogeneous=engine.ph(4,900),configurations=[3,5].map(n=>fixture(n));
const invariants=configurations.map(c=>{const totalLength=c.connections.reduce((s,v)=>s+v.lengthM,0),totalMinorK=c.connections.reduce((s,v)=>s+v.minorK,0),coef=c.connections.map(v=>H.coefficients(homogeneous,v)),linear=coef.reduce((s,v)=>s+v.linear,0),quadratic=coef.reduce((s,v)=>s+v.quadratic,0),analytic=H.coefficients(homogeneous,{...c.connections[0],lengthM:physicalLength,minorK:1002});
 near(totalLength,physicalLength,1e-12);assert.equal(totalMinorK,1002);assert(c.connections.slice(1,-1).every(v=>v.minorK===0));near(linear,analytic.linear,1e-8);near(quadratic,analytic.quadratic,1e-6);
 near(c.volumeFractions.reduce((s,v)=>s+v*geometry.totalVolumeM3,0),geometry.totalVolumeM3,1e-15);near(c.heatKW.reduce((s,v)=>s+v,0),18,1e-12);
 for(const profile of ['uniform','graded'])near(heatInputs(c.sectionCount,18,profile).reduce((s,v)=>s+v,0),18,1e-12);
 return {sectionCount:c.sectionCount,cellVolumeM3:geometry.totalVolumeM3/c.sectionCount,cellLengthM:physicalLength/c.sectionCount,totalLengthM:totalLength,totalMinorK,homogeneousLinearResistance:linear,homogeneousQuadraticResistance:quadratic};
});
near(invariants[0].homogeneousLinearResistance,invariants[1].homogeneousLinearResistance,1e-8);near(invariants[0].homogeneousQuadraticResistance,invariants[1].homogeneousQuadraticResistance,1e-6);report.contracts.geometry=invariants;
for(const n of [4,17,33])assert.throws(()=>fixture(n),/approved/); // validation only: no integrated finer model is created.
// For each mesh, independently compare 1e-6 / 1e-7 / 1e-8 tolerance and smaller
// maximum steps/event brackets. Also isolate a maximum-step refinement at 1e-7.
const meshRuns=new Map();
for(let caseIndex=0;caseIndex<cases(3).length;caseIndex++){
 const meshResults=[];
 for(const n of [3,5]){
  const c=cases(n)[caseIndex],domain=n===5&&caseIndex===0,runs=[];
  for(const [tolerance,maxStep,eventStepSeconds]of [[1e-6,.5,.002],[1e-7,.25,.0005],[1e-8,.125,.0001]]){
   const r=run(engine,c,{...numericalOptions(tolerance),maxStep,eventStepSeconds});checkRun(r,domain);runs.push(r);
  }
  const nominalErrors=temporalDifference(runs[0],runs[2]),tightErrors=temporalDifference(runs[1],runs[2]);
  assert(nominalErrors.enthalpyKJkg<report.limits.temporalEnthalpyKJkg,c.name+JSON.stringify(nominalErrors));assert(nominalErrors.pressureBar<report.limits.temporalPressureBar);assert(nominalErrors.temperatureK<report.limits.temporalTemperatureK);assert(nominalErrors.eventSeconds<report.limits.temporalEventSeconds);assert(nominalErrors.domainSeconds<.0001);assert(nominalErrors.profileMassL1Kg<2e-6);
  if(nominalErrors.enthalpyKJkg>1e-3)assert(tightErrors.enthalpyKJkg<nominalErrors.enthalpyKJkg);
  const stepRefined=run(engine,c,{...numericalOptions(1e-7),maxStep:.125,eventStepSeconds:.0005});checkRun(stepRefined,domain);const stepErrors=temporalDifference(stepRefined,runs[1]);assert(stepErrors.enthalpyKJkg<.01);assert(stepErrors.eventSeconds<.001);assert(stepErrors.domainSeconds<.0001);
  meshRuns.set(n+':'+c.name,runs);
  meshResults.push({sectionCount:n,initial:runs[0].initial,nominal:{...compact(runs[0]),rows:runs[0].rows,final:runs[0].final},temporal:{settings:[{relativeTolerance:1e-6,maxStep:.5,eventStepSeconds:.002},{relativeTolerance:1e-7,maxStep:.25,eventStepSeconds:.0005},{relativeTolerance:1e-8,maxStep:.125,eventStepSeconds:.0001}],runs:runs.map(compact),nominalErrors,tightErrors,maximumStepComparison:stepErrors}});
  // Independent direct-EOS continuous-time startup for both approved meshes.
  if(caseIndex===0){const direct=reference.startup.find(v=>v.sectionCount===n),[lo,hi]=direct.runs;near(lo.seconds,hi.seconds,1e-6);lo.samples.forEach((v,j)=>v.sections.forEach((w,i)=>{near(w.h,hi.samples[j].sections[i].h,1e-4);near(w.p,hi.samples[j].sections[i].p,1e-7);}));
   const errors={pressureBar:0,enthalpyKJkg:0,temperatureK:0,eventSeconds:0,domainSeconds:0};hi.samples.forEach(v=>{const match=runs[2].rows.find(w=>Math.abs(w.seconds-v.seconds)<1e-9);assert(match);v.sections.forEach((w,i)=>{errors.pressureBar=Math.max(errors.pressureBar,Math.abs(w.p-match.sections[i].p));errors.enthalpyKJkg=Math.max(errors.enthalpyKJkg,Math.abs(w.h-match.sections[i].h));errors.temperatureK=Math.max(errors.temperatureK,Math.abs(w.T-match.sections[i].T));});});
   if(domain)errors.domainSeconds=Math.abs(runs[2].final.seconds-hi.domainEventsSeconds[0]);else errors.eventSeconds=Math.abs(runs[2].final.terminalEvents[0].seconds-hi.wetEventsSeconds[0]);
   assert(errors.pressureBar<.0001);assert(errors.enthalpyKJkg<.02);assert(errors.temperatureK<.01);assert(errors.eventSeconds<.0001);assert(errors.domainSeconds<.0001);report.independentReference.startup.push({sectionCount:n,errors,directDomainSeconds:hi.domainEventsSeconds,directWetEventsSeconds:hi.wetEventsSeconds});
  }
  console.error('Temporal refinement passed: '+c.name+' N='+n);
 }
 const [three,five]=meshResults,rows=[];near(three.initial.totals.massKg,five.initial.totals.massKg,1e-12);near(three.initial.totals.internalEnergyKJ,five.initial.totals.internalEnergyKJ,1e-9);assert(three.initial.profile.every((v,i)=>Math.abs(v.massKg-five.initial.profile[i].massKg)<1e-12));
 // Attribute spatial differences only after comparing tighter runs on each mesh.
 const [fine3,fine5]=[meshRuns.get('3:'+cases(3)[caseIndex].name)[2],meshRuns.get('5:'+cases(5)[caseIndex].name)[2]];
 fine3.rows.forEach(a=>{const b=fine5.rows.find(v=>Math.abs(v.seconds-a.seconds)<1e-9);if(b)rows.push({seconds:a.seconds,differenceFiveMinusThree:delta(a,b)});});
 const terminalEvents3=fine3.final.terminalEvents,terminalEvents5=fine5.final.terminalEvents;
 const matchedEvents=[];if(terminalEvents3.length===terminalEvents5.length)terminalEvents3.forEach((v,i)=>{assert.equal(v.boundary,terminalEvents5[i].boundary);assert.equal(v.direction,terminalEvents5[i].direction);matchedEvents.push({boundary:v.boundary,direction:v.direction,threeSeconds:v.seconds,fiveSeconds:terminalEvents5[i].seconds,differenceSeconds:terminalEvents5[i].seconds-v.seconds});});
 if(caseIndex>0)assert(rows.some(v=>v.differenceFiveMinusThree.terminal.wetDisagrees),'Paired snapshots inside the different transition windows must expose wet/dry disagreement.');
 report.scenarios.push({name:cases(3)[caseIndex].name,meshes:meshResults,spatial:{usesTightlyTimeResolvedRuns:true,rows,matchedEvents,terminalEventCounts:{three:terminalEvents3.length,five:terminalEvents5.length},fiveToThreeCallsRatio:five.nominal.calls/three.nominal.calls,fiveToThreeIterationsRatio:five.nominal.iterations/three.nominal.iterations,fiveToThreeElapsedRatio:five.nominal.elapsedMS/three.nominal.elapsedMS}});
}
// Same uniform initial conditions and physical fixtures for an open one-hour
// control volume. All output schedules are the same on both meshes.
for(const [totalHeatKW,profile]of [[12,'uniform'],[18,'uniform'],[18,'graded']]){
 const results=[];
 for(const n of [3,5]){
  const c={config:fixture(n,{totalHeatKW,profile}),samples:[1,2,5,15,60,600,1800,3600],changes:[]},r=run(engine,c);checkRun(r);assert.equal(r.final.terminal.wet,totalHeatKW===12);assert.equal(r.final.terminal.superheatK===0,totalHeatKW===12);
  const ref=reference.steady.find(v=>v.sectionCount===n&&v.totalHeatKW===totalHeatKW&&v.heatProfile===profile),errors={flowRelative:Math.abs(r.final.portOutflowKgS/ref.flowKgS-1),pressureBar:0,enthalpyKJkg:0,temperatureK:0};
  r.final.sections.forEach((v,i)=>{const w=ref.sections[i];errors.pressureBar=Math.max(errors.pressureBar,Math.abs(v.p-w.p));errors.enthalpyKJkg=Math.max(errors.enthalpyKJkg,Math.abs(v.h-w.h));errors.temperatureK=Math.max(errors.temperatureK,Math.abs(v.T-w.T));});
  assert(errors.flowRelative<.001);assert(errors.pressureBar<.002);assert(errors.enthalpyKJkg<.1);assert(errors.temperatureK<.05);report.independentReference.steady.push({sectionCount:n,totalHeatKW,profile,errors});
  results.push({sectionCount:n,...compact(r),final:r.final,rows:r.rows});console.error('Extended/reference passed: '+profile+' '+totalHeatKW+' kW N='+n);
 }
 report.extended.push({totalHeatKW,profile,meshes:results,differenceFiveMinusThree:delta(results[0].final,results[1].final),fiveToThreeCallsRatio:results[1].calls/results[0].calls,fiveToThreeElapsedRatio:results[1].elapsedMS/results[0].elapsedMS});
}
// Expected domain finding is frozen, with no equipment trip, repaired inventory
// or discarded refrigerant. Other stop types are not accepted as this finding.
const warm5=cases(5)[0],model=createEvaporator(engine,numericalOptions(1e-6)),state=model.create(warm5.config),stopped=model.advance(state,1);assert.equal(stopped.stop.kind,'domain');const frozen=JSON.stringify(state);model.advance(state,10);assert.equal(JSON.stringify(state),frozen);
report.recommendation='Five sections are a more informative investigative mesh; three sections are not established as adequate for inventory or transition timing. Neither mesh is spatially converged. Request approval for a finer reference before a final count or Live Plant integration.';
report.passed=true;report.verificationMeaning='All comparison/regression criteria passed; the five-section warm-start EOS-domain stop is an explicitly verified model limitation, not successful operation.';
if(process.argv[2])fs.writeFileSync(path.resolve(process.argv[2]),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,meshes:report.meshes,scenarios:report.scenarios.map(v=>({name:v.name,spatial:v.spatial})),extended:report.extended.map(v=>({totalHeatKW:v.totalHeatKW,profile:v.profile,differenceFiveMinusThree:v.differenceFiveMinusThree,fiveToThreeElapsedRatio:v.fiveToThreeElapsedRatio})),independentReference:report.independentReference,recommendation:report.recommendation},null,2));
