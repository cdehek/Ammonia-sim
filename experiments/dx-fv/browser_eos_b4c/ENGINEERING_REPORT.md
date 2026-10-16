# Research B4C — controlled upper-quality phase classification

**FOCUSED REPAIR PASS**

The invalid upper-quality extrapolation is corrected in the supported focused
cases, original scientific budgets pass, and no material regression is introduced.
Full backend qualification remains pending. Stop for engineering review and
explicit approval.

Branch: `research/browser-eos-b4c-upper-quality-repair-20261016`.
Starting checkpoint: exact B4B `d0d11d59756c4dc32bbfdb22a5975fd6f4527e05`.
The full delivery SHA is supplied in the final response and identifies the commit
containing this report. Work is additive under this directory only.

## Preservation and scope

The starting HEAD matched exactly and the tree was clean before creating B4C.
All **1,313** previously tracked files retain their original SHA256, including
all fixtures, results, sources, reference artifacts and B1/B4A/B4B patches.
Protected remote heads are audited against `refs-before.txt`; only the requested
B4C branch is pushed. Accepted A2, production main, PR #3, release/UI/Live Plant
branches and hosting are untouched.

Pinned CoolProp 8.0.0: `ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`. All **1,782** tracked source hashes
match B4B before the new patch. All nine dependency digests match B4B. Historical
native compressed/decompressed and browser artifacts and the independent 8.0.0
wheel binaries verify. B4B's report, patch, algorithm and evidence; B4A's repair;
and B3's source-level phase traces/proposals were reviewed.

The original protected scientific checkpoints remain A2
`be9eb35a4ddf5098e685182f8104685127c6a6ee`, B1
`ef1562ae1680fccf3323391e9ec83788c5ae1e69`, B2
`6a220dd6c94bff08e00e0107cfec71854166ede2`, B3
`4e1295be9493d8bce4ca35ee0cf61accb7465226`, B4A
`94f77bb062b75ffebf17a1c9758d11c1adc61711`, B4B above, and workstation UI
`262b6092b2ed694073ad9ffd41265f44dd0b6ca0`.

## Reproduction and physical classification

The unchanged B4B native and browser replays reproduce all **86** saved base
inputs and **344** signed probes exactly, excluding native timing metadata.
Separately rebuilt native and WASM controls reproduce those scientific rows
exactly too. Historical fixtures were read, never regenerated or replaced.

Extracting the failures reproduces **11 native** and **nine per browser** invalid
upper-quality base states. Seven base states are resolved stable superheated
vapor. Four native/two browser base states are one-ULP neighbors of hg, unresolved
at the original independent reference resolution. There are **14 supported**
same-physical-vapor derivative comparisons touching the invalid band, plus one
otherwise same-vapor comparison above the existing 35-bar support limit. That
unsupported probe is retained separately. These counts are derived from evidence,
not encoded as expected test totals.

Source-traced quality and the historical two-phase Q getter are the actual molar
classifier result. The independent `rawQuality` field in the native reference
samples is recomputed from mass-specific endpoint enthalpies; mass/molar rounding
can change its last bit. Both values are retained rather than conflated.

See [the exact binary64 matrix](UPPER_QUALITY_MATRIX.md), the CSV input inventory,
and `original-upper-quality-inventory.json`. Considering invalid signed-probe
outputs as well as bases gives **14 unique native** and **12 unique browser**
input pairs. Every pair has unchanged-bit before/after execution and canonical
recovery, not just the 11/nine base rows.

Independent reference work uses the same ammonia EOS through separate unmodified
8.0.0 DT states, homogeneous Newton roots and saturation equilibrium. It is not
a different EOS or external experimental dataset. Resolved roots satisfy original
reference limits **1e-5 Pa / 1e-8 J/kg**, positive cp/cv/compressibility and T above
equilibrium. Their superheat is approximately **1.89e-7–6.66e-7 K**. Full-VLE and
superancillary endpoints are independently compared; the largest sampled hg
disagreement is about **8.82e-8 J/kg**, much smaller than the resolved
0.000915–0.001416 J/kg superheat, but larger than one ULP. Gibbs/chemical-potential
differences and endpoint pressure residuals are recorded.

Thus a sign at one-ULP distance cannot establish proven superheat. These rows
remain endpoint-unresolved. Exact endpoints, valid coexistence, supported stable
liquid/vapor, unsupported inputs and real physical crossings remain distinct.
Historical browser labels calling Q>1 coexistence are not used as physical proof;
the independent physical ledgers explicitly correct that interpretation.

## Algorithm, owner and exact source change

