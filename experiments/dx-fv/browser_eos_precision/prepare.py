"""Read-only checkpoint and deterministic diagnostic inputs. Research only."""
from pathlib import Path
import hashlib,json,math,struct,subprocess
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'browser_eos'
def bits(x):return struct.pack('>d',x).hex()
def save(name,x):
 p=B/name
 if p.exists():
  assert json.loads(p.read_text())==x, f'Retain evidence; mismatch: {p}'
 else:p.write_text(json.dumps(x,indent=2)+'\n')
files=subprocess.check_output(['git','ls-tree','-r','--name-only','f17623f61592bd897200206692ec002088f0a605'],cwd=R,text=True).splitlines()
save('evidence/checkpoint.json',{'repository':subprocess.check_output(['git','remote','get-url','origin'],cwd=R,text=True).strip(),'startingCommit':'f17623f61592bd897200206692ec002088f0a605','acceptedA2':'be9eb35a4ddf5098e685182f8104685127c6a6ee','originalFiles':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},'priorStudy':'Complete at starting commit; retain all browser_eos evidence unchanged. New precision diagnostics and physical-iPad preparation were unfinished.'})
old=json.loads((OLD/'inputs.json').read_text());requests=old['requests']
p,h=next(q['args'] for q in requests if q['id']=='p0.3029893712344606-liquid-z1.0-PH')
assert (p,h)==(30298.937123458254,94523.34612321304)
cases=[{'id':'exact-saved','args':[p,h],'primary':True},{'id':'nominal-text','args':[.3029893712344606*1e5,94.52334612321303*1000]}]
for axis in [0,1]:
 for direction in [-math.inf,math.inf]:
  a=[p,h];a[axis]=math.nextafter(a[axis],direction);cases.append({'id':f'one-ulp-{axis}-{direction}','args':a})
cases += [{'id':q['id'],'args':q['args'],'historical':q.get('historical',False)} for q in requests if q['mode']=='PH' and q['region']=='liquid']
for q in cases:
 q['inputBits']=[bits(x) for x in q['args']]
 q['dp']=1e-7*max(1,abs(q['args'][0]/1e5))*1e5
 q['dh']=1e-8*max(1,abs(q['args'][1]/1000))*1000
save('inputs.json',{'units':'SI mass based, default HEOS reference; no fitting or input rounding','sourceSHA256':hashlib.sha256((OLD/'inputs.json').read_bytes()).hexdigest(),'steps':'Accepted forward pressure/enthalpy steps; sweeps are diagnostic only. Primary dp remains 0.01 Pa.','cases':cases,'sweep':[.0001,.001,.003,.01,.03,.1,.3,1,3,10],'methods':['fresh','reused','reverse','after-PT','after-PQ','after-DU','molar','high','high-liquid']})
print('Preserved',len(files),'original files; prepared',len(cases),'liquid inputs')
