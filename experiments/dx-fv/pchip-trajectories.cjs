'use strict';
// Bounded diagnostic runs only. Existing candidate/default sources stay intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {performance}=require('node:perf_hooks');
const data=require('../../properties.json'),{createEngine}=require('../../engine');
const {createTemperatureEngine}=require('./saturation-temperature.cjs');
const {createCoupledModel}=require('./coupled-model.cjs'),F=require('./coupled-fixtures.cjs');
const [mode,output,mesh='5',selection='linear',tolerance='1e-8']=process.argv.slice(2),N=Number(mesh),tol=Number(tolerance);
assert.match(process.version,/^v22\./);assert.ok([5,9].includes(N));assert.ok(['extended','liquid','liquid-timing'].includes(mode));
assert.ok(['linear','pchip-log-pressure'].includes(selection));assert.ok([1e-7,1e-8].includes(tol));
const root=path.resolve(__dirname,'../..'),resolved=path.resolve(output),actual=fs.existsSync(resolved)?fs.realpathSync(resolved):path.join(fs.realpathSync(path.dirname(resolved)),path.basename(resolved));
assert.ok(!actual.startsWith(root+path.sep));
for(const protectedDir of ['/tmp/ammonia-stage2b-evidence','/tmp/ammonia-phase-event-evidence','/tmp/ammonia-saturation-evidence'])assert.ok(!actual.startsWith(protectedDir+path.sep));
const hash=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
let activeSnapshot=null;
function config(name){return name==='extended'?{...F.fixture('cold'),sectionCount:N,initial:Array.from({length:N},()=>({p:3.5,h:500})),
  schedule:[{seconds:120,patch:{airLoadKW:0,inlet:{p:3.5,h:500}}},{seconds:180,patch:{inlet:{p:3.3,h:500}}},{seconds:240,patch:{airLoadKW:1,inlet:{p:4,h:500}}}]}:
  {...F.fixture('cold'),sectionCount:N,initial:Array.from({length:N},()=>({p:32.65314902038559,h:686.779725665})),sealed:true,
    thermal:{tubeProfileK:343.42777804386204,finProfileK:343.42777804386204,airInitialK:343.42777804386204,airLoadKW:0}};}
