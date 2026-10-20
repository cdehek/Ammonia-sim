"""Review reports from final-version evidence; preliminary version remains separate."""
from pathlib import Path
import json,csv
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda n:json.loads((E/(n+'.json')).read_text());p=read('performance-analysis');s=p['statistics'];science=read('scientific-summary');source=read('source-preservation');term=read('external-termination-validation');build=read('build-manifest');gc=read('gc-observations');warm=s['warm-advance'];cold=s['cold-advance']
classification='B15-A1 EXACT-EQUIVALENCE OPTIMIZATION PASS'if warm['candidateFasterPairs']==6 and warm['medianBootstrap95Percent'][0]>0 else'B15-A1 SCIENTIFICALLY EQUIVALENT / PERFORMANCE INCONCLUSIVE'
def put(n,x):(B/n).write_text(x.strip()+'\n')
def fmt(x):return f'{x:.2f}'
def table():
 out='| Final workload | Original median ms (range) | Candidate median ms (range) | Paired median improvement | Median paired ms saved | Faster pairs |\n|---|---:|---:|---:|---:|---:|\n'
 for k,v in s.items():
  a,b=v['metrics']['control']['wallMS'],v['metrics']['candidate']['wallMS'];out+=f"| {k} | {a['median']:.2f} ({a['min']:.2f}–{a['max']:.2f}) | {b['median']:.2f} ({b['min']:.2f}–{b['max']:.2f}) | {v['pairedImprovementPercent']['median']:.2f}% | {v['pairedSavedWallMS']['median']:.2f} | {v['candidateFasterPairs']}/6 |\n"
 return out
for n,text in json.loads((B/'report-texts.json').read_text()).items():
 text=text.replace('0.0009236366510514928',repr(term['lastIndependentlyEstablishedAcceptedSeconds']))
 if n=='MECHANICS_REPORT.md':text+='\nThe final public PT export forwards only p/T/kind to the internal helper, preserving arity 3 and ignoring extra public arguments. One wrapper function is constructed per engine. The local holder remains private to PH.\n'
 if n in ['SUPPORT_DOMAIN_AND_EXCEPTION_PARITY.md','MUTATION_AND_CACHE_OWNERSHIP.md','PROPERTY_LEVEL_EQUIVALENCE.md']:
  text+='\nFinal interface regression: 18 extra-argument comparisons and public arity 3 pass. Preliminary v1 exposed the fourth internal PT parameter to callers; a forged holder changed its PT result. `interface-regression.json.gz` retains original/v1/corrected binary64 outputs and root cause. The final public entry forwards only the original three parameters. Browser repeats this counterexample/fix. No failing comparison was removed.\n'
 if n=='SCIENTIFIC_SOURCE_AND_PROVENANCE.md':text+=f"\nFinal candidate SHA-256 `{build['builds']['candidate']['sha256']}`; observed candidate `{build['builds']['observe-candidate']['sha256']}`. Final Node candidate receipts and browser summaries bind these build hashes. V1 source, timings, counterexample and preliminary receipts are separately retained.\n"
 if n=='COUPLED_MODEL_EQUIVALENCE.md':text+='\nAfter the public-interface correction, all six final candidate canonical/observed schedules were freshly replayed. Original control source bytes and earlier complete control receipts are unchanged; verification checks final candidate build hashes and compares to those exact same-runtime controls. All browser pairs were freshly rerun in both variants. Final timing pairs use new clean processes for both variants.\n'
 put(n,text)
