// New diagnostics via the public bindings. The inherited loader stays unchanged.
export function sharedCallers(eos,requests){
 const m=eos.module,k=m.parameters,a=eos.state,dt=m.factory('HEOS','Ammonia'),rows=[];
 const props=s=>({p:s.p(),T:s.T(),rho:s.rhomass(),h:s.hmass(),s:s.smass(),u:s.umass(),Q:s.Q()});
 const pairs={PH:['HmassP_INPUTS',true],PS:['PSmass_INPUTS',false],PU:['PUmass_INPUTS',false]};
 try{for(const q of requests){const [p,y]=q.input,[pair,reverse]=pairs[q.mode],row={id:q.id,mode:q.mode,input:q.input,inputBits:q.inputBits},fresh=m.factory('HEOS','Ammonia');
  try{
   for(const state of [a,fresh])state.update(m.input_pairs[pair],reverse?y:p,reverse?p:y);
   const s=props(a),f=props(fresh);dt.update(m.input_pairs.DmassT_INPUTS,s.rho,s.T);row.state=s;row.freshState=f;row.freshEqualsReused=JSON.stringify(s)===JSON.stringify(f);row.independentDT=props(dt);
   if(s.Q<0){row.getterDifferences=Object.fromEntries(['p','h','u','s'].map(k=>[k,s[k]-row.independentDT[k]]));row.derivatives={cp:dt.cpmass(),cv:dt.cvmass(),kappa:dt.isothermal_compressibility(),hT_p:dt.first_partial_deriv(k.iHmass,k.iT,k.iP),sT_p:dt.first_partial_deriv(k.iSmass,k.iT,k.iP),uT_p:dt.first_partial_deriv(k.iUmass,k.iT,k.iP)};}
   else row.equilibriumQualityValid=s.Q>=0&&s.Q<=1;
  }catch(e){row.error=String(e);}finally{fresh.delete();}
  rows.push(row);
 }return {rows,memoryBytes:eos.memory()};}finally{dt.delete();}
}
