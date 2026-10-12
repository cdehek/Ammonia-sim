"""Static-only frozen-data candidates. Never imported by an accepted solver.

Gibbs energy is a more direct potential than Helmholtz energy for this PT grid.
All fits use frozen samples only; CoolProp is deliberately absent from this file.
Engineering units: p bar, T K, g/h/u kJ/kg, s kJ/(kg K), rho kg/m3.
"""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import make_interp_spline, PchipInterpolator
from scipy.sparse import coo_matrix, vstack, eye
from scipy.optimize import lsq_linear, brentq

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / 'properties.json').read_text())
P = np.array(DATA['p']); X = np.log(P); Z = np.array(DATA['sc'], dtype=float)
SAT = np.array(DATA['sat']); F = np.array([[v if v is not None else [np.nan]*3
                                         for v in row] for row in DATA['liquid']])
VALID = np.isfinite(F[:,:,0])

def differentiate(values, axis):
    """Local degree-six derivative, one-sided at finite-data boundaries."""
    result = np.full_like(values, np.nan)
    grid = X if axis == 0 else Z
    for j in range(values.shape[1-axis]):
        a = values[:,j] if axis == 0 else values[j,:]
        valid = np.flatnonzero(np.isfinite(a))
        for k in valid:
            near = valid[np.argsort(abs(grid[valid]-grid[k]))[:7]]
            near.sort(); scale = max(abs(grid[near]-grid[k]))
            fit = np.polynomial.polynomial.polyfit((grid[near]-grid[k])/scale,
                                                   a[near], len(near)-1)
            if axis == 0: result[k,j] = fit[1]/scale
            else: result[j,k] = fit[1]/scale
    return result

def hermite_matrix(order):
    n = order+1; size = 2*n; a = np.zeros((size,size))
    import math
    for side in range(2):
        for d in range(n):
            for k in range(d,size):
                a[side*n+d,k] = math.factorial(k)/math.factorial(k-d)*side**(k-d)
    return np.linalg.inv(a)

class GridBase:
    def __init__(self):
        # Interpolating quintic is a coordinate map, not an adopted saturation API.
        # Its error/monotonicity is audited independently. No extrapolation.
        self.ts = make_interp_spline(X, SAT[:,0]+273.15, k=5)
    def bounds(self,p):
        if not .3 <= p <= 35: raise ValueError('Pressure outside frozen domain')
        i = min(len(P)-2,max(0,int(np.searchsorted(P,p,side='right')-1)))
        zmax = Z[np.flatnonzero(VALID[i] & VALID[i+1])[-1]]
        return i, float(zmax)
    def temperature(self,p,z): return float(self.ts(np.log(p)))-z
    def ph(self,p,h):
        _,zm = self.bounds(p)
        f = lambda z: self.at(p,z,derivatives=False)['h']-h
        if f(0)*f(zm)>0: raise ValueError('PH outside single-phase candidate domain')
        z = brentq(f,0,zm,xtol=2e-12,rtol=1e-14)
        return self.at(p,z,derivatives=False)
    def at_density(self,p,rho):
        _,zm = self.bounds(p)
        f = lambda z: self.at(p,z,derivatives=False)['rho']-rho
        if f(0)*f(zm)>0: raise ValueError('Density outside single-phase candidate domain')
        return self.at(p,brentq(f,0,zm,xtol=5e-14,rtol=2e-15),derivatives=False)
    def roots(self,rho,u,pressures):
        roots=[]; previous=None;self.last_root_checks=[]
        for p in pressures:
            try: f=self.at_density(float(p),rho)['u']-u
            except (ValueError,FloatingPointError): previous=None;continue
            if abs(f)<2e-12: root=float(p)
            elif previous is not None and previous[1]*f<0:
                try: root=brentq(lambda q:self.at_density(q,rho)['u']-u,
                                previous[0],p,xtol=5e-15,rtol=9e-16)
                except ValueError: previous=(p,f);continue
            else: previous=(p,f);continue
            # A bracket may surround a jump caused by multivalued density
            # recovery. A converged Brent interval is NOT sufficient evidence.
            state=self.at_density(root,rho)
            er=state['u']-u;dr=state['rho']-rho
            valid=abs(er)<1e-7 and abs(dr)<1e-7
            self.last_root_checks.append(dict(p=root,energyResidualKJkg=er,
                                         densityResidualKgM3=dr,validated=bool(valid)))
            if valid and (not roots or abs(root-roots[-1])>1e-8):roots.append(root)
            previous=(p,f)
        return roots

