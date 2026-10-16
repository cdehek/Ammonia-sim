"""Original scientific budgets applied to fresh C1 evidence; no new tolerances."""
import hashlib,json,statistics,subprocess,difflib
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';X=B.parent;R=B.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read(X/'browser_eos_b4c/evidence/native-controlA.json')['rows']
mechanisms=read(X/'browser_eos_b5b/evidence/seven-case-analysis.json')
out=dict(browsers={},native={},failures=[],fullQualification=False,physicalIPad=False)
def check(v,label,**data):
 if not v:out['failures'].append(dict(check=label,**data))
def median_cost(rows,label,group=None):
 values=[r['elapsedMS']/r['count'] for r in rows if r['label']==label and (group is None or r['group']==group)]
 return statistics.median(values) if values else None
for browser in ['chromium','webkit']:
 data=read(E/(browser+'-replay.json'));check(data['passed'],'browser pass',browser=browser)
 supplemental=read(E/(browser+'-guards.json'));check(supplemental['passed'] and len(supplemental['rows'])==8,'supplemental guards and loader refusal',browser=browser)
 if not data['passed']:continue
 original=read(X/'browser_eos_b5b/evidence'/(browser+'-replay.json'))
 for r in data['rows']:
  old=next(q for q in original['rows'] if q['key']==r['key']);check(r['calls'][0]['raw']==old['raw'],'original raw bits',key=r['key'])
  check(r['input']['bits']==old['input']['bits'],'original input bits',key=r['key'])
  d=r['error']['evidence']['propertyFailure'];check(not r['state'] and d['reason']=='boundary-unresolved' and d['checks']['support']=='fail' and d['physicalTrajectoryExit']=='unproved','strict refusal',key=r['key'])
  check(abs(r['canonical']['p'])<=.1 and abs(r['canonical']['h'])<=.1 and abs(r['canonical']['T'])<=1e-4,'canonical seven',key=r['key'])
  check(max(r['normalizedResiduals'].values())<=1e-11,'nonlinear seven',key=r['key'])
 for r in data['falseAcceptance']:
  old=next(q for q in original['falseAcceptance'] if q['key']==r['key']);check(r['calls'][0]['raw']==old['raw'] and r['state']==old['adapter'],'inward hazard unchanged',key=r['key'])
 check(len(data['rows'])==7 and len(data['falseAcceptance'])==2 and len(data['matrix'])==24,'complete boundary matrix',browser=browser)
 samples=[];probes=[];canonical=[]
 for row in data['focused']['rows']:
  ref=next(q for q in refs if q['request']['id']==row['id']);s=row['base']['state'];p,h=row['args'];rt=ref['base'].get('reference',{})
  for name,z in [('base',row['base'])]+[(q['axis']+str(q['step']),q.get('output')) for q in row['probes']]:
   check(z is not None,'focused property exception',browser=browser,id=row['id'],sample=name)
   if not z:continue
   if z['phase']==6:continue # homogeneous derivatives do not apply in coexistence
   a=z['state'];dt=z['direct'];pp,hh=z['p'],z['h'];V=.003/5;M=a['rho']*V;U=M*(hh/1000)-100*(pp/1e5)*V
   v=dict(id=row['id'],sample=name,p=dt['p']-pp,h=dt['h']-hh,normalizedEnergy=abs(M*dt['u']/1000-U)/max(1,abs(U)),getterP=a['p']-dt['p'],getterH=a['h']-dt['h'],getterU=a['u']-dt['u'])
   if name=='base' and rt.get('converged'):v['T']=a['T']-rt['state']['T']
   check(abs(v['p'])<=.1 and abs(v['h'])<=.1 and abs(v.get('T',0))<=1e-4 and v['normalizedEnergy']<=1e-11,'original focused EOS budgets',browser=browser,**v)
   check(all(abs(v[k])<=.1 for k in ['getterP','getterH','getterU']),'getter cache consistency',browser=browser,**v);samples.append(v)
  for q in row['probes']:
   n=next(z for z in ref['probes'] if z['axis']==q['axis'] and z['step']==q['step']);v=q.get('output')
   if not v or not n.get('samePhysicalBranch') or not n['output']['supportedInput'] or not rt.get('converged'):continue
   deriv=rt['derivatives']['rhoP' if q['axis']=='P' else 'rhoH'];V=.003/5;M=s['rho']*V;U=M*(h/1000)-p*V/1000;rho=v['state']['rho'];step=q['step'];dU=deriv*V*(h/1000)+(-V/1000 if q['axis']=='P' else M/1000)
   mass=V*abs(rho-s['rho']-deriv*step)/max(.01,M);energy=abs(rho*V*v['h']/1000-v['p']*V/1000-U-dU*step)/max(1,abs(U))
   check(mass<=1e-11 and energy<=1e-11,'original signed FD budget',browser=browser,id=row['id'],axis=q['axis'],step=step,mass=mass,energy=energy);probes.append(dict(id=row['id'],axis=q['axis'],step=step,mass=mass,energy=energy))
 for r in data['focusedAdapter']:
  v=r['canonical'];check(abs(v['p'])<=.1 and abs(v['h'])<=.1 and abs(v['T'])<=1e-4,'focused canonical',browser=browser,id=r['id'],sample=r['sample'],differences=v);canonical.append(v)
 for r in data['cache']['rows']:
  check('error' not in r,'B4B cache sequence',browser=browser)
  for z in r.get('sequences',[]):check('error' not in z,'supported PT sequence',browser=browser);check(all(abs(v)<=.1 for v in z.get('getterDifferences',{}).values()),'PT getter consistency',browser=browser)
 for r in data['a2']['rows']:
  if r.get('persistent'):
   check(r['acceptedRollback'] and r['identityPreserved'] and r['everyRejectedTrialRollback'],'exact rollback',browser=browser,scenario=r['scenario'])
   check(r['record']['stop']['kind']=='solver' and not r['record']['stop']['evidence']['confirmed'],'numerical stop',browser=browser,scenario=r['scenario'])
  if r['scenario']=='matched-real-error-retry':check(r['pair'][0]['stop']['kind']=='domain' and r['pair'][1]['stop']['kind']=='solver','historical false-proof corrected',browser=browser)
 costs={g:{k:median_cost(data['perf'],k,g) for k in ['control','candidate']} for g in ['success','rejected']}
 for v in costs.values():v['candidateOverControl']=v['candidate']/v['control']
 prop={k:median_cost(data['a2']['propagationPerformance'],k) for k in ['control','candidate']}
 out['browsers'][browser]=dict(version=data['version'],originalSevenRefused=7,rawAndInputBitsUnchanged=True,falseAcceptanceQualificationBlockers=2,
  supplementalGuardCases=len(supplemental['rows']),
  focusedSamples=samples,originalSignedFDProbes=probes,canonical=canonical,phaseLabels={r['id']:r['base']['phaseLabel'] for r in data['focused']['rows']},
  a2Scenarios=len(data['a2']['rows']),worker=data['worker'],lifecycle=data['lifecycle'],medianMSPerCall=costs,propagationMSPerCall=prop)
