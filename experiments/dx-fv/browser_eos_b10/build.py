"""Exact pinned workstation plus isolated console presentation; B10 outputs only."""
import hashlib,json,re,subprocess,tarfile,io,difflib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';OP='262b6092b2ed694073ad9ffd41265f44dd0b6ca0'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(v):return hashlib.sha256(v).hexdigest()
historical=json.loads((E/'starting-files-sha256.json').read_text())
assert all(sha((R/p).read_bytes())==v for p,v in historical.items()),'Historical input changed'
assert sha((B.parent/'browser_eos_b9c/candidate-bundle.mjs').read_bytes())=='f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919'
manifest=json.loads((E/'operator-source-manifest.json').read_text())
archive=git('archive',OP);source=B/'.runtime/build-source';source.mkdir(parents=True,exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(source,filter='data')
assert all(sha((source/p).read_bytes())==v['sha256'] for p,v in manifest.items())
receipt=subprocess.check_output(['python3',str(source/'tools/build.py'),str(source/'dist')])
original=git('show',OP+':index.html');assert (source/'index.html').read_bytes()==original
(E/'reproduced-build.log').write_bytes(receipt)
(B/'artifacts').mkdir(exist_ok=True);(B/'artifacts/pinned-workstation.html').write_bytes(original)
console=git('show',OP+':operator-console.js').decode();entry=" 'b10-a2-shadow':[$('b10-a2-shadow'),'A2 — Five-Section Evaporator Research'],\n"
assert console.count('const tools={\n')==1
changed=console.replace('const tools={\n','const tools={\n'+entry)
prepare="""<script data-b10="mount">
(()=>{const node=document.createElement('section');node.id='b10-a2-shadow';node.setAttribute('aria-label','A2 — Five-Section Evaporator Research');node.innerHTML='<p>A2 — Five-Section Evaporator Research · not initialized. Local HTTP-served research only.</p>';document.getElementById('view-live').append(node);const link=document.createElement('a');link.href='#b10-a2-shadow';link.id='b10-a2-link';link.textContent='A2 Evaporator Research';document.querySelector('.plant-nav').append(link);})();
</script>"""
bootstrap="""<script data-b10="bootstrap">
(()=>{let loading=false;async function open(event){if(event.detail.tool!=='b10-a2-shadow'||!event.detail.open||loading)return;loading=true;const host=document.getElementById('b10-a2-shadow');try{const module=await import('/experiments/dx-fv/browser_eos_b10/panel.mjs');await module.mount(host);document.removeEventListener('ammonia-console-change',open);}catch(error){host.textContent='A2 scientific panel unavailable · '+error.message+' · use local HTTP serving. Original workstation remains available.';loading=false;}}document.addEventListener('ammonia-console-change',open);})();
</script>"""
text=original.decode();anchor='<script>'+console+'</script>';assert text.count(anchor)==1 and text.count('</body>')==1
text=text.replace(anchor,prepare+'<script>'+changed+'</script>').replace('</body>',bootstrap+'</body>')
reverse=text.replace(bootstrap,'').replace(prepare+'<script>'+changed+'</script>',anchor)
assert reverse.encode()==original
(B/'index.html').write_text(text)
# Reuse the small B9D transport adapters, preserving numerical call order literally.
changes={}
for name in ['service.mjs','client.mjs','worker.mjs']:
 old=(B.parent/'browser_eos_b9d'/name).read_text();new=old
 if name=='service.mjs':
  new=new.replace('trackedSteps=0;','trackedSteps=0,lastAdvanceRange=null;')
  new=new.replace('({protocol:1,backendId:BACKEND,sessionId,','({protocol:1,backendId:BACKEND,source:{...SOURCE},requestRange:structuredClone(lastAdvanceRange),sessionId,')
  new=new.replace('scientific=true;let t=performance.now();',"lastAdvanceRange={startSeconds:state.seconds,intervalSeconds:INTERVALS[step],targetSeconds:state.seconds+INTERVALS[step]};\n    scientific=true;let t=performance.now();")
 if name=='client.mjs':
  new=new.replace("import {BACKEND}","import {BACKEND,SOURCE}")
  new=new.replace("this.clockSeconds=null;","this.clockSeconds=null;this.failureRange=null;this.currentStateKnown=true;")
  new=new.replace("if(!r.success){this.stale", "if(!r.success){this.failureRange=r.requestRange;this.stale")
  new=new.replace("this.snapshot=r.snapshot;this.stale=false;", "this.snapshot=r.snapshot;this.failureRange=null;this.stale=false;")
  new=new.replace(" receive(r){\n  const p=", " receive(r){\n  if(!r.source||Object.keys(SOURCE).some(k=>r.source[k]!==SOURCE[k])){this.lose('Scientific source identity mismatch');return false;}\n  const p=")
  new=new.replace("this.view.receive(r);", "if(this.metrics.length>512)this.metrics.shift();this.view.receive(r);")
  new=new.replace("this.view.status='lost';", "this.view.status='lost';this.view.currentStateKnown=false;")
 (B/name).write_text(new)
 changes[name]={'originalSHA256':sha(old.encode()),'B10SHA256':sha(new.encode()),'diff':''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='B9D/'+name,tofile='B10/'+name))}
(E/'bridge-adapter-diff.json').write_text(json.dumps(changes,indent=2)+'\n')
(B/'isolated').mkdir(exist_ok=True)
mechanical=git('show','b67afb3215075b2ec82bef376d39e03953dc0da2:experiments/dx-fv/browser_eos_b9c/isolated/coupled-model.cjs')
(B/'isolated/coupled-model.cjs').write_bytes(mechanical)
result={'pinnedCommit':OP,'allPinnedInputsVerified':len(manifest),'originalBytes':len(original),'originalSHA256':sha(original),'derivedBytes':len(text.encode()),'derivedSHA256':sha(text.encode()),'reversibleToExactOriginal':True,'existingFunctionBodiesUnchanged':True,'consoleRegistryEntriesAdded':1,'iframe':False,'lazyScientificImport':True,'sourceHashManifest':'operator-source-manifest.json','scientificBundleSHA256':sha((B.parent/'browser_eos_b9c/candidate-bundle.mjs').read_bytes())}
(E/'build-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