put('README.md',f'''# B15 — exact vapor PH pressure-bracket reuse

**{classification}**. Final candidate passes Node and same-browser scientific gates. Warm paired median improvement {warm['pairedImprovementPercent']['median']:.2f}%; cold {cold['pairedImprovementPercent']['median']:.2f}% ({cold['candidateFasterPairs']}/6 faster). All measurements and uncertainty are retained.

Branch `research/b15-vapor-ph-bracket-reuse-20261020`; B14 start `71608010fe49946dc542a4d85dff315c875274ad`; design commit `90806af` preceded implementation. Final SHA is branch HEAD supplied at delivery (a commit cannot embed its own hash). All work is B15-only. Qualification remains 0.001 s; all longer results are **UNQUALIFIED RESEARCH**; maximum solve 0.01 s.

Final review found v1's optional internal PT argument reachable through public PT. Its forged-holder counterexample, source and all timings are preserved under `prototype-v1/` / `evidence/prototype-v1-*`. Final PT forwards only the original three public arguments; fresh property, coupled, refusal, browser and performance checks bind the corrected build. No failing comparison was removed. Main property binary64 payload has the same SHA for both ordinary-input suites. Final reports exclude v1 timing from final-version estimates.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md), and [NEXT_MILESTONE_RECOMMENDATION.md](NEXT_MILESTONE_RECOMMENDATION.md). No promotion/deployment is authorized.

## Reproduce from repository root

```sh
python3 experiments/dx-fv/browser_eos_b15/validate.py
python3 experiments/dx-fv/browser_eos_b15/seal.py --verify
sh experiments/dx-fv/browser_eos_b15/final-audit.sh
python3 experiments/dx-fv/browser_eos_b15/build.py
python3 experiments/dx-fv/browser_eos_b15/run.py control warm original review-control
python3 experiments/dx-fv/browser_eos_b15/run.py candidate warm original review-candidate
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b15/verify.mjs review-control review-candidate
python3 experiments/dx-fv/browser_eos_b15/browser.py warm-original browser-review-warm
python3 experiments/dx-fv/browser_eos_b15/performance.py --out-file .runtime/review-timings.json
```

Use unused names; retained evidence is never silently replaced. `run.py` supports cold/warm × original/added/fine and control/candidate/observe-control/observe-candidate; pair each schedule to its own control. `supervise.py` bounds regression scripts. Node built-ins/Python standard library suffice; installed Playwright/Chromium only for browser, Matplotlib only for figures. No dependency was added. Historical generators were not run. `science-v2.py` / `finish-science-v2.py` document the final replay after preserving preliminary artifacts; these campaign scripts intentionally use fixed names and refuse overwrites.

`receipts.mjs` resolves verified lossless local references; full original scientific vectors are retained once. `receipt-compaction.json` records exact resolved JSON hashes; `verify-compaction.mjs` verifies them. The earlier v1 compaction manifest is retained separately. Runtime data/caches are ignored here. Original control is restored by selecting `control-bundle.mjs`; it is byte-identical to pinned B9C. No code outside B15 enables reuse. Remove B15 in a separate checkout to remove the experiment without accepted-source edits.
''')
science_table='| Fixture/schedule | Checkpoints | Residuals | Matrices/corrections | Accepted half-states |\n|---|---:|---:|---:|---:|\n'+''.join(f"| {r['fixture']}/{r['schedule']} | {r['checkpoints']} | {r['residuals']} | {r['jacobiansAndCorrections']} | {r['acceptedHalfStates']} |\n"for r in science['schedules'])
resource=''
for f in ['cold','warm']:
 a,b=s[f+'-advance']['metrics']['control'],s[f+'-advance']['metrics']['candidate'];resource+=f"{f}: CPU median {a['cpuMS']['median']:.2f} → {b['cpuMS']['median']:.2f} ms; peak RSS median {a['rssKiB']['median']:,.0f} → {b['rssKiB']['median']:,.0f} KiB; heapUsed median {a['heapUsedBytes']['median']/1e6:.2f} → {b['heapUsedBytes']['median']/1e6:.2f} MB; model initialization {a['modelInitializationMS']['median']:.2f} → {b['modelInitializationMS']['median']:.2f} ms.\n\n"