class JointPchip(GridBase):
    """Shape-preserving independent fields: comparator, NOT a potential.

    Shared PT coordinates and h-u work identity do not ensure Maxwell identities.
    No compressibility guarantee is implied by monotonicity along grid axes.
    """
    def __init__(self):
        super().__init__(); self.curves=[]
        for k in range(3):
            columns=[]
            for j in range(len(Z)):
                v=VALID[:,j]; values=F[v,j,k]
                columns.append(PchipInterpolator(X[v],np.log(values) if k==2 else values,
                                                 extrapolate=False))
            self.curves.append(columns)
    def fields(self,p,z):
        _,zm=self.bounds(p)
        if not 0 <= z <= zm: raise ValueError('Offset outside frozen domain')
        axis=Z[Z<=zm]; x=np.log(p)
        result=[]
        for k in range(3):
            curve=PchipInterpolator(axis,[self.curves[k][j](x) for j in range(len(axis))],
                                    extrapolate=False)
            value=float(curve(z));result.append(np.exp(value) if k==2 else value)
        h,s,rho=result
        return dict(p=p,T=self.temperature(p,z),z=z,h=h,s=s,rho=rho,u=h-100*p/rho)
    def at(self,p,z,derivatives=True):
        a=self.fields(p,z)
        if not derivatives:return a
        # Physical PT partials, separately tested at two finite-difference scales.
        dp=min(p*2e-5, (35-.3)*1e-5);dt=2e-4
        pm=max(.3,p-dp);pp=min(35,p+dp)
        # One-sided physical derivative where a centered probe would cross the
        # liquid saturation boundary. No evaluation or extrapolation into vapor.
        for direction,q in [('minus',pm),('plus',pp)]:
            offset=self.temperature(q,0)-a['T']
            if not 0<=offset<=self.bounds(q)[1]:
                if direction=='minus':pm=p
                else:pp=p
        if pm==pp:raise ValueError('Physical derivative unsupported at this corner')
        b=self.fields(pm,self.temperature(pm,0)-a['T'])
        c=self.fields(pp,self.temperature(pp,0)-a['T'])
        _,zm=self.bounds(p);zm1=max(0,z-dt);zp=min(zm,z+dt)
        d=self.fields(p,zm1);e=self.fields(p,zp)
        hp=(c['h']-b['h'])/(pp-pm);rp=(c['rho']-b['rho'])/(pp-pm)
        ht=(d['h']-e['h'])/(zp-zm1);rt=(d['rho']-e['rho'])/(zp-zm1)
        a.update(cp=ht,kappa=rp/a['rho'],rhoP=rp,rhoT=rt,
                 maxwell=hp-100*(1/a['rho']+a['T']*rt/a['rho']**2))
        return a

