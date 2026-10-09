const assert=require('node:assert/strict'),P=require('../equipment-profiles'),e=require('../engine').createEngine(require('../properties.json')),m=require('../storage-engine').createStorage(e,P),T=require('../training-engine');
function load(id){const recipe=T.setup(id),s=m.create(P.DEFAULT,recipe.room,recipe.operations);if(recipe.warmup)m.advance(s,recipe.warmup);return {s,a:T.start(id,s)};}
function perturb(a,s){const d=T.EXERCISES[a.exercise];m.update(s,d.operations,d.boundary);T.injected(a,s);T.observe(a,s);}
function advance(a,s,time){m.advance(s,time);T.observe(a,s);}
const reports=[];
for(const id of Object.keys(T.EXERCISES).filter(id=>!T.EXERCISES[id].initialCapacity)){
 const {s,a}=load(id);assert(!s.fault);const unchanged=JSON.stringify({v:s.vessels,c:s.controller,T:s.T,time:s.time});T.observe(a,s);assert.equal(JSON.stringify({v:s.vessels,c:s.controller,T:s.T,time:s.time}),unchanged,'Grading is read-only');
 assert.equal(T.answer(a,1,s.time),false);assert(!a.goals[a.goals.length-1].met);T.answer(a,0,s.time);
 if(id!=='startup')perturb(a,s);
 if(id==='hot'){
  while(!s.fault)advance(a,s,10);assert.equal(a.expectedFault.message,'High discharge temperature');assert(a.goals[0].met&&a.goals[1].met);const fault=JSON.stringify(a.expectedFault);
  m.clearFault(s);T.observe(a,s);assert(!a.goals[2].met,'Clearing alone is not continuation or correction');advance(a,s,1);assert(s.fault);
  m.update(s,{compressorOn:false,valveMode:'closed'},{ambient:25});T.restored(a,s);T.observe(a,s);m.clearFault(s);advance(a,s,9);assert(!a.goals[2].met,'Require ten seconds after restoration, not the original trip');advance(a,s,1);assert.equal(JSON.stringify(a.expectedFault),fault);assert(!s.fault);
 }else{for(let i=0;i<30&&a.status==='active';i++)advance(a,s,10);assert(!s.fault,id);}
 assert.equal(a.status,'completed',id+': '+a.reason);assert(a.goals.every(g=>g.met));const r=m.record(s);assert(Math.abs(r.massResidualKg)<1e-8&&Math.abs(r.energyResidualKJ)<1e-6);const report=T.report(a,s);assert.equal(report.attempt.profile.id,'default');assert.equal(report.history.initialRoom.initial,15);assert.deepEqual(report.attempt.goals,a.goals);reports.push({id,seconds:s.time,goals:a.goals.length});
}
const {s:early,a:insufficient}=load('startup');T.answer(insufficient,0,early.time);advance(insufficient,early,10);assert.equal(insufficient.status,'active','Reflection and a transient target crossing cannot complete startup');
const {s:changed,a:invalid}=load('load');m.update(changed,{speed:.8});T.observe(invalid,changed);assert.equal(invalid.status,'interrupted');
const {s:starved,a:failed}=load('restriction');perturb(failed,starved);advance(failed,starved,60);assert.equal(failed.status,'stopped');assert(!failed.goals[2].met);
const recipe=T.setup('startup'),normal=m.create(P.DEFAULT,recipe.room,recipe.operations),observed=m.create(P.DEFAULT,recipe.room,recipe.operations),attempt=T.start('startup',observed);for(let i=0;i<20;i++){m.advance(normal,1);m.advance(observed,1);T.observe(attempt,observed);}assert.deepEqual(normal.vessels,observed.vessels);assert.deepEqual(normal.controller,observed.controller);assert.equal(normal.electricalKWh,observed.electricalKWh);
for(const chunk of [1,10]){const {s,a}=load('restriction');T.answer(a,0,s.time);perturb(a,s);for(let t=0;t<10;t+=chunk)advance(a,s,chunk);assert.equal(a.status,'completed');assert(Math.abs(a.goals[1].evidence.seconds-40)<1e-8);}
// The app grades accepted outer endpoints inside each playback request.
function guarded(a,s,seconds){m.advance(s,seconds,[],current=>{T.observe(a,current);return a.status==='active';});T.observe(a,s);}
for(const chunk of [0.25,2.5,15,60,75]){
 const {s,a}=load('restriction');T.answer(a,0,s.time);perturb(a,s);
 for(let i=0;i<100&&a.status==='active';i++)guarded(a,s,chunk);
 assert.equal(a.status,'completed','Chunk '+chunk);assert(!s.fault);assert(Math.abs(s.time-40)<1e-8);assert.equal(s.pending,0);assert(Math.abs(a.endedAt-40)<1e-8);
 const exported=T.report(a,s),snapshot=JSON.stringify(exported);m.advance(s,.1);assert(Math.abs(s.time-40.1)<1e-8,'Unused batch must not leak into later exploration');assert.equal(JSON.stringify(exported),snapshot,'Exported evidence stays frozen');
}
for(const id of ['startup','load','tuning']){
 const {s,a}=load(id);T.answer(a,0,s.time);if(id!=='startup')perturb(a,s);guarded(a,s,300);
 assert.equal(a.status,'completed',id);assert.equal(s.pending,0);assert(!s.fault);assert(Math.abs(s.time-a.endedAt)<1e-8);assert(s.time<300+a.startedAt);
}
const {s:hotBatch,a:hotAttempt}=load('hot');T.answer(hotAttempt,0,hotBatch.time);perturb(hotAttempt,hotBatch);guarded(hotAttempt,hotBatch,300);assert(hotBatch.fault&&hotAttempt.expectedFault);assert.equal(hotAttempt.status,'active');const originalHotFault=JSON.stringify(hotAttempt.expectedFault);m.update(hotBatch,{compressorOn:false,valveMode:'closed'},{ambient:25});T.restored(hotAttempt,hotBatch);T.observe(hotAttempt,hotBatch);m.clearFault(hotBatch);guarded(hotAttempt,hotBatch,300);assert.equal(hotAttempt.status,'completed');assert(Math.abs(hotBatch.time-hotAttempt.restoredAt-10)<1e-8);assert.equal(hotBatch.pending,0);assert.equal(JSON.stringify(hotAttempt.expectedFault),originalHotFault);
const {s:unanswered,a:noQuiz}=load('restriction');perturb(noQuiz,unanswered);guarded(noQuiz,unanswered,75);assert.equal(noQuiz.status,'stopped');assert(unanswered.fault,'Physical stops still win when a reflection is missing');assert(!noQuiz.goals[2].met);
const {s:edited,a:editAttempt}=load('load');m.update(edited,{speed:.8});const editTime=edited.time;guarded(editAttempt,edited,75);assert.equal(editAttempt.status,'interrupted');assert.equal(edited.time,editTime,'Incompatible accepted inputs interrupt before advancing');
const clean=m.create(P.DEFAULT,recipe.room,recipe.operations),observedOnly=m.create(P.DEFAULT,recipe.room,recipe.operations);m.advance(clean,20);m.advance(observedOnly,20,[],()=>true);assert.deepEqual(observedOnly,clean,'A read-only non-stopping observer changes no physics/history');
assert.throws(()=>m.advance(clean,1,[],true),/observer/);
assert.throws(()=>T.setup('defrost'),/Unknown/);assert.throws(()=>T.answer(insufficient,-1,early.time),/Select/);const custom=P.copy(P.DEFAULT);custom.id='custom';assert.throws(()=>T.start('startup',m.create(custom)),/Default/);
console.log(JSON.stringify({passed:true,exercises:reports,checks:'Measured objectives, correct/incorrect reflections, warmup, real disturbances, conserved balances, exact trip evidence, clearing vs continuation, wrong-control interruption, starvation failure, read-only grading, accepted-boundary completion, pending-time discard, missing reflection, frozen evidence and batching.'},null,2));
