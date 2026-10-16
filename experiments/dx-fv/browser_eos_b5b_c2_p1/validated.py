"""Uniform contraction/Krawczyk diagnostic; no physical-branch success flag.

For F(x,t), fixed exact rational nonsingular C, T_t(x)=x-C F(x,t).
K=x0-C F(x0,P)+(I-C J(X,P))(X-x0). If K is strictly inside
closed convex X and ||I-C J||_infinity<1, Banach proves a unique root in X
for every t in P. All calculations below are Arb enclosures; a point inverse
only proposes C. Parameter inclusion is uniform, not midpoint transfer.
"""
from fractions import Fraction as F
from flint import ctx, arb
from eos_interval import eos, ball, serialize, stability

class EnclosureFailure(ArithmeticError):
    def __init__(self,message,evidence):
        super().__init__(message)
        self.evidence=evidence

def interval(a,b):
    return ball(F(a)).union(ball(F(b)))

def sat_system(x,T):
    l,v = eos(x[0],T),eos(x[1],T)
    residual = [(l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6]
    jac = [[l['pr']/10**6,-v['pr']/10**6],
           [l['gr']/10**6,-v['gr']/10**6]]
    return residual,jac,l,v

def fractions(rl,rv,d):
    if not (rl > rv and rv > 0 and d > 0):
        raise ArithmeticError('nonpositive/overlapping endpoint density boxes')
    den = d*(rl-rv)
    return (rl-d)*rv/den,(d-rv)*rl/den

def mix_system(x,d,u,mode):
    rl,rv,T=x
    residual,jac,l,v=sat_system([rl,rv],T)
    q,w=fractions(rl,rv,d)
    du=v['u']-l['u']
    energy=(l['u']-u)+q*du if mode=='liquid' else (v['u']-u)-w*du
    dv=1/rv-1/rl
    # Analytic derivatives of the exactly eliminated volume equation.
    qr=w/(rl**2*dv)
    qv=q/(rv**2*dv)
    jac[0].append((l['pt']-v['pt'])/10**6)
    jac[1].append((l['gt']-v['gt'])/10**6)
    jac.append([(w*l['ur']+du*qr)/10**6,
                (q*v['ur']+du*qv)/10**6,
                (w*l['cv']+q*v['cv'])/10**6])
    return residual+[energy/10**6],jac,l,v

def matvec(A,x):
    return [sum((a*b for a,b in zip(row,x)),arb(0)) for row in A]

def determinant(A):
    if len(A)==1:return A[0][0]
    return sum(((-1)**j*A[0][j]*determinant([r[:j]+r[j+1:] for r in A[1:]])
                for j in range(len(A))),arb(0))

def prove(centers,radii,Cvalues,system,precision=256):
    ctx.prec=precision
    centers,radii=list(map(F,centers)),list(map(F,radii))
    if any(r<=0 for r in radii):raise ArithmeticError('nonpositive radius')
    x0=list(map(ball,centers))
    X=[interval(c-r,c+r) for c,r in zip(centers,radii)]
    n=len(X)
    if not (X[0]>X[1] and X[1]>0):raise ArithmeticError('density separation invalid')
    C=[[ball(F(v)) for v in row] for row in Cvalues]
    if determinant(C).contains(0):raise ArithmeticError('preconditioner nonsingularity unproved')
    f0,_,_,_=system(x0)
    residual,J,l,v=system(X)
    if not all(a.is_finite() for a in residual+f0+[v for row in J for v in row]):
        raise ArithmeticError('nonfinite residual/Jacobian')
    A=[[ball(int(i==j))-sum((C[i][k]*J[k][j] for k in range(n)),arb(0))
        for j in range(n)] for i in range(n)]
    # Exact rational upper row sums of interval absolute-value bounds.
    norm=max(sum(F(str(abs(a).upper().fmpq())) for a in row) for row in A)
    corr=matvec(C,f0)
    offset=[interval(-r,r) for r in radii]
    tail=matvec(A,offset)
    K=[x0[i]-corr[i]+tail[i] for i in range(n)]
    strict=all(k>ball(c-r) and k<ball(c+r) for k,c,r in zip(K,centers,radii))
    proof=dict(method='uniform fixed-preconditioner contraction / Krawczyk',
        precisionBits=precision,rootExists=False,uniqueWithinBox=False,
        box=[serialize(x) for x in X],fullResidual=[serialize(f) for f in residual],
        centerResidual=[serialize(f) for f in f0],wholeBoxJacobian=[[serialize(a) for a in row] for row in J],
        preconditioner=[[str(F(v)) for v in row] for row in Cvalues],
        preconditionerDeterminant=serialize(determinant(C)),
        krawczyk=[serialize(k) for k in K],contractionNormUpper=str(norm),
        strictInclusion=strict,densitySeparation=serialize(X[0]-X[1]),
        globalEquilibriumProved=False)
    if not (strict and norm<1):
        raise EnclosureFailure('uniform strict Krawczyk inclusion / contraction failed',proof)
    if not all(f.contains(0) for f in residual):
        raise EnclosureFailure('full residual enclosure excludes zero',proof)
    proof.update(rootExists=True,uniqueWithinBox=True)
    return X,proof,l,v

def saturation(centers,C,Tlo,Thi,precision=256,radius='1e-24'):
    ctx.prec=precision
    T=interval(Tlo,Thi)
    if not T>0:raise ArithmeticError('invalid parameter temperature')
    X,proof,l,v=prove(centers,[radius]*2,C,lambda x:sat_system(x,T),precision)
    proof.update(parameterTemperature=serialize(T),parameterScope='every real T in parameterTemperature',
        pressurePa=serialize(l['p'].intersection(v['p'])),
        endpointStability=[stability(l,X[0],T),stability(v,X[1],T)])
    return X,proof

def mixture(centers,C,d,u,mode,precision=256,radii=('1e-24','1e-24','1e-26')):
    ctx.prec=precision
    d,u=ball(d),ball(u)
    X,proof,l,v=prove(centers,radii,C,lambda x:mix_system(x,d,u,mode),precision)
    rl,rv,T=X
    q,w=fractions(rl,rv,d)
    fv=w/rl+q/rv-1/d
    fu=w*l['u']+q*v['u']-u
    if not (fv.contains(0) and fu.contains(0)):
        raise ArithmeticError('independent original volume/energy residual excludes zero')
    admissible=bool(q>0 and w>0 and q<1 and w<1)
    quality='INTERIOR' if admissible else 'Q_LT_ZERO' if q<0 else 'Q_GT_ONE' if w<0 else 'ENDPOINT_SIGN_UNRESOLVED'
    proof.update(quality=serialize(q),liquidFraction=serialize(w),qualityStatus=quality,
        mixtureAdmissible=admissible,exactEndpointEqualityProved=False,
        volumeResidual=serialize(fv),originalEnergyResidual=serialize(fu),
        pressurePa=serialize(l['p'].intersection(v['p'])),
        entropyJkgK=serialize(w*l['s']+q*v['s']),
        endpointStability=[stability(l,rl,T),stability(v,rv,T)],
        completePhysicalBranchCertification=False)
    return X,proof
