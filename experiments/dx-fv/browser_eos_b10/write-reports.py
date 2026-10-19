"""Generate final reports only from completed B10 receipts. No scientific writes."""
import csv,gzip,hashlib,importlib.metadata,json,platform,statistics,subprocess,zipfile
from pathlib import Path
from xml.sax.saxutils import escape
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2]
def read(name):
 p=E/name;return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(name,text):(B/name).write_text(text.strip()+'\n')
def section(name,heading,text):
 p=B/name;prefix=p.read_text().split('\n## '+heading+'\n',1)[0];p.write_text(prefix.rstrip()+'\n\n## '+heading+'\n\n'+text.strip()+'\n')
def summary(values):
 a=[x for x in values if x is not None];return 'unavailable' if not a else f'{statistics.median(a):.2f} [{min(a):.2f}–{max(a):.2f}], n={len(a)}'
science={n:read(f'review-{n}.json.gz') for n in ['chromium','webkit']}
integration={n:read(f'integration-{n}.json.gz') for n in science}
isolation={n:read(f'isolation-{n}.json.gz') for n in science}
performance={n:read(f'performance-{n}.json') for n in science}
assert all(v['passed'] for group in [science,integration,isolation,performance] for v in group.values())
render=read('independent-render.json')
assert len(render)==2 and all(v['passed'] and v['independentFormulaChecks'] and len(v['rows'])==16 and all(r['sourceUnchanged'] for r in v['rows']) for v in render)
regressions={};regtable=[]
for n in science:
 baselinePath='baseline-webkit-pre-implementation' if n=='webkit' else 'baseline-chromium'
 baseline={r['suite']:r['code'] for r in read(baselinePath+'/results.json')};candidate={r['suite']:r['code'] for r in read(f'candidate-{n}/results.json')};sequential={r['suite']:r['code'] for r in read(f'baseline-{n}/results.json')};assert set(baseline)==set(candidate)
 rows=[]
 for name in baseline:
  assert not (baseline[name]==0 and candidate[name]!=0),(n,name,'NEW REGRESSION')
  expected='PASS' if baseline[name]==0 else 'FAIL';actual='PASS' if candidate[name]==0 else 'FAIL'
  if baseline[name] and candidate[name]:
   before=(E/baselinePath/(name+'.log')).read_text();after=(E/f'candidate-{n}/{name}.log').read_text()
   assertion='storage-pause.isDisabled at training-ui:34' if name=='training-ui' else 'Chart geometry expands at desktop width'
   same=('storage-pause' in before and 'storage-pause' in after and '34:' in before and '34:' in after) if name=='training-ui' else ('Chart geometry expands at desktop width' in before and 'Chart geometry expands at desktop width' in after)
   assert same,(n,name,'different failure needs investigation')
  elif baseline[name]:
   before=(E/baselinePath/(name+'.log')).read_text();again=(E/f'baseline-{n}'/(name+'.log')).read_text()
   assert name=='training-ui' and all('storage-pause' in text and '34:' in text for text in [before,again])
   assertion='Baseline storage-pause.isDisabled at training-ui:34; candidate PASS (variable, no fix claimed)';same=None
  else:assertion='unchanged original assertions';same=True
  row={'suite':name,'baseline':expected,'sequentialBaseline':'PASS' if sequential[name]==0 else 'FAIL','candidate':actual,'sameAssertion':same,'newRegression':False,'priorFailureDisappeared':bool(baseline[name] and not candidate[name]),'assertion':assertion};rows.append(row);regtable.append(f'| {n} | {name} | {expected} | {actual} | {assertion} |')
 for name in ['candidate-console-'+n+'.log','retained-'+n+'.log']:assert 'PASS:' in (E/name).read_text()
 regressions[n]=rows
(E/'regression-comparison.json').write_text(json.dumps(regressions,indent=2)+'\n')
training=[]
for n,v in isolation.items():
 assert len(v['training'])==5
 for row in v['training']:
  assert row['byteExact'] and row['allObjectives'];training.append({'browser':n,**row})
