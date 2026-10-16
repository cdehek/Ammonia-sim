# Research B4B — controlled vapor PT/cache consistency repair

**FOCUSED REPAIR PASS**

The saved vapor defect is corrected in this experimental ammonia backend.
Independent EOS and original relevant numerical budgets pass; no material
regression appears in the supported focused tests. Full backend qualification
remains pending. Stop for engineering review and explicit approval.

Branch: `research/browser-eos-b4b-vapor-cache-repair-20261016`.
Starting commit: `94f77bb062b75ffebf17a1c9758d11c1adc61711`.
The final delivery commit is reported with the push receipt; `git rev-parse HEAD`
identifies the checked-out delivery. All additions are under this B4B directory.

## Checkpoints and preservation

The branch was created directly from exact B4A, with a clean checkout before new
files. All 1,102 starting tracked files retain their SHA256. The starting remote
heads are captured in `evidence/refs-before.txt`; protection audits compare every
previous head, excluding only this new delivery branch. These checkpoints remain:

| Checkpoint | Commit |
|---|---|
| Accepted five-section A2 | `be9eb35a4ddf5098e685182f8104685127c6a6ee` |
| B1 precision | `ef1562ae1680fccf3323391e9ec83788c5ae1e69` |
| B2 blocked qualification | `6a220dd6c94bff08e00e0107cfec71854166ede2` |
| B3 forensics | `4e1295be9493d8bce4ca35ee0cf61accb7465226` |
| B4A liquid repair | `94f77bb062b75ffebf17a1c9758d11c1adc61711` |
| Operator Workstation UI | `262b6092b2ed694073ad9ffd41265f44dd0b6ca0` |

