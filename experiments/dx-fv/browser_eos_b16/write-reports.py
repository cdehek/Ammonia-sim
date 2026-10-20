"""Render reports from actual retained measurements. No decorative estimates."""
from pathlib import Path
import json,gzip,statistics as s,struct,csv
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):
 p=E/(name+'.json');return json.loads(p.read_text() if p.exists() else gzip.decompress((E/(name+'.json.gz')).read_bytes()))
A=read('analysis');S=read('chromium-science');C=read('context-counts');N=read('node-primary');M=read('chromium-retention');J=read('jit-gc-trace-summary')
def write(name,text):(B/(name+'.md')).write_text(text.strip()+'\n')
def num(x):return f'{x:.2f}'
def table(items):
 out=['| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |','|---|---:|---:|---:|---:|---:|']
 for name,x in items:out.append(f"| {name} | {num(x['controlMS']['median'])} | {num(x['candidateMS']['median'])} | {num(x['improvementPercent']['median'])} | {num(x['savedMS']['median'])} | {x['candidateFasterPairs']}/{x['savedMS']['n']} |")
 return '\n'.join(out)
primaryNode=[(f'{f}, {"fresh" if w==0 else "2 warmups"}',A['node'][f'{f}-warmups{w}-wallMS'])for w in [0,2]for f in ['cold','warm']]
primaryWorker=[(f'{f}, {"fresh" if w==0 else "2 warmups"}',A['worker'][f'{f}-warmups{w}-computeMS'])for w in [0,2]for f in ['cold','warm']]
micro=[(k,v)for k,v in A['micro'].items()]
allStats=[('Node '+k,v)for k,v in A['node'].items()]+[('Worker '+k,v)for k,v in A['worker'].items()]+[(k,v)for k,v in A['micro'].items()]+[(k,v)for k,v in A['sensitivity'].items()]
disp=['| Case | Original ms range / IQR | Candidate ms range / IQR | Paired % range / IQR |','|---|---:|---:|---:|']
for name,x in allStats:
 def d(k):v=x[k];return f"{num(v['min'])}–{num(v['max'])} / {num(v['iqr'])}"
 disp.append(f"| {name} | {d('controlMS')} | {d('candidateMS')} | {d('improvementPercent')} |")
write('BENCHMARK_RESULTS',f'''# Actual benchmark results

All valid samples retained; no timing exclusions or outlier trimming. Six pairs per primary row, same runtime/options/inputs, AB/BA/BA/AB/AB/BA. Positive paired values mean candidate faster. Paired medians are not ratios of group medians. Fresh means fresh process/Worker JIT, not empty disk/network cache. Two warmups are untimed bounded model resets followed by a new measured model. All solver rows end at 0.01 s; >0.001 s is UNQUALIFIED RESEARCH.

## Node 24.19.0 engine wall time

{table(primaryNode)}

CPU milliseconds are recorded separately. CPU paired results:

{table([(f'{f}, warmups={w}',A['node'][f'{f}-warmups{w}-cpuMS'])for w in [0,2]for f in ['cold','warm']])}

## Actual Linux Chromium 154 Web Worker compute wall time

{table(primaryWorker)}

Worker compute includes original model.advance and original record work, excludes asset/init, compact projection, message transport and main handler. Full state/record/attempt digests checked after timing match per pair. Same-runtime comparison only; exploratory Node and browser trajectories need not be bit-identical.

## Supported PH microbenchmarks — 20,000 calls per class

{table(micro)}

Each has 3,000 untimed calls; equal-count mixed is a research input sequence. Microbenchmark gains are not coupled-solver gains. Two-phase is an explicit near-zero-benefit control.

## Supplemental scopes and sensitivity

{table([(k,v)for k,v in A['worker'].items()if 'transition' in k or '-added' in k or '-fine' in k]+list(A['sensitivity'].items()))}

Added/fine: two independent pairs each, exploratory only. Jitless: three pairs each, a separate interpreter sensitivity run, not normal browser performance. Counters: six pairs each with perturbed code shape. Four traced V8 processes are separate observed samples with no primary-pair inference. Raw sample counts: 60 primary Node processes (48 solver, 12 PH), 24 counters-only, 12 jitless, four trace-observed; 64 Worker solver samples (48 primary, 16 supplemental), 12 Worker PH samples. Twelve bounded retention sessions and 24 packaged-UI validation samples are separate evidence, not primary timing substitutions. Every valid and failed setup/harness attempt remains retained.

## Range and dispersion

Ranges and IQRs below retain extremes. IQR is linearly interpolated over observed samples; these are descriptive small-sample statistics, not device-population confidence intervals. Raw pairs, all medians/ranges/IQRs and service/roundtrip statistics are in `evidence/analysis.json`.

{chr(10).join(disp)}
''')
contexts=[]
for f in ['cold','warm']:
 r=next(x for x in C['rows']if x['fixture']==f and x['variant']=='candidate');c=r['advanceCounts'];p=r['advancePH'];v=c['ownedHolders'];outside=sum(n for k,n in p.items()if k.startswith('outside-implicit-stage'));columns=sum(n for k,n in p.items()if '|column-'in k)
 contexts.append(f"| {f} | {c['phCalls']:,} | {v:,} ({100*v/c['phCalls']:.2f}%) | {c['phCalls']-v:,} | {outside:,} | {columns:,} | {c['boundary.hit']:,}/{c['boundary.miss']:,} | {c['section.hit']:,}/{c['section.miss']:,} |")
