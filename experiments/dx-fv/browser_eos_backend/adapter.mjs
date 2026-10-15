// Research engine-interface adapter. Original balances and solver are untouched.
// Original bar/kJ/kg/degree-C interface semantics retain requested PH coordinates.
// Returned density is the unaltered EOS flash result. Actual PH residuals are
// independently measured in the standalone matrices; no property is corrected.
export function createAdapter(eos,domainGuard){
 const counts={ph:0,sat:0,stateMVU:0,domainGuards:0};
 function sat(p){
  counts.sat++;if(!Number.isFinite(p)||p<.3||p>35)throw Object.assign(Error('Outside accepted pressure domain'),{faultKind:'domain'});
  const s=eos.evaluate({mode:'SAT',args:[p*1e5,0]});
  return {...s,p,T:s.T-273.15,hf:s.hf/1000,hg:s.hg/1000,sf:s.sf/1000,sg:s.sg/1000};
 }
 function guard(p,h){counts.domainGuards++;domainGuard.ph(p,h);}
 function convert(s,p,h){
  guard(p,h);
  const a=sat(p),x=s.Q>=0&&s.Q<=1?s.Q:null;
  const phase=x===null?(h<a.hf?'Subcooled liquid':'Superheated vapor'):x===0?'Saturated liquid':x===1?'Saturated vapor':'Liquid + vapor';
  // The table guard preserves its actual bounded support; also reject a direct
  // EOS state outside the same physical offsets instead of expanding support.
  if(s.T<195.495||s.T-273.15<a.T-30||s.T-273.15>a.T+250)throw Object.assign(Error('EOS state outside original physical temperature envelope'),{faultKind:'domain'});
  return {p,h,T:s.T-273.15,s:s.s/1000,rho:s.rho,u:s.u/1000,x,phase};
 }
 function ph(p,h){counts.ph++;guard(p,h);const s=eos.evaluate({mode:'PH',args:[p*1e5,h*1000]});return convert(s,p,h);}
 function stateMVU(massKg,volumeM3,internalEnergyKJ,guess){
  counts.stateMVU++;
  if(!(massKg>0&&volumeM3>0&&Number.isFinite(internalEnergyKJ)))throw Object.assign(Error('Invalid canonical inventory'),{faultKind:'domain'});
  const rho=massKg/volumeM3,u=internalEnergyKJ/massKg;
  const s=eos.evaluate({mode:'DU',args:[rho,u*1000]});
  const out=convert(s,s.p/1e5,s.h/1000),a=sat(out.p);
  return {...out,massKg,volumeM3,internalEnergyKJ,densityResidual:(s.rho-rho)/rho,energyResidual:s.u/1000-u,
    liquidVolumeFraction:out.x===null?(out.phase.includes('liquid')?1:0):(1-out.x)*rho/a.rhof};
 }
 return {ph,sat,stateMVU,counts};
}
