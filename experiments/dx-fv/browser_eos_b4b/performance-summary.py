"""Descriptive medians from three bounded matched workload rounds."""
import json,os,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'));out={}
for runtime in ['native','chromium','webkit']:
 pairs={}
 for build in ['controlA','candidateB']:
  f=E/(f'performance-native-{build}.json'if runtime=='native'else f'{runtime}-{build}-cost.json');d=json.loads(f.read_text());assert'error'not in d
  if runtime!='native':assert'error'not in d['worker'] and all(not r['errors']for r in d['worker']['result']['rows'])
  assert all(not r['errors']for r in d['rows'])
  times={g:statistics.median([r['elapsedMS']*1000/r['calls']for r in d['rows']if r['group']==g])for g in {r['group']for r in d['rows']}}
  pairs[build]=dict(medianMicroseconds=times,maxRSSKiB=d.get('maxRSSKiB'),init=d.get('init'),linearMemory=d.get('memoryBytes'),jsHeap=d.get('jsHeap'),worker=d.get('mainThreadDuringWorker'))
 pairs['ratios']={g:pairs['candidateB']['medianMicroseconds'][g]/pairs['controlA']['medianMicroseconds'][g]for g in pairs['controlA']['medianMicroseconds']};out[runtime]=pairs
target=E/'performance-summary.json';text=json.dumps(out,indent=2)+'\n'
if target.exists():assert json.loads(target.read_text())==out
else:target.write_text(text)
print('All native/browser/worker matched workloads complete without property exceptions.')