write('COLD_PERFORMANCE_ROOT_CAUSE',f'''# Cold performance: bounded evidence, unresolved cause

B15's five-of-six cold regression is not a stable universal result in B16. Node wall timing improves on this host; Chromium changes sign between fresh and warmed-engine strata. Warmed Chromium cold median regression is {num(A['worker']['cold-warmups2-computeMS']['savedMS']['median'])} ms saved (negative means lost), {num(A['worker']['cold-warmups2-computeMS']['improvementPercent']['median'])}%, candidate faster in {A['worker']['cold-warmups2-computeMS']['candidateFasterPairs']}/6. Its paired range includes both signs. This small sample supports a real engineering tradeoff to retain, but not a statistically firm general cold penalty or a proven causal root cause.

{table(primaryNode+[(f'Chromium {name}',x)for name,x in primaryWorker])}

## Confirmed workload and ownership

Advance-only original schedule, initialization excluded, no additional checkpoint records. Frozen observer context probe matches original/candidate science and property distributions. Counts below are Node observations; separate Chromium diagnostic receipts include initialization/additional record observations and can follow a different exploratory adaptive path.

| Fixture | PH calls | Eligible vapor holders | Other PH (mixture here) | PH outside implicit stages | PH in finite-difference columns | Boundary cache hit/miss | Section cache hit/miss |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(contexts)}

Cold pressure brackets 27,324 → 19,134 (8,190 removed); warm 764,565 → 150,744 (613,821 removed). All 38 bisections and 40 branch interpolations per successful eligible vapor PH remain unchanged. Cold column PH calls are mixture calls; vapor work is concentrated in other stage/trial/record work. Existing stage caches mean many residual section requests hit cached thermodynamic states; property calls are not uniformly distributed among residual coordinates. `context-counts.json` retains all contexts and cache counts, exactly equal by variant.

The cold candidate constructs 210 local holders during advance; two-phase returns before holder construction. Public PT has one forwarding closure per engine and an extra public call layer, while internal branch helpers carry an additional optional argument and ownership test. Source-level bracket-array construction is reduced, but machine-code allocation elimination is unknown. No per-inversion allocation profile was measured. Lower heap snapshots do not establish savings.

## Controls and interpretation

Uninstrumented primary cases use no inner lexical counters or scientific hashing. Six paired counters-only samples per fixture are separate; their cold paired median {num(A['sensitivity']['counters-cold']['improvementPercent']['median'])}% does not isolate holder overhead, since instrumentation changes both code shape and runtime. Three no-optimizing-JIT pairs yield cold {num(A['sensitivity']['jitless-cold']['improvementPercent']['median'])}% and warm {num(A['sensitivity']['jitless-warm']['improvementPercent']['median'])}% median improvement. Disabling JIT is a sensitivity control, not causal decomposition or a recommended setting.

Fresh versus warmed Chromium changes the cold sign. Node fresh cold CPU is {num(A['node']['cold-warmups0-cpuMS']['improvementPercent']['median'])}% paired while its wall time improves; CPU includes concurrent compiler/GC work and cannot be substituted for wall latency. Counterbalanced order, fresh ownership and exact counts rule out a deliberately different scientific workload, but do not remove scheduling/JIT/GC variability. The large fresh-cold pair remains included. Browser cache effects are shared controls, not experimentally isolated.

V8 traces show optimization/inlining/deoptimization and GC in both variants. They do not identify a unique candidate-only deoptimization responsible for cold timing, quantify exclusive fast-path overhead, or establish GC as the cause. No overlapping timer subtraction is used. The small vapor fraction makes fixed/code-shape overhead a plausible hypothesis, not a demonstrated explanation. The evidence is runtime/warmup-sensitive and too variable/small for a general root-cause claim. Keep the cold tradeoff visible and measure intended devices before a default decision. No frozen prototype is modified to improve these results.
''')
jrows=[]
for r in J['rows']:jrows.append(f"| {r['file']} | {r['deoptimizationCount']} | {r['gcEvents']} | {num(r['gcPauseMS'])} |")
write('JIT_AND_GC_SENSITIVITY',f'''# JIT and GC sensitivity

Fresh and two-replay warmed-JIT cases are separate primary strata. The warmed model is newly created after untimed resets; no state crosses samples. Chromium cold flips from {num(A['worker']['cold-warmups0-computeMS']['improvementPercent']['median'])}% to {num(A['worker']['cold-warmups2-computeMS']['improvementPercent']['median'])}% paired improvement; warm remains beneficial, with all six warmed pairs faster. Node cold does not show the same wall-time regression. This demonstrates sensitivity, not proof that warmup explains most of B15's slowdown.

{table(list(A['sensitivity'].items()))}

Counters-only frozen sources perturb code shape and cannot be used as primary speed estimates. `--jitless` disables optimizing execution in separate Node processes, three counterbalanced pairs per case; no browser or deployment setting is changed. The limited three-pair result is descriptive.

Four observed processes run trace-opt, trace-deopt, trace-turbo-inlining, trace-file-names and trace-gc-nvp. Whole traces are retained compressed, bounded by process/CPU/output limits. Relevant function examples/counts and deoptimization reasons are in `jit-gc-trace-summary.json`. `pBracket`, `branch`, `inverse` and solver functions become hot and compile; the traces show Maglev and, in warm work, TurboFan activity. Inlining lines include decisions/candidates as well as actual inlining and are not all successful inlines. Generic wrong-map/type deoptimizations occur in both variants. No stable candidate-only causal mechanism is isolated.

| Observed process | Deoptimizations | GC events | Whole-process GC pause ms |
|---|---:|---:|---:|
{chr(10).join(jrows)}

These are single observed processes including startup, table parse/freeze, initialization and compute; trace output adds overhead. Whole-process pauses are not exclusive solver GC cost and are not subtracted from solver time. Primary Node receipts also retain timestamped PerformanceObserver GC events, memory and CPU; callbacks run after synchronous work and may straddle scope boundaries. Neither lower post-run heap nor fewer source arrays establishes allocator-byte savings, escape analysis, peak live memory, or GC causation. Per-allocation/per-function profiles and controlled target-browser compiler traces remain gaps.
''')
def decode(v):
 if isinstance(v,list):return list(map(decode,v))
 if isinstance(v,dict):
  if set(v)=={'f64'}:return struct.unpack('>d',bytes.fromhex(v['f64']))[0]
  return {k:decode(x)for k,x in v.items()}
 return v
