"""Fail closed on historical files, scientific policy and protected remote heads."""
import os
import json,hashlib,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));R=B.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((E/'starting-file-hashes.json').read_text());changed=[n for n,h in old.items() if not (R/n).is_file() or sha(R/n)!=h]
assert not changed,changed
status=subprocess.check_output(['git','diff','--name-status','e30ad9d76bc892aa355126339997d6184c8729d2'],cwd=R,text=True)
assert all(line.startswith('A\texperiments/dx-fv/browser_eos_b5a/') for line in status.splitlines()),status
refs=lambda p:dict(line.split()[::-1] for line in p.read_text().splitlines())
before=refs(E/'refs-before.txt');after=refs(E/'refs-after.txt');branch='refs/heads/research/browser-eos-b5a-du-saturation-repair-20261016'
remoteChanged={n:dict(before=s,after=after.get(n)) for n,s in before.items() if n!=branch and after.get(n)!=s}
assert not remoteChanged,remoteChanged
out=dict(startingFiles=len(old),changedStartingFiles=changed,allPriorTrackedFilesPreserved=True,protectedRemoteChanges=remoteChanged,scientificBudgetsUnchanged=True,acceptedA2ByteIdentical=True,adapterLoaderLivePlantUIUnchanged=True,onlyB5AAdditions=True,branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),allPass=True)
(E/'final-preservation.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
