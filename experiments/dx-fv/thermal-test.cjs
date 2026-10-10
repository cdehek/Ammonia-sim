'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {createIntegrator}=require('./thermal-network.cjs'),{createThermalConfig,geometry}=require('./thermal-geometry.cjs');
const reference=JSON.parse(fs.readFileSync(process.env.DX_THERMAL_REFERENCE_PATH||path.join(__dirname,'thermal-reference.json'),'utf8'));
const sum=a=>a.reduce((x,y)=>x+y,0),max=a=>Math.max(0,...a.map(Math.abs));
const near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} versus ${b}, limit ${t}`);
const summary={source:reference.source,referenceVersions:{numpy:reference.numpy,scipy:reference.scipy},acceptance:{energyKJ:1e-6,nominalTemperatureK:.01,tightTemperatureK:.001},cases:[],checks:[],worstCombinedResidualKJ:0,worstNodeResidualKJ:0};
function conservation(r){
 const global=Math.abs(r.energyResidualKJ),local=max(r.nodes.map(n=>n.residualKJ));
 assert.ok(global<=1e-6&&local<=1e-6,'Per-node/global energy conservation');
 summary.worstCombinedResidualKJ=Math.max(summary.worstCombinedResidualKJ,global);summary.worstNodeResidualKJ=Math.max(summary.worstNodeResidualKJ,local);
 near(sum(r.ledger.nodesKJ),r.ledger.externalKJ,1e-6,'Paired internal links cancel');
}
function compact(r){return {seconds:r.seconds,temperatureK:r.nodes.map(n=>n.temperatureK),energyResidualKJ:r.energyResidualKJ,energyScaleKJ:r.energyScaleKJ,scaleRelativeEnergyResidual:r.energyResidualKJ/r.energyScaleKJ,nodeResidualsKJ:r.nodes.map(n=>n.residualKJ),maxNodeResidualKJ:max(r.nodes.map(n=>n.residualKJ)),externalKJ:r.ledger.externalKJ,acceptedSteps:r.acceptedSteps,rejectedSteps:r.rejectedSteps,accuracyRejectedSteps:r.accuracyRejectedSteps,domainRejectedSteps:r.domainRejectedSteps,linearSolves:r.attemptedLinearSolves,minStep:r.minAcceptedStepSeconds,maxStep:r.maxAcceptedStepSeconds,stop:r.stop};}
const profiles={tubeProfileK:[{left:0,right:.3,temperatureK:260},{left:.3,right:1,temperatureK:320}],finProfileK:[{left:0,right:.6,temperatureK:290},{left:.6,right:1,temperatureK:270}]};
const modes={nominal:{},tight:{relativeTolerance:1e-7,temperatureAbsoluteK:1e-5,maxStep:.25},reference:{relativeTolerance:1e-8,temperatureAbsoluteK:1e-6,maxStep:.125},maxStepRefined:{maxStep:.025}};
function config(name,n){
 const c={sectionCount:n};
 if(name==='loaded')c.airLoadKW=1;
 if(name==='stepped'){c.airLoadKW=1;c.schedule=[{seconds:15,patch:{loadsKW:{air:2}}},{seconds:30,patch:{loadsKW:{air:1}}}];}
 if(name==='reservoir'){c.airReservoirK=293.15;c.schedule=[{seconds:15,patch:{reservoirs:{air:303.15}}},{seconds:30,patch:{reservoirs:{air:283.15}}}];}
 if(name.startsWith('nonuniform'))Object.assign(c,profiles);
 return createThermalConfig(c);
}
function compare(r,sample,nonuniform,n){
 let t=r.nodes.map(v=>v.temperatureK),links=r.ledger.linksKJ;
 if(!nonuniform){
  t=[t[0],t[1],...(t.length===2*n?[]:[t.at(-1)])];
  // Every uniform section must match, not just the first pair.
  for(let i=0;i<n;i++){near(r.nodes[2*i].temperatureK,t[0],1e-10,'Uniform tube symmetry');near(r.nodes[2*i+1].temperatureK,t[1],1e-10,'Uniform fin symmetry');}
  links=[0,1,2].map(k=>sum(links.filter((_,i)=>i%3===k)));
 }
 assert.equal(t.length,sample.temperaturesK.length);
 return {temperatureK:max(t.map((v,i)=>v-sample.temperaturesK[i])),linkEnergyKJ:max(links.map((v,i)=>v-sample.linksKJ[i]))};
}
for(const n of [5,9])for(const name of ['closed','loaded','stepped','reservoir',`nonuniform${n}`]){
 const ref=reference.cases[name],runs=[];
 for(const [mode,settings]of Object.entries(modes)){
  const I=createIntegrator({...settings,trace:true}),s=I.create(config(name,n));let tempError=0,linkError=0;
  for(const sample of ref.samples){
   const r=sample.seconds===0?I.record(s):I.advance(s,sample.seconds-s.seconds);
   assert.equal(r.stop,null);assert.equal(r.seconds,sample.seconds);conservation(r);
   const error=compare(r,sample,name.startsWith('nonuniform'),n);tempError=Math.max(tempError,error.temperatureK);linkError=Math.max(linkError,error.linkEnergyKJ);
   near(sum(r.ledger.loadsKJ),sample.loadKJ,1e-9,'Exact external-load integral');
   assert.ok(r.trace.every(v=>v.error<=1));
   if(name==='closed')assert.ok(r.nodes.every(v=>v.temperatureK>=273.15-1e-10&&v.temperatureK<=293.15+1e-10),'Closed relaxation has no overshoot');
  }
  const r=I.record(s);assert.ok(tempError<(['nominal','maxStepRefined'].includes(mode)?.01:.001));
  // Ledger trajectory accuracy is independent of its tiny conservation residual.
  assert.ok(linkError<.01);
  if(name==='stepped'||name==='reservoir'){
   assert.deepEqual(r.boundaryEvents.map(v=>v.seconds),[15,30]);
   assert.ok(r.trace.every(v=>![15,30].some(t=>v.startSeconds<t&&v.endSeconds>t)),'No accepted step straddles a scheduled edit');
  }
  runs.push({mode,maximumTemperatureErrorK:tempError,maximumLinkIntegralErrorKJ:linkError,...compact(r)});
 }
 assert.ok(runs[1].maximumTemperatureErrorK<runs[0].maximumTemperatureErrorK,'Tighter settings improve independent accuracy');
 assert.ok(runs[2].maximumTemperatureErrorK<runs[1].maximumTemperatureErrorK);
 summary.cases.push({name,sections:n,runs});
}
// Closed-form two-node solution, coded independently of matrix assembly.
function two(initial=[280,320],g=.4){return {nodes:[{id:'a',capacityKJK:2,initialK:initial[0]},{id:'b',capacityKJK:3,initialK:initial[1]}],links:[{id:'exchange',from:'b',to:'a',conductanceKWK:g}]};}
for(const initial of [[280,320],[320,280]]){
 const I=createIntegrator(),s=I.create(two(initial));let error=0;
 for(const t of [.1,1,5,60]){
  const r=I.advance(s,t-s.seconds),eq=(2*initial[0]+3*initial[1])/5,decay=Math.exp(-.4*(1/2+1/3)*t);
  const expected=initial.map(v=>eq+(v-eq)*decay);
  error=Math.max(error,max(r.nodes.map((v,i)=>v.temperatureK-expected[i])));conservation(r);
  assert.equal(Math.sign(r.ledger.linksKJ[0]),Math.sign(initial[1]-initial[0]));
  near(r.totalEnergyKJ,2*(initial[0]-273.15)+3*(initial[1]-273.15),1e-8,'Closed energy');
 }
 assert.ok(error<.01);summary.checks.push({name:'Independent two-node analytic heat exchange/reversal',initialK:initial,maxTemperatureErrorK:error});
}
// Direct three-node qualification, separately from replicated section allocations.
{
 const g=geometry(),I=createIntegrator(),s=I.create({nodes:[{id:'tube',capacityKJK:g.tubeCapacityKJK,initialK:273.15},{id:'fin',capacityKJK:g.finCapacityKJK,initialK:283.15},{id:'air',capacityKJK:g.airCapacityKJK,initialK:293.15}],links:[{id:'air-tube',from:'air',to:'tube',conductanceKWK:g.airTubeConductanceKWK},{id:'air-fin',from:'air',to:'fin',conductanceKWK:g.airFinConductanceKWK},{id:'fin-tube',from:'fin',to:'tube',conductanceKWK:g.contactConductanceKWK}]});
 let error=0;
 for(const sample of reference.cases.closed.samples){const r=sample.seconds?I.advance(s,sample.seconds-s.seconds):I.record(s);conservation(r);error=Math.max(error,max(r.nodes.map((v,i)=>v.temperatureK-sample.temperaturesK[i])));}
 assert.ok(error<.01);summary.checks.push({name:'Direct three-node independent matrix exponential',maxTemperatureErrorK:error});
}
// Fixed-step order and adaptive tolerance refinement, including stiff finite C/G.
for(const method of ['tr-bdf2','backward-euler']){
 const errors=[.2,.1,.05].map(h=>{const I=createIntegrator({method,adaptive:false,maxStep:h}),s=I.create(two());const r=I.advance(s,5);conservation(r);return Math.abs(r.nodes[0].temperatureK-(304-24*Math.exp(-5/3)));});
 const orders=errors.slice(1).map((v,i)=>Math.log2(errors[i]/v));
 assert.ok(orders.every(v=>v>(method==='tr-bdf2'?1.9:.9)&&v<(method==='tr-bdf2'?2.1:1.1)));
 summary.checks.push({name:'Fixed-step analytic temporal order',method,errorsK:errors,orders});
}
for(const g of [.004,40]){
 const errors=[1e-4,1e-5,1e-6].map(tol=>{
  const time=1/(g*(1/2+1/3)),I=createIntegrator({relativeTolerance:tol,temperatureAbsoluteK:tol*100,maxStep:time}),s=I.create(two([280,320],g));
  const r=I.advance(s,time);assert.equal(r.stop,null);conservation(r);return {errorK:Math.abs(r.nodes[0].temperatureK-(304-24/Math.E)),...compact(r)};
 });assert.ok(errors[1].errorK<errors[0].errorK&&errors[2].errorK<errors[1].errorK);assert.ok(errors[2].errorK<.01);
 summary.checks.push({name:'Weak/strong finite conductance refinement',conductanceKWK:g,runs:errors});
}
// Geometry and nonuniform initial-energy integrals do not depend on cell centers.
const allocations=[5,9].map(n=>{const I=createIntegrator(),s=I.create(createThermalConfig({sectionCount:n,...profiles})),r=I.record(s),a=r.metadata.allocation,g=geometry();
 for(const [key,total]of Object.entries({finEquivalents:1910,tubeMassKg:g.tubeMassKg,finMassKg:g.finMassKg,tubeCapacityKJK:g.tubeCapacityKJK,finCapacityKJK:g.finCapacityKJK,finAreaM2:g.finAreaM2,bareTubeAreaM2:g.bareTubeAreaM2}))near(sum(a.map(v=>v[key])),total,1e-11,key);
 near(sum(a.map(v=>v.initialTubeEnergyKJ)),g.tubeCapacityKJK*(302-273.15),1e-10,'Physical tube initial energy');
 near(sum(a.map(v=>v.initialFinEnergyKJ)),g.finCapacityKJK*(282-273.15),1e-10,'Physical fin initial energy');
 const linkTotals=[0,1,2].map(k=>sum(s.spec.links.filter((_,i)=>i%3===k).map(v=>v.conductanceKWK)));
 [g.airTubeConductanceKWK,g.airFinConductanceKWK,g.contactConductanceKWK].forEach((v,i)=>near(linkTotals[i],v,1e-12,'Conductance invariant'));
 assert.equal(g.activeRefrigerantConductanceKWK,0);assert.equal(s.spec.links.some(v=>v.id.includes('refrigerant')),false);
 return {sections:n,totalInitialEnergyKJ:r.totalEnergyKJ,finEquivalents:a.map(v=>v.finEquivalents),linkTotalsKWK:linkTotals};});
near(allocations[0].totalInitialEnergyKJ,allocations[1].totalInitialEnergyKJ,1e-10,'Mesh-independent physical initial energy');summary.allocation=allocations;
// Reference convention changes records only, never internal energies/error norm.
for(const n of [5,9]){
 const runs=[-1e6,273.15,1e6].map(ref=>{const I=createIntegrator({trace:true}),c=config('stepped',n);c.energyReferenceK=ref;const s=I.create(c);I.advance(s,60);return {s,r:I.record(s)};});
 for(const v of runs.slice(1)){
  assert.deepEqual(v.s.energies,runs[0].s.energies);assert.deepEqual(v.r.trace,runs[0].r.trace);assert.deepEqual(v.r.rejectionTrace,runs[0].r.rejectionTrace);assert.deepEqual(v.r.ledger,runs[0].r.ledger);
  assert.equal(v.r.rejectedSteps,runs[0].r.rejectedSteps);conservation(v.r);
 }
 summary.checks.push({name:'Exact energy-reference trajectory/timestep invariance',sections:n,referencesK:[-1e6,273.15,1e6],acceptedSteps:runs[0].r.acceptedSteps,rejectedSteps:runs[0].r.rejectedSteps});
}
// trial and invalid boundary edits are pure/atomic, including a mixed valid+invalid patch.
{
 const I=createIntegrator(),s=I.create(config('reservoir',5)),before=JSON.stringify(s);I.trial(s,.1);assert.equal(JSON.stringify(s),before);
 assert.throws(()=>I.update(s,{reservoirs:{air:300},conductancesKWK:{missing:1}}));assert.equal(JSON.stringify(s),before);
 I.advance(s,1);const energy=[...s.energies],ledger=JSON.stringify(s.ledger),time=s.seconds;I.update(s,{reservoirs:{air:280}});
 assert.deepEqual(s.energies,energy);assert.equal(JSON.stringify(s.ledger),ledger);assert.equal(s.seconds,time);
 const heated=I.create({nodes:[{id:'air',capacityKJK:4.308,initialK:399.9}],loadsKW:{air:1}}),heatedBefore=JSON.stringify(heated);
 assert.throws(()=>I.trial(heated,1));assert.equal(JSON.stringify(heated),heatedBefore);
 const detached=I.record(s);detached.nodes[0].temperatureK=999;assert.notEqual(I.record(s).nodes[0].temperatureK,999);
 summary.checks.push({name:'Pure trials and atomic boundary edits',passed:true});
}
function physical(s){return JSON.stringify({energies:s.energies,seconds:s.seconds,ledger:s.ledger,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex});}
for(const kind of ['accuracy','solver','domain']){
 const opts=kind==='accuracy'?{maxStep:10,minStep:9}:kind==='solver'?{maxStep:10,maxAttempts:1}:{maxStep:1,minStep:.9};
 const I=createIntegrator(opts),s=I.create(kind==='domain'?{nodes:[{id:'air',capacityKJK:4.308,initialK:399.9}],loadsKW:{air:1}}:two());
 if(kind!=='domain'){I.advance(s,.001);I.update(s,{loadsKW:{a:0}});}
 const before=physical(s);I.advance(s,60);assert.equal(s.stop.kind,kind);assert.equal(physical(s),before);
 const stopped=JSON.stringify(s);I.advance(s,1);assert.equal(JSON.stringify(s),stopped);assert.throws(()=>I.update(s,{loadsKW:{air:0}}));assert.equal(JSON.stringify(s),stopped);conservation(I.record(s));
 summary.checks.push({name:'Complete rollback/frozen stop',kind,evidence:s.stop});
}
// Boundary landing errors must refine against independent expm/root and exact air solution.
summary.domain=[];
for(const n of [5,9]){
 const I=createIntegrator(),s=I.create(createThermalConfig({sectionCount:n,airLoadKW:1}));const r=I.advance(s,2000);
 assert.equal(r.stop.kind,'domain');assert.equal(r.stop.evidence.confirmed,true);conservation(r);
 near(r.seconds,reference.connectedDomainSeconds,.001,'Connected domain clock');assert.ok(r.nodes.every(v=>v.temperatureK<=400&&v.temperatureK>=200));
 summary.domain.push({sections:n,independentDomainSeconds:reference.connectedDomainSeconds,errorSeconds:r.seconds-reference.connectedDomainSeconds,...compact(r)});
}
for(const load of [1,-1]){
 const start=load>0?293.15:273.15,target=load>0?400:200,exact=(target-start)*4.308/load;
 const I=createIntegrator(),s=I.create({nodes:[{id:'air',capacityKJK:4.308,initialK:start}],loadsKW:{air:load}}),r=I.advance(s,exact+2);
 assert.equal(r.stop.kind,'domain');near(r.seconds,exact,1e-7,'Exact isolated-air domain clock');conservation(r);
 const expected=load*(r.seconds);near(r.energyChangeKJ,expected,1e-7,'Exact isolated-air input');
 summary.domain.push({name:'Isolated air',loadKW:load,exactSeconds:exact,errorSeconds:r.seconds-exact,...compact(r)});
}
// Reject unsupported physics, invalid topology/capacity, profiles, and schedules.
for(const action of [()=>createThermalConfig({sectionCount:17}),()=>createThermalConfig({geometry:{air:{cpKJKgK:.7}}}),()=>createThermalConfig({tubeProfileK:[{left:0,right:.9,temperatureK:280}]}),()=>createThermalConfig({airReservoirK:290,airLoadKW:1}),()=>createIntegrator().create({nodes:[{id:'a',capacityKJK:0,initialK:280}]}),()=>createIntegrator().create({nodes:[{id:'a',capacityKJK:1,initialK:280}],schedule:[{seconds:1,patch:{loadsKW:{missing:1}}}]}),()=>createIntegrator().create({nodes:[{id:'a',capacityKJK:1,initialK:280}],ventilation:1}),()=>createIntegrator({relativeTolerance:0}),()=>createIntegrator().create({nodes:[{id:'a',capacityKJK:1,initialK:280}],domainK:[200,500]})])assert.throws(action);
summary.checks.push({name:'Configuration/domain/scope guards',passed:true});
summary.passed=true;
const output=process.argv[2];if(output)fs.writeFileSync(output,JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({passed:true,cases:summary.cases.length,checks:summary.checks.length,worstCombinedResidualKJ:summary.worstCombinedResidualKJ,worstNodeResidualKJ:summary.worstNodeResidualKJ,domain:summary.domain.map(v=>({sections:v.sections,name:v.name,errorSeconds:v.errorSeconds}))}));
