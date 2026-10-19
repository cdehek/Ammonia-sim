"""Reports from completed retained receipts; does not run models or alter science."""
import csv,gzip,hashlib,json,statistics,subprocess,re
from pathlib import Path
from audit import B,R,PINS
E=B/'evidence'
def read(n):
 p=E/n;return json.loads(gzip.decompress(p.read_bytes()) if n.endswith('.gz') else p.read_text())
def write(n,t):(B/n).write_text(t.strip()+'\n')
def stat(a):
 return f'{statistics.median(a):.2f} [{min(a):.2f}–{max(a):.2f}], n={len(a)}' if a else 'unavailable'
I={n:read(f'integration-{n}.json.gz') for n in ['chromium','webkit']};S={n:read(f'review-{n}.json.gz') for n in I};T={n:read(f'isolation-{n}.json.gz') for n in I};P={n:read(f'portability-{n}.json') for n in I};F={n:read(f'performance-{n}.json') for n in I}
assert all(d['passed'] for group in [I,S,T,P,F] for d in group.values())
assert all(x['passed'] for x in read('independent-render.json'))
reg={};new=[]
for n in I:
 a=read(f'baseline-{n}/results.json');c=read(f'candidate-{n}/results.json');assert [x['suite'] for x in a]==[x['suite'] for x in c]
 rows=[]
 for x,y in zip(a,c):
  failure={}
  for mode,r in [('baseline',x),('candidate',y)]:
   if r['code']:
    text=(E/f'{mode}-{n}/{r["suite"]}.log').read_text();failure[mode]=text[text.find('AssertionError'):][-2200:]
  sameFailure=None
  if x['code'] and y['code']:
   signature=lambda text:(text.split('\n')[0],re.findall(r'tests/[^\s]+:\d+:\d+',text)[:1])
   sameFailure=signature(failure['baseline'])==signature(failure['candidate']);assert sameFailure,(n,x['suite'],'different failed assertion')
  rows.append({'suite':x['suite'],'baseline':x['code'],'candidate':y['code'],'failureContext':failure,'sameFailedAssertion':sameFailure,'historicalVariableTrainingPauseRemainsOpen':n=='webkit' and x['suite']=='training-ui'})
  if x['code']==0 and y['code']!=0:new.append({'browser':n,'suite':x['suite']})
 reg[n]={'baselinePass':sum(x['code']==0 for x in a),'candidatePass':sum(x['code']==0 for x in c),'total':len(a),'rows':rows}
assert not new,new
(E/'regression-comparison.json').write_text(json.dumps({'newRequiredSuiteRegressions':new,'browsers':reg},indent=2)+'\n')
exits=dict(line.split('\t') for line in (E/'campaign-exits.tsv').read_text().splitlines())
for n,v in exits.items():
 if n=='portability-run' and v!='0':assert exits.get('portability-final')=='0' and 'violates the following Content Security Policy' in (E/'initial-csp-harness-portability-run.log').read_text()
 elif n not in ['baseline-webkit','candidate-webkit']:assert v=='0',(n,v)
