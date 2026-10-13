"""Read-only scientific evidence/preservation audit. PASS is not qualification."""
import ast,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';load=lambda f:json.loads((E/f).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base='458a3b3c07dbf2171248e4cf237ed99c582a65b2';pres=load('preservation.json');checkpoint=load('resume-checkpoint.json')
for p,h in pres['preservedFiles'].items():assert sha(R/p)==h,p
for p,h in checkpoint['filesAtInterruption'].items():
 if p not in ['eos.mjs','worker.mjs']:assert sha(B/p)==h,p
assert sha(E/'checkpoint-eos.mjs')==checkpoint['filesAtInterruption']['eos.mjs']
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='research/browser-eos-feasibility-20261012'
assert subprocess.check_output(['git','merge-base',base,'HEAD'],cwd=R,text=True).strip()==base
assert subprocess.run(['git','merge-base','--is-ancestor','be9eb35a4ddf5098e685182f8104685127c6a6ee','HEAD'],cwd=R).returncode==0
# Independently inspect actual names rather than rely on a pathspec exclusion.
changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=R,text=True).splitlines()
dirty=subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).splitlines()
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
assert all(p.startswith('experiments/dx-fv/browser_eos/') for p in changed+dirty+untracked)
for a in load('assets.json')['assets']:assert sha(B/a['path'])==a['sha256'] and (B/a['path']).stat().st_size==a['bytes']
inputs=json.loads((B/'inputs.json').read_text());assert len(inputs['requests'])==612
summary=load('summary.json');assert not summary['qualifiedPropertyEngine'] and not summary['testedOnPhysicalIPad']
for version in ['7.2.0','8.0.0']:
 p=load(f'python-{version}.json');assert p['inputsSHA256']==sha(B/'inputs.json') and len(p['rows'])==612
 assert p['defaultReferenceUnchanged']
for name in ['chromium','webkit']:
 acc=load(name+'-accuracy.json');assert len(acc['builds'])==2
 for d in acc['builds']:
  ref=load('python-'+d['requestedVersion']+'.json');assert d['capabilities']['git']==ref['git']
  assert len(d['rows'])==612 and all(r['id']==q['id'] for r,q in zip(d['rows'],inputs['requests']))
  for r,q in zip(d['rows'],ref['rows']):
   assert bool(r.get('error'))==bool(q.get('error')),(name,r['id'])
   if r.get('errors'):assert abs(r['errors']['p'])<10 and abs(r['errors']['T'])<.01 and abs(r['errors']['h'])<50
  stress=d['stress'];assert stress['nativeErrors']==stress['subsequentValidUpdates']==100
  assert stress['stackBefore']==stress['stackAfter'] and stress['linearMemoryBefore']==stress['linearMemoryAfter']
 assert 'PT_INPUTS' in acc['builds'][0]['capabilities']['inputPairs'] and 'HmassP_INPUTS' not in acc['builds'][0]['capabilities']['inputPairs']
 assert 'HmassP_INPUTS'in acc['builds'][1]['capabilities']['inputPairs']
 assert 'hmass' not in acc['builds'][0]['capabilities']['stateMethods']
 perf=load(name+'-performance.json');assert len(perf['sustained'])==3 and len(set(r['linearMemoryBytes'] for r in perf['sustained']))==1
 assert all(r['maxDifference']==0 for r in perf['cacheProof']['rows'])
 assert len(load(name+'-interior-patterns.json')['rounds'])==54
 worker=load(name+'-worker.json');assert worker['mainThreadTicks']>=50 and worker['work']['calls']>1000
 offline=load(name+'-offline-server-disabled.json');assert offline['offlineVerification']['serverUnavailableDuringReloadAndEOSLoad']
 assert abs(offline['offline']['state']['p']-30174.790361846546)<1e-6
 assert offline['missingAssetError']=='WASM asset unavailable: HTTP 404'
 assert not offline['mimeFallback']['init']['streaming']
 supp=load(name+'-scientific-supplement.json');assert len(supp['canonical'])==189 and all('recoveryErrors'in r for r in supp['canonical'])
 for r in supp['canonical']:assert abs(r['recoveryErrors']['p'])<10 and abs(r['recoveryErrors']['T'])<.01 and abs(r['recoveryErrors']['h'])<50
 # Record the scientific failure as a failure, not a condition to fix here.
 sweep=load(name+'-probe-sweep.json');r=next(r for d in sweep['builds'] if d['version']=='8.0.0' for r in d['rows'] if r['target']=='exact-saved-input' and r['pressureStepPa']==.01)
 assert r['finiteRhoPAtH']/r['analyticRhoPAtH']>19
 assert abs(r['perturbedUnderlyingHResidualJkg'])>.0004
 assert load(name+'-legacy-high-level.json')['timings']
 assert summary['browsers'][name]['accuracy']['8.0.0']['staticValueGatesPass']
for f,h in summary['codeHashes'].items():assert sha(B/f)==h,f
for p in B.glob('*.py'):ast.parse(p.read_text())
for f in ['ENGINEERING_REPORT.md','MECHANICS_REPORT.md','README.md','vendor/THIRD_PARTY.md']:assert (B/f).stat().st_size>500
out=dict(evidenceAuditPassed=True,qualifiedPropertyEngine=False,EOSMigrationAuthorized=False,scientificClassification=summary['classification'],oldTrackedFilesPreserved=len(pres['preservedFiles']),checkpointAssetsInputsAndPythonRunsPreserved=True,staticValueGatesPassedOnComparableValidStates=True,accountingRoundtripsPerBrowser=189,desktopOfflineAndWorkerChecksPassed=True,actualIPadTested=False,unchangedFiniteDifferenceCompatibilityDemonstrated=False,observedFlashPrecisionProblemRetained=True,noCoupledOrLongTrajectoryRuns=True,firstHarnessAndWebKitNetworkEmulationFailuresRetained=True,
         currentSourceHashes={str(p.relative_to(B)):sha(p) for p in B.iterdir() if p.is_file()},referenceHashes={f:sha(E/f) for f in ['python-7.2.0.json','python-8.0.0.json']})
(E/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['currentSourceHashes','referenceHashes']},indent=2))
