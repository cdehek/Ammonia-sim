# B1 — Precision-controlled browser EOS feasibility

**PROMISING: Precision improves, with additional scientific qualification required.**

A traceable CoolProp 8.0.0 WASM build with one stopping-rule expression changed
from 30 to 44 bits removes the preserved liquid PH pressure-derivative defect in
both tested desktop engines. A separately compiled unmodified source control
reproduces the official 8.0 measurements exactly. A full second compilation of
the patched source produces identical JS/WASM hashes. The accepted Newton
routine passes the original static M/U/V cases, and the original five-section
A2 equations complete the five operating fixtures at all three original tolerance
regimes in Chromium and WebKit.

This is a successful controlled feasibility experiment, **not full backend or A2
qualification**. A near-saturation vapor caloric residual remains; the complete
A2 order/domain/rollback/control suite, long runs, other accepted option
combinations and physical iPad Safari have not been qualified with this adapter.
44 bits is the first tested setting, not an established final optimum.

## Checkpoint and preservation

Repository `cdehek/Ammonia-sim`; verified clean starting checkout exactly
`7736625b3de8e901f4a305a16ffeb16aa27d3de4` on
`research/browser-eos-flash-precision-20261013`. Created the new branch
`research/browser-eos-precision-backend-20261015` directly from that commit.
All 391 starting tracked files remain byte-identical. All changes are additions
under `experiments/dx-fv/browser_eos_backend/`. The delivery commit's full SHA is
reported in the final handoff; it is also the Git commit containing this report.

Independent checkpoints are preserved: UI `262b6092b2ed694073ad9ffd41265f44dd0b6ca0`,
accepted A2 `be9eb35a4ddf5098e685182f8104685127c6a6ee`, and prior precision
`7736625b3de8e901f4a305a16ffeb16aa27d3de4`. Protected remote refs, including main,
PR #3, UI and release candidate, are recorded before/after. No merge, application
integration, production-engine change, hosting or Cloudflare change is made.

Both prior engineering reports, exact inputs, raw native/browser results,
independent residuals, source attribution and accepted A2 sources were reviewed
before building. Historical native PH derivative values remain historical.
The new browser matrices and independent native DT evaluations/reference roots
are newly executed B1 evidence, stored separately from all historical files.

## Traceable controlled build

Upstream: https://github.com/CoolProp/CoolProp, source commit
`ae81610e7d23efc57f9d051c8e70a4d66e87537f` (8.0.0).
Original flash SHA256:
`debf60f85d1d0955f08596e64d3a4958d7f369657cb3161a6b7625fa508cf3df`.
Experimental flash SHA256:
`9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3`.

[Exact patch](flash-44.patch), [build recipe](BUILD.md), [source and toolchain
manifest](evidence/build-provenance.json), compiler commands/cache and build logs
are retained. The sole source change is `eps_tolerance<double>(30)` to `(44)` in
the main bracketed `HSU_P_flash_singlephase_Brent` path. This shared H/S/U-at-P
routine affects more than the PH API. Other flash paths, including its narrow
supercritical fallback, retain upstream settings. No EOS coefficient, formulation,
fluid data, reference convention or solver-budget change is made.

Emscripten 4.0.12, emcc source `6f625bd62ee64f4f8cd11476774741b961e4a2d5`, clang
22.0.0git `7f93487862d98bf1c168babba87daf6224d8a46f`, CMake 3.31.6 and Ninja
1.11.1.4. Flags are upstream Release `-O3 -DNDEBUG -std=gnu++17`, with embind,
ES modules, modularization, assertions, exception catching and growing memory;
no fast-math. Full dependency pins/content digests, generated-header hashes,
compiler/tool hashes, exact commands and notices are supplied. Core CoolProp is
MIT; Eigen remains unmodified MPL-covered source with its source archive linked;
Boost, fmt, JSON, miniz, toolchain and other required notices accompany the assets.
See [third-party record](vendor/THIRD_PARTY.md).

