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
 {
  let calls=0;const work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};
  try{F.testNewton(x=>{if(++calls>=3)throw realFailure();return {residual:[x[0]-1],states:[{p:x[0],h:1100,T:0,x:null,phase:'Superheated vapor'}]};},[0],[{kind:'pressure',section:0}],{maxIterations:30,nonlinearTolerance:1e-11},work);}catch(e){lineSearchFailure=e;}
  ok(lineSearchFailure?.faultKind==='solver'&&lineSearchFailure.nonlinearResidual===1);ok(lineSearchFailure.propertyCause?.evidence.propertyFailure.reason==='boundary-unresolved');
  ok(work.diagnostics.filter(e=>e.type==='line-search'&&e.outcome==='probe-failed').every(e=>e.failure.evidence.propertyFailure));
  rows.push({scenario:'Newton-line-search-propagation',actualNonlinearResidual:lineSearchFailure.nonlinearResidual,propertyCause:lineSearchFailure.propertyCause,work});
 }
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
 for(const kind of ['numerical','boundary','real-browser-boundary','unsupported','legacy-domain-text','untyped-domain','line-search-wrapped'])for(const persistent of [false,true]){
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
 // Preserve errors thrown while preparing the second detached half-commit.
 // The original commit design must never install the already-prepared first half.
 {
  let crossings=0;const I=load(sources,null,(f,a)=>{if(++crossings===4)throw realFailure();return f(...a);});
  const m=I(engine),s=m.create({sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:273.15,finProfileK:273.15,airInitialK:273.15,airLoadKW:0}}),before=accepted(s),identity=s.cells;let error=null;
  try{m.advance(s,.0001);}catch(e){error=e;}ok(error&&crossings===4,'detached commit injection');equal(accepted(s),before);ok(s.cells===identity);
  rows.push({scenario:'second-half-detached-commit',crossings,exactAcceptedRollback:true,error:{message:error.message,evidence:error.evidence}});
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
 // Independently recheck a false thermal proof rather than trusting labels.
 {
  const I=load(sources,()=>{throw Object.assign(Error('False thermal claim'),{faultKind:'domain',evidence:{source:'thermal',stage:'initial-direction',node:'air',temperatureK:400,rateKS:1}});});
  const m=I(engine),s=m.create(),b=accepted(s),r=m.advance(s,.001);ok(r.stop.kind==='solver'&&!r.stop.evidence.confirmed);equal(accepted(s),b);
  rows.push({scenario:'false-thermal-proof',stop:r.stop,rollback:true});
 }
 // Input refusal and edit transaction, using real explicit pressure guard.
 {
  const m=F(engine),s=m.create();let e=null;try{m.create({initial:Array(5).fill({p:35.00000000000001,h:1100})});}catch(x){e=x;}ok(e?.faultKind==='domain');
  const snapshot=JSON.stringify(s);let updateError=null;try{m.update(s,{inlet:{p:35.00000000000001,h:1100}});}catch(x){updateError=x;}ok(updateError);equal(JSON.stringify(s),snapshot);
  rows.push({scenario:'E-input-and-edit',error:{message:e.message,evidence:e.evidence},updateError:{message:updateError.message,evidence:updateError.evidence},exactStatePreserved:true});
 }
 // Persistent accepted-state recovery failure must retain a solver stop even
 // if evidence gathering and final record both fail. No success-shaped record.
 {
  let armed=false;const e={...engine,stateMVU(...a){if(armed)throw realFailure();return engine.stateMVU(...a);}};
  const m=F(e,{trace:true}),s=m.create(),before=accepted(s);armed=true;let error=null;try{m.advance(s,.001);}catch(x){error=x;}
  ok(error&&error.recordFailure&&!error.recordFailure.propertyStatesReturned);ok(s.stop.kind==='solver'&&!s.stop.evidence.confirmed);equal(accepted(s),before);
  rows.push({scenario:'accepted-record-unavailable',error:{message:error.message,evidence:error.evidence,recordFailure:error.recordFailure},stop:s.stop,exactRollback:true});
 }
 // Matched historical versus C1 error/retry path, including the original
 // false refrigerant-domain proof. Real saved property errors are replayed into
 // synthetic solver lineage; this is not a simulated 35-bar plant excursion.
 {
  const pair=[];
  for(const [label,src,failure]of [['control',controlSources,historicalFailure],['candidate',sources,realFailure]]){
   let armed=false,stage=false,keys=new Set();
   const e={...engine,ph(...a){if(armed&&stage)throw failure();return engine.ph(...a);},stateMVU(...a){if(armed&&!keys.has(JSON.stringify(a.slice(0,3))))throw failure();return engine.stateMVU(...a);}};
   const I=load(src,(f,a)=>{stage=true;try{return f(...a);}finally{stage=false;}}),m=I(e,{trace:true}),s=m.create();
   keys=new Set(s.cells.map(c=>JSON.stringify([c.massKg,c.volumeM3,c.internalEnergyKJ])));const before=accepted(s);armed=true;const start=performance.now(),r=m.advance(s,.001),elapsedMS=performance.now()-start;
   equal(accepted(s),before);pair.push({label,elapsedMS,rejectedSteps:s.rejectedSteps,stop:r.stop,rollback:true});
  }
  ok(pair[1].stop.kind==='solver'&&!pair[1].stop.evidence.confirmed);equal(pair[0].rejectedSteps,pair[1].rejectedSteps);
  rows.push({scenario:'matched-real-error-retry',pair,syntheticReplayOfRealPropertyError:true});
 }
 // Independent thermal evidence remains decisive even when a property refusal
 // triggered the trial failure. The failed record returns no property state.
 {
  let armed=false;const e={...engine,stateMVU(...a){if(armed)throw realFailure();return engine.stateMVU(...a);}};
  const m=F(e),s=m.create({sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:400,finProfileK:400,airInitialK:400,airLoadKW:1}}),before=accepted(s);
  armed=true;let error;try{m.advance(s,.001);}catch(e){error=e;}ok(error?.recordFailure);ok(s.stop.kind==='domain'&&s.stop.evidence.confirmed&&s.stop.evidence.source==='thermal');equal(accepted(s),before);
  rows.push({scenario:'independent-thermal-proof-with-property-failure',stop:s.stop,rollback:true,noPropertyStateReturned:true});
 }
 const propagationPerformance=[];
 for(let round=0;round<3;round++)for(const [label,f]of [['control',C],['candidate',F]]){
  const thermo=f.testThermo({ph(){throw Object.assign(Error('Synthetic numerical property domain text'),{faultKind:'solver'});}}),start=performance.now();let count=0;
  do{try{thermo.ph(3.5,1100);}catch(e){ok(e.faultKind==='solver');count++;}}while(performance.now()-start<20&&count<10000);
  propagationPerformance.push({round,label,count,elapsedMS:performance.now()-start});
 }
 return {passed:true,rows,propagationPerformance,rollbackSemantics:'Original accepted JSON snapshot plus cell/thermal/ledger identity and nextStep equality. No controller exists in accepted dependency closure.',
  settings:F(engine).settings,tableEngineAvailable:!!tableEngine,fullA2Qualification:false};
 }catch(error){error.a2Partial={rows};throw error;}
}
module.exports={runA2};
