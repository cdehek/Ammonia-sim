"""Read-only historical/inherited audit; writes receipts only in C2."""
import hashlib,importlib.util,json,subprocess,sys
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='7809d08be67eab7cb9b537b1c1199b456b2da122';TARGET='refs/heads/research/browser-eos-b5b-c2-inventory-certification-feasibility-20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((E/n).read_text())
old=read('historical-file-hashes.json');bad=[p for p,h in old.items() if sha(R/p)!=h];assert not bad,bad
spec=importlib.util.spec_from_file_location('prior',B.parent/'browser_eos_b5b/audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);prior=m.verify()
changes=subprocess.check_output(['git','diff',START,'--name-status'],cwd=R,text=True).splitlines();assert all(s.startswith('A\texperiments/dx-fv/browser_eos_b5b_c2/') for s in changes),changes
def refs(n):return dict(line.split()[::-1] for line in (E/n).read_text().splitlines())
before,after=refs('refs-before.txt'),refs('refs-after.txt');drift={k:[v,after.get(k)] for k,v in before.items() if after.get(k)!=v};assert not drift,drift;assert set(after)-set(before)<={TARGET}
matrix=read('matrix.json')['rows'];assert len(matrix)==37 and all(x['certificateStatus']=='UNRESOLVED' and x['physicalTrajectoryExit']=='unproved' for x in matrix)
for row in matrix:
 assert all(v['certificateStatus']=='UNRESOLVED' and not v['physicalBranchCertified'] for v in row['targets'].values())
 assert max(float(v) for v in row['normalizedResiduals'].values())<=1e-11
 assert all(row['actual'][n]['input']['bits']==row['exactInput']['bits'] for n in ['chromium','webkit'])
assert sum(x['canonicalPass'] is True for x in matrix)==33
for n in ['chromium','webkit']:
 a=read(n+'-replay.json');assert a['historicalExactMatch'] and len(a['rows'])==7
 assert all('error'in x and 'adapter'not in x for x in a['rows'])
 assert all('adapter'in x for x in a['falseAcceptance'])
 assert all(x.get('error',{}).get('faultKind')=='solver' for x in a['c1'] if 'error'in x)
 b=read(n+'-origins.json');assert b['historicalExactMatch'] and len(b['rows'])==2
 for origin in b['rows']:
  corresponding=next(r for r in matrix if r['key']==origin['key']);assert origin['input']['bits']==corresponding['exactInput']['bits']
native=read('native.json');saved=json.loads((B.parent/'browser_eos_b5/evidence/native-fixed-replay.json').read_text())['rows'];saved={r['key']:r['result']['B4C'] for r in saved}
for row in native['rows']:
 if row['group'] not in ['rows','falseAcceptance']:continue
 actual=row['raw']['bits'];expected=saved[row['key']]['DU']['bits'];assert all(actual[k]==v for k,v in expected.items())
assert sum('error'in x for x in native['gateAEndpoints'])==3
assert (R/'engine.js').read_bytes()==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:engine.js'],cwd=R)
assert F(.003/5)==F(2767011611056433,4611686018427387904)
for key in ['webkit-ledger-69','webkit-ledger-76']:
 row=next(x for x in matrix if x['key']==key);z=row['targets']['exact_MUV'];assert float(z['pressureMinusLimitPaDiagnostic'])>0 and z['localRootEnclosure']['localPressureSide']=='OUTSIDE'
 rowbits=row['exactInput']['bits'];report=(B/'ENGINEERING_REPORT.md').read_text();assert all(rowbits[k] in report for k in ['M','U_kJ','V'])
source=read('source-verification.json');assert source['reconstructedSourceFiles']==1782 and not source['sourceMismatches']
for p in source['patches']:assert p['forwardApplicable'] and p['reverseApplicable']
science=read('scientific-audit.json');assert science['standaloneNumericalRows']==37 and not science['fullBackendQualified'] and not science['fullA2Run']
out=dict(start=START,historicalFiles=len(old),historicalMismatches=bad,artifactIdentities=len(prior['artifacts']),acceptedA2Snapshots=len(prior['acceptedA2']),reconstructedSourceFiles=1782,scientificPatches=len(source['patches']),C1BytesPreserved=True,protectedRemoteRefsChecked=len(before),protectedRemoteRefDrift=drift,onlyAllowedNewRemoteRef=TARGET,changes=changes,matrixRows=len(matrix),canonicalRowsChecked=33,maxNormalizedResidual=max(float(v) for row in matrix for v in row['normalizedResiduals'].values()),fullCertificatesIssued=0,budgetsUnchanged=True,noEOSAdapterA2Changes=True)
(E/'final-preservation.json').write_text(json.dumps(out,indent=2)+'\n')
# Bind every new artifact/code/report except self-referential audit receipts.
manifest={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file() and '__pycache__'not in str(p) and p.name not in ['source-manifest.json','final-preservation.json']}
(E/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('preserved',len(old),'historical files;',len(before),'remote refs;',len(matrix),'matrix rows; zero full certificates')
