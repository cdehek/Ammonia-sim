export const BACKEND='A2-table-B9C-b67afb3';
export const SOURCE={acceptedA2:'be9eb35a4ddf5098e685182f8104685127c6a6ee',optimizedB9C:'b67afb3215075b2ec82bef376d39e03953dc0da2',bundleSHA256:'f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919'};
export const QUALIFICATION='Bounded five-section table-backed research; uncalibrated conductance; nonqualified prototype; bulk wet is not compressor suction safety.';
export const INTERVALS=[.0001,.0004,.0005];
export function project(r,s,sessionId,acceptedVersion){
 return {protocol:1,backendId:BACKEND,source:{...SOURCE},qualification:QUALIFICATION,sessionId,acceptedVersion,clockSeconds:r.seconds,status:'accepted-state',freshness:'accepted',
 units:{pressure:'bar absolute',refrigerantTemperature:'degC',thermalTemperature:'K',mass:'kg',internalEnergy:'kJ',volume:'m3',enthalpy:'kJ/kg',flow:'kg/s',power:'kW',time:'s',quality:'dimensionless',wet:'boolean'},
 sections:r.sections.map((v,i)=>({pressureBarAbsolute:v.p,temperatureC:v.T,massKg:s.cells[i].massKg,internalEnergyKJ:s.cells[i].internalEnergyKJ,volumeM3:s.cells[i].volumeM3,enthalpyKJkg:v.h,phase:v.phase,quality:v.x,wet:v.wet,superheatK:v.superheatK})),
 nodes:r.nodes.map(n=>({id:n.id,temperatureK:n.temperatureK,energyKJ:n.energyKJ})),
 flows:{inlet:{...r.fluxes.faces[0]},outlet:{...r.fluxes.faces.at(-1)},scope:'instantaneous signed accepted-endpoint faces; positive inlet-to-outlet'},
 totals:{...r.totals},conservation:{massResidualKg:r.massResidualKg,refrigerantEnergyResidualKJ:r.refrigerantEnergyResidualKJ,thermalEnergyResidualKJ:r.thermalEnergyResidualKJ,combinedEnergyResidualKJ:r.combinedEnergyResidualKJ,boundaryMassKg:r.ledger.boundaryMassKg,boundaryEnthalpyKJ:r.ledger.boundaryEnthalpyKJ,airLoadKJ:r.ledger.airLoadKJ},
 stop:structuredClone(r.stop),unavailable:{compressorState:null,compressorPerformance:null,condenserHeatRejection:null,receiverInventory:null,receiverLevels:null,valveActuator:null,equipmentSafetyTrips:null,plantWideBalance:null}};
}
