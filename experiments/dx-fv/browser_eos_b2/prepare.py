"""Exact B1 fixtures plus explicitly labelled diagnostic saturation approaches."""
import json,struct
from pathlib import Path
from CoolProp.CoolProp import PropsSI
B=Path(__file__).resolve().parent
old=json.loads((B.parent/'browser_eos/inputs.json').read_text())['requests']
rows=[dict(q,origin='B1 saved fixture') for q in old if q['mode']=='PH' and q['region'] in ['liquid','vapor','two-phase']]
rows.append(dict(id='B1-vapor-regression',mode='PH',args=[799999.9981754856,1624022.744737779],region='vapor',origin='B1 report exact failing binary64'))
for p in [30298.937123458254,350000.,799999.9981754856,3500000.]:
 hf,hg=[PropsSI('Hmass','P',p,'Q',q,'Ammonia') for q in [0,1]]
 ts=PropsSI('T','P',p,'Q',0,'Ammonia')
 for side,h0,sign in [('liquid',hf,-1),('vapor',hg,1)]:
  for dh in [0.,1e-5,.001,.01,1.,100.]:
   rows.append(dict(id=f'approach-{p}-{side}-{dh}',mode='PH',args=[p,h0+sign*dh],region=side,origin='diagnostic native saturation enthalpy offset',saturationSource=dict(version='8.0.0',hf=hf,hg=hg,T=ts)))
 for x in [1e-8,.01,.5,.99,1-1e-8]:
  rows.append(dict(id=f'mixture-{p}-{x}',mode='PH',args=[p,hf+x*(hg-hf)],region='two-phase',origin='diagnostic native coexistence interior'))
for q in rows:q['inputBits']=[struct.pack('>d',x).hex() for x in q['args']]
(B/'inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
print(len(rows),'PH fixtures')
