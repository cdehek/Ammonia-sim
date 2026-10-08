const assert=require('node:assert/strict'),P=require('../equipment-profiles'),e=require('../engine').createEngine(require('../properties.json'));
const model=require('../storage-engine').createStorage(e,P),ops={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto'};
const observed=model.create(P.DEFAULT,{},ops),control=model.create(P.DEFAULT,{},ops);
const frozen=JSON.stringify(observed),c=model.observeCompressor(observed);
assert.equal(JSON.stringify(observed),frozen,'Observation cannot alter inventories, controller, time or history');
assert(c.massFlow>0&&c.electrical>c.fluidWork&&c.dischargeTemperature>observed.states.condenser.T);
const suction=observed.states.outlet,discharge=e.ph(observed.states.condenser.p,suction.h+c.fluidWork/c.massFlow);
assert(Math.abs(discharge.T-c.dischargeTemperature)<1e-8,'Discharge temperature agrees with compressor energy balance');
for(let i=0;i<5;i++){model.observeCompressor(observed);model.advance(observed,1);model.advance(control,1);}
assert.deepEqual(observed,control,'Display sampling has no effect on the simulation trajectory');
model.update(observed,{compressorOn:false});const off=model.observeCompressor(observed);assert.equal(off.massFlow,0);assert.equal(off.electrical,0);assert.equal(off.dischargeTemperature,null);
const p=P.copy(P.DEFAULT);p.equipment.highTrip=10;const trip=model.create(p,{},ops);model.advance(trip,1);assert(trip.fault);const snapshot=JSON.stringify(trip);assert(model.observeCompressor(trip).inhibited);assert.equal(model.observeCompressor(trip).massFlow,undefined);assert.equal(JSON.stringify(trip),snapshot);
console.log('PASS: read-only compressor telemetry, energy-consistent discharge temperature, unchanged trajectories, off/latched-stop demand.');
