"""Reconstruct physical budgets, compare frozen EOS trajectories and refinements.

No JavaScript balance/controller implementation is imported by this auditor.
"""
import json,hashlib,math
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2]
refPath=B.parent/'coupled-reference.json';refs=json.loads(refPath.read_text())
a=AbstractState('HEOS','Ammonia');results=[];groups={}
def maxabs(values):return max([0]+[abs(v) for v in values])
def comparisons(rows,reference):
 out={k:0 for k in ['pressureBar','enthalpyKJkg','fluidTemperatureK','thermalTemperatureK']}
 for row,other in zip(rows,reference):
  assert row['seconds']==other['seconds']
  for s,t in zip(row['sections'],other['sections']):
   for field,key in [('p','pressureBar'),('h','enthalpyKJkg'),('T','fluidTemperatureK')]:out[key]=max(out[key],abs(s[field]-t[field]))
  temps=other.get('temperaturesK') or [n['temperatureK'] for n in other['nodes']]
  out['thermalTemperatureK']=max(out['thermalTemperatureK'],maxabs(n['temperatureK']-t for n,t in zip(row['nodes'],temps)))
 return out
for f in sorted(E.glob('*-coupled-*.json')):
 if 'native-state-audit' in f.name:continue
 d=json.loads(f.read_text());groups.setdefault((d['browser'],d['case']),{})[d['relativeTolerance']]=d
 ini=d.get('initial');rows=[r['record'] for r in d['rows']]
 if ini is None:results.append({'file':f.name,'error':d.get('harnessError')});continue
 maxima={k:0 for k in ['sectionMassKg','sectionEnergyKJ','nodeEnergyKJ','globalMassKg','globalEnergyKJ']}
 independent=[];domainExceptions=[]
 for row in rows:
  led=row['ledger'];mass=[];energy=[]
  for i,(s,z) in enumerate(zip(row['sections'],ini['sections'])):
   mr=s['massKg']-z['massKg']-led['faces'][i]['massKg']+led['faces'][i+1]['massKg']
   er=s['internalEnergyKJ']-z['internalEnergyKJ']-led['faces'][i]['energyKJ']+led['faces'][i+1]['energyKJ']-led['tubeRefrigerantKJ'][i]
   mass.append(mr);energy.append(er)
   try:
    a.update(C.DmassT_INPUTS,s['rho'],s['T']+273.15)
    independent.append({'seconds':row['seconds'],'section':i,'x':s['x'],'nativePMinusReportedPa':a.p()-s['p']*1e5,
       'nativeHMinusReportedJkg':a.hmass()-s['h']*1000,'nativeUMinusStoredJkg':a.umass()-s['internalEnergyKJ']/s['massKg']*1000})
   except Exception as exc:domainExceptions.append({'seconds':row['seconds'],'section':i,'error':str(exc)})
  nodes=[0.]*11;nodes[10]=led['airLoadKJ']
  for i in range(5):
   at,af,ft=led['thermalLinksKJ'][3*i:3*i+3];tr=led['tubeRefrigerantKJ'][i]
   nodes[10]-=at+af;nodes[2*i]+=at+ft-tr;nodes[2*i+1]+=af-ft
  nres=[s['energyChangeKJ']-v for s,v in zip(row['nodes'],nodes)]
  fluidChange=sum(s['internalEnergyKJ']-z['internalEnergyKJ'] for s,z in zip(row['sections'],ini['sections']))
  thermalChange=sum(s['energyChangeKJ'] for s in row['nodes'])
  globalEnergy=fluidChange+thermalChange-led['boundaryEnthalpyKJ']-led['airLoadKJ']
  globalMass=sum(s['massKg']-z['massKg'] for s,z in zip(row['sections'],ini['sections']))-led['boundaryMassKg']
  for k,v in [('sectionMassKg',maxabs(mass)),('sectionEnergyKJ',maxabs(energy)),('nodeEnergyKJ',maxabs(nres)),('globalMassKg',abs(globalMass)),('globalEnergyKJ',abs(globalEnergy))]:maxima[k]=max(maxima[k],v)
 target=next(c for c in refs['cases'] if c['name']==d['case'])['runs'][1]
 direct=comparisons(rows,target['samples']) if len(rows)==len(target['samples']) else None
 final=rows[-1] if rows else ini;events=[v for v in final['events'] if v['section']==4 and v['boundary']=='vapor']
 eventRef=target['terminalSaturationEventsSeconds']
 eventError=maxabs(v['seconds']-t for v,t in zip(events,eventRef)) if len(events)==len(eventRef) else None
 trace=d.get('finalStateDiagnostics',{}).get('trace',[])
 rejections=d.get('finalStateDiagnostics',{}).get('rejectionTrace',[])
 item={'file':f.name,'browser':d['browser'],'case':d['case'],'relativeTolerance':d['relativeTolerance'],
   'completedAllSamples':d.get('completedAllSamples',False),'stop':final['stop'],'harnessError':d.get('harnessError'),
   'independentConservation':maxima,'conservationPass':all(v<(1e-8 if 'Mass' in k else 1e-6) for k,v in maxima.items()),
   'frozenDirectEOSComparison':direct,'terminalEventCount':len(events),'referenceTerminalEventCount':len(eventRef),'terminalEventErrorSeconds':eventError,
   'maxAcceptedTemporalError':max([0]+[v['error'] for v in trace]),'acceptedHalfSteps':final['acceptedSteps'],'rejections':final['rejectedSteps'],
   'rejectionKinds':{k:sum(v['kind']==k for v in rejections) for k in sorted({v['kind'] for v in rejections})},
   'maxCanonicalDensityResidual':maxabs(s['densityResidual'] for row in rows for s in row['sections']),
   'maxCanonicalEnergyResidualKJkg':maxabs(s['energyResidual'] for row in rows for s in row['sections']),
   'independentNativeStateMax':{k:maxabs(r[k] for r in independent) for k in ['nativePMinusReportedPa','nativeHMinusReportedJkg','nativeUMinusStoredJkg']},
   'directStateExceptions':domainExceptions,'elapsedSeconds':d['elapsedSeconds'],
   'settings':d.get('settings'),'counts':d.get('finalStateDiagnostics',{}).get('counts'),
   'initialEOSMinusTable':[{k:s[k]-t[k] for k in ['p','h','T','rho']} for s,t in zip(ini['sections'],d['initialTable'])]}
 item['frozenDirectEOSPass']=direct is not None and direct['pressureBar']<1e-4 and direct['enthalpyKJkg']<.05 and direct['fluidTemperatureK']<.01 and direct['thermalTemperatureK']<.01 and eventError is not None and eventError<.001
 results.append(item)
 ip=E/(f.stem+'-native-state-audit.json');ip.write_text(json.dumps({'version':CoolProp.__version__,'git':CoolProp.__gitrevision__,'rows':independent,'exceptions':domainExceptions},indent=2)+'\n')
