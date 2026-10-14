(function(root){
'use strict';
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function create(container,adapter){
 const T=root.AmmoniaTraining;let attempt=null,plant=null,savedReport=null,hint=false,lastStatus=null;
 container.innerHTML='<div class="training-heading"><h3>Guided exercises</h3><span class="version">Default training model</span></div><p class="text">Loading/resetting replaces the connected run with fixed Default equipment and training room conditions. Apply Default in the equipment panel first. Custom profiles remain saved. Exercises use model inputs and computed outcomes; they are not plant operating procedures.</p><div class="training-toolbar"><label for="training-select">Exercise</label><select id="training-select">'+Object.entries(T.EXERCISES).map(([id,d])=>'<option value="'+id+'">'+esc(d.name)+'</option>').join('')+'</select><button type="button" class="btn primary" id="training-load">Load exercise</button><button type="button" class="btn" id="training-reset" disabled>Reset exercise</button><button type="button" class="btn" id="training-end" disabled>End exercise</button><button type="button" class="btn" id="training-export" disabled>Export attempt · JSON</button></div><p class="error" id="training-error" role="alert" hidden></p><h4 id="training-selected-title"></h4><p id="training-description" class="text"></p><p id="training-selection-note" class="hint" hidden></p><h4 id="training-attempt-title"></h4><p id="training-status" class="status" role="status">Choose an exercise and load its setup.</p><ol id="training-objectives" class="training-objectives"></ol><div class="training-toolbar"><button type="button" class="btn primary" id="training-disturbance" hidden>Apply disturbance</button><button type="button" class="btn" id="training-restore" hidden>Restore off-state controls</button><button type="button" class="btn" id="training-hint" aria-expanded="false">Show hint</button></div><p id="training-hint-text" class="training-hint" hidden></p><fieldset id="training-reflection"><legend>Reflection</legend><p id="training-question" class="text"></p><label for="training-answer">Your answer</label><select id="training-answer"></select><button type="button" class="btn" id="training-check" disabled>Check answer</button><p id="training-feedback" class="hint" role="status"></p></fieldset><div id="training-debrief" class="training-debrief" hidden></div><div class="training-toolbar"><button type="button" class="btn" id="training-advance" disabled>Advance 10 seconds</button><button type="button" class="btn" id="training-run" disabled>Start exercise playback</button><button type="button" class="btn" id="training-clear" hidden>Clear modeled stop</button></div><p class="hint">Use the connected playback controls above or the exercise actions to start, pause or advance. Successful objectives pause playback. Reset starts a fresh attempt; export before resetting or reloading to retain evidence.</p>';
 const $=id=>container.querySelector('#'+id),active=()=>attempt?.status==='active';
 const next=document.createElement('section');next.className='training-next';next.setAttribute('aria-label','Suggested next action');
 next.innerHTML='<h4>Suggested next action</h4><p id="training-next-text"></p><button type="button" class="btn" id="training-next-control">Go to control</button><p class="hint">This is guidance, not an extra grading sequence. The measured objectives below decide completion; supported actions may be taken in a different order.</p><div id="training-observations" class="training-observations"></div>';
 $('training-status').before(next);

 const summary=document.createElement('div');summary.className='training-current';
 summary.append($('training-attempt-title'),$('training-status'));next.before(summary);
 const actions=document.createElement('div');actions.className='training-actions';
 actions.append($('training-disturbance').parentElement,$('training-advance').parentElement);
 next.after(actions);
 const note=next.querySelector('.hint');note.classList.add('training-guidance-note');actions.after(note,$('training-observations'));
 const purpose=document.createElement('p');purpose.id='training-purpose';purpose.className='hint';summary.after(purpose);
 const library=document.createElement('details');library.className='training-library';
 library.innerHTML='<summary>Choose, load or manage an exercise</summary>';
 const toolbar=$('training-load').parentElement;
 library.append(toolbar,$('training-selected-title'),$('training-description'),$('training-selection-note'),container.querySelector('.training-heading + .text'));
 container.querySelector('.training-heading').after(library);
 const learning=document.createElement('div');learning.className='training-learning';
 learning.append($('training-reflection'),$('training-hint-text'),$('training-objectives'));
 actions.after(learning);
 let nextControl='training-load',presentedAttempt=null;library.open=true;
 $('training-next-control').addEventListener('click',()=>{const el=$(nextControl);if(el&&!el.disabled){el.focus();el.scrollIntoView({block:'nearest'});}});
 function guidance(d){
  const a=attempt,quiz=a?.goals[a.goals.length-1].met;
  $('training-purpose').textContent={startup:'Watch the DX circuit establish feed and sustained superheat control.',load:'Watch the room respond to a larger heat load.',hot:'See hotter condenser air produce a measured pressure rise and discharge-temperature trip.',restriction:'Compare commanded opening, actuator lag and reduced liquid feed.',tuning:'Watch actual and sensed superheat settle around the new target.'}[a?.exercise||$('training-select').value];
  let text,target='training-advance';
  if(!adapter.defaultActive()){text='Open Equipment Profiles and apply Default equipment, then return here to load the exercise.';target=null;}
  else if(!a){text='Load '+d.name+'. The established '+d.warmup+'-second warmup runs automatically before the attempt begins.';target='training-load';}
  else if(a.status==='completed'){text='All graded objectives have recorded evidence. Review the debrief and export your attempt to keep the observations.';target='training-export';}
  else if(a.status!=='active'){text='This attempt '+a.status+'. Review the recorded reason and export its evidence, or reset to try again.';target='training-export';}
  else if(!quiz){text='Answer the reflection question. Use the hint or inspect the live readings if you need help. You can also observe the plant first; reflection is a required objective, not a required first step.';target='training-answer';}
  else if(d.action&&a.injectedAt===null){text='Automatic warmup is complete. '+d.action+'. Keep the established exercise controls so the measured response can be graded.';target='training-disturbance';}
  else if(a.exercise==='hot'&&a.expectedFault&&!a.restored){text='The engine recorded the high-discharge-temperature equipment trip. Inspect its captured evidence in Operator Assist, then restore the off-state controls here.';target='training-restore';}
  else if(a.exercise==='hot'&&a.restored&&plant?.fault){text='Off-state controls are restored: compressor disabled, feed commanded closed and condenser air restored. Clear the modeled stop, then advance 10 simulated seconds.';target='training-clear';}
  else if(a.exercise==='hot'&&a.restored){text='Advance simulated time with the compressor off. Recovery is graded only after the engine accepts the required 10 seconds.';}
  else if(a.exercise==='hot'){text='Advance simulated time and watch condenser pressure and discharge temperature. Inspect the actual modeled trip when it occurs; a pressure rise alone does not complete the exercise.';}
  else if(a.exercise==='load'){text='Advance simulated time. Watch the room-temperature response for the required 30 seconds after the 20 kW load change.';}
  else if(a.exercise==='restriction'){text='Advance 10 simulated seconds. Compare the 2% command with actual valve opening and reduced feed flow. Longer starvation can cause a real modeled trip.';}
  else if(a.exercise==='tuning'){text='Advance simulated time and watch actual and sensed outlet superheat. The engine needs the new band held for 20 consecutive seconds, at least 30 seconds after the change.';}
  else {text='Advance simulated time and observe feed and compressor demand. A brief target crossing is not enough: actual and sensed superheat must remain in the required band.';}
  if(a!==presentedAttempt){library.open=!a;presentedAttempt=a;}
 $('training-next-text').textContent=text;nextControl=target;$('training-next-control').hidden=!target;$('training-next-control').textContent=target==='training-answer'?'Go to reflection':target==='training-export'?'Go to evidence export':'Go to '+(target==='training-load'?'Load exercise':target==='training-disturbance'?'disturbance':target==='training-restore'?'restore controls':target==='training-clear'?'clear stop':'Advance');
  const samples=(!active()&&savedReport?savedReport.history:plant?.history)?.samples||[],p=samples[samples.length-1],f=(v,n=2)=>Number.isFinite(v)?v.toFixed(n):'unavailable';
  $('training-observations').textContent=a&&p?(active()?'Accepted attempt readings · ':'Retained attempt readings · ')+f(p.seconds,1)+' s · condenser '+f(p.pressures.condenser)+' bar(a) · actual / sensed SH '+f(p.actualSuperheat)+' / '+f(p.sensedSuperheat)+' K · feed '+f(p.feedMassFlow,4)+' kg/s · opening '+f(p.opening*100)+'%':'';
  document.dispatchEvent(new CustomEvent('ammonia-training-presentation',{detail:a?d.name+' · '+a.status+' · '+a.goals.filter(g=>g.met).length+'/'+a.goals.length+' objectives':''}));
 }

 function evidenceText(e){
  const labels={feedKgS:['Feed','kg/s'],baselineFeedKgS:['Baseline feed','kg/s'],gainKW:['Room load','kW'],roomC:['Room','°C'],baselineRoomC:['Baseline room','°C'],command:['Command','fraction'],opening:['Opening','fraction'],targetK:['Target SH','K'],actualSuperheatK:['Actual SH','K'],sensedSuperheatK:['Sensed SH','K'],condenserBar:['Condenser','bar(a)'],baselineBar:['Baseline condenser','bar(a)'],ambientC:['Condenser air','°C'],holdSince:['Band held since','s']};
  return Object.entries(e).flatMap(([key,v])=>{
   if(labels[key]){const [label,unit]=labels[key];return label+' '+Number(v).toFixed(3)+' '+unit;}
   if(key==='fault')return 'Equipment trip · '+v.message;
   if(key==='compressorEnabled')return 'Compressor '+(v?'enabled':'disabled');
   if(key==='answerIndex')return 'Correct reflection recorded';
   if(key==='source')return v;
   return [];
  }).join(' · ');
 }
 function description(){const selected=$('training-select').value,d=T.EXERCISES[selected];$('training-selected-title').textContent='Selected lesson · '+d.name;$('training-description').textContent=d.description;const different=!!attempt&&attempt.exercise!==selected;$('training-selection-note').hidden=!different;$('training-selection-note').textContent='Load exercise starts the selected lesson and replaces the retained attempt. Export the retained attempt first to keep its evidence.';}
 function render(){
  description();const id=attempt?.exercise||$('training-select').value,d=T.EXERCISES[id];guidance(d);$('training-attempt-title').textContent=attempt?(active()?'Current attempt · ':'Retained attempt · ')+d.name:'Lesson objectives · '+d.name;
  $('training-reset').textContent=attempt&&!active()?'Reset retained attempt':'Reset exercise';$('training-export').textContent=attempt&&!active()?'Export retained attempt · JSON':'Export attempt · JSON';$('training-select').disabled=active();$('training-load').disabled=!adapter.defaultActive();$('training-reset').disabled=!attempt||!adapter.defaultActive();$('training-end').disabled=!active();$('training-export').disabled=!attempt;
  $('training-advance').disabled=!active()||!!plant?.fault;$('training-run').disabled=!active()||!!plant?.fault;$('training-run').textContent=adapter.isRunning()?'Pause exercise playback':'Start exercise playback';$('training-clear').hidden=attempt?.exercise!=='hot'||!attempt.expectedFault;$('training-clear').disabled=!active()||!attempt.restored||!plant?.fault;
  $('training-check').disabled=!active();$('training-disturbance').hidden=!d.action||!attempt;$('training-disturbance').textContent=d.action||'Apply disturbance';$('training-disturbance').disabled=!active()||attempt.injectedAt!==null;
  $('training-restore').hidden=id!=='hot'||!attempt;$('training-restore').disabled=!active()||!attempt.expectedFault||attempt.restored;
  $('training-status').textContent=!adapter.defaultActive()?'Apply Default equipment before loading a supported exercise.':!attempt?'Choose an exercise and load its setup.':({active:'In progress',completed:'Objectives completed',stopped:'Stopped before completion',interrupted:'Exercise interrupted'})[attempt.status]+' · '+d.name+' · '+attempt.goals.filter(g=>g.met).length+'/'+attempt.goals.length+' objectives · began at '+attempt.startedAt.toFixed(3)+' simulated seconds'+(attempt.reason?' · '+attempt.reason:'');
  $('training-objectives').innerHTML=attempt?attempt.goals.map(g=>'<li class="'+(g.met?'met':'')+'">'+(g.met?'✓ ':'○ ')+esc(g.label)+(g.evidence?' <small>Recorded evidence · '+g.evidence.seconds.toFixed(3)+' s · '+esc(evidenceText(g.evidence))+'</small>':' <small>Awaiting graded evidence</small>')+'</li>').join(''):d.goals.map(g=>'<li>'+esc(g)+'</li>').join('');
  $('training-hint-text').textContent=d.hint;$('training-hint-text').hidden=!hint;$('training-hint').setAttribute('aria-expanded',String(hint));$('training-hint').textContent=hint?'Hide hint':'Show hint';
  $('training-question').textContent=d.question;
  if($('training-answer').dataset.exercise!==id){$('training-answer').dataset.exercise=id;$('training-answer').innerHTML='<option value="">Select an answer</option>'+d.answers.map((label,i)=>'<option value="'+i+'">'+esc(label)+'</option>').join('');$('training-feedback').textContent='';}
  $('training-debrief').hidden=!attempt||active();if(attempt&&!active())$('training-debrief').innerHTML='<h4>Debrief · '+esc(d.name)+'</h4><p class="text">'+esc(d.debrief)+'</p><p class="text">'+esc(attempt.status==='completed'?'Measured objectives and reflection were met.':attempt.reason||'The attempt ended before all objectives were met.')+'</p><p class="hint">The exported attempt links objective evidence to SI observations and original stop events. Exercise completion does not establish measured plant accuracy.</p>';
 }
 function finalize(){if(!attempt||active())return;if(lastStatus===attempt.status)return;lastStatus=attempt.status;if(plant)adapter.event(plant,'Exercise '+attempt.status,{exercise:attempt.exercise,reason:attempt.reason,endedAt:attempt.endedAt});adapter.pause('Exercise '+attempt.status);if(plant)savedReport=T.report(attempt,plant);}
 function load(id){
  try{
   if(!adapter.defaultActive())throw Error('Apply Default equipment before loading this exercise.');
   adapter.pause('Loading exercise');attempt=null;plant=adapter.load(T.setup(id));attempt=T.start(id,plant);savedReport=null;lastStatus=null;hint=false;$('training-answer').dataset.exercise='';$('training-feedback').textContent='';$('training-error').hidden=true;adapter.event(plant,'Exercise loaded',{exercise:id,warmupSeconds:T.EXERCISES[id].warmup});render();adapter.refresh();
  }catch(e){$('training-error').textContent=e.message;$('training-error').hidden=false;render();}
 }
 $('training-load').addEventListener('click',()=>load($('training-select').value));$('training-reset').addEventListener('click',()=>load(attempt.exercise));
 $('training-select').addEventListener('change',()=>{description();render();});
 $('training-end').addEventListener('click',()=>{if(!active())return;T.finish(attempt,'interrupted',plant.time,'Ended by learner.');finalize();render();});
 $('training-disturbance').addEventListener('click',()=>{try{const d=T.EXERCISES[attempt.exercise];adapter.pause('Applying exercise disturbance');adapter.apply(d.operations,d.boundary);T.injected(attempt,plant);adapter.event(plant,'Exercise disturbance applied',{exercise:attempt.exercise});update(plant);adapter.refresh();}catch(e){$('training-error').textContent=e.message;$('training-error').hidden=false;}});
 $('training-restore').addEventListener('click',()=>{try{adapter.pause('Restoring off-state controls');adapter.apply({compressorOn:false,valveMode:'closed'},{ambient:25});T.restored(attempt,plant);adapter.event(plant,'Exercise off-state controls restored',{exercise:attempt.exercise});update(plant);adapter.refresh();}catch(e){$('training-error').textContent=e.message;$('training-error').hidden=false;}});
 $('training-advance').addEventListener('click',()=>adapter.advance());$('training-run').addEventListener('click',()=>adapter.toggleRun());$('training-clear').addEventListener('click',()=>adapter.clearStop());
 $('training-hint').addEventListener('click',()=>{hint=!hint;render();});
 $('training-check').addEventListener('click',()=>{try{if(!$('training-answer').value)throw Error('Select a reflection answer.');const correct=T.answer(attempt,Number($('training-answer').value),plant.time);$('training-feedback').textContent=correct?'Correct. Measured objectives must also be met.':'Try again; inspect the evidence and hint.';adapter.event(plant,'Exercise reflection checked',{exercise:attempt.exercise,correct});update(plant);adapter.refresh();$('training-error').hidden=true;}catch(e){$('training-error').textContent=e.message;$('training-error').hidden=false;}});
 $('training-export').addEventListener('click',()=>{if(!attempt)return;const report=savedReport||T.report(attempt,plant),url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='ammonia-training-'+attempt.exercise+'-v050.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 function acceptBoundary(s){if(active()&&s===plant)T.observe(attempt,s);return active();}
 function update(s){if(s===plant){if(active())T.observe(attempt,s);finalize();}render();}
 function interrupt(reason){if(active()){T.finish(attempt,'interrupted',plant.time,reason);finalize();}render();}
 description();render();return {update,interrupt,isActive:active,acceptBoundary};
}
root.AmmoniaTrainingApp={create};
})(typeof globalThis!=='undefined'?globalThis:this);
