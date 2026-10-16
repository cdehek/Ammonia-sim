"""Verify inherited inputs before any native load; never rewrite historical files."""
import hashlib, json, lzma, os, platform, struct, subprocess, sys
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; X=B.parent
E=Path(os.environ.get('GATE_B_EVIDENCE',B/'evidence')); E.mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text())
def digest(b): return hashlib.sha256(b).hexdigest()
def write(n,v):
    p=E/n; assert not p.exists(),p; p.write_text(json.dumps(v,indent=2)+'\n')
S=Path('/workspace/coolprop-b5')
expected=read(X/'browser_eos_b5a/evidence/source-stage-A1.json')['trackedSourceSHA256']
bad=[n for n,h in expected.items() if digest((S/n).read_bytes())!=h]
assert not bad,bad
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip()=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
patches=[]
for n in ['browser_eos_backend/flash-44.patch','browser_eos_b4a/liquid-classification.patch','browser_eos_b4b/pt-cache-consistency.patch','browser_eos_b4c/upper-quality-classification.patch','browser_eos_b5a/gate-a.patch']:
    p=X/n; subprocess.run(['git','apply','--reverse','--check',str(p)],cwd=S,check=True)
    patches.append(dict(file=n,sha256=digest(p.read_bytes()),reverseApplicable=True))
artifacts=[]
L=Path('/workspace/gate-b-libs');L.mkdir(exist_ok=True)
for folder in ['browser_eos_b3','browser_eos_b4a','browser_eos_b4b','browser_eos_b4c','browser_eos_b5','browser_eos_b5a']:
    for label,v in read(X/folder/'evidence/native-binaries.json').items():
        p=X/folder/v['archive'];raw=p.read_bytes();binary=lzma.decompress(raw)
        assert digest(raw)==v['archiveSHA256'] and digest(binary)==v['sha256'],p
        artifacts.append(dict(file=str(p.relative_to(R)),archiveSHA256=digest(raw),binarySHA256=digest(binary)))
        if folder=='browser_eos_b5a': (L/(label+'.so')).write_bytes(binary)
for folder,manifest in [('browser_eos_backend','build-provenance.json'),('browser_eos_b4a','provenance.json'),('browser_eos_b4b','provenance.json'),('browser_eos_b4c','provenance.json')]:
    for n,v in read(X/folder/'evidence'/manifest)['artifacts'].items():
        p=X/folder/n; h=digest(p.read_bytes()); assert h==v['sha256'],p
        artifacts.append(dict(file=str(p.relative_to(R)),sha256=h))
a2=[]
for n,h in read(X/'browser_eos_b4c/evidence/accepted-a2-verification.json')['files'].items():
    raw=subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/'+n],cwd=R)
    assert digest(raw)==h==digest((X/'browser_eos_backend/accepted'/n).read_bytes()),n
    a2.append(dict(file=n,sha256=h))
ids={146,148,151,152,162,164,165}; fixed=[]
for r in read(X/'browser_eos_b5a/evidence/fixed-inputs.json'):
    if r['key'] not in {'native-ledger-'+str(i) for i in ids}:continue
    for n in ['rho','u']:
        x=struct.unpack('>d',bytes.fromhex(r['input']['bits'][n]))[0]
        assert struct.pack('>d',r['input']['values'][n]).hex()==r['input']['bits'][n]
        r['input']['values'][n]=x
    fixed.append(r)
assert len(fixed)==7
write('fixed-inputs.json',fixed)
write('start-audit.json',dict(sourceHEAD='ae81610e7d23efc57f9d051c8e70a4d66e87537f',sourceFiles=len(expected),sourceMismatches=bad,patches=patches,artifacts=artifacts,acceptedA2=a2,fluidSHA256=digest((S/'dev/fluids/Ammonia.json').read_bytes()),dependencyTrees='Not downloaded: archived verified libraries used; inherited dependency manifests preserved, no new build',python=platform.python_version(),allPass=True))
print('verified',len(expected),'source files,',len(artifacts),'artifacts,',len(a2),'A2 snapshots, seven exact inputs')
