# B2 — Browser EOS precision and accepted A2 qualification

**Final assessment: BLOCKED.** The preserved 44-bit candidate has a demonstrated
near-liquid-boundary property/canonical defect that also rejects a zero-exchange
trial in the unchanged coupled model. The complete A2 option/reference matrix
remains incomplete. Successful tests below do not certify the complete A2
operating domain or a physical iPad.

Delivery branch: `research/browser-eos-b2-qualification-20261015`. The delivery
commit is the Git commit containing this report; its full SHA is supplied in the
handoff. Starting branch was exactly
`research/browser-eos-precision-backend-20261015`, clean HEAD
`ef1562ae1680fccf3323391e9ec83788c5ae1e69`. Accepted five-section A2 is exactly
`be9eb35a4ddf5098e685182f8104685127c6a6ee`.

## Scope, provenance and qualification boundary

[QUALIFICATION_MATRIX.md](QUALIFICATION_MATRIX.md) records the pre-experiment B1
versus B2 boundary. [SUITE_RESULTS.md](SUITE_RESULTS.md) is the final per-contract
ledger, including every pass, failure, blocked and unexecuted accepted path.
Machine-readable results, source hashes and independent audits are in `evidence/`.
[README.md](README.md) gives reproduction commands and output isolation.
[HARNESS_BOUNDARIES.md](HARNESS_BOUNDARIES.md) identifies concrete missing
interfaces and separates them from unexecuted but mathematically equivalent
configuration/reference paths.

The 12 B1 accepted dependency snapshots were verified byte-for-byte against the
accepted A2 Git objects. All 609 B1 starting tracked files are pinned in
`evidence/checkpoint.json` and checked again at completion. Experimental additions
are confined to this B2 directory. Original official 8.0, source 30-bit, official
7.2 and source 44-bit JS/WASM, source patch, B1 evidence and reports remain intact.
No EOS coefficient, ammonia data, reference convention, accepted source, fixture,
solver, perturbation, tolerance, rollback rule or result is modified.

The candidate uses the unchanged B1 loader and PH/DU adapter. Separate domain
experiments add the isolated B2 `adapter-pt.mjs` mapping described below.
Canonical equations are
M=rho V and U=Mh−PV; density is the untouched PH flash result and DU recovers the
actual inventory. Stage PH coordinates retain their requested values. The
accepted table supplies a support guard, not returned EOS properties. Accepted
M/U/V conservation, transport, signed face fluxes, thermal exchanges, five-section
geometry, TR-BDF2/Newton, line search, event refinement and failure-aware growth
run from the accepted source. No property correction, smoothing, input rounding,
clamp, fallback table property or silent restart is introduced.

## Exact near-saturation experiment

The new matrix contains 236 PH inputs: preserved B1 liquid/vapor/two-phase inputs,
the exact B1 failing vapor point, and labelled diagnostic approaches at four
pressures. Enthalpy offsets from saturation are 0, 1e-5, .001, .01, 1 and 100 J/kg;
interior qualities include 1e-8, .01, .5, .99 and 1−1e-8. Every input and perturbed
input retains its binary64 bits. Both signs of the original pressure and enthalpy
probes run unchanged, with nominal denominators and actual representable increments
recorded. These offsets are diagnostic fixtures, not replacement solver probes.

All four backends run in Chromium and WebKit. Each has 1,180 base/probe snapshots,
no flash exception in this PH matrix, and 78 probes changing backend phase.
Homogeneous derivative ratios are excluded on phase crossing and coexistence
outputs. Exclusion does not mean that an invalid returned state passes a value or
canonical gate. Stable liquid, equilibrium coexistence and stable vapor have
separate results in `phase-region-summary.json`. Native 8.0 independently evaluates
7,080 browser DT states; native 7.2 evaluates 2,360. Matching native/browser DT
pressure disagreements are at most 2.51e-8 and 7.87e-8 Pa, respectively; enthalpy
disagreements are at most 2.91e-11 and 1.75e-10 J/kg. There are no native DT audit
exceptions. These are implementation checks of the same EOS, not experimental
ammonia accuracy claims.

The first B2 diagnostic omitted homogeneous supercritical-gas phase enum 2.
All eight matrices were rerun with phases 0,1,2,3,5 treated as homogeneous;
critical phase 4 stays excluded. This adds 640 analytic-derivative snapshots.
Every physical output and input is bit-identical to the first run. The originals
remain in `evidence/phase-v1/`; `phase-classification-correction.json` records
the comparison. The corrected candidate has 747 homogeneous, 410 physically
bounded coexistence and 23 outside-quality snapshots per browser.

