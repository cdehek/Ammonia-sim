# Browser EOS flash-precision compatibility study

**Experimental and unqualified — stop for review.** Official CoolProp 8.0.0 WASM
still fails the accepted solver's demonstrated small-pressure-probe requirement.
The error mechanism is established: an input-dependent PH caloric flash residual
changes density enough to corrupt the finite difference. The reported 8.0.0 source's
relaxed stopping rule is strongly implicated. Final WASM bracket/iteration behavior
remains uninstrumented; no shipped public API tested here fixes the problem.

The next recommended decision is a separately authorized, traceable backend-build
study with precision-controlled flashes and efficient reusable state bindings,
together with physical iPad measurements. No backend build, migration, tolerance
change, production change, publication or coupled qualification is authorized by
this result. The physical-device testing package is ready; no iPad was available.

## 1. Verified checkpoint and scope

Repository `cdehek/Ammonia-sim`, origin verified from Git. Starting HEAD was exactly
`f17623f61592bd897200206692ec002088f0a605` on
`research/browser-eos-feasibility-20261012`, with a clean working tree. The accepted
A2 restore `be9eb35a4ddf5098e685182f8104685127c6a6ee` is an ancestor. New work is
isolated on `research/browser-eos-flash-precision-20261013`.

The prior browser study was complete: pinned official assets, Python references,
Chromium/WebKit accuracy and performance tests, worker/deployment/offline evidence,
historical inventory comparisons, precision blocker and reports. Its evidence was
read rather than rerun. This study adds the focused source/API diagnosis, identical
input matrix, canonical synthetic closure and physical-iPad preparation that were
unfinished. [checkpoint.json](evidence/checkpoint.json) records SHA-256 for all
**341 original tracked files**. The final audit verifies every one unchanged.

All previously unqualified frozen-data, Gibbs, PCHIP and Stage 2B candidates remain
unqualified. Nothing changes `engine.js`, frozen properties, Live Plant, root tools,
UI, workflows, main, PR #3, physical equations, Newton/TR-BDF2 or protected restore
branches. Synthetic tests import only the unchanged generic Newton and linear-solve
functions; they never import or advance the coupled model or time integrator.

## 2. Backend provenance and API

Both official binaries and the previous loader are reused without alteration.

| Backend | Reported source commit | WASM bytes | Matching native reference |
|---|---|---:|---|
| 8.0.0 | `ae81610e7d23efc57f9d051c8e70a4d66e87537f` | 9,196,512 | Python CoolProp 8.0.0, same reported commit |
| 7.2.0 | `98b3523d5daa98454618d381d2ae53f7471d216b` | 6,967,191 | Python CoolProp 7.2.0, same reported commit |

WASM SHA-256: 8.0 `28a83d839ab69c7e6ea480298955ce223b6507dc6ffb83349dd31f1540867307`;
7.2 `cb77d0381fbe639bffb65a3e8fa44ff8e2a110f21c18125c89a9b336135bd194`.
JS hashes and licensing are retained in the previous vendor manifest and the new
package manifest. Core CoolProp is MIT licensed; dependency notices accompany the
package, including Boost and Eigen notices. These permit a free local research
application subject to their notice requirements; this study makes no legal warranty.

Backend is `HEOS::Ammonia`, default HEOS mass-based reference, SI units. There is
no reference reset, fit, input rounding, property cache or fallback property value.
Python and browser calculations use their matching versions before any historical
cross-version comparison. Agreement validates implementation consistency against
that formulation, not ammonia's experimentally measured real-world accuracy.

Official 8.0 exposes reusable `AbstractState`, PH/DU/PT/PQ/DT and molar input pairs,
property getters and analytic partial derivatives. Its shipped bindings do **not**
expose `specify_phase`, `phase`, configuration setters, flash tolerance setters,
`update_with_guesses`, debug-level control or final-bracket inspection. The public
high-level `P|liquid` input is available and was tested. Official 7.2's delivered
low-level interface lacks the PH/DU/property surface needed for these snapshots;
browser 7.2 comparison therefore uses high-level string calls, which repeatedly
construct/flash states. Unsupported low-level tests are identified, not emulated.

