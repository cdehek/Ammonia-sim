"""Read-only recorded ref/PR identity comparison. --published adds live head check."""
import argparse,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2];OWN='refs/heads/research/b15-vapor-ph-bracket-reuse-20261020'
p=argparse.ArgumentParser();p.add_argument('--published',action='store_true');a=p.parse_args()
def refs(path):return{r.split()[1]:r.split()[0]for r in path.read_text().splitlines()if r.strip()}
before=refs(E/'remote-refs-before.txt');after=refs(E/'remote-refs-after.txt')
assert OWN not in before
if a.published:
 text=subprocess.check_output(['git','ls-remote','--heads','--tags','origin'],cwd=R).decode();after={r.split()[1]:r.split()[0]for r in text.splitlines()}
assert {k:v for k,v in after.items()if k!=OWN}==before,'Protected remote refs changed'
local=refs(E/'local-refs-before.txt');current={r.split()[1]:r.split()[0]for r in subprocess.check_output(['git','show-ref'],cwd=R).decode().splitlines()}
assert all(current.get(k)==v for k,v in local.items()if k!=OWN),'Protected local refs changed'
assert set(current)-set(local)<= {OWN,OWN.replace('refs/heads/','refs/remotes/origin/')},'Unexpected local ref addition'
x=json.loads((E/'pr3-before.json').read_text());y=json.loads((E/'pr3-after.json').read_text());keys=['number','state','merged','draft','base','base_sha','head','head_sha','head_repo_full_name'];assert {k:x[k]for k in keys}=={k:y[k]for k in keys}
if a.published:assert after[OWN]==subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
result=dict(passed=True,protectedRemoteHeadsAndTags=len(before),pr3IdentityUnchanged=True,historicalLocalRefsUnchanged=True,onlyPermittedRemoteAddition=OWN,publishedHeadVerified=a.published)
if not a.published:(E/'protected-ref-pr3-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
