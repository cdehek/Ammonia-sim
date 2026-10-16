# B5A Gate B — endpoint-constrained DU recovery feasibility

**CONDITIONALLY FEASIBLE**

A physically admissible mathematical recovery exists for each original exact
inventory under the unchanged ammonia EOS. Endpoint-centered equilibrium
equations and stable homogeneous branch checks demonstrate those solutions in
65/90-digit arithmetic. Ordinary binary64 recovery with certifiable phase has
**not** been demonstrated for the four unresolved endpoints. Original scientific
qualification remains incomplete. No functional patch or qualified backend is
delivered. Stop for engineering review and explicit approval.

Branch: `research/browser-eos-b5a-gate-b-feasibility-20261016`.
Starting commit: `cc2ec6b54d40cabea93fa761d10a2ecab59def25`, clean before branch
creation. The research delivery SHA is the commit containing this report; obtain
it with `git rev-parse HEAD`, or the exact SHA in the delivery response. This
avoids a self-referential hash inside its own commit.

## Preservation and native reproduction

The pre-experiment audit verifies all 1,782 reconstructed Gate A source hashes,
all five inherited patches by hash and reverse applicability, 143 historical
artifact identities (including compressed/decompressed native libraries), and
all 12 accepted A2 dependency snapshots against Git objects at
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. Source is pinned upstream 8.0.0
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`. Only inherited patches are applied
to the external verification checkout. No compile occurs. Dependency trees are
not downloaded or rebuilt; their historical manifests remain preserved and no
new dependency-build verification is claimed.

The uninstrumented Gate A library SHA256 is
`3cbe3fd0ad16309ca498ccce7ec6c89f37bf7b1fe9036a5799f37ce612fba6f0`;
the inherited logging-only Gate A library is
`86186ff71e9fdceb9a8b6b7807922991d58ca25c172bd3b2cf12327d978e24c9`.
Both are verified before loading. All seven saved records reproduce the exact
inherited results, with logging and fresh/reused parity. The three repaired
stable-liquid controls (146,151,152) retain their original bits and outcomes.

| Original ledger | rho bits | u bits | Gate A native result |
|---|---|---|---|
| 148 | `403c0d271287772f` | `4136f0424572bf7f` | QT refuses Q=1.000000000000002 |
| 162 | `40804c41552836e8` | `4125463722133410` | raw homogeneous liquid; physical qualification unresolved |
| 164 | `403c0d2712877730` | `4136f0424572bf7e` | QT refuses Q=1.0000000000000018 |
| 165 | `403c0d271287772d` | `4136f0424572bf80` | QT refuses Q=1.0000000000000024 |

Requested (rho kg/m³,u J/kg) are respectively
(28.051377447197577,1503298.271282166),
(521.531900705505,697115.5665527601),
(28.05137744719758,1503298.2712821658), and
(28.05137744719757,1503298.2712821662).
Inputs are decoded from bits, not reconstructed from these display decimals.
Original M,U,V and the original bar/kJ operation order remain in the fixed ledger.

The three refused updates dispatch coexistence and end Brent at iteration 10,
T=345.5636735993518 K, on its unchanged scaled-residual criterion. Final quality
residuals are -1.9984e-15, -1.9984e-15 and -2.22045e-15, below the captured
1.53461e-13 stopping threshold. Last-evaluated and returned T agree. Their C API
error is exactly `Error: Input vapor quality [Q] must be between 0 and 1`, wrapped
as `ValueError`; underlying historical C++ type is `OutOfRangeError` at QT.
No returned DU state exists after these exceptions.

`four-case-reproduction-and-controls.json` retains every requested/internal bit,
phase decision, final saturation coordinates, Brent event, returned state or
exception, and fresh/reused result. It recomputes saturation at the **actual
traced internal molar coordinates**, at both precisions. Internal input-minus-
saturation u is -1.42178e-10 (148), +2.33353e-9 (162), -3.52750e-10 (164), and
+6.53502e-11 J/kg (165). These repeat the inherited B5A mathematical signs.
External mass-inventory and internal molar-coordinate references are labeled
separately; their conversion differences are never silently removed.

For refused cases, independently reconstructed QT endpoint/algebraic-mixture
audits report volume/u residuals without claiming access to a returned state.
QT pressure getters share a saturation pressure; their zero difference is not
an independent EOS equality check. `supplement.json` additionally evaluates p/g,
volume and energy with the independent 90-digit EOS at those reconstructed
endpoint coordinates. Row 162's fresh homogeneous DT u residual is
3.49246e-10 J/kg and volume residual is zero; passing those numerical checks
does not resolve its physical endpoint classification.

## Independent mathematical recovery

[FORMULATION.md](FORMULATION.md) derives pL=pV, gL=gV and original-volume/energy
constraints and admissibility. The standalone high-precision prototype computes
the small endpoint fraction directly, solves three equilibrium unknowns, rejects
extrapolated mixture qualities, and verifies stable homogeneous roots separately.
It neither modifies CoolProp nor supplies properties to the accepted solver.

The following are **mathematical same-EOS** results for the exact external mass
inventories. Full digits, pressure, mixture density/u and all stability/residual
checks are machine readable. The coexistence continuation for 162/165 is
explicitly inadmissible, even though its equations converge.

| Ledger | Mathematical selected branch | Selected T (K, diagnostic display) | Coexistence continuation's small endpoint fraction | External u minus fixed-density saturation u (J/kg) |
|---|---|---:|---:|---:|
| 148 | equilibrium | 345.563673599351758912 | 1-Q=+1.2928515583e-16 | -1.0153043823e-10 |
| 162 | stable liquid | 345.563673599351872542 | Q=-9.7725547090e-17, excluded | +2.2769883590e-9 |
| 164 | equilibrium | 345.563673599351752898 | 1-Q=+4.2220767149e-16 | -3.3156884589e-10 |
| 165 | stable vapor | 345.563673599351801198 | 1-Q=-1.6008182838e-16, excluded | +1.2571573344e-10 |

At the 148 equilibrium T, coexistence densities are approximately
521.531900705503555554 and 28.051377447197573766 kg/m³. For 164 they are
521.531900705503567668 and 28.051377447197569544 kg/m³. Full endpoint coordinates
and the inadmissible continuations for 162/165 are retained. Homogeneous cv is
about 2748.79 J/kg/K for liquid, 2645.56 for vapor, with dp/drho|T about 459101
and 83745.7 Pa/(kg/m³), respectively. cp and compressibility are also positive.
148/164's homogeneous candidates still lie inside the dome and are rejected.

Seven original roots repeat at 65 and 90 digits: maximum selected-pressure
change is 4.75e-54 Pa. Two deliberately displaced coexistence seeds per
unresolved original converge to the same local root (maximum T spread
4.44e-52 K). All 47 mathematical inventory cases converge. Across that matrix,
maximum equilibrium p/g/u residual magnitudes are about 6.52e-51 Pa,
1.17e-52 J/kg and 4.18e-54 J/kg. These tiny residuals check arithmetic convergence,
not physical ammonia accuracy. Original independent phase resolution remains
1e-5 Pa / 1e-8 J/kg; all four original separations remain below it.

## Binary64 feasibility and neighboring states

The binary64 prototype uses separate unmodified native DT EOS states, analytic
thermodynamic Jacobians, endpoint-centered fractions/energy residuals and a
dense 3x3 Newton solve. Three local seeds are tested with two diagnostic stop
policies: original independent residual limits, and continued iteration until
coordinate repetition/stagnation or a 20-iteration bound. Neither stop changes
any accepted backend or solver criterion.

All **282** algebraic attempts meet original p/g/u residual limits, yet many
return an inadmissible or incorrect-branch mixture. All **42** original-case
attempts repeat exactly in a separate process, apart from elapsed time.
Determinism does not make a wrong branch acceptable.

| Ledger | Float64 Q range across six attempts | Why it is not a certified recovery |
|---|---|---|
| 148 | 0.9999999999999989 to 1.000000000000001 | physical fraction changes with seed/termination |
| 162 | -9.91296e-17 to +2.35433e-16 | mixture sign changes; raw liquid return remains separately reproducible |
| 164 | 0.9999999999999994 to 1.0000000000000009 | admissible, endpoint and invalid outputs occur |
| 165 | 0.9999999999999996 to 1.0000000000000016 | apparently admissible mixtures conflict with mathematical stable vapor |

The inventory inputs themselves are exactly representable and preserved. The
obstacle is evaluating/locating the thermodynamic boundary accurately enough.
Endpoint energies are O(1e6 J/kg), while relevant differences are O(1e-10–1e-9).
Centered sums cannot remove error in the endpoint EOS evaluations. Ordinary
homogeneous native roots can also change the sign of density-minus-saturation
for the vapor cases with different seeds, despite positive local derivatives.

One temperature ULP is 5.68434e-14 K here. 148/164's equilibrium T lies only
0.086/0.281 ULP below its external fixed-density saturation boundary. 165's
algebraic coexistence continuation lies 0.106 ULP above its boundary. No physical
native-QT sign bracket is established in the adjacent-temperature experiment.
The 162 continuation is about 7.83 ULP above its boundary, but the original
caloric phase resolution still cannot qualify the sign. This is evidence of
endpoint inequality uncertainty, not a proof of fundamental binary64 impossibility.

The bounded matrix contains seven exact controls/originals plus 40 explicit
diagnostics: rho±1/±16 ULP, u±1/±16 ULP and fixed-density u±0.01 J/kg for each
unresolved original. The latter offsets are diagnostic binary64 additions,
never accepted finite-difference perturbations or substitute inventories.
The -0.01 cases are genuine mathematical coexistence and all six float64
attempts have physical fractions; +0.01 cases have stable homogeneous roots
and their extrapolated mixtures are rejected. Nearer neighbors switch branch
and/or native exception outcome. [NEIGHBORS.md](NEIGHBORS.md) retains every case.
All 47 native fresh/reused results agree; **13 QT exceptions remain**. No
homogeneous derivative smoothness is imposed across boiling.

## Three separate questions, case by case

| Original | A: admissible same-EOS mathematical solution? | B: reproducible binary64 recovery certified at the exact input? | C: all original qualification/reference criteria met? |
|---|---|---|---|
| 148 | YES, coexistence | NOT DEMONSTRATED; QT refusal, prototype sign sensitivity | UNRESOLVED; independent phase separation below resolution; no browser candidate |
| 162 | YES, stable liquid | NOT DEMONSTRATED as certified recovery; raw Gate A liquid is reproducible | UNRESOLVED; raw numerical success is not independently resolved phase qualification |
| 164 | YES, coexistence | NOT DEMONSTRATED; QT refusal and inconsistent prototype endpoint admissibility | UNRESOLVED; independent phase separation below resolution; no browser candidate |
| 165 | YES, stable vapor | NOT DEMONSTRATED; QT refusal and false mixture candidates | UNRESOLVED; homogeneous-side mathematical sign is not physical certainty |

None of these B/C conclusions asserts that all possible improved binary64
algorithms are impossible. No all-four binary64 recovery certificate has been
established under the available interface and unchanged reference contract.

## Cost, browser limits and recommendation

Measured local Python prototype times include EOS work and diagnostic collection,
but exclude factory initialization. Equilibrium binary64 attempts have median
0.816 ms, maximum 5.97 ms, over mixed seeds/stopping policies. Of 282 attempts,
141 stop at original reference limits; 108 hit the iteration bound, 30 repeat
coordinates, and three corrections round to unchanged coordinates. High-
precision equilibrium solves have median 0.170 s, maximum 0.385 s, 2–3 Newton
steps in these local seeds (54 solves including precision repeats). Native Gate A
47-case reused updates have median 0.390 ms; failed updates remain failures.
These single-host samples are not rigorous throughput comparisons or estimates
of a compiled implementation. Per-attempt timings and iteration histories remain.

Binary64 Jacobian work is two endpoint DT updates per iteration plus a constant-
size linear solve. High-precision numerical differentiation costs additional
EOS evaluations, recorded in each solve. No speculative native/WASM compilation,
browser candidate test, worker/memory test or physical iPad test is performed.
Native evidence cannot qualify browser recovery. Porting the centered formulation
is plausible; certifiable endpoint evaluation and native/WASM last-bit parity
remain unmeasured requirements. The preserved browser interface does not expose
the inherited full-VLE configuration. No backend is qualified by this report.

[STRATEGIES.md](STRATEGIES.md) compares coupled, bracketed, stable-homogeneous,
higher-precision and uncertainty-classification approaches, including H/S/U
caller risks and future acceptance gates. Recommend further work on centered
equilibrium residuals with stable-branch/error certification. A separate reviewed
uncertainty policy may be necessary if the original reference contract cannot
distinguish a state. It is not adopted here. No quality clamp, endpoint snap or
unconditional homogeneous fallback is justified.

All canonical limits remain <=0.1 Pa, <=0.1 J/kg, <=1e-4 K; original fluid
nonlinear scale <=1e-11, standalone strictly <10 Pa/<50 J/kg/<0.01 K, independent
root resolution 1e-5 Pa/1e-8 J/kg, original conservation/derivative/support,
Newton/TR-BDF2/hydraulic/thermal requirements remain unchanged. Accepted A2,
B1–B5A and UI checkpoints and all historical files are protected by the starting
manifest and remote audit. B5's seven browser 35-bar strict-support failures and
their mathematical diagnoses remain unchanged, as does rejected-PT loader
cleanup. No B5B work, loader change, A2 campaign, production/UI/Live Plant change,
merge or deployment occurs. Only this additive research branch is pushed.
