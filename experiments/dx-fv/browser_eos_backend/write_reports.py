"""Render the engineering report from completed, separately retained evidence."""
from pathlib import Path
import json,statistics
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(n):return json.loads((E/n).read_text())
precision=read('precision-summary-8.0.0.json')+read('precision-summary-7.2.0.json')
coupled=read('coupled-summary.json');assert len(coupled['runs'])==30 and all(r['completedAllSamples'] for r in coupled['runs'])
assert len(coupled['temporalComparisons'])==20
prop={r['file']:r for r in precision};provenance=read('build-provenance.json')
lines=[]
def add(s=''):lines.append(s)
add('''# B1 — Precision-controlled browser EOS feasibility

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
|---|---:|---|''')
for build in ['build30','build44']:
 for name in ['coolprop.js','coolprop.wasm']:
  p=provenance['artifacts'][f'vendor/{build}/{name}'];add(f"| {build}/{name} | {p['bytes']} | `{p['sha256']}` |")
add('''
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
|---|---:|---:|---:|---:|---:|''')
for build in ['official8','build30','build44','official72']:
 p=prop[f'chromium-{build}.json']['primary'];s=p['perturbed']
 add(f"| {build} | {p['analytic']:.12g} | {p['finite']:.12g} | {p['ratio']:.12g} | {s['pResidual']:+.9g} | {s['hResidual']:+.9g} |")
add('\nDensity/enthalpy derivatives at fixed pressure, units `(kg/m³)/(J/kg)`; both original enthalpy perturbation signs are retained:\n\n| Backend | Analytic rho_h | Forward finite difference | Forward ratio | Reverse finite difference | Reverse ratio |\n|---|---:|---:|---:|---:|---:|')
for build in ['official8','build30','build44','official72']:
 rows=read(f'chromium-{build}.json')['precision']['rows'];method='high' if build=='official72' else 'reused'
 a=next(r for r in rows if r['id']=='exact-saved' and r['method']==method and r['axis']=='H' and r['step']>0)
 b=next(r for r in rows if r['id']=='exact-saved' and r['method']==method and r['axis']=='H' and r['step']<0)
 add(f"| {build} | {a['analytic']:.12g} | {a['finite']:.12g} | {a['ratio']:.10g} | {b['finite']:.12g} | {b['ratio']:.10g} |")
add('''
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
|---:|---:|---:|''')
for step in [.0001,.001,.003,.01,3,10,-.01]:
 vals=[]
 for build in ['official8','build44']:
  rows=read(f'chromium-{build}.json')['precision']['rows'];r=next(r for r in rows if r['id']=='exact-saved' and r['method']=='reused' and r['axis']=='P' and r['step']==step);vals.append(r['ratio'])
 add(f'| {step:g} | {vals[0]:.10g} | {vals[1]:.10g} |')
add('\nSaved high-pressure PH probes, using their original pressure/enthalpy steps:\n\n| Saved PH state | 30-bit rho_P ratio | 44-bit rho_P ratio | 30-bit rho_h ratio | 44-bit rho_h ratio |\n|---|---:|---:|---:|---:|')
for ident in ['saved-high-initial-PH','saved-high-endpoint-PH']:
 vals=[]
 for axis in ['P','H']:
  for build in ['build30','build44']:
   rows=read(f'chromium-{build}.json')['precision']['rows'];r=next(r for r in rows if r['id']==ident and r['method']=='reused' and r['axis']==axis);vals.append(r['ratio'])
 add(f'| {ident} | '+ ' | '.join(f'{v:.10g}' for v in vals)+' |')
add('\nDirect recovery of the **original saved inventories**, without redefining them from PH:\n\n| Original inventory | Build44 recovered pressure bar |\n|---|---:|')
rows=read('chromium-build44.json')['accuracy']
for ident in ['historical-low-original-inventory','saved-high-initial-original-DU','saved-high-endpoint-original-DU']:
 r=next(r for r in rows if r['id']==ident);add(f"| {ident} | {r['state']['p']/1e5:.14g} |")
add('\nThe assigned table pressures at the two high inventories differ from these direct-EOS recovered pressures by about 2283 and 3264 Pa. The precision patch does not turn a fixed-inventory recovery into a PH test or erase that representation difference.\n')
add('''
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
|---|---:|---:|---:|---:|---:|''')
for r in coupled['runs']:
 if r['relativeTolerance']!=1e-8:continue
 d=r['frozenDirectEOSComparison'];add(f"| {r['browser']} / {r['case']} | {d['pressureBar']*1e5:.6g} | {d['enthalpyKJkg']*1000:.6g} | {d['fluidTemperatureK']:.6g} | {d['thermalTemperatureK']:.6g} | {r['terminalEventErrorSeconds']:.6g} |")