m=json.loads((B/'preview/asset-manifest.json').read_text());rt=read('runtime-manifest.json')
status={'milestone':'B11','classification':'B11 PORTABLE SERVED-PREVIEW PASS','packageIdentity':m['packageIdentity'],'artifact':{'root':'preview/','zip':'preview.zip','zipSHA256':hashlib.sha256((B/'preview.zip').read_bytes()).hexdigest(),'runtimeAssets':len(m['assets']),'manifest':'preview/asset-manifest.json','branch':'research/b11-portable-ipad-preview-20261019'},'pins':PINS,'architectureCommit':'9b7827c7204b72bba96ec6092ac9cb4f6d9a8e91','declaredPassedExecutionTarget':'Independent static HTTP root/nested path on desktop Chromium and desktop WPE WebKit loopback; original inherited WebKit findings retained','gates':{'A_source_and_science':'PASS','B_portable_served_package':'PASS','C_workstation_preservation':'PASS','D_browser_compatibility':'SEPARATE RESULTS BELOW','E_performance_characterization':'PASS','F_physical_iPad':'NOT TESTED / AWAITING USER','G_deployment_authorization':'NO-GO'},'independent':{'portableArtifact':'PASS','exactA2ScientificParity':'PASS','originalWorkstationPreservation':'PASS','chromium':'PASS','desktopWebKit':'PARTIAL','offline':'NOT QUALIFIED','localNetworkOrigin':'BLOCKED','localNetworkDetail':'Direct cloud private-address HTTP returned 503 before app startup. Reserved nonsecure HTTP origin with locally fulfilled exact package bytes proves crypto unavailability/unqualified A2 while original operates; this is origin-policy evidence only. Owner-network device reachability UNTESTED. Trusted HTTPS feasible but not hosted/tested.','physicalIPad':'AWAITING USER','physicalIPadStatus':'AWAITING USER DEVICE REVIEW','researchPreviewDeployment':'AWAITING APPROVAL','productionMerge':'NO-GO','fullLivePlantCoupling':'NO-GO'},'normalA2HorizonSeconds':.001,'normalCheckpointsSeconds':[0,.0001,.0005,.001],'trainingExportsByteIdentical':10,'protectedHistoryFiles':read('preservation.json')['historicalFiles'],'remoteHosted':False,'originalSuites':reg,'evidence':['source-integrity.json','reproducibility.json','integration-{browser}.json.gz','review-{browser}.json.gz','isolation-{browser}.json.gz','portability-{browser}.json','performance-{browser}.json','regression-comparison.json','preservation.json']}
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
with (B/'milestone-status.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['milestone','item','status']);w.writerows(['B11',k,v] for k,v in status['independent'].items())
write('README.md',f'''# B11 — Portable workstation research preview

**{status['classification']}** for the declared desktop HTTP-served scope. Desktop WebKit remains PARTIAL for inherited application assertions. Physical iPad: **AWAITING USER DEVICE REVIEW**. Offline NOT QUALIFIED. Deployment AWAITING APPROVAL; production merge and full Live Plant coupling NO-GO.

Copy `preview/` alone to another directory/computer, or extract `preview.zip` after checking `preview.zip.sha256`. No checkout is needed to serve the result:

```sh
cd /path/to/copied/preview
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. Select **A2 Evaporator Research** in the original bottom console (scroll the tool rail if needed), expand, and initialize cold or warm. Request only .0001, .0004 and .0005 s; accepted times are 0/.0001/.0005/.001 s. Original Initialize auto DX/Start/Pause/+10 s and training use the independent original illustrative plant, never A2. The delivered interface intentionally remains B10's actual workstation.

Ordinary private-LAN HTTP does not supply B10's secure crypto APIs in the tested browsers. For an iPad use a separately approved, reachable trusted HTTPS origin, then execute PHYSICAL_IPAD_REVIEW.md. A localhost test does not establish device reachability. See PREVIEW_HOSTING_HANDOFF.md for exact server/MIME/CSP/approval requirements. No host or public URL has been created.

Package identity: `{m['packageIdentity']}`. Scientific bundle remains exact B9C. Rebuild from these Git identities:

```sh
python3 experiments/dx-fv/browser_eos_b11/build.py
python3 experiments/dx-fv/browser_eos_b11/verify-source.py
python3 experiments/dx-fv/browser_eos_b11/audit.py
python3 experiments/dx-fv/browser_eos_b11/seal-delivery.py --check
```

Build requires only Python standard library and Git objects; all browser dependencies stay ignored in B11/.runtime. Full rerun setup and campaign commands are in SOURCE_AND_BUILD_AUDIT.md. Reports/receipts include complete exact accepted-state comparisons, ten full exercise exports, original baseline/candidate logs, viewport screenshots, independent root/nested serving and matched B10/B11 performance. Read ENGINEERING_REPORT.md before interpreting this scoped pass.
''')
write('SOURCE_AND_BUILD_AUDIT.md',f'''# Source and build audit

Starting branch/HEAD were verified at exact B10 `{PINS['B10']}` with a clean tracked/untracked tree before B11 additions. New isolated B11 branch was created there. Gate 0 hashed all {status['protectedHistoryFiles']} starting tracked files and their Git blobs, recorded refs/tags/remote heads and PR #3, and verified all fourteen accepted A2 closure files. Architecture and source audit were committed at `{status['architectureCommit']}` before functional packaging.

| Protected source | Exact SHA |
|---|---|
'''+ '\n'.join(f'| {k} | {v} |' for k,v in PINS.items())+f'''

`build.py` reads immutable Git blobs; twelve generated runtime assets plus the JSON manifest total {(sum(a['bytes'] for a in m['assets'])+(B/'preview/asset-manifest.json').stat().st_size):,} bytes. Seven literal specifier replacements across index/service/snapshot/view are recorded individually in the manifest (counts included). All other bytes are preserved. `verify-source.py` reverses every relocation and B10 insertion to exact original HTML SHA-256 `0485cdf94b22101f976e365d6e5099bb3f8e15669914d5c12038e3eb37147945`. It verifies the complete local static import graph and forbids unmanifested package files. The complete original 574-file input manifest is freshly verified against the original Git blobs and SHA-256s by verify-source.py; B10's original build receipt also remains protected by starting hashes. No original script/model/training source is rebuilt or edited.

B9C bundle SHA-256 `f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919`; it contains the required literal property tables, engine, accepted A2 mechanics/fixtures and exact B9C boundary-PH optimization. No EOS downloads or thermodynamic service is involved. B10's hash verification and owned worker remain unchanged. Source/build identity and each Git blob, SHA-256, source/target path, bytes, MIME and relocation are in `preview/asset-manifest.json`; ASSET_MANIFEST.md additionally hashes the JSON manifest. No timestamp or checkout path enters the runtime artifact.

Two builds to different output directories produced identical complete file maps and identical ZIP bytes (`evidence/reproducibility.json`). ZIP is sorted, has fixed timestamps/modes and uses stored entries to avoid compressor-version dependence. Check `preview.zip.sha256`. `seal-delivery.py` hashes all nonignored B11 delivery files excluding its own seal; Git seals that inventory. No node_modules, browser downloads, caches or environments are committed.

## Optional full verification setup

Run from repository root, with Internet access only for test tooling installation. Use the same Playwright versions and isolated libraries for matched historical browser receipts:

```sh
python3 -m venv experiments/dx-fv/browser_eos_b11/.runtime/venv
experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/pip install playwright==1.62.0
python3 experiments/dx-fv/browser_eos_b11/prepare-tests.py --install-node
PLAYWRIGHT_BROWSERS_PATH="$PWD/experiments/dx-fv/browser_eos_b11/.runtime/browsers" experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python -m playwright install chromium webkit
experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/setup-runtime.py
python3 experiments/dx-fv/browser_eos_b11/prepare-verification.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/run-integration.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/run-scientific-review.py
bash experiments/dx-fv/browser_eos_b11/run-verification.sh
python3 experiments/dx-fv/browser_eos_b11/write-reports.py
```

The host-requirement skip selects the actual WPE binary with the exact B10-pinned extracted libraries, without modifying browser security. Runtime executable hashes/versions and host resource limits are in runtime-manifest.json. Chromium {I['chromium']['version']}; desktop WPE WebKit {I['webkit']['version']}; Python Playwright 1.62.0, Node Playwright 1.62.1. Original assertions are literal pinned suites in disposable Git archives. B11 test adapters change only URLs, output roots, runtime selection and additional exact B10 comparisons; `test-adapter-derivation.json` records their diffs. Scientific review reuses unchanged B9C/B9D harnesses and compact B10 evidence retention to bound memory. No physical equations/limits or original assertions are weakened. All large browser campaigns ran sequentially on a {int(rt['memoryMaxBytes'])/2**30:.0f}-GiB cgroup host.

An initial sandbox lacked local socket permission; the failure log remains. Enabling ordinary network access for the server/browser process resolved that environment issue. The first packaging run exposed a missing B9D view dependency; its failed receipt is retained and the final build closes that exact import without source edits. A later CSP probe exposed Playwright string-wait eval, resolved by test-only direct polling with no CSP/security change; its original failure and final follow-up remain separate. Direct private-address transport also returned 503 before the application loaded; that failure is separately retained, and nonsecure API behavior is qualified only by a labeled local-interception origin-policy test, not peer-device reachability.
''')
# Seven replacement occurrences: index1 + service2 + snapshot2 + view2.
science=['# Exact scientific parity','', 'PASS against saved B10 same-browser references and original accepted controls. Every normal cold/warm session stays within 0/.0001/.0005/.001 simulated seconds. Cross-browser bit equality is not assumed.','', '| Browser | Fixture | Saved B10 state + record | Attempt hashes | Residuals | Accepted half-steps | Rejections |','|---|---|---|---|---:|---:|---:|']
for n,d in I.items():
 for row in d['science']:
  assert row['exactSavedB10AcceptedStateRecordAndAttempts'];v=row['rows'][-1]['work'];science.append(f"| {n} | {row['fixture']} | bit-exact at all four times | exact | {v['residuals']} | {v['accepted']} | {v['rejected']} |")
science+=['','`production-projection-parity.json` also compares actual production panel final projections and all accepted history to saved B10, excluding only the fresh session UUID. `integration-{browser}.json.gz` retains complete exactly encoded accepted state/record at every checkpoint, original attempt hashes, source-to-render comparisons and saved-control identity. `review-{browser}.json.gz` retains full science/component hashes from the unchanged exhaustive harness, ten original and fourteen additional supported paired regressions and C1 refusal/rollback contracts. Original raw reference arrays remain protected in B9C/B9D; no rounded gauge is used as a reference.','', 'Coverage: five refrigerant M/U/V inventories and pressure/enthalpy states, eleven tube/fin/air nodes and energies, original face/heat fluxes and ledgers, conservation budgets, 21 coordinates, signed finite differences, Newton/Jacobian/correction/line search, both TR-BDF2 stages, error/step proposals, accepted/rejected trials and exact physical/object rollback. Support limits, phase/refusal rules, PH/MUV recovery and exact B9C boundary PH reuse are unchanged.','', 'Owned-table hardening passes in both browsers: 38,335 recursively frozen objects, unowned/injected/proxy/other-registry/null refusal, signed zero/exact key/nonfinite rules, failed-cache exclusion, two-slot clearing and independent new closures. These are trusted-registry mechanical eligibility checks, not hostile-code sandbox claims. No property substitution, EOS repair, optimizer, CoolProp backend or extended A2 campaign is introduced.']
write('SCIENTIFIC_PARITY_MATRIX.md','\n'.join(science))
reglines=['# Original workstation regression','', 'PASS for preservation; desktop WebKit remains PARTIAL as a release target. Comparator is exact 262b6092, not the different repository-root application. The original embedded model/control/Assist/training/history and UI function bodies are byte-preserved. Eleven original numerical suites pass. All original assertions remain unchanged.','', '| Browser | Suite | Original pinned | B11 package |','|---|---|---|---|']
for n,d in reg.items():
 for row in d['rows']:reglines.append(f"| {n} | {row['suite']} | {'PASS' if row['baseline']==0 else 'FAIL'} | {'PASS' if row['candidate']==0 else 'FAIL'} |")
reglines+=['',f"Chromium: baseline {reg['chromium']['baselinePass']}/{reg['chromium']['total']}, package {reg['chromium']['candidatePass']}/{reg['chromium']['total']}. Desktop WebKit: baseline {reg['webkit']['baselinePass']}/{reg['webkit']['total']}, package {reg['webkit']['candidatePass']}/{reg['webkit']['total']}. Raw logs and assertion context are retained in baseline/candidate directories and regression-comparison.json; no new required-suite regression.",'', 'B10 previously recorded Chromium 19/19, WebKit baseline 7/9 and integrated 8/9: chart width failed historically and the training-pause assertion was variable. B11 reproduces the current sequential samples above. A passing training sample is not a repair or proof that flakiness is resolved; the chart/playback source/assertions are unchanged. No unrelated repair is made.','', 'Additional original operator-console and retained-reading suites pass in both browsers. They exercise collapsed/partial/expanded states, seven original tools, touch/keyboard/focus/Escape, original schematic and settings/units, all five lessons, hot-trip/recovery, retained Assist, full training and SI exports and standalone original offline bytes. Original offline setContent evidence does not qualify the scientific worker.','', 'isolation-{browser}.json.gz retains fourteen original state/history/clock workflows, exact original storage/history CSV checks, Assist and full exercise exports. A2-only initialization leaves original state null; advancing either model leaves the other state/history exact. Idle, initializing, running, stopped, disposed and lost/refusal paths preserve original controls. Real worker startup loss leaves original playback running. No A2 history enters Live Plant history and no A2 fault becomes an equipment alarm.']
write('ORIGINAL_WORKSTATION_REGRESSION.md','\n'.join(reglines))
training=['# Complete exercise export parity','', 'PASS. Ten full B11 export files are byte-identical to the pinned original baseline receipts (five per tested browser). Baselines remain unchanged in B10/evidence/baseline-training; candidate bytes are retained here in evidence/training-{browser}. Comparison includes full SI histories, grading/goals, accepted times, reflection/actions, final/stop evidence and frozen interpretation.','', '| Browser | Exercise | Bytes | Samples | Events | Completion s | SHA-256 |','|---|---|---:|---:|---:|---:|---|']
for n,d in T.items():
 for x in d['training']:
  assert x['byteExact'];actual=(E/f'training-{n}/{x["exercise"]}.json').read_bytes();expected=(B.parent/f'browser_eos_b10/evidence/baseline-training/{n}-{x["exercise"]}-evidence.json').read_bytes();assert actual==expected
  training.append(f"| {n} | {x['exercise']} | {x['bytes']} | {x['samples']} | {x['events']} | {x['completedAt']} | {x['sha256']} |")
training+=['','A fresh original-only startup lesson also passes without loading A2. All five exports with an existing A2 session leave its snapshot/history/session hashes unchanged. Original lesson history and Assist retain their own interpretation and original model; training never dispatches A2 advances.']
write('TRAINING_EXPORT_PARITY.md','\n'.join(training))
perf=['# Browser performance and resources','', 'PASS for measurement/characterization, without a real-time threshold. Fresh B10 and B11 samples use the same host, browser versions, 1440×1000 viewport, original playback plus trusted tool/schematic input and exactly three A2 intervals. Two sequential rounds per browser/fixture, order reversed in round 2. Fresh contexts retain natural browser/OS caches; “cold fixture” describes the physical initial condition, not a guaranteed empty OS cache.','', 'Milliseconds are median [min–max], n. Compute is the sum of worker timing.advanceMS across the original three intervals; it excludes asset loading and includes original model work. Tool and readiness roundtrips include automation/actionability/render scheduling.','', '| Browser | Fixture | Artifact | Navigation to original ready | Lazy A2 panel | First accepted/rendered t=0 | Three-advance compute | Tool switch during compute |','|---|---|---|---|---|---|---|']
for n,d in F.items():
 for f in ['cold','warm']:
  for mode in ['B10','B11']:
   rows=[x for x in d['samples'] if x['fixture']==f and x['mode']==mode]
   perf.append(f"| {n} | {f} | {mode} | {stat([x['navigationToOriginalReadyMS'] for x in rows])} | {stat([x['lazyPanelMS'] for x in rows])} | {stat([x['session']['firstAcceptedAndRenderedMS'] for x in rows])} | {stat([sum(v['timing']['advanceMS'] for v in x['workerMetrics'] if v['type']=='advance') for x in rows])} | {stat([x['switchDuringComputeMS'] for x in rows])} |")
perf+=['', '| Browser | Artifact | Worker creation | Bundle hash/fetch | Module/owned table | Model create/record | Original initialize UI | Dispose | Restart to rendered t=0 |','|---|---|---|---|---|---|---|---|']
for n,d in F.items():
 for mode in ['B10','B11']:
  rows=[x for x in d['samples'] if x['mode']==mode];get=lambda fn:stat([fn(x) for x in rows])
  perf.append(f"| {n} | {mode} | {get(lambda x:x['session']['workerCreationMS'])} | {get(lambda x:x['initialization']['timing']['assetVerificationMS'])} | {get(lambda x:x['initialization']['timing']['importAndOwnedTableMS'])} | {get(lambda x:x['initialization']['timing']['createAndRecordMS'])} | {get(lambda x:x['originalInitializeMS'])} | {get(lambda x:x['disposeMS'])} | {get(lambda x:x['restart']['firstAcceptedAndRenderedMS'])} |")
perf+=['', '| Browser | Artifact | Main heartbeat gaps | rAF gaps | Trusted event acknowledgement | DOM render | Browser/driver RSS MiB after solve |','|---|---|---|---|---|---|---|']
for n,d in F.items():
 for mode in ['B10','B11']:
  rows=[x for x in d['samples'] if x['mode']==mode];flat=lambda key:[v for x in rows for v in x['observations']['data'][key]]
  perf.append(f"| {n} | {mode} | {stat(flat('heartbeat'))} | {stat(flat('frames'))} | {stat([v['ackMS'] for v in flat('clicks') if v['trusted']])} | {stat([v for x in rows for v in x['renderMS']])} | {stat([x['memoryAfter']['totalRSSKiB']/1024 for x in rows])} |")
perf+=['','## Observed packaging differences','', 'B11 minus matched B10 medians below are observations from two samples per fixture, not causal estimates or guarantees. Positive deltas mean additional observed time/resource use.','']
for n,d in F.items():
 med=lambda mode,fixture,fn:statistics.median(fn(x) for x in d['samples'] if x['mode']==mode and (fixture is None or x['fixture']==fixture))
 delta=lambda fixture,fn:med('B11',fixture,fn)-med('B10',fixture,fn)
 perf.append(f"- {n}: cold-fixture navigation {delta('cold',lambda x:x['navigationToOriginalReadyMS']):+.2f} ms; lazy panel {delta('cold',lambda x:x['lazyPanelMS']):+.2f} ms; first accepted/rendered initialization {delta('cold',lambda x:x['session']['firstAcceptedAndRenderedMS']):+.2f} ms; warm three-advance compute {delta('warm',lambda x:sum(v['timing']['advanceMS'] for v in x['workerMetrics'] if v['type']=='advance')):+.2f} ms; tool-switch median {delta(None,lambda x:x['switchDuringComputeMS']):+.2f} ms; coarse after-solve RSS median {delta(None,lambda x:x['memoryAfter']['totalRSSKiB']/1024):+.2f} MiB.")
perf+=['','Raw performance-{browser}.json preserves every sample, worker projection/service/delivery/roundtrip time, startup navigation entries, original model-call time, trusted-event pending counts, frames/heartbeat, coarse Chromium heap (WebKit may be null), RSS process observations and disposal timer state. B10/B11 scientific snapshot cores match exactly in each pair. Main-thread delays/tool roundtrips are real; event acknowledgement starts at the browser timestamp and omits actionability waiting. DOM timing is not display scanout. Negative transfer estimates from timer resolution, if present, are retained.','', 'No scientific assets are compressed/rebuilt at runtime; no new worker/page/service worker/cache exists. The packaged B9D formatter dependency is about 3 KB; the scientific bundle is present once. Original embedded properties and scientific owned tables intentionally remain independent, as in B10. RSS includes shared browser/driver pages and cannot isolate worker memory or establish leaks. Matched sample variation is too small a campaign for causal scheduling or memory conclusions; inspect the tables for startup/compute/switch outliers. The package introduces no new startup failure in supported origins and no additional asset download dependency. No stable nonlinear speedup or sustained real-time performance is claimed.','', 'Historical B10 warm compute medians were about 610 ms Chromium and 1,004 ms desktop WebKit. They are context, not thresholds for this host. Use the matched rows above. Only .001 simulated seconds is computed; wall-clock time and UI stalls remain material limitations, especially on WebKit. Physical iPad resource behavior awaits owner review.']
write('BROWSER_PERFORMANCE.md','\n'.join(perf))
compat=['# Server and origin compatibility','', 'The copied standalone package passes root and nested-path serving in both actual desktop browsers, outside the repository. Strict local assets plus a same-origin CSP were tested; no historical path, /workspace path, CDN, external API or runtime model download is requested. Every source path/worker import resolves inside preview. Actual requests are retained in independent-server-requests.json and portability-{browser}.json. MIME types are explicit in the server handler and asset manifest; successful browser module loads verify MIME acceptance.','', '| Target | Result | Boundary |','|---|---|---|','| Desktop HTTP localhost | PASS, Chromium and desktop WPE WebKit | Root and /review/b11/, cold/warm, all three advances, disposal/restart |','| Private-address LAN HTTP origin | BLOCKED / device reachability UNTESTED | Actual cloud private-address requests returned HTTP 503 before app startup. Separate locally intercepted nonsecure HTTP origin policy test lacks required crypto |','| Another device on owner LAN | UNTESTED | No owner iPad or LAN access; firewall/routing/Wi-Fi must be checked there |','| Separate trusted HTTPS preview | Suitable static artifact; origin requirements inspected | No HTTPS host/URL deployed or actual HTTPS test performed; separately approve host and test device |','| Native file | NOT QUALIFIED | Module/CORS startup failure retained separately |','| Browser offline | NOT QUALIFIED | No service worker/cache installation supplied |','']
for n,d in P.items():compat.append(f"- {n} direct private-address transport: `{json.dumps(d['privateNetworkTransport'],separators=(',',':'))}`\n- {n} nonsecure HTTP policy observation (locally intercepted package, not reachability evidence): `{json.dumps(d['privateHTTP'],separators=(',',':'))}`")
compat+=['','B10 requires crypto.randomUUID in the page/client and crypto.subtle.digest in the worker before bundle use. Loopback HTTP is potentially trustworthy; ordinary private-LAN HTTP is not. Workers/modules are not by themselves proof that the crypto-dependent backend will initialize. The separate origin-policy probe serves exact local package bytes through Playwright interception at a reserved .invalid HTTP origin, with unchanged CSP and browser security. It preserves original operation while A2 reports unqualified with a null snapshot. It performs no external network access and proves no LAN/server reachability. Direct private-address transport attempts are retained separately as HTTP 503 failures before app startup (private-origin-reachability.json and private-transport-*). No verification/UUID/security fallback was added.','', 'Use same-origin module workers with correct JavaScript MIME; no CORS headers are required for same-origin assets and no SharedArrayBuffer/cross-origin isolation is used. HTTPS must be trusted on the actual device. Serve all files coherently, real missing-asset 404s and no HTML rewrite of module URLs. CSP tested: default-src self; script/style self + unsafe-inline for the original inline application; worker/connect self; img self + data; object none; base-uri self. No unsafe-eval needed. Exact header is in PREVIEW_HOSTING_HANDOFF.md.','', 'The network must reach the server for any uncached asset, lazy module or new worker. A server with local assets can function without Internet, while browser offline mode may still block that local server. HTTPS on a disconnected network, a cached/service-worker PWA and native Files/Safari are distinct modes. Physical-device startup, memory, trust, backgrounding and touch remain untested.']
write('SERVER_AND_ORIGIN_COMPATIBILITY.md','\n'.join(compat))
off=['# Offline and native-file boundary','', '**NOT QUALIFIED.** No service worker/PWA or single-file scientific package was introduced. No scientific source was modified for offline compatibility.','', '| Mode | B11 observation |','|---|---|','| All local assets served, browser online, localhost | PASS independently in both browsers; no external scientific/application request |','| HTTPS with network disconnected | UNTESTED; no HTTPS deployment/host established |','| Existing fully loaded localhost worker, then browser offline | Three bounded advances pass; a new worker restart fails; no offline-startup qualification |','| Browser offline before lazy panel import | Panel unavailable, original ready |','| Browser offline after panel import, before worker | Scientific worker lost/unqualified, no accepted snapshot |','| Cached/service-worker offline mode | NOT IMPLEMENTED / NOT QUALIFIED |','| Native file on desktop | Actual observations below; NOT QUALIFIED |','| Native iPad Files/Safari | NOT TESTED / AWAITING USER |','']
for n,d in P.items():
 off.append(f"- {n} native file: `{json.dumps(d['file'],separators=(',',':'))}`")
 for row in d['cases']:
  if row['case'].startswith('offline'):off.append(f"- {n} {row['case']}: `{json.dumps(row,separators=(',',':'))}`")
off+=['','Missing/corrupt scientific bundle tests also retain genuine unqualified/null-snapshot states. Original classic-script standalone/offline workflows pass separately in the original console suite; this is not scientific offline startup evidence. Local server availability is not equivalent to Safari browser offline mode, cached HTTPS, or Files opening. A separately authorized future offline package must test transport/security/cache lifecycle without changing model acceptance or introducing a fallback engine.']
write('OFFLINE_COMPATIBILITY.md','\n'.join(off))
write('FAILURE_AND_LIFECYCLE.md','''# Failure and lifecycle preservation

PASS in both tested served desktop browsers. Unchanged B10 worker, protocol, reducer and model call order are used with relocated URLs. Missing and deliberately corrupt scientific bundle initialization returns unqualified with no snapshot; worker startup/loss/offline behavior stays truthful. No illustrative plant engine is substituted. The original simulator remains usable after scientific startup failure.

Actual numerical refusal preserves B10's real prior accepted substeps (18 valid half-step commits at 4.8828125e-7 s), while the last successful display stays stale at 0 s with its separate request target and known worker time. Whole-request rollback is not falsely assumed. Real 200/400 K outward thermal stops independently confirm domain classification; no new commits preserve exact physical bits and original object identities. All complete stopped states/records equal the original control. These modeled stops are not equipment alarms. Original transient/persistent/boundary property, retry-floor and record-failure C1 contracts remain unchanged; injected C1 properties exist only in test harnesses, not the packaged table worker.

Integration receipts cover stale/out-of-order/equal-version fault ordering, exact duplicate replay, altered duplicate refusal, pending advance/stop/dispose, duplicate initialization/disposal, commands during disposal, session restart, hard termination, actual deadline loss, and old-session DOM clearing. Five bounded repeated restarts/disposals per browser leave no pending commands or heartbeat/frame callbacks. Real pagehide ends pending work and cleans resources. Scheduling stop waits for a synchronous solve boundary; it cannot preempt Newton work. Lost in-flight state is unknown and cannot be guessed/resumed.

Original state/history/Assist/export hashes stay exact across A2 actions and faults. Original playback survives actual worker startup loss. Both clocks remain independent; no A2 history or numerical error becomes original plant history or equipment alarms. Native-file and insecure/private-HTTP failures are reported separately, never hidden.

Retained engineering iterations: initial sandbox denied server socket creation; rerun enabled ordinary process network access. Initial packaging missed B9D view.mjs; the timeout receipt/log is retained, and exact supporting source was added to close the asset graph. The independent CSP campaign initially failed because Playwright's string wait invokes page eval. A test-only direct polling wait preserves the CSP (no unsafe-eval) and original assertions/application. That failure and the successful follow-up are separately retained. No assertion, acceptance budget, scientific algorithm or original UI was repaired. A direct private-address attempt returned HTTP 503 before application startup; it is a transport limitation, retained separately from the successful root/nested run and locally intercepted HTTP security-context probe. No proxy or browser security was bypassed. Any additional retained failures are in evidence/*failure* and campaign logs with their context; use the final receipts to assess disposition. Long-duration memory or page-background/session behavior on a physical iPad remains unqualified.
''')
write('MECHANICS_REPORT.md','''# Mechanic’s report

The actual B10 workstation can now be copied as one static folder and served independently. Its original plant schematic, compressor/controller displays, controls, history, Operator Assist and five training lessons retain their original model. All ten complete lesson exports match the pinned original bytes.

The A2 research panel still uses real accepted calculations for five evaporator sections: conserved refrigerant mass/internal energy/fixed volume, pressure/enthalpy/phase, tube/fin/air storage, signed flows, heat exchange and balance residuals. Cold/warm calculations match B10 bit for bit at 0, .0001, .0005 and .001 seconds. The panel is not a full plant and terminal bulk wet does not measure compressor safety. Training/Live Plant clocks and histories remain independent.

Missing assets, unsupported origins and numerical refusal remain visible. Old accepted readings are marked stale; no invented state replaces a failed calculation. Stop waits for an already-running calculation; disposal/restart creates a fresh session. Real-time operation is not demonstrated: only .001 simulated seconds is authorized and wall-time/UI stalls remain significant.

Desktop Chromium passes. Desktop WebKit passes the new package/scientific checks but retains historical application chart/training findings and is PARTIAL. File/offline startup is not qualified. Ordinary LAN HTTP lacks required crypto in the tested browsers; use a separately approved trusted HTTPS origin for future device review. Physical iPad status is AWAITING USER DEVICE REVIEW. No host, public URL, production merge or Live Plant scientific coupling is authorized.
''')
write('ENGINEERING_REPORT.md',f'''# B11 engineering disposition

**{status['classification']}**

The exact B10 operator workstation and genuine B9C-powered five-section A2 sidecar are reproducibly packaged as a standalone static folder. Scoped PASS: independent desktop HTTP-served root/nested-path operation, exact science and original application preservation. This does not mean a clean WebKit release, working ordinary LAN HTTP A2, qualified offline startup, physical iPad validation, deployment authorization or sustained real-time physics.

| Gate | Result | Retained evidence / limit |
|---|---|---|
| A — source/science | PASS | All {status['protectedHistoryFiles']} starting files unchanged; exact bundle/derivation; saved B10 complete bit-exact checkpoints and attempts; ownership/C1 controls |
| B — portable served package | PASS | Twelve local runtime assets + manifest; deterministic ZIP; copy outside checkout as HTTP root and nested path; exact local import graph |
| C — workstation preservation | PASS | No new required suite regression, eleven numerical suites, all five complete exports per browser, independent clocks/state/history/Assist |
| D — Chromium | PASS | Original {reg['chromium']['candidatePass']}/{reg['chromium']['total']}, package/source/render/lifecycle/origin checks |
| D — desktop WebKit | PARTIAL | Original {reg['webkit']['candidatePass']}/{reg['webkit']['total']}; historical chart/variable training pause finding retained; package checks pass |
| D — native file/browser offline | NOT QUALIFIED | Separate observed failures, no service worker/PWA |
| D — private LAN HTTP | BLOCKED | Direct cloud transport 503; separate reserved HTTP origin-policy test confirms missing secure crypto. Other-device reachability untested |
| D — future trusted HTTPS | FEASIBLE / UNTESTED | Static requirements specified; no host or URL created |
| E — performance | PASS for characterization | Matched sequential B10/B11 startup/worker/compute/render/switch/heartbeat/frame/input/RSS; outliers retained; no real-time claim |
| F — physical iPad | NOT TESTED / AWAITING USER | Owner checklist and return form supplied |
| G — deployment | NO-GO | Separately approve host/URL/access and exact package; no public deployment |

Architecture was committed at `{status['architectureCommit']}` before packaging. Source relocations preserve B10's numerical call order, original inline application and hash/identity security. B9C bundle is byte-exact; full original reverse derivation and all scientific/property dependencies are auditable. The normal scientific ceiling stays .001 s; no full campaign, scientific repair, optimizer, EOS substitution or plant-wide connection was added.

Read SCIENTIFIC_PARITY_MATRIX.md, ORIGINAL_WORKSTATION_REGRESSION.md, TRAINING_EXPORT_PARITY.md, BROWSER_PERFORMANCE.md and SERVER_AND_ORIGIN_COMPATIBILITY.md for exact results. Raw browser failures and environmental setup iterations remain retained. PHYSICAL_IPAD_REVIEW.md is the next hands-on step after a supported reachable origin is available. PREVIEW_HOSTING_HANDOFF.md supplies commands/MIME/CSP/trust/approval requirements. Machine tracker: milestone-status.json/csv. Protected-ref/PR and publication receipts are separate from the deterministic artifact identity.

Portable artifact PASS; exact A2 parity PASS; original preservation PASS; Chromium PASS; desktop WebKit PARTIAL; offline NOT QUALIFIED; local-network origin BLOCKED for ordinary HTTP (other-device access UNTESTED); physical iPad AWAITING USER; research preview deployment AWAITING APPROVAL; production merge NO-GO; full Live Plant coupling NO-GO. Stop for engineering review.
''')
print(status['classification'])
