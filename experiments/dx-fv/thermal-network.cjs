'use strict';
// Stage 1 only: constant-capacity sensible thermal nodes; no refrigerant imports.
const {solveLinear}=require('./implicit.cjs');
const {factor}=require('./time-control.cjs');
const ANCHOR_K=273.15;
const clone=x=>JSON.parse(JSON.stringify(x));
const sum=a=>a.reduce((x,y)=>x+y,0);
const finite=(x,label)=>{if(!Number.isFinite(x))throw Error(`Finite ${label} required.`);return x;};
const positive=(x,label)=>{finite(x,label);if(x<=0)throw Error(`Positive ${label} required.`);return x;};
const map=(value,label)=>{if(!value||typeof value!=='object'||Array.isArray(value))throw Error(`Object ${label} required.`);};
function keys(value,allowed,label){
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).some(k=>!allowed.includes(k)))throw Error(`Invalid ${label} fields.`);
}
function normalize(config){
 keys(config,['nodes','links','reservoirs','loadsKW','schedule','energyReferenceK','domainK','metadata'],'configuration');
 const c=clone(config);
 c.domainK=c.domainK||[200,400];c.energyReferenceK=c.energyReferenceK??ANCHOR_K;
 finite(c.energyReferenceK,'energy reference');
 if(!Array.isArray(c.domainK)||c.domainK.length!==2||c.domainK.some(v=>!Number.isFinite(v))||c.domainK[0]<200||c.domainK[1]>400||c.domainK[1]<=c.domainK[0])throw Error('Domain must lie within the declared 200–400 K constant-property range.');
 if(!Array.isArray(c.nodes)||!c.nodes.length||c.nodes.length>19)throw Error('One to nineteen standalone thermal nodes required.');
 const ids=new Set();
 for(const n of c.nodes){
  keys(n,['id','capacityKJK','initialK'],'node');
  if(typeof n.id!=='string'||!n.id.length||ids.has(n.id))throw Error('Unique node IDs required.');ids.add(n.id);
  positive(n.capacityKJK,'capacity');finite(n.initialK,'initial temperature');
  if(n.initialK<c.domainK[0]||n.initialK>c.domainK[1])throw Error('Initial temperature outside supported domain.');
 }
 c.reservoirs=c.reservoirs||{};c.loadsKW=c.loadsKW||{};c.links=c.links||[];c.schedule=c.schedule||[];
 map(c.reservoirs,'reservoirs');map(c.loadsKW,'loads');
 if(!Array.isArray(c.links)||!Array.isArray(c.schedule))throw Error('Array links/schedule required.');
 for(const [id,t]of Object.entries(c.reservoirs)){
  if(ids.has(id)||!id.length)throw Error('Reservoir IDs must be distinct from dynamic nodes.');
  finite(t,'reservoir temperature');if(t<c.domainK[0]||t>c.domainK[1])throw Error('Unsupported reservoir temperature.');
 }
 const endpoints=new Set([...ids,...Object.keys(c.reservoirs)]),linkIds=new Set();
 for(const l of c.links){
  keys(l,['id','from','to','conductanceKWK'],'link');
  if(typeof l.id!=='string'||!l.id.length||linkIds.has(l.id)||!endpoints.has(l.from)||!endpoints.has(l.to)||l.from===l.to||(!ids.has(l.from)&&!ids.has(l.to)))throw Error('Invalid thermal link.');
  linkIds.add(l.id);positive(l.conductanceKWK,'active conductance');
 }
 for(const [id,q]of Object.entries(c.loadsKW)){if(!ids.has(id))throw Error('Loads require dynamic nodes.');finite(q,'external load');}
 let previous=0,probe=c;
 for(const event of c.schedule){
  keys(event,['seconds','patch'],'scheduled boundary');positive(event.seconds,'scheduled time');
  if(event.seconds<=previous)throw Error('Schedule must be strictly increasing after zero.');previous=event.seconds;
  probe=boundaryPatch(probe,event.patch);
 }
 return c;
}
function boundaryPatch(spec,patch){
 keys(patch,['loadsKW','reservoirs','conductancesKWK'],'boundary patch');
 for(const k of ['loadsKW','reservoirs','conductancesKWK'])if(Object.hasOwn(patch,k))map(patch[k],k);
 const next=clone(spec),nodeIds=new Set(next.nodes.map(n=>n.id));
 for(const [id,q]of Object.entries(patch.loadsKW||{})){if(!nodeIds.has(id))throw Error('Unknown load node.');next.loadsKW[id]=finite(q,'load');}
 for(const [id,t]of Object.entries(patch.reservoirs||{})){
  if(!Object.hasOwn(next.reservoirs,id))throw Error('Unknown reservoir.');finite(t,'reservoir temperature');
  if(t<next.domainK[0]||t>next.domainK[1])throw Error('Unsupported reservoir temperature.');next.reservoirs[id]=t;
 }
 for(const [id,g]of Object.entries(patch.conductancesKWK||{})){
  const l=next.links.find(v=>v.id===id);if(!l)throw Error('Unknown conductance.');l.conductanceKWK=positive(g,'conductance');
 }
 return next;
}
function createIntegrator(options={}){
 keys(options,['method','adaptive','maxStep','minStep','relativeTolerance','temperatureAbsoluteK','temperatureScaleK','linearResidualK','maxAttempts','trace'],'numerical settings');
 const settings={method:'tr-bdf2',adaptive:true,maxStep:.5,minStep:1e-9,relativeTolerance:1e-6,temperatureAbsoluteK:1e-4,temperatureScaleK:50,linearResidualK:1e-9,maxAttempts:100000,trace:false,...options};
 if(!['tr-bdf2','backward-euler'].includes(settings.method)||typeof settings.adaptive!=='boolean'||typeof settings.trace!=='boolean')throw Error('Invalid method/mode.');
 for(const k of ['maxStep','minStep','relativeTolerance','temperatureAbsoluteK','temperatureScaleK','linearResidualK'])positive(settings[k],k);
 if(settings.maxStep<settings.minStep||!Number.isInteger(settings.maxAttempts)||settings.maxAttempts<1)throw Error('Invalid step/attempt limits.');
 const order=settings.method==='tr-bdf2'?2:1;
 function create(config){
  const spec=normalize(config),energies=spec.nodes.map(n=>n.capacityKJK*(n.initialK-ANCHOR_K));
  energies.forEach(e=>finite(e,'initial energy'));
  return {model:'standalone-tube-fin-air-stage1',spec,energies,initialEnergies:[...energies],seconds:0,scheduleIndex:0,
   ledger:{nodesKJ:energies.map(()=>0),loadsKJ:energies.map(()=>0),linksKJ:spec.links.map(()=>0),reservoirsKJ:Object.fromEntries(Object.keys(spec.reservoirs).map(k=>[k,0])),externalKJ:0},
   nextStepSeconds:settings.maxStep,acceptedSteps:0,rejectedSteps:0,accuracyRejectedSteps:0,domainRejectedSteps:0,attemptedLinearSolves:0,attemptedFluxEvaluations:0,
   minAcceptedStepSeconds:null,maxAcceptedStepSeconds:0,lastTimeError:null,lastResidualK:null,boundaryEvents:[],trace:[],rejectionTrace:[],stop:null};
 }
 function temperatures(s,energy){return energy.map((e,i)=>ANCHOR_K+e/s.spec.nodes[i].capacityKJK);}
 function recover(s,energy,stage){
  const t=temperatures(s,energy),[lo,hi]=s.spec.domainK;
  const i=t.findIndex(v=>!Number.isFinite(v)||v<lo||v>hi);
  if(i>=0)throw Object.assign(Error('Thermal energy recovery outside supported temperature domain.'),{kind:'domain',evidence:{stage,node:s.spec.nodes[i].id,temperatureK:t[i],domainK:[lo,hi]}});
  return t;
 }
 function evaluate(s,energy){
  const t=temperatures(s,energy),indices=new Map(s.spec.nodes.map((n,i)=>[n.id,i]));
  const temp=id=>indices.has(id)?t[indices.get(id)]:s.spec.reservoirs[id];
  const loads=s.spec.nodes.map(n=>s.spec.loadsKW[n.id]||0),rates=[...loads];
  const links=s.spec.links.map(l=>{
   const q=l.conductanceKWK*(temp(l.from)-temp(l.to));
   if(indices.has(l.from))rates[indices.get(l.from)]-=q;
   if(indices.has(l.to))rates[indices.get(l.to)]+=q;
   return q;
  });return {rates,links,loads};
 }
 function jacobian(s){
  const n=s.energies.length,a=Array.from({length:n},()=>Array(n).fill(0)),ix=new Map(s.spec.nodes.map((v,i)=>[v.id,i]));
  for(const l of s.spec.links){
   const f=ix.get(l.from),t=ix.get(l.to),g=l.conductanceKWK;
   if(f!==undefined){a[f][f]-=g/s.spec.nodes[f].capacityKJK;if(t!==undefined)a[f][t]+=g/s.spec.nodes[t].capacityKJK;}
   if(t!==undefined){a[t][t]-=g/s.spec.nodes[t].capacityKJK;if(f!==undefined)a[t][f]+=g/s.spec.nodes[f].capacityKJK;}
  }return a;
 }
 function solve(s,a,rhs,weight,work){
  work.solves++;const matrix=a.map((row,i)=>row.map((v,j)=>(i===j?1:0)-weight*v));
  const delta=solveLinear(matrix,rhs);
  const residual=Math.max(...matrix.map((row,i)=>Math.abs(sum(row.map((v,j)=>v*delta[j]))-rhs[i])/s.spec.nodes[i].capacityKJK));
  if(!Number.isFinite(residual)||residual>settings.linearResidualK)throw Object.assign(Error('Implicit linear residual exceeds budget.'),{kind:'solver',evidence:{residualK:residual}});
  return {delta,residual};
 }
 function trial(s,dt,work={solves:0,evaluations:0}){
  positive(dt,'trial interval');recover(s,s.energies,'initial');
  const a=jacobian(s),f0=evaluate(s,s.energies);work.evaluations++;
  let terms,result;
  if(order===1){
   result=solve(s,a,f0.rates.map(v=>dt*v),dt,work);
   const energies=s.energies.map((v,i)=>v+result.delta[i]);recover(s,energies,'backward-euler');
   const end=evaluate(s,energies);work.evaluations++;terms=[[1,end]];
  }else{
   const gamma=2-Math.sqrt(2),wa=1/(2*(2-gamma)),wb=(1-gamma)/(2-gamma);
   const first=solve(s,a,f0.rates.map(v=>gamma*dt*v),gamma*dt/2,work);
   const stage=s.energies.map((v,i)=>v+first.delta[i]);recover(s,stage,'trapezoidal-stage');
   const fg=evaluate(s,stage);work.evaluations++;
   result=solve(s,a,f0.rates.map((v,i)=>dt*((wa+wb)*v+wa*fg.rates[i])),wb*dt,work);
   result.residual=Math.max(result.residual,first.residual);
   terms=[[wa,f0],[wa,fg]];
  }
  const energies=s.energies.map((v,i)=>v+result.delta[i]);recover(s,energies,'endpoint');
  if(order===2){const end=evaluate(s,energies);work.evaluations++;terms.push([(1-(2-Math.sqrt(2)))/(2-(2-Math.sqrt(2))),end]);}
  const integrate=key=>terms[0][1][key].map((_,i)=>dt*sum(terms.map(([w,f])=>w*f[key][i])));
  return {energies,linksKJ:integrate('links'),loadsKJ:integrate('loads'),residualK:result.residual};
 }
 function commit(s,t,dt){
  const ix=new Map(s.spec.nodes.map((n,i)=>[n.id,i]));
  const node=[...t.loadsKJ];
  t.loadsKJ.forEach((q,i)=>{s.ledger.loadsKJ[i]+=q;s.ledger.externalKJ+=q;});
  t.linksKJ.forEach((q,i)=>{
   const l=s.spec.links[i];s.ledger.linksKJ[i]+=q;
   if(ix.has(l.from))node[ix.get(l.from)]-=q;else{s.ledger.reservoirsKJ[l.from]+=q;s.ledger.externalKJ+=q;}
   if(ix.has(l.to))node[ix.get(l.to)]+=q;else{s.ledger.reservoirsKJ[l.to]-=q;s.ledger.externalKJ-=q;}
  });node.forEach((q,i)=>s.ledger.nodesKJ[i]+=q);
  s.energies=t.energies;s.seconds+=dt;s.acceptedSteps++;s.lastResidualK=t.residualK;
  s.minAcceptedStepSeconds=s.minAcceptedStepSeconds===null?dt:Math.min(s.minAcceptedStepSeconds,dt);s.maxAcceptedStepSeconds=Math.max(s.maxAcceptedStepSeconds,dt);
 }
 function stop(s,kind,message,dt,evidence){s.stop={kind,message,seconds:s.seconds,attemptedStepSeconds:dt,evidence:clone(evidence||{})};}
 function applyBoundary(s,patch,scheduled=false){
  const next=boundaryPatch(s.spec,patch); // Validate the complete patch before any mutation.
  const before={loadsKW:clone(s.spec.loadsKW),reservoirs:clone(s.spec.reservoirs)};
  s.spec=next;s.nextStepSeconds=settings.maxStep;
  s.boundaryEvents.push({seconds:s.seconds,scheduled,patch:clone(patch),before});
 }
 function advance(s,duration){
  positive(duration,'advance duration');if(s.stop)return record(s);
  const target=s.seconds+duration;finite(target,'target time');if(target<=s.seconds)throw Error('Duration is below clock resolution.');
  let attempts=0,dt=s.nextStepSeconds;
  while(s.seconds<target){
   const event=s.spec.schedule[s.scheduleIndex];
   if(event&&event.seconds===s.seconds){applyBoundary(s,event.patch,true);s.scheduleIndex++;dt=s.nextStepSeconds;continue;}
   const boundary=Math.min(target,event?.seconds??Infinity),remaining=boundary-s.seconds;
   dt=Math.min(dt,remaining);
   if(++attempts>settings.maxAttempts){stop(s,'solver','Thermal attempt budget exhausted.',dt,{maxAttempts:settings.maxAttempts});break;}
   const work={solves:0,evaluations:0};let pieces,error=0;
   try{
    const full=trial(s,dt,work);pieces=[[full,dt]];
    if(settings.adaptive){
     const half=trial(s,dt/2,work),fine=trial({...s,energies:half.energies},dt/2,work);
     error=Math.max(...fine.energies.map((e,i)=>Math.abs(e-full.energies[i])/(2**order-1)/s.spec.nodes[i].capacityKJK/(settings.temperatureAbsoluteK+settings.relativeTolerance*settings.temperatureScaleK)));
     if(!Number.isFinite(error))throw Object.assign(Error('Nonfinite temporal error.'),{kind:'solver'});
     pieces=[[half,dt/2],[fine,dt/2]];
    }
   }catch(cause){
    s.rejectedSteps++;if(cause.kind==='domain')s.domainRejectedSteps++;
    if(settings.trace)s.rejectionTrace.push({seconds:s.seconds,trialSeconds:dt,kind:cause.kind||'solver'});
    const next=dt/2;
    if(next<settings.minStep||s.seconds+next===s.seconds){
     const t=temperatures(s,s.energies),rates=evaluate(s,s.energies).rates;
     const directional=t.map((v,i)=>({node:s.spec.nodes[i].id,temperatureK:v,rateKS:rates[i]/s.spec.nodes[i].capacityKJK}));
     const confirmed=cause.kind==='domain'&&directional.some(v=>(v.rateKS>0&&v.temperatureK+dt*v.rateKS>s.spec.domainK[1])||(v.rateKS<0&&v.temperatureK+dt*v.rateKS<s.spec.domainK[0]));
     stop(s,confirmed?'domain':'solver',cause.message,dt,{originalCause:cause.kind||'solver',trial:cause.evidence||{},directional,confirmed});break;
    }
    dt=next;continue;
   }finally{s.attemptedLinearSolves+=work.solves;s.attemptedFluxEvaluations+=work.evaluations;}
   if(error>1){
    s.rejectedSteps++;s.accuracyRejectedSteps++;
    if(settings.trace)s.rejectionTrace.push({seconds:s.seconds,trialSeconds:dt,kind:'accuracy',error});
    const next=dt*factor(error,order,false);
    if(next<settings.minStep||s.seconds+next===s.seconds){stop(s,'accuracy','Thermal error tolerance cannot be met above minimum step.',dt,{normalizedError:error});break;}
    dt=next;continue;
   }
   const start=s.seconds;
   // Both accepted halves have already recovered successfully: commit atomically.
   for(const [piece,h]of pieces)commit(s,piece,h);
   s.seconds=dt===remaining?boundary:start+dt;s.lastTimeError=error;
   if(settings.trace)s.trace.push({startSeconds:start,endSeconds:s.seconds,trialSeconds:dt,error});
   dt=Math.min(settings.maxStep,settings.adaptive?dt*factor(error,order,true):settings.maxStep);s.nextStepSeconds=dt;
  }
  // A scheduled transition at the requested endpoint is visible immediately.
  if(!s.stop){const event=s.spec.schedule[s.scheduleIndex];if(event&&event.seconds===s.seconds){applyBoundary(s,event.patch,true);s.scheduleIndex++;}}
  return record(s);
 }
 function update(s,patch){if(s.stop)throw Error('Stopped thermal state is frozen.');applyBoundary(s,patch);return record(s);}
 function record(s){
  const t=recover(s,s.energies,'record'),offset=ANCHOR_K-s.spec.energyReferenceK;
  const residuals=s.energies.map((e,i)=>e-s.initialEnergies[i]-s.ledger.nodesKJ[i]);
  return clone({model:s.model,seconds:s.seconds,nodes:s.spec.nodes.map((n,i)=>({id:n.id,capacityKJK:n.capacityKJK,temperatureK:t[i],energyKJ:s.energies[i]+n.capacityKJK*offset,energyChangeKJ:s.energies[i]-s.initialEnergies[i],residualKJ:residuals[i]})),
   totalEnergyKJ:sum(s.energies.map((e,i)=>e+s.spec.nodes[i].capacityKJK*offset)),energyChangeKJ:sum(s.energies.map((e,i)=>e-s.initialEnergies[i])),energyResidualKJ:sum(s.energies.map((e,i)=>e-s.initialEnergies[i]))-s.ledger.externalKJ,
   energyScaleKJ:sum(s.spec.nodes.map(n=>n.capacityKJK*settings.temperatureScaleK)),ledger:s.ledger,fluxesKW:evaluate(s,s.energies).links,boundaries:{loadsKW:s.spec.loadsKW,reservoirs:s.spec.reservoirs},
   energyReferenceK:s.spec.energyReferenceK,computationalEnergyAnchorK:ANCHOR_K,numerics:settings,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps,accuracyRejectedSteps:s.accuracyRejectedSteps,domainRejectedSteps:s.domainRejectedSteps,
   attemptedLinearSolves:s.attemptedLinearSolves,attemptedFluxEvaluations:s.attemptedFluxEvaluations,minAcceptedStepSeconds:s.minAcceptedStepSeconds,maxAcceptedStepSeconds:s.maxAcceptedStepSeconds,lastTimeError:s.lastTimeError,lastResidualK:s.lastResidualK,
   boundaryEvents:s.boundaryEvents,trace:s.trace,rejectionTrace:s.rejectionTrace,stop:s.stop,metadata:s.spec.metadata||{}});
 }
 return {create,advance,update,record,trial,settings};
}
module.exports={createIntegrator,normalize,ANCHOR_K};
