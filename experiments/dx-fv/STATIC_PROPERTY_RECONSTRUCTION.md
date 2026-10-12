# Static joint-property reconstruction experiment

**No tested candidate is acceptable for integration.** A thermodynamic potential
enforces identities, but does not automatically enforce stability or accurate
canonical recovery. Independent shape-preserving field interpolation improves
values and sampled compressibility, but still violates thermodynamic identities.
All candidates and the earlier saturation-only PCHIP remain unqualified.

Plain language: the liquid is nearly incompressible. Very small errors in the
slope of a fitted energy surface can imply a large pressure error or several
different pressures for the same stored mass and energy. Matching the table and
even satisfying an energy identity cannot make those extra states physical.

Repository `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`, HEAD
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. This is static research only:
no coupled runs, solver imports of these candidates, adoption, commit or push.
All 206 pre-existing tracked/untracked files, including uncommitted Stage 2B,
PCHIP, prior diagnostics, frozen samples and references, are preserved by SHA-256.
There are no applicable AGENTS.md files in the available workspace.

## Frozen information and mathematical choice

The source has 241 log-pressure rows, 31 liquid subcooling offsets and **7,234
non-null liquid knots**; 237 cold entries are unsupported. Pressure spans 0.3–35
bar; subcooling spans 0–30 K subject to the existing cold mask. The generator
used true EOS saturation temperature to locate offset states, then rounded
saturation T to 8 decimals and h/s/rho to 7 decimals. It was read, never executed.
Every liquid knot was independently reevaluated with CoolProp 7.2.0. Maximum
source errors are 4.96914e-9 K, 4.99951e-8 kJ/kg, 4.99929e-8 kJ/(kg K), and
4.99974e-8 kg/m³, respectively. Thus the source-rounding half-widths are
5e-9 K and 5e-8 in the three other engineering units. No samples were changed.

**Gibbs energy g(p,T)** fits this pressure/temperature grid more directly than
Helmholtz energy. With p in bar and g in kJ/kg:

`s = -g_T; v = g_p/100; rho = 1/v; h = g-T*g_T; u = h-p*g_p`.

The Maxwell identity is `h_p|T = 100*(v-T*v_T)`.
Stability additionally requires `g_pp<0`, `g_TT<0`, and
`g_TT*g_pp-g_Tp²>0`: equivalently positive isothermal compressibility, cp and cv.
A Helmholtz representation `a(T,rho)=g-p*g_p` is a locally equivalent Legendre
transform **only where volume/pressure recovery is invertible**. The present
nonmonotone fits cannot provide a unique global transform. This does not prove
that a separately constrained Helmholtz fit is impossible.

Candidates use curvilinear coordinates `x=log(p), z=T_sat(p)-T`, with
`G(x,z)=g(p,T)`. A frozen-data interpolating quintic saturation coordinate map
matches all knots. It has maximum EOS temperature error **7.18845e-9 K** on 4,080
samples, positive slopes and no sampled interval overshoot. This is an isolated
coordinate construction, not a change to the accepted saturation API.

The transformed first derivatives are `G_z=s` and
`G_x=100*p/rho-s*T_sat,x`; physical `g_p=(G_x+s*T_sat,x)/p`.
The analytic derivatives include all coordinate-map first and second derivatives.
No EOS value or EOS derivative is used in candidate fitting.

Methods compared:

| Method | Construction and constraints | Decision |
| --- | --- | --- |
| Raw Gibbs bicubic / biquintic controls | Hermite potential from rounded g=h-Ts and first-derivative jets; shared mixed jets estimated from local degree-six derivatives | Rejected: rounding-naive exact-knot controls create large derivative artifacts |
| Rounding-aware Gibbs biquintic | Bounded least-squares projection of pressure/subcooling gradient integrals onto a single-valued nodal potential; h/rho knots retained; entropy may move within ±5e-8 | Rejected: integrability improves, stability and uniqueness fail |
| Joint-coordinate PCHIP comparator | Shape-preserving h/s/log(rho) in shared log-pressure/subcooling coordinates | Rejected as foundation: fields remain independently interpolated and Maxwell fails |

