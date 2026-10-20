import{readReceipt,evidenceURL}from'./receipts.mjs';
// Offline analysis: separate original engine, no calls added to integrated solver.
import fs from 'node:fs';import zlib from'node:zlib';import{createHash}from'node:crypto';
import{loader}from'../browser_eos_b9c/candidate-bundle.mjs';import{exact,same,auditRecord,assert}from'../browser_eos_b9/values.mjs';
const B=new URL('./',import.meta.url),E=evidenceURL;
const read=readReceipt;
const save=(name,data)=>fs.writeFileSync(new URL(name+'.json',E),JSON.stringify(data,null,2)+'\n');
const load=loader(),engine=load('table-only.cjs').createTableEngine(),thermo=load('thermodynamics.cjs').createThermodynamics(engine),Time=load('time-control.cjs'),C=load('conservation.cjs');
const labels=Array.from({length:5},(_,i)=>['pressure-'+i,'enthalpy-'+i]).flat().concat(Array.from({length:5},(_,i)=>['tube-'+i,'fin-'+i]).flat(),'air');
const coord=c=>thermo.ph(c.pressureGuess,(c.internalEnergyKJ+100*c.pressureGuess*c.volumeM3)/c.massKg);
const median=a=>[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];
const summary={fixtures:{},boundaries:[],timing:{},limitations:['Inclusive nested timings; not additive','Allocation bytes and GC causal/exclusive attribution not measured','Short-process JIT, timer and diagnostic allocation effects overlap','Output schedule sensitivity is not convergence proof']};
for(const fixture of ['cold','warm']){
 const name=fixture==='cold'?'observed-cold-r1-fixed':'observed-warm-r1',rows=read(name),d=rows.find(r=>r.type==='diagnostics'),check=rows.filter(r=>r.type==='checkpoint'),initial=check[0].science.state,settings=check[0].science.record.settings,last=check.at(-1).science;
 const errors=d.temporals.map(t=>{
  const terms=[],initialStates=t.initialCells.map(coord);
  for(let i=0;i<5;i++){
   for(const[key,abs,unit]of[['massKg',settings.massAbsoluteKg,'kg'],['internalEnergyKJ',settings.energyAbsoluteKJ,'kJ']]){
    const scale=abs+settings.relativeTolerance*Math.max(Math.abs(t.initialCells[i][key]),Math.abs(t.fine.cells[i][key]));
    const delta=t.fine.cells[i][key]-t.coarse.cells[i][key];terms.push({section:i,coordinate:key,label:key+'-'+i,unit,initial:t.initialCells[i][key],coarse:t.coarse.cells[i][key],fine:t.fine.cells[i][key],difference:delta,scale,normalized:Math.abs(delta)/3/scale});
   }
   for(const[key,abs,unit]of[['p',settings.pressureAbsoluteBar,'bar absolute'],['h',settings.enthalpyAbsoluteKJkg,'kJ/kg']]){
    const scale=abs+settings.relativeTolerance*Math.max(Math.abs(initialStates[i][key]),Math.abs(t.fine.states[i][key]));const delta=t.fine.states[i][key]-t.coarse.states[i][key];
    terms.push({section:i,coordinate:key,label:key+'-'+i,unit,initial:initialStates[i][key],coarse:t.coarse.states[i][key],fine:t.fine.states[i][key],difference:delta,scale,normalized:Math.abs(delta)/3/scale});
   }
  }
  for(let i=0;i<11;i++){
   const capacity=initial.spec.thermal.nodes[i].capacityKJK,delta=t.fine.energies[i]-t.coarse.energies[i],scaleK=settings.temperatureAbsoluteK+settings.relativeTolerance*settings.temperatureScaleK;
   terms.push({node:labels[10+i],coordinate:'thermal-energy',label:labels[10+i],unit:'kJ',initial:t.initialEnergies[i],coarse:t.coarse.energies[i],fine:t.fine.energies[i],difference:delta,capacityKJK:capacity,scaleK,normalized:Math.abs(delta)/3/capacity/scaleK});
  }
  const aggregate=Math.max(...terms.map(v=>v.normalized));assert(same(aggregate,t.error),'original temporal maximum exact');
  const accepted=!t.failure&&!t.rejectionReason,leading=[...terms].sort((a,b)=>b.normalized-a.normalized),proposal=t.trialSeconds*Time.factor(t.error,2,accepted);
  const acceptedController=accepted?d.controllers.find(v=>same(v.seconds,t.startSeconds+t.trialSeconds)||Math.abs(v.seconds-t.startSeconds-t.trialSeconds)<1e-17):null;
  return {trialIndex:t.trialIndex,startSeconds:t.startSeconds,endSeconds:t.startSeconds+t.trialSeconds,trialSeconds:t.trialSeconds,accepted,rejectionReason:t.rejectionReason,originalError:t.error,reconstructedError:aggregate,bitExact:true,proposal:Math.min(settings.maxStep,proposal),acceptedController,leading:leading.slice(0,5).map(v=>({label:v.label,normalized:v.normalized})),phaseInitial:initialStates.map(v=>v.phase),phaseCoarse:t.coarse.states.map(v=>v.phase),phaseFine:t.fine.states.map(v=>v.phase),terms};
 });
 save('temporal-'+fixture,errors);
 const col=labels.map((label,k)=>{
  const a=d.columns.filter(r=>r.column===k),counts={};for(const r of a)for(const[key,v]of Object.entries(r.counts))counts[key]=(counts[key]||0)+v;
  return {column:k,label,kind:a[0]?.kind,evaluations:a.length,totalMS:a.reduce((s,r)=>s+(r.ms||0),0),medianMS:median(a.map(r=>r.ms||0)),minMS:Math.min(...a.map(r=>r.ms||0)),maxMS:Math.max(...a.map(r=>r.ms||0)),perturbationMin:Math.min(...a.flatMap(r=>r.probes.map(p=>p.step))),perturbationMax:Math.max(...a.flatMap(r=>r.probes.map(p=>p.step))),positiveFirstOnly:a.every(r=>r.probes.length===1&&r.probes[0].step>0&&r.probes[0].shrink===0),counts};
 });save('columns-'+fixture,col);
 const nodes=initial.spec.thermal.nodes,fromState=(cells,energies,ledger)=>{
  const sections=cells.map((c,i)=>{
   const recovered=thermo.recover(c),sat=engine.sat(recovered.p);
   return {section:i,conserved:{massKg:c.massKg,internalEnergyKJ:c.internalEnergyKJ,volumeM3:c.volumeM3},derived:{pBarAbsolute:recovered.p,hKJkg:recovered.h,temperatureK:recovered.T+273.15,quality:recovered.x,phase:recovered.phase,superheatK:recovered.phase==='Superheated vapor'?recovered.T-sat.T:null,saturation:{temperatureK:sat.T+273.15,hfKJkg:sat.hf,hgKJkg:sat.hg,rhofKgM3:sat.rhof,rhogKgM3:sat.rhog},hMinusHgKJkg:recovered.h-sat.hg},PHCoordinates:coord(c)};
  });
  return {sections,nodes:nodes.map((n,i)=>({id:n.id,conservedEnergyRelative273_15K_KJ:energies[i],temperatureK:273.15+energies[i]/n.capacityKJK,capacityKJK:n.capacityKJK})),ledger};
 };
 const accepted=[{seconds:0,...fromState(initial.cells,initial.energies,initial.ledger)}];let auditMax={massKg:0,fluidKJ:0,thermalKJ:0,combinedKJ:0,sectionMassKg:0,sectionEnergyKJ:0,nodeKJ:0,independentNodeKJ:0},lastCells=initial.cells,lastEnergies=initial.energies,lastTime=0;
 for(const c of d.commits){
  const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'}),s={...structuredClone(initial),cells:c.cells,energies:c.energies,ledger:c.ledger,seconds:c.seconds,lastResidual:c.error};const r=model.record(s),audit=auditRecord(r);
  const max=(k,v)=>auditMax[k]=Math.max(auditMax[k],Math.abs(v));max('massKg',audit.mass);max('fluidKJ',audit.fluid);max('thermalKJ',audit.thermal);max('combinedKJ',audit.combined);
  for(const v of audit.sections){max('sectionMassKg',v.massKg);max('sectionEnergyKJ',v.energyKJ);}for(const n of audit.nodes){max('nodeKJ',n.residual);max('independentNodeKJ',n.independent);}
  // Independently recompute instantaneous donor enthalpy from signed flow.
  const current=c.endpoint,props=c.cells.map(coord),fluid=initial.spec.fluid,flowNodes=[thermo.ph(fluid.inlet.p,fluid.inlet.h),...props,thermo.ph(fluid.outlet.p,fluid.outlet.h)];
  current.faces.forEach((f,i)=>assert(Math.abs(f.energyKW-f.massKgS*(f.massKgS>=0?flowNodes[i].h:flowNodes[i+1].h))<1e-10,'donor enthalpy transport'));
  accepted.push({seconds:c.seconds,startSeconds:c.startSeconds,dt:c.dt,...fromState(c.cells,c.energies,c.ledger),acceptedPHStates:c.states,integratedRate:c.integratedRate,endpoint:c.endpoint,audit,changes:{massKg:c.cells.map((v,i)=>v.massKg-lastCells[i].massKg),internalEnergyKJ:c.cells.map((v,i)=>v.internalEnergyKJ-lastCells[i].internalEnergyKJ),thermalEnergyKJ:c.energies.map((v,i)=>v-lastEnergies[i]),elapsedSeconds:c.seconds-lastTime}});
  lastCells=c.cells;lastEnergies=c.energies;lastTime=c.seconds;
 }
 save('accepted-'+fixture,accepted);save('conservation-'+fixture,{passed:true,acceptedHalfStates:d.commits.length,auditMax,donorTransportAudit:true,originalTolerances:{massKg:1e-8,energyKJ:1e-6}});
 const groups={};for(const e of errors){const group=e.startSeconds<.001?'startup':e.endSeconds<.00535?'pre-transition':e.startSeconds<.00543?'transition':'post-transition';const a=groups[group]??={trials:0,rejected:0,dominants:{},maxError:0,thermalMax:0};a.trials++;if(!e.accepted)a.rejected++;a.maxError=Math.max(a.maxError,e.originalError);a.thermalMax=Math.max(a.thermalMax,...e.terms.filter(v=>v.coordinate==='thermal-energy').map(v=>v.normalized));a.dominants[e.leading[0].label]=(a.dominants[e.leading[0].label]||0)+1;}
 summary.fixtures[fixture]={acceptedPhysicalSubsteps:last.state.acceptedSteps,rejected:last.state.rejectedSteps,counts:d.counts,scopesMS:d.ms,calls:d.calls,groups,events:last.state.events,rejections:errors.filter(r=>!r.accepted).map(({terms,...r})=>r),columnTotals:col,ph:d.phaseCalls,phTrials:d.phTrials,repeatPH:d.repeatPH,auditMax};
 if(fixture==='warm'){
  const event=last.state.events[0],bracket=accepted.filter(v=>v.seconds>=event.bracketStartSeconds-1e-17&&v.seconds<=event.bracketEndSeconds+1e-17);save('transition-bracket',{event,acceptedStates:bracket,eventIsInterpolated:true,widthSeconds:event.bracketEndSeconds-event.bracketStartSeconds});
  const p=bracket[0].sections[0].derived.pBarAbsolute,sat=engine.sat(p),probes=[];
  for(const eps of [1e-2,1e-3,1e-4,1e-5]){
   const a=thermo.ph(p,sat.hg-eps),b=thermo.ph(p,sat.hg),c=thermo.ph(p,sat.hg+eps);probes.push({epsilonKJkg:eps,minus:a,at:b,plus:c,derivatives:{rhoLeft:(b.rho-a.rho)/eps,rhoRight:(c.rho-b.rho)/eps,TLeft:(b.T-a.T)/eps,TRight:(c.T-b.T)/eps}});
  }
  const table=load('properties.json'),logs=table.p.map(Math.log);let i=0;while(logs[i+1]<=Math.log(p))i++;save('constitutive-probes',{scope:'Offline PH evaluations of unchanged original engine; not solver perturbations or accepted states',pBarAbsolute:p,sat,probes,pressureBracket:[table.p[i],table.p[i+1]],satRows:[table.sat[i],table.sat[i+1]],vaporZeroRows:[table.vapor[i][0],table.vapor[i+1][0]],vaporFirstRows:[table.vapor[i][1],table.vapor[i+1][1]],fixedInverseIterations:38});
 }
}
for(const schedule of ['added','fine']){
 const file=new URL('canonical-warm-'+schedule+'.jsonl.gz',E);if(!fs.existsSync(file))continue;
 const original=read('canonical-warm-r1').filter(r=>r.type==='checkpoint'),r=read('canonical-warm-'+schedule).filter(r=>r.type==='checkpoint'),last=r.at(-1).science.record;
 const comparisons=[];
 for(const a of original){const b=r.find(r=>r.seconds===a.seconds);if(!b)continue;const settings=a.science.record.settings,terms=[];
  for(let i=0;i<5;i++)for(const[key,abs,unit]of[['massKg',settings.massAbsoluteKg,'kg'],['internalEnergyKJ',settings.energyAbsoluteKJ,'kJ'],['p',settings.pressureAbsoluteBar,'bar absolute'],['h',settings.enthalpyAbsoluteKJkg,'kJ/kg']]){
   const av=['p','h'].includes(key)?a.science.record.sections[i][key]:a.science.state.cells[i][key],bv=['p','h'].includes(key)?b.science.record.sections[i][key]:b.science.state.cells[i][key],scale=abs+settings.relativeTolerance*Math.max(Math.abs(av),Math.abs(bv));terms.push({label:key+'-'+i,difference:bv-av,unit,scale,normalized:Math.abs(bv-av)/scale});
  }
  for(let i=0;i<11;i++){const delta=b.science.state.energies[i]-a.science.state.energies[i],cap=a.science.state.spec.thermal.nodes[i].capacityKJK,scale=settings.temperatureAbsoluteK+settings.relativeTolerance*settings.temperatureScaleK;terms.push({label:labels[10+i],differenceK:delta/cap,scaleK:scale,normalized:Math.abs(delta)/cap/scale});}
  comparisons.push({seconds:a.seconds,maximumToleranceRatio:Math.max(...terms.map(v=>v.normalized)),terms});
 }
 summary.boundaries.push({schedule,acceptedPhysicalSubsteps:last.acceptedSteps,rejected:last.rejectedSteps,events:last.events,rejectionTrace:last.rejectionTrace,comparisons});
}
for(const f of ['cold','warm']){
 const obsNames=[f==='cold'?'observed-cold-r1-fixed':'observed-warm-r1',...['r2','r3'].map(r=>'observed-'+f+'-'+r)],canNames=['r1','r2','r3'].map(r=>'canonical-'+f+'-'+r);
 const measurements=names=>names.filter(n=>fs.existsSync(new URL(n+'.jsonl.gz',E))).map(n=>{const r=read(n),d=r.find(r=>r.type==='diagnostics');return {name:n,advanceWallMS:r.filter(v=>v.type==='checkpoint').reduce((s,v)=>s+v.wallMS,0),advanceCpuMS:r.filter(v=>v.type==='checkpoint').reduce((s,v)=>s+v.cpuMS,0),scopesMS:d.ms,columnMS:labels.map((_,k)=>d.columns.filter(c=>c.column===k).reduce((s,c)=>s+(c.ms||0),0))};});
 const canonical=measurements(canNames),observed=measurements(obsNames),stats=a=>({n:a.length,median:median(a),min:Math.min(...a),max:Math.max(...a)});
 summary.timing[f]={canonical,observed,canonicalWallMS:stats(canonical.map(v=>v.advanceWallMS)),observedWallMS:stats(observed.map(v=>v.advanceWallMS)),medianOverheadRatio:median(observed.map(v=>v.advanceWallMS))/median(canonical.map(v=>v.advanceWallMS))};
}
save('analysis',summary);console.log(JSON.stringify({fixtures:Object.fromEntries(Object.entries(summary.fixtures).map(([k,v])=>[k,{groups:v.groups,rejections:v.rejections.map(x=>({start:x.startSeconds,dt:x.trialSeconds,error:x.originalError,top:x.leading}))}])),boundaries:summary.boundaries.map(v=>({schedule:v.schedule,accepted:v.acceptedPhysicalSubsteps,rejected:v.rejected,max:v.comparisons.at(-1)?.maximumToleranceRatio}))},null,2));
