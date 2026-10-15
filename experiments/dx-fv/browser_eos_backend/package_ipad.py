"""Build an isolated local artifact; never publish or alter application assets."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2]
evidence_path=B/'evidence'/(sys.argv[2] if len(sys.argv)>2 else 'ipad-package.json')
assert not evidence_path.exists(),'Retain existing package evidence; supply a new manifest filename as the second argument'
out=Path(sys.argv[1]).resolve();assert not out.exists(),'Use a new output directory'
page=out/'experiments/dx-fv/browser_eos_backend';page.mkdir(parents=True)
files=[B/n for n in ['index.html','app.mjs','worker.mjs','loader.mjs','workloads.mjs','sw.js']]
files+=list((B/'vendor').rglob('*'))
old=B.parent/'browser_eos'
files+=list((old/'vendor').rglob('*'))+[old/'inputs.json',B.parent/'browser_eos_precision/inputs.json',B.parent/'browser_eos_precision/diagnostic.mjs']
manifest={}
for p in files:
 if not p.is_file():continue
 rel=p.relative_to(R);dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 import os
 manifest[os.path.relpath(dest,page)]=hashlib.sha256(dest.read_bytes()).hexdigest()
(page/'offline-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'README.txt').write_text('Experimental Ammonia B1. Serve over trusted HTTPS for physical iPad offline tests. Open /experiments/dx-fv/browser_eos_backend/. No application integration or publication. See repository IPAD_TEST_INSTRUCTIONS.md.\n')
archive=out.with_suffix('.zip');assert not archive.exists()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():
   info=zipfile.ZipInfo(str(p.relative_to(out)),date_time=(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compresslevel=9)
evidence={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
 'page':'experiments/dx-fv/browser_eos_backend/','assets':manifest,'physicalIPadTested':False}
evidence_path.write_text(json.dumps(evidence,indent=2)+'\n');print(archive,evidence['bytes'],evidence['sha256'])