The projection minimizes weighted edge-integral inconsistencies, with a weak
minimum-adjustment tie choosing the potential constant. Edge scales are derived
from entropy rounding; they are **not rigorous integral-error bounds**. It uses
7,234 bounded adjustments and 14,196 grid edges. It does not enforce Hessian
negativity, saturation coexistence, or bound interpolation derivatives. Its
success status describes this least-squares problem, not scientific acceptance.
The raw controls demonstrate the danger of forcing contradictory rounded values;
they are not proposed remedies. The comparator's grid-axis monotonicity is also
not a mathematical guarantee of physical isothermal compressibility.

## Static EOS accuracy and stability

Each of 6,963 supported liquid cells has a 2×2 interior sampling. Additional
near-saturation points include 1 µK, 1 mK, 10 mK and 0.1 K subcooling, plus domain
edges and the reported probes: **30,006 identical physical PT comparisons**.
Sampled temperatures span 200.338–345.554 K. CoolProp uses explicitly selected
stable liquid for PT arbitrarily close to saturation, and PQ at saturation;
otherwise its PT ambiguity guard rejects the 1 µK points. No metastable or
extrapolated reference states are used. The initial guard failure is preserved.

Maximum absolute errors at fixed PT (pressure/T are equal by construction):

| Representation | h, kJ/kg | rho, kg/m³ | u, kJ/kg | Nonpositive compressibility samples | Other cv failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original frozen bilinear surface | 0.00614851 | 0.00685081 | 0.00606181 | 1,045 | Not a consistent potential |
| Joint-coordinate PCHIP | 0.000115043 | 0.000119254 | 0.000113510 | 0 | Not a consistent potential |
| Raw Gibbs bicubic | 0.0109413 | 22.8534 | 0.0107237 | 14,555 | 205 |
| Raw Gibbs biquintic | 0.0134333 | 28.7964 | 0.0117731 | 14,589 | 142 |
| Rounding-aware Gibbs | 0.0000269977 | 0.0408705 | 0.0000240956 | 6,105 | 679 |

All sampled cp values are positive. The 679 projected cv failures occur among
samples with positive compressibility; total projected unstable samples are
6,784. Its minimum compressibility is **-0.0251019 /bar**; minimum cv is
**-911.228 kJ/(kg K)**. These are numerical representation defects in a stable
EOS liquid domain, not physical domain boundaries.

The original / joint-PCHIP maximum Maxwell mismatches are **0.135840 /
0.00236821 kJ/(kg bar)**. Potential-based mismatches remain below 8.9e-16 in
analytic assembly, as structurally expected. Independent direct EOS checks give
zero to roundoff and positive compressibility. Finite-difference checks verify
the potential gradients but expose cancellation at very small pressure steps:
projected low-pressure rho_p estimates differ by up to 0.00846 kg/(m³ bar) at
relative steps 1e-6/3e-7. Both still confirm its negative sign. Algebraic identity
agreement is not presented as an independent proof of stable derivatives.

## PH, canonical recovery and the specific reported defects

77 EOS liquid PH requests independently test PH inversion and EOS recovery of
each candidate's resulting rho/u. This reverse canonical comparison holds
candidate inventory fixed and reports `p_candidate-p_EOS(rho,u)`; it is distinct
from pressure at fixed PH, which is prescribed and cannot measure pressure error.

| Representation | Maximum PH T error | Maximum inventory-equivalent pressure error |
| --- | ---: | ---: |
| Original | 1.03023 mK | 0.0404802 bar = 4.048 kPa |
| Joint-coordinate PCHIP | 14.5932 µK | 0.000471647 bar = 47.165 Pa |
| Rounding-aware Gibbs | 7.35852 µK | 1.20142 bar = 120.142 kPa |

The raw Gibbs controls are already rejected; their corresponding worst pressure
errors exceed 350 bar. No good temperature result compensates for these defects.

At the saved 0.1-s endpoint p=32.80473738460169 bar,
h=686.845872427996 kJ/kg, evaluated **statically**:

| Representation | PH T error | Inventory-equivalent pressure error |
| --- | ---: | ---: |
| Original | -0.836614 mK | +0.0326389255 bar = +3.263893 kPa |
| Joint-coordinate PCHIP | -11.6471 µK | +0.000460055 bar = +46.0055 Pa |
| Rounding-aware Gibbs | +3.12488 µK | -0.001318184 bar = -131.818 Pa |

Both proposed improvements still fail the existing 1e-4-bar **10 Pa** budget.
This static constitutive error is not the earlier total trajectory error:
it excludes the evolution contribution. No trajectory or event requirement is
waived or newly claimed passed.