Source snapshots and licenses are in [upstream](upstream/PROVENANCE.json). The
previous official build-workflow evidence pins Emscripten 4.0.12, but the binaries
do not supply sufficient producer metadata to independently prove every compiled
flag. We did not rebuild them or alter private WASM internals.

## 3. Exact saved calculation

Inputs, preserved as binary64:

```
P = 30298.937123458254 Pa       bits 40dd96bbf9d4ab61
h = 94523.34612321304 J/kg      bits 40f713b589b87e86
dP = 0.01 Pa                  unchanged accepted forward pressure perturbation
P + dP                        bits 40dd96bc9dabb59e
dh = 0.0009452334612321304 J/kg unchanged accepted enthalpy perturbation
```

The actual rounded pressure increment is saved in each row. JSON round trip,
DataView reconstruction and full-precision JS literals retain the exact bits. The
solver's bar-coordinate perturbation converts to the same perturbed pressure bits
in this case. Nominal historical text inputs differ by about 1.2e-8 Pa and 1.5e-11
J/kg; they are separately labelled different inputs and never substitute for this case.

Analytic density derivative comes directly from the EOS:
`rho_P|h = rho_P|T - rho_T|P * h_P|T / cp`, also checked through
`first_partial_deriv(iDmass,iP,iHmass)`. The forward calculation remains
`[rho(P+0.01,h)-rho(P,h)]/0.01`.

| Implementation at identical saved inputs | Analytic rho_P, kg/(m³ Pa) | Forward derivative | Forward / analytic |
|---|---:|---:|---:|
| Native 8.0.0 | 6.61684134856e-7 | 6.61646026856e-7 | 0.9999424076 |
| Chromium 8.0.0 | 6.61684134856e-7 | 1.33597040985e-5 | **20.1904555282** |
| WebKit 8.0.0 | 6.61684134856e-7 | 1.33597040985e-5 | **20.1904555282** |
| Native 7.2.0 | 6.61684134856e-7 | 6.61691501591e-7 | 1.0000111333 |
| Chromium / WebKit 7.2.0 | 6.61684134856e-7 | 6.61680132907e-7 | 0.9999939519 |

Residuals below are independently evaluated at the returned **density and
temperature**, rather than trusting an input-echoing pressure/enthalpy getter:

| Implementation | Base EOS P residual, Pa | Perturbed EOS P residual, Pa | Base EOS h residual, J/kg | Perturbed EOS h residual, J/kg |
|---|---:|---:|---:|---:|
| Native 8.0 | +4.17e-8 | +7.71e-8 | −4.51e-10 | +7.13e-10 |
| Browser 8.0, both | +3.34e-8 | −5.27e-7 | −1.16e-9 | **−4.74579065e-4** |
| Native 7.2 | +2.17e-7 | +1.19e-7 | +1.00e-9 | +9.17e-10 |
| Browser 7.2, both | +7.51e-8 | −6.91e-7 | +1.16e-10 | −2.31e-9 |

Browser 8.0 density goes from `708.6710614955963` to `708.6710616291933` kg/m³.
Native 8.0 perturbed density is `708.6710615022126` kg/m³. Browser/native perturbed
temperature differs by approximately −1.08369e-7 K. Actual state pressure getters
also have sub-micro-Pa cache/evaluation differences, recorded separately in raw
snapshots. They do not explain the density artefact.

High-level `PropsSI('Hmass','P',P,'Hmass',h,...)` returns the input h. Its apparent
zero residual is not flash convergence evidence. Combining that h with the returned
u/rho gives a perturbed `h-u-P/rho` defect of about **+0.000474579 J/kg**. The coherent
low-level snapshot at its actual returned state satisfies the work identity to
about 2.2e-12 J/kg here, while missing the requested h by the amount above.

## 4. Mechanism, source attribution and uncertainty

For small errors at a liquid PH state,

```
delta rho ≈ rho_h|P * delta h + rho_P|h * delta P
rho_h|P = -0.00026756503094 kg/m³ per J/kg
```

The change in caloric residual predicts a density artefact of
**1.269800799e-7 kg/m³**. The observed excess over the physical pressure increment
is **1.269801996e-7 kg/m³**: attribution differs by only 9.43e-7 relatively.
The physical density increment is only **6.61684135e-9 kg/m³**. This explains the
20× forward slope without negative physical compressibility or a wrong EOS branch.

