'use strict';
(()=>{
 const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const engine=AmmoniaEngine.createEngine(JSON.parse($('property-data').textContent)),model=AmmoniaStorage.createStorage(engine,AmmoniaProfiles);
 const schematic=AmmoniaSchematic.create($('storage-schematic'));
 const trends=AmmoniaTrends.create($('storage-trends'));
 let state=null,running=false,timer=null,last=0,units={p:'psig',T:'F'},training=null;
 const f=(v,n=3)=>Number.isFinite(v)?v.toFixed(n):'—',temp=v=>Number.isFinite(v)?(units.T==='F'?v*1.8+32:v):NaN;
 const pressure=v=>Number.isFinite(v)?(v-(units.p.endsWith('g')?1.01325:0))*(units.p.startsWith('psi')?14.503773773:1):NaN,pl=()=>({bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'})[units.p];
 // Display projection only: these functions never write simulator state.
 function renderDraft(){
  let dirty=false,message='Initialize to apply these settings.';
  if(state){
   try{
    const o=operations(),b=roomBoundary(),different=(a,v)=>typeof v==='number'?Math.abs(a-v)>1e-8:a!==v;
    dirty=Object.entries(o).some(([k,v])=>different(state.operations[k],v))||Object.entries(b).some(([k,v])=>different(state.roomConfig[k],v));
    message=dirty?'Draft changes · not applied to the connected run.':'Applied · controls match the connected run.';
   }catch{dirty=true;message='Draft incomplete or invalid · applied run settings retained.';}
  }
  $('storage-form').dataset.dirty=String(dirty);$('storage-draft').textContent=message;
 }
 function renderDashboard(r=null,c=null){
  const connected=!!r?.vessels.outlet,flows=r?.flows&&!r.flows.error?r.flows:null,o=state?.operations;
  const compressor=!state?'—':state.fault?'Stopped':!o.compressorOn?'Off':c?.inhibited?'Unavailable':running?'Running':'Paused';
  const cards=[
   ['Suction pressure',f(pressure((r?.vessels.outlet||r?.vessels.evaporator)?.p),2),pl(),!state?'Not initialized':connected?'Resolved outlet volume':'Evaporator vapor boundary','suction'],
   ['Discharge pressure',f(pressure(r?.vessels.condenser?.p),2),pl(),state?'Condenser bulk pressure':'Not initialized','discharge'],
   ['Compressor',compressor,'',state?f(o.speed*100,0)+'% speed setting · '+(o.compressorOn?'enabled':'disabled'):'No connected run','compressor'],
   ['Room temperature',f(temp(r?.T),2),'°'+units.T,state?'Connected room state':'Not initialized','room'],
   ['Actual superheat',f(flows?.superheat*(units.T==='F'?1.8:1),2),units.T==='F'?'°F Δ':'K',!state?'Not initialized':!connected?'Unavailable · isolated circuit':flows?.interval?'Accepted flow interval':'Current outlet state','superheat'],
   ['Feed valve',connected?f(r.controller.opening*100,2):'—','%',!state?'Not initialized':connected?'Actual opening · '+o.valveMode:'Unavailable · isolated circuit','feed']
  ];
  $('storage-overview').innerHTML=cards.map(([label,value,unit,note,key])=>'<div class="metric" data-summary="'+key+'"><label>'+esc(label)+'</label><strong>'+esc(value)+' <span class="readout-unit">'+esc(unit)+'</span></strong><small>'+esc(note)+'</small></div>').join('');
  $('storage-mode').textContent=!state?'Connected circuit · not initialized':(connected?'Circulating DX':'Isolated storage')+' · '+(o.thermalMode==='air'?'room / ambient exchange':'sealed test boundaries')+' · '+state.profile.name+' r'+state.profile.revision;
  $('storage-playback').textContent=!state?'Ready':state.fault?'Stopped':running?'Running · '+$('storage-speed').value+'×':'Paused';
  const fault=state?.fault;
  $('storage-alarm').dataset.severity=!state?'idle':fault?(fault.kind==='equipment'?'equipment':'model'):'normal';
  $('storage-alarm-summary').textContent=!state?'Not initialized · no connected run to assess.':!fault?'No active modeled trip or stop.':fault.kind==='equipment'?'EQUIPMENT TRIP · '+fault.message: (fault.kind==='solver'?'NUMERICAL / SOLVER STOP':'MODEL-DOMAIN STOP')+' · '+fault.message+' · no equipment trip asserted.';
  if(!state)$('storage-status').textContent='Initialize the DX example or choose circuit settings and initialize storage.';
  $('storage-applied').textContent=!state?'No applied connected controls yet.':'Applied: compressor '+(o.compressorOn?'enabled':'disabled')+' at '+f(o.speed*100,0)+'% · feed '+o.valveMode+(o.valveMode==='manual'?' command '+f(o.manualOpening*100,1)+'%':'')+' · ambient '+f(temp(state.roomConfig.ambient),1)+' °'+units.T+' · room gain '+f(state.roomConfig.gain,1)+' kW.';
  renderDraft();
 }
 $('storage-form').addEventListener('input',renderDraft);
 $('storage-form').addEventListener('change',renderDraft);
 document.querySelector('.plant-nav').addEventListener('click',e=>{
  const link=e.target.closest('a');if(!link)return;
  const target=$(link.getAttribute('href').slice(1));if(!target)return;
  e.preventDefault();target.setAttribute('tabindex','-1');target.focus({preventScroll:true});(target.id==='storage-form'?$('storage-control-panel'):target).scrollIntoView({block:'start'});
 });

 function operations(){const o={thermalMode:$('storage-thermalMode').value,compressorOn:$('storage-compressorOn').checked,circuit:$('storage-circuit').value,valveMode:$('storage-valveMode').value,drainEnabled:$('storage-drainEnabled').checked};for(const key of ['receiverHeat','evaporatorHeat','condenserHeat']){if(!$('storage-'+key).value.trim())throw Error('Fill in storage heat rates.');o[key]=Number($('storage-'+key).value);}if(!$('storage-compressorSpeed').value.trim())throw Error('Fill in compressor speed.');o.speed=Number($('storage-compressorSpeed').value)/100;for(const key of ['manualOpening','superheatTarget','kp','ki']){const el=$('storage-'+key);if(!el.value.trim())throw Error('Fill in valve operating controls.');o[key]=Number(el.value);}o.manualOpening/=100;o.superheatTarget/=units.T==='F'?1.8:1;return model.validateOperations(o);}
 function roomBoundary(){const c={};for(const key of ['ambient','gain','leakUA']){const el=$('storage-'+key);if(!el.value.trim())throw Error('Fill in room/condenser boundaries.');c[key]=Number(el.value);}if(units.T==='F')c.ambient=(c.ambient-32)/1.8;return c;}
 function showError(e){$('storage-error').textContent=e.message;$('storage-error').hidden=false;}
 function clearError(){$('storage-error').hidden=true;}
 function pause(reason='User pause'){if(running&&state)model.logPlayback(state,'pause',{reason});running=false;clearInterval(timer);timer=null;$('storage-pause').disabled=true;render();}
 function initialize(){const snapshot=AmmoniaPlantSnapshot(),next=model.create(snapshot.profile,{...snapshot.roomConfig,...roomBoundary()},operations());training?.interrupt('Connected run reinitialized outside the exercise.');pause();state=next;clearError();render();}
 function step(seconds){if(!state)initialize();model.advance(state,seconds,[],training?.isActive()?training.acceptBoundary:null);if(state.fault)pause('Simulation stop');render();}
 function render(){
  $('storage-start').disabled=running;$('storage-export').disabled=!state;
  training?.update(state);
  if(!state){renderDashboard();schematic.update(null,units,false);trends.update(null,units);$('storage-clock').textContent='0.0 s simulated';$('storage-metrics').innerHTML='';$('storage-states').innerHTML='';$('storage-balance').innerHTML='';$('storage-flows').innerHTML='';$('storage-flow-window').textContent='';return;}
  const r=model.record(state);renderDashboard(r,model.observeCompressor(state));schematic.update({...r,compressorCount:state.profile.equipment.compressors,profileLabel:state.profile.name+' revision '+state.profile.revision,compressor:model.observeCompressor(state)},units,running);$('storage-clock').textContent=f(state.time,1)+' s simulated';
  const status=state.fault?{equipment:'TRIPPED',solver:'SOLVER LIMIT',domain:'MODEL LIMIT'}[state.fault.kind]:running?'Running':'Paused';
  $('storage-status').textContent=status+' · '+state.profile.name+' revision '+state.profile.revision+(state.fault?' · '+state.fault.message+' · detected at '+f(state.fault.seconds,3)+' s. Correct controls and clear the stop, or reinitialize storage.':' · '+state.operations.thermalMode+' boundaries · '+state.operations.circuit+' circuit.');
  if(state.fault?.readings){const v=state.fault.readings;$('storage-status').textContent+=' Captured suction / discharge '+f(pressure(v.pressure),2)+' / '+f(pressure(v.condensing),2)+' '+pl()+', discharge temperature '+f(temp(v.discharge),2)+' °'+units.T+'.';}
  const metrics=[['Stored charge',f(r.totalMassKg)+' kg'],['Room temperature',f(temp(state.T),2)+' °'+units.T],['Compressor electricity',f(r.electricalKWh,5)+' kWh']];$('storage-metrics').innerHTML=metrics.map(([label,value])=>'<div class="metric"><label>'+esc(label)+'</label><strong style="font-size:20px">'+esc(value)+'</strong></div>').join('');
  $('storage-states').innerHTML='<table><thead><tr><th>Volume</th><th>Pressure · '+esc(pl())+'</th><th>Temperature · °'+units.T+'</th><th>Phase</th><th>Mass · kg</th><th>Liquid volume · %</th><th>Vapor mass · %</th><th>Internal energy · kJ</th></tr></thead><tbody>'+Object.entries(r.vessels).map(([key,v])=>'<tr><td>'+key+'</td><td>'+f(pressure(v.p),2)+'</td><td>'+f(temp(v.T),2)+'</td><td>'+esc(v.phase)+'</td><td>'+f(v.massKg)+'</td><td>'+f(v.liquidVolumeFraction*100,2)+'</td><td>'+f(v.x===null?NaN:v.x*100,2)+'</td><td>'+f(v.internalEnergyKJ)+'</td></tr>').join('')+'</tbody></table>';
  const balance=[['Mass residual',f(r.massResidualKg,9)+' kg'],['Combined room / refrigerant energy residual',f(r.energyResidualKJ,7)+' kJ'],['External heat',f(r.externalHeatKJ)+' kJ'],['Mechanical work into refrigerant (compressor + drain head)',f(r.fluidWorkKJ)+' kJ'],['Drain gravity contribution',f(r.gravityEnergyKJ)+' kJ'],['Accepted / rejected integration steps',r.acceptedSteps+' / '+r.rejectedSteps]];$('storage-balance').innerHTML=balance.map(([label,value])=>'<div>'+esc(label)+'<strong>'+esc(value)+'</strong></div>').join('');
  const flows=r.flows;$('storage-flow-window').textContent=flows?.interval?'Port flows averaged over '+f(flows.interval.from,4)+'–'+f(flows.interval.to,4)+' simulated seconds.':'Port flow demand at the current state.';if(flows&&!flows.error){const values=[['Actual outlet superheat',f(flows.superheat*(units.T==='F'?1.8:1),2)+' '+(units.T==='F'?'°F Δ':'K')],['Measured sensor superheat',f(r.controller.sensor*(units.T==='F'?1.8:1),2)+' '+(units.T==='F'?'°F Δ':'K')],['Valve command / actual opening',f(flows.command*100,2)+' / '+f(r.controller.opening*100,2)+' %'],...['feed','drain','vapor'].map(k=>[k+' flow',f(flows[k].massFlow,5)+' kg/s · '+flows[k].status+(flows[k].phaseLimited?' · phase supply limited':'')])];$('storage-flows').innerHTML=values.map(([k,v])=>'<div>'+esc(k)+'<strong>'+esc(v)+'</strong></div>').join('');}else $('storage-flows').textContent=flows?.error||'Feed and drain isolated.';trends.update(state.history,units);
 }
 $('storage-example').addEventListener('click',()=>{try{pause();$('storage-circuit').value='circulating';$('storage-thermalMode').value='air';$('storage-compressorOn').checked=true;$('storage-compressorSpeed').value=70;$('storage-valveMode').value='auto';$('storage-drainEnabled').checked=true;for(const [key,value]of Object.entries({receiverHeat:0,evaporatorHeat:0,condenserHeat:0,manualOpening:25,superheatTarget:units.T==='F'?9:5,kp:.04,ki:.004,ambient:units.T==='F'?77:25,gain:2,leakUA:.1}))$('storage-'+key).value=value;initialize();}catch(e){showError(e);}});
 $('storage-initialize').addEventListener('click',()=>{try{initialize();}catch(e){showError(e);}});
 $('storage-step').addEventListener('click',()=>{try{pause();if(state)model.update(state,operations(),roomBoundary());clearError();if(!state)initialize();model.logPlayback(state,'step',{requestedSeconds:10,reason:'Advance requested: 10 simulated seconds'});step(10);}catch(e){showError(e);}});
 $('storage-pause').addEventListener('click',()=>pause());
 $('storage-start').addEventListener('click',()=>{try{if(!state)initialize();if(state.fault)throw Error('Clear the storage stop after correcting controls, or reinitialize.');model.update(state,operations(),roomBoundary());$('live-pause').click();clearError();running=true;model.logPlayback(state,'start',{speed:Number($('storage-speed').value)});$('storage-pause').disabled=false;last=performance.now();timer=setInterval(()=>{try{const now=performance.now(),elapsed=Math.min(1,(now-last)/1000);last=now;step(elapsed*Number($('storage-speed').value));}catch(e){pause();showError(e);}},250);render();}catch(e){showError(e);}});
 $('storage-form').addEventListener('submit',e=>{e.preventDefault();try{const o=operations();if(state)model.update(state,o,roomBoundary());clearError();render();}catch(e){showError(e);}});
 $('storage-clear').addEventListener('click',()=>{if(state){model.clearFault(state);clearError();render();}});
 document.addEventListener('ammonia-equipment',()=>{training?.interrupt('Applied equipment changed.');pause();state=null;render();$('storage-status').textContent='Active equipment changed. Initialize storage from the new profile.';});
 document.addEventListener('ammonia-run-live',()=>pause('Switched to quasi-steady playback'));
 document.addEventListener('ammonia-units',e=>{const ambient=$('storage-ambient'),air=ambient.value.trim()?(units.T==='F'?(Number(ambient.value)-32)/1.8:Number(ambient.value)):null;const el=$('storage-superheatTarget'),v=el.value.trim()?Number(el.value)/(units.T==='F'?1.8:1):null;units={...e.detail};if(air!==null)ambient.value=units.T==='F'?air*1.8+32:air;$('storage-tunit').textContent='°'+units.T;if(v!==null)el.value=v*(units.T==='F'?1.8:1);$('storage-dunit').textContent=units.T==='F'?'°F Δ':'K';render();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&running)pause('Browser moved to background');});
 window.addEventListener('error',()=>{if(running)pause('Browser error');});window.addEventListener('unhandledrejection',()=>{if(running)pause('Browser error');});
 $('storage-speed').addEventListener('change',()=>{if(state){model.logPlayback(state,'speed',{speed:Number($('storage-speed').value)});render();}});
 $('storage-export').addEventListener('click',()=>{
  if(!state)return;const rows=[['Storage model','v0.4.5; connected valves / resolved outlet'],['Equipment JSON SI',JSON.stringify(state.profile)],['Initial room conditions JSON SI',JSON.stringify(state.initialRoomConfig)],['Current room conditions JSON SI',JSON.stringify(state.roomConfig)],['Seconds','Room C','Charge kg','Refrigerant U kJ','Room energy change kJ','Mass residual kg','Combined energy residual kJ','External heat kJ','Fluid work kJ','Compressor kWh','Thermal mode','Receiver heat kW','Evaporator heat kW','Condenser heat kW','Compressor enabled','Speed fraction',...Object.keys(state.vessels).flatMap(key=>[key+' bar absolute',key+' C',key+' phase',key+' kg',key+' U kJ',key+' liquid volume fraction',key+' vapor mass fraction']),'Circuit','Valve mode','Manual command fraction','Superheat target K','PI kp fraction/K','PI ki fraction/(K s)','Drain enabled','Actual opening fraction','Sensor superheat K','Integrator fraction','Actual superheat K','Feed kg/s','Drain kg/s','Vapor link kg/s','Flow diagnostics JSON SI','Drain gravity energy kJ','Ambient C','Room gain kW','Room leak UA kW/K','Fault snapshot JSON SI','Fault kind','Fault message','Fault detection seconds','Fault readings JSON SI'],...state.rows.map(r=>[r.seconds,r.T,r.totalMassKg,r.totalEnergyKJ,r.roomEnergyKJ,r.massResidualKg,r.energyResidualKJ,r.externalHeatKJ,r.fluidWorkKJ,r.electricalKWh,r.operations.thermalMode,r.operations.receiverHeat,r.operations.evaporatorHeat,r.operations.condenserHeat,r.operations.compressorOn,r.operations.speed,...Object.values(r.vessels).flatMap(v=>[v.p,v.T,v.phase,v.massKg,v.internalEnergyKJ,v.liquidVolumeFraction,v.x??'']),r.operations.circuit,r.operations.valveMode,r.operations.manualOpening,r.operations.superheatTarget,r.operations.kp,r.operations.ki,r.operations.drainEnabled,r.controller.opening,r.controller.sensor,r.controller.integral,r.flows?.superheat??'',r.flows?.feed?.massFlow??'',r.flows?.drain?.massFlow??'',r.flows?.vapor?.massFlow??'',JSON.stringify(r.flows),r.gravityEnergyKJ,r.roomBoundary.ambient,r.roomBoundary.gain,r.roomBoundary.leakUA,r.fault?JSON.stringify(r.fault):'',r.fault?.kind??'',r.fault?.message??'',r.fault?.seconds??'',r.fault?JSON.stringify(r.fault.readings):''])];
  const csv=rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n'),url=URL.createObjectURL(new Blob([csv],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='ammonia-storage-v045.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 });

 function fillTrainingControls(s){
  for(const key of ['circuit','thermalMode','valveMode'])$('storage-'+key).value=s.operations[key];
  for(const key of ['compressorOn','drainEnabled'])$('storage-'+key).checked=s.operations[key];
  for(const key of ['receiverHeat','evaporatorHeat','condenserHeat','kp','ki'])$('storage-'+key).value=s.operations[key];
  $('storage-compressorSpeed').value=s.operations.speed*100;$('storage-manualOpening').value=s.operations.manualOpening*100;$('storage-superheatTarget').value=s.operations.superheatTarget*(units.T==='F'?1.8:1);
  $('storage-ambient').value=units.T==='F'?s.roomConfig.ambient*1.8+32:s.roomConfig.ambient;$('storage-gain').value=s.roomConfig.gain;$('storage-leakUA').value=s.roomConfig.leakUA;
 }
 training=AmmoniaTrainingApp.create($('storage-training'),{
  defaultActive:()=>AmmoniaPlantSnapshot().profile.id==='default',pause,refresh:render,isRunning:()=>running,advance:()=>$('storage-step').click(),toggleRun:()=>$(running?'storage-pause':'storage-start').click(),clearStop:()=>$('storage-clear').click(),
  load(recipe){const next=model.create(AmmoniaProfiles.DEFAULT,recipe.room,recipe.operations);if(recipe.warmup)model.advance(next,recipe.warmup);if(next.fault)throw Error('Training warmup reached a model stop.');state=next;fillTrainingControls(state);clearError();render();return state;},
  apply(o,r){model.update(state,o,r);fillTrainingControls(state);clearError();},
  event(s,reason,details){AmmoniaHistory.sample(s.history,model.record(s),model.observeCompressor(s),'training');AmmoniaHistory.event(s.history,s.time,'training',{reason,...details});}
 });
 render();
})();
