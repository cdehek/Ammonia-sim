"""Deterministic B10 relocation only; scientific bundle remains byte-exact."""
import argparse,hashlib,json,mimetypes,subprocess,zipfile
from pathlib import Path
from audit import PINS
B=Path(__file__).resolve().parent;R=B.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def source(commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=R)
def build(out):
 out.mkdir(parents=True,exist_ok=True);assets=[]
 def put(target,commit,path,replacements=()):
  original=source(commit,path);raw=original
  for old,new,count in replacements:
   assert raw.count(old.encode())==count,(path,old)
   raw=raw.replace(old.encode(),new.encode())
  reverse=raw
  for old,new,count in reversed(replacements):reverse=reverse.replace(new.encode(),old.encode())
  assert reverse==original
  dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  mime={'.mjs':'text/javascript','.html':'text/html','.css':'text/css'}[dest.suffix]
  assets.append({'path':target,'bytes':len(raw),'sha256':sha(raw),'mime':mime,'sourceCommit':commit,'sourcePath':path,'sourceGitBlob':subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=R).decode().strip(),'sourceSHA256':sha(original),'relocations':[{'from':a,'to':b,'count':c} for a,b,c in replacements]})
 base='experiments/dx-fv/'
 put('index.html',PINS['B10'],base+'browser_eos_b10/index.html',[('/experiments/dx-fv/browser_eos_b10/panel.mjs','./panel.mjs',1)])
 for n in ['panel.mjs','panel.css','client.mjs','worker.mjs']:
  put(n,PINS['B10'],base+'browser_eos_b10/'+n)
 put('view.mjs',PINS['B10'],base+'browser_eos_b10/view.mjs',[('../browser_eos_b9d/view.mjs','./support/view.mjs',2)])
 put('support/view.mjs',PINS['B9D'],base+'browser_eos_b9d/view.mjs')
 put('snapshot.mjs',PINS['B10'],base+'browser_eos_b10/snapshot.mjs',[('../browser_eos_b9d/snapshot.mjs','./support/snapshot.mjs',2)])
 put('service.mjs',PINS['B10'],base+'browser_eos_b10/service.mjs',[('../browser_eos_b9/values.mjs','./support/values.mjs',1),('../browser_eos_b9c/candidate-bundle.mjs','./science/candidate-bundle.mjs',1)])
 put('support/snapshot.mjs',PINS['B9D'],base+'browser_eos_b9d/snapshot.mjs')
 put('support/values.mjs',PINS['B10'],base+'browser_eos_b9/values.mjs')
 put('science/candidate-bundle.mjs',PINS['B9C'],base+'browser_eos_b9c/candidate-bundle.mjs')
 assert assets[-1]['sha256']=='f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919'
 manifest={'schema':1,'build':'B11-portable-static-v1','pins':PINS,'command':'python3 experiments/dx-fv/browser_eos_b11/build.py','runtime':{'requires':['ES modules','dedicated module workers','structuredClone','crypto.randomUUID','crypto.subtle.digest','same-origin fetch'],'origin':'same-origin HTTP localhost or trusted HTTPS; LAN HTTP secure APIs unqualified','javascriptMIME':'text/javascript','externalRuntimeRequests':False,'serviceWorker':False,'scientificHorizonSeconds':.001},'assets':sorted(assets,key=lambda a:a['path'])}
 manifest['packageIdentity']=sha(canonical(manifest));(out/'asset-manifest.json').write_bytes(canonical(manifest))
 assert {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}=={a['path'] for a in assets}|{'asset-manifest.json'},'Unexpected output file; use a clean package directory'
 # Fixed timestamps, permissions, order and stored bytes avoid zlib-version dependence.
 zpath=out.parent/('preview.zip' if out==B/'preview' else out.name+'.zip')
 with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_STORED) as z:
  for p in sorted(out.rglob('*')):
   if p.is_file():
    zi=zipfile.ZipInfo('preview/'+p.relative_to(out).as_posix(),(2026,10,19,0,0,0));zi.external_attr=0o100644<<16;zi.create_system=3;z.writestr(zi,p.read_bytes())
 if out==B/'preview':
  (B/'preview.zip.sha256').write_text(sha(zpath.read_bytes())+'  preview.zip\n')
  lines=['# Complete preview asset manifest','',f"Package identity: `{manifest['packageIdentity']}`.",'','Build: `python3 experiments/dx-fv/browser_eos_b11/build.py`. Source/build mappings and every relocation are in `preview/asset-manifest.json`. No remote runtime assets. Serve JavaScript as text/javascript, HTML as text/html, CSS as text/css, JSON as application/json. Worker must be same-origin. Secure context required by unchanged B10 crypto APIs.','', '| Path | Bytes | MIME | SHA-256 |','|---|---:|---|---|']
  for a in manifest['assets']+[{'path':'asset-manifest.json','bytes':(out/'asset-manifest.json').stat().st_size,'mime':'application/json','sha256':sha((out/'asset-manifest.json').read_bytes())}]:lines.append(f"| {a['path']} | {a['bytes']} | {a['mime']} | {a['sha256']} |")
  lines+=['',f"ZIP SHA-256: `{sha(zpath.read_bytes())}`. ZIP uses fixed timestamps/order/permissions and uncompressed entries for cross-version repeatability."]
  (B/'ASSET_MANIFEST.md').write_text('\n'.join(lines)+'\n')
 print(manifest['packageIdentity'],len(assets),'assets;',sum(a['bytes'] for a in assets),'bytes; ZIP',sha(zpath.read_bytes()))
 return manifest
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=B/'preview');args=ap.parse_args();build(args.out.resolve())
