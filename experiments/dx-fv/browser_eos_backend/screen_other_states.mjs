// Additional stable single-phase liquid/vapor screening. Coexistence endpoints
// are not assigned smooth homogeneous derivatives. No changed solver probes.
export function screenOther(eos,requests){
 const m=eos.module,k=m.parameters,low=!!eos.state.hmass;
 const audit=low?m.factory('HEOS','Ammonia'):null,rows=[];
 function sample(p,h,method){
  const a=low?(method==='fresh'?m.factory('HEOS','Ammonia'):eos.state):null;
  try{
   let s;
   if(low){a.update(m.input_pairs.HmassP_INPUTS,h,p);s={rho:a.rhomass(),T:a.T(),Q:a.Q()};}
   else{s={};for(const [name,field] of Object.entries({rho:'Dmass',T:'T',Q:'Q'}))s[name]=m.PropsSI(field,'P',p,'Hmass',h,'HEOS::Ammonia');}
   if(s.Q>=0&&s.Q<=1)return {...s,derivativeDomain:false};
   if(low){audit.update(m.input_pairs.DmassT_INPUTS,s.rho,s.T);Object.assign(s,{pEOS:audit.p(),hEOS:audit.hmass(),rhoP:audit.first_partial_deriv(k.iDmass,k.iP,k.iHmass),rhoH:audit.first_partial_deriv(k.iDmass,k.iHmass,k.iP)});}
   else for(const [name,field] of Object.entries({pEOS:'P',hEOS:'Hmass',rhoP:'d(Dmass)/d(P)|Hmass',rhoH:'d(Dmass)/d(Hmass)|P'}))s[name]=m.PropsSI(field,'Dmass',s.rho,'T',s.T,'HEOS::Ammonia');
   return {...s,derivativeDomain:true,pResidual:s.pEOS-p,hResidual:s.hEOS-h};
  }finally{if(a&&a!==eos.state)a.delete();}
 }
 for(const q of requests.filter(q=>q.mode==='PH'&&['liquid','vapor'].includes(q.region))){
  const [p,h]=q.args,dp=1e-7*Math.max(1,Math.abs(p/1e5))*1e5,dh=1e-8*Math.max(1,Math.abs(h/1000))*1000;
  for(const method of low?['fresh','reused']:['high-fresh-internal'])for(const [axis,step] of [['P',dp],['H',dh]]){
   try{const base=sample(p,h,method),perturbed=sample(p+(axis==='P'?step:0),h+(axis==='H'?step:0),method);
    const row={id:q.id,region:q.region,args:q.args,method,axis,step,base,perturbed};
    if(base.derivativeDomain&&perturbed.derivativeDomain){const analytic=base[axis==='P'?'rhoP':'rhoH'],finite=(perturbed.rho-base.rho)/step;Object.assign(row,{analytic,finite,ratio:finite/analytic});}
    else row.exclusion='Coexistence endpoint or two-phase output: homogeneous derivative not evaluated';
    rows.push(row);
   }catch(err){rows.push({id:q.id,region:q.region,args:q.args,method,axis,step,error:String(err)});}
  }
 }
 audit?.delete();return {rows,linearMemory:eos.memory()};
}