function checked(r){assert.equal(r.stop,null,JSON.stringify(r.stop));
  assert.ok(r.lastResidual===null||r.lastResidual<=1e-11);assert.ok(r.lastTimeError===null||r.lastTimeError<=1);
  for(const x of [r.massResidualKg,...r.sectionResiduals.map(v=>v.massKg)])assert.ok(Math.abs(x)<1e-8);
  for(const x of [r.refrigerantEnergyResidualKJ,r.thermalEnergyResidualKJ,r.combinedEnergyResidualKJ,...r.sectionResiduals.map(v=>v.energyKJ),...r.nodes.map(v=>v.residualKJ)])assert.ok(Math.abs(x)<1e-6);
  for(const v of r.sections)assert.ok(Math.abs(v.energyResidual)<1e-7&&Math.abs(v.densityResidual)<1e-7);
  return r;
}
function withoutTrace(r){const out=structuredClone(r);out.trace=[];out.rejectionTrace=[];out.settings.trace=false;return out;}
function run(name,choice,silent=false){
  const engine=createTemperatureEngine(createEngine(data),data,choice),counts={ph:0,sat:0,stateMVU:0},counted={...engine};
  for(const key of Object.keys(counts))counted[key]=(...args)=>{counts[key]++;return engine[key](...args);};
  const settings={...F.accuracyOptions(tol),trace:true},m=createCoupledModel(counted,settings),s=m.create(config(name));
  const initial=withoutTrace(checked(m.record(s))),seed={cells:structuredClone(s.cells),energies:[...s.energies]},rows=[],start=performance.now();
  activeSnapshot={initial,seed,rows,lastEvaluation:null};
  const times=name==='extended'?[.01,.2,1,5,15,30,60,120,120.1,150]:[.001,.01,.05,.1];
  for(const t of times){const row=m.advance(s,t-s.seconds);activeSnapshot.lastEvaluation=row;checked(row);
    // Duration subtraction/addition can change an output clock by one ulp.
    // This diagnostic timestamp check does not alter any solver/event budget.
    assert.ok(Math.abs(row.seconds-t)<=4*Number.EPSILON*Math.max(1,t));rows.push(withoutTrace(row));if(!silent)console.error(name+' '+N+' '+choice+' '+tol+' t='+t+' accepted='+s.acceptedSteps/2+' rejected='+s.rejectedSteps);}
  const elapsedMS=performance.now()-start;
  const failures=s.rejectionTrace.filter(r=>r.kind==='solver'&&r.nonlinearResidual!==null);
  const otherFailures=s.rejectionTrace.filter(r=>r.kind==='solver'&&r.nonlinearResidual===null);
  const work={accepted:s.acceptedSteps/2,rejected:s.rejectedSteps,newtonFailures:failures.length,otherSolverFailures:otherFailures.length,
    temporalRejected:s.accuracyRejectedSteps,eventRejected:s.eventRejectedSteps,domainRejected:s.domainRejectedSteps,
    iterations:s.attemptedIterations,residualEvaluations:s.attemptedResidualEvaluations,linearSolves:s.attemptedLinearSolves};
  const last=rows.at(-1);return {name,sectionCount:N,interpolation:choice,tolerance:tol,settings:initial.settings,config:config(name),seed,
    initial,rows,elapsedMS,propertyCalls:counts,work,events:s.events,stop:s.stop,seedHash:hash(seed),recordHash:hash(rows),
    acceptedHistoryHash:hash(s.trace),rejectedHistoryHash:hash(s.rejectionTrace),nonlinearFailures:failures,otherFailures,
    terminalVaporEventSeconds:s.events.find(e=>e.section===N-1&&e.boundary==='vapor'&&e.direction==='heating')?.seconds??null,
    finalTotals:last.totals,finalLiquidMassKg:last.sections.reduce((a,v)=>a+v.massKg*(v.x===null?(v.phase.includes('liquid')?1:0):1-v.x),0)};
}
const report={diagnosticOnly:true,runtime:process.version,mode,sectionCount:N,interpolation:selection,tolerance:tol,qualified:false};
try{
  if(mode==='liquid-timing'){
    const warm=[run('liquid','linear',true),run('liquid','pchip-log-pressure',true)],pairs=[];
    for(let i=0;i<5;i++){const choices=i%2?['pchip-log-pressure','linear']:['linear','pchip-log-pressure'],pair={};
      for(const c of choices){const r=run('liquid',c,true),old=warm.find(v=>v.interpolation===c);for(const key of ['recordHash','seedHash','work','propertyCalls'])assert.deepEqual(r[key],old[key]);
        pair[c]={elapsedMS:r.elapsedMS,work:r.work,propertyCalls:r.propertyCalls};}pairs.push(pair);}
    report.pairs=pairs;report.warmup=warm.map(v=>({interpolation:v.interpolation,elapsedMS:v.elapsedMS,work:v.work}));
  }else{
    report.run=run(mode,selection);
    if(mode==='extended'&&selection==='linear'){
      const filename=path.join('/tmp/ammonia-stage2b-evidence',N===5?'five-extra.json':'nine-extra.json'),saved=JSON.parse(fs.readFileSync(filename,'utf8')).runs.find(v=>v.name.startsWith('extended')&&v.tolerance===tol);
      assert.deepEqual(report.run.initial,saved.initial);assert.deepEqual(report.run.rows,saved.rows.filter(v=>v.seconds<=150));report.defaultExactlyReproducesSavedPrefix=true;
    }
  }
  report.completed=true;
}catch(error){report.completed=false;report.progress=activeSnapshot;report.failure={name:error.name,message:error.message,stack:error.stack};fs.writeFileSync(output+'.failure.json',JSON.stringify(report,null,2)+'\n');throw error;}
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({completed:true,output,mode,sectionCount:N,event:report.run?.terminalVaporEventSeconds,work:report.run?.work}));
