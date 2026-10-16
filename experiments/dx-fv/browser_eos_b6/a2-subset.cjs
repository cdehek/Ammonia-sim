'use strict';
// Shared Node/browser scientific integration harness. Injection wraps the real
// Newton entry, but delegates to real Newton and real property calls otherwise.
function runA2({sources,controlSources,engine,tableEngine,realFailure,historicalFailure=realFailure,onProgress=null}){
 const ok=(v,m)=>{if(!v)throw Error(m||'assertion failed');};
 const equal=(a,b,m)=>ok(JSON.stringify(a)===JSON.stringify(b),m||'exact comparison failed');
 const accepted=s=>JSON.stringify({spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,
  ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
 function load(src,onNewton=null,commitFault=null){const cache={};function require(name){const k=name.replace(/^\.\//,'');if(cache[k])return cache[k].exports;
  const m={exports:{}};cache[k]=m;ok(src[k],'unexpected import '+k);new Function('module','exports','require',src[k])(m,m.exports,require);
  if(k==='coupled-implicit.cjs'&&onNewton){const f=m.exports.coupledNewton;m.exports.coupledNewton=(...a)=>onNewton(f,a);}
  if(k==='time-control.cjs'&&commitFault){const f=m.exports.crossings;m.exports.crossings=(...a)=>commitFault(f,a);}return m.exports;}
  const factory=require('./coupled-model.cjs').createCoupledModel;factory.testNewton=require('./coupled-implicit.cjs').coupledNewton;factory.testThermo=require('./thermodynamics.cjs').createThermodynamics;return factory;}
 const F=load(sources),C=load(controlSources),rows=[];
 const append=rows.push.bind(rows);rows.push=(...items)=>{const n=append(...items);if(onProgress)onProgress(rows);return n;};
 function scientific(r){
  for(const [k,v]of Object.entries({mass:r.massResidualKg,fluid:r.refrigerantEnergyResidualKJ,thermal:r.thermalEnergyResidualKJ,combined:r.combinedEnergyResidualKJ}))ok(Math.abs(v)<(k==='mass'?1e-8:1e-6),k+' conservation');
  r.sectionResiduals.forEach(v=>{ok(Math.abs(v.massKg)<1e-8);ok(Math.abs(v.energyKJ)<1e-6);});r.nodes.forEach(v=>ok(Math.abs(v.residualKJ)<1e-6));
  // Independent signed thermal budget, identical accepted test arithmetic.
  const b=Array(11).fill(0);b[10]=r.ledger.airLoadKJ;
  for(let i=0;i<5;i++){const [at,af,ft]=r.ledger.thermalLinksKJ.slice(3*i,3*i+3),tr=r.ledger.tubeRefrigerantKJ[i];b[10]-=at+af;b[2*i]+=at+ft-tr;b[2*i+1]+=af-ft;}
  r.nodes.forEach((n,i)=>ok(Math.abs(n.energyChangeKJ-b[i])<=1e-6,'independent thermal budget'));
  ok(r.lastResidual===null||r.lastResidual<=1e-11);ok(r.lastTimeError===null||r.lastTimeError<=1);return r;
 }
 try{
 let lineSearchFailure;
 // Supported success with real properties and original nonzero exchange.
 {
  const m=F(engine,{trace:true,timestepGrowth:'failure-aware'}),c=C(engine,{trace:true,timestepGrowth:'failure-aware'}),s=m.create(),t=c.create();
  const start=performance.now(),r=scientific(m.advance(s,.001)),candidateMS=performance.now()-start;
  const q0=performance.now(),q=scientific(c.advance(t,.001)),controlMS=performance.now()-q0;
  ok(!r.stop&&!q.stop);equal(s.cells,t.cells);equal(s.energies,t.energies);equal(s.ledger,t.ledger);equal(s.events,t.events);
  equal(r.settings,q.settings);rows.push({scenario:'A-supported',candidateMS,controlMS,exactAcceptedMatch:true,record:r});
 }
 // Original floor / attempts are never overridden. Fail real Newton property
 // evaluations; directional recovery fails separately from accepted recovery.
 for(const kind of ['real-browser-boundary'])for(const persistent of [false,true]){
  let stage=false,armed=false,remaining=persistent?Infinity:2,trialFailures=0,acceptedKeys=new Set();
  const fresh=()=>{
   if(kind==='real-browser-boundary')return realFailure();
   if(kind==='line-search-wrapped')return Object.assign(Error(lineSearchFailure.message),{faultKind:'solver',nonlinearResidual:lineSearchFailure.nonlinearResidual,propertyCause:JSON.parse(JSON.stringify(lineSearchFailure.propertyCause))});
   if(kind==='untyped-domain')return Object.assign(Error('Legacy property domain failure'),{faultKind:'domain'});
   const reason=kind==='unsupported'?'explicit-unsupported-input':kind==='boundary'?'boundary-unresolved':'inverse-recovery-failure';
   return Object.assign(Error('Injected property domain failure: '+reason),{faultKind:kind==='unsupported'?'domain':'solver',evidence:{propertyFailure:{schemaVersion:'C1/1',
    operation:kind==='unsupported'?'ph':'stateMVU',reason,physicalTrajectoryExit:'unproved',rawRecovery:kind==='boundary'?'returned':'failed'}}});
  };
  const e={...engine,ph(...a){if(armed&&stage&&remaining>0){remaining--;trialFailures++;throw fresh();}return engine.ph(...a);},
   stateMVU(...a){if(armed&&persistent&&!acceptedKeys.has(JSON.stringify(a.slice(0,3))))throw fresh();return engine.stateMVU(...a);}};
  const I=load(sources,(fn,a)=>{stage=true;try{return fn(...a);}finally{stage=false;}}),attempts=[];
  let snapshot;const m=I(e,{trace:true,timestepGrowth:'failure-aware'},a=>{attempts.push(a);if(armed&&a.failure)equal(accepted(s),snapshot,'rollback at every rejected trial');}),s=m.create();
  // Nonempty accepted ledger and boundary history precede the rejected work.
  m.advance(s,.0001);m.update(s,{airLoadKW:1.5});s.nextStepSeconds=.001;
  acceptedKeys=new Set(s.cells.map(c=>JSON.stringify([c.massKg,c.volumeM3,c.internalEnergyKJ])));
  snapshot=accepted(s);const identity=s.cells,thermalIdentity=s.energies,ledgerIdentity=s.ledger,nextStep=s.nextStepSeconds;
  attempts.length=0;armed=true;const begin=performance.now(),r=scientific(m.advance(s,.001)),elapsedMS=performance.now()-begin;
  const failures=attempts.filter(a=>a.failure);ok(failures.length>=2,'property failure trials');
  for(let i=1;i<failures.length;i++)ok(failures[i].trialSeconds===failures[i-1].trialSeconds/2,'original halving');
  ok(!s.growthHistory.nonlinearFailures,'property error must not invent Newton growth learning');
  if(persistent){ok(r.stop?.kind==='solver','unproved failure must stop numerically');ok(!r.stop.evidence.confirmed);equal(accepted(s),snapshot,'exact accepted rollback');
   ok(s.cells===identity&&s.energies===thermalIdentity&&s.ledger===ledgerIdentity,'accepted object identity');ok(s.nextStepSeconds===nextStep,'proposal unchanged on failed advance');
   ok(r.stop.attemptedStepSeconds/2<1e-9,'original floor exhausted');
   const frozen=JSON.stringify(s);m.advance(s,.001);equal(JSON.stringify(s),frozen,'retained stop freeze');let refused=false;try{m.update(s,{airLoadKW:0});}catch(e){refused=true;}ok(refused);equal(JSON.stringify(s),frozen);
  }else{ok(!r.stop);ok(s.seconds===.0011);}
  rows.push({scenario:kind,persistent,elapsedMS,trialFailures,everyRejectedTrialRollback:true,acceptedRollback:persistent?accepted(s)===snapshot:null,identityPreserved:persistent?s.cells===identity:null,
   floor:m.settings.minStep,attempts:failures.map(a=>({trialSeconds:a.trialSeconds,failure:a.failure})),record:r});
 }
 // Genuine independently rechecked physical-domain protection, both limits.
 for(const limit of [200,400]){
  const config={sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:0}};
  const m=F(engine,{trace:true}),c=C(engine,{trace:true}),s=m.create(config),t=c.create(config);
  m.advance(s,.0001);c.advance(t,.0001);m.update(s,{airLoadKW:limit===400?1:-1});c.update(t,{airLoadKW:limit===400?1:-1});
  const before=accepted(s),r=scientific(m.advance(s,.001)),q=scientific(c.advance(t,.001));
  ok(r.stop?.kind==='domain'&&r.stop.evidence.confirmed);ok(r.stop.evidence.confirmation==='exact-boundary-outward-direction');
  equal(accepted(s),before);equal(s.cells,t.cells);equal(s.energies,t.energies);equal(s.ledger,t.ledger);
  rows.push({scenario:'D-physical-thermal-exit',limit,acceptedRollback:true,controlStop:q.stop,candidateStop:r.stop});
 }
 return {passed:true,rows,fullA2Qualification:false};
 }catch(error){error.a2Partial={rows};throw error;}
}
module.exports={runA2};
