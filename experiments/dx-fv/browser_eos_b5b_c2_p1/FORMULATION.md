# Mathematical formulation and implemented theorem

## Exact target and unchanged EOS

The exact input is the rational triple represented by original binary64
M kg, U_kJ kJ and V m³. Decode hexadecimal bits before arithmetic:
d*=M/V, u*=1000 U_kJ/M. Rounded rho_DU/u_DU are not substituted.
The accepted operation sequence is retained verbatim in
`PROOF_OBLIGATIONS.md` and in generated-control construction in `diagnostic.py`.
Stored V is `3f43a92a30553262`, or
2767011611056433/4611686018427387904, not decimal-real 0.0006.

The EOS is exactly C2's saved `Ammonia.json`, SHA256
`4d451fadbe6eb1c2441169c599890cf7cd6edc818918f23959e2afb20a881e14`.
Original decimal tokens are parsed as binary64, then their exact rationals are
enclosed. Derived constants are real expressions of those constants:
R=R_molar/W, rho_c=n_c W, delta=rho/rho_c, tau=Tc/T.
All eight power, ten Gaussian and two GaoB terms and all original ideal terms
remain. Original lead a1/a2 preserve entropy/energy reference; no setter or
offset change occurs. No new saturation fit or interpolation is used.

For alpha=alpha0+alphar:

```
p = rho R T (1 + delta alphar_delta)
u = R Tc alpha_tau
s = R (tau alpha_tau - alpha)
g = R T (alpha + 1 + delta alphar_delta)
f = R T alpha
cv = -R tau^2 alpha_tautau
p_rho = R T (1 + 2 delta alphar_delta + delta^2 alphar_deltadelta)
p_T = rho R (1 + delta alphar_delta - delta tau alphar_deltatau)
u_rho = R Tc alphar_taudelta / rho_c
g_rho = p_rho/rho
g_T = -s + p_T/rho
```

`eos_interval.py` extends the independent C2 ball evaluator with ar, second
density derivatives, cross derivatives, entropy and g. For each residual term
v, logarithmic derivatives give v_dd=v(ld²+ldd), v_tt=v(lt²+ltt),
v_dt=v ld lt. The exponent is separable in density and temperature for every
inherited term, so the mixed logarithmic derivative is zero. Positive density
and T, nonzero GaoB and Planck denominators and finite outputs establish the
analytic domain used here. Endpoint cv, p_rho, cp and compressibility must all
have positive finite enclosures over the entire respective boxes.

Independent diagnostic expressions use the original inherited mpmath evaluator,
including g=u+p/rho−Ts; analytic derivatives are audited by mp.diff. Its sole
hardcoded JSON path is redirected in memory to C2's saved identical JSON. This
changes no source bytes or mathematical expression. The alternate interval
g expression is also checked on full coexistence boxes.

## Homogeneous inversion: inherited scalar theorem

At fixed exact d*, continuity and strict opposite signs of u(d*,T)−u* at
rational bracket endpoints prove a root by the intermediate value theorem.
An enclosed positive cv over the entire bracket proves uniqueness there.
Evaluate pressure over that whole bracket to enclose the root pressure. The
inherited proposed radius 1e-30 K is independently verified, never an assumed
root error or support tolerance. This proves no stable phase by itself.

## Formulation 1: parameterized coexistence

Let x=(rhoL,rhoV), parameter t=T, and

```
F1(x,t) = (p(rhoL,t)-p(rhoV,t))/1e6
F2(x,t) = (g(rhoL,t)-g(rhoV,t))/1e6
J = [[pL_rho, -pV_rho], [pL_rho/rhoL, -pV_rho/rhoV]]/1e6
```

The factor 1e6 only scales equations; it is no tolerance. X consists of
separated, strictly positive density intervals. The temperature parameter P is
the **entire rational outward homogeneous temperature enclosure**, including
its hull rounding, not a midpoint. Full F(X,P) and J(X,P) are ball expressions.

Choose exact rational x0, symmetric rational radius vector r, and an exact
rational square preconditioner C proposed by an independently differentiated
mpmath point inverse. Prove det(C) does not contain zero. With
X0=[x0−r,x0+r], compute

