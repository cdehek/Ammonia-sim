"""Verify runtime relocations, original derivation, registry property/source closure."""
import hashlib,json,re,subprocess
from pathlib import Path
from audit import B,R,PINS,sha,git
m=json.loads((B/'preview/asset-manifest.json').read_text())
for a in m['assets']:
 raw=(B/'preview'/a['path']).read_bytes();assert sha(raw)==a['sha256']
 for change in reversed(a['relocations']):raw=raw.replace(change['to'].encode(),change['from'].encode())
 assert raw==git('show',a['sourceCommit']+':'+a['sourcePath'])
# Independently verify the full pinned original source inventory sealed by B10.
operator=json.loads(git('show',PINS['B10']+':experiments/dx-fv/browser_eos_b10/evidence/operator-source-manifest.json'))
proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for path,identity in operator.items():
 proc.stdin.write((PINS['original']+':'+path+'\n').encode());proc.stdin.flush()
 header=proc.stdout.readline().split();raw=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
 assert header[0].decode()==identity['gitBlob'] and sha(raw)==identity['sha256'],path
proc.stdin.close();proc.wait()
text=(B/'preview/index.html').read_text().replace('./panel.mjs','/experiments/dx-fv/browser_eos_b10/panel.mjs')
original=git('show',PINS['original']+':index.html')
text=re.sub(r'<script data-b10="(?:mount|bootstrap)">.*?</script>','',text,flags=re.S)
entry=" 'b10-a2-shadow':[$('b10-a2-shadow'),'A2 — Five-Section Evaporator Research'],\n";assert text.count(entry)==1
text=text.replace(entry,'');assert text.encode()==original
bundle=(B/'preview/science/candidate-bundle.mjs').read_bytes()
# Exact bundle equality proves all embedded registry tables/model/fixtures unchanged.
assert bundle==git('show',PINS['B9C']+':experiments/dx-fv/browser_eos_b9c/candidate-bundle.mjs')
assert {p.relative_to(B/'preview').as_posix() for p in (B/'preview').rglob('*') if p.is_file()}=={a['path'] for a in m['assets']}|{'asset-manifest.json'}
# Verify every local static import/export/new-URL dependency resolves inside preview.
for p in (B/'preview').rglob('*.mjs'):
 for spec in re.findall(r"(?:from\s*|new URL\()'([^']+)'",p.read_text()):
  if spec.startswith('.'):
   target=(p.parent/spec).resolve();assert target.is_relative_to((B/'preview').resolve()) and target.is_file(),(p,spec)
report={'passed':True,'allAssetsVerified':len(m['assets']),'fullPinnedOriginalSourceInputsVerified':len(operator),'allRelocationsReverseToPinnedSources':True,'reverseToOriginalWorkstation':True,'originalSHA256':sha(original),'exactScientificBundleSHA256':sha(bundle),'sourcePins':PINS,'noScientificAlgorithmChanges':True,'originalEmbeddedPropertiesPreserved':True}
(B/'evidence/source-integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