Chromium/WebKit numerical phase rows are identical for each backend. Source30
matches official8 exactly. The native versions/revisions are pinned in evidence;
no native 44-bit source build is claimed. Native unmodified PH bias and independent
DT roots are reported separately.

### Remaining vapor residual and source attribution

Exact primary vapor input is P=799999.9981754856 Pa (bits `412869ffff10db75`),
h=1624022.744737779 J/kg (bits `4138c7d6bea72295`). Returned T is approximately
291.01436145 K and rho approximately 6.26655090 kg/m³, about .001 K above
saturation. Detailed per-backend pressure/h residuals, analytic derivatives and
both signed fixed-probe estimates are in the phase summary and raw files.

The 44-bit candidate still has an independent caloric residual near
−1.1919e-4 J/kg. Its fixed-probe slopes remain close to the homogeneous EOS
partials. Independent native 8.0 reproduces about −1.19462e-4 J/kg, even when its
PH getter misses requested h by only +2.73576e-7 J/kg. Thus the getter is not a
sufficient convergence test. Reinitializing a fresh state, or the same state, at
returned DT exposes different pressure and enthalpy at unchanged physical DT.
Native 7.2's coherent PH getter also misses the requested h by about −1.19e-4 J/kg.

A public PT call at the returned T reproduces the cache inconsistency independently
of the outer PH root solve. Native warm-path opt-out `PXFLASH_DIRECT_EOS=0`, gas
phase imposition, and disabling superancillaries do not remove it at this point.
An independent diagnostic DT Newton root changes T by about 3.98e-8 K and reaches
the prior reference residual limits, 1e-5 Pa/1e-8 J/kg. That root is never fed into
WASM, the adapter or the coupled solver.

Source inspection strongly identifies a separate cache-consistency path:

- `src/Backends/Helmholtz/FlashRoutines.cpp::PT_flash` assigns the density returned
  by `solver_rho_Tp` directly (line 336 in the pinned source).
- `src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp::SolverTPResid::call`
  evaluates and caches properties at the trial density.
- `src/Solvers.cpp::Householder4` evaluates that residual, increments x, then can
  return the incremented x without a final residual evaluation.
- The outer PH routine resets its iteration count and evaluates the bracket
  midpoint through this cold PT path. Tightening the outer bracket does not
  clear cached inner-density derivatives at the final assigned density.

A first-order calculation that accounts for the final explicit delta prefactor
in `calc_hmolar` predicts cached-minus-DT h=0.0001197352405 J/kg, versus observed
0.0001197354868 J/kg: relative attribution error approximately 2.06e-6. A retained
initial full-gradient estimate differed by 31%; the refined derivation removes
the explicit-prefactor contribution that is already evaluated at final density.
Both calculations remain visible. Source snapshots, native public-API trials,
reference root steps and both attribution records are preserved. This is strong
source/numerical evidence, not an instrumented final WASM iteration trace.

The 44-bit homogeneous sample maxima are approximately 1.36e-6 Pa and
1.19761e-4 J/kg. The local five-section inventory energy contamination scale at
the saved vapor point is 4.49e-10 kJ normalized by the accepted unit energy scale,
above the existing 1e-11 nonlinear scale. That is a local risk screen, not a new
universal property tolerance or proof that every trajectory fails.

### Demonstrated liquid-boundary defect

A distinct, larger defect occurs at the physically valid liquid input:

```
P = 30298.937123458254 Pa
h = 98904.56398938334 J/kg
h − hf = approximately −0.001 J/kg
```

The flash returns T=218.26293725550536 K, rho=707.4995406964335 kg/m³,
phase=two-phase, Q=−6.99036205016646e-10. A fresh DT evaluation returns
P=33169.439756531385 Pa and h=98907.15313182138 J/kg: errors **+2870.502633 Pa**
and **+2.589142438 J/kg**. The pressure error exceeds the unchanged standalone
10 Pa budget. An independent stable-liquid EOS root exists for the exact input;
this is not an invalid caller request or a demand for smooth derivatives across
a first-order phase boundary.

The pinned phase-determination source admits Q in [−1e-9,1+1e-9] into the two-phase
lever formula. Below hf, negative Q extrapolates specific volume outside the
physical coexistence interval. Small negative quality is greatly amplified on
the dense liquid side. The 44-bit PH single-phase patch does not control this
phase-classification/extrapolation path. All four browser backends reproduce the
same maximum, so this is not a defect newly introduced by the 44-bit change.

