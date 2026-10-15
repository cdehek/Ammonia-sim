'use strict';
const {createThermodynamics}=require('./thermodynamics.cjs'),C=require('./conservation.cjs'),{connectionFlow}=require('./hydraulics.cjs'),{newton}=require('./implicit.cjs');
const Time=require('./time-control.cjs');
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
 const thermo=createThermodynamics(engine),numerics={maxStep:.5,minStep:1e-5,nonlinearTolerance:1e-11,maxIterations:24,maxAttempts:100000,method:'backward-euler',adaptive:false,relativeTolerance:1e-5,massAbsoluteKg:1e-10,energyAbsoluteKJ:1e-7,pressureAbsoluteBar:1e-6,enthalpyAbsoluteKJkg:1e-3,eventStepSeconds:.002,...(options.adaptive===true?Time.adaptiveDefaults:{}),...options};
 if(!Number.isFinite(numerics.maxStep)||!Number.isFinite(numerics.minStep)||numerics.minStep<=0||numerics.maxStep<numerics.minStep||!Number.isFinite(numerics.nonlinearTolerance)||numerics.nonlinearTolerance<=0||!Number.isInteger(numerics.maxIterations)||numerics.maxIterations<1||!Number.isInteger(numerics.maxAttempts)||numerics.maxAttempts<1)throw Error('Invalid implicit numerical settings.');
 if(!['backward-euler','trapezoid','tr-bdf2'].includes(numerics.method)||typeof numerics.adaptive!=='boolean')throw Error('Invalid integration method/mode.');
 for(const key of ['relativeTolerance','massAbsoluteKg','energyAbsoluteKJ','pressureAbsoluteBar','enthalpyAbsoluteKJkg','eventStepSeconds'])if(!Number.isFinite(numerics[key])||numerics[key]<=0)throw Error('Positive finite time-accuracy settings required.');
 let workCalls=0,workIterations=0;
 const order=numerics.method==='backward-euler'?1:2;
 function create(config){
  const spec=normalize(config),cells=spec.initial.map((v,i)=>thermo.initialize(v.p,v.h,spec.totalVolumeM3*spec.volumeFractions[i]));
  thermo.ph(spec.inlet.p,spec.inlet.h);thermo.ph(spec.outlet.p,spec.outlet.h);
  return {schemaVersion:1,model:'experimental-dx-fv',spec,seconds:0,cells,initial:C.totals(cells),initialCells:clone(cells),ledger:{massKg:0,energyKJ:0,heatKJ:0,boundaryEnthalpyKJ:0,sectionHeatKJ:cells.map(()=>0),faces:spec.connections.map(()=>({massKg:0,energyKJ:0}))},acceptedSteps:0,rejectedSteps:0,iterations:0,residualEvaluations:0,lastResidual:null,lastFluxes:null,stop:null,nextStepSeconds:numerics.maxStep,lastTimeError:null,accuracyRejectedSteps:0,eventRejectedSteps:0,attemptedResidualEvaluations:0,attemptedIterations:0,minAcceptedStepSeconds:null,maxAcceptedStepSeconds:0,events:[]};
 }
 function transport(spec,states){
  const nodes=[thermo.ph(spec.inlet.p,spec.inlet.h),...states,thermo.ph(spec.outlet.p,spec.outlet.h)];
  return spec.connections.map((face,i)=>{const flow=face.closed?0:connectionFlow(nodes[i],nodes[i+1],face);return C.flux(flow,flow>=0?nodes[i]:nodes[i+1]);});
 }
 function blendFaces(terms){
  return terms[0][1].map((_,i)=>({massKgS:terms.reduce((sum,[w,faces])=>sum+w*faces[i].massKgS,0),energyKW:terms.reduce((sum,[w,faces])=>sum+w*faces[i].energyKW,0)}));
 }
 function solveStage(spec,old,base,dt,known,weight,guess){
  const scales=old.flatMap(v=>[Math.max(.01,v.massKg),Math.max(1,Math.abs(v.internalEnergyKJ))]);
  const solved=newton(x=>{
   const states=old.map((_,i)=>thermo.ph(x[2*i],x[2*i+1])),cells=states.map((state,i)=>({...C.inventory(state,old[i].volumeM3),volumeM3:old[i].volumeM3,pressureGuess:state.p}));
   const endpointFaces=transport(spec,states),faces=blendFaces([...known,[weight,endpointFaces]]),rates=C.assemble(faces,spec.heatKW);
   const residual=cells.flatMap((v,i)=>[(v.massKg-base[i].massKg-dt*rates[i].massKgS)/scales[2*i],(v.internalEnergyKJ-base[i].internalEnergyKJ-dt*rates[i].energyKW)/scales[2*i+1]]);
   return {residual,cells,faces,states,endpointFaces};
  },guess.flatMap(v=>[v.p,v.h]),{tolerance:numerics.nonlinearTolerance,maxIterations:numerics.maxIterations,lineSearchMinimum:numerics.adaptive||order===2?2**-28:1/4096,onEvaluation:()=>workCalls++,onIteration:()=>workIterations++,pressureDifference:numerics.adaptive||order===2?1e-7:1e-5,enthalpyDifference:numerics.adaptive||order===2?1e-8:1e-4,sameRegion:numerics.adaptive||order===2?(a,b,k)=>{const phase=v=>v.x===null?(v.phase.includes('liquid')?'liquid':'vapor'):'mixture';return phase(a.states[Math.floor(k/2)])===phase(b.states[Math.floor(k/2)]);}:null});
  // Canonical recovery is part of acceptance, including every implicit stage.
  solved.value.cells.forEach(thermo.recover);return solved;
 }
 function coordinates(cell){return thermo.ph(cell.pressureGuess,(cell.internalEnergyKJ+100*cell.pressureGuess*cell.volumeM3)/cell.massKg);}
 function trial(s,dt){
  if(!Number.isFinite(dt)||dt<=0)throw Error('Trial step must be positive and finite.');
  const old=s.cells,previous=old.map(numerics.adaptive||order===2?coordinates:thermo.recover);
  if(numerics.method==='backward-euler')return solveStage(s.spec,old,old,dt,[],1,previous);
  const initialFaces=transport(s.spec,previous);
  if(numerics.method==='trapezoid')return solveStage(s.spec,old,old,dt,[[.5,initialFaces]],.5,previous);
  // TR-BDF2, gamma=2-sqrt(2): self-starting, second order and L-stable.
  // Eliminating the stage inventory yields positive face quadrature weights.
  const gamma=2-Math.sqrt(2),a=1/(2*(2-gamma)),b=(1-gamma)/(2-gamma);
  const stage=solveStage(s.spec,old,old,gamma*dt,[[.5,initialFaces]],.5,previous);
  const solved=solveStage(s.spec,old,old,dt,[[a,initialFaces],[a,stage.value.endpointFaces]],b,stage.value.states);
  solved.calls+=stage.calls;solved.iterations+=stage.iterations;solved.error=Math.max(stage.error,solved.error);
  return solved;
 }
 function commit(s,t,dt,error){
  const before=s.cells.map(numerics.adaptive||order===2?coordinates:thermo.recover),after=t.value.states;
  for(const event of Time.crossings(before,after,engine.sat)){
   const fraction=Math.abs(event.left)/(Math.abs(event.left)+Math.abs(event.right));
   s.events.push({section:event.section,boundary:event.boundary,direction:event.direction,seconds:s.seconds+dt*fraction,bracketStartSeconds:s.seconds,bracketEndSeconds:s.seconds+dt});
  }
  s.cells=t.value.cells;s.seconds+=dt;s.acceptedSteps++;s.iterations+=t.iterations;s.residualEvaluations+=t.calls;s.lastResidual=t.error;s.lastFluxes=t.value.endpointFaces;s.lastTimeError=error;
  s.minAcceptedStepSeconds=s.minAcceptedStepSeconds===null?dt:Math.min(s.minAcceptedStepSeconds,dt);s.maxAcceptedStepSeconds=Math.max(s.maxAcceptedStepSeconds,dt);
  const first=t.value.faces[0],last=t.value.faces.at(-1),heat=s.spec.heatKW.reduce((a,b)=>a+b,0),mass=dt*(first.massKgS-last.massKgS),portEnergy=dt*(first.energyKW-last.energyKW);
  s.ledger.massKg+=mass;s.ledger.boundaryEnthalpyKJ+=portEnergy;s.ledger.heatKJ+=dt*heat;s.ledger.energyKJ+=portEnergy+dt*heat;
  s.spec.heatKW.forEach((q,i)=>{s.ledger.sectionHeatKJ[i]+=dt*q;});
  t.value.faces.forEach((f,i)=>{s.ledger.faces[i].massKg+=dt*f.massKgS;s.ledger.faces[i].energyKJ+=dt*f.energyKW;});
 }
 function advance(s,seconds){
  if(!Number.isFinite(seconds)||seconds<=0)throw Error('Advance duration must be finite and positive.');if(s.stop)return record(s);
  let remaining=seconds,dt=numerics.adaptive?s.nextStepSeconds:numerics.maxStep,attempts=0;
  while(remaining>1e-12){
   dt=Math.min(dt,remaining);let pieces,error=null,reason=null;const callsBefore=workCalls,iterationsBefore=workIterations;
   try{
    if(++attempts>numerics.maxAttempts)throw Error('Implicit attempt budget exhausted.');
    const coarse=trial(s,dt);
    pieces=[[coarse,dt]];
    if(numerics.adaptive){
     const half=trial(s,dt/2),second=trial({...s,cells:half.value.cells},dt/2);
     error=Time.estimate(coarse.value,second.value,{cells:s.cells,states:s.cells.map(coordinates)},order,numerics);
     if(!Number.isFinite(error))throw Error('Non-finite temporal error estimate.');
     pieces=[[half,dt/2],[second,dt/2]];
     const events=[...Time.crossings(s.cells.map(coordinates),half.value.states,engine.sat),...Time.crossings(half.value.states,second.value.states,engine.sat)];
     if(error>1)reason='accuracy';else if(events.length&&dt/2>numerics.eventStepSeconds)reason='event';
    }
   }catch(cause){
    s.rejectedSteps++;
    if(dt/2<numerics.minStep||attempts>numerics.maxAttempts){
     // A failed line search is not automatically a domain stop. At an exhausted
     // very small step, corroborate encountered domain trials with independent
     // canonical recovery of the local M/U transport direction. Diagnostic only;
     // no predictor is ever accepted or charged to a ledger.
     let boundaryCause=null;
     if(cause.domainCause&&dt<=1e-6){const rates=C.assemble(transport(s.spec,s.cells.map(coordinates)),s.spec.heatKW);s.cells.forEach((cell,i)=>{try{thermo.recover({...cell,massKg:cell.massKg+dt*rates[i].massKgS,internalEnergyKJ:cell.internalEnergyKJ+dt*rates[i].energyKW});}catch(error){if(error.faultKind==='domain')boundaryCause=error;}});}
     s.stop={kind:boundaryCause?'domain':cause.faultKind||'solver',message:boundaryCause?boundaryCause.message:cause.message,seconds:s.seconds,attemptedStepSeconds:dt,...(boundaryCause?{numericalCause:cause.message,domainEvidence:'Local conservative M/U transport direction leaves the bounded EOS at the exhausted step.'}:{})};break;
    }
    dt/=2;continue;
   }finally{s.attemptedResidualEvaluations+=workCalls-callsBefore;s.attemptedIterations+=workIterations-iterationsBefore;}
   if(reason){
    s.rejectedSteps++;if(reason==='accuracy')s.accuracyRejectedSteps++;else s.eventRejectedSteps++;
    const next=reason==='accuracy'?dt*Time.factor(error,order,false):Math.min(dt/2,2*numerics.eventStepSeconds);
    if(next<numerics.minStep){s.stop={kind:'accuracy',message:'Temporal error/event tolerance cannot be met above the minimum step.',seconds:s.seconds,attemptedStepSeconds:dt,error};break;}
    dt=next;continue;
   }
   // Coarse and rejected candidates never change time, physical state or ledgers.
   for(const [piece,step]of pieces)commit(s,piece,step,error);
   remaining-=dt;
   dt=Math.min(numerics.maxStep,numerics.adaptive?dt*Time.factor(error,order,true):dt*2);
   s.nextStepSeconds=dt;
  }
  return record(s);
 }
 function update(s,patch){
  if(!patch||typeof patch!=='object'||Array.isArray(patch)||Object.keys(patch).some(k=>!['heatKW','inlet','outlet','connections'].includes(k)))throw Error('Only isolated boundaries, heat and connections can change.');
  const next=normalize({...s.spec,...clone(patch)});thermo.ph(next.inlet.p,next.inlet.h);thermo.ph(next.outlet.p,next.outlet.h);s.spec=next;if(numerics.adaptive)s.nextStepSeconds=Math.max(numerics.minStep,Math.min(numerics.maxStep,.05));return record(s);
 }
 function record(s){
  const sections=s.cells.map(thermo.recover),sum=C.totals(s.cells),last=sections.at(-1);
  const sectionResiduals=s.cells.map((c,i)=>({massKg:c.massKg-s.initialCells[i].massKg-s.ledger.faces[i].massKg+s.ledger.faces[i+1].massKg,energyKJ:c.internalEnergyKJ-s.initialCells[i].internalEnergyKJ-s.ledger.sectionHeatKJ[i]-s.ledger.faces[i].energyKJ+s.ledger.faces[i+1].energyKJ}));
  return clone({model:s.model,seconds:s.seconds,sectionCount:s.cells.length,sections,sectionResiduals,terminal:{p:last.p,h:last.h,T:last.T,phase:last.phase,quality:last.x,wet:last.wet,superheatK:last.superheatK},totals:sum,ledger:s.ledger,massResidualKg:sum.massKg-s.initial.massKg-s.ledger.massKg,energyResidualKJ:sum.internalEnergyKJ-s.initial.internalEnergyKJ-s.ledger.energyKJ,integration:{method:numerics.method,order,adaptive:numerics.adaptive,relativeTolerance:numerics.relativeTolerance,eventStepSeconds:numerics.eventStepSeconds},events:s.events,lastTimeError:s.lastTimeError,accuracyRejectedSteps:s.accuracyRejectedSteps,eventRejectedSteps:s.eventRejectedSteps,attemptedResidualEvaluations:s.attemptedResidualEvaluations,attemptedIterations:s.attemptedIterations,minAcceptedStepSeconds:s.minAcceptedStepSeconds,maxAcceptedStepSeconds:s.maxAcceptedStepSeconds,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps,nonlinearIterations:s.iterations,acceptedResidualEvaluations:s.residualEvaluations,lastResidual:s.lastResidual,lastFluxes:s.lastFluxes,stop:s.stop});
 }
 return {create,advance,update,record,trial,thermo,numerics};
}
module.exports={createEvaporator,normalize};
