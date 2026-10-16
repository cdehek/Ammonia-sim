"""Offline decision prototype. Outputs classifications, NEVER property states.

All reference claims are research evidence, not runtime numerical certificates.
Hypothetical contract tests are labeled and cannot qualify an observed state.
"""
import hashlib,json
from collections import Counter
from decimal import Decimal as D
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
def read(p):return json.loads(p.read_text())
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def binding(bits):return hashlib.sha256(json.dumps(bits,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def decide(e):
    """Evidence capability flags are supplied by the offline trusted ledger only."""
    if e.get('requestedUnsupported'):
        c,reason='E','The original explicit requested coordinate is outside support; inward recovery cannot authorize it.'
    elif e.get('physicalTrajectoryProofVerified'):
        c,reason='A','Independent resolved trajectory-domain proof (hypothetical test capability only).'
    elif e.get('inverseFailed') or e.get('numericalRequirementsFailed'):
        c,reason='B','No qualified raw recovery: inverse exception or a failed original numerical requirement; no domain-exit inference.'
    elif e.get('unresolved') or not e.get('evidenceBoundToInput',False):
        c,reason='C','Boundary or provenance is unresolved. Mathematical sign and raw canonical accuracy alone cannot accept it.'
    elif e.get('adapterAccepted') and e.get('originalGatesPass') and e.get('focusedSupportResolved'):
        c,reason='D','Observed adapter success plus independent focused support, phase and original numerical gates; no backend qualification.'
    else:
        c,reason='C','Insufficient evidence for successful supported recovery or physical-domain exit; retain refusal.'
    return dict(proposedClass=c,justification=reason,propertyStateReturned=False,physicalTrajectoryExitEstablished=c=='A',compatibilityFaultKind=None if c=='D' else 'domain' if c in ['A','E'] else 'solver',hypothetical=e.get('hypothetical',False))
rows=[]
seven=read(E/'seven-case-analysis.json')['rows']
for r in seven:
    evidence=dict(adapterAccepted=False,originalGatesPass=True,evidenceBoundToInput=True,unresolved=True)
    rows.append(dict(id=r['key'],observedAdapterAccepted=False,observedFaultKind='domain',mechanism=r['mechanism'],inputBinding=binding(r['fixedInput']['bits']),evidence=evidence,proposal=decide(evidence)))
for r in read(E/'false-acceptance-controls.json')['rows']:
    e=dict(adapterAccepted=True,unresolved=True,evidenceBoundToInput=True)
    rows.append(dict(id=r['key'],observedAdapterAccepted=True,mechanism='numerical-wrong-side-inward',inputBinding=binding(r['original']['input']['bits']),evidence=e,proposal=decide(e),referenceScope='same-EOS mathematical outside; below original physical/reference resolution; not a physical excursion proof'))
mathematics={r['id']:r for r in read(E/'matrix-mathematics.json')['rows']}
for r in read(E/'chromium-replay.json')['matrix']:
    m=mathematics[r['id']];delta=D(m['pMinusLimit'])
    # 1e-5 Pa is the inherited independent-reference resolution, NOT a support
    # tolerance or a rigorous interval bound. It can force uncertainty only.
    unresolved=abs(delta)<=D('0.00001')
    supportResolved=delta < -D('0.00001')
    e=dict(requestedUnsupported=r['request']['values']['p']>3500000,adapterAccepted='adapter' in r,originalGatesPass=m['canonicalPass'] and m['nonlinearPass'],unresolved=unresolved,focusedSupportResolved=supportResolved,evidenceBoundToInput=True)
    rows.append(dict(id=r['id'],observedAdapterAccepted='adapter' in r,observedFaultKind=r.get('error',{}).get('faultKind'),evidence=e,proposal=decide(e),referenceScope='offline focused same-EOS evidence; no interval certificate or new runtime policy'))
gate=read(B.parent/'browser_eos_b5a_gate_b/evidence/four-case-reproduction-and-controls.json')
# Real retained exception evidence, not a new native run or a repaired Gate B.
for key in ['native-ledger-148','native-ledger-164','native-ledger-165']:
    e=dict(inverseFailed=True,evidenceBoundToInput=True)
    rows.append(dict(id='inherited-Gate-B/'+key,observedAdapterAccepted=False,source='../browser_eos_b5a_gate_b/evidence/four-case-reproduction-and-controls.json',evidence=e,proposal=decide(e)))
tests=[]
for name,e,expected in [
 ('hypothetical-resolved-trajectory-proof',dict(physicalTrajectoryProofVerified=True,hypothetical=True),'A'),
 ('unverified-claimed-proof',dict(unresolved=True,evidenceBoundToInput=False,hypothetical=True),'C'),
 ('stale-origin-certificate',dict(adapterAccepted=True,originalGatesPass=True,focusedSupportResolved=True,evidenceBoundToInput=False,hypothetical=True),'C'),
 ('wrong-EOS-certificate',dict(adapterAccepted=True,originalGatesPass=True,focusedSupportResolved=True,evidenceBoundToInput=False,hypothetical=True),'C'),
 ('inward-result-from-unsupported-request',dict(requestedUnsupported=True,adapterAccepted=True,hypothetical=True),'E'),
 ('raw-energy-residual-failure',dict(numericalRequirementsFailed=True,adapterAccepted=True,hypothetical=True),'B')]:
    out=decide(e);assert out['proposedClass']==expected;tests.append(dict(name=name,evidence=e,result=out,expected=expected))
groups={}
for r in read(E/'chromium-replay.json')['matrix']:
    key=binding({k:r['input']['bits'][k] for k in ['M','V','U_kJ']});groups.setdefault(key,[]).append(dict(id=r['id'],request=r['request'],inventory=r['input']))
collisions=[dict(binding=k,rows=v) for k,v in groups.items() if len({r['request']['bits']['p'] for r in v})>1]
assert any(any(r['request']['values']['p']>3500000 for r in c['rows']) and any(r['request']['values']['p']<=3500000 for r in c['rows']) for c in collisions)
write('information-loss-collisions.json',dict(rows=collisions,conclusion='Identical M,V,U bits and guess=35 cannot encode distinct original requested PH support classes.'))
write('prototype-results.json',dict(rows=rows,hypotheticalPolicyTests=tests,counts=dict(Counter(r['proposal']['proposedClass'] for r in rows)),propertyStatesReturned=0,liveAdapterModified=False,warning='Proposals remain distinct from observed adapter behavior. No hypothetical capability is available in the live interface. No A plant-exit case is observed.'))
print('offline classification counts',dict(Counter(r['proposal']['proposedClass'] for r in rows)),'; six hypothetical policy tests; zero property states returned')
