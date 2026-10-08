/* Synchronized history views. Everything is a projection of retained SI data. */
(function(root){
'use strict';
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const groups={pressure:'Pressures',temperature:'Temperatures',superheat:'Outlet superheat',valve:'Feed valve',level:'Liquid volume',power:'Compressor electrical demand'};
const last=a=>a&&a[a.length-1];
const colors=['#28796f','#dc713e','#3389ac','#8356ac','#986b22','#b24a60'];
const reasons={initialize:'Initialized',periodic:'Periodic observation','before-change':'Before applied change','after-change':'After applied change',stop:'Stop detected','stop-cleared':'After stop cleared',start:'Playback started',pause:'Playback paused',step:'Before manual advance',speed:'Playback speed changed'};
// Preserve first/last/extrema and gap boundaries in each time bucket. Exact
// observations remain available through the cursor and CSV, independently.
function envelope(points,definition,buckets=150){
 if(points.length<=buckets*4)return points;
 const first=points[0].seconds,span=Math.max(1e-8,last(points).seconds-first),bins=new Map();
 points.forEach((s,i)=>{const key=Math.min(buckets-1,Math.floor((s.seconds-first)/span*buckets));if(!bins.has(key))bins.set(key,[]);bins.get(key).push(i);});
 const indices=new Set();for(const bin of bins.values()){
  indices.add(bin[0]);indices.add(last(bin));let min=null,max=null,gapFirst=null,gapLast=null;
  for(const i of bin){const v=definition.read(points[i]);if(v===null){gapFirst??=i;gapLast=i;continue;}if(min===null||v<definition.read(points[min]))min=i;if(max===null||v>definition.read(points[max]))max=i;}
  for(const i of [min,max,gapFirst,gapLast])if(i!==null)indices.add(i);
 }
 return [...indices].sort((a,b)=>a-b).map(i=>points[i]);
}
function series(group,units,points){
 const pLabel={bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'}[units.p],temperature=x=>units.T==='F'?x*1.8+32:x,pressure=x=>(x-(units.p.endsWith('g')?1.01325:0))*(units.p.startsWith('psi')?14.503773773:1),delta=x=>x*(units.T==='F'?1.8:1);
 let definitions=[];
 if(group==='pressure')definitions=['receiver','condenser','evaporator','outlet'].map(key=>({key,label:key==='outlet'?'Outlet / suction':key,unit:pLabel,value:s=>s.pressures[key],convert:pressure}));
 if(group==='temperature')definitions=[...['room','condenser','evaporator','outlet','ambient'].map(key=>({key,label:key,unit:'°'+units.T,value:s=>s.temperatures[key],convert:temperature})),{key:'discharge',label:'Compressor discharge',unit:'°'+units.T,value:s=>s.dischargeTemperature,convert:temperature}];
 if(group==='superheat')definitions=[['actualSuperheat','Actual'],['sensedSuperheat','Sensed'],['targetSuperheat','Target']].map(([key,label])=>({key,label,unit:units.T==='F'?'°F Δ':'K',value:s=>s[key],convert:delta,step:key==='targetSuperheat'}));
 if(group==='valve')definitions=[['opening','Actual opening'],['command','Command']].map(([key,label])=>({key,label,unit:'%',value:s=>s[key],convert:x=>x*100}));
 if(group==='level')definitions=['receiver','condenser','evaporator','outlet'].map(key=>({key,label:key,unit:'%',value:s=>s.levels[key],convert:x=>x*100}));
 if(group==='power')definitions=[{key:'electricalDemand',label:'Electrical demand',unit:'kW',value:s=>s.electricalDemand,convert:x=>x}];
 return definitions.filter(d=>points.some(s=>Number.isFinite(d.value(s)))).map((d,i)=>({...d,color:colors[i],read:s=>Number.isFinite(d.value(s))?d.convert(d.value(s)):null}));
}
function create(container){
 let h=null,units={p:'psig',T:'F'},pinnedId=null,frozenEnd=null,selectedEvent=null,signature='',cardsKey='';
 const hidden=new Set(),cards=new Map(),f=(x,n=2)=>Number.isFinite(x)?x.toFixed(n):'—';
 container.innerHTML='<div class="history-heading"><h3>Trends &amp; event history</h3><button type="button" id="storage-history-export" class="btn" disabled>History CSV · SI</button></div><div class="history-controls"><label>View <select id="storage-trend-group"><option value="all">All trends</option>'+Object.entries(groups).map(([k,v])=>'<option value="'+k+'">'+v+'</option>').join('')+'</select></label><label>Window <select id="storage-trend-window"><option value="60">Last 60 seconds</option><option value="300" selected>Last 5 minutes</option><option value="1800">Last 30 minutes</option><option value="all">All retained</option></select></label><label><input type="checkbox" id="storage-trend-follow" checked> Follow newest</label></div><p id="storage-history-retention" class="hint">Initialize storage to begin a new history.</p><div class="history-inspection"><button type="button" class="btn" id="storage-trend-prev" aria-label="Previous history sample" disabled>Previous</button><input id="storage-trend-cursor" type="range" min="0" max="0" value="0" aria-label="Inspect retained history sample" disabled><button type="button" class="btn" id="storage-trend-next" aria-label="Next history sample" disabled>Next</button></div><p id="storage-trend-time" class="status"></p><div id="storage-trend-charts" class="history-charts"></div><p class="hint">Charts share simulated time and the inspection cursor. Swipe plots horizontally on smaller screens. Select a curve to show/hide it; tap a chart or use Previous/Next to inspect samples. Periodic samples are nominally 1 simulated second apart; applied changes and stops add exact-time observations. Gaps mean a reading is unavailable. Compressor electrical demand and discharge temperature are current-state calculations, not interval averages. Long plots retain the first/last values, extrema and gap boundaries in each time bucket; exact samples remain available for inspection and CSV. Straight segments join samples; they do not add simulated states.</p><div class="history-heading"><h4>Event history</h4><label>Filter <select id="storage-event-filter"><option value="all">All events</option><option value="controls">Applied changes</option><option value="stops">Stops &amp; clearing</option><option value="playback">Playback</option></select></label></div><p id="storage-event-count" class="hint"></p><div class="table-scroll history-event-scroll"><table><thead><tr><th>Simulated time</th><th>Event</th><th>Inspect</th></tr></thead><tbody id="storage-events"></tbody></table></div><div id="storage-event-detail" class="history-event-detail" hidden></div>';
 const $=id=>container.querySelector('#'+id);
 function points(){
  if(!h?.samples.length)return [];
  const first=h.samples[0].seconds,end=$('storage-trend-follow').checked?last(h.samples).seconds:Math.max(first,frozenEnd??last(h.samples).seconds),window=$('storage-trend-window').value;
  return h.samples.filter(s=>s.seconds<=end+1e-8&&(window==='all'||s.seconds>=end-Number(window)-1e-8));
 }
 function inspected(list){
  if(!list.length)return null;
  if($('storage-trend-follow').checked)return last(list);
  return list.find(s=>s.id===pinnedId)||list.reduce((best,s)=>Math.abs(s.id-(pinnedId??s.id))<Math.abs(best.id-(pinnedId??best.id))?s:best,list[0]);
 }
 function selectSample(index){const list=points();if(!list.length)return;if($('storage-trend-follow').checked)frozenEnd=last(h.samples).seconds;$('storage-trend-follow').checked=false;pinnedId=list[Math.max(0,Math.min(list.length-1,index))].id;render();}
 function eventName(e){return {initialize:'Initialized',controls:'Applied changes',stop:e.details.fault?.kind==='equipment'?'Equipment trip':e.details.fault?.kind==='solver'?'Solver stop':'Model stop',clear:'Stop cleared',start:'Playback started',pause:'Playback paused',step:'Manual advance',speed:'Playback speed changed'}[e.type]||e.type;}
 function formatChange(c,value){
  if(typeof value!=='number')return String(value);
  if(c.key==='ambient')return f(units.T==='F'?value*1.8+32:value)+' °'+units.T;
  if(c.key==='superheatTarget')return f(value*(units.T==='F'?1.8:1))+' '+(units.T==='F'?'°F Δ':'K');
  if(['speed','manualOpening'].includes(c.key))return f(value*100)+'%';
  return f(value,4)+({gain:' kW',leakUA:' kW/K',receiverHeat:' kW',evaporatorHeat:' kW',condenserHeat:' kW',kp:' fraction/K',ki:' fraction/(K s)'}[c.key]||'');
 }
 function drawEventDetail(){
  const e=h?.events.find(e=>e.id===selectedEvent);$('storage-event-detail').hidden=!selectedEvent;
  if(!selectedEvent)return;
  if(!e){$('storage-event-detail').textContent='This event is no longer retained.';return;}
  const labels={ambient:'Ambient air',gain:'Room heat gain',leakUA:'Room leakage UA',compressorOn:'Compressor enabled',speed:'Compressor speed setting',valveMode:'Feed mode',manualOpening:'Manual feed command',superheatTarget:'Superheat target',drainEnabled:'Condenser drain enabled',thermalMode:'Thermal boundary',kp:'PI proportional gain',ki:'PI integral gain'};
  const details=e.details.changes?e.details.changes.map(c=>(labels[c.key]||c.key)+': '+formatChange(c,c.before)+' → '+formatChange(c,c.after)).join('; '):e.details.fault?e.details.fault.message+(e.type==='clear'?'. Clearing permits another attempt; it does not prove the cause is corrected.':''):e.type==='initialize'?e.details.profileName+' revision '+e.details.profileRevision:e.details.reason||('Playback '+(e.details.speed??'')+'×'+(e.details.requestedSeconds?' · requested '+e.details.requestedSeconds+' s':''));
  $('storage-event-detail').innerHTML='<h4>'+esc(eventName(e))+' · '+f(e.seconds,4)+' s</h4><p class="text">'+esc(details)+'</p><details><summary>Recorded SI details</summary><pre>'+esc(JSON.stringify(e,null,2))+'</pre></details>';
 }
 function drawEvents(){
  const filter=$('storage-event-filter').value,filtered=(h?.events||[]).filter(e=>filter==='all'||filter==='controls'&&e.type==='controls'||filter==='stops'&&['stop','clear'].includes(e.type)||filter==='playback'&&['start','pause','step','speed'].includes(e.type)),visible=filtered.slice(-100);
  const key=[h?.nextEventId,h?.droppedEvents,filter,units.p,units.T].join('|');
  if(signature!==key){signature=key;$('storage-events').innerHTML=visible.length?visible.slice().reverse().map(e=>'<tr data-event-id="'+e.id+'"><td>'+f(e.seconds,4)+' s</td><td>'+esc(eventName(e))+'</td><td><button type="button" class="btn" data-event="'+e.id+'">Inspect #'+e.id+'</button></td></tr>').join(''):'<tr><td colspan="3">No matching events.</td></tr>';}
  $('storage-event-count').textContent=visible.length+' shown of '+filtered.length+' matching retained events · '+(h?.droppedEvents||0)+' older events removed. Chart markers show up to 100 events in the displayed time range.';
  drawEventDetail();
 }
 function buildCards(list){
  const chosen=$('storage-trend-group').value,keys=chosen==='all'?Object.keys(groups):[chosen],key=keys.map(group=>group+':'+series(group,units,list).map(d=>d.key).join(',')).join('|')+'|'+units.p+'|'+units.T;
  if(cardsKey===key)return;cardsKey=key;cards.clear();$('storage-trend-charts').innerHTML='';
  for(const group of keys){
   const definitions=series(group,units,list),card=document.createElement('section');card.className='history-chart';card.dataset.group=group;
   card.innerHTML='<h4>'+groups[group]+'</h4><div class="history-plot svg-scroll" data-plot="'+group+'"></div><div class="history-legend">'+definitions.map(d=>'<label><input type="checkbox" data-series="'+group+':'+d.key+'" '+(hidden.has(group+':'+d.key)?'':'checked')+'><i style="background:'+d.color+'"></i>'+esc(d.label)+' <strong data-value="'+d.key+'">—</strong></label>').join('')+'</div>';
   $('storage-trend-charts').append(card);cards.set(group,card);
  }
 }
 function drawChart(group,card,list,selected){
  const definitions=series(group,units,list),shown=definitions.filter(d=>!hidden.has(group+':'+d.key)),values=list.flatMap(s=>shown.map(d=>d.read(s))).filter(Number.isFinite);
  const start=list[0]?.seconds??0,end=last(list)?.seconds??0,span=Math.max(1,end-start);
  let low=values.length?Math.min(...values):0,high=values.length?Math.max(...values):1;
  const pad=Math.max((high-low)*.08,group==='valve'||group==='level'?1:.1);low-=pad;high+=pad;
  if(group==='valve'||group==='level'){low=0;high=100;}
  if(group==='superheat'||group==='power'||group==='pressure'&&!units.p.endsWith('g'))low=Math.max(0,low);
  const x=t=>60+(t-start)/span*550,y=v=>190-(v-low)/(high-low)*145;
  let svg='<svg viewBox="0 0 640 240" role="img" aria-label="'+groups[group]+' from '+f(start,3)+' to '+f(end,3)+' simulated seconds"><text x="60" y="20" class="history-axis">'+esc(definitions[0]?.unit||'No available readings')+'</text>';
  for(let i=0;i<=3;i++){const value=low+(high-low)*i/3,yy=y(value);svg+='<path d="M60 '+yy+'H610" stroke="#d8e1dd" fill="none"/><text x="54" y="'+(yy+4)+'" text-anchor="end" class="history-axis">'+f(value)+'</text>';}
  const events=(h?.events||[]).filter(e=>e.seconds>=start-1e-8&&e.seconds<=end+1e-8).slice(-100);
  for(const e of events)svg+='<path data-marker="'+e.id+'" d="M'+x(e.seconds)+' 36V190" stroke="'+(e.type==='stop'?'#a9422a':e.type==='controls'?'#dc713e':'#a9b9b5')+'" stroke-dasharray="3 4" opacity=".7"><title>'+esc(eventName(e))+' · '+f(e.seconds,4)+' s</title></path>';
  for(const d of shown){let path='',previous=null;for(const s of envelope(list,d)){const v=d.read(s);if(v===null){previous=null;continue;}path+=(previous===null?'M':d.step?'H':'L')+x(s.seconds)+(previous!==null&&d.step?'V':' ')+y(v);previous=v;}svg+='<path data-curve="'+d.key+'" d="'+path+'" fill="none" stroke="'+d.color+'" stroke-width="2"/>';}
  if(selected)svg+='<path data-cursor="'+selected.id+'" d="M'+x(selected.seconds)+' 30V195" stroke="#17343e" stroke-width="1.5"/>';
  svg+='<path d="M60 35V190H610" stroke="#657b83" fill="none"/><text x="60" y="220" class="history-axis">'+f(start,1)+' s</text><text x="610" y="220" text-anchor="end" class="history-axis">'+f(end,1)+' s</text>'+(values.length?'':'<text x="100" y="112" class="history-axis">No available or selected readings</text>')+'</svg>';
  card.querySelector('[data-plot]').innerHTML=svg;
  for(const d of definitions){const value=card.querySelector('[data-value="'+d.key+'"]');if(value)value.textContent=f(selected?d.read(selected):null)+' '+d.unit;}
 }
 function render(){
  const list=points(),selected=inspected(list),index=selected?list.indexOf(selected):0;
  if(selected)pinnedId=selected.id;
  $('storage-history-export').disabled=!h;$('storage-trend-cursor').disabled=!list.length;$('storage-trend-cursor').max=Math.max(0,list.length-1);$('storage-trend-cursor').value=index;
  $('storage-trend-cursor').setAttribute('aria-valuetext',selected?f(selected.seconds,4)+' simulated seconds · '+(reasons[selected.reason]||selected.reason):'No samples');
  $('storage-trend-prev').disabled=!list.length||index===0;$('storage-trend-next').disabled=!list.length||index===list.length-1;
  $('storage-history-retention').textContent=h?h.samples.length+' retained samples · '+f(h.samples[0]?.seconds,3)+'–'+f(last(h.samples)?.seconds,3)+' s · nominal '+h.limits.cadenceSeconds+' s sampling · '+h.droppedSamples+' older samples removed. Initialization/reset starts a new history.':'Initialize storage to begin a new history.';
  $('storage-trend-time').textContent=selected?($('storage-trend-follow').checked?'Following newest':'Pinned inspection; playback can continue')+' · '+f(selected.seconds,4)+' s · '+(reasons[selected.reason]||selected.reason)+' · sample #'+selected.id:'No samples yet.';
  buildCards(list);for(const [group,card]of cards)drawChart(group,card,list,selected);drawEvents();
 }
 for(const id of ['storage-trend-group','storage-trend-window','storage-event-filter'])$(id).addEventListener('change',()=>{cardsKey='';render();});
 $('storage-trend-follow').addEventListener('change',()=>{frozenEnd=last(h?.samples)?.seconds??null;render();});
 $('storage-trend-cursor').addEventListener('input',e=>selectSample(Number(e.target.value)));
 $('storage-trend-prev').addEventListener('click',()=>{const list=points();selectSample(list.indexOf(inspected(list))-1);});
 $('storage-trend-next').addEventListener('click',()=>{const list=points();selectSample(list.indexOf(inspected(list))+1);});
 $('storage-trend-charts').addEventListener('change',e=>{const key=e.target.dataset.series;if(!key)return;if(e.target.checked)hidden.delete(key);else hidden.add(key);render();});
 $('storage-trend-charts').addEventListener('click',e=>{const svg=e.target.closest('svg');if(!svg)return;const list=points();if(!list.length)return;const rect=svg.getBoundingClientRect(),fraction=Math.max(0,Math.min(1,((e.clientX-rect.left)/rect.width*640-60)/550)),time=list[0].seconds+fraction*Math.max(1,last(list).seconds-list[0].seconds);let index=0;list.forEach((s,i)=>{if(Math.abs(s.seconds-time)<=Math.abs(list[index].seconds-time))index=i;});selectSample(index);});
 $('storage-events').addEventListener('click',e=>{const button=e.target.closest('[data-event]');if(!button)return;selectedEvent=Number(button.dataset.event);const event=h.events.find(e=>e.id===selectedEvent);$('storage-trend-follow').checked=false;frozenEnd=event.seconds;pinnedId=event.sampleId;render();});
 $('storage-history-export').addEventListener('click',()=>{if(!h)return;const url=URL.createObjectURL(new Blob([root.AmmoniaHistory.csv(h)],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='ammonia-history-v050-stage2.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 render();
 return {update(history,displayUnits){if(history!==h){pinnedId=null;frozenEnd=null;selectedEvent=null;signature='';cardsKey='';$('storage-trend-follow').checked=true;}h=history;units={...displayUnits};render();}};
}
const api={series,envelope,create};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AmmoniaTrends=api;
})(typeof globalThis!=='undefined'?globalThis:this);
