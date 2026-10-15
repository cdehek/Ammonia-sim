'use strict';
// A1 qualification adapters leave all established suites/fixtures/references intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const Module=require('node:module'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const {createCoupledModel,exactThermalColumns}=require('./coupled-model.cjs');
const {fixture,cases,accuracyOptions}=require('./coupled-fixtures.cjs');
const {createEngine}=require('../../engine'),data=require('../../properties.json');
const BASE='31f641dfb81722dfb3b7cfdb8be14856fe70052e',root=fs.realpathSync(path.resolve(__dirname,'../..'));
const [mode,output,...args]=process.argv.slice(2);
assert.match(process.version,/^v22\./,'Qualify with Node 22.');
assert.ok(output,'Usage: roadmap-a1.cjs MODE /tmp/output.json [arguments]');
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
  const {engine,counts}=counted(),m=factory(engine,{...options,...(choice==='exact'?{thermalJacobian:'exact'}:{})},observer);
  const start=performance.now(),s=m.create(c.config),initial=m.record(s),rows=[];
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
const report={stage:'A1',startingCommit:BASE,runtime:process.version,mode};
async function main(){
  if(mode==='suite'){
    const [choice,name]=args;assert.ok(['baseline','exact'].includes(choice));assert.ok(['coupled-test','coupled-controls','coupled-domain-test','coupled-browser'].includes(name));
    process.argv=[process.argv[0],path.join(__dirname,name+'.cjs'),output];
    let source=fs.readFileSync(path.join(__dirname,name+'.cjs'),'utf8');
    // The existing browser suite executes source inside browsers, outside Node require.
    if(choice==='exact'&&name==='coupled-browser'){
      assert.equal(source.split('m=create(engine),').length,2,'Browser adapter must select the exact path once.');
      source=source.replace('m=create(engine),','m=create(engine,{thermalJacobian:"exact"}),');
    }
    assert.ok(choice!=='exact'||name!=='coupled-domain-test','Use the A1 domain mode; legacy domain suite requires historical bitwise equality.');
    const overrides=choice==='exact'?{'./coupled-model.cjs':{createCoupledModel:(engine,options={},observe=null)=>createCoupledModel(engine,{...options,thermalJacobian:'exact'},observe)}}:{};
    compiled(name+'.cjs',source,overrides);return;
  }
  if(mode==='baseline'){
    const originalFactory=original();report.cases=[];
    const workloads=cases().flatMap(c=>c.name==='heat-reversal'?[1e-6,1e-7,1e-8].map(t=>[c,t]):[[c,1e-6]]);
    for(const [c,t]of workloads){
      const options={...accuracyOptions(t),trace:true},a=run(c,'baseline',options,originalFactory),b=run(c,'baseline',options);
      assert.deepEqual(b.state,a.state);assert.deepEqual(b.rows,a.rows);assert.deepEqual(b.counts,a.counts);assert.deepEqual(b.work,a.work);
      report.cases.push({name:c.name,relativeTolerance:t,...summary(b)});console.error('Default identical: '+c.name+' '+t);
    }
    assert.equal(Object.hasOwn(createCoupledModel(createEngine(data)).settings,'thermalJacobian'),false);
    assert.throws(()=>createCoupledModel(createEngine(data),{thermalJacobian:'other'}));
    report.passed=true;
  }else if(mode==='columns'){
    report.trials=[];
    const selections=cases().filter(c=>['cold','warm','heat-reversal'].includes(c.name));
    selections.push({name:'zero-exchange',config:fixture('cold',{refrigerantConductanceKWK:0})},
      {name:'closed-relaxation',config:fixture('cold',{sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:283.15,airInitialK:293.15,airLoadKW:0}})});
    for(const c of selections)for(const method of ['tr-bdf2','backward-euler'])for(const dt of [.001,.5]){
      const engine=createEngine(data),m=createCoupledModel(engine,{thermalJacobian:'exact',method}),s=m.create(c.config);
      const before=JSON.stringify(s),work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};let failure=null;
      try{m.trial(s,dt,work);}catch(e){failure={message:e.message,faultKind:e.faultKind};}
      assert.equal(JSON.stringify(s),before);
      const groups=[];let current=null;
      for(const e of work.diagnostics){
        if(e.type==='iteration'&&e.context){current={context:e.context,columns:[]};groups.push(current);}
        if(e.type==='exact-thermal-column'&&e.iteration===0)current.columns.push({column:e.column,values:e.values});
        if(e.type==='derivative')assert.ok(e.column<10,'No finite-difference thermal probes in exact mode.');
        if(e.type==='iteration'&&e.status==='converged'){assert.ok(e.fluidNorm<=1e-11);assert.ok(e.thermalNorm*1e-12/1e-11<=1e-12);}
      }
      assert.ok(groups.some(g=>g.columns.length===11));
      groups.forEach(g=>{
        assert.deepEqual(g.columns.map(c=>c.values),exactThermalColumns(s.spec,g.context.stageSeconds,g.context.stageWeight,g.context.physicalScales));
      });
      const baseline=createCoupledModel(engine,{method}),baseState=baseline.create(c.config),baseWork={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};
      let baselineFailure=null;try{baseline.trial(baseState,dt,baseWork);}catch(e){baselineFailure={message:e.message,faultKind:e.faultKind};}
      const baselineGroups=[];let base=null;
      for(const e of baseWork.diagnostics){
        if(e.type==='iteration'&&e.iteration===0){base={context:e.context,residual:e.residual,probes:[]};baselineGroups.push(base);}
        if(e.type==='derivative'&&e.iteration===0&&e.column>=10&&e.outcome==='used')base.probes.push(e);
      }
      report.trials.push({name:c.name,method,dt,failure,baselineFailure,conductancesKWK:s.spec.conductancesKWK,spec:s.spec,groups,baselineGroups,work:{evaluations:work.evaluations,iterations:work.iterations,linearSolves:work.linearSolves}});
    }
    // Mutating the detached recorded columns cannot change the next Newton assembly.
    const c=cases()[0],options={maxStep:.1},a=run(c,'exact',options),b=run(c,'exact',options,createCoupledModel,e=>{for(const d of e.events)if(d.type==='exact-thermal-column')d.values.fill(12345);});
    assert.deepEqual(a.state,b.state);assert.deepEqual(a.rows,b.rows);assert.deepEqual(a.counts,b.counts);
    report.detachedColumnMutationPassed=true;report.passed=true;
  }else if(mode==='compare'){
    report.cases=[];
    for(const c of cases())for(const t of [1e-6,1e-7,1e-8]){
      const options={...accuracyOptions(t),trace:true},a=run(c,'baseline',options),b=run(c,'exact',options);
      report.cases.push({name:c.name,relativeTolerance:t,baseline:summary(a),exact:summary(b),maximumDifferences:compare(a,b),
        identicalAcceptedTrace:hash(a.state.trace)===hash(b.state.trace),identicalRejectedTrace:hash(a.state.rejectionTrace)===hash(b.state.rejectionTrace),
        baselineState:a.state,exactState:b.state,baselineRows:a.rows,exactRows:b.rows});
      console.error('Compared: '+c.name+' '+t+' rejections '+a.work.rejectedTrials+' -> '+b.work.rejectedTrials);
    }
    report.passed=true;
  }else if(mode==='failures'){
    const c=cases().find(c=>c.name==='heat-reversal');report.failures=[];report.converged={solves:0,maximumFluidNorm:0,maximumThermalK:0};
    let derivativeCount=0,exactCount=0,lineSearchCount=0;
    const result=run(c,'exact',{...accuracyOptions(),trace:true},createCoupledModel,attempt=>{
      for(const e of attempt.events){
        if(e.type==='derivative'){assert.ok(e.column<10);derivativeCount++;}
        if(e.type==='exact-thermal-column')exactCount++;
        if(e.type==='line-search')lineSearchCount++;
        if(e.type==='iteration'&&e.status==='converged'){
          report.converged.solves++;report.converged.maximumFluidNorm=Math.max(report.converged.maximumFluidNorm,e.fluidNorm);
          report.converged.maximumThermalK=Math.max(report.converged.maximumThermalK,e.thermalNorm*.1);
          assert.ok(e.fluidNorm<=1e-11&&e.thermalNorm*.1<=1e-12);
        }
        if(e.type==='solve-failed'){
          const last=e.lastIteration;report.failures.push({seconds:attempt.startSeconds,trialSeconds:attempt.trialSeconds,
            message:e.message,faultKind:e.faultKind,iteration:last?.iteration,fluidNorm:last?.fluidNorm,
            thermalK:last?.thermalNorm*.1,dominantIndex:last?.dominantIndex,phases:last?.states.map(v=>v.phase)});
        }
      }
    });
    report.result=summary(result);report.state=result.state;report.rows=result.rows;
    report.diagnostics={derivativeCount,exactCount,lineSearchCount};report.passed=true;
  }else if(mode==='performance'){
    const pairs=Number(args[0]||5);assert.ok(Number.isInteger(pairs)&&pairs>=5);
    const workload=choice=>cases().map(c=>({name:c.name,...summary(run(c,choice,accuracyOptions()))}));
    // One complete untimed warm-up for each path in this same Node process.
    workload('baseline');workload('exact');report.warmupPairs=1;report.pairs=[];
    for(let pair=0;pair<pairs;pair++){
      const order=pair%2?['exact','baseline']:['baseline','exact'],runs={};
      for(const choice of order)runs[choice]=workload(choice);
      report.pairs.push({pair,order,...runs});console.error('Measured pair '+(pair+1)+'/'+pairs);
    }
    const cpuQuota='/sys/fs/cgroup/cpu.max';
    report.hardware={platform:process.platform,arch:process.arch,kernel:require('node:os').release(),cpus:require('node:os').cpus().map(c=>c.model),
      cgroupCpuMax:fs.existsSync(cpuQuota)?fs.readFileSync(cpuQuota,'utf8').trim():null,totalMemoryBytes:require('node:os').totalmem()};
    report.passed=true;
  }else if(mode==='domain'){
    report.cases=[];const engine=createEngine(data);
    const physical=s=>JSON.stringify({spec:s.spec,cells:s.cells,energies:s.energies,ledger:s.ledger,seconds:s.seconds,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
    for(const minStep of [1e-9,1e-5,.5])for(const limit of [200,400])for(const direction of ['outward','inward','zero']){
      const load=direction==='zero'?0:(limit===400?1:-1)*(direction==='outward'?1:-1);
      const m=createCoupledModel(engine,{thermalJacobian:'exact',minStep,maxStep:.5,trace:true}),s=m.create({sealed:true,refrigerantConductanceKWK:0,
        thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:load},schedule:[{seconds:2,patch:{airLoadKW:0}}]}),before=physical(s),r=m.advance(s,.5);
      if(direction==='outward'){
        assert.equal(r.stop?.kind,'domain');assert.equal(r.stop.evidence.confirmation,'exact-boundary-outward-direction');assert.equal(physical(s),before);
        const frozen=JSON.stringify(s);m.advance(s,1);assert.throws(()=>m.update(s,{airLoadKW:0}));assert.equal(JSON.stringify(s),frozen);
      }else{check(r);assert.equal(r.seconds,.5);if(direction==='zero')assert.deepEqual(s.energies,s.initialEnergies);}
      report.cases.push({minStep,limit,direction,seconds:s.seconds,stop:s.stop});
    }
    for(const minStep of [1e-9,1e-5,.5])for(const limit of [200,400]){
      const m=createCoupledModel(engine,{thermalJacobian:'exact',minStep,maxStep:.5}),s=m.create({sealed:true,refrigerantConductanceKWK:0,
        thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:0}});
      m.advance(s,.01);m.update(s,{airLoadKW:limit===400?1:-1});const before=physical(s),r=m.advance(s,.01);
      assert.equal(r.stop?.kind,'domain');assert.equal(physical(s),before);report.cases.push({minStep,limit,priorHistory:true,stop:r.stop});
    }
    // Probe-only domain errors must not be relabelled as a proven physical boundary.
    for(const kind of ['solver','domain','false-boundary-proof'])for(const minStep of [1e-9,1e-5,.5]){
      const injected=compiled('coupled-model.cjs',fs.readFileSync(path.join(__dirname,'coupled-model.cjs'),'utf8'),{'./coupled-implicit.cjs':{coupledNewton:()=>{throw Object.assign(Error('Injected probe failure'),{faultKind:kind==='solver'?'solver':'domain',...(kind==='false-boundary-proof'?{evidence:{source:'thermal',stage:'initial-direction',node:'air',temperatureK:400,rateKS:1}}:{})});}}}).createCoupledModel;
      const normal=createCoupledModel(engine,{thermalJacobian:'exact'}),s=normal.create(fixture('warm'));normal.advance(s,.001);normal.update(s,{airLoadKW:1.5});s.nextStepSeconds=.5;
      const before=physical(s),r=injected(engine,{thermalJacobian:'exact',minStep,maxStep:.5}).advance(s,.5);
      assert.equal(r.stop.kind,'solver');assert.equal(r.stop.evidence.confirmed,false);assert.equal(physical(s),before);
      report.cases.push({kind,minStep,probeOnly:true,stop:r.stop});
    }
    for(const minStep of [1e-9,1e-5,.5]){
      const hot=engine.statePT(3.5,450-273.15),m=createCoupledModel(engine,{thermalJacobian:'exact',minStep,maxStep:.5}),s=m.create({sealed:true,initial:Array.from({length:5},()=>({p:hot.p,h:hot.h})),thermal:{tubeProfileK:400,finProfileK:400,airInitialK:400,airLoadKW:0}});
      const before=physical(s),r=m.advance(s,.5);assert.equal(r.stop?.kind,'domain');assert.equal(r.stop.evidence.node,'tube-0');assert.equal(physical(s),before);report.cases.push({minStep,signedExchange:true,stop:r.stop});
    }
    report.passed=true;
  }else throw Error('Unknown mode '+mode);
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,mode,output}));
}
main().catch(e=>{report.passed=false;report.failure={message:e.message,stack:e.stack};fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(e);process.exitCode=1;});