temporal=[]
for (browser,case),runs in sorted(groups.items()):
 if not all(t in runs and runs[t].get('completedAllSamples') for t in [1e-6,1e-7,1e-8]):continue
 tight=[r['record'] for r in runs[1e-8]['rows']]
 for tol in [1e-6,1e-7]:
  rows=[r['record'] for r in runs[tol]['rows']];diff=comparisons(rows,tight)
  ea,eb=rows[-1]['events'],tight[-1]['events'];matches=len(ea)==len(eb) and all((a['section'],a['boundary'],a['direction'])==(b['section'],b['boundary'],b['direction']) for a,b in zip(ea,eb))
  ee=maxabs(a['seconds']-b['seconds'] for a,b in zip(ea,eb)) if matches else None
  tempLimit=.01 if tol==1e-6 else .001
  temporal.append({'browser':browser,'case':case,'relativeTolerance':tol,'errors':diff,'eventErrorSeconds':ee,'eventIdentitiesMatch':matches,
    'pass':diff['pressureBar']<5e-5 and diff['enthalpyKJkg']<.05 and diff['fluidTemperatureK']<tempLimit and diff['thermalTemperatureK']<tempLimit and matches and ee<.001})
out={'sourceCommit':'be9eb35a4ddf5098e685182f8104685127c6a6ee','frozenReferenceSHA256':hashlib.sha256(refPath.read_bytes()).hexdigest(),
 'configuration':'original finite-difference thermal Jacobian and accepted opt-in failure-aware growth',
 'runs':results,'temporalComparisons':temporal,
 'limits':{'massKg':1e-8,'energyKJ':1e-6,'sameEOSTemporalPressureBar':5e-5,'frozenDirectEOSPressureBar':1e-4,'hKJkg':.05,'nominalK':.01,'tightK':.001,'eventSeconds':.001},
 'qualificationLimit':'Five operating fixtures and temporal refinements only. Not the full A2 verification/domain/rollback/order suite; no multihour or physical-device qualification.'}
(E/'coupled-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(len(results),'runs',sum(r.get('completedAllSamples',False) for r in results),'completed',sum(t['pass'] for t in temporal),'/',len(temporal),'temporal comparisons pass')