Density ULP is 1.13687e-13 kg/m³. A conservative two-ULP representational scale
divided by 0.01 is 2.27374e-11 kg/(m³ Pa), roughly 560,000 times smaller than the
excess slope. Decimal arithmetic at 60 digits on the exact binary64 outputs agrees
with the finite-difference numerator. Subtraction of these nearby positive binary64
values is exact under Sterbenz's lemma. Evaluation error before subtraction remains;
this is not a claim that EOS outputs are correctly rounded. Enlarging a probe is
not a fix: other sweep sizes hit different residual branches.

The reported official source contains a direct relevant change:

- 7.2 `HSU_P_flash_singlephase_Brent` uses TOMS748 `eps_tolerance<double>(44)`.
- 8.0 uses `eps_tolerance<double>(30)`, then evaluates the final bracket midpoint.
- The pinned Boost header tests `abs(a-b) <= eps * min(abs(a),abs(b))`, with
  `eps = max(2^(1-bits),4*double_epsilon)`.

This relaxes the bracket by **16,384×**. At 217.263 K, the 30-bit rule permits a
bracket width of about 4.04684e-7 K; half that width corresponds to about
**0.00088610 J/kg** through cp. The measured 0.00047458 J/kg residual fits this
envelope. The 8.0 source comment incorrectly equates `2^(1-30)` to 9.31e-10; the
actual expression is **1.862645149230957e-9**, which this analysis uses.

**Established:** returned flash states carry the caloric residual; it predicts the
density artefact; both browser engines agree; fresh states, ordering and transport
preserve it; matching native 8.0 has related failures; 7.2 behaves differently.
**Strongly supported:** loose 8.0 PH stopping permits input/build-dependent bracket
termination. **Unresolved:** exact last bracket and branch in the shipped binary,
compiler/libm effects on the iterates, and whether a tighter official build eliminates
every affected state without unacceptable cost. No internal iteration trace is
exported, so source inspection is not represented as a captured WASM trace.

At 222 identical returned D/T points, native 8.0 versus WASM 8.0 direct EOS evaluation
differs by at most **2.51e-8 Pa** and **2.91e-11 J/kg**. This strongly separates the
PH numerical inversion defect from formulation disagreement. These are observed
cross-build evaluation differences, not rigorous absolute error bounds or real-world
EOS uncertainty. Independent static target roots record every residual-polish step
and declare reference evaluation limits of 1e-5 Pa and 1e-8 J/kg. Those limits govern
the research reference calculation only; no solver tolerance is changed.

## 5. Lifecycle, APIs, configurations and nearby inputs

The 8.0 matrix tests fresh/reused states, reversed PH order, PH following PT/PQ/DU,
mass and molar enthalpy inputs, high-level PH and phase-imposed liquid PH. All nine
produce the identical saved forward discrepancy in both browsers. Thirty repeated
saved flashes are deterministic. Input transport retains exact bits. An input can
move between accurate and biased flash outcomes without changing physical phase.

There are **63 input cases**: exact saved, nominal text, four one-ULP variants, and
57 previously saved supported liquid states including the saved high-pressure
initial/endpoint PH states. Each source liquid state uses the accepted pressure and
enthalpy steps. Saturation approaches reach 0.001 K subcooling. No two-phase analytic
single-phase derivative is evaluated in this matrix.

For descriptive reporting only, counting derivative ratios more than 1% from unity:

| Implementation | Liquid source states | Pressure probes | Enthalpy probes |
|---|---:|---:|---:|
| Browser 8.0, each engine | 57 | 8 | 4 |
| Native 8.0 | 57 | 9 | 5 |
| Browser 7.2, each engine | 57 | 0 | 0 |
| Native 7.2 | 57 | 0 | 0 |

This 1% count is **not** a new acceptance tolerance. Native 8.0 even produces a
negative numerical pressure slope at the saved 16 bar / 15 K subcooled state
(ratio −0.11237), despite positive analytic compressibility. Source-state browser
8.0 maximum caloric residual is 0.001412 J/kg. All tested source liquid cp, cv,
kappa and density remain positive (minimum cp 4327.53 J/kg/K, cv 2746.36 J/kg/K,
kappa 5.21077e-10 Pa^-1). These samples do not certify an entire region.

