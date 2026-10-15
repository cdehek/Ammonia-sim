'use strict';
// Trace-based qualification/statistics, separate from independent trajectory accuracy.
const assert=require('node:assert/strict'),fs=require('node:fs');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createCoupledModel}=require('./coupled-model.cjs'),{cases,fixture}=require('./coupled-fixtures.cjs');
const report={stage:'2A',runtime:process.version,cases:[]};
for(const c of cases()){
  const m=createCoupledModel(engine,{trace:true}),s=m.create(c.config);
  for(const t of c.samples){const r=m.advance(s,t-s.seconds);assert.equal(r.stop,null);}
  const r=m.record(s);assert.ok(s.trace.length>0);assert.equal(s.acceptedSteps,2*s.trace.length);
  assert.ok(s.trace.every(v=>Number.isFinite(v.error)&&v.error>=0&&v.error<=1));
  assert.ok(s.events.every(v=>v.bracketEndSeconds-v.bracketStartSeconds<=m.settings.eventStepSeconds+1e-12));
  report.cases.push({name:c.name,settings:m.settings,acceptedTrials:s.trace.length,acceptedHalfSteps:s.acceptedSteps,rejectedTrials:s.rejectedSteps,
    accuracyRejected:s.accuracyRejectedSteps,eventRejected:s.eventRejectedSteps,domainRejected:s.domainRejectedSteps,
    maximumAcceptedNormalizedError:Math.max(...s.trace.map(v=>v.error)),minAcceptedStepSeconds:s.minAcceptedStepSeconds,maxAcceptedStepSeconds:s.maxAcceptedStepSeconds,
    attemptedResidualEvaluations:s.attemptedResidualEvaluations,attemptedIterations:s.attemptedIterations,terminal:r.terminal,outlet:r.outlet});
}
const m=createCoupledModel(engine),s=m.create(fixture()),before=JSON.stringify(s);
// Validate that a valid first field cannot survive an invalid subsequent field.
assert.throws(()=>m.update(s,{inlet:{p:4.3,h:500},airLoadKW:NaN}));assert.equal(JSON.stringify(s),before);
assert.throws(()=>m.update(s,{inlet:{p:4.3,h:500},outlet:{p:100,h:1700}}));assert.equal(JSON.stringify(s),before);
report.validFirstMixedPatchRollback=true;report.passed=true;
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