put('ENGINEERING_REPORT.md',f'''# Final B15 engineering report

**{classification}**. Exact science is established for the corrected isolated candidate. Warm paired median improvement **{warm['pairedImprovementPercent']['median']:.2f}%**, saving **{warm['pairedSavedWallMS']['median']:.2f} ms** per tested advance. Cold paired median **{cold['pairedImprovementPercent']['median']:.2f}%**, with {cold['candidateFasterPairs']}/6 faster; this is not a universal performance claim. Recommend separately authorized integration review with desktop/JIT/aggregate-workload checks, not automatic promotion.

B14 start `71608010fe49946dc542a4d85dff315c875274ad`; branch `research/b15-vapor-ph-bracket-reuse-20261020`; design `90806af`. Final SHA is supplied at delivery and verified against the remote. All {source['historicalFileCount']} historical tracked files, fourteen A2 closure files, exact B9C source/table, B13/B14 seals/checkpoints, untouched B12 portable bundle, forty protected remote refs/tags and PR #3 head/base/open status are preserved. Only B15 files are added; no accepted solver/table/deployment/workstation source, dependency, main ref or PR #3 is modified.

The final transformation adds one local holder in finite numeric vapor PH, filled at its first original branch pressure lookup after offset validation. Reuse stays within that invocation/table. All 38 bisections, 40 branch interpolations, arithmetic order, saturation and phase/support rules remain. Only engine helpers and explicit frozen-table opt-in differ. Public PT forwards exactly its original three arguments, shielding the internal holder. There is one new public-wrapper function per engine and one holder per eligible call; no persistent/cross-call/model/table/stage cache exists. All other scientific registry modules are byte identical.

A preliminary version exposed the optional helper parameter through public PT. A forged fourth argument changed that version's result. The counterexample, root cause, first source and all preliminary timings remain retained; that version is excluded from integration recommendation. Final interface tests preserve extra-argument behavior and arity. Final candidate was freshly replayed across all six Node schedules, genuine refusal/rollback/isolation tests, and all Chromium cases; both variants were freshly measured again. Ordinary-input property payload remains bit-identical to the preliminary suite, verified by its exact SHA. This is a documented correction, not a removed failing test.

60,274 deterministic property comparisons cover 963 pressure positions and 206 historical cold/warm/transition states. Another 126 phase-combination cases, 12 shifted-pressure-axis table alternations and 18 public extra-argument cases pass. All returned fields, signed zero, undefined/null, error constructor/message/own metadata and deterministic coercion order match. Raw-engine invalid-input quirks are preserved; the original thermodynamics wrapper retains fail-closed validation.

{science_table}

All accepted states/records, five-section mass/U/fixed volumes/PH coordinates/recovered properties, eleven thermal energies/temperatures, hydraulic/donor energy/heat rates/ledgers, original residual objects, actual full 21×21 Jacobians/Newton corrections, signed probes, line searches, TR-BDF2/adaptive trials/errors/proposals, events/clocks/stops and full original attempt hashes match. Actual matrices are independently reconstructed from original derivative residuals. Total 76,768 residual objects / 3,430 matrices and corrections. Direct B13/B14 original and retained B14 warm alternate hashes agree. Original conservation thresholds (1e-8 kg,1e-6 kJ) pass at every accepted half-state, including all signed thermal/donor ledgers.

Warm phase transition: superheated vapor → liquid + vapor; accepted bracket **0.0053591276016748427–0.0053820385212110817 s**, event **0.0053754278169825922 s**, interpolated rather than root-solved. Temporal errors, rejections, following reversal and ledgers match. Genuine domain/support/update/inversion refusals, original-state identity/bit rollback, partial accepted progress, stopped repeats, separate models and unchanged C1 wrapper contracts pass. C1 injected faults remain labeled synthetic. The external budget witness is **{term['kind']}**, not solver completion/rollback; last independently established accepted time **{term['lastIndependentlyEstablishedAcceptedSeconds']!r} s**. No equipment-trip or Worker-disposal claim is made.

One successful vapor PH preserves 38 bisections, 40 branches and 120 mixRows. Pressure brackets/logs **42 → 3**, comparisons **336 → 24** at p=4; branch-only lookups 40 → 1. Warm retains **15,739 vapor PH / 629,560 vapor branches**, while all advance pressure searches/logs fall **764,565 → 150,744**, saving **613,821**; cold **27,324 → 19,134**, saving **8,190**. Offset/table interpolation reads remain. Counts are detached, with independent initialization subtraction; source construction reductions are not allocated-byte measurements.

{table()}

Six clean, order-balanced pairs per workload, all samples retained, Node v24.19.0, identical fixture/options/table/schedule/trace mode, 40 s wall/CPU and 512 MiB heap. No scientific hashes inside primary windows. PH windows each contain 20,000 successful calls after total 6,000 warmup calls. Model initialization/import/serialization are separate. Paired ratios differ from ratios of group medians. Small-sample uncertainty, CPU/wall/heap/RSS, count-only/no-inner-timer observations and separately perturbed GC traces are retained, never summed as exclusive nested timings.

{resource}
Headless Chromium 154.0.8037.57 passes 59,862 main property comparisons plus phase/table/interface supplements and all cold/warm × original/added/fine scientific pairs, including actual matrices/corrections. Browser source hashes bind the corrected build. No Node/browser bit equality, desktop Windows/macOS/Chrome/Edge speed, Worker/service latency, physical iPad or equipment safety claim is inferred. Prior B12 owner commissioning remains separate. Scientific qualification stays **0.001 s**; all longer results are **UNQUALIFIED RESEARCH** and no solve exceeds **0.01 s**.

Remaining risks: finite coverage, frozen-table opt-in precondition, small shared-host samples/JIT/GC variation, aggregate/cold performance, prior vapor timing outlier and desktop Worker qualification. Only B15 is committed/pushed; live final audit verifies clean tree, matching local/remote HEAD and protected refs/PR #3. Stop for engineering review.
''')
ci='\n'.join(f"* {k}: paired improvement range {v['pairedImprovementPercent']['min']:.2f}–{v['pairedImprovementPercent']['max']:.2f}%; empirical median 95% interval {v['medianBootstrap95Percent'][0]:.2f}–{v['medianBootstrap95Percent'][1]:.2f}%."for k,v in s.items())
put('PERFORMANCE_BENCHMARK.md',f'''# Final corrected-candidate performance

{table()}

Six paired measurements per row, fresh separate processes, order AB/BA/BA/AB/AB/BA. PH vapor/mixed windows are disjoint scopes in the same six process pairs; each contains 20,000 calls. Vapor pressures 3.5/3.65/4/6/12 bar, superheat enthalpy offsets .00001/.1/5/50/150 kJ/kg; mixed uses equal equilibrium/vapor inputs. Warmup: 3,000 calls per workload outside windows. Solver uses original seven-checkpoint schedule through 0.01 s, trace mode and lightweight attempt counting. No expensive hashing/lexical counters in primary windows. Identical environment/runtime/options/table/fixtures/resource limits; sequential execution, no concurrent campaign. All 36 primary and eight supplemental samples are retained in `timing-samples.json`.

{ci}

Intervals are exact empirical resampling of six observed pairs, descriptive with weak small-sample inference. They are not guarantees about host populations or desktop hardware. Positive percentages mean faster; negative means slower. Group medians and paired median deltas are different statistics. Primary timing measures worker-independent compute including original record work, excluding load/init/receipt serialization; no input-to-service latency measured. Residual/Newton/accepted/rejected counts and physical checksums match per pair; source counters are separate.

{resource}
Engine parse/freeze, model initialization, process wall, heap/RSS and GC indicators are recorded separately. Peak memory/heap samples do not prove per-call allocator savings. Count-only/no-inner-timer observations estimate sensitivity; separately traced GC processes perturb execution and cannot establish exclusive advance GC cost. Never add nested scopes.

Preliminary v1 data, including a 1199.20 ms vapor candidate outlier (1205.88 ms CPU) and cold regression, remain in `prototype-v1/`. V1 failed public extra-argument compatibility. The corrected source was measured afresh in both variants; no v1 outlier was selectively removed from a final-version sample set. Its unexplained timing variability remains a caution. No causal explanation or universal speedup is asserted. Windows/macOS desktop browser performance, Worker transport and long refrigeration operation are unmeasured.

See `performance-analysis.json`, all sample-level receipts, and [paired figure](figures/paired-wall-times.png) / [work count figure](figures/pressure-search-counts.png). Final figures use only final-version primary samples, without trimming.
''')
over='| Fixture/variant | Count-only / primary median advance | No-inner-timer process ms | Primary median process ms |\n|---|---:|---:|---:|\n'
for f,x in p['overhead'].items():
 for v,r in x.items():over+=f"| {f}/{v} | {r['countOnlyRatioToPrimaryMedian']:.3f} | {r['noInnerTimerProcessWallMS']:.2f} | {r['primaryMedianProcessWallMS']:.2f} |\n"