At the saved high-pressure initial/endpoint PH states, browser 8.0 pressure ratios
are 0.99996461 and 0.99978297, and enthalpy ratios 1.00000820 and 1.00000009. They
do not reproduce the low-pressure catastrophic slope; the diagnosis remains broader
than one pressure row. Historical original-inventory DU comparisons remain the
unchanged [previous study evidence](../browser_eos/ENGINEERING_REPORT.md): the
original low inventory recovers about 30174.79036 Pa, and high inventories differ
from their original table-assigned pressures by about 2283 and 3263 Pa. A PH call
at an assigned pressure does not represent recovery of the same M/U/V inventory.

Diagnostic sweeps use 0.0001–10 Pa plus a negative 0.01 Pa pressure probe, and both
enthalpy signs. Browser 8.0 saved ratios include 64.96788 at 0.003 Pa, 20.19046 at
0.01, near unity at 0.03, and 1.06417 at 3 Pa; the negative 0.01 probe is −18.19011.
Native 8.0's saved forward enthalpy ratio is **0.49793**, while browser 8.0's reverse
enthalpy ratio is **1.50207**. Shrinking, reversing or enlarging probes can change
which flash residual occurs and cannot be silently used to bypass the blocker.

Native source environment toggle `PXFLASH_DIRECT_EOS=0` reproduces the same primary
outputs as default, excluding that warm-path optimization as a sufficient explanation
or fix here. Native `ENABLE_SUPERANCILLARIES=false` changes failing probe locations
but still fails the negative-pressure and reverse-enthalpy probes. It is not a
general cure, and the shipped WASM bindings expose neither configuration route.
No altered build, private environment mutation or undocumented enum hack was tried.

## 6. Accepted numerical contract and canonical closure

Read-only solver inspection verifies pressure epsilon
`1e-7*max(1,abs(p_bar))` bar, enthalpy epsilon
`1e-8*max(1,abs(h_kJkg))` kJ/kg, both signs with up to 12 shrink levels, nonlinear
norm **1e-11**, at most **30 Newton iterations**, unchanged branch checks and line
search. Canonical equations remain `M=rho*V` and `U=M*h-P*V` in SI.

For `V=0.003/N`, the pressure-probe density artefact corresponds to mass error
**7.62e-11 kg (N=5)** or **4.23e-11 kg (N=9)**. With the actual fluid scales,
the normalized mass and input-enthalpy accounting energy contaminations are both
about **1.79e-10**, roughly **18×** the nonlinear tolerance. Comparing a local
probe's artefact with a residual tolerance indicates risk, not a theorem that every
coupled solve must fail.

The coherent analytic local inventory Jacobian has nonzero determinant. Its 2-norm
condition number after fluid residual scaling is about **250.46** in bar/kJ/kg
coordinates; applying `max(1,coordinate)` column scaling gives about **23,236**.
That explains sensitivity and proves only local regularity at this liquid state.
It proves neither global canonical uniqueness nor the full coupled Jacobian's
conditioning. No table-based nested inversion assumptions are silently used.

The synthetic workload has 21/37 variables for five/nine sections, static inventory
blocks and identity thermal rows. It uses the **unchanged generic coupled Newton
routine**, analytic physical target inventories from native 8.0 DT roots, and the
accepted pressure/enthalpy probes, residual scales, iteration and line-search limits.
It contains no transport, TR-BDF2 stage, evaporator or trajectory. Four low-pressure
targets cover saved base, P-plus, h-plus and nominal text.

Two explicitly identified interface semantics are tested: preserving the requested
h in accounting (as an input-echoing PH interface does), and using the low-level
flash's actually returned h. Both retain `U=M*h-P*V`; neither is proposed for adoption.

| Backend, each browser | Closures | Converged | Failures |
|---|---:|---:|---|
| Official 8.0 | 16 | 14 | N=5 saved base, input-h; N=9 saved h-plus, input-h |
| Official 7.2 | 16 | 16 | None in this limited static workload |

The 8.0 failures are line-search failures at norms **4.47206e-11** and
**6.71519e-10**, with reductions attempted down to `2^-28`. Other 8.0 closures need
up to **14 iterations**; 7.2 needs one here. Returned-h closures all pass, while
the formal PH derivative discrepancy persists. Passing this deliberately simple
closure cannot establish compatibility with moving states, phase changes, transport
or the accepted coupled trajectory. It is not a precision workaround.

