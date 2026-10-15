'use strict';
// Units: kg, kJ, s, bar absolute. Each face is evaluated once and shared.
function inventory(state,volumeM3){
 const massKg=state.rho*volumeM3;
 return {massKg,internalEnergyKJ:massKg*state.h-100*state.p*volumeM3};
}
function flux(massFlowKgS,donor){
 if(!Number.isFinite(massFlowKgS)||!Number.isFinite(donor.h))throw Error('Invalid conservative face flux.');
 return {massKgS:massFlowKgS,energyKW:massFlowKgS*donor.h};
}
function assemble(faces,heatKW){
 if(faces.length!==heatKW.length+1)throw Error('One shared face is required at each section boundary.');
 return heatKW.map((q,i)=>({massKgS:faces[i].massKgS-faces[i+1].massKgS,energyKW:q+faces[i].energyKW-faces[i+1].energyKW}));
}
function totals(cells){return cells.reduce((a,c)=>({massKg:a.massKg+c.massKg,internalEnergyKJ:a.internalEnergyKJ+c.internalEnergyKJ}),{massKg:0,internalEnergyKJ:0});}
module.exports={inventory,flux,assemble,totals};
