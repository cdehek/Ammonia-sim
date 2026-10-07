'use strict';
(()=>{
 const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const engine=AmmoniaEngine.createEngine(JSON.parse($('property-data').textContent)),model=AmmoniaDynamic.createDynamic(engine);
 const PSI=14.503773773,ATM=1.01325;let units={p:'psig',T:'F'},state=model.create({}),running=false,timer=null,last=0;
 const f=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'—';
 const td=(v,delta=false)=>units.T==='F'?v*1.8+(delta?0:32):v;
 const ti=(v,delta=false)=>units.T==='F'?(v-(delta?0:32))/1.8:v;
 const pd=v=>(v-(units.p.endsWith('g')?ATM:0))*(units.p.startsWith('psi')?PSI:1);
 const pi=v=>v/(units.p.startsWith('psi')?PSI:1)+(units.p.endsWith('g')?ATM:0);
 const pl=()=>({bara:'bar(a)',barg:'bar(g)',psia:'psia',psig:'psig'})[units.p];
 function displayed(kind,v){return kind==='t'?td(v):kind==='dt'?td(v,true):kind==='p'?pd(v):kind==='percent'?v*100:v;}
 function internal(kind,v){return kind==='t'?ti(v):kind==='dt'?ti(v,true):kind==='p'?pi(v):kind==='percent'?v/100:v;}
 function read(){const c={};for(const el of document.querySelectorAll('[data-live]')){if(!el.value.trim())throw Error('Fill in '+el.previousElementSibling.textContent+'.');c[el.dataset.live]=internal(el.dataset.kind,Number(el.value));}c.mode=$('live-mode').value;c.available=$('live-available').checked;return model.validate(c);}
 function fill(c){for(const el of document.querySelectorAll('[data-live]'))el.value=Number(displayed(el.dataset.kind,c[el.dataset.live]).toFixed(6));$('live-mode').value=c.mode;$('live-available').checked=c.available;unitLabels();}
 function unitLabels(){document.querySelectorAll('.live-tunit').forEach(el=>el.textContent='°'+units.T);document.querySelectorAll('.live-dunit').forEach(el=>el.textContent=units.T==='F'?'°F Δ':'K');document.querySelectorAll('.live-punit').forEach(el=>el.textContent=pl());document.querySelector('[data-disturbance="ambient"]').textContent='Warmer air +'+(units.T==='F'?'9 °F':'5 K');}
 function error(e){$('live-error').textContent=e.message||String(e);$('live-error').hidden=false;}
 function clearError(){$('live-error').hidden=true;}
 function pause(){running=false;clearInterval(timer);timer=null;$('live-pause').disabled=true;$('live-start').disabled=false;$('live-start').textContent=state.time?'Resume':'Start';render();}
 function advance(seconds){model.step(state,seconds);if(state.trip||state.T< -40||state.T>50)pause();render();}
 function start(){try{const c=read();if(state.time===0)state=model.create(c);else model.update(state,c);clearError();if(state.trip)throw Error('Reset the trip before resuming.');if(state.T< -40||state.T>50)throw Error('Reset the plant with an initial room temperature inside the model domain.');running=true;$('live-pause').disabled=false;$('live-start').disabled=true;last=performance.now();timer=setInterval(()=>{try{const now=performance.now(),elapsed=Math.min(1,(now-last)/1000);last=now;advance(elapsed*Number($('live-speed').value));}catch(e){pause();error(e);}},250);render();}catch(e){error(e);}}
 function render(){
  const row=model.record(state),r=state.point&&state.point.r,clock=Math.floor(state.time),h=Math.floor(clock/3600),m=Math.floor(clock%3600/60),s=clock%60;
  $('live-clock').textContent=[h,m,s].map(x=>String(x).padStart(2,'0')).join(':')+' simulated';
  $('live-status').textContent=(state.trip?'TRIPPED':running?'Running':state.time?'Paused':'Ready')+' · '+state.reason+' · '+state.starts+' compressor start'+(state.starts===1?'':'s');
  const metrics=[['Room temperature',f(td(state.T))+' °'+units.T],['Actual suction',r?f(pd(r.config.pressure),2)+' '+pl():'— (off)'],['Actual discharge',r?f(pd(r.pHigh),2)+' '+pl():'— (off)'],['Per-stage speed · '+state.stages+' running',f(state.speed*100,0)+' / '+f(state.command*100,0)+'%'],['Delivered cooling',f(row.Q)+' kW'],['Electrical input',f(row.power)+' kW'],['Operating COP',f(row.COP,2)],['Compressor electricity',f(state.energy,2)+' kWh'],['Discharge temperature',r?f(td(r.states[1].T))+' °'+units.T:'— (off)']];
  $('live-metrics').innerHTML=metrics.map(([label,value])=>'<div class="metric"><label>'+esc(label)+'</label><strong style="font-size:20px">'+esc(value)+'</strong></div>').join('');
  const balance=state.config.thermalMass*1000*(state.T-state.config.initial)-(state.leakHeat+state.gainHeat-state.removed);
  const vals=[['Room energy residual',f(balance,6)+' kJ'],['Cycle energy residual',r?r.balance.toExponential(2)+' kW':'—'],['UA relative residual',state.point?Math.max(...state.point.residual.map(Math.abs)).toExponential(2):'—'],['Evap. / condenser required UA',state.point?f(state.point.evapRequired,2)+' / '+f(state.point.condRequired,2)+' kW/K':'—'],['Example isentropic / volumetric η',state.point?f(state.point.etaIs*100)+' / '+f(state.point.etaVol*100)+'%':'—'],['Control target',f(pd(state.config.suctionTarget),2)+' '+pl()]];
  $('live-balance').innerHTML=vals.map(([label,value])=>'<div>'+esc(label)+'<strong>'+esc(value)+'</strong></div>').join('');
  $('live-events').innerHTML=state.events.length?state.events.slice(-12).reverse().map(e=>'<p>'+f(e.seconds/60,1)+' min · '+esc(e.text)+'</p>').join(''):'No events yet.';
  $('live-export').disabled=!state.rows.length;draw();
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
 $('live-reset').addEventListener('click',()=>{try{const c=read();pause();state=model.create(c);clearError();render();}catch(e){error(e);}});
 $('live-step').addEventListener('click',()=>{try{pause();if(state.time===0)state=model.create(read());clearError();advance(60);}catch(e){error(e);}});
 $('live-form').addEventListener('submit',e=>{e.preventDefault();try{const c=read();if(state.time&&c.thermalMass!==state.config.thermalMass)throw Error('Reset the plant to change thermal mass; this preserves the room energy balance.');if(state.time&&c.initial!==state.config.initial)throw Error('Reset the plant to change initial temperature.');model.update(state,c);clearError();render();}catch(e){error(e);}});
 $('live-trip-reset').addEventListener('click',()=>{model.resetTrip(state);clearError();render();});
 for(const button of document.querySelectorAll('[data-disturbance]'))button.addEventListener('click',()=>{try{const patch={};switch(button.dataset.disturbance){case'gain':patch.gain=state.config.gain+10;break;case'ambient':patch.ambient=state.config.ambient+5;break;case'condenser':patch.condUA=state.config.condUA*.75;break;case'availability':patch.available=!state.config.available;break;}model.update(state,patch);fill(state.config);clearError();render();}catch(e){error(e);}});
 document.addEventListener('ammonia-units',event=>{const drafts={};for(const el of document.querySelectorAll('[data-live]'))drafts[el.id]=el.value.trim()?internal(el.dataset.kind,Number(el.value)):null;units={...event.detail};for(const el of document.querySelectorAll('[data-live]'))if(drafts[el.id]!==null)el.value=Number(displayed(el.dataset.kind,drafts[el.id]).toFixed(6));unitLabels();render();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&running){pause();$('live-status').textContent+=' · Playback paused while browser is in background.';}});
 $('live-export').addEventListener('click',()=>{const rows=[['Seconds','Room C','Compressor enabled','Actual speed fraction','Command fraction','Suction bar absolute','Discharge bar absolute','Cooling kW','Electrical kW','COP','Discharge C','Compressor kWh','Starts','Control reason','Trip','Relative UA residual','Active compressor stages','Setpoint C','Ambient C','Internal gain kW','Evaporator UA kW/K','Condenser UA kW/K'],...state.rows.map(r=>[r.seconds,r.T,r.on,r.speed,r.command,r.pressure??'',r.condensing??'',r.Q,r.power,r.COP??'',r.discharge??'',r.kWh,r.starts,r.reason,r.trip??'',r.residual??'',r.stages,r.target,r.ambient,r.gain,r.evapUA,r.condUA])];const text=rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n'),url=URL.createObjectURL(new Blob([text],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='ammonia-live-v030.csv';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 $('runtime-dismiss').addEventListener('click',()=>{$('runtime-notice').hidden=true;});
 function runtimeFailure(message){pause();$('runtime-message').textContent='An application error occurred: '+message+'. Live playback was paused; reload if a control stops responding.';$('runtime-notice').hidden=false;}
 window.addEventListener('error',event=>{if(event.filename===location.href&&event.message&&event.message!=='Script error.')runtimeFailure(event.message);});
 window.addEventListener('unhandledrejection',event=>{if(event.reason instanceof Error)runtimeFailure(event.reason.message);});
 fill(state.config);render();if(window.AmmoniaStartup)window.AmmoniaStartup.ready=true;$('startup-notice').hidden=true;
})();