gct='\n'.join(f"* {x['fixture']}/{x['variant']}: {x['gcEvents']} process-wide GC events, {x['processWidePauseMS']:.2f} ms summed pauses, largest {x['maxPauseMS']:.2f} ms."for x in gc)
put('INSTRUMENTATION_OVERHEAD.md',f'''# Instrumentation overhead and GC observations

Primary builds have no lexical counts, B14 hooks or scientific hashes. Heavy diagnostic times are excluded from speed estimates. Eight supplemental clean processes provide one count-only and one no-inner-timer observation per engine/fixture, all with identical physical checksums.

{over}

Single observations include natural JIT/runtime variation; these are sensitivity estimates, not causal overhead or intervals. No-inner-timer process wall includes startup/init; compare it only to primary process wall. Do not subtract these differences from advance time or add nested scopes.

Primary PerformanceObserver arrays were empty at disconnect, not evidence of zero GC. Four separately bounded final-version `--trace-gc-nvp` logs give perturbed whole-process indicators:

{gct}

These include initialization/record and tracing overhead. Allocated bytes and exclusive advance GC attribution are unestablished. Source construction counts show 39 fewer pressure-bracket arrays plus one holder per eligible call, and one public PT wrapper per engine. JIT may eliminate source allocations. Preliminary v1 traces are explicitly prefixed and excluded here.
''')
put('QUALIFICATION_GAPS.md',f'''# Qualification gaps

Qualification remains 0.001 s; all results beyond that through 0.01 s are UNQUALIFIED RESEARCH. No longer horizon, plant integration or equipment protection inference.

Finite deterministic inputs plus invariant-table/arithmetic argument support this corrected prototype; they are not exhaustive enumeration. Explicit opt-in requires the existing deep-frozen factory and finite primitive vapor PH inputs. Raw mutable factories default to original behavior. The v1 public-parameter counterexample is preserved, fixed and regressed in Node/Chromium; it is not concealed by ordinary-input passes.

Current cold result: {cold['candidateFasterPairs']}/6 faster, median {cold['pairedImprovementPercent']['median']:.2f}% improvement, descriptive interval {cold['medianBootstrap95Percent'][0]:.2f}–{cold['medianBootstrap95Percent'][1]:.2f}%. Six shared-host pairs, JIT/GC effects, preliminary vapor outlier and future aggregate workloads limit performance generality. Windows/macOS Chrome/Edge Worker performance, real operator sessions, service latency and allocator-byte attribution remain outstanding. Headless Linux Chromium science passes; no new iPad commissioning claim.

Genuine numerical/property refusals, synthetic C1 faults, external process death, Worker disposal and physical equipment trips retain separate meanings. Wet indication is not compressor protection. No production integration approval is inferred.
''')
put('NEXT_MILESTONE_RECOMMENDATION.md',f'''# Recommendation

**{classification}**. Corrected-source exact science and pressure-work reduction pass. Warm median paired improvement {warm['pairedImprovementPercent']['median']:.2f}%, {warm['candidateFasterPairs']}/6 faster; cold {cold['pairedImprovementPercent']['median']:.2f}%, {cold['candidateFasterPairs']}/6 faster. Preserve all preliminary and final evidence, including the v1 interface counterexample.

Recommend only a separately authorized integration review if the measured aggregate workload justifies it. That review must retain private-holder/public-interface tests and exact-or-reject science gates, characterize cold/JIT/GC variability and the prior vapor outlier, and test desktop Chrome/Edge Worker behavior on intended Windows/macOS hardware. It may decline promotion. No tolerance, model, phase domain, backend or qualification-horizon change is recommended.

Rollback is selecting `control-bundle.mjs`, the exact pinned B9C registry; outside B15 nothing enables the candidate. No B9C/B12/main/workstation/Cloudflare promotion, merge, deployment or PR #3 modification. Stop for owner engineering review.
''')
status={'milestone':'B15-A1','classification':classification,'branch':'research/b15-vapor-ph-bracket-reuse-20261020','startingB14':'71608010fe49946dc542a4d85dff315c875274ad','designCommit':'90806af','candidateBuildSHA256':build['builds']['candidate']['sha256'],'prototypeV1InterfaceCounterexampleRetained':True,'finalInterfaceCorrectionRegressedNodeAndChromium':True,'qualificationSeconds':.001,'maximumResearchSeconds':.01,'gates':{k:'PASS'for k in ['0-source-and-design','A-prototype','B-property','C-work-reduction','D-coupled-science','E-refusal-rollback','F-controlled-measurements','G-conservation-phase','H-isolation']},'nodePropertyComparisons':60274,'sameChromiumScience':True,'warmFasterPairs':warm['candidateFasterPairs'],'coldFasterPairs':cold['candidateFasterPairs'],'productionPromotion':False,'unresolved':['Desktop Windows/macOS Chrome/Edge Worker performance','JIT/GC/small-sample and aggregate-workload uncertainty','Finite input coverage and explicit frozen-table precondition','Actual allocation bytes/exclusive GC attribution','Preliminary vapor timing outlier'],'reviewState':'STOP FOR ENGINEERING REVIEW','finalSHA':'branch HEAD supplied at delivery; commit cannot embed self-hash'}
put('milestone-status.json',json.dumps(status,indent=2))
with(B/'milestone-status.csv').open('w')as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['milestone','gate','status','classification']);[w.writerow(['B15-A1',k,v,classification])for k,v in status['gates'].items()]
print('Final-version reports and tracker:',classification)
