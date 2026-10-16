'use strict';
// Illustrative inputs, not manufacturer data. Uniform axial homogenization of fins.
const {ANCHOR_K}=require('./thermal-network.cjs');
const defaults=Object.freeze({
 tube:{outerDiameterM:.024,densityKgM3:7850,cpKJKgK:.470,conductivityWMK:45},
 fins:{count:1910,outerDiameterM:.080,thicknessM:.0002,densityKgM3:2700,cpKJKgK:.900,conductivityWMK:205},
 air:{volumeM3:5,massKg:6,cvKJKgK:.718,cpKJKgK:1.005},airCoefficientWM2K:50,contactConductanceKWK:2
});
function positive(v,name){if(!Number.isFinite(v)||v<=0)throw Error(`Positive ${name} required.`);}
function fields(obj,allowed){if(!obj||typeof obj!=='object'||Array.isArray(obj)||Object.keys(obj).some(k=>!allowed.includes(k)))throw Error('Unsupported thermal geometry/configuration field.');}
function geometry(options={}){
 fields(options,['tube','fins','air','airCoefficientWM2K','contactConductanceKWK']);
 const p={...defaults,...options,tube:{...defaults.tube,...options.tube},fins:{...defaults.fins,...options.fins},air:{...defaults.air,...options.air}};
 for(const group of ['tube','fins','air']){fields(p[group],Object.keys(defaults[group]));for(const [k,v]of Object.entries(p[group]))positive(v,k);}
 positive(p.airCoefficientWM2K,'air coefficient');positive(p.contactConductanceKWK,'contact conductance');
 const boreM=.020,volumeM3=.003,lengthM=volumeM3/(Math.PI*boreM**2/4),d=p.tube.outerDiameterM,f=p.fins;
 if(d<=boreM||f.outerDiameterM<=d||!Number.isInteger(f.count)||f.count*f.thicknessM>=lengthM||p.air.cpKJKgK<=p.air.cvKJKgK)throw Error('Inconsistent geometry or air heat capacities.');
 const tubeVolumeM3=Math.PI/4*(d*d-boreM*boreM)*lengthM,finPlanM2=Math.PI/4*(f.outerDiameterM**2-d*d);
 const finVolumeM3=f.count*finPlanM2*f.thicknessM,finAreaM2=f.count*(2*finPlanM2+Math.PI*f.outerDiameterM*f.thicknessM);
 const bareTubeAreaM2=Math.PI*d*(lengthM-f.count*f.thicknessM),innerAreaM2=Math.PI*boreM*lengthM;
 const tubeMassKg=p.tube.densityKgM3*tubeVolumeM3,finMassKg=f.densityKgM3*finVolumeM3;
 return {assumption:'Illustrative constant-property lumped network; uniformly homogenized annular fins; constant forced convection; perfect bulk air mixing.',parameters:p,
  boreM,refrigerantVolumeM3:volumeM3,lengthM,tubeVolumeM3,finVolumeM3,tubeMassKg,finMassKg,finAreaM2,bareTubeAreaM2,innerAreaM2,finPitchM:lengthM/f.count,
  tubeCapacityKJK:tubeMassKg*p.tube.cpKJKgK,finCapacityKJK:finMassKg*f.cpKJKgK,airCapacityKJK:p.air.massKg*p.air.cvKJKgK,
  airTubeConductanceKWK:bareTubeAreaM2*p.airCoefficientWM2K/1000,airFinConductanceKWK:finAreaM2*p.airCoefficientWM2K/1000,
  contactConductanceKWK:p.contactConductanceKWK,radialWallConductanceKWK:2*Math.PI*p.tube.conductivityWMK*lengthM/Math.log(d/boreM)/1000,
  proposedRefrigerantConductanceKWK:.60,activeRefrigerantConductanceKWK:0};
}
function profileIntegral(profile,left,right,domain){
 if(typeof profile==='number'){if(!Number.isFinite(profile)||profile<domain[0]||profile>domain[1])throw Error('Unsupported profile temperature.');return profile*(right-left);}
 if(!Array.isArray(profile)||!profile.length)throw Error('A temperature or piecewise-constant physical profile is required.');
 let end=0,result=0;
 for(const bin of profile){
  fields(bin,['left','right','temperatureK']);
  if(bin.left!==end||!Number.isFinite(bin.right)||bin.right<=bin.left||bin.right>1||!Number.isFinite(bin.temperatureK)||bin.temperatureK<domain[0]||bin.temperatureK>domain[1])throw Error('Profile must cover [0,1] contiguously in supported temperatures.');
  result+=Math.max(0,Math.min(right,bin.right)-Math.max(left,bin.left))*bin.temperatureK;end=bin.right;
 }
 if(end!==1)throw Error('Profile must cover the whole physical length.');return result;
}
function createThermalConfig(options={}){
 fields(options,['sectionCount','geometry','tubeProfileK','finProfileK','airInitialK','airLoadKW','airReservoirK','schedule','energyReferenceK','domainK']);
 const n=options.sectionCount??5;if(![5,9].includes(n))throw Error('Stage 1 allocation permits five or nine sections only.');
 const g=geometry(options.geometry),domain=options.domainK||[200,400],tube=options.tubeProfileK??273.15,fin=options.finProfileK??283.15;
 const airK=options.airInitialK??293.15,reservoir=options.airReservoirK!==undefined;
 if(reservoir&&options.airLoadKW!==undefined)throw Error('A reservoir has no finite-air load state.');
 const nodes=[],links=[],allocation=[];
 for(let i=0;i<n;i++){
  const left=i/n,right=(i+1)/n,fraction=right-left;
  // Integral of physical energy density -> cell energy -> temperature, never
  // interpolate old cell centers or round a fractional fin-equivalent count.
  const tt=profileIntegral(tube,left,right,domain)/fraction,tf=profileIntegral(fin,left,right,domain)/fraction;
  nodes.push({id:`tube-${i}`,capacityKJK:g.tubeCapacityKJK*fraction,initialK:tt},{id:`fin-${i}`,capacityKJK:g.finCapacityKJK*fraction,initialK:tf});
  links.push({id:`air-tube-${i}`,from:'air',to:`tube-${i}`,conductanceKWK:g.airTubeConductanceKWK*fraction},
   {id:`air-fin-${i}`,from:'air',to:`fin-${i}`,conductanceKWK:g.airFinConductanceKWK*fraction},
   {id:`fin-tube-${i}`,from:`fin-${i}`,to:`tube-${i}`,conductanceKWK:g.contactConductanceKWK*fraction});
  allocation.push({left,right,fraction,finEquivalents:g.parameters.fins.count*fraction,tubeMassKg:g.tubeMassKg*fraction,finMassKg:g.finMassKg*fraction,
   tubeCapacityKJK:g.tubeCapacityKJK*fraction,finCapacityKJK:g.finCapacityKJK*fraction,finAreaM2:g.finAreaM2*fraction,bareTubeAreaM2:g.bareTubeAreaM2*fraction,
   initialTubeEnergyKJ:g.tubeCapacityKJK*profileIntegral(tube,left,right,domain)-g.tubeCapacityKJK*fraction*ANCHOR_K,
   initialFinEnergyKJ:g.finCapacityKJK*profileIntegral(fin,left,right,domain)-g.finCapacityKJK*fraction*ANCHOR_K});
 }
 if(!reservoir)nodes.push({id:'air',capacityKJK:g.airCapacityKJK,initialK:airK});
 return {nodes,links,reservoirs:reservoir?{air:options.airReservoirK}:{},loadsKW:reservoir?{}:{air:options.airLoadKW??0},schedule:options.schedule||[],energyReferenceK:options.energyReferenceK??ANCHOR_K,domainK:domain,
  metadata:{sectionCount:n,geometry:g,allocation,airClosure:reservoir?'Prescribed-temperature external reservoir, signed external energy ledger.':'Fixed-volume/fixed-mass ideal-gas internal energy; perfectly mixed; pressure dynamics and ventilation omitted.'}};
}
module.exports={geometry,createThermalConfig,profileIntegral};