(E/'training-export-comparison.json').write_text(json.dumps(training,indent=2)+'\n')
decisions=[
 ('A','Source and historical preservation','PASS','preservation-final.json; 2,958 historical hashes; protected refs and PR #3'),
 ('B','Actual workstation derivation','PASS','build-manifest.json; exact reverse recovery; 574 pinned inputs'),
 ('C','Two-model scientific/state isolation','PASS','isolation-*.json.gz; original full state/history hashes and separate clocks'),
 ('D','Genuine A2 shadow-panel integration','PASS','integration-*.json.gz; real console slot, source/render/viewport receipts'),
 ('E','Exact scientific parity','PASS','review-*.json.gz; B9C same-engine hashes; integrated four checkpoints and all attempt hashes'),
 ('F','Failure and rollback','PASS','original C1 and genuine A2 numerical/200/400 K; duplicate/stale/lost/dispose'),
 ('G','Original training/export preservation','PASS','five complete byte-identical exercise exports in each browser; actual SI histories'),
 ('H','Original Live Plant/Assist/history preservation','PASS','19 original Chromium suites; WebKit baseline 7/9, candidate 8/9; exact original hashes/CSVs/Assist'),
 ('I','Chromium browser behavior','PASS','19/19 original suites plus original console, retained readings and B10 checks'),
 ('J','Desktop WebKit browser behavior','PARTIAL','B10 checks pass; baseline 7/9, candidate 8/9; inherited chart failure, variable training pause assertion'),
 ('K','Performance/responsiveness characterization','PASS','matched A/B/C/D/E and bare B9C; actual outliers and memory observations retained'),
 ('L','Served research workstation readiness','CONDITIONAL GO','bounded opt-in served engineering review only; inherited WebKit findings remain'),
 ('M','Offline/local-file readiness','NOT QUALIFIED','module-worker/packaging startup limitations; no offline claim'),
 ('N','Physical iPad readiness','NOT TESTED','desktop viewport/touch emulation only'),
 ('O','Production workstation merge','NO-GO','no merge or deployment authorized'),
 ('P','Live Plant/plant-wide backend','NO-GO','five-section evaporator only; no plant coupling')]