The second compilation uses an empty object directory and identical source and
dependency paths. It reuses dependency downloads and generated headers. It is
not a different-platform or path-independent reproducibility claim.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| build30/coolprop.js | 167060 | `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217` |
| build30/coolprop.wasm | 9196512 | `b1baa13a092fc30e73d3ebb974a3d56013e4d20c56da89360c5d966a3eff47d5` |
| build44/coolprop.js | 167060 | `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217` |
| build44/coolprop.wasm | 9196512 | `30decd700ad8b46530a8accadd051bdf7147cc7a894904e2ce83d6babfdd63ab` |

Both builds still report the upstream version/revision; **external build identity
and hashes are mandatory**. Their JS is identical to official 8.0 JS. The local
30-bit WASM is not byte-identical to the official WASM, but all 365 precision rows
and all 612 property requests match the official results exactly in each engine.
This controls compiler/binding effects before interpreting the one-line patch.

## Exact primary experiment and independent residuals

Inputs are unchanged binary64 values:

```text
P = 30298.937123458254 Pa       40dd96bbf9d4ab61
h = 94523.34612321304 J/kg      40f713b589b87e86
dP = 0.01 Pa                   P+dP bits 40dd96bc9dabb59e
dh = 0.0009452334612321304 J/kg
rho_P numerical = [rho(P+dP,h)-rho(P,h)]/dP
```

The finite-difference denominator remains nominal 0.01; the actual rounded input
increment is recorded. Nominal-text and one-ULP variants are separate labeled
cases, never substitutions. Both desktop engines give identical property rows.
The table below shows their newly measured common result, using reused 8.0 states
and the supported high-level 7.2 interface.

| Backend | Analytic rho_P kg/(m³ Pa) | Forward rho_P | Ratio | Perturbed EOS P residual Pa | Perturbed EOS h residual J/kg |
|---|---:|---:|---:|---:|---:|
| official8 | 6.61684134856e-07 | 1.33597040985e-05 | 20.1904555282 | -5.26964868e-07 | -0.000474579065 |
| build30 | 6.61684134856e-07 | 1.33597040985e-05 | 20.1904555282 | -5.26964868e-07 | -0.000474579065 |
| build44 | 6.61684134856e-07 | 6.6165739554e-07 | 0.999959589003 | -6.65691914e-07 | -2.09547579e-09 |
| official72 | 6.61684134856e-07 | 6.61680132907e-07 | 0.999993951875 | -6.90739398e-07 | -2.31375452e-09 |

Density/enthalpy derivatives at fixed pressure, units `(kg/m³)/(J/kg)`; both original enthalpy perturbation signs are retained:

| Backend | Analytic rho_h | Forward finite difference | Forward ratio | Reverse finite difference | Reverse ratio |
|---|---:|---:|---:|---:|---:|
| official8 | -0.00026756503094 | -0.000267565225863 | 1.000000729 | -0.000401901579455 | 1.502070648 |
| build30 | -0.00026756503094 | -0.000267565225863 | 1.000000729 | -0.000401901579455 | 1.502070648 |
| build44 | -0.00026756503094 | -0.000267565225863 | 1.000000729 | -0.000267564624494 | 0.9999984809 |
| official72 | -0.00026756503094 | -0.000267565105589 | 1.000000279 | -0.000267564985316 | 0.9999998295 |

For build44, base/perturbed densities are 708.6710614955963 /
708.6710615022129 kg/m³; temperatures are 217.26293725549874 /
217.26293725343407 K. Base independently evaluated P/h residuals are
`+3.33748e-8 Pa`, `-1.16415e-9 J/kg`. Every raw snapshot is retained.

Residuals use a separate state updated with returned **density and temperature**,
not PH getters that can echo requested inputs. Matching native 8.0 and 7.2 then
independently evaluate those same returned DT coordinates. Across the focused
8.0 matrix, native versus WASM DT disagreement is at most `2.51e-8 Pa` and
`2.91e-11 J/kg`. Native reference PH roots are polished by direct DT derivatives,
with all corrections retained only in the reference trace; no correction enters
WASM or the solver. The prior diagnostic evaluation limits remain `1e-5 Pa` and
`1e-8 J/kg`, separate from solver budgets.

