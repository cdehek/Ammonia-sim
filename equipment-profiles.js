/* Versioned equipment specifications. Operating settings remain outside profiles. */
(function(root){
'use strict';
const keys=['compressors','displacement','evapUA','condUA','highTrip','lowTrip','dischargeTrip','performanceMode','etaVol','etaIs','etaMotor'];
const connectionBounds={feedAreaM2:[1e-9,.1],feedRecovery:[.1,1],openingExponent:[.2,5],actuatorSeconds:[.05,300],sensorSeconds:[.05,300],drainAreaM2:[1e-9,.1],drainRecovery:[.1,1],drainHeightM:[0,20],outletVolumeFraction:[.01,.5],outletUAFraction:[.001,.5],vaporAreaM2:[1e-9,.1],outletInitialSuperheatK:[0,30]};
const exampleConnections={feedAreaM2:2e-5,feedRecovery:.8,openingExponent:1.5,actuatorSeconds:2,sensorSeconds:2,drainAreaM2:2e-5,drainRecovery:.9,drainHeightM:2,outletVolumeFraction:.15,outletUAFraction:.015,vaporAreaM2:2e-4,outletInitialSuperheatK:5};
const storageKey='ammonia-lab-equipment-v1';
const equipment={compressors:1,displacement:180,evapUA:12,condUA:25,highTrip:24,lowTrip:.4,dischargeTrip:170,performanceMode:'example',etaVol:75,etaIs:75,etaMotor:92};
function object(v,label){if(!v||typeof v!=='object'||Array.isArray(v))throw Error(label+' must be an object.');}
function string(v,label,max,required=false){if(typeof v!=='string'||v.length>max||(required&&!v.trim()))throw Error(label+' must be '+(required?'non-empty ':'')+'text, up to '+max+' characters.');return v.trim();}
function normalize(p){
 object(p,'Profile');if(p.schema!=='ammonia-equipment-profile'||![1,2,3].includes(p.schemaVersion))throw Error('Unsupported equipment profile format/version.');
 const name=string(p.name,'Profile name',80,true),description=string(p.description,'Description',2000),source=string(p.source,'Source',1000);
 if(!['example','assumption','manufacturer'].includes(p.sourceKind))throw Error('Unknown data source category.');
 if(p.sourceKind==='manufacturer'&&!source)throw Error('Provide a manufacturer document/reference. This does not establish validated performance curves.');
 if(p.arrangement!=='single-stage-dx')throw Error('Live equipment profiles currently support single-stage DX with identical compressors.');
 if(!Number.isInteger(p.revision)||p.revision<1||p.revision>100000)throw Error('Invalid profile revision.');
 const id=string(p.id,'Profile ID',100,true);
 for(const key of ['createdAt','updatedAt'])if(typeof p[key]!=='string'||!Number.isFinite(Date.parse(p[key])))throw Error('Invalid profile timestamp.');
 object(p.equipment,'Equipment');const clean={};for(const key of keys){if(!(key in p.equipment))throw Error('Missing equipment specification: '+key);clean[key]=p.equipment[key];}
 const bounds={compressors:[1,3],displacement:[10,2000],evapUA:[.1,1000],condUA:[.1,2000],highTrip:[3,30],lowTrip:[.35,8],dischargeTrip:[80,250],etaVol:[20,100],etaIs:[40,100],etaMotor:[50,100]};
 for(const [key,[low,high]]of Object.entries(bounds))if(typeof clean[key]!=='number'||!Number.isFinite(clean[key])||clean[key]<low||clean[key]>high)throw Error(key+' must be between '+low+' and '+high+' (SI / percent).');
 if(!Number.isInteger(clean.compressors)||clean.lowTrip>=clean.highTrip)throw Error('Use an integer compressor count and low-pressure limit below high-pressure limit.');
 if(!['example','fixed'].includes(clean.performanceMode))throw Error('Choose example curves or fixed efficiency assumptions.');
 const inventory=p.schemaVersion===1?{volumes:p.futureVolumes,initialization:null}:p.inventory;
 object(inventory,'Refrigerant inventory');object(inventory.volumes,'Refrigerant volumes');const volumes={};
 for(const key of ['receiver','evaporator','condenser']){const v=inventory.volumes[key];if(v!==null&&(typeof v!=='number'||!Number.isFinite(v)||v<.0001||v>1000))throw Error(key+' volume must be blank or 0.0001–1000 m³.');volumes[key]=v;}
 let initialization=null;
 if(inventory.initialization!==null){
  const init=inventory.initialization;object(init,'Inventory initialization');
  if(!['levels','charge'].includes(init.mode))throw Error('Choose liquid fills or total charge initialization.');
  if(Object.values(volumes).some(v=>v===null))throw Error('Configure all three refrigerant volumes before enabling initialization.');
  for(const [key,low,high]of [['suctionPressure',.35,8],['dischargePressure',3,30]])if(typeof init[key]!=='number'||!Number.isFinite(init[key])||init[key]<low||init[key]>high)throw Error(key+' must be between '+low+' and '+high+' bar absolute.');
  if(init.suctionPressure>=init.dischargePressure)throw Error('Initial suction pressure must be below initial discharge pressure.');
  object(init.liquidFractions,'Liquid volume fractions');const liquidFractions={};
  for(const key of ['receiver','evaporator','condenser']){
   const v=init.liquidFractions[key];
   if(key==='receiver'&&init.mode==='charge'){if(v!==null)throw Error('Receiver fill must be calculated from total charge, not specified as well.');liquidFractions[key]=null;continue;}
   if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>1)throw Error(key+' liquid volume fraction must be between 0 and 1.');liquidFractions[key]=v;
  }
  if(init.mode==='levels'){if(init.chargeKg!==null)throw Error('Total charge is calculated from liquid fills; do not specify both.');}
  else if(typeof init.chargeKg!=='number'||!Number.isFinite(init.chargeKg)||init.chargeKg<=0||init.chargeKg>1e7)throw Error('Total charge must be greater than zero and at most 10,000,000 kg.');
  initialization={mode:init.mode,chargeKg:init.chargeKg,suctionPressure:init.suctionPressure,dischargePressure:init.dischargePressure,liquidFractions};
 }
 let connections=null;
 if(p.schemaVersion===3&&p.connections!==null){
  object(p.connections,'Valve and outlet specifications');connections={};
  for(const [key,[low,high]]of Object.entries(connectionBounds)){const v=p.connections[key];if(typeof v!=='number'||!Number.isFinite(v)||v<low||v>high)throw Error(key+' must be between '+low+' and '+high+' in SI units.');connections[key]=v;}
 }
 return {schema:'ammonia-equipment-profile',schemaVersion:3,id,name,description,sourceKind:p.sourceKind,source,arrangement:p.arrangement,revision:p.revision,createdAt:p.createdAt,updatedAt:p.updatedAt,equipment:clean,inventory:{volumes,initialization},connections};
}
const DEFAULT=normalize({schema:'ammonia-equipment-profile',schemaVersion:3,id:'default',name:'Default',description:'Built-in example equipment. Duplicate it to create your own specifications.',sourceKind:'example',source:'Ammonia Lab example curves; see DYNAMIC_MODEL.md.',arrangement:'single-stage-dx',revision:3,createdAt:'2026-10-07T00:00:00.000Z',updatedAt:'2026-10-07T00:00:00.000Z',equipment,connections:exampleConnections,inventory:{volumes:{receiver:.25,evaporator:.08,condenser:.12},initialization:{mode:'levels',chargeKg:null,suctionPressure:2.5,dischargePressure:12,liquidFractions:{receiver:.3,evaporator:.1,condenser:.1}}}});
Object.freeze(DEFAULT.connections);Object.freeze(DEFAULT.equipment);Object.freeze(DEFAULT.inventory.volumes);Object.freeze(DEFAULT.inventory.initialization.liquidFractions);Object.freeze(DEFAULT.inventory.initialization);Object.freeze(DEFAULT.inventory);Object.freeze(DEFAULT);
const copy=p=>JSON.parse(JSON.stringify(p));
const newId=()=> 'equipment-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,10);
function duplicate(p,name){const clean=normalize(p),now=new Date().toISOString();return {...copy(clean),id:newId(),name:name||clean.name+' copy',revision:1,createdAt:now,updatedAt:now};}
function revise(original,draft){const base=normalize(original);if(base.id==='default')throw Error('Default is read-only. Duplicate it first.');return normalize({...draft,id:base.id,revision:base.revision+1,createdAt:base.createdAt,updatedAt:new Date().toISOString()});}
function imported(p){const clean=normalize(p);return normalize({...copy(clean),id:newId(),name:clean.id==='default'?'Default imported':clean.name});}
function restore(raw){object(raw,'Profile library');if(![1,2,3].includes(raw.schemaVersion)||!Array.isArray(raw.profiles)||raw.profiles.length>20)throw Error('Invalid equipment library.');const profiles=[],seen=new Set();let rejected=0,migrated=0;for(const p of raw.profiles){try{const clean=normalize(p);if(clean.id==='default'||seen.has(clean.id))throw Error('Duplicate/reserved ID.');seen.add(clean.id);profiles.push(clean);if(p.schemaVersion<3)migrated++;}catch{rejected++;}}return {profiles,activeId:raw.activeId==='default'||seen.has(raw.activeId)?raw.activeId:'default',rejected,migrated};}
function apply(config,profile){const p=normalize(profile);return {...config,...p.equipment};}
const api={keys,connectionBounds,storageKey,DEFAULT,normalize,duplicate,revise,imported,restore,apply,copy};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaProfiles=api;
})(typeof globalThis!=='undefined'?globalThis:this);
