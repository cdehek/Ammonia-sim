'use strict';
// A0 comparators are consumers of evaluated diagnostics, never solver inputs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const crypto=require('node:crypto'),zlib=require('node:zlib'),Module=require('node:module');
const {execFileSync}=require('node:child_process');
const {createCoupledModel}=require('./coupled-model.cjs');
const {coupledNewton}=require('./coupled-implicit.cjs');
const {cases,accuracyOptions}=require('./coupled-fixtures.cjs');
const data=require('../../properties.json'),{createEngine}=require('../../engine');
const BASE='9a231b1ed5da1dce07f3d613aeb79336ce8541c7';
const hash=x=>crypto.createHash('sha256').update(typeof x==='string'||Buffer.isBuffer(x)?x:JSON.stringify(x)).digest('hex');
const output=process.argv[2],archive=process.argv[3];
if(!output||!archive)throw Error('Usage: node roadmap-a-diagnostics.cjs /tmp/report.json /tmp/probes.jsonl.gz');
assert.match(process.version,/^v22\./,'Use the qualified Node 22 runtime.');
const repositoryRoot=fs.realpathSync(path.resolve(__dirname,'../..'));
for(const file of [output,archive]){
  const resolved=fs.existsSync(file)?fs.realpathSync(file):path.join(fs.realpathSync(path.dirname(path.resolve(file))),path.basename(file));
  assert.ok(resolved!==repositoryRoot&&!resolved.startsWith(repositoryRoot+path.sep),'Generated evidence must be outside the repository.');
}
assert.notEqual(path.resolve(output),path.resolve(archive),'Report and archive need separate paths.');
if(!['--replay','--memory','--memory-worker'].includes(process.argv[4]))fs.writeFileSync(archive,'');
function originalFactory(){
  const load=(file,override)=>{
    const filename=path.join(__dirname,file),m=new Module(filename,module);m.filename=filename;m.paths=module.paths;
    if(override){const ordinary=m.require.bind(m);m.require=id=>id==='./coupled-implicit.cjs'?override:ordinary(id);}
    m._compile(execFileSync('git',['show',BASE+':experiments/dx-fv/'+file],{encoding:'utf8'}),filename);
    return m.exports;
  };
  return load('coupled-model.cjs',load('coupled-implicit.cjs')).createCoupledModel;
}
function countedEngine(){
  const original=createEngine(data),counts={ph:0,sat:0,stateMVU:0},engine={...original};
  for(const key of Object.keys(counts))engine[key]=(...args)=>{counts[key]++;return original[key](...args);};
  return {engine,counts}; // Public calls only; nested engine-internal calls are not counted.
}
const comparatorEngine=createEngine(data),logs=data.p.map(Math.log);
function exactTemperature(p,h){
  const sat=comparatorEngine.sat(p);
  if(h>=sat.hf-1e-8&&h<=sat.hg+1e-8)return sat.T;
  const vapor=h>sat.hg,axis=vapor?data.sh:data.sc,rows=vapor?data.vapor:data.liquid;
  let i=0;while(i<logs.length-2&&logs[i+1]<=Math.log(p))i++;
  const w=(Math.log(p)-logs[i])/(logs[i+1]-logs[i]);
  const hs=axis.map((_,j)=>rows[i][j]&&rows[i+1][j]?rows[i][j][0]+(rows[i+1][j][0]-rows[i][j][0])*w:null);
  let j=0;while(j<axis.length-2&&hs[j+1]!==null&&(vapor?hs[j+1]<h:hs[j+1]>h))j++;
  assert.ok(hs[j]!==null&&hs[j+1]!==null);
  const offset=axis[j]+(h-hs[j])/(hs[j+1]-hs[j])*(axis[j+1]-axis[j]);
  assert.ok(offset>=axis[j]-1e-8&&offset<=axis[j+1]+1e-8);
  return sat.T+(vapor?offset:-offset);
}
function exactColumns(spec,context){
  const nodes=spec.thermal.nodes,ix=new Map(nodes.map((n,i)=>[n.id,i])),n=nodes.length;
  const rate=Array.from({length:n},()=>Array(n).fill(0));
  for(const l of spec.thermal.links){
    const f=ix.get(l.from),t=ix.get(l.to),g=l.conductanceKWK;
    rate[f][f]-=g/nodes[f].capacityKJK;rate[f][t]+=g/nodes[t].capacityKJK;
    rate[t][f]+=g/nodes[f].capacityKJK;rate[t][t]-=g/nodes[t].capacityKJK;
  }
  const tau=context.stageSeconds*context.stageWeight;
  for(let i=0;i<5;i++){const t=ix.get('tube-'+i);rate[t][t]-=spec.conductancesKWK[i]/nodes[t].capacityKJK;}
  const columns=nodes.map((node,k)=>Array.from({length:21},(_,row)=>{
    if(row>=10)return ((row-10===k?1:0)-tau*rate[row-10][k])/context.physicalScales[row];
    if(row%2===0)return 0;
    const cell=(row-1)/2;
    return node.id==='tube-'+cell?-tau*spec.conductancesKWK[cell]/node.capacityKJK/context.physicalScales[row]:0;
  }));
  return columns;
}
function schemaChecks(){
  // Synthetic constitutive probes deliberately exercise all three outcomes.
  const diagnostics=[],work={evaluations:0,iterations:0,linearSolves:0,diagnostics};
  const held=[];
  const evaluate=x=>{
    if(x[0]>1)throw Error('deliberate unsupported positive probe');
    const residual=[x[0]-.9];held.push(residual);
    return {residual,states:[{p:x[0],h:1,T:1,phase:x[0]<1?'Subcooled liquid':'Superheated vapor',x:null}]};
  };
  assert.throws(()=>coupledNewton(evaluate,[1],[{kind:'pressure',section:0}],{maxIterations:1,nonlinearTolerance:1e-11},work));
  const probes=diagnostics.filter(e=>e.type==='derivative');
  assert.ok(probes.some(e=>e.outcome==='probe-failed')&&probes.some(e=>e.outcome==='branch-rejected'));
  for(const p of probes){assert.equal(p.actualPerturbation,p.perturbedCoordinate-p.originalCoordinate);
    assert.equal('residual' in p,p.outcome!=='probe-failed');if(p.residual)assert.ok(!held.includes(p.residual));}
  const w={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};
  coupledNewton(x=>({residual:[x[0]-1],states:[{p:1,h:1,T:1,phase:'Superheated vapor',x:null}]}),[0],
    [{kind:'thermal-energy',capacityKJK:1}],{maxIterations:3,nonlinearTolerance:1e-11},w);
  assert.ok(w.diagnostics.some(e=>e.type==='derivative'&&e.outcome==='used'&&e.residual));
  return {passed:true,successfulAndBranchRejectedDetached:true,failedProbesHaveNoResidual:true};
}
function conservation(r){
  assert.ok(Math.abs(r.massResidualKg)<1e-8);
  for(const v of [r.refrigerantEnergyResidualKJ,r.thermalEnergyResidualKJ,r.combinedEnergyResidualKJ,...r.nodes.map(n=>n.residualKJ)])assert.ok(Math.abs(v)<1e-6);
  for(const v of r.sectionResiduals){assert.ok(Math.abs(v.massKg)<1e-8);assert.ok(Math.abs(v.energyKJ)<1e-6);}
}
function metrics(){return {probes:0,maximumRelativeNonzeroError:0,maximumThermalTemperatureDerivativeError:0,
  maximumFluidEnergyDerivativeError:0,maximumUnexpectedZero:0,maximumCoordinateStepRelativeDifference:0,worst:null};}
