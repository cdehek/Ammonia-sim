"""Small deterministic local handoff; no scientific dependency installation."""
from pathlib import Path
import argparse,zipfile,hashlib,json
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',default='b16-owner-benchmark.zip');a=p.parse_args();out=(B/a.output).resolve();assert out.is_relative_to(B) and not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
files=['index.html','app.mjs','suite.mjs','client.mjs','worker.mjs','science.mjs','hash.mjs','serve.py','OWNER_DESKTOP_BENCHMARK.md','assets/values.mjs','assets/snapshot.mjs','assets/control-bundle.mjs','assets/candidate-bundle.mjs']
manifest={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in files}
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in files:
  i=zipfile.ZipInfo(name,date_time=(2026,10,20,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,(B/name).read_bytes())
 z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
(B/'evidence'/('desktop-package-manifest.json' if a.output=='b16-owner-benchmark.zip' else 'rebuilt-package-manifest.json')).write_text(json.dumps({'package':str(out.relative_to(B)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'files':manifest,'scope':'Local experimental performance handoff; observer/counters bundles deliberately omitted, full science suite runs from full B16 directory'},indent=2)+'\n')
print(out.name,out.stat().st_size,'bytes')
