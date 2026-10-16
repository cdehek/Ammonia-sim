"""Read-only preservation verification; --receipt explicitly writes P1 receipts.

Pass a fresh git ls-remote snapshot via --remote-refs to verify protected refs.
No fetch, branch update, network call, merge or deployment is performed here.
"""
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path

B=Path(__file__).resolve().parent
R=B.parents[2]
E=B/'evidence'
START='7c75d9538d57080a01dffbf7e06128a27e2b9ccd'
TARGET='research/browser-eos-b5b-c2-p1-phase-certification-20261016'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def refs(p):return dict(line.split()[::-1] for line in p.read_text().splitlines())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt',action='store_true')
    parser.add_argument('--remote-refs',type=Path,required=True)
    parser.add_argument('--require-clean',action='store_true')
    args=parser.parse_args()
    assert git('branch','--show-current')==TARGET
    assert git('merge-base',START,'HEAD')==START
    baseline=json.loads((E/'starting-files-sha256.json').read_text())
    assert len(baseline)==1996
    bad=[p for p,h in baseline.items() if sha(R/p)!=h]
    assert not bad,bad
    changes=git('diff',START,'--name-status').splitlines()
    assert all(x.startswith('A\texperiments/dx-fv/browser_eos_b5b_c2_p1/') for x in changes),changes
    status=git('status','--porcelain=v1','--untracked-files=all')
    if args.require_clean:assert not status,status
    assert all('experiments/dx-fv/browser_eos_b5b_c2_p1/' in x for x in status.splitlines()),status
    before,after=refs(E/'remote-refs-before.tsv'),refs(args.remote_refs)
    drift={k:[v,after.get(k)] for k,v in before.items() if after.get(k)!=v}
    assert not drift,drift
    allowed='refs/heads/'+TARGET
    assert set(after)-set(before)<={allowed}
    if allowed in after:assert after[allowed]==git('rev-parse','HEAD')
    spec=importlib.util.spec_from_file_location('inherited_audit',B.parent/'browser_eos_b5b/audit.py')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    prior=m.verify()
    assert (R/'engine.js').read_bytes()==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:engine.js'],cwd=R)
    runtime=json.loads((E/'runtime.json').read_text())
    for p,h in runtime['inheritedIdentities'].items():assert sha(R/p)==h
    for p,h in runtime['prototypeIdentities'].items():assert sha(B/p)==h
    manifest=E/'delivery-manifest-sha256.json'
    if manifest.exists() and not args.receipt:
        for p,h in json.loads(manifest.read_text()).items():assert sha(B/p)==h,p
    matrix=json.loads((E/'phase-matrix.json').read_text())
    assert matrix['classification']=='PARTIAL PHASE CERTIFICATION'
    assert len(matrix['rows'])==17 and not any(r['completePhysicalBranchCertification'] for r in matrix['rows'])
    receipt=dict(start=START,startingTree=git('rev-parse',START+'^{tree}'),historicalTrackedFilesChecked=len(baseline),
        historicalByteMismatches=bad,protectedRemoteRefsChecked=len(before),remoteRefDrift=drift,
        permittedNewRemoteRef=allowed,newRefPresent=allowed in after,
        acceptedA2Snapshots=len(prior['acceptedA2']),artifactIdentities=len(prior['artifacts']),patchDigests=len(prior['patches']),
        historicalInventoriesEOSReferenceSupportAndC1Preserved=True,acceptedEngineByteIdentical=True,
        noProductionUIOrLivePlantChanges=True,noMergeOrDeployment=True,completePhysicalCertificates=0,
        receiptScope='precommit/prepush receipt when recorded; run --require-clean with fresh refs for final read-only verification')
    if args.receipt:
        (E/'preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
        hashes={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=manifest}
        manifest.write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
