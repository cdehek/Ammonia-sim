/* Closed-loop checks exercise actual MVU balances, independent protection and accepted clocks. */
const assert=require('node:assert/strict'),P=require('../equipment-profiles'),C=require('../capacity-controller'),e=require('../engine').createEngine(require('../properties.json'));
const make=n=>require('../storage-engine').createStorage(e,P,n),m=make(),ops={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto'};
function valid(model,s){const r=model.record(s);assert.equal(r.capacity.seconds,r.seconds);assert.equal(r.capacity.pendingSeconds,0);assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);assert(r.controller.opening>=0&&r.controller.opening<=1);assert(r.capacity.actualSpeed===0||r.capacity.actualSpeed>=.2&&r.capacity.actualSpeed<=1);return r;}
const run=(step,chunk=30)=>{const model=make({maxStep:step}),s=model.create(P.DEFAULT,{},ops,{mode:'auto'});for(let t=0;t<30;t+=chunk)model.advance(s,chunk);valid(model,s);assert(!s.fault);return s;};
const base=run(.1),batched=run(.1,1);assert.deepEqual(base.vessels,batched.vessels);assert.deepEqual(base.capacity,batched.capacity);
const finer=[run(.05),run(.025)];for(const s of finer){assert(Math.abs(base.states.outlet.p-s.states.outlet.p)<.01);assert(Math.abs(base.capacity.speed-s.capacity.speed)<.003);assert(Math.abs(base.electricalKWh/s.electricalKWh-1)<.005);}
assert.equal(base.operations.speed,.7);assert.equal(base.history.events.filter(x=>x.type==='controls').length,0);assert(base.history.samples.every(x=>x.capacity));assert(base.history.samples.length<=32);assert.notEqual(base.capacity.speed,.7);assert(base.electricalKWh>0);assert(base.controller.opening>0);
// Compare identical loads at different requested suction pressures: more delivered
// compression must lower suction while both independent feed controllers operate.
const lower=m.create(P.DEFAULT,{},ops,{mode:'auto',suctionTarget:1.5}),higher=m.create(P.DEFAULT,{},ops,{mode:'auto',suctionTarget:4.5});
for(const s of [lower,higher]){m.advance(s,120);valid(m,s);assert(!s.fault);}
assert(lower.capacity.speed>higher.capacity.speed);assert(lower.states.outlet.p<higher.states.outlet.p);assert(lower.electricalKWh>higher.electricalKWh);
assert(lower.capacity.command===1&&lower.capacity.limitedBy.includes('maximum speed'));
const saturatedSpeed=lower.capacity.speed;m.updateCapacity(lower,{suctionTarget:6});m.advance(lower,30);valid(m,lower);assert(!lower.fault);assert(lower.capacity.speed<saturatedSpeed,'Recover from upper saturation after target relaxation');
const H=require('../storage-history'),csv=H.csv(lower.history).split('\r\n');const header=csv[4];assert(header.includes('Actual compressor fraction'));const count=line=>[...line.matchAll(/"((?:[^"]|"")*)"(?:,|$)/g)].length;assert(csv.slice(5).every(line=>count(line)===count(header)),'Managed CSV columns align');
const before=base.capacity.speed;m.updateCapacity(base,{mode:'manual'});assert.equal(base.capacity.speed,before);assert.equal(base.capacity.settings.manualSpeed,before);m.update(base,{speed:.8});m.advance(base,10);valid(m,base);assert(Math.abs(base.capacity.speed-.8)<Math.abs(before-.8));assert.equal(base.operations.speed,.8);assert.equal(base.history.events.filter(x=>x.type==='capacity-settings').length,2);
const unchanged=JSON.stringify(base);assert.throws(()=>m.updateCapacity(base,{suctionTarget:.4}));assert.equal(JSON.stringify(base),unchanged);assert.throws(()=>m.update(base,{speed:NaN}));assert.equal(JSON.stringify(base),unchanged);
const load=m.create(P.DEFAULT,{},ops,{mode:'auto'});m.advance(load,30);m.update(load,{}, {gain:20});m.advance(load,30);valid(m,load);assert(!load.fault);
// A single form edit is one transaction across plant and capacity settings.
const transaction=m.create(P.DEFAULT,{},ops,{mode:'auto'});m.advance(transaction,1);const prior=JSON.stringify(transaction);
assert.throws(()=>m.update(transaction,{speed:.8},{gain:20},{suctionTarget:.4}));assert.equal(JSON.stringify(transaction),prior);
m.update(transaction,{speed:.8},{gain:20},{suctionTarget:3});assert.equal(transaction.operations.speed,.8);assert.equal(transaction.capacity.settings.manualSpeed,.8);assert.equal(transaction.roomConfig.gain,20);assert.equal(transaction.capacity.settings.suctionTarget,3);
const actual=transaction.capacity.speed;m.update(transaction,{}, {},{mode:'manual'});assert.equal(transaction.capacity.speed,actual);assert.equal(transaction.operations.speed,actual);assert.equal(transaction.capacity.settings.manualSpeed,actual);
const eventCount=transaction.history.events.length;m.update(transaction,{}, {},{mode:'manual'});assert.equal(transaction.history.events.length,eventCount);
const manual=m.create(P.DEFAULT,{},ops);assert(!('capacity' in m.record(manual)));assert.equal(manual.operations.speed,.7);assert.throws(()=>m.updateCapacity(manual,{mode:'auto'}),/explicitly/);
for(const invalid of [[],true,42,Object.create({mode:'auto'})])assert.throws(()=>m.create(P.DEFAULT,{},ops,invalid),/plain object/);
const bank=P.copy(P.DEFAULT);bank.equipment.compressors=2;assert.doesNotThrow(()=>m.create(bank,{},ops));assert.throws(()=>m.create(bank,{},ops,{mode:'auto'}),/one compressor/);
const delayed=m.create(P.DEFAULT,{}, {...ops,compressorOn:false},{minOff:1,startDelay:.25,minOn:2});m.update(delayed,{compressorOn:true});m.advance(delayed,1);assert(!delayed.capacity.running);m.advance(delayed,.2);assert(!delayed.capacity.running);m.advance(delayed,.1);assert(delayed.capacity.running);assert(Math.abs(delayed.capacity.lastSwitch-1.25)<1e-9);m.update(delayed,{compressorOn:false});assert.equal(delayed.capacity.speed,0);assert.equal(delayed.capacity.lastSwitch,delayed.time);
// Protection still checks the final running interval when demand stops at its endpoint.
const deadlineProfile=P.copy(P.DEFAULT);deadlineProfile.equipment.lowTrip=2.3092;
const deadlineOps={...ops,speed:1},legacyDeadline=m.create(deadlineProfile,{},deadlineOps);m.advance(legacyDeadline,.1);assert.equal(legacyDeadline.fault?.message,'Low suction pressure');
for(const chunk of [.05,.1,1]){
 const s=m.create(deadlineProfile,{},deadlineOps,{mode:'manual',minOn:.1});m.update(s,{compressorDemand:false});for(let i=0;i<2&&!s.fault;i++)m.advance(s,chunk);
 assert.equal(s.fault?.kind,'equipment');assert.equal(s.fault.message,'Low suction pressure');assert(Math.abs(s.time-.1)<1e-9);assert(s.states.outlet.p<deadlineProfile.equipment.lowTrip);assert.equal(s.fault.readings.pressure,s.states.outlet.p);assert.equal(s.fault.readings.speed,1);
 assert.equal(s.capacity.speed,0);assert.deepEqual(s.capacity.lastStop,s.fault);assert.equal(s.pending,0);assert.equal(s.capacity.pending,0);assert(Math.abs(s.capacity.lastSwitch-s.time)<1e-9);assert(Math.abs(C.record(s.capacity).minimumOffRemaining-90)<1e-9);valid(m,s);
 assert(Math.abs(s.states.outlet.p-legacyDeadline.states.outlet.p)<1e-9);assert(Math.abs(s.electricalKWh-legacyDeadline.electricalKWh)<1e-12);assert(s.electricalKWh>0);
 assert(s.history.events.some(e=>e.type==='stop'));assert(!s.history.events.some(e=>e.type==='capacity-state'),'Trip wins over an ordinary demand-stop event');const frozen=JSON.stringify(s);m.advance(s,10);assert.equal(JSON.stringify(s),frozen);
}
// Off intervals do not invent trips, but an endpoint start must still check protection.
// Isolate one accepted interval: newly commanded speed must neither hide nor invent a trip.
const speedModel=make({maxStep:.1,minStep:.1,tolerance:1}),speedProfile=P.copy(P.DEFAULT);speedProfile.equipment.dischargeTrip=140.6;
for(const [speed,request,trip]of [[.2,1,true],[.3,.2,false]]){
 const o={...ops,speed},legacy=speedModel.create(speedProfile,{},o),managed=speedModel.create(speedProfile,{},o,{actuatorSeconds:.05,rampPerSecond:1});
 speedModel.updateCapacity(managed,{manualSpeed:request});speedModel.advance(legacy,.1);speedModel.advance(managed,.1);
 assert.equal(managed.acceptedSteps,1);assert.equal(managed.time,.1);assert.equal(!!managed.fault,trip);assert.deepEqual(managed.fault,legacy.fault);assert.deepEqual(managed.vessels,legacy.vessels);assert.equal(managed.electricalKWh,legacy.electricalKWh);valid(speedModel,managed);
 if(trip){assert.equal(managed.fault.message,'High discharge temperature');assert.equal(managed.fault.readings.speed,speed);assert(managed.fault.readings.discharge>=speedProfile.equipment.dischargeTrip);assert.equal(managed.capacity.speed,0);}
 else{assert(managed.capacity.speed<speed);const nextOutput=speedModel.observeCompressor(managed);assert(nextOutput.inhibited,'Next output would cross the limit, but did not drive this interval');assert.equal(managed.capacity.running,true);speedModel.advance(managed,.1);assert.equal(managed.fault?.message,'High discharge temperature');assert.equal(managed.time,.1,'New output receives protection before the next physical interval');}
}
const offProfile=P.copy(P.DEFAULT);offProfile.equipment.lowTrip=2.7;
const offAtLimit=m.create(offProfile,{}, {...ops,compressorOn:false},{suctionTarget:3,minOff:0,startDelay:.1});m.advance(offAtLimit,.1);assert(offAtLimit.states.outlet.p<offProfile.equipment.lowTrip);assert(!offAtLimit.fault);assert.equal(offAtLimit.electricalKWh,0);
const startingAtLimit=m.create(offProfile,{}, {...ops,compressorOn:false},{suctionTarget:3,minOff:0,startDelay:.1});m.update(startingAtLimit,{compressorOn:true});m.advance(startingAtLimit,.1);assert.equal(startingAtLimit.fault?.message,'Low suction pressure');assert(Math.abs(startingAtLimit.time-.1)<1e-9);assert.equal(startingAtLimit.electricalKWh,0);valid(m,startingAtLimit);
// Fractional accepted controller stop records the physical clock and starts rest there.
const pending=C.create(P.DEFAULT,{}, {running:true,speed:.7});C.advance(pending,.125,{pressureBarAbsolute:2.5});C.advance(pending,1,{pressureBarAbsolute:2.5,stop:{kind:'equipment',message:'Pending fractional stop',seconds:.125}});assert.equal(pending.time,.125);assert.equal(pending.lastSwitch,.125);assert.equal(pending.pending,0);
const c=C.create(P.DEFAULT,{}, {running:true,speed:.7});C.advanceAccepted(c,.1,{pressureBarAbsolute:2.5});C.advanceAccepted(c,.025,{pressureBarAbsolute:2.5});const fault={kind:'equipment',message:'Fractional stop',seconds:.125,readings:{pressure:2.5}};C.advanceAccepted(c,0,{pressureBarAbsolute:2.5,stop:fault});assert.equal(c.time,.125);assert.equal(c.lastSwitch,.125);assert.deepEqual(c.stop,fault);assert.equal(C.record(c).minimumOffRemaining,90);
for(const [label,model,profile,o]of [
 ['equipment',m,P.DEFAULT,{...ops,valveMode:'closed'}],
 ['solver',make({maxStep:.1,minStep:.1,tolerance:1e-12}),P.DEFAULT,ops],
 ['domain',m,(()=>{const p=P.copy(P.DEFAULT);p.inventory.initialization.liquidFractions.receiver=1;return p;})(),{...ops,receiverHeat:100,compressorOn:false}]
]){const s=model.create(profile,{},o,{mode:'auto'});model.advance(s,60);assert.equal(s.fault?.kind,label);valid(model,s);assert.equal(s.capacity.speed,0);assert.equal(s.capacity.lastStop.seconds,s.time);assert.deepEqual(s.capacity.lastStop,s.fault);const frozen=JSON.stringify(s);model.advance(s,30);assert.equal(JSON.stringify(s),frozen);model.update(s,{compressorOn:false});model.clearFault(s);assert.deepEqual(s.capacity.lastStop,JSON.parse(frozen).fault);model.advance(s,1);valid(model,s);assert.equal(s.capacity.speed,0);}
console.log('PASS: coupled suction feedback/feed PI, conservation, load response, actuator switching, exact fractional clocks/start/rest, accepted-only updates, fault freeze/recovery, SI history without event floods, explicit manual/bank compatibility, batching and .1/.05/.025 s refinement.');
