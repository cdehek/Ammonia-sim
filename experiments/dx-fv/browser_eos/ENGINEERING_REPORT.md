# Browser EOS feasibility — experimental, no migration qualification

**An established ammonia EOS can run locally in the tested Chromium and desktop
WebKit browsers, without a thermodynamic server.** Official CoolProp 8.0.0 offers
the required reusable state interface, matches pinned Python references within
the unchanged static value limits, handles the saved liquid inventories, runs
in a worker, and reloads from an offline cache. Its startup and memory costs are
material but bounded in these desktop measurements.

**Migration is not cleared.** A reproducible low-pressure PH flash precision
problem affects finite differences at the accepted solver's unchanged step.
Physical iPad Safari performance and compatibility were not tested. Long-duration
coupled performance is uncertain and can be dominated by existing nonlinear
failures. No backend was adopted and no coupled model was modified or advanced.

Preferred architecture for a future decision: **one persistent CoolProp 8.0.0
HEOS::Ammonia state in a Web Worker, with bounded exact memoization of complete
state results and saturation results**. Before any migration, request separate
approval for flash-precision/unchanged-solver compatibility and actual iPad
validation. Do not relax scientific tolerances or enlarge solver probes to
conceal the finding. [Mechanic's Report](MECHANICS_REPORT.md) gives the plain
language explanation; [README](README.md) gives reproduction and evidence paths.

## Scope, checkpoint and preservation

Repository `cdehek/Ammonia-sim`; branch
`research/browser-eos-feasibility-20261012`; exact parent
`458a3b3c07dbf2171248e4cf237ed99c582a65b2`; accepted A2 ancestor
`be9eb35a4ddf5098e685182f8104685127c6a6ee`.

The interrupted checkpoint was inspected before resuming. All **250 pre-existing
tracked files** were byte-identical. Official binaries/source snapshots, initial
prototype and both **612-request Python reference runs** already existed. Their
inputs, results and asset hashes were retained unchanged; no completed Python
reference experiment was regenerated. Browser accuracy/performance evidence,
offline/worker tests, licensing details and reports remained unfinished.
`evidence/resume-checkpoint.json` records the inventory and hashes. The initial
loader is retained as `evidence/checkpoint-eos.mjs`; only new research prototype
files were developed further.

All changes are new files below `experiments/dx-fv/browser_eos/`. Production
`engine.js`, `properties.json`, Live Plant, training UI, root tools/tests,
workflows, main, PR #3, accepted simulator, protected restores and old evidence
are unchanged. Static comparisons read the original engine/table as a baseline.
No EOS candidate was inserted into the evaporator. No trajectory, full Stage 2B
matrix or multi-hour simulation was run. All earlier unqualified results remain
unqualified. This report describes architecture feasibility, not a new milestone.

## Official versions, provenance and free use

The [official JavaScript wrapper documentation](https://coolprop.org/coolprop/wrappers/Javascript/index.html)
provides JavaScript plus WASM downloads and an Emscripten source build recipe.
The documentation observed on 2026-10-12 points to 8.0.0. Both 7.2.0 and 8.0.0
were downloaded from their official SourceForge release directories and retained
**unmodified** locally; no floating CDN or nightly is loaded by the prototype.

| Build | Runtime/source git revision | Matching Python package |
| --- | --- | --- |
| 7.2.0 | `98b3523d5daa98454618d381d2ae53f7471d216b` | CoolProp 7.2.0 |
| 8.0.0 | `ae81610e7d23efc57f9d051c8e70a4d66e87537f` | CoolProp 8.0.0 |

Runtime version/git values agree with Python. SHA-256, release URLs, sizes and
compressed sizes are in `evidence/assets.json`. Exact upstream binding source,
CMake files, dependency pins and build workflows are retained in `upstream/`.
The workflow names Emscripten 4.0.12, with ES-module/modularized output,
exception catching, assertions and growing memory enabled. The binaries omit
producer metadata and were not independently rebuilt here; a source recipe is
not a compiler attestation. Reproduction uses the hashed official assets.

CoolProp is **MIT licensed**, allowing free commercial use and redistribution
with its notices retained. The prototype uses HEOS, which needs no REFPROP
purchase, license key, remote API or account. The implementation includes the
[Gao, Wu, Bell and Lemmon (2020) ammonia formulation](https://coolprop.org/fluid_properties/fluids/Ammonia.html).
Agreement against Python CoolProp is numerical implementation verification of
that formulation, **not experimental validation of real ammonia properties**.

Dependency notices are retained in `vendor/notices/`, including Eigen MPL 2.0,
Boost, fmt, JSON libraries, miniz, IF97/interface headers, Emscripten and toolchain
notices. `vendor/THIRD_PARTY.md` records pins, source availability and the exact
limits of build provenance. These obligations are compatible with a free
browser application; preserve notices and covered source availability when
redistributing. No proprietary REFPROP library is bundled or used.

## API capabilities and gaps

| Required operation | Official 7.2.0 | Official 8.0.0 |
| --- | --- | --- |
| High-level `PropsSI`, HEOS::Ammonia | Works | Works |
| Reusable AbstractState | Very limited binding | Required state outputs available |
| PH input | Scalar string API | `HmassP_INPUTS` + one state update |
| Density/internal-energy input | Scalar string API | `DmassUmass_INPUTS` + one state update |
| P/Q saturation and quality | Scalar string API | `PQ_INPUTS`, Q and phase endpoint outputs |
| T, h, s, rho, u, cp, cv | Scalar calls; most state accessors missing | Direct state accessors |
| Physical derivatives | Scalar derivative strings | `first_partial_deriv` and related accessors |
| Full saturation row | Several scalar calls | One PQ update plus liquid/vapor keyed outputs |
| Phase imposition | High-level input suffix | High-level suffix; state method not exported |
| Reference-state setter | Not exported | Not exported |

The 7.2 binding exports only `PT_INPUTS` and a handful of state methods; using
numeric enum values cannot manufacture missing output methods. The 8.0 binding
provides the needed PH/DU/PQ enums and outputs. It does not expose every C++ API:
phase imposition and reference-state setters are unavailable through this
reusable state binding. `T|liquid` via the high-level API was tested for known
stable states just below saturation. No phase is forced across unknown
canonical states. Default mass-based reference conventions remain unchanged.

All prototype inputs/outputs are **SI**: Pa, K, J/kg, J/(kg K), kg/m³. The table
comparison converts absolute bar/kJ/kg/Celsius explicitly. Canonical recovery
uses `rho=M/V` and `u=U/M`. Extra getters use the same state update, keeping the
quantities tied to one EOS state rather than independent interpolators.

The test envelope is 0.3–35 bar and the saved liquid/vapor offsets; it does not
establish application behavior near the triple/critical points, at the EOS's
full high-pressure limits, with mixtures, or with oil/water contamination.
CoolProp's published ammonia limits include 725 K and 1 GPa, with a triple
point near 195.495 K and critical temperature near 405.56 K. Those source limits
are not an expansion of the simulator's approved domain. Transport accessors
exist but were not benchmarked or qualified for new physical closures here.

Q is a quality only in `[0,1]`. Both versions can return out-of-range sentinels,
including **10000**, for homogeneous states. Some endpoint DU sentinels changed
between versions. An eventual adapter must map those to “quality undefined” and
classify phase through valid thermodynamic information; it must not display them
as physical quality or infer wetness from `Q<1` without checking its range.

The prototype catches native errors, restores the exported shadow-stack
position and releases native exception storage. Those raw ABI functions were
verified in the pinned binaries. Explicit `.delete()` releases state objects;
worker termination releases the module as a whole. This ABI-dependent handling
is research code, not a general future-version compatibility promise. The
[Emscripten exception guidance](https://emscripten.org/docs/porting/exceptions.html)
explains why cleanup matters when continuing after failed flashes.

## Static numerical comparison and the historical states

The unchanged input set has 187 physical source states over 0.3–35 bar:
subcooled liquid, superheated vapor, saturation endpoints and qualities near
0/1 and in the interior. It generates PH, DU, PT or PQ requests, plus saved
inventories, bubble/dew approaches, explicit stable-liquid near-saturation calls
and invalid-input probes: **612 requests**. No EOS values are fitted into a new
interpolator. Both matching Python packages evaluated the same saved SI inputs
in separate processes with default HEOS reference states. The Python results
include checks through an independent high-level entry path.

Both browsers completed both versions. Failure behavior agrees with the matching
Python version: 598 successes/14 errors for 7.2.0, 600 successes/12 errors for
8.0.0. One successful raw “below triple temperature” probe is physically
unsupported and is excluded from valid-state gates, explicitly retained as a
domain-guard warning. Near-saturation ambiguous PT errors are expected: use
PH/PQ or a justified stable phase, not silent extrapolation or phase guessing.

Maximum matching-Python differences, the same in these two desktop engines:

| Quantity | 7.2.0 WASM vs Python 7.2.0 | 8.0.0 WASM vs Python 8.0.0 |
| --- | ---: | ---: |
| Pressure | 0.009292 Pa | 0.000540 Pa |
| Temperature | <7e-13 K | 1.086e-7 K |
| Enthalpy | 1.193e-7 kJ/kg | 4.753e-7 kJ/kg |
| Density | 2.488e-9 kg/m³ | 1.272e-7 kg/m³ |
| Internal energy | 2.534e-10 kJ/kg | 4.752e-7 kJ/kg |

The unchanged static limits, **p error <10 Pa, T error <0.01 K, h error
<0.05 kJ/kg**, pass on the comparable valid-value subset. This says nothing
about trajectory/event gates or the strict nonlinear solver residuals.

Separate Python 7.2→8.0 differences on common successful valid states are at
most 0.009284 Pa, 2.855e-7 K, 1.413e-6 kJ/kg in h and 4.789e-7 kg/m³ in rho.
The two 7.2 DU failures at high-pressure saturated-liquid inventories succeed
in 8.0. Quality sentinels are reported separately from physical version errors.
Small differences include flash-algorithm behavior; they are not automatically
changes to the physical ammonia formulation or WASM implementation errors.

For the historical original low-pressure inventory
`rho=708.6710262223568`, `u=94.48059153610271 kJ/kg`, browser 8.0 recovers
**0.301747903618465 bar**, agreeing with matching Python. The original table's
three saved roots remain preserved in the earlier report. The direct EOS
recovery does not use that folded table surface. Its tested liquid response is
positive in compressibility, cp and cv. This demonstrates removal of the
relevant representation defect at the tested states; no exhaustive global EOS
root certificate or universal flash-success claim is made.

At the original high-pressure inventories, browser 8.0 recovers:

| Inventory from saved original table state | EOS pressure, bar | Original assigned pressure minus EOS |
| --- | ---: | ---: |
| Initial | 32.63031686678555 | about +2,283.215 Pa |
| 0.1-s endpoint | 32.77209845911512 | about +3,263.893 Pa |

The browser agrees with independent matching-version Python to the recorded
numerical precision. These are static inventories; no trajectory was replayed.
Direct PH at the originally assigned pressures represents a different inventory,
so prescribing pressure must not be confused with recovering it from fixed M/U/V.

Repeated valid/invalid updates, reversed historical requests and bubble/dew
sequences are retained. After 100 native errors, 100 succeeding valid updates
completed in each browser/build; stack positions and linear-memory size were
unchanged. This is bounded error-recovery evidence, not an unbounded leak proof.

### Original physical accounting and thermodynamic identities

For 189 PH states in each browser, the supplemental test uses the **unchanged**
accounting `M=rho*V`, `U=M*h-P*V`, then recovers via native DU. All 189 recoveries
succeed. Maximum roundtrip errors are 0.01392 Pa, 3.057e-7 K, 5.881e-7 kJ/kg in h,
4.082e-11 kg/m³ in rho and 1.034e-10 kJ/kg in returned u versus stored U/M.
There is no time integration or conservation-trajectory qualification.

The maximum 8.0 observed `h-u-P/rho` residual is **0.0003854 J/kg**. It is small
relative to the static h budget, but not merely machine roundoff. Single-phase
Maxwell residual is below 3e-15 m³/kg in the tested derivative assembly.
Saturation Gibbs and latent consistency at 3.5 bar are within about 2e-9 J/kg.
No homogeneous cp/cv/compressibility condition is applied inside two-phase
coexistence. Physical-EOS uncertainty is not supplied by this experiment.

### Scientific blocker for an unchanged-solver migration

At the exact saved low-pressure liquid PH input
`P=30298.937123458254 Pa`, `h=94523.34612321304 J/kg`, the accepted pressure probe
is **0.01 Pa**. Both browser engines using official 8.0 WASM give:

- Analytic `(d rho/d P)_h`: **6.61684e-7 kg/(m³ Pa)**.
- Finite difference at the unchanged step: **1.33597e-5**, about **20.19 times**
  the analytic slope.
- Base flash enthalpy residual about −1.2e-9 J/kg; perturbed residual about
  **−0.00047458 J/kg**. The pressure probe changes the numerical convergence
  residual enough to contaminate its tiny density difference.

The implied density artefact is about 1.27e-7 kg/m³. At a five-section cell volume
0.0006 m³, that corresponds to roughly 7.6e-11 kg, material against the typical
scaled `1e-11` fluid nonlinear target. This static observation does not prove
that every coupled solve fails, but it blocks an assumption of drop-in numerical
compatibility under the unchanged budgets.

Independent native Python diagnostics retained fresh/reused states, high-level
calls and both exact input layouts. Python 8.0 does **not** reproduce the 20×
slope at the exact saved input. At the historical rounded-input variant, both
WASM and native Python 8.0 have nearly equal approximate enthalpy residuals and
the slope is close to analytic. Official 7.2 WASM is close to analytic at both
layouts. This supports **build/input-sensitive flash convergence**, not physical
negative compressibility. It does not establish the internal cause. Agreement
of ordinary state values against the same EOS is insufficient to qualify tiny
solver finite differences.

A step-size sweep is retained only as a diagnostic. **No pressure probe,
enthalpy probe, Newton rule, TR-BDF2 algorithm, accounting equation or tolerance
was changed.** Exact caching does not fix this. A separately approved precision
study is needed before migration: establish reliable PH/DU residual accuracy
and unchanged-solver behavior, or reject that backend/build for this use.

## Initialization, size and memory

Environment: Linux x64, AMD EPYC 9V74 host, three visible logical CPUs, shared
cloud runtime; Node 24.19.0, Playwright 1.62.1. Tested browsers are Chromium
**151.0.7922.34** and desktop Playwright WebKit **26.5**. WebKit's Safari-like UA
is not evidence of an Apple device. Installed browser dependencies were kept
outside the repository. No iPad was attached or tested, and no emulation result
is represented as iPad timing or memory.

| Metric | Chromium | Desktop WebKit |
| --- | ---: | ---: |
| 8.0 initialization mean, three fresh contexts | 2.060 s | 2.361 s |
| Observed context-start range | 2.030–2.086 s | 2.050–2.563 s |
| First ammonia factory mean | 1.963 s | 2.142 s |
| Ready/final WASM linear memory | 56,360,960 bytes (53.75 MiB) | same |
| Final 7.2 accuracy-run linear memory | 97,910,784 bytes (93.38 MiB) | same |

Startup is dominated by first fluid factory/library initialization, not the
simple network fetch or arithmetic. The timed loader downloads an ArrayBuffer
before instrumenting the streaming compiler, so it does **not** measure overlap
of download and compilation. Fresh contexts can share browser compiler and OS
caches. Measurements are loopback, not first-ever WAN or mobile downloads.

| Assets | Uncompressed combined | Gzip equivalent at measurement |
| --- | ---: | ---: |
| Official 7.2 JS + WASM | 7,128,376 bytes | 4,479,178 bytes |
| Official 8.0 JS + WASM | 9,363,572 bytes | 4,342,400 bytes |

The preferred deployment would ship only its chosen build, not both research
versions. Gzip sizes are calculated; actual host transfer compression was not
asserted. An 8.0 payload of 4.34 MB would require about 3.5 seconds at 10 Mbit/s
or 0.7 seconds at 50 Mbit/s before latency and startup, if the host uses that
compression. Uncompressed transfer would be larger.

The measured complete browser process-tree RSS is approximately 528 MiB Chromium
and 703 MiB WebKit after the main performance workload; baseline trees are about
391/361 MiB. **Summed RSS double-counts shared pages and includes browser/code
caches and prior contexts; it is not the engine's exclusive memory.** Chromium
reports about 8.1 MiB used JS heap and 8.9 MiB backing storage in that snapshot.
The instrumented loader retains its WASM download buffer; linear-memory bytes
are a more portable hard observation than these process totals. No iPad memory
limit, OS eviction behavior, thermal throttling or battery use is established.

## Property cost and comparison with the accepted table

Identical SI request coordinates and seven state outputs are used. Three short
interleaved timing rounds per workload exclude construction and reference work.
Means in microseconds per state (table/8.0 reusable state):

| Workload | Chromium | Desktop WebKit |
| --- | ---: | ---: |
| PH liquid | 9.66 / **84.55** | 11.49 / **101.96** |
| PH vapor | 10.17 / **76.02** | 10.42 / **79.38** |
| PH two-phase | 4.49 / **5.32** | 4.26 / **5.59** |
| DU liquid | 133.70 / **26.71** | 137.13 / **21.73** |
| DU two-phase | 64.24 / **25.87** | 59.84 / **24.61** |
| DU vapor | 163.48 / **22.24** | 153.14 / **21.36** |
| PT liquid | 0.38 / **9.29** | 0.41 / **9.71** |
| Full saturation row | 0.28 / **6.26** | 0.17 / **5.49** |

The table DU-vapor workload contains rejected states near its bounded envelope;
its timing includes failed attempts and is not an all-success equivalent
benchmark. Failed-call counts remain recorded. Existing table accuracy/stability
limitations are not cured by fast timing. The other reported state workloads
retain their own failure counts, all zero in the recorded successful groups.

Calling scalar 8.0 `PropsSI` separately for the same seven outputs costs roughly
**1.1–2.3 ms/state**, much slower than one reusable update plus getters. Official
7.2 scalar fallback on its selected inputs costs **8.23/8.67 ms** for liquid PH,
**3.17/3.91 ms** for the historical liquid DU inventory, and **7.67/9.23 ms** for
a full saturation row (Chromium/WebKit). Its different selected workload is
retained explicitly; these are not matched multi-state speed ratios. String
convenience calls are unsuitable as the inner-loop default for this objective.

Three 1.5-second sustained mixed PH/DU epochs achieved roughly 25,000–29,000
states/s, with unchanged 8.0 linear-memory size. This is a few seconds of desktop
sustained execution, not a multi-hour mobile throttling test. Worker batches
kept the main thread ticking: 90 Chromium and 75 WebKit 20-ms timer callbacks
while a roughly 1.8-second workload ran. Timers are evidence of responsiveness,
not a frame-rate or complete UI integration benchmark. Batch messages avoid
one worker roundtrip for every property output.

### Five-/nine-section call patterns and exact caching

The static call graph follows the preserved finite-difference stage solver:
base residual, 2N fluid perturbations, 2N+1 thermal probes, one trial update,
unchanged stage cache for exact cell PH pairs, repeated boundary PH/saturation
calls, and final canonical recovery. It models **23/39 residual evaluations**
and **147/255 logical property calls** per five-/nine-section iteration pattern.
No linear solve, integrator, heat exchange or physical timestep is executed.

Initial near-boundary patterns are retained; separate interior patterns use
0.1 K subcooled liquid, 25 K superheat and quality 0.2, with distinct boundary
states. Ten patterns per timing round reduce coarse-timer uncertainty. Mean
milliseconds per representative iteration pattern:

| Sections / seeded phase | Chromium: table / direct / exact cached EOS | WebKit: table / direct / exact cached EOS |
| --- | ---: | ---: |
| 5 liquid | 2.11 / 6.95 / **1.73** | 4.17 / 9.77 / **2.07** |
| 5 vapor | 1.24 / 5.85 / **2.10** | 1.47 / 6.33 / **2.03** |
| 5 two-phase | 0.073 / 1.01 / **0.427** | 0.133 / 1.00 / **0.400** |
| 9 liquid | 3.84 / 7.53 / **2.74** | 4.70 / 8.20 / **2.80** |
| 9 vapor | 2.03 / 11.19 / **3.58** | 2.50 / 12.63 / **4.07** |
| 9 two-phase | 0.133 / 1.93 / **0.787** | 0.133 / 2.17 / **1.00** |

Small means have timer/JIT/scheduler uncertainty; SDs and all rounds are retained.
This is a synthetic call-pattern comparison, not a coupled runtime measurement.

The hybrid uses the **same EOS** and exact input keys, never rounded coordinates
or an approximate interpolator. Complete immutable results are cached in a
bounded map for one fixed version/fluid/reference convention. Tested exact-cache
comparisons have zero differences. Changed states still require native flashes;
there is no claimed hit rate for a real plant trajectory. No mutable C++ object
is returned as a cached state. An eventual implementation must include phase
policy and reference/configuration in key/invalidation rules and retain failures.
Quantized caches can corrupt finite differences, canonical recovery and
thermodynamic consistency; they are not justified or implemented. Caching does
not correct the flash precision issue, and it is not uniformly faster than the
current table in two-phase workloads.

## Implications for multi-hour simulation

The report does not estimate runtime from a single cheap PT call. It combines
measured iteration-pattern costs with **existing** accepted five-section
cold/warm iteration counts: 4,635/7,847 iterations in 120 simulated seconds,
38.625/65.392 iterations per simulated second. If those rates and measured cache
behavior persisted, property work alone would cost approximately:

- Five sections, cached EOS: **56–494 seconds per simulated hour** across the
  tested phase/browser/rate combinations.
- Nine sections, cached EOS: **109–957 seconds per simulated hour**, assuming
  the same iteration rates solely for a what-if comparison.
- Six simulated hours: roughly **6–49 minutes** five-section or **11–96 minutes**
  nine-section property work under those assumptions, before other solver work.

These are conditional cost examples, not bounds or promised full runtimes.
The pattern includes canonical recovery per iteration, which can overcount;
extra line searches/retries, larger plant topology, phase events and mobile
slowdown can undercut the estimates. Nine-section iteration rates are not
invented as measured data. EOS could change iteration counts; that was not tested.

The retained historical heat-reversal case is much worse: about **701 Newton
iterations per simulated second**, 921 failed Newton attempts and 298,993
nonreducing line-search evaluations over 60 seconds. Holding that pathological
rate fixed yields **5,100–10,300 seconds of cached EOS property work per simulated
hour** in the illustrative five/nine vapor patterns, before extra failed-line-
search cost. It is not a forecast, but demonstrates why an EOS and cache alone
cannot establish fast industrial multi-hour behavior. Existing strict budgets,
thermal closure and failure-aware numerics are not changed by this study.

## Deployment, offline use and device limits

The prototype uses relative ES-module URLs under a project-prefix path,
locally bundled JS/WASM and an asynchronous loader. The tested HTTP server
serves `application/wasm`; the ArrayBuffer path also works when that MIME is
wrong. A missing asset gives an explicit HTTP 404 error. A single module worker
uses ordinary, **nonshared** WASM memory; no pthreads, SharedArrayBuffer,
COOP/COEP headers or cross-origin isolation are required in these tests.

[GitHub Pages is static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages),
which fits this asset-only architecture. Project-prefix routing, worker URLs,
module MIME and a research-scoped service worker were tested locally. This
study **did not publish a site, alter Pages settings, modify a workflow, or
confirm the exact live Pages WASM MIME header**. An attempted public demo asset
URL returned 404, so it is not treated as hosting evidence. The tested MIME
fallback reduces that dependency, while correct JavaScript MIME and HTTPS
remain necessary. A future isolated deployment must verify actual asset paths,
compression, cache headers and branch/build inclusion before claiming hosting
qualification. The existing production build is not assumed to copy this folder.

After a successful online installation, all six required 8.0 research page/
module/worker/JS/WASM assets were cached. Both engines then **reloaded the page
and initialized a fresh EOS while the local server was configured to reject
requests**. Historical DU recovery succeeded. This tests restart from cache,
not only already-loaded arithmetic. Future releases must version the cache and update the complete JS/WASM asset
set together; this prototype does not certify upgrade/eviction behavior.
Cache availability can be revoked by
storage eviction or user action; indefinite offline availability is not proved.

An earlier Playwright WebKit network-emulation reload produced an internal
error; it is preserved. Direct server-unavailability testing succeeded in both
engines. `navigator.onLine` is not used as proof of offline operation.
Service-worker scope is restricted to this experiment's directory, so it cannot
control the root application. Tests clean up their isolated registrations.

Opening via `file://` is unsupported. Modern desktop browser support is observed;
physical iPad Safari support, performance, memory pressure, persistence,
background suspension and thermal behavior remain **unverified**. Linux WebKit
and its Safari-like user agent do not substitute for that device. No benchmark
suggests a real-iPad pass or minimum-iPad guarantee.

## Ranked architecture decision and next approval

1. **Persistent official 8.0 HEOS state in one worker, exact bounded caching.**
   Best demonstrated browser API/performance balance. Local/offline, free and
   removes the relevant frozen-surface defects on tested inventories. Keep it
   experimental until flash-precision/unchanged-solver and real-device gates
   are established. Worker batching belongs around a coherent calculation
   workload; per-property asynchronous crossings would add avoidable overhead.
2. **A pinned 7.2 source build with expanded low-level bindings**, if 8.0
   precision compatibility cannot be demonstrated. It preserves the historical
   reference version and has smooth tested low-pressure probes, but missing
   bindings, saturated-liquid DU failures and compiler-dependent behavior need
   independent resolution. No such binary was built or qualified here. The
   official scalar 7.2 fallback is a measured functional alternative with poor
   inner-loop cost, not a migration recommendation.
3. **Retain the accepted table while a qualified EOS adapter is investigated.**
   It is fast in its established envelope, with known additional liquid stability
   and accuracy limitations. This study does not authorize table changes or
   reinterpret earlier fixture qualification as universal accuracy.
4. **Native CoolProp tabular backends or a Python/Pyodide stack** are future
   alternatives, not measured solutions. Native TTSE/bicubic acceleration needs
   separate canonical/derivative/phase accuracy, table-build/storage and browser
   memory evidence. Pyodide adds an interpreter/dependency layer to an already
   available C++ WASM route. Neither automatically satisfies the 10 Pa gate or
   the unchanged nonlinear budgets. No new custom interpolation fitting occurs.
5. **Remote EOS service** is a fallback only. It forfeits guaranteed local/offline
   use and introduces latency, hosting cost and service availability. It is not
   preferred for this free browser application and was not implemented.

The study is complete and reproducible as **experimental research**. Desktop
architecture feasibility is demonstrated; production replacement and fast
multi-hour plant simulation are not. The concrete scientific finding makes a
separate flash-precision/solver-compatibility decision necessary. Request approval
for that focused study and actual-iPad testing before migration or a further
stage. Stop here for review; no tolerance change, integration or promotion.
