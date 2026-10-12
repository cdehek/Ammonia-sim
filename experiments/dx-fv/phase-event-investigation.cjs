'use strict';
// Diagnostic comparators only. Never edits or replaces an accepted solver.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const crypto=require('node:crypto'),Module=require('node:module');
const {execFileSync}=require('node:child_process');
const {createEngine}=require('../../engine.js'),data=require('../../properties.json');
const Model=require('./coupled-model.cjs'),F=require('./coupled-fixtures.cjs');
const root=path.resolve(__dirname,'../..'),BASE='be9eb35a4ddf5098e685182f8104685127c6a6ee';
const [mode,output,mesh='5',seedKind='js']=process.argv.slice(2),N=Number(mesh);
assert.match(process.version,/^v22\./);assert.ok([5,9].includes(N));
assert.ok(output&&!path.resolve(output).startsWith(root+path.sep));
const evidence=process.env.PHASE_EVIDENCE||'/tmp/ammonia-stage2b-evidence';
const actualOutput=path.join(fs.realpathSync(path.dirname(path.resolve(output))),path.basename(output));
assert.ok(!actualOutput.startsWith(root+path.sep)&&!actualOutput.startsWith(fs.realpathSync(evidence)+path.sep),'Diagnostic outputs must not overwrite protected source or saved evidence.');
const hash=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
const load=n=>JSON.parse(fs.readFileSync(path.join(evidence,n),'utf8'));
const matrix=load((N===5?'five':'nine')+'-extra.json');
const saved=matrix.runs.find(v=>v.name.startsWith('extended')&&v.tolerance===1e-8);
const event=saved.state.events.find(v=>v.section===N-1&&v.boundary==='vapor'&&v.direction==='heating');
const config={...F.fixture('cold'),sectionCount:N,initial:Array.from({length:N},()=>({p:3.5,h:500})),
  schedule:[{seconds:120,patch:{airLoadKW:0,inlet:{p:3.5,h:500}}},{seconds:180,patch:{inlet:{p:3.3,h:500}}},{seconds:240,patch:{airLoadKW:1,inlet:{p:4,h:500}}}]};
function original(){
  function compiled(f,overrides={}){const filename=path.join(__dirname,f),m=new Module(filename,module);m.filename=filename;m.paths=module.paths;
    const normal=m.require.bind(m);m.require=id=>overrides[id]||normal(id);
    m._compile(execFileSync('git',['show',BASE+':experiments/dx-fv/'+f],{cwd:root,encoding:'utf8'}),filename);return m.exports;}
  return compiled('coupled-model.cjs',{'./coupled-implicit.cjs':compiled('coupled-implicit.cjs')}).createCoupledModel;
}
function engineCounted(){const engine=createEngine(data),counts={ph:0,sat:0,stateMVU:0},wrapped={...engine};
  for(const k of Object.keys(counts))wrapped[k]=(...a)=>{counts[k]++;return engine[k](...a);};return {engine:wrapped,counts};}
function physical(s){return {seconds:s.seconds,cells:s.cells,energies:s.energies,spec:s.spec,events:s.events};}
function localSeed(m,s){
  assert.ok(['js','eos'].includes(seedKind));
  if(seedKind==='js'){
    const row=saved.rows.find(v=>v.seconds===120);
    s.cells=row.sections.map(v=>({massKg:v.massKg,internalEnergyKJ:v.internalEnergyKJ,volumeM3:v.volumeM3,pressureGuess:v.p}));
    s.energies=row.nodes.map(v=>v.energyKJ);
  }else{
    const reference=load((N===5?'five':'nine')+'-fresh-reference.json');
    const row=reference.cases.find(v=>v.name==='cold').runs[1].samples.find(v=>v.seconds===120);
    s.cells=row.sections.map((v,i)=>({massKg:v.rho*.003/N,internalEnergyKJ:v.rho*.003/N*v.u,volumeM3:s.cells[i].volumeM3,pressureGuess:v.p}));
    s.energies=row.temperaturesK.map((v,i)=>s.spec.thermal.nodes[i].capacityKJK*(v-273.15));
  }
  // Local comparator bookkeeping starts at 120 s. Physical M/U/V and E are
  // detached inputs; the solver, properties, tolerances and upcoming patch stay
  // exactly original. No such initialization is inserted into qualification.
  s.initialCells=structuredClone(s.cells);s.initialEnergies=[...s.energies];s.seconds=120;
}
function inspect(s){const e=createEngine(data),cap=s.spec.thermal.nodes.map(v=>v.capacityKJK);
  return {seconds:s.seconds,thermalK:s.energies.map((v,i)=>273.15+v/cap[i]),
    fluid:s.cells.map(c=>{const p=c.pressureGuess,h=(c.internalEnergyKJ+100*p*c.volumeM3)/c.massKg;
      const ph=e.ph(p,h),canonical=e.stateMVU(c.massKg,c.volumeM3,c.internalEnergyKJ,p);
      return {massKg:c.massKg,internalEnergyKJ:c.internalEnergyKJ,volumeM3:c.volumeM3,
        coordinate:ph,canonical,marginKJkg:ph.h-e.sat(ph.p).hg,canonicalMarginKJkg:canonical.h-e.sat(canonical.p).hg};})};}
