from pathlib import Path
import json
B=Path(__file__).resolve().parent;E=B/'evidence';B16='refs/heads/research/b16-desktop-worker-performance-20261020'
def refs(name):return dict((ref,sha)for sha,ref in (line.split()for line in (E/name).read_text().splitlines()))
before=refs('initial-remote-refs.txt');after=refs('final-remote-refs.txt');assert {k:v for k,v in after.items()if k!=B16}==before,'protected remote ref changed'
a=json.loads((E/'initial-pr3.json').read_text());b=json.loads((E/'final-pr3.json').read_text())
keys=['number','state','merged','base','base_sha','head','head_sha','head_repo_full_name'];assert {k:a[k]for k in keys}=={k:b[k]for k in keys}
assert b['state']=='open' and not b['merged']
pins={'experimental/dx-fv-stage-3':'be9eb35a4ddf5098e685182f8104685127c6a6ee','research/browser-eos-b9c-boundary-ph-reuse-20261018':'b67afb3215075b2ec82bef376d39e03953dc0da2','research/browser-eos-b9d-hardening-hookup-readiness-20261018':'20ddac46423a7a742af19ac415ef8796cf3a429f','research/b10-operator-workstation-shadow-hookup-20261018':'a49c5c4ade306fe02117139cf81c30a59727a7b1','research/b11-portable-ipad-preview-20261019':'909de1579051bfadca0e282adf93eaedc0e24b9c','research/b12-private-https-ipad-preview-20261019':'e6779247eec9a39350a39551eec1740f06097aeb','research/b13-dx-fv-horizon-diagnostics-20261019':'eddb2e7add904238162ead68ef9e2c1b8874f04d','research/b14-phase-jacobian-diagnostics-20261019':'71608010fe49946dc542a4d85dff315c875274ad','research/b15-vapor-ph-bracket-reuse-20261020':'eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35'}
for ref,sha in pins.items():assert before['refs/heads/'+ref]==after['refs/heads/'+ref]==sha
out={'passed':True,'allInitialRemoteRefsUnchanged':True,'initialRemoteRefs':len(before),'initialTags':sum(k.startswith('refs/tags/')for k in before),'protectedCheckpointPins':pins,'PR3':{k:b[k]for k in keys},'mainUnchanged':before['refs/heads/main']==after['refs/heads/main'],'noCloudflareAccountAccess':True,'hostedWorkstationPreservation':'No account/API/deployment action was taken; all historical B12 source bytes independently audited. Hosted runtime content was not actively re-probed or redeployed.'}
(E/'protected-ref-pr3-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS: all protected remote refs, main and PR #3 head/base/open identity unchanged')
