"""Generate review reports only from measured receipts and explicit evidence limits."""
import json,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';a=json.loads((E/'analysis.json').read_text());C=a['results']['cold'];W=a['results']['warm'];pins=json.loads((E/'source-preservation.json').read_text())['pins']
def write(name,text): (B/name).write_text(text.strip()+'\n')
def fmt(v):return f'{v:.4g}'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def measured(rows):return table(['Fixture','Actual t (s)','Accepted substeps','Rejected trials','Residuals','Newton corrections / Jacobians','TR-BDF2 stages'],[[f,fmt(r['seconds']),r['acceptedSubsteps'],r['rejectedTrials'],r['residuals'],r['corrections'],r['observed']['profile']['calls']['stage']] for f,r in rows])
common='All times above 0.001 s are UNQUALIFIED RESEARCH. No longer-duration scientific qualification is claimed.'
write('README.md',f'''# B13-A0 scientific horizon diagnostics

**B13-A0 DIAGNOSTIC CHARACTERIZATION PASS**

Exact B12 parent `{pins['B12']}`; new branch `research/b13-dx-fv-horizon-diagnostics-20261019`. All changes remain in this directory. No deployment, production merge, plant coupling, solver optimization, source change or tolerance relaxation.

{common}

{measured([('cold',C),('warm',W)])}

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md) for the decision, [SOLVER_PERFORMANCE_RESULTS.md](SOLVER_PERFORMANCE_RESULTS.md) for measured cost, [LONG_HORIZON_FEASIBILITY.md](LONG_HORIZON_FEASIBILITY.md) for conditional cost projections, and [NEXT_SOLVER_MILESTONE_PROPOSAL.md](NEXT_SOLVER_MILESTONE_PROPOSAL.md) for the next investigation. The owner-reported B12 commissioning retrospective is separate from instrumented evidence.

Reproduction from repository root (Python 3.12, Node 24.19.0; standard library only except optional figures):

```sh
python3 experiments/dx-fv/browser_eos_b13/audit.py
python3 experiments/dx-fv/browser_eos_b13/run.py --fixture cold --horizon 0.001 --name review-cold-baseline.jsonl.gz
node experiments/dx-fv/browser_eos_b13/verify-results.mjs
python3 experiments/dx-fv/browser_eos_b13/analyze.py
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b13/contracts.mjs
python3 experiments/dx-fv/browser_eos_b13/plot.py
python3 experiments/dx-fv/browser_eos_b13/write-reports.py
```

Wrap contracts in `timeout 30` as in the recorded run. Use fresh receipt names; `run.py` refuses overwrite. Select each next horizon only after reviewing the earlier result under [HORIZON_PROBE_PROTOCOL.md](HORIZON_PROBE_PROTOCOL.md). The runner never chooses a longer horizon. Canonical three-replicate full probes use the sequence 0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01 s. `--variant observed` selects separate measurement code, `--variant control` selects original accepted A2 with unchanged settings.

`evidence/analysis.json` contains interval tables, phase events, convergence distributions, profiles, physical records and projections. Raw complete JSON lines are retained in compressed receipts. `scienceExact` preserves binary64 state/record bits. Each checkpoint's `attemptsHash` covers the original full cumulative diagnostic stream; the verifier restores the original undefined iteration-context field omitted by JSON and independently recomputes all canonical science/attempt hashes. To avoid committing repeated identical scientific payloads, `compact.py` verified their hashes and exact state encodings before replacing them with explicit references to canonical r1 checkpoints; independent timings, counters, CPU/memory samples and observed profiles remain in each run. `analyze.py` and `verify-results.mjs` resolve these references. Both canonical r1 receipts retain the full diagnostic streams. `receipt-deduplication.json` records the operation. No runtime/browser cache is tracked.

Node measurements are from a managed Linux VM, not a desktop Chrome/Edge benchmark or an owner-device test. Preserved B12 deployment is established by the owner's report and unchanged package/source bytes; B13 does not independently inspect the private deployment.

Stop for engineering review after the authorized research-branch push. Milestone status is in `milestone-status.json`.
''')
write('ENGINEERING_REPORT.md',f'''# Engineering decision

**B13-A0 DIAGNOSTIC CHARACTERIZATION PASS**

The accepted five-section fixture advanced to an actually observed 0.01 s in both cold and warm cases, in three independent canonical processes plus a diagnostic replay for each. {common} Horizon progression stops here because the A0 characterization is sufficient; no 0.1 s, 1 s, 10 s, 60 s or one-hour solve was attempted.

{measured([('cold',C),('warm',W)])}

Accepted A2 integrity: unchanged fourteen-file source closure, protected B9C bundle identity, all historical B12 tracked bytes and portable assets verified. Fresh original-A2, B9C and instrumented B9C state/record/attempt hashes agree bit exactly at 0, 0.0001, 0.0005 and 0.001 s in Node 24. Canonical repetitions and diagnostic replay also agree through 0.01 s. Retained Chromium 151 receipts are revalidated but differ from Node binary64 results; cross-version/browser equality is not asserted.

Bottleneck ranking depends on fixture. Jacobian construction accounts for about 61% (cold) and 60% (warm) of instrumented advance wall time, including its residual/property work. All public thermodynamic calls account for about 19% and 57%, respectively. Warm PH inversion alone is about 49%. These overlap: property work is mostly inside residuals and Jacobians. Linear algebra is about 6%/2%, respectively. Finite-difference residual assembly and warm vapor-property inversion are demonstrated costs; worker/UI transport is not timed by this harness and is not assigned solver time.

Median total advance cost for the measured 0.01 s is {fmt(C['timingReplicates']['medianSecondsWallPerSimSecond'])} wall seconds per accepted simulated second cold and {fmt(W['timingReplicates']['medianSecondsWallPerSimSecond'])} warm. This ratio includes startup, accepted diagnostic allocation, record generation, sparse progress output and runtime overhead. Recent-window rates differ strongly, so these are measured local throughput ratios, not steady-state forecasts. CPU includes V8 background/JIT threads and can exceed wall time.

Conservation: maximum sampled global mass residuals are {C['conservation']['massResidualKg']:.3g} kg cold / {W['conservation']['massResidualKg']:.3g} kg warm. Maximum sampled combined-energy residuals are {C['conservation']['combinedEnergyResidualKJ']:.3g} / {W['conservation']['combinedEnergyResidualKJ']:.3g} kJ. Section/node closures pass the preserved audits. No normal-fixture numerical/domain stop or property exception occurred.

All observed normal-fixture rejections were temporal accuracy rejections. Newton converged in 2–5 corrections per stage cold and 2–7 warm, with every recorded line search accepting factor 1 and every derivative using its first positive probe. The failure-aware nonlinear growth ceiling never activated. Warm section 0 crosses the vapor boundary near 0.00537543 s and incurs five further accuracy rejections in the last interval; this challenges duration extrapolation without demonstrating Newton instability or a physical equipment fault.

A separate sealed, zero-exchange, exact-200 K support-boundary witness commits 0.0001 s of an initial 0.0002 s request, then refuses outward thermal motion with confirmed domain evidence. Earlier progress survives; no current rejected state leaks; stopped repeats and invalid boundary updates preserve physical state. Original A2/B9C contracts agree bit exactly. It is a contract witness, not normal-fixture behavior.

Performance projection confidence: strong for work counts and repeatability at these output boundaries; limited for component-time percentages (one detailed replay, nested probes and JIT noise); low for 0.1 s; unsupported as physical-success predictions for 1–3600 s. The current fixture has fixed pressure/enthalpy reservoirs, uncalibrated hydraulic/heat-transfer inputs and no complete refrigeration loop.

Recommended next investigation: bounded phase-boundary temporal-error and Jacobian/residual decomposition, with independent equivalence gates before any optimization. Keep worker computation and desktop-first review. No production or deployed assets change. Stop for review.
''')
write('SCIENTIFIC_BASELINE_AND_PROVENANCE.md',f'''# Scientific baseline and provenance

The clean starting checkout was detached at exact B12 `{pins['B12']}` and matched `origin/research/b12-private-https-ipad-preview-20261019` before creating the new isolated branch. No repository AGENTS.md files were found. `evidence/local-refs-before.txt`, `remote-refs-before.txt`, and `pr3-before.json` preserve pre-implementation identities. No remote mutation is authorized except pushing the new B13 branch.

{table(['Protected reference','Commit'],pins.items())}

`audit.py` reads every tracked B12 blob through Git and compares its bytes with the working tree. `evidence/historical-files.json` retains blob IDs, SHA-256 and byte counts; `source-preservation.json` records the fourteen-file accepted A2 closure, including original thermodynamic tables. Snapshot sources match protected A2 blobs exactly. Root research files that historically differed from A2 are not silently used: the pinned bundle contains the accepted closure.

B9C `candidate-bundle.mjs`, `diagnostic-candidate-bundle.mjs`, original-A2 `control-bundle.mjs` and isolated model match their protected Git blobs. B11's deployed science copy is byte-identical to the B9C candidate. B11 portable ZIP/assets and original workstation source derivations are checked by the read-only B12 verifier, with output redirected into B13. Retained Chromium/WebKit receipts and training exports are revalidated, not regenerated or overwritten.

Fresh Node comparisons establish bit-exact original-A2 ↔ B9C ↔ diagnostic B9C equality at the four accepted checkpoints. Three canonical 0.01 s runs and the observed replay have exact checkpoint and cumulative attempt hashes. Settings match B9D's `trace:true,timestepGrowth:'failure-aware'`; no tolerance, minStep, iteration or attempt budget changes. `thermalJacobian` remains its original default finite differences, not the optional exact mode.

Retained browser comparison: all eight Node-versus-Chromium state/record comparisons differ at the binary64 level. A cold initial density witness is Chromium `4033d96d03316dda` versus Node `4033d96d03316dd9`; initial total mass differs accordingly. Different engine versions/math implementations are a plausible explanation, not an isolated proven cause. This pre-existing runtime difference is already present with original A2 and does not arise from B13 instrumentation. Same-engine equality remains mandatory and passes. No fresh browser parity or personal-device benchmark is claimed.

PR #3 baseline: open/unmerged; base `main` at `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`; head `v0.5.5-stage-1` at `d4422425750a1d3c4e432cc103ac42ead40b7cc6`. The before/after audit compares these plus state/draft/repository identities. The owner reports B12 as deployed; private hosted assets were not inspected or modified.
''')
write('MECHANICS_REPORT.md',f'''# Mechanics and reproducibility

`probe.mjs` imports the pinned read-only B9C registry, constructs its owned frozen original-table engine and five-section model, and advances explicit requested intervals. `run.py` owns process wall/CPU/file/heap budgets and records exit status independently of solver status. `contracts.mjs` exercises genuine support-domain refusal without changing numerical settings. `audit.py`, `verify-results.mjs`, `analyze.py`, `plot.py`, `compact.py` and this generator are B13-only tools.

Observed mode imports the historical diagnostic bundle from an in-memory data URL after two exact single-occurrence timing insertions around the existing Jacobian loop. Export wrappers are installed before the coupled modules capture linear/Newton exports. The existing diagnostic hooks count stages, trials, evaluations, properties and cache hits. Instrumentation does not change coordinates, tolerances, residual values, property implementation or step controller. Full science/attempt hashes prove decisions unchanged in the measured runs; timing noise is assessed separately.

Nested scopes include property, residual, Jacobian, Newton, TR-BDF2 stage, trial, evaluate and record. Jacobian includes its residual/property calls. Residual includes endpoint evaluation and property work. Public property categories are disjoint from each other at the public-call layer; lexical counts include nested work. Remaining time cannot be assigned wholly to adaptive control: it includes recovery, records, diagnostics, object allocation, garbage collection and runtime scheduling.

The managed host reports AMD EPYC 9V74, three visible logical CPUs, cgroup quota equivalent to two CPUs and an 8 GiB memory cgroup. The scientific solve is synchronous JavaScript; V8 may use background threads. Node is 24.19.0 on Linux x86_64. Timing samples are cold processes with JIT warmup inside the short probe. No browser renderer or worker transport is involved. Owner-reported iPad latency is recorded separately.

Receipt write time outside `model.advance` is excluded from advance wall/CPU samples but included in process wall. Sparse partial-state writes inside the observer are measured by `observerMS`. Diagnostic event generation inside the accepted solver remains included. End-checkpoint RSS/heap values include serialization, repeated exact encoding and retained event arrays; they are not a minimal solver working set.

All complete scientific payload duplicates are explicitly referenced after hash/bit checks. Canonical r1 raw streams remain self-contained. JSON decimal events retain the full original attempt hashes. JSON omits the original iteration event's explicitly undefined `context` on iterations after zero; `verify-results.mjs` restores that one known original field before recomputing all fourteen canonical cumulative attempt hashes. Every hash matches, including numerical bits. No guessed numerical values are inserted; state/record additionally retain explicit binary64 tags. Incomplete termination streams may end with a truncated line; the process supervisor parses only complete JSON lines. A missing complete record is not replaced with stale readings.

Re-run with fresh output names. Analysis and report scripts intentionally regenerate their B13 products. No historical builder, browser setup, Cloudflare CLI or deployment command is run. No screenshots or private access details are stored.
''')
write('TIME_STEP_AND_CONVERGENCE_ANALYSIS.md',f'''# Adaptive time steps and convergence

{common}

The original TR-BDF2 adaptive trial computes one coarse step and two half steps, each with two implicit stages. Accepted adaptive trials commit two physical substeps; attempted coarse states never become accepted states. Rejected trials consume all six stages here because rejection occurred after successful solves during temporal-error estimation.

{measured([('cold',C),('warm',W)])}

{table(['Fixture','Attempted dt range (s)','Accepted physical half-step range (s)','Next proposed dt (s)'],[[f,f"{r['minAttemptSeconds']:.6g}–{r['maxAttemptSeconds']:.6g}",f"{r['minAcceptedSubstepSeconds']:.6g}–{r['maxAcceptedSubstepSeconds']:.6g}",fmt(r['nextStepSeconds'])] for f,r in [('cold',C),('warm',W)]])}

Cold rejects its initial 0.0001 s trial at normalized temporal error 1.1122, then completes with no further rejection. Warm rejects initial trials at errors 23.9649, 4.0542 and 1.58075. Near the subsequent vapor crossing, errors reach 54.4708 and require additional subdivision. The smallest warm trial is an output-boundary remainder; minimum dt alone is not evidence of physical stiffness. The final physical state is supported and has no stop.

Newton corrections per stage:

{table(['Fixture','Corrections : stage count'],[[f,str(r['newtonIterationHistogram'])] for f,r in [('cold',C),('warm',W)]])}

Every recorded derivative is used at shrink 0 and positive sign; signed fallback capability remains unchanged but is not exercised by these normal-fixture runs. All recorded line searches accept factor 1. No Newton iteration-budget exhaustion, line-search refusal, branch-rejected derivative or failed constitutive probe occurs. Warm has more stages/iterations and expensive vapor PH inversions, not a demonstrated nonlinear failure ceiling.

Original controller proposal is `dt * clamp(0.85 * error^(-1/3), 0.1, accepted ? 2 : 0.8)`, capped at maxStep and output/event boundaries; zero error proposes factor 2. Failure-aware nonlinear history is unchanged and records zero nonlinear failures. Warm phase crossing resets growth history once. `state.trace`, `rejectionTrace`, `growthHistory` and per-attempt diagnostics retain every observed proposal input and retry. The next attempted duration, target remainder and nextStepSeconds distinguish growth from output clipping.

![Adaptive steps](figures/adaptive-steps.svg)

The event timestamp is a linear interpolation inside a committed bracket, not a precisely root-solved physical transition. No event causes an invented equipment alarm. Detailed interval tables are in `evidence/analysis.json` and SOLVER_PERFORMANCE_RESULTS.md.
''')
# Profile tables
profileRows=[]
for f,r in [('cold',C),('warm',W)]:
 p=r['observed']['profile'];ms=p['ms'];wall=r['observed']['totalAdvanceWallMS']
 profileRows.append([f,p['calls']['property.ph'],p['calls']['property.stateMVU'],p['calls']['property.sat'],fmt(ms['property.ph']),fmt(ms['property.stateMVU']),fmt(ms['property.sat']),fmt(sum(v for k,v in ms.items() if k.startswith('property.'))/wall*100)+'%'])
