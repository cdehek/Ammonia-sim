const assert=require('node:assert/strict'),C=require('../capacity-controller'),P=require('../equipment-profiles');
const input=p=>({pressureBarAbsolute:p}),ready=(settings={})=>C.create(P.DEFAULT,settings,{running:true,speed:.7}),near=(a,b,t=1e-8)=>assert(Math.abs(a-b)<t,a+' vs '+b);
const s=ready();C.advance(s,1,input(2.5));near(s.speed,.7);C.update(s,{manualSpeed:.9});const before=s.speed;C.advance(s,.1,input(2.5));assert(s.speed>before&&s.speed<=before+.002+1e-10);assert(C.record(s).limitedBy.includes('actuator response'));
const ramp=ready({manualSpeed:1,actuatorSeconds:.05,rampPerSecond:.01});C.advance(ramp,1,input(2.5));near(ramp.speed,.71);assert(C.record(ramp).limitedBy.includes('ramp rate'));
const auto=ready({mode:'auto'});C.advance(auto,1,input(2.5));near(auto.command,.7);C.advance(auto,10,input(3.5));assert(auto.command>.7&&auto.speed>.7);const elevated=auto.speed;C.advance(auto,10,input(1.5));assert(auto.speed<elevated,'High suction asks for more speed; low suction asks for less');
const band=ready({mode:'auto'});C.advance(band,10,input(2.54));near(band.speed,.7);assert.equal(C.record(band).errorBar,0);
const sensor=ready({mode:'auto',sensorSeconds:2});C.advance(sensor,1,input(2.5));C.advance(sensor,2,input(3.5));near(sensor.sensedPressure,3.5-Math.exp(-1));assert(sensor.sensedPressure<3.5);
// Extended saturation cannot accumulate a hidden unbounded integral.
const saturated=ready({mode:'auto',ki:.02,actuatorSeconds:1});C.advance(saturated,1,input(2.5));C.advance(saturated,1200,input(8));assert(saturated.command===1&&saturated.speed<=1);assert(Math.abs(saturated.integral)<5);C.advance(saturated,1200,input(.5));assert(saturated.command===.2&&saturated.speed>=.2);assert(Math.abs(saturated.integral)<5);C.advance(saturated,30,input(3));assert(saturated.speed>.2&&saturated.command>.2,'Reverse error recovers from saturation without a long windup hold');
const switched=ready();C.advance(switched,2,input(3));const oldSpeed=switched.speed;C.update(switched,{mode:'auto'});near(switched.speed,oldSpeed);C.advance(switched,.1,input(3));near(switched.speed,oldSpeed);C.advance(switched,5,input(3));const automaticSpeed=switched.speed;C.update(switched,{mode:'manual'});near(switched.settings.manualSpeed,automaticSpeed);near(switched.speed,automaticSpeed);C.advance(switched,.1,input(3));near(switched.speed,automaticSpeed);
// Accepted mode edits must return correct telemetry immediately, without a clock tick.
for(const [from,to,reason]of [['manual','auto','Automatic suction PI'],['auto','manual','Manual capacity']]){
 const state=ready({mode:from,manualSpeed:.85});C.advance(state,2,input(3));
 const prior=C.record(state),physical=JSON.parse(JSON.stringify(state));
 const returned=C.update(state,{mode:to});
 assert.equal(returned.mode,to);assert.equal(returned.reason,reason);assert.deepEqual(returned,C.record(state));
 // The pre-existing bumpless transition still rebases request/integral to delivered speed.
 assert.equal(returned.actualSpeed,prior.actualSpeed);assert.equal(returned.requestedSpeed,prior.actualSpeed);assert.equal(returned.rawCommand,prior.actualSpeed);
 near(returned.integral,prior.actualSpeed-state.settings.kp*returned.errorBar);assert.equal(state.track,true);
 if(to==='manual')assert.equal(returned.settings.manualSpeed,prior.actualSpeed);
 assert.deepEqual(returned.limitedBy,[],'Rebased interior-speed request has no stale limits');
 for(const key of ['time','pending','speed','running','lastSwitch','startDemandAt','starts','input','measuredPressure','sensedPressure','stop','lastStop','profile'])assert.deepEqual(state[key],physical[key],from+'→'+to+' preserves '+key);
 for(const key of ['seconds','pendingSeconds','lastSwitchSeconds','minimumOnRemaining','minimumOffRemaining','startDelayRemaining'])assert.deepEqual(returned[key],prior[key]);
 returned.reason='Changed detached record';assert.equal(C.record(state).reason,reason);
 const unchanged=JSON.stringify(state);assert.equal(C.update(state,{mode:to}).reason,reason);assert.equal(JSON.stringify(state),unchanged,'No-op mode edits remain pure');
}
// Remove prior actuator, ramp and saturation flags; preserve real boundary-speed flags.
for(const [from,to]of [['manual','auto'],['auto','manual']])for(const [flag,settings]of [
 ['actuator response',{manualSpeed:.9}],['ramp rate',{manualSpeed:1,actuatorSeconds:.05,rampPerSecond:.01}],['maximum speed',{manualSpeed:1,kp:2}]
]){
 const state=ready({mode:from,...settings});C.advance(state,1,input(2.5));C.advance(state,2,input(3.5));const before=C.record(state);
 assert(before.limitedBy.includes(flag),from+' fixture exercises '+flag);assert(before.actualSpeed>.2&&before.actualSpeed<1);
 const after=C.update(state,{mode:to});assert.deepEqual(after.limitedBy,[]);assert.deepEqual(after,C.record(state));assert.equal(after.actualSpeed,before.actualSpeed);assert.equal(after.seconds,before.seconds);assert.equal(after.requestedSpeed,after.actualSpeed);
}
for(const speed of [.2,1]){const state=C.create(P.DEFAULT,{manualSpeed:speed},{running:true,speed});C.advance(state,1,input(2.5));const before=C.record(state),after=C.update(state,{mode:'auto'});assert.deepEqual(after.limitedBy,[speed===.2?'minimum speed':'maximum speed']);assert.equal(after.actualSpeed,before.actualSpeed);assert.equal(after.seconds,before.seconds);}
// Mode labels cannot override an active run hold or an off-state inhibit/delay.
for(const [from,to]of [['manual','auto'],['auto','manual']])for(const kind of ['initial','hold','rest','delay','disabled','stop']){
 const state=kind==='rest'||kind==='delay'?C.create(P.DEFAULT,{mode:from,minOff:kind==='delay'?0:90,startDelay:3}):ready({mode:from});
 if(kind==='hold')C.advanceAccepted(state,0,{...input(2.5),demand:false});
 if(kind==='rest'||kind==='delay')C.advanceAccepted(state,0,input(2.5));
 if(kind==='disabled')C.advanceAccepted(state,0,{...input(2.5),enabled:false});
 if(kind==='stop')C.advanceAccepted(state,0,{...input(2.5),stop:{kind:'equipment',message:'Original stop',seconds:0}});
 const before=C.record(state),after=C.update(state,{mode:to});assert.equal(after.mode,to);
 assert.equal(after.reason,kind==='initial'?(to==='auto'?'Automatic suction PI':'Manual capacity'):before.reason);
 assert.equal(after.seconds,before.seconds);assert.equal(after.actualSpeed,before.actualSpeed);assert.equal(after.running,before.running);assert.equal(after.minimumOnRemaining,before.minimumOnRemaining);assert.equal(after.minimumOffRemaining,before.minimumOffRemaining);assert.deepEqual(after.stop,before.stop);
}
// Rest/run delays are accepted simulated time; initial off age is never invented.
const timers=C.create(P.DEFAULT,{minOff:2,startDelay:1,minOn:2});C.advance(timers,2,input(2.5));assert(!timers.running);assert.equal(timers.reason,'Start delay');C.advance(timers,1,input(2.5));assert(timers.running);near(timers.lastSwitch,3);assert.equal(timers.starts,1);near(timers.speed,.2);
C.advance(timers,1,{...input(2.5),demand:false});assert(timers.running);assert.equal(timers.reason,'Minimum on time');C.advance(timers,1,{...input(2.5),demand:false});assert(!timers.running);near(timers.lastSwitch,5);C.advance(timers,3,input(2.5));assert(timers.running);assert.equal(timers.starts,2);
const cancelled=C.create(P.DEFAULT,{minOff:0,startDelay:2,minOn:0});C.advance(cancelled,1,input(2.5));C.advance(cancelled,1,{...input(2.5),demand:false});C.advance(cancelled,1,input(2.5));assert(!cancelled.running);C.advance(cancelled,1,input(2.5));assert(cancelled.running,'Start delay requires fresh continuous demand');near(cancelled.lastSwitch,4);
for(const change of [{enabled:false},{available:false},{pressureBarAbsolute:null},{pressureBarAbsolute:NaN},{pressureBarAbsolute:Infinity},{pressureBarAbsolute:.1}]){const off=ready();C.advance(off,.05,{...input(2.5),...change});assert(!off.running);assert.equal(off.speed,0);assert.equal(off.command,0);}
for(const kind of ['equipment','domain','solver']){const stopped=ready();C.advance(stopped,1,input(2.5));const time=stopped.time,fault={kind,message:'Original stop',seconds:time,readings:{pressure:2.5},limits:{lowTrip:.4}};C.advance(stopped,60,{...input(2.5),stop:fault});near(stopped.time,time);assert(!stopped.running);assert.equal(stopped.pending,0);assert.deepEqual(C.record(stopped).stop,fault);fault.readings.pressure=999;assert.equal(C.record(stopped).stop.readings.pressure,2.5);C.advance(stopped,1,input(2.5));assert(!stopped.running);assert.equal(C.record(stopped).lastStop.readings.pressure,2.5);}
const retained=ready();C.advance(retained,1,input(2.5));const report=C.record(retained),frozen=JSON.stringify(report);C.advance(retained,1,input(3));assert.equal(JSON.stringify(report),frozen);
const batched=chunk=>{const x=ready({mode:'auto'});for(let t=0;t<10-1e-8;t+=chunk)C.advance(x,chunk,input(3));return x;};assert.deepEqual(batched(10),batched(1));assert.deepEqual(batched(1),batched(.05));
const partial=ready();C.advance(partial,.05,input(2.5));const snap=JSON.stringify(partial);assert.throws(()=>C.advance(partial,.05,input(3)),/cadence/);assert.equal(JSON.stringify(partial),snap);C.advance(partial,.05,{...input(3),enabled:false});assert(!partial.running);near(partial.time,0);near(partial.pending,.05);C.update(partial,{manualSpeed:.8});assert.equal(partial.pending,0);
const noop=C.create(P.DEFAULT,{minOff:0,startDelay:2});C.advance(noop,.05,input(2.5));const noopBefore=JSON.stringify(noop);C.update(noop,{});assert.equal(JSON.stringify(noop),noopBefore,'No-op edits cannot erase pending time or restart a delay');assert.throws(()=>C.normalize(P.DEFAULT,new Date()),/object/);
const invalid=ready();for(const patch of [{mode:'bogus'},{suctionTarget:.4},{suctionTarget:NaN},{maxSpeed:.6},{minSpeed:.8},{minOn:-1},{kp:'1'},{actuatorSeconds:0},{unexpected:true},{constructor:1}]){const old=JSON.stringify(invalid);assert.throws(()=>C.update(invalid,patch));assert.equal(JSON.stringify(invalid),old);}
for(const args of [[0,input(2.5)],[3601,input(2.5)],[1,{pressureBarAbsolute:'2.5'}],[1,{enabled:'true'}],[1,{stop:{kind:'trip'}}]]){const old=JSON.stringify(invalid);assert.throws(()=>C.advance(invalid,...args));assert.equal(JSON.stringify(invalid),old);}
const bank=P.copy(P.DEFAULT);bank.equipment.compressors=2;assert.throws(()=>C.create(bank),/one compressor/);const profile=P.copy(P.DEFAULT),pSnapshot=JSON.stringify(profile);C.create(profile);assert.equal(JSON.stringify(profile),pSnapshot);assert(Object.isFrozen(C.DEFAULTS));
// Independent observation/control calculations cannot alter the connected plant.
const engine=require('../engine').createEngine(require('../properties.json')),model=require('../storage-engine').createStorage(engine,P),ops={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto'},normal=model.create(P.DEFAULT,{},ops),watched=model.create(P.DEFAULT,{},ops),controller=ready({mode:'auto'});
for(let t=0;t<30;t++){model.advance(normal,1);model.advance(watched,1);C.advance(controller,1,input(watched.states.outlet.p));}assert.deepEqual(watched,normal);
console.log('PASS: manual/auto direction and deadband, sensor/actuator/ramp response, tracking anti-windup, bumpless switching, run/rest/start timing, stop/sensor/operator priority, exact fault evidence, atomic rejection, cadence batching, single-compressor scope and unchanged connected trajectories.');
