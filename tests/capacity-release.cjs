/* Stage 4 acceptance: connected demand, measured lessons and sustained dynamics. */
const assert=require('node:assert/strict'),P=require('../equipment-profiles'),C=require('../capacity-controller'),T=require('../training-engine'),H=require('../storage-history');
const e=require('../engine').createEngine(require('../properties.json')),make=n=>require('../storage-engine').createStorage(e,P,n),m=make();
const ops={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto'};
const near=(a,b,t=1e-8)=>assert(Math.abs(a-b)<t,a+' vs '+b);
function valid(model,s){const r=model.record(s);near(r.seconds,r.capacity.seconds,1e-9);assert.equal(r.capacity.pendingSeconds,0);assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);assert(r.capacity.actualSpeed===0||r.capacity.actualSpeed>=r.capacity.settings.minSpeed&&r.capacity.actualSpeed<=r.capacity.settings.maxSpeed);return r;}
function lesson(id){const recipe=T.setup(id),s=m.create(P.DEFAULT,recipe.room,recipe.operations,recipe.capacity);if(recipe.warmup)m.advance(s,recipe.warmup);assert(!s.fault);return {s,a:T.start(id,s)};}
function apply(a,s){const d=T.EXERCISES[a.exercise];m.update(s,d.operations,d.boundary,d.capacity||null);T.injected(a,s);T.observe(a,s);}
function guarded(a,s,seconds){m.advance(s,seconds,[],current=>{T.observe(a,current);return a.status==='active';});T.observe(a,s);}