write('PROPERTY_EVALUATION_PROFILE.md',f'''# Original-table property workload

No EOS substitution, new thermodynamics or table adjustment is used. Counts/times below exclude initialization and include six advance calls plus their records. They come from one observed replay per fixture; all canonical science/attempt hashes match.

{table(['Fixture','PH calls','M/U/V recovery calls','Public sat calls','PH ms','Recovery ms','Sat ms','Public property share'],profileRows)}

Lexical counts cold/warm: saturation 18,924 / 61,259; inverse 5,028 / 17,416; branch interpolation 8,400 / 703,306. These are nested internal counts, not extra public calls. Warm PH inversion repeatedly traverses the original vapor table's iterative inverse; average branch work is much higher than in the wet cold fixture. Lexical counts support attribution, while public timing establishes measured cost. Recovery also includes nested inverse work and is not free.

{table(['Fixture','Section requests','Section hits / misses','Boundary requests','Boundary hits / misses'],[[f,p['section']['requests'],str(p['section']['hits'])+' / '+str(p['section']['misses']),p['boundary']['requests'],str(p['boundary']['hits'])+' / '+str(p['boundary']['misses'])] for f,r in [('cold',C),('warm',W)] for p in [r['observed']['profile']]])}

Stage-local section caching already avoids many repeated PH evaluations during unchanged-coordinate probes. B9C exact-input boundary caching also avoids most boundary requests. Boundary misses outside implicit stages include required original trial/record evaluations; hit percentages are not a proposal to cache across changed inputs or stages. No failed public property call was observed in either normal probe. Warm phase transition remains supported by the original table in this experiment.

Thermodynamics is a major warm cost (about 57% of observed wall time); it is only about 19% cold. Therefore “property evaluation alone limits all simulation” is not supported. PH timing includes wrappers and runtime effects; repeated fresh production/browser measurements are required before quantifying an optimization opportunity. Replacing inverse results or changing stopping criteria could change science and is not authorized.
''')
write('JACOBIAN_AND_TRBDF2_PROFILE.md',f'''# Jacobian, Newton and TR-BDF2 cost

Original coupled state: ten refrigerant P/H coordinates used to solve conserved M/U/V balances, plus eleven thermal-energy increments. The accepted 21-coordinate formulation, signed finite differences, Newton tolerances and TR-BDF2 arithmetic remain unchanged. Neither thermal exact-column mode nor Jacobian reuse is enabled.

{table(['Fixture','Trials','TR-BDF2 stages','Jacobians','Residual evaluations','Jacobian ms','All residual ms','Linear ms'],[[f,r['observed']['profile']['calls']['trial'],r['observed']['profile']['calls']['stage'],r['jacobianBuilds'],r['residuals'],fmt(r['observed']['profile']['ms']['jacobian']),fmt(r['observed']['profile']['ms']['residual']),fmt(r['observed']['profile']['ms']['linear'])] for f,r in [('cold',C),('warm',W)]])}

Each observed correction builds all 21 finite-difference columns and solves one 21×21 linear system. Derivative calls are exactly 21×235 = 4,935 cold and 21×867 = 18,207 warm. Residual counts close as initial-stage evaluations + 21 derivatives/correction + one accepted line-search evaluation/correction: 102 + 22×235 = 5,272; 306 + 22×867 = 19,380. This explains the measured workload without assuming a hidden linear-algebra bottleneck.

Jacobian timing includes residual and property time, but excludes the subsequent linear solve. It is about 61%/60% of observed advance wall; all residuals are about 66%/80%. Public property timing overlaps these scopes. The linear systems are about 6%/2%. Newton stage totals and complete nested scopes are in `analysis.json`; the rest includes recovery, adaptive error checks, commit/record work, diagnostics, allocation and runtime effects.

![Component costs](figures/component-profile.svg)

TR-BDF2 work multiplies nonlinear stages: every adaptive trial here completes six stages, including each of the rejected coarse/fine comparisons. Cold performs 102 stages for 16 accepted adaptive trials plus one rejected trial; warm performs 306 for 43 accepted trials plus eight rejected trials. These counts demonstrate the architectural expense of adaptive step doubling; they do not authorize replacing the integrator or error estimator.

A future equivalence study could separate object/array allocation from constitutive arithmetic in residuals, evaluate existing exact thermal columns under strict identity gates, and inspect vapor inverse repeat work. No speedup is promised until equivalent residuals, Jacobians, decisions and conservation are demonstrated. Faster linear algebra is a low-priority hypothesis on current evidence.
''')
# Physical and conservation reports
domainRows=[]
for f,r in [('cold',C),('warm',W)]:
 for row in r['propertyRangesByInterval'][1:]:
  ph=row['ranges']['ph'];recovery=row['ranges']['stateMVU']
  domainRows.append([f,fmt(row['seconds']),f"{ph['min']['p']:.6g}–{ph['max']['p']:.6g}",f"{ph['min']['T']+273.15:.6g}–{ph['max']['T']+273.15:.6g}",f"{recovery['min']['p']:.6g}–{recovery['max']['p']:.6g}",f"{recovery['min']['T']+273.15:.6g}–{recovery['max']['T']+273.15:.6g}",', '.join(ph['phase'])])
