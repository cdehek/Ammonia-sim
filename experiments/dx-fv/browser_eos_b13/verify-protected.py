"""Compare recorded read-only remote snapshots. Never mutates a ref or PR."""
import argparse,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2]
OWN='refs/heads/research/b13-dx-fv-horizon-diagnostics-20261019'
def refs(n):return {row.split()[1]:row.split()[0] for row in (E/n).read_text().splitlines() if row.strip()}
ap=argparse.ArgumentParser();ap.add_argument('--published',action='store_true');ap.add_argument('--after',default='evidence/remote-refs-after.txt');ap.add_argument('--pr-after',default='evidence/pr3-after.json');a=ap.parse_args()
before,after=refs('remote-refs-before.txt'),refs(str((B/a.after).resolve()))
assert OWN not in before,'B13 was not a new remote branch'
assert {k:v for k,v in after.items() if k!=OWN}==before,'Protected remote head/tag changed'
assert after['refs/heads/research/b12-private-https-ipad-preview-20261019']=='e6779247eec9a39350a39551eec1740f06097aeb'
keys=['number','state','merged','draft','base','base_sha','head','head_sha','head_repo_full_name']
x=json.loads((E/'pr3-before.json').read_text());y=json.loads((B/a.pr_after).read_text())
assert {k:x[k] for k in keys}=={k:y[k] for k in keys},'PR3 identity changed'
local=refs('local-refs-before.txt');current=dict(row.split()[::-1] for row in subprocess.check_output(['git','show-ref'],cwd=R).decode().splitlines())
assert all(current.get(k)==v for k,v in local.items() if k not in [OWN,'refs/remotes/origin/research/b13-dx-fv-horizon-diagnostics-20261019']), 'Protected local ref changed'
if a.published:assert after[OWN]==subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
receipt=dict(passed=True,protectedRemoteRefs=len(before),protectedLocalRefs=len(local)-1,pr3IdentitiesUnchanged=True,b12Unchanged=True,onlyPermittedRemoteAddition=OWN,publishedHeadChecked=a.published,snapshotB13Head=after.get(OWN),scope='Read-only recorded snapshots; current final HEAD equality is checked with --published after the push')
# Avoid modifying the committed prepublication receipt during final clean-tree verification.
if not a.published:(E/'protected-ref-pr3-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
