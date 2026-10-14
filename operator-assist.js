/* Offline, deterministic display projection. No simulator references or commands. */
(function(root){
'use strict';
function analyze({record:r=null,compressor:c=null,running=false,units={p:'psig',T:'F'},draft=false}={}){
 const finite=Number.isFinite,fmt=(v,u)=>finite(v)?v.toFixed(2)+' '+u:'Unavailable';
 const pressure=v=>finite(v)?(v-(units.p.endsWith('g')?1.01325:0))*(units.p.startsWith('psi')?14.503773773:1):null;
 const pu={bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'}[units.p];
 const temperature=v=>finite(v)?(units.T==='F'?v*1.8+32:v):null;
 const delta=v=>finite(v)?v*(units.T==='F'?1.8:1):null;
 const percent=v=>finite(v)?v*100:null;
 const reading=(label,value,note)=>({label,value,note});
 const empty={status:'NOT INITIALIZED',tone:'idle',explanation:'There is no accepted connected-model state to interpret yet.',compressor:'Compressor state unavailable.',readings:[],evidence:[],tip:'Initialize auto DX to explore the connected circuit, or inspect the equipment profile first.',scope:'Connected simulator only · deterministic rules · read-only',settings:'No applied connected settings.'};
 if(!r)return empty;
 if(!pu||!['C','F'].includes(units.T)||!['closed','circulating'].includes(r.operations?.circuit)||!finite(r.seconds))return {...empty,status:'UNSUPPORTED STATE',explanation:'The connected record or display units are unsupported. No operating diagnosis is available.',tip:'Inspect the connected model and selected units.'};
 const o=r.operations,connected=o.circuit==='circulating'&&!!r.vessels?.outlet;
 const flows=connected&&r.flows&&!r.flows.error?r.flows:null;
 const enabled=o.compressorOn===true,disabled=o.compressorOn===false;
 const setting=fmt(percent(o.speed),'%');
 const compressor=disabled?'Disabled in applied settings; compressor is off.':!enabled?'Compressor enabled state unavailable.':r.fault?'Enabled at '+setting+' in applied settings; the recorded stop inhibits compressor demand.':!running?'Enabled at '+setting+' in applied settings; playback is paused, so the compressor is not actively advancing.':c?.inhibited?'Enabled at '+setting+'; current compressor demand is unavailable: '+(c.error||'no observation reason recorded')+'.':finite(c?.massFlow)&&c.massFlow>0?'Enabled at '+setting+'; playback is advancing with supported current compressor demand.':c?.massFlow===0?'Enabled at '+setting+'; playback is advancing, but observed current compressor demand is zero.':'Enabled at '+setting+'; current compressor demand is unavailable.';
 const out={status:running?'OPERATING':'PLAYBACK PAUSED',tone:running?'running':'paused',seconds:r.seconds,explanation:running?'The modeled system is operating as playback advances. No active modeled trip or stop is recorded.':'Playback is paused at the accepted model state. No active modeled trip or stop is recorded.',compressor,
  readings:[reading('Suction pressure',fmt(pressure((r.vessels?.outlet||r.vessels?.evaporator)?.p),pu),connected?'Resolved outlet volume':'Evaporator vapor boundary'),reading('Discharge / condenser pressure',fmt(pressure(r.vessels?.condenser?.p),pu),'Condenser bulk state'),reading('Applied compressor speed',setting,enabled?'Enabled setting · separate from playback':disabled?'Disabled setting':'Enablement unavailable'),reading('Actual outlet superheat',fmt(delta(flows?.superheat),units.T==='F'?'°F Δ':'K'),connected?'Current outlet state':'Unavailable in isolated circuit'),reading('Actual feed-valve opening',fmt(connected?percent(r.controller?.opening):null,'%'),connected?'Accepted actuator position':'Unavailable in isolated circuit'),reading('Feed-valve command',fmt(percent(flows?.command),'%'),flows?'Current command · '+o.valveMode:'No supported command observation')],evidence:[],
  observation:flows?'Actual opening is the accepted actuator position; the command is its current target. Superheat is an outlet temperature difference, not an absolute temperature.':'Connected feed and superheat observations are unavailable for this state.',
  tip:running?(connected?'Inspect the feed valve and outlet in the schematic; compare command, actual opening and superheat. A changing reading alone does not establish a fault.':'Inspect vessel inventory and thermal boundaries; isolated volumes provide no connected feed or outlet superheat readings.'):'Start playback to watch accepted readings evolve, or select equipment in the schematic to inspect the current state.',scope:empty.scope,
  settings:draft?'Unapplied draft controls present. This analysis uses accepted readings and applied settings.':'Analysis uses accepted readings and applied settings.'};
 const fault=r.fault;
 if(!fault)return out;
 const kind=fault.kind,known=['equipment','solver','domain'].includes(kind),v=fault.readings||{};
 out.status=kind==='equipment'?'EQUIPMENT TRIP':kind==='solver'?'NUMERICAL / SOLVER STOP':kind==='domain'?'MODEL-DOMAIN STOP':'RECORDED STOP';
 out.tone=kind==='equipment'?'equipment':'model';
 out.explanation=kind==='equipment'?'The simulator recorded an equipment trip. Playback is stopped; captured evidence below belongs to that stop.':known?'The simulator stopped at a numerical or model-domain boundary. This is not an equipment trip. Captured readings describe the accepted state, not a rejected trial.':'A stop is recorded, but its category is unsupported. No cause is inferred.';
 out.reason=typeof fault.message==='string'?fault.message:'Original recorded reason unavailable';
 out.detected=finite(fault.seconds)?fault.seconds.toFixed(3)+' s simulated':'Unavailable';
 out.readings=[reading('Captured suction pressure',fmt(pressure(v.pressure),pu),'Recorded stop evidence'),reading('Captured discharge pressure',fmt(pressure(v.condensing),pu),'Recorded stop evidence'),reading('Captured discharge temperature',fmt(temperature(v.discharge),'°'+units.T),'Unavailable if not captured'),reading('Captured compressor speed',fmt(percent(v.speed),'%'),'Recorded setting; not proof of running')];
 const thresholds={'High discharge pressure':['highTrip','Modeled high-pressure trip threshold','condensing','≥',pressure,pu],'Low suction pressure':['lowTrip','Modeled low-pressure trip threshold','pressure','≤',pressure,pu],'High discharge temperature':['dischargeTrip','Modeled discharge-temperature trip threshold','discharge','≥',temperature,'°'+units.T]};
 const threshold=kind==='equipment'?thresholds[fault.message]:null;
 if(threshold){const [key,label,captured,relation,convert,unit]=threshold;out.evidence.push(reading(label,fmt(convert(fault.limits?.[key]),unit),'Recorded profile limit'));if(finite(v[captured])&&finite(fault.limits?.[key]))out.observation='Recorded triggering comparison: '+fmt(convert(v[captured]),unit)+' '+relation+' '+fmt(convert(fault.limits[key]),unit)+'. This is a modeled threshold, not a real-plant safety rating.';else out.observation='Triggering comparison unavailable; the original recorded reason is retained.';}
 else out.observation=fault.attemptedReadings?'Rejected trial evidence is retained in fault history and is separate from the accepted captured readings shown here.':'No additional triggering comparison is available for this recorded stop.';
 out.tip='Inspect the stop in Trends & history'+(threshold?' and review its recorded modeled threshold.':'; review the original reason and supported model inputs.')+' Clearing a stop removes the latch; it does not establish that the underlying issue is repaired.';
 return out;
}
const api={analyze};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaOperatorAssist=api;
})(typeof globalThis!=='undefined'?globalThis:this);