physicalRows=[]
for f,r in [('cold',C),('warm',W)]:
 initial=r['initialRecord'];final=r['finalRecord']
 physicalRows.append([f,fmt(initial['totals']['massKg']),fmt(final['totals']['massKg']),fmt(final['ledger']['boundaryMassKg']),fmt(final['ledger']['boundaryEnthalpyKJ']),fmt(sum(final['ledger']['tubeRefrigerantKJ']))])
write('PHYSICAL_DOMAIN_AND_PHASE_ANALYSIS.md',f'''# Physical-domain and phase analysis

{common}

The fixture has five fixed refrigerant control volumes totaling 0.003 m³, with original mass/internal-energy/volume state and P/H nonlinear coordinates. Tube/fin/finite-air storage adds eleven thermal nodes. The illustrative 20 mm bore corresponds to about 9.55 m of tube. These are research inputs, not equipment calibration.

{table(['Fixture','Initial inventory kg','Final inventory kg','Boundary Δmass kg','Boundary enthalpy kJ','Tube→fluid heat kJ'],physicalRows)}

Cold inventory changes from 0.05954796 to 0.05954394 kg; all sections remain liquid–vapor mixture. At 0.01 s, pressure decreases spatially from about 3.51005 to 3.50371 bar and enthalpy from 500.579 to 500.555 kJ/kg. Quality spans about 0.13995–0.14008. Refrigerant temperature spans about 267.839–267.885 K.

Warm inventory changes from 0.00817275 to 0.00807025 kg. All sections start superheated; section 0 becomes two phase while the remaining four stay superheated. At 0.01 s, pressure spans about 3.50977–3.52133 bar and enthalpy about 1566.14–1649.79 kJ/kg; section 0 quality is about 0.972244. Section 0 crosses the vapor saturation boundary at interpolated t=0.0053754278 s in bracket [0.0053591276, 0.0053820385] s. This is supported in the measured trajectory; it does not qualify general phase-transition dynamics.

Supported public PH pressure is 0.3–35 bar. Superheated support ends at 250 K above saturation; subcooled support depends on populated liquid-table temperatures. The thermal-node domain is [200,400] K. No property/domain refusal occurred in the normal fixtures. A second diagnostic replay records successful public property pressure, enthalpy, temperature and quality ranges for each tested interval, separately for PH, M/U/V recovery and saturation; `T` is original engine °C, so add 273.15 for kelvin. Phase histograms count property results, not physical time or inventory. These include boundary states and nonlinear probe states and therefore exceed the physical-cell range. See `propertyRangesByInterval` in `evidence/analysis.json` for every interval. The range replay's exact state/attempt hashes match canonical; range-accounting overhead is included in the primary observed cost profile.

Successful public-property call envelopes per interval ending at the listed time (PH includes fixed boundary donors and Newton probes; recovery includes committed and stage candidate states):

{table(['Fixture','Interval end s','PH pressure bar','PH temperature K','Recovery pressure bar','Recovery temperature K','PH phase labels'],domainRows)}

Tube/fin storage is active. Cold tubes lose roughly 0.006 kJ each while fins gain about 0.008735 kJ each; finite air loses 0.03557 kJ despite receiving 0.01 kJ external load. Warm tubes lose about 0.00752–0.02398 kJ each; the air gains about 0.009988 kJ while feeding small net heat to solids. Signed link and tube–refrigerant ledgers close with these changes. Air is a fixed-volume, fixed-mass, perfectly mixed energy node; no ventilation or air-pressure dynamics are coupled.

Boundaries are fixed inlet 4 bar / 500 kJ/kg and outlet 3.5 bar / 1700 kJ/kg reservoirs, with the original signed donor-enthalpy transport. The actual outlet energy uses the internal donor under forward flow. Fixed pressures and hydraulic loss coefficients determine flow; there is no valve/controller response to refrigerant inventory. The warm initial pressure mismatch produces a large initial outflow transient. Constant uncalibrated tube-to-bulk conductance is 0.60 kW/K distributed over sections; film/radial and phase-dependent transfer are unresolved.

The formulation is a credible conservation-based component research foundation: spatial pressure/enthalpy, liquid–vapor transition and solid/air energy storage are represented. It is not a complete refrigeration system. No scientific compressor, receiver, condenser, feed valve or plant control has been coupled. Slip/void dynamics, detailed boiling/dryout, oil, frost/defrost, distributor maldistribution and validated equipment correlations are absent. Manufacturer/measurement calibration, realistic reservoir dynamics and mesh/time convergence remain gaps.

Bulk wet indication is an equilibrium section diagnostic. It is not compressor suction protection; even a dry terminal reading would not establish a safe compressor inlet. Missing plant coupling limits physical interpretation independently of the observed numerical integration cost. Numerical accuracy rejections near the transition are not fabricated physical alarms.
''')
write('CONSERVATION_AND_ROLLBACK.md',f'''# Conservation, rollback and refusal

{table(['Maximum absolute sampled residual','Cold','Warm'],[[key,f"{C['conservation'][key]:.6g}",f"{W['conservation'][key]:.6g}"] for key in C['conservation']])}

Units are kg for mass and kJ for energy. These maxima cover the seven completed output checkpoints through 0.01 s; they are not claims about every arbitrary intermediate time. The original audit checks global and section mass, fluid energy, thermal energy, combined energy and each thermal node. It independently reconstructs signed air/tube/fin exchange from ledgers. Preserved audit limits are 1e-8 kg and 1e-6 kJ; B13 changes no acceptance tolerance. The actual residuals are far smaller. Maximum nonlinear residual and normalized temporal error satisfy their original acceptance limits at output records.

Canonical normal fixtures end at 0.01 s with `stop:null`. Rejected coarse/fine trials never commit their candidate inventories or ledgers. Both accepted half-step commits are prepared against detached ledgers/events before installing the accepted trial. Earlier accepted adaptive trials within a multi-trial advance remain committed if a later trial stops. “Whole request rolled back” would be false in that situation.

Fresh contract witness: a sealed, zero-refrigerant-exchange fixture starts all thermal nodes at exactly 200 K with zero load. A scheduled -1 kW air load at 0.0001 s points out of the original supported domain. The request is 0.0002 s; actual committed progress is 0.0001 s. The original solver retries then returns a confirmed thermal-domain refusal at that accepted time. The evidence identifies node/stage/outward direction, retains the last physical state and stop, and preserves exact M/U/V, thermal energies and ledgers from before the refused motion. Repeating advance on the stopped state is unchanged. Invalid inlet p=0.29 bar update refuses before changing live state. Original-A2 and B9C witnesses agree bit exactly. See `evidence/domain-and-rollback.json`.

The separate one-second CPU-budget run is an external termination, not a solver/domain refusal. The supervisor retains its last complete output and sparse accepted-state progress observations, which may be later than that output. The incomplete pending trial is not labeled accepted. See `budget-termination-warm-010.jsonl.exit.json`; `timedOut:false` means the CPU signal arrived before the parent's wall-time kill, not that the solve completed. No accepted partial progress is discarded or described as a request-wide rollback.

No state clipping, artificial convergence, altered conservation, remapped property failure, illustrative-physics fallback or equipment alarm is introduced. No genuine normal-fixture numerical refusal occurred by 0.01 s, so such a refusal is not fabricated for this report. The separate original C1 regression receipt remains retained historical evidence; B13 does not claim a fresh general fault-injection campaign.
''')
performance=[]
for f,r in [('cold',C),('warm',W)]:
 for x in r['intervals']:performance.append([f,f"{x['start']:.4g}→{x['end']:.4g}",fmt(x['requested']),fmt(x['actual']),fmt(x['wallMS']),fmt(x['cpuMS']),x['acceptedSubsteps'],x['rejectedTrials'],x['residuals'],x['corrections']])
