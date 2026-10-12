"""Exact-rational Bernstein certificate for the frozen binary64 coefficients.

No floating grid is used to certify positivity. Bounds enclose the polynomial
on a physical PT rectangle containing the declared liquid patch. The extension
is only a proof device; it is not a two-phase or metastable property claim.
"""
import hashlib,json,math,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from model import BASE,TERMS,load

Q=lambda v:F(float(v))
def add(a,b):
    c=a.copy()
    for k,v in b.items():c[k]=c.get(k,F(0))+v
    return {k:v for k,v in c.items() if v}
def mul(a,b):
    c={}
    for (i,j),v in a.items():
        for (k,l),w in b.items():c[i+k,j+l]=c.get((i+k,j+l),F(0))+v*w
    return c
def deriv(a,axis,scale):
    c={}
    for (i,j),v in a.items():
        n=(i,j)[axis]
        if n:c[i-(axis==0),j-(axis==1)]=v*n/scale
    return c
def bounds(a,box):
    # Power basis -> Bernstein on arbitrary rational rectangle. All sums,
    # products and combinatorial conversions are exact rational operations.
    nx=max(i for i,j in a);ny=max(j for i,j in a);lx,hx,ly,hy=box
    b={}
    for (i,j),v in a.items():
        for k in range(i+1):
            vx=v*math.comb(i,k)*lx**(i-k)*(hx-lx)**k
            for l in range(j+1):
                b[k,l]=b.get((k,l),F(0))+vx*math.comb(j,l)*ly**(j-l)*(hy-ly)**l
    coeff=[]
    for k in range(nx+1):
        for l in range(ny+1):
            coeff.append(sum(v*F(math.comb(k,i),math.comb(nx,i))*F(math.comb(l,j),math.comb(ny,j)) for (i,j),v in b.items() if i<=k and j<=l))
    return min(coeff),max(coeff)
def envelope(a,subdiv=4,pad=F(0)):
    cells=[]
    for i in range(subdiv):
        for j in range(subdiv):
            cells.append(bounds(a,(-1+F(2*i,subdiv)-pad,-1+F(2*(i+1),subdiv)+pad,-1+F(2*j,subdiv)-pad,-1+F(2*(j+1),subdiv)+pad)))
    return min(a for a,b in cells),max(b for a,b in cells)
