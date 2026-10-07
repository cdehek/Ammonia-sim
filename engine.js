/* Ammonia Lab v0.2.0: bounded real-fluid interpolation and cycle solver. */
(function(root){
'use strict';
function createEngine(data){
 const eps=1e-8;
 const lerp=(a,b,w)=>a+(b-a)*w;
 function bracket(values,x){if(x<values[0]-eps||x>values.at(-1)+eps)throw Error('State outside the validated property domain.');if(x>=values.at(-1))return [values.length-2,1];let lo=0,hi=values.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(values[m]<=x)lo=m;else hi=m;}return [lo,(x-values[lo])/(values[lo+1]-values[lo])];}
 const logs=data.p.map(Math.log);
 function pBracket(p){if(!(p>0))throw Error('Absolute pressure must be positive.');return bracket(logs,Math.log(p));}
 function mixRow(a,b,w){if(!a||!b)throw Error('Liquid state below the property table temperature limit.');return [lerp(a[0],b[0],w),lerp(a[1],b[1],w),Math.exp(lerp(Math.log(a[2]),Math.log(b[2]),w))];}
 function sat(p){const [i,w]=pBracket(p),a=data.sat[i],b=data.sat[i+1];return {p,T:lerp(a[0],b[0],w),hf:lerp(a[1],b[1],w),sf:lerp(a[2],b[2],w),rhof:Math.exp(lerp(Math.log(a[3]),Math.log(b[3]),w)),hg:lerp(a[4],b[4],w),sg:lerp(a[5],b[5],w),rhog:Math.exp(lerp(Math.log(a[6]),Math.log(b[6]),w))};}
 function satP(T){const temps=data.sat.map(row=>row[0]),[i,w]=bracket(temps,T);return Math.exp(lerp(logs[i],logs[i+1],w));}
 function branch(p,offset,kind){const axis=kind==='vapor'?data.sh:data.sc,[j,u]=bracket(axis,offset),[i,w]=pBracket(p);return mixRow(mixRow(data[kind][i][j],data[kind][i][j+1],u),mixRow(data[kind][i+1][j],data[kind][i+1][j+1],u),w);}
 function statePT(p,T,kind){const a=sat(p),d=T-a.T;
  if(kind==='liquid'||d < -eps){const r=branch(p,Math.max(0,-d),'liquid');return {p,T,h:r[0],s:r[1],rho:r[2],x:null,phase:d<-eps?'Subcooled liquid':'Saturated liquid'};}
  const r=branch(p,Math.max(0,d),'vapor');return {p,T,h:r[0],s:r[1],rho:r[2],x:null,phase:d>eps?'Superheated vapor':'Saturated vapor'};
 }
 function statePX(p,x){if(x<0||x>1)throw Error('Vapor quality must be between zero and one.');const a=sat(p);return {p,T:a.T,h:lerp(a.hf,a.hg,x),s:lerp(a.sf,a.sg,x),rho:1/((1-x)/a.rhof+x/a.rhog),x,phase:x===0?'Saturated liquid':x===1?'Saturated vapor':'Liquid + vapor'};}
 function inverse(p,target,key){const a=sat(p),f=key==='h'?a.hf:a.sf,g=key==='h'?a.hg:a.sg;
  if(target>=f-eps&&target<=g+eps)return statePX(p,Math.max(0,Math.min(1,(target-f)/(g-f))));
  const kind=target>g?'vapor':'liquid',col=key==='h'?0:1,max=kind==='vapor'?250:30;
  if(kind==='liquid')throw Error('Inverse subcooled-liquid state is outside this cycle solver.');
  if(branch(p,max,kind)[col]<target-eps)throw Error('Compressor discharge exceeds the property table (250 K superheat). Use a lower ratio or higher efficiency.');
  let low=0,high=max;for(let i=0;i<38;i++){const mid=(low+high)/2;if(branch(p,mid,kind)[col]<target)low=mid;else high=mid;}
  const result=statePT(p,a.T+(low+high)/2);result[key]=target;return result;
 }
 const ph=(p,h)=>inverse(p,h,'h'),ps=(p,s)=>inverse(p,s,'s');
 const defaults={system:'dx',pressure:2.5,condensing:12,highMode:'pressure',ambient:25,approach:10,evapSH:5,lineSH:2,subcool:3,suctionDrop:0,liquidDrop:0,etaIs:75,etaMotor:92,flowMode:'mass',massFlow:.1,load:100,displacement:180,etaVol:75,evapUA:12,condUA:25,spaceTemp:0,dischargeLimit:150,ratioLimit:8};
 function solve(inputs){const c={...defaults,...inputs};const finiteKeys=Object.keys(defaults).filter(k=>typeof defaults[k]==='number');for(const k of finiteKeys)if(!Number.isFinite(c[k]))throw Error('Enter a finite number for '+k+'.');
  const bounds={pressure:[.35,8],condensing:[3,30],ambient:[-20,50],approach:[3,25],evapSH:[0,20],lineSH:[0,20],subcool:[0,20],suctionDrop:[0,.5],liquidDrop:[0,1],etaIs:[40,100],etaMotor:[50,100],massFlow:[.001,5],load:[1,5000],displacement:[1,10000],etaVol:[20,100],evapUA:[.1,1000],condUA:[.1,2000],spaceTemp:[-50,30],dischargeLimit:[80,250],ratioLimit:[2,20]};
  for(const [k,[low,high]] of Object.entries(bounds))if(c[k]<low||c[k]>high)throw Error(`${k}: enter a value between ${low} and ${high}.`);
  if(!['dx','flooded'].includes(c.system)||!['pressure','ambient'].includes(c.highMode)||!['mass','load','displacement'].includes(c.flowMode))throw Error('Unknown application mode.');
  if(c.system==='flooded'&&c.evapSH!==0)throw Error('Flooded separator mode requires zero evaporator superheat.');
  const pHigh=c.highMode==='ambient'?satP(c.ambient+c.approach):c.condensing;
  if(pHigh<3||pHigh>30)throw Error('Ambient + approach requires condensing pressure outside 3–30 bar(a).');
  const pEvap=c.pressure+c.suctionDrop;if(pEvap>=pHigh)throw Error('Condensing pressure must exceed evaporator pressure.');
  const low=sat(pEvap),high=sat(pHigh);
  if(high.T<=c.ambient)throw Error('Condensing temperature must be above the cooling-air temperature.');
  const evapOut=c.evapSH===0?statePX(pEvap,1):statePT(pEvap,low.T+c.evapSH);
  const afterDrop=ph(c.pressure,evapOut.h);
  const suction=c.lineSH===0?afterDrop:statePT(c.pressure,afterDrop.T+c.lineSH);
  if(suction.x!==null&&suction.x<1-eps)throw Error('Wet compressor suction is not a valid dry-vapor compression state.');
  const ideal=ps(pHigh,suction.s),discharge=ph(pHigh,suction.h+(ideal.h-suction.h)/(c.etaIs/100));
  if(discharge.s<suction.s-1e-6)throw Error('Compressor entropy decreased; invalid compression state.');
  const liquid=c.subcool===0?statePX(pHigh,0):statePT(pHigh,high.T-c.subcool,'liquid');
  const valveP=pHigh-c.liquidDrop;if(valveP<=pEvap)throw Error('Liquid-line outlet pressure must exceed evaporator pressure.');
  if(liquid.h>sat(valveP).hf+eps)throw Error('Liquid-line pressure loss causes flash gas before the valve. Increase subcooling or reduce liquid-line loss.');
  const valve=ph(pEvap,liquid.h);if(valve.x===null||valve.x<=0||valve.x>=1)throw Error('Valve outlet is outside the supported two-phase evaporator inlet.');
  const q=evapOut.h-valve.h,w=discharge.h-suction.h,qLine=suction.h-evapOut.h;
  if(q<=0||w<=0||qLine < -eps)throw Error('Non-positive cooling/work or negative suction-line heating.');
  const m=c.flowMode==='load'?c.load/q:c.flowMode==='displacement'?c.displacement/3600*(c.etaVol/100)*suction.rho:c.massFlow;
  const Q=m*q,W=m*w,Qline=m*qLine,Qcond=m*(discharge.h-liquid.h),electrical=W/(c.etaMotor/100),motorLoss=electrical-W,ratio=pHigh/c.pressure;
  const COP=Q/electrical,carnot=(low.T+273.15)/(high.T-low.T),balance=Qcond-Q-Qline-W;
  if(COP>carnot*1.001)throw Error('Calculated COP exceeds the saturation-temperature Carnot limit.');
  const requiredDisplacement=m/suction.rho/(c.etaVol/100)*3600;
  const capacityUA=c.evapUA*Math.max(0,c.spaceTemp-low.T),condenserScreenUA=Qcond/(high.T-c.ambient);
  const diagnostics=[];const warn=(code,text)=>diagnostics.push({code,level:'warning',text});
  if(discharge.T>c.dischargeLimit)warn('discharge',`Discharge ${discharge.T.toFixed(1)} °C exceeds your ${c.dischargeLimit} °C screening limit.`);
  if(ratio>c.ratioLimit)warn('ratio',`Compression ratio ${ratio.toFixed(2)} exceeds your ${c.ratioLimit}:1 screening limit; evaluate staging and a compressor map.`);
  if(suction.T-sat(c.pressure).T<2)warn('superheat','Less than 2 K suction superheat. This ideal dry-vapor state does not prove protection against liquid carryover.');
  if(c.spaceTemp<=evapOut.T&&c.spaceTemp>low.T)warn('outlet-approach','Evaporator outlet temperature is at or above the cold-space temperature. The specified superheat cannot be supplied by that space at this operating point.');
  if(c.spaceTemp<=low.T)warn('temperature-lift','Cold-space temperature is at or below evaporation temperature; the coil cannot provide cooling at that condition.');
  else if(Q>capacityUA)warn('evap-ua',`Cycle duty exceeds the UA × temperature-difference estimate (${capacityUA.toFixed(1)} kW). Actual delivered duty needs a coupled heat-exchanger/equipment solution.`);
  if(condenserScreenUA>c.condUA)warn('cond-ua','Condenser duty exceeds the isothermal UA screening estimate. This is a screening result, not a segmented condenser rating.');
  if(c.flowMode==='displacement')warn('fixed-volume','Flow uses your fixed volumetric efficiency. No manufacturer compressor map or unloading model is supplied.');
  if(c.flowMode==='load')warn('required-flow','Flow and swept volume are requirements to meet the specified load; they are not verified available compressor capacity.');
  if(c.system==='flooded')warn('flooded-scope','Ideal flooded separator: saturated vapor leaves the separator. Pump head, recirculation flow, vessel inventory and oil behavior are not modeled.');
  return {config:c,pHigh,pEvap,low,high,states:[{name:'1 · Compressor suction',...suction},{name:'2 · Compressor discharge',...discharge},{name:'3 · Condenser liquid',...liquid},{name:'4 · Valve outlet',...valve},{name:'5 · Evaporator outlet',...evapOut},{name:'2s · Isentropic discharge',...ideal}],m,q,w,Q,W,Qline,Qcond,electrical,motorLoss,ratio,COP,carnot,balance,requiredDisplacement,capacityUA,condenserScreenUA,diagnostics,flashFraction:valve.x};
 }
 function roomSimulation(result,opts){const {initial,target,deadband,thermalMass,leakUA,internalGain,hours}=opts;
  for(const [k,v] of Object.entries(opts))if(!Number.isFinite(v))throw Error('Invalid transient input: '+k);
  if(thermalMass<=0||leakUA<0||internalGain<0||hours<=0||hours>168||deadband<=0||target>=initial||target<=result.states[4].T)throw Error('Use positive thermal mass, non-negative heat gains, 0–168 hours, initial above setpoint, and setpoint above evaporating temperature.');
  const U=leakUA,A=result.config.ambient,C=thermalMass*1000; // MJ/K -> kJ/K
  const dt=60,duration=hours*3600,lower=target-deadband/2,upper=target+deadband/2;
  if(lower<=result.states[4].T)throw Error('Thermostat lower threshold must stay above the evaporator outlet temperature to sustain the specified superheat.');
  let T=initial,on=true,t=0,energy=0,firstSetpoint=null;
  const rows=[{minutes:0,T,on:true,electricalKWh:0}];
  const capacity=T=>Math.min(result.Q,result.config.evapUA*Math.max(0,T-result.low.T));
  // Piecewise-linear ODE: UA coil is limited by available cycle capacity.
  function segment(T,on,remaining){
   const split=result.low.T+result.Q/result.config.evapUA;
   const coilLimited=on&&T<split;
   const a=U+(coilLimited?result.config.evapUA:0);
   const b=U*A+internalGain+(coilLimited?result.config.evapUA*result.low.T:0)-(on&&!coilLimited?result.Q:0);
   const next=seconds=>a>0?b/a+(T-b/a)*Math.exp(-a*seconds/C):T+b*seconds/C;
   let eventTime=remaining,event=null;
   const thresholds=[{T:on?lower:upper,event:'thermostat'}];
   if(on)thresholds.push({T:split,event:'coil'});
   if(firstSetpoint===null&&on)thresholds.push({T:target,event:'setpoint'});
   const end=next(remaining);
   for(const threshold of thresholds){const z=threshold.T;if((z-T)*(z-end)<=0&&Math.abs(z-T)>1e-7){let crossing=a>0?-C/a*Math.log((z-b/a)/(T-b/a)):(z-T)*C/b;if(crossing>1e-7&&crossing<eventTime){eventTime=crossing;event=threshold.event;}}}
   return {T:next(eventTime),seconds:eventTime,event};
  }
  for(let n=0;t<duration-1e-7&&n<11000;n++){
   let remaining=Math.min(dt,duration-t),guard=0;
   while(remaining>1e-7&&guard++<1000){
    if(on&&T<=lower+1e-7)on=false;else if(!on&&T>=upper-1e-7)on=true;
    const before=T, step=segment(T,on,remaining);
    if(on){const a=U+(before<result.low.T+result.Q/result.config.evapUA?result.config.evapUA:0);const b=U*A+internalGain+(before<result.low.T+result.Q/result.config.evapUA?result.config.evapUA*result.low.T:0)-(before>=result.low.T+result.Q/result.config.evapUA?result.Q:0);const integralT=a>0?(b/a)*step.seconds+(before-b/a)*C/a*(1-Math.exp(-a*step.seconds/C)):(before+step.T)/2*step.seconds;const removed=U*(A*step.seconds-integralT)+internalGain*step.seconds+C*(before-step.T);energy+=Math.max(0,removed)/result.COP/3600;}
    T=step.T;t+=step.seconds;remaining-=step.seconds;
    if(step.event==='thermostat')on=!on;
    if(step.event==='setpoint'&&firstSetpoint===null)firstSetpoint=t/60;
    if(step.event==='coil')T+= (U*(A-T)+internalGain-capacity(T))*1e-9;
   }
   if(remaining>1e-7)throw Error('Thermostat cycling is too rapid for this model; increase thermal mass or deadband.');
   rows.push({minutes:t/60,T,on,electricalKWh:energy});
  }
  if(t<duration-1e-7)throw Error('Simulation exceeded its time-resolution limit.');
  return {rows,firstSetpoint,energy,finalT:T,assumptions:'Fixed cycle pressures and efficiencies; ideal proportional flow/power modulation; UA-limited cooling; lumped thermal mass; thermostat control. Not refrigerant-inventory or startup dynamics.'};
 }
 return {sat,satP,statePT,statePX,ph,ps,solve,roomSimulation,defaults};
}
if(typeof module!=='undefined'&&module.exports)module.exports={createEngine};else root.AmmoniaEngine={createEngine};
})(typeof globalThis!=='undefined'?globalThis:this);
