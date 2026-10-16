"""Separate PH coordinate error, inventory rounding and DU recovery drift."""
import importlib.util,json,sys,struct
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))
spec=importlib.util.spec_from_file_location('hp',B/'high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
def bits(x):return struct.pack('>d',float(x)).hex()
fail=json.loads((E/'original-failures.json').read_text())['rows'];rows=[];referenceInventories=[]
# Independent fixed-pressure saturation, with displaced initial seeds.
seed=fail[0]['independentReference']['equilibrium'];rL0=seed['liquid']['values']['rho'];rV0=seed['vapor']['values']['rho'];T0=seed['state']['values']['T']
def sat_res(rL,rV,T):
 l,g=hp.eos(rL,T),hp.eos(rV,T);return ((l['p']-3500000)/1e6,(g['p']-3500000)/1e6,(l['g']-g['g'])/1e6)
rL,rV,Ts=mp.findroot(sat_res,(rL0*1.000001,rV0*.999999,T0+.01),tol=mp.mpf('1e-52'));L,G=hp.eos(rL,Ts),hp.eos(rV,Ts)
for r in fail:
 p,h=map(mp.mpf,r['originalPHInput']);ph=r['originalPH']['values'];x=r['fixedInput']['values'];d,u=mp.mpf(x['rho']),mp.mpf(x['u']);rh,T=mp.mpf(ph['rho']),mp.mpf(ph['T']);cal=hp.eos(rh,T)
 hc=h-L['h'];hg=h-G['h']
 if hc<0 or hg>0:
  rr,tt=mp.findroot(lambda z,t:((hp.eos(z,t)['p']-p)/1e6,(hp.eos(z,t)['h']-h)/1e6),(rh,T),tol=mp.mpf('1e-52'));physicalPH=hp.eos(rr,tt);phase='liquid'if hc<0 else'vapor'
 else:
  q=(h-L['h'])/(G['h']-L['h']);rr=1/((1-q)/rL+q/rV);tt=Ts;physicalPH=dict(p=p,h=h,rho=rr,T=tt,u=h-p/rr,Q=q);phase='two-phase'
 # The stable homogeneous original cases admit this differential decomposition.
 fixed=r['highPrecisionReference'];selected=fixed[fixed['selection']];pf=mp.mpf(selected['p']);pu=mp.mpf(fixed['conditioning']['pU_rho']);pr=mp.mpf(fixed['conditioning']['pRho_u'])
 uideal=h-p/rh;dr=d-rh;du_round=u-uideal;du_ph=uideal-cal['u']
 raw=r['originalRecovery'].get('DU',{}).get('values');pd=mp.mpf(raw['p'])if raw else None
 vals=dict(requestP=p,PH_eosP=cal['p'],fixedPhysicalP=pf,PH_eosPminusRequest=cal['p']-p,PH_hResidual=cal['h']-h,PH_uResidualToIdeal=cal['u']-uideal,densityRoundoff=dr,uInventoryRoundoff=du_round,inventoryPressureShift=pf-cal['p'],linearRhoContribution=pr*dr,linearURoundoffContribution=pu*du_round,linearPHCaloricContribution=pu*du_ph,linearizationRemainder=pf-cal['p']-pr*dr-pu*(du_round+du_ph),hMinusHf=hc,hMinusHg=hg)
 if pd is not None:vals.update(rawDU_P=pd,rawMinusPhysicalFixed=pd-pf,rawMinusRequest=pd-p,convertedBar=mp.mpf(raw['p']/1e5),conversionRoundoffBar=mp.mpf(raw['p']/1e5)-pd/100000)
 V=.003/5;rrf=float(rr);ttf=float(tt);M=rrf*V;U=M*(float(h)/1000)-100*(float(p)/1e5)*V;di=M/V;ui=(U/M)*1000
 ref=dict(failureKey=r['failureKey'],origin='new-independent-PH-reference',requestedP=float(p),requestedH=float(h),referenceT=ttf,referenceRho=rrf,input=dict(M=M,V=V,U_kJ=U,rho=di,u=ui));ref['bits']={k:bits(v)for k,v in ref['input'].items()};referenceInventories.append(ref)
 rows.append(dict(failureKey=r['failureKey'],phase=phase,endpointUnresolved=abs(hc)<mp.mpf('1e-8')or abs(hg)<mp.mpf('1e-8'),linearizationApplicability='homogeneous only; endpoint/coexistence decomposition is diagnostic and not a stable-mixture derivative',physicalPH=hp.enc(physicalPH),attribution=hp.enc(vals),originalPHBits={k:bits(v)for k,v in ph.items()},originalCanonicalError=r['originalRecovery'].get('canonicalDifferences',r['originalRecovery'].get('differences')),normalizedPHInventoryEnergyMismatch=float(abs(mp.mpf(x['M'])*cal['u']/1000-mp.mpf(x['U_kJ']))/max(1,abs(x['U_kJ'])))))
(E/'pressure-error-attribution.json').write_text(json.dumps(dict(saturation=dict(liquid=hp.enc(L),vapor=hp.enc(G)),rows=rows,precisionNote='Same-EOS high precision isolates arithmetic; it does not establish experimental EOS accuracy at nanopa scale.'),indent=2)+'\n')
(E/'reference-inventories.json').write_text(json.dumps(referenceInventories,indent=2)+'\n');print('attributed',len(rows),'original failure records')
