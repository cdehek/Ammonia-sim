const assert=require('node:assert/strict');
const engine=require('../engine').createEngine(require('../properties.json'));
const {createDynamic}=require('../dynamic-engine');const d=createDynamic(engine);
let cases=0;
for(const room of [-20,-5,10])for(const ambient of [15,30])for(const speed of [.3,.7,1]){
 const p=d.coupled(room,{ambient},speed);
 assert(Math.max(...p.residual.map(Math.abs))<1e-6);
 assert(Math.abs(p.r.balance)<1e-8);
 assert(p.r.config.pressure<p.r.pHigh);
 assert(p.r.states[4].T<room);
 assert(p.r.states[3].x>0&&p.r.states[3].x<1);
 assert(p.r.states[2].T>ambient);
 assert(Math.abs(p.evapRequired-12)<.00002);
 assert(Math.abs(p.condRequired-25)<.00004);cases++;
}
const base=d.coupled(15,{},.7),weakEvap=d.coupled(15,{evapUA:3},.7),weakCond=d.coupled(15,{condUA:10},.7),warmAir=d.coupled(15,{ambient:35},.7);
assert(weakEvap.r.Q<base.r.Q*.7);assert(weakCond.r.pHigh>base.r.pHigh);assert(weakCond.r.Q<base.r.Q);assert(warmAir.r.pHigh>base.r.pHigh);assert(warmAir.r.COP<base.r.COP);
assert.throws(()=>d.coupled(15,{condUA:.1},1),/equilibrium/);
assert.throws(()=>d.validate({thermalMass:NaN}));
const run=(model,chunk=60,opts={})=>{const s=model.create(opts);for(let t=0;t<28800;t+=chunk)model.step(s,chunk);return s;};
const a=run(d),b=run(d,15);
assert.equal(a.trip,null);assert(a.starts>=2);assert.equal(a.T,b.T);assert.equal(a.energy,b.energy);assert.equal(a.starts,b.starts);
const refined=run(createDynamic(engine,{timeStep:.5}));
assert(Math.abs(a.T-refined.T)<.03);assert(Math.abs(a.energy/refined.energy-1)<.002);
const balance=s=>s.config.thermalMass*1000*(s.T-s.config.initial)-(s.leakHeat+s.gainHeat-s.removed);
assert(Math.abs(balance(a))<.0001);assert(Math.abs(balance(refined))<.0001);
const unavailable=d.create({available:false});d.step(unavailable,600);assert.equal(unavailable.starts,0);assert.equal(unavailable.energy,0);assert(unavailable.T>unavailable.config.initial);assert.equal(d.record(unavailable).pressure,null);
const trip=d.create({highTrip:3});d.step(trip,60);assert.match(trip.trip,/High discharge pressure/);assert.equal(trip.on,false);assert.equal(trip.energy,0);d.resetTrip(trip);d.update(trip,{highTrip:24});d.step(trip,30);assert.equal(trip.on,false);d.step(trip,60);assert.equal(trip.on,true);
const manual=d.create({mode:'manual',manualSpeed:.6});d.step(manual,600);assert.equal(manual.command,.6);assert(Math.abs(manual.speed-.6)<1e-6);assert.equal(manual.trip,null);
const disturbed=d.create({});d.step(disturbed,600);d.update(disturbed,{gain:12,ambient:30,condUA:18});d.step(disturbed,600);assert.equal(disturbed.trip,null);assert(Math.abs(balance(disturbed))<.0001);assert.throws(()=>d.update(disturbed,{thermalMass:40}),/Reset/);
const staged=d.create({compressors:3,gain:30});for(let i=0;i<180;i++)d.step(staged,10);assert.equal(staged.trip,null);assert.equal(staged.stages,3);assert.equal(staged.starts,3);assert(staged.events.some(e=>e.text==='Compressor stage 3 enabled'));assert(Math.abs(balance(staged))<.0001);
assert.throws(()=>d.update(staged,{compressors:2}),/Reset/);d.update(staged,{suctionTarget:8});d.step(staged,600);assert(staged.events.some(e=>/retained after unloading/.test(e.text)));
const manualBank=d.create({compressors:2,mode:'manual',manualSpeed:.5});d.step(manualBank,60);assert.equal(manualBank.stages,2);assert.equal(manualBank.starts,2);assert.equal(manualBank.trip,null);
const timers=d.create({minOn:120,minOff:120,thermalMass:1});for(let i=0;i<360;i++)d.step(timers,10);
let lastOn=null,lastOff=null;for(const e of timers.events){if(e.text==='Thermostat requested cooling'){if(lastOff!==null)assert(e.seconds-lastOff>=120);lastOn=e.seconds;}if(e.text==='Thermostat satisfied'){assert(e.seconds-lastOn>=120);lastOff=e.seconds;}}
console.log(JSON.stringify({passed:true,coupledCases:cases,baseQ:base.r.Q,weakEvapQ:weakEvap.r.Q,weakCondPressure:weakCond.r.pHigh,basePressure:base.r.pHigh,eightHourStarts:a.starts,roomEnergyResidualKJ:balance(a),stepRefinementTemperatureK:Math.abs(a.T-refined.T),stepRefinementElectricityPercent:100*Math.abs(a.energy/refined.energy-1)},null,2));
