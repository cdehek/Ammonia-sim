// Minimum isolated interface extension for accepted hot-refrigerant boundary
// fixtures. Original B1 adapter/source and all PH/DU behavior remain unchanged.
// Uses the existing PT flash, with no PH reflash, property correction or clamp.
export function withPT(base,eos,guard){
 base.counts.statePT=0;
 return {...base,statePT(p,T,kind){
  base.counts.statePT++;
  if(kind!==undefined)throw Error('B2 PT mapping supports unambiguous, unimposed PT only; phase-imposed interface is not supplied.');
  if(!Number.isFinite(p)||p<.3||p>35||!Number.isFinite(T))throw Object.assign(Error('Outside accepted PT input domain'),{faultKind:'domain'});
  const raw=eos.evaluate({mode:'PT',args:[p*1e5,T+273.15]}),h=raw.h/1000;
  guard.ph(p,h);const sat=base.sat(p),x=raw.Q>=0&&raw.Q<=1?raw.Q:null;
  if(raw.T<195.495||raw.T-273.15<sat.T-30||raw.T-273.15>sat.T+250)throw Object.assign(Error('EOS PT outside original physical temperature envelope'),{faultKind:'domain'});
  const phase=x===null?(h<sat.hf?'Subcooled liquid':'Superheated vapor'):x===0?'Saturated liquid':x===1?'Saturated vapor':'Liquid + vapor';
  return {p,h,T:raw.T-273.15,s:raw.s/1000,rho:raw.rho,u:raw.u/1000,x,phase};
 }};
}
