const assert=require('node:assert/strict');
const {analyze}=require('../operator-assist'),P=require('../equipment-profiles');
const e=require('../engine').createEngine(require('../properties.json'));
const model=require('../storage-engine').createStorage(e,P),ops={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto'};
const freeze=x=>{if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;};
const projection=(s,extra={})=>analyze({record:model.record(s),compressor:model.observeCompressor(s),...extra});
assert.equal(analyze().status,'NOT INITIALIZED');assert.deepEqual(analyze().readings,[]);
const s=model.create(P.DEFAULT,{},ops),paused=projection(s);
assert.match(paused.compressor,/Enabled at 70.00 %.*not actively advancing/);assert.equal(paused.status,'PLAYBACK PAUSED');assert.match(paused.explanation,/No active modeled/);
const frozen=freeze({record:model.record(s),compressor:model.observeCompressor(s),running:true});
const snapshot=JSON.stringify(frozen),active=analyze(frozen);assert.equal(JSON.stringify(frozen),snapshot);assert.equal(active.status,'OPERATING');assert.match(active.compressor,/supported current compressor demand/);
model.update(s,{compressorOn:false});const off=projection(s,{running:true});assert.match(off.compressor,/Disabled.*off/);assert.equal(off.status,'OPERATING');
const trippedProfile=P.copy(P.DEFAULT);trippedProfile.equipment.highTrip=10;
const tripped=model.create(trippedProfile,{},ops);model.advance(tripped,1);
assert.equal(tripped.fault.kind,'equipment');let a=projection(tripped,{running:true});assert.equal(a.status,'EQUIPMENT TRIP');assert.equal(a.reason,tripped.fault.message);assert.match(a.explanation,/Playback is stopped/);assert.match(a.observation,/≥/);assert.match(a.tip,/does not establish.*repaired/);assert.match(a.readings[2].value,/Unavailable/);
assert.equal(a.evidence[0].value,((10-1.01325)*14.503773773).toFixed(2)+' psig');
const strict=require('../storage-engine').createStorage(e,P,{maxStep:.1,minStep:.1,tolerance:1e-12}),solver=strict.create(P.DEFAULT,{},ops);strict.advance(solver,1);assert.equal(solver.fault.kind,'solver');assert.equal(projection(solver).status,'NUMERICAL / SOLVER STOP');assert.match(projection(solver).explanation,/not an equipment trip/);
const liquid=P.copy(P.DEFAULT);liquid.inventory.initialization.liquidFractions.receiver=1;const domain=model.create(liquid,{}, {receiverHeat:100});model.advance(domain,10);assert.equal(domain.fault.kind,'domain');assert.equal(projection(domain).status,'MODEL-DOMAIN STOP');assert.deepEqual(projection(domain).evidence,[]);
model.update(tripped,{compressorOn:false});model.clearFault(tripped);a=projection(tripped);assert.equal(a.status,'PLAYBACK PAUSED');assert.equal(a.reason,undefined);assert.deepEqual(a.evidence,[]);assert.match(a.explanation,/No active modeled/);assert.equal(projection(model.create(P.DEFAULT,{},ops)).reason,undefined);assert.equal(analyze().reason,undefined);
const normal=model.create(P.DEFAULT,{},ops),r=model.record(normal),reading=(units,index)=>analyze({record:r,units}).readings[index].value;
assert.equal(reading({p:'bara',T:'C'},0),r.vessels.outlet.p.toFixed(2)+' bar(a)');
assert.equal(reading({p:'barg',T:'C'},0),(r.vessels.outlet.p-1.01325).toFixed(2)+' bar(g)');
assert.equal(reading({p:'psia',T:'F'},0),(r.vessels.outlet.p*14.503773773).toFixed(2)+' psia');
assert.equal(reading({p:'psig',T:'F'},3),(r.flows.superheat*1.8).toFixed(2)+' °F Δ');
assert.equal(reading({p:'bara',T:'C'},3),r.flows.superheat.toFixed(2)+' K');
const hot=P.copy(P.DEFAULT);hot.equipment.dischargeTrip=80;const thermal=model.create(hot,{},ops);model.advance(thermal,1);assert.equal(thermal.fault.message,'High discharge temperature');assert.equal(projection(thermal).evidence[0].value,'176.00 °F');assert.equal(projection(thermal,{units:{p:'bara',T:'C'}}).evidence[0].value,'80.00 °C');
const missing=structuredClone(r);missing.vessels.outlet.p=null;missing.vessels.condenser.p=NaN;missing.controller.opening=null;missing.flows={error:'unavailable'};assert(analyze({record:missing}).readings.filter((_,i)=>[0,1,3,4,5].includes(i)).every(v=>v.value==='Unavailable'));
const isolated=projection(model.create(P.DEFAULT));assert.equal(isolated.readings[3].value,'Unavailable');assert.equal(isolated.readings[4].value,'Unavailable');
assert.match(projection(normal,{running:true,compressor:{massFlow:0}}).compressor,/demand is zero/);assert.match(projection(normal,{running:true,compressor:null}).compressor,/demand is unavailable/);
assert.equal(analyze({record:{seconds:0,operations:{circuit:'unsupported'}}}).status,'UNSUPPORTED STATE');assert.match(projection(normal,{draft:true}).settings,/Unapplied draft/);assert.match(projection(normal,{running:true,compressor:{inhibited:true,error:'observed limit'}}).compressor,/unavailable: observed limit/);
// Compare the entire evolving state, including history, counters, controller and pending time.
// Repeated observations and all display units must leave the numerical trajectory identical.
const control=model.create(P.DEFAULT,{},ops),observed=model.create(P.DEFAULT,{},ops);
for(let i=0;i<20;i++){
 for(const p of ['bara','barg','psia','psig'])for(const T of ['C','F'])projection(observed,{running:i%2===0,units:{p,T},draft:true});
 assert.deepEqual(observed,control,'Analysis cannot mutate any model state');model.advance(control,1);model.advance(observed,1);assert.deepEqual(observed,control,'Observation cannot change trajectories');
}
console.log('PASS: Operator Assist uninitialized, paused/enabled, running, off, real equipment/solver/domain stops, clear/reset, four pressure units, absolute/delta temperatures, missing data, drafts, frozen inputs and identical full numerical trajectories.');
