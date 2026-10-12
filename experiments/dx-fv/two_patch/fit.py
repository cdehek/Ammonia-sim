"""Frozen-source-only, constrained physical Gibbs fit. Run before validate.py.

The all-zero row-temperature offsets are a deliberate bounded subfamily, not
independent per-knot noise. Every polynomial coefficient, hence every higher
jet, is an optimization unknown. EOS is neither imported nor queried.
"""
import hashlib,json,platform,time,sys
from pathlib import Path
import numpy as np
import scipy
import cvxpy as cp
from model import ROOT,BASE,TERMS,basis,Patch

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'evidence'
OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((ROOT/'properties.json').read_text())

def fit(name,rows,zmax):
    start=time.perf_counter();P=np.array(D['p'])[rows];S=np.array(D['sat'])[rows];Ts=S[:,0]+273.15
    pc=(P[0]+P[-1])/2;ps=(P[-1]-P[0])/2;tc=(Ts[0]+Ts[-1]-zmax)/2;ts=(Ts[-1]-Ts[0]+zmax)/2
    x=(P-pc)/ps;n=len(P)
    # Hermite boundary passes all T rows. Slopes use only rounded coexistence
    # values. Compatibility with their intervals is separately constrained below.
    slopes=100*Ts*(1/S[:,6]-1/S[:,3])/(S[:,4]-S[:,1])
    B=[];rhs=[]
    for q,T,sp in zip(x,Ts,slopes):
        B.extend([[q**k for k in range(2*n)],[0 if k==0 else k*q**(k-1) for k in range(2*n)]])
        rhs.extend([T,sp*ps])
    satc=np.linalg.solve(B,rhs)
    # Physical PT polynomial: derivative constraints in physical units.
    def w(p,T,a=0,b=0):return basis((p-pc)/ps,(T-tc)/ts,a,b,ps,ts)
    A=[];lower=[];upper=[];labels=[]
    for i,p,T0 in zip(rows,P,Ts):
        for z in range(zmax+1):
            T=T0-z;h,s,r=D['liquid'][i][z]
            for vec,l,u,label in [(w(p,T)-T*w(p,T,0,1),h-5e-8,h+5e-8,'h'),(-w(p,T,0,1),s-5e-8,s+5e-8,'s'),(w(p,T,1),100/(r+5e-8),100/(r-5e-8),'gp')]:
                A.append(np.r_[vec,np.zeros(n)]);lower.append(l);upper.append(u);labels.append([i,z,label])
        vander=np.array([((p-pc)/ps)**k for k in range(n)])
        for vec,l,u,label in [(np.r_[w(p,T0),T0*vander],S[list(rows).index(i),4]-5e-8,S[list(rows).index(i),4]+5e-8,'hg'),(np.r_[np.zeros(len(TERMS)),vander],S[list(rows).index(i),5]-5e-8,S[list(rows).index(i),5]+5e-8,'sg'),(np.r_[w(p,T0,1)+slopes[list(rows).index(i)]*w(p,T0,0,1),slopes[list(rows).index(i)]*vander],100/(S[list(rows).index(i),6]+5e-8),100/(S[list(rows).index(i),6]-5e-8),'gpg')]:
            A.append(vec);lower.append(l);upper.append(u);labels.append([i,0,label])
    A=np.array(A);lower=np.array(lower);upper=np.array(upper);center=(lower+upper)/2;half=(upper-lower)/2
    # A low-degree least-squares initializer; it supplies no fixed derivative jets.
    ids=[k for k,(a,b) in enumerate(TERMS) if a+b<=2]+list(range(len(TERMS),len(TERMS)+n))
    c0=np.zeros(A.shape[1]);c0[ids]=np.linalg.lstsq(A[:,ids]/half[:,None],center/half,rcond=1e-15)[0]
    shift=1e-5;v=cp.Variable(A.shape[1]);c=c0+shift*v
    # Subtract in extended precision; preserve a 2% evaluation margin inside
    # actual source intervals. This is a stricter constraint, no relaxed budget.
    residual=np.array(np.asarray(A,dtype=np.longdouble)@np.asarray(c0,dtype=np.longdouble)-np.asarray(center,dtype=np.longdouble),dtype=float)/half
    constraints=[A*shift/half[:,None]@v+residual<=.98,A*shift/half[:,None]@v+residual>=-.98]
    physical_scales=(2e-5,.02)
    for px in np.linspace(-1,1,9):
        p=pc+ps*px;t0=np.polynomial.polynomial.polyval(px,satc)
        for z in np.linspace(0,zmax,9):
            T=t0-z
            gp=w(p,T,1)@c[:len(TERMS)];pp=w(p,T,2)@c[:len(TERMS)];pt=w(p,T,1,1)@c[:len(TERMS)];tt=w(p,T,0,2)@c[:len(TERMS)]
            a,b=physical_scales
            constraints.extend([gp>=.05,pt>=1e-6,
                cp.bmat([[-pp/a,-pt/np.sqrt(a*b)],[-pt/np.sqrt(a*b),-tt/b]]) >> np.eye(2)*.02])
    # Smoothness prior: minimize normalized high-order physical-pressure and
    # temperature coefficients. Not an EOS prior or estimated fixed Hessian.
    weights=np.array([0 if a+b<3 else 10.**(a+b-3) for a,b in TERMS]+[0]*n)
    objective=cp.sum_squares(cp.multiply(weights,c/shift))+1e-8*cp.sum_squares(v)
    problem=cp.Problem(cp.Minimize(objective),constraints)
    try:
        problem.solve(solver='CLARABEL',max_iter=300,tol_gap_abs=1e-9,tol_feas=1e-10,tol_gap_rel=1e-9)
        status=problem.status;coef=None if v.value is None else c0+shift*v.value
    except Exception as exc:status=str(exc);coef=None
    result=dict(name=name,rows=list(rows),zmax=zmax,pc=pc,ps=ps,tc=tc,ts=ts,saturationCoefficients=satc.tolist(),rowTemperatureOffsetsK=[0.]*n,
                saturationSlopeKPerBar=slopes.tolist(),status=status,fitSeconds=time.perf_counter()-start,solverIterations=problem.solver_stats.num_iters if problem.solver_stats else None,
                liquidKnots=n*(zmax+1),sourceConstraintCount=len(labels),constraintLabels=labels)
    if coef is not None:
        result.update(coefficients=coef[:len(TERMS)].tolist(),vaporEntropyCoefficients=coef[len(TERMS):].tolist(),
                      maximumNormalizedIntervalDeviation=float(np.max(abs(A@coef-center)/half)),
                      intervalResiduals=((A@coef-center)/half).tolist(),objective=float(problem.value))
    print(name,status,result.get('maximumNormalizedIntervalDeviation'),flush=True)
    return result

start=time.perf_counter()
results=[fit('low',list(range(4)),2),fit('high',[236,237],1)]
obj=dict(staticOnly=True,qualified=False,baseCommit='5318173b49719e263c2adda214a222a9c0533a47',sourceSHA256=hashlib.sha256((ROOT/'properties.json').read_bytes()).hexdigest(),
         fitCodeSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),noEOSUsed=True,
         representation='total-degree-five polynomial in affine physical pressure and temperature; one potential per patch',
         sourceTemperaturePolicy='one deltaT per row, fixed to zero in this subfamily; all knots share it',
         patches=results,fitSeconds=time.perf_counter()-start,
         versions=dict(Python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,cvxpy=cp.__version__))
(OUT/'candidate.json').write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
(OUT/'candidate.sha256').write_text(hashlib.sha256((OUT/'candidate.json').read_bytes()).hexdigest()+'  candidate.json\n')