The existing scientific limits remain unchanged: independent pressure **strictly
below 10 Pa**, temperature below **0.01 K**, enthalpy below **0.05 kJ/kg**, and all
existing conservation, event and nonlinear limits. The earlier static accuracy
results remain valid within their declared scope. A caloric residual much smaller
than 50 J/kg can still invalidate these much smaller numerical probes.

## 7. Performance and computational implications

Desktop environment: Linux x64 AMD EPYC 9V74 host, Playwright 1.62.1, Chromium
151.0.7922.34 and Linux WPE WebKit 26.5. No physical iPad measurements. Times are
observations, not guaranteed limits. Browser/compiler/OS caches can remain warm.

The new packaged worker uses three fixed liquid/saturated-vapor/two-phase states,
seven returned fields per PH/DU update, three 500 ms rounds per pathway and three
1 s mixed epochs, with no property caching. This is a hot repeated-call workload,
not the cost of arbitrary liquid flashes or a coupled trajectory.

| Desktop worker, online | EOS initialization | PH calls/s | DU calls/s | Final WASM linear memory | Max page 50 ms timer gap |
|---|---:|---:|---:|---:|---:|
| Chromium 8.0 | 2.152 s | 36,226 | 43,178 | 53.75 MiB | 52.9 ms |
| WebKit 8.0 | 2.347 s | 34,434 | 42,258 | 53.75 MiB | 56 ms |
| Chromium 7.2 | 1.817 s | 139 | 345 | 93.38 MiB | 212.6 ms |
| WebKit 7.2 | 2.104 s | 116 | 239 | 93.38 MiB | 153 ms |

No throughput failures occurred. Five intentional invalid PQ requests per version
were followed by five successful valid updates with unchanged stack pointer and
linear memory. Worker responsiveness includes startup/result handling; it is not
touch-latency or OS-memory measurement. Heap buffers, compiled code and browser
overhead are additional memory. Safari normally exposes no JS heap metric.

In the synthetic closures, 8.0 costs about 7–159 ms; 7.2 about 0.74–2.63 s in
Chromium, despite needing fewer iterations. These are deliberately uncached repeated
section evaluations, not production-stage timings. The previous representative
five/nine-section call-pattern benchmark and accepted-table comparison are retained
unchanged; its stage-local reuse and exact cached alternative have different cost
semantics. Exact reuse of identical requests cannot repair a changed-input slope.
Approximate caching was neither introduced nor evaluated as a fix.

For planning, total property cost depends on successful and rejected stages, Newton
iterations, line-search retries and evolving phase mix. Multiply **measured relevant
per-pattern cost by the number of executed patterns**, not simulated hours by one
PH timing. Even a few extra Newton iterations can erase a fast backend's nominal
advantage. For a concrete comparison, the retained interior-liquid call-pattern
medians (with the original stage-local reuse, without an added EOS property cache)
are:

| Pattern | Chromium table / state8 | WebKit table / state8 |
|---|---:|---:|
| Five sections | 1.83 / 4.69 ms | 2.80 / 7.30 ms |
| Nine sections | 3.84 / 7.45 ms | 4.50 / 8.10 ms |

An illustrative 100,000 such patterns would spend about 7.8–13.5 minutes in state8
property work on these desktops, versus about 3.1–7.5 minutes in the table path.
This is arithmetic on a declared pattern count, not a forecast of how many patterns
a multihour plant trajectory needs. Solver retries, integrator stages, physical
coupling and real device performance remain unmeasured for an EOS integration.
A tighter backend would need its own precision/performance measurements;
no supported build or iPad slowdown factor is inferred here. No multihour coupled
run or full Stage 2B qualification was launched.

## 8. Physical-iPad preparation, offline behavior and deployment

[IPAD_TEST_INSTRUCTIONS.md](IPAD_TEST_INSTRUCTIONS.md) specifies hardware/OS labels,
cold versus warm loads, foreground/manual interaction checks, three fresh-page
runs per version, exported evidence, error/memory observations and an actual
network-disconnected restart. The self-contained ZIP includes both pinned official
versions, notices, worker, SHA manifest, fixed inputs and an isolated service worker.