write('SOLVER_PERFORMANCE_RESULTS.md',f'''# Measured solver performance

{common}

Representative canonical r1 interval receipts (wall/CPU in milliseconds):

{table(['Fixture','Accepted interval s','Requested Δt','Actual Δt','Wall ms','CPU ms','Substeps','Rejects','Residuals','Corrections'],performance)}

{table(['Fixture','Three total advance wall samples ms','Median wall s / simulated s','Median CPU s / simulated s','Observed profile / median canonical'],[[f,', '.join(fmt(v) for v in r['timingReplicates']['totalAdvanceWallMS']),fmt(r['timingReplicates']['medianSecondsWallPerSimSecond']),fmt(r['timingReplicates']['medianCPUSecondsPerSimSecond']),fmt(r['timingReplicates']['observedOverCanonicalMedian'])] for f,r in [('cold',C),('warm',W)]])}

Ratios are measured total advance time divided by 0.01 accepted physical seconds. They are not repeated-one-second benchmark measurements. The 0.005→0.01 s interval costs {', '.join(fmt(v) for v in C['timingReplicates']['lastIntervalSecondsWallPerSimSecond'])} wall s/s cold and {', '.join(fmt(v) for v in W['timingReplicates']['lastIntervalSecondsWallPerSimSecond'])} warm. Output clipping, initialization dynamics and JIT warmup make whole-probe and late-window rates differ substantially. All three runs have identical scientific work counts and state/attempt hashes.

Canonical advance includes original accepted diagnostic generation, commit/record and sparse observer progress output. Observer callbacks cost {fmt(C['observerMS'])} ms cold and {fmt(W['observerMS'])} ms warm in representative r1. Construction, table import and full receipt encoding/compression are excluded from advance timing. Whole child/supervisor execution takes much longer because the research stream serializes full states and many diagnostic events. Do not present that serialization cost as property or integrator time.

Primary observed replay adds nested timing wrappers. Its total is {fmt(C['observed']['totalAdvanceWallMS'])} ms cold and {fmt(W['observed']['totalAdvanceWallMS'])} warm. Primary observed time is about 6% cold and 5% warm above canonical median. Earlier lightweight timing-only replays are retained separately; short-run variation must not be interpreted as a scientific speedup. This is measurement perturbation of timing, not decisions; exact hash equality passes. The primary observed replay includes public-property range accounting; earlier timing-only replays are also retained.

Representative maximum sampled RSS is {C['maxRSSKiB']/1024:.1f} MiB cold and {W['maxRSSKiB']/1024:.1f} MiB warm; sampled heap used is {C['maxHeapUsedBytes']/1024**2:.1f} / {W['maxHeapUsedBytes']/1024**2:.1f} MiB. These include rich diagnostics and serialization, not just 21 unknowns. No long-duration memory stability is demonstrated. Diagnostic histories/attempt arrays and trace grow with work; B9D retains attempts in its worker. Such retention needs an explicit later design before long sessions.

Worker transport and UI rendering: no fresh browser measurement here. Retained B11 Chromium/WebKit commissioning evidence contains historical service/roundtrip/render measurements, revalidated as saved evidence only. They are not mixed into Node solver timing. Browser scheduling or transfer/dispatch residuals cannot be attributed to science. B12 owner reports responsive physical iPad review; that is not an instrumented throughput benchmark.

Desktop Chrome/Edge implication: keep synchronous scientific computation in a worker and deliver bounded accepted snapshots so controls remain responsive. This harness demonstrates finite solver work on a cloud CPU, not performance of an ordinary desktop or the owner's laptop. Benchmark nominated desktop hardware and current browser versions separately before committing a UI pacing target. No browser-dependent scientific branch is added.
''')
projectionRows=[]
for f,r in [('cold',C),('warm',W)]:
 for target,p in sorted(r['conditionalProjection'].items(),key=lambda item:float(item[0])):projectionRows.append([f,target,fmt(p['fastestRecentWindowWallSeconds']),fmt(p['medianWholeProbeWallSeconds']),fmt(p['slowestObservedWindowWallSeconds'])])
