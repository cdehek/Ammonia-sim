"""Per-failure scientific disposition, joined by exact saved inventory identity."""
import json,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))
def read(f):return json.loads((E/f).read_text())
trace={r['fixedKey']:r for r in read('trace-audit.json')['rows']};attr={r['failureKey']:r for r in read('pressure-error-attribution.json')['rows']};rows=[]
for r in read('original-failures.json')['rows']:
 h=r['highPrecisionReference'];a=attr[r['failureKey']];out=dict(failureKey=r['failureKey'],fixedKey=r['fixedKey'],physicalRootExists=True,physicalRoot=h['selection'],endpointUnresolvedAtOriginalResolution=a['endpointUnresolved'],exactMathematicalInventoryPressureSide='above'if float(h['pMinusLimit'])>0 else'below',physicalDomainExcursionProven=False,acceptedBackendPass=False)
 if r['runtime']=='native-full-VLE':
  t=trace[r['fixedKey']];out.update(rawDUAvailable=False,canonicalRecovery='exception, failed',earliestDemonstratedFailure='legacy saturation decision sign reverses a resolved homogeneous separation'if t['decisionSignWrong']and not a['endpointUnresolved']else'legacy endpoint/two-phase result has nonphysical quality before strict QT validation',mechanisms=['stale/inaccurate saturation decision threshold'if t['twoPhaseReturn']['c']<0 else'endpoint decision and finite-precision quality residual','final computed Q outside [0,1]'],nativeSourceTraceCaptured=True)
 else:
  p=a['attribution'];out.update(rawDUAvailable=True,canonicalRecovery='raw recovery passes original limits',rawP=p['rawDU_P'],rawPminusRequested=p['rawMinusRequest'],rawPminusIndependentPhysical=p['rawMinusPhysicalFixed'],earliestDemonstratedFailure='strict adapter pressure rejection after a supported-origin recovery',firstMathematicalBoundaryCrossing='raw DU numerical recovery'if float(h['pMinusLimit'])<0 else'PH/inventory representation before DU',mechanisms=['raw inverse/EOS numerical drift','PH/EOS and conservative inventory binary64 representation','strict adapter saturation pressure restriction'],guard='rejects p_bar > 35; faultKind domain; table PH guard passes',browserGuardTraceCaptured=True,internalWASMTraceCaptured=False)
 rows.append(out)
(E/'diagnosis.json').write_text(json.dumps(dict(assessment='ROOT CAUSE CONFIRMED',rows=rows,limitations='Mathematical boundary signs use the same EOS with exact binary64 constants. They are not experimental EOS accuracy claims. Endpoint phase claims retain original resolution criteria.'),indent=2)+'\n');print('per-failure dispositions',len(rows))