science=[];totalResiduals=totalMatrices=0
for c in S['cases']:
 r=c['runs']['observed-control'];d=r['diagnostics']['streams'];totalResiduals+=d['residuals']['count'];totalMatrices+=d['linear']['count'];science.append(f"| {c['fixture']} | {c['schedule']} | {len(r['checkpoints'])} | {d['residuals']['count']:,} | {d['linear']['count']:,} | {d['commits']['count']} | PASS |")
warm=next(c for c in S['cases']if c['fixture']=='warm' and c['schedule']=='original')['runs']['control'];event=decode(warm['events'])[0]
write('BROWSER_SCIENTIFIC_PARITY',f'''# Actual Chromium Worker scientific parity — PASS

Local-origin Chromium {S['browserVersion']}, real module Web Workers, identical original/candidate fixtures, options, source loading and protocol. Uninstrumented and frozen-observer workers run separately, sequentially. Same-runtime complete state/original record/checkpoint and attempt binary64 hashes match at 0, 0.0001, 0.0005 and 0.001 s, and every additional scheduled checkpoint through 0.01 s. Every result above 0.001 s remains UNQUALIFIED RESEARCH. No Node/Chromium bit-equality or physical desktop qualification is claimed.

| Fixture | Schedule | Checkpoints | Full residual objects | Matrices/RHS/corrections | Accepted half commits | Result |
|---|---|---:|---:|---:|---:|---|
{chr(10).join(science)}

Across schedules: {totalResiduals:,} full residual objects and {totalMatrices:,} actual linear matrices/RHS/corrections per variant. Exact length-delimited SHA-256 streams also compare signed probes, all columns, temporal coarse/fine objects, normalized error and controller decisions, and complete committed states/pieces/ledgers. All stream counts and digests match. No residual/Jacobian surrogate is substituted. Complete accepted state and original record include five M/U/V inventories, PH/properties, eleven thermal energies and tube/fin/air temperatures, signed boundary fluxes, ledgers, stop metadata and accepted clock. Original attempts include accepted/rejected trials and TR-BDF2 decisions. Original conservation checks pass without relaxed thresholds.

Chromium warm original phase event is interpolated within [{event['bracketStartSeconds']:.17g}, {event['bracketEndSeconds']:.17g}] s; reported event time {event['seconds']:.17g} s. It is an interpolated event, not a root-solved physical event. Candidate/control event objects match. The first internal face is negative at 0.005 s ({warm['checkpoints'][-2]['flows'][1]:.17g} kg/s) and positive at 0.01 s ({warm['checkpoints'][-1]['flows'][1]:.17g}), preserving subsequent internal reversal at observed checkpoints. Node/B15's exploratory bracket can differ from Chromium's because cross-runtime equality is not supported. No new science horizon is qualified.

Actual Worker failures preserve genuine thermal support-domain refusal, invalid pressure, validated invalid enthalpy, failed inversion, invalid-update rollback, committed 0.0001 s then domain refusal, and repeat after stopped state. The constrained numerical fixture retains its original accepted partial clock 4.2724609375e-7 s before solver refusal. Full original stopped state/record/attempts match by variant; no fake whole-request rollback is claimed when earlier commits exist. Public PT arity and extra/throwing fourth-argument behavior match.

Raw engine PH with NaN enthalpy historically returns a NaN-containing state; the thermodynamics wrapper refuses it. Both behaviors are preserved. First harness attempt wrongly assumed raw rejection; the next wrongly assumed a zero numerical-refusal clock. Their failed receipts and completed case receipts are retained, assumptions corrected, full suite rerun and passed. Neither failure was counted as a scientific candidate mismatch or hidden.

Session tests verify Worker-visible refusal/stale state, no new fresh snapshot after refusal, malformed commands/envelopes, stale/cross-session response rejection, disposal/restart at time zero and external in-flight Worker loss. External loss says scientific result unknown and is never numerical refusal. Original stop objects remain unchanged; protocol rejections are separate. All 64 timed solver samples and packaged handoff pairs subsequently match full state/record/attempt digests outside timing windows. Exact science receipts are losslessly compressed in `chromium-science.json.gz`, with raw SHA-256 in `lossless-compaction.json`.
''')
life=[]
for name in ['constructMS','readyMS','assetVerificationMS','importMS','tableMS','initializeMS','initialSnapshotRoundtripMS','disposeMS','projectionMS','mainPostMS','dispatchToWorkerMS','returnDeliveryMS','handlerMS','textAssignmentMS','ping-roundtripMS','echo-roundtripMS','workerPostMS']:
 a,b=[A['lifecycle'][v][name]for v in ['control','candidate']];life.append(f"| {name} | {num(a['median'])} ({num(a['min'])}–{num(a['max'])}) | {num(b['median'])} ({num(b['min'])}–{num(b['max'])}) |")
