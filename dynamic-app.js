'use strict';
(()=>{
 const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const engine=AmmoniaEngine.createEngine(JSON.parse($('property-data').textContent)),model=AmmoniaDynamic.createDynamic(engine);
 const profilesAPI=AmmoniaProfiles,initializer=AmmoniaInventory.createInitializer(engine,AmmoniaProfiles);let profiles=[],activeProfile=profilesAPI.copy(profilesAPI.DEFAULT),profileDraft=null,profileLoadNotice='Default example equipment is active.';
 try{const raw=localStorage.getItem(profilesAPI.storageKey);if(raw){const loaded=profilesAPI.restore(JSON.parse(raw));profiles=loaded.profiles;activeProfile=profilesAPI.copy(profiles.find(p=>p.id===loaded.activeId)||profilesAPI.DEFAULT);profileLoadNotice=loaded.rejected?loaded.rejected+' invalid stored profile(s) skipped.':loaded.migrated?loaded.migrated+' older profile(s) upgraded in memory; missing valve specifications remain unconfigured. Export JSON to back up.':'Restored equipment profile; the plant starts a new run.';}}catch{profileLoadNotice='Stored profiles could not be read. Default is active; JSON exports remain available.';}
 const PSI=14.503773773,ATM=1.01325;let units={p:'psig',T:'F'},state=model.create(profilesAPI.apply({},activeProfile)),running=false,timer=null,last=0;
 const f=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'—';
 const td=(v,delta=false)=>units.T==='F'?v*1.8+(delta?0:32):v;
 const ti=(v,delta=false)=>units.T==='F'?(v-(delta?0:32))/1.8:v;
 const pd=v=>(v-(units.p.endsWith('g')?ATM:0))*(units.p.startsWith('psi')?PSI:1);
 const pi=v=>v/(units.p.startsWith('psi')?PSI:1)+(units.p.endsWith('g')?ATM:0);
 const pl=()=>({bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'})[units.p];
 function displayed(kind,v){return kind==='t'?td(v):kind==='dt'?td(v,true):kind==='p'?pd(v):kind==='percent'?v*100:v;}
 function internal(kind,v){return kind==='t'?ti(v):kind==='dt'?ti(v,true):kind==='p'?pi(v):kind==='percent'?v/100:v;}
 function read(){const c=profilesAPI.apply({},activeProfile);for(const el of document.querySelectorAll('[data-live]')){if(el.readOnly){c[el.dataset.live]=state.config[el.dataset.live];continue;}if(!el.value.trim())throw Error('Fill in '+el.previousElementSibling.textContent+'.');c[el.dataset.live]=internal(el.dataset.kind,Number(el.value));}c.mode=$('live-mode').value;c.available=$('live-available').checked;return model.validate(c);}
 function fill(c){for(const el of document.querySelectorAll('[data-live]'))el.value=Number(displayed(el.dataset.kind,c[el.dataset.live]).toFixed(6));$('live-mode').value=c.mode;$('live-available').checked=c.available;unitLabels();}
 function unitLabels(){document.querySelectorAll('.live-tunit').forEach(el=>el.textContent='°'+units.T);document.querySelectorAll('.live-dunit').forEach(el=>el.textContent=units.T==='F'?'°F Δ':'K');document.querySelectorAll('.live-punit').forEach(el=>el.textContent=pl());document.querySelector('[data-disturbance="ambient"]').textContent='Warmer air +'+(units.T==='F'?'9 °F':'5 K');}
 function error(e){$('live-error').textContent=e.message||String(e);$('live-error').hidden=false;}
 function clearError(){$('live-error').hidden=true;}
 function selectedProfile(){return profiles.find(p=>p.id===$('profile-select').value)||profilesAPI.DEFAULT;}
 function persistProfiles(message){try{localStorage.setItem(profilesAPI.storageKey,JSON.stringify({schemaVersion:3,activeId:activeProfile.id,profiles}));$('profile-status').textContent=message;}catch{$('profile-status').textContent=message+' Saved in this session only: browser storage is unavailable. Export JSON to keep your profiles.';}}
 function profileList(selected){const id=selected||$('profile-select').value||activeProfile.id;$('profile-select').innerHTML=[profilesAPI.DEFAULT,...profiles].map(p=>'<option value="'+esc(p.id)+'">'+esc(p.name)+' · r'+p.revision+'</option>').join('');$('profile-select').value=[profilesAPI.DEFAULT,...profiles].some(p=>p.id===id)?id:'default';profileSummary();}
 function profileSummary(){const p=selectedProfile();$('profile-edit').disabled=p.id==='default';$('profile-delete').disabled=p.id==='default';$('profile-use').textContent=state.time||running?'Use profile & reset plant':'Use profile';$('profile-active-label').textContent=activeProfile.name+' · revision '+activeProfile.revision;
  $('profile-summary').innerHTML='<p><strong>'+esc(p.name)+'</strong> · revision '+p.revision+' · '+esc(p.arrangement)+'<br>'+esc(p.description)+'</p><p>'+p.equipment.compressors+' identical compressor(s), '+p.equipment.displacement+' m³/h each; evaporator / condenser UA '+p.equipment.evapUA+' / '+p.equipment.condUA+' kW/K.<br>'+esc(p.equipment.performanceMode==='example'?'Built-in example curves':'User fixed-efficiency assumptions')+' · '+esc({example:'Example data',assumption:'User assumptions',manufacturer:'User-entered manufacturer values; not independently validated'}[p.sourceKind])+'<br>Source: '+esc(p.source||'Not supplied')+'</p>';
  const preview=initializer.preview(p);$('profile-summary').innerHTML+='<p><strong>Starting inventory · stage 1 preview</strong><br>'+esc(inventoryText(preview))+'<br>Initialize the storage laboratory to use these settings. The quasi-steady Live plant is independent.</p><p>Connected circuit: '+(p.connections?'configured · effective feed area '+p.connections.feedAreaM2+' m²':'not configured · edit a duplicate to enter valve and outlet specifications')+'</p>';
 }
 function editProfile(p,isNew){profileDraft={original:isNew?null:profilesAPI.copy(p),value:profilesAPI.copy(p)};const d=profileDraft.value;$('profile-editor-title').textContent=isNew?'New equipment profile':'Edit '+d.name+' · next revision '+(d.revision+1);for(const [id,key]of [['profile-name','name'],['profile-description','description'],['profile-source','source'],['profile-source-kind','sourceKind'],['profile-arrangement','arrangement']])$(id).value=d[key];$('profile-performance').value=d.equipment.performanceMode;for(const el of document.querySelectorAll('[data-profile-equipment]')){el.value=Number(displayed(el.dataset.kind,d.equipment[el.dataset.profileEquipment]).toFixed(6));el.dataset.originalText=el.value;el.dataset.originalValue=d.equipment[el.dataset.profileEquipment];}for(const key of ['receiver','evaporator','condenser'])$('profile-volume-'+key).value=d.inventory.volumes[key]===null?'':d.inventory.volumes[key];
  const init=d.inventory.initialization||profilesAPI.DEFAULT.inventory.initialization;$('profile-init-mode').value=d.inventory.initialization?init.mode:'none';$('profile-init-mode').dataset.previousMode=$('profile-init-mode').value;
  for(const el of document.querySelectorAll('[data-profile-initial]')){const v=init[el.dataset.profileInitial];el.value=Number(displayed(el.dataset.kind,v).toFixed(6));el.dataset.originalText=el.value;el.dataset.originalValue=v;}
  for(const key of ['receiver','evaporator','condenser']){const el=$('profile-fill-'+key),v=init.liquidFractions[key]??.3;el.value=v*100;el.dataset.originalText=el.value;el.dataset.originalValue=v;}
  $('profile-connections-enabled').checked=!!d.connections;for(const el of document.querySelectorAll('[data-profile-connection]'))el.value=(d.connections||profilesAPI.DEFAULT.connections)[el.dataset.profileConnection];connectionFields();
  $('profile-charge').value=init.chargeKg===null?'':init.chargeKg;inventoryFields();$('profile-error').hidden=true;$('profile-form').hidden=false;performanceFields();$('profile-name').focus();}
 function connectionFields(){$('profile-connections-fields').hidden=!$('profile-connections-enabled').checked;}
 $('profile-connections-enabled').addEventListener('change',connectionFields);
 function readConnections(){if(!$('profile-connections-enabled').checked)return null;const c={};for(const el of document.querySelectorAll('[data-profile-connection]')){if(!el.value.trim())throw Error('Fill in valve/outlet specifications.');c[el.dataset.profileConnection]=Number(el.value);}return c;}
 function inventoryText(preview){
  if(!preview.ready)return preview.message;
  return 'Calculated charge '+f(preview.totalMassKg,3)+' kg · Receiver fill '+f(preview.vessels.receiver.liquidVolumeFraction*100,2)+'% · Initial evaporator / high-side saturation temperatures '+f(td(preview.vessels.evaporator.temperatureC),2)+' / '+f(td(preview.vessels.receiver.temperatureC),2)+' °'+units.T+'. '+Object.entries(preview.vessels).map(([key,v])=>key+': '+f(v.massKg,3)+' kg').join('; ')+'. '+preview.warnings.join(' ');
 }
 function readInventory(){
  const volumes={};for(const key of ['receiver','evaporator','condenser']){const raw=$('profile-volume-'+key).value.trim();volumes[key]=raw?Number(raw):null;}
  const mode=$('profile-init-mode').value;if(mode==='none')return {volumes,initialization:null};
  const initialization={mode,chargeKg:null,liquidFractions:{}};
  for(const el of document.querySelectorAll('[data-profile-initial]')){if(!el.value.trim())throw Error('Fill in initial pressure.');initialization[el.dataset.profileInitial]=el.value===el.dataset.originalText?Number(el.dataset.originalValue):internal(el.dataset.kind,Number(el.value));}
  for(const key of ['receiver','evaporator','condenser']){const el=$('profile-fill-'+key);if(key==='receiver'&&mode==='charge'){initialization.liquidFractions[key]=null;continue;}if(!el.value.trim())throw Error('Fill in '+key+' liquid volume percentage.');initialization.liquidFractions[key]=el.value===el.dataset.originalText?Number(el.dataset.originalValue):Number(el.value)/100;}
  if(mode==='charge'){if(!$('profile-charge').value.trim())throw Error('Fill in total ammonia charge.');initialization.chargeKg=Number($('profile-charge').value);}
  return {volumes,initialization};
 }
 function inventoryFields(){
  const mode=$('profile-init-mode').value;$('profile-init-fields').hidden=mode==='none';$('profile-fill-receiver-control').hidden=mode==='charge';$('profile-charge-control').hidden=mode!=='charge';inventoryPreview();
 }
 function inventoryPreview(){
  if(!profileDraft)return;
  try{const p={...profileDraft.value,inventory:readInventory()},preview=initializer.preview(p);$('profile-inventory-preview').textContent=inventoryText(preview)+' Equilibrium preview; initialize the storage laboratory to use it.';}
  catch(e){$('profile-inventory-preview').textContent='Initialization incomplete: '+e.message;}
 }
 $('profile-inventory').addEventListener('input',inventoryFields);
 $('profile-init-mode').addEventListener('change',()=>{
  const el=$('profile-init-mode'),next=el.value,previous=el.dataset.previousMode;
  try{
   el.value=previous;const preview=initializer.preview({...profileDraft.value,inventory:readInventory()});
   if(preview.ready&&next==='charge')$('profile-charge').value=preview.totalMassKg;
   if(preview.ready&&next==='levels'){const input=$('profile-fill-receiver'),fraction=preview.vessels.receiver.liquidVolumeFraction;input.value=fraction*100;input.dataset.originalText=input.value;input.dataset.originalValue=fraction;}
  }catch{}finally{el.value=next;el.dataset.previousMode=next;inventoryFields();}
 });
 function performanceFields(){const fixed=$('profile-performance').value==='fixed';document.querySelectorAll('[data-fixed-efficiency]').forEach(el=>el.hidden=!fixed);}
 function closeProfileEditor(){profileDraft=null;$('profile-form').hidden=true;$('profile-error').hidden=true;}
 $('profile-select').addEventListener('change',()=>{profileSummary();$('profile-status').textContent='Selected '+selectedProfile().name+'. Use profile to apply it; equipment changes reset the plant.';});
 $('profile-new').addEventListener('click',()=>{const p=profilesAPI.duplicate(profilesAPI.DEFAULT,'My equipment');p.sourceKind='assumption';p.source='';p.description='';editProfile(p,true);});
 $('profile-duplicate').addEventListener('click',()=>editProfile(profilesAPI.duplicate(selectedProfile()),true));
 $('profile-edit').addEventListener('click',()=>{const p=selectedProfile();if(p.id!=='default')editProfile(p,false);});
 $('profile-cancel').addEventListener('click',closeProfileEditor);$('profile-performance').addEventListener('change',performanceFields);
 $('profile-form').addEventListener('submit',event=>{event.preventDefault();try{
  if(!profileDraft)throw Error('Create or edit a profile first.');const d=profilesAPI.copy(profileDraft.value);d.name=$('profile-name').value;d.description=$('profile-description').value;d.source=$('profile-source').value;d.sourceKind=$('profile-source-kind').value;d.arrangement=$('profile-arrangement').value;d.equipment.performanceMode=$('profile-performance').value;
  for(const el of document.querySelectorAll('[data-profile-equipment]')){if(!el.value.trim())throw Error('Fill in '+el.previousElementSibling.textContent+'.');d.equipment[el.dataset.profileEquipment]=el.value===el.dataset.originalText?Number(el.dataset.originalValue):internal(el.dataset.kind,Number(el.value));}
  d.inventory=readInventory();d.connections=readConnections();const preview=initializer.preview(d);if(preview.status==='invalid')throw Error(preview.message);
  const next=profileDraft.original?profilesAPI.revise(profileDraft.original,d):profilesAPI.normalize(d);if(!profileDraft.original&&profiles.length>=20)throw Error('Up to 20 custom profiles are supported. Delete one before adding another.');
  if(profileDraft.original)profiles=profiles.map(p=>p.id===next.id?next:p);else profiles.push(next);
  closeProfileEditor();profileList(next.id);persistProfiles('Saved '+next.name+' revision '+next.revision+'. Use profile to activate it'+(state.time?' and reset the plant.':'.'));
 }catch(e){$('profile-error').hidden=false;$('profile-error').textContent=e.message;}});
 $('profile-use').addEventListener('click',()=>{try{const next=profilesAPI.copy(selectedProfile()),config=model.validate(profilesAPI.apply(read(),next));pause();activeProfile=next;state=model.create(config);fill(config);clearError();render();profileSummary();persistProfiles('Active: '+next.name+' revision '+next.revision+'. Plant reset; operating settings retained.');document.dispatchEvent(new CustomEvent('ammonia-equipment'));}catch(e){error(e);}});
 $('profile-delete').addEventListener('click',()=>{const p=selectedProfile();if(p.id==='default')return;if(p.id===activeProfile.id){$('profile-status').textContent='Use another profile before deleting the active profile.';return;}profiles=profiles.filter(x=>x.id!==p.id);if(profileDraft&&profileDraft.value.id===p.id)closeProfileEditor();profileList(activeProfile.id);persistProfiles('Deleted '+p.name+'.');});
 $('profile-export').addEventListener('click',()=>{const p=selectedProfile(),url=URL.createObjectURL(new Blob([JSON.stringify(p,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='ammonia-equipment-profile-v3.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 $('profile-import').addEventListener('click',()=>$('profile-import-file').click());
 $('profile-import-file').addEventListener('change',async()=>{const file=$('profile-import-file').files[0];if(!file)return;try{if(file.size>100000)throw Error('Equipment profile exceeds 100 KB.');if(profiles.length>=20)throw Error('Custom profile limit reached.');const p=profilesAPI.imported(JSON.parse(await file.text())),preview=initializer.preview(p);if(preview.status==='invalid')throw Error(preview.message);profiles.push(p);profileList(p.id);persistProfiles('Imported '+p.name+'. Review the specifications, then Use profile to activate.');}catch(e){$('profile-status').textContent='Import rejected: '+e.message;}finally{$('profile-import-file').value='';}});
 function pause(){running=false;clearInterval(timer);timer=null;$('live-pause').disabled=true;$('live-start').disabled=false;$('live-start').textContent=state.time?'Resume':'Start';render();}
 function advance(seconds){model.step(state,seconds);if(state.fault)pause();render();}
 function start(){try{if(state.fault)throw Error(state.fault.kind==='equipment'?'Reset the trip before resuming.':'Clear the model stop after correcting inputs, or reset the plant.');const c=read();if(state.time===0)state=model.create(c);else model.update(state,c);clearError();if(state.T< -40||state.T>50)throw Error('Reset the plant with an initial room temperature inside the model domain.');document.dispatchEvent(new CustomEvent('ammonia-run-live'));running=true;$('live-pause').disabled=false;$('live-start').disabled=true;last=performance.now();timer=setInterval(()=>{try{const now=performance.now(),elapsed=Math.min(1,(now-last)/1000);last=now;advance(elapsed*Number($('live-speed').value));}catch(e){pause();error(e);}},250);render();}catch(e){error(e);}}
 function render(){
  const row=model.record(state),r=state.point&&state.point.r,clock=Math.floor(state.time),h=Math.floor(clock/3600),m=Math.floor(clock%3600/60),s=clock%60;
  $('live-clock').textContent=[h,m,s].map(x=>String(x).padStart(2,'0')).join(':')+' simulated';
  $('live-status').textContent=(state.fault?({equipment:'TRIPPED',solver:'SOLVER LIMIT',domain:'MODEL LIMIT'}[state.fault.kind]):running?'Running':state.time?'Paused':'Ready')+' · '+state.reason+' · '+state.starts+' compressor start'+(state.starts===1?'':'s');
  const metrics=[['Room temperature',f(td(state.T))+' °'+units.T],['Actual suction',r?f(pd(r.config.pressure),2)+' '+pl():'— (off)'],['Actual discharge',r?f(pd(r.pHigh),2)+' '+pl():'— (off)'],['Per-stage speed · '+state.stages+' running',f(state.speed*100,0)+' / '+f(state.command*100,0)+'%'],['Delivered cooling',f(row.Q)+' kW'],['Electrical input',f(row.power)+' kW'],['Operating COP',f(row.COP,2)],['Compressor electricity',f(state.energy,2)+' kWh'],['Discharge temperature',r?f(td(r.states[1].T))+' °'+units.T:'— (off)']];
  $('live-metrics').innerHTML=metrics.map(([label,value])=>'<div class="metric"><label>'+esc(label)+'</label><strong style="font-size:20px">'+esc(value)+'</strong></div>').join('');
  const balance=state.config.thermalMass*1000*(state.T-state.config.initial)-(state.leakHeat+state.gainHeat-state.removed);
  const vals=[['Room energy residual',f(balance,6)+' kJ'],['Cycle energy residual',r?r.balance.toExponential(2)+' kW':'—'],['UA relative residual',state.point?Math.max(...state.point.residual.map(Math.abs)).toExponential(2):'—'],['Evap. / condenser required UA',state.point?f(state.point.evapRequired,2)+' / '+f(state.point.condRequired,2)+' kW/K':'—'],['Compressor isentropic / volumetric η',state.point?f(state.point.etaIs*100)+' / '+f(state.point.etaVol*100)+'%':'—'],['Control target',f(pd(state.config.suctionTarget),2)+' '+pl()]];
  $('live-balance').innerHTML=vals.map(([label,value])=>'<div>'+esc(label)+'<strong>'+esc(value)+'</strong></div>').join('');
  $('live-events').innerHTML=state.events.length?state.events.slice(-12).reverse().map(e=>'<p>'+f(e.seconds/60,1)+' min · '+esc(e.text)+'</p>').join(''):'No events yet.';
  $('live-fault').hidden=!state.fault;
  $('live-trip-reset').textContent=state.fault&&state.fault.kind!=='equipment'?'Clear model stop':'Reset trip';
  if(state.fault){
   const fault=state.fault,v=fault.readings;
   const values=['Room '+f(td(v.room))+' °'+units.T];
   if(fault.kind==='equipment')values.push('Suction '+f(pd(v.pressure),2)+' '+pl(),'Discharge '+f(pd(v.condensing),2)+' '+pl(),'Discharge temperature '+f(td(v.discharge))+' °'+units.T,'Speed '+f(v.speed*100,1)+'%; '+v.stages+' stage(s)', 'Limits: high '+f(pd(fault.limits.highTrip),2)+' '+pl()+', low '+f(pd(fault.limits.lowTrip),2)+' '+pl()+', discharge temperature '+f(td(fault.limits.dischargeTrip))+' °'+units.T);
   const help=fault.kind==='equipment'?'Captured readings at the trip, not current off-state pressures. Correct the cause and reset the trip; minimum-off timers still apply.':fault.kind==='solver'?'The solver could not establish an operating point; no equipment trip is asserted. Review equipment and operating inputs, then clear the model stop to retry.':'The model reached its supported domain limit; no equipment trip is asserted. Review inputs; reset the plant if room temperature is outside −40 to 50 °C.';
   $('live-fault').textContent=fault.message+' · Detected at '+f(fault.seconds,2)+' simulated seconds. '+values.join(' · ')+'. '+help;
  }
  $('live-export').disabled=!state.rows.length;draw();profileSummary();
 }
 function draw(){
  if(!state.rows.length){$('live-trends').innerHTML='<div class="empty">Trends appear when the plant advances.</div>';return;}
  let rows=state.rows.filter(r=>r.seconds>=state.time-7200);const stride=Math.max(1,Math.ceil(rows.length/400));rows=rows.filter((_,i)=>i%stride===0||i===rows.length-1);
  const W=900,H=660,l=65,rr=20,start=Math.max(0,state.time-7200),end=Math.max(start+60,state.time),x=s=>l+(s-start)/(end-start)*(W-l-rr);
  const panels=[{title:'Room · °'+units.T,lines:[['T',v=>td(v),'#3389ac','Room'],['target',v=>td(v),'#a7aba3','Setpoint']]},{title:'Pressure · '+pl(),lines:[['pressure',v=>pd(v),'#3389ac','Suction'],['condensing',v=>pd(v),'#dc713e','Discharge']]},{title:'Speed · %',lines:[['speed',v=>v*100,'#28796f','Actual'],['command',v=>v*100,'#a7aba3','Commanded']]},{title:'Duty / power · kW',lines:[['Q',v=>v,'#3389ac','Cooling'],['power',v=>v,'#dc713e','Electricity']]}];
  let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Live room temperature, pressure, compressor speed, cooling duty and electrical input trends">`;
  panels.forEach((panel,k)=>{
   const top=25+k*155,bottom=top+115;let values=[];for(const [key,convert] of panel.lines)for(const row of rows){const v=row[key]===null?null:convert(row[key]);if(Number.isFinite(v))values.push(v);}
   let min=values.length?Math.min(...values):0,max=values.length?Math.max(...values):1;if(k===2){min=0;max=100;}else if(k===3)min=0;const pad=Math.max(1,(max-min)*.1);if(k!==2){min-=pad;max+=pad;}if(max-min<1)max=min+1;
   const y=v=>bottom-(v-min)/(max-min)*(bottom-top);
   svg+=`<text x="${l}" y="${top-8}" fill="#17343e" font-size="11">${esc(panel.title)}</text>`;
   for(let i=0;i<=3;i++){const v=min+(max-min)*i/3;svg+=`<path d="M${l} ${y(v)}H${W-rr}" stroke="#e0e7e3"/><text x="${l-8}" y="${y(v)+4}" text-anchor="end" font-size="10" fill="#657b83">${f(v)}</text>`;}
   panel.lines.forEach(([key,convert,color,label],j)=>{let path='',pen=false;for(const row of rows){const v=row[key]===null?null:convert(row[key]);if(!Number.isFinite(v)){pen=false;continue;}path+=(pen?'L':'M')+x(row.seconds)+' '+y(v);pen=true;}svg+=`<path d="${path}" fill="none" stroke="${color}" stroke-width="2" ${key==='command'||key==='target'?'stroke-dasharray="5 4"':''}/><text x="${W-230+j*105}" y="${top-8}" fill="${color}" font-size="10">${esc(label)}</text>`;});
  });
  for(let i=0;i<=5;i++){const s=start+(end-start)*i/5;svg+=`<text x="${x(s)}" y="643" text-anchor="middle" font-size="10" fill="#657b83">${f(s/60,1)}</text>`;}svg+='<text x="450" y="657" text-anchor="middle" fill="#657b83" font-size="10">Simulation time · minutes</text></svg>';$('live-trends').innerHTML=svg;
 }
 $('live-start').addEventListener('click',start);$('live-pause').addEventListener('click',pause);
 $('live-reset').addEventListener('click',()=>{try{const c=model.validate(profilesAPI.apply(read(),activeProfile));pause();state=model.create(c);fill(c);clearError();render();profileSummary();}catch(e){error(e);}});
 $('live-step').addEventListener('click',()=>{try{pause();if(state.time===0)state=model.create(read());clearError();advance(60);}catch(e){error(e);}});
 $('live-form').addEventListener('submit',e=>{e.preventDefault();try{const c=read();if(state.time&&c.thermalMass!==state.config.thermalMass)throw Error('Reset the plant to change thermal mass; this preserves the room energy balance.');if(state.time&&c.initial!==state.config.initial)throw Error('Reset the plant to change initial temperature.');model.update(state,c);clearError();render();}catch(e){error(e);}});
 $('live-trip-reset').addEventListener('click',()=>{model.resetTrip(state);clearError();render();});
 for(const button of document.querySelectorAll('[data-disturbance]'))button.addEventListener('click',()=>{try{const patch={};switch(button.dataset.disturbance){case'gain':patch.gain=state.config.gain+10;break;case'ambient':patch.ambient=state.config.ambient+5;break;case'condenser':patch.condUA=state.config.condUA*.75;break;case'availability':patch.available=!state.config.available;break;}model.update(state,patch);fill(state.config);clearError();render();}catch(e){error(e);}});
 document.addEventListener('ammonia-units',event=>{const drafts={};for(const el of document.querySelectorAll('[data-live], [data-profile-equipment], [data-profile-initial]'))drafts[el.id]=el.value.trim()?((el.dataset.profileEquipment||el.dataset.profileInitial)&&el.value===el.dataset.originalText?Number(el.dataset.originalValue):internal(el.dataset.kind,Number(el.value))):null;units={...event.detail};for(const el of document.querySelectorAll('[data-live], [data-profile-equipment], [data-profile-initial]'))if(drafts[el.id]!==null){el.value=Number(displayed(el.dataset.kind,drafts[el.id]).toFixed(6));if(el.dataset.profileEquipment||el.dataset.profileInitial){el.dataset.originalText=el.value;el.dataset.originalValue=drafts[el.id];}}unitLabels();inventoryPreview();render();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&running){pause();$('live-status').textContent+=' · Playback paused while browser is in background.';}});
 $('live-export').addEventListener('click',()=>{const rows=[['Equipment profile',activeProfile.name,'Revision',activeProfile.revision],['Equipment specification JSON (SI)',JSON.stringify(activeProfile)],[],['Seconds','Room C','Compressor enabled','Actual speed fraction','Command fraction','Suction bar absolute','Discharge bar absolute','Cooling kW','Electrical kW','COP','Discharge C','Compressor kWh','Starts','Control reason','Trip','Relative UA residual','Active compressor stages','Setpoint C','Ambient C','Internal gain kW','Evaporator UA kW/K','Condenser UA kW/K','Fault kind','Fault message','Fault detection seconds','Captured suction bar absolute','Captured discharge bar absolute','Captured discharge C','Captured room C','Captured speed fraction','Captured stages','Trip high limit bar absolute','Trip low limit bar absolute','Trip discharge limit C'],...state.rows.map(r=>[r.seconds,r.T,r.on,r.speed,r.command,r.pressure??'',r.condensing??'',r.Q,r.power,r.COP??'',r.discharge??'',r.kWh,r.starts,r.reason,r.trip??'',r.residual??'',r.stages,r.target,r.ambient,r.gain,r.evapUA,r.condUA,r.fault?.kind??'',r.fault?.message??'',r.fault?.seconds??'',r.fault?.readings.pressure??'',r.fault?.readings.condensing??'',r.fault?.readings.discharge??'',r.fault?.readings.room??'',r.fault?.readings.speed??'',r.fault?.readings.stages??'',r.fault?.limits?.highTrip??'',r.fault?.limits?.lowTrip??'',r.fault?.limits?.dischargeTrip??''])];const text=rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n'),url=URL.createObjectURL(new Blob([text],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='ammonia-live-v045.csv';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 $('runtime-dismiss').addEventListener('click',()=>{$('runtime-notice').hidden=true;});
 function runtimeFailure(message){pause();$('runtime-message').textContent='An application error occurred: '+message+'. Live playback was paused; reload if a control stops responding.';$('runtime-notice').hidden=false;}
 window.addEventListener('error',event=>{if(event.filename===location.href&&event.message&&event.message!=='Script error.')runtimeFailure(event.message);});
 window.addEventListener('unhandledrejection',event=>{if(event.reason instanceof Error)runtimeFailure(event.reason.message);});
 window.AmmoniaPlantSnapshot=()=>({profile:profilesAPI.copy(activeProfile),roomConfig:{...state.config}});
 fill(state.config);profileList(activeProfile.id);$('profile-status').textContent=profileLoadNotice;render();if(window.AmmoniaStartup)window.AmmoniaStartup.ready=true;$('startup-notice').hidden=true;
})();
