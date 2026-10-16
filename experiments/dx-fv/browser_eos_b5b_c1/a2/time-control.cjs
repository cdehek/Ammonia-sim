'use strict';
// Estimates the error of TWO half steps; never extrapolates the accepted inventory.
function estimate(coarse,fine,initial,order,settings){
 const divisor=2**order-1,terms=[];
 for(let i=0;i<fine.cells.length;i++){
  for(const [key,absolute]of [['massKg',settings.massAbsoluteKg],['internalEnergyKJ',settings.energyAbsoluteKJ]]){
   const scale=absolute+settings.relativeTolerance*Math.max(Math.abs(initial.cells[i][key]),Math.abs(fine.cells[i][key]));
   terms.push(Math.abs(fine.cells[i][key]-coarse.cells[i][key])/divisor/scale);
  }
  // Inventory convergence alone can conceal pressure/enthalpy error near saturation.
  for(const [key,absolute]of [['p',settings.pressureAbsoluteBar],['h',settings.enthalpyAbsoluteKJkg]]){
   const scale=absolute+settings.relativeTolerance*Math.max(Math.abs(initial.states[i][key]),Math.abs(fine.states[i][key]));
   terms.push(Math.abs(fine.states[i][key]-coarse.states[i][key])/divisor/scale);
  }
 }
 return Math.max(...terms);
}
function factor(error,order,accepted){
 const value=error===0?2:.85*error**(-1/(order+1));
 return Math.max(.1,Math.min(accepted?2:.8,value));
}
// Crossings use actual h minus saturation h, not a superheat clamp or quality flag.
function crossings(before,after,saturation){
 const result=[];
 before.forEach((a,i)=>{const b=after[i],sa=saturation(a.p),sb=saturation(b.p);
  for(const [boundary,key]of [['liquid','hf'],['vapor','hg']]){
   const left=a.h-sa[key],right=b.h-sb[key];
   if((left<0&&right>=0)||(left>=0&&right<0))result.push({section:i,boundary,direction:right>left?'heating':'cooling',left,right});
  }
 });return result;
}
const adaptiveDefaults=Object.freeze({method:'tr-bdf2',adaptive:true,maxStep:.5,minStep:1e-9,relativeTolerance:1e-6,massAbsoluteKg:1e-11,energyAbsoluteKJ:1e-8,pressureAbsoluteBar:1e-6,enthalpyAbsoluteKJkg:1e-4,eventStepSeconds:.002});
module.exports={estimate,factor,crossings,adaptiveDefaults};
