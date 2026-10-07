'use strict';
(()=>{
 const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const engine=AmmoniaEngine.createEngine(JSON.parse($('property-data').textContent)),model=AmmoniaStorage.createStorage(engine,AmmoniaProfiles);
 let state=null,running=false,timer=null,last=0,units={p:'psig',T:'F'};
 const f=(v,n=3)=>Number.isFinite(v)?v.toFixed(n):'—',temp=v=>Number.isFinite(v)?(units.T==='F'?v*1.8+32:v):NaN;
 const pressure=v=>Number.isFinite(v)?(v-(units.p.endsWith('g')?1.01325:0))*(units.p.startsWith('psi')?14.503773773:1):NaN,pl=()=>({bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'})[units.p];
 function operations(){const o={thermalMode:$('storage-thermalMode').value,compressorOn:$('storage-compressorOn').checked};for(const key of ['receiverHeat','evaporatorHeat','condenserHeat']){if(!$('storage-'+key).value.trim())throw Error('Fill in storage heat rates.');o[key]=Number($('storage-'+key).value);}if(!$('storage-compressorSpeed').value.trim())throw Error('Fill in compressor speed.');o.speed=Number($('storage-compressorSpeed').value)/100;return model.validateOperations(o);}
 function showError(e){$('storage-error').textContent=e.message;$('storage-error').hidden=false;}
 function clearError(){$('storage-error').hidden=true;}
 function pause(){running=false;clearInterval(timer);timer=null;$('storage-pause').disabled=true;render();}
 function initialize(){const snapshot=AmmoniaPlantSnapshot(),next=model.create(snapshot.profile,snapshot.roomConfig,operations());pause();state=next;clearError();render();}
 function step(seconds){if(!state)initialize();model.advance(state,seconds);if(state.fault)pause();render();}
 function draw(){
  if(!state)return;
  const rows=state.rows.filter(r=>r.seconds>=state.time-7200),stride=Math.max(1,Math.ceil(rows.length/400)),sample=rows.filter((_,i)=>i%stride===0||i===rows.length-1);
  const max=Math.max(1,...sample.flatMap(r=>Object.values(r.vessels).map(v=>pressure(v.p)))),min=Math.min(0,...sample.flatMap(r=>Object.values(r.vessels).map(v=>pressure(v.p)))),end=Math.max(10,state.time),start=Math.max(0,state.time-7200);
  const x=t=>55+(t-start)/(end-start)*795,y=p=>230-(p-min)/(max-min)*200;
  let svg='<svg viewBox="0 0 900 280" role="img" aria-label="Storage pressures over simulated seconds"><text x="55" y="18" font-size="12">Stored pressures · '+esc(pl())+'</text><path d="M55 30V230H850" fill="none" stroke="#bdcfca"/>';
  for(const [key,color]of [['receiver','#28796f'],['evaporator','#3389ac'],['condenser','#dc713e']]){const d=sample.map((r,i)=>(i?'L':'M')+x(r.seconds)+' '+y(pressure(r.vessels[key].p))).join('');svg+='<path d="'+d+'" fill="none" stroke="'+color+'" stroke-width="2"/>';}
  svg+='<text x="55" y="255" font-size="11">'+f(start,1)+' s</text><text x="820" y="255" font-size="11">'+f(end,1)+' s</text><text x="55" y="274" font-size="11">Receiver (green) · evaporator (blue) · condenser (orange)</text></svg>';$('storage-trends').innerHTML=svg;
 }
 function render(){
  $('storage-start').disabled=running;$('storage-export').disabled=!state;
  if(!state){$('storage-clock').textContent='0.0 s simulated';$('storage-metrics').innerHTML='';$('storage-states').innerHTML='';$('storage-balance').innerHTML='';$('storage-trends').innerHTML='';return;}
  const r=model.record(state);$('storage-clock').textContent=f(state.time,1)+' s simulated';
  const status=state.fault?{equipment:'TRIPPED',solver:'SOLVER LIMIT',domain:'MODEL LIMIT'}[state.fault.kind]:running?'Running':'Paused';
  $('storage-status').textContent=status+' · '+state.profile.name+' revision '+state.profile.revision+(state.fault?' · '+state.fault.message+' · detected at '+f(state.fault.seconds,3)+' s. Correct controls and clear the stop, or reinitialize storage.':' · '+state.operations.thermalMode+' boundaries. Feed/drain closed.');
  if(state.fault?.readings){const v=state.fault.readings;$('storage-status').textContent+=' Captured suction / discharge '+f(pressure(v.pressure),2)+' / '+f(pressure(v.condensing),2)+' '+pl()+', discharge temperature '+f(temp(v.discharge),2)+' °'+units.T+'.';}
  const metrics=[['Stored charge',f(r.totalMassKg)+' kg'],['Room temperature',f(temp(state.T),2)+' °'+units.T],['Compressor electricity',f(r.electricalKWh,5)+' kWh']];$('storage-metrics').innerHTML=metrics.map(([label,value])=>'<div class="metric"><label>'+esc(label)+'</label><strong style="font-size:20px">'+esc(value)+'</strong></div>').join('');
  $('storage-states').innerHTML='<table><thead><tr><th>Volume</th><th>Pressure · '+esc(pl())+'</th><th>Temperature · °'+units.T+'</th><th>Phase</th><th>Mass · kg</th><th>Liquid volume · %</th><th>Vapor mass · %</th><th>Internal energy · kJ</th></tr></thead><tbody>'+Object.entries(r.vessels).map(([key,v])=>'<tr><td>'+key+'</td><td>'+f(pressure(v.p),2)+'</td><td>'+f(temp(v.T),2)+'</td><td>'+esc(v.phase)+'</td><td>'+f(v.massKg)+'</td><td>'+f(v.liquidVolumeFraction*100,2)+'</td><td>'+f(v.x===null?NaN:v.x*100,2)+'</td><td>'+f(v.internalEnergyKJ)+'</td></tr>').join('')+'</tbody></table>';
  const balance=[['Mass residual',f(r.massResidualKg,9)+' kg'],['Combined room / refrigerant energy residual',f(r.energyResidualKJ,7)+' kJ'],['External heat',f(r.externalHeatKJ)+' kJ'],['Compressor work into refrigerant',f(r.fluidWorkKJ)+' kJ'],['Accepted / rejected integration steps',r.acceptedSteps+' / '+r.rejectedSteps]];$('storage-balance').innerHTML=balance.map(([label,value])=>'<div>'+esc(label)+'<strong>'+esc(value)+'</strong></div>').join('');draw();
 }
 $('storage-initialize').addEventListener('click',()=>{try{initialize();}catch(e){showError(e);}});
 $('storage-step').addEventListener('click',()=>{try{pause();if(state)model.update(state,operations());clearError();step(10);}catch(e){showError(e);}});
 $('storage-pause').addEventListener('click',pause);
 $('storage-start').addEventListener('click',()=>{try{if(!state)initialize();if(state.fault)throw Error('Clear the storage stop after correcting controls, or reinitialize.');model.update(state,operations());$('live-pause').click();clearError();running=true;$('storage-pause').disabled=false;last=performance.now();timer=setInterval(()=>{try{const now=performance.now(),elapsed=Math.min(1,(now-last)/1000);last=now;step(elapsed*Number($('storage-speed').value));}catch(e){pause();showError(e);}},250);render();}catch(e){showError(e);}});
 $('storage-form').addEventListener('submit',e=>{e.preventDefault();try{const o=operations();if(state)model.update(state,o);clearError();render();}catch(e){showError(e);}});
 $('storage-clear').addEventListener('click',()=>{if(state){model.clearFault(state);clearError();render();}});
 document.addEventListener('ammonia-equipment',()=>{pause();state=null;render();$('storage-status').textContent='Active equipment changed. Initialize storage from the new profile.';});
 document.addEventListener('ammonia-run-live',pause);
 document.addEventListener('ammonia-units',e=>{units={...e.detail};render();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&running)pause();});
 window.addEventListener('error',()=>{if(running)pause();});window.addEventListener('unhandledrejection',()=>{if(running)pause();});
 $('storage-export').addEventListener('click',()=>{
  if(!state)return;const rows=[['Storage model','v0.4.5-stage.2; feed/drain closed'],['Equipment JSON SI',JSON.stringify(state.profile)],['Room conditions JSON SI',JSON.stringify(state.roomConfig)],['Seconds','Room C','Charge kg','Refrigerant U kJ','Room energy change kJ','Mass residual kg','Combined energy residual kJ','External heat kJ','Fluid work kJ','Compressor kWh','Thermal mode','Receiver heat kW','Evaporator heat kW','Condenser heat kW','Compressor enabled','Speed fraction',...['receiver','evaporator','condenser'].flatMap(key=>[key+' bar absolute',key+' C',key+' phase',key+' kg',key+' U kJ',key+' liquid volume fraction',key+' vapor mass fraction']),'Fault kind','Fault message','Fault detection seconds','Fault readings JSON SI'],...state.rows.map(r=>[r.seconds,r.T,r.totalMassKg,r.totalEnergyKJ,r.roomEnergyKJ,r.massResidualKg,r.energyResidualKJ,r.externalHeatKJ,r.fluidWorkKJ,r.electricalKWh,r.operations.thermalMode,r.operations.receiverHeat,r.operations.evaporatorHeat,r.operations.condenserHeat,r.operations.compressorOn,r.operations.speed,...Object.values(r.vessels).flatMap(v=>[v.p,v.T,v.phase,v.massKg,v.internalEnergyKJ,v.liquidVolumeFraction,v.x??'']),r.fault?.kind??'',r.fault?.message??'',r.fault?.seconds??'',r.fault?JSON.stringify(r.fault.readings):''])];
  const csv=rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n'),url=URL.createObjectURL(new Blob([csv],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='ammonia-storage-stage2.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
 render();
})();
