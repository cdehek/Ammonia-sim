"""Extract saved scientific observations only. No EOS calls. Timeout: 30s."""
import json,hashlib,struct,csv
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';used={}
def read(name):
 p=X/name;used[name]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
def write(n,d):(E/n).write_text(json.dumps(d,indent=2)+'\n')
def bits(v):return struct.pack('>d',v).hex()
def decode(v):return struct.unpack('>d',bytes.fromhex(v))[0]
q=read('browser_eos_b7/evidence/quality-disposition.json');rows=q['strictPhysicalRefusals'];assert len(rows)==44
history=read('browser_eos_b5a/evidence/shared-density.json')['rows'];native=read('browser_eos_b7/evidence/shared-native-audit.json')['rows']
shared={eng:read(f'browser_eos_b7/evidence/shared-{eng}.json')['result']['rows'] for eng in ['chromium','webkit']}
groups={}
for i,r in enumerate(rows):
 k=(r['fullVLE'],*r['inputBits']);groups.setdefault(k,[]).append((i,r))
assert len(groups)==11 and sum(k[0] for k in groups)==8
out=[]
for j,(key,observations) in enumerate(sorted(groups.items()),1):
 r=observations[0][1];assert len(observations)==4
 assert { (z['engine'],z['artifact']) for _,z in observations}=={(e,a) for e in shared for a in ['rebuiltB4C','gateA']}
 assert [bits(x) for x in r['input']]==r['inputBits']
 old=[(i,z) for i,z in enumerate(history) if z['mode']=='DP' and z['fullVLE']==r['fullVLE'] and z['inputBits']==r['inputBits']];assert len(old)==1
 for _,z in observations:
  v=z['rawReturn']['values'];assert v['phase']==6 and not 0<=v['Q']<=1 and not z['physicalQualityAdmissible'] and z['controlCandidateExact']
  block=next(b for b in shared[z['engine']] if b['id']==z['artifact'] and b['fullVLE']==z['fullVLE'])
  row=next(b for b in block['results'] if b['mode']=='DP' and b['inputBits']==z['inputBits'] and b['id']==z['id'])
  assert row['reused']['state']==row['fresh']['state']==z['rawReturn']
  n=next(b for b in native if b['label']==('candidate' if z['artifact']=='gateA' else 'control') and b['fullVLE']==z['fullVLE'] and b['mode']=='DP' and b['inputBits']==z['inputBits'] and b['id']==z['id'])
  assert n['reused']['state']==n['fresh']['state']==z['nativeRaw']
  nq=z['nativeRaw']['values']['Q']
  if r['fullVLE']:assert nq==v['Q']==z['preservedNativeRaw']['Q'] and not 0<=nq<=1
  else:assert nq in [0,1]
 out.append(dict(issueId=f'DP-{j:02}',fixtureId=r['id'],inputPair='DmassP_INPUTS',input=r['input'],inputBits=r['inputBits'],fullVLE=r['fullVLE'],classification='inherited-native-invalid-quality' if r['fullVLE'] else 'browser-endpoint-rounding-relative-to-native',historicalRowIndex=old[0][0],historicalRow=old[0][1],observationIndices=[i for i,_ in observations],observations=[z for _,z in observations],nativeReturned=True,browsersReturned=True,phaseEnum=6,phaseEnumMeaning='iphase_twophase numerical label; not independent phase certification',qualityAdmissible=False,independentPhysicalPhaseReference='NOT ESTABLISHED for exact DP input; same-EOS endpoint fixture provenance is not an independent phase certificate',acceptedPropertyEligible=False,adapterDPMethodImplemented=False,acceptedA2RequestsDP=False,currentReachability='No CoolProp DP edge in complete accepted dependency closure; bounded trace supports static exclusion',futureConsumerConsequence='A finite-only raw loader can expose this state. A future consumer must refuse invalid equilibrium quality; historical convert maps out-of-range Q to x=null and supplies no independent phase certificate. No current DP adapter edge exists.',scientificDisposition='REFUSED / DP NOT QUALIFIED',severity='P3',confidence='HIGH for current interface exclusion and invalid quality; no physical branch qualification'))
