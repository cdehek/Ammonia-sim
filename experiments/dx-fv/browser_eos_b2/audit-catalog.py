"""Verify the actually supplied assertion/module catalog against accepted Git bytes."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2]
E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
C='be9eb35a4ddf5098e685182f8104685127c6a6ee'
path=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/b2-runtime/catalog.json')
d=json.loads(path.read_text())
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
sources={}
for name,text in d['sources'].items():
 target='engine.js' if name=='../../engine' else 'properties.json' if name=='../../properties.json' else 'experiments/dx-fv/'+name
 original=subprocess.check_output(['git','show',C+':'+target],cwd=R).decode()
 assert text==original,target
 sources[name]=digest(text)
source=d['sources']['coupled-test.cjs'];blocks=[]
assert source.startswith(d['prefix']) and d['setup'] in source
for block in d['blocks']:
 assert block['text'] in source and digest(block['text'])==block['sha256']
 assert source.count('\n',0,source.index(block['text']))+1==block['line']
 matches=list(E.glob('*-suite-fd-aware-'+block['id']+'.json'))
 for f in matches:
  r=json.loads(f.read_text())
  assert r['assertionTextSHA256']==block['sha256'],str(f)
 blocks.append(dict(id=block['id'],line=block['line'],sha256=block['sha256'],verifiedCompletedFiles=[f.name for f in matches]))
assert d['domain']['text'] in d['sources']['roadmap-a1.cjs']
out=dict(acceptedCommit=C,passed=True,catalogSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),sourceSHA256=sources,blocks=blocks,prefixSHA256=digest(d['prefix']),setupSHA256=digest(d['setup']),domainAssertionSHA256=digest(d['domain']['text']),meaning='All supplied source/data strings match accepted Git bytes; completed browser blocks match the exact accepted assertion hashes. Catalog selectors/instrumentation remain isolated harness code.')
(E/'catalog-integrity.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(sources),'accepted source/data strings;',len(blocks),'assertion entries verified')
