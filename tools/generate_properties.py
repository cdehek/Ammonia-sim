"""Generate the bounded offline HEOS ammonia property grid. Requires CoolProp 7.2.0."""
import sys, json, math
from pathlib import Path
import CoolProp
from CoolProp.CoolProp import PropsSI
assert CoolProp.__version__ == '7.2.0'
ROOT=Path(__file__).resolve().parents[1]
pressures=[.3*math.exp(math.log(35/.3)*i/240) for i in range(241)]
superheats=list(range(0,251,2))
subcools=list(range(0,31))
def props(p,t=None,q=None):
 args=('P',p*1e5,'Q',q,'Ammonia') if q is not None else ('P',p*1e5,'T',t+273.15,'Ammonia')
 return [round(PropsSI(key,*args)/scale,7) for key,scale in [('Hmass',1000),('Smass',1000),('Dmass',1)]]
sat=[]; vapor=[]; liquid=[]
for i,p in enumerate(pressures):
 t=PropsSI('T','P',p*1e5,'Q',0,'Ammonia')-273.15
 f=props(p,q=0);g=props(p,q=1)
 sat.append([round(t,8),*f,*g])
 vapor.append([g if sh==0 else props(p,t+sh) for sh in superheats])
 liquid.append([f if sc==0 else (props(p,t-sc) if t-sc>=-73.15 else None) for sc in subcools])
 if i%60==0:print('Generated pressure row',i,flush=True)
data={'version':'CoolProp 7.2.0 HEOS Ammonia','eos':'Gao, Wu, Bell & Lemmon (2020)','p':pressures,'sh':superheats,'sc':subcools,'sat':sat,'vapor':vapor,'liquid':liquid,'units':{'p':'bar absolute','T':'C','h':'kJ/kg','s':'kJ/(kg K)','rho':'kg/m3'},'limits':{'p':[.3,35],'superheat':[0,250],'subcool':[0,30],'minLiquidT':-73.15}}
(ROOT/'properties.json').write_text(json.dumps(data,separators=(',',':')))
print('Property grid bytes:',(ROOT/'properties.json').stat().st_size)
