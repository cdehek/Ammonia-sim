# B4A algorithm decision — recorded before source modification

Starting evidence: B3 at `4e1295be9493d8bce4ca35ee0cf61accb7465226`.
Upstream source: `ae81610e7d23efc57f9d051c8e70a4d66e87537f`.
The historical source44 control has been independently executed in this session;
its saved input selects phase 6, Q=-6.990365783288272e-10, with fresh-DT
pressure error 2870.504165824288 Pa and canonical pressure error
4245.089360319271 Pa. See `evidence/historical-control.json`.

## Selected strategy

For caloric pressure inputs H/S/U, a negative computed quality is an instruction
to resolve the original coordinates on the liquid branch, never permission to
extrapolate an equilibrium specific volume. Extend the existing liquid-dispatch
condition to negative Q for these callers in BOTH the superancillary and full-VLE
paths. Preserve the original condition for density inputs. Preserve all current
outer-flash settings, including the exact B1 44-bit patch.

This selects an existing physical branch and bounded inversion, not a returned
density or imposed final state. `HSU_P_flash` uses the existing melting/minimum
temperature bound and saturation temperature as its upper liquid bound, then
`HSU_P_flash_singlephase_Brent` solves at the original P and original caloric
input. Its original convergence, range and phase checks remain. An inversion
failure propagates; there is no substitute saturation state, table, clamp,
polished reference, retry with altered inputs, or new numerical tolerance.

The physical basis is positive liquid heat capacity and a stable isobaric
liquid branch immediately below the coexistence endpoint, independently shown
by B3's displaced homogeneous and Gibbs-equilibrium roots. This is qualified
only for this experimental ammonia support envelope, not every CoolProp fluid.

## Numerical uncertainty and physical boundaries

Q divides an endpoint property difference by a latent-property interval; its
uncertainty is not a physical vapor fraction. The old -1e-9 band corresponds to
about .00143 J/kg at the primary pressure, much larger than binary64 endpoint
rounding, and produces a physically incorrect inventory. No revised Q tolerance
is introduced. Instead the homogeneous inversion resolves negative differences
using the same EOS and the existing saturation-bounded temperature interval.

Before editing source, `evidence/endpoint-rounding-preimplementation.json`
records all four pressures, both endpoints and h plus/minus one binary64 ULP.
All 24 independent homogeneous roots converge within the original 1e-5 Pa /
1e-8 J/kg reference limits. Exactly returned PQ h values round-trip to molar
enthalpy without difference in this native runtime. Neighboring values can be
indistinguishable at reference resolution. Such cases are labeled endpoint
unresolved; no homogeneous two-sided derivative assertion is made there.
The backend must still invert the original input; rounded endpoint density must
not be installed as an answer. Endpoint/browser/full-VLE continuity, canonical
recovery and original signed probes are mandatory empirical gates. A tiny
negative Q caused by saturation rounding may resolve to an indistinguishable
liquid endpoint or fail explicitly. Neither justifies extrapolated mixture volume.

| Physical situation | Decision / verification |
|---|---|
| Stable subcooled liquid, Q<0 | Existing bounded homogeneous liquid inversion; fresh DT and stability checks |
| Saturated-liquid endpoint, Q=0 | Existing equilibrium endpoint, unchanged |
| 0<Q<1 | Existing equilibrium T and lever volume, unchanged |
| Saturated-vapor endpoint, Q=1 | Existing equilibrium endpoint, unchanged |
| Stable superheated vapor beyond original band | Existing vapor inversion, unchanged |
| Endpoint uncertainty / one-ULP neighbors | Original-coordinate solve; label independent phase unresolved inside B3 reference resolution; test continuity |
| Invalid/out-of-support inputs | Existing limits and explicit exceptions; no enlarged domain |

The upper 1<Q<=1+1e-9 extrapolation remains a separately reported known
classification limitation; it is sampled without claiming legitimate equilibrium.
This milestone does not change the vapor dispatcher or PT/cache mechanism.
No broad phase-validity claim is possible while those findings remain.

## Source ownership and shared consequences

`HelmholtzEOSMixtureBackend.cpp::p_phase_determination_pure_or_pseudopure`
has the two affected quality branches (upstream lines 1839 and 2079).
`FlashRoutines.cpp::HSU_P_flash` (line 3350) calls this classifier for iHmolar,
iSmolar and iUmolar. Mass variants convert to molar in the existing pre-update.
The existing B1 stopping-rule modification is shared by these three inversions.
Other direct callers are PT_flash (iT) and DP_flash (iDmolar); neither is changed
by the new caloric-input condition. DU uses HSU_D_flash, unchanged. Full-VLE
retains `saturation_called` and its saturated liquid bound. Superancillary
retains cache clearing and `_TLanc=Tsat` on the existing liquid-dispatch branch.
Pseudo-pure caloric inputs share the full-VLE branch; they are an unqualified
shared-code consequence, not an asserted ammonia result.

## Rejected alternatives

* Clipping Q or using saturated-liquid density changes the requested inventory.
* Enlarging a Q band makes invalid lever extrapolation worse.
* Rejecting every negative-Q input denies independently established valid liquid.
* A bare zero-threshold replacement for all callers ignores density, saturation
  rounding and shared-code effects. This change instead limits dispatch to
  caloric inputs, uses existing bounded inversion, investigates ULP neighbors,
  and gates the result on independent EOS and original canonical budgets.
* A new custom Newton solver or reference-root substitution duplicates existing
  inversion machinery and enlarges the patch without evidence of necessity.
* Fixing upper-quality dispatch or PT caches here would couple separate defects.

## Execution gates

Build control and repair separately. First require exact saved PH, fresh-DT
residuals, stable liquid reference and original canonical .1 Pa/.1 J/kg/1e-4 K
limits. Then check original signed probes against homogeneous EOS derivatives
using the accepted normalized inventory/nonlinear scale 1e-11. The reverse-P
probe is a physical coexistence crossing, excluded from homogeneous smoothness.
Retain all 57 B3 matrix inputs and four signed probes without input regeneration,
add only explicitly labeled focused regressions, and preserve historical B.
Only after the focused gates pass run limited accepted A2 compatibility and
bounded performance checks. No complete B2/A2 campaign, production integration,
vapor fix or deployment is authorized. Use hard process deadlines and retain
every exception and incomplete output.