resp=[]
for v in ['control','candidate']:
 r=A['lifecycle'][v]['responsiveness'];resp.append(f"| {v} | {r['delaysMS']['n']} | {num(r['delaysMS']['median'])}/{num(r['delaysMS']['p95'])}/{num(r['delaysMS']['max'])} | {r['inputAcknowledgementMS']['n']} | {num(r['inputAcknowledgementMS']['median'])}/{num(r['inputAcknowledgementMS']['max'])} | {num(r['toolSwitchMS']['median'])}/{num(r['toolSwitchMS']['max'])} | {len(A['lifecycle'][v]['longTasks'])} |")
write('WORKER_LATENCY_AND_RESPONSIVENESS',f'''# Genuine Worker latency and main-thread observations

Timing separates solver compute, service, request/response transport, main handler and text assignment. Original/candidate use the same message and snapshot format. Fresh-JIT primary rows below pool six cold and six warm sessions per variant (n=12); ping has 144 and snapshot echo 96 observations per variant. Source import/table creation follow an identical fetch/hash verification step. Browser cache is not emptied. Worker startup and init are latency costs, not solver CPU.

| Scope | Original median ms (range) | Candidate median ms (range) |
|---|---:|---:|
{chr(10).join(life)}

Worker construction is synchronous new Worker time; ready includes module loading/scheduling before the handshake. First snapshot roundtrip includes asset verification, engine/table initialization and original model create/record. The synchronous Worker post cost is reported after the original reply; it includes clone/enqueue and is not exclusive serialization CPU. Epoch-based dispatch and return-delivery contain scheduling/queueing; timer quantization affects tiny values. Structured clone is exercised with actual compact snapshots in echo controls. Service and roundtrip summaries for every solver case are in `analysis.json`; no inclusive-scope subtraction is claimed as exclusive clone cost.

| Variant | Heartbeats | Delay median/p95/max ms | Synthetic input count | Input median/max ms | Tool switch median/max ms | Observed long tasks |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(resp)}

Heartbeat period is 10 ms; delays are excess over scheduled period. It runs independently on the main thread while Worker initialization/warmups/computation proceeds, ending at the accepted response, before deliberate diagnostic transfer/hash validation. Input and tool measurements are actual timer-scheduled DOM click acknowledgements in this harness, not fabricated interaction numbers or physical device input latency. Long Tasks observer is available in Chromium. Zero observed long tasks in these windows is a bounded observation, not full workstation responsiveness qualification. Main-thread handler includes compact display bookkeeping; textContent assignment is measured separately. No layout/paint latency is measured.

In-flight termination/refusal/restart evidence is retained in the science protocol receipt. Worker loss occurs at the harness boundary, rejects pending work as externally lost/unknown, and a fresh session restarts at zero. Terminate/disposal timing is not an OS process reclamation or memory-release guarantee. No responsive full workstation UI, browser background behavior, or owner laptop is qualified.
''')
mix=['| Hypothetical request mix | Warmups | Cold request fraction | Median paired ms saved | Median paired improvement % |','|---|---:|---:|---:|---:|']
for k,v in A['hypotheticalMixes'].items():mix.append(f"| {k.rsplit('-warmups',1)[0]} | {k.rsplit('warmups',1)[1]} | {v['coldRequestFraction']:.0%} | {num(v['medianPairedSavedMS'])} | {num(v['medianPairedPercent'])} |")
write('WORKLOAD_MIX_ANALYSIS',f'''# Workload realism and tradeoffs

The actual distribution of future ammonia installation conditions and operator requests is NOT established. The original cold/warm fixtures are illustrative, materially different property workloads. Cold has 4.18% eligible vapor PH calls during advance; warm 90.37%. This does not make warm representative of all industrial refrigeration. No plant duty cycle is fabricated.

The measured matrix includes both original fixtures, repeated independent starts, fresh and warmed JIT, original/added/fine schedules, a transition-bearing warm 0.005→0.01 s interval, supported vapor-dominant/two-phase-dominant/equal-count mixed PH sequences, and short reset/history sessions. All advances remain ≤0.01 s. Detailed paired absolute and relative results, sample counts and dispersion are in `BENCHMARK_RESULTS.md` / `analysis.json`.

{table(primaryWorker)}

Vapor/mixed property benefits do not translate directly to coupled solver gains. Two-phase PH shows near-zero gain, and warmed Chromium cold has a small median regression while warm improves. A cold slowdown is retained even where its absolute milliseconds are smaller than warm savings. Node/browser and JIT differences prevent a universal default conclusion. Transition-bearing interval timing is exploratory and can include both vapor and mixture work.

## Hypothetical planning scenarios only

Each scenario weights whole bounded cold/warm requests, combines matched pair-index absolute timings, then computes each pair's relative improvement. These are declared request-count mixes, not physical time, energy, plant operating distributions or operator usage evidence. There are six synthetic paired scenarios each; pairing index across separate cases adds another planning assumption. They are not new measured mixed solver sessions.

{chr(10).join(mix)}

A favorable scenario does not authorize integration or resolve the cold penalty. Retain the original as independently selectable control/default for any future review. Establish target-device behavior and intended research workloads before considering candidate opt-in policy.
''')
mem=['| Fixture / variant (fresh Node) | End heap median MB | Max RSS median MiB | Recorded GC events median |','|---|---:|---:|---:|']
for f in ['cold','warm']:
 for v in ['control','candidate']:
  r=[x for x in N if x['kind']==f and x['variant']==v and x['warmups']==0];mem.append(f"| {f}/{v} | {s.median(x['memoryEnd']['heapUsed'] for x in r)/1e6:.2f} | {s.median(x['resources']['maxRSS'] for x in r)/1024:.2f} | {s.median(len(x['gc']) for x in r):g} |")
