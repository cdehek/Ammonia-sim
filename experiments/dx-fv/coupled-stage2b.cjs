'use strict';
// Stage 2B adapters and research measurements. Established source/tests stay intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const {execFileSync}=require('node:child_process'),crypto=require('node:crypto');
const Model=require('./coupled-model.cjs'),F=require('./coupled-fixtures.cjs');
const {createEngine}=require('../../engine'),data=require('../../properties.json');
const BASE='be9eb35a4ddf5098e685182f8104685127c6a6ee',root=path.resolve(__dirname,'../..');
const [mode,output,choice='baseline',mesh='9',...args]=process.argv.slice(2),N=Number(mesh);
assert.match(process.version,/^v22\./);assert.ok([5,9].includes(N));assert.ok(output);
const resolved=path.resolve(output),parent=fs.realpathSync(path.dirname(resolved));
assert.ok(!path.join(parent,path.basename(resolved)).startsWith(root+path.sep),'Evidence belongs outside Git.');
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const choices=['baseline','exact','fd-aware','exact-aware'];
function selection(c){assert.ok(choices.includes(c));return {...(c.startsWith('exact')?{thermalJacobian:'exact'}:{}),...(c.endsWith('aware')?{timestepGrowth:'failure-aware'}:{})};}
function compiled(file,source,overrides={}){const m=new Module(path.join(__dirname,file),module);m.filename=path.join(__dirname,file);m.paths=module.paths;const ordinary=m.require.bind(m);m.require=id=>Object.hasOwn(overrides,id)?overrides[id]:ordinary(id);m._compile(source,m.filename);return m.exports;}
function original(){const source=f=>execFileSync('git',['show',BASE+':experiments/dx-fv/'+f],{cwd:root,encoding:'utf8'});return compiled('coupled-model.cjs',source('coupled-model.cjs'),{'./coupled-implicit.cjs':compiled('coupled-implicit.cjs',source('coupled-implicit.cjs'))}).createCoupledModel;}
function config(c,n){if(c.sectionCount===n)return structuredClone(c);const out={...structuredClone(c),sectionCount:n};if(out.initial){assert.ok(out.initial.every(v=>v.p===out.initial[0].p&&v.h===out.initial[0].h),'Nonuniform cell PH cannot be interpolated. Use physical profiles.');out.initial=Array.from({length:n},()=>({...out.initial[0]}));}return out;}
function counted(){const engine=createEngine(data),counts={ph:0,sat:0,stateMVU:0},wrapped={...engine};for(const k of Object.keys(counts))wrapped[k]=(...a)=>{counts[k]++;return engine[k](...a);};return {engine:wrapped,counts};}
function check(r,stop=false){if(!stop)assert.equal(r.stop,null,JSON.stringify(r.stop));for(const v of [r.massResidualKg,...r.sectionResiduals.map(v=>v.massKg)])assert.ok(Math.abs(v)<1e-8);for(const v of [r.refrigerantEnergyResidualKJ,r.thermalEnergyResidualKJ,r.combinedEnergyResidualKJ,...r.sectionResiduals.map(v=>v.energyKJ),...r.nodes.map(v=>v.residualKJ)])assert.ok(Math.abs(v)<1e-6);assert.ok(r.sections.every(v=>v.massKg>0&&Math.abs(v.energyResidual)<1e-7&&Math.abs(v.densityResidual)<1e-7));if(r.lastTimeError!==null)assert.ok(r.lastTimeError<=1);}
function run(c,n,sel,options={},factory=Model.createCoupledModel,observer=null){const start=performance.now(),{engine,counts}=counted(),m=factory(engine,{...options,...selection(sel)},observer),s=m.create(config(c.config,n)),initial=m.record(s),rows=[];for(const t of c.samples){const r=m.advance(s,t-s.seconds);check(r);assert.equal(r.seconds,t);rows.push(r);if(c.name.startsWith('extended'))console.error('Extended sample '+n+' '+sel+' '+t+' accepted '+s.acceptedSteps/2+' rejected '+s.rejectedSteps);}const elapsedMS=performance.now()-start;return {initial,rows,state:s,elapsedMS,propertyCalls:counts,work:{acceptedTrials:s.acceptedSteps/2,rejectedTrials:s.rejectedSteps,newtonFailures:s.rejectedSteps-s.accuracyRejectedSteps-s.eventRejectedSteps-s.domainRejectedSteps,iterations:s.attemptedIterations,residualEvaluations:s.attemptedResidualEvaluations,linearSolves:s.attemptedLinearSolves},stateHash:hash(s),recordHash:hash(rows)};}
function summary(r){return {elapsedMS:r.elapsedMS,propertyCalls:r.propertyCalls,work:r.work,stateHash:r.stateHash,recordHash:r.recordHash};}
function temporal(a,b,tight=false){
 const e={pressureBar:0,enthalpyKJkg:0,fluidK:0,thermalK:0,eventSeconds:0};
 a.rows.forEach((row,j)=>{const ref=b.rows[j];assert.equal(row.seconds,ref.seconds);row.sections.forEach((v,i)=>{for(const [k,f]of [['pressureBar','p'],['enthalpyKJkg','h'],['fluidK','T']])e[k]=Math.max(e[k],Math.abs(v[f]-ref.sections[i][f]));});row.nodes.forEach((v,i)=>{e.thermalK=Math.max(e.thermalK,Math.abs(v.temperatureK-ref.nodes[i].temperatureK));});});
 assert.equal(a.state.events.length,b.state.events.length);a.state.events.forEach((v,i)=>{const w=b.state.events[i];for(const k of ['section','boundary','direction'])assert.equal(v[k],w[k]);e.eventSeconds=Math.max(e.eventSeconds,Math.abs(v.seconds-w.seconds));});
 assert.ok(e.pressureBar<5e-5&&e.enthalpyKJkg<.05&&e.fluidK<(tight?.001:.01)&&e.thermalK<(tight?.001:.01)&&e.eventSeconds<.001,JSON.stringify(e));return e;
}
const report={stage:'2B',startingCommit:BASE,runtime:process.version,mode,choice,sectionCount:N,checks:[]};
function write(suffix=''){fs.writeFileSync(output+suffix,JSON.stringify(report,null,2)+'\n');}
function adaptedFactory(n,sel){return (engine,options={},observer=null)=>{const m=Model.createCoupledModel(engine,{...options,...selection(sel)},observer);if(n===9){const create=m.create;m.create=c=>create(c&&c.sectionCount!==undefined&&![5,9].includes(c.sectionCount)?c:config(c||{},n));}return m;};}
function adaptedFixtures(n){return {...F,fixture:(kind,extra)=>config(F.fixture(kind,extra),n),cases:()=>F.cases().map(c=>({...c,config:config(c.config,n)}))};}
function replace(source,before,after){assert.ok(source.includes(before),'Missing adapter token '+before);return source.split(before).join(after);}
function suite(){
  if(N===9&&!process.env.DX_COUPLED_REFERENCE_PATH)process.env.DX_COUPLED_REFERENCE_PATH=path.join(__dirname,'coupled-stage2b-reference.json');
  const kind=args[0]||'coupled-test',filename=kind+'.cjs';assert.ok(['coupled-test','coupled-controls','coupled-browser'].includes(kind));
  let source=fs.readFileSync(path.join(__dirname,filename),'utf8');
  if(N===9&&kind==='coupled-test'){
    for(const [a,b]of [['sectionCount:5','sectionCount:9'],['r.sectionCount,5','r.sectionCount,9'],['r.nodes.length,11','r.nodes.length,19'],['Array(11)','Array(19)'],['b[10]','b[18]'],['i<5','i<9'],['v-.12','v-.60/9'],['length:5','length:9'],['v.section===4','v.section===8'],['s.cells[4]','s.cells[8]'],['recoveries===31','recoveries===55']])if(source.includes(a))source=replace(source,a,b);
    source=replace(source,'[273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,273.15,278.15]','[...Array(18).fill(273.15),278.15]');
    source=replace(source,"assert.equal(reference.sectionCount,5)","assert.equal(reference.sectionCount,9)");
  }
  if(N===9&&kind==='coupled-browser'){
    source=replace(source,'sectionCount:5','sectionCount:9');source=replace(source,'v.section===4','v.section===8');
    source=replace(source,"return cases().map(c=>{","return cases().map(c=>{ c.config.sectionCount=9; c.config.initial=Array.from({length:9},()=>({...c.config.initial[0]}));");
  }
  if(kind==='coupled-browser')source=replace(source,'const m=create(engine),s=m.create(c.config)',`const m=create(engine,${JSON.stringify(selection(choice))}),s=m.create(c.config)`);
  // Browser adapter reads actual current coupled sources, not modified application.
  process.argv[2]=output;
  compiled(filename,source,{'./coupled-model.cjs':{...Model,createCoupledModel:adaptedFactory(N,choice)},'./coupled-fixtures.cjs':adaptedFixtures(N)});
  return true;
}
async function main(){
 if(mode==='suite'){suite();return;}
 if(mode==='domain'){
  let source=fs.readFileSync(path.join(__dirname,'roadmap-a1.cjs'),'utf8');
  source=source.replaceAll("thermalJacobian:'exact'",`...${JSON.stringify(selection(choice))}`);
  process.argv=[process.argv[0],process.argv[1],'domain',output];
  compiled('roadmap-a1.cjs',source,{'./coupled-model.cjs':{...Model,createCoupledModel:adaptedFactory(N,'baseline')},'./coupled-fixtures.cjs':adaptedFixtures(N)});return;
 }
 if(mode==='rules'){
  process.argv=[process.argv[0],process.argv[1],'rules',output];
  compiled('roadmap-a2.cjs',fs.readFileSync(path.join(__dirname,'roadmap-a2.cjs'),'utf8'),{
   './coupled-model.cjs':{...Model,createCoupledModel:adaptedFactory(N,'baseline')},'./coupled-fixtures.cjs':adaptedFixtures(N)});return;
 }
 if(mode==='baseline'||mode==='baseline-history'){
  report.comparisons=[];const old=original();
  for(const sel of (mode==='baseline-history'?['baseline']:choices))for(const c of F.cases()){
   console.error('A2 equivalence '+sel+' '+c.name);const opts={...F.accuracyOptions(),...(mode==='baseline-history'?{trace:true}:{})},a=run(c,5,sel,opts,old),b=run(c,5,sel,opts);
   assert.equal(a.stateHash,b.stateHash);assert.equal(a.recordHash,b.recordHash);assert.deepEqual(a.propertyCalls,b.propertyCalls);assert.deepEqual(a.work,b.work);
   report.comparisons.push({name:c.name,choice:sel,...summary(b),acceptedHistory:b.state.trace.length,rejectedHistory:b.state.rejectionTrace.length});write('.partial.json');
  }
 }else if(mode==='geometry'||mode==='columns'){
  const engine=createEngine(data),m=Model.createCoupledModel(engine),{coefficients}=require('./hydraulics.cjs');report.geometry=[];
  for(const n of [5,9]){
   const s=m.create({sectionCount:n}),g=s.spec.thermal.metadata.geometry,r=m.record(s),cap=prefix=>s.spec.thermal.nodes.filter(v=>v.id.startsWith(prefix)).reduce((a,v)=>a+v.capacityKJK,0);
   assert.equal(s.cells.length,n);assert.equal(s.energies.length,2*n+1);assert.equal(s.spec.fluid.connections.length,n+1);
   const near=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
   near(s.cells.reduce((a,v)=>a+v.volumeM3,0),.003);near(cap('tube'),g.tubeCapacityKJK);near(cap('fin'),g.finCapacityKJK);near(cap('air'),g.airCapacityKJK);near(s.spec.conductancesKWK.reduce((a,v)=>a+v,0),.60);
   near(s.spec.fluid.connections.reduce((a,v)=>a+v.lengthM,0),g.lengthM);
   const donor=engine.ph(3.5,500),parts=s.spec.fluid.connections.map(f=>coefficients(donor,f)),whole=coefficients(donor,{...s.spec.fluid.connections[0],lengthM:g.lengthM,minorK:1002});
   for(const key of ['linear','quadratic'])near(parts.reduce((a,v)=>a+v[key],0)/whole[key],1);
   report.geometry.push({sectionCount:n,spec:s.spec,initial:r,capacityTotals:{tube:cap('tube'),fin:cap('fin'),air:cap('air')},hydraulicParts:parts,hydraulicWhole:whole});
  }
  const profile=[{left:0,right:.27,p:3.5,h:500},{left:.27,right:.64,p:3.5,h:600},{left:.64,right:1,p:3.5,h:700}],tube=[{left:0,right:.43,temperatureK:273.15},{left:.43,right:1,temperatureK:290}],fin=[{left:0,right:.61,temperatureK:278.15},{left:.61,right:1,temperatureK:288}];
  report.uniformProfiles=[5,9].map(n=>{const a=m.create({sectionCount:n}),b=m.create({sectionCount:n,initialProfile:[{left:0,right:1,p:a.spec.fluid.initial[0].p,h:a.spec.fluid.initial[0].h}]});for(let i=0;i<n;i++)for(const k of ['massKg','internalEnergyKJ','volumeM3'])assert.ok(Math.abs(a.cells[i][k]-b.cells[i][k])<1e-12);return {sectionCount:n,ordinary:m.record(a),integrated:m.record(b)};});
  report.nonuniform=[5,9].map(n=>{const s=m.create({sectionCount:n,initialProfile:profile,thermal:{tubeProfileK:tube,finProfileK:fin,airInitialK:293.15}});return {sectionCount:n,config:{sectionCount:n,initialProfile:profile,thermal:{tubeProfileK:tube,finProfileK:fin,airInitialK:293.15}},cells:s.cells,energies:s.energies,spec:s.spec,record:m.record(s)};});
  for(const key of ['massKg','internalEnergyKJ'])assert.ok(Math.abs(report.nonuniform[0].record.totals[key]-report.nonuniform[1].record.totals[key])<1e-10);
  assert.ok(Math.abs(report.nonuniform[0].energies.reduce((a,v)=>a+v,0)-report.nonuniform[1].energies.reduce((a,v)=>a+v,0))<1e-10);
  assert.throws(()=>m.create({sectionCount:17}),/five or nine refrigerant sections only/);assert.throws(()=>m.create({initialProfile:[{left:0,right:.9,p:3.5,h:500}]}));
  if(mode==='columns'){
   report.columns=[];
   for(const n of [5,9])for(const method of ['tr-bdf2','backward-euler'])for(const c of [...F.cases().filter(c=>['cold','warm','heat-reversal'].includes(c.name)),{name:'zero-exchange',config:F.fixture('cold',{sealed:true,refrigerantConductanceKWK:0})},{name:'closed-relaxation',config:F.fixture('cold',{sealed:true})}])for(const dt of [.001,.5]){
    const captures=[],x=Model.createCoupledModel(engine,{method,thermalJacobian:'exact'},a=>captures.push(a));const s=x.create(config(c.config,n)),before=hash(s),work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};let failure=null;try{x.trial(s,dt,work);}catch(e){failure={kind:e.faultKind,message:e.message};}assert.equal(hash(s),before);
    report.columns.push({sectionCount:n,method,name:c.name,dt,spec:s.spec,work,failure});
   }
  }
 }else if(mode==='extra'){
  const g=JSON.parse(fs.readFileSync(args[0]||path.join(path.dirname(output),'geometry.json'),'utf8'));
  const nonuniform=g.nonuniform.find(v=>v.sectionCount===N).config;
  const extras=[{name:'nonuniform',config:nonuniform,samples:[.01,.05,.2,1,5,15,30,60]},
   {name:'extended pressure-drive removal/reversal/restoration',config:F.fixture('cold',{schedule:[{seconds:120,patch:{airLoadKW:0,inlet:{p:3.5,h:500}}},{seconds:180,patch:{inlet:{p:3.3,h:500}}},{seconds:240,patch:{airLoadKW:1,inlet:{p:4,h:500}}}]}),samples:[.01,.2,1,5,15,30,60,120,120.1,150,180,180.1,210,240,240.1,270,300,360]}];
  report.runs=[];for(const c of extras)for(const tolerance of [1e-6,1e-7,1e-8]){
   console.error('Extended '+N+' '+choice+' '+c.name+' '+tolerance);const r=run(c,N,choice,F.accuracyOptions(tolerance));report.runs.push({name:c.name,tolerance,...r});write('.partial.json');
  }
 }else if(mode==='compare'){
  report.runs=[];report.temporal=[];for(const sel of choices)for(const c of F.cases()){
   const runs=[];for(const tolerance of [1e-6,1e-7,1e-8]){
    console.error('Comparison '+N+' '+sel+' '+c.name+' '+tolerance);const r=run(c,N,sel,F.accuracyOptions(tolerance));runs.push(r);report.runs.push({name:c.name,choice:sel,tolerance,...r});write('.partial.json');
   }
   report.temporal.push({name:c.name,choice:sel,nominal:temporal(runs[0],runs[2]),tight:temporal(runs[1],runs[2],true)});
  }
 }else if(mode==='spatial'){
  const five=JSON.parse(fs.readFileSync(args[0]||path.join(path.dirname(output),'five-frozen.json'),'utf8'));
  const nine=JSON.parse(fs.readFileSync(args[1]||path.join(path.dirname(output),'nine-compare.json'),'utf8'));
  assert.ok(five.passed&&nine.passed);const engine=createEngine(data);
  function project(r,n){
   if(!r.nodes){const spec=require('./thermal-geometry.cjs').createThermalConfig({sectionCount:n});r={...r,nodes:spec.nodes.map((v,i)=>({...v,temperatureK:r.temperaturesK[i],energyKJ:v.capacityKJK*(r.temperaturesK[i]-273.15)})),totals:{massKg:r.sections.reduce((a,v)=>a+v.massKg,0),internalEnergyKJ:r.sections.reduce((a,v)=>a+v.internalEnergyKJ,0)}};}
   const bins=Array.from({length:45},(_,j)=>{const left=j/45,right=(j+1)/45;let mass=0,energy=0,liquid=0,tubeEnergy=0,finEnergy=0;
    r.sections.forEach((v,i)=>{const overlap=Math.max(0,Math.min(right,(i+1)/n)-Math.max(left,i/n)),fraction=overlap*n;
     const state=v.x===undefined?engine.ph(v.p,v.h):v,x=state.x===null?(state.phase.toLowerCase().includes('liquid')?0:1):state.x;
     mass+=fraction*v.massKg;energy+=fraction*v.internalEnergyKJ;liquid+=fraction*v.massKg*(1-x);
     tubeEnergy+=fraction*r.nodes[2*i].energyKJ;finEnergy+=fraction*r.nodes[2*i+1].energyKJ;
    });return {left,right,massKg:mass,internalEnergyKJ:energy,liquidMassKg:liquid,tubeEnergyKJ:tubeEnergy,finEnergyKJ:finEnergy};});
   for(const [key,expected]of [['massKg',r.totals.massKg],['internalEnergyKJ',r.totals.internalEnergyKJ],['tubeEnergyKJ',r.nodes.filter(v=>v.id.startsWith('tube')).reduce((a,v)=>a+v.energyKJ,0)],['finEnergyKJ',r.nodes.filter(v=>v.id.startsWith('fin')).reduce((a,v)=>a+v.energyKJ,0)]])assert.ok(Math.abs(bins.reduce((a,v)=>a+v[key],0)-expected)<1e-10);
   return {bins,totals:Object.fromEntries(['massKg','internalEnergyKJ','liquidMassKg','tubeEnergyKJ','finEnergyKJ'].map(k=>[k,bins.reduce((a,v)=>a+v[k],0)])),air:r.nodes.at(-1),ports:{inlet:r.fluxes.faces[0],outlet:r.fluxes.faces.at(-1),outletState:r.outlet},totalTubeRefrigerantKW:r.fluxes.tubeRefrigerant.reduce((a,v)=>a+v,0),boundaryLedger:{inlet:r.ledger.faces[0],outlet:r.ledger.faces.at(-1)},positions:[.1,.3,.5,.7,.9].map(x=>{const i=Math.floor(x*n),v=r.sections[i],ph=engine.ph(v.p,v.h);return {x,cellLeft:i/n,cellRight:(i+1)/n,fluid:{...v,quality:ph.x,phase:ph.phase,superheatK:Math.max(0,ph.T-engine.sat(ph.p).T)},tube:r.nodes[2*i],fin:r.nodes[2*i+1]};}),events:r.events};
  }
  report.spatial=[];for(const c of five.cases){const a=c.runs.find(v=>v.relativeTolerance===1e-8),b=nine.runs.find(v=>v.name===c.name&&v.choice==='baseline'&&v.tolerance===1e-8);assert.ok(a&&b);
   const rows=a.rows.map((v,j)=>{const w=b.rows[j];assert.equal(v.seconds,w.seconds);const p=project(v,5),q=project(w,9);return {seconds:v.seconds,five:p,nine:q,differences:Object.fromEntries(Object.keys(p.totals).map(k=>[k,q.totals[k]-p.totals[k]]))};});report.spatial.push({name:c.name,rows});
  }
  const geometry=JSON.parse(fs.readFileSync(path.join(path.dirname(output),'geometry.json'),'utf8'));
  report.initialUniform=geometry.geometry.map(v=>({sectionCount:v.sectionCount,...project(v.initial,v.sectionCount)}));
  report.initialNonuniform=geometry.nonuniform.map(v=>({sectionCount:v.sectionCount,...project(v.record,v.sectionCount)}));
  const extras=[5,9].map(n=>path.join(path.dirname(output),(n===5?'five':'nine')+'-extra.json'));
  if(extras.every(v=>fs.existsSync(v))){const [a,b]=extras.map(v=>JSON.parse(fs.readFileSync(v,'utf8')));assert.ok(a.passed&&b.passed);
   for(const r of a.runs.filter(v=>v.tolerance===1e-8)){const q=b.runs.find(v=>v.name===r.name&&v.tolerance===1e-8);assert.ok(q);report.spatial.push({name:r.name,rows:r.rows.map((v,j)=>{const w=q.rows[j];assert.equal(v.seconds,w.seconds);const p=project(v,5),q=project(w,9);return {seconds:v.seconds,five:p,nine:q,differences:Object.fromEntries(Object.keys(p.totals).map(k=>[k,q.totals[k]-p.totals[k]]))};})});}
  }
  report.projection='45 equal accounting intervals, not a simulated mesh. Extensive M/U and thermal E are integrated by overlap; PH, quality and temperatures are piecewise-constant reconstructions at common physical positions. Port flows and donor enthalpy transport are compared at identical boundaries.';
 }else if(mode==='observed'){
  report.runs=[];for(const sel of choices)for(const c of F.cases()){
   const stats={convergedSolves:0,failedNewton:0,otherFailedSolves:0,fluidNorm:0,thermalClosureK:0,attempts:[]};
   const observer=a=>{
    for(const e of a.events){
     if(e.type==='iteration'&&e.status==='converged'){assert.ok(e.fluidNorm<=1e-11&&e.thermalNorm*.1<=1e-12);stats.convergedSolves++;stats.fluidNorm=Math.max(stats.fluidNorm,e.fluidNorm);stats.thermalClosureK=Math.max(stats.thermalClosureK,e.thermalNorm*.1);}
     if(e.type==='solve-failed'){if(Number.isFinite(e.nonlinearResidual))stats.failedNewton++;else stats.otherFailedSolves++;}
     // Detached recording cannot change numerical arithmetic.
     if(e.type==='derivative'&&e.residual)e.residual.fill(123);
     if(e.type==='exact-thermal-column')e.values.fill(456);
    }
    stats.attempts.push({seconds:a.startSeconds,dt:a.trialSeconds,failure:a.failure,reason:a.rejectionReason,error:a.temporalError});
   };
   console.error('Observer equivalence '+N+' '+sel+' '+c.name);const opts={...F.accuracyOptions(),trace:true},a=run(c,N,sel,opts,Model.createCoupledModel),b=run(c,N,sel,opts,Model.createCoupledModel,observer);
   assert.equal(a.stateHash,b.stateHash);assert.equal(a.recordHash,b.recordHash);assert.deepEqual(a.work,b.work);assert.deepEqual(a.propertyCalls,b.propertyCalls);
   assert.equal(stats.failedNewton+stats.otherFailedSolves,b.work.newtonFailures);const untraced=x=>JSON.parse(JSON.stringify(x,(k,v)=>k==='trace'?(Array.isArray(v)?[]:false):k==='rejectionTrace'?[]:v));
   report.runs.push({name:c.name,choice:sel,...summary(b),stateHash:hash(untraced(b.state)),recordHash:hash(untraced(b.rows)),equivalenceStateHash:b.stateHash,equivalenceRecordHash:b.recordHash,acceptedHistory:b.state.trace.length,rejectedHistory:b.state.rejectionTrace.length,stats});write('.partial.json');
  }
 }else if(mode==='orders'){
  report.orders=[];
  for(const sel of choices){
   const c={name:'sealed smooth fixed-step order',config:F.fixture('cold',{sealed:true}),samples:[1]};
   const ref=run(c,N,sel,{...F.accuracyOptions(1e-9),maxStep:.005});
   for(const method of ['tr-bdf2','backward-euler']){
    const errors=[.1,.05,.025].map(maxStep=>{const r=run(c,N,sel,{method,adaptive:false,maxStep});return Math.max(...r.rows[0].nodes.map((v,i)=>Math.abs(v.temperatureK-ref.rows[0].nodes[i].temperatureK)));});
    const orders=errors.slice(1).map((v,i)=>Math.log2(errors[i]/v));assert.ok(orders.every(v=>v>(method==='tr-bdf2'?1.8:.8)&&v<(method==='tr-bdf2'?2.2:1.2)),JSON.stringify({sel,method,errors,orders}));
    report.orders.push({choice:sel,method,errorsK:errors,orders});
   }
  }
 }else if(mode==='memory'){
  assert.equal(typeof global.gc,'function','Use a fresh node --expose-gc process.');global.gc();const before=process.memoryUsage();
  const c=F.cases().find(v=>v.name===(args[0]||'cold'));assert.ok(c);const r=run(c,N,choice,F.accuracyOptions());global.gc();
  report.sample={name:c.name,...summary(r),before,retained:process.memoryUsage(),peakRSSKiB:process.resourceUsage().maxRSS,stateSerializedBytes:Buffer.byteLength(JSON.stringify(r.state)),recordSerializedBytes:Buffer.byteLength(JSON.stringify(r.rows))};
  report.memoryMeaning='Fresh process, full cold fixture and original output schedule. maxRSS includes property tables, JIT, transient allocations and retained output; heap is after GC. Timing is not a controlled benchmark.';
 }else if(mode==='performance'){
  const pairs=Number(args[0]||5);assert.ok(pairs>=5);report.hardware={platform:process.platform,arch:process.arch,cpu:require('node:os').cpus()[0].model,kernel:require('node:os').release(),cpuMax:fs.readFileSync('/sys/fs/cgroup/cpu.max','utf8').trim()};report.blocks=[];
  const configs=choices.flatMap(sel=>[5,9].map(n=>({sel,n}))),warm=[];
  for(let block=-1;block<pairs;block++){
   const order=block<0?configs:[...configs.slice(block%8),...configs.slice(0,block%8)];if(block%2===1)order.reverse();const rows=[];
   for(const {sel,n}of order)for(const c of F.cases()){const r=run(c,n,sel,F.accuracyOptions()),row={name:c.name,choice:sel,sectionCount:n,...summary(r)};if(block>=0){const reference=warm.find(v=>v.name===c.name&&v.choice===sel&&v.sectionCount===n);for(const k of ['work','propertyCalls','stateHash','recordHash'])assert.deepEqual(row[k],reference[k]);}rows.push(row);console.error('Timing '+block+' '+sel+' '+n+' '+c.name);}
   if(block<0)warm.push(...rows);else report.blocks.push(rows);report.warmup=warm;write('.partial.json');
  }
 }else throw Error('Unknown Stage 2B mode');
 report.passed=true;write();console.log(JSON.stringify({passed:true,mode,output}));
}
main().catch(e=>{report.passed=false;report.failure={message:e.message,stack:e.stack};write('.failure.json');console.error(e);process.exitCode=1;});
