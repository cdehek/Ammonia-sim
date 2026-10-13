"""Build a self-contained ZIP outside the repo, preserving official asset hashes."""
import json,hashlib,shutil,sys,zipfile
from pathlib import Path
B=Path(__file__).resolve().parent;OLD=B.parent/'browser_eos'
DEST=Path(sys.argv[1]).resolve();assert not DEST.exists(),'Choose a new output directory; preserve completed packages'
DEST.mkdir(parents=True)
for f in (B/'ipad').iterdir():
 if f.is_file():shutil.copy2(f,DEST/f.name)
for source,name in [(OLD/'eos.mjs','eos.mjs'),(B/'diagnostic.mjs','diagnostic.mjs'),(B/'inputs.json','inputs.json')]:shutil.copy2(source,DEST/name)
for version,jsSHA,wasmSHA in [('8.0.0','ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217','28a83d839ab69c7e6ea480298955ce223b6507dc6ffb83349dd31f1540867307'),('7.2.0','8a4993ac260a98c4a7053c9f42bbb58bc0fb2ebd3411c8d13df7bbb1fc511b2b','cb77d0381fbe639bffb65a3e8fa44ff8e2a110f21c18125c89a9b336135bd194')]:
 shutil.copytree(OLD/'vendor'/version,DEST/'vendor'/version)
 for name,expected in [('coolprop.js',jsSHA),('coolprop.wasm',wasmSHA)]:assert hashlib.sha256((DEST/'vendor'/version/name).read_bytes()).hexdigest()==expected
shutil.copytree(OLD/'vendor/notices',DEST/'vendor/notices')
if (B/'IPAD_TEST_INSTRUCTIONS.md').exists():shutil.copy2(B/'IPAD_TEST_INSTRUCTIONS.md',DEST/'IPAD_TEST_INSTRUCTIONS.md')
assets={str(p.relative_to(DEST)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(DEST.rglob('*')) if p.is_file()}
runtime=['index.html','app.mjs','worker.mjs','sw.js','eos.mjs','diagnostic.mjs','inputs.json']+[f'vendor/{v}/coolprop.{ext}' for v in ['8.0.0','7.2.0'] for ext in ['js','wasm']]
manifest={'experimental':True,'physicalIPadQualification':False,'versions':['8.0.0','7.2.0'],'assets':assets,'runtimeAssets':runtime};(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=DEST.with_suffix('.zip');assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(DEST.rglob('*')):
  if p.is_file():
   info=zipfile.ZipInfo(str(p.relative_to(DEST)),date_time=(2026,10,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
metadata={'archiveBytes':archive.stat().st_size,'archiveSHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifest':manifest,'note':'Generated package outside Git; local static server only. No publishing.'}
(DEST.with_suffix('.metadata.json')).write_text(json.dumps(metadata,indent=2)+'\n');print(archive,archive.stat().st_size,'bytes')