native=read(E/'native-replay.json');wrapper=read(E/'native-wrapper.json');a2=read(E/'native-A2.json')
check(native['passed'] and len(native['rows'])==250 and all(r['exactHistoricalMatch'] for r in native['rows']),'native archived parity')
check(wrapper['passed'] and a2['passed'],'native wrapper and actual native A2')
check(sum(r.get('fullVLE',False) and r['candidate']['error']['evidence']['propertyFailure']['reason']=='inverse-recovery-failure' for r in wrapper['rows'])==3,'actual native QT errors remain errors')
out['native']=dict(fixedRecords=250,exactArchivedParity=True,wrapperCases=len(wrapper['rows']),a2Scenarios=len(a2['rows']),gateANativeControls=native['gateA'],maxRSSKiB=native['maxRSSKiB'])
# Every accepted dependency copied before editing. Only these three may differ.
changed=[];patch=[];closure={}
for n,h in read(E/'a2-before-edit.json').items():
 original=X/'browser_eos_backend/accepted'/n;copy=B/'a2'/n;check(sha(original)==h,'accepted source identity',file=n)
 same=original.read_bytes()==copy.read_bytes();closure[n]=dict(acceptedSHA256=h,candidateSHA256=sha(copy),byteIdentical=same)
 if not same:
  changed.append(n);patch.extend(difflib.unified_diff(original.read_text().splitlines(True),copy.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
check(sorted(changed)==['coupled-implicit.cjs','coupled-model.cjs','thermodynamics.cjs'],'narrow source owners',changed=changed)
patch.extend(difflib.unified_diff([], (B/'a2/failure-contract.cjs').read_text().splitlines(True),fromfile='/dev/null',tofile='b/failure-contract.cjs'))
(B/'a2-error-propagation.patch').write_text(''.join(patch))
out.update(acceptedClosure=closure,changedAcceptedCopies=changed,classificationOnly=True,numericalPressureEnclosure=False,
 inheritedBlockers=['two saved exact-inventory inward false acceptances','B5A Gate B endpoint recovery','Gate A browser unqualified','rejected-PT loader cleanup','full backend/A2 qualification','physical iPad qualification'])
out['gate1']='PASS';out['gate2']='PASS' if not out['failures'] else 'INCOMPLETE/FAIL'
# Explicit byte proof for thermal direction protection and detached commit.
original=(X/'browser_eos_backend/accepted/coupled-model.cjs').read_text();candidate=(B/'a2/coupled-model.cjs').read_text()
for begin,end in [('    // An exact boundary with an outward derivative','    // A branch-aware Newton failure'),('  function commit(s, piece, dt, start)','  function applyBoundary'),('      const start=s.seconds,eventCount=s.events.length','      Object.assign(s,accepted);')]:
 check(original[original.index(begin):original.index(end)]==candidate[candidate.index(begin):candidate.index(end)],'physical protection / commit bytes',begin=begin)
matrix=[]
for browser in ['chromium','webkit']:
 data=read(E/(browser+'-replay.json'))
 for row in data['rows']:
  reference=next(r for r in mechanisms['rows'] if r['id']==row['id'])
  matrix.append(dict(browser=browser,key=row['key'],id=row['id'],input=row['input'],raw=row['calls'][0]['raw'],runtimeReason=row['error']['evidence']['propertyFailure']['reason'],
   refused=row['state'] is None,physicalDomainProof=False,independentMechanism=reference['mechanism'],mathematicalPressureMinusLimitPa=reference['mathematical']['values']['pMinusLimit'],
   referenceSource='../browser_eos_b5b/evidence/seven-case-analysis.json',referenceSHA256=sha(X/'browser_eos_b5b/evidence/seven-case-analysis.json'),canonical=row['canonical'],normalizedResiduals=row['normalizedResiduals']))
write('classification-matrix.json',dict(rows=matrix,mechanismAttribution='Offline mathematical evidence joined only by report; no fixture identities or pressure gaps enter runtime classifier.',numericalPressureEnclosure=False))
out['gate2']='PASS' if not out['failures'] else 'INCOMPLETE/FAIL'
write('scientific-audit.json',out);print('scientific audit',out['gate2'],'failures',len(out['failures']))
for r in out['failures'][:12]:print(r)
assert not out['failures']
