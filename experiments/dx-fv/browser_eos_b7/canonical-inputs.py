"""Extract original PH provenance only; never rerun PH to construct DU inputs."""
import hashlib,json,struct
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
read=lambda p:json.loads(p.read_text())
bits=lambda v:struct.pack('>d',v).hex()
metadata={}
for full in [False,True]:
 p=X/'browser_eos_b4c/evidence'/('native-candidateB'+('-full-vle' if full else '')+'.json')
 for r in read(p)['rows']:metadata[(r['request']['id'],full)]=(p,r)
rows={}
historical=read(X/'browser_eos_b4b/evidence/35bar-fixed-inventories.json')['rows']
for r in read(E/'fixed-inputs.json'):
 p,m=metadata[(r['id'],r['fullVLE'])];pp,hh=m['request']['args'];s=m['base']['PH']['values']
 if r['origin']=='historical-B4B-fixed-ledger':
  old=historical[int(r['key'].rsplit('-',1)[1])]
  assert old['input']==r['input']
  p=X/'browser_eos_b4b/evidence'/('native-'+old['origin']+('-full-vle' if r['fullVLE'] else '')+'.json')
  m=next(q for q in read(p)['rows'] if q['request']['id']==r['id']);pp,hh=m['request']['args']
  s=m['base']['reference']['state'] if old['inventory']=='A' else m['base']['PH']['values']
 if r['origin'].startswith(('chromium-','webkit-')):
  engine,origin=r['origin'].split('-',1);p=X/f'browser_eos_b4c/evidence/{engine}-{origin}-focused.json'
  m=next(q for q in read(p)['rows'] if q['id']==r['id']);pp,hh=m['args'];s=m['base']['state']
 V=.003/5;M=s['rho']*V;U=M*(hh/1000)-100*(pp/1e5)*V
 computed=dict(V=V,M=M,U_kJ=U,rho=M/V,u=(U/M)*1000)
 assert all(bits(v)==r['input']['bits'][k] for k,v in computed.items()),r['key']
 rows[r['key']]=dict(p=pp,h=hh,T=s['T'],originalPH=s,source=str(p.relative_to(X)),sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),exactOriginalArithmetic=True)
(E/'canonical-provenance.json').write_text(json.dumps(rows,indent=2)+'\n')
print('All 250 original conservative constructions reproduce bit-exactly from preserved PH records; no PH rerun')
