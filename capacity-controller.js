/* Independent single-compressor control. No refrigerant states or plant trips are changed. */
(function(root){
'use strict';
const profiles=typeof module!=='undefined'&&module.exports?require('./equipment-profiles'):root.AmmoniaProfiles;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),copy=x=>JSON.parse(JSON.stringify(x)),CADENCE=.1,EPS=1e-9;
const DEFAULTS=Object.freeze({mode:'manual',manualSpeed:.7,suctionTarget:2.5,minSpeed:.2,maxSpeed:1,kp:.45,ki:.003,deadbandBar:.05,sensorSeconds:2,actuatorSeconds:30,rampPerSecond:.02,trackingSeconds:10,startDelay:3,minOn:90,minOff:90});
const BOUNDS={manualSpeed:[.2,1],suctionTarget:[.35,8],minSpeed:[.2,1],maxSpeed:[.2,1],kp:[0,2],ki:[0,.1],deadbandBar:[0,.5],sensorSeconds:[.05,300],actuatorSeconds:[.05,300],rampPerSecond:[.0001,1],trackingSeconds:[.1,300],startDelay:[0,600],minOn:[0,3600],minOff:[0,3600]};
function object(x,label){if(!x||typeof x!=='object'||Array.isArray(x)||(Object.getPrototypeOf(x)!==Object.prototype&&Object.getPrototypeOf(x)!==null))throw Error(label+' must be an object.');}
function normalize(profile,settings={}){
 const p=profiles.normalize(profile);if(p.equipment.compressors!==1)throw Error('Managed capacity supports exactly one compressor.');
 object(settings,'Controller settings');for(const k of Object.keys(settings))if(!Object.prototype.hasOwnProperty.call(DEFAULTS,k))throw Error('Unknown capacity setting: '+k);
 const c={...DEFAULTS,...settings};if(!['manual','auto'].includes(c.mode))throw Error('Capacity mode must be manual or auto.');
 for(const [k,[a,b]]of Object.entries(BOUNDS))if(typeof c[k]!=='number'||!Number.isFinite(c[k])||c[k]<a||c[k]>b)throw Error(k+' is outside the supported controller range.');
 if(c.minSpeed>c.maxSpeed||c.manualSpeed<c.minSpeed||c.manualSpeed>c.maxSpeed)throw Error('Manual speed must fit the configured minimum/maximum speed.');
 if(c.suctionTarget-c.deadbandBar<=p.equipment.lowTrip||c.suctionTarget+c.deadbandBar>=Math.min(8,p.equipment.highTrip))throw Error('Suction target and deadband must stay strictly inside profile pressure limits and the supported target range.');
 return c;
}
function errorFor(s){if(s.sensedPressure===null)return 0;const e=s.sensedPressure-s.settings.suctionTarget;return Math.abs(e)<=s.settings.deadbandBar?0:e-Math.sign(e)*s.settings.deadbandBar;}
function create(profile,settings={},initial={}){
 const p=profiles.normalize(profile),c=normalize(p,settings);object(initial,'Initial controller state');for(const k of Object.keys(initial))if(!['running','speed'].includes(k))throw Error('Unknown initial controller field: '+k);
 const running=initial.running??false,speed=initial.speed??c.manualSpeed;if(typeof running!=='boolean'||!Number.isFinite(speed)||speed<c.minSpeed||speed>c.maxSpeed)throw Error('Initial running/speed must be valid for the configured range.');
 return {schemaVersion:1,profile:p,settings:c,time:0,pending:0,input:null,running,speed:running?speed:0,command:running?speed:0,rawCommand:running?speed:0,integral:0,sensedPressure:null,measuredPressure:null,lastSwitch:0,startDemandAt:null,starts:0,track:true,reason:running?'Running':'Stopped',limitedBy:[],stop:null,lastStop:null};
}
function validateInput(input){
 object(input,'Controller input');for(const k of Object.keys(input))if(!['pressureBarAbsolute','enabled','demand','available','stop'].includes(k))throw Error('Unknown controller input: '+k);
 const u={pressureBarAbsolute:null,enabled:true,demand:true,available:true,stop:null,...input};
 for(const k of ['enabled','demand','available'])if(typeof u[k]!=='boolean')throw Error(k+' must be boolean.');
 if(u.pressureBarAbsolute!==null&&typeof u.pressureBarAbsolute!=='number')throw Error('Pressure input must be a number in bar absolute or null.');
 u.pressureBarAbsolute=Number.isFinite(u.pressureBarAbsolute)&&u.pressureBarAbsolute>=.3&&u.pressureBarAbsolute<=35?u.pressureBarAbsolute:null;
 if(u.stop!==null){object(u.stop,'Model stop');if(!['equipment','domain','solver'].includes(u.stop.kind)||typeof u.stop.message!=='string'||!Number.isFinite(u.stop.seconds)||u.stop.seconds<0)throw Error('Provide a valid existing model-stop snapshot.');u.stop=copy(u.stop);}
 return u;
}
function off(s,reason){if(s.running)s.lastSwitch=s.time;s.running=false;s.speed=0;s.command=0;s.rawCommand=0;s.integral=0;s.track=true;s.startDemandAt=null;s.reason=reason;s.limitedBy=[];}
function gate(s,u){
 if(u.stop){s.stop=copy(u.stop);s.lastStop=copy(u.stop);off(s,'Model stop: '+u.stop.kind);return;}
 s.stop=null;
 if(!u.enabled){off(s,'Disabled by operator');return;}
 if(!u.available){off(s,'Equipment unavailable');return;}
 if(u.pressureBarAbsolute===null){s.sensedPressure=null;off(s,'Pressure signal unavailable');return;}
 if(!u.demand){s.startDemandAt=null;if(s.running&&s.time-s.lastSwitch+EPS<s.settings.minOn)s.reason='Minimum on time';else off(s,'No run demand');return;}
 if(s.running){s.reason=s.settings.mode==='auto'?'Automatic suction PI':'Manual capacity';return;}
 if(s.time-s.lastSwitch+EPS<s.settings.minOff){s.startDemandAt=null;s.reason='Minimum off time';return;}
 if(s.startDemandAt===null)s.startDemandAt=s.time;
 if(s.time-s.startDemandAt+EPS<s.settings.startDelay){s.reason='Start delay';return;}
 s.running=true;s.lastSwitch=s.time;s.starts++;s.speed=s.settings.minSpeed;s.command=s.speed;s.rawCommand=s.speed;s.track=true;s.reason=s.settings.mode==='auto'?'Automatic suction PI':'Manual capacity';s.startDemandAt=null;
}
function tick(s,u,dt=CADENCE){
 const c=s.settings;
 if(u.pressureBarAbsolute!==null)s.sensedPressure+=(u.pressureBarAbsolute-s.sensedPressure)*(-Math.expm1(-dt/c.sensorSeconds));
 if(s.running){
  const error=errorFor(s);if(s.track){s.integral=s.speed-c.kp*error;s.track=false;}
  s.rawCommand=c.mode==='manual'?c.manualSpeed:c.kp*error+s.integral;
  s.command=clamp(s.rawCommand,c.minSpeed,c.maxSpeed);s.limitedBy=[];
  if(s.rawCommand<=c.minSpeed+EPS)s.limitedBy.push('minimum speed');if(s.rawCommand>=c.maxSpeed-EPS)s.limitedBy.push('maximum speed');
  const lag=(s.command-s.speed)*(-Math.expm1(-dt/c.actuatorSeconds)),movement=clamp(lag,-c.rampPerSecond*dt,c.rampPerSecond*dt);
  if(Math.abs(lag)>c.rampPerSecond*dt+EPS)s.limitedBy.push('ramp rate');
  s.speed=clamp(s.speed+movement,c.minSpeed,c.maxSpeed);if(Math.abs(s.command-s.speed)>1e-7)s.limitedBy.push('actuator response');
  // Tracking actual delivered capacity unwinds saturation and rate/actuator limitation.
  if(c.mode==='auto')s.integral+=dt*(c.ki*error+(s.speed-s.rawCommand)/c.trackingSeconds);
  else s.integral=s.speed-c.kp*error;
 }
 s.time+=dt;s.pending=Math.max(0,s.pending-dt);gate(s,u);
}
function advance(s,seconds,input={}){
 if(!Number.isFinite(seconds)||seconds<=0||seconds>3600)throw Error('Advance controller by greater than zero and at most 3600 seconds.');
 const u=validateInput(input),next=copy(s),urgent=!!u.stop||!u.enabled||!u.available||u.pressureBarAbsolute===null;
 if(next.pending>EPS&&next.input&&JSON.stringify(next.input)!==JSON.stringify(u)){
  if(urgent){if(!u.stop)next.pending=0;}else throw Error('Change controller measurements/permissions only at an accepted cadence boundary.');
 }
 // A stop may occur within already-requested sub-cadence physical time.
 // Reconcile only that accepted remainder using its original held observation.
 if(u.stop&&Math.abs(u.stop.seconds-next.time)>EPS){
  const remainder=u.stop.seconds-next.time;
  if(remainder<0||remainder>next.pending+EPS||!next.input)throw Error('Stop time is outside requested controller time.');
  tick(next,next.input,remainder);next.pending=0;
 }
 next.input=copy(u);next.measuredPressure=u.pressureBarAbsolute;
 if(next.sensedPressure===null&&u.pressureBarAbsolute!==null)next.sensedPressure=u.pressureBarAbsolute;
 gate(next,u);
 // A latched plant stop never consumes requested time or permits an automatic restart.
 if(u.stop)next.pending=0;
 else {const total=next.pending+seconds,ticks=Math.floor((total+EPS)/CADENCE);next.pending=total;for(let i=0;i<ticks;i++)tick(next,u);next.pending=Math.max(0,total-ticks*CADENCE);if(next.pending<EPS)next.pending=0;}
 Object.assign(s,next);return record(s);
}
// Coupled solver path: consume only committed physical time, including fractional stops.
// Call on a detached trial or after acceptance; never on a rejected plant predictor.
function advanceAccepted(s,seconds,input={}){
 if(!Number.isFinite(seconds)||seconds<0||seconds>CADENCE+EPS)throw Error('Accepted controller interval must be 0–0.1 seconds.');
 if(s.pending>EPS)throw Error('Do not mix pending standalone cadence with accepted plant time.');
 const u=validateInput(input),next=copy(s);
 if(u.stop&&Math.abs(u.stop.seconds-next.time)>EPS)throw Error('Model stop must match the accepted controller clock.');
 next.input=copy(u);next.measuredPressure=u.pressureBarAbsolute;
 if(next.sensedPressure===null&&u.pressureBarAbsolute!==null)next.sensedPressure=u.pressureBarAbsolute;
 gate(next,u);
 if(!u.stop&&seconds>0){tick(next,u,seconds);next.pending=0;}
 Object.assign(s,next);return record(s);
}
function nextBoundary(s){
 if(!s.input?.enabled||!s.input?.available||s.input.pressureBarAbsolute===null||s.stop)return Infinity;
 if(s.running){const at=s.lastSwitch+s.settings.minOn;return !s.input.demand&&at>s.time+EPS?at-s.time:Infinity;}
 if(!s.input.demand)return Infinity;
 const at=s.startDemandAt===null?s.lastSwitch+s.settings.minOff:s.startDemandAt+s.settings.startDelay;
 return at>s.time+EPS?at-s.time:Infinity;
}
function update(s,patch){
 object(patch,'Controller settings');const changedMode='mode' in patch&&patch.mode!==s.settings.mode,nextPatch={...patch};
 if(changedMode&&patch.mode==='manual'&&!('manualSpeed' in patch)&&s.running)nextPatch.manualSpeed=s.speed;
 for(const k of Object.keys(patch))if(!Object.prototype.hasOwnProperty.call(DEFAULTS,k))throw Error('Unknown capacity setting: '+k);
 const c=normalize(s.profile,{...s.settings,...nextPatch});
 if(JSON.stringify(c)===JSON.stringify(s.settings))return record(s);
 if(s.running&&(s.speed<c.minSpeed||s.speed>c.maxSpeed))throw Error('Stop the controller before setting speed limits that exclude its actual speed.');
 s.settings=c;
 if(changedMode){s.command=s.speed;s.rawCommand=s.speed;s.integral=s.speed-c.kp*errorFor(s);s.track=true;}
 // No elapsed time is invented, and unapplied sub-cadence time is discarded at an edit boundary.
 s.pending=0;s.startDemandAt=null;return record(s);
}
function record(s){return copy({schemaVersion:s.schemaVersion,profile:{id:s.profile.id,revision:s.profile.revision,compressors:s.profile.equipment.compressors},settings:s.settings,seconds:s.time,pendingSeconds:s.pending,mode:s.settings.mode,running:s.running,actualSpeed:s.speed,requestedSpeed:s.command,rawCommand:s.rawCommand,measuredPressureBarAbsolute:s.measuredPressure,sensedPressureBarAbsolute:s.sensedPressure,targetBarAbsolute:s.settings.suctionTarget,errorBar:errorFor(s),integral:s.integral,reason:s.reason,limitedBy:s.limitedBy,starts:s.starts,lastSwitchSeconds:s.lastSwitch,minimumOnRemaining:s.running?Math.max(0,s.settings.minOn-(s.time-s.lastSwitch)):0,minimumOffRemaining:!s.running?Math.max(0,s.settings.minOff-(s.time-s.lastSwitch)):0,startDelayRemaining:s.startDemandAt===null?null:Math.max(0,s.settings.startDelay-(s.time-s.startDemandAt)),stop:s.stop,lastStop:s.lastStop});}
const api={DEFAULTS,CADENCE,normalize,create,advance,advanceAccepted,nextBoundary,update,record};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaCapacity=api;
})(typeof globalThis!=='undefined'?globalThis:this);