Build44's maximum deviation from those polished native roots in the focused
matrix is `1.924e-10 kg/m³` and `1.146e-10 K`; all reference roots meet their
evaluation limits. This compares implementations of the same EOS, not measured
ammonia accuracy. Historical native 8.0 primary PH ratio was 0.9999424076; native
7.2 was 1.0000111333. Those historical raw derivative runs were read, not rerun
under a claim of newly measured native PH derivatives.

The controlled counterfactual establishes that this expression is sufficient to
remove the preserved defect in this source/toolchain experiment. It does not
capture the shipped binary's final internal bracket or prove every flash route.

## Supported states, lifecycle and regressions

The unchanged 63-case focused matrix includes the exact point, nominal text,
four one-ULP variants and 57 historical supported liquid PH entries, including
the saved high-pressure initial/endpoint inputs. It covers 0.001 K approaches
to saturation and retains original accepted pressure/h probes. Each 8.0 build
has 365 rows per engine; 7.2 has 274 through its supported scalar interfaces.
No focused flash exception occurs. All nine primary lifecycle/API routes are
retained, with 30 deterministic repetitions and both signs/diagnostic sweeps.

The 30-bit controls have 8 liquid pressure ratios and 4 enthalpy ratios more than
1% from unity; build44 and official72 have none. **1% is descriptive, not an
acceptance threshold.** Build44's largest normalized liquid probe-density
contamination is `6.706e-14`, and caloric residual scale `1.052e-12`, below the
existing `1e-11` nonlinear scale used for local risk screening. This is not a
certificate that every coupled Jacobian is well conditioned.

An additional fresh/reused liquid/vapor matrix has 448 rows per 8.0 build and
engine (224 scalar 7.2 rows). No exceptions or derivative-domain exclusions
occur on those stable source states. The controls have 24 descriptive >1%
rows; build44 has none, with ratios 0.99947052–1.00042014. The baseline includes
ratios as low as 0.45797 and as high as 20.22636. Fresh/reused results agree.
No smooth homogeneous derivative requirement is imposed on coexistence endpoints,
two-phase interiors or invalid states.

**Remaining precision limitation:** at the 8-bar vapor state only 0.001 K above
saturation (`P=799999.9981754856 Pa`, `h=1624022.744737779 J/kg`), build44 retains
about `-0.00011919 J/kg` independently verified caloric residual. Official 7.2
has a similar residual. Derivatives there remain close to analytic. This is
larger than the liquid's repaired residual and has not been attributed to the
remaining PT/PH internal paths. It must not be hidden behind a passing slope or
called solved by 44 bits. No further tolerance/algorithm change was attempted.

The original 612-request accuracy matrix runs on every build/engine: PH, DU,
PT, saturation endpoints/interiors, saved original inventories, boundary probes
and invalid requests. Each 8.0 build has 600 successes/12 errors; 7.2 has
598 successes/14 errors, matching its historical native version. There are no
new success/failure changes. Invalid/ambiguous errors remain recorded. The raw
below-triple PT success is explicitly unsupported, excluded from valid-value
gates and blocked by the coupled adapter; it does not expand the physical domain.
7.2's known high-pressure saturated-liquid DU failures remain visible.

Build44 versus an **unmodified** native 8.0 PH flash can differ more than the
30-bit control does, because native 8.0 itself retains loose-flash bias at other
inputs. Maximum valid-value differences are `0.0005392 Pa`, `0.001412 J/kg`,
`2.855e-7 K`, and `4.789e-7 kg/m³`; all original coarse value budgets pass.
The independent polished-DT comparison above distinguishes this from a regression.
All original saved M/U/V inputs remain unchanged: they are not replaced with PH
states at table-assigned pressures. PH and fixed-inventory recovery are distinct
experiments, retained separately in the 612 rows.

Diagnostic pressure-step ratios at the saved case illustrate the remaining
finite-resolution limit; none replaces the solver's 0.01 Pa probe:

| dP Pa | 30-bit ratio | 44-bit ratio |
|---:|---:|---:|
| 0.0001 | 0.9948051581 | 0.9948051581 |
| 0.001 | 0.9992723316 | 0.9992723316 |
| 0.003 | 64.96787849 | 0.9997305032 |
| 0.01 | 20.19045553 | 0.999959589 |
| 3 | 1.064167475 | 0.9999999081 |
| 10 | 1.019390591 | 0.9999999826 |
| -0.01 | -18.19010681 | 1.000045496 |

