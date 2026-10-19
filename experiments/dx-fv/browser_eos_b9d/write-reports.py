"""Reports derived from sealed source review and actual-browser receipts."""
import csv,gzip,json,statistics,struct
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
review=json.loads((E/'review-summary.json').read_text())
shadow={n:json.loads(gzip.decompress((E/f'shadow-{n}.json.gz').read_bytes())) for n in ['chromium','webkit']}
assert all(d['passed'] for d in shadow.values())
def write(name,text):(B/name).write_text(text.strip()+'\n')
def stats(a):return f"{statistics.median(a):.2f} [{min(a):.2f}–{max(a):.2f}], n={len(a)}"
decisions={'A_B9C_HARDENING':'PASS','B_A2_WORKSTATION_FIELD_MAPPING':'VERIFIED','C_WORKER_DISPLAY_CONTRACT':'PASS','D_ISOLATED_READ_ONLY_SHADOW_PROTOTYPE':'PASS','E_SCIENTIFIC_PARITY':'PASS','F_FAILURE_ROLLBACK':'PASS','G_CHROMIUM':'PASS — local HTTP; native-file/offline startup unavailable','G_DESKTOP_WEBKIT':'PASS — local HTTP; native-file/offline startup unavailable','H_FIRST_SHADOW_HOOKUP_READINESS':'CONDITIONAL GO — served isolated research only; explicit engineering review and deployment target selection','I_EXISTING_WORKSTATION_INTEGRATION':'NO-GO','J_PRODUCTION_LIVE_PLANT':'NO-GO'}
classification='B9D HARDENING & SHADOW-BRIDGE FEASIBILITY PASS'
status={'milestone':'B9D','classification':classification,'decisions':decisions,'startingCommit':'b67afb3215075b2ec82bef376d39e03953dc0da2','branch':'research/browser-eos-b9d-hardening-hookup-readiness-20261018','prerequisiteGateCommit':'6d9bb14cf708630d9f48dce085179a77172efd99','scientificAlgorithmChanged':False,'optimizedBackend':'original owned accepted table only','researchHorizonSeconds':.001,'physicalIPadTested':False,'offlineWorkstationPackaging':'OPEN / NOT COMPATIBLE AS CURRENT MULTI-FILE ARTIFACT','mergeAuthorized':False,'deploymentAuthorized':False,'nextMilestone':'After explicit review, select offline/browser packaging and design one opt-in workstation shadow panel with independent session/history and original training/history/Assist/control preservation tests.'}
status['performanceScope']='Worker responsiveness retained; observed cold compute overhead versus bare B9C, cause unisolated; no zero-overhead or real-time claim.'
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
with (B/'milestone-status.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['decision','result']);w.writerows(decisions.items());w.writerow(['overall',classification])
matrix=[]
for n,d in review.items():
 for f,v in d['fixtures'].items():matrix.append(f"| {n} | {f} | EXACT / saved B9C match | {v['work']['residuals']} | {v['work']['accepted']} | {v['work']['rejected']} |")
write('SCIENTIFIC_PARITY_MATRIX.md','''# Scientific parity

**PASS**, same-engine exact binary64 comparison. No tolerance replaces equality.

| Browser | Fixture | Full scientific result | Residual evaluations | Accepted half-steps | Rejected requests within adaptation |
|---|---|---|---|---|---|
'''+ '\n'.join(matrix)+'''

Both browsers additionally pass ten original B9C and fourteen additional supported paired scenarios (24 per browser), 31 original PH support/phase cases, four refused updates and the original missing liquid-row statePT refusal. `review-*.json.gz` retains full states, records, attempts and component hashes. Cold/warm science hashes match the original saved B9C same-browser controls, which retain the earlier B9B/B9A chain. Every additional pair compares complete state/record/attempt encoding and full residual return, Jacobian/correction and converged-stage hashes.

Compared scientific content: section M/U/V and guesses; recovered p/T/h/rho/u, phase/quality/wet; six refrigerant faces; eleven thermal energies/temperatures; heat/enthalpy/mass rates; all residual inputs/outputs, signed FD, matrices and Newton decisions; TR-BDF2 stages; accepted/rejected histories and time errors; conservation ledgers; events, schedules, clocks, domain evidence and final accepted physical state. Original record audits independently recompute signed thermal closure and section/aggregate residuals. Fresh original creates reproduce independent initial state.

The shadow worker matches all four original control checkpoint hashes per fixture (0, .0001, .0005, .001 s) in each browser. `shadow-*.json.gz:science` records these hashes plus source projection audits and verification of all 81 current numerical/phase/wet display cells and historical rows. `shadow-tests.mjs::verify` explicitly maps each field to original record/cells before formatting. Detached mutation cannot change the worker. Raw source science remains available in the review receipts; no rounded display number is a comparison input.

Preserved budgets: canonical p≤0.1 Pa, h≤0.1 J/kg, T≤1e-4 K; normalized fluid mass/energy≤1e-11; standalone p<10 Pa, h<50 J/kg, T<.01 K; original independent reference resolution 1e-5 Pa / 1e-8 J/kg. Section/aggregate mass <1e-8 kg and energy <1e-6 kJ; original thermal nonlinear closure 1e-12 K. Original .3–35 bar absolute, subcool/superheat support, 200–400 K thermal domain, 21 coordinates, finite differences, Newton, TR-BDF2, adaptation and rollback remain unchanged. Complete standalone/reference campaigns are preserved by source/artifact identity, not newly rerun. No EOS repair, new acceptance, pressure epsilon, property substitution, added quality clipping or alternate step.
''')
cases=review['chromium']['cases']
write('BOUNDARY_AND_PHASE_REGRESSIONS.md','''# Bounded supported regressions

**PASS** in Chromium and desktop WebKit; same-engine control/candidate exact.

| Scenario | Both browsers |
|---|---|
'''+ '\n'.join('| '+c['name']+' | EXACT |' for c in cases)+'''

Original cold/warm nonzero-exchange fixtures retain .0001/.0004/.0005 requested intervals to .001 s and naturally reject one/three accuracy trials. Other cases remain bounded to .0002 s; scheduled patches occur at .0001 and .0002 s. Additional saturated liquid/vapor and x=.25/.75 inlet/outlet cases derive h from the original saturation interface; they are valid prescribed boundaries, not fabricated phase coordinates. Superheated inlet uses original statePT at Tsat+20 K. Original B9C also covers genuine x=.4 mixture and superheated outlet. All fourteen additional trajectories return without stop in both browsers, including strict valid .3/35-bar inlet boundaries.

Original reversal verifies negative inlet/outlet flows and actual reversed outlet donor h=1700 kJ/kg in energy transport. Manual inlet-only/outlet-only and sequential scheduled changes use model.update/original schedule, preserving boundary event times and state ownership. New stages see the changed boundary; no stage cache survives.

Strict PH tests retain .3±1e-12 / 35±1e-12 bar, endpoints, nonfinite/zero pressure, supported hf/hg and subcool/superheat edges and original refusals. Unsupported enthalpies and missing liquid rows refuse through the original applicable interfaces. Missing-row statePT is not falsely represented as a PH failure: original PH branchLimit avoids those rows. Valid update interfaces reject unsupported inputs before spec/state installation. These negative tests establish original refusal semantics, not new supported physical phases.

Genuine outward thermal 200/400 K fixtures retain original confirmed domain proof and exact no-commit physical/identity rollback. Numerical-stop fixtures deliberately use existing maxIterations=1/maxAttempts=20 only for fault tests, never cold/warm timing/qualification. They may retain earlier accepted substeps; per-rejection rollback is distinct from reverting an entire requested interval. Restart and repeated record generation compare exactly. Scope is local phase/boundary regression, not inventory-wide phase/topology or full A2 qualification.
''')
write('FAILURE_AND_ROLLBACK.md','''# Failure, accepted state and lifecycle

**PASS** in both actual browsers. Original C1 local and six B9A C1 session scenarios are rerun unchanged through original controls. These retain typed numerical/unproved property classification, persistent 20 attempts / 19 halvings to 1.9073486328125e-9 s with the original 1e-9 floor, per-rejection physical bits and object identities, record refusal and genuine independent thermal exits. Synthetic dispatch/injection evidence is labeled; it is not natural EOS phase qualification. B9C optimized ownership refuses injected/CoolProp engines and is never installed into C1.

| Shadow case | Verified outcome |
|---|---|
| Numerical refusal after supported work | No new successful snapshot; original stopped state/record exactly match unchanged control, including legitimate prior accepted substeps. Prior display stale with its original clock. |
| Thermal 200 / 400 K outward exit | Original confirmed proof, zero new commits, exact physical bits and cells/energy/ledger identities preserved. |
| Latest after fault | Refuses fresh success; retained stale snapshot and failure evidence remain. |
| Duplicate advance | Client refuses second outstanding physics request; identical raw request ID replays original result without executing twice. Altered duplicate refuses. |
| Out-of-order / stale request | Raw worker sequence and expected-version refusals preserve state. |
| Out-of-order response / stale snapshot | Production reducer tests with genuine snapshot copies and synthetic transport envelopes cannot clear newer fault or install older version/session. No synthetic physics is displayed. |
| Stop during pending advance | Actual worker FIFO accepts already-dispatched synchronous work before stop acknowledgement; no mid-stage cancellation claim. Further advance refuses. |
| Dispose after error | Releases state/model/attempt/cache references, acknowledges original clock, then terminates worker. |
| Worker termination / communication deadline | Explicit termination retains stale readings; actual termination during pending work reaches lost status and rejects pending work. Shortened 50-ms test deadline tests semantics, not startup/performance acceptance. Normal deadline is 30 s. |
| Restart / view lifecycle | New session exactly recreates original independent fixture, clears prior-session DOM before initialization, ignores old identities; pagehide clears heartbeat/frame callbacks and terminates worker. |
| Missing scientific bundle | unqualified-backend, null snapshot, original fetch diagnostic. |
| Browser offline / native file | Failure reported; no illustrative substitute or fabricated continuation. |

Important retained finding: maxIterations=1 fault fixture accepts 18 half-steps before stopping in the tested request. Requiring whole-request rollback was a test error. Correct behavior keeps those accepted steps authoritative, emits no new successful display snapshot after refusal, retains the older displayed timestamp and separately reports current accepted time/version. Unchanged-control comparison proves the stopped state, rather than deleting valid progress. Thermal no-commit tests and original C1 per-rejection checks prove exact rollback at their proper scope.

Iteration receipts remain: `review-path-failure*` is a relative-fetch test packaging error; `shadow-cell-count-failure*` is an incorrect test count (actual 81 display cells); `shadow-whole-request-assumption*` records the mistaken whole-request rollback assertion. `shadow-before-lifecycle-extension*` passed before additional restart-DOM/pending-termination coverage. Final `shadow-*.json.gz` includes the completed tests. No optimized scientific source was repaired. Restart DOM cleanup is a B9D presentation fix only.

The final interface also refuses overlapping initialization, shares duplicate disposal acknowledgement, refuses new commands once disposal begins and synchronizes accepted version/time even when an original advance throws after prior commits. These are B9D lifecycle protections, not scientific changes. `shadow-before-disposal-hardening*` retains the preceding pass. `performance-key-order-failure*` records an evidence-hash object-key order mistake (`state,record` versus original `record,state`), corrected without changing any values.
''')
perf=[];detail=[]
for n,d in shadow.items():
 for p in d['primary']:
  metrics=p['metrics'];init=next(m for m in metrics if m['type']=='initialize');adv=[m['timing']['advanceMS'] for m in metrics if m['type']=='advance'];trans=[m['delivery']['transferAndDispatchMS'] for m in metrics]
  before=sum(x['advanceMS'] for x in p['B9CBefore']['timing']);after=sum(x['advanceMS'] for x in p['B9CAfter']['timing'])
  perf.append(f"| {n} | {p['fixture']} | {init['delivery']['roundtripMS']:.2f} | {', '.join(f'{v:.2f}' for v in adv)} | {before:.2f} / {sum(adv):.2f} / {after:.2f} |")
  detail.append(f"| {n} | {p['fixture']} | {stats(trans)} | {stats(p['render'])} | {stats(p['heartbeat'])} | {stats(p['frames'])} | {stats([x['ackMS'] for x in p['input']])} |")
write('PERFORMANCE_AND_RESPONSIVENESS.md','''# Bounded responsiveness and lifecycle measurements

Actual primary display, original trace/observer generation, fresh workers. Milliseconds; all samples retained in shadow browser receipts. No startup/FPS threshold is invented. One sequential B9C→shadow→B9C bracket per fixture/browser is descriptive, not a population estimate or repeated B9C performance campaign.

| Browser | Fixture | Initialize + first t=0 snapshot RTT ms | Three original advance compute ms | B9C before / shadow / B9C after compute sum ms |
|---|---|---|---|---|
'''+ '\n'.join(perf)+'''

| Browser | Fixture | Transfer + dispatch | Render | 10-ms heartbeat gaps | rAF frame gaps | Trusted input acknowledgement |
|---|---|---|---|---|---|---|
'''+ '\n'.join(detail)+'''

Cells contain median [minimum–maximum], n. First accepted snapshot is the genuine initialized t=0 record, not a successful advance. Initialization components separate asset hash verification, module/owned-table construction and create+record. First-advance RTT, every per-command service/transfer/roundtrip sample, stop acknowledgement, disposal and fresh initialization remain in raw evidence. Transfer+dispatch uses correlated timeOrigin+performance.now across worker/window and includes clone, scheduling and message delivery; it is not an isolated network or memcpy benchmark. Render timing measures DOM projection execution; rAF measures delivered frame gaps, not physical display scanout. Input acknowledgement is trusted browser event timestamp to handler execution. Timing excludes test-only full scientific retrieval; primary display does not load diagnostic test bundles.

The worker retains the B9C algorithm and reduction in property work; exact scientific counters/checkpoint hashes remain original. Sparse timing brackets show JIT/loader/runtime variability and must not be read as guaranteed identical compute latency. The warm computation takes hundreds of milliseconds for only .001 simulated seconds; this is not real-time plant operation. The main event loop continues while it runs. Outliers above nominal 10-ms heartbeat / frame cadence are retained and shown; no smoothness or physical iPad guarantee follows. Stop queues behind synchronous work. Basic diagnostics are compact, while original full detail is test-only and can be expensive. No timing work removes record generation, observer, finite differences or conservation checks.

Disposal RTT / owner service ms: '''+'; '.join(f"{n}: {d['disposal']['delivery']['roundtripMS']:.2f} / {d['disposal']['timing']['serviceMS']:.2f}" for n,d in shadow.items())+'''. Fresh warm initialization after disposal recreates exact original state. This bounded evidence is not long-duration heap/leak qualification or device performance certification.
''')
decision_table='\n'.join(f'| {k} | {v} |' for k,v in decisions.items())
write('ENGINEERING_REPORT.md',f'''# B9D engineering disposition

**{classification}**

The independent table-only hardening review, truthful field mapping and isolated local-HTTP worker/display proof pass. Both actual browsers display genuine accepted five-section A2 data. Existing workstation integration and production/Live Plant remain NO-GO. Offline/native-file compatibility and physical iPad evidence remain open; this pass is scoped to the served research prototype.

| Independent decision | Result |
|---|---|
{decision_table}

Gate 0 verifies exact B9C start and clean tracked tree, 2874 starting file hashes, fourteen accepted A2 source bodies, B9C literal control/candidate packaging and patch, B9/B9A/B9B/C1/B6/B7 scientific artifacts, every remote head/tag identity and PR #3. Operator source is pinned to 262b6092; it is read-only reference material. Gates 1–4 and both-browser receipts were committed at 6d9bb14cf708630d9f48dce085179a77172efd99 before any shadow implementation.

Independent source reconstruction establishes the narrow synchronous owned-table equivalence, including exact keys/signed zero, recursive freeze/private registration, original validation precedence, failure clearing, flat results/no aliases and stage-local lifetime. It does not assume purity for mutable general engines or CoolProp. Runtime walks 38335 table objects, refuses unowned/injected/proxied/cross-registry engines and checks actual extracted cache mechanics. The trusted private loader/intrinsics condition is explicit. Full scientific qualification remains open where inventoried; no unsupported assumption is manufactured into a proof.

Both browsers reproduce exact same-engine saved cold/warm science and all residual/FD/matrix/stage evidence, plus 24 supported bounded regression pairs each. Every shadow source checkpoint matches the unchanged accepted control; 81 current display cells and actual accepted-history rows are checked against unrounded source values. Worker owns M/U/V and solver; display receives detached accepted projections only. Numerical/domain refusals never generate a new successful snapshot. Genuine partial accepted progress before a stop remains in worker authority and is disclosed separately from stale displayed time.

The workstation audit identifies incompatible whole-plant concepts rather than inventing values. A2 terminal bulk is not a suction vessel; finite air is not the connected room; coil totals are not plant charge; there is no compressor/condenser/receiver/actuator/safety-trip state. Original training/scoring/Assist/history and model controls are untouched. Workstation modules assume main-thread storage records and single-page lifecycle; offline build is a self-contained classic-script HTML. Current ESM worker assets fail native file / browser-offline startup. Served desktop success does not establish iPad file support.

PERFORMANCE_AND_RESPONSIVENESS.md reports startup, first snapshot, original advance computation, delivery/render, heartbeat/frame/input, disposal and restart, with all outliers and no invented threshold. Original conservation, domain and numerical budgets remain unchanged. There is no EOS repair, new property acceptance, pressure epsilon, hidden recovery, fallback plant backend, merge or deployment. Iteration failures and their scopes remain in FAILURE_AND_ROLLBACK.md; none required a scientific algorithm modification.

Next milestone: after explicit engineering review, select the intended offline/browser packaging and design one opt-in workstation shadow panel with independent session/history and tests proving original training exports, Live Plant history, Assist and controls are preserved. Do not automatically integrate, extend the horizon or start plant coupling. Stop for explicit engineering review after isolated commit/push preservation audit.
''')
write('MECHANICS_REPORT.md','''# Mechanic’s report

The readings now come off a real five-section ammonia evaporator calculation. Each section has its own calculated pressure, refrigerant temperature, mass and internal energy. The panel also shows the five tubes, five fins, finite air node, signed inlet/outlet flow and the original coil energy and mass accounting. The accepted clock only moves when the calculation accepts work. The small history contains actual accepted snapshots.

These pressures are bar absolute. A psig instrument would need the existing workstation's atmospheric subtraction before conversion. Superheat is a temperature difference; vapor quality is a mass fraction only where the original calculation provides one. A wet terminal bulk reading does not tell us a compressor is protected against liquid carryover.

The workstation's compressor status, discharge gauge, condenser, receiver level, feed-valve actuator and connected room belong to its existing illustrative plant model. This coil calculation cannot supply those readings. We leave them unavailable instead of drawing a convincing plant around an evaporator. A section inventory is not a receiver level, and coil air temperature is not a whole cold-room measurement.

The worker keeps the original refrigerant inventories and calculations. It sends a detached set of accepted readings to the panel; rounding cannot feed back into the solver. The B9C shortcut only avoids repeating an identical successful boundary property lookup within the same nonlinear stage. It does not hold the coil pressures fixed or own refrigerant state. Supported manual and scheduled boundary changes were tested through the original laboratory interfaces; new stages use the new validated boundary. This prototype gives the operator fixed cold/warm fixtures and short advance buttons, not unrestricted edits.

If recovery or the numerical solve refuses, there is no fresh successful gauge set. The old readings stay visible with a stale label and their own original time. The worker's actual accepted time and stop reason are separate. Some valid small steps can have been accepted before the stop; those remain real progress. A proven thermal-domain exit is a model limit, not an equipment safety trip. If communication is lost, the session is lost; it does not restart itself with guessed conditions.

Both Chromium and desktop WebKit ran the served panel with real computed readings and exact original-control agreement. The interface continues acknowledging input while the worker calculates, but a few tenths of a second of calculation buys only .001 simulated seconds. Stop scheduling waits for synchronous work already under way. This is a responsive research demonstration, not continuous plant-speed operation; measured delays and outliers are in the performance report. Native-file and browser-offline startup failed honestly. A physical iPad has not been tested.

We are ready to review the first isolated served shadow connection. We are not ready to wire this into the real workstation without the packaging and preservation checks in the integration contract. Compressors, condensers, receivers, controls, equipment protection, calibration and broader operating qualification still need their own engineering. The next job is selecting the actual browser/offline package and reviewing a separate coil panel that cannot interfere with existing training or plant controls. No merge or deployment is authorized.
''')
offline='\n\n## B9D actual outcomes\n\n'
for n,d in shadow.items():offline+=f"- {n} {d['version']}: local HTTP PASS; missing bundle `{d['packaging']['missingScientificBundle']['status']}` with null snapshot; browser-offline `{d['packaging']['browserOffline']['status']}` with no snapshot; native file {d['packaging']['nativeFile']['navigation']}, application module loaded={d['packaging']['nativeFile'].get('appLoaded',False)}. Exact error/status is retained in the browser receipt.\n"
path=B/'OFFLINE_BROWSER_COMPATIBILITY.md';text=path.read_text().split('\n\n## B9D actual outcomes')[0];path.write_text(text.rstrip()+offline)
extra=[]
for n in ['chromium','webkit']:
 p=json.loads((E/f'performance-{n}.json').read_text());assert p['passed']
 for f in ['cold','warm']:
  rounds=[r for r in p['rounds'] if r['fixture']==f]
  controls=[v['computeMS'] for r in rounds for v in r['samples'] if v['mode']=='control']
  bare=[v['computeMS'] for r in rounds for v in r['samples'] if v['mode']=='candidate']
  bridge=[v['computeMS'] for r in rounds for v in r['samples'] if v['mode']=='shadow']
  reduction=[100*(1-r['samples'][2]['computeMS']/statistics.mean([r['samples'][0]['computeMS'],r['samples'][4]['computeMS']])) for r in rounds]
  extra.append(f'| {n} | {f} | {stats(controls)} | {stats(bare)} | {stats(bridge)} | {statistics.median(reduction):.1f}% |')
with (B/'PERFORMANCE_AND_RESPONSIVENESS.md').open('a') as f:f.write('''
## Follow-up on measured compute overhead

The first primary brackets showed slower shadow sums than both flanking bare B9C samples. Three additional sequential control→B9C→shadow→B9C→control brackets per fixture/browser investigate that concern. They use unchanged .001-s workloads, retain all samples, compare every original control/candidate full science hash and shadow final state/record plus every original attempt diagnostic. Test-only pre-advance physical copies are outside compute timers; these follow-ups are separate from primary UI responsiveness samples.

| Browser | Fixture | Unoptimized accepted control ms | Bare B9C ms | Shadow ms | Median paired reduction versus control |
|---|---|---|---|---|---|
'''+ '\n'.join(extra)+'''

The bounded shadow retains a compute reduction versus unchanged accepted controls in every follow-up bracket. Cold shadow work is consistently slower than the bare B9C medians; warm observations overlap and vary. The cause is **OPEN**: message cadence, allocation/JIT/GC and scheduling are hypotheses, not demonstrated attribution. We do not claim unchanged wall time or zero bridge overhead. Main-thread worker separation and measured input/heartbeat responsiveness remain intact. This supports a bounded read-only feasibility result, with performance investigation required before a longer/continuous-operation claim. No numerical or property-work shortcut was introduced to improve this result.
''')
(E/'shadow-summary.json').write_text(json.dumps({'passed':True,'classification':classification,'decisions':decisions,'browsers':{n:{'version':d['version'],'packaging':d['packaging'],'science':[{'fixture':x['fixture'],'checkpointHashes':x['checkpointHashes'],'exactOriginalControlCheckpoints':x['exactOriginalControlCheckpoints']} for x in d['science']],'lifecycle':d['lifecycle']} for n,d in shadow.items()}},indent=2)+'\n')
print(classification)