[ALGORITHM.md](ALGORITHM.md) and its hashed decision receipt were recorded before
the functional edit. Both pressure-caloric decision paths now dispatch **Q>1 for
H/S/U inputs** to the existing bounded homogeneous vapor flash. Its original
requested pressure/caloric value, saturation lower temperature bound, maximum
temperature, convergence, range checks and failure propagation are preserved.
Positive cp, cp/T and du/dT at fixed p independently support caloric ordering on
the tested vapor branches. This is thermodynamic justification, not a symmetry
assumption based on B4A.

Owner: `HelmholtzEOSMixtureBackend.cpp::p_phase_determination_pure_or_pseudopure`.
The exact new patch changes two conditions, and nothing else:

```cpp
} else if (Q > 1 + 1e-9 || (Q > 1 && (other == iHmolar || other == iSmolar || other == iUmolar))) {
```

Superancillary dispatch retains SatL/SatV clearing and its gas sentinel; HSU_P
reconstructs Tmin from T(p). Full VLE retains saturation_called, copied endpoints
and Tmin=SatV->T(). For Q=0, Q=1 and 0<Q<1, existing equilibrium calculations
remain. Density input retains its original upper tolerance. PT iT classification,
DU HSU_D_flash, mixtures and ancillary fast decisions are unchanged.

No Q clamp, saturated-density substitution, p/h rounding, EOS/fluid-data change,
support expansion, perturbation enlargement or solver-budget change occurs.
The model never consumes reference-polished coordinates. An unsuccessful
homogeneous inversion would still propagate; none occurs in the focused saved
matrix or shared-caller diagnostics. Numerical endpoint uncertainty is resolved
by the existing inversion, not represented as an artificial vapor fraction.

The B1 44-bit expression, B4A liquid conditions and B4B PT/cache commit remain
byte-for-byte intact. Generic Householder4 and DU are unchanged. Reversing only
the B4C condition changes restores exact B4B source. Pure and pseudopure fluids
share this classifier, so non-ammonia consequences require separate qualification;
this report certifies only its focused ammonia envelope.

Patch SHA256: `9c42f70817ac1ff812f55ab64670cb7cc81fb1606976de06ac6fa1c87e71e24a`.

## Example: approximately 8 bar, 0.001 J/kg above hg

Original P=`799999.9981754856` Pa, bits `412869ffff10db75`;
h=`1624019.7431341156` J/kg, bits `4138c7d3be3e0993`.
This is separate from the B4B saved cache fixture, whose h is
`1624022.744737779` J/kg. Neither input is rounded.

| Native result | B4B control | B4C candidate |
|---|---:|---:|
| Phase / Q | two-phase / 1.0000000008369332 | gas / -1 |
| T, K | 291.01336143550407 | 291.01336176856717 |
| Density, kg/m³ | 6.266584034238387 | 6.266584028393989 |
| Independent EOS p residual, Pa | -0.00058754394 | 0 |
| Independent EOS h residual, J/kg | -0.00094949291 | -4.66e-10 |
| Normalized inventory energy mismatch | 5.72e-10 | 1.58e-16 |
| PH→M/U/V→DU pressure difference, Pa | +0.00095402496 | +6.98e-10 |

The old coarse canonical checks could pass while its nonlinear energy scale
failed. Removing Q>1 alone would not establish this repair. Independent EOS,
stable vapor, energy accounting and recovery all agree after the change.

## Original scientific gates and signed derivatives

Original canonical limits remain **0.1 Pa / 0.1 J/kg / 1e-4 K**; standalone limits
remain **strictly below 10 Pa / 50 J/kg / 0.01 K**. Original normalized nonlinear
mass/energy scale remains **1e-11**. No acceptance tolerance is relaxed.

Inventories preserve exact accepted operations: `V=.003/5; M=rho*V;
U_kJ=M*(h/1000)-100*(P/1e5)*V; rhoDU=M/V; uDU=U_kJ/M*1000`.
All binary64 inputs, separate historical/reference/current inventories and actual
rounding through M/V are recorded. Every unique invalid base/probe input now
passes raw canonical recovery. Native upper-case maxima are approximately
**1.02e-7 Pa / 5.36e-9 J/kg / 4.47e-11 K**; browsers are approximately
**1.02e-7 Pa / 5.59e-9 J/kg / 4.36e-11 K**.

Across default native homogeneous base/probe snapshots, maximum independent
requested p/h residuals are **1.10e-6 Pa / 3.81e-6 J/kg**; maximum resolved-root
T error is **2.20e-11 K**. Maximum normalized inventory energy mismatch is
**6.11e-13**. Browser maxima are **1.40e-6 Pa / 3.72e-6 J/kg**, resolved-root T
**1.10e-11 K**, normalized energy **5.96e-13**. The largest tiny h/getter offsets
occur in unresolved endpoint inversions and are retained, not asserted to be
bit-exact EOS answers. Derivative-cache comparisons at all 11 upper bases and
the three inherited regressions are exactly equal to fresh independent DT
derivatives in the native sample.