Final ZIP: **8,871,386 bytes**, SHA-256
`300c7588487580563856177f36768f6f0cd50f2e12cea487759530ad2999f874`.
The package's raw binary assets are larger than its compressed ZIP. Actual HTTP
download depends on server compression and network. Neither WAN startup nor iPad
RAM/performance has been measured.

V1 cached `index.html` but omitted the directory navigation URL. Fresh-page restart
failed in both desktop browsers with the origin disabled; those results are retained.
V2 explicitly caches both URLs. Desktop Chromium and WebKit then restarted a fresh
page and fresh **8.0 worker** successfully with the static origin returning 503 for
every uncached request. Both versions passed online worker testing and their assets
were verified/cached. Physical offline restart, complete Safari relaunch, cache
eviction and offline execution of 7.2 still require the device test sequence.

HTTPS/localhost is required for service workers. An iPad visiting a laptop's ordinary
LAN HTTP URL cannot perform the specified offline restart. The instructions describe
an owner-managed trusted LAN HTTPS server and, if that is unavailable, a minimal
**separate temporary HTTPS research origin requiring explicit publication approval**.
No site, GitHub Pages configuration, production origin or workflow was changed.
No certificate was installed on a device. All server tests used loopback locally.

## 9. Ranked options and next decision

1. **Keep the accepted simulator and tables as the operational baseline.** Their
   known property limitations and all unqualified research findings remain visible.
   This is a preservation decision, not scientific qualification of those surfaces.
2. **Preferred next research architecture: a traceable EOS build with adequate flash
   precision and reusable worker state APIs.** Seek separate authorization to
   instrument the PH bracket and test a tighter backend stopping rule, keeping
   solver equations/steps/tolerances fixed. Pin source/toolchain/options, label it
   distinct from official binaries, independently compare native/WASM, repeat this
   matrix and benchmark it. A 7.2-source build with fuller bindings is another
   comparison option, with its existing DU/phase-boundary limitations still exposed.
   Neither build is made or adopted here.
3. **Official 7.2 as a research/reference fallback.** It passes this limited precision
   matrix and closure test, but delivered high-level cost and previously observed
   DU saturation limitations prevent recommending it for long simulations as-is.
4. **Official 8.0 as shipped is not a migration candidate yet.** Public phase flags,
   mass/molar updates, object lifecycle and call order do not resolve the blocker.
   Returning actual enthalpy or favourable input rounding must not conceal it.
5. **Deferred EOS-backed acceleration/hybrid or remote service.** Only after a precise
   canonical backend is demonstrated. Exact stage-local reuse may save cost but
   cannot fix a noisy flash; approximate state maps introduce their own accuracy,
   derivative and thermodynamic consistency obligations. A remote API conflicts
   with the preferred local/offline/free architecture and is not the selected path.

The current study is complete within diagnostic/preparation scope. **No interface
resolution has been demonstrated; the shipped 8.0 blocker remains.** Review these
findings and choose whether to authorize the separately described backend-build
study and/or hosted physical-device test origin. Actual physical iPad collection
can use the prepared owner-managed package; it is not represented as completed here.

## 10. Reproducibility and evidence

[README.md](README.md) provides pinned environments and commands. Raw native/browser
matrices retain input bits, base/perturbed snapshots, derivative ratios and all
diagnostic sizes. [root-cause.json](evidence/root-cause.json) reproduces arithmetic,
Decimal comparison and local conditioning; [native-contract.json](evidence/native-contract.json)
retains cross-build EOS checks and independently constructed canonical targets.
Synthetic JSON records convergence/failure, iteration histories, representative
first Jacobian columns, call counts and line-search minima. It retains selected
diagnostics rather than claiming a complete coupled trace.

[ipad-smoke-v1.json](evidence/ipad-smoke-v1.json) retains the package failure;
[ipad-smoke-v2.json](evidence/ipad-smoke-v2.json) contains online and offline readiness
measurements. Package manifests preserve both artifact versions. Source provenance,
prior-file hashes and the new boundary audit complete the experiment record.
The short [Mechanic's Report](MECHANICS_REPORT.md) explains the practical conclusion.
Authored-file whitespace checks pass. The pinned Boost header retains its upstream
trailing whitespace and final blank line so its source SHA-256 remains exact.