tracker=[{'id':a,'decision':b,'result':c,'evidence':d,'reviewRequired':a in ['J','L','M','N','O','P']} for a,b,c,d in decisions]
(B/'milestone-status.json').write_text(json.dumps({'classification':'B10 OPERATOR WORKSTATION SHADOW HOOK-UP PASS','scope':'bounded local HTTP-served research','decisions':tracker,'backlog':'QUALIFICATION_BACKLOG.md','nextMilestone':'Engineering review; separately scope inherited WebKit and intended packaging/device investigation','productionMerge':'NO-GO','plantBackend':'NO-GO'},indent=2)+'\n')
with (B/'milestone-status.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(tracker[0]));w.writeheader();w.writerows(tracker)
# Minimal standards-based XLSX with inline strings, no runtime dependency.
headers=list(tracker[0]);rows=[headers]+[[str(r[k]) for k in headers] for r in tracker]
sheet='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join('<row r="'+str(i+1)+'">'+''.join('<c r="'+chr(65+j)+str(i+1)+'" t="inlineStr"><is><t>'+escape(str(v))+'</t></is></c>' for j,v in enumerate(row))+'</row>' for i,row in enumerate(rows))+'</sheetData></worksheet>'
with zipfile.ZipFile(B/'milestone-status.xlsx','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
 z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="B10 decisions" sheetId="1" r:id="rId1"/></sheets></workbook>')
 z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
 z.writestr('xl/worksheets/sheet1.xml',sheet)
parity=[]
for n,v in science.items():
 for f in ['cold','warm']:
  r=v['results'][f];assert r['exact'] and r['savedB9CMatch'];a=next(a for a in integration[n]['science'] if a['fixture']==f);assert a['exactSavedControl'] and a['allOriginalAttemptDiagnosticsExact']
  parity.append(f"| {n} | {f} | EXACT | {r['control']['work']['residuals']} | {r['control']['work']['accepted']} | {r['control']['work']['rejected']} |")
write('SCIENTIFIC_PARITY_MATRIX.md','''# Exact scientific parity

PASS against unchanged accepted A2 controls and saved B9C same-browser receipts. B10 integrated workers match B9D's exact control checkpoint hashes at 0/.0001/.0005/.001 s and the hash of every original attempt diagnostic. No tolerance replaces exact binary64 encoding. Cross-browser bit equality is not assumed.

| Browser | Fixture | Result | Residual evaluations | Accepted half-steps | Rejections |
|---|---|---|---|---|---|
'''+ '\n'.join(parity)+'''

The unchanged exhaustive harness hashes every residual's full return and coordinates, Jacobian/rhs/correction and converged stage; control/candidate component hashes match. Full state/record/attempt science hashes match saved B9C. This covers M/U/V, recovery guesses and PH/phase/quality/wet, thermal energies/temperatures, every face/heat flux, conservative ledgers, signed finite differences, Newton/line search, TR-BDF2 stages/errors, accepted/rejected trials, proposals, events and final clocks. Ten original and fourteen additional supported paired cases also pass per browser. Original property-support, invalid-update and missing-region refusals are retained.

`integration-*.json.gz:science.fullAcceptedDetails` retains B10's complete accepted state and original record at all four checkpoints, using exact numeric encoding. Complete attempt hashes match the original protected B9D raw attempt evidence. `review-*.json.gz` contains fresh science/component hashes, full C1 results and regression receipts; original raw exhaustive probe arrays remain preserved in B9C/B9D. Hashing occurs before duplicate detail is released, without changing or reducing any numerical work.

All 93 SI reading cells and 98 US-view cells trace to accepted source paths and conversion identifiers, including thermal nodes, heat rates, inventories, residuals and the latest original interval/proposal. independent-render.json independently recomputes the unit formulas for every cell at all four checkpoints, both fixtures and browsers; formatting leaves the accepted projection unchanged. Every history row is an actual accepted projection. Display mutation cannot affect worker state. Original canonical recovery, mass (<1e-8 kg), energy (<1e-6 kJ), thermal/nonlinear, Newton/TR-BDF2 and domain budgets remain unchanged; original record audits recompute signed closure. This is not a new full-duration or mesh-convergence campaign. No EOS backend, DP dependency, clamp, pressure epsilon, alternate state or new solver optimization is introduced.
''')
write('ORIGINAL_WORKSTATION_REGRESSION.md','''# Original workstation regression preservation

PASS for preservation. Exact source at 262b6092 is the comparator, not the different root application on the research branch. Rebuilt HTML is byte-identical before the reversible presentation insertion. Eleven original numerical suites pass. Chromium is 19/19 in baseline and B10; original console and retained-reading suites also pass. Desktop WebKit is 7/9 in both the sealed pre-implementation baseline and the final sequential pinned baseline; the final sequential B10 candidate is 8/9. No assertion is weakened and no new original-suite regression is observed.

| Browser | Original suite | Baseline | B10 | Assertion |
|---|---|---|---|---|
'''+ '\n'.join(regtable)+'''

Startup, Live Plant initialization/playback/start-stop, equipment controls/profiles, schematic inspection, original units, inventory, trends/history, guided exercises/scoring/exports, retained attempts, Assist conclusions, seven original console tools, focus/keyboard/Escape and collapsed/partial/expanded behavior retain original assertions. Existing standalone/offline-original workflows remain intact because A2 modules load only on selecting the new tool. This does not qualify offline A2 startup.

`regression-comparison.json` explicitly records same/different assertions, new regressions and disappeared prior failures. The inherited chart-width assertion at visual-pass2-ui:22 fails identically in baseline and candidate. The training pause assertion at training-ui:34 fails in both pinned baseline samples but passes in the final sequential candidate sample: its prior failure disappeared in that sample. This variable result is not a claimed fix; original training functions and assertions are unchanged. B10 is not fully green on WebKit. Original console step-based completion/export checks and all five full export comparisons pass.

`isolation-*.json.gz` contains full original state/history hashes, independent clocks, exact storage/history CSV hashes, retained Assist text and all fourteen required workflows. A2-only initialization leaves original state null; advancing either model leaves the other's snapshot/history exact. Tool changes, faults and disposal do not mutate the original plant. Trusted original Start input is acknowledged during an actual pending A2 advance. Worker startup loss is caught locally while original playback remains running. Training never dispatches A2 work.
''')
tt=['| Browser | Exercise | Bytes | SI samples | Events | Completion s | SHA-256 |','|---|---|---|---|---|---|---|']
for r in training:tt.append(f"| {r['browser']} | {r['exercise']} | {r['bytes']} | {r['samples']} | {r['events']} | {r['completedAt']!r} | {r['sha256']} |")
write('TRAINING_EXPORT_PARITY.md','''# Five complete exercise evidence comparisons

PASS in Chromium and desktop WebKit. All five B10 exports are byte-for-byte equal to the actual pinned workstation baseline files. Comparison includes the entire JSON: original SI histories, times, grading evidence, objective completion, quiz/actions, accepted boundaries, stop events, final state and interpretation. It does not compare only banners. Full candidate files are in evidence/training-{browser}; baseline files are in evidence/baseline-training.

'''+ '\n'.join(tt)+'''

The startup exercise also completes with A2 uninitialized on a fresh workstation. All five complete after an independent A2 session has existed; A2 session/snapshot/history hashes remain unchanged during training. Hot Condenser Air uses the genuine original equipment trip, off-state restoration, clearing and accepted continuation. Existing original console tests independently compare the entire exports against their historical contract in both browsers. Retained reading/timestamp tests and original frozen-report assertions pass. No training, scoring, recipe, accepted-history or Assist source is modified.
''')
write('FAILURE_AND_ROLLBACK.md','''# Failure, rollback and lifecycle

PASS in both browsers. Original C1 tests remain a separate injected-property experiment; no injected/CoolProp engine is installed in the optimized owned-table worker. Fresh unchanged local and six session C1 scenarios verify transient/persistent/boundary property refusal, retry-floor numerical stop, exact rejected-trial bits and object identity, accepted-record failure and independently confirmed 200/400 K outward thermal exits.

Genuine B10 numerical and thermal fixtures reproduce the unchanged control's stopped state and record exactly. Numerical refusal retains 18 valid half-step commits at 4.8828125e-7 s, while the previous successful display stays stale at 0 s and the failed request target remains .0001 s. Whole-request rollback is not assumed. Thermal exits accept zero new commits and preserve physical bits and cells/energies/ledger identities. Their proven modeled-domain status is not an equipment alarm.

Supported operation, initialize error, missing scientific bundle, actual worker startup/termination/loss, duplicate advance replay, altered duplicate refusal, stale sequence/version/response, equal-version fault ordering, stop while pending, pending advance during disposal, duplicate dispose, commands during disposal, restart after error and old-session DOM clearing are checked. Refused property/record work cannot create a new successful gauge set. Latest after fault retains stale evidence. New sessions clear old history and use fresh UUIDs. Source identity is attached to every response, including null snapshots and errors.

Five repeated actual panel restarts/disposals per browser leave no pending commands or panel heartbeat/frame callbacks. Navigation with an in-flight advance triggers the real pagehide handler: worker termination, pending rejection handling and resource cleanup are recorded from the departing page. B10 adds no ResizeObserver; original single-page observers remain unchanged. This bounded evidence does not certify long-duration memory behavior.

Retained engineering iterations: concurrent WebKit training/console click timeouts coincided with memory pressure; their attribution is unproved and they are not relabeled as inherited assertions. The final sequential baseline/candidate comparison and unchanged original console suite are retained separately. Initial candidate test runtime selection failed before application launch; the external preload was corrected for the copied Playwright module. A review run exceeded the 10-GB memory budget while retaining duplicate exhaustive diagnostics (exit 137/EPIPE); a later duplicate-detail integration run was deliberately stopped before further growth. Loading the large historical reference archives also exceeded the test memory budget; final integration instead reads protected compact summaries and computes the unchanged original reference worker's full hashes. Final runners preserve all original computation, exact scientific/component/attempt hashes and accepted states/records while releasing duplicate test evidence. A relative test fetch initially lacked the literal mechanical closure source; B10 now derives a byte-exact test-only copy from pinned B9C. None changed a scientific algorithm, acceptance rule, original assertion or original workstation model. Logs remain in evidence/*failure*, review-memory*, integration-archive-memory-limit.log and integration-duplicate-detail-memory-stop.log.
''')
ui=[]
for n,r in integration.items():
 for v in r['viewports']:ui.append(f"| {n} | {v['label']} {v['width']}×{v['height']} | PASS | {v['tableScroll']['client']} / {v['tableScroll']['scroll']} |")
write('BROWSER_UI_RESULTS.md','''# Served-browser UI results

B10 scientific/display/lifecycle/isolation checks PASS in actual Chromium 151.0.7922.34 and desktop WPE WebKit 26.5/build 2336. Original Chromium remains 19/19 plus console; pinned WebKit baseline is 7/9 and final sequential B10 candidate is 8/9, plus passing console. The inherited chart assertion still fails identically. The training pause assertion passes in that candidate sample, a variable result without a claimed fix. See ORIGINAL_WORKSTATION_REGRESSION.md. No physical iPad was tested.

| Browser | Viewport | Focus/touch/overflow/control access | Section table client / scroll px |
|---|---|---|---|
'''+ '\n'.join(ui)+'''

The new region is inside the real console-content; it is not an iframe or second workstation. Real accepted cold/warm instruments appear beneath the original schematic workspace. Desktop, landscape and portrait reviews check 44-pixel controls, no page overflow/duplicate parent IDs, correct resizing and horizontal table confinement. Expanded/partial/collapsed behavior, keyboard activation, Escape and focus return retain existing console ownership. Expanded screenshots show source/qualification labels and genuine values; instrument screenshots review scrolling. Existing playback controls remain above the expanded console. Expansion intentionally occupies the detail workspace; collapse/Plant overview returns to the original schematic.

Actual pagehide cleanup and five restart/disposal cycles per browser pass. B10 uses one isolated root and bounded metrics; no panel ResizeObserver is created. No listener/observer growth is introduced by tool switching in this bounded design; this is not a sustained leak campaign. Interaction/status/clock logs and screenshots are evidence/integration-*, isolation-* and candidate-*. Original schematic/training/Assist interactions are independently covered by the unmodified suites.
''')
perfrows=[];startup=[];responsiveness=[];workstation=[];messages=[];operation=[];memoryrows=[]
for n,p in performance.items():
 for fixture in ['cold','warm']:
  rounds=[r for r in p['rounds'] if r['fixture']==fixture]
  by={case:[next(c for c in r['cases'] if c['case']==case) for r in rounds] for case in ['A','B','C','D','E','bareB9C']}
  for case in ['A','B']:
   rr=by[case];workstation.append(f"| {n} | {fixture} | {case} | {summary([x['navigationRoundtripMS'] for x in rr])} | {summary([x['originalModelCreationMS'] for x in rr])} | {summary([x['originalInitializationRoundtripMS'] for x in rr])} | {summary([x['toolSwitchRoundtripMS'] for x in rr])} |")
  compute=lambda cases:[sum(m['timing'].get('advanceMS',0) for m in r['metrics']) for r in cases]
  perfrows.append(f"| {n} | {fixture} | {summary(compute(by['D']))} | {summary(compute(by['E']))} | {summary([sum(t['advanceMS'] for t in c['result']['timing']) for c in by['bareB9C']])} |")
  c=by['C'];startup.append(f"| {n} | {fixture} | {summary([x['session']['workerCreationMS'] for x in c])} | {summary([x['session']['firstAcceptedAndRenderedMS'] for x in c])} | {summary([x['initialize']['timing']['importAndOwnedTableMS'] for x in c])} | {summary([x['initialize']['timing']['createAndRecordMS'] for x in c])} |")
  for case in ['D','E']:
   advances=[m for row in by[case] for m in row['metrics'] if m['type']=='advance']
   messages.append(f"| {n} | {fixture} | {case} | "+' | '.join(summary([m[group].get(field) for m in advances]) for group,field in [('timing','advanceMS'),('timing','projectionMS'),('timing','serviceMS'),('delivery','transferAndDispatchMS'),('delivery','roundtripMS')])+' |')
  d=by['D'];operation.append(f"| {n} | {fixture} | {summary([x['lazyPanelOpenRoundtripMS'] for x in d])} | {summary([x['toolSwitchDuringComputeMS'] for x in d])} | {summary([v for x in d for v in x['render']])} | {summary([x['disposeRoundtripMS'] for x in d])} | {summary([x['restart']['firstAcceptedAndRenderedMS'] for x in d])} |")
  for case in ['C','D','E']:
   memoryrows.append(f"| {n} | {fixture} | {case} | {summary([x['memory']['totalRSS']/1048576 for x in by[case]])} |")
  for case in ['A','B','C','D','E']:
   rr=by[case];beats=[v for x in rr for v in x['observations']['data']['heartbeat']];frames=[v for x in rr for v in x['observations']['data']['frames']];inputs=[v['ackMS'] for x in rr for v in x['observations']['data']['clicks'] if v['trusted']]
   responsiveness.append(f'| {n} | {fixture} | {case} | {summary(beats)} | {summary(frames)} | {summary(inputs)} |')
write('PERFORMANCE_AND_RESPONSIVENESS.md','''# Matched bounded integration measurements

PASS for characterization, without a speed/FPS threshold or continuous-operation claim. All samples are in performance-{browser}.json. Two sequential rounds per frozen cold/warm fixture/browser compare A original pinned workstation, B B10 inactive, C A2 initialized/idle, D A2 computing while original playback/UI operates, E bare B9D, plus bare B9C. Scientific D/E snapshot cores match exactly; bare B9C matches saved same-engine full science. No unrelated scientific workload is attributed to UI overhead. Units below are milliseconds, median [min–max], n.

| Browser | Fixture | D worker three-advance compute sum | E bare B9D sum | Bare B9C sum |
|---|---|---|---|---|
'''+ '\n'.join(perfrows)+'''

| Browser | Fixture | Worker creation | First accepted + rendered t=0 | Source import + owned table | Model create + record |
|---|---|---|---|---|---|
'''+ '\n'.join(startup)+'''

| Browser | Fixture | Case | 10-ms heartbeat gaps | rAF gaps | Trusted input acknowledgement |
|---|---|---|---|---|---|
'''+ '\n'.join(responsiveness)+'''

Scientific computation time is measured inside unchanged model.advance, with original record/observer/diagnostic work. Startup separates worker construction, hash-verifying fetch, import/owned table, model/create record and first rendered accepted state. The t=0 reading is initialization, not an accepted advance. Projection, service/transport, delivery, DOM rendering, original initialization, navigation and tool-switch roundtrips, dispose/restart, all frame/input outliers and memory observations are retained separately in raw receipts. Transfer includes clone/dispatch/scheduling, not an isolated memcpy benchmark. Main-thread render timing measures DOM work, not display scanout.

D intentionally includes original playback and trusted tool/schematic interactions during the same .001-s A2 workload. Its end-to-end interaction roundtrip is therefore not a pure UI overhead subtraction from bare E. CPU scheduling, allocation/JIT/GC and message cadence are not independently attributed. Cold bridge overhead remains an investigation item; no new optimization or scientific shortcut is made. The clocks stay independent. Warm work can take about one second for only .001 simulated seconds, and observed scheduling/input/frame outliers are real limitations. The interface acknowledges input while the worker computes; this does not establish sustained real-time refrigeration or physical iPad performance.

Observed limitations in these samples: D's three-advance compute sums reach 657.5 ms in Chromium and 1014 ms in WebKit. WebKit original-model initialization UI roundtrips take 5.26–5.84 seconds in A/B even though the model-create call itself takes 3–4 ms. D tool-switch roundtrips reach 777.57 ms, a WebKit heartbeat gap reaches 712 ms, and an original-baseline rAF gap reaches 820 ms. Trusted event acknowledgement reaches 22 ms in D; that interval starts at the browser event timestamp and does not include all automation or user waiting. The tool-switch roundtrip is a more complete measured interaction cost. These are material responsiveness limits, not steady frame or input guarantees.

Transfer/dispatch estimates subtract page and worker timestamps and include scheduling/clone work. Small negative samples (-0.1 ms Chromium, -1 ms WebKit) reflect cross-context clock/timer resolution; they are retained as measurement uncertainty, not negative physical transport. No values are clamped to improve the result.

RSS totals cover this runner's browser/driver descendants and may count shared pages; Chromium heap data is coarse main-page information and WebKit may provide null. They are observations, not isolated worker heap or long-duration leak certification. Disposal/restart and bounded timer cleanup are independently tested. Performance runs are sequential after other test jobs; earlier busy-host integration timings are not pooled into these matched results.
''')
with (B/'PERFORMANCE_AND_RESPONSIVENESS.md').open('a') as f:f.write('\n## Original versus inactive B10 startup\n\nA is the exact original; B has the research tool available without loading it. Original model creation is measured by a test-only observer around the unchanged create API. Roundtrips include browser automation/action/render scheduling.\n\n| Browser | Fixture bracket | Case | Navigation roundtrip | Original model creation | Initialize UI roundtrip | Tool switch roundtrip |\n|---|---|---|---|---|---|---|\n'+'\n'.join(workstation)+'\n')
with (B/'PERFORMANCE_AND_RESPONSIVENESS.md').open('a') as f:
 f.write('\n## Advance and message costs\n\nPer accepted requested interval, not per internal adaptive half-step. Bare B9D uses its unchanged UI, while D includes the actual workstation. Values below retain browser timer resolution, including measured zeros.\n\n| Browser | Fixture | Case | Advance compute | Projection | Worker service | Transfer/dispatch | Request roundtrip |\n|---|---|---|---|---|---|---|---|\n'+'\n'.join(messages)+'\n')
 f.write('\n## Panel operations\n\nRoundtrips include trusted automation scheduling where applicable; render is measured DOM work for all bounded updates in the session. Restart includes creation through the first accepted rendered initialization reading.\n\n| Browser | Fixture | Lazy panel open | Tool switch during compute | DOM render | Dispose | Restart to rendered t=0 |\n|---|---|---|---|---|---|---|\n'+'\n'.join(operation)+'\n')
 f.write('\n## Memory observations\n\nBrowser/driver descendant RSS totals in MiB, median [min–max], n. These may count shared memory multiple times and include the browser shell and automation driver; they are not isolated JavaScript heap measurements. Raw receipts also retain coarse Chromium heap values and each process observation.\n\n| Browser | Fixture | Case | Descendant RSS MiB |\n|---|---|---|---|\n'+'\n'.join(memoryrows)+'\n')
pack=[]
for n,r in integration.items():pack.append({'browser':n,'missingModule':r['missingModule'],'offline':r['offline'],'nativeFile':r['nativeFile']})
(E/'packaging-outcomes.json').write_text(json.dumps(pack,indent=2)+'\n')
section('OFFLINE_AND_IPAD_LIMITATIONS.md','Actual B10 observations','\n'.join('- '+r['browser']+': browser-offline A2 status `'+r['offline']['status']+'`; native-file result `'+json.dumps(r['nativeFile'],separators=(',',':'))+'`.' for r in pack)+'\n\nMissing scientific modules return an explicit unqualified backend and null snapshot in both browsers. Local HTTP passes. Original standalone workflows pass separately; this does not make the A2 sidecar package offline-ready.')
table='\n'.join(f'| {a} — {b} | {c} | {d} |' for a,b,c,d in decisions)
write('ENGINEERING_REPORT.md','''# B10 engineering disposition

**B10 OPERATOR WORKSTATION SHADOW HOOK-UP PASS**

The first genuine opt-in evaporator panel is integrated inside an exactly derived copy of the actual operator workstation. This PASS is scoped to bounded local HTTP-served research. It preserves the original functionality and evidence, with the inherited chart failure and variable training pause finding explicitly retained; it is not an all-green WebKit release, offline/device qualification, production authorization or plant-wide backend.

| Independent decision | Result | Evidence / limit |
|---|---|---|
'''+table+'''

Gate 0 records exact B9D start, clean tree, all 2,958 historical hashes, accepted fourteen-file A2 closure, B9/B9A compact worker, B9C source/patch/table identity, B9D bridge/mapping, all remote heads/tags and protected PR #3. Architecture was committed at 6b362530e2850a563f8f3f80fac43607b068f892; exact original build and complete baselines were sealed at 4362b79 before functional implementation. The original 1,736,280-byte workstation rebuild matches pinned SHA-256 0485cdf94b22101f976e365d6e5099bb3f8e15669914d5c12038e3eb37147945. The B10 transformation is reversible to those exact bytes. It adds one console tool registry entry, mounting nodes and a caught lazy bootstrap; existing function bodies, scientific inputs, training/Assist/history and controls stay literal.

Each actual browser verifies four cold/warm checkpoints, complete accepted state/records, exact original attempt hashes, exhaustive residual/Newton/stage hashes, original support/rollback and C1 contracts, all source/render cells, lifecycle faults, ordering, restart/disposal and desktop/tablet layouts. B10's extra projection fields are original heat rates and numerical diagnostics only. There is no physics optimization, backend substitution, mutable model sharing or inferred equipment coupling. Five full exercise exports per browser are byte-identical, including original SI histories, times, grading/objective and stop evidence. Fourteen independent-clock/state/history workflows and original Assist/CSVs remain intact. Actual worker loss does not pause the original plant.

Original Chromium is 19/19 plus passing console/retained checks. Pinned WebKit is 7/9 in both sealed and final sequential baselines; the final sequential B10 candidate is 8/9. The inherited chart assertion is identical. Training passes in that candidate sample despite the baseline pause assertion failing; this variable result is not a fix and remains an investigation item. B10 scientific/lifecycle/isolation/viewport and five-export checks pass in WebKit. Timing, startup, message/render cost, independent original playback interference, frame/input outliers and bounded memory observations are characterized without real-time or physical-device claims. Failed test setup/evidence-retention iterations are retained and explained; no original assertion or numerical budget was relaxed.

Open scientific obligations remain in QUALIFICATION_BACKLOG.md: longer durations, broader envelope and phase/topology, spatial convergence, calibrated heat transfer, experimental EOS/VLE/DU hazards and support endpoints, unused DP, compressor/condenser/receiver/actuator physics and coupling, equipment protection, offline package and physical iPad workflow/performance. Table parity does not close these obligations.

Recommended next milestone: engineering review of this exact branch/artifact and receipts, followed only by separately authorized investigation of inherited WebKit behavior and intended packaging/device workflow. Keep the two models separate and the normal A2 horizon at .001 s. No production/feature-branch merge, deployment, full EOS integration, plant connection or long campaign is authorized. Commit/push B10 only, audit clean preservation, and stop for engineering review.
''')
write('MECHANICS_REPORT.md','''# Mechanic’s report

The first workstation hook-up succeeds as a served research connection. Select A2 Evaporator Research in the actual operator console. Its readings come from five calculated sections of an ammonia evaporator, with refrigerant mass and internal energy in fixed volumes, hydraulic/enthalpy flow, tube and fin storage and a finite air node. The pressures, refrigerant temperatures, phase/quality where supplied, bulk wet indication, metal/air temperatures, signed inlet/outlet flows, heat exchange and balance residuals are genuine accepted calculations. The clock only reaches .001 simulated seconds. The small history contains real accepted states, not an animation of hours of operation.

The existing Live Plant is still the original illustrative circuit. Its compressor, condenser, receiver, feed controller, connected room, histories and clock continue under their own model. Those readings are not supplied by A2. An evaporator section is not compressor suction, coil mass is not plant charge, finite coil air is not the complete room and a bulk wet indication cannot prove compressor protection. The research panel plainly leaves unsupported equipment unavailable. Its bar absolute readings and optional psig/temperature conversions keep their source meaning; an unavailable quality is not silently made zero.

Existing controls, equipment profiles, schematic inspections, Operator Assist and all five lessons remain functional. Every complete lesson export matches the pinned original byte for byte in both tested browsers, including actual histories, measured objectives, stop events and accepted times. The original hot-condenser equipment trip still belongs to that illustrative plant. A2 calculation failure cannot fabricate that alarm or enter its history. Both independent models can advance, or remain idle, without advancing the other. Opening and closing tools preserves them.

The worker carries the actual numerical solve and all original mass/energy accounting. No balance, acceptance budget, Newton/TR-BDF2 control, phase rule or property support was changed. The workstation continues acknowledging input during calculations, with measured frame/input outliers retained. Computing .001 seconds of simulated refrigeration can take about one second of wall time. Some WebKit tool switches take roughly .78 seconds and main-thread pauses remain visible; this is not a smooth real-time claim. Stop scheduling waits for synchronous work already running; it is not an instant interruption of a nonlinear solve.

When the calculation refuses, there is no new successful gauge set. Prior readings stay visible as stale at their original time. The panel separately states known worker accepted time and failed request target/reason. The numerical test retains genuine earlier accepted substeps at 4.8828125e-7 s while displaying the last successful 0-s readings; it does not erase that real progress. Independently proven 200/400 K exits are modeled thermal-domain stops, not equipment trips. Worker loss ends the session and leaves the original plant operating. Restart creates a fresh independent fixture, not a guessed continuation.

This is not continuous operation or a complete industrial ammonia plant. Longer operation, broader conditions, resolution/convergence, calibrated heat transfer, compressor/condenser/receiver/control physics and conservative coupling still need engineering. Desktop Chromium and WebKit pass the new connection checks. WebKit's original chart failure remains; its training pause assertion is variable (baseline fails, final candidate sample passes), without a claimed fix. Offline scientific startup and a physical iPad remain unqualified. The next action is engineering review, with no production merge or deployment.
''')
for filename,paragraph in [('TWO_MODEL_ISOLATION.md','Both browsers pass all fourteen required independence workflows. evidence/isolation-*.json.gz contains exact full original state/history hashes, independent clock/session/snapshot/history hashes, Assist text, CSV parity, pending trusted input and all five complete export receipts. Original playback continues after actual A2 worker startup loss.'),('WORKSTATION_SOURCE_DERIVATION.md','Final build-manifest.json verifies all 574 pinned inputs, the original HTML SHA and exact reverse recovery. bridge-adapter-diff.json records the only small B9D transport adaptations. Normal worker science comes from the exact original candidate bundle; isolated/coupled-model.cjs is a byte-exact B9C mechanical-test source copy, not a separately maintained backend.')]:
 section(filename,'Verified B10 result',paragraph)
runtime={'python':platform.python_version(),'pythonPlaywright':importlib.metadata.version('playwright'),'node':subprocess.check_output(['node','--version']).decode().strip(),'nodePlaywright':json.loads((B/'.runtime/pinned/node_modules/playwright/package.json').read_text())['version'],'browserVersions':{n:science[n]['version'] for n in science},'binaries':{}}
for p in list((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))+list((B/'.runtime/browsers').glob('webkit-*/minibrowser-wpe/bin/*'))+[B/'.runtime/webkit.sh']:
 if p.is_file():runtime['binaries'][str(p.relative_to(B))]=hashlib.sha256(p.read_bytes()).hexdigest()
(E/'runtime-manifest.json').write_text(json.dumps(runtime,indent=2)+'\n')
(E/'optimized-source-manifest.json').write_bytes((B.parent/'browser_eos_b9d/evidence/optimized-source-manifest.json').read_bytes())
write('PROTECTED_REFS_AND_PR3_AUDIT.md','''# Preservation audit

Exact B9D start: 20ddac46423a7a742af19ac415ef8796cf3a429f. All 2,958 starting tracked files retain SHA-256 identity. Accepted A2 be9eb35a, B9C b67afb32, B9D, C1/C2, B6/B7 and all other historical artifacts remain unchanged. The operator feature branch remains at 262b6092; production main, demo release candidate and every starting remote head/tag are protected. No tags existed in the starting ls-remote inventory.

evidence/remote-refs-before.txt and remote-refs-final.txt record every protected branch identity; local-refs-before.txt and preservation-final.json record local preservation. The only permitted new remote ref is research/b10-operator-workstation-shadow-hookup-20261018. PR #3 stays open at head d4422425750a1d3c4e432cc103ac42ead40b7cc6 and base 0473d32f62db992fde0f581d116e1bd0c8e7d8ed, with identity/body/status unchanged. Full snapshots are pr3-before.json and pr3-final.json. No PR comments or mutations are made.

All committed differences from B9D are additions under this B10 directory. No historical checkpoint, main/feature/release branch, original training/history/Assist, scientific source, deployment configuration or production artifact is modified. Final publication receipts refer to the preceding audited commit to avoid a self-referential commit hash. Re-run preservation.py with fresh connector/remote receipts to verify the final branch.
''')
print('Reports and CSV/JSON/XLSX decisions generated from passing receipts')
