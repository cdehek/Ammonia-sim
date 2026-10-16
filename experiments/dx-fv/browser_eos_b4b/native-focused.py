"""Immutable B3 cases, independent EOS references, signed probes and A/B/C ledgers.

Reference roots are diagnostic only; the tested backend never consumes them.
"""
import os
import argparse,ctypes as ct,json,math,sys,time
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent.parent/'browser_eos_b4a';R=B.parents[2];E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'))
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,root,inventory,pack,save,bits
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--label',required=True);ap.add_argument('--output',required=True);ap.add_argument('--full-vle',action='store_true');ap.add_argument('--primary-only',action='store_true');args=ap.parse_args()
eos=Backend(args.library);audit=Backend();sat=Backend()
if args.full_vle:
 eos.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];eos.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
old=json.loads((B.parent/'browser_eos_b3/evidence/chromium-build44.json').read_text())['rows']
requests=json.loads((B.parent/'browser_eos_b3/inputs.json').read_text())
requests+= [dict(id='B1-liquid-precision',mode='PH',args=[30298.937123458254,94523.34612321304])]
for p in sorted({q['args'][0] for q in requests}):
 f=sat.state('PQ',p,0);g=sat.state('PQ',p,1)
 requests += [dict(id=f'focused-{p}-{name}',mode='PH',args=[p,h])for name,h in [('stable-liquid',f['h']-1000),('mixture',f['h']+.4*(g['h']-f['h'])),('stable-vapor',g['h']+10000)]]
 for endpoint,s in [('hf',f),('hg',g)]:
  for sign in [-1,1]:requests.append(dict(id=f'ULP-{p}-{endpoint}-{sign}',mode='PH',args=[p,math.nextafter(s['h'],-math.inf if sign<0 else math.inf)],origin='diagnostic one-ULP endpoint neighbor'))
# Once recorded, the complete B4A matrix is authoritative on every replay.
if (B/'inputs.json').exists():
 saved=json.loads((B/'inputs.json').read_text());assert saved[:57]==json.loads((B.parent/'browser_eos_b3/inputs.json').read_text());requests=saved
if args.primary_only:requests=[q for q in requests if q['id'] in ['B1-vapor-regression','approach-30298.937123458254-liquid-0.001','B1-liquid-precision']]
def reference(p,h):
 f=sat.state('PQ',p,0);g=sat.state('PQ',p,1);df=h-f['h'];dg=h-g['h']
 phase='liquid' if df < -1e-8 else 'gas' if dg>1e-8 else 'equilibrium' if df>1e-8 and dg< -1e-8 else 'endpoint-unresolved'
 out=dict(physicalPhase=phase,hMinusHf=df,hMinusHg=dg,rawQuality=(h-f['h'])/(g['h']-f['h']),saturation=dict(liquid=pack(f),vapor=pack(g)))
 if phase in ('liquid','gas'):
  s=f if phase=='liquid' else g;out['reference']=root(p,h,phase,(s['rho'],s['T']))
 return out
def sample(p,h):
 ref=reference(p,h);t=time.perf_counter();s=eos.state('PH',p,h);elapsed=time.perf_counter()-t;dt=audit.state('DT',s['rho'],s['T'])
 return dict(p=p,h=h,inputBits=[bits(p),bits(h)],PH=pack(s),independentDT=pack(dt),residuals=dict(p=dt['p']-p,h=dt['h']-h),elapsedSeconds=elapsed,supportedInput=3e4<=p<=35e5,**ref)
rows=[]
for q in requests:
 p,h=q['args'];row=dict(request=q,probes=[])
 print(json.dumps(dict(marker=q['id'],args=[p,h],inputBits=[bits(p),bits(h)])),file=sys.stderr,flush=True)
 try:
  base=sample(p,h);row['base']=base;s=base['PH']['values'];row['inventories']={}
  previous=next((r for r in old if r['id']==q['id']),None)
  rt=base.get('reference',{});a=rt.get('state') if rt.get('converged') else None
  for name,state in [('A',a),('B',previous['base']['state'] if previous else None),('C',s)]:
   if state:row['inventories'][name]=inventory(eos,p,h,state['rho'],state['T'])
  # The exact B3 signed input values are reused, not re-created from decimal text.
  if previous:
   probes=[(r['axis'],r['step'],r['output']['p'],r['output']['h'])for r in previous['probes']]
  else:
   dp=1e-7*max(1,abs(p/1e5))*1e5;dh=1e-8*max(1,abs(h/1000))*1000
   probes=[(axis,sign*step,p+(sign*step if axis=='P' else 0),h+(sign*step if axis=='H' else 0))for axis,step in [('P',dp),('H',dh)]for sign in [1,-1]]
  for axis,step,pp,hh in probes:
   probe=dict(axis=axis,step=step,actualIncrement=pp-p if axis=='P' else hh-h)
   try:
    v=sample(pp,hh);probe['output']=v;rho=v['PH']['values']['rho'];same=base['physicalPhase']==v['physicalPhase'] and base['physicalPhase'] in ('liquid','gas')
    probe['samePhysicalBranch']=same;probe['finite']=(rho-s['rho'])/step
    if same and rt.get('converged'):
     deriv=rt['derivatives']['rhoP' if axis=='P' else 'rhoH'];contamination=abs(rho-s['rho']-deriv*step);V=.003/5
     probe.update(analytic=deriv,ratio=probe['finite']/deriv,normalizedMassProbeContamination=V*contamination/max(.01,s['rho']*V),nonlinearScale=1e-11)
     M=s['rho']*V;U=M*(h/1000)-p*V/1000;newU=rho*V*(hh/1000)-pp*V/1000
     dU=deriv*V*(h/1000)+(-V/1000 if axis=='P'else M/1000)
     probe['normalizedEnergyProbeContamination']=abs(newU-U-dU*step)/max(1,abs(U))
     probe['nonlinearScalePass']=probe['normalizedMassProbeContamination']<=1e-11 and probe['normalizedEnergyProbeContamination']<=1e-11
    else:probe['derivativeExclusion']='Physical crossing, coexistence, or unresolved endpoint'
   except Exception as exc:probe['error']=str(exc)
   row['probes'].append(probe)
  if q['id']=='B1-vapor-regression':
   pt=eos.state('PT',p,s['T']);dt=audit.state('DT',pt['rho'],pt['T']);row['PT']=pack(pt);row['PTindependentDT']=pack(dt);row['PTcacheDifference']={k:pt[k]-dt[k]for k in ['p','h','u']}
 except Exception as exc:row['error']=str(exc)
 rows.append(row)
perf=[] # Dedicated performance campaign is gated separately.
save(Path(args.output),dict(label=args.label,library=args.library,fullVLE=args.full_vle,wheelVersion=CoolProp.__version__,wheelRevision=CoolProp.__gitrevision__,rows=rows,performance=perf,physicalIPad=False))
print(args.label,len(rows),'rows;',sum('error'in r for r in rows),'base errors')
