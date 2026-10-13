"""Standalone pinned Python HEOS references. Never alters frozen project data."""
import hashlib,json,platform,sys,time
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as CP
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
FIELDS={'p':'P','T':'T','h':'Hmass','s':'Smass','rho':'Dmass','u':'Umass','Q':'Q'}

def snapshot(a):
    q=dict(p=a.p(),T=a.T(),h=a.hmass(),s=a.smass(),rho=a.rhomass(),u=a.umass(),Q=a.Q())
    if not 0<a.Q()<1:
        q.update(cp=a.cpmass(),cv=a.cvmass(),kappa=a.isothermal_compressibility(),rhoP=a.first_partial_deriv(CP.iDmass,CP.iP,CP.iT),rhoT=a.first_partial_deriv(CP.iDmass,CP.iT,CP.iP),hp=a.first_partial_deriv(CP.iHmass,CP.iP,CP.iT))
    return q

def generate_inputs():
    assert CoolProp.__version__=='7.2.0'
    a=AbstractState('HEOS','Ammonia');sat=AbstractState('HEOS','Ammonia');states=[];requests=[]
    pressures=[.3,.3029893712344606,.3183890254214986,1.,3.5,8.,16.,32.33098463554795,32.65314902038559,32.80473738460169,35.]
    for pbar in pressures:
        p=pbar*1e5;sat.update(CP.PQ_INPUTS,p,0);Ts=sat.T()
        for z in [.001,.1,1.,5.,15.]:
            if Ts-z<200:continue
            a.update(CP.PT_INPUTS,p,Ts-z);states.append(dict(id=f'p{pbar}-liquid-z{z}',region='liquid',state=snapshot(a)))
        for z in [.001,1.,25.,100.,250.]:
            a.update(CP.PT_INPUTS,p,Ts+z);states.append(dict(id=f'p{pbar}-vapor-z{z}',region='vapor',state=snapshot(a)))
        for quality in [0.,1e-8,.2,.5,.99,1.-1e-8,1.]:
            a.update(CP.PQ_INPUTS,p,quality);states.append(dict(id=f'p{pbar}-Q{quality}',region='saturation' if quality in [0,1] else 'two-phase',state=snapshot(a)))
    for row in states:
        s=row['state']
        for mode,args in [('PH',[s['p'],s['h']]),('DU',[s['rho'],s['u']])]:
            requests.append(dict(id=row['id']+'-'+mode,mode=mode,args=args,region=row['region'],origin=row['id']))
        if row['region'] in ['saturation','two-phase']:requests.append(dict(id=row['id']+'-PQ',mode='PQ',args=[s['p'],s['Q']],region=row['region'],origin=row['id']))
        else:requests.append(dict(id=row['id']+'-PT',mode='PT',args=[s['p'],s['T']],region=row['region'],origin=row['id']))
    # Saved exact problem inventories, not regenerated trajectory states.
    old=json.loads((R/'experiments/dx-fv/two_patch/evidence/probes.json').read_text())['rows']
    requests.append(dict(id='historical-low-original-inventory',mode='DU',args=[708.6710262223568,94480.59153610271],region='liquid',historical=True))
    for r in old:
        if 'original' in r:
            requests.append(dict(id=r['name']+'-PH',mode='PH',args=[r['p']*1e5,r['h']*1000],region='liquid',historical=True))
            requests.append(dict(id=r['name']+'-original-DU',mode='DU',args=[r['original']['rho'],r['original']['u']*1000],region='liquid',historical=True))
    # Deterministic phase-boundary sequences and explicit near-saturation guards.
    for p in [30298.93712344606,350000.,3280473.738460169]:
        sat.update(CP.PQ_INPUTS,p,0);hf=sat.hmass();Ts=sat.T();sat.update(CP.PQ_INPUTS,p,1);hg=sat.hmass()
        for edge,h in [('bubble',hf),('dew',hg)]:
            for delta in [-1.,-1e-4,0.,1e-4,1.]:requests.append(dict(id=f'boundary-{p}-{edge}-{delta}',mode='PH',args=[p,h+delta],region='boundary',sequence=True))
        for z in [0.,1e-6,-1e-6]:
            requests.append(dict(id=f'near-saturation-{p}-{z}',mode='PT',args=[p,Ts-z],region='boundary',expectedAmbiguity=True))
        requests.append(dict(id=f'imposed-stable-liquid-{p}',mode='PTliquid',args=[p,Ts-1e-6],region='liquid',highLevelOnly=True))
    # Clearly invalid thermodynamic inputs, not clamped or assigned fake states.
    for id,mode,args in [('negative-P','PH',[-1.,500000.]),('negative-density','DU',[-1.,100000.]),('quality-outside','PQ',[350000.,1.1]),('below-triple-T','PT',[350000.,100.])]:
        requests.append(dict(id=id,mode=mode,args=args,region='invalid',expectedFailure=True))
    (B/'inputs.json').write_text(json.dumps(dict(seedVersion=CoolProp.__version__,seedGit=CoolProp.__gitrevision__,units='SI, mass-based, default HEOS energy reference',states=states,requests=requests),indent=2,allow_nan=False)+'\n')

if len(sys.argv)>1 and sys.argv[1]=='seed':generate_inputs()
inputs=json.loads((B/'inputs.json').read_text());rows=[];a=AbstractState('HEOS','Ammonia');start=time.perf_counter()
for r in inputs['requests']:
    row=dict(id=r['id'],mode=r['mode'])
    try:
        x,y=r['args'];mode=r['mode'];a.unspecify_phase()
        if mode=='PTliquid':a.specify_phase(CP.iphase_liquid);a.update(CP.PT_INPUTS,x,y)
        elif mode=='PH':a.update(CP.HmassP_INPUTS,y,x)
        elif mode=='DU':a.update(CP.DmassUmass_INPUTS,x,y)
        elif mode=='PQ':a.update(CP.PQ_INPUTS,x,y)
        elif mode=='PT':a.update(CP.PT_INPUTS,x,y)
        row['state']=snapshot(a)
        s=row['state'];row['workIdentityJkg']=s['h']-s['u']-s['p']/s['rho']
        # High-level independent entry path, same model, same physical inputs.
        if len(rows)%19==0 or r.get('historical'):
            keys,vals={'PH':(['P','Hmass'],[x,y]),'DU':(['Dmass','Umass'],[x,y]),'PQ':(['P','Q'],[x,y]),'PT':(['P','T'],[x,y]),'PTliquid':(['P','T|liquid'],[x,y])}[mode]
            row['highLevelDifferences']={k:CP.PropsSI(v,keys[0],vals[0],keys[1],vals[1],'HEOS::Ammonia')-s[k] for k,v in FIELDS.items()}
    except Exception as exc:row['error']=str(exc)
    rows.append(row)
output=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,Python=platform.python_version(),inputsSHA256=hashlib.sha256((B/'inputs.json').read_bytes()).hexdigest(),defaultReferenceUnchanged=True,backend='HEOS::Ammonia',rows=rows,seconds=time.perf_counter()-start)
(E/f'python-{CoolProp.__version__}.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
print(CoolProp.__version__,len(rows),'requests',sum('error'in r for r in rows),'errors',output['seconds'],'seconds',flush=True)