def down(x):return float(np.nextafter(float(x),-np.inf))
def up(x):return float(np.nextafter(float(x),np.inf))
def certified(patch):
    t=time.perf_counter();d=patch.d;g={ab:Q(v) for ab,v in zip(TERMS,patch.c)}
    gp=deriv(g,0,Q(patch.ps));gt=deriv(g,1,Q(patch.ts));pp=deriv(gp,0,Q(patch.ps));pt=deriv(gp,1,Q(patch.ts));tt=deriv(gt,1,Q(patch.ts))
    det=add(mul(pp,tt),{k:-v for k,v in mul(pt,pt).items()})
    polys=dict(g=g,gp=gp,gt=gt,gpp=pp,gpt=pt,gtt=tt,det=det)
    env={k:envelope(v,4,F(1,10**10)) for k,v in polys.items()}
    enclosing_env=env.copy()
    # Ts monotonicity and image containment, exactly, including floating
    # evaluation of the coordinate map at frozen source pressure rows.
    sat={(i,0):Q(v) for i,v in enumerate(patch.satc)}
    st=deriv(sat,0,Q(patch.ps));slo,shi=bounds(st,(F(-1)-F(1,10**12),F(1)+F(1,10**12),F(0),F(0)))
    tlo,thi=bounds(sat,(F(-1),F(1),F(0),F(0)))
    # Monotonicity makes endpoint evaluations sharper than raw Bernstein.
    if slo>0:
        tlo=sum(v*(-1-F(1,10**12))**i for (i,j),v in sat.items());thi=sum(v*(1+F(1,10**12))**i for (i,j),v in sat.items())
    rectlo=Q(patch.tc)-Q(patch.ts)*(1+F(1,10**10));recthi=Q(patch.tc)+Q(patch.ts)*(1+F(1,10**10))
    contains=rectlo<=tlo-Q(patch.zmax) and recthi>=thi
    # A coarse enclosing rectangle may include liquid-polynomial extensions
    # far outside the curved domain. Cover the actual patch with thin physical
    # boxes whose T endpoints are bounded by monotone Ts. No grid-only claim.
    leaf_count=0
    if env['gpp'][1]>=0 or env['det'][0]<=0:
        accum={k:[] for k in polys}
        def satval(x):return sum(v*x**i for (i,j),v in sat.items())
        for i in range(64):
            lx=-1+F(2*i,64)-F(1,10**12);hx=-1+F(2*(i+1),64)+F(1,10**12)
            for j in range(8):
                za=Q(patch.zmax)*F(j,8);zb=Q(patch.zmax)*F(j+1,8)
                ly=(satval(lx)-zb-Q(patch.tc))/Q(patch.ts)-F(1,10**10)
                hy=(satval(hx)-za-Q(patch.tc))/Q(patch.ts)+F(1,10**10)
                for k,v in polys.items():accum[k].append(bounds(v,(lx,hx,ly,hy)))
                leaf_count+=1
        env={k:(min(a for a,b in v),max(b for a,b in v)) for k,v in accum.items()}
    boundary_min=env['gpp'][0]+env['gpt'][0]*slo
    # Conservative absolute binary64 evaluation bounds via coefficient sums,
    # coordinate rounding and gamma(100); exact model certificate is separate.
    u=2.**-53;ex=u*(abs(patch.pc-patch.ps)+abs(patch.pc+patch.ps)+2*abs(patch.pc))/patch.ps+4*u
    ey=u*(2*abs(patch.tc)+2*patch.ts)/patch.ts+4*u
    errors={}
    for k,a in polys.items():
        s=float(sum(abs(v)*(F(1)+F(1,10**10))**(i+j) for (i,j),v in a.items()))
        sx=float(sum(abs(v)*i*(F(1)+F(1,10**10))**max(0,i+j-1) for (i,j),v in a.items()))
        sy=float(sum(abs(v)*j*(F(1)+F(1,10**10))**max(0,i+j-1) for (i,j),v in a.items()))
        errors[k]=(100*u/(1-100*u))*s+sx*ex+sy*ey
    # Explicit Hessian product propagation, rather than direct determinant
    # polynomial bound, covers the model evaluator's separate derivative path.
    errors['det']=max(errors['det'],max(abs(float(v)) for v in env['gpp'])*errors['gtt']+max(abs(float(v)) for v in env['gtt'])*errors['gpp']+2*max(abs(float(v)) for v in env['gpt'])*errors['gpt']+4*u*(max(abs(float(v)) for v in env['gpp'])*max(abs(float(v)) for v in env['gtt'])+max(abs(float(v)) for v in env['gpt'])**2))
    valid=contains and env['gp'][0]>Q(errors['gp']) and env['gpp'][1]<-Q(errors['gpp']) and env['gtt'][1]<-Q(errors['gtt']) and env['det'][0]>Q(errors['det'])
    recovery=valid and env['gpt'][0]>Q(errors['gpt']) and boundary_min>0 and slo>0
    # Derived exact positive lower margins over the complete liquid domain.
    cpmin=-(tlo-Q(patch.zmax))*env['gtt'][1]
    cvmin=(tlo-Q(patch.zmax))*env['det'][0]/(-env['gpp'][0])
    kappamin=-env['gpp'][1]/env['gp'][1]
    jmin=100*(tlo-Q(patch.zmax))*env['det'][0]/env['gp'][1]**2
    u_p_min=(tlo-Q(patch.zmax))*env['det'][0]/env['gpt'][1]
    return dict(stabilityCertified=bool(valid),uniqueCanonicalRecoveryOnImage=bool(recovery),
        method='exact rational Bernstein bounds on a padded enclosing rectangle or 64x8 physical boxes covering the curved liquid patch',
        curvedCoverBoxes=leaf_count,coarseEnclosingRectangleBounds={k:[down(a),up(b)] for k,(a,b) in enclosing_env.items()},
        certifiedDomain=dict(pressure=[patch.pc-patch.ps,patch.pc+patch.ps],subcooling=[0,patch.zmax]),
        polynomialBounds={k:[down(a),up(b)] for k,(a,b) in env.items()},
        binary64EvaluationAbsoluteBounds=errors,saturationSlopeBounds=[down(slo),up(shi)],saturationTBounds=[down(tlo),up(thi)],rectangleContainsLiquidDomain=bool(contains),
        positiveMargins=dict(volume=down(env['gp'][0]/100),kappa=down(kappamin),cp=down(cpmin),cv=down(cvmin),hessianDeterminant=down(env['det'][0]),canonicalJacobianAbsolute=down(jmin),isochoricUP=down(u_p_min),boundaryVolumeSlopeTimes100=down(boundary_min)),
        noExistenceClaimOutsideCanonicalImage=True,seconds=time.perf_counter()-t)

if __name__=='__main__':
    start=time.perf_counter();rows={k:certified(c) for k,c in load().items()}
    out=dict(candidateSHA256=hashlib.sha256((BASE/'evidence/candidate.json').read_bytes()).hexdigest(),patches=rows,seconds=time.perf_counter()-start)
    (BASE/'evidence/certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
