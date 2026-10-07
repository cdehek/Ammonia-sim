/* Conservative fixed-volume equilibrium storage. Stage 3 adds conservative connected valve flow and outlet control. */
(function(root){
'use strict';
const names=['receiver','evaporator','condenser'];
function createStorage(engine,profiles,numerics={}){
 const valves=(typeof module!=='undefined'&&module.exports?require('./valve-engine'):root.AmmoniaValves).createValves(engine);
 const initializer=(typeof module!=='undefined'&&module.exports?require('./inventory-initialization'):root.AmmoniaInventory).createInitializer(engine,profiles);
 const maxStep=numerics.maxStep??.1,minStep=numerics.minStep??.00001,tolerance=numerics.tolerance??1e-5;
 if(!Number.isFinite(maxStep)||maxStep<.001||maxStep>1||!Number.isFinite(minStep)||minStep<=0||minStep>maxStep||!Number.isFinite(tolerance)||tolerance<=0)throw Error('Invalid storage integration settings.');
 function stop(kind,message,readings){const error=new Error(message);error.faultKind=kind;error.readings=readings;return error;}
 function validateOperations(o={}){
  const c={thermalMode:'sealed',receiverHeat:0,evaporatorHeat:0,condenserHeat:0,compressorOn:false,speed:.25,circuit:'closed',valveMode:'closed',manualOpening:.25,superheatTarget:5,kp:.04,ki:.004,drainEnabled:true,...o};
  if(!['sealed','air'].includes(c.thermalMode)||typeof c.compressorOn!=='boolean')throw Error('Invalid storage operating mode.');
  for(const key of ['receiverHeat','evaporatorHeat','condenserHeat'])if(!Number.isFinite(c[key])||Math.abs(c[key])>1000)throw Error('Storage heat rates must be finite, between −1000 and 1000 kW.');
  if(!Number.isFinite(c.speed)||c.speed<.2||c.speed>1)throw Error('Storage compressor speed must be 20–100%.');
  if(!['closed','circulating'].includes(c.circuit)||!['closed','manual','auto'].includes(c.valveMode)||typeof c.drainEnabled!=='boolean')throw Error('Invalid connected-loop controls.');
  for(const [key,[low,high]]of Object.entries({manualOpening:[0,1],superheatTarget:[1,30],kp:[0,1],ki:[0,1]}))if(!Number.isFinite(c[key])||c[key]<low||c[key]>high)throw Error(key+' is outside its operating range.');
  return c;
 }
 function recover(raw){const states={};for(const key of Object.keys(raw.vessels)){const v=raw.vessels[key];states[key]=engine.stateMVU(v.massKg,v.volumeM3,v.internalEnergyKJ,v.guess);}return states;}
 function create(profile,roomConfig={},operations={}){
  const clean=profiles.normalize(profile),preview=initializer.preview(clean);
  if(!preview.ready)throw Error(preview.message);
  const room={initial:15,thermalMass:30,leakUA:.1,gain:2,ambient:25,...roomConfig};
  for(const key of ['initial','thermalMass','leakUA','gain','ambient'])if(!Number.isFinite(room[key]))throw Error('Invalid storage room condition: '+key);
  if(room.thermalMass<=0||room.leakUA<0||room.gain<0||room.initial< -40||room.initial>50||room.ambient< -20||room.ambient>45)throw Error('Storage room conditions are outside the supported domain.');
  const vessels={};for(const key of names){const v=preview.vessels[key];vessels[key]={massKg:v.massKg,volumeM3:v.volumeM3,internalEnergyKJ:v.internalEnergyKJ,guess:v.pressureBarAbsolute};}
  const ops=validateOperations(operations);
  if(ops.circuit==='circulating'){
   if(!clean.connections)throw Error('Configure valve and outlet geometry in the equipment profile before initializing circulation.');
   const v=vessels.evaporator,volume=v.volumeM3*clean.connections.outletVolumeFraction,dry=engine.statePT(v.guess,engine.sat(v.guess).T+clean.connections.outletInitialSuperheatK),mass=volume*dry.rho,energy=mass*(dry.h-100*dry.p/dry.rho);
   if(preview.vessels.evaporator.liquidVolumeFraction>1-clean.connections.outletVolumeFraction)throw Error('Initial evaporator vapor space cannot contain the configured dry outlet volume.');
   vessels.outlet={massKg:mass,volumeM3:volume,internalEnergyKJ:energy,guess:v.guess};v.massKg-=mass;v.volumeM3-=volume;v.internalEnergyKJ-=energy;
  }
  const s={profile:clean,roomConfig:room,operations:ops,controller:{opening:0,sensor:0,integral:0},gravityEnergyKJ:0,time:0,pending:0,T:room.initial,vessels,states:null,initialMassKg:preview.totalMassKg,initialEnergyKJ:preview.totalInternalEnergyKJ,externalHeatKJ:0,fluidWorkKJ:0,electricalKWh:0,evaporatorHeatKJ:0,fault:null,rows:[],acceptedSteps:0,rejectedSteps:0};
  s.states=recover(s);if(s.states.outlet)s.controller.sensor=Math.max(0,s.states.outlet.T-engine.sat(s.states.outlet.p).T);s.rows.push(record(s));return s;
 }
 function phaseOutlet(state,phase){
  if(phase==='bulk')return state;
  if(state.x!==null){if(phase==='vapor'&&state.x>1e-10)return engine.statePX(state.p,1);if(phase==='liquid'&&state.x<1-1e-10)return engine.statePX(state.p,0);}
  else if(phase==='vapor'&&['Superheated vapor','Saturated vapor'].includes(state.phase)||phase==='liquid'&&['Subcooled liquid','Saturated liquid'].includes(state.phase))return state;
  throw stop('domain','The requested '+phase+' outlet phase is unavailable in the storage volume.');
 }
 // Port balances consume an explicit flow/enthalpy boundary. Hydraulic laws supply these boundaries without changing the port accounting.
 function portRates(states,transfers=[]){
  const keys=Object.keys(states),rates=Object.fromEntries(keys.map(key=>[key,{mass:0,energy:0}]));let fluidWork=0;
  for(const transfer of transfers){
   if(!keys.includes(transfer.from)||!keys.includes(transfer.to)||transfer.from===transfer.to||!Number.isFinite(transfer.massFlow)||transfer.massFlow<0)throw Error('Invalid storage transfer boundary.');
   if(transfer.massFlow===0)continue;
   const out=phaseOutlet(states[transfer.from],transfer.phase||'bulk'),incoming=transfer.inletEnthalpy??out.h;
   if(!Number.isFinite(incoming))throw Error('Transfer inlet enthalpy must be finite.');
   rates[transfer.from].mass-=transfer.massFlow;rates[transfer.to].mass+=transfer.massFlow;
   rates[transfer.from].energy-=transfer.massFlow*out.h;rates[transfer.to].energy+=transfer.massFlow*incoming;
   fluidWork+=transfer.massFlow*(incoming-out.h);
  }
  return {rates,fluidWork};
 }
 function compressor(s,states,checkTrips=true){
  if(!s.operations.compressorOn)return null;
  const low=states.outlet||states.evaporator,high=states.condenser,c=s.profile.equipment,speed=s.operations.speed;
  const readings={room:s.T,pressure:low.p,condensing:high.p,discharge:null,speed,stages:c.compressors};
  if(checkTrips&&high.p>=c.highTrip)throw stop('equipment','High discharge pressure',readings);
  if(checkTrips&&low.p<=c.lowTrip)throw stop('equipment','Low suction pressure',readings);
  if(high.p<=low.p)throw stop('domain','Compression requires discharge pressure above suction pressure.',readings);
  if(states.outlet&&low.x!==null&&low.x<1-1e-7)throw stop('domain','Wet compressor suction: the resolved outlet is not dry vapor.',readings);
  const suction=phaseOutlet(low,'vapor'),ratio=high.p/low.p,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const etaVol=c.performanceMode==='fixed'?c.etaVol/100:clamp(.88-.035*(ratio-2),.35,.9);
  const etaIs=c.performanceMode==='fixed'?c.etaIs/100:clamp(.78-.004*(ratio-4)**2-.035*(1-speed)**2,.45,.8);
  const etaMotor=c.performanceMode==='fixed'?c.etaMotor/100:clamp(.93-.07*(1-speed)**2,.8,.94);
  const ideal=engine.ps(high.p,suction.s),discharge=engine.ph(high.p,suction.h+(ideal.h-suction.h)/etaIs);
  readings.discharge=discharge.T;
  if(checkTrips&&discharge.T>=c.dischargeTrip)throw stop('equipment','High discharge temperature',readings);
  const massFlow=c.displacement/3600*c.compressors*speed*etaVol*suction.rho;
  const fluidWork=massFlow*(discharge.h-suction.h);
  if(!(fluidWork>0))throw stop('domain','The compressor state does not produce positive compression work.',readings);
  return {massFlow,fluidWork,electrical:fluidWork/etaMotor,dischargeTemperature:discharge.T,suctionEnthalpy:suction.h,dischargeEnthalpy:discharge.h};
 }
 function hydraulics(s,states){
  if(!states.outlet)return null;
  const spec=s.profile.connections,control=valves.controller(s.controller,s.operations,spec,Math.max(0,states.outlet.T-engine.sat(states.outlet.p).T));
  const liquidPort=(from,to,area,opening,recovery,exponent,head=0)=>{
   let out;try{out=phaseOutlet(states[from],'liquid');}catch(error){if(error.faultKind==='domain')return {massFlow:0,status:'liquid unavailable',choked:false};throw error;}
   const flow=valves.liquid(out,states[to].p,area,opening,recovery,exponent,head);
   return {...flow,transfer:{from,to,phase:'liquid',massFlow:flow.massFlow,inletEnthalpy:out.h+(flow.gravityEnthalpy||0)}};
  };
  const feed=liquidPort('receiver','evaporator',spec.feedAreaM2,s.controller.opening,spec.feedRecovery,spec.openingExponent);
  const drain=liquidPort('condenser','receiver',spec.drainAreaM2,s.operations.drainEnabled?1:0,spec.drainRecovery,1,spec.drainHeightM);
  let vapor;try{const out=phaseOutlet(states.evaporator,'vapor');vapor=valves.vapor(out,states.outlet.p,spec.vaporAreaM2);}catch(error){if(error.faultKind==='domain')vapor={massFlow:0,status:'vapor unavailable',choked:false};else throw error;}
  const transfers=[feed.transfer,drain.transfer,{from:'evaporator',to:'outlet',phase:'vapor',massFlow:vapor.massFlow}].filter(Boolean);
  return {feed,drain,vapor,control,transfers,superheat:Math.max(0,states.outlet.T-engine.sat(states.outlet.p).T),gravityWork:drain.massFlow*(drain.gravityEnthalpy||0)};
 }
 function derivatives(s,states,transfers=[],checkTrips=true){
  const c=s.operations,r=s.roomConfig,equipment=s.profile.equipment,comp=compressor(s,states,checkTrips);
  const hydraulic=hydraulics(s,states),boundary=[...transfers,...(hydraulic?.transfers||[])];if(comp)boundary.push({from:states.outlet?'outlet':'evaporator',to:'condenser',massFlow:comp.massFlow,phase:'vapor',inletEnthalpy:comp.dischargeEnthalpy});
  const ports=portRates(states,boundary),heat={receiver:c.receiverHeat,evaporator:c.evaporatorHeat,condenser:c.condenserHeat,...(states.outlet?{outlet:0}:{})};
  if(c.thermalMode==='air'){const outletFraction=states.outlet?s.profile.connections.outletUAFraction:0;heat.evaporator+=equipment.evapUA*(1-outletFraction)*(s.T-states.evaporator.T);if(states.outlet)heat.outlet=equipment.evapUA*outletFraction*(s.T-states.outlet.T);heat.condenser+=equipment.condUA*(r.ambient-states.condenser.T);}
  for(const key of Object.keys(states))ports.rates[key].energy+=heat[key];
  // Applied evaporator heat is exchanged with the room in air mode; otherwise it is an external test source.
  const roomHeat=c.thermalMode==='air'?r.leakUA*(r.ambient-s.T)+r.gain-heat.evaporator-(heat.outlet||0):0;
  const externalHeat=c.thermalMode==='air'?heat.receiver+heat.condenser+r.leakUA*(r.ambient-s.T)+r.gain:heat.receiver+heat.evaporator+heat.condenser+(heat.outlet||0);
  return {...ports,heat,room:roomHeat/(r.thermalMass*1000),externalHeat,electrical:comp?comp.electrical:0,comp,hydraulic,control:hydraulic?.control||{opening:0,sensor:0,integral:0},gravityWork:hydraulic?.gravityWork||0};
 }
 function projected(s,a,dt,b){
  const avg=(x,y)=>b?(x+y)/2:x,trial={...s,vessels:{},T:s.T+dt*avg(a.room,b?.room)};
  trial.controller={};for(const key of ['opening','sensor','integral'])trial.controller[key]=s.controller[key]+dt*avg(a.control[key],b?.control[key]);
  if(!Object.values(trial.controller).every(Number.isFinite)||trial.controller.opening<0||trial.controller.opening>1||trial.controller.sensor<0)throw stop('solver','Controller trial left its bounded state domain.');
  for(const key of Object.keys(s.vessels)){const v=s.vessels[key];trial.vessels[key]={...v,massKg:v.massKg+dt*avg(a.rates[key].mass,b?.rates[key].mass),internalEnergyKJ:v.internalEnergyKJ+dt*avg(a.rates[key].energy,b?.rates[key].energy),guess:s.states[key].p};}
  if(!Number.isFinite(trial.T)||trial.T< -40||trial.T>50)throw stop('domain','Storage room left the supported −40 to 50 °C domain.');
  trial.states=recover(trial);return trial;
 }
 function errorEstimate(euler,heun){
  let error=Math.abs(euler.T-heun.T)/Math.max(1,Math.abs(heun.T));
  for(const key of ['opening','sensor','integral'])error=Math.max(error,Math.abs(euler.controller[key]-heun.controller[key])/Math.max(1,Math.abs(heun.controller[key])));
  for(const key of Object.keys(heun.vessels)){const a=euler.vessels[key],b=heun.vessels[key];error=Math.max(error,Math.abs(a.massKg-b.massKg)/Math.max(.001,b.massKg),Math.abs(a.internalEnergyKJ-b.internalEnergyKJ)/Math.max(1,Math.abs(b.internalEnergyKJ)),Math.abs(euler.states[key].p-heun.states[key].p)/Math.max(.3,heun.states[key].p));}
  return error;
 }
 function latch(s,error){
  s.fault={kind:error.faultKind||'domain',message:error.message,seconds:s.time,readings:error.readings||{room:s.T,pressure:(s.states.outlet||s.states.evaporator).p,condensing:s.states.condenser.p},limits:s.profile.equipment};s.pending=0;
 }
 function advance(s,seconds,transfers=[]){
  if(!Number.isFinite(seconds)||seconds<=0||seconds>3600)throw Error('Advance storage by greater than zero and at most 3600 seconds.');
  if(s.fault)return record(s);
  s.pending+=seconds;let budget=0;
  // Fixed outer intervals make playback chunking invariant; substeps adapt inside each interval.
  while(s.pending>=maxStep-1e-10&&!s.fault){
   let remaining=maxStep,dt=maxStep;
   while(remaining>1e-10&&!s.fault){
    if(++budget>200000){latch(s,stop('solver','Storage integration exceeded its step budget.'));break;}
    dt=Math.min(dt,remaining);let a,euler,b,heun;
    try{
     a=derivatives(s,s.states,transfers);euler=projected(s,a,dt);b=derivatives(euler,euler.states,transfers,false);heun=projected(s,a,dt,b);
     const error=errorEstimate(euler,heun);
     if(error>tolerance){if(dt/2<minStep)throw stop('solver','Storage integration could not meet its error tolerance.');s.rejectedSteps++;dt/=2;continue;}
    }catch(error){
     if(!error.faultKind&&/property table|property domain|superheat/.test(error.message))error.faultKind='domain';
     if(!error.faultKind)throw error;
     if(error.faultKind!=='equipment'&&dt/2>=minStep){s.rejectedSteps++;dt/=2;continue;}
     latch(s,error);break;
    }
    s.vessels=heun.vessels;s.states=heun.states;s.T=heun.T;s.controller=heun.controller;s.time+=dt;s.acceptedSteps++;remaining-=dt;
    s.externalHeatKJ+=dt*(a.externalHeat+b.externalHeat)/2;s.fluidWorkKJ+=dt*(a.fluidWork+b.fluidWork)/2;
    s.gravityEnergyKJ+=dt*(a.gravityWork+b.gravityWork)/2;
    s.electricalKWh+=dt*(a.electrical+b.electrical)/2/3600;s.evaporatorHeatKJ+=dt*(a.heat.evaporator+(a.heat.outlet||0)+b.heat.evaporator+(b.heat.outlet||0))/2;
    try{compressor(s,s.states);}catch(error){if(!error.faultKind&&/property table|property domain|superheat/.test(error.message))error.faultKind='domain';if(!error.faultKind)throw error;latch(s,error);}
    dt=Math.min(maxStep,dt*2);
   }
   if(!s.fault)s.pending=Math.max(0,s.pending-maxStep);
  }
  const row=record(s);if(s.rows[s.rows.length-1].seconds===s.time)s.rows[s.rows.length-1]=row;else s.rows.push(row);if(s.rows.length>7200)s.rows.shift();return row;
 }
 function record(s){
  const keys=Object.keys(s.vessels),totalMassKg=keys.reduce((sum,key)=>sum+s.vessels[key].massKg,0),totalEnergyKJ=keys.reduce((sum,key)=>sum+s.vessels[key].internalEnergyKJ,0),roomEnergyKJ=s.roomConfig.thermalMass*1000*(s.T-s.roomConfig.initial);
  const vessels={};for(const key of keys){const v=s.states[key];vessels[key]={massKg:s.vessels[key].massKg,internalEnergyKJ:s.vessels[key].internalEnergyKJ,p:v.p,T:v.T,phase:v.phase,x:v.x===null?(v.phase.includes('liquid')?0:1):v.x,liquidVolumeFraction:v.liquidVolumeFraction};}
  let flows=null;try{const h=hydraulics(s,s.states);if(h)flows={feed:h.feed,drain:h.drain,vapor:h.vapor,superheat:h.superheat,command:h.control.command};}catch(error){flows={error:error.message};}
  return {seconds:s.time,controller:{...s.controller},flows,gravityEnergyKJ:s.gravityEnergyKJ,T:s.T,totalMassKg,totalEnergyKJ,roomEnergyKJ,massResidualKg:totalMassKg-s.initialMassKg,energyResidualKJ:totalEnergyKJ-s.initialEnergyKJ+roomEnergyKJ-s.externalHeatKJ-s.fluidWorkKJ,electricalKWh:s.electricalKWh,fluidWorkKJ:s.fluidWorkKJ,externalHeatKJ:s.externalHeatKJ,evaporatorHeatKJ:s.evaporatorHeatKJ,operations:{...s.operations},vessels,fault:s.fault,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps};
 }
 function update(s,operations){const next=validateOperations({...s.operations,...operations});if(next.circuit!==s.operations.circuit)throw Error('Reinitialize storage to change circuit geometry.');if(next.valveMode!==s.operations.valveMode&&next.valveMode==='auto')s.controller.integral=s.controller.opening-next.kp*(s.controller.sensor-next.superheatTarget);s.operations=next;}
 function clearFault(s){s.fault=null;s.pending=0;}
 return {create,advance,record,update,clearFault,phaseOutlet,portRates,validateOperations,hydraulics};
}
const api={createStorage};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaStorage=api;
})(typeof globalThis!=='undefined'?globalThis:this);
