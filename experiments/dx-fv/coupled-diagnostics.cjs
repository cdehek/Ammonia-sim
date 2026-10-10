'use strict';
// Observes unmodified numerical decisions. No alternative EOS/solver is used
// in an integrated trajectory; analytic PH inversion below is diagnostic only.
const fs=require('node:fs'),assert=require('node:assert/strict'),zlib=require('node:zlib'),crypto=require('node:crypto');
const engine=require('../../engine').createEngine(require('../../properties.json')),data=require('../../properties.json');
const {createCoupledModel}=require('./coupled-model.cjs'),{candidateFactory}=require('./coupled-candidate.cjs');
const {cases,accuracyOptions}=require('./coupled-fixtures.cjs');
const output=process.argv[2],raw=process.argv[3];
if(!output||!raw)throw Error('Output JSON and failed-attempt JSONL.gz paths required.');
fs.writeFileSync(raw,'');
const candidate=candidateFactory(),report={stage:'2A-R',runtime:process.version,candidate:candidate.commit,
  observerContract:'Detached diagnostics only; tolerances, perturbations, line search, method and heat transfer unchanged.',cases:[],failedNewtonAttempts:[]};
const hash=s=>crypto.createHash('sha256').update(JSON.stringify(s)).digest('hex');
const physical=s=>({cells:s.cells,energies:s.energies,seconds:s.seconds,ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,
  trace:s.trace,rejectionTrace:s.rejectionTrace,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps,attemptedResidualEvaluations:s.attemptedResidualEvaluations});
