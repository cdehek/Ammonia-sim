"""Semantic/provenance validation, not new property/model qualification. Timeout 45s."""
import csv,gzip,hashlib,json,re,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;R=B.parents[2];E=B/'evidence'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for manifest in ['source-evidence-sha256.json','reviewed-source-sha256.json']:
 for name,h in read(E/manifest).items():assert sha((X/name).read_bytes())==h,name
q=read(E/'dp-observations-44.json');original=read(X/'browser_eos_b7/evidence/quality-disposition.json');assert q==original
assert not q['physicalAcceptanceOfInvalidQuality'] and q['DPPhysicalQualification']=='FAIL / NOT QUALIFIED'
dp=read(E/'dp-identities-11.json');assert len(dp['rows'])==11 and dp['fullVLE']==8 and dp['default']==3
assert sorted(i for r in dp['rows'] for i in r['observationIndices'])==list(range(44))
for r in dp['rows']:
 assert not r['qualityAdmissible'] and not r['acceptedPropertyEligible'] and not r['acceptedA2RequestsDP']
 assert len(r['observations'])==4 and r['severity']=='P3'
 for z in r['observations']:assert not 0<=z['rawReturn']['values']['Q']<=1 and z['rawReturn']['values']['phase']==6 and z['nativeRaw']['values']['phase']==6
 for e in ['chromium','webkit']:
  z=[o for o in r['observations'] if o['engine']==e];assert z[0]['rawReturn']==z[1]['rawReturn']
du=read(E/'du-endpoints.json');assert [r['ledger'] for r in du['rows']]==[148,162,164,165]
for r in du['rows']:
 assert len(r['observations'])==12 and r['severity']=='P2'
 assert all(not o['physicalAccepted'] for o in r['observations'])
 candidate=[o for o in r['observations'] if o['artifact'] in ['gateA','candidate']]
 assert len(candidate)==6
 for o in candidate:
  if o['fullVLE'] and r['ledger']!=162:assert not o['returned']
  else:assert o['returned'] and not o['strictBarSupport']
replay=read(E/'du-adapter-replay.json');assert replay['passed'] and len(replay['rows'])==24
for r in replay['rows']:assert not r['accepted'] and r['error']['faultKind']=='solver' and r['error']['evidence']['propertyFailure']['physicalTrajectoryExit']=='unproved'
initial=read(E/'initialization-provenance.json');assert initial['passed'] and len(initial['rows'])==18 and all(r['acceptedInitializerArithmeticExact'] for r in initial['rows'])
summary=read(E/'a2-trace-summary.json');compressed=(E/'a2-trace.json.gz').read_bytes();assert sha(compressed)==summary['traceArtifact']['sha256'];raw=gzip.decompress(compressed);assert sha(raw)==summary['traceArtifact']['uncompressedSHA256'];trace=json.loads(raw)
assert trace['passed'] and trace['exactObservationParity'] and trace['durationSeconds']==.001
assert sorted(trace['counts'])==['ph','sat','stateMVU'] and len(trace['calls'])==sum(trace['counts'].values())
for name,v in trace['files'].items():assert sha((R/v['snapshot']).read_bytes())==v['sha256']
assert len(trace['files'])==14 and len(trace['edges'])==19
assert trace['record']['stop'] is None and trace['record']['sectionCount']==5 and trace['settings']['minStep']==1e-9
assert trace['derivativeEvents']>0 and trace['lineSearchEvents']>0
for event in [e for a in trace['attempts'] for e in a['events'] if e['type']=='iteration' and e['status']=='converged']:
 assert event['fluidNorm']<=1e-11 and event['thermalNorm']*.1<=1e-12
# Source index records actual definitions/imports/property edges in verified original snapshots.
index=[]
for name,v in trace['files'].items():
 if not name.endswith(('.js','.cjs')):continue
 lines=(R/v['snapshot']).read_text().splitlines()
 for n,line in enumerate(lines,1):
  if re.search(r'function\s+\w+|require\(|engine\.(?:ph|sat|stateMVU)|DmassP|DmassUmass',line):index.append(dict(file=name,snapshot=v['snapshot'],line=n,text=line))
(E/'source-reference-index.json').write_text(json.dumps(index,indent=2)+'\n')
start=read(E/'start-audit.json');assert start['historicalFiles']==2372 and start['remoteRefs']==34 and start['onlyAdditiveB8']
assert start['canonicalCheckpoints']['C2']=='7c75d9538d57080a01dffbf7e06128a27e2b9ccd'
for source in ['browser_eos_b5b_c1/evidence/source-manifest.json','browser_eos_b7/evidence/a2-audit.json']:
 assert (X/source).is_file()
c1=read(E/'c1-reused-a2-audit.json');assert c1==read(X/'browser_eos_b7/evidence/a2-audit.json') and c1['passed'] and c1['scenariosPerEngine']==10
boundary=read(E/'boundary-attribution.json');assert boundary==read(X/'browser_eos_b7/evidence/support-attribution.json')
assert len(boundary['rows'])==14 and boundary['roundedDUHistoricalSplit']=='two inside / five outside' and boundary['exactMUVSplit']=='one inside / six outside' and boundary['twoInwardHazardsRemainUnqualified']
for key in ['webkit-ledger-69','webkit-ledger-76']:
 hazards=read(E/(key+'-hazard.json'));assert len(hazards)==8
 for r in hazards:assert not r['certified'] and r['qualificationBlocker']
issues=read(E/'issue-priorities.json');assert len(issues['issues'])==35 and not issues['triageIsScientificQualification']
assert len({r['issueId'] for r in issues['issues']})==35
assert {r['issueId'] for r in dp['rows']}|{r['issueId'] for r in du['rows']}<={r['issueId'] for r in issues['issues']}
with (E/'issue-priorities.csv').open() as f:assert len(list(csv.DictReader(f)))==35
required=['README.md','ENGINEERING_REPORT.md','MECHANICS_REPORT.md','DU_ENDPOINT_DISPOSITION.md','DP_FAILURE_DISPOSITION.md','PROPERTY_CALL_GRAPH.md','A2_PROPERTY_REACHABILITY_MATRIX.md','ISSUE_PRIORITY_MATRIX.md','NEXT_MILESTONE_RECOMMENDATION.md','C1_FAILURE_PROPAGATION_REVIEW.md','SCIENTIFIC_CONTRACT_AUDIT.md','PROTECTED_CHECKPOINT_AUDIT.md','EXECUTION_NOTES.md']
for n in required:assert (B/n).is_file(),n
out=dict(classification='B8 TRIAGE PASS — ACTIONABLE DISPOSITION',gates={'A':'PASS — SCIENTIFIC EVIDENCE CLASSIFIED','B':'PASS — A2 REACHABILITY VERIFIED','C':'PASS — ACTIONABLE ENGINEERING DISPOSITION'},duUnresolved=4,dpIdentities=11,dpObservations=44,dpFullVLE=8,dpDefault=3,invalidDPAccepted=False,baselineA2Pairs=['PH','SAT','MUV/table DU'],rawCoolPropDPDependency=False,traceObserverParity=True,traceFullA2Qualification=False,c1ExistingCoverageReused=True,exactNaturalTransientEndpointOccurrence='UNKNOWN; not required to prove implementation/configuration distinction; not downgraded to diagnostic-only',boundaryRefusalsPerEngine=7,inwardHazards=2,canonicalC2=start['canonicalCheckpoints']['C2'],recommendedNext='Option C — isolated worker-first browser research',nextMilestoneStarted=False,functionalSourceChanged=False,scientificAcceptanceRelaxed=False,provenanceVerified=True)
(E/'acceptance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
