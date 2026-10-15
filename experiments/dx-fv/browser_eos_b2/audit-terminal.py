"""Independent native terminal phase/quality/superheat; no new acceptance budget."""
import json, os
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
a=AbstractState('HEOS','Ammonia');sat=AbstractState('HEOS','Ammonia');rows=[]
for f in sorted(E.glob('*-suite-fd-aware-operating-*.json')):
 d=json.loads(f.read_text())
 for case in d.get('result',{}).get('cases',[]):
  for run in case['runs']:
   s=run['rows'][-1];last=s['sections'][-1];reported=s['terminal']
   row=dict(file=f.name,case=case['name'],relativeTolerance=run['relativeTolerance'],seconds=s['seconds'],reported=reported,stop=s['stop'])
   try:
    a.update(C.DmassT_INPUTS,last['massKg']/(.003/5),last['T']+273.15)
    phase=int(a.phase());q=a.Q();q=q if 0<=q<=1 else None
    sat.update(C.PQ_INPUTS,a.p(),1);superheat=max(0,a.T()-sat.T()) if phase in [1,2,3,5] else 0
    row.update(nativePhase=phase,nativeQuality=q,nativeSuperheatK=superheat,qualityDifference=None if q is None or reported['quality'] is None else q-reported['quality'],superheatDifferenceK=superheat-reported['superheatK'])
   except Exception as error:row['error']=str(error)
   rows.append(row)
out=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,referenceOnly=True,newAcceptanceBudget=None,rows=rows)
target=E/'independent-terminal-audit.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print(len(rows),'terminal states,',sum('error'in r for r in rows),'errors; max quality/superheat differences',max(abs(r.get('qualityDifference')or 0)for r in rows),max(abs(r.get('superheatDifferenceK')or 0)for r in rows))