The 14 original supported vapor comparisons improve maximum normalized mass
contamination **7.10e-10→8.30e-16**, energy **1.49e-9→1.64e-15** natively.
All original supported same-physical-phase probes pass in both browsers too.
Every original signed perturbation is preserved. Real coexistence crossings and
endpoint-unresolved probes are excluded from homogeneous two-sided slopes, with
their original results retained; invalid upper-band vapor is not mislabeled as
a physical crossing.

## Saturation and mandatory inherited regressions

The saved matrices cover approximately 0.302989371, 3.5, 8 and exactly 35 bar,
liquid approach, hf, interior mixture, hg, superheated vapor, both sides of the
original ±0.99e-9 / ±1.01e-9 quality diagnostics, and exact/one-ULP endpoint
neighbors. Diagnostic offsets never replace solver perturbations.

Both saturation-decision paths eliminate invalid upper-Q returns. **567**
default equilibrium snapshots across runtimes pass endpoint/lever checks;
full-VLE equilibrium and original supported signed probes pass too. Continuity
is checked against equilibrium endpoints and independent homogeneous roots,
without requiring single-phase derivative smoothness across coexistence.

The B1 saved 44-bit PH fixture and its original signed precision probes pass.
The exact B4A P/h=`30298.937123458254 / 98904.56398938334` remains stable liquid,
with no negative lever extrapolation, consistent EOS, canonical recovery and
original same-liquid probes. Its reverse-P probe still physically crosses into
coexistence. The exact B4B P/h=`799999.9981754856 / 1624022.744737779` retains
consistent final PT density/derivatives, independent p/h/u, original canonical
recovery and nonlinear energy consistency. Their complete default base/probe
values are unchanged by B4C; legitimate upper-band outputs do change.

There are **47 lifecycle cases** per build/runtime: fresh/reused PH/PT/DU,
repeated state reuse, endpoints, mixture and stable offsets. Existing native
three rejected sequence calls and browser six rejected sequence calls remain
identical. **96 PH/PS/PU diagnostics** per build/runtime/path cover stable liquid,
endpoints/ULP neighbors, mixture and upper-band vapor. All candidate diagnostics
return without property exceptions, agree fresh versus reused, show independent
stable/caloric derivatives, and have no upper-quality PH/PS/PU extrapolation.
This does not extend original PH budgets into an invented universal entropy budget.

Native source traces show **430** saved PH snapshots. Logging-on/off and
uninstrumented results match exactly; they match the full scientific matrix.
Fourteen dispatches change. Total homogeneous residual calls are **1545→1627**,
with 4–8 calls for each newly resolved upper input. These are actual residual
evaluations, not mislabeled Newton iterations. Browser internal execution counts
are not inferred from native instrumentation; adapter call counts are separate.

## Limited accepted A2 compatibility

All twelve injected dependency snapshots match accepted A2 exactly. Its original
scientific check is extracted verbatim from the Git object and applied to each
recorded sample and zero-exchange trial. Mass/internal-energy inventories,
transport/enthalpy fluxes, tube/fin/air equations, TR-BDF2, Newton limit 30,
original finite differences, temporal/nonlinear/thermal tolerances, domain guard,
rollback and conservation code remain unchanged.

Both browsers complete cold/warm/heat reversal through 0.2 s and feed disturbance
through 15.01 s. Accepted/rejected step counts remain **58/5, 172/22, 250/9,
58/1**, respectively. Newton work, residual evaluations, property-call counts
and phase events are unchanged in these bounded fixtures. All original assertions
pass. Maximum aggregate/section mass residuals are approximately **1.35e-12 /
1.20e-12 kg** (<1e-8); maximum combined/section energy residuals **4.32e-10 /
6.14e-10 kJ** (<1e-6). Recorded temporal errors and nonlinear norms pass.

Original liquid and saved B4B vapor zero-exchange trials pass, as does an isolated
upper-quality vapor trial through the unchanged accepted interfaces at original
P/h=`799999.9981754856 / 1624019.7431341156`. Trial input objects remain exactly
preserved. Liquid norm is **5.88e-17**, both vapor norms zero. A control zero
residual alone is not physical validation; the independent property gates above
establish the upper fixture's corrected inventory.

This is limited compatibility, not complete A2 option/reference/event/domain-stop,
rollback or long-duration qualification. No full campaign was run.

## Builds, provenance and performance

Native Linux: GCC 14.2.0, Python 3.12.14, CMake 4.4.4, Ninja 1.13.2. WASM:
Emscripten 4.0.12 / pinned emsdk above, LLVM revision in `build-versions.json`.
Release `-O3 -DNDEBUG -std=gnu++17`; native shared EXTERNC and upstream WASM
exception/embind/ES6/memory-growth settings. No fast-math. Exact compiler commands,
CMake caches, dependency digests, patches, native archives and JS/WASM hashes,
licensing notices and source-stage manifests are preserved.

