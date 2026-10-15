"""Read-only scientific/boundary audit; never regenerates historical evidence."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';PREFIX=str(B.relative_to(R))+'/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checkpoint=json.loads((E/'checkpoint.json').read_text())
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()==checkpoint['experimentalBranch']
assert all(sha(R/name)==digest for name,digest in checkpoint['files'].items())
changed=subprocess.check_output(['git','diff','--name-only',checkpoint['startingCommit']],cwd=R,text=True).splitlines()
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
assert all(n.startswith(PREFIX) for n in changed+untracked),(changed,untracked)
accepted=json.loads((E/'accepted-source.json').read_text())
for name,digest in accepted['sha256'].items():
 p=B/'accepted'/name
 original=subprocess.check_output(['git','show',f"{accepted['commit']}:experiments/dx-fv/{name}"],cwd=R)
 assert p.read_bytes()==original and sha(p)==digest,name
prov=json.loads((E/'build-provenance.json').read_text())
assert prov['upstreamCommit']=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
assert prov['originalFlashSHA256']=='debf60f85d1d0955f08596e64d3a4958d7f369657cb3161a6b7625fa508cf3df'
assert prov['experimentalFlashSHA256']=='9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3'
for rel,meta in prov['artifacts'].items():assert sha(B/rel)==meta['sha256'],rel
assert all(r['equal'] for r in json.loads((E/'rebuild-verification.json').read_text())['artifacts'].values())
inputs=json.loads((B.parent/'browser_eos_precision/inputs.json').read_text())
matrixChecks=[]
for browser in ['chromium','webkit']:
 official=json.loads((E/f'{browser}-official8.json').read_text());control=json.loads((E/f'{browser}-build30.json').read_text())
 assert official['precision']['rows']==control['precision']['rows'] and official['accuracy']==control['accuracy']
 for build in ['official8','build30','build44','official72']:
  q=json.loads((E/f'{browser}-{build}.json').read_text())
  assert len(q['accuracy'])==612
  for row in q['precision']['rows']:
   inp=next(x for x in inputs['cases'] if x['id']==row['id'])
   if 'error' not in row:
    assert row['args']==inp['args'] and row['inputBits']==inp['inputBits']
  s=json.loads((E/f'{browser}-synthetic-{build}.json').read_text())
  assert len(s['rows'])==16
  passed=sum(r['converged'] for r in s['rows']);assert passed==(16 if build in ['build44','official72'] else 14)
  for r in s['rows']:assert r['settings']=={'nonlinearTolerance':1e-11,'maxIterations':30}
  matrixChecks.append({'browser':browser,'build':build,'precisionRows':len(q['precision']['rows']),'syntheticConverged':passed})
engineEquality=[]
for build in ['official8','build30','build44','official72']:
 a=json.loads((E/f'chromium-{build}.json').read_text());b=json.loads((E/f'webkit-{build}.json').read_text())
 assert a['precision']['rows']==b['precision']['rows'] and a['accuracy']==b['accuracy']
 engineEquality.append(build)
coupled=json.loads((E/'coupled-summary.json').read_text())
assert len(coupled['runs'])==30 and len(coupled['temporalComparisons'])==20
for row in coupled['runs']:
 assert row['completedAllSamples'] and row['stop'] is None and row['harnessError'] is None,row['file']
 assert row['conservationPass'] and row['frozenDirectEOSPass'],row['file']
 assert row['maxAcceptedTemporalError']<=1 and row['maxCanonicalDensityResidual']<1e-7 and row['maxCanonicalEnergyResidualKJkg']<1e-7
 assert row['settings']['nonlinearTolerance']==1e-11 and row['settings']['thermalResidualK']==1e-12 and row['settings']['maxIterations']==30
 assert row['settings']['method']=='tr-bdf2'
 raw=json.loads((E/row['file']).read_text())
 assert all(x['record']['lastResidual'] is None or x['record']['lastResidual']<=1e-11 for x in raw['rows'])
assert all(r['pass'] for r in coupled['temporalComparisons'])
offline=json.loads((E/'ipad-origin-disabled-smoke-v3.json').read_text())
assert len(offline)==2 and all(len(r['builds'])==4 and all(b.get('result',{}).get('ok') for b in r['builds']) for r in offline)
perf=[]
for browser in ['chromium','webkit']:
 for build in ['official8','build30','build44','official72']:
  p=json.loads((E/f'{browser}-performance-{build}.json').read_text());w=p['worker']['result']
  assert w['ok'] and len(p['startup'])==3
  perf.append({'browser':browser,'build':build,'workloadFailures':sum(r['failures'] for r in w['performance']['timings'])})
report={'passed':True,'protectedStartingFiles':len(checkpoint['files']),'onlyNewResearchDirectoryChanged':True,
 'verbatimAcceptedSources':len(accepted['sha256']),'repeatCompiledArtifactHashesMatch':True,
 'officialAndSource30MeasurementsEqual':True,'enginePropertyMatricesExactlyEqual':engineEquality,'matrices':matrixChecks,
 'coupledRuns':30,'temporalComparisons':20,'allConservationAndFrozenEOSChecksPass':True,'performance':perf,
 'physicalIPadTested':False,'qualification':'PROMISING; limited research evidence, not full A2 or device qualification.'}
text=json.dumps(report,indent=2)+'\n';out=E/'audit.json'
if out.exists():assert out.read_text()==text,'Retain completed audit'
else:out.write_text(text)
print(json.dumps(report,indent=2))