function compareColumns(m,e,base,context,columns,spec){
  const k=e.column-10,c=spec.thermal.nodes[k].capacityKJK;m.probes++;
  m.maximumCoordinateStepRelativeDifference=Math.max(m.maximumCoordinateStepRelativeDifference,Math.abs(e.actualPerturbation/e.step-1));
  for(let row=0;row<21;row++){
    const actual=(e.residual[row]-base.residual[row])/e.step,exact=columns[k][row],difference=actual-exact;
    if(exact!==0)m.maximumRelativeNonzeroError=Math.max(m.maximumRelativeNonzeroError,Math.abs(difference/exact));
    else m.maximumUnexpectedZero=Math.max(m.maximumUnexpectedZero,Math.abs(actual));
    const physical=difference*context.physicalScales[row]*c;
    if(row>=10){const err=Math.abs(physical/spec.thermal.nodes[row-10].capacityKJK);
      if(err>m.maximumThermalTemperatureDerivativeError){m.maximumThermalTemperatureDerivativeError=err;m.worst={column:k,row,actual,exact,step:e.step,stageSeconds:context.stageSeconds,stageWeight:context.stageWeight};}}
    else if(row%2)m.maximumFluidEnergyDerivativeError=Math.max(m.maximumFluidEnergyDerivativeError,Math.abs(physical));
  }
}
const report={schema:'Ammonia-A0-v1',baselineCommit:BASE,runtime:process.version,passed:false,
  propertyCountDefinition:'Public ph/sat/stateMVU calls through a transparent engine wrapper; engine-internal calls excluded. Comparator calls are separate.',
  cases:[],schemaChecks:schemaChecks(),diagnosticOnly:true};
