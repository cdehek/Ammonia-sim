"""Final read-only scientific review receipt before preservation sealing."""
import hashlib,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda n:json.loads((E/n).read_text())
assert read('acceptance.json')['assessment']=='FOCUSED BROWSER GATE A PASS'
assert read('shared-native-audit.json')['passed']
differences=[]
for r in read('shared-native-audit.json')['rows']:
 for c in r['browserComparisons']:
  if c['nativeBrowserPhaseDifference']:
   assert c['originalEndpointControl'] and not r['fullVLE'] and c['historicalDefaultBrowserExact']
   differences.append(dict(id=r['id'],mode=r['mode'],label=r['label'],engine=c['engine'],nativePhase=c['nativePhase'],browserPhase=c['browserPhase'],physicalQualification='unchanged endpoint uncertainty'))
assert len(differences)==44 and len({(r['id'],r['mode']) for r in differences})==11
quality=read('quality-disposition.json')
assert not quality['physicalAcceptanceOfInvalidQuality'] and quality['DPPhysicalQualification']=='FAIL / NOT QUALIFIED'
assert quality['rawComparisons']==44 and quality['uniqueDPPathInputs']==11
source=read('source-candidate.json')['trackedSourceSHA256'];S=Path('/workspace/b7-work/upstream')
assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==h for n,h in source.items())
for r in read('artifacts-with-diagnostics.json').values():
 assert hashlib.sha256((B/r['jsPath']).read_bytes()).hexdigest()==r['jsSHA256']
 assert hashlib.sha256((B/r['wasmPath']).read_bytes()).hexdigest()==r['wasmSHA256']
assert read('pr3-before.json')==read('pr3-prepush.json')
for name in ['README.md','ENGINEERING_REPORT.md','BUILD.md','FAILURE_MATRIX.md','EXCEPTION_ABI.md','DESIGN.md','MECHANICS_REPORT.md','PERFORMANCE_AND_MEMORY.md','EXECUTION_NOTES.md']:assert (B/name).is_file()
for p in Path('/workspace/b7-work').glob('*.log'):
 target=E/'logs'/p.name
 if target.exists():assert target.read_bytes()==p.read_bytes(),p.name
 else:shutil.copyfile(p,target)
out=dict(assessment='FOCUSED BROWSER GATE A PASS',gate1='PASS',gate2='PASS',additionalNativeSharedNumericalComparisonPassed=True,endpointLabelDifferencesRetained=differences,additionalDPPhysicalQualification='FAIL / NOT QUALIFIED; invalid raw states strictly refused by scientific audit',invalidPhysicalQualityAccepted=False,sourceAndArtifactIdentitiesRechecked=True,PR3IdentitiesUnchanged=True,allReportsPresent=True,scope='Three resolved Gate A liquids only; original endpoint/support blockers and supplemental unqualified DP failures remain. No global DP/backend/A2, device, production or responsiveness qualification.')
p=E/'final-review.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Final scientific review PASS; additional native endpoint differences explicitly retained')