function run(factory,local,observed){
  const {engine,counts}=engineCounted(),samples=[],captures=[];let s,lastCaptured=-Infinity;
  const observer=observed?a=>{
    if(Math.abs(a.startSeconds-event.seconds)<.025){
      if(a.startSeconds!==lastCaptured){captures.push({kind:'accepted-start',state:structuredClone(s)});lastCaptured=a.startSeconds;}
      if(!a.failure&&!a.rejectionReason){
        const contexts=new Map(),endpoints=[];
        for(const v of a.events){if(v.type==='iteration'&&v.context)contexts.set(v.solveId,v.context);
          if(v.type==='iteration'&&v.status==='converged')endpoints.push({context:contexts.get(v.solveId),states:structuredClone(v.states)});}
        captures.push({kind:'evaluated-endpoints',startSeconds:a.startSeconds,trialSeconds:a.trialSeconds,endpoints});
      }
    }
  }:null;
  const m=factory(engine,F.accuracyOptions(1e-8),observer);s=m.create(config);if(local)localSeed(m,s);
  const initial=m.record(s),seedPhysical=structuredClone(physical(s));
  const times=local?[120.1,150]:saved.rows.map(v=>v.seconds).filter(v=>v<=150);
  for(const t of times){const r=m.advance(s,t-s.seconds);assert.equal(r.stop,null);assert.equal(r.seconds,t);samples.push(r);console.error('Targeted '+N+' '+seedKind+' '+t);}
  return {initial,samples,state:s,seedPhysical,physicalHash:hash(physical(s)),stateHash:hash(s),recordHash:hash(samples),propertyCalls:counts,
    captures:captures.map(v=>v.state?{kind:v.kind,...inspect(v.state)}:v),work:{accepted:s.acceptedSteps/2,rejected:s.rejectedSteps,iterations:s.attemptedIterations,residualEvaluations:s.attemptedResidualEvaluations,linearSolves:s.attemptedLinearSolves}};
}
const report={diagnosticOnly:true,mode,sectionCount:N,seedKind,runtime:process.version,startingCommit:BASE};
if(mode==='legacy-prefix'){
  assert.equal(N,5);const r=run(original(),false,false);
  assert.deepEqual(r.initial,saved.initial);
  assert.deepEqual(r.samples,saved.rows.filter(v=>v.seconds<=150));
  report.legacyExactlyReproducesSavedPrefix=true;report.run=r;
}else if(mode==='local'){
  const a=run(Model.createCoupledModel,true,false),b=run(Model.createCoupledModel,true,true);
  for(const k of ['stateHash','recordHash','propertyCalls','work'])assert.deepEqual(a[k],b[k]);
  report.observationalEquivalence=true;report.run=b;
  report.eventDifferenceFromSavedSeconds=b.state.events.find(v=>v.section===N-1&&v.boundary==='vapor').seconds-event.seconds;
  if(N===5&&seedKind==='js'){
    const old=run(original(),true,false);for(const k of ['stateHash','recordHash','propertyCalls','work'])assert.deepEqual(a[k],old[k]);
    report.legacyLocalExactlyEquivalent=true;
  }
}else if(mode==='localization-check'){
  const filename=process.argv[6];assert.ok(filename);const r=JSON.parse(fs.readFileSync(filename,'utf8')).run;
  const event=r.state.events.find(e=>e.section===N-1&&e.boundary==='vapor'),engine=createEngine(data);
  const trial=r.captures.find(c=>c.kind==='evaluated-endpoints'&&c.startSeconds<=event.bracketStartSeconds&&c.startSeconds+c.trialSeconds>=event.bracketEndSeconds);
  const pre=r.captures.find(c=>c.kind==='accepted-start'&&c.seconds===trial.startSeconds);
  const first=event.bracketStartSeconds===trial.startSeconds;
  const left=first?pre.fluid[N-1].coordinate:trial.endpoints[3].states[N-1],right=trial.endpoints[first?3:5].states[N-1];
  assert.ok(Math.abs(left.h-engine.sat(left.p).hg-event.left)<1e-8);
  assert.ok(Math.abs(right.h-engine.sat(right.p).hg-event.right)<1e-8);
  const V=pre.fluid[N-1].volumeM3;
  const inventory=v=>{const q=engine.ph(v.p,v.h),M=q.rho*V;return {M,U:M*q.h-100*q.p*V};};
  const a=inventory(left),b=inventory(right);
  function surface(alpha){const M=a.M+alpha*(b.M-a.M),U=a.U+alpha*(b.U-a.U),rho=M/V;
    // Algebraic inverse of the existing log-linear saturated-vapor density
    // curve. Zero is exactly the same dew surface h=hg; only a diagnostic
    // interpolation of accepted M/U is used, never a changed event definition.
    let i=0;while(i+1<data.p.length&&data.sat[i+1][6]<rho)i++;
    assert.ok(i+1<data.p.length&&rho>=data.sat[i][6]);
    const w=(Math.log(rho)-Math.log(data.sat[i][6]))/(Math.log(data.sat[i+1][6])-Math.log(data.sat[i][6]));
    const p=Math.exp(Math.log(data.p[i])+w*(Math.log(data.p[i+1])-Math.log(data.p[i])));
    return U-M*engine.sat(p).hg+100*p*V;
  }
  assert.ok(surface(0)<0&&surface(1)>0);let lo=0,hi=1;
  for(let i=0;i<40;i++){const mid=(lo+hi)/2;if(surface(mid)<0)lo=mid;else hi=mid;}
  const alpha=(lo+hi)/2,time=event.bracketStartSeconds+alpha*(event.bracketEndSeconds-event.bracketStartSeconds);
  report.result={nativeEvent:event,conservedLinearRootSeconds:time,nativeMinusConservedLinearSeconds:event.seconds-time,
    surfaceResidualKJ:surface(alpha),leftState:left,rightState:right,leftInventory:a,rightInventory:b,volumeM3:V};
}else if(mode==='table-check'){
  const filename=process.argv[6];assert.ok(filename);const ref=JSON.parse(fs.readFileSync(filename,'utf8'));assert.equal(ref.propertyKind,'table');
  const engine=createEngine(data),V=.003/N,worst={pressureBar:0,enthalpyKJkg:0,temperatureK:0,densityRelative:0};
  report.comparisons=ref.samples.map(v=>{
    const direct=v.state,mu=engine.stateMVU(v.massKg,V,v.internalEnergyKJ,direct.p),ph=engine.ph(direct.p,direct.h);
    worst.pressureBar=Math.max(worst.pressureBar,Math.abs(mu.p-direct.p));worst.enthalpyKJkg=Math.max(worst.enthalpyKJkg,Math.abs(mu.h-direct.h));
    worst.temperatureK=Math.max(worst.temperatureK,Math.abs(mu.T-direct.T),Math.abs(ph.T-direct.T));worst.densityRelative=Math.max(worst.densityRelative,Math.abs(ph.rho/direct.rho-1),Math.abs(mu.rho/direct.rho-1));
    return {seconds:v.seconds,independentTable:direct,originalMU:mu,originalPH:ph};
  });
  assert.ok(worst.pressureBar<1e-6&&worst.enthalpyKJkg<1e-4&&worst.temperatureK<1e-4&&worst.densityRelative<1e-7,JSON.stringify(worst));report.worst=worst;
}else if(mode==='properties'){
  const filename=process.argv[6];assert.ok(filename);const ref=JSON.parse(fs.readFileSync(filename,'utf8')),engine=createEngine(data),V=.003/N;
  function evaluate(v){const p=v.state.p,h=v.state.h,M=v.massKg,U=v.internalEnergyKJ,ph=engine.ph(p,h),du=engine.stateMVU(M,V,U,p),sat=engine.sat(p);
    return {seconds:v.seconds,eos:v.state,EOSMarginKJkg:v.marginKJkg,tableAtSamePH:ph,tableAtSameMU:du,tableSaturation:sat,
      MUPropertyMarginKJkg:du.h-engine.sat(du.p).hg};}
  report.comparisons=ref.samples.map(evaluate);
  report.event=ref.eventSeconds;report.seedPhysical=ref.seedPhysical;
}else throw Error('Unknown diagnostic mode');
report.passed=true;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:true,mode,output}));
