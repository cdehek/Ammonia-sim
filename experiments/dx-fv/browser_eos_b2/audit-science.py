import os
"""Independent Python physical ledgers, native DT and reference comparisons.

Reads completed or partial B2 evidence. Never imports the JavaScript balances.
No failed block is reclassified as a passing full suite.
"""
import json,math,hashlib
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True);a=AbstractState('HEOS','Ammonia')
length=.003/(math.pi*.020**2/4)
tube=math.pi/4*(.024**2-.020**2)*length*7850*.470
fin=1910*math.pi/4*(.080**2-.024**2)*.0002*2700*.900
capacities=[tube/5,fin/5]*5+[6*.718]
out={'operating':[],'historyAudits':[],'contractConservation':[],'limits':{'massKg':1e-8,'energyKJ':1e-6},'noJavaScriptBalanceImports':True}
tableFile=E/'table-coupled-test-fd-aware.json'
table={}
if tableFile.exists():
 for b in json.loads(tableFile.read_text())['blocks']:
  for c in b.get('result',{}).get('cases',[]):table[c['name']]=c
def differences(rows,refs):
 result={k:0. for k in ['pressureBar','enthalpyKJkg','fluidK','thermalK']}
 for s,t in zip(rows,refs):
  assert s['seconds']==t['seconds']
  for x,y in zip(s['sections'],t['sections']):
   for key,field in [('pressureBar','p'),('enthalpyKJkg','h'),('fluidK','T')]:result[key]=max(result[key],abs(x[field]-y[field]))
  result['thermalK']=max(result['thermalK'],max(abs(x-y) for x,y in zip(s['temperaturesK'],t['temperaturesK'])))
 return result
documents={f.name:json.loads(f.read_text()) for f in sorted(E.glob('*-suite-*.json'))}
def ledger_audit(s,initial):
 led=s['ledger'];faces=led['faces'];thermal=[0.]*10+[led['airLoadKJ']]
 worst=dict(sectionMassKg=0.,globalMassKg=0.,sectionEnergyKJ=0.,nodeEnergyKJ=0.,refrigerantEnergyKJ=0.,thermalEnergyKJ=0.,combinedEnergyKJ=0.)
 fluid=mass=0.
 for i,(x,z) in enumerate(zip(s['sections'],initial['sections'])):
  dm=x['massKg']-z['massKg'];du=x['internalEnergyKJ']-z['internalEnergyKJ'];mass+=dm;fluid+=du
  worst['sectionMassKg']=max(worst['sectionMassKg'],abs(dm-faces[i]['massKg']+faces[i+1]['massKg']))
  worst['sectionEnergyKJ']=max(worst['sectionEnergyKJ'],abs(du-faces[i]['energyKJ']+faces[i+1]['energyKJ']-led['tubeRefrigerantKJ'][i]))
  at,af,ft=led['thermalLinksKJ'][3*i:3*i+3];thermal[10]-=at+af;thermal[2*i]+=at+ft-led['tubeRefrigerantKJ'][i];thermal[2*i+1]+=af-ft
 delta=[c*(x['temperatureK']-y) for c,x,y in zip(capacities,s['nodes'],initial['temperaturesK'])]
 worst['nodeEnergyKJ']=max(abs(x-y) for x,y in zip(delta,thermal))
 worst['globalMassKg']=abs(mass-faces[0]['massKg']+faces[-1]['massKg'])
 fr=fluid-faces[0]['energyKJ']+faces[-1]['energyKJ']-sum(led['tubeRefrigerantKJ']);tr=sum(delta)-led['airLoadKJ']+sum(led['tubeRefrigerantKJ'])
 worst['refrigerantEnergyKJ']=abs(fr);worst['thermalEnergyKJ']=abs(tr);worst['combinedEnergyKJ']=abs(fr+tr)
 return worst