// A fractional minimum-run deadline is a real accepted plant boundary, not the next UI tick.
function held(step,chunk){const model=make({maxStep:step}),s=model.create(P.DEFAULT,{}, {...ops,valveMode:'closed'},{minOn:7.525,minOff:3,startDelay:2});model.update(s,{compressorDemand:false});assert(s.capacity.running);assert.equal(s.capacity.reason,'Minimum on time');for(let t=0;t<10-1e-8;t+=chunk)model.advance(s,chunk);valid(model,s);assert(!s.fault);assert(!s.capacity.running);near(s.capacity.lastSwitch,7.525,1e-9);const event=s.history.events.find(x=>x.type==='capacity-state');near(event.seconds,7.525,1e-9);const sample=s.history.samples.find(x=>x.id===event.sampleId);assert.equal(sample.capacity.actualSpeed,0);near(sample.capacity.lastSwitchSeconds,7.525,1e-9);assert.equal(s.history.events.filter(x=>x.type==='capacity-state').length,1);return s;}
const heldBatch=held(.1,10),heldSingles=held(.1,1);assert.deepEqual(heldBatch.vessels,heldSingles.vessels);assert.deepEqual(heldBatch.capacity,heldSingles.capacity);
for(const step of [.05,.025]){const s=held(step,10);near(s.states.outlet.p,heldBatch.states.outlet.p,.001);near(s.electricalKWh,heldBatch.electricalKWh,.0001);}
// Demand cancellation requires a fresh start delay; master disable overrides the run hold.
const restart=m.create(P.DEFAULT,{}, {...ops,compressorOn:false,valveMode:'closed'},{minOff:3,startDelay:2,minOn:7.5});m.update(restart,{compressorOn:true});m.advance(restart,4);assert.equal(restart.capacity.reason,'Start delay');m.update(restart,{compressorDemand:false});m.advance(restart,1);assert(!restart.capacity.running);m.update(restart,{compressorDemand:true});m.advance(restart,2);near(restart.capacity.lastSwitch,7,1e-9);assert(restart.capacity.running);m.update(restart,{compressorDemand:false});assert(restart.capacity.running);m.update(restart,{compressorOn:false});assert(!restart.capacity.running);assert.equal(restart.capacity.speed,0);near(restart.capacity.lastSwitch,restart.time);valid(m,restart);
const initOff=m.create(P.DEFAULT,{}, {...ops,compressorDemand:false},{minOn:90});assert(!initOff.capacity.running,'No-demand initialization cannot invent a minimum-run hold');assert.equal(initOff.capacity.speed,0);
const before=JSON.stringify(restart);assert.throws(()=>m.update(restart,{compressorDemand:'false'},{gain:20}));assert.equal(JSON.stringify(restart),before);
const legacy=m.create(P.DEFAULT,{},ops);const oldLegacy=JSON.stringify(legacy);assert.throws(()=>m.update(legacy,{compressorDemand:false}),/managed/);assert.equal(JSON.stringify(legacy),oldLegacy);assert.throws(()=>m.create(P.DEFAULT,{}, {...ops,compressorDemand:false}),/managed/);
// Documented two-step range edit: rejected combined disable cannot partly stop/change the plant.
const limits=m.create(P.DEFAULT,{},ops,{mode:'manual'}),oldLimits=JSON.stringify(limits);assert.throws(()=>m.update(limits,{compressorOn:false,speed:.5},{gain:20},{maxSpeed:.5}),/Stop/);assert.equal(JSON.stringify(limits),oldLimits);m.update(limits,{compressorOn:false});m.update(limits,{speed:.5},{},{maxSpeed:.5});assert.equal(limits.capacity.settings.maxSpeed,.5);assert.equal(limits.capacity.speed,0);
// Independent stops override a demand hold, freeze accepted time and retain evidence after clear.
for(const [kind,model,profile,o]of [
 ['equipment',m,P.DEFAULT,{...ops,valveMode:'closed'}],
 ['solver',make({maxStep:.1,minStep:.1,tolerance:1e-12}),P.DEFAULT,ops],
 ['domain',m,(()=>{const p=P.copy(P.DEFAULT);p.inventory.initialization.liquidFractions.receiver=1;return p;})(),{...ops,receiverHeat:100,compressorOn:false}]
]){const s=model.create(profile,{},o,{mode:'manual',minOn:900});model.update(s,{compressorDemand:false});model.advance(s,120);assert.equal(s.fault?.kind,kind);valid(model,s);assert.equal(s.capacity.speed,0);const original=JSON.parse(JSON.stringify(s.fault)),restAtStop=C.record(s.capacity).minimumOffRemaining,frozen=JSON.stringify(s);model.advance(s,10);assert.equal(JSON.stringify(s),frozen);model.update(s,{compressorOn:false,valveMode:'closed'});model.clearFault(s);assert.deepEqual(s.capacity.lastStop,original);assert.equal(s.capacity.speed,0);near(C.record(s.capacity).minimumOffRemaining,restAtStop);}

