// All original probes retained. No phase-boundary smoothness assertion.
export function investigate(eos,requests){
 const m=eos.module,k=m.parameters,low=!!eos.state.hmass;
 const audit=low?m.factory('HEOS','Ammonia'):null;
 const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
 function direct(rho,T){
  if(audit){audit.update(m.input_pairs.DmassT_INPUTS,rho,T);return {p:audit.p(),h:audit.hmass(),u:audit.umass(),Q:audit.Q()};}
  const a={};for(const [key,field]of Object.entries({p:'P',h:'Hmass',u:'Umass',Q:'Q'}))a[key]=m.PropsSI(field,'Dmass',rho,'T',T,'Ammonia');return a;
 }
 function sample(p,h){
  const s=eos.evaluate({mode:'PH',args:[p,h]});
  const dt=direct(s.rho,s.T),sat=eos.evaluate({mode:'SAT',args:[p,0]});
  const phase=m.PropsSI('Phase','P',p,'Hmass',h,'Ammonia');
  const out={p,h,inputBits:[bits(p),bits(h)],state:s,direct:dt,pResidual:dt.p-p,hResidual:dt.h-h,phase,
   phaseLabel:{0:'liquid',1:'supercritical',2:'supercritical gas',3:'supercritical liquid',4:'critical point',5:'vapor',6:'two-phase'}[phase]||'unknown',distance:{TK:s.T-sat.T,hMinusHf:h-sat.hf,hMinusHg:h-sat.hg},saturation:sat};
  if([0,1,2,3,5].includes(phase)&&s.Q<0){
   if(audit){const d=(a,b,c)=>audit.first_partial_deriv(a,b,c);out.derivatives={rhoP:d(k.iDmass,k.iP,k.iHmass),rhoH:d(k.iDmass,k.iHmass,k.iP),cp:audit.cpmass(),cv:audit.cvmass(),kappa:audit.isothermal_compressibility()};}
   else{out.derivatives={};for(const [key,field]of Object.entries({rhoP:'d(Dmass)/d(P)|Hmass',rhoH:'d(Dmass)/d(Hmass)|P',cp:'Cpmass',cv:'Cvmass',kappa:'ISOTHERMAL_COMPRESSIBILITY'}))out.derivatives[key]=m.PropsSI(field,'Dmass',s.rho,'T',s.T,'Ammonia');}
  }else out.derivativeExclusion='Coexistence endpoints/interior: homogeneous partials are not an acceptance target';
  return out;
 }
 const rows=[];
 for(const q of requests){
  const [p,h]=q.args,dp=1e-7*Math.max(1,Math.abs(p/1e5))*1e5,dh=1e-8*Math.max(1,Math.abs(h/1000))*1000;
  const row={...q,probes:[]};
  try{row.base=sample(p,h);}catch(e){row.error=String(e);rows.push(row);continue;}
  for(const [axis,step]of [['P',dp],['H',dh]])for(const sign of [1,-1]){
   const a=p+(axis==='P'?sign*step:0),b=h+(axis==='H'?sign*step:0),probe={axis,step:sign*step,actualIncrement:axis==='P'?a-p:b-h};
   try{probe.output=sample(a,b);probe.crossesPhase=probe.output.phase!==row.base.phase;
    probe.finite=(probe.output.state.rho-row.base.state.rho)/(sign*step);
    if(!probe.crossesPhase&&row.base.derivatives&&probe.output.derivatives){probe.analytic=row.base.derivatives[axis==='P'?'rhoP':'rhoH'];probe.ratio=probe.finite/probe.analytic;}
   }catch(e){probe.error=String(e);}row.probes.push(probe);
  }
  if(q.id==='B1-vapor-regression'){
   try{row.PTatReturnedT=eos.evaluate({mode:'PT',args:[p,row.base.state.T]});}catch(e){row.PTerror=String(e);}
   try{row.DUroundtrip=eos.evaluate({mode:'DU',args:[row.base.state.rho,row.base.direct.u]});}catch(e){row.DUerror=String(e);}
  }
  rows.push(row);
 }
 audit?.delete();return {rows,linearMemory:eos.memory()};
}
