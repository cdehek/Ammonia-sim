'use strict';
// A2 qualification adapters leave all established suites/fixtures/references intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const Module=require('node:module'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const {createCoupledModel,exactThermalColumns,createGrowthHistory,resetGrowth,noteNonlinearFailure,recoveredGrowth}=require('./coupled-model.cjs');
const {fixture,cases,accuracyOptions}=require('./coupled-fixtures.cjs');
const {createEngine}=require('../../engine'),data=require('../../properties.json');
const BASE='c2de1f0808048f6be6f3e912cd0fcffa9a646cf0',root=fs.realpathSync(path.resolve(__dirname,'../..'));
const [mode,output,...args]=process.argv.slice(2);
assert.match(process.version,/^v22\./,'Qualify with Node 22.');
assert.ok(output,'Usage: roadmap-a2.cjs MODE /tmp/output.json [arguments]');
for(const file of [output,output+'.failure.json']){
  const resolved=fs.existsSync(file)?fs.realpathSync(file):path.join(fs.realpathSync(path.dirname(path.resolve(file))),path.basename(file));
  assert.ok(resolved!==root&&!resolved.startsWith(root+path.sep),'Evidence must be outside the repository.');
}
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
function compiled(file,source,overrides={}){
  const filename=path.join(__dirname,file),m=new Module(filename,module);m.filename=filename;m.paths=module.paths;
  const ordinary=m.require.bind(m);m.require=id=>Object.hasOwn(overrides,id)?overrides[id]:ordinary(id);
  m._compile(source,filename);return m.exports;
}
function original(){
  const source=file=>execFileSync('git',['show',BASE+':experiments/dx-fv/'+file],{encoding:'utf8',cwd:root});
  return compiled('coupled-model.cjs',source('coupled-model.cjs'),{'./coupled-implicit.cjs':compiled('coupled-implicit.cjs',source('coupled-implicit.cjs'))}).createCoupledModel;
}
function counted(){
  const engine=createEngine(data),counts={ph:0,sat:0,stateMVU:0},wrapped={...engine};
  for(const key of Object.keys(counts))wrapped[key]=(...a)=>{counts[key]++;return engine[key](...a);};
  return {engine:wrapped,counts}; // Actual public invocations; internal nested calls are not included.
}
function check(r){
  assert.equal(r.stop,null,JSON.stringify(r.stop));
  for(const v of [r.massResidualKg,...r.sectionResiduals.map(v=>v.massKg)])assert.ok(Math.abs(v)<1e-8);
  for(const v of [r.refrigerantEnergyResidualKJ,r.thermalEnergyResidualKJ,r.combinedEnergyResidualKJ,...r.nodes.map(v=>v.residualKJ),...r.sectionResiduals.map(v=>v.energyKJ)])assert.ok(Math.abs(v)<1e-6);
  assert.ok(r.sections.every(v=>v.massKg>0&&Math.abs(v.energyResidual)<1e-7&&Math.abs(v.densityResidual)<1e-7));
  assert.ok(r.nodes.every(v=>v.temperatureK>=200&&v.temperatureK<=400));
  if(r.lastTimeError!==null)assert.ok(r.lastTimeError<=1);
}
function run(c,choice,options={},factory=createCoupledModel,observer=null){
  // End-to-end simulation workload includes engine/factory/state creation and
  // all scheduled output/conservation checks. Hashing and evidence I/O follow.
  const start=performance.now();
  const {engine,counts}=counted(),m=factory(engine,{...options,...selection(choice)},observer);
  const s=m.create(c.config),initial=m.record(s),rows=[];
  for(const t of c.samples){const r=m.advance(s,t-s.seconds);check(r);assert.equal(r.seconds,t);rows.push(r);}
  const elapsedMS=performance.now()-start;
  return {state:s,initial,rows,counts:{...counts},elapsedMS,work:{acceptedTrials:s.acceptedSteps/2,rejectedTrials:s.rejectedSteps,
    failures:s.rejectedSteps-s.accuracyRejectedSteps-s.eventRejectedSteps-s.domainRejectedSteps,
    accuracyRejected:s.accuracyRejectedSteps,eventRejected:s.eventRejectedSteps,domainRejected:s.domainRejectedSteps,
    iterations:s.attemptedIterations,evaluations:s.attemptedResidualEvaluations,linearSolves:s.attemptedLinearSolves}};
}
function summary(r){return {work:r.work,propertyCalls:r.counts,elapsedMS:r.elapsedMS,stateHash:hash(r.state),recordHash:hash(r.rows)};}
function compare(a,b){
  const maximum={pressureBar:0,enthalpyKJkg:0,fluidTemperatureK:0,thermalTemperatureK:0,massKg:0,fluidEnergyKJ:0,linkIntegralKJ:0,eventSeconds:0};
  for(let j=0;j<a.rows.length;j++){
    const r=a.rows[j],w=b.rows[j];assert.equal(r.seconds,w.seconds);
    r.sections.forEach((v,i)=>{for(const [key,field]of [['pressureBar','p'],['enthalpyKJkg','h'],['fluidTemperatureK','T'],['massKg','massKg'],['fluidEnergyKJ','internalEnergyKJ']])maximum[key]=Math.max(maximum[key],Math.abs(v[field]-w.sections[i][field]));});
    r.nodes.forEach((v,i)=>{maximum.thermalTemperatureK=Math.max(maximum.thermalTemperatureK,Math.abs(v.temperatureK-w.nodes[i].temperatureK));});
    r.ledger.tubeRefrigerantKJ.forEach((v,i)=>{maximum.linkIntegralKJ=Math.max(maximum.linkIntegralKJ,Math.abs(v-w.ledger.tubeRefrigerantKJ[i]));});
  }
  const ae=a.state.events,be=b.state.events;assert.equal(ae.length,be.length);
  ae.forEach((v,i)=>{const w=be[i];for(const key of ['section','boundary','direction'])assert.equal(v[key],w[key]);maximum.eventSeconds=Math.max(maximum.eventSeconds,Math.abs(v.seconds-w.seconds));});
  assert.deepEqual(a.state.boundaryEvents,b.state.boundaryEvents);
  assert.ok(maximum.pressureBar<5e-5&&maximum.enthalpyKJkg<.05&&maximum.fluidTemperatureK<.01&&maximum.thermalTemperatureK<.01&&maximum.eventSeconds<.001,JSON.stringify(maximum));
  return maximum;
}
const choices=['baseline','exact','fd-aware','exact-aware'];
function selection(choice){
  assert.ok(choices.includes(choice));
  return {...(choice.startsWith('exact')?{thermalJacobian:'exact'}:{}),
    ...(choice.endsWith('aware')?{timestepGrowth:'failure-aware'}:{})};
}
const report={stage:'A2',startingCommit:BASE,runtime:process.version,mode};
function write(){fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,mode,output}));}
function phaseReplay(choice,seeded=false,observe=false,factory=createCoupledModel){
  const {engine,counts}=counted(),attempts=[];let s;
  const physical=state=>({cells:state.cells,energies:state.energies,ledger:state.ledger,seconds:state.seconds,
    events:state.events,boundaryEvents:state.boundaryEvents,scheduleIndex:state.scheduleIndex,spec:state.spec,acceptedSteps:state.acceptedSteps});
  const m=factory(engine,{...selection(choice),trace:true},observe?attempt=>{
    const failed=attempt.events.filter(e=>e.type==='solve-failed');
    for(const e of attempt.events)if(e.type==='iteration'&&e.status==='converged')assert.ok(e.fluidNorm<=1e-11&&e.thermalNorm*.1<=1e-12);
    attempts.push({seconds:attempt.startSeconds,dt:attempt.trialSeconds,failure:attempt.failure,reason:attempt.rejectionReason,
      error:attempt.temporalError,work:{evaluations:attempt.evaluations,iterations:attempt.iterations,linearSolves:attempt.linearSolves},
      failedSolves:failed,acceptedSnapshot:JSON.parse(JSON.stringify(physical(s))),history:s.growthHistory?JSON.parse(JSON.stringify(s.growthHistory)):null,
      nextStepSeconds:s.nextStepSeconds});
  }:null);
  s=m.create(fixture('warm'));const initial=m.record(s);
  if(seeded){noteNonlinearFailure(s.growthHistory,.5);recoveredGrowth(s.growthHistory,.25,.5,.5);}
  const initialHistory=s.growthHistory?JSON.parse(JSON.stringify(s.growthHistory)):null;
  const rows=[m.advance(s,2)];check(rows[0]);assert.ok(s.events.length>0);
  for(let i=0;i<attempts.length-1;i++){
    const a=attempts[i],next=attempts[i+1];
    if(a.failure||a.reason){assert.deepEqual(next.acceptedSnapshot,a.acceptedSnapshot);assert.equal(next.seconds,a.seconds);}
    if(a.failure){assert.equal(next.dt,a.dt/2);assert.equal(a.failure.kind,'solver');assert.ok(a.failedSolves.length>0);}
  }
  return {choice,seeded,initialHistory,initial,rows,state:s,propertyCalls:counts,attempts};
}
async function main(){
  if(mode==='suite'){
    const [choice,name]=args,selected=selection(choice);
    assert.ok(['coupled-test','coupled-controls','coupled-browser','coupled-domain-test'].includes(name));
    assert.ok(name!=='coupled-domain-test'||!choice.endsWith('aware'),'Experimental domain checks use domain mode.');
    process.argv=[process.argv[0],path.join(__dirname,name+'.cjs'),output];
    let source=fs.readFileSync(path.join(__dirname,name+'.cjs'),'utf8');
    if(name==='coupled-browser'){
      assert.equal(source.split('m=create(engine),').length,2);
      source=source.replace('m=create(engine),',`m=create(engine,${JSON.stringify(selected)}),`);
    }
    compiled(name+'.cjs',source,{'./coupled-model.cjs':{createCoupledModel:(engine,options={},observer=null)=>createCoupledModel(engine,{...options,...selected},observer)}});return;
  }
  if(mode==='domain'){
    const selected=selection(args[0]);assert.ok(args[0].endsWith('aware'));
    let source=fs.readFileSync(path.join(__dirname,'roadmap-a1.cjs'),'utf8');
    // Reuse all 36 qualified A1 classification/rollback cases, selecting A2 even
    // in the in-memory injected factories. No established source is edited.
    source=source.replaceAll("thermalJacobian:'exact'",Object.entries(selected).map(([k,v])=>`${k}:${JSON.stringify(v)}`).join(','));
    source=source.replace("stage:'A1'","stage:'A2'");
    process.argv=[process.argv[0],path.join(__dirname,'roadmap-a1.cjs'),'domain',output];
    compiled('roadmap-a1.cjs',source);return;
  }
  if(mode==='phase-diagnosis'){
    report.runs=[];
    for(const choice of ['fd-aware','exact-aware'])for(const seeded of [false,true]){
      const a=phaseReplay(choice,seeded,true),b=phaseReplay(choice,seeded,true),plain=phaseReplay(choice,seeded,false);
      assert.deepEqual(a,b);assert.deepEqual(a.state,plain.state);assert.deepEqual(a.rows,plain.rows);assert.deepEqual(a.propertyCalls,plain.propertyCalls);
      // Replay each failed interval at its accepted state independently. No
      // accepted-path residual or property evaluation is substituted.
      const m=createCoupledModel(createEngine(data),selection(choice));
      for(const trial of a.attempts.filter(a=>a.failure)){
        const snapshot=JSON.stringify(trial.acceptedSnapshot),work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};let failure;
        try{m.trial(trial.acceptedSnapshot,trial.dt,work);}catch(e){failure={kind:e.faultKind||'solver',message:e.message};}
        assert.deepEqual(failure,trial.failure);assert.equal(JSON.stringify(trial.acceptedSnapshot),snapshot);
        trial.independentTrialFailure=failure;
      }
      report.runs.push(a);console.error('Phase replay '+choice+' seeded='+seeded+' actual failures='+a.attempts.filter(a=>a.failure).length+' counter='+a.state.growthHistory.nonlinearFailures);
    }
    const old=original();for(const choice of ['baseline','exact']){
      const a=phaseReplay(choice,false,true,old),b=phaseReplay(choice,false,true);
      assert.deepEqual(a,b);report.runs.push(a);
    }
    report.algorithmSHA256=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'coupled-model.cjs'))).digest('hex');
    report.passed=true;
  }else if(mode==='rules'){
    const h=createGrowthHistory();assert.equal(recoveredGrowth(h,.1,.2,.5),.2);
    noteNonlinearFailure(h,.2);assert.equal(recoveredGrowth(h,.1,.2,.5),.1);
    for(let i=0;i<3;i++)assert.equal(recoveredGrowth(h,.1,.2,.5),.1);
    assert.equal(recoveredGrowth(h,.1,.2,.5),.125);
    const streak=h.successes;recoveredGrowth(h,.001,.002,.5);assert.equal(h.successes,streak);
    let steps=0;while(h.ceilingSeconds!==null&&steps++<100){const dt=h.ceilingSeconds;recoveredGrowth(h,dt,Math.min(.5,2*dt),.5);}
    assert.equal(h.ceilingSeconds,null);assert.ok(steps<100);
    for(const reason of ['manual-boundary','scheduled-boundary','phase-event','event-refinement','domain-rejection','other-failure']){
      noteNonlinearFailure(h,.2);recoveredGrowth(h,.1,.2,.5);resetGrowth(h,reason);
      assert.equal(h.ceilingSeconds,null);assert.equal(h.pendingFailure,false);assert.equal(h.lastFailedSeconds,null);
    }
    const engine=createEngine(data);
    assert.throws(()=>createCoupledModel(engine,{timestepGrowth:'other'}));
    assert.equal(Object.hasOwn(createCoupledModel(engine).settings,'timestepGrowth'),false);
    assert.equal(Object.hasOwn(createCoupledModel(engine,{timestepGrowth:'failure-aware'}).settings,'thermalJacobian'),false);
    // Boundaries clear memory only after the entire patch validates.
    for(const choice of choices.filter(c=>c.endsWith('aware'))){
      const m=createCoupledModel(engine,selection(choice)),s=m.create(fixture());
      noteNonlinearFailure(s.growthHistory,.2);recoveredGrowth(s.growthHistory,.1,.2,.5);
      const before=JSON.stringify(s);assert.throws(()=>m.update(s,{airLoadKW:2,inlet:{p:100,h:500}}));assert.equal(JSON.stringify(s),before);
      m.update(s,{airLoadKW:2});assert.equal(s.growthHistory.ceilingSeconds,null);
      const fixed=createCoupledModel(engine,{...selection(choice),adaptive:false});assert.equal(Object.hasOwn(fixed.create(fixture()),'growthHistory'),false);
      const scheduled=m.create(fixture('cold',{refrigerantConductanceKWK:0,sealed:true,schedule:[{seconds:.001,patch:{airLoadKW:0}}]}));
      noteNonlinearFailure(scheduled.growthHistory,.002);recoveredGrowth(scheduled.growthHistory,.001,.002,.5);
      check(m.advance(scheduled,.001));assert.equal(scheduled.growthHistory.ceilingSeconds,null);
      assert.equal(scheduled.growthHistory.resets['scheduled-boundary'],1);
      const phase=phaseReplay(choice,true,true);
      const actualFailures=phase.attempts.filter(a=>a.failure);
      // A manually seeded history entry is not a Newton evaluation. Additional
      // real failures are counted and examined, never suppressed or fixed-count.
      assert.equal(phase.state.growthHistory.nonlinearFailures,phase.initialHistory.nonlinearFailures+actualFailures.length);
      assert.equal(phase.state.domainRejectedSteps,0);
      assert.ok(phase.state.growthHistory.resets['phase-event']>0);
      let cleared=0;
      for(let i=1;i<phase.attempts.length;i++){
        const before=phase.attempts[i-1],after=phase.attempts[i];
        if(after.acceptedSnapshot.events.length>before.acceptedSnapshot.events.length){
          assert.equal(before.failure,null);assert.equal(before.reason,null);
          assert.equal(after.history.ceilingSeconds,null);assert.equal(after.history.lastRecoverySeconds,null);
          if(!after.failure){assert.equal(after.history.pendingFailure,false);assert.equal(after.history.lastFailedSeconds,null);}
          const factor=before.error===0?2:Math.max(.1,Math.min(2,.85*before.error**(-1/3)));
          const proposed=Math.min(.5,before.dt*factor);
          assert.equal(after.nextStepSeconds,proposed);assert.equal(after.dt,Math.min(proposed,2-after.seconds));cleared++;
        }
      }
      assert.ok(cleared>0,'Observe cleared history and unrestricted original proposals after phase events.');
      const originalPhase=phaseReplay(choice==='fd-aware'?'baseline':'exact');
      const differences=compare(originalPhase,phase);
      assert.ok(phase.state.events.every(e=>e.bracketEndSeconds-e.bracketStartSeconds<=m.settings.eventStepSeconds+1e-12));
      report.phaseChecks??=[];report.phaseChecks.push({choice,seededHistoryEntries:phase.initialHistory.nonlinearFailures,
        actualNonlinearFailures:actualFailures.length,observedPostEventResets:cleared,differences});
      const accuracy=m.create(fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0}}));
      check(m.advance(accuracy,.5));assert.ok(accuracy.accuracyRejectedSteps>0);
      assert.equal(accuracy.growthHistory.nonlinearFailures,0);assert.equal(accuracy.growthHistory.ceilingSeconds,null);
    }
    report.history=h;report.passed=true;
  }else if(mode==='baseline'){
    const old=original();report.cases=[];
    for(const c of cases())for(const t of (c.name==='heat-reversal'?[1e-6,1e-7,1e-8]:[1e-6]))for(const choice of ['baseline','exact']){
      const options={...accuracyOptions(t),trace:true},a=run(c,choice,options,old),b=run(c,choice,options);
      assert.deepEqual(b.state,a.state);assert.deepEqual(b.rows,a.rows);assert.deepEqual(b.counts,a.counts);assert.deepEqual(b.work,a.work);
      const explicit=run(c,choice,{...options,timestepGrowth:'original'});
      explicit.rows.forEach(r=>delete r.settings.timestepGrowth);
      assert.deepEqual(explicit.rows,b.rows);assert.deepEqual(explicit.state,b.state);assert.deepEqual(explicit.counts,b.counts);
      report.cases.push({name:c.name,relativeTolerance:t,choice,...summary(b)});console.error('A1 identical: '+c.name+' '+t+' '+choice);
    }report.passed=true;
  }else if(mode==='methods'){
    // Deferred exploratory nominal adaptive-BE scenario. This known baseline
    // failure is retained for reproduction and is not an A2 acceptance gate.
    console.error('EXPLORATORY: broader adaptive BE; known baseline accuracy failure, outside required qualification.');
    report.cases=[];
    const reference=JSON.parse(fs.readFileSync(path.join(__dirname,'coupled-reference.json'),'utf8'));
    for(const c of cases().filter(c=>['cold','warm','heat-reversal'].includes(c.name))){
      const runs={};
      for(const choice of choices){
        const r=run({...c,samples:c.samples.filter(t=>t<=1)},choice,{...accuracyOptions(),method:'backward-euler',trace:true});
        const direct=reference.cases.find(v=>v.name===c.name).runs[1];
        for(const row of r.rows){
          const ref=direct.samples.find(v=>v.seconds===row.seconds);assert.ok(ref);
          row.sections.forEach((v,i)=>{assert.ok(Math.abs(v.p-ref.sections[i].p)<1e-4&&Math.abs(v.h-ref.sections[i].h)<.05&&Math.abs(v.T-ref.sections[i].T)<.01);});
          row.nodes.forEach((v,i)=>assert.ok(Math.abs(v.temperatureK-ref.temperaturesK[i])<.01));
        }
        runs[choice]={...summary(r),state:r.state,initial:r.initial,rows:r.rows};
      }
      for(const choice of choices.slice(1))compare(runs.baseline,runs[choice]);
      report.cases.push({name:c.name,relativeTolerance:1e-6,runs});console.error('Adaptive backward-Euler controls: '+c.name);
    }report.passed=true;
  }else if(mode==='compare'||mode==='smoke'){
    report.cases=[];
    for(const c of (mode==='smoke'?cases().filter(c=>c.name==='heat-reversal'):cases()))for(const t of (mode==='smoke'?[1e-6]:[1e-6,1e-7,1e-8])){
      const runs={},options={...accuracyOptions(t),trace:true};
      for(const choice of choices){
        const r=run(c,choice,options);runs[choice]={...summary(r),state:r.state,initial:r.initial,rows:r.rows};
        console.error('Compared '+c.name+' '+t+' '+choice+': '+JSON.stringify(r.work));
      }
      const differences={};for(const choice of choices.slice(1))differences[choice]=compare(runs.baseline,runs[choice]);
      report.cases.push({name:c.name,relativeTolerance:t,runs,differences});
    }report.passed=true;
  }else if(mode==='observed'){
    report.cases=[];
    const c=cases().find(c=>c.name==='heat-reversal');
    for(const choice of ['fd-aware','exact-aware']){
      const observed={attempts:[],converged:0,maxFluid:0,maxThermalK:0,failedSolves:0,failures:[]};
      const options={...accuracyOptions(),trace:true},a=run(c,choice,options),b=run(c,choice,options,createCoupledModel,attempt=>{
        observed.attempts.push({seconds:attempt.startSeconds,dt:attempt.trialSeconds,failure:attempt.failure,reason:attempt.rejectionReason,
          evaluations:attempt.evaluations,iterations:attempt.iterations,linearSolves:attempt.linearSolves});
        for(const e of attempt.events){
          if(e.type==='iteration'&&e.status==='converged'){
            observed.converged++;observed.maxFluid=Math.max(observed.maxFluid,e.fluidNorm);observed.maxThermalK=Math.max(observed.maxThermalK,e.thermalNorm*.1);
            assert.ok(e.fluidNorm<=1e-11&&e.thermalNorm*.1<=1e-12);
          }
          if(e.type==='solve-failed'){
            observed.failedSolves++;observed.failures.push({seconds:attempt.startSeconds,dt:attempt.trialSeconds,
              kind:e.faultKind,message:e.message,iteration:e.lastIteration?.iteration,
              fluidNorm:e.lastIteration?.fluidNorm,thermalK:e.lastIteration?.thermalNorm*.1,
              dominantIndex:e.lastIteration?.dominantIndex,phases:e.lastIteration?.states.map(v=>v.phase),
              stageSeconds:e.context?.stageSeconds,stageWeight:e.context?.stageWeight});
          }
          // Confirm observer vectors cannot mutate solver data.
          if(e.residual)e.residual.fill(12345);if(e.values)e.values.fill(12345);
        }
      });
      assert.deepEqual(a.state,b.state);assert.deepEqual(a.rows,b.rows);assert.deepEqual(a.counts,b.counts);assert.deepEqual(a.work,b.work);
      report.cases.push({choice,...summary(b),observed});
    }report.passed=true;
  }else if(mode==='performance'){
    const pairs=Number(args[0]||5);assert.ok(Number.isInteger(pairs)&&pairs>=5);
    const workload=choice=>cases().map(c=>({name:c.name,...summary(run(c,choice,accuracyOptions()))}));
    for(const choice of choices){workload(choice);console.error('Warm-up complete '+choice);}report.warmups=1;report.pairs=[];
    for(let pair=0;pair<pairs;pair++){
      // Balanced four-path orders: each path occupies every position in four
      // blocks, with all ordered adjacent pairs covered once. Repeat for block 5.
      const orders=[[0,1,3,2],[1,2,0,3],[2,3,1,0],[3,0,2,1]];
      const order=orders[pair%4].map(i=>choices[i]),runs={};
      for(const choice of order){runs[choice]=workload(choice);console.error('Measured block '+(pair+1)+' '+choice+' complete');}
      report.pairs.push({pair,order,runs});console.error('Measured four-path block '+(pair+1)+'/'+pairs);
    }
    report.hardware={platform:process.platform,arch:process.arch,kernel:require('node:os').release(),cpu:require('node:os').cpus()[0].model,
      cgroupCpuMax:fs.readFileSync('/sys/fs/cgroup/cpu.max','utf8').trim()};report.passed=true;
  }else throw Error('Unknown mode '+mode);
  write();
}
main().catch(e=>{report.passed=false;report.failure={message:e.message,stack:e.stack};fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(e);process.exitCode=1;});
