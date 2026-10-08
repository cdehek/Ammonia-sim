/* Bounded SI observation history. No integration, interpolation or plant control. */
(function(root){
'use strict';
const copy=x=>JSON.parse(JSON.stringify(x));
const LIMITS={samples:7201,events:2000,cadenceSeconds:1};
function changes(before,after){
 const result=[];
 for(const scope of ['operations','roomBoundary'])for(const key of Object.keys(after[scope])){
  const a=before[scope][key],b=after[scope][key];
  if(a!==b&&!(typeof a==='number'&&typeof b==='number'&&Math.abs(a-b)<1e-12))result.push({scope,key,before:a,after:b});
 }
 return result;
}
function sample(h,r,compressor,reason='periodic'){
 const finite=x=>Number.isFinite(x)?x:null,connected=!!r.vessels.outlet;
 const point={id:h.nextSampleId++,seconds:r.seconds,reason,pressures:{},temperatures:{room:r.T,ambient:r.roomBoundary.ambient},levels:{},roomBoundary:{...r.roomBoundary},operations:{...r.operations},actualSuperheat:finite(r.flows?.superheat),sensedSuperheat:connected?r.controller.sensor:null,targetSuperheat:connected?r.operations.superheatTarget:null,opening:connected?r.controller.opening:null,command:finite(r.flows?.command),speedSetting:r.operations.speed,electricalDemand:finite(compressor?.electrical),dischargeTemperature:finite(compressor?.dischargeTemperature),faultKind:r.fault?.kind??null};
 for(const [key,v]of Object.entries(r.vessels)){point.pressures[key]=v.p;point.temperatures[key]=v.T;point.levels[key]=v.liquidVolumeFraction;}
 h.samples.push(point);
 if(h.samples.length>h.limits.samples){h.samples.shift();h.droppedSamples++;}
 return point;
}
function event(h,seconds,type,details={}){
 const value={id:h.nextEventId++,seconds,type,sampleId:h.samples[h.samples.length-1]?.id??null,details:copy(details)};
 h.events.push(value);if(h.events.length>h.limits.events){h.events.shift();h.droppedEvents++;}return value;
}
function create(r,profile,initialRoom,compressor,limits=LIMITS){
 if(!Number.isInteger(limits.samples)||limits.samples<2||!Number.isInteger(limits.events)||limits.events<1||!Number.isFinite(limits.cadenceSeconds)||limits.cadenceSeconds<=0)throw Error('Invalid history retention settings.');
 const h={schemaVersion:1,profile:copy(profile),initialRoom:copy(initialRoom),limits:{...limits},samples:[],events:[],nextAt:limits.cadenceSeconds,nextSampleId:1,nextEventId:1,droppedSamples:0,droppedEvents:0};
 sample(h,r,compressor,'initialize');event(h,r.seconds,'initialize',{operations:r.operations,roomBoundary:r.roomBoundary,profileName:profile.name,profileRevision:profile.revision});return h;
}
function due(h,seconds){return seconds>=h.nextAt-1e-8;}
function periodic(h,r,compressor){
 if(!due(h,r.seconds))return;
 sample(h,r,compressor);while(h.nextAt<=r.seconds+1e-8)h.nextAt+=h.limits.cadenceSeconds;
}
function csv(h){
 const keys=['receiver','condenser','evaporator','outlet'];
 const header=['Record type','Sequence','Seconds','Observation reason','Room C','Ambient C',...keys.map(k=>k+' bar absolute'),...keys.map(k=>k+' C'),...keys.map(k=>k+' liquid volume fraction'),'Actual superheat K','Sensed superheat K','Target superheat K','Actual valve fraction','Valve command fraction','Compressor speed setting fraction','Electrical demand kW','Compressor discharge C','Fault kind','Event type','Linked sample ID','Details JSON SI'];
 const samples=h.samples.map(s=>({seconds:s.seconds,sample:s.id,kind:0,row:['sample',s.id,s.seconds,s.reason,s.temperatures.room,s.temperatures.ambient,...keys.map(k=>s.pressures[k]??''),...keys.map(k=>s.temperatures[k]??''),...keys.map(k=>s.levels[k]??''),s.actualSuperheat??'',s.sensedSuperheat??'',s.targetSuperheat??'',s.opening??'',s.command??'',s.speedSetting,s.electricalDemand??'',s.dischargeTemperature??'',s.faultKind??'','',s.id,JSON.stringify(s)]}));
 const events=h.events.map(e=>{const row=Array(header.length).fill('');row[0]='event';row[1]=e.id;row[2]=e.seconds;row[header.indexOf('Event type')]=e.type;row[header.indexOf('Linked sample ID')]=e.sampleId??'';row[row.length-1]=JSON.stringify(e);return {seconds:e.seconds,sample:e.sampleId??0,kind:1,row};});
 const records=[...samples,...events].sort((a,b)=>a.seconds-b.seconds||a.sample-b.sample||a.kind-b.kind);
 const rows=[['History schema',h.schemaVersion],['Equipment JSON SI',JSON.stringify(h.profile)],['Initial room conditions JSON SI',JSON.stringify(h.initialRoom)],['Retention JSON',JSON.stringify({limits:h.limits,droppedSamples:h.droppedSamples,droppedEvents:h.droppedEvents})],header,...records.map(r=>r.row)];
 return rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n');
}
const api={LIMITS,create,sample,event,changes,due,periodic,csv};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaHistory=api;
})(typeof globalThis!=='undefined'?globalThis:this);
