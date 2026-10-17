"""Keep rounded-DU math, exact M/U/V local proofs and adapter outcomes separate."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';read=lambda p:json.loads(p.read_text())
hp={r['key']:r['reference'] for r in read(E/'high-precision-references.json')['rows']}
c2=read(X/'browser_eos_b5b_c2_p1/evidence/c2-reproduction.json');exact={r['key']:r for r in c2['rows']};rows=[]
for engine in ['chromium','webkit']:
 blocks=read(E/f'c1-{engine}-explicit-bar.json')['result']['rows']
 for r in next(q for q in blocks if q['id']=='gateA' and not q['fullVLE'])['cases']:
  key=r['key'];reference=hp[key]
  matches=[q for q in exact.values() if q['inputBits']==r['input']['bits']]
  assert len(matches)==1,(key,len(matches));proof=matches[0]['trials'][-1]
  rows.append(dict(engine=engine,key=key,input=r['input'],defaultRaw=r.get('raw'),defaultAdapterError=r['error'],roundedDUMathematicalSelection=reference['selection'],roundedDUPressureMinusLimitPa=reference['pMinusLimit'],roundedDUReferenceResolution='1e-5 Pa / 1e-8 J/kg; sub-resolution mathematical side is not original physical qualification',exactMUVProofSourceKey=matches[0]['key'],exactMUVLocalPressureSide=proof['localPressureSide'],exactMUVLocalPressureMinusLimitPa=proof['pMinusLimitPa'],exactMUVPhysicalBranchCertified=proof['physicalBranchCertified'],exactMUVFullInventoryCertified=proof['fullInventoryCertified'],explicitOriginPHSupport='The preserved original PH request was exactly 35 bar; recovered inventory support is a different question',physicalTrajectoryExit='unproved',numericalEnclosureImplementedInRuntime=False))
out=dict(rows=rows,roundedDUHistoricalSplit=c2['roundedDUHistoricalSplit'],exactMUVSplit=c2['exactMUVSplit'],scope='Read-only attribution of preserved mathematics, not a new certificate or runtime support decision',twoInwardHazardsRemainUnqualified=True)
p=E/'support-attribution.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Original seven attribution retained; rounded DU and exact M/U/V remain distinct')