// All managed recipes complete from real accepted observations at every playback batching scale.
const ids=['capacity-startup','capacity-hold','capacity-response'],outcomes=[];
for(const id of ids)for(const chunk of [.25,2.5,15,75,300]){
 const {s,a}=lesson(id);T.answer(a,1,s.time);assert(!a.goals[a.goals.length-1].met);T.answer(a,0,s.time);apply(a,s);
 for(let i=0;i<150&&a.status==='active';i++)guarded(a,s,chunk);
 assert.equal(a.status,'completed',id+': '+a.reason);assert(a.goals.every(g=>g.met));assert(!s.fault);assert.equal(s.pending,0);near(s.time,a.endedAt);near(s.time,id==='capacity-response'?150:10);valid(m,s);
 const report=T.report(a,s),frozen=JSON.stringify(report);assert(report.final.capacity);assert(report.attempt.actions[0].capacity);assert(report.history.samples.every(p=>p.capacity));m.update(s,{compressorOn:false});m.advance(s,1);assert.equal(JSON.stringify(report),frozen);
 if(chunk===300)outcomes.push({exercise:id,completedSeconds:a.endedAt,objectives:a.goals.length});
}
// Grading checks every capacity setting, master/demand controls and model basis.
for(const patch of [{suctionTarget:5},{ki:.004},{minOn:8},{mode:'manual'},{maxSpeed:.99}]){const {s,a}=lesson('capacity-response');m.updateCapacity(s,patch);const at=s.time;guarded(a,s,75);assert.equal(a.status,'interrupted');near(s.time,at);}
for(const o of [{compressorDemand:false},{compressorOn:false}]){const {s,a}=lesson('capacity-response');m.update(s,o);guarded(a,s,75);assert.equal(a.status,'interrupted');}
const {s:unstarted,a:premature}=lesson('capacity-hold');guarded(premature,unstarted,10);assert.equal(premature.status,'interrupted');assert.match(premature.reason,/action before advancing/);
const r=T.setup('startup'),wrongBasis=m.create(P.DEFAULT,r.room,r.operations,{mode:'auto'});assert.throws(()=>T.start('startup',wrongBasis),/setup/);
const {s:missing,a:noReflection}=lesson('capacity-startup');apply(noReflection,missing);guarded(noReflection,missing,10);assert.equal(noReflection.status,'active');assert(!noReflection.goals[3].met);
// The grader never changes physical state or accepted histories.
const recipe=T.setup('capacity-response'),normal=m.create(P.DEFAULT,recipe.room,recipe.operations,recipe.capacity),observed=m.create(P.DEFAULT,recipe.room,recipe.operations,recipe.capacity);m.advance(normal,120);m.advance(observed,120);const attempt=T.start('capacity-response',observed);for(const s of [normal,observed])m.update(s,{},{},{suctionTarget:6});T.injected(attempt,observed);m.advance(normal,20);m.advance(observed,20,[],current=>{T.observe(attempt,current);return true;});assert.deepEqual(observed,normal);

// Ten minutes of coupled PI/feed operation with disturbances and live mode switches.
const sustained=m.create(P.DEFAULT,{},ops,{mode:'auto',suctionTarget:4.5});
for(let i=0;i<20;i++){if(i===5)m.update(sustained,{}, {gain:20});if(i===10)m.update(sustained,{}, {gain:2},{suctionTarget:6});if(i===15)m.update(sustained,{}, {},{mode:'manual'});if(i===16)m.update(sustained,{}, {},{mode:'auto'});m.advance(sustained,30);valid(m,sustained);assert(!sustained.fault,'Sustained step '+i);assert(Number.isFinite(sustained.capacity.integral));}
assert(sustained.electricalKWh>0);assert(sustained.history.events.filter(x=>x.type==='capacity-settings').length<=3,'No per-tick setting-event flood');
// Coupled lower saturation and error reversal recover actual capacity through the ramp.
const lower=m.create(P.DEFAULT,{},ops,{mode:'auto',suctionTarget:4.5});m.advance(lower,120);m.updateCapacity(lower,{suctionTarget:7.8,kp:2,ki:.05,actuatorSeconds:1});m.advance(lower,30);valid(m,lower);assert(!lower.fault);assert.equal(lower.capacity.command,.2);assert(lower.capacity.limitedBy.includes('minimum speed'));const floorSpeed=lower.capacity.speed;m.updateCapacity(lower,{suctionTarget:1.5});m.advance(lower,10);valid(m,lower);assert(!lower.fault);assert(lower.capacity.speed>floorSpeed);assert.equal(lower.capacity.command,1);
const csv=H.csv(sustained.history).split('\r\n'),count=line=>[...line.matchAll(/"((?:[^"]|"")*)"(?:,|$)/g)].length;assert(csv.slice(5).every(line=>count(line)===count(csv[4])));assert(csv.some(line=>line.includes('compressorDemand')));
console.log(JSON.stringify({passed:true,outcomes,sustainedSeconds:sustained.time,checks:'Connected ordinary demand vs master override, fractional deadlines/refinement, cancellation/restart, atomic range edits, three measured lessons, exact batch-independent completion, strict recipe guards, frozen SI evidence, observation purity and ten-minute coupled operation.'},null,2));
