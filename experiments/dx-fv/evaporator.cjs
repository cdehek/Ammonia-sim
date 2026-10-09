'use strict';
const {createThermodynamics}=require('./thermodynamics.cjs'),C=require('./conservation.cjs'),{connectionFlow}=require('./hydraulics.cjs'),{newton}=require('./implicit.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
function normalize(config){
 const c={sectionCount:3,totalVolumeM3:.003,diameterM:.02,viscosityPaS:1e-5,darcyF:.02,inletMinorK:20,outletMinorK:2,...clone(config)};
 if(!Number.isInteger(c.sectionCount)||c.sectionCount<1||c.sectionCount>64)throw Error('Section count must be an integer from 1 to 64.');
 for(const k of ['totalVolumeM3','diameterM','viscosityPaS'])if(!Number.isFinite(c[k])||c[k]<=0)throw Error('Positive geometry/viscosity required.');
 for(const k of ['darcyF','inletMinorK','outletMinorK'])if(!Number.isFinite(c[k])||c[k]<0)throw Error('Nonnegative hydraulic loss required.');
 const n=c.sectionCount;
 c.volumeFractions=c.volumeFractions||Array(n).fill(1/n);c.heatKW=c.heatKW||Array(n).fill(0);
 if(c.volumeFractions.length!==n||c.volumeFractions.some(v=>!Number.isFinite(v)||v<=0)||Math.abs(c.volumeFractions.reduce((a,b)=>a+b,0)-1)>1e-12)throw Error('Section volumes must sum to total volume.');
 if(c.heatKW.length!==n||c.heatKW.some(q=>!Number.isFinite(q)))throw Error('One finite heat input is required per section.');
 if(!Array.isArray(c.initial)||c.initial.length!==n||!c.inlet||!c.outlet)throw Error('Initial section and boundary p/h states are required.');
 for(const state of [...c.initial,c.inlet,c.outlet])if(!Number.isFinite(state.p)||!Number.isFinite(state.h))throw Error('Finite p/h states required.');
 c.connections=c.connections||Array.from({length:n+1},(_,i)=>({diameterM:c.diameterM,viscosityPaS:c.viscosityPaS,darcyF:c.darcyF,minorK:i===0?c.inletMinorK:i===n?c.outletMinorK:0,lengthM:c.totalVolumeM3/(Math.PI*c.diameterM**2/4)*(i===0?c.volumeFractions[0]/2:i===n?c.volumeFractions[n-1]/2:(c.volumeFractions[i-1]+c.volumeFractions[i])/2),checkValve:false}));
 if(c.connections.length!==n+1)throw Error('One connection is required at each section boundary.');
 for(const face of c.connections){for(const k of ['diameterM','lengthM','viscosityPaS'])if(!Number.isFinite(face[k])||face[k]<=0)throw Error('Invalid face geometry.');for(const k of ['darcyF','minorK'])if(!Number.isFinite(face[k])||face[k]<0)throw Error('Invalid face resistance.');if(typeof face.checkValve!=='boolean'||face.closed!==undefined&&typeof face.closed!=='boolean')throw Error('Connection valve behavior must be boolean.');}
 return c;
}
function createEvaporator(engine,options={}){
 const thermo=createThermodynamics(engine),numerics={maxStep:.5,minStep:1e-5,nonlinearTolerance:1e-11,maxIterations:24,maxAttempts:100000,...options};
 if(!Number.isFinite(numerics.maxStep)||!Number.isFinite(numerics.minStep)||numerics.minStep<=0||numerics.maxStep<numerics.minStep||!Number.isFinite(numerics.nonlinearTolerance)||numerics.nonlinearTolerance<=0||!Number.isInteger(numerics.maxIterations)||numerics.maxIterations<1||!Number.isInteger(numerics.maxAttempts)||numerics.maxAttempts<1)throw Error('Invalid implicit numerical settings.');
 function create(config){
  const spec=normalize(config),cells=spec.initial.map((v,i)=>thermo.initialize(v.p,v.h,spec.totalVolumeM3*spec.volumeFractions[i]));
  thermo.ph(spec.inlet.p,spec.inlet.h);thermo.ph(spec.outlet.p,spec.outlet.h);
  return {schemaVersion:1,model:'experimental-dx-fv',spec,seconds:0,cells,initial:C.totals(cells),initialCells:clone(cells),ledger:{massKg:0,energyKJ:0,heatKJ:0,boundaryEnthalpyKJ:0,sectionHeatKJ:cells.map(()=>0),faces:spec.connections.map(()=>({massKg:0,energyKJ:0}))},acceptedSteps:0,rejectedSteps:0,iterations:0,residualEvaluations:0,lastResidual:null,lastFluxes:null,stop:null};
 }
 function transport(spec,states){
  const nodes=[thermo.ph(spec.inlet.p,spec.inlet.h),...states,thermo.ph(spec.outlet.p,spec.outlet.h)];
  return spec.connections.map((face,i)=>{const flow=face.closed?0:connectionFlow(nodes[i],nodes[i+1],face);return C.flux(flow,flow>=0?nodes[i]:nodes[i+1]);});
 }
 function trial(s,dt){
  const old=s.cells,previous=old.map(thermo.recover),scales=old.flatMap(v=>[Math.max(.01,v.massKg),Math.max(1,Math.abs(v.internalEnergyKJ))]);
  const solved=newton(x=>{
   const states=old.map((_,i)=>thermo.ph(x[2*i],x[2*i+1])),cells=states.map((state,i)=>({...C.inventory(state,old[i].volumeM3),volumeM3:old[i].volumeM3,pressureGuess:state.p}));
   const faces=transport(s.spec,states),rates=C.assemble(faces,s.spec.heatKW),residual=cells.flatMap((v,i)=>[(v.massKg-old[i].massKg-dt*rates[i].massKgS)/scales[2*i],(v.internalEnergyKJ-old[i].internalEnergyKJ-dt*rates[i].energyKW)/scales[2*i+1]]);
   return {residual,cells,faces,states};
  },previous.flatMap(v=>[v.p,v.h]),{tolerance:numerics.nonlinearTolerance,maxIterations:numerics.maxIterations});
  // Independent canonical m/U recovery must succeed before any trial is committed.
  solved.value.cells.forEach(thermo.recover);return solved;
 }
 function advance(s,seconds){
  if(!Number.isFinite(seconds)||seconds<=0)throw Error('Advance duration must be finite and positive.');if(s.stop)return record(s);
  let remaining=seconds,dt=numerics.maxStep,attempts=0;
  while(remaining>1e-12){
   dt=Math.min(dt,remaining);let t;
   try{if(++attempts>numerics.maxAttempts)throw Error('Implicit attempt budget exhausted.');t=trial(s,dt);}catch(error){
    s.rejectedSteps++;
    if(dt/2<numerics.minStep||attempts>numerics.maxAttempts){s.stop={kind:error.faultKind||'solver',message:error.message,seconds:s.seconds,attemptedStepSeconds:dt};break;}
    dt/=2;continue;
   }
   s.cells=t.value.cells;s.seconds+=dt;remaining-=dt;s.acceptedSteps++;s.iterations+=t.iterations;s.residualEvaluations+=t.calls;s.lastResidual=t.error;s.lastFluxes=t.value.faces;
   const first=t.value.faces[0],last=t.value.faces.at(-1),heat=s.spec.heatKW.reduce((a,b)=>a+b,0),mass=dt*(first.massKgS-last.massKgS),portEnergy=dt*(first.energyKW-last.energyKW);
   s.ledger.massKg+=mass;s.ledger.boundaryEnthalpyKJ+=portEnergy;s.ledger.heatKJ+=dt*heat;s.ledger.energyKJ+=portEnergy+dt*heat;
   s.spec.heatKW.forEach((q,i)=>{s.ledger.sectionHeatKJ[i]+=dt*q;});
   t.value.faces.forEach((f,i)=>{s.ledger.faces[i].massKg+=dt*f.massKgS;s.ledger.faces[i].energyKJ+=dt*f.energyKW;});
   dt=Math.min(numerics.maxStep,dt*2);
  }
  return record(s);
 }
 function update(s,patch){
  if(!patch||typeof patch!=='object'||Array.isArray(patch)||Object.keys(patch).some(k=>!['heatKW','inlet','outlet','connections'].includes(k)))throw Error('Only isolated boundaries, heat and connections can change.');
  const next=normalize({...s.spec,...clone(patch)});thermo.ph(next.inlet.p,next.inlet.h);thermo.ph(next.outlet.p,next.outlet.h);s.spec=next;return record(s);
 }
 function record(s){
  const sections=s.cells.map(thermo.recover),sum=C.totals(s.cells),last=sections.at(-1);
  const sectionResiduals=s.cells.map((c,i)=>({massKg:c.massKg-s.initialCells[i].massKg-s.ledger.faces[i].massKg+s.ledger.faces[i+1].massKg,energyKJ:c.internalEnergyKJ-s.initialCells[i].internalEnergyKJ-s.ledger.sectionHeatKJ[i]-s.ledger.faces[i].energyKJ+s.ledger.faces[i+1].energyKJ}));
  return clone({model:s.model,seconds:s.seconds,sectionCount:s.cells.length,sections,sectionResiduals,terminal:{p:last.p,h:last.h,T:last.T,phase:last.phase,quality:last.x,wet:last.wet,superheatK:last.superheatK},totals:sum,ledger:s.ledger,massResidualKg:sum.massKg-s.initial.massKg-s.ledger.massKg,energyResidualKJ:sum.internalEnergyKJ-s.initial.internalEnergyKJ-s.ledger.energyKJ,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps,nonlinearIterations:s.iterations,acceptedResidualEvaluations:s.residualEvaluations,lastResidual:s.lastResidual,lastFluxes:s.lastFluxes,stop:s.stop});
 }
 return {create,advance,update,record,trial,thermo,numerics};
}
module.exports={createEvaporator,normalize};
