// Public official APIs only. No input rounding, caching, tolerance changes or fallback values.
export function bits(x){const b=new ArrayBuffer(8),d=new DataView(b);d.setFloat64(0,x,false);return d.getBigUint64(0,false).toString(16).padStart(16,'0');}
export function fromBits(hex){const b=new ArrayBuffer(8),d=new DataView(b);d.setBigUint64(0,BigInt('0x'+hex),false);return d.getFloat64(0,false);}
export async function diagnose(eos,inputs){
 const m=eos.module,k=m.parameters,low=!!eos.state.hmass,shared=eos.state,audit=low?m.factory('HEOS','Ammonia'):null;
 function sample(p,h,method){
  let a=method==='fresh'&&low?m.factory('HEOS','Ammonia'):shared;
  try{
   let out;
   if(!low||method.startsWith('high')){
    const pk=method==='high-liquid'?'P|liquid':'P';out={};
    for(const [f,key] of Object.entries({p:'P',h:'Hmass',rho:'Dmass',T:'T',u:'Umass',Q:'Q'}))out[f]=m.PropsSI(key,pk,p,'Hmass',h,'HEOS::Ammonia');
   }else{
    if(method==='after-PT')a.update(m.input_pairs.PT_INPUTS,350000,240);
    if(method==='after-PQ')a.update(m.input_pairs.PQ_INPUTS,350000,.5);
    if(method==='after-DU')a.update(m.input_pairs.DmassUmass_INPUTS,708.6710262223568,94480.59153610271);
    if(method==='molar')a.update(m.input_pairs.HmolarP_INPUTS,h*a.molar_mass(),p);
    else a.update(m.input_pairs.HmassP_INPUTS,h,p);
    out={p:a.p(),h:a.hmass(),rho:a.rhomass(),T:a.T(),u:a.umass(),Q:a.Q()};
   }
   if(low){
    audit.update(m.input_pairs.DmassT_INPUTS,out.rho,out.T);
    Object.assign(out,{pEOS:audit.p(),hEOS:audit.hmass(),cp:audit.cpmass(),cv:audit.cvmass(),kappa:audit.isothermal_compressibility(),rhoP:audit.first_partial_deriv(k.iDmass,k.iP,k.iHmass),rhoH:audit.first_partial_deriv(k.iDmass,k.iHmass,k.iP),hp:audit.first_partial_deriv(k.iHmass,k.iP,k.iT),rhoT:audit.first_partial_deriv(k.iDmass,k.iT,k.iP)});
   }else{
    for(const [f,key]of Object.entries({pEOS:'P',hEOS:'Hmass',cp:'Cpmass',cv:'Cvmass',kappa:'ISOTHERMAL_COMPRESSIBILITY',rhoP:'d(Dmass)/d(P)|Hmass',rhoH:'d(Dmass)/d(Hmass)|P',hp:'d(Hmass)/d(P)|T',rhoT:'d(Dmass)/d(T)|P'}))out[f]=m.PropsSI(key,'Dmass',out.rho,'T',out.T,'HEOS::Ammonia');
   }
   out.pResidual=out.pEOS-p;out.hResidual=out.hEOS-h;out.workIdentity=out.h-out.u-out.p/out.rho;
   if(!Object.values(out).every(Number.isFinite))throw Error('Nonfinite official API output');
   return out;
  }finally{if(a!==shared)a.delete();}
 }
 const start=performance.now(),rows=[];
 for(const q of inputs.cases){
  let [p,h]=q.args;
  const methods=q.primary?(low?inputs.methods:['high','high-liquid']):['reused','high-liquid'];
  for(const method of methods){
   const probes=q.primary?[...inputs.sweep.map(dp=>['P',dp]),['P',-.01],['H',q.dh],['H',-q.dh]]:[['P',q.dp],['H',q.dh]];
   for(const [axis,step]of probes){
    const args=axis==='P'?[p+step,h]:[p,h+step];
    try{
     let base,pert;
     if(method==='reverse'){pert=sample(...args,method);base=sample(p,h,method);}else{base=sample(p,h,method);pert=sample(...args,method);}
     const analytic=base[axis==='P'?'rhoP':'rhoH'],finite=(pert.rho-base.rho)/step;
     rows.push({id:q.id,method:low?method:method==='reused'?'high-unavailable-low-level':method,axis,step,args:[p,h],inputBits:[bits(p),bits(h)],perturbedInputBits:args.map(bits),actualStep:args[axis==='P'?0:1]-q.args[axis==='P'?0:1],base,perturbed:pert,analytic,finite,ratio:finite/analytic});
    }catch(e){rows.push({id:q.id,method,axis,step,error:String(e)});}
   }
  }
 }
 // Binary64 transport, independent of PH flash. Text unit conversions are separate inputs.
 const q=inputs.cases[0],transport={json:q.args.map(v=>bits(JSON.parse(JSON.stringify(v)))),dataView:q.inputBits.map(hex=>bits(fromBits(hex))),literal:[bits(30298.937123458254),bits(94523.34612321304)],original:q.inputBits,
  solverBarProbe:bits((q.args[0]/1e5+1e-7*Math.max(1,q.args[0]/1e5))*1e5),directSIProbe:bits(q.args[0]+.01)};
 // Deterministic repetition measures reproducibility, never averages properties.
 const repetition=[];for(let i=0;i<30;i++){const a=sample(...q.args,'reused'),b=sample(q.args[0]+.01,q.args[1],'reused');repetition.push({rhoBits:[bits(a.rho),bits(b.rho)],hResidual:[a.hResidual,b.hResidual]});}
 audit?.delete();return {version:eos.capabilities.version,git:eos.capabilities.git,capabilities:eos.capabilities,init:eos.init,rows,transport,repetition,elapsedMS:performance.now()-start,linearMemory:eos.memory(),physicalIPad:false};
}
