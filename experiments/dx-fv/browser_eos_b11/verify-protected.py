"""Protected remote refs / PR identity. --live is read-only and checks published B11 HEAD."""
import argparse,json,subprocess
from audit import B,R,git
ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');args=ap.parse_args();E=B/'evidence'
def refs(text):return dict(line.split()[::-1] for line in text.splitlines() if line.strip())
before=refs((E/'remote-refs-before.txt').read_text());own='refs/heads/research/b11-portable-ipad-preview-20261019'
after=refs(git('ls-remote','--heads','--tags','origin').decode() if args.live else (E/'remote-refs-after.txt').read_text())
assert {k:v for k,v in after.items() if k!=own}=={k:v for k,v in before.items() if k!=own},'Protected remote ref changed'
assert own not in before,'B11 was not a new remote branch at start'
if args.live:assert after[own]==git('rev-parse','HEAD').decode().strip(),'Remote B11 does not equal local HEAD'
a=json.loads((E/'pr3-before.json').read_text());b=json.loads((E/'pr3-after.json').read_text());keys=['number','state','merged','base','base_sha','head','head_sha','head_repo_full_name','draft']
assert {k:a[k] for k in keys}=={k:b[k] for k in keys},'PR #3 identity/status changed'
receipt={'passed':True,'remoteProtectedRefsAndTagsUnchanged':True,'B11WasNewBranch':True,'onlyAllowedRemoteChange':own,'PR3':{k:b[k] for k in keys},'noPR3MutationPerformed':True,'workflowInspection':'Existing push workflows target main and experimental/dx-fv-stage-3, not B11; no workflow or hosting configuration changed','remoteHostingActionPerformed':False,'productionMerge':'NO-GO','fullLivePlantCoupling':'NO-GO'}
if not args.live:(E/'protected-refs-pr3.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: all protected remote heads/tags and recorded PR #3 identity;'+(' published B11 equals HEAD' if args.live else ' only B11 remote change permitted'))
