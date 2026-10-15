import os,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
requests={q['id']:q for q in json.loads((B.parent/'browser_eos/inputs.json').read_text())['requests']}
out={'runs':[],'limits':{'pressurePa':10,'enthalpyJkg':50,'temperatureK':.01},'warning':'Matching native PH flashes can share inversion/cache defects. These value comparisons do not replace independent DT/canonical checks.'}
for browser in ['chromium','webkit']:
 for build in ['official8','build30','build44','official72']:
  file=E/f'{browser}-{build}.json'
  if not file.exists():out['runs'].append(dict(file=file.name,status='NOT RUN'));continue
  d=json.loads(file.read_text());version='7.2.0' if build=='official72' else '8.0.0'
  native=json.loads((E/f'python-{version}.json').read_text());reference={r['id']:r for r in native['rows']}
  maxima=dict(pressurePa=0.,enthalpyJkg=0.,temperatureK=0.);mismatches=[];invalid=[];errorRows=[]
  for r in d['accuracy']:
   n=reference[r['id']];request=requests[r['id']]
   if ('error'in r)!=('error'in n):mismatches.append(r['id'])
   if 'error'in r:errorRows.append(dict(id=r['id'],mode=r['mode'],region=r['region'],error=r['error']))
   if request['region']=='invalid':invalid.append(dict(id=r['id'],mode=r['mode'],browserError=r.get('error'),nativeError=n.get('error'),rawSuccessUnsupported='error' not in r));continue
   if 'state' in r and 'state' in n:
    for key,field in [('pressurePa','p'),('enthalpyJkg','h'),('temperatureK','T')]:maxima[key]=max(maxima[key],abs(r['state'][field]-n['state'][field]))
  saved=[r for r in d['precision']['rows'] if r['id']=='exact-saved' and r['method']=='fresh' and r['axis']=='P' and r['step']==.01]
  out['runs'].append(dict(file=file.name,status='PASS' if not mismatches and all(maxima[k]<out['limits'][k] for k in maxima) else 'FAIL',build=build,browser=browser,accuracyRequests=len(d['accuracy']),precisionRows=len(d['precision']['rows']),successes=sum('state'in r for r in d['accuracy']),errors=errorRows,successFailurePatternMismatches=mismatches,invalidRequests=invalid,maxValidValueDifferences=maxima,savedLiquidPressureProbe=saved,linearMemory=d['linearMemory']))
(E/'regression-summary.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out['runs']:print(r['file'],r['status'],r.get('maxValidValueDifferences'))
