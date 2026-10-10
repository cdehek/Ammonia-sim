'use strict';
// Diagnostic availability probe only. It does not classify a trajectory exit,
// run a new physical closure, modify a table, or alter any reference generator.
const fs=require('node:fs');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createThermodynamics}=require('./thermodynamics.cjs'),C=require('./conservation.cjs');
const thermo=createThermodynamics(engine);
function runtimeSupport(point){
 const output={p:point.p,h:point.h,physicalTemperatureK:point.temperatureK};
 try{
  const state=thermo.ph(point.p,point.h);output.ph={supported:true,temperatureK:state.T+273.15,phase:state.phase};
  const volumeM3=.003/5,cell={...C.inventory(state,volumeM3),volumeM3,pressureGuess:point.p};
  const recovered=thermo.recover(cell);
  output.tableInventoryRecovery={supported:true,consistentWithStage:Math.abs(recovered.p-state.p)<=1e-6&&Math.abs(recovered.h-state.h)<=1e-4&&Math.abs(recovered.T-state.T)<=1e-4,
   pressureDifferenceBar:recovered.p-state.p,enthalpyDifferenceKJkg:recovered.h-state.h,temperatureDifferenceK:recovered.T-state.T};
 }catch(error){output.ph=output.ph||{supported:false,message:error.message,kind:error.faultKind||'solver'};
  if(output.ph.supported)output.tableInventoryRecovery={supported:false,message:error.message,kind:error.faultKind||'solver'};}
 if(Number.isFinite(point.rho)&&Number.isFinite(point.u)){
  try{
   const state=thermo.recover({massKg:point.rho*.003/5,internalEnergyKJ:point.rho*.003/5*point.u,volumeM3:.003/5,pressureGuess:point.p});
   output.directEOSInventoryRecovery={supported:true,p:state.p,h:state.h,temperatureK:state.T+273.15};
  }catch(error){output.directEOSInventoryRecovery={supported:false,message:error.message,kind:error.faultKind||'solver'};}
 }
 return output;
}
if(require.main===module){const points=JSON.parse(fs.readFileSync(0,'utf8'));if(!Array.isArray(points))throw Error('Array of PH diagnostic points required.');console.log(JSON.stringify({runtime:process.version,points:points.map(runtimeSupport)}));}
module.exports={runtimeSupport};