B3's report, proposals and execution traces and B4A's report, algorithm, patch
and prerequisites were reviewed. The pinned source is CoolProp 8.0.0
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`. All 1,782 tracked source hashes
match the documented B4A stage before this repair. The original B1 source
archives and source-stage hashes, reconstructed B3 diagnostic30/44 sources,
all previous preserved native archives, browser artifacts/notices and both
8.0/7.2 reference-wheel binary hashes verify. All nine dependencies match B4A.
See `historical-*-hash-verification.json`, source-stage manifests and provenance.

## Mechanism, ownership and reviewed algorithm

`Householder4` evaluates a density residual and three derivatives at x, computes
dx, advances x, and can terminate using the old residual or relative step. Its
returned density need not be its final evaluated density. `SolverTPResid::call`
uses `update_DmolarT_direct`; its pressure and derivative cache therefore belong
to the evaluated coordinate. `solver_rho_Tp` returns the advanced coordinate.

The pure/pseudopure homogeneous `PT_flash` previously assigned that density
directly. `post_update` updates reduced coordinates but does not invalidate the
derivatives. Pressure remains the previous residual's EOS pressure. Enthalpy and
internal energy combine final explicit coordinates with earlier Helmholtz
derivatives. Thus different getters can describe different physical states.

The decision was recorded in [ALGORITHM.md](ALGORITHM.md) before the functional
patch. [pt-cache-consistency.patch](pt-cache-consistency.patch) replaces the bare
density assignment with a saved-temperature density solve followed by the existing
`update_DmolarT_direct(rhomolar,T)` commit. This clears state-dependent caches,
assigns final coordinates, calculates pressure from EOS and restores reduced
variables. Pressure evaluation fills residual derivatives at those coordinates;
remaining caches are filled when requested. Phase selection is preserved and
the existing `_Q=-1` assignment follows the commit.

Other mixture PT paths and `update_TP_guessrho` already use this operation.
The repair is confined to the missing pure/pseudopure PT commit, shared with
PT evaluations inside homogeneous H/S/U-pressure inversion. No generic solver,
density-selection test, residual budget, iteration count or physical equation
is changed. The critical-point shortcut, mixture PT, DU implementation and
B4A liquid classifier remain unchanged. Non-ammonia/pseudopure consequences
require broader qualification.

A generic Householder final evaluation/termination change was rejected because
it affects unrelated callers. A solver_rho_Tp-wide synchronization would require
all early/fallback returns and broaden side effects. Manually clearing selected
derivatives risks missing pressure, ideal or caloric caches. Installing requested
pressure after clearing would be an input echo. The existing complete DT commit
provides the narrowest demonstrated correction without these changes.

Functional-source SHA256:

| Item | SHA256 |
|---|---|
| B4A/B1 FlashRoutines.cpp | `9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3` |
| Candidate FlashRoutines.cpp | `f40afccde19c0799bf93b4f144d22e5affba4d0a69c0081d00501a1bffd34c3f` |
| B4B patch | `621375770c2663fb86a0e3621fd85da34c4b410dbd4b592154dee402d860fe14` |

Reversing the B4B patch restores exact B4A source. The B1 44-bit expression and
B4A patch remain byte-for-byte preserved. Solvers.cpp and the backend classifier
hashes remain identical to B4A. No EOS coefficient, reference convention or
ammonia source-data file changes.

## Exact saved vapor: independent before/after

Original binary64 P=`412869ffff10db75` (799999.9981754856 Pa),
h=`4138c7d6bea72295` (1624022.744737779 J/kg). Its equilibrium vapor endpoint is
about .001 K colder; the saved input is stable homogeneous gas, outside the
upper-quality band. Inputs and original four signed perturbations are retained.

| Native PH result | B4A control A | Candidate B |
|---|---:|---:|
| T K | 291.01436145364335 | 291.0143614933306 |
| rho kg/m³ | 6.26655090474472 | 6.266550903429728 |
| getter P Pa | 799999.9963514368 | 799999.9981754855 |
| getter h J/kg | 1624022.7447383238 | 1624022.7447377462 |
| getter u J/kg | 1496360.8123073722 | 1496360.81228019 |
| Q / phase | -1 / gas (5) | -1 / gas (5) |
| independent DT P minus requested P, Pa | 0 | -1.16415321827e-10 |
| independent DT h minus requested h, J/kg | -0.000119190430269 | -3.28291207552e-8 |
| getter minus DT P, Pa | -0.00182404881343 | 0 |
| getter minus DT h, J/kg | +0.000119735253975 | 0 |
| getter minus DT u, J/kg | +0.000119551317766 | 0 |
| normalized PH inventory energy mismatch | 7.96537734361e-11 | 2.19431447906e-14 |

Independent DT uses an unmodified native 8.0.0 reference state at actual returned
rho/T. A separately constructed homogeneous p/h Newton root converges to
T=291.0143614933414 K, rho=6.266550903429371 kg/m³ with its original
1e-5 Pa / 1e-8 J/kg reference-resolution limits and positive cp/cv/compressibility.
It is diagnostic and never substituted into the backend or model.

Isolated public PT has no enthalpy input. At the control's PH-returned T it
reproduces all three stale-cache discrepancies above. At candidate PH-returned
T all three are zero. Fixed PT at the **original captured B3 source30 T**, read
from its saved trace rather than hardcoded, reproduces this exact sequence:

```text
evaluated rho_molar = 367.96004400516597
relative residual  = -2.2800613130288793e-9 (ftol unchanged at 1e-8)
increment          = +9.463514042295842e-7
returned rho_molar = 367.9600449515174
old cache delta    = 0.02686624153075102
committed delta    = 0.026866241599847938
```

Candidate B returns the **same density at this fixed PT input**. Its additional
DT commit fills the cache at committed delta, with matching pressure/h/u. The
solver's old-residual termination remains visible. `trace-audit.json` compares
the last fill against the actual explicit final density coordinate, not against
the stale reduced-coordinate field. Both fixed PT30/PT44 repetitions prove
this; native logging-off/on and uninstrumented results compare exactly.

## Five distinct scientific requirements

1. Requested-property accuracy uses independent EOS at returned coordinates
   and an independent reference root for T, rather than matching input echoes.
2. Getter consistency compares p/h/u and derivatives with fresh DT at actual
   returned coordinates, including public PT without an h request.
3. EOS residuals measure p/h at the original requested PH, with no modified input.
4. Canonical recovery uses unchanged `V=.003/5; M=rho*V;
   U_kJ=M*(h/1000)-100*(P/1e5)*V; rhoDU=M/V; uDU=U_kJ/M*1000`.
5. Nonlinear compatibility uses the accepted mass/energy scales and perturbations,
   including `abs(M*u_EOS/1000-U_kJ)/max(1,abs(U_kJ)) <= 1e-11`.

These are independently recorded. Passing .1 Pa/.1 J/kg/1e-4 K canonical
budgets alone never excuses a local energy failure. V's actual binary64 value,
all input/output bits, separate historical/reference/current inventories and
rounding through M/V remain in the JSON. No inventory normalization is used.

Chromium/WebKit saved-vapor canonical differences are +6.0070e-8 Pa,
+9.7789e-9 J/kg, +1.5973e-11 K. Native values are separately retained.
Candidate native matrix maxima over 229 homogeneous base/probe snapshots:
requested p 1.0973e-6 Pa, requested h 6.5658e-8 J/kg, getter-vs-DT p
7.8138e-7 Pa, h 2.4593e-9 J/kg, u 1.1059e-9 J/kg; normalized inventory-energy
mismatch 5.1827e-13. Last-digit differences include mass/molar round trips.
Control has 21 homogeneous snapshots above 1e-11; candidate has zero.

## Lifecycle, phase and B4A/B1 regression

The unchanged 86 B4A inputs and 344 signed probes run natively and in Chromium
151.0.7922.34 / WPE WebKit 26.5. Both browsers' complete candidate rows compare
exactly equal. Independent native DT p/h/u agrees with browser DT throughout
this finite sample. All supported same-physical-branch probes whose two
outputs are homogeneous meet original mass/energy nonlinear scales.

The separate 47-case lifecycle matrix covers fresh/reused states, PH→PT→PH,
repeated PT/PH, DU→PT, both signed saved-vapor probes, subcooled and superheated
states, both saturation endpoints, coexistence and new explicitly labeled
±.001/±.01/+10 K diagnostic offsets at four pressures through 35 bar. Valid
two-phase states use equilibrium endpoint/lever checks, not a homogeneous
derivative imposed at mean density. Physical boiling crossings and unresolved
endpoints are excluded from two-sided homogeneous slope assertions.

Browser lifecycle derivative differences are zero for residual-alpha T/density
derivatives and p_rho/h_T/u_T at sampled homogeneous coordinates. Native
differences are at ordinary round-trip resolution (maximum p_rho absolute
1.281e-9; h_T 9.095e-13; u_T 1.819e-12). Getter-energy normalized mismatch is
at most 1.670e-16 native and 1.635e-15 browser. No new derivative tolerance is
introduced: original signed-probe inventory requirements provide the gate.

Saved B4A liquid P=30298.937123458254 Pa, h=98904.56398938334 J/kg remains
stable liquid, Q=-1, phase 0. Native T=218.26293702735893 K,
rho=707.4983265879032 kg/m³. Fresh-DT requested p/h residuals are -9.516e-7 Pa
and -3.929e-10 J/kg. Canonical differences are -0.000430944296 Pa,
-5.9312e-7 J/kg and -4.6867e-11 K. The original three same-liquid signed probes
pass; reverse-P crosses to physical coexistence. No negative-quality lever
extrapolation returns. The original faulty B3 inventory remains untouched.

The original B1 P/h=30298.937123458254/94523.34612321304 precision fixture
retains the exact 44-bit source correction and passes all four original signed
probes, independent EOS, canonical and normalized numerical checks. Recomputed
pressure can change final digits because that is the purpose of the commit;
this is not a claim of bit identity for every getter after B4B.

The low-pressure liquid and a 3.5-bar endpoint are inside public PT's existing
saturation-ambiguity guard. Fresh direct PT retains the actual guard message.
The inherited research JS loader's exception cleanup instead emits a reference-
count assertion on six rejected sequence calls per browser. Identical calls
fail in control and candidate; later PH calls succeed. This loader issue is
retained, separate and uncorrected. It is not a successful PT update. The first
native lifecycle writer mislabeled a final fresh-PT rejection as a row error;
its original output is preserved, and the corrected writer/replay records the
rejection separately without changing the backend or input.

## Limited accepted A2 compatibility

All twelve injected dependency files match accepted A2 exactly. Its original
`check` function is extracted verbatim from the Git object and applied to every
recorded supported sample, including independently reconstructed thermal-node
ledgers. Original trace temporal acceptance and nonlinear norms are audited.
The solver, hydraulics, TR-BDF2, Newton limit 30, finite differences, support
guard, 1e-11 fluid and 1e-12 K thermal settings are unchanged.

Both browsers complete cold/warm/heat-reversal through .01/.05/.2 s and feed
disturbance through .01/.2/1/5/15/15.01 s. Accepted/rejected step counts are
58/5 cold, 172/22 warm, 250/9 feed and 58/1 heat reversal. Newton iterations,
residual evaluations, linear solves and rejection categories equal B4A at
every final selected fixture. Property calls are recorded separately in the
audit. No numerical pattern change requires a tolerance exception.

Maximum aggregate mass residual is 1.3471e-12 kg; section mass 1.1937e-12 kg
(original <1e-8). Maximum section energy is 6.1365e-10 kJ; combined energy
4.3108e-10 kJ (original <1e-6). All sampled original assertions pass. Wet cold
and feed outlets are legitimate coexistence, not numerical failures.

The original liquid zero-exchange and an isolated exact saved-vapor zero-exchange
.001 s trial also pass, with the full original scientific check on the trial
inventories. Trial input objects remain exactly preserved. Liquid trial norm
is 5.8803e-17, vapor norm zero; vapor converges with two residual evaluations,
zero Newton iterations/linear solves. No conservative model change occurs.

This is limited compatibility. The complete option/refinement/frozen-reference,
domain-stop/rollback and long-run matrix remains pending; exact pure-trial
preservation and unchanged source do not substitute for full qualification.

## Builds, cost and memory

Native Linux: Debian 13, GCC 14.2.0, Python 3.12.14, CMake 4.4.4, Ninja 1.13.2.
WASM: emsdk `389a68bc35dcff7ebae4614e1615099dafda00d1`, Emscripten 4.0.12
`6f625bd62ee64f4f8cd11476774741b961e4a2d5`, LLVM
`7f93487862d98bf1c168babba87daf6224d8a46f`, SDK Node 22.16.0. Release
`-O3 -DNDEBUG -std=gnu++17`; native EXTERNC shared library; upstream WASM
exception/embind/ES6/modularization/memory-growth flags. No fast-math.
Exact flags, dependencies, licenses, source stages and tool hashes are archived.

| Artifact | SHA256 |
|---|---|
| preserved B4A native control | `7a31ae229a6f62bc3f53b570759f631b29c393f743826a6de08ce9d1b87e36de` |
| rebuilt native control | `8b8630549a261ad5093d64855f71ecdba14cf139dbbe872a6de7877ddee37a4a` |
| native candidate | `b1835d39a44e3f732149fddc0abc8743ff883071efc29eb110080cac6d9e5d9e` |
| control WASM | `e74ac0694f6f85706d9b8dd71044074741bb05b4d14b7b0bc93b4aa7bb5b0078` |
| candidate WASM | `cd12d7d0c5e7271df867d3f633929c68dbd02a155aa071585153d6c0be7840d3` |

Both JS wrappers hash `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
Native diagnostics and compressed archive hashes are in `native-binaries.json`.
Build path strings and upstream-generated ordering of 126 incompressible-fluid
objects explain observed control string differences; their property content
compares equal after sorting only top-level fluid names. Rebuilt controls
match original B4A's 86 full rows/probes exactly natively and in both browsers.
Bit-identical whole binaries across different build directories are not claimed.

