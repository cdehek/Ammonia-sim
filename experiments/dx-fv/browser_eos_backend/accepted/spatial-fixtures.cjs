'use strict';
const {normalize}=require('./evaporator.cjs');
const geometry=Object.freeze({totalVolumeM3:.003,diameterM:.02,viscosityPaS:1e-5,darcyF:.02,inletMinorK:1000,outletMinorK:2});
// Comparisons are explicitly limited to the three approved meshes. The component
// itself stays configurable; a finer integrated mesh requires another approval.
function heatInputs(n,total,profile='uniform'){
 if(![3,5,9].includes(n))throw Error('Only three/five/nine sections are approved for this comparison.');
 if(!Number.isFinite(total)||!['uniform','graded'].includes(profile))throw Error('Invalid distributed heat fixture.');
 return Array.from({length:n},(_,i)=>{const a=i/n,b=(i+1)/n;return total*(profile==='uniform'?b-a:.5*(b-a)+.5*(b*b-a*a));});
}
function fixture(n,{totalHeatKW=18,profile='uniform',initial={p:3.5,h:500}}={}){
 const heatKW=heatInputs(n,totalHeatKW,profile);
 return normalize({...geometry,sectionCount:n,inlet:{p:4,h:500},outlet:{p:3.5,h:1700},initial:Array.from({length:n},()=>({...initial})),heatKW});
}
function cases(n){
 const patchHeat=(q,profile='uniform')=>({heatKW:heatInputs(n,q,profile)});
 const common={profile:'uniform'};
 return [
  {name:'warm startup',config:fixture(n,{...common,totalHeatKW:12,initial:{p:3.65,h:1650}}),samples:[.01,.05,.2,.6,1,2,5,15],changes:[]},
  {name:'cold wet startup',config:fixture(n,common),samples:[.01,.05,.2,.6,1,1.9,2,5,15,30,60],changes:[]},
  {name:'load loss and restoration',config:fixture(n,common),samples:[1,2,5,15,15.1,15.4,15.5,17,20,30,30.1,30.5,31.11,32,35,45],changes:[{seconds:15,patch:patchHeat(12)},{seconds:30,patch:patchHeat(18)}]},
  {name:'feed increase and decrease',config:fixture(n,common),samples:[1,2,5,15,15.1,15.4,15.5,17,20,30,30.1,30.5,30.95,32,35,45],changes:[{seconds:15,patch:{inlet:{p:4.3,h:500}}},{seconds:30,patch:{inlet:{p:4,h:500}}}]},
  {name:'graded heat cold startup',config:fixture(n,{profile:'graded'}),samples:[.01,.05,.2,.6,1,2,2.1,5,15,30,60],changes:[]}
 ];
}
function numericalOptions(tolerance){
 return {adaptive:true,method:'tr-bdf2',relativeTolerance:tolerance,massAbsoluteKg:1e-5*tolerance,energyAbsoluteKJ:.01*tolerance,pressureAbsoluteBar:Math.max(1e-6,.1*tolerance),enthalpyAbsoluteKJkg:100*tolerance,minStep:1e-9};
}
module.exports={geometry,fixture,heatInputs,cases,numericalOptions};
