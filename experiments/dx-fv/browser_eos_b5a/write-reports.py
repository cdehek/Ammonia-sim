"""Render review documents from preserved scientific evidence, not expected totals."""
from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parent;E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
read=lambda n:json.loads((E/n).read_text());a=read('gate-A-audit.json');fixed=read('fixed-comparison-summary.json');reg=read('regression-audit.json');bins=read('native-binaries.json');perf=read('native-performance.json');orig=read('original-failures.json')['rows'];lut={r['fixedKey']:r for r in orig if r['runtime']=='native-full-VLE'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(H/'fixed-inventory.csv',E/'fixed-inventory.csv')
assert read('fixed-inputs.json')==json.loads((H/'fixed-inputs.json').read_text())
(E/'inventory-preservation.json').write_text(json.dumps(dict(all250RecordsAndMetadataIdentical=True,uniquePairs=len({tuple(r['input']['bits'][k] for k in ['rho','u']) for r in read('fixed-inputs.json')}),fixedInputSHA256=sha(E/'fixed-inputs.json'),fixedCSVByteIdentical=sha(E/'fixed-inventory.csv')==sha(H/'fixed-inventory.csv')),indent=2)+'\n')
rows=[]
for r in a['rows']:
 old=lut[r['key']];x=old['fixedInput'];out=r['result'];q=out.get('DU',{}).get('values',{}).get('Q');current='liquid, Q=10000 sentinel' if r['disposition']=='resolved-stable-liquid' else 'raw liquid; unresolved' if q is not None else 'QT refusal; unresolved'
 rows.append(f"| {r['key']} | `{old['id']}` | {x['values']['rho']!r} | {x['values']['u']!r} | `{x['bits']['rho']}` / `{x['bits']['u']}` | {current} |")
(B/'FAILURE_MATRIX.md').write_text('''# Original seven DU failures — preserved before/after identities

All seven originally raised underlying C++ `OutOfRangeError` at the unchanged
`HelmholtzEOSMixtureBackend.cpp:1547` QT range check. The C API reports
`Error: Input vapor quality [Q] must be between 0 and 1`; the research wrapper
raises `ValueError`. No DU state exists after these failed updates. Original
Q, T, residuals, iteration stops, saturation thresholds and independent roots
are in `evidence/original-reproduction.json`, not discarded after repair.

| Fixed key | Original fixture | Requested rho kg/m³ | Requested u J/kg | rho / u binary64 bits | A1 disposition |
|---|---|---:|---:|---|---|
'''+ '\n'.join(rows)+'''

Only rows 146, 151 and 152 are independently resolved physical successes.
Row 162 passes raw numerical checks but remains endpoint-unresolved under the
original reference resolution. Rows 148, 164 and 165 retain the exact original
quality-range exception. Their Q remains respectively 1.000000000000002,
1.0000000000000018 and 1.0000000000000024. No clamp is applied.

`gate-A-audit.json` gives each A1 final cached coordinate, both densities,
pressure/chemical-potential residuals, caloric comparison, current output/error,
reference difference and all trace events. `gate-B-characterization.json`
retains every unresolved identity and mathematical reference. `control-comparison.json`
and `A1-comparison.json` include every historical row and all 73 unique pairs
on both paths. `additional-inventories.json` retains all 21 separate saved B5
reference inventories, including the three remaining A1 full-VLE failures.

The seven original browser rejections per engine remain in
`original-failures.json` and the unchanged B5 FAILURE_MATRIX.md, with their
below/above-35-bar mathematical diagnoses. They are separate from this matrix.
No A1 browser candidate was qualified or strict support guard bypassed.
''')
resolved=[r for r in a['rows'] if r['disposition']=='resolved-stable-liquid'];maxcanon={k:max(abs(r['result']['canonicalDifferences'][k]) for r in resolved) for k in ['p','h','T']};maxnorm=max(max(r['result']['normalizedResiduals'].values()) for r in resolved)
artifactTable='\n'.join(f"| {name} | `{v['sha256']}` |" for name,v in bins.items())
perfTable=[]
for full in [False,True]:
 for group in ['resolved-liquid','vapor-endpoint','mixture','stable-vapor']:
  r=[next(x for x in perf['rows'] if x['build']==build and x['fullVLE']==full and x['group']==group) for build in ['control','A1']]
  perfTable.append(f"| {'full VLE' if full else 'default'} | {group} | {r[0]['medianMicroseconds']:.2f} | {r[1]['medianMicroseconds']:.2f} | {'control fails; A1 succeeds' if full and group=='resolved-liquid' else 'both fail' if full and group=='vapor-endpoint' else 'both return'} |")
patchsha=sha(B/'gate-a.patch')
report=f'''# Research B5A — controlled DU saturation repair

**PARTIAL REPAIR**

Gate A corrects the demonstrated stale DU saturation decision and independently
recovers the three resolved original liquids at unchanged rho/u. Four original
endpoint states remain unresolved at the original reference resolution; three
still throw invalid-quality exceptions. Gate B is not passed and no Gate B
patch or Gate A+B candidate is delivered. A raw return from the hf ULP case is
not counted as a physical success. Stop for engineering review and explicit
approval; this backend is not qualified for integration.

## Branch, chronology and preservation

Branch: `research/browser-eos-b5a-du-saturation-repair-20261016`.
Start: exact B5 `e30ad9d76bc892aa355126339997d6184c8729d2`, clean before branching.
The full delivery SHA is the final commit containing this report (`git rev-parse
HEAD` and the delivery response), avoiding a self-referential commit identifier.
Gate A implementation/independent verification commit:
`b013448bc1005d9bb922c4420772b590180febd2`.
Pre-edit design commits: `2a610e2ba018394243737308c979f63fece44557` and its
conditioning revision `83fde7145ff8e7f63d48b0951b9c20d8b9abdd8b`.

All 1,661 B5 starting tracked files are preserved by SHA256. Work is additive
under `experiments/dx-fv/browser_eos_b5a/`. Protected remote refs, including
production, UI, research checkpoints and PR #3, are captured in `refs-before.txt`
and compared in the final preservation receipt. Only the requested B5A branch
is pushed. No production, UI, Live Plant, release, deployment, loader or adapter
source changes occur. Accepted A2 is `be9eb35a4ddf5098e685182f8104685127c6a6ee`;
all twelve five-section dependency snapshots match its Git objects exactly.

Pinned upstream 8.0.0: `ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`. All 1,782 reconstructed B4C source
hashes, 137 inherited native/browser artifact identities, four inherited patches
and all nine dependency digests match. All four patches remain reverse-applicable
unchanged after A1. B1's 44-bit expression, B4A liquid classification, B4B PT
cache synchronization and B4C upper-quality classification are preserved.

The additional three B5 native archives and installed 8.0 wheel identities also
verify. Sequencing limitation: explicit SHA256 checking of the B5 diagnostic
archives was recorded after first diagnostic replay/A1 application, although
those files were already protected by the exact B5 Git checkout and all traces
reproduced. Do not interpret that later receipt as a pre-load audit. Full details,
setup warnings and retained attempts are in `execution-notes.json`.

## Exact reproduction and independent references

Before functional edits, all seven original exceptions reproduced individually.
All 250 fixed-ledger results matched B5, as did archived diagnostic events and
fresh/reused results. The separately rebuilt unchanged control also matches all
250 scientific rows exactly. The 250 records represent 73 unique rho/u pairs;
all are retained on their historical paths and both paths are independently
exercised for every unique pair. All original bits and operation ordering remain:

```
V = .003 / 5
M = rho * V
U_kJ = M * (h / 1000) - 100 * (P / 1e5) * V
rho_DU = M / V
u_DU = (U_kJ / M) * 1000
```

Neither a PH rerun nor independent reference replaces these inventories. The
separate 21 already-saved B5 reference inventories are also replayed bit-exactly,
with fresh independent homogeneous and coexistence roots; original control
results reproduce. Their full-VLE errors change from 10 to 3, not to a physical
endpoint qualification. All 84 build/path records retain errors or fresh EOS
checks. Returned states pass original canonical/nonlinear limits.

All 73 fixed-inventory homogeneous roots and coexistence roots are recomputed
using separate unmodified 8.0 DT states. Coexistence independently enforces
pL=pV, gL=gV, specific-volume and energy equations; positive cp/cv/compressibility
and dp/drho are retained. An algebraic homogeneous root inside the coexistence
dome is excluded as a physical solution. The separate same-EOS 65-digit roots
repeat B5's stored values exactly, and 90-digit repeats meet the original
1e-5 Pa / 1e-8 J/kg resolution. Coefficients and exact binary64 constants are
unchanged. These are mathematical EOS diagnostics, not experimental ammonia
measurements or a new physical operating envelope.

## Gate A: consistent evaluated state and decision accuracy

ALGORITHM_A.md and its hashed pre-edit receipts precede source changes. The
minimal opt-in belongs to `saturation_D_pure`, selected only by legacy DU in
`HSU_D_flash`. Other H/S/P callers retain the original routine behavior.
A1 accepts the evaluated saturation coordinates only when the original norm
is <=1e-9 and the local undamped Newton correction reaches roundoff scale in
tau and the reduced-density vector. The loop then breaks before another advance.
The imposed density remains the exact internal requested density, including
actual mass-to-molar conversion rounding. No saturated density is substituted.

The vector scale accounts for residual cancellation involving liquid-density
terms at low vapor density. Tau retains its own relative criterion because the
caloric boundary is evaluated at imposed rho. This is local DU polishing,
not a global CoolProp tolerance change. A final refresh alone was not presumed
accurate: actual final p/g and caloric errors were independently checked.
Original iteration/retry budgets, generic solvers and QT validation are unchanged.

Both cached densities and temperatures equal the final evaluated coordinates
for every original failure. Maximum final saturation mismatch is
{max(abs(r['pressureDifferencePa']) for r in a['rows']):.6g} Pa and
{max(abs(r['chemicalPotentialDifferenceJkg']) for r in a['rows']):.6g} J/kg in
chemical potential. The resolved liquids' final cached caloric errors are below
1.28e-9 J/kg, versus the original approximately +9.26e-5 J/kg error. Their
positive input-minus-saturation energy signs are now correct.

For row 146 the comparison changes from approximately -5.0070e-5 J/kg to
+4.2558032449e-5 J/kg, against an independent +4.2557268528e-5 J/kg. A1 dispatches
the existing stable homogeneous liquid solver. Rows 151/152 behave likewise.
Their largest original-PH canonical differences are {maxcanon['p']:.6g} Pa,
{maxcanon['h']:.6g} J/kg and {maxcanon['T']:.6g} K. Maximum fresh-EOS normalized
mass/energy residual is {maxnorm:.6g}. All original applicable budgets pass.

Gate A's independent focused check passes, including 106 phase-resolved
cross-path records, 42 resolved focused primary states across supported
pressures, genuine coexistence, final caches, original inputs and logging parity.
All 250 uninstrumented/logging-on/logging-off fresh/reused rows agree exactly.
The source is restored to the exact uninstrumented A1 manifest afterward.

Patch SHA256: `{patchsha}`.
Exactly three source files change; the other 1,779 remain byte-identical.
The sole patch is `gate-a.patch`. It does not alter generic Newton/Brent or
`HelmholtzEOSMixtureBackend.cpp`. The shared routine's non-DU stale-state behavior
is intentionally not globally repaired or qualified by this milestone.

## Gate B and each original disposition

FAILURE_MATRIX.md gives all seven original IDs, decimal inputs and binary64
coordinates. Rows 146, 151 and 152 are resolved stable-liquid successes.
Row 162 returns raw homogeneous liquid and passes numerical value/closure checks,
but its ~2.33e-9 J/kg mathematical separation remains endpoint-unresolved.
Rows 148, 164 and 165 still fail the exact QT quality validator, with
Q=1.000000000000002, 1.0000000000000018 and 1.0000000000000024.

Their quality residuals converge at the original iteration-10 scaled-residual
stop, at T=345.5636735993518 K. Returned and last-evaluated T agree. Actual
residuals are approximately -2.00e-15, -2.00e-15 and -2.22e-15; an algebraic
residual is not proof of an admissible quality. No raw DU state exists after
these exceptions. C++ `OutOfRangeError` at the unchanged QT check becomes C API
error text and research-wrapper `ValueError`.

High precision places 148/164 just inside mathematical equilibrium; choosing
a homogeneous fallback would replace equilibrium with an algebraic branch.
For 165 the mathematical root is infinitesimally homogeneous, but A1's caloric
comparison is equal at binary64 precision. All three remain below the original
phase-resolution contract. GATE_B_DECISION.md documents the rounding/dispatch
contributions and why no safe fallback is established here. No clamp, endpoint
density substitution, pressure movement, input-energy change, metastable-root
acceptance or validator weakening is implemented. Gate B is NOT PASSED.

Raw fixed-ledger errors change 29→9; unique-pair cross-path errors change 21→4.
These are evidence counts, not acceptance counts. Every exception and every
unresolved raw return remains classified. All 167 default ledger states are
bit-identical to control; all returned fixed/cross-path states meet the original
canonical, fresh-EOS nonlinear, standalone and quality-range checks. Endpoint
physical acceptance remains separate and incomplete.

## Native regressions and original scientific requirements

The original B4C native focused auditor passes all its assertions on newly run
86 base fixtures and 344 unchanged signed probes. All default scientific rows
match B4C exactly; full-VLE PH bases/probes also match. This reruns B1 precision,
B4A subcooled-liquid phase/canonical recovery, B4B PT/cache/EOS/energy and all
11 original B4C upper-band base fixtures. Fourteen independent derivative-cache
snapshots are exact, with zero derivative differences. Forty-seven lifecycle
rows, including rejected sequences, are exact.

Each of default/full-VLE PH/PS/PU has 96 newly run diagnostics, unchanged outputs
and fresh/reused agreement. A full-VLE DU canonical failure originating from
`PS-3500000.0-hg-minus-ULP` remains explicit. The 120 DH/DS/DP shared-density
comparisons are exact, including five failures in both builds. Existing errors
are not called passes. Tests include endpoints, genuine coexistence, supported
pressures around 0.303/3.5/8 bar and exactly 35 bar. Non-ammonia, pseudopure,
critical-region and general mixture consequences remain unqualified.

No scientific contract changes: canonical <=0.1 Pa / <=0.1 J/kg / <=1e-4 K;
nonlinear mass/energy <=1e-11; standalone strictly <10 Pa / <50 J/kg / <0.01 K;
original independent resolution 1e-5 Pa / 1e-8 J/kg. Five-section volume,
conservative equations, signed finite differences, Newton/TR-BDF2 limits,
conservation checks and support domain remain byte-identical. No new coupled
conservation result is claimed because A2 trials were not run.

## Browser, A2, B5B and loader status

New native Linux control/A1/diagnostic builds are traceable below. No A1 WASM
build or Chromium/desktop WebKit candidate run is claimed: essential B5A
acceptance is incomplete, and no Gate A+B candidate exists. Native default-path
equivalence is not substituted for a browser execution. Desktop Chromium is
available; emcc is absent in this fresh workspace. Tool installation/builds were
not pursued after the Gate B blocker. No physical iPad performance is claimed.

The unchanged accepted A2 dependency closure verifies, but cold/warm startup,
feed disturbance, heat reversal, liquid/vapor zero exchange and selected 35-bar
accepted-model trials are NOT RUN because essential scientific gates do not
pass. No guard is bypassed and no unattempted trial is called a guard-induced
BLOCKED result. The full original B2/A2 campaigns remain out of scope.

All seven original strict browser rejections per engine and their B5 mathematical
diagnoses remain explicit: five exact rounded inventories slightly exceed the
35-bar maximum; two lie below while numerical recovery overshoots. All original
raw browser recoveries pass canonical budgets. B5B is unresolved. No adapter
support guard, pressure maximum, unit conversion or domain classification
changes. A1 incidentally changes full-VLE raw output where it fixes dispatch;
those values and pressure sides are recorded separately, not called a B5B fix.

The rejected-PT browser loader reference-count/cleanup defect is unchanged and
unresolved. Its six rejected browser sequence calls are preserved historical
failures, not newly executed tests. Native lifecycle rejection evidence is
newly rerun and unchanged. No loader exception handling or Live Plant change.

## Measured native cost and build identities

Serial matched complete C API update/getter timing uses five 150 ms rounds.
These are descriptive host measurements; failed calls are counted separately.

| Path | Workload | Control µs | A1 µs | Outcome |
|---|---|---:|---:|---|
'''+ '\n'.join(perfTable)+f'''

The liquid full-VLE comparison is failure→success, not a valid speedup ratio.
Factory initialization is about {next(r['initializationSeconds'] for r in perf['rows'] if r['build']=='control'):.3f} s control and
{next(r['initializationSeconds'] for r in perf['rows'] if r['build']=='A1'):.3f} s A1 in this single-process sample.
Peak process RSS ranges 121196–155508 KiB across sequentially loaded libraries;
it includes Python/reference and both backends, not an isolated per-build memory
increment. WASM linear memory, worker responsiveness and browser initialization
are NOT MEASURED in B5A. No simulator slowdown ratio is inferred.

For each resolved original liquid, saturation evaluations change 2→3, adding
two saturated-state DT updates. Their legacy quality residual calls change
11→0. Existing homogeneous residual evaluations are 5, 6 and 6. Remaining vapor
endpoint cases retain 11 quality residual calls and iteration-10 Brent stopping.
Individual lower-level EOS/cache operations are not separately instrumented;
these are actual state-update/residual counts, not fabricated kernel counts.
Logging adds cached-coordinate reads only; parity against uninstrumented A1 is
exact. No browser internal counts are inferred from native logs.

Compiler/runtime: GCC 14.2.0-19, Python 3.12.14, CMake 4.4.4, Ninja 1.13.2;
Release O3/NDEBUG/C++17, EXTERNC shared library, no fast-math. Full CMake cache,
compile commands, all source hashes, dependency digests and archive hashes are
preserved. The first control build timed out at 900 s after 57/69 steps; one
unchanged 300 s continuation completed. A1 and diagnostic incremental builds
completed within their 300 s bounds. All property/reference runs completed
within their explicit bounds; preserved partial logs and guarded setup attempts
are retained. At most two compiler jobs were used. The build-directory library
is diagnostic; named archived artifacts below are authoritative. External source
was restored to uninstrumented A1.

| Native artifact | Decompressed SHA256 |
|---|---|
{artifactTable}

BUILD.md gives reproducible commands, immutable input handling, instrumentation,
restoration and bounds. Native archives include the upstream licenses/notices
already retained in the unchanged research vendor trees; no EOS/data refit.

## Evidence index and next acceptance gates

| Deliverable | Evidence |
|---|---|
| Start, protected refs, historical/source/A2 closure | checkpoint, starting-file-hashes, preservation-verification, dependency-verification, refs-before/after, final-preservation |
| Original seven reproduction and exact inputs | original-reproduction, original-failures, fixed-inputs, fixed-inventory.csv, FAILURE_MATRIX.md |
| Gate A algorithm, patch, final physical decision | ALGORITHM_A.md, preimplementation receipts, gate-a.patch, source-stage-A1, gate-A-audit |
| Gate B remaining qualities/dispositions | GATE_B_DECISION.md, gate-B-characterization, retained trace JSONL |
| Independent homogeneous/coexistence references | independent-fixed-references, high-precision-references, precision-audit, reference-repeat-audit |
| Identical fixed inventory build comparisons | control-comparison, A1-comparison, fixed-comparison-summary, additional-inventories, additional-eos-audit |
| Inherited regressions and retained rejections | native matrices, inherited-focused-gate, regression-audit, shared callers, cache, lifecycle |
| Native/browser/A2 execution distinctions | gated-execution-status; unchanged B5/B4C browser evidence |
| Cost, iterations, caches and build identities | native-performance/progress, native-binaries, instrumentation, CMake cache/commands, source manifests |
| Plain-English explanation | MECHANICS_REPORT.md |

Before B5B, independently review the unresolved endpoint recovery and require
physical Q, stable/equilibrium branch selection at actual inventories, p/g/volume/
energy consistency and all original budgets across native and actual candidate
WASM/browser builds. B5B must separately preserve the seven guard failures,
exact rounded boundary signs and raw-versus-adapter distinction. No epsilon,
pressure rounding, support expansion or numerical-failure-as-domain-proof shortcut.

Before full A2 qualification, require both B5A physical gates plus focused
native/Chromium/WebKit regression and provenance checks, then the complete
original five-section option/controller/Jacobian, temporal/reference/event,
conservation, domain-stop/rollback and long-duration matrix under unchanged
contracts. Broader fluids and physical Safari/iPadOS need their own evidence.
Loader cleanup requires separate approval. No B5B, loader cleanup, full A2 or
Live Plant migration is begun. Stop for engineering review and explicit approval.
'''
(B/'ENGINEERING_REPORT.md').write_text(report)
(B/'MECHANICS_REPORT.md').write_text('''# 🔧 Ammonia Lab — The Mechanic’s Report

**PARTIAL REPAIR**

We fixed the demonstrated wrong decision for three valid liquid inventories.
The calculator had advanced its saturation calculation but was using properties
from the previous iteration to decide whether to solve liquid or mixture.
It sent those liquids into a mixture calculation, which then produced a negative
vapor fraction and correctly failed its quality check.

The experimental repair makes that DU decision use one consistent, sufficiently
refined saturation state. The original density and energy are unchanged. All
three resolved liquids now recover as stable liquid and satisfy the original
accuracy and energy checks. The earlier four backend corrections remain intact.

The tiny endpoint cases are still a separate problem. Three vapor examples
still calculate a fraction just above one and are refused. A fourth, near the
liquid endpoint, now returns a number but remains too close to the boundary for
the original reference checks to certify its physical phase. We have not called
that a physical success.

We did not trim a fraction to fit, replace an inventory with a saturated one,
force a vapor/liquid answer or weaken the validator. Two mathematical endpoint
references are equilibrium mixtures, so a blanket single-phase fallback would
be wrong. No defensible Gate B recovery was established under the unchanged
contract, and no Gate B source patch was made.

Native focused regressions pass their applicable checks. The browser candidate
and coupled five-section trials were not run after that scientific blocker.
The separate 35-bar browser guard issue and rejected-PT loader defect remain.
All original failures and exact inventories are retained for review.

This is an experimental partial repair, not a qualified backend or production
change. The accepted five-section model, UI, Live Plant and hosting are unchanged.
Work stops here for engineering review and explicit approval.
''')
summary=dict(assessment='PARTIAL REPAIR',branch='research/browser-eos-b5a-du-saturation-repair-20261016',startingCommit='e30ad9d76bc892aa355126339997d6184c8729d2',gateAImplementationCommit='b013448bc1005d9bb922c4420772b590180febd2',GateAApplicablePass=a['gateAApplicableChecksPass'],GateBPass=False,GateBPatch=None,physicalOriginalSuccesses=[r['key'] for r in resolved],originalUnresolved=[r['key'] for r in a['rows'] if r not in resolved],originalCurrentExceptions=[r['key'] for r in a['rows'] if 'error' in r['result']],allOriginalFailuresRetained=True,nativeRegressionsPass=reg['allApplicableNativeRegressionChecksPass'],browserCandidateExecuted=False,A2CompatibilityExecuted=False,backendQualified=False,B5BResolved=False,rejectedPTLoaderResolved=False,productionChanged=False,scientificBudgetsChanged=False,canonicalMaxResolved=maxcanon,nonlinearMaxResolved=maxnorm,patchSHA256=patchsha)
(E/'scientific-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)