write('LONG_HORIZON_FEASIBILITY.md',f'''# Long-horizon feasibility: projections only

Maximum actually simulated time is 0.01 s. The following targets were **not simulated**: 0.1 s, 1 s, 10 s, 60 s and one hour. No scientific qualification expands beyond 0.001 s.

Measured costs vary enough that predictive optimistic/central/pessimistic confidence bounds are unsupported. The table instead gives reproducible conditional arithmetic budgets, in wall seconds: fastest measured recent-window rate × target; median whole-probe rate × target; slowest observed interval rate × target. The slow rate includes tiny startup intervals. These are observed cost scenarios, not probabilities, limits or forecasts of physical success. A domain/numerical refusal can prevent reaching a target at any CPU budget.

{table(['Fixture','Projection target simulated s','Fast recent-rate budget wall s','Median whole-probe-rate budget wall s','Slow observed-rate budget wall s'],projectionRows)}

Formula: interval rate = wallMS / (1000 × actual accepted Δt). Whole-probe rate = sum(advance wallMS) / (1000 × 0.01). Process startup/receipt serialization is excluded. CPU budgets at the median observed CPU rate are {fmt(C['timingReplicates']['medianCPUSecondsPerSimSecond'])} × target seconds cold and {fmt(W['timingReplicates']['medianCPUSecondsPerSimSecond'])} × target warm. CPU and wall differ because V8 compilation/GC/background threads and scheduling contribute. These CPU rates are not assumed to stay constant.

Even 0.1 s is ten times the longest observed horizon and remains a low-confidence extrapolation. For 1, 10, 60 and 3600 s the factors are 100, 1,000, 6,000 and 360,000: current evidence does not establish the phase path, stable adaptive steps, support-domain reachability, inventory positivity, boundary realism, convergence or memory behavior. One hour's arithmetic is especially unsuitable as a feasibility promise.

The warm trajectory already changes phase near 0.005375 s and adds five temporal rejections in the last interval. Cold grows its steps while warm subdivides a saturation crossing. Neither trajectory samples mature coupled plant dynamics or a steady operating condition. Repeating startup tiny-step expense forever is not a justified pessimistic forecast; maintaining the best late-window step is not a justified optimistic forecast. The table exposes the sensitivity without asserting either future.

Measured bottleneck ranking: (1) Jacobian-associated residual workload, plus substantial warm PH inversion inside it; (2) repeated TR-BDF2 stages needed for accepted adaptive accuracy and phase transitions; (3) other recovery/assembly/diagnostic/runtime work; (4) linear algebra, currently small. Fixed boundary physics and thermodynamic domain support limit future physical meaning/reachability but caused no normal-fixture refusal in the measured interval. Worker/UI cost is not measured here and is not ranked as a scientific bottleneck.

Memory cannot be projected from the 21-coordinate state alone: original diagnostic history grows with corrections/attempts, while B13 receipt encoding adds temporary copies. A bounded history/transport design and heap profiling are required before extended worker sessions. No unsupported memory-per-hour figure is supplied.

Required next evidence: controlled desktop-browser timing, phase-boundary error decomposition, support-domain monitoring with accepted partial-state retention, longer-horizon step/energy/refinement checks under a separately approved protocol, and realistic coupled boundaries/calibration. Speed improvements alone would not establish an industrial refrigeration simulator.
''')
write('QUALIFICATION_GAPS.md','''# Qualification gaps

Accepted scientific qualification stays at 0.001 s. Successful 0.002/0.005/0.01 s probes are diagnostic research only. They do not establish extended-duration accuracy, convergence under time refinement, phase-event timing accuracy, mesh convergence, stability under other boundary conditions or complete thermodynamic coverage.

- Same-engine original-A2/B9C/instrumented equality passes. Fresh browser comparisons were not run; retained Chromium binary64 results differ from Node even at initialization. No cross-engine bit-exact claim.
- Timings characterize one managed VM and Node version, three canonical replicates and a detailed observed replay. No ordinary desktop, Chrome/Edge, owner laptop or independently instrumented physical iPad benchmark.
- Component probes nest and perturb timing; disjoint CPU attribution, allocation profiles and JIT/GC decomposition remain open. Worker/UI/transport overhead was not freshly measured.
- No normal-fixture nonlinear refusal or property exception was observed. A controlled exact-support boundary witness verifies genuine domain stop and retained prior progress, but not every possible failure path. No general fault-injection campaign was repeated.
- Per-interval public-property extrema include nonlinear and boundary calls; they are not equipment limits or residence-time distributions. Phase event time is interpolated, not root-qualified.
- Conservation is verified at completed sampled records with the original audit and detailed signed ledgers. Small closure residuals alone do not prove accurate long-duration physical trajectories.
- Rich diagnostic retention and research serialization inflate memory. Long-session history disposal/backpressure and cancellation at synchronous boundaries remain separate engineering work.
- Fixed pressure/enthalpy reservoirs, uncalibrated hydraulic/thermal inputs, homogeneous equilibrium bulk phases and simplified finite air limit industrial realism. Compressor/receiver/condenser/feed valve/controls are not scientifically coupled.
- B12 private deployment and iPad checklist success are owner-reported. No credentials or device screenshots were supplied to or committed by this investigation. The deployed workstation is untouched.

The diagnostic milestone passes because these limits are explicit and the required bounded characterization is reproducible. None is silently promoted to extended scientific qualification.
''')
write('NEXT_SOLVER_MILESTONE_PROPOSAL.md','''# Proposed next solver investigation

Recommend a separate B14-A0 phase-boundary temporal-error and Jacobian/residual cost investigation. Keep this B13 branch frozen for engineering review; implement no optimization here.

First reproduce the warm section-0 vapor crossing around 0.005375 s, with the same table and conserved state. Attribute the normalized temporal error to mass, internal energy, pressure, enthalpy and each thermal component using detached diagnostic copies only. Compare bounded output-boundary sequences and approved time refinements. Establish whether transition-related rejection is expected physical accuracy demand, constitutive interpolation behavior or an estimator sensitivity before changing the controller. Preserve refusal and accepted partial progress.

Then profile allocation and constitutive arithmetic inside the 21-column signed finite-difference Jacobian. Measure where residual object/array construction and warm PH inverse loops consume CPU. The present data show a large Jacobian envelope and fixture-dependent property cost; they do not identify a proven safe speedup.

Candidate experiments, each needing an isolated equivalence gate, include the existing optional exact thermal columns, equivalent residual assembly/allocation changes, and exact-input reuse with strict ownership/lifetime boundaries. Any change must preserve residual/Jacobian coordinates, stage results, controller decisions, M/U/V, thermal storage, signed fluxes, property failures and conservation. If a mathematically equivalent change shifts binary64 decisions, document it separately and obtain a scientific qualification plan rather than silently replacing accepted behavior. Table inversion replacements, new backends, relaxed tolerances and clipping are outside the proposed first comparison.

Prioritize desktop Chrome/Edge worker tests on nominated ordinary hardware with actual CPU/browser versions, main-thread responsiveness, cancel/dispose behavior, memory/history retention and accepted-state delivery measured separately. Keep the deployed B12 assets and accepted UI horizon frozen. Owner physical-device activity stays separate.

A later bounded horizon increment may be proposed only after reviewing the current phase/conservation evidence, with explicit wall/CPU/memory budgets and stop gates. Do not jump to minutes/hours. Physical progress also requires a separate boundary/coupling/calibration program: feed and suction reservoir dynamics, validated equipment correlations and inventory/energy accounting across components. Solver efficiency and plant realism are distinct acceptance decisions.

Review gate: choose the next diagnostic question, equivalence requirements and bounded horizon protocol. No production merge, deployment or optimization is authorized by this proposal.
''')
status=dict(milestone='B13-A0',decision='B13-A0 DIAGNOSTIC CHARACTERIZATION PASS',acceptedScientificHorizonSeconds=.001,maxActuallyObservedExperimentalHorizonSeconds=.01,exploratoryQualification='UNQUALIFIED RESEARCH',acceptedA2BaselineIntegrity='PASS: source closure and fresh same-engine state/record/attempt bit equality',b9cSourceIdentity='PASS: protected blobs unchanged',conservation='PASS: original sampled section/node/global audits',termination='Normal probes completed; genuine separate domain witness preserves prior progress; external CPU-budget termination retained as external',dominantBottleneck='Jacobian residual work; warm PH inversion is a substantial nested cost; linear algebra small',projectionConfidence='Measured local rates; low/unsupported physical-success extrapolation beyond 0.01 s',qualificationGaps='See QUALIFICATION_GAPS.md',nextInvestigation='Phase-boundary temporal-error and Jacobian/residual decomposition',deployedReference='B12, owner reported; unchanged source/package; no private remote verification',productionMerge=False,deployment=False,scientificSourceOptimization=False,engineeringReviewRequired=True)
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
(B/'milestone-status.csv').write_text('item,status\n'+''.join(f'"{k}","{str(v).replace(chr(34),chr(34)*2)}"\n' for k,v in status.items()))
print('Wrote all B13 review reports and machine-readable milestone status')

with (B/'README.md').open('a') as f:f.write("\nFinal local review gate:\n\n```sh\npython3 experiments/dx-fv/browser_eos_b13/validate.py\npython3 experiments/dx-fv/browser_eos_b13/seal.py --verify\n```\n\n`evidence/remote-refs-after.txt` and `pr3-after.json` are post-implementation, pre-push snapshots. They prove no protected remote changes during research. After pushing only the new branch, read fresh snapshots into ignored `.runtime/remote-refs-published.txt` and `.runtime/pr3-published.json`, then run:\n\n```sh\npython3 experiments/dx-fv/browser_eos_b13/verify-protected.py --published --after .runtime/remote-refs-published.txt --pr-after .runtime/pr3-published.json\ngit status --porcelain\n```\n\nThe final published-HEAD equality and clean-tree check are reported at handoff; they cannot be embedded in the same commit while naming that commit's own final SHA. No PR or deployed reference is mutated by these checks.\n")
