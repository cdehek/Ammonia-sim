'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createCoupledModel}=require('./coupled-model.cjs'),{fixture,cases,accuracyOptions}=require('./coupled-fixtures.cjs');
const {createEvaporator}=require('./evaporator.cjs'),{createIntegrator}=require('./thermal-network.cjs'),{createThermalConfig}=require('./thermal-geometry.cjs');
const output=process.argv[2];
const report={stage:'2A',sectionCount:5,startingCommit:'dd0ca33cc834e2056ebede756f8cf59ed1157a07',runtime:process.version,
  limits:{massKg:1e-8,energyKJ:1e-6,nominalTemperatureK:.01,tightTemperatureK:.001,pressureBar:5e-5,enthalpyKJkg:.05,eventSeconds:.001},
  conservation:{massKg:0,sectionMassKg:0,refrigerantKJ:0,thermalKJ:0,combinedKJ:0,sectionEnergyKJ:0,nodeEnergyKJ:0},cases:[],checks:[],failures:[]};
let activeCase=null,lastRecord=null;
const maximum=a=>Math.max(0,...a.map(Math.abs));
const near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} vs ${b}, limit ${t}`);
function check(r,stopAllowed=false){
  lastRecord=r;assert.equal(r.sectionCount,5);assert.equal(r.nodes.length,11);
  if(!stopAllowed)assert.equal(r.stop,null,JSON.stringify(r.stop));
  const residual={massKg:Math.abs(r.massResidualKg),sectionMassKg:maximum(r.sectionResiduals.map(v=>v.massKg)),refrigerantKJ:Math.abs(r.refrigerantEnergyResidualKJ),thermalKJ:Math.abs(r.thermalEnergyResidualKJ),combinedKJ:Math.abs(r.combinedEnergyResidualKJ),sectionEnergyKJ:maximum(r.sectionResiduals.map(v=>v.energyKJ)),nodeEnergyKJ:maximum(r.nodes.map(v=>v.residualKJ))};
  for(const [key,value]of Object.entries(residual)){
    assert.ok(value<(key.includes('mass')||key.includes('Mass')?1e-8:1e-6),key+': '+value);
    report.conservation[key]=Math.max(report.conservation[key],value);
  }
  // Independently rebuild each node budget from signed integrated links, not the solver's node ledger.
  const b=Array(11).fill(0);b[10]=r.ledger.airLoadKJ;
  for(let i=0;i<5;i++){
    const [at,af,ft]=r.ledger.thermalLinksKJ.slice(3*i,3*i+3),tr=r.ledger.tubeRefrigerantKJ[i];
    b[10]-=at+af;b[2*i]+=at+ft-tr;b[2*i+1]+=af-ft;
  }
  r.nodes.forEach((n,i)=>near(n.energyChangeKJ,b[i],1e-6,'Independent thermal node budget'));
  near(b.reduce((a,v)=>a+v,0)+r.ledger.tubeRefrigerantKJ.reduce((a,v)=>a+v,0),r.ledger.airLoadKJ,1e-8,'Internal exchanges cancel');
  near(r.ledger.boundaryMassKg,r.ledger.faces[0].massKg-r.ledger.faces.at(-1).massKg,1e-10,'Boundary mass ledger');
  near(r.ledger.boundaryEnthalpyKJ,r.ledger.faces[0].energyKJ-r.ledger.faces.at(-1).energyKJ,1e-7,'Boundary enthalpy ledger');
  assert.ok(r.sections.every(v=>v.massKg>0&&Math.abs(v.energyResidual)<1e-7&&Math.abs(v.densityResidual)<1e-7));
  assert.ok(r.nodes.every(v=>v.temperatureK>=200&&v.temperatureK<=400));
  if(r.lastTimeError!==null)assert.ok(r.lastTimeError<=1);
  return r;
}
function compact(r){return {seconds:r.seconds,sections:r.sections.map(v=>({p:v.p,h:v.h,T:v.T,massKg:v.massKg,internalEnergyKJ:v.internalEnergyKJ})),temperaturesK:r.nodes.map(v=>v.temperatureK),terminal:r.terminal,outlet:r.outlet,
  massResidualKg:r.massResidualKg,refrigerantEnergyResidualKJ:r.refrigerantEnergyResidualKJ,thermalEnergyResidualKJ:r.thermalEnergyResidualKJ,combinedEnergyResidualKJ:r.combinedEnergyResidualKJ,
  ledger:r.ledger,fluxes:r.fluxes,events:r.events,boundaryEvents:r.boundaryEvents,acceptedSteps:r.acceptedSteps,rejectedSteps:r.rejectedSteps,accuracyRejectedSteps:r.accuracyRejectedSteps,eventRejectedSteps:r.eventRejectedSteps,domainRejectedSteps:r.domainRejectedSteps,
  attemptedResidualEvaluations:r.attemptedResidualEvaluations,attemptedIterations:r.attemptedIterations,minAcceptedStepSeconds:r.minAcceptedStepSeconds,maxAcceptedStepSeconds:r.maxAcceptedStepSeconds,stop:r.stop};}
function run(c,options={}){
  activeCase=c.name;const m=createCoupledModel(engine,options),s=m.create(c.config),start=performance.now();
  const initial=compact(check(m.record(s))),rows=[];
  for(const t of c.samples){const r=check(m.advance(s,t-s.seconds));assert.equal(r.seconds,t);rows.push(compact(r));}
  const final=check(m.record(s));
  assert.ok(s.trace.every(v=>v.error<=1));
  return {model:m,state:s,initial,rows,final:compact(final),elapsedMS:performance.now()-start};
}
function differences(a,b){
  assert.equal(a.rows.length,b.rows.length);
  const error={pressureBar:0,enthalpyKJkg:0,refrigerantTemperatureK:0,thermalTemperatureK:0,eventSeconds:0,linkIntegralKJ:0};
  a.rows.forEach((row,j)=>{
    const ref=b.rows[j];assert.equal(row.seconds,ref.seconds);
    row.sections.forEach((v,i)=>{error.pressureBar=Math.max(error.pressureBar,Math.abs(v.p-ref.sections[i].p));error.enthalpyKJkg=Math.max(error.enthalpyKJkg,Math.abs(v.h-ref.sections[i].h));error.refrigerantTemperatureK=Math.max(error.refrigerantTemperatureK,Math.abs(v.T-ref.sections[i].T));});
    error.thermalTemperatureK=Math.max(error.thermalTemperatureK,maximum(row.temperaturesK.map((v,i)=>v-ref.temperaturesK[i])));
    error.linkIntegralKJ=Math.max(error.linkIntegralKJ,maximum(row.ledger.tubeRefrigerantKJ.map((v,i)=>v-ref.ledger.tubeRefrigerantKJ[i])));
  });
  assert.equal(a.final.events.length,b.final.events.length,'No missing/spurious saturation crossings');
  a.final.events.forEach((v,i)=>{const w=b.final.events[i];assert.equal(v.section,w.section);assert.equal(v.boundary,w.boundary);assert.equal(v.direction,w.direction);error.eventSeconds=Math.max(error.eventSeconds,Math.abs(v.seconds-w.seconds));});
  return error;
}
function temporalAcceptance(e,tight=false){
  assert.ok(e.pressureBar<5e-5,JSON.stringify(e));assert.ok(e.enthalpyKJkg<.05,JSON.stringify(e));
  assert.ok(e.refrigerantTemperatureK<(tight?.001:.01),JSON.stringify(e));assert.ok(e.thermalTemperatureK<(tight?.001:.01),JSON.stringify(e));assert.ok(e.eventSeconds<.001,JSON.stringify(e));
}
function physical(s){return JSON.stringify({cells:s.cells,energies:s.energies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,spec:s.spec});}
function verification(){
  const reference=JSON.parse(fs.readFileSync(process.env.DX_COUPLED_REFERENCE_PATH||path.join(__dirname,'coupled-reference.json'),'utf8'));
  assert.equal(reference.sectionCount,5);report.independentSource=reference.source;
  {
    const m=createCoupledModel(engine),s=m.create(fixture());
    const defaultState=m.create();assert.equal(defaultState.spec.thermal.loadsKW.air,1);
    assert.deepEqual(m.record(defaultState).nodes.map(v=>v.temperatureK),[273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,278.15]);
    near(s.spec.conductancesKWK.reduce((a,v)=>a+v,0),.60,1e-15,'Total effective G_tr');
    assert.ok(s.spec.conductancesKWK.every(v=>Math.abs(v-.12)<1e-15));
    near(s.cells.reduce((a,v)=>a+v.volumeM3,0),.003,1e-15,'Refrigerant volume');
    assert.ok(s.spec.fluid.heatKW.every(v=>v===0));
    near(s.spec.thermal.nodes.filter(v=>v.id.startsWith('tube')).reduce((a,v)=>a+v.capacityKJK,0),reference.geometry.tubeCapacityKJK,1e-12,'Tube capacity');
    near(s.spec.thermal.nodes.filter(v=>v.id.startsWith('fin')).reduce((a,v)=>a+v.capacityKJK,0),reference.geometry.finCapacityKJK,1e-12,'Fin capacity');
    report.checks.push({name:'Five-section physical allocation and no added prescribed heat',totalConductanceKWK:.60});
  }
  for(const c of cases()){
    console.error('Qualifying coupled '+c.name);
    const direct=reference.cases.find(v=>v.name===c.name),[lo,hi]=direct.runs;
    assert.equal(lo.domainEventsSeconds.length,0);assert.equal(hi.domainEventsSeconds.length,0);
    assert.equal(lo.samples.length,c.samples.length);assert.equal(hi.samples.length,c.samples.length);
    const own={pressureBar:0,enthalpyKJkg:0,refrigerantTemperatureK:0,thermalTemperatureK:0,eventSeconds:0};
    lo.samples.forEach((r,j)=>{
      r.sections.forEach((v,i)=>{own.pressureBar=Math.max(own.pressureBar,Math.abs(v.p-hi.samples[j].sections[i].p));own.enthalpyKJkg=Math.max(own.enthalpyKJkg,Math.abs(v.h-hi.samples[j].sections[i].h));own.refrigerantTemperatureK=Math.max(own.refrigerantTemperatureK,Math.abs(v.T-hi.samples[j].sections[i].T));});
      own.thermalTemperatureK=Math.max(own.thermalTemperatureK,maximum(r.temperaturesK.map((v,i)=>v-hi.samples[j].temperaturesK[i])));
    });
    assert.equal(lo.terminalSaturationEventsSeconds.length,hi.terminalSaturationEventsSeconds.length);
    lo.terminalSaturationEventsSeconds.forEach((v,i)=>{own.eventSeconds=Math.max(own.eventSeconds,Math.abs(v-hi.terminalSaturationEventsSeconds[i]));});
    assert.ok(own.enthalpyKJkg<1e-4&&own.pressureBar<1e-7&&own.refrigerantTemperatureK<1e-4&&own.thermalTemperatureK<1e-5&&own.eventSeconds<1e-6,JSON.stringify(own));
    for(const sample of hi.samples){assert.ok(sample.maximumMassResidualKg<1e-8);assert.ok(sample.maximumFluidEnergyResidualKJ<1e-6);assert.ok(sample.maximumThermalResidualKJ<1e-6);assert.ok(Math.abs(sample.combinedEnergyResidualKJ)<1e-6);}
    const runs=[1e-6,1e-7,1e-8].map(tol=>run(c,accuracyOptions(tol))),nominal=differences(runs[0],runs[2]),tight=differences(runs[1],runs[2]);
    temporalAcceptance(nominal);temporalAcceptance(tight,true);
    const independent={pressureBar:0,enthalpyKJkg:0,refrigerantTemperatureK:0,thermalTemperatureK:0,eventSeconds:0},interpolation={temperatureK:0,densityRelative:0,specificEnergyKJkg:0};
    hi.samples.forEach((sample,j)=>{
      const row=runs[2].rows[j];assert.equal(row.seconds,sample.seconds);
      sample.sections.forEach((v,i)=>{
        independent.pressureBar=Math.max(independent.pressureBar,Math.abs(row.sections[i].p-v.p));independent.enthalpyKJkg=Math.max(independent.enthalpyKJkg,Math.abs(row.sections[i].h-v.h));independent.refrigerantTemperatureK=Math.max(independent.refrigerantTemperatureK,Math.abs(row.sections[i].T-v.T));
        const table=engine.ph(v.p,v.h);
        interpolation.temperatureK=Math.max(interpolation.temperatureK,Math.abs(table.T-v.T));interpolation.densityRelative=Math.max(interpolation.densityRelative,Math.abs(table.rho/v.rho-1));interpolation.specificEnergyKJkg=Math.max(interpolation.specificEnergyKJkg,Math.abs(table.h-100*table.p/table.rho-v.u));
      });
      independent.thermalTemperatureK=Math.max(independent.thermalTemperatureK,maximum(row.temperaturesK.map((v,i)=>v-sample.temperaturesK[i])));
    });
    const terminalEvents=runs[2].final.events.filter(v=>v.section===4&&v.boundary==='vapor');
    assert.equal(terminalEvents.length,hi.terminalSaturationEventsSeconds.length);
    terminalEvents.forEach((v,i)=>{independent.eventSeconds=Math.max(independent.eventSeconds,Math.abs(v.seconds-hi.terminalSaturationEventsSeconds[i]));});
    // Direct EOS includes initial/property-closure differences, separate from same-table temporal error.
    assert.ok(independent.pressureBar<1e-4&&independent.enthalpyKJkg<.05&&independent.refrigerantTemperatureK<.01&&independent.thermalTemperatureK<.01&&independent.eventSeconds<.001,JSON.stringify(independent));
    const refined=run(c,{...accuracyOptions(1e-7),maxStep:.025}),capErrors=differences(refined,runs[2]);temporalAcceptance(capErrors,true);
    if(c.config.schedule){assert.deepEqual(runs[0].final.boundaryEvents.map(v=>v.seconds),[15,30]);near(runs[0].final.ledger.airLoadKJ,c.name==='load-step'?75:60,1e-8,'Scheduled load integral');}
    if(c.name==='heat-reversal'){assert.ok(runs[0].rows[0].fluxes.tubeRefrigerant.every(v=>v<0));assert.ok(runs[0].rows.at(-1).fluxes.tubeRefrigerant.every(v=>v>0));}
    report.cases.push({name:c.name,nominalTemporalErrors:nominal,tightTemporalErrors:tight,maxStepRefinementErrors:capErrors,independentReferenceRefinement:own,directEOSComparison:independent,matchedPHInterpolation:interpolation,
      runs:runs.map((r,i)=>({relativeTolerance:[1e-6,1e-7,1e-8][i],elapsedMS:r.elapsedMS,initial:r.initial,rows:r.rows,final:r.final})),maxStepRefined:{elapsedMS:refined.elapsedMS,final:refined.final}});
  }
  // Zero G_tr: same physical thermal limit and unchanged zero-prescribed-heat fluid model.
  {
    const thermal={tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0};
    const m=createCoupledModel(engine),s=m.create(fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal}));
    const I=createIntegrator(),z=I.create(createThermalConfig({sectionCount:5,...thermal}));let error=0;
    for(const t of [1,5,60,300]){const r=check(m.advance(s,t-s.seconds)),w=I.advance(z,t-z.seconds);error=Math.max(error,maximum(r.nodes.map((v,i)=>v.temperatureK-w.nodes[i].temperatureK)));assert.ok(r.ledger.tubeRefrigerantKJ.every(v=>v===0));near(r.ledger.airLoadKJ,0,0,'Closed external load');}
    assert.ok(error<.01);report.checks.push({name:'Closed zero-exchange thermal relaxation versus unchanged Stage 1',maximumTemperatureDifferenceK:error});
    const fluid=createEvaporator(engine,{adaptive:true}),c=m.create(fixture('cold',{refrigerantConductanceKWK:0})),f=fluid.create(c.spec.fluid);
    const a=check(m.advance(c,5)),b=fluid.advance(f,5);assert.equal(b.stop,null);a.sections.forEach((v,i)=>{near(v.h,b.sections[i].h,.01,'Uncoupled refrigerant h');near(v.p,b.sections[i].p,5e-5,'Uncoupled refrigerant p');});
    report.checks.push({name:'Zero-exchange refrigerant equivalence to unchanged prescribed-zero-heat model',passed:true});
  }
  // Exact uniform equilibrium: no numerical heat or mass source, including reporting offsets.
  {
    const T=engine.sat(3.5).T+273.15,config=fixture('cold',{sealed:true,thermal:{tubeProfileK:T,finProfileK:T,airInitialK:T,airLoadKW:0}});
    const m=createCoupledModel(engine),s=m.create(config),before=physical(s),r=check(m.advance(s,10));near(r.combinedEnergyResidualKJ,0,1e-8,'Equilibrium energy');r.nodes.forEach(v=>near(v.temperatureK,T,1e-8,'Equilibrium temperature'));report.checks.push({name:'Sealed coupled isothermal equilibrium',passed:true});
  }
  // Fixed-step accuracy on a nonlinear sealed fixture; first/second order without adaptive estimator.
  {
    const c={name:'smooth coupled order',config:fixture('cold',{sealed:true}),samples:[1]},reference=run(c,{...accuracyOptions(1e-9),maxStep:.005});
    const rows=[];
    for(const method of ['tr-bdf2','backward-euler']){
      const errors=[.1,.05,.025].map(maxStep=>{const r=run(c,{method,adaptive:false,maxStep});return maximum(r.final.temperaturesK.map((v,i)=>v-reference.final.temperaturesK[i]));});
      const orders=errors.slice(1).map((v,i)=>Math.log2(errors[i]/v));assert.ok(orders.every(v=>v>(method==='tr-bdf2'?1.8:.8)&&v<(method==='tr-bdf2'?2.2:1.2)),JSON.stringify({method,errors,orders}));rows.push({method,errorsK:errors,orders});
    }report.checks.push({name:'Smooth coupled fixed-step order',rows});
  }
  // Reporting reference cannot alter physical states, ledgers, or any adaptive decision.
  {
    const c=cases()[2],runs=[-1e6,273.15,1e6].map(ref=>run({...c,samples:[15,30,60],config:{...c.config,thermal:{...c.config.thermal,energyReferenceK:ref}}},{trace:true}));
    for(const r of runs.slice(1)){assert.deepEqual(r.state.cells,runs[0].state.cells);assert.deepEqual(r.state.energies,runs[0].state.energies);assert.deepEqual(r.state.ledger,runs[0].state.ledger);assert.deepEqual(r.state.trace,runs[0].state.trace);assert.deepEqual(r.state.rejectionTrace,runs[0].state.rejectionTrace);}
    report.checks.push({name:'Exact thermal-reference physical/timestep/rejection invariance',referencesK:[-1e6,273.15,1e6]});
  }
  {
    const m=createCoupledModel(engine),s=m.create(fixture()),before=JSON.stringify(s);m.trial(s,.001);assert.equal(JSON.stringify(s),before);
    assert.throws(()=>m.update(s,{airLoadKW:2,inlet:{p:100,h:500}}));assert.equal(JSON.stringify(s),before);
    const c=cases()[2],scheduled=run({...c,samples:[15,30,60]},{trace:true});assert.ok(scheduled.state.trace.every(v=>![15,30].some(t=>v.startSeconds<t&&v.endSeconds>t)));
    report.checks.push({name:'Pure trial, atomic mixed patch and exact scheduled transitions',passed:true});
  }
  {
    // 15 recoveries per TR-BDF2 trial: initial five + both solved stages.
    // Fail once at the start of the second half, after coarse/first-half success.
    let recoveries=0;
    const instrumented={...engine,stateMVU(...args){if(++recoveries===31)throw Object.assign(Error('Injected recovery failure in second half.'),{faultKind:'solver'});return engine.stateMVU(...args);}};
    const m=createCoupledModel(instrumented,{maxStep:.5,minStep:.5}),s=m.create(fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0}}));
    recoveries=0;const before=physical(s),r=check(m.advance(s,.5),true);
    assert.equal(r.stop?.kind,'solver');assert.ok(r.stop.message.includes('second half'));assert.equal(physical(s),before);assert.equal(r.acceptedSteps,0);
    report.failures.push({name:'Injected second-half recovery failure after valid coarse/first-half trials; complete rollback',stop:r.stop});
  }
  for(const kind of ['solver','accuracy','domain']){
    const opt=kind==='solver'?{maxIterations:1,maxStep:.5,minStep:.5}:kind==='accuracy'?{maxStep:.5,minStep:.5,relativeTolerance:1e-10,temperatureAbsoluteK:1e-8}:{maxStep:.5,minStep:1e-9};
    const m=createCoupledModel(engine,opt),config=kind==='domain'?fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:400,finProfileK:400,airInitialK:400,airLoadKW:1}})
      :kind==='accuracy'?fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0}}):fixture('warm');
    if(kind==='accuracy')m.trial(m.create(config),.5); // The fixture must first converge its stages.
    const s=m.create(config),before=physical(s),r=check(m.advance(s,1),true);assert.equal(r.stop?.kind,kind,JSON.stringify(r.stop));assert.equal(physical(s),before);assert.equal(r.acceptedSteps,0);
    const frozen=JSON.stringify(s);m.advance(s,1);assert.equal(JSON.stringify(s),frozen);assert.throws(()=>m.update(s,{airLoadKW:0}));assert.equal(JSON.stringify(s),frozen);
    if(kind==='domain'){assert.equal(r.stop.evidence.source,'thermal');assert.equal(r.stop.evidence.confirmed,true);}
    report.failures.push({name:'Forced '+kind+' stop with full rollback',stop:r.stop});
  }
  for(const kind of ['solver','accuracy']){
    const config=kind==='accuracy'?fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0}}):fixture('warm');
    const normal=createCoupledModel(engine),s=normal.create(config);check(normal.advance(s,.001));
    const m=createCoupledModel(engine,kind==='solver'?{maxIterations:1,maxStep:.5,minStep:.5}:{relativeTolerance:1e-10,temperatureAbsoluteK:1e-8,maxStep:.5,minStep:.5});
    s.nextStepSeconds=.5;const before=physical(s),r=check(m.advance(s,1),true);
    assert.equal(r.stop?.kind,kind,JSON.stringify(r.stop));assert.equal(physical(s),before);
    report.failures.push({name:'Forced '+kind+' stop after accepted state/ledger',stop:r.stop});
  }
  {
    const independentDomain=require('./coupled-domain-reference.json');assert.equal(independentDomain.diagnosticOnly,true);assert.ok(independentDomain.diagnosticPressureBar>35);assert.ok(independentDomain.heatKW>0);
    const m=createCoupledModel(engine),s=m.create({sealed:true,initial:Array.from({length:5},()=>({p:35,h:engine.sat(35).hg})),thermal:{tubeProfileK:400,finProfileK:400,airInitialK:400,airLoadKW:0}});
    const before=physical(s),r=check(m.advance(s,.1),true);assert.equal(r.stop?.kind,'domain');assert.equal(r.stop.evidence.source,'refrigerant');assert.equal(r.stop.evidence.confirmed,true);assert.equal(physical(s),before);
    report.failures.push({name:'Confirmed refrigerant pressure-domain stop with full rollback; numerical stress fixture only',independentDomain,stop:r.stop});
  }
  {
    const referenceThermal=require('./thermal-reference.json'),rows=[];
    for(const maxStep of [.5,.25]){
      const m=createCoupledModel(engine,{maxStep}),s=m.create({sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:1}}),r=check(m.advance(s,1600),true);
      assert.equal(r.stop?.kind,'domain');assert.equal(r.stop.evidence.source,'thermal');assert.equal(r.stop.evidence.confirmed,true);
      near(r.seconds,referenceThermal.connectedDomainSeconds,.001,'Independent zero-exchange domain clock');
      const frozen=JSON.stringify(s);m.advance(s,1);assert.equal(JSON.stringify(s),frozen);
      rows.push({maxStep,seconds:r.seconds,errorSeconds:r.seconds-referenceThermal.connectedDomainSeconds,stop:r.stop,combinedEnergyResidualKJ:r.combinedEnergyResidualKJ});
    }report.checks.push({name:'Zero-exchange thermal domain-clock refinement versus independent expm/root',rows});
  }
  // Unsupported trial is diagnostic only; no cumulative or state mutation.
  {
    const m=createCoupledModel(engine),s=m.create(fixture('warm'));s.cells[4]={...s.cells[4],internalEnergyKJ:1e6};
    const before=JSON.stringify(s);assert.throws(()=>m.trial(s,.001));assert.equal(JSON.stringify(s),before);report.checks.push({name:'Unsupported refrigerant trial leaves state untouched',passed:true});
  }
  for(const f of [()=>createCoupledModel(engine,{temperatureAbsoluteK:0}),()=>createCoupledModel(engine).create({sectionCount:9}),()=>createCoupledModel(engine).create({refrigerantConductanceKWK:1}),()=>createCoupledModel(engine).create({thermal:{airReservoirK:300}}),()=>createCoupledModel(engine).create({thermal:{domainK:[200,450]}}),()=>createCoupledModel(engine).create({schedule:[{seconds:1,patch:{heatKW:[1,1,1,1,1]}}]})])assert.throws(f);
  report.checks.push({name:'Stage 2A mesh/closure/domain/scope guards',passed:true});
  report.passed=true;
}
try{verification();if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,cases:report.cases.length,checks:report.checks.length,conservation:report.conservation,comparisons:report.cases.map(c=>({name:c.name,nominal:c.nominalTemporalErrors,direct:c.directEOSComparison}))}));}
catch(error){report.passed=false;report.failure={activeCase,message:error.message,stack:error.stack,lastAcceptedRecord:lastRecord};if(output)fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(error);process.exitCode=1;}
