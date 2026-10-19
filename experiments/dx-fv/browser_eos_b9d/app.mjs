import {Client} from './client.mjs';
import {render} from './view.mjs';
import {INTERVALS} from './snapshot.mjs';
const $=id=>document.getElementById(id);let client=null,step=0,generation=0,initializing=false;
const metrics={renders:[],heartbeat:[],frames:[],input:[]};let lastBeat=performance.now(),lastFrame=null,frame;
const beat=setInterval(()=>{const t=performance.now();metrics.heartbeat.push(t-lastBeat);lastBeat=t;},10);
function tick(t){if(lastFrame!==null)metrics.frames.push(t-lastFrame);lastFrame=t;frame=requestAnimationFrame(tick);}frame=requestAnimationFrame(tick);
function update(v){const t=performance.now();render(v,document);metrics.renders.push(performance.now()-t);$('advance').disabled=!client||client.closed||client.pending.size>0||step>=3||!!v.fault||['scheduling-stopped','disposed'].includes(v.status);$('advance').textContent=step<3?'Advance '+INTERVALS[step]+' s':'Bounded horizon complete';}
async function initialize(fixture){if(initializing)throw Error('Initialization already pending');initializing=true;$('cold').disabled=$('warm').disabled=true;try{const id=++generation;if(client&&!client.closed)await client.dispose();step=0;client=new Client(v=>{if(id===generation)update(v);});window.shadow.client=client;update(client.view);return await client.request('initialize',{fixture});}finally{initializing=false;$('cold').disabled=$('warm').disabled=false;}}
async function action(type){if(!client)throw Error('Initialize cold or warm first');if(type==='advance'){step++;const r=await client.request(type);update(client.view);return r;}if(type==='dispose')return client.dispose();const r=await client.request(type);if(type==='diagnostics')$('diagnostics').textContent=JSON.stringify(r.result||r.error,null,2);return r;}
for(const id of ['cold','warm','advance','latest','diagnostics-button','stop','dispose'])$(id).addEventListener('click',async e=>{metrics.input.push({id,trusted:e.isTrusted,ackMS:performance.now()-e.timeStamp});try{if(id==='cold'||id==='warm')await initialize(id);else await action(id==='diagnostics-button'?'diagnostics':id);}catch(error){$('operation-error').textContent=error.message;}});
window.shadow={get client(){return client;},set client(v){client=v;},metrics,initialize,action,update};
window.addEventListener('pagehide',()=>{clearInterval(beat);cancelAnimationFrame(frame);client?.lose('View disposed');},{once:true});
$('status').textContent='Ready to initialize · no computed readings yet';
