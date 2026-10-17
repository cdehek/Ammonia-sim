"""Parse actual generated WASM imports/exports, function types and memory limits."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
class Reader:
 def __init__(self,b):self.b=b;self.i=0
 def byte(self):v=self.b[self.i];self.i+=1;return v
 def uint(self):
  v=shift=0
  while True:
   c=self.byte();v|=(c&127)<<shift
   if not c&128:return v
   shift+=7
 def name(self):n=self.uint();s=self.b[self.i:self.i+n].decode();self.i+=n;return s
 def limits(self):
  flags=self.uint();out=dict(flags=flags,min=self.uint())
  if flags&1:out['max']=self.uint()
  return out
def parse(p):
 raw=p.read_bytes();assert raw[:8]==b'\0asm\x01\0\0\0';r=Reader(raw);r.i=8;sections={}
 while r.i<len(raw):
  n=r.byte();size=r.uint();start=r.i;sections[n]=raw[start:start+size];r.i+=size
 r=Reader(sections[1]);types=[];names={0x7f:'i32',0x7e:'i64',0x7d:'f32',0x7c:'f64',0x70:'funcref',0x6f:'externref'}
 for _ in range(r.uint()):
  assert r.byte()==0x60;params=[names[r.byte()] for _ in range(r.uint())];results=[names[r.byte()] for _ in range(r.uint())];types.append(dict(params=params,results=results))
 imports=[];function_types=[];r=Reader(sections[2])
 for _ in range(r.uint()):
  row=dict(module=r.name(),name=r.name());kind=r.byte();row['kind']=kind
  if kind==0:t=r.uint();function_types.append(t);row['signature']=types[t]
  elif kind==1:row.update(element=r.byte(),limits=r.limits())
  elif kind==2:row['limits']=r.limits()
  elif kind==3:row.update(valueType=r.byte(),mutable=r.byte())
  else:raise ValueError(('unexpected import',kind))
  imports.append(row)
 r=Reader(sections[3]);function_types.extend(r.uint() for _ in range(r.uint()))
 r=Reader(sections[5]);memories=[r.limits() for _ in range(r.uint())]
 r=Reader(sections[7]);exports=[]
 for _ in range(r.uint()):
  name,kind,index=r.name(),r.byte(),r.uint();row=dict(name=name,kind=kind)
  if kind==0:row['signature']=types[function_types[index]]
  exports.append(row)
 return dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),imports=imports,exports=exports,memories=memories)
old=parse(B.parent/'browser_eos_b4c/vendor/candidateB/coolprop.wasm');rows={}
for label in ['control','candidate','control-diagnostic','candidate-diagnostic']:
 q=parse(B/'vendor'/label/'coolprop.wasm')
 q['importSignaturesMatchHistorical']=q['imports']==old['imports'];q['exportSignaturesMatchHistorical']=q['exports']==old['exports'];q['memoryLimitsMatchHistorical']=q['memories']==old['memories']
 assert all(q[k] for k in ['importSignaturesMatchHistorical','exportSignaturesMatchHistorical','memoryLimitsMatchHistorical']),label
 rows[label]=q
t=E/'wasm-abi-inventory.json';assert not t.exists();t.write_text(json.dumps(dict(historical=old,builds=rows,allMatch=True),indent=2)+'\n')
print('Actual imports, exports, signatures and memory limits match historical B6 artifact for all four B7 modules')
