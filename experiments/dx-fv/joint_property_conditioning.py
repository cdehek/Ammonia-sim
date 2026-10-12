"""Static root/thermodynamic identity checks of existing property surfaces."""
import ast
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import PchipInterpolator
from CoolProp.CoolProp import PropsSI

ROOT=Path(__file__).resolve().parents[2];E=Path(sys.argv[1]).resolve()
assert not E.is_relative_to(ROOT)
source=ROOT/'experiments/dx-fv/joint_property_analysis.py';tree=ast.parse(source.read_text());prefix=[]
for node in tree.body:
    if isinstance(node,ast.If) and ast.unparse(node.test)=="MODE == 'prepare'":break
    prefix.append(node)
else:raise AssertionError('Missing diagnostic-definition boundary')
argv=sys.argv;sys.argv=[str(source),'analyze',str(E)];ns={'__file__':str(source)}
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(source),'exec'),ns);sys.argv=argv
S=ns['surface'];D=ns['DATA'];curve=PchipInterpolator(np.log(D['p']),np.array(D['sat'])[:,0],extrapolate=False)
points=json.loads((E/'properties.json').read_text())['points'];out=[]
def partials(p,z,rho):
    i,w=S.bracket(p);axis,hc,rc=S.curves(p,'liquid')
    j=min(len(axis)-2,max(0,int(np.searchsorted(axis,z,side='right')-1)));v=(z-axis[j])/(axis[j+1]-axis[j])
    a,b=np.array(D['liquid'][i][:len(axis)]),np.array(D['liquid'][i+1][:len(axis)])
    interp=lambda row,col:row[j,col]+v*(row[j+1,col]-row[j,col])
    ha,hb=interp(a,0),interp(b,0)
    la,lb=interp(np.log(a[:,2:3]),0),interp(np.log(b[:,2:3]),0)
    width=(S.x[i+1]-S.x[i])*p
    return (hb-ha)/width,(hc[j+1]-hc[j])/(axis[j+1]-axis[j]),rho*(lb-la)/width,rho*(rc[j+1]-rc[j])/(axis[j+1]-axis[j])
names=['liquid-p0.3029893712344606-sc1.0','liquid-p1.0-sc0.1','saved-five-linear-0']
for name in names:
    row=next(p for p in points if p['name']==name);a=row['originalPH']['state'];rho=a['rho'];u=a['h']-100*a['p']/rho;p=a['p']
    residual=lambda q:S.from_density(q,rho)['u']-u
    sample_pressures=sorted(set([p]+[p+d for d in np.linspace(-.002,.018,2001) if .3<=p+d<=35]+[p+d for d in [-1e-7,-1e-8,1e-8,1e-7]]))
    samples=[dict(p=q,residualKJkg=residual(q)) for q in sample_pressures]
    roots=[]
    for a,b in zip(samples,samples[1:]):
        if a['residualKJkg']*b['residualKJkg']<0:
            q=brentq(residual,a['p'],b['p'],xtol=1e-12,rtol=1e-14)
            if not roots or abs(q-roots[-1])>1e-8:roots.append(q)
    z=S.from_ph(p,row['h'])['offsetK'];hp,hz,rp,rz=partials(p,z,rho)
    i,w=S.bracket(p);tslope=(S.rows[i+1,0]-S.rows[i,0])/((S.x[i+1]-S.x[i])*p)
    pslope=float(curve.derivative()(np.log(p)))/p
    identities={}
    for label,T,slope in [('original',S.saturation(p)['T']-z,tslope),('pchip',float(curve(np.log(p)))-z,pslope)]:
        hP=hp+hz*slope;rhoP=rp+rz*slope;rhoT=-rz
        rhs=100*(1/rho+(T+273.15)*rhoT/rho**2)
        identities[label]=dict(temperatureC=T,saturationSlopeKBar=slope,
            hPressureSlopeAtFixedTKJkgBar=hP,maxwellRHSKJkgBar=rhs,maxwellMismatchKJkgBar=hP-rhs,
            rhoPressureSlopeAtFixedTKgM3Bar=rhoP,isothermalCompressibilityPerBar=rhoP/rho)
    T=row['eos']['T']+273.15
    hP=100*PropsSI('d(Hmass)/d(P)|T','P',p*1e5,'T',T,'Ammonia')
    rhoP=1e5*PropsSI('d(Dmass)/d(P)|T','P',p*1e5,'T',T,'Ammonia')
    rhoT=PropsSI('d(Dmass)/d(T)|P','P',p*1e5,'T',T,'Ammonia');re=PropsSI('Dmass','P',p*1e5,'T',T,'Ammonia')
    rhs=100*(1/re+T*rhoT/re**2)
    identities['directEOS']=dict(hPressureSlopeAtFixedTKJkgBar=hP,maxwellRHSKJkgBar=rhs,maxwellMismatchKJkgBar=hP-rhs,
        rhoPressureSlopeAtFixedTKgM3Bar=rhoP,isothermalCompressibilityPerBar=rhoP/re)
    # One-sided slopes distinguish derivative kinks from a central average.
    eps=1e-7;f=residual(p)
    slopes=dict(leftKJkgBar=(f-residual(p-eps))/eps,rightKJkgBar=(residual(p+eps)-f)/eps)
    out.append(dict(name=name,densityKgM3=rho,UKJkg=u,tableRootSamples=samples,tableRootsBar=roots,
                    oneSidedIsochoricUSlopes=slopes,thermodynamicIdentities=identities))
scan=[]
for i in range(len(D['p'])-1):
    for j in range(17):
        p=(35. if i==len(D['p'])-2 else D['p'][i+1]) if j==16 else D['p'][i] if j==0 else float(np.exp(S.x[i]+(S.x[i+1]-S.x[i])*j/16))
        truth=ns['sat'](p)['T'];linear=S.saturation(p)['T'];candidate=float(curve(np.log(p)))
        scan.append(dict(p=p,originalErrorK=linear-truth,candidateErrorK=candidate-truth))
stats={}
for label in ['original','candidate']:
    values=np.array([r[label+'ErrorK'] for r in scan]);stats[label]=dict(maximumAbsoluteK=float(max(abs(values))),rmsK=float(np.sqrt(np.mean(values*values))))
(E/'conditioning.json').write_text(json.dumps(dict(diagnosticOnly=True,points=out,temperatureScan=scan,temperatureScanStats=stats,completed=True),indent=2)+'\n')
print(json.dumps([dict(name=r['name'],roots=r['tableRootsBar'],identities=r['thermodynamicIdentities']) for r in out]))
