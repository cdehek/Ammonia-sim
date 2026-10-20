"""Deduplicate already-verified science; preserve canonical numerical traces."""
import gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';log=[]
for p in sorted(E.glob('*.jsonl.gz')):
 name=p.name[:-9]
 if name.startswith('initialization-') or name=='observed-cold-r1' or name=='external-budget-witness':continue
 raw=p.read_bytes();rows=[json.loads(x)for x in gzip.decompress(raw).decode().splitlines()]
 if any('scienceReference'in x or 'attemptsReference'in x for x in rows):continue
 header=next(r for r in rows if r['type']=='header');f=header['fixture'];schedule=header['schedule']
 reference=None
 if header['variant']=='observed':reference=('canonical-'+f+'-'+(name.rsplit('-',1)[-1]if name.rsplit('-',1)[-1]in ['added','fine']else'r1'))
 elif name.endswith(('-r2','-r3')) or name.startswith('control-'):reference='canonical-'+f+'-r1'
 if reference:
  source=[json.loads(x)for x in gzip.open(E/(reference+'.jsonl.gz'),'rt')]
  for r in rows:
   if r['type']=='checkpoint':
    origin=next(x for x in source if x['type']=='checkpoint'and x['seconds']==r['seconds']);assert origin['scienceHash']==r['scienceHash']and origin['attemptsHash']==r['attemptsHash']
    del r['science'];r['scienceReference']={'name':reference,'seconds':r['seconds']}
   if r['type']=='attempts':
    # Control baseline contains only prefix attempts; retain them rather than alias full horizon.
    if not name.startswith('control-'):del r['attempts'];r['attemptsReference']=reference
 if name.endswith(('-r2','-r3')):
  for r in rows:
   if r['type']=='diagnostics':
    r['temporals']=[];r['commits']=[];r['controllers']=[];r['columns']=[{'column':v['column'],'ms':v.get('ms',0)}for v in r['columns']];r['compactionNote']='Repeat detailed vectors omitted after exact equivalence; original r1 retains vectors, actual matrix hashes retained here.'
 compressed=gzip.compress(('\n'.join(json.dumps(r,separators=(',',':'))for r in rows)+'\n').encode(),mtime=0)
 p.write_bytes(compressed);log.append(dict(file=p.name,beforeBytes=len(raw),afterBytes=len(compressed),beforeSHA256=hashlib.sha256(raw).hexdigest(),afterSHA256=hashlib.sha256(compressed).hexdigest(),reference=reference))
(E/'receipt-compaction.json').write_text(json.dumps(log,indent=2)+'\n')
print('Compacted',len(log),'receipts; rerun exact verifiers to validate resolution')