The low-pressure point is p=0.3029893712344606 bar and EOS subcooling 1 K,
h=94.52334612321303 kJ/kg. Its original common inventory has
rho=708.6710262223568 kg/m³ and u=94.48059153610271 kJ/kg. The preserved original
surface has three roots: **0.302985440688, 0.302989370566, 0.314879847305 bar**.
Independent EOS recovery gives **0.301747903655 bar** for this inventory.

At the reported PT point, original compressibility is approximately
-8.48038e-5 /bar; EOS gives +5.92315e-5 /bar. Joint PCHIP gives +5.98873e-5 /bar,
while projected Gibbs gives approximately **-2.38107e-4 /bar**. Thus projection
does not cure the specific stability defect.

For the exact original inventory, the refined scans find one residual-validated
joint-PCHIP root, **0.301764852834 bar**, and **nine projected Gibbs roots**:
0.301046648, 0.306499363, 0.310362813, 0.314387320, 0.317535759, 0.329753621,
0.338124230, 0.345029735, 0.352280736 bar. With true EOS inventory at the reported
point, joint PCHIP gives 0.302979279106 bar (about -1.01 Pa), but projected Gibbs
again has nine roots. Raw fits also retain multiple validated roots.

Every reported root satisfies rho and specific-energy residuals below the
original 1e-7 recovery criterion. Converged brackets failing residual checks are
explicitly rejected: raw fits exhibit branch jumps from multivalued density
recovery. Initial unvalidated bracket evidence is preserved and is **not used as
a root count**. Seven additional same-candidate PH/canonical tests pass the PH
roundtrip, but expose both extra canonical roots and density-branch ambiguity.
The bracket-based density-inversion comparator recovers the starting state in
7/7 projected and joint-PCHIP cases, but only 4/7 raw cubic and 3/7 raw quintic
cases: folded density curves can defeat endpoint bracketing or select a different
offset branch. Those failures are recorded, not repaired or counted as physical
domain limits.
Roundtrip success does not demonstrate uniqueness. The finite pressure scans,
including local grid halving, establish counterexamples; they cannot enumerate
all roots or prove global uniqueness, especially in rejected multivalued fits.

## Knots, saturation and conditioning

`knots.json` records **every** reconstructed deviation in T/h/s/rho, plus EOS
errors. Maximum changes are:

| Candidate | T, K | h, kJ/kg | s, kJ/(kg K) | rho, kg/m³ |
| --- | ---: | ---: | ---: | ---: |
| Joint-coordinate PCHIP | 1.14e-13 | 1.14e-13 | 4.44e-16 | 9.10e-13 |
| Raw potential controls | 1.14e-13 | 2.28e-13 | 4.44e-16 | 2.67e-11 |
| Rounding-aware potential | 1.14e-13 | 2.28e-13 | 5.000000014e-8 | 3.36e-11 |

The last entropy value exceeds the nominal half-width by only 1.4e-16 numerical
evaluation roundoff. No reconstructed knot moves beyond source uncertainty,
apart from that explicitly quantified floating evaluation effect. The source
file itself is unchanged. Source uncertainty is not an EOS accuracy guarantee:
choosing the opposite side of a rounding interval can approach twice its
half-width of error relative to the unknown unrounded value.

Potential patches are mathematically C1 (bicubic) or C2 (biquintic), using shared
jets; the coordinate spline is smoother. Boundary-side state/derivative samples
and strict domain rejection are recorded. C2 continuity does not imply stability.
Pressure-volume cancellation and compressed-liquid inversion cause large
conditioning: the projected maximum scaled PT→rho/u Jacobian condition is
**1.43e8**, using input scales p,T and output scales rho,max(1,|u|).

At saturation, projected liquid g differs from direct EOS vapor g by at most
8.05e-8 kJ/kg in the dense scan. But retaining the old interpolated vapor fields
alongside any new liquid representation leaves coexistence g mismatches up to
approximately **0.00165 kJ/kg**. This includes old vapor interpolation error;
it is not attributed entirely to the liquid candidate. Clapeyron compatibility
with unchanged vapor fields is also unproved. A future multiphase foundation
needs a consistent phase boundary and vapor potential, not a liquid-only patch.

## Prototype cost and audit

