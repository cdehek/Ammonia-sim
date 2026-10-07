import sys,json,random,math
from pathlib import Path
from CoolProp.CoolProp import PropsSI as CP
root=Path(__file__).resolve().parents[1]
rng=random.Random(20261007)
def point(p,T=None,Q=None):
 args=('P',p*1e5,'Q',Q,'Ammonia') if Q is not None else ('P',p*1e5,'T',T+273.15,'Ammonia')
 return dict(p=p,T=CP('T',*args)-273.15,h=CP('H',*args)/1000,s=CP('S',*args)/1000,rho=CP('D',*args))
props=[]
for i in range(400):
 p=math.exp(rng.uniform(math.log(.35),math.log(30)))
 t=CP('T','P',p*1e5,'Q',0,'Ammonia')-273.15
 sh=rng.uniform(0,220)
 props.append(dict(kind='vapor',ref=point(p,t+sh)))
for i in range(160):
 p=rng.uniform(3,30);t=CP('T','P',p*1e5,'Q',0,'Ammonia')-273.15
 props.append(dict(kind='liquid',ref=point(p,t-rng.uniform(.01,20))))
saturations=[dict(p=p,T=CP('T','P',p*1e5,'Q',0,'Ammonia')-273.15) for p in [math.exp(rng.uniform(math.log(.35),math.log(30))) for _ in range(160)]]
cycles=[]
for i in range(160):
 c=dict(system='dx' if i%4 else 'flooded',pressure=rng.uniform(.8,6),condensing=rng.uniform(11,22),ambient=5,evapSH=rng.uniform(0,15) if i%4 else 0,lineSH=rng.uniform(0,8),subcool=rng.uniform(2,10),suctionDrop=rng.uniform(0,.15),liquidDrop=0,etaIs=rng.uniform(60,95),etaMotor=rng.uniform(80,99),massFlow=rng.uniform(.01,.5),flowMode='mass')
 pe=c['pressure']+c['suctionDrop'];pl=c['pressure'];ph=c['condensing']
 te=CP('T','P',pe*1e5,'Q',1,'Ammonia')-273.15
 eo=point(pe,te+c['evapSH']) if c['evapSH'] else point(pe,Q=1)
 Td=CP('T','P',pl*1e5,'H',eo['h']*1000,'Ammonia')-273.15
 su=point(pl,Td+c['lineSH']);h2s=CP('H','P',ph*1e5,'S',su['s']*1000,'Ammonia')/1000
 h2=su['h']+(h2s-su['h'])/(c['etaIs']/100)
 T2=CP('T','P',ph*1e5,'H',h2*1000,'Ammonia')-273.15
 tc=CP('T','P',ph*1e5,'Q',0,'Ammonia')-273.15;liq=point(ph,tc-c['subcool'])
 q=eo['h']-liq['h'];w=h2-su['h'];m=c['massFlow'];Q=m*q;W=m*w;el=W/(c['etaMotor']/100)
 cycles.append(dict(config=c,ref=dict(T2=T2,Q=Q,electrical=el,COP=Q/el,Qcond=m*(h2-liq['h']),flash=CP('Q','P',pe*1e5,'H',liq['h']*1000,'Ammonia'))))
(root/'tests/reference-cases.json').write_text(json.dumps(dict(properties=props,saturation=saturations,cycles=cycles),separators=(',',':')))
print('Direct-CoolProp fixtures:',len(props),'single-phase states,',len(saturations),'saturation states,',len(cycles),'cycles')
