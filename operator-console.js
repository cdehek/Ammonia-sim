/* Workstation presentation only. Move existing nodes; never clone model controls. */
(function(){
'use strict';
const $=id=>document.getElementById(id),live=$('view-live');
const consolePanel=document.createElement('section');
consolePanel.id='operator-console';consolePanel.dataset.size='collapsed';
consolePanel.setAttribute('aria-label','Operator Console');
consolePanel.innerHTML='<div class="console-bar"><button class="btn" id="console-open" aria-expanded="false" aria-controls="console-body">Open console ↑</button><span id="console-task" class="console-task"></span><span class="console-spacer"></span><button class="btn" id="console-expand" aria-controls="console-body" hidden>Expand ↑</button><button class="btn" id="console-collapse" hidden>Collapse ↓</button><button class="btn" id="console-close" hidden aria-label="Close Operator Console">Close ×</button></div><div id="console-tools"></div><div id="console-body" hidden><h2 id="console-title" tabindex="-1">Guided Exercises</h2><div id="console-content"></div></div>';
live.append(consolePanel);
const form=$('storage-form'),process=form.querySelector('.plant-process');
form.before(process);
const room=document.createElement('div');
room.append($('independent-room'),$('independent-trends'),$('live-balance').closest('.two-col'));
const tools={
 'storage-training':[$('storage-training'),'Guided Exercises'],
 'storage-form':[form,'Plant Controls'],
 'storage-trends':[$('storage-trends'),'Trends & History'],
 'plant-diagnostics':[$('plant-diagnostics'),'Inventory'],
 'equipment-profiles':[$('equipment-profiles'),'Equipment Profiles'],
 'operator-assist':[$('operator-assist'),'Operator Assist'],
 'independent-room':[room,'Independent Room Model']
};
let selected='storage-training',size='collapsed',returnFocus=$('console-open');
const nav=live.querySelector('.plant-nav');
$('console-tools').append(nav);
// Keep the existing seven section links and add the existing Assist launcher.
nav.querySelector('[href="#storage-training"]').before(nav.querySelector('[href="#storage-form"]'));
nav.prepend(nav.querySelector('[href="#storage-training"]'));
nav.append($('operator-assist-toggle'));
for(const [id,[node]] of Object.entries(tools)){node.dataset.consoleTool=id;$('console-content').append(node);}
function render(){
 consolePanel.dataset.size=size;
 $('console-body').hidden=size==='collapsed';
 $('console-open').setAttribute('aria-expanded',String(size!=='collapsed'));
 $('console-open').textContent=size==='collapsed'?'Open console ↑':'Operator Console';
 $('console-expand').hidden=size==='expanded'||size==='collapsed';
 $('console-collapse').hidden=size==='collapsed';
 $('console-collapse').textContent=size==='expanded'?'Partial height ↓':'Collapse ↓';
 $('console-close').hidden=size==='collapsed';
 $('console-title').textContent=tools[selected][1];
 for(const [id,[node]] of Object.entries(tools))node.hidden=id!==selected;
 nav.querySelectorAll('a').forEach(a=>{const active=a.hash.slice(1)===selected&&size!=='collapsed';a.setAttribute('aria-current',active?'true':'false');});
 document.body.classList.toggle('console-visible',size!=='collapsed');
 document.body.classList.toggle('console-expanded',size==='expanded');
 // Assist remains the same read-only projection and keeps its own keyboard handling.
 document.dispatchEvent(new CustomEvent('ammonia-console-change',{detail:{tool:selected,open:size!=='collapsed'}}));
 requestAnimationFrame(measure);
}
function measure(){
 const root=document.documentElement;
 const viewport=window.visualViewport;
 root.style.setProperty('--console-viewport-height',(viewport?.height||window.innerHeight)+'px');
 root.style.setProperty('--console-keyboard-inset',Math.max(0,window.innerHeight-(viewport?.height||window.innerHeight)-(viewport?.offsetTop||0))+'px');
 root.style.setProperty('--console-height',consolePanel.getBoundingClientRect().height+'px');
 const heading=$('storage-lab').querySelector('.plant-heading');
 root.style.setProperty('--console-ceiling',Math.max(140,heading.getBoundingClientRect().bottom+8)+'px');
}
function open(id,trigger){
 if(!tools[id]){close();$('storage-lab').setAttribute('tabindex','-1');$('storage-lab').focus({preventScroll:true});$('storage-lab').scrollIntoView({block:'start'});return;}
 returnFocus=trigger||$('console-open');selected=id;if(size==='collapsed')size='partial';render();
 if(id!=='operator-assist')$('console-title').focus({preventScroll:true});
}
function close(){const restore=consolePanel.contains(document.activeElement);size='collapsed';render();if(restore)returnFocus.focus({preventScroll:true});}
nav.addEventListener('click',e=>{const link=e.target.closest('a');if(!link)return;e.preventDefault();e.stopImmediatePropagation();const id=link.hash.slice(1);open(id,link);if(id!=='storage-lab'){const target=$(id);target.setAttribute('tabindex','-1');target.focus({preventScroll:true});}},true);
$('console-open').addEventListener('click',()=>{if(size==='collapsed')open(selected,$('console-open'));});
$('console-expand').addEventListener('click',()=>{size='expanded';render();$('console-collapse').focus({preventScroll:true});});
$('console-collapse').addEventListener('click',()=>{if(size==='expanded'){size='partial';render();}else close();});
$('console-close').addEventListener('click',close);
consolePanel.addEventListener('keydown',e=>{if(e.key==='Escape'&&!e.defaultPrevented){e.preventDefault();if(size==='expanded'){size='partial';render();$('console-collapse').focus({preventScroll:true});}else close();}});
document.addEventListener('ammonia-assist-open',e=>{if(e.detail.open)open('operator-assist',$('operator-assist-toggle'));else if(selected==='operator-assist'&&size!=='collapsed')close();});
document.addEventListener('ammonia-training-presentation',e=>{$('console-task').textContent=e.detail;measure();});
new ResizeObserver(measure).observe(consolePanel);
new ResizeObserver(measure).observe($('storage-lab').querySelector('.plant-heading'));
window.addEventListener('resize',measure);
window.addEventListener('scroll',measure,{passive:true});
window.visualViewport?.addEventListener('resize',measure);
window.visualViewport?.addEventListener('scroll',measure);
render();
})();
