"""Read-only historical verification; write receipts only in B8. Timeout: 120s."""
import hashlib, importlib.util, json, lzma, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent; R=B.parents[2]; X=B.parent; E=B/'evidence'
START='429ce020128763454324529cc1c7640cf1f474e8'
A2='be9eb35a4ddf5098e685182f8104685127c6a6ee'
BRANCH='research/browser-eos-b8-blocker-disposition-20261017'
def git(*a): return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text())
def write(n,v): (E/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert git('branch','--show-current')==BRANCH
 assert git('merge-base',START,'HEAD')==START
 if '--start' in sys.argv:
  assert git('rev-parse','HEAD')==START
  write('starting-files-sha256.json',{n:sha((R/n).read_bytes()) for n in git('ls-tree','-r','--name-only',START).splitlines()})
  write('checkpoint.json',dict(start=START,tree=git('rev-parse',START+'^{tree}'),branch=BRANCH,initialClean=True,observation='Clone clean; detached exact B7; empty porcelain before switch -c. Sandbox network clone failure retained in execution notes.'))
 starting=read(E/'starting-files-sha256.json')
 assert all(sha((R/n).read_bytes())==h for n,h in starting.items())
 spec=importlib.util.spec_from_file_location('old',X/'browser_eos_b5b/audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);prior=m.verify()
 seals={}
 for folder in ['browser_eos_b6','browser_eos_b7']:
  manifest=read(X/folder/'evidence/delivery-manifest-sha256.json')
  for n,h in manifest.items(): assert sha((X/folder/n).read_bytes())==h,n
  seals[folder]=len(manifest)
 artifacts=read(X/'browser_eos_b7/evidence/artifacts-with-diagnostics.json')
 for v in artifacts.values():
  for k in ['js','wasm']: assert sha((X/'browser_eos_b7'/v[k+'Path']).read_bytes())==v[k+'SHA256']
 native=read(X/'browser_eos_b7/evidence/native-artifact-identities.json')
 for v in native.values():
  b=(R/v['archive']).read_bytes();assert sha(b)==v['archiveSHA256'] and sha(lzma.decompress(b))==v['binarySHA256']
 c1={str(p.relative_to(R)):sha(p.read_bytes()) for p in sorted((X/'browser_eos_b5b_c1').rglob('*')) if p.is_file() and (p.suffix in ['.cjs','.mjs','.patch'] or p.name=='source-manifest.json')}
 for n,h in c1.items(): assert h==sha(subprocess.check_output(['git','show','7809d08be67eab7cb9b537b1c1199b456b2da122:'+n],cwd=R))
 accepted={}
 for n in ['engine.js','properties.json']+['experiments/dx-fv/'+r['file'] for r in prior['acceptedA2']]:
  raw=subprocess.check_output(['git','show',A2+':'+n],cwd=R)
  snapshot=R/n if '/' not in n else X/'browser_eos_backend/accepted'/Path(n).name
  assert raw==snapshot.read_bytes();accepted[n]=dict(sha256=sha(raw),snapshot=str(snapshot.relative_to(R)),rootMatches=(R/n).read_bytes()==raw)
 canonical={}
 for label,ref in [('B5A','research/browser-eos-b5a-du-saturation-repair-20261016'),('GateB','research/browser-eos-b5a-gate-b-feasibility-20261016'),('C1','research/browser-eos-b5b-c1-failclosed-propagation-20261016'),('C2','research/browser-eos-b5b-c2-inventory-certification-feasibility-20261016'),('P1','research/browser-eos-b5b-c2-p1-phase-certification-20261016'),('B6','research/browser-eos-b6-rejected-pt-loader-repair-20261016'),('B7','research/browser-eos-b7-gatea-wasm-qualification-20261017'),('UI','feature/operator-workstation-bottom-panel-20261014')]:
  canonical[label]=git('rev-parse','refs/remotes/origin/'+ref);git('cat-file','-e',canonical[label]+'^{commit}')
 assert canonical['C2']=='7c75d9538d57080a01dffbf7e06128a27e2b9ccd'
 expected={'B5A':'cc2ec6b54d40cabea93fa761d10a2ecab59def25','GateB':'14b8b386148c687fcb549d5f17003fa9e63fbca8','C1':'7809d08be67eab7cb9b537b1c1199b456b2da122','C2':'7c75d9538d57080a01dffbf7e06128a27e2b9ccd','P1':'75e015fd3455e75fa85074e8748bc01eb8973624','B6':'f6227de0760d81994c60497869f5c6013a9d403f','B7':START,'UI':'262b6092b2ed694073ad9ffd41265f44dd0b6ca0'}
 assert canonical==expected
 prBefore=read(E/'pr3-before.json');prAfter=read(E/'pr3-prepush.json') if '--final' in sys.argv else prBefore
 for key in ['base_sha','head_sha','merge_commit_sha','state','merged']:assert prBefore[key]==prAfter[key]
 assert prBefore['base_sha']=='0473d32f62db992fde0f581d116e1bd0c8e7d8ed' and prBefore['head_sha']=='d4422425750a1d3c4e432cc103ac42ead40b7cc6' and prBefore['merge_commit_sha']=='f440560fccfa45421ec2bf679bac32df10df63ae' and not prBefore['merged']
 before=dict(line.split()[::-1] for line in (E/'remote-before.tsv').read_text().splitlines())
 refpath=E/('remote-prepush.tsv' if '--final' in sys.argv else 'remote-before.tsv')
 after=dict(line.split()[::-1] for line in refpath.read_text().splitlines())
 assert before['refs/heads/main']==prBefore['base_sha'] and before['refs/pull/3/head']==prBefore['head_sha'] and before['refs/pull/3/merge']==prBefore['merge_commit_sha']
 assert all(after.get(k)==v for k,v in before.items());assert set(after)-set(before)<={'refs/heads/'+BRANCH}
 assert all(x.startswith('A\texperiments/dx-fv/browser_eos_b8/') for x in git('diff',START,'--name-status').splitlines())
 assert all('experiments/dx-fv/browser_eos_b8/' in x for x in git('status','--porcelain=v1','--untracked-files=all').splitlines())
 out=dict(start=START,historicalFiles=len(starting),historicalMismatches=[],remoteRefs=len(before),remoteDrift={},canonicalCheckpoints=canonical,acceptedA2=accepted,c1Sources=c1,B6LoaderSHA256=sha((X/'browser_eos_b6/loader.mjs').read_bytes()),sealedFiles=seals,artifacts=artifacts,native=native,inherited=prior,onlyAdditiveB8=True,noSourceChange=True)
 write('final-preservation.json' if '--final' in sys.argv else 'start-audit.json',out)
 print(json.dumps(dict(historicalFiles=len(starting),artifacts=len(prior['artifacts']),acceptedFiles=len(accepted),C2=canonical['C2'],passed=True)))
if __name__=='__main__':main()
