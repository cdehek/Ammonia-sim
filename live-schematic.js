/* Connected-circuit display only. Values are supplied by the storage model. */
(function(root){
'use strict';
const names={compressor:'Compressor bank',condenser:'Condenser',receiver:'Receiver',feed:'Liquid feed valve',evaporator:'Evaporator core',outlet:'Outlet / suction'};
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function create(container){
 let current=null,units={T:'F',p:'psig'},running=false,selected='receiver',motion=true;
 container.innerHTML='<div class="schematic-heading"><div><h3>Live refrigerant schematic <span class="schematic-scope">Illustrative · no physical scale</span></h3><p id="schematic-status" class="hint">Initialize storage to see model readings.</p></div><button type="button" class="btn" id="schematic-motion" aria-pressed="true">Flow animation: on</button></div><div id="schematic-graphic" class="schematic-scroll" tabindex="0" role="region" aria-label="Live schematic; scroll horizontally on small screens"></div><p id="schematic-flow-note" class="hint"></p><div class="schematic-select" role="group" aria-label="Inspect equipment">'+Object.entries(names).map(([key,name])=>'<button type="button" class="btn" data-component="'+key+'" aria-pressed="'+(key===selected)+'">'+name+'</button>').join('')+'</div><div id="schematic-detail" class="schematic-detail"></div><p class="hint">Swipe the diagram horizontally on smaller screens; tap equipment or use the inspection buttons below. Liquid fill represents modeled liquid volume fraction in a lumped vessel, not a measured sight-glass height. Arrows show supported transport direction; animation indicates playback with positive modeled flow, not measured velocity. Dashed connections are isolated.</p>';
 const $=id=>container.querySelector('#'+id),f=(v,n=2)=>Number.isFinite(v)?v.toFixed(n):'—';
 const p=v=>f((v-(units.p.endsWith('g')?1.01325:0))*(units.p.startsWith('psi')?14.503773773:1))+' '+({bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'})[units.p];
 const T=v=>f(units.T==='F'?v*1.8+32:v)+' °'+units.T;
 const delta=v=>f(v*(units.T==='F'?1.8:1))+' '+(units.T==='F'?'°F Δ':'K');
 // Illustrative industrial symbols, not physical dimensions or extra equipment.
 const tx=(x,y,value,cls='schematic-caption',attrs='')=>'<text x="'+x+'" y="'+y+'" class="'+cls+'" '+attrs+'>'+esc(value)+'</text>';
 const rect=(x,y,w,h,fill,rx=3,extra='')=>'<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+rx+'" fill="'+fill+'" '+extra+'/>';
 const line=(d,stroke,width=2,extra='')=>'<path d="'+d+'" fill="none" stroke="'+stroke+'" stroke-width="'+width+'" '+extra+'/>';
 const circle=(x,y,rad,fill,extra='')=>'<circle cx="'+x+'" cy="'+y+'" r="'+rad+'" fill="'+fill+'" '+extra+'/>';
 const metal='url(#schematic-steel)',edge='#818c89',dark='#202423';
 function component(key,content,x,y,w,h,dy=0){
  return '<g data-inspect="'+key+'" data-illustration="'+key+'" '+(current?.vessels[key]?'data-vessel="'+key+'"':'')+' class="schematic-equipment '+(selected===key?'selected':'')+(key==='outlet'&&!current?.vessels.outlet?' schematic-inactive':'')+'">'+'<g transform="translate(0 '+dy+')">'+rect(x,y,w,h,'transparent',6,'class="equipment-hit"')+content+'</g></g>';
 }
 function fillBar(key,x,y,w,h,clip=''){
  const fraction=current?.vessels[key]?.liquidVolumeFraction,level=Number.isFinite(fraction)?Math.max(0,Math.min(1,fraction)):0;
  return rect(x,y,w,h,'#171919',3)+rect(x,y+h-h*level,w,h*level,'url(#schematic-liquid)',2,'data-level="'+key+'" data-fraction="'+(fraction??'')+'" '+(clip?'clip-path="url(#'+clip+')"':''))+line('M'+x+' '+(y+h-h*level)+'h'+w,'#abb2b0',1.5,'opacity="'+(level>0?.8:0)+'"');
 }
 function vesselReadings(key,x,y){
  const v=current?.vessels[key];
  return tx(x,y,v?p(v.p):'—','schematic-value','data-reading="'+key+'-pressure"')+tx(x+142,y,v?T(v.T):'—','schematic-value secondary','data-reading="'+key+'-temperature"')+tx(x,y+22,v?.phase||'Not initialized','schematic-caption compact')+tx(x+142,y+22,v?f(v.liquidVolumeFraction*100)+'% liquid vol.':'—','schematic-caption compact','data-reading="'+key+'-level"');
 }
 function compressorIllustration(status,c){
  let shape=tx(88,60,'Compressor bank','schematic-title');
  shape+=tx(88,82,current?.compressorCount?current.compressorCount+' modeled · aggregate symbol':'Aggregate equipment symbol');
  // Motor, coupling and compressor housing share one aggregate bank symbol.
  shape+='<g class="machine-surface">';
  shape+=rect(91,129,99,57,'url(#schematic-machine)',11,'class="machine-body" stroke="'+edge+'"')+circle(102,158,26,'#383d3c','stroke="'+edge+'"')+circle(102,158,19,dark,'stroke="#646e6b"')+circle(102,158,8,'#656f6c');
  for(let x=116;x<187;x+=9)shape+=line('M'+x+' 137v41','#1d2120',4)+line('M'+(x-1)+' 137v41','#858f8d',1.5);
  shape+=rect(190,147,22,25,metal,2)+rect(211,124,61,64,'url(#schematic-machine)',8,'class="machine-body" stroke="'+edge+'"')+circle(242,157,24,'#393e3d','stroke="'+edge+'"')+circle(242,157,15,'#2a2d2c','stroke="#646d6b"')+circle(242,157,6,'#808b88');
  for(const [x,y]of [[225,137],[257,137],[225,176],[257,176]])shape+=circle(x,y,2,'#a1a9a7');
  shape+=rect(232,108,23,16,metal,2)+rect(229,103,29,7,'#838d8b',2)+rect(120,187,18,14,metal,1)+rect(240,188,15,13,metal,1)+rect(84,201,201,7,'#353a39',2);
  shape+=line('M118 132H181M216 129H264','#c9cdcc',1,'opacity=".65"')+line('M120 183H180M215 184H267','#0f1110',3)+circle(102,158,19,'url(#schematic-face)','stroke="#848f8c"')+circle(102,158,8,'#606967')+circle(242,157,15,'url(#schematic-face)','stroke="#848f8c"')+circle(242,157,6,'#808a88')+'</g>';
  shape+=tx(88,244,status,'schematic-value','data-reading="compressor-status"')+tx(88,266,current?f(current.operations.speed*100,0)+'% speed setting':'—','schematic-caption','data-reading="compressor-speed"')+tx(286,223,'Discharge: '+(Number.isFinite(c?.dischargeTemperature)?T(c.dischargeTemperature):'—'),'schematic-caption','data-reading="discharge-temperature"');
  return component('compressor',shape,76,46,324,237,-30);
 }
 function condenserIllustration(){
  let shape=tx(432,60,'Condenser','schematic-title')+tx(432,82,'Bulk refrigerant state');
  shape+='<g class="machine-surface">';
  shape+=rect(435,105,219,96,metal,7,'class="machine-body" stroke="'+edge+'"')+rect(446,116,197,67,dark,2);
  for(let x=453;x<640;x+=9)shape+=line('M'+x+' 118v62','#848e8c',1.5)+line('M'+(x+2)+' 118v62','#232726',3);
  shape+=line('M451 123H633V143H451V164H633V178H451','#563b24',7,'stroke-linejoin="round"')+line('M451 123H633V143H451V164H633V178H451','#edb363',3.5,'stroke-linejoin="round"');
  shape+=rect(432,137,12,31,metal,2)+rect(646,137,12,31,metal,2)+rect(452,201,13,11,metal,1)+rect(627,201,13,11,metal,1)+rect(429,212,233,6,'#353a39',2);
  shape+=line('M441 109H648M441 110V194','#d7dad9',1,'opacity=".6"')+circle(443,112,2,'#b8bebd')+circle(646,194,2,'#b8bebd')+fillBar('condenser',446,187,197,7)+'</g>'+vesselReadings('condenser',432,244);
  return component('condenser',shape,418,46,287,237,-30);
 }
 function receiverIllustration(){
  let shape=tx(810,60,'Receiver','schematic-title')+tx(810,82,'Modeled liquid volume');
  shape+='<g class="machine-surface">';
  shape+='<path class="machine-body" d="M840 108C840 82 945 82 945 108V201C945 224 840 224 840 201Z" fill="'+metal+'" stroke="'+edge+'"/>';
  shape+='<ellipse cx="892.5" cy="108" rx="52.5" ry="17" fill="url(#schematic-cap)" stroke="'+edge+'"/>';
  shape+=line('M850 120v76','#c3c8c7',2,'opacity=".5"')+line('M936 120v76','#343938',3)+rect(831,140,9,25,metal,2)+rect(945,175,11,22,metal,2)+rect(861,218,13,13,metal,2)+rect(912,218,13,13,metal,2);
  shape+=fillBar('receiver',875,125,34,74)+rect(873,122,38,80,'none',4,'stroke="#848f8c" stroke-width="2"')+line('M918 130h9M918 151h9M918 173h9M918 195h9','#778380');
  shape+=line('M844 116Q892 134 941 117M846 198Q892 218 940 200','#cfd3d2',1,'opacity=".45"')+line('M880 129V194','#e2e5e4',1,'opacity=".2"')+circle(871,120,1.8,'#c4cac8')+circle(913,204,1.8,'#c4cac8')+'</g>';
  shape+=vesselReadings('receiver',810,244);
  return component('receiver',shape,793,46,270,237,-30);
 }
 function evaporatorIllustration(){
  let shape=tx(432,343,'Evaporator core','schematic-title');
  shape+='<g class="machine-surface">';
  shape+=rect(435,372,220,69,metal,6,'class="machine-body" stroke="'+edge+'"')+rect(446,382,198,48,dark,2);
  for(let x=452;x<641;x+=8)shape+=line('M'+x+' 384v43','#8f9996',1)+line('M'+(x+2)+' 384v43','#252928',3);
  shape+=line('M451 388H635V402H451V417H635','#393f3d',7,'stroke-linejoin="round"')+line('M451 388H635V402H451V417H635','#84c3a8',3.5,'stroke-linejoin="round"')+rect(431,390,12,25,metal,2)+rect(648,390,12,25,metal,2);
  shape+=fillBar('evaporator',446,434,198,6)+rect(453,442,14,8,metal,1)+rect(627,442,14,8,metal,1);
  shape+=line('M441 376H648M441 378V435','#c9cdcc',1,'opacity=".65"')+circle(443,378,2,'#babfbe')+circle(647,434,2,'#babfbe')+'</g>';
  shape+=vesselReadings('evaporator',432,480);
  return component('evaporator',shape,418,325,287,218,-70);
 }
 function outletIllustration(connected){
  let shape=tx(88,343,'Outlet / suction','schematic-title')+tx(88,365,connected?'Resolved model volume':'Inactive · isolated storage');
  shape+='<g class="model-partition-surface">';
  // Partition symbol deliberately differs from the receiver: no added separator.
  shape+='<path class="machine-body model-volume" d="M102 380Q178 357 253 380V426Q178 450 102 426Z" fill="url(#schematic-steel)" stroke="'+edge+'" stroke-dasharray="5 3"/>';
  shape+='<ellipse cx="177.5" cy="380" rx="75.5" ry="11" fill="url(#schematic-cap)" stroke="'+edge+'" stroke-dasharray="5 3"/>';
  shape+=line('M112 391v30','#a2aaa8',2,'opacity=".5"')+rect(90,391,12,25,metal,2)+rect(253,391,12,25,metal,2)+fillBar('outlet',125,422,104,7);
  shape+='</g>';
  shape+=vesselReadings('outlet',88,480);
  return component('outlet',shape,76,325,286,218,-70);
 }
 function valveIllustration(connected){
  let shape=tx(810,343,'Liquid feed valve','schematic-title');
  shape+='<g class="machine-surface">';
  shape+=rect(870,364,45,22,'#383e3c',4,'class="machine-body" stroke="'+edge+'"')+rect(882,386,21,18,metal,2);
  shape+='<path class="machine-body" d="M864 389L894 405L864 421ZM924 389L894 405L924 421Z" fill="'+metal+'" stroke="'+edge+'" stroke-width="2"/>';
  shape+=rect(856,387,8,37,'#66706d',2)+rect(924,387,8,37,'#66706d',2)+line('M881 373h22','#70aa90',2);
  shape+=line('M875 367H910M858 391V418M930 391V418','#ced2d1',1,'opacity=".75"')+circle(860,392,1.8,'#c5cac9')+circle(928,419,1.8,'#c5cac9')+'</g>';
  shape+=tx(810,480,connected?f(current.controller.opening*100)+'% actual':'Isolated','schematic-value','data-reading="valve-opening"');
  shape+=tx(810,502,connected?current.operations.valveMode+' · '+(current?.flows&&!current.flows.error?current.flows.feed.status:'flow unavailable'):'Feed / drain disconnected');

  return component('feed',shape,793,325,270,218,-70);
 }
 function pipe(key,path,color,flow,isolated=false){
  // Arrows require positive supported transport. Stops show no live demand.
  const active=!isolated&&!current?.fault&&Number.isFinite(flow)&&flow>0;
  return '<g data-port="'+key+'" data-active="'+active+'" class="process-port '+(active?'port-active':'port-inactive')+'">'+line(path,'#080808',11,'stroke-linecap="round" stroke-linejoin="round"')+line(path,isolated?'#5d6563':color,5,'stroke-linecap="round" stroke-linejoin="round" '+(isolated?'stroke-dasharray="7 7"':active?'marker-end="url(#schematic-arrow-'+color.slice(1)+')"':''))+(isolated?'':line(path,'#f7f7f7',1,'opacity=".22" stroke-linecap="round" stroke-linejoin="round"'))+(active?line(path,'#e9ebea',1.8,'class="schematic-flow" stroke-dasharray="2 20"'):'')+'</g>';
 }
 function render(){
  container.classList.toggle('schematic-stopped',!!current?.fault);
  const r=current,connected=!!r?.vessels.outlet,flows=r?.flows&&!r.flows.error?r.flows:null,c=r?.compressor;
  const moving=running&&motion&&!r?.fault&&!c?.inhibited;
  const compressorStatus=!r?'Not initialized':r.fault?'STOPPED':!r.operations.compressorOn?'OFF':c?.inhibited?'UNAVAILABLE':running?'RUNNING':'PAUSED · enabled';
  $('schematic-status').textContent=r?f(r.seconds,1)+' s · '+(r.fault?'Stopped · '+r.fault.message:running?'Running':'Paused')+' · '+(connected?'Circulating DX':'Isolated storage'):'Initialize storage to see model readings.';
  $('schematic-flow-note').textContent=!r?'No simulation values yet.':(flows?.interval?'Feed/drain/vapor arrows: accepted average flow over '+f(flows.interval.from,4)+'–'+f(flows.interval.to,4)+' s.':'Feed/drain/vapor arrows: current-state demand.')+' Compressor flow and discharge temperature: current-state demand; unavailable during a stop. Paused arrows are static.';
  let svg='<svg viewBox="0 0 1080 438" role="img" aria-labelledby="schematic-svg-title schematic-svg-desc" class="'+(moving?'':'schematic-still')+'" style="--schematic-delay:-'+(performance.now()/1000).toFixed(4)+'s"><title id="schematic-svg-title">Connected ammonia circuit at '+f(r?.seconds||0,1)+' simulated seconds</title><desc id="schematic-svg-desc">'+esc(compressorStatus)+'. Illustrative aggregate equipment symbols, not physical dimensions. Flow follows outlet to compressor, condenser, receiver, feed valve, evaporator core and outlet. The resolved outlet is a model partition, not an additional vessel. Readings and inspection buttons follow the diagram.</desc><defs><linearGradient id="schematic-steel" x1="0" x2="1"><stop stop-color="#202524"/><stop offset=".12" stop-color="#5b6462"/><stop offset=".24" stop-color="#c9cecd"/><stop offset=".3" stop-color="#8e9795"/><stop offset=".48" stop-color="#505856"/><stop offset=".72" stop-color="#373c3b"/><stop offset=".91" stop-color="#737d7b"/><stop offset="1" stop-color="#1f2221"/></linearGradient><linearGradient id="schematic-cap" x2="0" y2="1"><stop stop-color="#c3c8c7"/><stop offset=".24" stop-color="#86918e"/><stop offset=".8" stop-color="#434a48"/><stop offset="1" stop-color="#252928"/></linearGradient><linearGradient id="schematic-machine" x2="0" y2="1"><stop stop-color="#77827f"/><stop offset=".15" stop-color="#555e5c"/><stop offset=".45" stop-color="#363b3a"/><stop offset=".82" stop-color="#262928"/><stop offset="1" stop-color="#141716"/></linearGradient><linearGradient id="schematic-liquid" x2="0" y2="1"><stop stop-color="#a0d9bd"/><stop offset=".1" stop-color="#70bfa2"/><stop offset=".7" stop-color="#347c66"/><stop offset="1" stop-color="#204b3e"/></linearGradient><radialGradient id="schematic-face" cx="35%" cy="30%"><stop stop-color="#68726f"/><stop offset=".55" stop-color="#363b3a"/><stop offset="1" stop-color="#1b1e1d"/></radialGradient><filter id="schematic-depth" x="-15%" y="-20%" width="130%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="2" flood-color="#050606" flood-opacity=".7"/></filter></defs>';
  // Each route ends at a supported component connection; no extra headers.
  svg=svg.replace('</defs>', ['#cd9863','#70aa90','#82b7a1','#a0b9ae'].map(color=>'<marker id="schematic-arrow-'+color.slice(1)+'" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="3.4" markerHeight="3.4" orient="auto"><path d="M0 0L10 5L0 10Z" fill="'+color+'"/></marker>').join('')+'</defs>');
  svg+=pipe('discharge','M272 123H435','#cd9863',c?.massFlow,!r);
  svg+=pipe('drain','M658 123H831','#70aa90',flows?.drain.massFlow,!connected);
  svg+=pipe('feed','M956 156H1023Q1035 156 1035 168V323Q1035 335 1023 335H932M856 335H660','#82b7a1',flows?.feed.massFlow,!connected);
  svg+=pipe('vapor','M431 335H265','#a0b9ae',flows?.vapor.massFlow,!connected);
  svg+=pipe('suction',connected?'M90 333H45Q33 333 33 321V140Q33 128 45 128H76':'M540 302V247H45Q33 247 33 235V140Q33 128 45 128H76','#a0b9ae',c?.massFlow,!r);
  svg+=tx(298,99,'Discharge')+tx(694,99,'Drain transfer')+tx(295,313,'Core → outlet')+tx(696,313,'Feed transfer');
  svg+=tx(290,145,Number.isFinite(c?.massFlow)?f(c.massFlow,5)+' kg/s':'—','schematic-caption','data-reading="compressor-flow"')+tx(688,145,flows?f(flows.drain.massFlow,5)+' kg/s':'isolated','schematic-caption','data-reading="drain-flow"')+tx(686,357,'Feed: '+(flows?f(flows.feed.massFlow,5)+' kg/s':'isolated'),'schematic-caption','data-reading="feed-flow"');
  svg+=compressorIllustration(compressorStatus,c)+condenserIllustration()+receiverIllustration()+evaporatorIllustration()+outletIllustration(connected)+valveIllustration(connected);
  svg+='</svg>';
  $('schematic-graphic').innerHTML=svg;
  let values=[],explanation='Initialize the connected circuit to inspect this component.';
  if(r&&r.vessels[selected]){const v=r.vessels[selected];values=[['Pressure',p(v.p)],['Temperature',T(v.T)],['Phase',v.phase],['Mass',f(v.massKg,3)+' kg'],['Liquid volume',f(v.liquidVolumeFraction*100)+'%'],['Internal energy',f(v.internalEnergyKJ,3)+' kJ']];explanation=selected==='outlet'?'Resolved outlet volume supplies compressor suction. Its temperature and saturation pressure determine actual superheat.':'Pressure and phase are recovered from conserved mass and internal energy in this fixed volume.';}
  if(r&&selected==='outlet'&&!connected)explanation='The resolved outlet is inactive in isolated storage. Compressor suction uses the evaporator vapor phase.';
  if(r&&selected==='feed'){values=[['Mode',connected?r.operations.valveMode:'Isolated'],['Actual opening',connected?f(r.controller.opening*100)+'%':'—'],['Command',Number.isFinite(flows?.command)?f(flows.command*100)+'%':'—'],['Mass flow',flows?f(flows.feed.massFlow,5)+' kg/s':'—'],['Flow condition',flows?flows.feed.status+(flows.feed.phaseLimited?' · phase supply limited':''):'Disconnected'],['Actual / sensed superheat',flows?delta(flows.superheat)+' / '+delta(r.controller.sensor):'—']];explanation='Command and actual opening differ while the actuator responds. Automatic control uses lagged sensed outlet superheat. A closed command takes time to close the valve.';}
  if(r&&selected==='compressor'){values=[['State',compressorStatus],['Speed setting',f(r.operations.speed*100)+'%'],['Suction pressure',p((r.vessels.outlet||r.vessels.evaporator).p)],['Discharge pressure',p(r.vessels.condenser.p)],['Discharge temperature',Number.isFinite(c?.dischargeTemperature)?T(c.dischargeTemperature):'—'],['Electrical demand',Number.isFinite(c?.electrical)?f(c.electrical,3)+' kW':'—']];explanation=c?.error?'Demand unavailable: '+c.error:'Current-state demand from the active profile; speed is manual. Condenser bulk temperature is separate from compressor discharge temperature.';}
  $('schematic-detail').innerHTML='<h4>'+names[selected]+'</h4><p class="text">'+esc(explanation)+'</p><dl>'+values.map(([k,v])=>'<div><dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd></div>').join('')+'</dl>';
 }
 container.querySelector('.schematic-select').addEventListener('click',e=>{const button=e.target.closest('[data-component]');if(!button)return;selected=button.dataset.component;container.querySelectorAll('[data-component]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));render();});
 $('schematic-graphic').addEventListener('click',e=>{const target=e.target.closest('[data-inspect]');if(target)container.querySelector('[data-component="'+target.dataset.inspect+'"]').click();});
 $('schematic-motion').addEventListener('click',()=>{motion=!motion;$('schematic-motion').setAttribute('aria-pressed',String(motion));$('schematic-motion').textContent='Flow animation: '+(motion?'on':'off');render();});
 render();
 return {update(record,displayUnits,isRunning){current=record;units={...displayUnits};running=isRunning;render();}};
}
const api={create};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaSchematic=api;
})(typeof globalThis!=='undefined'?globalThis:this);