The unchanged accepted adapter and equations give an even more direct failure:
with V=.003/5 m³, form M=rho V and U=Mh−PV, then call stateMVU. Recovered pressure
moves by **0.04245087079 bar**, h by **0.00600012696 kJ/kg**, and T by
**0.000495447 K**. Original allowed differences are 1e-6 bar, 1e-4 kJ/kg and
1e-4 K. All three fail. Adapter bar/kJ-to-SI round trips preserve the exact input
binary64 values for these fixtures; the recorded values verify that explicitly.

Each engine's additional eight-case canonical screen passes one endpoint and
fails seven entries: six show numerical PH/DU inconsistency and the 35-bar entry
encounters the original support guard on recovery. The originating PH state is
supported; an inversion that leaves support is not evidence of a genuine physical
operating-domain exit. Every error remains visible. The same screen fails with
source30. Independent native stable-liquid roots, their traces and homogeneous
partials are in `boundary-native-roots.json`.

The supplementary zero-exchange initialization experiment loads the unchanged
accepted five-section coupled source with these same PH inputs, sealed faces,
zero refrigerant exchange and zero external load. It advances no trajectory.
Six liquid-side cases initialize at different recovered P/H and then reject a
0.001 s pure trial with **Canonical M/U/V recovery disagrees with stage PH
coordinates**, fault kind solver. The state is preserved exactly. In the detailed primary trial the original
Newton residual already converges at iteration zero (fluid norm about
2.29e-14), then the unchanged stage/recovery compatibility check rejects it.
Thus a green residual or mass ledger alone would miss the fault. The endpoint
case completes that trial; the 35-bar case errors on initial recovery. These are
additional declared diagnostics, not replacements or edits to accepted operating
fixtures. This demonstrates a material backend failure through the accepted
solver contract, without interpreting an intentionally wet outlet as a failure.

Physical coexistence points with Q in [0,1] have a maximum independently evaluated
P residual 9.76e-8 Pa and h residual 4.66e-10 J/kg in this sample. Negative/outside
quality results are reported separately; neither that successful interior sample
nor a favourable derivative ratio can certify the boundary.

### Phase-aware interpretation

Actual backend phase, returned Q, h−hf, h−hg and T−Tsat are retained at every
base/probe state. For unchanged single-phase branches, analytic density partials
and signed fixed finite differences are compared. The candidate's descriptive
ratio range is about .99947052–1.00737433; no evaluated same-phase ratio differs
by more than 1% **within that backend-homogeneous subset only**. That 1% statistic
is descriptive, never an acceptance budget or a claim about all physically
single-phase inputs. The independently classified liquid counterexample below
fails severely and is outside that restricted subset.
30-bit controls retain the original large/negative liquid slopes.

The 78 crossing probes are not subjected to a homogeneous smoothness assertion.
Coexistence endpoints/interiors have no imposed homogeneous derivative contract.
For the invalid negative-quality outputs, the browser state is not treated as a
valid homogeneous derivative reference; independent stable-liquid roots supply
the thermodynamically meaningful homogeneous derivatives separately. No enlarged
probe, perturbed input or reference-polished property replaces the accepted probe.

At the low-pressure failing point, the stable-liquid rho_h is about
−0.000267784 kg/m³ per J/kg; the coexistence bubble-side limit from the exact
lever relation is about −1.214375, roughly 4,535 times larger. That large
one-sided coexistence gradient is physical. Applying it below hf with negative
quality is the invalid extrapolation. `phase-boundary-sensitivity.json` preserves
this distinction quantitatively.

The separate `boundary-derivatives-native-8.0.0.json` and matching 7.2 file
reclassify physical input branches using independent saturation values and
converged homogeneous DT roots, while retaining the actual erroneous backend
phase/Q. They reuse every original signed browser probe unchanged. At the
low-pressure h=hf−.001 J/kg point, the forward pressure probe stays physically
liquid and gives finite/analytic rho_P approximately **−182,709**. The forward h
probe also stays physically liquid and gives approximately **4,534.91**; the
reverse h ratio is about **−4,583.12**. These are numerical errors on a single
physical branch, not a demand for a smooth liquid/two-phase transition. The
reverse pressure probe crosses the physical phase boundary and is excluded.

On the vapor side at 8 bar and h=hg+.001 J/kg, the backend similarly reports
Q>1. The forward enthalpy probe remains physically vapor and has a ratio about
**1.02523**; the reverse pressure ratio is about **1.00717**. The other two probes
cross physically and carry no homogeneous ratio requirement. This closer
vapor quality-band error is distinct from the saved .001 K-superheated PT-cache
residual. The original ratio subset alone would miss these failures. Endpoints
within the native reference resolution are explicitly excluded from two-sided
homogeneous requirements. The retained v1 derived file used relative density
under the normalized-mass label; the current derivation explicitly applies
V*delta_rho/max(.01,M), keeping the accepted mass scale for low vapor inventories.

