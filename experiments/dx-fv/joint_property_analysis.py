"""Diagnostic mathematics for the EXISTING frozen bilinear property surfaces.

No new interpolation candidate, solver substitution or accepted reference write.
Exact analytical inversions here only separate native iteration precision from
the existing representation. Component swaps are static EOS comparisons, not
new selectable properties or coupled integration paths.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
import CoolProp
from CoolProp import AbstractState, HmassP_INPUTS, DmassUmass_INPUTS, DmassT_INPUTS, PQ_INPUTS
from CoolProp.CoolProp import PropsSI
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[2]
MODE,E=sys.argv[1],Path(sys.argv[2]).resolve()
assert MODE in ('prepare','analyze') and not E.is_relative_to(ROOT)
DATA=json.loads((ROOT/'properties.json').read_text())
eos=AbstractState('HEOS','Ammonia')
assert CoolProp.__version__=='7.2.0'

def snapshot():
    q=eos.Q()
    return dict(p=eos.p()/1e5,h=eos.hmass()/1000,T=eos.T()-273.15,rho=eos.rhomass(),u=eos.umass()/1000,
                quality=q if 0<=q<=1 else None)
def ph(p,h):eos.update(HmassP_INPUTS,h*1000,p*1e5);return snapshot()
def sat(p):
    eos.update(PQ_INPUTS,p*1e5,0);f=snapshot();sf=eos.smass()/1000
    eos.update(PQ_INPUTS,p*1e5,1);g=snapshot();sg=eos.smass()/1000
    return dict(T=f['T'],hf=f['h'],hg=g['h'],rhof=f['rho'],rhog=g['rho'],sf=sf,sg=sg)
def du(rho,u):
    try:eos.update(DmassUmass_INPUTS,rho,u*1000)
    except ValueError as error:
        if 'Input vapor quality' not in str(error):raise
        # The already established independent-reference fallback, unchanged.
        def residual(T):eos.update(DmassT_INPUTS,rho,T);return eos.umass()-u*1000
        T=brentq(residual,200,600,xtol=1e-10);eos.update(DmassT_INPUTS,rho,T)
        assert abs(eos.umass()/1000-u)<1e-7
        return dict(**snapshot(),directDUFailure=str(error),existingDTFallback=True)
    return dict(**snapshot(),existingDTFallback=False)

class ExistingSurface:
    def __init__(self):
        self.p=np.array(DATA['p']);self.x=np.log(self.p);self.rows=np.array(DATA['sat'])
    def bracket(self,p):
        assert .3<=p<=35
        i=min(len(self.p)-2,max(0,int(np.searchsorted(self.p,p,side='right')-1)))
        return i,(math.log(p)-self.x[i])/(self.x[i+1]-self.x[i])
    def saturation(self,p):
        i,w=self.bracket(p);a,b=self.rows[i:i+2]
        l=lambda j:float(a[j]+w*(b[j]-a[j]));g=lambda j:math.exp(math.log(a[j])+w*(math.log(b[j])-math.log(a[j])))
        return dict(T=l(0),hf=l(1),hg=l(4),sf=l(2),sg=l(5),rhof=g(3),rhog=g(6))
    def curves(self,p,kind):
        i,w=self.bracket(p);axis=DATA['sc' if kind=='liquid' else 'sh']
        pairs=[(z,a,b) for z,a,b in zip(axis,DATA[kind][i],DATA[kind][i+1]) if a is not None and b is not None]
        z=np.array([v[0] for v in pairs]);a=np.array([v[1] for v in pairs]);b=np.array([v[2] for v in pairs])
        return z,a[:,0]+w*(b[:,0]-a[:,0]),np.log(a[:,2])+w*(np.log(b[:,2])-np.log(a[:,2]))
    def branch(self,p,z,kind):
        axis,h,r=self.curves(p,kind);assert axis[0]<=z<=axis[-1]
        return dict(h=float(np.interp(z,axis,h)),rho=math.exp(float(np.interp(z,axis,r))))
    def from_ph(self,p,h):
        a=self.saturation(p)
        if a['hf']<=h<=a['hg']:
            q=(h-a['hf'])/(a['hg']-a['hf']);rho=1/((1-q)/a['rhof']+q/a['rhog']);T=a['T'];z=0.
        else:
            kind='liquid' if h<a['hf'] else 'vapor';axis,hc,rc=self.curves(p,kind)
            assert min(hc)<=h<=max(hc)
            z=float(np.interp(-h,-hc,axis)) if kind=='liquid' else float(np.interp(h,hc,axis))
            rho=math.exp(float(np.interp(z,axis,rc)));T=a['T']+(-z if kind=='liquid' else z);q=None
        return dict(p=p,h=h,rho=rho,u=h-100*p/rho,T=T,quality=q,offsetK=z)
    def from_density(self,p,rho):
        a=self.saturation(p)
        if a['rhog']<=rho<=a['rhof']:
            q=(1/rho-1/a['rhof'])/(1/a['rhog']-1/a['rhof']);h=a['hf']+q*(a['hg']-a['hf']);T=a['T'];z=0.
        else:
            kind='liquid' if rho>a['rhof'] else 'vapor';axis,hc,rc=self.curves(p,kind);r=math.log(rho)
            assert min(rc)<=r<=max(rc)
            z=float(np.interp(r,rc,axis)) if kind=='liquid' else float(np.interp(-r,-rc,axis))
            h=float(np.interp(z,axis,hc));T=a['T']+(-z if kind=='liquid' else z);q=None
        return dict(p=p,h=h,rho=rho,u=h-100*p/rho,T=T,quality=q,offsetK=z)
    def exact_du(self,rho,u,guess):
        def residual(p):return self.from_density(p,rho)['u']-u
        # Multiple mathematical roots are possible on this EXISTING surface.
        # Resolve the nearest local branch before any wide diagnostic bracket;
        # a distant root must never be labeled native iteration error.
        fg=residual(guess)
        if abs(fg)<1e-13:return dict(**self.from_density(guess,rho),diagnosticRootScope='local')
        for width in [1e-8,1e-7,1e-6,1e-5,1e-4]:
            roots=[]
            for a,b in [(max(.3,guess-width),guess),(guess,min(35,guess+width))]:
                try:fa,fb=residual(a),residual(b)
                except AssertionError:continue
                if fa*fb<0:roots.append(brentq(residual,a,b,xtol=1e-12,rtol=1e-14))
            if roots:
                p=min(roots,key=lambda p:abs(p-guess));return dict(**self.from_density(p,rho),diagnosticRootScope='local')
        # Search only supported intervals of the original surface; do not clamp
        # or bridge unsupported portions. This local diagnostic never runs in JS.
        probes=sorted(set([float(p) for p in self.p if .3<=p<=35]+[guess]+[max(.3,guess-.2),min(35,guess+.2)]))
        probes.sort(key=lambda p:abs(p-guess));valid=[]
        for p in probes:
            try:v=residual(p)
            except AssertionError:continue
            if abs(v)<1e-13:return dict(**self.from_density(p,rho),diagnosticRootScope='remote')
            valid.append((p,v));ordered=sorted(valid)
            for (a,fa),(b,fb) in zip(ordered,ordered[1:]):
                if fa*fb<0:
                    try:root=brentq(residual,a,b,xtol=1e-12,rtol=1e-14)
                    except AssertionError:continue
                    return dict(**self.from_density(root,rho),diagnosticRootScope='remote')
        raise ValueError('No supported original-surface diagnostic bracket')

surface=ExistingSurface()
def save(name,value):(E/name).write_text(json.dumps(value,indent=2)+'\n')

if MODE=='prepare':
    points=[]
    def add(name,p,h,region):
        try:truth=ph(p,h);s=sat(p)
        except ValueError as error:raise RuntimeError((name,error))
        points.append(dict(name=name,p=p,h=h,region=region,eos=truth,saturationEOS=s))
    pressures=[.3,.3029893712344606,1.,2.5,3.5,3.65,8.,16.,32.65314902038559,35.]
    for p in pressures:
        s=sat(p)
        for z in [.1,.5,1.,5.,15.,30.]:
            T=s['T']-z
            if T<-73.15:continue
            add(f'liquid-p{p}-sc{z}',p,PropsSI('Hmass','P',p*1e5,'T',T+273.15,'Ammonia')/1000,'liquid')
        for q in [0.,.5,1.]:add(f'saturation-p{p}-q{q}',p,s['hf']+q*(s['hg']-s['hf']),'saturated')
        for z in [5.,40.,150.]:add(f'vapor-p{p}-sh{z}',p,PropsSI('Hmass','P',p*1e5,'T',s['T']+273.15+z,'Ammonia')/1000,'vapor')
    for n,mesh in [(5,'five'),(9,'nine')]:
        for mode in ['linear','pchip']:
            run=json.loads((E/f'liquid-{mesh}-{mode}.json').read_text())['run']
            for j,row in enumerate([run['initial']]+run['rows']):
                v=row['sections'][-1];add(f'saved-{mesh}-{mode}-{j}',v['p'],v['h'],'saved-liquid')
    save('property-inputs.json',dict(points=points,versions=dict(CoolProp=CoolProp.__version__)))
    print(json.dumps(dict(prepared=len(points))))
    raise SystemExit

samples=json.loads((E/'properties.json').read_text())['points'];results=[];failures=[]
for row in samples:
    if not row['originalPH']['success']:
        failures.append(dict(name=row['name'],path='PH',evidence=row['originalPH']));continue
    a,b=row['originalPH']['state'],row['candidatePH']['state'];s=row['saturationEOS'];rho,u=a['rho'],a['h']-100*a['p']/a['rho']
    try:
        exact=surface.from_ph(row['p'],row['h']);inverted=surface.exact_du(rho,u,row['p']);truth_mu=du(rho,u)
    except (ValueError,AssertionError) as error:
        failures.append(dict(name=row['name'],path='diagnostic-DU',message=str(error)));continue
    original=row['originalRecovery'];native_p=original['state']['p'] if original['success'] else None
    r=dict(name=row['name'],region=row['region'],p=row['p'],h=row['h'],
        originalTemperatureErrorK=a['T']-row['eos']['T'],candidateTemperatureErrorK=b['T']-row['eos']['T'],
        densityRelativeError=rho/row['eos']['rho']-1,
        exactExistingSurface=exact,exactExistingDU=inverted,EOSAtSameDU=truth_mu,
        nativePHMinusExactTemperatureK=a['T']-exact['T'],nativePHMinusExactDensityRelative=rho/exact['rho']-1,
        tablePressureMinusEOSBar=row['p']-truth_mu['p'],
        nativeDUMinusExactPressureBar=None if native_p is None or inverted['diagnosticRootScope']!='local' else native_p-inverted['p'],
        nativeDUFailure=None if original['success'] else original,
        saturationTemperatureBiasK=row['originalSaturation']['T']-s['T'],
        saturationLiquidEnthalpyBiasKJkg=row['originalSaturation']['hf']-s['hf'])
    if row['region'] in ('liquid','saved-liquid') and exact['offsetK']<1 and exact['offsetK']>0:
        z=exact['offsetK'];ze=s['T']-row['eos']['T'];tab_correct=surface.branch(row['p'],ze,'liquid')['rho']
        hf=surface.saturation(row['p'])['hf'];slope=hf-surface.branch(row['p'],1.,'liquid')['h']
        anchor=(hf-s['hf'])/slope;other=(s['hf']-row['h'])/slope-ze
        eos_at_offset=PropsSI('Dmass','P',row['p']*1e5,'T',s['T']-z+273.15,'Ammonia')
        rhof=surface.saturation(row['p'])['rhof'];factor=tab_correct/rhof
        density_anchor=(rhof-s['rhof'])*factor;density_shape=s['rhof']*factor-row['eos']['rho']
        def static_pressure(rho_value):return du(rho_value,row['h']-100*row['p']/rho_value)['p']
        r['liquidComponents']=dict(tableOffsetK=z,EOSOffsetK=ze,
            offsetErrorK=z-ze,enthalpyAnchorOffsetErrorK=anchor,otherEnthalpyShapeOffsetErrorK=other,
            densitySurfaceErrorKgM3=tab_correct-row['eos']['rho'],enthalpyOffsetDensityEffectKgM3=exact['rho']-tab_correct,
            saturatedDensityAnchorEffectKgM3=density_anchor,otherDensityShapeEffectKgM3=density_shape,
            nativePHInversionDensityEffectKgM3=rho-exact['rho'],
            pressureIfOnlyEOSOffsetUsedBar=static_pressure(tab_correct),
            pressureIfOnlyEOSDensitySurfaceUsedBar=static_pressure(eos_at_offset),
            pressureIfBothEOSUsedBar=static_pressure(row['eos']['rho']))
    results.append(r)

decomposition=[]
for n,name in [(5,'five'),(9,'nine')]:
    reference=json.loads((E/f'liquid-{name}-eos-fine.json').read_text())
    for kind in ['linear','pchip']:
        run=json.loads((E/f'liquid-{name}-{kind}.json').read_text())['run']
        for row,ref in zip([run['initial']]+run['rows'],reference['samples']):
            c=row['sections'][-1];rho=c['massKg']/c['volumeM3'];u=c['internalEnergyKJ']/c['massKg'];p=c['p']
            exact=surface.exact_du(rho,u,p);flash=du(rho,u);eos_trajectory=ref['sections'][-1]
            terms=dict(nativeInversion=p-exact['p'],constitutive=exact['p']-flash['p'],trajectory=flash['p']-eos_trajectory['p'])
            assert abs(sum(terms.values())-(p-eos_trajectory['p']))<1e-12
            delta=.001
            uplus=PropsSI('Umass','Dmass',rho,'P',(flash['p']+delta)*1e5,'Ammonia')/1000
            uminus=PropsSI('Umass','Dmass',rho,'P',(flash['p']-delta)*1e5,'Ammonia')/1000
            h_at_p=PropsSI('Hmass','Dmass',rho,'P',p*1e5,'Ammonia')/1000
            u_at_p=h_at_p-100*p/rho
            volume_flash=du(c['massKg']/(.003/n),u)
            decomposition.append(dict(sectionCount=n,interpolation=kind,seconds=row['seconds'],tableState=c,
                canonicalDensityKgM3=rho,canonicalUKJkg=u,exactExistingTable=exact,EOSAtSameDU=flash,
                EOSTrajectory=eos_trajectory,pressureErrorBar=p-eos_trajectory['p'],termsBar=terms,
                EOSIsochoricDUDpKJkgBar=(uplus-uminus)/(2*delta),EOSUMismatchAtTablePressureKJkg=u_at_p-u,
                uniformVolumeConventionEffectBar=volume_flash['p']-flash['p']))

knots=[]
for i in range(0,len(DATA['p']),12):
    p=min(35.,DATA['p'][i]);s=sat(p);table=DATA['sat'][i]
    knots.append(dict(index=i,p=p,temperatureErrorK=table[0]-s['T'],hfErrorKJkg=table[1]-s['hf'],hgErrorKJkg=table[4]-s['hg'],
        rhofErrorKgM3=table[3]-s['rhof'],rhogErrorKgM3=table[6]-s['rhog'],
        gibbsMismatchKJkg=(table[4]-table[1])-(table[0]+273.15)*(table[5]-table[2])))
coverage=dict(pressureMinimumBar=math.inf,pressureMaximumBar=0.,liquidStates=0,twoPhaseStates=0,vaporStates=0,minimumWetQuality=1.)
frozen=json.loads((ROOT/'experiments/dx-fv/coupled-reference.json').read_text())
for case in frozen['cases']:
    for row in case['runs'][1]['samples']:
        for v in row['sections']:
            coverage['pressureMinimumBar']=min(coverage['pressureMinimumBar'],v['p']);coverage['pressureMaximumBar']=max(coverage['pressureMaximumBar'],v['p'])
            if v['quality'] is not None:
                coverage['twoPhaseStates']+=1;coverage['minimumWetQuality']=min(coverage['minimumWetQuality'],v['quality'])
            elif v['h']<sat(v['p'])['hf']:coverage['liquidStates']+=1
            else:coverage['vaporStates']+=1
save('analysis.json',dict(diagnosticOnly=True,points=results,failures=failures,pressureDecomposition=decomposition,
    frozenKnotChecks=knots,acceptedFixtureCoverage=coverage,versions=dict(CoolProp=CoolProp.__version__,NumPy=np.__version__),completed=True))
print(json.dumps(dict(completed=True,analyzed=len(results),failures=len(failures),acceptedFixtureCoverage=coverage)))