heaps=[r['rendererMemory']['usedJSHeapSize']for r in M['rows']]
write('MEMORY_AND_HISTORY_RETENTION',f'''# Bounded memory/history observations

Twelve reset Worker sessions (six per variant, alternating cold/warm) each end at 0.01 s. After advance, 48 repeated latest-snapshot requests do not add model attempts or Worker snapshot versions. Worker history retains two accepted snapshots (init/final) in this scenario; maximum allowed is eight. Client display history stays at eight. Cold retains 17 attempts and warm 52 on this Chromium path; each fixture's count stays unchanged during latest requests. Dispose reports dropping those attempt/snapshot references and terminates the Worker. No physical session exceeds the authorized horizon.

Property-table memory: one deep-frozen scientific table per fresh Worker. The self-contained ~1.44 MB source asset is not its live heap size. Model state: five cells plus eleven energies, original accepted state/ledgers. Attempt history: bounded at 256. Worker command count: bounded at 128, no response cache. Serialized snapshots: compact projection, payload JSON-byte estimate in stats; actual structured-clone storage differs. Client histories/metrics and heartbeat arrays are bounded by session/request lifetime. Diagnostic hashing retains stream state instead of raw residual histories, though full failure receipts contain detailed original evidence.

{chr(10).join(mem)}

Node snapshots include engine/table, model, retained attempts, parser/compiler/GC state and instrumentation scaffolding. Max RSS includes process/native memory; Node CPU/heap is not browser Worker memory. Lower post-run heap does not establish allocation savings or a leak fix. Per-object allocation bytes are not measured.

Chromium retention-session renderer performance.memory usedJSHeapSize observations range {min(heaps)/1e6:.2f}–{max(heaps)/1e6:.2f} MB. These are coarse browser-provided renderer readings with GC/quantization effects and harness instrumentation; they do not isolate Worker heap, table memory, native/renderer RSS or total browser memory. No Worker heap snapshot or long-session retained-object profile was collected. They cannot establish monotonic memory stability or per-inversion allocation differences.

Reference dropping is verified, immediate OS reclamation is not. Short reset sessions provide bounded history evidence only; they make no hours-long memory-stability claim. A later integration must audit its own observer/attempt/record/response history policies, since retaining records without caps could grow excessively even with this optimization. B16 does not rewrite historical workstation retention behavior.
''')
write('INTEGRATION_READINESS_DECISION',f'''# Integration decision: CONDITIONAL GO

Scientific correctness and Linux Chromium Worker compatibility support considering a separately authorized, isolated research prototype. This is a recommendation only. No integration, deployment, accepted-engine promotion, default change or workstation replacement is performed or authorized by B16.

Evidence: exact same-runtime full science/failure/public-interface parity, frozen sources, genuine Worker execution/lifecycle/compact transport, reproducible warm gains (warmed Chromium {num(A['worker']['warm-warmups2-computeMS']['improvementPercent']['median'])}%, {num(A['worker']['warm-warmups2-computeMS']['savedMS']['median'])} ms saved, 6/6 faster), and responsive minimal-harness observations. Fresh warm includes one slower pair, retained. Cold behavior varies: warmed Chromium median {num(A['worker']['cold-warmups2-computeMS']['improvementPercent']['median'])}% ({num(A['worker']['cold-warmups2-computeMS']['savedMS']['median'])} ms saved); Node wall and fresh Chromium do not reproduce B15's cold regression. A causal root cause and general cold cost are unproven. JIT/GC and browser/device differences remain material uncertainty.

Conditions for a later review:

1. Obtain genuine intended Windows/macOS laptop/desktop results using the supplied package, including actual Edge if intended. Run matching scientific gates on the target runtime; preserve all failures/extremes. Owner-device status is currently NOT TESTED.
2. Keep exact B9C independently available and the default. Any candidate mode must be explicit opt-in, isolated to research, with source hashes, new session on switch and immediate auditable control rollback. No engine source substitution in accepted/training/production paths.
3. Define intended bounded research workloads and an explicit acceptable cold regression budget before a default decision. Do not infer installation usage from warm fixtures or hypothetical mixes. If target cold/service/lifecycle performance is unacceptable, HOLD the integration rather than revising frozen B15 in this milestone.
4. Preserve original stop/refusal/stale semantics, strict rollback, history/attempt limits and public-holder isolation tests. Review actual workstation protocol/history/security implications separately; B16's minimal client is not a complete production transport implementation.
5. Maintain 0.001 s accepted qualification and label every longer result UNQUALIFIED RESEARCH, with 0.01 s maximum. No longer-duration physical claim follows from a faster solve.

No owner Cloudflare account was accessed. A later publication would require its own explicit authorization and review of static asset provenance, localhost-versus-HTTPS behavior, content/MIME/cache/security policy and operational rollback. No new external service or dependency is introduced here. PASS as a diagnostic milestone is independent from this conditional integration decision. GO is not selected solely from property microbenchmarks; NO-GO is not indicated by a scientific mismatch because none was found.
''')
write('QUALIFICATION_GAPS','''# Qualification gaps

Actual owner laptop, Windows/macOS hardware, actual Microsoft Edge and desktop WebKit are NOT TESTED. Linux Chromium is not proof of those platforms. Genuine target-device paired science/performance, power mode, foreground/background behavior, browser version and intended operator workload distribution remain open.

Cold penalty is not stable across runtimes/JIT strata. Small pair counts and timing ranges do not establish a universal or causal regression; counters/profiler/jitless are perturbing controls. Holder/public-wrapper allocations, escape analysis, browser-specific inlining, exclusive clone CPU and worker-only heap are not isolated. Raw heap and RSS do not establish allocator savings. No hours-long memory stability is claimed.

Minimal harness responsiveness does not qualify full workstation input/render/layout, native user input, training workflows or long-lived transport behavior. The owner ZIP tests bounded performance and per-pair scientific digests, not every full diagnostic/failure gate. Its actual cloud UI verification remains distinct from an owner-device benchmark. No unavailable result is replaced with illustrative Live Plant values.

Accepted scientific horizon is 0.001 s, maximum exploratory solve 0.01 s. All longer results remain UNQUALIFIED RESEARCH. No tolerance/interpolation/support-domain expansion, new solver, compressor substitution or equipment safety inference is allowed. Original HEM, conductance/calibration, five-section discretization, table/property bounds and short-time validation limitations persist. Terminal bulk wet is not proof of carryover or a compressor trip.

No B12/B11/B10/B9D integration, production/training promotion, main/PR change or Cloudflare deployment is included. Any such work requires separate authorization. Exact original control and source provenance remain mandatory.
''')
write('NEXT_MILESTONE_RECOMMENDATION','''# Recommended B17

Run intended-device desktop characterization and a separate research integration design review. Use genuine Windows/macOS laptop results from the small local B16 handoff, including actual Edge/Chrome/Safari/WebKit only where truly available. Preserve per-runtime exact science/failure tests, six or more balanced pairs, cold/warm and transition-bearing requests, fresh/warmed JIT, initialization/service costs, responsiveness and bounded history evidence. Record power/foreground/background context and all valid extremes.

Define an acceptable cold-case budget and intended research workload before deciding on candidate opt-in. Review real workstation session/stop/stale/rollback/retention/security boundaries. Keep original B9C the independently available default with immediate auditable reversal. If target results are inconclusive or unacceptable, HOLD integration.

B16 recommends CONDITIONAL GO for a future separately authorized research review. It does not authorize implementing or deploying that integration. Any actual integration needs a new explicit instruction, isolated branch/directory, preserved accepted source and source-identifiable candidate mode. Do not modify frozen B15 to chase B16 timings. Potential wrapper/holder/code-shape optimization ideas require a different future experiment and new exact gates.

No longer-duration physics qualification, domain widening, tolerance change or production promotion is recommended. Stop at B16 for engineering review.
''')
write('ENGINEERING_REPORT',f'''# B16-A0 final engineering report

**B16-A0 DESKTOP/WORKER READINESS PASS**. Independent integration recommendation: **CONDITIONAL GO** for a later separately authorized isolated research review. No integration or deployment occurred.

Start: exact B15 `eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35`, initially clean. Branch: `research/b16-desktop-worker-performance-20261020`. Design commit `20406db` preceded harness implementation. Final SHA is the delivered branch HEAD (a commit cannot embed itself). Initial/final byte/ref/PR receipts and completion remote-HEAD check bind delivery. All 4,057 historical tracked files, 312 B15 sealed files, A2 closure, B9C control, table and B12 scientific/workstation sources remain unchanged. PR #3 remains open at original head `d4422425750a1d3c4e432cc103ac42ead40b7cc6`, base/main `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`; protected remote refs/tags are reverified. No Cloudflare account/deployment/host modification occurs.

Scientific parity: PASS in actual Chromium module Workers across cold/warm × original/added/fine schedules, uninstrumented/observer modes. Complete state/record/attempt, full residual, Jacobian/RHS/Newton correction, temporal/controller/phase/ledger and failure semantics match exactly by runtime. {totalResiduals:,} full residuals and {totalMatrices:,} actual matrices/corrections compare per variant; conservation passes original thresholds. Raw NaN and numerical partial-progress semantics are retained, including initial harness-assumption failures and fresh passing rerun. Accepted checkpoints include 0/.0001/.0005/.001 s. Maximum solve .01 s; >.001 s remains UNQUALIFIED RESEARCH.

## Node wall results (ms; six pairs each)

{table(primaryNode)}

Node CPU results and full dispersion are separate in `BENCHMARK_RESULTS.md`. B15's cold wall regression is not reproduced consistently here. Counters reproduce exactly 210/15,739 eligible cold/warm vapor inversions and 8,190/613,821 removed pressure brackets; no scientific source changed.

## Actual Chromium Worker compute results (ms; six pairs each)

{table(primaryWorker)}

Warm improvements translate to real Worker compute and service latency on this host. Warmed Chromium cold has a small regression; fresh cold and Node wall differ. Ranges, all valid extremes, absolute savings and paired percentages are retained; there is no universal speedup or proven cold root cause. Property microbenchmarks show supported vapor/mixed benefits and near-zero two-phase gain, not a substitute for solver evidence. Added/fine and transition intervals are separately labeled exploratory.

Worker lifecycle/transport: original/candidate ready medians {num(A['lifecycle']['control']['readyMS']['median'])}/{num(A['lifecycle']['candidate']['readyMS']['median'])} ms; initial snapshot roundtrip {num(A['lifecycle']['control']['initialSnapshotRoundtripMS']['median'])}/{num(A['lifecycle']['candidate']['initialSnapshotRoundtripMS']['median'])} ms; ping {num(A['lifecycle']['control']['ping-roundtripMS']['median'])}/{num(A['lifecycle']['candidate']['ping-roundtripMS']['median'])} ms. Asset verification, import/table/create, service, clone/enqueue envelope, handler, text assignment, disposal/restart are separately retained. No exclusive serialization CPU or layout claim is made.

Independent main-thread heartbeat/synthetic DOM input/tool acknowledgements are measured through Worker startup/compute; fresh primary heartbeat max excess delay {num(max(A['lifecycle'][v]['responsiveness']['delaysMS']['max']for v in ['control','candidate']))} ms, with no observed long tasks in those windows. This is minimal-harness evidence only. Twelve reset/history sessions show bounded attempts/snapshots and disposal reference dropping; coarse renderer/Node memory cannot establish worker allocation savings or hours-long stability. V8 optimization/inlining/deopt/GC and jitless receipts characterize uncertainty without causal overclaiming.

Host: Linux cloud, AMD EPYC 9V45 identification, two-CPU quota, 8 GiB limit; Node 24.19.0, Chromium 154.0.8037.57, Playwright 1.62.0. Desktop WebKit and actual Edge NOT TESTED (executables absent); Windows/macOS hardware and owner desktop NOT TESTED. The local owner ZIP's actual UI/download passed on this cloud host only. No public deployment is required.

Remaining limits: unknown real installation/usage distribution, cold/JIT/GC sensitivity, small one-host samples, unisolated allocation/clone/worker heap, minimal rather than full workstation UI, unqualified >.001 s science and original physical/calibration bounds. Recommendation: B17 target-device characterization and separate integration design review, keep exact B9C default/rollback, no candidate promotion without explicit future authorization. Working tree and matching pushed B16 remote HEAD are verified at delivery, after final commit. Stop for engineering review.
''')
write('README','''# B16 — desktop browser Worker performance and integration readiness

**B16-A0 DESKTOP/WORKER READINESS PASS**. Integration decision: **CONDITIONAL GO** for a later separately authorized isolated research review. No integration, deployment, default change or accepted-engine promotion.

Start B15 `eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35`; branch `research/b16-desktop-worker-performance-20261020`; design `20406db` committed before implementation. Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md), [COLD_PERFORMANCE_ROOT_CAUSE.md](COLD_PERFORMANCE_ROOT_CAUSE.md) and [INTEGRATION_READINESS_DECISION.md](INTEGRATION_READINESS_DECISION.md). Every file is B16-owned. Scientific bundles are frozen B15 copies; all accepted/historical files remain unchanged.

Actual Linux Chromium Workers pass exact science/failures. Warm benefit persists; cold tradeoff depends on runtime/warmup and remains unresolved causally. No actual owner Windows/macOS/Edge/WebKit qualification. Accepted horizon .001 s; all longer results UNQUALIFIED RESEARCH, maximum solve .01 s. No refrigeration run is extended in time by repeated reset sessions.

## Owner handoff

Extract [b16-owner-benchmark.zip](b16-owner-benchmark.zip), run `python3 serve.py` (Windows often `py serve.py`), open localhost:8765. Read [OWNER_DESKTOP_BENCHMARK.md](OWNER_DESKTOP_BENCHMARK.md). Python standard library plus an existing browser; no scientific environment/npm install, public deployment or Cloudflare access. Genuine owner-device status is NOT TESTED. Packaged actual UI/download validation was Linux cloud only.

## Reproduce from repository root

```sh
python3 experiments/dx-fv/browser_eos_b16/audit.py review
python3 experiments/dx-fv/browser_eos_b16/validate.py
python3 experiments/dx-fv/browser_eos_b16/run-browser.py science --name review-science
python3 experiments/dx-fv/browser_eos_b16/run-browser.py performance --name review-worker
python3 experiments/dx-fv/browser_eos_b16/run-browser.py micro --name review-micro
python3 experiments/dx-fv/browser_eos_b16/run-browser.py retention --name review-retention
python3 experiments/dx-fv/browser_eos_b16/run-node.py primary --name review-node
python3 experiments/dx-fv/browser_eos_b16/run-node.py counters --name review-counters
python3 experiments/dx-fv/browser_eos_b16/run-node.py jitless --name review-jitless
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b16/context-counts.mjs
```

Use fresh names: retained receipts are never overwritten by campaign runners. `trace` campaign has fixed trace artifact names; reproduce it in a fresh isolated checkout/directory rather than overwriting delivered trace evidence. Installed Playwright/Chromium are required only for automation. Primary performance runners fail closed unless the retained pinned Chromium science receipt passed. Run heavy suites sequentially. Scripts bound processes/CPU/heap/history and tear down Workers/browser; external loss is not scientific refusal. Analyze retained delivered samples with `analyze.py`; rerender reports with `write-reports.py`; plot actual pairs with `plot.py`. Review-named samples remain separate and are not silently substituted into delivered statistics.

`assets/` contains original/candidate plus separate counted/observer sources. `evidence/` retains exact science hashes, compressed full refusal records, failed initial harness assumptions, every valid timing sample, V8 traces, context/cache counts, short memory observations and protected-source/ref/PR audits. `lossless-compaction.json` verifies raw science JSON bytes after decompression. `.runtime/` is ignored temporary runtime/download/socket storage, never a dependency tree or committed trace cache. Machine-readable milestone status is at the directory root. Final branch SHA and remote/clean completion check are supplied at delivery.
''')
status={'milestone':'B16-A0','classification':'B16-A0 DESKTOP/WORKER READINESS PASS','integrationReadinessDecision':'CONDITIONAL GO','startingB15SHA':'eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35','branch':'research/b16-desktop-worker-performance-20261020','designCommit':'20406db','scientificParity':True,'historicalTrackedFiles':4057,'frozenB15':True,'actualChromiumWebWorkers':True,'residualObjectsComparedPerVariant':totalResiduals,'actualMatricesAndCorrectionsPerVariant':totalMatrices,'workerSolverSamples':64,'workerPrimaryPairsPerCase':6,'nodePrimarySamples':60,'nodeCounterSamples':24,'nodeJitlessSamples':12,'nodeTracedSamples':4,'workerMicroSamples':12,'retentionSessions':12,'ownerPackageCloudValidationSamples':24,'ownerDevice':'NOT TESTED','actualEdge':'NOT TESTED','desktopWebKit':'NOT TESTED','windowsHardware':'NOT TESTED','macOSHardware':'NOT TESTED','coldRootCause':'unresolved; runtime/JIT-sensitive tradeoff, small warmed Chromium regression','qualificationSeconds':.001,'maximumExploratorySeconds':.01,'productionMerge':False,'cloudflareAccessOrDeployment':False,'workstationIntegration':False,'acceptedSourcePromotion':False,'PR3Modified':False,'rollback':'select exact independent B9C control, dispose candidate, new original session','deliveryHEAD':'Final committed/pushed branch HEAD supplied in delivery; no self-referential commit hash'}
status['gates']={'0': 'PASS: exact B15, clean start, protected source/ref/PR audit; design committed first', 'A': 'PASS diagnostic characterization; causal cold root cause remains unresolved', 'B': 'PASS actual Linux Chromium Workers; Edge/WebKit NOT TESTED', 'C': 'PASS exact same-runtime science and original failures', 'D': 'PASS bounded service, lifecycle and minimal-harness responsiveness measurements', 'E': 'PASS bounded research matrix, absolute/relative tradeoffs and hypothetical-only mixes', 'F': 'PASS six-pair primary counterbalanced samples; all valid extremes retained', 'G': 'PASS local handoff prepared and cloud UI/download verified; owner device NOT TESTED', 'H': 'CONDITIONAL GO recommendation only; no integration authorized or performed'}
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
with (B/'milestone-status.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['field','value']);w.writerows((k,json.dumps(v)if isinstance(v,dict)else v)for k,v in status.items())
print('Rendered 12 measurement-driven reports plus JSON/CSV milestone status')