| Artifact | SHA256 |
|---|---|
| Rebuilt native B4B control | `d8fa3a5ac1993dd5f6e6a001e70084838e1eea4baa590e1347ea5cb13795c00a` |
| Native B4C candidate | `1dbd593fb568d18af704bedc5e29b790abddbadd7f6f03838819ca193b9afbb1` |
| Rebuilt control WASM | `c8520e9c867e662c2731ed581c02d4157df2a5eed284be866ed3b45d29b2519d` |
| Candidate WASM | `8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5` |
| Both JS wrappers | `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217` |

Native diagnostic and compressed hashes are in `native-binaries.json`. Different
source-directory strings/generated ordering can change rebuilt whole-binary
hashes; complete scientific control equivalence is separately demonstrated.

Authoritative timings use five 150 ms rounds, medians of full update/getter
calls, serially after science and compilers. These are descriptive host timings.

| Runtime | Upper-band PH, control→candidate µs | Ordinary B4B vapor PH µs | Stable-liquid PH µs | Two-phase PQ µs |
|---|---:|---:|---:|---:|
| Native | 19.11→85.59 | 89.23→88.20 | 78.60→77.59 | 18.83→18.65 |
| Chromium | 5.57→70.86 | 72.89→73.93 | 66.46→63.83 | 5.26→5.41 |
| Desktop WebKit | 5.59→76.18 | 77.92→75.42 | 68.49→66.61 | 4.86→5.04 |

The newly resolved flash costs 4.48× native, 12.73× Chromium and 13.63× WebKit
versus the invalid lever shortcut. This is local property cost, not simulator
slowdown. Other groups remain close to control within short-run variability.
Native factory initialization is about 731→740 ms, RSS 120120→120124 KiB including
Python/reference wheel. Browser initialization is Chromium 2094→1972 ms, WebKit
2170→2287 ms in these samples. Memory grows from **22,544,384 to 56,360,960 bytes**
at first factory and remains there for both main/worker workloads. Candidate
maximum observed main-thread heartbeat gaps during worker work are **11.2 ms
Chromium / 44 ms WebKit**. No performance property/worker/init exception occurs.

Separate matched end-to-end 0.2 s cold A2 advances cost **2094→2039 ms Chromium**,
**2194→2269 ms WebKit**, with identical work counts. Both controls already include
B1+B4A+B4B; these directly measure additional B4C cost. Historical B4A/B4B ratios
are not multiplied into a fictitious cumulative simulator slowdown. One bounded
cold timing per runtime/build is not a statistical speed guarantee or real iPad
measurement. Native, browser and worker absolute microseconds include different
interface overheads and are not pure-kernel cross-runtime comparisons.

## Preserved limitations, mistakes and next gates

At exactly 35 bar, property correctness is separate from inversion/support.
The same **seven full-VLE canonical exceptions** and **seven browser strict
adapter recovery rejections** remain at the same saved fixture IDs. A tiny
recovered-pressure overshoot is not evidence of a physical domain exit. No
rounding, clamping, support enlargement or DU repair is made. **166 identical
native fixed-inventory evaluations** and **42 per browser** retain identical
control/candidate raw DU and guard behavior, including historical failures.

Rejected-PT loader cleanup/reference-count assertions remain unchanged: all six
rejected sequence calls per browser are retained as failures, not successful PT
updates; later supported PH operations continue. The B4C loader changes asset
mapping only. No loader cleanup repair is included.

Retained non-scientific failures: initial sandbox proxy isolation; missing apt
package indexes resolved by verified isolated package downloads; Playwright's
host-library warning resolved with unchanged WPE setup; the first boundary
auditor wrongly treated homogeneous DU's established Q=10000 sentinel as mixture
quality (rejected audit preserved, source/native/EOS-based interpretation fixed);
and a first native timing pair overlapped A2 zero-exchange (retained as
`contended-do-not-use`, excluded from all reported timings). No scientific
acceptance criterion was weakened and no unsuccessful scientific gate is hidden.
All build/test process deadlines completed.

Recommended next milestone, after explicit engineering approval: controlled
35-bar inverse/support forensics using identical original inventories, independent
stable roots, EOS residuals and original canonical/nonlinear budgets. Distinguish
inverse numerical overshoot from genuine domain exit before proposing a repair.
The separate loader defect also needs its own review. Full accepted A2 option,
reference/refinement, phase-event, domain-stop/rollback and long-duration
qualification, broader fluid/source review and physical Safari/iPadOS memory,
performance/offline testing remain future gates. No deployment or Cloudflare
change is authorized or performed.