function targetedReplays(){
  const saved=JSON.parse(fs.readFileSync(output,'utf8'));assert.ok(saved.passed);
  const original=originalFactory();saved.targetedReplays=[];
  for(const name of ['cold','warm','heat-reversal']){
    const c=cases().find(c=>c.name===name),settings={...accuracyOptions(1e-6),trace:true};
    const m=original(createEngine(data),settings),s=m.create(c.config);
    for(const t of c.samples.filter(t=>t<=1))m.advance(s,t-s.seconds);
    assert.equal(s.seconds,1);assert.equal(s.stop,null);
    for(const dt of [.5,.025]){
      const call=(factory,recorded)=>{
        const snapshot=JSON.parse(JSON.stringify(s)),before=hash(snapshot),work={evaluations:0,iterations:0,linearSolves:0};
        if(recorded)work.diagnostics=[];
        let result,error;try{result=factory(createEngine(data),settings).trial(snapshot,dt,work);}
        catch(cause){error={message:cause.message,faultKind:cause.faultKind||'solver',nonlinearResidual:cause.nonlinearResidual??null};}
        assert.equal(hash(snapshot),before,'Uncommitted replay must not mutate accepted state.');
        return {resultHash:result?hash(result):null,error,work:{evaluations:work.evaluations,iterations:work.iterations,linearSolves:work.linearSolves},events:work.diagnostics};
      };
      const baseline=call(original,false),originalObserved=call(original,true),plain=call(createCoupledModel,false),observed=call(createCoupledModel,true);
      for(const key of ['resultHash','error','work']){assert.deepEqual(plain[key],baseline[key]);assert.deepEqual(observed[key],baseline[key]);assert.deepEqual(originalObserved[key],baseline[key]);}
      const priorEvents=observed.events.map(e=>{
        if(e.type!=='derivative')return e;
        const {residual,originalCoordinate,perturbedCoordinate,actualPerturbation,...prior}=e;return prior;
      });
      assert.deepEqual(priorEvents,originalObserved.events,'Every replayed iteration/probe/line-search decision must match the original observer.');
      const contexts=new Map(),iterations=new Map(),columns=metrics();
      for(const e of observed.events){
        if(e.type==='iteration'){if(e.context)contexts.set(e.solveId,e.context);iterations.set(e.solveId,e);}
        if(e.type==='derivative'&&e.kind==='thermal-energy'&&e.outcome==='used'){
          const context=contexts.get(e.solveId);compareColumns(columns,e,iterations.get(e.solveId),context,exactColumns(s.spec,context),s.spec);
        }
      }
      saved.targetedReplays.push({name,startSeconds:1,trialSeconds:dt,passed:true,originalSolverDecisionHash:hash(originalObserved.events),resultHash:observed.resultHash,error:observed.error||null,
        work:observed.work,columns,spec:s.spec,events:observed.events});
    }
  }
  fs.writeFileSync(output,JSON.stringify(saved,null,2)+'\n');
  console.log(JSON.stringify({passed:true,targetedReplays:saved.targetedReplays.map(({events,spec,...rest})=>rest)}));
}
function memoryWorker(){
  const mode=process.argv[5];assert.ok(['original','observed'].includes(mode));
  const original=originalFactory(),c=cases().find(c=>c.name==='heat-reversal'),{engine,counts}=countedEngine();
  const payload={probeVectors:0,maximumProbeNumbersPerAttempt:0,maximumEventsPerAttempt:0};
  const observer=a=>{
    let numbers=0;
    for(const e of a.events)if(e.type==='derivative'&&e.residual){payload.probeVectors++;numbers+=e.residual.length;}
    payload.maximumProbeNumbersPerAttempt=Math.max(payload.maximumProbeNumbersPerAttempt,numbers);
    payload.maximumEventsPerAttempt=Math.max(payload.maximumEventsPerAttempt,a.events.length);
  };
  const m=(mode==='original'?original:createCoupledModel)(engine,{...accuracyOptions(1e-6),trace:true},mode==='original'?null:observer),s=m.create(c.config),records=[];
  for(const t of c.samples){const r=m.advance(s,t-s.seconds);assert.equal(r.stop,null);conservation(r);records.push(r);}
  console.log(JSON.stringify({mode,runtime:process.version,stateHash:hash(s),recordsHash:hash(records),counts,
    work:{evaluations:s.attemptedResidualEvaluations,iterations:s.attemptedIterations,linearSolves:s.attemptedLinearSolves},
    maximumResidentSetKiB:process.resourceUsage().maxRSS,payload,
    qualification:'Fresh-process paired RSS observation; minimal observer excludes comparator/serialization IO. Not a universal memory bound or timing benchmark.'}));
}
function memoryComparison(){
  const saved=JSON.parse(fs.readFileSync(output,'utf8'));assert.ok(saved.passed);
  const run=mode=>JSON.parse(execFileSync(process.execPath,[__filename,output,archive,'--memory-worker',mode],{encoding:'utf8',maxBuffer:1024*1024}));
  const original=run('original'),observed=run('observed');
  for(const key of ['runtime','stateHash','recordsHash','counts','work'])assert.deepEqual(original[key],observed[key]);
  const nominal=saved.cases.find(c=>c.name==='heat-reversal'&&c.tolerance===1e-6);
  assert.equal(original.stateHash,nominal.observationalEquivalence.stateHash);assert.deepEqual(original.work,nominal.work);
  saved.memoryComparison={passed:true,original,observed,differenceKiB:observed.maximumResidentSetKiB-original.maximumResidentSetKiB};
  fs.writeFileSync(output,JSON.stringify(saved,null,2)+'\n');console.log(JSON.stringify(saved.memoryComparison));
}
if(process.argv[4]==='--memory-worker')memoryWorker();
else if(process.argv[4]==='--memory')memoryComparison();
else if(process.argv[4]==='--replay')targetedReplays();else try{
  const original=originalFactory();
  for(const c of cases())for(const tolerance of c.name==='heat-reversal'?[1e-6,1e-7,1e-8]:[1e-6]){
    console.error('A0 '+c.name+' '+tolerance);
    let observedState,observedModel;
    const stats={attempts:[],failedSolves:0,failedColumns:metrics(),successfulColumns:metrics(),columns:Array.from({length:11},metrics),
      maximumConvergedThermalClosureK:0,maximumFailedThermalClosureK:0,probeOutcomes:{},
      quantization:{points:0,maximumTemperatureDifferenceK:0,maximumEndpointThermalShiftK:0,maximumEndpointFluidEnergyShiftKJ:0,
        failedFinalPoints:0,failedFinalShiftExceedsBudget:0,failedFinalMovesWithinBudget:0,failedFinalMovesFurtherOutside:0,worst:null},
      storage:{totalEvents:0,totalSuccessfulProbeResidualNumbers:0,maximumEventsPerAttempt:0,maximumSerializedAttemptBytes:0,selectedAttempts:0},selection:{}};
    const observer=a=>{
      const spec=observedState.spec,failed=new Set(a.events.filter(e=>e.type==='solve-failed').map(e=>e.solveId));
      stats.failedSolves+=failed.size;
      stats.attempts.push({startSeconds:a.startSeconds,trialSeconds:a.trialSeconds,failure:a.failure?.kind||null,rejectionReason:a.rejectionReason,
        evaluations:a.evaluations,iterations:a.iterations,linearSolves:a.linearSolves});
      const iterations=new Map(),contexts=new Map(),cache=new Map(),quantRows=[];
      for(const e of a.events){
        if(e.type==='iteration'){
          if(e.context)contexts.set(e.solveId,e.context);
          const context=contexts.get(e.solveId);iterations.set(e.solveId,e);
          const closure=Math.max(...e.residual.slice(10).map((v,i)=>Math.abs(v)*context.physicalScales[10+i]/context.thermalCapacitiesKJK[i]));
          if(e.status==='converged'){assert.ok(closure<=1e-12);assert.ok(e.fluidNorm<=1e-11);stats.maximumConvergedThermalClosureK=Math.max(stats.maximumConvergedThermalClosureK,closure);}
          if(failed.has(e.solveId)&&e.iteration===30)stats.maximumFailedThermalClosureK=Math.max(stats.maximumFailedThermalClosureK,closure);
          for(let cell=0;cell<5;cell++){
            const ph=e.states[cell],key=ph.p+':'+ph.h;
            if(!cache.has(key))cache.set(key,exactTemperature(ph.p,ph.h));
            const exactT=cache.get(key),deltaT=exactT-ph.T,tube=spec.thermal.nodes.findIndex(n=>n.id==='tube-'+cell),
              exchangeShiftKJ=context.stageSeconds*context.stageWeight*spec.conductancesKWK[cell]*deltaT,
              thermalShiftK=-exchangeShiftKJ/spec.thermal.nodes[tube].capacityKJK,
              currentK=e.residual[10+tube]*context.physicalScales[10+tube]/spec.thermal.nodes[tube].capacityKJK;
            const q=stats.quantization;q.points++;
            q.maximumTemperatureDifferenceK=Math.max(q.maximumTemperatureDifferenceK,Math.abs(deltaT));
            q.maximumEndpointFluidEnergyShiftKJ=Math.max(q.maximumEndpointFluidEnergyShiftKJ,Math.abs(exchangeShiftKJ));
            if(Math.abs(thermalShiftK)>q.maximumEndpointThermalShiftK){q.maximumEndpointThermalShiftK=Math.abs(thermalShiftK);q.worst={startSeconds:a.startSeconds,trialSeconds:a.trialSeconds,stageSeconds:context.stageSeconds,stageWeight:context.stageWeight,cell,p:ph.p,h:ph.h,T:ph.T,exactT,thermalShiftK,currentK};}
            if(failed.has(e.solveId)&&e.iteration===30){q.failedFinalPoints++;if(Math.abs(thermalShiftK)>1e-12)q.failedFinalShiftExceedsBudget++;
              if(Math.abs(currentK)>1e-12&&Math.abs(currentK+thermalShiftK)<=1e-12)q.failedFinalMovesWithinBudget++;
              if(Math.abs(currentK+thermalShiftK)>Math.abs(currentK))q.failedFinalMovesFurtherOutside++;}
            quantRows.push({solveId:e.solveId,iteration:e.iteration,cell,p:ph.p,h:ph.h,T:ph.T,exactT,thermalShiftK,exchangeShiftKJ,currentK});
          }
        }else if(e.type==='derivative'){
          stats.probeOutcomes[e.outcome]=(stats.probeOutcomes[e.outcome]||0)+1;
          assert.equal(e.actualPerturbation,e.perturbedCoordinate-e.originalCoordinate);
          assert.equal('residual' in e,e.outcome!=='probe-failed');
          if(e.residual)stats.storage.totalSuccessfulProbeResidualNumbers+=e.residual.length;
          if(e.kind==='thermal-energy'&&e.outcome==='used'){
            const base=iterations.get(e.solveId),context=contexts.get(e.solveId),columns=exactColumns(spec,context);
            compareColumns(failed.has(e.solveId)?stats.failedColumns:stats.successfulColumns,e,base,context,columns,spec);
            compareColumns(stats.columns[e.column-10],e,base,context,columns,spec);
          }
        }
      }
      stats.storage.totalEvents+=a.events.length;stats.storage.maximumEventsPerAttempt=Math.max(stats.storage.maximumEventsPerAttempt,a.events.length);
      // Storage is observational overhead; no normal-operation timing claims.
      const bytes=Buffer.byteLength(JSON.stringify(a));stats.storage.maximumSerializedAttemptBytes=Math.max(stats.storage.maximumSerializedAttemptBytes,bytes);
      const bucket=a.failure?(a.startSeconds>=30?'late-failed':'early-failed'):(a.startSeconds>=30?'late-success':'early-success');
      if(!stats.selection[bucket]){stats.selection[bucket]=true;stats.storage.selectedAttempts++;
        fs.appendFileSync(archive,zlib.gzipSync(JSON.stringify({case:c.name,tolerance,bucket,spec,attempt:a,quantRows})+'\n'));}
      // Exercise detachment: deliberate consumer mutation after analysis.
      for(const e of a.events)if(e.type==='derivative'&&e.residual)e.residual.fill(12345);
    };
    function run(factory,observe){
      const {engine,counts}=countedEngine(),model=factory(engine,{...accuracyOptions(tolerance),trace:true},observe),s=model.create(c.config);
      if(observe){observedState=s;observedModel=model;}
      const records=[];
      for(const t of c.samples){const r=model.advance(s,t-s.seconds);assert.equal(r.stop,null);conservation(r);records.push(r);}
      return {stateHash:hash(s),recordsHash:hash(records),counts,work:{evaluations:s.attemptedResidualEvaluations,iterations:s.attemptedIterations,linearSolves:s.attemptedLinearSolves},
        accepted:s.trace.length,rejected:s.rejectedSteps,trace:s.trace,rejectionTrace:s.rejectionTrace,records};
    }
    const baseline=run(original,null),plain=run(createCoupledModel,null),observed=run(createCoupledModel,observer);
    // Includes every state field, ledger/event/stop/boundary and adaptive trace.
    for(const key of ['stateHash','recordsHash','counts','work','accepted','rejected'])assert.deepEqual(observed[key],baseline[key],key+' observational equivalence');
    for(const key of ['stateHash','recordsHash','counts','work','accepted','rejected'])assert.deepEqual(plain[key],baseline[key],key+' unobserved extension equivalence');
    const regrowth={solverFailures:0,nextAttemptHalved:0,sameStateRepeatedFailures:0,successfulRetryFollowedByGrowth:0,grownProposalFailed:0};
    const attempts=stats.attempts;
    for(let i=0;i<attempts.length;i++){
      const a=attempts[i],next=attempts[i+1];
      if(a.failure==='solver'){regrowth.solverFailures++;if(next&&next.startSeconds===a.startSeconds&&next.trialSeconds===a.trialSeconds/2)regrowth.nextAttemptHalved++;
        if(next?.failure==='solver'&&next.startSeconds===a.startSeconds)regrowth.sameStateRepeatedFailures++;}
      const previous=attempts[i-1];
      if(!a.failure&&!a.rejectionReason&&previous?.failure==='solver'&&previous.startSeconds===a.startSeconds&&next&&next.startSeconds>a.startSeconds&&next.trialSeconds>a.trialSeconds){
        regrowth.successfulRetryFollowedByGrowth++;if(next.failure==='solver')regrowth.grownProposalFailed++;}
    }
    report.cases.push({name:c.name,tolerance,settings:observedModel.settings,intervalSeconds:c.samples.at(-1),
      observationalEquivalence:{passed:true,stateHash:observed.stateHash,recordsHash:observed.recordsHash,mutatedDetachedProbeCopies:true},
      counts:observed.counts,work:observed.work,acceptedTrials:observed.accepted,rejectedTrials:observed.rejected,
      records:observed.records,stats,regrowth});
    fs.writeFileSync(output+'.partial.json',JSON.stringify(report,null,2)+'\n');
  }
  report.archive={path:path.basename(archive),bytes:fs.statSync(archive).size,sha256:hash(fs.readFileSync(archive)),
    format:'Concatenated gzip JSONL; selected evaluated trials, not complete histories'};
  report.preservedHistory={path:'COUPLED_R_FAILED_NEWTON.jsonl.gz',sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'COUPLED_R_FAILED_NEWTON.jsonl.gz'))).digest('hex')};
  assert.equal(report.preservedHistory.sha256,'c1ca2203fcf6026d2da70d5331c1bb5ac49ffe74a29997ce2cf8bdbcfe3a30fc');
  report.passed=true;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({passed:true,cases:report.cases.map(c=>({name:c.name,tolerance:c.tolerance,accepted:c.acceptedTrials,rejected:c.rejectedTrials,regrowth:c.regrowth,failedColumns:c.stats.failedColumns,quantization:c.stats.quantization,storage:c.stats.storage})),archive:report.archive}));
}catch(error){report.failure={message:error.message,stack:error.stack};fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(error);process.exitCode=1;}
