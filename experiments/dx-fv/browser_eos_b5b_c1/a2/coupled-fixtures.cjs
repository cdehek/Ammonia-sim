'use strict';
// Initial illustrative operating cases, not equipment calibration or a dry-outlet guarantee.
function fixture(kind='cold', extra={}) {
  if (!['cold','warm'].includes(kind)) throw Error('Unknown coupled startup.');
  const warm=kind==='warm';
  return {sectionCount:5,initial:Array.from({length:5},()=>({p:warm?3.65:3.5,h:warm?1650:500})),
    thermal:warm ? {tubeProfileK:293.15,finProfileK:293.15,airInitialK:293.15,airLoadKW:1}
      : {tubeProfileK:273.15,finProfileK:273.15,airInitialK:278.15,airLoadKW:1},...extra};
}
function cases() {
  const samples=[.01,.05,.2,1,5,15,30,60,120];
  return [
    {name:'cold',config:fixture('cold'),samples},
    {name:'warm',config:fixture('warm'),samples},
    {name:'load-step',config:fixture('cold',{schedule:[{seconds:15,patch:{airLoadKW:2}},{seconds:30,patch:{airLoadKW:1}}]}),samples:[.01,.2,1,5,15,15.1,20,30,30.1,45,60]},
    {name:'feed-step',config:fixture('cold',{schedule:[{seconds:15,patch:{inlet:{p:4.3,h:500}}},{seconds:30,patch:{inlet:{p:4,h:500}}}]}),samples:[.01,.2,1,5,15,15.01,15.1,20,30,30.01,30.1,45,60]},
    // Sealed is the existing closed-face fixture; no changed hydraulic equation.
    {name:'heat-reversal',config:fixture('warm',{sealed:true,thermal:{tubeProfileK:273.15,finProfileK:273.15,airInitialK:278.15,airLoadKW:1}}),samples:[.01,.05,.2,1,5,15,30,60]},
  ];
}
function accuracyOptions(tolerance=1e-6) {
  return {relativeTolerance:tolerance,massAbsoluteKg:1e-5*tolerance,energyAbsoluteKJ:.01*tolerance,
    pressureAbsoluteBar:Math.max(1e-6,.1*tolerance),enthalpyAbsoluteKJkg:100*tolerance,
    temperatureAbsoluteK:100*tolerance,maxStep:tolerance<=1e-8?.125:tolerance<=1e-7?.25:.5,
    eventStepSeconds:tolerance<=1e-8?.0001:tolerance<=1e-7?.0005:.002};
}
module.exports={fixture,cases,accuracyOptions};
