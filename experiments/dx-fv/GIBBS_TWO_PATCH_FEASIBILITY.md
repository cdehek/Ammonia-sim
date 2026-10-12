# Two-patch Gibbs feasibility experiment — rejected construction, unqualified research

**Decision: Chosen construction rejected.** Both frozen polynomial potentials
respect the source-rounding intervals and have between-node stability and
patch-local canonical injectivity certificates. They nevertheless fail the
unchanged **pressure error strictly below 10 Pa** requirement. The worst
successful comparisons are **331.279 Pa** in the low-pressure patch and
**6,017.648 Pa** in the high-pressure patch. A strictly interior high-pressure
comparison fails by **5,047.568 Pa**. These are independently reproduced accuracy
failures, not optimizer failures or evidence of impossible frozen data.

No property model is adopted; no Stage 2B, production or coupled-trajectory
qualification is claimed. Stop here for the user's decision. The recommended
next study is an **established EOS-backed browser architecture**, subject to new
authorization, rather than another broad frozen-table reconstruction effort.
The present experiment establishes that stable, consistent, source-compatible
local potentials exist; it does **not** establish an accurate reconstruction or
that such a reconstruction cannot exist.

The short [Mechanic's Report](two_patch/MECHANICS_REPORT.md) explains the result
without the mathematical detail. Reproducible scripts and all new evidence are
in [two_patch/](two_patch/README.md).

## 1. Authorization, provenance and preserved findings

Repository: `https://github.com/cdehek/Ammonia-sim.git`.
New isolated branch: `research/gibbs-two-patch-feasibility-20261012`.
Exact parent: `5318173b49719e263c2adda214a222a9c0533a47`.
Accepted A2 ancestor: `be9eb35a4ddf5098e685182f8104685127c6a6ee`.
The starting checkout was clean; repository identity, WIP ref, commit and A2
ancestry were verified before the new branch was created. The remote accepted
A2, WIP, main (`0473d32...`) and PR #3 head (`d442242...`) refs were recorded.
**All 215 pre-existing tracked files remain byte-identical.** No prior file,
frozen sample, default, root application file, workflow, solver or scientific
budget was edited. Only new experiment files were added. No transient was run.

Read and retained: `RESEARCH_WIP_HANDOFF.md`, `ASTRA_REVIEW_BRIEF.md`,
`JOINT_PROPERTY_CONSISTENCY.md`, `STATIC_PROPERTY_RECONSTRUCTION.md`, the static
reconstruction/qualification/diagnostic/audit sources, generator, property
engine and canonical adapter. The old files' statements that review was pending
remain historical. The present authorization and accepted Astra conclusions
come from the user's resumption instruction; a separate full Astra review
artifact was not supplied or fabricated.

Accepted findings remain explicit:

- Original Gibbs identities and coordinate transformations are correct.
- Existing interpolation has real negative-compressibility and multiple-root
  defects; these are not numerical timestep problems.
- Earlier fits omitted physical Hessian stability constraints. Their failures
  did not establish impossibility of a frozen-data reconstruction.
- The experimental joint-field PCHIP has a continuity defect where supported
  subcooling columns change. It and every earlier candidate remain unqualified.
- Two small static patches cannot establish a complete property backend or a
  qualified Stage 2B trajectory.

Historical external archives named in the handoff were absent in this fresh
workspace. Exact saved values in the committed reports and immutable source
were used for the static probes. Earlier full archives were not reconstructed
or represented as freshly audited. New evidence is retained in Git in full.

## 2. Source, domains and correlated rounding

Only these liquid samples entered the fit:

| Patch | Pressure, absolute bar | Offsets, K | Source rows (zero-based) | Liquid knots |
| --- | --- | --- | --- | ---: |
| Low | 0.300–0.3183890254214986 | 0, 1, 2 | 0–3 | 12 |
| High | 32.33098463554795–32.97852363503923 | 0, 1 | 236–237 | 4 |

Their six saturation rows supply liquid/vapor h, s, rho and saturation T.
**No extra liquid samples, EOS values, EOS derivatives or empirical pressure
corrections enter fitting.** The original source hash, runtime versions and
fitter hash are in `evidence/candidate.json`; complete preservation hashes are
in `evidence/provenance.json`.

The unchanged generator defines pressure coordinates as its binary64 pressure
values and computes all offsets using the true row saturation temperature before
rounding. T is rounded to eight decimals in Celsius; h, s and rho to seven:

- T interval: source Celsius + 273.15 ± **5e-9 K**.
- h interval: source ± **5e-8 kJ/kg**.
- s interval: source ± **5e-8 kJ/(kg K)**.
- rho interval: source ± **5e-8 kg/m³**.

The reconstruction uses `T_ij = Tsat_row + deltaT_row - z_j` with **one shared
row adjustment**, never independent temperature noise at different offsets.
This deliberately restricted construction chooses `deltaT_row = 0` during
fitting. The exported saturation polynomial's exact binary64 coefficients
realize row offsets of at most **2.851e-14 K** after coefficient rounding, still
shared by every offset in that row. This is a valid subset of the permitted
uncertainty set; it is not an exhaustive optimization over row temperatures.
No infeasibility conclusion can follow from rejecting this subset.

`exact-interval-audit.json` evaluates the exported potential with exact rational
arithmetic against **decimal** source centers and exact interval half-widths.
All 16 liquid knots and all 6 vapor boundary knots pass. Maximum deviations:

| Quantity | Low liquid | High liquid | Permitted half-width |
| --- | ---: | ---: | ---: |
| T, K | 2.851e-14 | 2.263e-14 | 5e-9 |
| h, kJ/kg | 4.900015e-8 | 4.900009e-8 | 5e-8 |
| s, kJ/(kg K) | 4.895706e-8 | 2.351606e-8 | 5e-8 |
| rho, kg/m³ | 4.899972e-8 | 4.900021e-8 | 5e-8 |

Vapor h/s/rho also pass, with the largest absolute entropy adjustment below
3.961e-8. Every deviation, rather than only maxima, is saved. Internal energy
has no separately rounded source column; it is derived from the same potential.

## 3. Mathematical construction and optimization constraints

Each assembly has **one total-degree-five polynomial**, with 21 coefficients,
in affine physical coordinates

`x = (p-pc)/ps`, `y = (T-tc)/ts`,

`g(p,T) = sum_{a+b<=5} c_ab x^a y^b`.

This alternative to a shared C2 biquintic is C-infinity throughout each patch;
it has no internal cell selection or independently estimated jets. The low
and high assemblies are disconnected and are not spliced together. All
coefficients, including every higher-order jet they determine, are optimized
simultaneously. No post-fit derivative stencil is used.

With p in bar, T in kelvin and g in kJ/kg:

` s=-g_T; v=g_p/100; rho=100/g_p; h=g-T*g_T; u=h-p*g_p. `

Let `D = g_pp*g_TT - g_pT²`. Physical single-phase stability requires

`g_p>0, g_pp<0, g_TT<0, D>0`,

and gives

`kappa_T=-g_pp/g_p`, `cp=-T*g_TT`, `cv=-T*D/g_pp`.

The physical derivative scaling by `ps` and `ts` is included explicitly. These
are constraints on the **physical thermodynamic Hessian**, not on an uncorrected
curvilinear-coordinate Hessian. The Maxwell identity is

`h_p|T = g_p - T*g_pT = 100*(v-T*v_T)`.

Linear knot constraints impose the actual h/s intervals and the exact reciprocal
rho interval `100/(rho_source+eps) <= g_p <= 100/(rho_source-eps)`.
The numerical fit targets 98% of each interval to retain evaluation margin;
this tightens constraints rather than changing the source or scientific budget.

At a 9×9 collocation set in each liquid patch the fit imposes `g_p>=0.05`,
`g_pT>=1e-6`, and positive definiteness of the negative physical Hessian, scaled
by `(2e-5, 0.02)` on its p and T diagonal entries, with matrix margin `0.02 I`.
Positive thermal expansion is an additional, stated constraint useful for the
historical nested inversion; stability alone does not require its sign.
**Collocation itself is not the stability certificate.** Certification of the
exported candidate is separate, below.

A convex quadratic smoothness objective penalizes coefficients of total degree
3–5, with weights `10^(degree-3)`, plus a small correction-norm tie. This is a
choice of prior among underdetermined fits, not a thermodynamic theorem or EOS
information. A low-degree least-squares initializer does not fix any derivative.
The source `fit.py` contains the complete scaling and objective.

Clarabel completed in 24/25 iterations and approximately 0.359/0.338 s. It
reported **`optimal_inaccurate` for low** and `optimal` for high. Optimality is
not claimed for low. Exact source-interval checks and separate stability
certificates, rather than the solver's status, establish the exported
candidate's constraint feasibility. The initial float normalized deviations
0.980000210/0.980004775 remain strictly below 1. An unchanged-code replay
reproduced all mathematical coefficients **bit for bit**; timing fields differ.

### Saturation and vapor compatibility

A single Hermite polynomial Ts(p) per assembly interpolates its saturation T
rows and slopes `100*T*(v_g-v_f)/(h_g-h_f)` computed from those frozen rows.
Degrees are seven (low, four rows) and three (high, two rows). Its coefficients
are source-only coordinate/boundary information. A polynomial vapor entropy
trace has degree three/one, with coefficients constrained in the same fit.

Define on the boundary

`G(p)=g_liquid(p,Ts(p))`, `g_v=G`,

`h_v=G+Ts*s_v`,

`100*v_v = g_p + Ts'(s_v-s_f)`.

Constraints on these vapor h/s/rho at the six rows use their actual intervals.
Thus Gibbs equality, `h_v-h_f=Ts*(s_v-s_f)`, and
`Ts'=100*Ts*(v_v-v_f)/(h_v-h_f)` hold along the entire modeled boundary. This is
a compatible **boundary trace**, not a qualified vapor property backend.
It can be understood as the first jet of
`g_v(p,T)=G(p)-s_v(p)*(T-Ts(p))` at the boundary. No vapor heat capacities,
physical off-boundary vapor extension or two-phase homogeneous Hessian are
claimed or constrained. The physical equilibrium derivative jump is retained.

Independent saturation comparisons use 41 pressures per patch. Max T errors
are 2.818e-8/6.285e-8 K. Floating Gibbs mismatches are zero; latent-identity
residuals are at most 2.274e-13 kJ/kg; Clapeyron residuals are at most
1.422e-14/4.441e-16 K/bar. These small identity residuals are structural,
not proof of accuracy. High-patch vapor-boundary h/rho errors reach
0.004873 kJ/kg and 0.0001112 kg/m³; high-patch saturated-liquid rho error reaches
0.006459 kg/m³. All boundary rows and EOS comparisons are saved.

## 4. Between-node certification and its scope

`certify.py` converts the exported binary64 coefficients to exact rational
numbers, differentiates them with exact scale factors, forms the physical
Hessian determinant polynomial, and converts power coefficients to Bernstein
coefficients on rational boxes. The convex-hull property encloses each entire
box. Printed bounds are rounded outward. This is a mathematical between-node
certificate for the specified finite polynomials, **not a dense-grid assertion**.

The high patch certifies on a padded enclosing physical PT rectangle subdivided
4×4. A coarse rectangle for the low patch gives an inconclusive negative lower
determinant bound because it includes distant extensions outside the curved
liquid domain. That bound is retained in the evidence. The low certificate uses
a 64×8 cover of the curved domain by physical rectangles whose T endpoints are
bounded using the separately certified monotone Ts polynomial. All 512 boxes
pass. Padding covers source endpoint and exported affine-coordinate roundoff.
No assertion of physical liquid behavior outside the declared patch follows
from the enclosing-box proof technique.

Conservative positive lower bounds on the complete declared liquid domains:

| Certified quantity | Low | High |
| --- | ---: | ---: |
| Volume, m³/kg | 0.00140839 | 0.00188434 |
| Compressibility, 1/bar | 2.07823e-5 | 2.26516e-4 |
| cp, kJ/(kg K) | 4.32698 | 5.41799 |
| cv, kJ/(kg K) | 0.0808986 | 0.395412 |
| Physical Hessian determinant | 4.11328e-9 | 1.16913e-7 |
| Absolute PT→rho/u Jacobian determinant | 0.00443762 | 0.110606 |
| `(du/dp)_v`, kJ/(kg bar) | 0.00377711 | 0.0517035 |

The exact-polynomial certificate is separate from binary64 runtime evaluation.
The script also supplies conservative coefficient-sum/coordinate-roundoff
estimates under normal IEEE arithmetic, including Hessian-product propagation.
Estimated determinant evaluation uncertainties are below 1e-19, many orders
smaller than the certificate margins. Independent 65/70-digit derivative and
state evaluations corroborate these estimates on tested points. This is not
a formally verified compiler or interval implementation of the runtime.

After the first frozen holdout run, certification code received only a more
conservative product-roundoff term and padding in its saturation slope bounds.
The coefficients, fitter, evaluator and holdout program were unchanged and their
freeze hashes are checked. First certificate output and all coarse bounds are
retained. These changes do not tune the property model against EOS.

## 5. Canonical recovery: local regularity and patch-wide injectivity

Fixed positive M,V,U give `rho=M/V`, `u=U/M`; no integration is involved.
For the physical potential,

`det d(rho,u)/d(p,T) = 100*T*D/g_p² > 0`.

This proves local regularity, **not alone global uniqueness**. For these specific
connected patch domains, the additional certified signs give a global argument:

1. `g_pT>0`: at fixed p, volume increases strictly with T. Density inversion has
   one T on the allowed vertical interval.
2. On each boundary `T=Ts(p)-z`,
   `100*dv/dp = g_pp + g_pT*Ts' > 0`. Hence both hot and cold boundary densities
   decrease with p. For any target rho, the supported pressure set is an interval
   (possibly empty), not disconnected pieces.
3. Along that connected isochore, `T'=-g_pp/g_pT>0` and
   `(du/dp)_v=T*D/g_pT>0`. Internal energy is strictly increasing.

There is therefore **at most one canonical state in each declared patch** for
any inventory, and exactly one for inventories in that patch's canonical image.
This is not a statement about the union of the disconnected patches, the full
table, or inventories outside either image. It does not guarantee every EOS
inventory belongs to the candidate image.

The historical algorithm assumes additional monotonicity that is not supplied
by `cp,cv,kappa>0` alone: its inner liquid density bisection assumes `rho_T<0`
(positive expansion), its pressure Newton step assumes a positive isochoric
energy slope, and its outer bracket assumes connected support. A stable fluid
can have zero or negative expansion. Coarse pressure-row searches can also miss
a narrow valid interval or a root without a sampled sign change. This static
recovery first locates the supported pressure interval from monotone boundary
curves; it is **not installed into the historical solver**. Fixed-pressure h
inversion is monotone because cp is positive.

All 30 same-candidate PH/canonical roundtrips pass with residual checks. They
support the implementation, but are not the injectivity proof. Eight explicit
out-of-domain queries are rejected. Independent high-precision differentiation
of the scalar polynomial checks physical first/second derivatives and Maxwell;
this avoids merely comparing two aliases of the same assembled identity.

### Original counterexample and saved probes

The immutable original surface, evaluated with its saved diagnostic class,
reproduces three residual-validated roots for the historical inventory
`rho=708.6710262223568`, `u=94.48059153610271`:

`0.302985440687645`, `0.302989370566117`, `0.314879847308798` bar.

The finite original scan establishes these counterexamples; it is not an
exhaustive root certificate. The new candidate's one low-patch root is
`0.302121252200157` bar, versus independent EOS `0.301747903654853`:
**+37.3349 Pa**, failing the accuracy gate despite uniqueness.

For the independent EOS inventory at the originally reported physical state
`p=0.3029893712344606 bar`, 1 K subcooling, the candidate root is
`0.302980118534660` bar. Its error against EOS inventory recovery is
**−0.92527 Pa**. Passing this one fixture does not rescue the failed patch.

| Saved high PH state | Forward candidate pressure error at EOS rho/u | Reverse `p - p_EOS(candidate rho/u)` |
| --- | ---: | ---: |
| Initial: p=32.65314902038559, h=686.779725665 | −5,057.81 Pa | −3,392.55 Pa |
| Endpoint: p=32.80473738460169, h=686.845872427996 | +2,637.41 Pa | +1,691.53 Pa |

Forward and reverse errors are different comparisons and are not conflated.
At the original table's saved initial inventory, the candidate has **no state
inside the high patch**; independently evaluated energy endpoint residuals are
both positive. At the original endpoint inventory, its unique root is
32.7803437812065 bar and differs from EOS by **+824.532 Pa**. Original-surface
inventories reconstructed from exact saved PH differ in last bits from the
rounded narrative initial inventory; the actual numbers used are recorded.
No stored trajectory was changed or rerun.

## 6. Frozen holdout accuracy and uncertainty

Before the first EOS import, `validate.py` checks `candidate.sha256` and records
`freeze.json`, including code hashes and the deterministic holdout design.
Candidate SHA-256:

`fe646584649da33f7467a430dd15cf28c46b06c2a1532c4a6e171c89dcfc8808`.

There was one fitted construction, with one assembly per patch. It was not
retuned after EOS results. The later identical-code refit was solely a
reproducibility check and did not replace the frozen coefficients.

CoolProp **7.2.0 HEOS Ammonia**, unchanged energy reference, supplies validation
only. Each cell uses five fixed interior pressure fractions and supported
subcooling offsets including 1e-6, .001, .01, .1, .25, .5, .75 and points near
the cold boundary. Pressure-row interfaces/edges, the z=1 interface, saturation,
and the saved problematic states are included. PT comparisons use the **same
physical T**, not merely matching offset labels. Near-saturation PT reference
calls explicitly select the stable liquid branch; saturation uses PQ.

| Static holdout result | Low | High |
| --- | ---: | ---: |
| PT/canonical holdouts | 211 | 53 |
| Successful canonical recoveries | 178 | 30 |
| Inventories outside candidate image | 33 | 23 |
| Maximum successful pressure error | **331.279 Pa** | **6,017.648 Pa** |
| Maximum strictly interior pressure error | **331.279 Pa** | **5,047.568 Pa** |
| Maximum successful T error | 3.864e-5 K | 0.002695 K |
| Maximum successful h error | 0.0004682 kJ/kg | 0.011366 kJ/kg |
| Maximum fixed-PT rho error | 9.205e-5 kg/m³ | 0.008613 kg/m³ |
| Maximum fixed-PT u error | 1.223e-7 kJ/kg | 0.0007799 kJ/kg |
| Maximum fixed-PT cp error | 8.607e-7 kJ/(kg K) | 0.003478 kJ/(kg K) |
| Maximum fixed-PT cv error | 2.34312 kJ/(kg K) | 1.81558 kJ/(kg K) |

The unchanged limits are **p error <10 Pa, T error <0.01 K, h error <0.05 kJ/kg**.
The successful subsets meet T/h limits but fail pressure. Failed queries remain
failures, not excluded successes. All 56 failures were independently checked
at 65 digits: density support exists, but target energy is outside its monotone
endpoint range. The smallest endpoint-sign magnitude is 2.004e-8 kJ/kg, well
above the observed arithmetic uncertainty. No extrapolated state is counted.
This numeric existence audit is not a formal interval root enclosure; the
analytic injectivity result remains separate.

High-precision rejection witnesses, with fixed M/U/V, are retained. Low:
`p=0.30643755129082695`, EOS offset .25 K, gives +331.27906734 Pa.
High: `p=32.33098463554795`, EOS offset .5 K, gives +6017.64766105 Pa.
Both roots lie strictly inside their candidate images and have high-precision
rho/u residuals below 1e-55. The high witness is on a pressure edge but off-knot
in temperature; the separate strictly interior failure removes edge dependence.

Numerical/reference uncertainty is evaluated separately from source rounding:

- Direct HEOS PT vs independent DT and DU input paths were checked at a fixed
  subset. The largest high-pressure prescribed-P residual is **0.02542 Pa**;
  DU-vs-PT pressure difference is **0.05020 Pa**, T difference ≤2.381e-8 K,
  h difference ≤1.103e-7 kJ/kg. Low-pressure DU disagreement is ≤2.715e-6 Pa.
  These are measured numerical discrepancies, not rigorous all-state bounds.
- Candidate binary64 vs 65/70-digit evaluation differs by ≤3.909e-13 kg/m³ in
  rho and ≤2.045e-13 kJ/kg in h/u on the checked subset. Recovery pressure
  disagreement is ≤**3.897e-6 Pa**, T ≤4.270e-13 K and h ≤5.343e-12 kJ/kg.
- Independent EOS Maxwell residual is ≤8.327e-17 kJ/(kg bar). Candidate
  identities follow a common scalar potential and are also checked by
  high-precision differentiation, rather than only float algebraic cancellation.
- CoolProp does not provide an independent experimental uncertainty estimate
  here. These gates compare against the specified HEOS model. No claim of
  experimental ammonia accuracy follows from agreement with that model.

The pressure failures exceed all evaluated numerical uncertainties by large
margins. No tolerance was relaxed. There is no accuracy certificate between EOS
holdouts; a demonstrated holdout failure is sufficient to reject this candidate.

## 7. Continuity, conditioning, cost and limitations

C-infinity continuity inside each assembly is structural. Two-sided physical
state/derivative probes across internal pressure lines and z=1 are recorded at
1e-7 and 1e-9 separations; differences decrease with separation. There is no
support-column switch in either complete rectangular knot assembly. No
continuity between the disconnected low/high domains is asserted.

Maximum sampled scaled PT→rho/u condition numbers are **1.003e7** and
**2.662e3**, using input scales p,T and output scales rho,max(1,|u|).
This sensitivity explains why close values and stable signs do not force
accurate pressure. In particular, positive cv is not accurate cv: large cv and
compressibility discrepancies remain despite certification.

Five rounds of Python static evaluation, including derivatives and condition
number calculation, cost approximately **64.4±7.2 microseconds/state** low and
**62.0±3.2 microseconds/state** high. Static nested recovery costs
**7.86±0.77 ms/state** and **5.01±0.13 ms/state** on its small same-candidate
workload. Retained polynomial coefficients use 264/216 bytes; these exclude
objects, source arrays, libraries and evidence. Validation process peak RSS is
187,268 KiB. Final exact-rational certification took about 20.35 s, dominated
by the low curved-domain cover. These are single-machine prototype observations,
not browser performance or solver integration costs.

Failures and unresolved limitations:

- Pressure accuracy fails on both patches, including strict interior points;
  some valid EOS inventories lie outside the candidate image.
- The low optimizer did not certify optimality. Postchecks establish this
  exported fit's feasibility; they do not establish that the smoothing prior
  selected the most accurate source-compatible potential.
- Row temperature shifts were fixed at centers, and the polynomial family,
  slope construction and regularizer are choices. Other choices are untested.
- Stable source-compatible potentials are nonunique. The sample/constraint set
  does not, by this experiment, identify the missing compressibility/isochoric
  accuracy tightly enough to infer a 10 Pa guarantee.
- Vapor work is a coexistence trace only. Whole-domain liquid, vapor, two-phase
  recovery, critical behavior and inter-patch joining remain untested.
- Neither local success nor failure proves global adequacy or insufficiency
  of the frozen table. No information-theoretic impossibility result is claimed.
- No full coupled simulation, event timing, conservation trajectory, temporal
  order test, browser integration or Stage 2B qualification was performed.
  Newton, TR-BDF2, physics, defaults and all original budgets are unchanged.

## 8. Recommendation and retained evidence

The classification is **Chosen construction rejected**, not “locally viable”
and not merely “inconclusive”: independently reproduced pressure failures
invalidate this frozen candidate. The certification work is still informative:
stable, coherent, source-rounding-compatible local potentials **can** be
constructed for these regions. Stability and source compatibility do not select
an accurate isochoric response by themselves.

Do not expand this fit into the full property domain or the evaporator. There
is no demonstrated clear viability to justify another broad reconstruction
implementation. Recommend the next separately authorized study examine an
established EOS-backed browser architecture, including a reproducible HEOS
reference convention, browser/WASM or service feasibility, licensing, offline
needs, latency and domain/error handling. None of that work is implemented here.
A further frozen-data study would be a targeted mathematical identifiability
question, requiring a new decision; this rejection does not prohibit it or
prove it hopeless.

The evidence audit passes **as an evidence audit**. It verifies exact source
intervals, stable exported polynomials, canonical injectivity hypotheses,
independent rejection witnesses, source preservation and unchanged frozen
coefficients. It does not qualify the candidate. The README gives pinned
reproduction commands and a map of every evidence file. The branch is research
only and remains unqualified. Stop for review; no merge or promotion.
