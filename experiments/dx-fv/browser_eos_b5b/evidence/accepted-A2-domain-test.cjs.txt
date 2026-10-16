'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createCoupledModel}=require('./coupled-model.cjs'),{candidateFactory}=require('./coupled-candidate.cjs');
const {fixture}=require('./coupled-fixtures.cjs');
const candidate=candidateFactory(),report={stage:'2A-R',runtime:process.version,candidate:candidate.commit,cases:[],solverFailures:[]};
const accepted=s=>JSON.stringify({spec:s.spec,cells:s.cells,energies:s.energies,initialCells:s.initialCells,initialEnergies:s.initialEnergies,seconds:s.seconds,
  ledger:s.ledger,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
try {
 for(const minStep of [1e-9,1e-5,.5])for(const limit of [200,400])for(const direction of ['outward','inward','zero']){
  const load=direction==='zero'?0:(limit===400?1:-1)*(direction==='outward'?1:-1);
  const config={sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:load},
    schedule:[{seconds:2,patch:{airLoadKW:0}}]};
  const options={minStep,maxStep:.5,trace:true},beforeModel=candidate.create(engine,options),afterModel=createCoupledModel(engine,options);
  const a=beforeModel.create(config),b=afterModel.create(config),snapshot=accepted(b);
  const previous=beforeModel.advance(a,.5),current=afterModel.advance(b,.5);
  if(direction==='outward'){
   assert.equal(current.stop?.kind,'domain');assert.equal(current.stop.evidence.confirmed,true);
   assert.equal(current.stop.evidence.confirmation,'exact-boundary-outward-direction');
   assert.equal(accepted(b),snapshot);assert.equal(b.acceptedSteps,0);
   const frozen=JSON.stringify(b);afterModel.advance(b,1);assert.equal(JSON.stringify(b),frozen);
   assert.throws(()=>afterModel.update(b,{airLoadKW:0}));assert.equal(JSON.stringify(b),frozen);
   assert.equal(previous.stop?.kind,minStep===1e-9?'domain':'solver');
  }else{
   assert.equal(current.stop,null);assert.equal(previous.stop,null);assert.equal(b.seconds,.5);
   assert.deepEqual(b.cells,a.cells);assert.deepEqual(b.energies,a.energies);assert.deepEqual(b.ledger,a.ledger);
   assert.deepEqual(b.events,a.events);assert.deepEqual(b.boundaryEvents,a.boundaryEvents);
   assert.ok(current.nodes.every(n=>n.temperatureK>=200&&n.temperatureK<=400));
   if(direction==='zero')assert.deepEqual(b.energies,b.initialEnergies);
  }
  assert.ok(Math.abs(current.combinedEnergyResidualKJ)<1e-6);
  assert.ok(current.nodes.every(n=>Math.abs(n.residualKJ)<1e-6));
  report.cases.push({minStep,limitK:limit,direction,airLoadKW:load,beforeStop:previous.stop,afterStop:current.stop,
    acceptedSteps:b.acceptedSteps,seconds:b.seconds,rejectedSteps:b.rejectedSteps,completeAcceptedRollback:direction==='outward'?accepted(b)===snapshot:null,
    combinedEnergyResidualKJ:current.combinedEnergyResidualKJ});
 }
 // Forced nonlinear failures and unsupported probes at a supported interior
 // accepted state must retain its nonempty clock/ledger/boundary history.
 for(const kind of ['solver','domain','false-boundary-proof'])for(const minStep of [1e-9,1e-5,.5]){
  const context=require.resolve('./coupled-implicit.cjs'),original=require.cache[context].exports.coupledNewton;
  require.cache[context].exports.coupledNewton=()=>{throw Object.assign(Error(kind==='solver'?'Injected ordinary nonlinear failure.':'Unsupported Newton probe only.'),{faultKind:kind==='solver'?'solver':'domain',...(kind==='false-boundary-proof'?{evidence:{source:'thermal',stage:'initial-direction',node:'air',temperatureK:400,rateKS:1}}:{})});};
  const modelPath=require.resolve('./coupled-model.cjs'),saved=require.cache[modelPath];delete require.cache[modelPath];
  const injected=require('./coupled-model.cjs').createCoupledModel;
  require.cache[context].exports.coupledNewton=original;require.cache[modelPath]=saved;
  const normal=createCoupledModel(engine),s=normal.create(fixture('warm'));
  normal.advance(s,.001);normal.update(s,{airLoadKW:1.5});s.nextStepSeconds=.5;
  const model=injected(engine,{minStep,maxStep:.5}),snapshot=accepted(s),r=model.advance(s,.5);
  assert.equal(r.stop.kind,'solver');assert.equal(r.stop.evidence.confirmed,false);assert.equal(accepted(s),snapshot);
  report.solverFailures.push({minStep,probeOnly:kind!=='solver',falseBoundaryProof:kind==='false-boundary-proof',stop:r.stop,acceptedRollback:true});
 }
 const normal=createCoupledModel(engine),s=normal.create(fixture('warm'));
 normal.advance(s,.001);normal.update(s,{airLoadKW:1.5});s.nextStepSeconds=.5;
 const snapshot=accepted(s),r=createCoupledModel(engine,{maxIterations:1,minStep:.5,maxStep:.5}).advance(s,.5);
 assert.equal(r.stop?.kind,'solver');assert.equal(accepted(s),snapshot);
 report.solverFailures.push({actualNewtonBudgetFailure:true,stop:r.stop,acceptedRollback:true});
 // Exercise exact outward stops after prior accepted work and boundary records.
 for(const minStep of [1e-9,1e-5,.5])for(const limit of [200,400]){
  const m=createCoupledModel(engine,{minStep,maxStep:.5}),s=m.create({sealed:true,refrigerantConductanceKWK:0,
    thermal:{tubeProfileK:limit,finProfileK:limit,airInitialK:limit,airLoadKW:0},schedule:[{seconds:2,patch:{airLoadKW:0}}]});
  m.advance(s,.01);m.update(s,{airLoadKW:limit===400?1:-1});
  const snapshot=accepted(s),r=m.advance(s,.01);
  assert.equal(r.stop?.kind,'domain');assert.equal(accepted(s),snapshot);
  report.cases.push({minStep,limitK:limit,priorAcceptedBoundaryHistory:true,stop:r.stop,completeAcceptedRollback:true});
 }
 // A tube boundary can also point outward through an approved signed G_tr
 // exchange. This is a support stress fixture, not a new operating boundary.
 for(const minStep of [1e-9,1e-5,.5]){
  const hot=engine.statePT(3.5,450-273.15),m=createCoupledModel(engine,{minStep,maxStep:.5});
  const s=m.create({sealed:true,initial:Array.from({length:5},()=>({p:hot.p,h:hot.h})),
    thermal:{tubeProfileK:400,finProfileK:400,airInitialK:400,airLoadKW:0}});
  const snapshot=accepted(s),r=m.advance(s,.5);
  assert.equal(r.stop?.kind,'domain');assert.equal(r.stop.evidence.node,'tube-0');assert.equal(accepted(s),snapshot);
  report.cases.push({minStep,limitK:400,node:'tube-0',signedRefrigerantExchange:true,stop:r.stop,completeAcceptedRollback:true});
 }
 report.passed=true;
 if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:true,boundaryCases:report.cases.length,solverChecks:report.solverFailures.length}));
}catch(error){report.passed=false;report.failure={message:error.message,stack:error.stack};if(process.argv[2])fs.writeFileSync(process.argv[2]+'.failure.json',JSON.stringify(report,null,2)+'\n');console.error(error);process.exitCode=1;}
