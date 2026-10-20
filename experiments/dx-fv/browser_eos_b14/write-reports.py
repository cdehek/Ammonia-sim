"""Generate engineering reports from retained B14 receipts; no solver execution."""
import json,statistics,csv,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(n):return json.loads((E/(n+'.json')).read_text())
def write(n,s):(B/n).write_text(s.strip()+'\n')
a=read('analysis');br=read('transition-bracket');event=br['event'];cold=a['fixtures']['cold'];warm=a['fixtures']['warm'];pins=read('source-preservation')['pins'];audit=read('source-preservation');tm=a['timing']
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |'for r in rows)
def fmt(v):return f'{v:.6g}'
colrows=[]
for i in range(21):
 row=[i,warm['columnTotals'][i]['label']]
 for f in ['cold','warm']:
  timings=[r['columnMS'][i]for r in tm[f]['observed']];c=a['fixtures'][f]['columnTotals'][i]
  row += [f'{statistics.median(timings):.2f} [{min(timings):.2f}, {max(timings):.2f}]',c['counts'].get('property.ph',0)]
 colrows.append(row)
columns_table=table(['Column','Coordinate','Cold ms median [range]','Cold PH calls','Warm ms median [range]','Warm PH calls'],colrows)
reject_table=table(['Start s','Trial s','Error max','Leading term','Next trial s'],[[fmt(r['startSeconds']),fmt(r['trialSeconds']),fmt(r['originalError']),r['leading'][0]['label'],fmt(r['proposal'])]for r in warm['rejections']])
resource=read('host-resources')
write('README.md',f'''
# B14-A0 — Phase-boundary temporal error and Jacobian cost

**B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS** — diagnostic research only, ready for engineering review. No optimization was implemented.

Baseline `{pins['B13']}`; branch `research/b14-phase-jacobian-diagnostics-20261019`. First design checkpoint `12dae83` preceded instrumentation. The final delivery SHA is the branch tip containing this report (`git rev-parse HEAD`) and is supplied in the delivery message; a commit cannot embed its own hash.

The original warm event is **superheated vapor → liquid + vapor**, cooling direction. The request's opposite direction is contradicted by the pinned original trace. Actual accepted bracket: **{event['bracketStartSeconds']:.17g}–{event['bracketEndSeconds']:.17g} s**, width {br['widthSeconds']*1e6:.3f} µs. Event {event['seconds']:.17g} s is interpolated, not root-solved.

The unchanged temporal estimator is a maximum over **31 scalar checks**, derived from 21 nonlinear coordinates. Extra trials reflect refrigerant inventory/pressure dynamics near a constitutive slope change and subsequent internal flow reversal; thermal errors do not lead. All original normal-fixture Newton solves converged with unit line searches and first positive derivatives. Original schedules reproduce B13 bit exactly through **0.01 s**; scientific qualification remains **0.001 s**.

Thermal Jacobian columns make zero PH calls because the existing stage cache works. Warm public PH calls: 17,416; 15,739 vapor calls each perform 38 bisections and 40 branch interpolations. The next proposed experiment is **exact pressure-bracket reuse inside a single vapor PH inversion**, with no cross-call cache and exact-or-reject gates. It is a proposal only.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [MECHANICS_REPORT.md](MECHANICS_REPORT.md), and [NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md](NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md). Detailed source, phase, estimator, scheduling, column, residual, PH, conservation, equivalence and limitations reports accompany machine-readable evidence.

## Reproduce and verify

From repository root:

```sh
python3 experiments/dx-fv/browser_eos_b14/audit.py
python3 experiments/dx-fv/browser_eos_b14/verify-protected.py
python3 experiments/dx-fv/browser_eos_b14/validate.py
# Optional fresh bounded replay, all outputs inside B14/.runtime, one process at a time:
python3 experiments/dx-fv/browser_eos_b14/campaign.py --repeats 1
# Three timing samples per original fixture require --repeats 3.
```

Node built-ins and Python standard library suffice for solves/audits; Matplotlib is required only for `plot.py`. `run.py --help` exposes individual bounded cases and refuses to overwrite receipts. `contracts.py` replays the separate domain witness and also refuses overwrite. Default outputs already exist; use a new B14 directory for replay (campaign handles this). No historical scripts that regenerate receipts are executed.

`receipts.mjs` resolves exact content references introduced by `compact.py`; repeated vectors are deduplicated only after exact verification. Canonical original/schedule traces and first observed detailed diagnostic vectors remain retained. `receipt-compaction.json` records transformations. Counts are stronger evidence than heavily instrumented submillisecond timings. No browser/Worker/Cloudflare testing or deployment occurred.
''')
write('SCIENTIFIC_SOURCE_AND_PROVENANCE.md',f'''
# Scientific sources and provenance

Observed Gate 0: exact detached B13 HEAD, clean worktree, then new isolated branch. All {audit['historicalFileCount']} B13 tracked files match their original Git blobs and SHA-256 inventory. No repository AGENTS.md was found. The starting B13 remote branch is exact. `audit.py` asserts ancestry and directory confinement.

{table(['Checkpoint','Commit'],pins.items())}

The fourteen-file accepted A2 closure is copied historically under `browser_eos_backend/accepted` plus root `engine.js`/`properties.json`; the B9C accepted-source manifest identifies each snapshot, hash and pinned original path. Some current root research files differ historically from A2, so they are not used as substitutes. B14 imports the pinned B9C literal registry read-only and verifies its identity against the B9C Git object. The registry's control bundle is original A2; candidate adds the already accepted exact-input boundary PH cache. The diagnostic registry is a separately labeled observation-only derivative of that same candidate.

`source-preservation.json` verifies all fourteen files, candidate/control/diagnostic bundles and isolated B9C model. All {audit['b13SealedFiles']} files in the B13 delivery seal are checked without regeneration. B12's read-only verifier is imported with its output destination explicitly redirected to B14; its package ZIP identity, thirteen assets, source derivations and retained browser receipts pass. B12 source bytes, B9D bridge and original workstation are among the all-file Git-object audit.

`evidence/observation-only.patch` documents canonical B9C → observed source, including existing B9C observation hooks. `instrumentation-transformations.json` lists every additional unique-anchor replacement and transformed SHA-256. The complete scientific registry is generated only in memory / ignored `.runtime`, not maintained as an unauditable new scientific implementation. No tables, solver defaults or floating arithmetic expressions change.

Precise functions: `coupled-model.cjs:createCoupledModel` owns `trial`, `solveStage`, `evaluate`, `errorEstimate`, `commit`, `advance`, `record`; `time-control.cjs:estimate/factor/crossings`; `coupled-implicit.cjs:coupledNewton`; `implicit.cjs:solveLinear`; `engine.js:inverse/branch/pBracket/sat/statePT/statePX/stateMVU`; `thermodynamics.cjs:ph/recover`. Initial PH, M/U/V, fixed reservoirs and thermal config come from original `coupled-fixtures.cjs:fixture` and original geometry/network sources.

Runtime: Node 24.19.0 Linux x86_64, recorded V8/libm versions in `node-runtime.json`, OS/CPU/cgroup resources in `host-resources.json`. Same-runtime comparisons to retained Node B13 hashes pass at all seven checkpoints. No claim of browser-versus-Node bit identity is imposed; the pre-existing B13 Chromium difference remains protected.

Remote audit records 39 head/tag refs and PR #3: open, unmerged, base main `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`, head v0.5.5-stage-1 `d4422425750a1d3c4e432cc103ac42ead40b7cc6`. Before/after identity fields agree. Only the new B14 branch may be pushed. No merge, tag move, deployment, browser installation or remote Worker test is part of B14.
''')
write('WARM_PHASE_TRANSITION_RECONSTRUCTION.md',f'''
# Warm phase transition reconstruction

Observed direction is **superheated vapor into liquid–vapor equilibrium**, in section index 0. It is not the opposite transition proposed in the mission wording. Original B13 and original B9C scientific traces agree exactly on the event and direction; no classification has been changed.

## Actual accepted bracket

{table(['Quantity','Left accepted state','Right accepted state'],[
['Time s',f"{br['acceptedStates'][0]['seconds']:.17g}",f"{br['acceptedStates'][1]['seconds']:.17g}"],
['Phase','Superheated vapor','Liquid + vapor'],
['Pressure bar absolute','3.536724628731566','3.5366027162082014'],
['Recovered enthalpy kJ/kg','1601.9251351171029','1601.7448627836231'],
['Recovered temperature K','268.12791881582734','268.07815267859576'],
['Quality','undefined (null)','0.9999595758797615'],
['Physical superheat K','0.04888194962404668','not a superheated state'],
['Mass kg','0.0017258764979199356','0.001726297263493033'],
['Internal energy kJ','2.5525214644916754','2.5528916104649'],
['Fixed volume m³','0.0006000000000000001','0.0006000000000000001'],
['Tube 0 temperature K','293.13970590341154','293.1396353195192'],
['Fin 0 temperature K','293.14999041334556','293.1499903079286'],
['Air temperature K','293.151243181539','293.1512484926965']])}

The bracket width is {br['widthSeconds']:.17g} s (22.911 µs). The original interpolated event is {event['seconds']:.17g} s. It linearly weights signed h−hg between accepted half endpoints. The event is not a new accepted state and is not a precision root. Floating additions of half steps and outer accepted intervals can differ in their last time bit; receipts retain original values without rounding them into equality.

`accepted-warm.json` contains every actual accepted half piece, all five conserved M/U/V inventories, eleven thermal energies/capacities/temperatures, recovered properties and original accepted PH states, saturation references, endpoint and integrated hydraulic/thermal rates, signed ledger, conservation audits, and section-wise changes. `transition-bracket.json` extracts the bracket. `temporal-warm.json` links attempts, accept/reject, original error and controller proposals. No output requests were added to the canonical schedule merely to observe these states.

## Inventory and transport interpretation

Over the bracket, section 0 mass increases by 4.207655730974289e-7 kg and U increases by 0.00037014597322482246 kJ, while specific h and temperature decrease. This is consistent with lower-enthalpy feed and changing inventory, not a loss of conserved energy. The fixed inlet is 4 bar absolute / 500 kJ/kg. At the left endpoint its signed transport is +0.014907647 kg/s / +7.45382349 kW. Face 1 is negative: −0.003703384 kg/s / −6.10415490 kW, so its donor is section 1 and it supplies energy to section 0. Tube-to-refrigerant heat is positive, about 3.00141445 kW. At the right endpoint those values are +0.014909608 kg/s / +7.45480419 kW, −0.002852126 kg/s / −4.70105291 kW, and +3.00737792 kW. Ledger integration, not endpoint-rate × time approximations, closes each balance.

Tube and fin energies are conserved thermal coordinates relative to the original 273.15 K anchor; temperatures are derived with each capacity. Tube 0 energy is 19.470533261688175 → 19.47046451100065 kJ, fin 0 is 16.984026834518538 → 16.984026744998257 kJ, finite air is 86.16535562607002 → 86.16537850653644 kJ. Original record energy references are retained separately. Neither p/h/T nor quality is a conserved coordinate.

Canonical M/U/V recovery and the implicit PH representation are separately retained: at the left endpoint recovered h differs from PH-coordinate h by about 5.2e-8 kJ/kg within the original recovery tolerance. Event left/right values use original PH coordinates (0.12753262334285864 and −0.05172204394148139 kJ/kg), not the separately recovered h. Both representations classify these endpoints identically.

## Constitutive regularity and solver behavior

At the left pressure, offline original-engine PH probes give dT/dh ≈0 on the mixture side and ≈0.38329 K/(kJ/kg) on the vapor side; dρ/dh ≈−0.00223865 versus −0.0053264 (kg/m³)/(kJ/kg). This is a measured slope change. Zero-offset vapor table rows agree with saturation rows; direct original `statePT(p,Tsat)` h and density match saturation bit exactly at the independently checked pressure. There is no evidence of a macroscopic value jump here. Piecewise interpolation has derivative changes, plus the original 1e-8 classification band and finite inversion precision; B14 leaves all intact. This is local evidence, not a proof of global table smoothness.

All 306 warm Newton solves converge, all 867 recorded line searches accept factor 1, and all 18,207 derivatives use the first positive probe. No normal domain probe fails. The event bracket therefore does not diagnose Newton failure.

An independently observed face-1 flow reversal lies in [0.005382038521211082, 0.005397063933720186] s, after entry to the mixture. The last rejected trial spans it. The donor rule switches there and the pressure gradient is small. These dynamics and the phase slope change jointly support a local accuracy burden; their individual causal shares are not isolated. See `hydraulic-transition.json` and [the figure](figures/warm-transition.png). Connecting lines are visual guides, not additional accepted states.
''')
write('TEMPORAL_ERROR_DECOMPOSITION.md',f'''
# Temporal-error decomposition

Observed: every reconstructed original aggregate equals its captured binary64 value exactly. The coupled nonlinear vector has 21 entries (P/H alternating for five sections, ten tube/fin increments and one finite-air increment); the temporal estimator tests **31** scalars. Inventing a 21-vector RMS would give a different acceptance rule.

For each section and each q ∈ M,U,P,H:

`term = abs(fine.q - coarse.q) / 3 / (absolute_q + rtol * max(abs(initial.q), abs(fine.q)))`.

For each thermal node:

`term = abs(Efine - Ecoarse) / 3 / capacity / (temperatureAbsoluteK + rtol * temperatureScaleK)`.

The final error is the maximum of all 31 terms. Operations retain original division order; there is no sum, RMS or norm weighting. `coarse` is the full TR-BDF2 trial, `fine` the endpoint of the second half trial; the first half endpoint supplies its initial inventory. The fine half pieces are committed without extrapolation. Initial P/H are recovered through the unchanged coordinate expression, not substituted from a rounded record.

Original settings include rtol 1e-6, M absolute 1e-11 kg, U absolute 1e-8 kJ, P absolute 1e-6 bar, h absolute 1e-4 kJ/kg, temperature absolute 1e-4 K plus 1e-6×50 K = 0.00015 K. The thermal Newton residual's separate 1e-12 K budget is unchanged and must not be confused with this temporal budget.

`temporal-cold.json` and `temporal-warm.json` retain all 31 initial/coarse/fine/difference/scale/normalized terms per attempt, phase arrays, original error, reason, original next proposal and captured accepted controller decision. The raw observed receipts additionally retain complete coarse/fine stage result objects. `controller-*.json` proves every rejected proposal matches the next actual trial bit exactly. Accepted controller proposals and installed nextStep are copied after the original decision; no hook modifies them.

## Observed contributors

Cold startup: section 0 U leads (initial rejected error 1.1122008032464925, M0 1.0739736506845754); all 17 cold trials are led by U0. Warm startup: section 4 U leads all 20 startup trials; initial rejected error 23.96490890435499, followed by P4 22.472884120582982 and M4 21.973118158527274. Subsequent startup rejections are 4.054196684874863 and 1.5807514032212349. These occur at t=0 while all warm sections are vapor; they cannot be attributed to the later phase crossing.

Near 0.005 s, U0 and U1 dominate, with strong M/P contributions. All five late rejections:

{reject_table}

The table also retains the three startup rejections for context. For the largest late error, U0 coarse/fine differ by −0.00041909988638533235 kJ with scale 2.5646744403986444e-6 kJ; division by 3 gives error 54.47083650380577. For the first late rejection U1 difference is +0.00024865981961719186 kJ against scale 2.4202304467561004e-6. These are real discrepancies in the two numerical predictions, not just a pressure scaling artifact.

A pre-transition retry at t=.005, dt=.0003362166821386039 stays entirely vapor at its endpoints and has max error .03585462835163402. Crossing attempts from .005336216682138604 have errors 54.47, 3.813, 3.524, then .971364 on the accepted 45.821839 µs interval. The last 39.327598 µs rejected trial starts after both coarse and fine section-0 endpoints are mixture; U1 error is 1.376511449620906. The accepted following interval is led by P1 at .425918. Endpoint phase equality does not mean the entire dynamics are smooth.

Thermal maxima are about 1.79e-5 in warm startup, .07449 across the broad transition attempts and 7.60e-5 post-transition. No thermal coordinate controls these rejections. Aggregate conservation error also remains tiny, so temporal prediction differences are not conservation leakage.

## Supported interpretation and limits

High confidence: the additional rejections are accuracy decisions driven mainly by refrigerant M/U/P differences, not Newton refusal, a thermal tolerance issue or a fabricated equipment alarm. Several independent variables agree, weakening a single-coordinate scaling explanation. Physical inventory transport and pressure equalization provide a strong transient; section 0 has a measured EOS slope change and the downstream face changes donor direction shortly afterward. Output clipping/growth affects which intervals encounter these changes.

Moderate confidence: the combination of constitutive non-smoothness and hydraulic redistribution explains the locally reduced useful step sizes. The final post-crossing rejection provides independent reason not to blame every late trial on phase classification alone. No experiment isolates an additive percentage for each mechanism. Pressure-table and superheat interpolation knots can affect other intervals; their complete global attribution is unresolved.

Hypothesis not established: the original estimator is overly conservative, poorly scaled or needs replacement. Bisection temperature interval width is ~9.09e-10 K, far below the .00015 K temporal scale; it does not alone explain observed O(1–54) inventory errors. No tolerance or method change, event root solve, or adaptive-controller refinement is authorized here.
''')
write('OUTPUT_BOUNDARY_SENSITIVITY.md',f'''
# Requested output boundary sensitivity

Three distinct warm integration trajectories use the identical original model, reservoirs, tables and numerical settings, all bounded to 0–0.01 s. Every schedule has a canonical uninstrumented and an observed replay; exact scientific/decision/Jacobian comparisons pass within its own schedule.

Original B13 requests: .0001, .0005, .001, .002, .005, .01 s. Added schedule inserts .00525 and .0055. Fine schedule inserts .0051, .0052, .0053, .0054, .0055, .0056. No setting, minStep, retry, stage, signed probe, eventStep or convergence tolerance changes. Boundary clipping is actual numerical segmentation and is not a pure observation call.

{table(['Schedule','Accepted physical halves','Rejected trials','Interpolated event s','Final max tolerance ratio'],[['original',86,8,fmt(event['seconds']),'reference']]+[[r['schedule'],r['acceptedPhysicalSubsteps'],r['rejected'],f"{r['events'][0]['seconds']:.17g}",fmt(r['comparisons'][-1]['maximumToleranceRatio'])]for r in a['boundaries']])}

At common requested times (0, .0001, .0005, .001, .002, .005, .01), differences in M/U/P/H are divided by the original absolute+relative scales, using max magnitude of the two compared states. Thermal differences are divided by capacity and the original .00015 K scale. For this **comparison only**, maximum ratio <=1 is a stated sensitivity criterion. There is no step-doubling divisor in this between-trajectory comparison. This diagnostic criterion does not replace the original solver's tolerance or qualify either trajectory.

Both schedules are exactly identical through .005 s. At .01, the added trajectory's maximum is .09274604145 (section 1 M difference +1.47427221e-10 kg). The fine trajectory's max is .23923652252 (M1 +3.80285566e-10 kg); U1 differs +5.26685075e-7 kJ, P0 +6.11135749e-7 bar, and U0 +4.11484011e-7 kJ. Full coordinate comparisons are retained in `analysis.json:boundaries`.

All accepted half states pass independent conservation audits: max combined errors 1.41501082e-10 and 1.61447633e-10 kJ. No failure/refusal, extra retry strategy or unsupported state occurred. Their brackets are [.005362130816122282,.00538042006543758] and [.005371654811139449,.005386134121015835] s. The event times differ by fractions of a microsecond, smaller than any accepted bracket width; none is a root-solved truth.

Observed rejection counts vary 8→7→5, confirming boundary/controller sensitivity. They do not improve monotonically in final distance from the original trajectory. Additional partitions are not a formal convergence proof or an established optimal output cadence. Common final-state differences are small under declared scales, but no long-duration accuracy, global order or equipment qualification follows.
''')
write('JACOBIAN_COLUMN_COST_ANALYSIS.md',f'''
# Jacobian column cost

Observed original schedule: cold 235 Jacobians / 4,935 derivative residuals; warm 867 / 18,207. Each build uses all 21 finite-difference columns. Every normal derivative uses first positive sign, shrink=0; no branch fallback, failed probe, skipped residual or optional exact column occurs. Full original residuals and actual numerical matrix hashes match canonical reconstruction exactly.

Perturbations remain P: `1e-7*max(1,abs(P))` bar; H: `1e-8*max(1,abs(h))` kJ/kg; thermal E: `capacityKJK*1e-6` kJ. The difference quotient divides by selected signed step, exactly as original, not by recomputed actual floating displacement. Raw original events preserve epsilon, selected step, actual displacement, sign, shrink, base and derivative residuals. `columns-*.json` gives ranges/counts and each detailed observed receipt associates per-column counts/times with stage and trial. Repeated runs retain compact column totals after equivalence verification.

{columns_table}

Timings are inclusive wall ms summed over that column across the entire run, n=3 separate processes. They include original derivative residual assembly, property work, original event recording and B14 accounting; ranges are empirical, not confidence intervals. Strong timing overhead means these are not exclusive production cost estimates. See [limitations](PERFORMANCE_MEASUREMENT_LIMITATIONS.md) and [figure](figures/jacobian-columns.png).

## What the counts establish

Each thermal column causes 235 cold / 867 warm residual evaluations and five cache hits per residual, with **zero section misses, zero PH calls and zero branch interpolations**. All eleven thermal columns together cause 2,585 cold / 9,537 warm derivative residuals and 12,925 / 47,685 section cache hits. Hydraulic faces and fluid inventories are nevertheless rebuilt with unchanged PH; thermal-rate networks and scaled residuals are recomputed for every probe.

P/H columns cause 2,350 / 8,670 derivative residuals, with 2,318 / 8,606 PH misses. Most probes need one section property; shared stage-cache keys also reuse identical PH across sections during the uniform initial iterations. This explains four fewer cold and eight fewer warm misses in columns 2–9 than their build counts. It is expected shared exact-pair reuse within the original stage, not an asymmetric derivative rule. Section 0 always misses on its own probes; after its transition, fewer of those misses invoke vapor inversion (23,360 branch operations per column, versus 34,360 for each other warm P/H column).

Median aggregate P/H column time across processes: cold 111.31 ms, warm 587.73 ms. Median thermal-column total: cold 84.90 ms, warm 218.27 ms. Thus individual P/H columns are typically more expensive, especially warm; thermal columns are numerous and still substantial through assembly. Thermal columns are not the PH cost center. No stable scientific column-order slowdown beyond these counts is established by noisy short timing samples.

The inclusive Jacobian timer starts after the original 21×21 array allocation and contains B14's actual-matrix hashing before the end timer. Matrix hashing is expensive observation work and is not the scientific finite-difference cost. Do not interpret the difference between Jacobian and summed column envelopes as original allocation time or exclusive overhead.
''')
write('RESIDUAL_ASSEMBLY_AND_ALLOCATION.md',f'''
# Residual assembly and allocation

The original Newton workload decomposes exactly into:

{table(['Fixture','Initial stage residuals','Derivative residuals','Line-search residuals','Total'],[['cold',102,4935,235,5272],['warm',306,18207,867,19380]])}

All line searches succeed at factor 1; none of this normal workload is wasted on failed nonlinear probes. Accuracy rejection still spends complete coarse/two-half stage work. The original stage closure builds states from exact PH keys, inventories from EOS density/enthalpy, thermal energies, endpoint rates, weighted integrated rates, then 21 scaled conservative residuals.

## Inclusive observed scopes

{table(['Scope','Cold ms median [range]','Warm ms median [range]'],[[scope]+[f"{statistics.median([r['scopesMS'][scope]for r in tm[f]['observed']]):.2f} [{min(r['scopesMS'][scope]for r in tm[f]['observed']):.2f}, {max(r['scopesMS'][scope]for r in tm[f]['observed']):.2f}]"for f in ['cold','warm']]for scope in ['residual','evaluate','property.ph','property.stateMVU','linear']])}

`evaluate` includes hydraulic and thermal-rate assembly and any boundary property calls; it is not an isolated array-allocation timer. Residual includes evaluate, section property/cache work, inventory assembly, blend, original diagnostics and B14 timers/counters. Property scopes nest inside residual/Jacobian; stateMVU recovery also occurs outside residuals. These rows cannot be summed or subtracted into exclusive CPU buckets.

## Demonstrably repeated construction

Source inspection establishes at least six selected array-producing sites per residual: states map, cells map, energies map, fluid flatMap, thermal map, final concat. That is at least **31,632 cold / 116,280 warm source-level array constructions** before counting nested map/flatMap pair arrays, blend term arrays, rate arrays, returned objects or the Jacobian. Every residual also calls evaluate and constructs a fresh thermal-node index Map from the same topology, plus temporary key arrays. At least 5,272 / 19,380 such Map constructions occur in residuals. Section string keys are constructed five times per residual even on hits. Counts describe JS operations; JIT escape analysis can change actual heap allocations.

On thermal probes PH is unchanged, so original fluid inventory objects and hydraulic faces are recomputed from unchanged inputs. All 9,537 warm thermal probes have zero PH misses, yet still traverse the six hydraulic connections and fifteen thermal links. This proves repeated constitutive assembly under identical fluid inputs. It does not authorize skipping it or prove its exclusive runtime.

`trial` calls evaluate twice on identical initial states/energies, once for the outward thermal-domain check and once for the initial TR-BDF2 rate. The table engine also repeatedly brackets the same pressure inside one PH inversion. These are independent observed/source-supported opportunities, with different proof and ownership concerns. Existing stage/boundary caches are preserved exactly; none of these computations was reused by B14.

## Allocation/GC attribution limit

No allocation profiler or causal GC attribution was run. Process max RSS, heap snapshots at completion and CPU totals are resource bounds, not bytes per residual. Original trace recording and B14 copied vectors, exact encodings, hash arrays and PH repeat maps add their own allocation and can trigger GC. JIT worker CPU also contributes. **The amount of wall time consumed by original temporary arrays/objects, and whether original allocation/GC is a material bottleneck, remain unmeasured.** No percentage or speculative precision is assigned. Counts and exact equivalence justify a candidate investigation, not a claimed optimization speedup.
''')
write('PH_INVERSION_COST_ANALYSIS.md',f'''
# PH inversion cost

Original B13 workload reproduces exactly after subtracting initialization measured separately: cold **5,028 PH / 8,400 branch interpolations**; warm **17,416 PH / 703,306 branch interpolations**. All supported normal PH probes succeed. B14 did not change table inversion, stopping rules, classification, cache ownership or support.

## Necessary original algorithmic work

Warm 15,739 public PH calls return superheated vapor; 1,677 return liquid + vapor. Every vapor PH inversion executes a bound-check branch, exactly 38 bisection branch evaluations, then one final statePT branch: **40 branch interpolations per call**, 629,560 total and 598,082 bisection iterations. Remaining 73,746 warm branch calls arise from canonical stored M/U/V recovery rather than public PH. Cold has 210 vapor PH calls (predominantly its fixed outlet), producing all 8,400 branches; 4,818 mixture PH calls need none. These counts come from original functions plus contextual counters; no iteration termination was approximated.

`branch` independently brackets superheat/subcool offset and pressure, and interpolates h/s/log-density from original rows. In a vapor PH inversion all 40 branch calls have the **same exact p**, while trial offset varies. Each repeats `Math.log(p)` and pressure-axis binary search and allocates bracket results. This establishes repeated invariant pressure-location work, not repeated identical thermodynamic states. The 38 variable-offset evaluations remain necessary to the authorized algorithm. The count does not establish how much of PH CPU is pressure search versus interpolation/log/exp.

Warm derivative columns contain 8,606 PH calls: 8,040 vapor calls →321,600 branch operations and 566 mixture calls →0. Pressure/enthalpy perturbations change exact inputs and cannot be treated as approximate cache hits. Thermal columns make no PH calls. Per-column counts and per-phase/context totals are in `columns-warm.json`, `analysis.json:fixtures.warm.ph`; observer-index PH bins are provided only as interval context and include record/commit calls between attempt observers, not exclusive trial scopes.

## Current cache effectiveness

Warm section requests 96,900: 82,461 hits / 14,439 misses (85.10%). Cold 26,360: 22,373 / 3,987 (84.87%). Original stage-owned shared exact-pair map explains both thermal hits and uniform-section reuse. Warm stage boundary requests are 38,760, with 612 misses (two per 306 stages) and 38,148 hits. Including nonstage trial/record calls gives 39,384 requests / 1,236 misses. Cold equivalent totals are 10,760 requests / 420 misses / 10,340 hits. Trial/record calls intentionally retain the original uncached path. These figures demonstrate expected B9C cache benefit without adding cross-stage reuse.

An observational exact binary64 input map over the entire run finds 12,501 distinct warm PH pairs in 17,431 initialization-inclusive calls: 4,930 calls repeat a prior pair; cold 3,427 distinct / 5,043 calls, 1,616 repeats. This map returns no properties and changes no cache. Warm fixed inlet and outlet each appear 620 times including initialization; each is seen across 307 observer stage indices. Many identical accepted coordinates recur during error estimation, phase checking and commit/record generation. Cross-stage/input repetition is not automatically safely reusable: spec identity, property ownership, support failures and returned-object aliasing still require proof.

## Conditioning and near-saturation cost

Mixture PH is inexpensive direct interpolation; vapor PH has the full fixed 38-iteration cost even arbitrarily close to saturation. Across the accepted section-0 boundary, density and temperature slopes change as documented in `constitutive-probes.json`, but iteration count does not increase. Public PH costs decrease for section 0 once it becomes mixture. Thus expensive warm PH is primarily **many vapor-side fixed-loop calls**, not an observed inversion convergence failure or extra iteration surge exactly at the event.

Bisection interval width is 250/2^38 ≈9.09e-10 K. It remains unaltered; the original classification tolerance band and p/h coupling are also retained. Local zero-offset table continuity passes; complete global conditioning and interpolation-knot influence are not characterized. No new thermodynamic engine, approximate cache, quantization, extrapolation or CoolProp path is introduced.

Observed PH timing median is about 618 ms warm (615–650) and 51.8 ms cold (50.7–53.6), n=3 diagnostic processes, including instrumentation and initialization. Protected B13's lighter public PH timing (~475.6 ms warm) is not overwritten or equated to these measurements. Short timing and observer costs limit precise CPU attribution.

## Opportunity assessment

The clearest bounded opportunity is **reuse of the pressure interpolation bracket only within one vapor PH inversion**. It targets 40 repeated pressure-location operations per vapor call while preserving the 38 bisections, offset lookups, branch interpolation arithmetic and final property calculation. Savings are bounded above by affected PH time; their actual fraction is unmeasured. The next proposal requires exact science/failure equality before any speed comparison. No such optimization has been implemented here.
''')
write('CONSERVATION_AND_ROLLBACK.md',f'''
# Conservation and rollback

PASS: every canonical output record and every retained accepted half-state in both primary fixtures and both alternate schedules passes the original mass <1e-8 kg / energy <1e-6 kJ budgets. Independent thermal closure reconstructs each node from signed air/tube/fin link ledgers and imposed air load. Donor energy transport is independently checked against flow sign and original donor enthalpy. No new tolerance is introduced.

{table(['Maximum absolute closure','Cold','Warm'],[[k,fmt(cold['auditMax'][k]),fmt(warm['auditMax'][k])]for k in cold['auditMax']])}

These maxima cover all accepted half states, not just requested outputs. Warm combined maximum 1.56176e-10 kJ can therefore exceed the protected B13 requested-output summary (~1.50e-10) without contradiction. Cold combined max remains ~6.32489e-12 kJ. Section mass and energy budgets, global refrigerant U, eleven-node storage, air-side 1 kW imposed load and combined coil energy all pass. Constant section volumes and global inventory are retained from the exact original states.

Ledger equations independently used: section mass change = left-face mass − right-face mass; section U change = left donor-enthalpy transport − right transport + tube heat. Thermal storage change = imposed air load − tube-to-refrigerant transfer globally, with link signs checked independently for each node. Combined energy eliminates internal tube exchange. Negative face flow uses the right donor; no unsigned-flow reinterpretation occurs. Changes in section 0 h/T at the event occur while its M and U both increase, without creating or losing inventory.

## Atomic accepted progress and domain refusal

`domain-and-rollback.json.gz` replays original B13's separately labeled sealed, zero-exchange 200 K fixture. It accepts 0.0001 s, applies the original scheduled −1 kW air load, and confirms an outward derivative at the exact thermal support boundary. The resulting **genuine domain refusal** retains earlier accepted time and inventories. Original A2, original B9C and the observed source match bit exactly for state, record, full attempt diagnostics, stop/evidence and partial accepted progress. Repeated advance after stop is unchanged; invalid inlet update p=.29 bar rolls back exactly. The witness requests .0002 s but actual committed horizon is .0001 s.

The original advance prepares both half pieces against detached ledgers/events before atomically installing them. B14 copies these prepared pieces but counts them as accepted only for completed trials whose original acceptance trace and final state are verified. No rejected candidate becomes an accepted diagnostic state. All original normal-fixture rejection decisions are temporal accuracy, not this domain witness.

## External termination

A deliberately labeled 1 s wall-budget canonical warm witness is killed as an entire process group. Exit −9 / `timedOut:true` is external supervision, not a solver stop or physical fault. Its last requested checkpoint is .0001 s; its last independently observed accepted snapshot is .0004911886098445242 s. Every retained partial snapshot is bit-exact against the corresponding canonical full run (`external-budget-validation.json`). No state after that snapshot is claimed; the pending trial is not accepted by the receipt. No retry was made. This independently preserves B13's distinction between budget exhaustion and numerical/domain refusal.

No numerical rejection becomes a plant alarm. Terminal bulk wet describes a model state, not compressor liquid carryover safety. This fixture is one evaporator with artificial fixed reservoirs, uncalibrated conductances and no compressor safety measurement.
''')
write('INSTRUMENTATION_EQUIVALENCE.md',f'''
# Instrumentation equivalence

**PASS for all completed scientific pairs.** Same Node runtime, fixture, options and requested schedule reproduce original state/record and original attempt hashes exactly. Canonical original schedule also reproduces every saved B13 hash at 0, .0001, .0005, .001, .002, .005, .01 s for both fixtures. Original A2 control and B9C match exactly at the four accepted baseline checkpoints.

`verify.mjs` independently recomputes exact encodings, compares complete states/records (including M/U/V, eleven energies, ledgers, trace, rejections, growth controller, phase events, time and stop), and compares full original attempts including every derivative residual. JSON drops explicitly undefined iteration contexts, so those original undefined keys are restored before recomputing attempt hashes. No numerical tolerance is used for these comparisons.

Actual observed Jacobians are hashed before `solveLinear`. Independently, the verifier reconstructs each canonical matrix from original base-iteration residual and each selected derivative residual divided by its original signed step. All 235 cold and 867 warm matrices match. Alternate schedules' own matrices also match their paired canonical runs. Matrix verification therefore covers numerical results beyond merely matching final output.

The estimator capture hook copies original coarse/fine results and initial conserved coordinates after the unchanged error is calculated. Offline reconstruction retains original expression ordering and equals each aggregate bit exactly. Controller hooks copy installed proposals; all rejected proposals reconstruct and match the following trial exactly. Original events are neither augmented nor reordered. Additional counters/vectors live outside scientific objects.

## Transformations and boundaries

B14 starts from pinned `diagnostic-candidate-bundle.mjs`, which itself differs from canonical only by the separately documented B9C observations. Existing hooks count lexical sat/branch/inverse/MVU, public properties, section hits and boundary calls, and time evaluate/trial/stage/record. B14 adds unique-anchor hooks for each column, actual matrix hash, detached temporal vectors, prepared accepted half pieces and installed controllers. Module-export wrappers time Newton/residual and linear solve while returning unchanged objects. No optional exact thermal Jacobian mode is enabled.

`instrumentation-transformations.json` retains base and transformed SHA-256 plus every replacement; `observation-only.patch` shows the full diff from canonical. An identity replacement for `errorEstimate` is only a fail-closed anchor verification, not a scientific edit. All expression operands and returned values are unchanged. Hook errors are not silently accepted: measured normal runs hit no observation limits or errors.

A development attempt `observed-cold-r1` failed closed on a nonunique source anchor **before initialization or any solve**. Its empty trace and exit receipt are retained. The anchor was narrowed to the commit/applyBoundary context, then `observed-cold-r1-fixed` passed all gates. This is a harness-construction error, not a scientific refusal or an equivalent measurement. The cold first sample predates addition of an aggregate PH observer-index counter; that counter adds no source/science changes and timing ranges include this minor observer variation. All profiles share the same transformed scientific registry hash.

The original uninstrumented run still uses its original optional attempt observer and trace settings, matching B13; 'uninstrumented' means no B14 transformation/timers. This common original observation overhead is part of both runs. True no-observer production throughput is not measured.

## Initialization, timing and compaction

Separate no-advance initialization measurements identify 15 initial PH calls in each fixture. These explain initialization-inclusive totals of 5,043 / 17,431 versus advance totals 5,028 / 17,416. The raw hook label `initialization` means **unscoped property context**, also covering error/commit operations outside trial/record; it must not all be subtracted as construction cost. Only the separately measured initialization counts are subtracted. Other timing scopes retain initialization where applicable and are labeled accordingly.

Instrumentation increases advance wall time median by about 90% cold / 49% warm. Counts and exact traces remain valid; measured subscopes include instrumentation. Timing inequality is expected and disclosed, numerical inequality is rejected.

Receipts are compacted only after equivalence. Canonical content is referenced by name/time/hash; repeat full estimator/commit vectors are omitted after matching science and actual matrix hashes. First-sample vectors and all canonical schedule traces remain. `receipts.mjs` resolves references and final verification reruns comparisons. `receipt-compaction.json` records pre/post byte counts and hashes. No historical B13 evidence is rewritten.
''')
write('PERFORMANCE_MEASUREMENT_LIMITATIONS.md',f'''
# Performance methodology and limitations

Sequential processes, same machine/runtime, original fixture schedules, n=3 canonical and n=3 detailed diagnostic measurements per fixture. Alternate schedules each use one canonical/observed pair for numerical sensitivity, not throughput statistics. No concurrent heavy profiling solves run. A short offline analysis overlapped one sensitivity process; **all sensitivity timings are excluded from the three-sample performance summary**. Counts/science remain exactly verified.

{table(['Fixture','Canonical advance wall median [range] ms','Observed advance wall median [range] ms','Median ratio'],[[f,f"{tm[f]['canonicalWallMS']['median']:.2f} [{tm[f]['canonicalWallMS']['min']:.2f}, {tm[f]['canonicalWallMS']['max']:.2f}]",f"{tm[f]['observedWallMS']['median']:.2f} [{tm[f]['observedWallMS']['min']:.2f}, {tm[f]['observedWallMS']['max']:.2f}]",f"{tm[f]['medianOverheadRatio']:.3f}"]for f in ['cold','warm']])}

Wall time sums six advance calls, including original record/observer work within advance, excludes later checkpoint hashing/serialization, initialization, module import and supervisor compression. Process receipts separately include serialization and gzip in supervisor wall time; do not compare that to solver time. CPU includes user+system CPU across process threads; it may exceed wall time on this two-CPU-quota host. Raw per-run wall/CPU, construction and resource data are retained. CPU and wall are not interchangeable.

Inclusive scopes overlap: Jacobian contains derivative residual/property work; residual contains evaluate; evaluate contains hydraulic/thermal and boundary properties; public PH contains inverse/branch. Counts of lexical branch work also include MVU recovery outside PH. Original diagnostics and B14 counter/map/clone/hash work can execute inside timers. Matrix hashing is explicitly inside the Jacobian timing envelope. Hook overhead is nonuniform across scopes, so dividing each observed scope by canonical time would be invalid. No additive pie chart or percentages summing to 100% are presented.

Public property timers include PH input tracking and result accounting, not only unwrapped engine code. Per-column timings include all instrumented residual work. Branch and PH counts give stronger algorithmic evidence than extrapolating these timer shares. No exclusive CPU percentage for pressure binary search, interpolation, allocation or GC is measured. PH observer-index bins include calls between attempts and are contextual, not causal intervals.

Short samples have JIT warmup, process startup, scheduler and GC noise. n=3 median/range is descriptive; it is not a statistical confidence interval or a desktop benchmark. Warm first-sample MVU timing is an outlier (137.7 versus about 68–69 ms) and is retained rather than discarded. Instrumentation wall overhead is large; no optimization speedup or real-time factor for desktop production is claimed.

Host: Linux x86_64 Xeon Platinum 8573C; 3 visible logical CPUs, quota 2; cgroup memory 8 GiB. Each solve has 40 s wall / CPU budget, process group and explicit kill, 512 MiB V8 old-space, 64 MiB output-file limit, no core dumps and capped attempts/columns/commits/input-map observations. Heap cap is not RSS cap: code, external buffers and runtime overhead remain outside V8 old space. The host cgroup provides the overall memory bound. All normal cases complete well within budgets; no bound was silently increased. Maximum normal per-run supervisor wall time was under 8 s.

The deliberate 1 s timeout is separately labeled external-budget evidence, never a scientific refusal. Failed unique-anchor construction has no scientific sample. The campaign does not repeat B13's full historical validation or run a physical horizon >.01 s. No browser installation, device run, public Worker call or deployment occurred.

Future desktop Chrome/Edge profiling on ordinary Windows/macOS remains necessary. B12 remains the known-good reference. Owner-observed iPad .5–1 s initialization/disposal feedback is useful responsiveness evidence but cannot benchmark solver throughput.
''')
write('QUALIFICATION_GAPS.md','''
# Qualification gaps and unresolved questions

B14 is an observation-only diagnostic pass, not new scientific qualification. Accepted A2 qualification remains **0.001 s**. Actual explored original and sensitivity trajectories reach **0.01 s**, explicitly UNQUALIFIED RESEARCH. No .1 s, one-second or long-duration plant trajectory is authorized or run.

Observed facts: exact B13 reproduction, event bracket and cooling direction, component maximum error contributions, per-column workload/cache behavior, fixed vapor PH inversion work, independent conservation and refusal/rollback equality. Supported deduction: phase-side slope changes and adjacent hydraulic redistribution create a local refrigerant accuracy burden; output segmentation affects trial history.

Unknowns requiring independent work:

- Individual causal shares of phase constitutive kinks, hydraulic reversal, other table knots, temporal estimator/controller response and output clipping. No counterfactual modified-science experiment isolates them here.
- True error against a more accurate independently qualified trajectory; extra outputs are not a convergence proof. The event is interpolated, with accepted-time uncertainty, not a root.
- Full property conditioning over the bounded domain, all interpolation knots and all failure regimes. Local table continuity does not establish global smoothness.
- Exclusive PH pressure-bracket CPU share, original bytes allocated per residual, GC causal cost, JIT allocation elimination and any realized optimization saving.
- Windows/macOS desktop Chrome/Edge solver throughput, memory and UI responsiveness. Current Linux Node performance cannot substitute for these measurements; historical cross-runtime bit differences remain.
- Calibration of heat transfer, geometry, flow and finite-air mixing; dynamic reservoirs and complete refrigeration plant behavior; long-duration stability and credible equipment operation.
- Terminal wet bulk state versus actual compressor carryover; no safety inference from the terminal diagnostic alone.

No tolerance relaxation, new backend, alternative integrator, state adjustment, domain widening or production feature is justified by these diagnostics. Any optimization must have separate authorization and exact science/failure gates; if binary64 decisions change it is no longer an exact-equivalence optimization and must stop for engineering qualification.
''')
write('NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md','''
# Exactly one recommended next experiment

**Recommend a narrowly scoped prototype of exact pressure-bracket reuse within a single vapor PH inversion.** Authorization is requested in the next milestone, not exercised by B14.

## Why this first

Warm 15,739 vapor PH calls each execute 40 branch interpolations, totaling 629,560 repeated pressure-location operations with unchanged p inside their own call. Source confirms every branch calls pBracket(p), repeating log(p), pressure-axis binary search and bracket-result construction. PH is a measured substantial inclusive scope (diagnostic median ~618 ms), while original B13 independently measured ~475.6 ms. The pressure-location fraction is unmeasured; neither value is promised savings. This identifies exact invariant work with a natural single-call owner, avoiding decisions about sharing across sections/stages/spec changes.

The candidate must preserve all 38 bisections, every offset lookup, interpolation operation/order, statePT/thermodynamic outputs, classification band, table/support bounds and exception behavior. A pressure bracket can be reused only after its original successful validation and only for the same exact p and owned immutable table during that inversion. No persistent cache, approximate match, quantization, table change, new stopping criterion or new backend is permitted by this proposal. Do not hoist calculations past domain checks or change refusal ordering. The ordinary two-phase path must remain untouched. This is an implementation plan for future review, not code in B14.

## Ranked candidates

| Rank | Candidate | Measured opportunity | Equivalence/proof and complexity | Phase/decision/conservation/refusal risk | Rollback |
|---|---|---|---|---|---|
| 1 | Single-inversion exact pressure-bracket reuse (D/C) | 40 repeated pressure searches per warm vapor PH; exact savings unknown within PH envelope | High likelihood of bit equality if all branch arithmetic/order retained; moderate proof/implementation, owned tables and failures mandatory | Low expected phase/decision/conservation risk only after exact proof; exception ordering needs deliberate tests | One isolated helper/path, no persistent state |
| 2 | Residual assembly/allocation reduction (B) | 19,380 residuals; repeated arrays/Map construction, 9,537 thermal probes rebuild unchanged fluid assembly | High for invariant topology lookup, moderate for broad rewrites; exclusive allocation cost unknown | Reassociation or alias changes can alter decisions/ledger; medium failure-scope proof | Small isolated source diff |
| 3 | Optional original exact thermal Jacobian columns (A) | 9,537 warm residual probes, median thermal column envelope ~218 ms | Lower likelihood of bit equality: analytic derivative need not equal finite difference binary64; scientific qualification likely, implementation easy but proof hard | Moderate/high Newton path/acceptance risk; conservation needs requalification if results differ | Existing option is easy to disable |
| 4 | Broader exact-input reuse across call sites (C) | 4,930 repeated warm PH inputs including initialization | Moderate proof: ownership, mutable outputs, changing spec, failed probes, stage lifetime; implementation moderate/high | Aliasing/stale cache could affect phase/refusal and decisions; conservation risk follows | New state must be removable and invalidated |
| 5 | Estimator/refinement investigation (E) | Extra transition rejections and schedule sensitivity established | Further science is useful, but changing estimator has no exact-equivalence presumption; complex independent qualification | High acceptance/event/trajectory risk; no current evidence authorizes relaxing accuracy | Separate diagnostic/qualified branch |

Ranking weighs proof and reversibility alongside measured opportunity. Candidate A has a larger direct residual-count opportunity than the narrow chosen prototype, but expected binary64 derivative differences make it a poor first exact-equivalence experiment. Candidate B is plausible but original allocation cost is unresolved. Candidate E remains a qualification question; timing coincidence does not justify changing the controller.

## Proposed controlled protocol

1. Start from the completed B14 branch in a new isolated authorized directory/branch. Preserve all protected source/package/ref/PR audits. First commit a design and exact-input ownership argument.
2. Compare original versus prototype on pinned tables: two-phase states, vapor just outside the 1e-8 band, every relevant pressure/superheat boundary, invalid/support inputs, aliasing and mutation isolation. Validate exception type/message/evidence and order; do not silently convert a refusal to a cache hit.
3. Replay cold/warm original B13 schedules and the two B14 sensitivity schedules, still no longer than .01 s without new authorization. Require bit-exact PH outputs, residuals, Jacobians, every original attempt/controller decision, accepted M/U/V, thermal energies, records, events/ledgers and stops. Replay genuine domain refusal, invalid update and external termination semantics.
4. Any numerical or scientific decision mismatch rejects the prototype as an exact-equivalence optimization. Do not relax the gate or rewrite fixtures; return for separate scientific qualification.
5. Only after proof, use bounded sequential process measurements to estimate actual pressure-location saving with light counters and a no-timer control. Separate counts, CPU/wall, instrument overhead, allocation/GC and serialization. Minimum reproducibility samples, desktop Chrome/Edge assessment later.
6. Keep prototype opt-in and independently removable. No merge/deployment until engineering review and separate approval.

Success would be demonstrated identical science plus measured work reduction, not a promised speedup. If pressure search is too small to matter, report the negative result and retain the original engine.
''')
write('MECHANICS_REPORT.md','''
# Mechanics report

B14 explains why this research evaporator sometimes asks the computer to take a smaller time step. It does not add a control, alarm or solver feature, and it does not change the working B12 simulator.

In the warm example, the first section starts as superheated vapor. Near 0.005375 simulated seconds it enters the liquid-and-vapor region. This is the cooling direction, contrary to the initial question's assumed direction. We know it changes between two accepted times, 0.00535913 and 0.00538204 s. The displayed event time is an interpolation inside that interval.

Mass and total internal energy in that section both increase while its specific enthalpy and temperature fall. Low-enthalpy feed and changing flow explain why falling temperature does not mean energy disappeared. Tube heat still enters the refrigerant. Every signed mass/energy ledger stays within the original tight limits.

The solver checks one full trial against two half trials. If their predicted inventories or properties differ too much, it discards the trial and tries a shorter interval. Near the transition, refrigerant internal energy, mass and pressure drive those decisions. Metal/fin/air temperature errors do not. Internal flow between the first two sections also reverses shortly after the phase change. This helps explain why not every extra rejection is caused by crossing the phase label itself.

All ordinary warm Newton solves converge and all their line searches accept their first full correction. These time-step accuracy rejections are therefore not evidence of a broken nonlinear solver or a physical equipment fault. A separate test deliberately reaches the model's temperature support boundary; it stops honestly and preserves earlier accepted progress. A computer time-budget kill is recorded separately again.

The expensive Jacobian is built by slightly changing each of 21 coordinates and recalculating the residual. Thermal changes already reuse cached refrigerant properties correctly. Pressure/enthalpy changes need new properties. Superheated PH recovery makes 38 bisection iterations per call, even near saturation, and repeatedly locates the same pressure in the table. The recommended next experiment is to investigate reusing that pressure location within one call while preserving every calculation and answer. B14 implements none of it.

The longest research run is only 0.01 simulated seconds. The accepted qualified horizon remains 0.001 s. This is one modeled evaporator with artificial fixed reservoirs and uncalibrated heat transfer, not a commissioned refrigeration plant. A wet terminal bulk state does not measure compressor liquid carryover or establish a safety limit.

Future throughput assessment should use ordinary Windows/macOS desktops and Chrome/Edge. The owner's iPad startup/disposal feedback remains useful but cannot measure solver throughput. Production, PR #3, the original workstation and Cloudflare deployments are unchanged. Work stops for engineering review.
''')
write('ENGINEERING_REPORT.md',f'''
# B14-A0 engineering report

**B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS**

Scientific equivalence PASS. Baseline `{pins['B13']}`; isolated branch `research/b14-phase-jacobian-diagnostics-20261019`. Gate 0/design was committed first as `12dae83`. The final delivery SHA is the tip containing this report, reported in the delivery response and available with `git rev-parse HEAD`; self-embedding a final commit hash is not possible. All work is confined to `experiments/dx-fv/browser_eos_b14/`.

## Main diagnosis

The warm section-0 transition is **superheated vapor → liquid + vapor (cooling)**. Its accepted bracket is [{event['bracketStartSeconds']:.17g}, {event['bracketEndSeconds']:.17g}] s; {event['seconds']:.17g} s is the unchanged interpolated event. The opposite direction assumed in the request is not supported by the pinned evidence. Quality is null outside the valid mixture domain and is never extended into vapor as a fraction.

Original warm startup rejections are led by U4. The five late rejections are led in order by U1, U0, U1, U0, U1, with max errors 34.2474, 54.4708, 3.81319, 3.52410 and 1.37651. M/P also contribute strongly. Cold is led by U0. All 31 original temporal terms reconstruct bit exactly; the aggregation is a maximum, not a 21-coordinate RMS. Warm thermal terms peak below .075 and never lead rejection.

High-confidence cause category: refrigerant temporal-prediction error during rapid inventory/pressure dynamics. Measured saturation-side slope changes and a subsequent face-1 flow reversal support a combined local constitutive/hydraulic mechanism with **moderate confidence in causal attribution**, not a quantified partition. The final rejected trial starts in mixture and spans the flow reversal. Extra outputs change rejection count while conserving state, confirming segmentation/controller sensitivity. No Newton refusal or failed normal property probe occurs. Neither 'phase label alone' nor 'bad scaling alone' is an established explanation.

## Reproduced science and workload

{table(['Metric','Cold','Warm'],[['Actual research horizon s',.01,.01],['Accepted physical half-steps',32,86],['Accuracy-rejected trials',1,8],['TR-BDF2 stages',102,306],['Jacobian builds',235,867],['Residual evaluations',5272,19380],['Derivative residuals',4935,18207],['Public PH calls during advance',5028,17416],['Max combined closure over all accepted halves kJ',fmt(cold['auditMax']['combinedKJ']),fmt(warm['auditMax']['combinedKJ'])]])}

All original schedule states, conserved inventories, thermal energies, records, attempts, controller decisions, events/ledgers/stops and actual Jacobian hashes match canonical exactly. All seven checkpoints match saved B13; original A2 control matches the four qualified baseline checkpoints. Accepted scientific qualification remains **0.001 s**. No physical horizon >.01 s is explored.

## Column, residual and PH findings

Thermal columns make zero PH calls and all expected stage-cache hits; they still perform 9,537 warm residual evaluations. P/H derivative columns cause 8,606 warm PH calls and 321,600 vapor branch interpolations. Median aggregate column envelopes are 587.73 ms P/H versus 218.27 ms thermal (three heavily instrumented processes). Expected shared initial PH pairs explain the small per-column call-count asymmetry. No fallback/sign/shrink asymmetry appears.

Warm public PH has 15,739 vapor calls with 38 bisections and 40 branch interpolations each (629,560 branch operations); total warm branch count 703,306 also includes MVU recovery. Many pressure-location operations are identical within each call, while bisection offsets vary. Existing section cache hit rate is 85.10%; stage boundary cache misses exactly twice per stage. Thermal-column PH work has already been eliminated by accepted caching, so it is not the opportunity it might appear to be from coordinate count alone.

Residual inclusive median is ~1,031 ms warm, evaluate ~140 ms, PH ~618 ms, linear solve ~18.8 ms, with nested scopes and substantial measurement overhead. These are not additive CPU shares. At least 116,280 selected source-array constructions and 19,380 topology Map constructions occur in warm residual assembly; actual heap bytes/GC/exclusive allocation time are **unknown**. No claim that allocation is the bottleneck is made.

The proposed next experiment is exactly one: **single-inversion exact pressure-bracket reuse in vapor PH**, retaining 38 bisections and all thermodynamics/acceptance/failure semantics. Measured repeated work and a narrow owner make it a defensible first proof experiment. No optimization or speedup is implemented or claimed. Ranked alternatives and rejection gates are in `NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md`.

## Schedule, conservation and failure evidence

Added/fine output schedules produce 88/98 accepted physical halves and 7/5 rejections. At .01 s their max differences from original are .09275/.23924 of declared original tolerance scales, with all accepted-state conservation budgets satisfied. These are distinct numerical trajectories, not bit-identical schedules or convergence proof.

Global/section mass/U, signed hydraulics, donor-enthalpy transport, tube/fin/air storage, independent thermal-node closure, air load and combined energy pass original tolerances. Separate original A2/B9C/observed domain witness preserves committed .0001 s and exact rollback/refusal evidence. Deliberate external wall-budget termination retains the last independently proven accepted .0004911886098445242 s; it is neither a numerical refusal nor plant alarm.

## Performance and resources

Canonical advance wall median/range: cold 213.05 [205.87,239.85] ms; warm 1139.25 [1094.53,1158.26] ms. Detailed observer median: cold 404.63 ms (+89.9%), warm 1692.30 ms (+48.5%), n=3. Jacobian timing includes actual-matrix hashing; per-column/property scopes include accounting. Counts/exact traces are stronger evidence than original-cost attribution from these scopes. CPU, process wall, serialization and worker transport are distinct; no browser transport is measured.

Linux Node 24.19.0, 3 visible CPUs / quota 2, 8 GiB cgroup memory. Normal process budgets: 40 s wall/CPU, 512 MiB V8 old space, 64 MiB output, capped observation history, process-group kill and no core dump. All normal runs complete in under 8 s supervisor wall. No budget extension, unsupported normal case or conservation violation occurs. The unique-anchor construction failure is retained as a pre-solve harness error and excluded from scientific samples.

## Remaining uncertainty and protection

Causal shares of phase/hydraulic/interpolation/estimator effects, true converged error, exclusive pressure-bracket/array/GC CPU cost and future desktop browser performance remain unresolved. None blocks reporting these diagnostics, and none authorizes changing the model. Fixed artificial reservoirs and uncalibrated transfer remain; wet terminal state is not compressor safety evidence.

All {audit['historicalFileCount']} historical files, A2 closure, B9C/B9D, B12 source/package, B13 evidence and original workstation are unchanged. All 39 protected remote head/tag identities and PR #3 identity pass before/after audit. Only this B14 branch is authorized for push; no merge, production/main change, Cloudflare deployment or public Worker testing occurs. Publication is verified separately against the final branch SHA. **Stop for engineering review.**
''')
status={'milestone':'B14-A0','classification':'B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS','diagnosticOnly':True,'baselineSHA':pins['B13'],'branch':'research/b14-phase-jacobian-diagnostics-20261019','designCommit':'12dae83','finalCommitLocator':'git rev-parse research/b14-phase-jacobian-diagnostics-20261019; exact SHA in delivery response','scientificEquivalence':'PASS','exploredHorizonSeconds':.01,'acceptedQualifiedHorizonSeconds':.001,'phaseDirection':'superheated vapor to liquid + vapor; cooling','phaseBracketSeconds':[event['bracketStartSeconds'],event['bracketEndSeconds']],'interpolatedEventSeconds':event['seconds'],'gates':{g:'PASS'for g in ['0','A','B','C','D','E','F','G','H']},'unresolved':['causal partition of coupled dynamics','exclusive pressure-bracket CPU fraction','original allocation/GC attribution','formal convergence and long-duration qualification','desktop browser performance'],'nextExperiment':'exact pressure-bracket reuse only within one vapor PH inversion','optimizationImplemented':False,'merge':False,'deployment':False,'engineeringReview':'AWAITING'}
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
with (B/'milestone-status.csv').open('w',newline='')as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['milestone','gate','status','scope']);w.writerows([['B14-A0',k,v,'diagnostic only; horizon <=0.01 s']for k,v in status['gates'].items()])
print('Wrote 15 final reports plus milestone trackers; original pre-instrumentation design retained')
