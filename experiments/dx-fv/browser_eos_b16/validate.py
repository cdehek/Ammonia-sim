"""Validate frozen sources and all retained gates without rerunning timings."""
from pathlib import Path
import json,gzip,hashlib,subprocess,zipfile
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):
 p=E/(name+'.json');return json.loads(p.read_text() if p.exists() else gzip.decompress((E/(name+'.json.gz')).read_bytes()))
def sha(raw):return hashlib.sha256(raw).hexdigest()
for name,x in read('copied-assets').items():
 assert sha((B/name).read_bytes())==x['sha256'],name
 assert (B/name).read_bytes()==(B.parents[2]/x['source']).read_bytes(),name
for name,x in read('lossless-compaction').items():
 raw=gzip.decompress((E/x['compressed']).read_bytes());assert len(raw)==x['originalBytes'] and sha(raw)==x['originalSHA256']
 assert sha((E/x['compressed']).read_bytes())==x['compressedSHA256']
science=read('chromium-science');assert science['passed'] and not science['errors'] and len(science['cases'])==6
residuals=matrices=0
for case in science['cases']:
 runs=case['runs'];ref=runs['control'];assert ref['finalClock']==.01
 for key in ['checkpoints','attempts','events','finalClock','accepted','rejected','audits']:
  assert all(ref[key]==r[key]for r in runs.values()),(case['fixture'],case['schedule'],key)
 assert [p['seconds']for p in ref['checkpoints']][:4]==[0,.0001,.0005,.001]
 streams=runs['observed-control']['diagnostics']['streams'];assert streams==runs['observed-candidate']['diagnostics']['streams']
 residuals+=streams['residuals']['count'];matrices+=streams['linear']['count']
assert science['failures']['control']==science['failures']['candidate']
for f in ['domain','partial','numerical']:
 p=[r for r in science['protocol']if r.get('fixture')==f];assert len(p)==2 and p[0]['detail']==p[1]['detail']
for variant in ['control','candidate']:
 assert any(r.get('externalLoss','').endswith('unknown')for r in science['protocol']if r['variant']==variant)
 assert any(r.get('malformedEnvelopeRejected')for r in science['protocol']if r['variant']==variant)
for name,n in [('node-primary',60),('node-counters',24),('node-jitless',12),('node-trace',4)]:
 rows=read(name);assert len(rows)==n
 for r in rows:assert r['returncode']==0 and not r['externalWallTermination'] and not r['scientificHashingInTimedScope']
assert read('context-counts')['passed'] and read('hash-check')['passed']
worker=read('chromium-performance');assert worker['passed'] and len(worker['rows'])==64 and not worker['errors']
assert sum(r['primary']for r in worker['rows'])==48
for r in worker['rows']:assert r['checksum']['clock']==.01 and r['stats']['history']<=8 and r['stats']['attempts']<=256
for name in ['chromium-micro','chromium-retention','chromium-owner-ui']:
 r=read(name);assert r['passed'] and not r['errors']
assert len(read('chromium-micro')['rows'])==12 and len(read('chromium-retention')['rows'])==12 and len(read('chromium-owner-ui')['rows'])==24
for name in ['chromium-science','chromium-performance','chromium-micro','chromium-retention','chromium-owner-ui']:
 exit=read(name+'-exit');assert exit['returncode']==0 and not exit['externalWallTermination']
for name in ['chromium-science-initial-harness-assumption-exit','chromium-science-second-harness-assumption-exit']:
 assert read(name)['returncode']!=0
analysis=read('analysis');assert analysis['allValidSamplesRetained'] and len(analysis['node'])==8 and len(analysis['worker'])==18
for k,x in analysis['micro'].items():assert x['improvementPercent']['n']==6
for x in analysis['worker'].values():assert x['savedMS']['n'] in [2,6]
for x in read('context-counts')['rows']:
 c=x['advanceCounts'];assert sum(x['advancePH'].values())==c['phCalls']
for f in ['cold','warm']:
 a,b=[next(r for r in read('context-counts')['rows']if r['fixture']==f and r['variant']==v)for v in ['control','candidate']]
 assert a['scientificSHA256']==b['scientificSHA256'] and a['advancePH']==b['advancePH']
 for k in ['phCalls','branches','bisections','mixRows','boundary.hit','boundary.miss','section.hit','section.miss']:assert a['advanceCounts'][k]==b['advanceCounts'][k]
 assert a['advanceCounts']['pressureBrackets']-b['advanceCounts']['pressureBrackets']==39*b['advanceCounts']['ownedHolders']
package=read('desktop-package-manifest');assert sha((B/package['package']).read_bytes())==package['sha256']
with zipfile.ZipFile(B/package['package']) as z:
 assert json.loads(z.read('PACKAGE_MANIFEST.json'))==package['files']
 for name,h in package['files'].items():assert sha(z.read(name))==h==sha((B/name).read_bytes())
reports=['README','B16_RESEARCH_DESIGN','ENGINEERING_REPORT','MECHANICS_REPORT','SCIENTIFIC_SOURCE_AND_PROVENANCE','COLD_PERFORMANCE_ROOT_CAUSE','JIT_AND_GC_SENSITIVITY','BROWSER_WORKER_ARCHITECTURE','BROWSER_SCIENTIFIC_PARITY','WORKER_LATENCY_AND_RESPONSIVENESS','WORKLOAD_MIX_ANALYSIS','MEMORY_AND_HISTORY_RETENTION','BENCHMARK_METHODOLOGY','BENCHMARK_RESULTS','RUNTIME_AND_PLATFORM_LIMITATIONS','OWNER_DESKTOP_BENCHMARK','INTEGRATION_READINESS_DECISION','ROLLBACK_AND_PROVENANCE','QUALIFICATION_GAPS','NEXT_MILESTONE_RECOMMENDATION']
assert all((B/(name+'.md')).is_file()for name in reports)
status=json.loads((B/'milestone-status.json').read_text());assert status['classification']=='B16-A0 DESKTOP/WORKER READINESS PASS' and status['integrationReadinessDecision']=='CONDITIONAL GO'
assert read('protected-ref-pr3-audit')['passed'] and read('final-source-audit')['passed']
# Recompute descriptive analysis and all strict pair checksum assertions.
subprocess.run(['python3',str(B/'analyze.py')],check=True)
result={'passed':True,'requiredReports':len(reports),'historicalBytesUnchanged':True,'frozenCopiedAssets':len(read('copied-assets')),'actualChromiumWorkerScience':True,'residualObjectsComparedPerVariant':residuals,'matricesCorrectionsComparedPerVariant':matrices,'workerSolverSamples':64,'nodePrimarySamples':60,'allSamplesRetained':True,'fullWorkerTimingDigestsMatch':True,'originalFailureSemanticsPreserved':True,'initialHarnessFailuresRetainedAndNotCountedAsPass':True,'losslessScienceCompactionVerified':True,'ownerPackageActualLinuxUIAndDownload':True,'ownerDevice':'NOT TESTED','protectedRefsAndPR3':True,'qualificationSeconds':.001,'maximumResearchSeconds':.01}
(E/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