Python-only static tests; no Node/coupled runtime improvement is claimed. Five
interleaved warm measurement rounds evaluate identical physical PT workloads
and the same p/T/h/s/rho/u outputs (300 evaluations per round). Means ± sample
standard deviations: original **19.641±5.657 ms**, joint PCHIP
**301.903±83.447 ms**, projected Gibbs **10.682±2.734 ms**. The large variability
and rejected physics prevent any adoption inference. Raw potential timings are
also recorded separately. One additional construction sample costs approximately
0.0095 / 0.692 / 3.406 / 13.270 s for joint / cubic / quintic / projected fits.

Potential patch arrays retain 891,264 bytes for cubic and 2,005,344 bytes for
quintic, plus small transform matrices and Python metadata. Full array totals
for every method are in `audit.json`; shared samples and object overhead are
separate. The comparison/evidence process peaked at **914,968 KiB (~894 MiB)**,
principally large diagnostic records, not normal solver memory. Evidence storage
is separately totaled by the audit. These prototypes do not measure browser,
JavaScript, future compressor/valve, or production-device performance.

The evidence/preservation audit **passed**. It verifies the frozen rounding bounds, domains,
independent EOS identities, residual-validated roots, recorded failures, and
unchanged files. **Passing the evidence audit means the investigation is
reproducible and honestly rejects the candidates; it is not scientific
qualification of a reconstruction.** No full Stage 2B matrix was run.

## Recommendation and remaining scope

Reject all current implementations. Recommend independent mathematical review
of the **rounding-bounded Gibbs formulation**, not adoption of this failed fit.
The smallest next authorized experiment would be a static feasibility study on
the first low-pressure cells: allow all source fields and their correlated T
coordinates to vary within demonstrated rounding intervals, and require a
negative-definite Gibbs Hessian together with PH/canonical uniqueness and EOS
accuracy. Review how stability can be certified between constraint points;
finite collocation alone is insufficient. No such correction was implemented.

Ranked alternatives: (1) stability-constrained Gibbs with explicit source
uncertainty and coexistence conditions; (2) directly constrained Helmholtz fit,
more natural for M/U/V but harder to condition on this nearly incompressible,
curvilinear sample grid; (3) joint monotonic field reconstruction only if Maxwell
and integrability are enforced, effectively restoring a common potential.
Expected accuracies of those unimplemented approaches remain unproved. Frozen
data demonstrate local potential information, not a unique robust global EOS.
Additional derivative/coexistence constraints or different information may prove
necessary; no new samples, oracle-fit values or empirical factors are assumed.

Untested: global stability certificates, exhaustive roots, intermediate regions
beyond finite sampling, reconstructed vapor/two-phase consistency, coupled
trajectories/events, and actual JS/browser cost. The strict 1 ms event budget and
all original conservation, temporal and nonlinear criteria remain unchanged.

## Files, environment and reproduction

Only five new files belong to this experiment:

* `experiments/dx-fv/static_property_reconstruction.py`
* `experiments/dx-fv/static_property_qualification.py`
* `experiments/dx-fv/static_property_diagnostics.py`
* `experiments/dx-fv/audit_static_properties.py`
* `experiments/dx-fv/STATIC_PROPERTY_RECONSTRUCTION.md`

Python 3.12.14, NumPy 2.5.3, SciPy 1.16.2, CoolProp 7.2.0; same frozen HEOS
Ammonia energy reference, no reference offset. Node 22.23.3 remains available but
is not used for these Python-only static candidates. Evidence is outside Git at
`/workspace/ammonia-static-property-evidence/`. The preserved joint-property
evidence is needed for replaying exact saved inventories. From repository root:

```bash
PY=/workspace/ammonia-joint-runtime/python/bin/python
E=/workspace/ammonia-static-property-evidence
$PY experiments/dx-fv/static_property_qualification.py "$E"
$PY experiments/dx-fv/static_property_diagnostics.py "$E"
$PY experiments/dx-fv/audit_static_properties.py "$E"
```

The `probes` diagnostic mode reuses completed static scans and refreshes saved
probes/derivative checks/timings. Preserve `preserved-files.json` before new work;
the original manifest audits 206 files. Generated evidence contains full knots,
PT/PH results, root attempts and validation, continuity, saturation, timings,
runtime versions, audit and early harness failures. An archive and checksums are
stored alongside the evidence for retention. Stop for review before any new fit,
integration, candidate adoption or full qualification.
