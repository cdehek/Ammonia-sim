/* Stage 1: explicit equilibrium starting inventories, not a transient solver. */
(function(root){
'use strict';
function createInitializer(engine,profiles){
 function preview(profile){
  const p=profiles.normalize(profile),{volumes,initialization:init}=p.inventory;
  if(!init)return {ready:false,status:'unconfigured',message:'Initialization not configured. Existing live calculations remain available.'};
  const low=engine.sat(init.suctionPressure),high=engine.sat(init.dischargePressure);
  const fractions={...init.liquidFractions};
  const mass=(v,f,s)=>v*(f*s.rhof+(1-f)*s.rhog);
  const otherMass=mass(volumes.evaporator,fractions.evaporator,low)+mass(volumes.condenser,fractions.condenser,high);
  const minCharge=otherMass+volumes.receiver*high.rhog,maxCharge=otherMass+volumes.receiver*high.rhof;
  if(init.mode==='charge'){
   const f=(init.chargeKg-minCharge)/(maxCharge-minCharge);
   if(f< -1e-10||f>1+1e-10)return {ready:false,status:'invalid',message:'Total charge cannot fit the receiver at these pressures, volumes and other fills. Feasible charge: '+minCharge.toFixed(3)+'–'+maxCharge.toFixed(3)+' kg.',minChargeKg:minCharge,maxChargeKg:maxCharge};
   fractions.receiver=Math.max(0,Math.min(1,f));
  }
  const vessels={},warnings=[];
  let totalMassKg=0,totalInternalEnergyKJ=0;
  for(const key of ['receiver','evaporator','condenser']){
   const sat=key==='evaporator'?low:high,V=volumes[key],f=fractions[key];
   const liquidMassKg=V*f*sat.rhof,vaporMassKg=V*(1-f)*sat.rhog,massKg=liquidMassKg+vaporMassKg;
   // p in bar -> kPa; h in kJ/kg. u = h - p/rho for each phase.
   const liquidU=sat.hf-sat.p*100/sat.rhof,vaporU=sat.hg-sat.p*100/sat.rhog;
   const internalEnergyKJ=liquidMassKg*liquidU+vaporMassKg*vaporU;
   vessels[key]={volumeM3:V,pressureBarAbsolute:sat.p,temperatureC:sat.T,liquidVolumeFraction:f,liquidMassKg,vaporMassKg,massKg,vaporMassFraction:vaporMassKg/massKg,internalEnergyKJ};
   totalMassKg+=massKg;totalInternalEnergyKJ+=internalEnergyKJ;
   if(f===0||f===1)warnings.push(key+' starts as a single saturated phase; phase-boundary handling will be required in stage 2.');
  }
  return {ready:true,status:'configured',mode:init.mode,totalMassKg,totalInternalEnergyKJ,minChargeKg:minCharge,maxChargeKg:maxCharge,vessels,warnings,assumptions:'Three isolated fixed volumes at saturated phase equilibrium; receiver and condenser at initial discharge pressure, evaporator at initial suction pressure. Connected piping, compressor and valve holdup and metal energy are excluded. This is an initialization preview, not a running inventory simulation.'};
 }
 return {preview};
}
const api={createInitializer};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaInventory=api;
})(typeof globalThis!=='undefined'?globalThis:this);
