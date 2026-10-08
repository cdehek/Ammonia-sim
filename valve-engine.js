/* Generic pressure-driven valve laws. Effective area is Cd*A, not nominal bore. */
(function(root){
'use strict';
function createValves(engine){
 const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
 function liquid(up,downPressure,area,opening=1,recovery=.8,exponent=1,headM=0){
  if(![downPressure,area,opening,recovery,exponent,headM].every(Number.isFinite)||area<0||opening<0||opening>1||recovery<=0||recovery>1||exponent<=0||headM<0)throw Error('Invalid liquid valve specification.');
  const available=(up.p-downPressure)*1e5+up.rho*9.80665*headM;
  if(opening===0||available<=0)return {massFlow:0,status:opening===0?'closed':'reverse pressure · check valve closed',choked:false};
  // IEC-style pressure recovery / flashing cap, using local vapor pressure.
  const vaporPressure=engine.satP(up.T),FF=.96-.28*Math.sqrt(vaporPressure/113.33);
  const limit=recovery**2*Math.max(0,(up.p-FF*vaporPressure)*1e5);
  const effective=Math.min(available,limit),choked=available>limit;
  return {massFlow:area*opening**exponent*Math.sqrt(2*up.rho*effective),status:choked?'flashing / capped':'liquid flow',choked,availablePa:available,effectivePa:effective,gravityEnthalpy:9.80665*headM/1000};
 }
 function vapor(up,downPressure,area){
  if(!Number.isFinite(area)||area<0||!Number.isFinite(downPressure)||downPressure<.3)throw Error('Invalid vapor connection specification.');
  if(downPressure>=up.p||area===0)return {massFlow:0,status:'reverse pressure · check valve closed',choked:false};
  const flux=p=>{const a=engine.ps(p,up.s);return a.rho*Math.sqrt(Math.max(0,2*(up.h-a.h)*1000));};
  if(downPressure/up.p>.8)return {massFlow:area*flux(downPressure),status:'vapor flow',choked:false};
  // Sample a fixed pressure-ratio path to find the real-fluid equilibrium choking maximum.
  let peak=0,critical=up.p,previous=0;
  for(let ratio=.95;ratio>=.1-1e-9;ratio-=.05){const p=Math.max(.3,up.p*ratio),G=flux(p);if(G>peak){peak=G;critical=p;}if(G<previous||p===.3)break;previous=G;}
  const choked=downPressure<=critical;
  return {massFlow:area*(choked?peak:flux(downPressure)),status:choked?'equilibrium vapor choking':'vapor flow',choked};
 }
 function controller(c,o,spec,actualSuperheat){
  const error=c.sensor-o.superheatTarget,raw=o.kp*error+c.integral;
  const command=o.valveMode==='auto'?clamp(raw,0,1):o.valveMode==='manual'?o.manualOpening:0;
  const integral=o.valveMode==='auto'&&!((raw>=1&&error>0)||(raw<=0&&error<0))?o.ki*error:0;
  return {command,opening:(command-c.opening)/spec.actuatorSeconds,sensor:(actualSuperheat-c.sensor)/spec.sensorSeconds,integral};
 }
 return {liquid,vapor,controller};
}
const api={createValves};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaValves=api;
})(typeof globalThis!=='undefined'?globalThis:this);
