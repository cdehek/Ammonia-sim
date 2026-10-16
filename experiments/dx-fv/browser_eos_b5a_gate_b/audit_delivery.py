"""Fail closed on any historical/source/remote change before research commit."""
import hashlib,json,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
branch='research/browser-eos-b5a-gate-b-feasibility-20261016'
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()==branch
baseline=json.loads((E/'starting-file-hashes.json').read_text())
changed=[n for n,h in baseline.items()if not(R/n).is_file()or sha(R/n)!=h];assert not changed,changed
source=Path('/workspace/coolprop-b5');expected=json.loads((B.parent/'browser_eos_b5a/evidence/source-stage-A1.json').read_text())['trackedSourceSHA256']
bad=[n for n,h in expected.items()if sha(source/n)!=h];assert not bad,bad
def refs(p):return {ln.split()[1]:ln.split()[0]for ln in p.read_text().splitlines()}
before=refs(E/'refs-before.txt');after=refs(E/'refs-before-commit.txt')
remoteChanges={n:dict(before=h,after=after.get(n))for n,h in before.items()if n!='refs/heads/'+branch and after.get(n)!=h};assert not remoteChanges,remoteChanges
checkpoints=['be9eb35a4ddf5098e685182f8104685127c6a6ee','ef1562ae1680fccf3323391e9ec83788c5ae1e69','6a220dd6c94bff08e00e0107cfec71854166ede2','4e1295be9493d8bce4ca35ee0cf61accb7465226','94f77bb062b75ffebf17a1c9758d11c1adc61711','d0d11d59756c4dc32bbfdb22a5975fd6f4527e05','3622000309cacdd35aaaebbb805ae40d27c75603','e30ad9d76bc892aa355126339997d6184c8729d2','cc2ec6b54d40cabea93fa761d10a2ecab59def25','262b6092b2ed694073ad9ffd41265f44dd0b6ca0']
for h in checkpoints:assert subprocess.check_output(['git','cat-file','-t',h],cwd=R,text=True).strip()=='commit'
science=json.loads((E/'scientific-audit.json').read_text());assert science['auditPass']and not science['backendQualified']
assert len(science['originals'])==7 and len(science['neighborRows'])==47
assert {r['key']for r in science['originals']if 'NOT DEMONSTRATED'in r['B']}=={'native-ledger-'+str(n)for n in [148,162,164,165]}
scope='experiments/dx-fv/browser_eos_b5a_gate_b/'
status=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=R,text=True)
assert all(ln[3:].startswith(scope)for ln in status.splitlines()),status
assert not list(B.rglob('*.so'))and not list(B.rglob('*.wasm'))and not list(B.rglob('*.patch'))
out=dict(branch=branch,start='cc2ec6b54d40cabea93fa761d10a2ecab59def25',startingFiles=len(baseline),changedHistoricalFiles=changed,sourceFiles=len(expected),sourceMismatches=bad,protectedRefChanges=remoteChanges,immutableCheckpointObjects=checkpoints,onlyNewResearchDirectory=True,noFunctionalSourceRepair=True,acceptedContractsUnchanged=True,allFourUnresolvedRetained=True,noProductionUIOrLivePlantChanges=True,noMergeOrDeployment=True,allPass=True,remoteAuditTiming='Before research commit/push; final post-push verification is reported in delivery response')
p=E/'final-preservation.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
manifest={str(p.relative_to(B)):sha(p)for p in sorted(B.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.name!='evidence-sha256.json'}
p=E/'evidence-sha256.json';assert not p.exists();p.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(out,indent=2))