## Scientific verification, conservation and execution

The final ledger and independent audit below distinguish operating completion,
assertion completion, partial cases, adapter blocks and unexecuted paths. The
accepted suite is executed as unchanged assertion blocks through dependency
injection; a failed block remains failed while subsequent independent contracts
can run. Scope/marker statements are not counted as standalone scientific tests.

Final selected-core result: **18/18 assertion groups pass per browser**.
The five operating groups each run nominal, tight and reference tolerances plus
the accepted cap refinement: 40 complete operating integrations across both
engines. The remaining groups cover order, reference invariance, sealed/zero
exchange, controls, forced stops and exact rollback. Separate Node controls and
rules pass; selected PT-enabled domain results are detailed below. The other
three full Jacobian/controller selections and distinct ancestor/fresh-reference
paths are explicitly NOT RUN in the ledger. This is not full A2 qualification.

[SCIENTIFIC_RESULTS.md](SCIENTIFIC_RESULTS.md) reports all ten independently
audited operating outputs. Maximum global mass residual is about 1.74e-11 kg;
maximum combined energy residual is about 5.44e-9 kJ. All 80 auditable
contract-history conservation records pass. There are 96 captured model histories,
64,312 trials, 892 rejected trials and 892 exact rollback checks with no failures.
The maximum accepted normalized temporal error is .990842116231, below the
unchanged limit 1. Frozen direct-EOS and fresh same-table differences are listed
separately. Terminal wet quality, superheat, phase-event and nonlinear work
records remain visible. Missing early cold trial histories remain unexecuted
verification scope.

[LIQUID_COUNTEREXAMPLE.md](LIQUID_COUNTEREXAMPLE.md) gives the exact physical
same-phase derivative failure and proposed next diagnostic.
[PERFORMANCE_RESULTS.md](PERFORMANCE_RESULTS.md) reports the serial matched
30/44 cost, memory and offline measurements separately from scientific campaign
elapsed times. Neither desktop engine establishes physical Safari performance.

Matched 44/30 short coupled cost ratios are .972–.990 in Chromium and
1.081–1.472 in WebKit. Every measured repetition reaches .2 s and repeats its
work counts exactly. Median candidate initialization is 2.845 s in Chromium and
3.786 s in WebKit. Peak observed WASM linear memory remains 53.75 MiB in both;
page-only CDP heap and unavailable worker/total-browser memory are distinguished
in the performance report. These three-repeat desktop observations do not
establish universal runtime, long-duration memory stability or optimal precision.

Chromium completes all four backend workers under offline-context emulation and
with the origin disabled. WebKit completes all four with the origin disabled,
but **fails all four fresh navigations under offline-context emulation** with
an internal error. Both raw outcomes are preserved; the cache replay does not
clear the emulation/device compatibility gate. There is no remote deployment.

An additional independent native terminal audit covers all 30 nominal/tight/
reference terminal states without errors: qualities match exactly in this
sample and maximum superheat difference is 2.28e-13 K. It introduces no new
acceptance tolerance or property correction.

Browser assertions use a pinned userland strict-assert implementation; Node 22
runs use native Node assertions. The assertion shim's initial missing process
polyfill caused a harness error; those attempts are retained under `harness-v1`
and excluded from scientific pass/fail totals. A redundant interrupted Node full
suite remains incomplete. Neither artifact is counted as a successful B2 test.

Independent Python reconstructs each section's mass and refrigerant energy from
signed face/heat ledgers and derives tube/fin/air capacities from physical
geometry. It rebuilds node exchanges, total fluid energy, thermal energy and
combined conservation without importing JS balance code. It also evaluates native
DT properties at recorded M/V and T, reports terminal quality/superheat, and
compares the same-EOS refinements. Frozen direct-EOS comparisons retain their
original refined-run protocol and budgets. Fresh accepted table-backed results
are a separate cross-backend comparison: they include different property and
initial-inventory representations and are not mislabeled temporal truncation
error or forced into the same-EOS temporal budget.

Detached per-trial histories, where collected, retain accepted/rejected clocks,
trial sizes, nonlinear work and exact physical rollback checks. The original
rollback assertions and domain proof tests remain unchanged. The first operating
cold executions predate the additional detached observer; those missing detailed
histories are not manufactured from aggregate counters. Native controls and
later contracts provide separate trace evidence. No successful full per-Newton
history archive is claimed where the raw file lacks one.

