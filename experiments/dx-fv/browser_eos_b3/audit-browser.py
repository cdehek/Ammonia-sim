"""Matching-version native DT audit and physical-branch derivative assessment."""
import json,os
from pathlib import Path
import CoolProp
from native import Backend,root,save,bits
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B3_EVIDENCE',B/'evidence'))
backend=Backend();satcache={};rootcache={}
def physical(p,h):
    if p not in satcache:satcache[p]=(backend.state('PQ',p,0),backend.state('PQ',p,1))
    sf,sg=satcache[p];dl=h-sf['h'];dg=h-sg['h'];tol=1e-8
    return ('liquid' if dl < -tol else 'gas' if dg>tol else 'equilibrium' if dl>tol and dg < -tol else 'endpoint-unresolved'),sf,sg
def ref(p,h,phase,sf,sg):
    key=(p,h,phase)
    if key not in rootcache:rootcache[key]=root(p,h,phase,((sf if phase=='liquid' else sg)['rho'],sf['T']))
    return rootcache[key]
out=[]
for file in sorted(E.glob('*.json')):
    if not (file.name.startswith(('chromium-','webkit-')) and file.stem.rsplit('-',1)[-1] in ['official8','build30','build44','official72']):continue
    if (CoolProp.__version__=='7.2.0') != (file.stem.endswith('official72')):continue
    data=json.loads(file.read_text());rows=[]
    for q in data['rows']:
        row=dict(id=q['id'],samples=[],probes=[],inventories={})
        for name,s in [('base',q.get('base'))]+[(str(i),x.get('output')) for i,x in enumerate(q['probes'])]:
            if not s:continue
            p,h=s['p'],s['h'];assert s['inputBits']==[bits(p),bits(h)]
            dt=backend.state('DT',s['state']['rho'],s['state']['T']);phase,sf,sg=physical(p,h)
            row['samples'].append(dict(name=name,physicalPhase=phase,inAcceptedPressureRange=3e4<=p<=35e5,
                independentDT=dt,nativeMinusBrowser={k:dt[k]-s['direct'][k] for k in ['p','h','u']},
                residuals=dict(p=dt['p']-p,h=dt['h']-h)))
        if q.get('base'):
            p,h=q['args'];phase,sf,sg=physical(p,h)
            reference=ref(p,h,phase,sf,sg) if phase in ['liquid','gas'] else None
            for i,probe in enumerate(q['probes']):
                if 'output' not in probe:continue
                s=probe['output'];pp,hh=s['p'],s['h'];probephase,psf,psg=physical(pp,hh)
                pr=dict(axis=probe['axis'],step=probe['step'],actualIncrement=probe['actualIncrement'],physicalBase=phase,physicalProbe=probephase,
                    backendPhaseChanges=probe['crossesPhase'],physicalPhaseCrossing=probephase!=phase)
                if not 3e4<=pp<=35e5:pr['exclusion']='outside accepted pressure domain'
                elif reference is None or probephase!=phase:pr['exclusion']='endpoint, physical coexistence, or physical phase crossing'
                elif not reference['converged']:pr['exclusion']='independent reference did not converge'
                else:
                    analytic=reference['derivatives']['rhoP' if probe['axis']=='P' else 'rhoH'];finite=probe['finite']
                    pr.update(analytic=analytic,finite=finite,ratio=finite/analytic,
                        normalizedMassContamination=abs((finite-analytic)*probe['step'])*(.003/5)/max(.01,reference['state']['rho']*(.003/5)))
                row['probes'].append(pr)
            for kind,inv in q.get('inventories',{}).items():
                if 'DU' not in inv:continue
                du=inv['DU']['values'];dt=backend.state('DT',du['rho'],du['T']);initial=inv['input']['values']
                row['inventories'][kind]=dict(independentDT=dt,independentDUResiduals=dict(p=dt['p']-du['p'],h=dt['h']-du['h'],u=dt['u']-initial['u']),
                    nativeInventoryResiduals=dict(rho=du['rho']-initial['rho'],u=du['u']-initial['u']))
        rows.append(row)
    out.append(dict(file=file.name,rows=rows))
save(E/f'audit-browser-native{CoolProp.__version__}.json',dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,files=out,
    roots=[dict(p=k[0],h=k[1],phase=k[2],reference=v)for k,v in rootcache.items()],
    referenceResidualLimits=dict(p=1e-5,h=1e-8),nonlinearScale=1e-11))
print(CoolProp.__version__,len(out),'files;',sum(len(r['samples'])for f in out for r in f['rows']),'states;',len(rootcache),'independent roots')