Three 150 ms rounds measure matched complete property snapshots. Native includes
ctypes plus seven getters; browser uses the low-level adapter. Descriptive medians:

| Runtime | vapor PT control→candidate, µs | vapor PH, µs | liquid PH, µs |
|---|---:|---:|---:|
| Native | 25.96→29.56 (1.139×) | 82.39→93.57 (1.136×) | 71.67→86.11 (1.201×) |
| Chromium | 11.63→13.19 (1.135×) | 70.92→79.00 (1.114×) | 64.99→67.60 (1.040×) |
| WebKit | 12.52→13.94 (1.114×) | 79.11→85.37 (1.079×) | 67.54→72.29 (1.070×) |

Fixed PT retains two density residual iterations and adds one DT commit/cache
fill. Saved vapor PH has seven outer residual calls in both builds and five
PT commits: total captured alpha fills 38→43; liquid 30→35. B1's sampled outer
calls change 8→7, while density residual calls stay 14. These include saturation
work and are not mislabeled Newton iterations. No necessary evaluation is skipped.
B4A's earlier near-liquid repair already cost roughly 9.8–12.1× versus its invalid
lever shortcut in prior update-only/adapter timings. B4B adds the measured cost
above. Unlike workloads are not multiplied into a false cumulative benchmark.