[RUN_BUDGETS.md](RUN_BUDGETS.md) records resource limits and interruptions.
Additional longer operating research, repeated-transition endurance, hour-scale
runs and long-duration temporal refinement are **NOT RUN**, because the valid
liquid-boundary canonical/zero-exchange gate fails. The accepted suite's existing zero-exchange relaxation
and thermal domain-clock fixtures do not constitute new long operating evidence.
No intentionally wet terminal state is called a numerical failure.

## Minimal PT harness extension and domain results

The original B1 adapter lacks statePT. The unmodified accepted A2 domain harness
completes 33 cases per selected configuration, then throws that exact interface
error on three hot-refrigerant cases. Those raw blocked files are preserved.

B2 supplies `adapter-pt.mjs` separately. It maps the existing unambiguous PT flash
into the original bar/kJ/C interface, applies the same PH support guard and
physical temperature envelope, and preserves every original B1 PH/DU method.
It does not reflash PH, correct density/enthalpy, impose a phase, clamp a result,
change an EOS source expression, or broaden support. Phase-imposed PT is explicitly
unsupported by this minimum interface; no accepted hot-boundary fixture asks for
it. The original hot fixture still requests exactly 3.5 bar and 450 K.

With that mapping, all **36/36** accepted A2 domain/classification cases pass for
FD/failure-aware and exact-thermal/failure-aware selections in Node 22. The same
unchanged accepted domain assertion body also passes **36/36 in each selection
and browser**, 144 browser cases in total. The original A2 configuration selection
is supplied by the isolated factory, including injected-failure factories. All
assertions, physical inputs and classification/rollback requirements remain
unchanged. The full field-level results and counts identify this PT extension
explicitly; they do not turn the earlier blocked B1-interface run into a pass.

These cases cover exact 200/400 K boundaries in both directions/zero direction,
three retry floors, prior accepted work and boundary updates, unsupported-probe
and false-proof solver classifications, and hot-refrigerant outward tube stops.
They establish those tested contracts with the minimum interface. They do not
repair or excuse the demonstrated valid-liquid PH/DU/zero-exchange failure.

## Remaining gates and recommendation

Stop for engineering review. Preserve this B2 restore point and the original B1
candidate. Recommend a separately authorized B2 remediation/requalification scope:

1. Review and instrument the exact PT cached-density path and the phase-quality
   tolerance path, with no fluid/EOS coefficient change. Any new source patch
   requires explicit authorization. 44 bits is not established as globally optimal.
2. Restore exact valid-state PH/DT/DU compatibility at every saved vapor and
   near-boundary fixture under the existing property, canonical and nonlinear
   contracts. Do not clamp quality/inventory, move the input, expand support,
   smooth properties or loosen a tolerance.
3. Review the concrete isolated PT mapping and its completed domain results.
   Keep phase-imposed/ambiguous PT unsupported unless an equivalent interface is
   separately established; retain the original blocked files and unchanged inputs.
4. Complete every accepted A2 suite/configuration, frozen/fresh reference path,
   temporal/order/event/control/domain/failure/rollback and independent conservation
   gate in both browser engines. All existing scientific budgets remain binding.
5. Only after complete short gates pass, test moderate supported operating
   durations with disturbances/refinements, then consider longer operation within
   explicit CPU/memory budgets. Record failure and preserve partial trajectories.
6. Establish actual iPad Safari runtime, total memory, offline operation and worker
   responsiveness on the physical device. Desktop WebKit is not device evidence.
   Hosting or deployment requires separate approval; none is done here.

The immediate next scientific experiment is the phase-decision trace and paired
native DU inventory comparison specified in LIQUID_COUNTEREXAMPLE.md. Its purpose
is to separate erroneous PH classification from recovery of inventories already
made inconsistent by PH. Review that evidence before deciding whether any backend
source change is warranted. The vapor cache path needs its own trace; changing a
single bracket precision cannot be assumed to repair either path.

Explicit acceptance gates for any later candidate remain: exact saved inputs and
original signed probes; valid thermodynamic branch classification with genuine
crossings excluded from homogeneous smoothness requirements; independent DT
residuals under the existing property limits; canonical recovery under 1e-6 bar,
1e-4 kJ/kg and 1e-4 K; original Newton/temporal/conservation budgets; complete
accepted configuration/reference, event/domain/failure/control and exact rollback
suites in both engines. Every unexecuted required path must complete before an
A2 qualification claim. Moderate-duration stability/refinement and physical iPad
qualification follow only after the short scientific gates pass. No new global
derivative percentage threshold or relaxed nonlinear scale is introduced here.

This result does not authorize another milestone, a production migration, Live
Plant integration, merge, UI change, hosting change or deployment.