Saved high-pressure PH probes, using their original pressure/enthalpy steps:

| Saved PH state | 30-bit rho_P ratio | 44-bit rho_P ratio | 30-bit rho_h ratio | 44-bit rho_h ratio |
|---|---:|---:|---:|---:|
| saved-high-initial-PH | 0.9999646098 | 0.9999646098 | 1.000008197 | 1.000008197 |
| saved-high-endpoint-PH | 0.9997829731 | 1.000000668 | 1.000000094 | 0.9999997096 |

Direct recovery of the **original saved inventories**, without redefining them from PH:

| Original inventory | Build44 recovered pressure bar |
|---|---:|
| historical-low-original-inventory | 0.30174790361847 |
| saved-high-initial-original-DU | 32.630316866786 |
| saved-high-endpoint-original-DU | 32.772098459115 |

The assigned table pressures at the two high inventories differ from these direct-EOS recovered pressures by about 2283 and 3264 Pa. The precision patch does not turn a fixed-inventory recovery into a PH test or erase that representation difference.


The reverse-h ratio improves from 1.50207065 to 0.999998481; forward-h is
1.000000729. The 0.0001 Pa residual slope error remains about 0.52%, illustrating
why no universal precision claim follows from a tighter stopping parameter.

## Original solver compatibility

[SOLVER_CONTRACT.md](SOLVER_CONTRACT.md) records exact original units, scales,
limits, probes, branch/line search, stage/recovery, TR-BDF2, event and physical
requirements. The adapter injects a synchronous engine through the original
factory interface. It preserves requested-PH accounting and unaltered density;
all actual state residuals remain separate. Table PH is used only as a support
guard, adding cost but no returned/interpolated property. Native DU recovers
the original canonical M/U/V equations. No accepted model or solver is edited.

All 16 static M/U/V closures pass with build44 in each engine, versus 14/16 for
both 30-bit controls and 16/16 for official72. These are four saved targets,
five/nine-section block dimensions and both input-h/returned-h accounting
diagnostics. Original Newton tolerance, 30-iteration limit and probes are fixed.
The retained 30-bit failures are nonreducing line searches, not successful runs.
The synthetic test has no dynamics or TR-BDF2 and is not coupled qualification.

Only after the focused standalone gate and those closures passed did the A2
operating runs begin. Verbatim accepted five-section sources are loaded from
`accepted/`, not the later nine-section implementation. The selected accepted
configuration uses finite-difference thermal columns and failure-aware timestep
growth. All original physical fixture inputs, schedules, sampling intervals and
three `accuracyOptions(1e-6,1e-7,1e-8)` regimes remain unchanged.

**30/30 operating runs complete**, with no stop or domain rejection. **20/20
nominal/tight versus refined temporal comparisons pass** unchanged limits.
Independent Python accounting reconstructs all section masses, fluid energies,
thermal-node energies and combined ledgers without importing the JS balances.
Native DT checks at returned coupled states provide an additional property audit.
Frozen direct-EOS comparisons below use each fixture's original refined 1e-8 run.

| Engine / fixture | P difference Pa | h difference J/kg | Fluid T difference K | Thermal T difference K | Terminal event difference s |
|---|---:|---:|---:|---:|---:|
| chromium / cold | 0.0157818 | 0.116987 | 1.14892e-06 | 6.32197e-07 | 0 |
| chromium / feed-step | 0.0155475 | 0.117575 | 1.13389e-06 | 6.32185e-07 | 0 |
| chromium / heat-reversal | 0.115446 | 0.184726 | 7.73417e-05 | 7.55609e-06 | 0 |
| chromium / load-step | 0.0155475 | 0.117575 | 1.13389e-06 | 1.43909e-06 | 0 |
| chromium / warm | 0.0109838 | 0.236757 | 3.07441e-05 | 3.19886e-06 | 7.65573e-07 |
| webkit / cold | 0.0157818 | 0.116987 | 1.14892e-06 | 6.32197e-07 | 0 |
| webkit / feed-step | 0.0155475 | 0.117575 | 1.13389e-06 | 6.32185e-07 | 0 |
| webkit / heat-reversal | 0.115446 | 0.184726 | 7.73417e-05 | 7.55609e-06 | 0 |
| webkit / load-step | 0.0155475 | 0.117575 | 1.13389e-06 | 1.43909e-06 | 0 |
| webkit / warm | 0.0109838 | 0.236757 | 3.07441e-05 | 3.19886e-06 | 7.65573e-07 |

