"""Deduplicate bit-identical scientific payloads, retaining measurements and hashes."""
import gzip,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(p):
 rows=[]
 for l in gzip.open(p,'rt'):
  try:rows.append(json.loads(l))
  except json.JSONDecodeError:pass
 return rows
base={f:read(E/f'canonical-{f}-010-r1.jsonl.gz') for f in ['cold','warm']}
reference={f:{r['seconds']:r for r in rows if r['type']=='checkpoint'} for f,rows in base.items()}
report=json.loads((E/'receipt-deduplication.json').read_text()) if (E/'receipt-deduplication.json').exists() else []
for p in sorted(E.glob('*.jsonl.gz')):
 if p.name in ['canonical-cold-010-r1.jsonl.gz','canonical-warm-010-r1.jsonl.gz']:continue
 rows=read(p)
 if any('scienceReference' in r for r in rows):continue
 if not any(r['type']=='complete' for r in rows):continue # preserve terminated streams as recorded
 result=[];count=0
 for r in rows:
  if r['type']=='partial-progress':continue # completion and referenced canonical trace retain committed path
  if r['type']=='checkpoint':
   src=reference[r['fixture']][r['seconds']]
   assert r['scienceHash']==src['scienceHash'] and r['attemptsHash']==src['attemptsHash']
   assert r['scienceExact']==src['scienceExact']
   for k in ['science','scienceExact','attempts']:r.pop(k)
   r['scienceReference']={'file':f"canonical-{r['fixture']}-010-r1.jsonl.gz",'seconds':r['seconds'],'scope':'science, scienceExact and cumulative attempts; bit-exact hash equality checked before compaction'};count+=1
  result.append(r)
 backup=B/'.runtime'/('full-'+p.name);shutil.copyfile(p,backup)
 before=p.stat().st_size
 with gzip.open(p,'wt',compresslevel=9) as z:
  for r in result:z.write(json.dumps(r,separators=(',',':'))+'\n')
 report.append(dict(file=p.name,checkpoints=count,allScientificPayloadsExact=True,bytesBefore=before,bytesAfter=p.stat().st_size))
(E/'receipt-deduplication.json').write_text(json.dumps(report,indent=2)+'\n')
print('Deduplicated',len(report),'complete runs; retained canonical payloads and all independent timings/profiles')
