'use strict';
const {observe,delta}=require('./spatial-observables.cjs');
const meshes=Object.freeze([3,5,9]);
// 45 bins are the LCM accounting grid, not additional thermodynamic cells.
function enrich(row,spec,engine){
 const state=row.sections.at(-1),outflow=row.portOutflowKgS,h=outflow>=0?state.h:spec.outlet.h;
 try{const trace=engine.ph(spec.outlet.p,h);row.outletTrace={p:trace.p,h:trace.h,T:trace.T,quality:trace.x,superheatK:Math.max(0,trace.T-engine.sat(trace.p).T),wet:trace.x!==null?trace.x<1:trace.phase.includes('liquid'),supported:true};}
 catch(error){row.outletTrace={p:spec.outlet.p,h,supported:false,reason:error.message};}
 // Instantaneous diagnostic rates. No state, ledger, heat or flux is modified.
 row.localBudget=row.sections.map((v,i)=>{const left=row.pressureDrop.faces[i],right=row.pressureDrop.faces[i+1],donorH=(face,index)=>face.massKgS>=0?(index===0?spec.inlet.h:row.sections[index-1].h):(index===row.sections.length?spec.outlet.h:row.sections[index].h);
  const massRate=left.massKgS-right.massKgS,advectiveEnergy=left.massKgS*donorH(left,i)-right.massKgS*donorH(right,i+1),u=v.internalEnergyKJ/v.massKg,heat=spec.heatKW[i];
  return {heatKW:heat,massRateKgS:massRate,advectiveEnergyKW:advectiveEnergy,internalEnergyRateKW:heat+advectiveEnergy,specificHeatRateKJkgS:heat/v.massKg,specificAdvectionRateKJkgS:(advectiveEnergy-u*massRate)/v.massKg,specificInternalEnergyRateKJkgS:(heat+advectiveEnergy-u*massRate)/v.massKg};
 });return row;
}
function measurement(record,spec,engine){return enrich(observe(record,spec,engine,45),spec,engine);}
function difference(a,b){const d=delta(a,b);d.outletTrace=a.outletTrace.supported&&b.outletTrace.supported?{enthalpyKJkg:b.outletTrace.h-a.outletTrace.h,temperatureK:b.outletTrace.T-a.outletTrace.T,superheatK:b.outletTrace.superheatK-a.outletTrace.superheatK,wetDisagrees:a.outletTrace.wet!==b.outletTrace.wet}:null;return d;}
function contraction(d35,d59){const metrics={};for(const key of ['totalMassKg','totalLiquidKg','pipePressureDropBar','profileMassL1Kg','profileEnergyL1KJ'])metrics[key]={delta35:d35[key],delta59:d59[key],absoluteRatio:Math.abs(d35[key])>1e-15?Math.abs(d59[key]/d35[key]):null};
 for(const key of ['enthalpyKJkg','temperatureK','superheatK'])if(d35.outletTrace&&d59.outletTrace)metrics['outlet_'+key]={delta35:d35.outletTrace[key],delta59:d59.outletTrace[key],absoluteRatio:Math.abs(d35.outletTrace[key])>1e-15?Math.abs(d59.outletTrace[key]/d35.outletTrace[key]):null};return metrics;}
module.exports={meshes,measurement,enrich,difference,contraction};
