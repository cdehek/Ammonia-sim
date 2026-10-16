"""Final preservation and remote-ref comparison; no writes outside B5."""
import json,hashlib,subprocess
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(f):return json.loads((E/f).read_text())
old=read('starting-file-hashes.json');changed=[n for n,h in old.items()if sha(R/n)!=h]
def refs(f):return {ref:sha for sha,ref in (x.split()for x in(E/f).read_text().splitlines())}
before=refs('refs-before.txt');after=refs('refs-before-push.txt');moved={k:dict(before=v,after=after.get(k))for k,v in before.items()if after.get(k)!=v}
branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip();assert branch=='research/browser-eos-b5-35bar-inverse-forensics-20261016'
tracked=subprocess.check_output(['git','diff','3622000309cacdd35aaaebbb805ae40d27c75603','--name-only'],cwd=R,text=True).splitlines();untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines();unexpected=[n for n in tracked+untracked if not n.startswith(str(B.relative_to(R))+'/')]
out=dict(start='3622000309cacdd35aaaebbb805ae40d27c75603',branch=branch,originalFiles=len(old),changedStartingFiles=changed,protectedRemoteHeads=len(before),movedProtectedHeads=moved,unexpectedPaths=unexpected,sourceRestored=read('provenance.json')['sourceRestoredToB4C'],scientificEvidenceAudit=read('scientific-audit.json')['evidenceAuditPass'],functionalRepair=False,sourceOrAdapterRepair=False,EOSDataChanged=False,budgetsChanged=False,merge=False,deployment=False,allFailuresRetained=True)
out['allPass']=not changed and not moved and not unexpected and out['sourceRestored']and out['scientificEvidenceAudit'];assert out['allPass'],out
(E/'final-preservation.json').write_text(json.dumps(out,indent=2)+'\n')
files={str(p.relative_to(B)):sha(p)for p in sorted(B.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.name!='delivery-file-hashes.json'}
(E/'delivery-file-hashes.json').write_text(json.dumps(files,indent=2)+'\n');print('Final preservation PASS;',len(files),'new files hashed;',len(before),'protected remote heads unchanged')
