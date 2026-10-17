"""Strict physical refusal of invalid raw DP diagnostics; never a Q tolerance."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';read=lambda p:json.loads(p.read_text());rows=[]
native=read(E/'shared-native-audit.json')['rows'];historical=read(X/'browser_eos_b5a/evidence/shared-density.json')['rows']
for engine in ['chromium','webkit']:
 blocks=read(E/f'shared-{engine}.json')['result']['rows'];lookup={(r['id'],r['fullVLE']):r for r in blocks}
 for block in blocks:
  for r in block['results']:
   if 'state' not in r['reused']:continue
   s=r['reused']['state']['values']
   if s['phase']!=6 or 0<=s['Q']<=1:continue
   assert r['mode']=='DP' and r['id'].endswith(('-hf','-hg'))
   other=lookup[('gateA' if block['id']=='rebuiltB4C' else 'rebuiltB4C',block['fullVLE'])]
   same=next(q for q in other['results'] if q['id']==r['id'] and q['mode']=='DP' and q['inputBits']==r['inputBits'])
   assert same['reused']['state']==r['reused']['state']
   n=next(q for q in native if q['label']==('candidate' if block['id']=='gateA' else 'control') and q['fullVLE']==block['fullVLE'] and q['id']==r['id'] and q['mode']=='DP')
   old=next(q for q in historical if q['fullVLE']==block['fullVLE'] and q['mode']=='DP' and q['inputBits']==r['inputBits'])['result']['A1']['state']['values']
   if block['fullVLE']:assert n['reused']['state']['values']['Q']==old['Q']==s['Q']
   rows.append(dict(engine=engine,artifact=block['id'],fullVLE=block['fullVLE'],id=r['id'],mode='DP',input=r['input'],inputBits=r['inputBits'],rawReturn=r['reused']['state'],nativeRaw=n['reused']['state'],preservedNativeRaw=old,physicalQualityAdmissible=False,scientificAcceptance='REFUSED — invalid physical quality',controlCandidateExact=True,DPInterfaceQualified=False,scope='Unchanged supplemental DP endpoint diagnostic, not a repaired DU state or an accepted A2/model state'))
assert len(rows)==44
unique={(r['id'],r['fullVLE'],tuple(r['inputBits'])) for r in rows};assert len(unique)==11
assert read(E/'seven-science-audit.json')['passed'] and read(E/'ledger-science-audit.json')['passed'] and read(E/'inherited-focused-audit.json')['passOriginalFocusedRequirements']
out=dict(physicalAcceptanceOfInvalidQuality=False,strictPhysicalRefusals=rows,uniqueDPPathInputs=len(unique),rawComparisons=len(rows),DPPhysicalQualification='FAIL / NOT QUALIFIED',focusedGateAQualificationUnaffected=True,scopeRationale='The original shared-density matrices were diagnostic comparisons, not a global DP physical qualification. All invalid raw DP outputs remain physical failures, unchanged by Gate A; no originally qualified DU/B1/B4A/B4B/B4C state regresses. No raw-return count is promoted to success, no quality clamp or tolerance is applied, and no model consumes these DP diagnostics.')
p=E/'quality-disposition.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Strictly refused 44 raw DP quality diagnostics / 11 path-input identities; no DP physical qualification')