for filename,d in documents.items():
 f=E/filename;r=d.get('result',{})
 for case in r.get('cases',[]):
  maxima={k:0. for k in ['sectionMassKg','globalMassKg','sectionEnergyKJ','thermalNodeKJ','combinedEnergyKJ','refrigerantEnergyKJ','thermalEnergyKJ']};native=[];samples=0
  for run in case['runs']:
   initial=run['initial']
   for s in run['rows']:
    samples+=1;led=s['ledger'];faces=led['faces'];thermal=[0.]*10+[led['airLoadKJ']];fluid=0.;mass=0.
    for i,(x,z) in enumerate(zip(s['sections'],initial['sections'])):
     dm=x['massKg']-z['massKg'];du=x['internalEnergyKJ']-z['internalEnergyKJ'];fluid+=du;mass+=dm
     mr=dm-faces[i]['massKg']+faces[i+1]['massKg'];ur=du-faces[i]['energyKJ']+faces[i+1]['energyKJ']-led['tubeRefrigerantKJ'][i]
     maxima['sectionMassKg']=max(maxima['sectionMassKg'],abs(mr));maxima['sectionEnergyKJ']=max(maxima['sectionEnergyKJ'],abs(ur))
     at,af,ft=led['thermalLinksKJ'][3*i:3*i+3];thermal[10]-=at+af;thermal[2*i]+=at+ft-led['tubeRefrigerantKJ'][i];thermal[2*i+1]+=af-ft
     rho=x['massKg']/(.003/5);n=dict(seconds=s['seconds'],section=i,relativeTolerance=run['relativeTolerance'])
     try:
      a.update(C.DmassT_INPUTS,rho,x['T']+273.15);n.update(pResidualPa=a.p()-x['p']*1e5,hResidualJkg=a.hmass()-x['h']*1000,uResidualJkg=a.umass()-x['internalEnergyKJ']/x['massKg']*1000,phase=int(a.phase()))
     except Exception as e:n['error']=str(e)
     native.append(n)
    thermalChange=[c*(x-y) for c,x,y in zip(capacities,s['temperaturesK'],initial['temperaturesK'])]
    maxima['thermalNodeKJ']=max(maxima['thermalNodeKJ'],max(abs(x-y) for x,y in zip(thermalChange,thermal)))
    gm=mass-faces[0]['massKg']+faces[-1]['massKg'];fluidR=fluid-faces[0]['energyKJ']+faces[-1]['energyKJ']-sum(led['tubeRefrigerantKJ']);thermalR=sum(thermalChange)-led['airLoadKJ']+sum(led['tubeRefrigerantKJ'])
    for key,v in [('globalMassKg',gm),('refrigerantEnergyKJ',fluidR),('thermalEnergyKJ',thermalR),('combinedEnergyKJ',fluidR+thermalR)]:maxima[key]=max(maxima[key],abs(v))
  t=table.get(case['name']);comparison=[{'relativeTolerance':run['relativeTolerance'],'differences':differences(run['rows'],tr['rows'])} for run,tr in zip(case['runs'],t['runs'])] if t else None
  out['operating'].append(dict(file=f.name,status=d['status'],case=case['name'],samples=samples,independentConservation=maxima,conservationPass=all(v<(1e-8 if 'Mass' in k else 1e-6) for k,v in maxima.items()),nativeDT=native,sameTableAcceptedReference=comparison,sameTableComparisonMeaning='Cross-backend property/initial-inventory differences; same-EOS temporal assertions are reported separately.',frozenDirectEOS=case['directEOSComparison'],nominalTemporal=case['nominalTemporalErrors'],tightTemporal=case['tightTemporalErrors'],maxStepRefinement=case['maxStepRefinementErrors']))
 for i,h in enumerate(d.get('histories',[])):
  attempts=h['attempts'];checks=h['rollbackChecks']
  out['historyAudits'].append(dict(file=f.name,model=i,attempts=len(attempts),rejections=sum(v['rejected'] for v in attempts),rollbackChecks=len(checks),rollbackFailures=[v for v in checks if not v['exactPhysicalRollback']],maxAcceptedTemporalError=max([v['error'] for v in attempts if not v['rejected']]+[0]),stopKinds=[v['stop'] for v in h['records'] if v['stop']],records=len(h['records'])))
  initials=h.get('initialRecords');source='direct captured initial inventories/declared node temperatures'
  if not initials and h['records']:
   other=documents.get(filename.replace('chromium-','webkit-') if filename.startswith('chromium-') else filename.replace('webkit-','chromium-'))
   if other and i<len(other.get('histories',[])):
    oh=other['histories'][i]
    if h['records']==oh['records'] and oh.get('initialRecords'):
     initials=oh['initialRecords'];source='other-engine captured initial inventories; complete returned record arrays verified exactly equal'
  if not h['records']:continue
  if not initials:
   out['contractConservation'].append(dict(file=f.name,model=i,status='NOT RUN',reason='Early harness did not capture independent initial inventories; no reconstructed initial state is invented.'));continue
  maxima={};missing=[]
  for j,s in enumerate(h['records']):
   if j>=len(initials) or initials[j] is None:missing.append(j);continue
   residual=ledger_audit(s,initials[j])
   for key,v in residual.items():maxima[key]=max(maxima.get(key,0),v)
  passed=not missing and all(v<(1e-8 if 'Mass' in key else 1e-6) for key,v in maxima.items())
  out['contractConservation'].append(dict(file=f.name,model=i,status='PASS' if passed else 'FAIL' if not missing else 'INCOMPLETE',initialSource=source,records=len(h['records']),missingInitialRows=missing,maxima=maxima))
(E/'independent-scientific-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(out['operating']),'operating audits;',len(out['historyAudits']),'history audits')
