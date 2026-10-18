export const qualification='Short five-section accepted table-backed research; uncalibrated conductance; no complete model/backend/operator qualification; bulk wet is not compressor safety';
export function compact(record,state,{status='ready',fault=null}={}){
 const last=record.trace.at(-1);
 return {schemaVersion:1,clockSeconds:record.seconds,acceptedVersion:record.acceptedSteps,status:record.stop?(record.stop.kind==='domain'?'physical-domain-stop':'numerical-stop'):status,
 sections:record.sections.map((s,i)=>({pressureBarAbsolute:s.p,temperatureK:s.T+273.15,massKg:state.cells[i].massKg,internalEnergyKJ:state.cells[i].internalEnergyKJ,phase:s.phase,quality:s.x,wet:s.wet})),
 tubeTemperaturesK:record.nodes.filter(n=>n.id.startsWith('tube-')).map(n=>n.temperatureK),finTemperaturesK:record.nodes.filter(n=>n.id.startsWith('fin-')).map(n=>n.temperatureK),airTemperatureK:record.nodes.find(n=>n.id==='air').temperatureK,
 inlet:{pressureBarAbsolute:state.spec.fluid.inlet.p,enthalpyKJkg:state.spec.fluid.inlet.h,scope:'specified boundary PH only'},terminal:structuredClone(record.terminal),outlet:structuredClone(record.outlet),totalMassKg:record.totals.massKg,totalInternalEnergyKJ:record.totals.internalEnergyKJ,
 accounting:{massResidualKg:record.massResidualKg,combinedEnergyResidualKJ:record.combinedEnergyResidualKJ,boundaryEnthalpyKJ:record.ledger.boundaryEnthalpyKJ,airLoadKJ:record.ledger.airLoadKJ},
 lastAcceptedStepSeconds:last?last.trialSeconds/(record.settings.adaptive?2:1):null,lastFault:fault??structuredClone(record.stop),qualification};
}