write('dp-observations-44.json',q)
write('dp-identities-11.json',dict(count=11,observations=44,fullVLE=8,default=3,rows=out))
fixed=read('browser_eos_b7/evidence/fixed-inputs.json');nf=read('browser_eos_b7/evidence/native-fresh-replay.json')['rows'];ledgers={e:read(f'browser_eos_b7/evidence/ledger-{e}.json')['result']['rows'] for e in shared}
repro=read('browser_eos_b5a_gate_b/evidence/four-case-reproduction-and-controls.json')['rows'];math=read('browser_eos_b5a_gate_b/evidence/mathematical-references.json')['rows'];supp=read('browser_eos_b5a_gate_b/evidence/supplement.json');activation={e:read(f'browser_eos_b7/evidence/activation-{e}.json') for e in shared}
du=[]
expected={148:['403c0d271287772f','4136f0424572bf7f'],162:['40804c41552836e8','4125463722133410'],164:['403c0d2712877730','4136f0424572bf7e'],165:['403c0d271287772d','4136f0424572bf80']}
for n,ib in expected.items():
 key=f'native-ledger-{n}';f=next(r for r in fixed if r['key']==key);v=f['input']['values'];b=f['input']['bits'];assert [b['rho'],b['u']]==ib
 assert bits(v['M']/v['V'])==ib[0] and bits((v['U_kJ']/v['M'])*1000)==ib[1]
 observations=[]
 for eng,blocks in [('native',nf),*ledgers.items()]:
  for block in blocks:
   label=block.get('label',block.get('id'));row=next(r for r in block['records'] if r['key']==key)
   assert row['input']['bits']==b and row['reused']==row['fresh'] if eng=='native' else row['input']['bits']==b and row['reused'].get('state',row['reused'].get('error'))==row['fresh'].get('state',row['fresh'].get('error'))
   state=row['reused'].get('state');values=state['values'] if state else None
   observations.append(dict(runtime=eng,artifact=label,fullVLE=block['fullVLE'],source=f'browser_eos_b7/evidence/{"native-fresh-replay" if eng=="native" else "ledger-"+eng}.json',reused=row['reused'],fresh=row['fresh'],returned=bool(state),strictPaSupport=bool(values and 30000<=values['p']<=3500000),strictBarSupport=bool(values and .3<=values['p']/1e5<=35),C1Classification='B inverse-recovery-failure / solver' if not state else 'C boundary-unresolved / solver (strict pressure guard fails)',physicalAccepted=False))
 candidate=[r for r in observations if r['artifact'] in ['candidate','gateA']];assert len(candidate)==6
 assert all(not r['strictBarSupport'] for r in candidate if r['returned'])
 original=next(r for r in repro if r['key']==key)
 mr=next(r for r in math if r['case']['key']==key)
 exactRho=Fraction(v['M'])/Fraction(v['V']);exactU=1000*Fraction(v['U_kJ'])/Fraction(v['M'])
 du.append(dict(issueId=f'DU-{n}',ledger=n,original=f,exactInventoryRationals=dict(rho=str(exactRho),uSI=str(exactU),rhoMinusRoundedDU=str(exactRho-Fraction(decode(ib[0]))),uMinusRoundedDU=str(exactU-Fraction(decode(ib[1]))),rationalMeaning='Exact stored binary64 M/U/V interpreted as rationals; no new root or support certificate computed'),observations=observations,originalReproduction=original,mathematicalReferences=mr,refusedReconstructionDiagnostics=next((r for r in supp['refusedMixtureIndependentEOS'] if r['key']==key),None),physicalQualification='UNRESOLVED under original 1e-8 J/kg independent phase resolution',baselineA2='Uses table engine; does not load B7 CoolProp',requiredOperation='Canonical stateMVU / DU recovery required by A2; full-VLE CoolProp branch is special experimental configuration',exactNaturalTrajectoryReachability='UNKNOWN / not demonstrated; saved inventory fixture is not a trajectory',severity='P2',confidence='HIGH for configuration and saved result; exact trajectory unverified'))
write('du-endpoints.json',dict(rows=du,browserVersions={e:activation[e]['browserVersion'] for e in activation},inputRule='Binary64 decoded/verified from saved bits, never reconstructed from report decimals'))
# Retain boundary attribution with all original exact identities, separate from DU ledger.
write('boundary-attribution.json',read('browser_eos_b7/evidence/support-attribution.json'))
a2audit=read('browser_eos_b7/evidence/a2-audit.json');assert a2audit['passed'] and a2audit['scenariosPerEngine']==10
write('c1-reused-a2-audit.json',a2audit)
for e in shared:
 d=read(f'browser_eos_b7/evidence/a2-{e}.json');assert d['result']['passed'];assert len(d['result']['a2'])==2
 for run in d['result']['a2']:
  assert run['result']['passed'] and len(run['result']['rows'])==5
  for r in run['result']['rows']:
   if r['scenario']=='real-browser-boundary' and r['persistent']:
    assert r['acceptedRollback'] and r['identityPreserved'] and r['floor']==1e-9 and len(r['attempts'])==20
    sizes=[z['trialSeconds'] for z in r['attempts']];assert sizes[-1]==1.9073486328125e-9 and all(b==a/2 for a,b in zip(sizes,sizes[1:]))
# Hash every original source read; includes full result provenance without copying large historical files.
write('source-evidence-sha256.json',used)
print('Retained four exact DU inventories, 44 DP observations / 11 identities, 8 full-VLE + 3 default; C1 subset rechecked')
