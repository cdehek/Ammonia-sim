'use strict';
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createEvaporator,normalize}=require('./evaporator.cjs'),{createThermodynamics}=require('./thermodynamics.cjs'),C=require('./conservation.cjs'),H=require('./hydraulics.cjs');
const reference=require(process.env.DX_FV_REFERENCE_PATH||'./reference.json'),copy=x=>JSON.parse(JSON.stringify(x)),near=(a,b,t,message)=>assert(Math.abs(a-b)<t,message||`${a} vs ${b}`);
const spec=(heatKW=[6,6,6])=>({sectionCount:3,inletMinorK:1000,inlet:{p:4,h:500},outlet:{p:3.5,h:1700},initial:[{p:3.9,h:1000},{p:3.8,h:1400},{p:3.65,h:1650}],heatKW});
const report={schemaVersion:1,sectionCount:3,source:reference.source,cases:[],referenceErrors:{temperatureK:0,densityRelative:0,recoveryPressureBar:0,recoveryTemperatureK:0},steadyErrors:{flowRelative:0,pressureBar:0,enthalpyKJkg:0,temperatureK:0}};
function check(r){
 assert.equal(r.sectionCount,3,'This stage exercises only the approved three-section prototype');assert(!r.stop,r.stop?.message);assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);
 for(const v of r.sectionResiduals){assert(Math.abs(v.massKg)<1e-8);assert(Math.abs(v.energyKJ)<1e-6);}
 for(const v of r.sections){assert(Number.isFinite(v.p)&&Number.isFinite(v.T));assert(v.massKg>0);assert(v.p>=.3&&v.p<=35);assert(v.liquidVolumeFraction>=0&&v.liquidVolumeFraction<=1+1e-12);}
 return r;
}
function summarize(name,r,elapsedMS){report.cases.push({name,seconds:r.seconds,sections:r.sections.map(v=>({p:v.p,h:v.h,T:v.T,quality:v.x,liquidVolumeFraction:v.liquidVolumeFraction,phase:v.phase,massKg:v.massKg})),terminal:r.terminal,flowKgS:r.lastFluxes?.[0].massKgS,massResidualKg:r.massResidualKg,energyResidualKJ:r.energyResidualKJ,sectionResiduals:r.sectionResiduals,acceptedSteps:r.acceptedSteps,rejectedSteps:r.rejectedSteps,iterations:r.nonlinearIterations,stop:r.stop,...(elapsedMS===undefined?{}:{elapsedMS})});}
// Contracts and references: actual mixture enthalpy, signed shared flux, no phase selection.
const th=createThermodynamics(engine);
for(const v of reference.states){
 const a=th.ph(v.p,v.h),b=th.recover({massKg:v.rho*.001,volumeM3:.001,internalEnergyKJ:v.rho*.001*v.u,pressureGuess:v.p});
 const errors={temperatureK:Math.abs(a.T-v.T),densityRelative:Math.abs(a.rho/v.rho-1),recoveryPressureBar:Math.abs(b.p-v.p),recoveryTemperatureK:Math.abs(b.T-v.T)};
 for(const[k,error]of Object.entries(errors))report.referenceErrors[k]=Math.max(report.referenceErrors[k],error);
 assert(errors.temperatureK<.02&&errors.densityRelative<.001&&errors.recoveryPressureBar<.05&&errors.recoveryTemperatureK<.02);
 if(v.kind==='mixture'){assert(a.x!==null);near(a.x,v.quality,.001);}
}
const faces=[C.flux(.03,{h:500}),C.flux(.02,{h:900}),C.flux(-.01,{h:1400}),C.flux(.015,{h:1700})],q=[1,2,3],rates=C.assemble(faces,q);
near(rates.reduce((s,r)=>s+r.massKgS,0),faces[0].massKgS-faces.at(-1).massKgS,1e-15);near(rates.reduce((s,r)=>s+r.energyKW,0),q.reduce((s,v)=>s+v,0)+faces[0].energyKW-faces.at(-1).energyKW,1e-12);
const connection=normalize(spec()).connections[1],left=th.ph(4,900),right=th.ph(3.9,1200),flow=H.connectionFlow(left,right,connection);
assert(flow>0);near(H.pressureDropPa(flow,left,connection),1e4,1e-8);assert(H.connectionFlow(right,left,connection)<0);assert.equal(H.connectionFlow(right,left,{...connection,checkValve:true}),0);assert.equal(H.connectionFlow(left,left,connection),0);
const legacy=require('../../storage-engine').createStorage(engine,require('../../equipment-profiles')),liquid=engine.statePT(4,engine.sat(4).T-2,'liquid');
assert.throws(()=>legacy.phaseOutlet(liquid,'vapor'),/unavailable/);const liquidFlow=H.connectionFlow(liquid,th.ph(3.9,900),connection);assert(liquidFlow>0);assert.equal(C.flux(liquidFlow,liquid).energyKW,liquidFlow*liquid.h);
// Independent direct-EOS steady solution, including different heat distributions.
for(const v of reference.steady){
 const m=createEvaporator(engine),config=spec(v.heatKW);config.initial=v.sections.map(w=>({p:w.p,h:w.h}));const s=m.create(config),r=check(m.advance(s,120));
 report.steadyErrors.flowRelative=Math.max(report.steadyErrors.flowRelative,Math.abs(r.lastFluxes[0].massKgS/v.flowKgS-1));assert(report.steadyErrors.flowRelative<.001);
 r.sections.forEach((w,i)=>{const e={pressureBar:Math.abs(w.p-v.sections[i].p),enthalpyKJkg:Math.abs(w.h-v.sections[i].h),temperatureK:Math.abs(w.T-v.sections[i].T)};for(const[k,a]of Object.entries(e))report.steadyErrors[k]=Math.max(report.steadyErrors[k],a);assert(e.pressureBar<.002&&e.enthalpyKJkg<.1&&e.temperatureK<.05);});
 const equilibriumFlow=r.lastFluxes[0].massKgS;for(const f of r.lastFluxes)near(f.massKgS,equilibriumFlow,1e-7);
 summarize('Direct-EOS steady heat '+v.heatKW.join('/'),r);
}
// Cold two-phase startup -> distributed evaporation -> dry terminal, then load loss.
const m=createEvaporator(engine),cold=spec();cold.initial=[{p:3.55,h:500},{p:3.53,h:500},{p:3.51,h:500}];const run=m.create(cold);assert(m.record(run).terminal.wet);
const warmed=check(m.advance(run,120));assert(!warmed.terminal.wet&&warmed.terminal.superheatK>0);assert(warmed.sections[0].x<warmed.sections[1].x);assert(warmed.sections[1].x<1);assert(warmed.sections[0].h<warmed.sections[1].h&&warmed.sections[1].h<warmed.sections[2].h);summarize('Cold wet startup to dry terminal',warmed);
const before=JSON.stringify(run.cells),time=run.seconds;m.update(run,{heatKW:[4,4,4]});assert.equal(run.seconds,time);assert.equal(JSON.stringify(run.cells),before);
const reduced=check(m.advance(run,120));assert(reduced.terminal.wet);assert.equal(reduced.terminal.superheatK,0);assert(reduced.terminal.quality<.8);summarize('Heat reduction exposes wet terminal',reduced);
m.update(run,{heatKW:[6,6,6]});const restored=check(m.advance(run,120));assert(!restored.terminal.wet);summarize('Heat restoration recovers dry terminal',restored);
// Boundary-pressure disturbances, inlet enthalpy and isolation changes are atomic.
const shutting=m.create(spec());check(m.advance(shutting,120));const shutMass=m.record(shutting).totals.massKg,shutFaces=copy(shutting.spec.connections);shutFaces[0].closed=true;m.update(shutting,{connections:shutFaces,heatKW:[0,0,0]});const shutdown=check(m.advance(shutting,2));assert.equal(shutdown.lastFluxes[0].massKgS,0);assert(shutdown.totals.massKg<shutMass);summarize('Feed isolation with physical redistribution',shutdown);
const rejected=JSON.stringify(run);assert.throws(()=>m.update(run,{heatKW:[1,2]}));assert.equal(JSON.stringify(run),rejected);assert.throws(()=>m.update(run,{inlet:{p:40,h:500}}));assert.equal(JSON.stringify(run),rejected);assert.throws(()=>m.update(run,{sectionCount:5}));assert.equal(JSON.stringify(run),rejected);
m.update(run,{inlet:{p:4.1,h:500},heatKW:[4,4,4]});const pressure=check(m.advance(run,120));assert(pressure.lastFluxes[0].massKgS>reduced.lastFluxes[0].massKgS);assert(pressure.terminal.wet);summarize('Increased feed pressure',pressure);
// Closed, zero-heat startup/shutdown: inventory and energy are not repaired.
const sealedConfig=spec([0,0,0]);sealedConfig.initial=Array(3).fill({p:4,h:900});sealedConfig.connections=normalize(sealedConfig).connections.map(c=>({...c,closed:true}));const sealed=m.create(sealedConfig),sealedBefore=copy(sealed.cells);const staticRow=check(m.advance(sealed,60));
sealed.cells.forEach((v,i)=>{near(v.massKg,sealedBefore[i].massKg,1e-10);near(v.internalEnergyKJ,sealedBefore[i].internalEnergyKJ,1e-8);});assert(staticRow.lastFluxes.every(f=>f.massKgS===0));
// Liquid-full transport remains a liquid/mixture flow, rather than disappearing.
const filledConfig=spec([1,1,1]);filledConfig.initial=[3.9,3.8,3.65].map(p=>({p,h:engine.statePT(p,engine.sat(p).T-2,'liquid').h}));const filled=m.create(filledConfig);assert(m.record(filled).sections.every(v=>v.liquidVolumeFraction===1));const filledAfter=check(m.advance(filled,10));assert(filledAfter.lastFluxes[1].massKgS>0);summarize('Initially liquid-full sections transport mixture',filledAfter);
// Sealed heat/cool traverses saturation without inventing a dry region.
const phaseConfig=spec([.1,.1,.1]);phaseConfig.initial=Array(3).fill({p:4,h:engine.statePX(4,.99).h});phaseConfig.connections=normalize(phaseConfig).connections.map(c=>({...c,closed:true}));const phase=m.create(phaseConfig),mass0=C.totals(phase.cells).massKg;
const boiled=check(m.advance(phase,10));assert(boiled.sections.every(v=>!v.wet));near(boiled.totals.massKg,mass0,1e-8);m.update(phase,{heatKW:[-.1,-.1,-.1]});const condensed=check(m.advance(phase,10));assert(condensed.sections.every(v=>v.x!==null&&v.x<1));near(condensed.totals.massKg,mass0,1e-8);summarize('Sealed boiling and condensation',condensed);
// Backward Euler is first-order/damping: demonstrate transient refinement, not
// merely matching the final steady state. Every tested mesh has three sections.
const refinement=[];
for(const step of [.2,.1,.05,.025]){const model=createEvaporator(engine,{maxStep:step}),s=model.create(spec([4,4,4])),r=check(model.advance(s,1));refinement.push({step,row:r});}
const errors=refinement.slice(0,3).map(v=>Math.abs(v.row.terminal.h-refinement[3].row.terminal.h));assert(errors[0]>errors[1]&&errors[1]>errors[2]);report.refinement=refinement.map(v=>({step:v.step,terminalPressure:v.row.terminal.p,terminalEnthalpy:v.row.terminal.h,terminalQuality:v.row.terminal.quality}));
const directTransient=refinement.at(-1).row;report.transientReferenceErrors={pressureBar:0,enthalpyKJkg:0,temperatureK:0};
directTransient.sections.forEach((v,i)=>{const b=reference.transient.sections[i],errors={pressureBar:Math.abs(v.p-b.p),enthalpyKJkg:Math.abs(v.h-b.h),temperatureK:Math.abs(v.T-b.T)};for(const[k,a]of Object.entries(errors))report.transientReferenceErrors[k]=Math.max(report.transientReferenceErrors[k],a);assert(errors.pressureBar<.002&&errors.enthalpyKJkg<.1&&errors.temperatureK<.05);});
const steadyRefined=[];for(const step of [.5,.25,.125]){const model=createEvaporator(engine,{maxStep:step}),s=model.create(spec()),r=check(model.advance(s,120));steadyRefined.push(r);summarize('Steady refinement '+step,r);}for(const r of steadyRefined){near(r.terminal.p,steadyRefined.at(-1).terminal.p,1e-5);near(r.terminal.h,steadyRefined.at(-1).terminal.h,.001);}
// Rollback: a rejected trial cannot consume physical time/energy. A true domain
// stop is distinct from a deliberately inadequate nonlinear iteration budget.
const failing=createEvaporator(engine,{maxIterations:1,minStep:.5,maxStep:.5}),faulted=failing.create(spec()),physical=copy(faulted.cells),ledgerBefore=copy(faulted.ledger);const failure=failing.advance(faulted,1);assert.equal(failure.stop.kind,'solver');assert.equal(faulted.seconds,0);assert.deepEqual(faulted.cells,physical);assert.deepEqual(faulted.ledger,ledgerBefore);const frozen=JSON.stringify(faulted);failing.advance(faulted,10);assert.equal(JSON.stringify(faulted),frozen);
const hot=m.create(spec([2,4,12])),domain=m.advance(hot,10);assert.equal(domain.stop.kind,'domain');assert.match(domain.stop.message,/property table/);assert(domain.terminal.superheatK>249);summarize('Unsupported startup enthalpy is a domain stop',domain);
// Extended isolated operation, bounded state and conservative ledgers.
const long=m.create(spec()),started=performance.now(),longRow=check(m.advance(long,3600));assert(!longRow.terminal.wet);assert(longRow.totals.massKg<.1);summarize('One-hour isolated three-section operation',longRow,performance.now()-started);
const wetLong=m.create(spec([4,4,4])),wetLongRow=check(m.advance(wetLong,3600));assert(wetLongRow.terminal.wet);assert.equal(wetLongRow.terminal.superheatK,0);summarize('One-hour wet isolated operation without fabricated dry vapor',wetLongRow);
report.passed=true;report.checks='Three-section only: direct EOS, independent steady shooting, mixture flux, reverse/check/closed flow, cold startup, heat/feed disturbances, wet/dry transitions, liquid-full transport, sealed boiling/condensation, per-section/global ledgers, atomic edits, rejection rollback, domain/solver distinction, transient/steady timestep refinement and one-hour operation.';
if(process.argv[2])fs.writeFileSync(path.resolve(process.argv[2]),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