add('\nIndependent conservation maxima across all runs:\n')
for k in ['sectionMassKg','globalMassKg','sectionEnergyKJ','nodeEnergyKJ','globalEnergyKJ']:
 add(f"- {k}: {max(r['independentConservation'][k] for r in coupled['runs']):.10g}.")
add('''
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
|---|---:|---:|---:|---:|---:|''')
perfSummary=[]
for browser in ['chromium','webkit']:
 for build in ['official8','build30','build44','official72']:
  p=read(f'{browser}-performance-{build}.json');worker=p['worker']['result'];assert worker['ok'];w=worker['performance']
  def cost(group):
   rows=[r for r in w['timings'] if r['group']==group];return sum(r['elapsedMS'] for r in rows)/sum(r['calls'] for r in rows)*1000
  init=statistics.mean(r['init']['totalMS'] for r in p['startup'])
  mem=max([w['linearMemory']]+[r['linearMemory'] for r in w['timings']+w['sustained']])/2**20
  out={'browser':browser,'build':build,'meanInitMS':init,'PHLiquidMicroseconds':cost('PH-liquid'),'DULiquidMicroseconds':cost('DU-liquid'),'perGroupMicroseconds':{group:cost(group) for group in sorted({r['group'] for r in w['timings']})},'peakWASMMiB':mem,'maxTimerGapMS':p['worker']['maxTimerGapMS'],
       'failures':sum(r['failures'] for r in w['timings']+w['sustained']),'errorRecovery':w['errorRecovery']}
  perfSummary.append(out);add(f"| {browser} / {build} | {init:.1f} | {out['PHLiquidMicroseconds']:.2f} | {out['DULiquidMicroseconds']:.2f} | {mem:.2f} | {out['maxTimerGapMS']:.1f} |")
add('\nMatched source-build elapsed-cost ratios, build44/build30 (three short rounds; observations, not statistically resolved speed guarantees):\n\n| Group | Chromium ratio | WebKit ratio |\n|---|---:|---:|')
for group in ['PH-liquid','PH-vapor','PH-two-phase','DU-liquid','DU-vapor','DU-two-phase']:
 ratios=[]
 for browser in ['chromium','webkit']:
  a=next(r for r in perfSummary if r['browser']==browser and r['build']=='build30')
  b=next(r for r in perfSummary if r['browser']==browser and r['build']=='build44')
  ratios.append(b['perGroupMicroseconds'][group]/a['perGroupMicroseconds'][group])
 add(f'| {group} | {ratios[0]:.4f} | {ratios[1]:.4f} |')
add('''
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
''')
package=read('ipad-package.json');add(f"Final ZIP: **{package['bytes']:,} bytes**, SHA256\n`{package['sha256']}`. A second packaging run reproduces the same SHA.\n")
add('''
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
''')
(B/'ENGINEERING_REPORT.md').write_text('\n'.join(lines).rstrip()+'\n')
(E/'performance-summary.json').write_text(json.dumps(perfSummary,indent=2)+'\n')
(B/'MECHANICS_REPORT.md').write_text('''# 🔧 Ammonia Lab — The Mechanic’s Report

**PROMISING — the precision fix works in the tests, but it is not ready for the
working plant simulator.**

The problem was in how far the browser property calculation followed its search
for the refrigerant state. When we asked for a tiny pressure change, it sometimes
stopped with a slightly different heat-content error. That error was small in
ordinary engineering units, but large compared with the tiny density change our
solver was trying to measure. The liquid appeared about 20 times too responsive.

We built the same CoolProp source two ways. One kept the original stopping rule;
the other made that search more precise. We did not change ammonia's property
equations, adjust reported density, or loosen the simulator's tolerances. The
original setting reproduced the fault. The tighter setting brought the pressure
response back close to the EOS's own calculated response in both desktop browsers.
A second complete compilation produced exactly the same experimental binary.

We then checked the mass-and-energy solver. The tighter build passed the small
inventory checks and completed the five-section cold, warm, load-change,
feed-change and heat-reversal cases at all three original accuracy settings in
Chromium and WebKit. Independent checks found the mass and energy books balanced
within the existing limits. Rejected trial steps stayed rejected.

There is still work to do. One vapor state very close to saturation retains a
small heat-content mismatch. We have not qualified every operating corner,
every safety/rollback check, or long-running simulations. A desktop WebKit result
does not tell us how a real iPad handles memory, battery or heat. An isolated test
package is ready for that physical device test; no iPad result has been claimed.

The tested route is worth pursuing. It is not permission to fit it to Live Plant.
The application, equipment controls, UI and production engines remain untouched.
Engineering review and explicit approval come next; nothing is merged or deployed.
''')
print('Wrote engineering, mechanic and performance summaries from completed evidence')