function run(c,tolerance,create,observer){
 const options={...accuracyOptions(tolerance),trace:true},m=create(engine,options,observer),s=m.create(c.config),start=performance.now();
 for(const t of c.samples){const r=m.advance(s,t-s.seconds);assert.equal(r.stop,null);}
 const r=m.record(s);assert.ok(Math.abs(r.combinedEnergyResidualKJ)<1e-6);assert.ok(r.nodes.every(n=>Math.abs(n.residualKJ)<1e-6));
 return {s,elapsedMS:performance.now()-start,hash:hash(physical(s)),record:r};
}
function observed(c,tolerance){
 const stats={attempts:0,failedNewton:0,accuracyRejected:0,eventRejected:0,iterationExhaustions:0,lineSearchFailures:0,
  derivativeOutcomes:{},lineSearchOutcomes:{},phaseFailures:{},dominantFailures:{},maxConvergedThermalResidualK:0,
  failedThermalResidualK:{min:null,max:0},failedFluidNorm:{min:null,max:0},failedThermalNorm:{min:null,max:0}};
 const observer=a=>{
  stats.attempts++;
  if(a.rejectionReason==='accuracy')stats.accuracyRejected++;
  if(a.rejectionReason==='event')stats.eventRejected++;
  const contexts=new Map();
  for(const e of a.events){
   if(e.type==='iteration'&&e.context)contexts.set(e.solveId,e.context);
   if(e.type==='derivative')stats.derivativeOutcomes[e.outcome]=(stats.derivativeOutcomes[e.outcome]||0)+1;
   if(e.type==='line-search')stats.lineSearchOutcomes[e.outcome]=(stats.lineSearchOutcomes[e.outcome]||0)+1;
   if(e.type==='iteration'&&e.status==='converged')stats.maxConvergedThermalResidualK=Math.max(stats.maxConvergedThermalResidualK,
    ...e.residual.slice(10).map((v,i)=>Math.abs(v)*contexts.get(e.solveId).physicalScales[10+i]/contexts.get(e.solveId).thermalCapacitiesKJK[i]));
  }
  const failed=a.events.filter(e=>e.type==='solve-failed');
  for(const e of failed){
   stats.failedNewton++;if(e.message.includes('iteration budget'))stats.iterationExhaustions++;
   if(e.message.includes('line search'))stats.lineSearchFailures++;
   const last=e.lastIteration,context=e.context;
   if(!last){report.failedNewtonAttempts.push({case:c.name,tolerance,startSeconds:a.startSeconds,trialSeconds:a.trialSeconds,message:e.message,residualAvailable:false});continue;}
   const label=context.labels[last.dominantIndex],phases=[...new Set(last.states.map(s=>s.phase))].sort().join(' / ');
   stats.dominantFailures[label]=(stats.dominantFailures[label]||0)+1;
   stats.phaseFailures[phases]=(stats.phaseFailures[phases]||0)+1;
   const thermalK=Math.max(...last.residual.slice(10).map((v,i)=>Math.abs(v)*context.physicalScales[10+i]/context.thermalCapacitiesKJK[i]));
   for(const [key,value]of [['failedThermalResidualK',thermalK],['failedFluidNorm',last.fluidNorm],['failedThermalNorm',last.thermalNorm]]){
    stats[key].min=stats[key].min===null?value:Math.min(stats[key].min,value);stats[key].max=Math.max(stats[key].max,value);
   }
   report.failedNewtonAttempts.push({case:c.name,tolerance,startSeconds:a.startSeconds,trialSeconds:a.trialSeconds,stageSeconds:context.stageSeconds,
    solveId:e.solveId,message:e.message,iteration:last.iteration,fluidNorm:last.fluidNorm,thermalNorm:last.thermalNorm,dominant:label,
    thermalResidualK:thermalK,phases,states:last.states,
    physicalResiduals:last.residual.map((v,i)=>({label:context.labels[i],value:v*context.physicalScales[i],unit:i<10&&i%2===0?'kg':'kJ'}))});
  }
  // Complete derivative/line-search/iteration histories of EVERY failed solve;
  // separate gzip members bound memory to a single trial, readable as JSONL.
  if(failed.length)fs.appendFileSync(raw,zlib.gzipSync(JSON.stringify({case:c.name,tolerance,...a})+'\n'));
 };
 const result=run(c,tolerance,createCoupledModel,observer);
 return {...result,stats};
}
try{
 for(const name of ['cold','warm','heat-reversal']){
  const c=cases().find(c=>c.name===name);
  for(const tolerance of name==='heat-reversal'?[1e-6,1e-7,1e-8]:[1e-6]){
   console.error('Node22 diagnostic '+name+' '+tolerance);
   const before=run(c,tolerance,candidate.create),plain=run(c,tolerance,createCoupledModel),diagnostic=observed(c,tolerance);
   assert.equal(before.hash,plain.hash,'Correction must preserve ordinary numerical behavior.');
   assert.equal(plain.hash,diagnostic.hash,'Observations must preserve every physical/adaptive decision.');
   report.cases.push({name,tolerance,intervalSeconds:c.samples.at(-1),identicalCandidateCorrectedObservedHash:plain.hash,
    elapsedMS:{candidate:before.elapsedMS,corrected:plain.elapsedMS,diagnostic:diagnostic.elapsedMS},
    acceptedTrials:diagnostic.s.trace.length,rejectedTrials:diagnostic.s.rejectedSteps,stats:diagnostic.stats,
    combinedEnergyResidualKJ:diagnostic.record.combinedEnergyResidualKJ,maximumNodeResidualKJ:Math.max(...diagnostic.record.nodes.map(n=>Math.abs(n.residualKJ)))});
  }
 }
 // An independently computed exact piecewise-linear inverse of table enthalpy
 // isolates inversion quantization from table interpolation/EOS error.
 const logp=data.p.map(Math.log);
 function analytic(p,h){
  let i=0;while(i<logp.length-2&&logp[i+1]<=Math.log(p))i++;
  const w=(Math.log(p)-logp[i])/(logp[i+1]-logp[i]),sat=engine.sat(p),vapor=h>sat.hg,rows=vapor?data.vapor:data.liquid,axis=vapor?data.sh:data.sc;
  if(h>=sat.hf&&h<=sat.hg)return sat.T;
  const hs=axis.map((_,j)=>rows[i][j]&&rows[i+1][j]?(1-w)*rows[i][j][0]+w*rows[i+1][j][0]:null);
  let j=0;while(j<axis.length-2&&hs[j+1]!==null&&(vapor?hs[j+1]<h:hs[j+1]>h))j++;
  assert.ok(hs[j]!==null&&hs[j+1]!==null);
  const offset=axis[j]+(h-hs[j])/(hs[j+1]-hs[j])*(axis[j+1]-axis[j]);
  return sat.T+(vapor?offset:-offset);
 }
 const points=[{p:3.65,h:1650},{p:3.5,h:engine.sat(3.5).hf-20}];
 for(const failed of report.failedNewtonAttempts.filter(x=>x.states).slice(0,30))points.push(...failed.states.filter(s=>s.x===null).map(({p,h})=>({p,h})));
 const quantization=points.map(({p,h})=>{
  const T=engine.ph(p,h).T,exact=analytic(p,h),same=[];
  for(const dh of [1e-13,1e-12,1e-11,1e-10,1e-9,1e-8])same.push({enthalpyPerturbationKJkg:dh,sameTemperature:engine.ph(p,h+dh).T===T,deltaTemperatureK:engine.ph(p,h+dh).T-T});
  return {p,h,phase:engine.ph(p,h).phase,errorAgainstAnalyticTableInverseK:T-exact,perturbations:same};
 });
 report.propertyResolution={preservedPHIterations:38,vaporSearchWidthK:250,vaporQuantizationWidthK:250/2**38,
  liquidSearchMaximumWidthK:30,liquidQuantizationMaximumWidthK:30/2**38,thermalClosureBudgetK:1e-12,
  maximumMeasuredAnalyticInverseErrorK:Math.max(...quantization.map(x=>Math.abs(x.errorAgainstAnalyticTableInverseK))),points:quantization,
  interpretation:'Quantization is measured within the same table, not direct-EOS interpolation error. Converged closures do meet 1e-12 K, but failed attempts show it is not achieved consistently at proposed larger steps; no tolerance remedy was adopted.'};
 report.failedHistory={path:raw.split('/').at(-1),format:'Concatenated gzip JSONL members; complete events for every failed Newton attempt',
  bytes:fs.statSync(raw).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(raw)).digest('hex')};
 report.passed=true;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:true,cases:report.cases.map(c=>({name:c.name,tolerance:c.tolerance,accepted:c.acceptedTrials,rejected:c.rejectedTrials,stats:c.stats})),propertyResolution:report.propertyResolution.maximumMeasuredAnalyticInverseErrorK}));
}catch(error){report.passed=false;report.failure={message:error.message,stack:error.stack};fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(error);process.exitCode=1;}
