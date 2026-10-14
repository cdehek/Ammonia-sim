/* Accessible contained console: display only; update accepts an analysis projection. */
(function(root){
'use strict';
function create(container,button){
 const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let current=null,open=false,lastStatus='';
 container.innerHTML='<div class="assist-head"><div><span class="assist-kicker">Connected model / diagnostic console</span><h3 id="operator-assist-title">Operator Assist <small>v0.1</small></h3></div><button type="button" class="btn" id="operator-assist-close" aria-label="Close Operator Assist">Close ×</button></div><div id="operator-assist-content"></div><p id="operator-assist-announcement" class="assist-sr" role="status" aria-live="polite"></p>';
 const content=container.querySelector('#operator-assist-content'),announcement=container.querySelector('#operator-assist-announcement'),close=container.querySelector('#operator-assist-close');
 function render(){
  if(!current||!open)return;
  const a=current,cards=rows=>rows.map(r=>'<div class="assist-reading"><dt>'+esc(r.label)+'</dt><dd>'+esc(r.value)+'</dd><small>'+esc(r.note)+'</small></div>').join('');
  container.dataset.state=a.tone;
  content.innerHTML='<div class="assist-state"><span class="assist-indicator" aria-hidden="true"></span><strong>'+esc(a.status)+'</strong><span>'+(Number.isFinite(a.seconds)?a.seconds.toFixed(1)+' s accepted':'No accepted time')+'</span></div><div class="assist-columns"><div><h4>What is happening?</h4><p>'+esc(a.explanation)+'</p><p class="assist-compressor">'+esc(a.compressor)+'</p>'+(a.reason?'<div class="assist-stop"><span>Original recorded reason · '+esc(a.detected)+'</span><strong>'+esc(a.reason)+'</strong></div>':'')+'<p class="assist-observation">'+esc(a.observation||'Initialize before interpreting readings.')+'</p><h4>What should I inspect?</h4><p>'+esc(a.tip)+'</p></div><div><h4>'+(a.reason?'Captured stop evidence':'Accepted readings')+'</h4><dl class="assist-readings">'+cards(a.readings)+cards(a.evidence)+'</dl></div></div><footer><span>'+esc(a.scope)+'</span><span>'+esc(a.settings)+'</span></footer>';
  const status=a.status+(a.reason?' · '+a.reason:'');if(status!==lastStatus){announcement.textContent=status;lastStatus=status;}
 }
 function setOpen(value){open=value;container.hidden=!open;button.setAttribute('aria-expanded',String(open));if(open){render();close.focus({preventScroll:true});container.scrollIntoView({block:'start'});}else button.focus({preventScroll:true});}
 button.addEventListener('click',()=>setOpen(!open));close.addEventListener('click',()=>setOpen(false));
 container.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();setOpen(false);}});
 return {update(analysis){current=analysis;render();}};
}
root.AmmoniaOperatorAssistApp={create};
})(typeof globalThis!=='undefined'?globalThis:this);
