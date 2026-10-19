"""Read-only historical files/remote/PR preservation; B9C-only receipts."""
import hashlib,json,subprocess,argparse
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
p=argparse.ArgumentParser();p.add_argument('--label',default='final');a=p.parse_args()
def git(*x):return subprocess.check_output(['git',*x],cwd=R).decode()
historical=json.loads((E/'starting-files-sha256.json').read_text())
changed=[n for n,v in historical.items() if not (R/n).exists() or hashlib.sha256((R/n).read_bytes()).hexdigest()!=v];assert not changed,changed
diff=git('diff','--name-status','ec2df3f9ee3efd7faef3d129282ad1dd7bdc896f','HEAD').splitlines();assert all(l.startswith('A\texperiments/dx-fv/browser_eos_b9c/') for l in diff)
def refs(p):return {line.split()[1]:line.split()[0] for line in p.read_text().splitlines()}
before=refs(E/'remote-before.tsv');after=refs(E/('remote-'+a.label+'.tsv'));branch='refs/heads/research/browser-eos-b9c-boundary-ph-reuse-20261018'
checkpoints=json.loads((E/'gate0.json').read_text())['canonicalCheckpoints']
assert all(v in before.values() for v in checkpoints.values()),'Canonical checkpoint lacks starting remote identity'
assert all(after.get(k)==v for k,v in before.items())
assert all(k in before or k==branch for k in after)
first=json.loads((E/'pr3-before.json').read_text());last=json.loads((E/('pr3-'+a.label+'.json')).read_text())
keys=['number','state','merged','base','base_sha','head','head_sha','merge_commit_sha','title','body'];assert all(first[k]==last[k] for k in keys)
receipt={'passed':True,'historicalFiles':len(historical),'historicalChanges':changed,'allCommittedChangesAdditiveB9C':True,'protectedRemoteRefsUnchanged':True,'PR3IdentitiesAndMetadataUnchanged':True,'PR3':{k:last[k] for k in ['base_sha','head_sha','merge_commit_sha','state','merged']},'head':git('rev-parse','HEAD').strip(),'branch':git('branch','--show-current').strip(),'remoteBranch':after.get(branch),'status':git('status','--porcelain=v1'),'label':a.label}
(E/('preservation-'+a.label+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print('Historical files, protected refs and PR #3 preservation PASS')