Independent conservation maxima across all runs:

- sectionMassKg: 9.109157872e-12.
- globalMassKg: 1.735530469e-11.
- sectionEnergyKJ: 3.343146204e-09.
- nodeEnergyKJ: 1.122257842e-11.
- globalEnergyKJ: 5.435410344e-09.

Original limits remain mass `<1e-8 kg`, required energies `<1e-6 kJ`, nonlinear
norm `<=1e-11`, thermal closure `<=1e-12 K`. The original code enforces stage
norms and recovery checks; stored sample last-residuals and accepted temporal
traces are audited. Successful per-iteration histories are not all archived;
all actual failed Newton attempts would be retained by the detached observer.

No new Newton-failure rejection occurs in these 44-bit operating runs. Accuracy
and phase-event rejections are retained, not accepted or erased. Chromium
nominal heat reversal uses 166 accepted full trials and one accuracy rejection;
the historical table FD/A2 nominal run used 1297 trials and 88 Newton failures.
That is **not a controlled attribution of the difference to the 44-bit patch**:
the property representation and adapter differ, and no coupled 30-bit control
was run. Matching-build property/closure comparisons isolate the patch; the
coupled runs establish only this candidate's observed compatibility.

Frozen independent trajectories are read unchanged. They represent the original
physical PH fixture initialization using direct EOS, not an identical table M/U/V
inventory; initial EOS/table differences are reported separately. All event
identities match within same-EOS temporal refinement; frozen comparisons cover
the terminal vapor event available in that reference. The complete original A2
verification, order, domain, rollback, zero-exchange and offset suite has not been
rerun through this adapter. No multihour or nine-section coupled run is claimed.

## Desktop runtime and memory

Linux x86_64 AMD EPYC desktop environment; Playwright 1.62.1, Chromium
151.0.7922.34 and WPE WebKit 26.5. These are actual desktop engines, not an
emulated or physical iPad. Performance runs occur after the coupled jobs finish,
using identical uncached inputs and seven outputs for all builds. Startup has
three fresh contexts; compiler/OS caches can remain warm. PH/DU liquid, vapor
and two-phase groups have three timed rounds plus repeated mixed epochs.
Official72 uses its slower scalar API because its delivered reusable bindings
cannot expose the required fields; that is an interface comparison, not an
intrinsic EOS speed claim.

| Engine / build | Mean init ms | PH liquid µs/state | DU liquid µs/state | Peak observed WASM MiB | Max worker/page timer gap ms |
|---|---:|---:|---:|---:|---:|
| chromium / official8 | 1963.1 | 68.71 | 19.84 | 53.75 | 50.9 |
| chromium / build30 | 1886.0 | 67.66 | 19.35 | 53.75 | 50.7 |
| chromium / build44 | 1939.8 | 67.07 | 19.26 | 53.75 | 50.5 |
| chromium / official72 | 1594.5 | 6772.22 | 2782.14 | 93.38 | 51.0 |
| webkit / official8 | 2162.0 | 73.00 | 18.05 | 53.75 | 59.0 |
| webkit / build30 | 2123.0 | 75.02 | 18.44 | 53.75 | 61.0 |
| webkit / build44 | 2049.3 | 71.16 | 18.22 | 53.75 | 144.0 |
| webkit / official72 | 1782.7 | 8069.44 | 3722.22 | 93.38 | 72.0 |

Matched source-build elapsed-cost ratios, build44/build30 (three short rounds; observations, not statistically resolved speed guarantees):