class GibbsHermite(GridBase):
    def __init__(self, projected=False, order=2):
        super().__init__();self.order=order; self.projected=projected
        temp=self.ts(X)[:,None]-Z[None,:]
        entropy=F[:,:,1].copy();g=F[:,:,0]-temp*entropy
        tx=self.ts(X,1)[:,None]
        gx=100*P[:,None]/F[:,:,2]-entropy*tx
        self.projection=None
        if projected:
            # Project discrete gradient integrals onto a single-valued potential,
            # within measured entropy rounding. h/rho remain exact frozen knots.
            # This is an integrability projection, NOT a stability-constrained fit.
            index=np.full(VALID.shape,-1,dtype=int);index[VALID]=np.arange(VALID.sum())
            rr=[];cc=[];vv=[];target=[];weights=[]
            for axis,derivative,grid in [(0,gx,X),(1,entropy,Z)]:
                for j in range(VALID.shape[1-axis]):
                    mask=VALID[:,j] if axis==0 else VALID[j,:]
                    ids=np.flatnonzero(mask)
                    values=derivative[ids,j] if axis==0 else derivative[j,ids]
                    ant=make_interp_spline(grid[ids],values,k=5).antiderivative()
                    for a,b in zip(ids[:-1],ids[1:]):
                        pos1=(a,j) if axis==0 else (j,a)
                        pos2=(b,j) if axis==0 else (j,b)
                        integral=float(ant(grid[b])-ant(grid[a]))
                        # Edge weight scales from entropy rounding, not rigorous
                        # integral-error bounds or statistical confidence limits.
                        if axis==0:
                            bound=5e-8*abs(float(self.ts(X[b])-self.ts(X[a])))+1e-10
                        else: bound=5e-8*(Z[b]-Z[a])
                        row=len(target); rr.extend([row,row]);cc.extend([index[pos1],index[pos2]])
                        vv.extend([-1/bound,1/bound]);target.append((integral-(g[pos2]-g[pos1]))/bound)
                        weights.append(bound)
            matrix=coo_matrix((vv,(rr,cc)),shape=(len(target),int(VALID.sum()))).tocsr()
            # Solve for micro-kJ/kg adjustments to avoid poorly scaled bounds.
            scale=1e-5;limits=temp[VALID]*5e-8/scale
            # A weak tie chooses a reference constant without changing convention.
            matrix=vstack([matrix*scale,eye(VALID.sum(),format='csr')*1e-4]).tocsr()
            rhs=np.r_[target,np.zeros(VALID.sum())]
            fit=lsq_linear(matrix,rhs,bounds=(-limits,limits),tol=1e-9,
                           lsmr_tol=1e-10,max_iter=200,verbose=0)
            if not fit.success:raise RuntimeError('Bounded potential projection did not converge')
            g[VALID]+=scale*fit.x;entropy[VALID]=(F[:,:,0][VALID]-g[VALID])/temp[VALID]
            gx=100*P[:,None]/F[:,:,2]-entropy*tx
            self.projection=dict(success=bool(fit.success),iterations=fit.nit,
                                 cost=float(fit.cost),optimality=float(fit.optimality),
                                 maximumEntropyKnotAdjustment=float(np.max(abs(entropy[VALID]-F[:,:,1][VALID]))))
        jets={(0,0):g,(1,0):gx,(0,1):entropy}
        cross=.5*(differentiate(gx,1)+differentiate(entropy,0));jets[(1,1)]=cross
        if order==2:
            jets[(2,0)]=differentiate(gx,0);jets[(0,2)]=differentiate(entropy,1)
            jets[(2,1)]=.5*(differentiate(jets[(2,0)],1)+differentiate(cross,0))
            jets[(1,2)]=.5*(differentiate(jets[(0,2)],0)+differentiate(cross,1))
            jets[(2,2)]=.5*(differentiate(jets[(2,1)],1)+differentiate(jets[(1,2)],0))
        n=order+1; H=hermite_matrix(order);self.H=H;self.coefficients={}
        for i in range(len(P)-1):
            for j in range(len(Z)-1):
                if not np.all(VALID[i:i+2,j:j+2]):continue
                dx=X[i+1]-X[i];dz=Z[j+1]-Z[j];d=np.zeros((2*n,2*n))
                for si in range(2):
                    for sj in range(2):
                        for a in range(n):
                            for b in range(n):
                                d[si*n+a,sj*n+b]=jets[a,b][i+si,j+sj]*dx**a*dz**b
                self.coefficients[i,j]=d
    def at(self,p,z,derivatives=True):
        i,zm=self.bounds(p)
        if not 0 <= z <= zm:raise ValueError('Offset outside frozen domain')
        j=min(int(z),int(zm)-1);dx=X[i+1]-X[i];dz=Z[j+1]-Z[j]
        a=(np.log(p)-X[i])/dx;b=(z-Z[j])/dz;coef=self.coefficients[i,j]
        size=coef.shape[0]
        def basis(t,d):
            import math
            return np.array([0 if k<d else math.factorial(k)/math.factorial(k-d)*t**(k-d)
                             for k in range(size)])
        def weights(t,d,width):
            # Exact endpoint cardinal identities avoid coefficient cancellation.
            # This does not replace any property with an independently fitted field.
            if t in (0.,1.) and d<=self.order:
                w=np.zeros(size);w[int(t)*(self.order+1)+d]=1
            else:w=basis(t,d)@self.H
            return w/width**d
        ax=[weights(a,d,dx) for d in range(3)];bz=[weights(b,d,dz) for d in range(3)]
        G=float(ax[0]@coef@bz[0]);Gx=float(ax[1]@coef@bz[0]);Gz=float(ax[0]@coef@bz[1])
        T=self.temperature(p,z);tx=float(self.ts(np.log(p),1))
        gp=(Gx+tx*Gz)/p
        if gp<=0:raise FloatingPointError('Nonpositive potential-derived volume')
        rho=100/gp;h=G+T*Gz
        result=dict(p=p,T=T,z=z,h=h,s=Gz,rho=rho,u=h-p*gp)
        if not derivatives:return result
        Gxx=float(ax[2]@coef@bz[0]);Gxz=float(ax[1]@coef@bz[1]);Gzz=float(ax[0]@coef@bz[2])
        txx=float(self.ts(np.log(p),2))
        gpp=(Gxx+2*tx*Gxz+tx*tx*Gzz+txx*Gz-Gx-tx*Gz)/p**2
        gtp=-(Gxz+tx*Gzz)/p
        cp=-T*Gzz;kappa=-gpp/gp
        cv=cp+T*gtp*gtp/gpp if gpp!=0 else float('nan')
        rp=-100*gpp/gp**2;rt=-100*gtp/gp**2
        hp=gp-T*gtp;maxwell=hp-100*(1/rho+T*rt/rho**2)
        J=np.array([[rp,rt],[-T*gtp-p*gpp,cp-p*gtp]])
        scaled=np.diag([1/rho,1/max(1,abs(result['u']))])@J@np.diag([p,T])
        result.update(cp=cp,cv=cv,kappa=kappa,rhoP=rp,rhoT=rt,maxwell=maxwell,
                      scaledRecoveryCondition=float(np.linalg.cond(scaled)))
        return result

def candidates():
    return {'joint-pchip':JointPchip(), 'gibbs-bicubic':GibbsHermite(order=1),
            'gibbs-biquintic':GibbsHermite(),
            'gibbs-rounded-projection':GibbsHermite(projected=True)}
