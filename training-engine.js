/* Guided exercises observe accepted model data; they never fabricate readings. */
(function(root){
'use strict';
const copy=x=>JSON.parse(JSON.stringify(x)),last=a=>a[a.length-1],near=(a,b,t=1e-8)=>Number.isFinite(a)&&Math.abs(a-b)<=t;
const C=typeof module!=='undefined'&&module.exports?require('./capacity-controller'):root.AmmoniaCapacity;
const ROOM={initial:15,thermalMass:30,leakUA:.1,gain:2,ambient:25};
const OPS={circuit:'circulating',thermalMode:'air',compressorOn:true,speed:.7,valveMode:'auto',manualOpening:.25,superheatTarget:5,kp:.04,ki:.004,drainEnabled:true,receiverHeat:0,evaporatorHeat:0,condenserHeat:0};
const EXERCISES={

 startup:{name:'DX startup',warmup:0,description:'Follow inventory and feed response from initialized equilibrium. Advance until the measured startup objectives are met.',goals:['Establish positive liquid feed and compressor demand after 10 s.','Run at least 60 s and observe actual/sensed superheat within ±1 K of target for 20 consecutive simulated seconds.','Answer the reflection correctly.'],question:'Which reading comes from the resolved evaporator outlet?',answers:['Actual outlet superheat','Valve command','Condenser bulk temperature'],correct:0,hint:'Use actual and sensed superheat trends together. Initial equilibrium is not proof of settled control.',debrief:'Inventory distribution and actuator/sensor lag create a startup transient. A momentary target crossing is not sustained control.'},
 load:{name:'Room load increase',warmup:30,description:'From a 30 s warmup, apply a room heat-gain increase from 2 to 20 kW. Observe another 30 s without changing other controls.',goals:['Apply the 20 kW load without an instantaneous room-temperature jump.','Observe 30 s at increased load with room-temperature response and no stop.','Answer the reflection correctly.'],operations:{},boundary:{gain:20},action:'Apply 20 kW room load',question:'What does the load button change directly?',answers:['Room heat input','Compressor speed','Stored refrigerant charge'],correct:0,hint:'The room has thermal capacity. Changing heat input changes its rate of response, not its temperature instantly.',debrief:'The disturbance enters through the room-energy boundary. Refrigerant inventories and pressures respond through the existing coupled model.'},
 hot:{name:'Hot condenser air',warmup:30,description:'Apply 104 °F (40 °C) condenser air after a 30 s warmup. Observe rising condenser pressure and the computed discharge-temperature trip. Restore off-state controls, clear the stop, and advance 10 s.',goals:['Apply hot air and observe condenser pressure rise by at least 0.5 bar.','Observe the modeled high-discharge-temperature equipment trip.','Restore off-state controls, clear the stop, and observe 10 s of stopped-compressor operation.','Answer the reflection correctly.'],operations:{},boundary:{ambient:40},action:'Apply 104 °F (40 °C) condenser air',question:'Which limit stops this Default exercise?',answers:['High discharge temperature','High discharge pressure','Low suction pressure'],correct:0,hint:'Read the recorded stop evidence. Restore sets air to 77 °F (25 °C), disables compression, and commands feed closed; clearing alone is not correction.',debrief:'Hotter condenser air reduces heat rejection and changes compression demand. Off-state continuation after clearing demonstrates model continuation, not qualification for a real plant restart.'},
 restriction:{name:'Restricted liquid feed',warmup:30,description:'Command 2% manual feed after a 30 s warmup. Inspect actuator lag and reduced flow after 10 s; answer the reflection promptly. Prolonged starvation may cause a temperature trip.',goals:['Observe actual opening remain above the new 2% command immediately after application.','After 10 s, observe feed below half its baseline with actual opening below 4%, without a stop.','Answer the reflection correctly.'],operations:{valveMode:'manual',manualOpening:.02},boundary:{},action:'Command 2% manual feed',question:'How does the modeled valve respond to the new command?',answers:['Opening follows with actuator lag','Flow stops instantly','The valve removes system charge'],correct:0,hint:'Compare command, actual opening and liquid-feed flow. This exercise changes effective opening, not valve geometry or total charge.',debrief:'Reduced opening limits pressure-driven feed. Actuator lag delays the flow response; prolonged starvation can reach a supported compression limit.'},
 tuning:{name:'Superheat target response',warmup:120,description:'Begin after a 120 s warmup. Raise the automatic target from 9 to 12.6 °F difference (5 to 7 K), then observe actual/sensed superheat within ±0.5 K for 20 consecutive simulated seconds.',goals:['Apply the 7 K automatic target.','Observe the new band for 20 consecutive simulated seconds, at least 30 s after the change.','Answer the reflection correctly.'],operations:{superheatTarget:7},boundary:{},action:'Set target to 7 K',question:'Which measured value drives the PI feed controller?',answers:['Lagged sensed outlet superheat','Receiver liquid level','Reference-cycle calculator temperature'],correct:0,hint:'The established warmup matters. Target changes during early inventory redistribution can produce a different outcome. Observe both actual and lagged sensed readings.',debrief:'The PI law uses sensed superheat error; actuator and sensor dynamics delay the response. This is a target-response exercise, not a manufacturer-validated gain-tuning procedure.'},
 'capacity-startup':{name:'Managed compressor startup',warmup:0,initialOperations:{compressorOn:false,valveMode:'closed'},initialCapacity:{mode:'manual',minOff:3,startDelay:2,minOn:7.5},description:'Start disabled with feed closed. Apply enable before advancing; observe 3 s minimum rest, then 2 s continuous start delay and ramped capacity. These shortened illustrative timers are for this lesson only.',goals:['Observe zero capacity during minimum rest and continuous start delay.','Observe the first accepted compressor start at 5 simulated seconds.','Observe five seconds of running response with positive compressor demand and no stop.','Answer the reflection correctly.'],operations:{compressorOn:true},boundary:{},action:'Enable managed compressor',question:'What happens after minimum rest expires?',answers:['Continuous start delay must also expire','Capacity jumps directly to 70%','Suction pressure is assigned to its target'],correct:0,hint:'Read compressor state separately from playback. Rest and start delay are sequential. Opening feed is outside this timing lesson.',debrief:'Enable grants permission; it does not bypass rest or continuous start delay. Delivered speed enters at the minimum supported speed and ramps. Timers are shortened teaching assumptions, not equipment specifications.'},
 'capacity-hold':{name:'Minimum-run demand hold',warmup:0,initialOperations:{valveMode:'closed'},initialCapacity:{mode:'manual',minOff:3,startDelay:2,minOn:7.5},description:'Begin from an already-running 70% snapshot with zero elapsed run age and feed closed. Remove ordinary demand before advancing; observe a 7.5 s minimum-run hold, then zero capacity. Master permission remains enabled.',goals:['Observe running capacity held after ordinary run demand is removed.','Observe the accepted demand stop at 7.5 simulated seconds.','Continue off to 10 simulated seconds without a stop.','Answer the reflection correctly.'],operations:{compressorDemand:false},boundary:{},action:'Remove ordinary run demand',question:'Which input overrides minimum run time immediately?',answers:['Disabling master compressor permission','Removing ordinary run demand','Pausing browser playback'],correct:0,hint:'Run demand and master permission have different priority. The 7.5 s minimum run is a shortened lesson assumption; an operator disable or independent model stop overrides it.',debrief:'Ordinary demand withdrawal honors minimum run time; master disable and modeled trips inhibit immediately. An off compressor still has evolving refrigerant pressures. This lesson does not add a room thermostat or bank sequencing.'},
 'capacity-response':{name:'Automatic suction target response',warmup:120,initialCapacity:{mode:'auto',suctionTarget:4.5},description:'After 120 s of actual managed automatic/feed warmup, raise suction target from 4.5 to 6 bar absolute (about 50.6 to 72.3 psig). Observe capacity decrease and suction pressure rise over 30 s. Target attainment is not required.',goals:['Apply the 6 bar absolute target without an instantaneous speed or pressure jump.','After 30 s, observe delivered speed at least 5 percentage points lower and suction at least 0.1 bar higher than baseline, without a stop.','Answer the reflection correctly.'],operations:{},boundary:{},capacity:{suctionTarget:6},action:'Raise suction target to 6 bar(a)',question:'How does greater suction pressure above target affect automatic demand?',answers:['It requests greater compressor capacity','It assigns suction pressure directly','It changes refrigerant charge'],correct:0,hint:'Inspect measured/sensed suction and requested/actual capacity. The disturbance changes only the target; pressure responds through mass and energy balances.',debrief:'Relaxing the suction target reduces delivered compression and lets suction pressure rise through the connected model. This short response is not proof of settled target tracking or manufacturer-validated tuning.'}
};
function setup(id){const d=EXERCISES[id];if(!d)throw Error('Unknown exercise.');return {room:{...ROOM},operations:{...OPS,...(d.initialOperations||{}),...(d.initialCapacity?{compressorDemand:true}:{})},capacity:d.initialCapacity?{...d.initialCapacity}:null,warmup:d.warmup};}
function start(id,s){
 const d=EXERCISES[id];if(!d)throw Error('Unknown exercise.');if(s.profile.id!=='default'||s.fault)throw Error('Exercises require supported Default equipment without a stop.');
 const a={schemaVersion:1,appVersion:'0.5.5',exercise:id,status:'active',startedAt:s.time,lastSampleId:last(s.history.samples).id,profile:copy(s.profile),initialRoom:copy(s.initialRoomConfig),baseline:copy(last(s.history.samples)),initialCapacitySettings:d.initialCapacity?C.normalize(s.profile,{manualSpeed:OPS.speed,...d.initialCapacity}):null,goals:d.goals.map(label=>({label,met:false,evidence:null})),injectedAt:null,holdStart:null,expectedFault:null,restored:false,quizAttempts:[],actions:[],endedAt:null,reason:null};
 if(!compatible(a,last(s.history.samples)))throw Error('Controls differ from the supported exercise setup.');return a;
}
function mark(a,index,p,values={}){if(!a.goals[index].met)a.goals[index]={...a.goals[index],met:true,evidence:{seconds:p.seconds,sampleId:p.id,...copy(values)}};}
function injected(a,s){if(a.status!=='active'||a.injectedAt!==null)throw Error('Load/reset the exercise before applying another disturbance.');a.injectedAt=s.time;a.lastSampleId=last(s.history.samples).id-1;a.actions.push({type:'disturbance',seconds:s.time,operations:copy(s.operations),roomBoundary:copy(last(s.history.samples).roomBoundary),capacity:s.capacity?C.record(s.capacity):null});}
function restored(a,s){if(a.exercise!=='hot'||!a.expectedFault||a.status!=='active')throw Error('Observe the hot-air stop before restoring controls.');a.restored=true;a.restoredAt=s.time;a.actions.push({type:'restore-off-state',seconds:s.time});}
function finish(a,status,seconds,reason=null){if(a.status!=='active')return;a.status=status;a.endedAt=seconds;a.reason=reason;}
function compatible(a,p){
 const o=p.operations,r=p.roomBoundary,id=a.exercise,injected=a.injectedAt!==null;
 const d=EXERCISES[id],expect={...OPS,...(d.initialOperations||{}),...(d.initialCapacity?{compressorDemand:true}:{}),...(injected?(EXERCISES[id].operations||{}):{})},boundary={ambient:25,gain:2,leakUA:.1,...(injected?(EXERCISES[id].boundary||{}):{})};
 if(id==='hot'&&a.restored){expect.compressorOn=false;expect.valveMode='closed';boundary.ambient=25;}
 const expectedCapacity=a.initialCapacitySettings?{...a.initialCapacitySettings,...(injected?(d.capacity||{}):{})}:null;
 if(!!p.capacity!==!!expectedCapacity||expectedCapacity&&!Object.entries(expectedCapacity).every(([k,v])=>typeof v==='number'?near(p.capacity.settings[k],v,1e-12):p.capacity.settings[k]===v))return false;
 return Object.entries(expect).every(([k,v])=>typeof v==='number'?near(o[k],v):o[k]===v)&&Object.entries(boundary).every(([k,v])=>near(r[k],v));
}
function observe(a,s){
 if(!a||a.status!=='active')return;
 if(a.initialCapacitySettings&&a.injectedAt===null&&s.time>a.startedAt+1e-8){finish(a,'interrupted',s.time,'Apply the lesson action before advancing. Reset to repeat the supported exercise.');return;}
 const d=EXERCISES[a.exercise],points=s.history.samples.filter(p=>p.id>a.lastSampleId);
 if(points.length&&points[0].id>a.lastSampleId+1){finish(a,'interrupted',s.time,'Required observations were removed by history retention. Reset the exercise.');return;}
 for(const p of points){
  a.lastSampleId=p.id;if(p.reason==='before-change')continue;
  if(!compatible(a,p)){finish(a,'interrupted',p.seconds,'Controls differ from the exercise setup. Reset to repeat the supported exercise.');break;}
  const elapsed=p.seconds-a.startedAt,since=a.injectedAt===null?null:p.seconds-a.injectedAt,id=a.exercise;
  if(id==='capacity-startup'&&since!==null){
   const c=p.capacity;if(!c.running&&c.actualSpeed===0){if(c.reason==='Minimum off time')a.restObserved=copy({seconds:p.seconds,sampleId:p.id});if(c.reason==='Start delay'&&a.restObserved)mark(a,0,p,{rest:a.restObserved,startDelaySeconds:c.startDelayRemaining});}
   if(c.running&&c.starts===1&&near(c.lastSwitchSeconds,5))mark(a,1,p,{startSeconds:c.lastSwitchSeconds,actualSpeed:c.actualSpeed});
   if(p.seconds>=10-1e-8&&c.running&&p.electricalDemand>0&&!p.faultKind)mark(a,2,p,{actualSpeed:c.actualSpeed,electricalKW:p.electricalDemand});
  }
  if(id==='capacity-hold'&&since!==null){
   const c=p.capacity;if(c.running&&c.reason==='Minimum on time'&&c.minimumOnRemaining>0)mark(a,0,p,{remainingSeconds:c.minimumOnRemaining,actualSpeed:c.actualSpeed});
   if(!c.running&&c.actualSpeed===0&&near(c.lastSwitchSeconds,7.5))mark(a,1,p,{stopSeconds:c.lastSwitchSeconds});
   if(p.seconds>=10-1e-8&&!c.running&&!p.faultKind)mark(a,2,p,{actualSpeed:c.actualSpeed,suctionBar:p.pressures.outlet});
  }
  if(id==='capacity-response'&&since!==null){
   const c=p.capacity,b=a.baseline.capacity;
   if(since<1e-8&&near(c.actualSpeed,b.actualSpeed)&&near(p.pressures.outlet,a.baseline.pressures.outlet))mark(a,0,p,{targetBar:c.targetBarAbsolute,actualSpeed:c.actualSpeed,suctionBar:p.pressures.outlet});
   if(since>=30-1e-8&&c.actualSpeed<=b.actualSpeed-.05&&p.pressures.outlet>=a.baseline.pressures.outlet+.1&&!p.faultKind)mark(a,1,p,{actualSpeed:c.actualSpeed,baselineSpeed:b.actualSpeed,suctionBar:p.pressures.outlet,baselineSuctionBar:a.baseline.pressures.outlet});
  }
  if(id==='startup'){
   if(elapsed>=10-1e-8&&p.feedMassFlow>0&&p.electricalDemand>0)mark(a,0,p,{feedKgS:p.feedMassFlow});
   const band=near(p.actualSuperheat,5,1)&&near(p.sensedSuperheat,5,1)&&!p.faultKind;
   if(!band)a.holdStart=null;else if(a.holdStart===null)a.holdStart=p.seconds;
   if(elapsed>=60-1e-8&&a.holdStart!==null&&p.seconds-a.holdStart>=20-1e-8)mark(a,1,p,{holdSince:a.holdStart,actualSuperheatK:p.actualSuperheat,sensedSuperheatK:p.sensedSuperheat});
  }
  if(id==='load'&&since!==null){
   if(since<1e-8&&near(p.temperatures.room,a.baseline.temperatures.room))mark(a,0,p,{gainKW:p.roomBoundary.gain});
   if(since>=30-1e-8&&!p.faultKind&&Math.abs(p.temperatures.room-a.baseline.temperatures.room)>1e-6)mark(a,1,p,{roomC:p.temperatures.room,baselineRoomC:a.baseline.temperatures.room});
  }
  if(id==='restriction'&&since!==null){
   if(since<1e-8&&p.opening>p.command+.01)mark(a,0,p,{command:p.command,opening:p.opening});
   if(since>=10-1e-8&&!p.faultKind&&p.opening<.04&&p.feedMassFlow<a.baseline.feedMassFlow*.5)mark(a,1,p,{feedKgS:p.feedMassFlow,baselineFeedKgS:a.baseline.feedMassFlow});
  }
  if(id==='tuning'&&since!==null){
   mark(a,0,p,{targetK:p.targetSuperheat});const band=near(p.actualSuperheat,7,.5)&&near(p.sensedSuperheat,7,.5)&&!p.faultKind;
   if(!band)a.holdStart=null;else if(a.holdStart===null)a.holdStart=p.seconds;
   if(since>=30-1e-8&&a.holdStart!==null&&p.seconds-a.holdStart>=20-1e-8)mark(a,1,p,{holdSince:a.holdStart,actualSuperheatK:p.actualSuperheat,sensedSuperheatK:p.sensedSuperheat});
  }
  if(id==='hot'&&since!==null){
   if(p.pressures.condenser>=a.baseline.pressures.condenser+.5)mark(a,0,p,{condenserBar:p.pressures.condenser,baselineBar:a.baseline.pressures.condenser});
   if(a.restored&&!p.faultKind&&p.seconds-(a.restoredAt??Infinity)>=10-1e-8)mark(a,2,p,{compressorEnabled:p.operations.compressorOn,ambientC:p.roomBoundary.ambient});
  }
 }
 if(a.status!=='active')return;
 if(a.exercise==='hot'&&a.restored&&a.expectedFault&&!s.fault&&!s.operations.compressorOn&&near(s.roomConfig.ambient,25)&&s.time-a.restoredAt>=10-1e-8){
  mark(a,2,{seconds:s.time,id:null},{source:'accepted endpoint',compressorEnabled:false,ambientC:s.roomConfig.ambient});
 }
 if(s.fault){
  if(a.exercise==='hot'&&a.injectedAt!==null&&s.fault.kind==='equipment'&&s.fault.message==='High discharge temperature'){
   if(!a.expectedFault){a.expectedFault=copy(s.fault);mark(a,1,last(s.history.samples),{fault:copy(s.fault)});}
  }else finish(a,'stopped',s.time,s.fault.message);
 }
 if(a.status==='active'&&a.goals.every(g=>g.met))finish(a,'completed',s.time);
}
function answer(a,index,seconds){
 if(a.status!=='active')throw Error('Load/reset an exercise to submit a reflection.');
 if(!Number.isInteger(index)||index<0||index>=EXERCISES[a.exercise].answers.length)throw Error('Select a reflection answer.');
 const correct=index===EXERCISES[a.exercise].correct;a.quizAttempts.push({seconds,index,correct});if(correct)mark(a,a.goals.length-1,{seconds,id:null},{answerIndex:index});return correct;
}
function report(a,s){return copy({attempt:a,history:s.history,final:{seconds:s.time,fault:s.fault,operations:s.operations,capacity:s.capacity?C.record(s.capacity):null,roomBoundary:last(s.history.samples).roomBoundary},interpretation:'Training evidence for the supported Default model; not measured plant or real restart qualification.'});}
const api={EXERCISES,setup,start,injected,restored,observe,answer,finish,report};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaTraining=api;
})(typeof globalThis!=='undefined'?globalThis:this);
