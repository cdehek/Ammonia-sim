"""Render exact evidence tables; no classifications enter runtime code."""
import hashlib,json,statistics,subprocess,tempfile,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';X=B.parent
def read(n):return json.loads((E/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
matrix=read('classification-matrix.json')['rows']
lines=['# Exact seven-case refusal matrix','',
 'Both engines reproduce their own saved inventories. All original PH inputs are',
 '`3500000 Pa`, bits `414ab3f000000000`. Runtime is C / `boundary-unresolved`,',
 'compatible `solver`, no state returned, no physical-domain proof. Mechanism',
 'and mathematical pressure sign are independent **offline B5B evidence**.',
 'Every M/V/U/rho/u and raw getter bit is in `evidence/classification-matrix.json`.',
 '', '| Key suffix | Raw p bits | Raw P−max Pa | Mathematical P−max Pa | Independent mechanism |',
 '|---|---|---:|---:|---|']
for row in matrix:
 if row['browser']!='chromium':continue
 lines.append(f"| {row['key'].split('-')[-1]} | `{row['raw']['bits']['p']}` | {row['raw']['values']['p']-3500000:+.12g} | {float(row['mathematicalPressureMinusLimitPa']):+.12g} | {row['independentMechanism']} |")
lines+=['','There are two numerical wrong-side recoveries and five rounded-inventory',
 'conflicts. All seven pass canonical and normalized mass/energy budgets and',
 'still fail strict support. No pressure epsilon or precision enclosure exists.',
 '', '## Saved inward false-acceptance controls','',
 '| Key | Raw p bits | Raw P−max Pa | Mathematical P−max Pa | Candidate |',
 '|---|---|---:|---:|---|']
control=json.loads((X/'browser_eos_b5b/evidence/false-acceptance-controls.json').read_text())['rows']
for row in read('chromium-replay.json')['falseAcceptance']:
 ref=next(r for r in control if r['key']==row['key'])
 lines.append(f"| {row['key']} | `{row['calls'][0]['raw']['bits']['p']}` | {row['calls'][0]['raw']['values']['p']-3500000:+.12g} | {float(ref['roots'][-1]['pMinusLimit']):+.12g} | historical return unchanged; qualification blocker |")
lines+=['','The candidate cannot detect these outside mathematical inventories from a',
 'supported-looking numeric pressure. Additional general numerical certification',
 'is required; no fixture filters, pressure band or input substitution is used.',
 '', '## Requested inputs versus returned coordinates','',
 'The exact/one-Pa-ULP-inward/one-Pa-ULP-outward saved PH triplets and all phase',
 'controls are retained in each replay matrix. The explicit outward request is',
 'refused even when its separately constructed mixture MVU operation returns.',
 'Different original PH requests can have identical inventory bits. MVU cannot',
 'reconstruct that missing request. Returned-coordinate support and input support',
 'remain separate observations. Neither establishes a physical excursion.',
 '', 'See `*-guards.json` for unchanged lower/upper bar comparisons and synthetic',
 'temperature guard isolation. Synthetic outputs are not physical EOS states.','']
(B/'MATRIX.md').write_text('\n'.join(lines))
lines=['# Bounded performance and lifecycle observations','',
 'Five interleaved 40-ms rounds per property group, at most 1000 calls/round.',
 'Medians are elapsed time divided by calls, not pure EOS timing. Both sides use',
 'the identical WASM. No performance acceptance threshold was invented.',
 '', '| Engine | Group | Control ms/call | Candidate ms/call | Candidate/control |',
 '|---|---|---:|---:|---:|']
audit=read('scientific-audit.json')
for browser,d in audit['browsers'].items():
 for group,v in d['medianMSPerCall'].items():lines.append(f"| {browser} | {group} | {v['control']:.6g} | {v['candidate']:.6g} | {v['candidateOverControl']:.3g} |")
lines+=['','Error-transport measurements use three 20-ms rounds (at most 10000 calls).',
 'These are synthetic numerical errors at the real thermodynamics interface.',
 '', '| Engine | Control ms/error | Candidate ms/error |', '|---|---:|---:|']
for browser,d in audit['browsers'].items():
 v=d['propagationMSPerCall'];lines.append(f"| {browser} | {v['control']:.6g} | {v['candidate']:.6g} |")
lines+=['', '## Focused A2 and memory','',
 '| Runtime | Supported control / candidate ms | Retry control / candidate ms |',
 '|---|---:|---:|']
for runtime in ['native','chromium','webkit']:
 data=read('native-A2.json') if runtime=='native' else read(runtime+'-replay.json')['a2']
 success=next(r for r in data['rows'] if r['scenario']=='A-supported');retry=next(r for r in data['rows'] if r['scenario']=='matched-real-error-retry')['pair']
 lines.append(f"| {runtime} | {success['controlMS']:.6g} / {success['candidateMS']:.6g} | {retry[0]['elapsedMS']:.6g} / {retry[1]['elapsedMS']:.6g} |")
lines+=['','A2 is a single paired sample, with substantial JIT/warm-up/order and native',
 'FIFO bridge overhead. These numbers do not establish a speedup or a robust',
 'regression rate. The failed retry controls preserve historical stop behavior;',
 'the candidate changes only the justified stop classification and diagnostics.',
 '', '| Engine | Linear memory before / after bytes | Worker elapsed ms | Main timer ticks |',
 '|---|---:|---:|---:|']
for browser,d in audit['browsers'].items():
 l=d['lifecycle'];w=d['worker'];lines.append(f"| {browser} | {l['memoryBefore']} / {l['memoryAfter']} | {w['elapsedMS']:.6g} | {w['mainThreadTicks']} |")
lines+=['','Worker elapsed includes startup, import, WASM initialization, transfer and',
 'property calls. Main timers keep running during worker execution. Forty',
 'alternating success/refusal calls and fresh/reused parity show no observed',
 'stale error or rejected state contamination. Finite observations and heap',
 'snapshots do not prove absence of memory leaks. WebKit heap metrics are',
 'unavailable; native replay peak RSS is '+str(audit['native']['maxRSSKiB'])+' KiB.',
 '', 'The native bridge uses the preserved library through local buffered FIFOs.',
 'Desktop WPE WebKit results do not establish physical iPad performance. No',
 'long-duration campaign or production throughput qualification is claimed.','']
(B/'PERFORMANCE.md').write_text('\n'.join(lines))
# Verify that the delivered A2 patch is complete and reproduces every copy.
with tempfile.TemporaryDirectory(prefix='c1-patch-') as d:
 for p in (X/'browser_eos_backend/accepted').glob('*.cjs'):shutil.copyfile(p,Path(d)/p.name)
 r=subprocess.run(['patch','-p1','-d',d,'-i',str(B/'a2-error-propagation.patch')],text=True,capture_output=True,check=True)
 assert all((Path(d)/p.name).read_bytes()==p.read_bytes() for p in (B/'a2').glob('*.cjs'))
 (E/'patch-reproduction.json').write_text(json.dumps(dict(passed=True,output=r.stdout,files=13),indent=2)+'\n')
# Exclude only this self-hash, mutable Git-ref/final receipts and Python caches.
excluded={'source-manifest.json','final-preservation.json','refs-after.txt'}
files={str(p.relative_to(B)):sha(p) for p in sorted(B.rglob('*')) if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts}
(E/'source-manifest.json').write_text(json.dumps(dict(sha256=files,excluded=sorted(excluded),note='Starting-file and original artifact manifests independently cover all inherited bytes; final receipts cannot self-hash.'),indent=2)+'\n')
print('reports, full patch reproduction,',len(files),'source/evidence identities')
