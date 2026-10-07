const assert=require('node:assert/strict'),P=require('../equipment-profiles');
const engine=require('../engine').createEngine(require('../properties.json'));
const initializer=require('../inventory-initialization').createInitializer(engine,P);
const baseline=P.copy(P.DEFAULT),a=initializer.preview(baseline);
assert.equal(baseline.schemaVersion,2);assert.equal(P.DEFAULT.revision,2);assert(a.ready);assert(a.totalMassKg>0);
assert(Object.isFrozen(P.DEFAULT.inventory.initialization.liquidFractions));
for(const [key,v]of Object.entries(a.vessels)){
 const state=engine.statePX(v.pressureBarAbsolute,v.vaporMassFraction);
 assert(Math.abs(v.massKg/state.rho-v.volumeM3)<1e-12);
 assert(Math.abs(v.massKg*(state.h-state.p*100/state.rho)-v.internalEnergyKJ)<1e-8);
 assert(Math.abs(v.liquidMassKg+v.vaporMassKg-v.massKg)<1e-12);
 assert.equal(v.liquidVolumeFraction,baseline.inventory.initialization.liquidFractions[key]);
}
assert(Math.abs(Object.values(a.vessels).reduce((sum,v)=>sum+v.massKg,0)-a.totalMassKg)<1e-10);
const charged=P.copy(baseline);charged.inventory.initialization.mode='charge';charged.inventory.initialization.chargeKg=a.totalMassKg;charged.inventory.initialization.liquidFractions.receiver=null;
const b=initializer.preview(charged);assert(b.ready);assert(Math.abs(b.vessels.receiver.liquidVolumeFraction-.3)<1e-12);assert(Math.abs(b.totalInternalEnergyKJ-a.totalInternalEnergyKJ)<1e-8);
for(const charge of [a.minChargeKg-1,a.maxChargeKg+1]){charged.inventory.initialization.chargeKg=charge;assert.equal(initializer.preview(charged).status,'invalid');}
for(const [charge,fill]of [[a.minChargeKg,0],[a.maxChargeKg,1]]){charged.inventory.initialization.chargeKg=charge;const result=initializer.preview(charged);assert(result.ready);assert(Math.abs(result.vessels.receiver.liquidVolumeFraction-fill)<1e-12);assert(result.warnings.length);}
const old={...P.copy(baseline),schemaVersion:1,futureVolumes:{receiver:.8,evaporator:null,condenser:.2}};delete old.inventory;
const snapshot=JSON.stringify(old),migrated=P.normalize(old);assert.equal(JSON.stringify(old),snapshot);assert.equal(migrated.schemaVersion,2);assert.deepEqual(migrated.inventory.volumes,old.futureVolumes);assert.equal(migrated.inventory.initialization,null);assert.equal(migrated.revision,old.revision);assert.equal(migrated.id,old.id);assert.equal(initializer.preview(migrated).status,'unconfigured');
const library=P.restore({schemaVersion:1,activeId:'legacy',profiles:[{...old,id:'legacy'}]});assert.equal(library.migrated,1);assert.equal(library.activeId,'legacy');assert.deepEqual(P.restore({schemaVersion:2,activeId:'legacy',profiles:library.profiles}).profiles,library.profiles);
const invalid=[{...baseline.inventory,volumes:{...baseline.inventory.volumes,receiver:null}},{...baseline.inventory,initialization:{...baseline.inventory.initialization,suctionPressure:8,dischargePressure:3}},{...baseline.inventory,initialization:{...baseline.inventory.initialization,chargeKg:10}},{...baseline.inventory,initialization:{...baseline.inventory.initialization,liquidFractions:{...baseline.inventory.initialization.liquidFractions,evaporator:1.1}}},{...baseline.inventory,initialization:{...baseline.inventory.initialization,suctionPressure:'2.5'}}];
for(const inventory of invalid)assert.throws(()=>P.normalize({...baseline,inventory}));
assert.throws(()=>P.normalize({...charged,inventory:{...charged.inventory,initialization:{...charged.inventory.initialization,liquidFractions:{...charged.inventory.initialization.liquidFractions,receiver:.3}}}}));
const incomplete=P.copy(baseline);incomplete.inventory={volumes:{receiver:null,evaporator:null,condenser:null},initialization:null};assert.equal(initializer.preview(incomplete).status,'unconfigured');
const other=P.copy(baseline);other.inventory.volumes.receiver=1;assert(initializer.preview(other).totalMassKg>a.totalMassKg);
assert.deepEqual(P.apply({},other),P.apply({},baseline)); // Stage 1 cannot alter live physics.
assert.deepEqual(P.imported(old).inventory,migrated.inventory);assert.deepEqual(P.imported(charged).inventory,charged.inventory);
for(const reference of require('./initialization-reference.json').cases){
 const profile=P.copy(baseline);Object.assign(profile.inventory.initialization,{suctionPressure:reference.suctionPressure,dischargePressure:reference.dischargePressure,liquidFractions:reference.liquidFractions});
 const result=initializer.preview(profile);assert(result.ready);
 for(const [key,v]of Object.entries(reference.vessels)){assert(Math.abs(result.vessels[key].massKg/v.massKg-1)<.0001);assert(Math.abs(result.vessels[key].internalEnergyKJ/v.internalEnergyKJ-1)<.0002);}
}
console.log('PASS: schema migration, initialization modes, charge feasibility, phase/volume/mass/energy consistency, boundary fills, validation and isolation from live physics.');