| Group | Chromium ratio | WebKit ratio |
|---|---:|---:|
| PH-liquid | 0.9913 | 0.9486 |
| PH-vapor | 0.9771 | 1.0065 |
| PH-two-phase | 0.9854 | 0.9719 |
| DU-liquid | 0.9954 | 0.9883 |
| DU-vapor | 0.9965 | 0.9857 |
| DU-two-phase | 1.0254 | 1.0115 |

All groups, epochs, error/recovery counts, memory snapshots and Chromium page-heap
observations remain in raw performance JSON. WASM linear memory excludes compiled
code, retained download buffers, JavaScript objects, browser/OS overhead and other
tabs. Page heap is not exclusive backend memory. Timer gaps are scheduling
observations, not measured touch latency. No physical-device memory limit, battery,
thermal throttling or long-run performance conclusion follows.

Coupled wall-clock times include the original table support guard, detached
diagnostics, browser startup and evolving solver work. Some early Chromium runs
overlap the source rebuild/screening jobs; they are not a controlled performance
ratio. The matched property workload above is the timing comparison. A production
adapter would need its own performance qualification without changing support or
scientific budgets. No property smoothing, approximate cache or server is used.

## Offline artifact and failures retained

The standalone iPad package contains all four labeled builds, exact inputs,
worker, SHA manifest and notices. It is independent of the deployed application.
Both desktop engines run all four builds from fresh pages/workers when every
origin request returns 503. Chromium also passes Playwright offline-network mode.
WebKit navigation fails in that automation mode; it succeeds in the separate
origin-disabled test. Those are separate observations, not a claim of physical
Safari disconnected/relaunch behavior.

Final ZIP: **17,651,776 bytes**, SHA256
`9086487fbf0b3320efb54a9afb52c8c1900090c95133d71399b9b6a6babb0e6b`. A second packaging run reproduces the same SHA.


[Physical iPad instructions](IPAD_TEST_INSTRUCTIONS.md) require real device/OS
labels, three fresh runs per build, manual responsiveness observations, exported
failures and actual disconnected Safari relaunch. No iPad, deployment, remote
property service, public origin or certificate installation is claimed.

Failures and unresolved observations are preserved:

- Official8/build30 reproduce the primary ~20.19 derivative ratio, nearby flash
  noise, and two static closure line-search failures per engine.
- The unchanged invalid/ambiguous property errors, below-triple raw-success guard
  warning, and 7.2 DU/interface limitations remain explicit.
- The remaining near-saturation vapor caloric residual is independently verified;
  the smallest diagnostic pressure probes still show finite-resolution error.
- V1 offline installation timed out in both engines because duplicate canonical
  URLs were passed to precache. V2 deduplicates them; V1 source/hash/failure logs
  remain. WebKit offline-emulation navigation failures remain in V2 smoke evidence;
  the unchanged V2 package passes the separate origin-disabled V3 harness.
- Initial executor network/socket permission failures and missing WebKit libraries
  were resolved using supported executor permissions and an external local sysroot.
  A mistaken FetchContent override replay was interrupted; correct CPM overrides
  produce the identical full rebuild. No failed build is presented as a result.
- An analysis replay initially re-read its own native-audit files and raised
  `KeyError: browser`; the file selector was corrected, without changing raw
  measurements or budgets. Its failure log is retained.

## Engineering decision

The approach is technically viable for continued research: source-level precision
control removes the demonstrated defect without changing the physics, solver
limits, perturbations, TR-BDF2 or acceptance budgets, and this candidate completes
the tested conservative five-section operating cases.

It is **not fully qualified**. Before adoption, engineering should review the
remaining vapor residual and other upstream flash paths, authorize the complete
A2 safety/order/domain suite plus longer supported runs, assess adapter cost,
and collect physical iPad results. A 44-bit optimum or global error guarantee
has not been demonstrated. No additional physics milestone begins here.

Stop for engineering review and explicit approval. No merge, Live Plant
integration, production migration or deployment is performed.

See [Mechanic’s Report](MECHANICS_REPORT.md), [audit](evidence/audit.json),
[coupled summary](evidence/coupled-summary.json), [precision summaries](evidence/precision-summary-8.0.0.json),
[additional-state summary](evidence/supplement-summary-8.0.0.json), and [reproduction](BUILD.md).
