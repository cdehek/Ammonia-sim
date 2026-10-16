"""Archived native C ABI, no build or source repair; JSON bridge for JS wrapper."""
import ctypes as ct,hashlib,json,lzma,struct,sys,time,resource
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';D=Path('/workspace/c1-native')
def bits(x):return struct.pack('>d',x).hex()
def pack(s):return dict(values=s,bits={k:bits(v) for k,v in s.items()})
class Native:
 def __init__(self,label='B4C'):
  folder,archive=('browser_eos_b4c','libCoolProp-candidateB.so.xz') if label=='B4C' else ('browser_eos_b5a','libCoolProp-A1.so.xz')
  manifest=json.loads((X/folder/'evidence/native-binaries.json').read_text())
  entry=next(v for v in manifest.values() if v['archive']=='artifacts/'+archive)
  raw=(X/folder/entry['archive']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['archiveSHA256']
  D.mkdir(exist_ok=True);p=D/(label+'.so')
  if not p.exists():p.write_bytes(lzma.decompress(raw))
  assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
  self.L=L=ct.CDLL(str(p));self.sha=entry['sha256']
  L.AbstractState_factory.restype=ct.c_long
  L.AbstractState_factory.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
  L.AbstractState_update.argtypes=[ct.c_long,ct.c_long,ct.c_double,ct.c_double,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
  L.AbstractState_keyed_output.restype=ct.c_double
  L.AbstractState_keyed_output.argtypes=[ct.c_long,ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
  for n in ['get_param_index','get_input_pair_index']:
   getattr(L,n).argtypes=[ct.c_char_p];getattr(L,n).restype=ct.c_long
  L.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
  self.handle=self.call(L.AbstractState_factory,b'HEOS',b'Ammonia')
 def call(self,f,*a):
  err=ct.c_long();msg=ct.create_string_buffer(4096);out=f(*a,ct.byref(err),msg,4096)
  if err.value:raise ValueError(msg.value.decode())
  return out
 def state(self,mode,a,b):
  pair,x,y={'PH':('HmassP_INPUTS',b,a),'DU':('DmassUmass_INPUTS',a,b),'DT':('DmassT_INPUTS',a,b),'PQ':('PQ_INPUTS',a,b),'PT':('PT_INPUTS',a,b)}[mode]
  self.call(self.L.AbstractState_update,self.handle,self.L.get_input_pair_index(pair.encode()),x,y)
  return {k:self.call(self.L.AbstractState_keyed_output,self.handle,self.L.get_param_index(v.encode())) for k,v in dict(p='P',T='T',rho='Dmass',h='Hmass',u='Umass',Q='Q',phase='Phase',s='Smass').items()}
 def evaluate(self,q):
  if q.get('fullVLE'):
   self.L.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
   try:return self.evaluate({k:v for k,v in q.items() if k!='fullVLE'})
   finally:self.L.set_config_bool(b'ENABLE_SUPERANCILLARIES',True)
  if q['mode']!='SAT':return {k:v for k,v in self.state(q['mode'],*q['args']).items() if k!='phase'}
  p=q['args'][0];a=self.state('PQ',p,0);b=self.state('PQ',p,1)
  return dict(p=a['p'],T=a['T'],hf=a['h'],hg=b['h'],sf=a['s'],sg=b['s'],rhof=a['rho'],rhog=b['rho'])
def run():
 fixed=json.loads((X/'browser_eos_b5/evidence/fixed-inputs.json').read_text());old={r['key']:r['result']['B4C'] for r in json.loads((X/'browser_eos_b5/evidence/native-fixed-replay.json').read_text())['rows']}
 e=Native();rows=[]
 for q in fixed:
  e.L.set_config_bool(b'ENABLE_SUPERANCILLARIES',not q['fullVLE']);x={k:struct.unpack('>d',bytes.fromhex(v))[0] for k,v in q['input']['bits'].items()}
  try:
   s=e.state('DU',x['rho'],x['u']);s.pop('s');result=dict(DU=pack(s));assert result['DU']==old[q['key']]['DU']
  except ValueError as ex:result=dict(error=str(ex));assert result['error']==old[q['key']]['error']
  rows.append(dict(key=q['key'],input=q['input'],result=result,exactHistoricalMatch=True))
 # Gate A native correction stays native-only and endpoints unresolved.
 gate=Native('GateA');gateRows=[]
 for q in fixed:
  if q['key'] not in ['native-ledger-146','native-ledger-148','native-ledger-151','native-ledger-152','native-ledger-162','native-ledger-164','native-ledger-165']:continue
  gate.L.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
  x=q['input']['values']
  try:result=dict(raw=pack(gate.state('DU',x['rho'],x['u'])))
  except ValueError as ex:result=dict(error=str(ex))
  gateRows.append(dict(key=q['key'],result=result,qualification='native control only; endpoint physical qualification unresolved'))
 out=dict(passed=True,librarySHA256=e.sha,gateALibrarySHA256=gate.sha,rows=rows,gateA=gateRows,maxRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 (E/'native-replay.json').write_text(json.dumps(out,indent=2)+'\n');print('native',len(rows),'exact archived outcomes; Gate A controls',len(gateRows))
if __name__=='__main__':
 if '--server' in sys.argv:
  with open(sys.argv[2]) as requests,open(sys.argv[3],'w') as responses:
   e=Native()
   for line in requests:
    try:result=dict(raw=e.evaluate(json.loads(line)))
    except Exception as ex:result=dict(error=str(ex))
    responses.write(json.dumps(result)+'\n');responses.flush()
 elif '--rpc' in sys.argv:
  try:print(json.dumps(dict(raw=Native().evaluate(json.loads(sys.stdin.read())))))
  except Exception as e:print(json.dumps(dict(error=str(e))))
 else:run()
