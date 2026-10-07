/* Example equipment model. Refrigerant is in quasi-steady equilibrium, not inventory dynamics. */
(function(root){
'use strict';
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const defaults={initial:15,target:0,deadband:2,thermalMass:30,leakUA:.1,gain:2,ambient:25,
 compressors:1,stageDelay:60,displacement:180,evapUA:12,condUA:25,mode:'auto',manualSpeed:.7,suctionTarget:2.5,
 kp:.45,ki:.003,actuatorSeconds:30,minOn:90,minOff:90,available:true,
 highTrip:24,lowTrip:.4,dischargeTrip:170};
function createDynamic(engine,numerics={}){
 const timeStep=numerics.timeStep===undefined?1:numerics.timeStep;
 if(!Number.isFinite(timeStep)||timeStep<.25||timeStep>1)throw Error('Numerical step must be 0.25–1 second.');
 function validate(o){
  const c={...defaults,...o};
  const bounds={compressors:[1,3],stageDelay:[10,600],initial:[-35,40],target:[-35,30],deadband:[.2,10],thermalMass:[.1,100000],leakUA:[0,100],gain:[0,5000],ambient:[-20,45],displacement:[10,2000],evapUA:[.1,1000],condUA:[.1,2000],manualSpeed:[.2,1],suctionTarget:[.35,8],kp:[0,5],ki:[0,.1],actuatorSeconds:[1,300],minOn:[0,1800],minOff:[0,1800],highTrip:[3,30],lowTrip:[.35,8],dischargeTrip:[80,250]};
  for(const [k,[a,b]] of Object.entries(bounds))if(!Number.isFinite(c[k])||c[k]<a||c[k]>b)throw Error(k+' must be between '+a+' and '+b+' (internal SI).');
  if(!['auto','manual'].includes(c.mode)||typeof c.available!=='boolean')throw Error('Invalid control mode or compressor availability.');
  if(!Number.isInteger(c.compressors))throw Error('Compressor count must be an integer.');
  if(c.lowTrip>=c.highTrip)throw Error('Low-pressure trip must be below high-pressure trip.');
  return c;
 }
 // Exact log-mean driving temperature for the approximate sensible zones.
 function lm(a,b){if(a<=0||b<=0)throw Error('Heat-exchanger temperature pinch.');return Math.abs(a-b)<1e-6?(a+b)/2:(a-b)/Math.log(a/b);}
 function evaluate(room,c,speed,te,tc,stages){
  const p=engine.satP(te),high=engine.satP(tc),ratio=high/p;
  const etaVol=clamp(.88-.035*(ratio-2),.35,.9);
  const etaIs=clamp(.78-.004*(ratio-4)**2-.035*(1-speed)**2,.45,.8);
  const motor=clamp(.93-.07*(1-speed)**2,.8,.94);
  const superheat=Math.min(3,.25*(room-te));
  const m=c.displacement/3600*stages*speed*etaVol*engine.statePT(p,te+superheat+2).rho;
  const r=engine.solve({pressure:p,condensing:high,ambient:c.ambient,spaceTemp:clamp(room,-50,30),
   evapSH:superheat,lineSH:2,subcool:Math.min(3,.25*(tc-c.ambient)),massFlow:m,flowMode:'mass',etaVol:etaVol*100,
   etaIs:etaIs*100,etaMotor:motor*100,evapUA:c.evapUA,condUA:c.condUA});
  const [s1,s2,s3,s4,s5]=r.states;
  const evapBoil=m*(r.low.hg-s4.h)/(room-te);
  const evapSH=m*(s5.h-r.low.hg)/lm(room-te,room-s5.T);
  const desuperheat=m*(s2.h-r.high.hg)/lm(s2.T-c.ambient,tc-c.ambient);
  const condensation=m*(r.high.hg-r.high.hf)/(tc-c.ambient);
  const subcool=m*(r.high.hf-s3.h)/lm(tc-c.ambient,s3.T-c.ambient);
  const evapRequired=evapBoil+evapSH,condRequired=desuperheat+condensation+subcool;
  return {r,te,tc,speed,etaVol,etaIs,residual:[evapRequired/c.evapUA-1,condRequired/c.condUA-1],
   zones:{evapBoil,evapSH,desuperheat,condensation,subcool},evapRequired,condRequired};
 }
 function coupled(room,options,speed,warm,stages=1){
  const c=validate(options);if(!Number.isInteger(stages)||stages<1||stages>c.compressors)throw Error('Invalid active compressor count.');if(!Number.isFinite(room)||room< -40||room>50)throw Error('Room left the supported −40 to 50 °C domain.');
  if(!Number.isFinite(speed)||speed<.2||speed>1)throw Error('Running compressor speed must be 20–100%.');
  const emin=engine.sat(.35).T+.001,emax=Math.min(engine.sat(8).T-.001,room-.05);
  const cmin=Math.max(engine.sat(3).T+.001,c.ambient+.05),cmax=engine.sat(30).T-.001;
  if(emin>=emax||cmin>=cmax)throw Error('No equipment equilibrium inside the supported property domain.');
  const norm=a=>Math.max(...a.residual.map(Math.abs));
  const safe=(te,tc)=>{if(te<emin||te>emax||tc<cmin||tc>cmax||tc<=te)return null;try{return evaluate(room,c,speed,te,tc,stages);}catch{return null;}};
  const seeds=warm?[[warm.te,warm.tc]]:[];
  seeds.push([clamp(room-10,emin,emax),clamp(c.ambient+12,cmin,cmax)],[clamp(room-20,emin,emax),clamp(c.ambient+20,cmin,cmax)],[clamp(room-5,emin,emax),clamp(c.ambient+6,cmin,cmax)],[clamp(room-4,emin,emax),clamp(c.ambient+2,cmin,cmax)]);
  let best=null;
  for(const seed of seeds){
   let a=safe(...seed);if(!a)continue;
   for(let i=0;i<35;i++){
    if(!best||norm(a)<norm(best))best=a;
    if(norm(a)<1e-6)return {...a,iterations:i+1,model:'Example compressor curves; segmented LMTD approximation; quasi-steady refrigerant.'};
    const h=.005,ex=safe(a.te+h,a.tc)||safe(a.te-h,a.tc),ey=safe(a.te,a.tc+h)||safe(a.te,a.tc-h);if(!ex||!ey)break;
    const j00=(ex.residual[0]-a.residual[0])/(ex.te-a.te),j10=(ex.residual[1]-a.residual[1])/(ex.te-a.te),j01=(ey.residual[0]-a.residual[0])/(ey.tc-a.tc),j11=(ey.residual[1]-a.residual[1])/(ey.tc-a.tc),det=j00*j11-j01*j10;
    if(Math.abs(det)<1e-12)break;
    const dx=clamp((-a.residual[0]*j11+j01*a.residual[1])/det,-15,15),dy=clamp((-j00*a.residual[1]+j10*a.residual[0])/det,-15,15);
    let next=null;for(let f=1;f>=1/128;f/=2){const b=safe(a.te+dx*f,a.tc+dy*f);if(b&&norm(b)<norm(a)){next=b;break;}}if(!next)break;a=next;
   }
  }
  throw Error('No converged equipment equilibrium within the pressure/temperature domain. Reduce load/speed or improve the heat exchangers.');
 }
 function create(options){const c=validate(options);return {config:c,time:0,pending:0,T:c.initial,on:false,speed:0,command:0,integral:0,stages:0,stageDemand:0,slots:Array.from({length:c.compressors},()=>({on:false,lastSwitch:-c.minOff})),lastSwitch:-c.minOff,warm:null,point:null,trip:null,reason:'Ready',energy:0,removed:0,leakHeat:0,gainHeat:0,starts:0,events:[],rows:[]};}
 function event(s,text){s.reason=text;s.events.push({seconds:s.time,text});if(s.events.length>200)s.events.shift();}
 function resetTrip(s){s.trip=null;s.integral=0;event(s,'Trip reset; waiting for restart conditions.');}
 function update(s,patch){const next=validate({...s.config,...patch});if(s.time&&(next.thermalMass!==s.config.thermalMass||next.initial!==s.config.initial||next.compressors!==s.config.compressors))throw Error('Reset the plant to change initial temperature, thermal mass or compressor count.');if(!s.time){s.T=next.initial;s.slots=Array.from({length:next.compressors},()=>({on:false,lastSwitch:-next.minOff}));}s.config=next;event(s,'Live inputs updated.');}
 function record(s){const r=s.point&&s.point.r;return {seconds:s.time,T:s.T,target:s.config.target,ambient:s.config.ambient,gain:s.config.gain,evapUA:s.config.evapUA,condUA:s.config.condUA,on:s.on,stages:s.stages,speed:s.speed,command:s.command,pressure:r?r.config.pressure:null,condensing:r?r.pHigh:null,Q:r?r.Q:0,power:r?r.electrical:0,COP:r?r.COP:null,discharge:r?r.states[1].T:null,kWh:s.energy,starts:s.starts,reason:s.reason,trip:s.trip,residual:s.point?Math.max(...s.point.residual.map(Math.abs)):null};}
 function step(s,seconds){
  if(!Number.isFinite(seconds)||seconds<=0||seconds>3600)throw Error('Advance by 0–3600 seconds.');
  s.pending+=seconds;
  while(s.pending>=timeStep-1e-9){
   const dt=timeStep,c=s.config;
   const off=reason=>{if(s.on){s.on=false;s.lastSwitch=s.time;event(s,reason);}s.reason=reason;for(const slot of s.slots)if(slot.on){slot.on=false;slot.lastSwitch=s.time;}s.stages=0;s.stageDemand=0;s.speed=0;s.command=0;s.point=null;s.warm=null;s.integral=0;};
   if(!c.available)off('Compressor unavailable');
   else if(s.trip)off('Tripped: '+s.trip);
   else if(s.on&&s.T<=c.target-c.deadband/2){if(s.slots.filter(slot=>slot.on).every(slot=>s.time-slot.lastSwitch>=c.minOn))off('Thermostat satisfied');else s.reason='Minimum run timer';}
   else if(!s.on&&s.T>=c.target+c.deadband/2){if(s.time-s.lastSwitch>=c.minOff){s.on=true;s.speed=.2;s.lastSwitch=s.time;s.stages=c.mode==='manual'?c.compressors:1;for(let i=0;i<s.stages;i++){s.slots[i].on=true;s.slots[i].lastSwitch=s.time;}s.starts+=s.stages;event(s,'Thermostat requested cooling');}else s.reason='Minimum off timer';}
   if(s.on){
    const p=s.point?s.point.r.config.pressure:c.suctionTarget;
    const error=p-c.suctionTarget;
    let command=c.mode==='manual'?c.manualSpeed:clamp(.5+c.kp*error+s.integral,.2,1);
    if(c.mode==='auto'&&((command>.2&&command<1)||(command===1&&error<0)||(command===.2&&error>0)))s.integral=clamp(s.integral+c.ki*error*dt,-.5,.5);
    command=c.mode==='manual'?c.manualSpeed:clamp(.5+c.kp*error+s.integral,.2,1);s.command=command;
    if(c.mode==='auto'){
     const direction=command>=.98&&error>.1&&s.stages<c.compressors&&s.T>c.target-c.deadband/2?1:command<=.45&&error<-.1&&s.stages>1?-1:0;
     s.stageDemand=direction&&Math.sign(s.stageDemand)===direction?s.stageDemand+direction*dt:direction*dt;
     if(Math.abs(s.stageDemand)>=c.stageDelay){
      const slot=direction>0?s.slots.find(slot=>!slot.on&&s.time-slot.lastSwitch>=c.minOff):[...s.slots].reverse().find(slot=>slot.on&&s.time-slot.lastSwitch>=c.minOn);
      if(slot){slot.on=direction>0;slot.lastSwitch=s.time;s.stages+=direction;if(direction>0)s.starts++;s.integral=0;s.stageDemand=0;s.warm=null;event(s,'Compressor stage '+s.stages+(direction>0?' enabled':' retained after unloading'));}
     }
    }else {s.stageDemand=0;for(const slot of s.slots)if(!slot.on&&s.time-slot.lastSwitch>=c.minOff){slot.on=true;slot.lastSwitch=s.time;s.stages++;s.starts++;s.warm=null;event(s,'Manual compressor stage '+s.stages+' enabled');}}
    s.speed=clamp(command+(s.speed-command)*Math.exp(-dt/c.actuatorSeconds),.2,1);
    try{
     s.point=coupled(s.T,c,s.speed,s.warm,s.stages);s.warm=s.point;
     const r=s.point.r;
     if(r.pHigh>=c.highTrip)s.trip='High discharge pressure';
     else if(r.config.pressure<=c.lowTrip)s.trip='Low suction pressure';
     else if(r.states[1].T>=c.dischargeTrip)s.trip='High discharge temperature';
     if(s.trip)off('Tripped: '+s.trip);
     else if(s.time-s.lastSwitch>=c.minOn&&s.T>c.target-c.deadband/2)s.reason=c.mode==='manual'?'Manual speed; thermostat enabled':command>=.999?'At maximum speed':command<=.201?'At minimum speed':'Suction PI control';
    }catch(error){s.trip=error.message;off('Tripped: '+s.trip);}
   }
   const Q=s.point?s.point.r.Q:0,P=s.point?s.point.r.electrical:0,C=c.thermalMass*1000;
   // Analytical room update for frozen equipment duty over this short step.
   const U=c.leakUA,b=U*c.ambient+c.gain-Q,before=s.T;
   s.T=U>0?b/U+(before-b/U)*Math.exp(-U*dt/C):before+b*dt/C;
   const integralT=U>0?b/U*dt+(before-b/U)*C/U*(-Math.expm1(-U*dt/C)):(before+s.T)/2*dt;
   s.removed+=Q*dt;s.leakHeat+=U*(c.ambient*dt-integralT);s.gainHeat+=c.gain*dt;s.energy+=P*dt/3600;s.time+=dt;s.pending-=dt;
   if(!Number.isFinite(s.T)||s.T< -40||s.T>50){s.trip='Room left supported −40 to 50 °C range';off('Tripped: '+s.trip);break;}
  }
  const row=record(s);if(s.rows.length&&s.rows[s.rows.length-1].seconds===s.time)s.rows[s.rows.length-1]=row;else s.rows.push(row);if(s.rows.length>7200)s.rows.shift();return row;
 }
 return {defaults,validate,coupled,create,step,update,resetTrip,record};
}
if(typeof module!=='undefined'&&module.exports)module.exports={createDynamic,defaults};else root.AmmoniaDynamic={createDynamic,defaults};
})(typeof globalThis!=='undefined'?globalThis:this);
