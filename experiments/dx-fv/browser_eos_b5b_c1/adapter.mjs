// C1 research classification wrapper. All property work and strict guards are
// delegated to the byte-preserved historical adapter and B4C loader.
import {createAdapter as historicalAdapter} from '../browser_eos_backend/adapter.mjs';
export function bits(x) {
 const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);
 return d.getBigUint64(0).toString(16).padStart(16,'0');
}
export const pack=s=>({values:{...s},bits:Object.fromEntries(Object.entries(s).filter(([,v])=>typeof v==='number').map(([k,v])=>[k,bits(v)]))});
const pressureSupport=p=>Number.isFinite(p)&&p>=30000&&p<=3500000?'supported':'unsupported';
export function errorJSON(e) {
 return {message:e.message??String(e),faultKind:e.faultKind??null,evidence:e.evidence??null,
   propertyCause:e.propertyCause??null,domainCause:e.domainCause??null,nonlinearResidual:e.nonlinearResidual??null};
}
export function createAdapter(eos,domainGuard) {
 let context=null;
 const tracedEOS={evaluate(request){
  if(context)context.lastRequest=request;
  try {const raw=eos.evaluate(request);if(context){context.raw=raw;if(request.mode==='DU'||request.mode==='PH')context.primaryRaw=raw;}return raw;}
  catch(e){if(context)context.source='EOS';throw e;}
 }};
 const tracedGuard={ph(p,h){try{return domainGuard.ph(p,h);}catch(e){if(context)context.source='table-PH-guard';throw e;}}};
 const base=historicalAdapter(tracedEOS,tracedGuard);
 function operation(name,input,fn) {
  const prior=context,c={};context=c;
  try{return fn();}
  catch(cause){
   const raw=c.primaryRaw;
   const explicit=name!=='stateMVU';
   const inputPressure=explicit?input.p*1e5:null;
   const invalidInventory=name==='stateMVU'&&!(input.massKg>0&&input.volumeM3>0&&Number.isFinite(input.internalEnergyKJ));
   const explicitRefusal=explicit&&(pressureSupport(inputPressure)==='unsupported'||c.source==='table-PH-guard'||!Number.isFinite(input.h??0));
   const reason=explicitRefusal||invalidInventory?'explicit-unsupported-input':
     raw&&c.source!=='EOS'?'boundary-unresolved':'inverse-recovery-failure';
   const kind=reason==='explicit-unsupported-input'&&explicit?'domain':'solver';
   const diagnostics={schemaVersion:'C1/1',operation:name,inputScope:explicit?'requested-coordinate':'fixed-inventory',
    input:pack(input),rawRecovery:raw?'returned':'failed',rawCoordinates:raw?pack(raw):null,
    lastRequest:c.lastRequest?{mode:c.lastRequest.mode,args:c.lastRequest.args.map(v=>({value:v,bits:bits(v)}))}:null,
    requestedInputSupport:explicit?pressureSupport(inputPressure):'unknown',
    returnedCoordinateSupport:raw?pressureSupport(raw.p):'unknown',exactInventorySupport:'unknown',
    checks:{support:reason==='boundary-unresolved'||explicitRefusal?'fail':'unmeasured',
     phase:'unmeasured',canonical:'unmeasured',nonlinear:'unmeasured'},
    observedResiduals:raw&&name==='stateMVU'?{densityResidual:(raw.rho-input.massKg/input.volumeM3)/(input.massKg/input.volumeM3),
     energyResidualKJkg:raw.u/1000-input.internalEnergyKJ/input.massKg}:null,
    physicalTrajectoryExit:'unproved',reason,errorSource:c.source??'adapter-support-or-inventory',
    originalError:{message:cause.message??String(cause),faultKind:cause.faultKind??null},
    numericalPressureEnclosure:false};
   throw Object.assign(Error(cause.message??String(cause)),{faultKind:kind,evidence:{propertyFailure:diagnostics}});
  }finally{context=prior;}
 }
 return {counts:base.counts,
  ph:(p,h)=>operation('ph',{p,h},()=>base.ph(p,h)),
  sat:p=>operation('sat',{p},()=>base.sat(p)),
  stateMVU:(massKg,volumeM3,internalEnergyKJ,guess)=>operation('stateMVU',{massKg,volumeM3,internalEnergyKJ,guess},()=>base.stateMVU(massKg,volumeM3,internalEnergyKJ,guess))};
}
