"""Verify retained evidence, references, source identity and honest interpretation."""
from pathlib import Path
import json,gzip,hashlib,subprocess,sys
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2];read=lambda n:json.loads((E/(n+'.json')).read_text())
def run(*args):
 p=subprocess.run(args,cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
assert run('python3',str(B/'audit.py')).startswith('PASS')
assert read('source-preservation')['historicalBytesUnchanged']
manifest=read('build-manifest')
for name,x in manifest['builds'].items():assert hashlib.sha256((B/(name+'-bundle.mjs')).read_bytes()).hexdigest()==x['sha256'],name
assert {k for k,v in manifest['modules'].items()if not v['unchanged']}=={'engine.js','table-only.cjs'}
assert (B/'control-bundle.mjs').read_bytes()==subprocess.check_output(['git','show','b67afb3215075b2ec82bef376d39e03953dc0da2:experiments/dx-fv/browser_eos_b9c/candidate-bundle.mjs'],cwd=R)
payload=gzip.decompress((E/'property-binary64.json.gz').read_bytes());assert read('property-summary')['receiptSHA256']==hashlib.sha256(payload).hexdigest();assert json.loads(payload)['passed']and read('property-summary')['cases']==60274
for name in ['regressions','isolation','edge-ownership','interface-regression']:assert json.loads(gzip.decompress((E/(name+'.json.gz')).read_bytes()))['passed']
run('node','--max-old-space-size=512',str(B/'verify-compaction.mjs'))
run('node','--max-old-space-size=512',str(B/'prototype-v1/verify-receipts.mjs'))
run('python3',str(B/'prototype-v1/verify-source.py'))
for f in ['cold','warm']:
 for suffix in ['','-added','-fine']:
  for left,right in [('control','candidate'),('control','observe-control'),('candidate','observe-candidate'),('observe-control','observe-candidate')]:
   x=read('equivalence-'+left+'-'+f+suffix+'--'+right+'-'+f+suffix);assert x['passed']and x['allScientificObjectsBitExact']and x['originalAttemptsBitExact']
   assert all(0<=r['seconds']<=.01 for r in x['checkpoints'])
   assert x['sources']['right']['sha256']==manifest['builds'][right]['sha256']
   if left=='observe-control':assert x['conservation']['passed']and x['actualMatricesAndCorrectionsCompared']>0 and x['completeResidualObjectsCompared']>0
 for s in ['original','added','fine']:
  x=read('browser-'+f+'-'+s);assert x['passed'] and x['sourceBuilds']['observe-candidate']==manifest['builds']['observe-candidate']['sha256'];assert x['sameBrowserBinary64ScienceAttemptsResidualsJacobiansCorrectionsHalfStepsAndDecisions'];assert x['results'][0]['checkpoints']==x['results'][1]['checkpoints'];assert x['results'][0]['attemptsHash']==x['results'][1]['attemptsHash']
assert read('browser-properties')['cases']==59862
assert read('browser-interface')['passed'] and read('browser-interface')['additionalPublicInterfaceComparisons']==18
assert read('browser-edges')['passed'] and read('browser-edges')['phaseCombinationComparisons']==126 and read('browser-edges')['differentPressureAxisAlternations']==12
assert read('scientific-summary')['residuals']==76768 and read('scientific-summary')['jacobiansAndCorrections']==3430
assert read('b13-direct-checkpoints')['passed']
w=read('integrated-work-counts');assert w['passed']
for f,x in w['fixtures'].items():
 a,b=x['control']['advanceCounts'],x['candidate']['advanceCounts'];assert a['pressureBrackets']-b['pressureBrackets']==39*x['candidate']['vaporPH']['calls']
 for k in ['phCalls','branches','bisections','mixRows','offsetAxisReads']:assert a[k]==b[k]
assert w['fixtures']['warm']['candidate']['vaporPH']=={'calls':15739,'branches':629560}
x=read('phase-transition-parity');assert x['passed']and x['eventIsInterpolatedNotRootSolved']and x['allLedgersBitExact']and x['allNormalizedTemporalErrorsAndControllersBitExact'];assert x['event']['bracketStartSeconds']==.0053591276016748427 and x['event']['bracketEndSeconds']==.0053820385212110817
assert read('external-termination-validation')['passed']and not read('external-termination-validation')['scientificSolverCompleted']and not read('external-termination-validation')['gracefulRollbackClaim']
binding=read('performance-source-identity');assert binding['sampleFileSHA256']==hashlib.sha256((E/'timing-samples.json').read_bytes()).hexdigest();assert binding['bundleSHA256']['candidate']==manifest['builds']['candidate']['sha256']
samples=read('timing-samples');assert len(samples)==44 and sum(x['pair']>0 for x in samples)==36
for s in samples:assert s['limits']=={'wallSeconds':40,'cpuSeconds':40,'heapMiB':512}and not s['scientificHashingInTimedScope']
x=read('performance-analysis');assert x['allSamplesRetained'];assert all(v['pairedImprovementPercent']['n']==6 and 0<=v['candidateFasterPairs']<=6 for v in x['statistics'].values())
# Every unexpected setup failure and deliberate termination is explicit, never counted PASS.
known={'regressions-node-fetch-setup-failure.exit.json','browser-network-setup-failure.exit.json','external-budget.exit.json','prototype-v1-external-budget.exit.json','browser-long-socket-setup-failure.exit.json'}
for p in E.glob('*.exit.json'):
 x=json.loads(p.read_text())
 if p.name not in known:assert x['returncode']==0,p.name
 else:assert x['returncode']!=0,p.name
reports=['README','BRACKET_REUSE_DESIGN_AND_OWNERSHIP','ENGINEERING_REPORT','MECHANICS_REPORT','SCIENTIFIC_SOURCE_AND_PROVENANCE','ORIGINAL_VS_CANDIDATE_SOURCE_DIFF','PROPERTY_LEVEL_EQUIVALENCE','SUPPORT_DOMAIN_AND_EXCEPTION_PARITY','MUTATION_AND_CACHE_OWNERSHIP','PRESSURE_LOOKUP_WORK_REDUCTION','COUPLED_MODEL_EQUIVALENCE','JACOBIAN_AND_RESIDUAL_PARITY','PHASE_TRANSITION_PARITY','CONSERVATION_AND_ROLLBACK','PERFORMANCE_BENCHMARK','INSTRUMENTATION_OVERHEAD','RUNTIME_AND_BROWSER_LIMITATIONS','QUALIFICATION_GAPS','NEXT_MILESTONE_RECOMMENDATION'];assert all((B/(f+'.md')).is_file()for f in reports)
assert read('protected-ref-pr3-audit')['passed'];run('python3',str(B/'verify-protected.py'))
status=json.loads((B/'milestone-status.json').read_text());assert status['classification']=='B15-A1 EXACT-EQUIVALENCE OPTIMIZATION PASS'and not status['productionPromotion'] and status['prototypeV1InterfaceCounterexampleRetained']
result={'passed':True,'classification':status['classification'],'sourceModuleHashesVerified':True,'propertyCases':60274,'sameBrowserCases':59862,'sixNodeAndSixChromiumFixtureSchedulePairs':True,'losslessReferencesVerified':True,'residualObjectsCompared':76768,'actualMatricesAndCorrectionsCompared':3430,'requiredReports':len(reports),'allTimingSamplesRetained':44,'preliminaryTimingAndInterfaceCounterexampleRetained':True,'finalCandidateScientificMismatches':0,'externalTerminationAndSetupFailuresSeparate':True,'qualificationSeconds':.001,'maximumResearchSeconds':.01,'protectedSourcesRefsAndPR3':True}
(E/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