```
A = I - C J(X,P)
K = x0 - C F(x0,P) + A [-r,r]
```

The evaluated ball hull X contains X0. Require K strictly inside X0 and the
rigorous maximum absolute row-sum bound ||A||_infinity<1. For each real t in P,
the map H_t(x)=x−C F(x,t) maps the closed convex X0 into itself by the mean-value
integral bound, and is a contraction on it. Banach's theorem supplies a fixed
point. Nonsingular C makes it a zero of F. The derivative bound also gives
uniqueness anywhere in the evaluated convex box X, since two zeros there would
contradict contraction. The entire connecting segment lies in X and the EOS
analytic domain. This argument is uniform for every t in P; no sampled-T
claim is transported to another temperature.

Require finite residuals/Jacobians, full residual enclosures containing zero,
positive separated densities (excluding the entire trivial diagonal), valid T,
and positive endpoint stability. Residual inclusion alone is only a consistency
check; strict K and contraction establish existence. Whole-box J is essential;
the point inverse is only a preconditioner proposal. Serialize every box,
residual, J, C, determinant, K and exact norm bound. Intersect the two endpoint
pressure enclosures because equality is established at the proved root.

At exact homogeneous d*, rigorous d*−rhoL>0 or d*−rhoV<0 proves a side
inequality relative to these endpoints for the exact unknown root T. It does
not establish that these endpoints form the equilibrium convex envelope.

## Formulation 2: volume-eliminated mixture

At original d*,u*, take x=(rhoL,rhoV,T), with

```
Q = (rhoL-d*)rhoV / [d*(rhoL-rhoV)]
w = (d*-rhoV)rhoL / [d*(rhoL-rhoV)]
Q+w = 1
F3 = [(uL-u*) + Q(uV-uL)]/1e6       near liquid
F3 = [(uV-u*) - w(uV-uL)]/1e6       near vapor
```

Separation and positive d* make elimination algebraically equivalent to the
original volume equation. No density/quality substitution or clipping occurs.
The exact rational inventory is constant, enclosed before arithmetic. Use
the same strict K/contraction theorem in three variables. The first two rows
gain T columns (pL_T−pV_T)/1e6 and (gL_T−gV_T)/1e6. With Dv=1/rhoV−1/rhoL:

```
Q_rhoL = w/(rhoL^2 Dv)
Q_rhoV = Q/(rhoV^2 Dv)
F3_rhoL = [w uL_rho + (uV-uL) Q_rhoL]/1e6
F3_rhoV = [Q uV_rho + (uV-uL) Q_rhoV]/1e6
F3_T = [w cvL + Q cvV]/1e6
```

Independently enclose original w/rhoL+Q/rhoV−V/M and
w uL+Q uV−1000 U_kJ/M, plus alternate g residual. Require strict positive
Q,w and both strictly below one for an interior mixture claim. Algebraic
continuations Q<0 or w<0 are rejected. Intervals crossing endpoints remain
unresolved; exact Q=0/1 equality is not proved in this experiment. Proposed
radius is 1e-24 kg/m³ for each endpoint and 1e-26 K; inclusion verifies it.

## Bounded exclusion versus global selection

For the generated dome-interior negative control, both the homogeneous root
and a physical-quality coexistence root satisfy the same exact M,U,V. Interval
comparison proves s_mix−s_hom>0. Under ordinary additive bulk-phase equilibrium
thermodynamics, the homogeneous root cannot maximize entropy at that U,V. This
excludes that homogeneous state without claiming the competitor is the global
maximum. Surface/interface energy, gravity, kinetics and nucleation are outside
this thermodynamic model; metastable operating persistence is a different
physical question.

No global supporting tangent or entropy maximum over all relevant competitors
is proved. [BRANCH_AND_TOPOLOGY.md](BRANCH_AND_TOPOLOGY.md) states the missing
obligation. Local root uniqueness does not exclude another root outside X, an
additional phase, or a different lower free-energy branch.