WASM initialization control→candidate is Chromium 2237→2179 ms, WebKit
2431→2642 ms in these snapshots. Linear memory grows from 22,544,384 to
56,360,960 bytes at factory and stays there for matched main/worker workloads.
Native RSS is 120188/120872 KiB including Python/wheel. Chromium JS heap
snapshots are about 29.4/23.1 MB; WebKit provides no matching heap metric.
Main-thread worker heartbeats continue: candidate maximum observed gaps 12.5 ms
Chromium and 45 ms WebKit. No performance-workload property or initialization
exception occurs. These short observations are not statistical speed guarantees
or physical iPad Safari measurements.

## Retained failures, scope and next gates

The upper `1<Q<=1+1e-9` classification remains invalid and uncorrected. Native
default has eleven invalid base qualities; browsers have nine. Fourteen sampled
same-physical-vapor probe comparisons touch that invalid classification band;
they remain failed/excluded from a homogeneous-cache pass, not called physical
phase crossings. All comparisons with two supported homogeneous outputs pass.

Default browser strict 35-bar recovery rejections change 9→7: tiny PH inventory
changes remove `hf-1.01e-9 latent` and `focused stable-liquid` rejections. Full-VLE
native DU exceptions change 9→7: the hf endpoint and its +1 ULP neighbor differ.
The original three full-VLE liquid DU exceptions remain. Every old failure is
retained in control evidence. At all 124 identical old/new native inventories,
control and candidate DU outputs/errors are identical; browser fixed-inventory
checks separately confirm identical raw DU and strict adapter guard behavior
at all 42 fixed browser inventories in each engine. No pressure
rounding, support expansion or DU repair occurs. Incidental successful recovery
of a different inventory does not resolve the 35-bar milestone.

Setup/verification failures remain documented: initial sandbox proxy access;
missing WebKit host libraries and isolated six-package WPE setup; an initial
overstrong whole-WASM hash expectation; the first lifecycle writer's fresh-PT
error placement; the superseded intermediate trace-summary coordinate comparison;
and inherited browser exception-cleanup assertions. Authoritative trace-audit.json
compares against final explicit density, and retains the failing control result. No failed
scientific gate was suppressed. Process deadlines and partial outputs are kept.

Next: engineering review of this exact patch and shared-source consequences;
separate approval for upper-quality classification and 35-bar inverse/support
work; full accepted A2 option/reference/temporal/domain/rollback qualification;
broader EOS/critical/triple/pseudopure/mixture review where applicable; longer
browser workloads and physical iPad testing. Independent verification here uses
the same ammonia EOS through separate DT states/roots, not a different EOS or
experimental dataset. No full backend qualification, production backend selection,
UI/Live Plant change, merge, hosting change or deployment is included.

Reproduction and machine-readable evidence are mapped in [BUILD.md](BUILD.md)
and [README.md](README.md). All historical fixtures and failures remain intact.
