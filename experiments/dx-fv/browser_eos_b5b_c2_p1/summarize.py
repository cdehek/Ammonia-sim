"""Build review matrix and exact same-EOS budget comparisons from saved proofs."""
import json,os,statistics
from fractions import Fraction as F
from pathlib import Path
import diagnostic as dg

B=Path(__file__).resolve().parent
E=Path(os.environ.get('P1_EVIDENCE',B/'evidence'))

def read(n):return json.loads((E/n).read_text())
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def midpoint(z):return (F(z['lower'])+F(z['upper']))/2
def fmt(z):return f'{float(midpoint(z)):+.12g}'
def diffbound(q,z):return max(abs(q-F(z['lower'])),abs(q-F(z['upper'])))

def main():
    rows=read('results.json')['rows']
    assert (E/'verification.json').exists()
    output=[]
    md=['# Phase certification matrix','',
        '**PARTIAL PHASE CERTIFICATION**. Exact rational outward endpoints are in',
        '`evidence/results.json` and `phase-matrix.json`; decimal table values are',
        'displays. No row has complete physical-branch certification. Conditional',
        'means the explicitly unproved convex-envelope/topology dependency in',
        '`BRANCH_AND_TOPOLOGY.md`. No row is original scientific or browser qualification.','',
        'The seven historical refusals remain refused; the two inward hazards retain',
        'their historical returns. Rounded DU remains two inside/five outside;',
        'exact M/U/V remains one inside/six outside. These are different targets.','',
        '| Exact-inventory case | Homogeneous p−3,500,000 (Pa) | Validated density side | Validated mixture continuation | Complete diagnostic outcome |',
        '|---|---:|---|---|---|']
    for r in rows:
        z=r['validated'][-1]['result']
        m=z['mixture']
        b=r['case']['inputBits']
        d,u=dg.target(b)
        h=z.get('homogeneous')
        p=fmt(h['pMinusLimitPa']) if h else 'not used'
        md.append(f"| {r['case']['key']} | {p} | {z.get('relativeSide','not used')} | {m['qualityStatus']} | {z['status']} |")
        output.append(dict(key=r['case']['key'],origin=r['case']['origin'],
            exactStoredInventoryIdentity={k:b[k] for k in ['M','U_kJ','V']},
            exactDensity=str(d),exactEnergyJkg=str(u),
            homogeneousRootExistenceUniquenessStatus='VALIDATED_LOCAL' if h else 'NOT_APPLICABLE_TO_SELECTED_MIXTURE_FORMULATION',
            homogeneousTemperature=h['temperature'] if h else None,
            homogeneousPressureEnclosure=h['pressurePa'] if h else None,
            saturationCoexistenceRootStatus=z['coexistenceRootStatus'],
            saturationAtEntireHomogeneousTemperature=z.get('saturation'),
            saturationEndpointEnclosures=z.get('saturation',{}).get('box'),
            relativeStableSideInequality=z.get('relativeSide'),
            inequalityMeaning='relative to validated locally stable coexistence endpoints; stable topology not proved',
            competingPhaseExclusionStatus=z['competingPhaseExclusion'],
            mixtureQuality=m['quality'],mixtureQualityAdmissibility=m['qualityStatus'],
            mathematicalPressureSupportClassification=z.get('mathematicalPressureSupport',z.get('mixturePressureSupport')),
            pressureClassificationScope='local enclosed mathematical root; stable equilibrium pressure conditional/unresolved',
            completePhysicalBranchCertification=False,diagnosticOutcome=z['status'],
            originalScientificQualificationStatus=r['originalScientificQualification'],
            browserPortability=r['browserPortability'],physicalTrajectoryExit='unproved',
            historicalOutcome=r['case'].get('historicalOutcome','separate diagnostic; never a simulator state')))
    md+=['','## Primary inventory identity and enclosures','',
         'For both primary rows: homogeneous existence and local uniqueness PASS;',
         'parameterized coexistence existence and local uniqueness PASS at every',
         'possible root T; endpoint stability PASS; competing-phase exclusion',
         'UNRESOLVED; complete physical branch FALSE; original scientific qualification',
         'UNRESOLVED; browser arithmetic portability NOT DEMONSTRATED.','']
    for key in ['webkit-ledger-69','webkit-ledger-76']:
        r=next(r for r in rows if r['case']['key']==key)
        z=r['validated'][-1]['result']
        b=r['case']['inputBits']
        md += [f'### {key}','',f"M `{b['M']}`, U_kJ `{b['U_kJ']}`, V `{b['V']}`.",'',
               '| Field | Validated enclosure (display) |','|---|---|',
               f"| Root T (K) | `{z['homogeneous']['temperature']['display']}` |",
               f"| Root p−max (Pa) | `{z['homogeneous']['pMinusLimitPa']['display']}` |",
               f"| rhoL (kg/m³), entire root T interval | `{z['saturation']['box'][0]['display']}` |",
               f"| rhoV (kg/m³), entire root T interval | `{z['saturation']['box'][1]['display']}` |",
               f"| d*−rhoL (kg/m³) | `{z['densityMinusLiquid']['display']}` |",
               f"| d*−rhoV (kg/m³) | `{z['densityMinusVapor']['display']}` |",
               f"| Algebraic continuation Q | `{z['mixture']['quality']['display']}` |",'']
    md += ['## Positive and negative controls','',
        'The separately generated liquid (335 K, about 34 bar), vapor (365 K, about',
        '34 bar), exterior liquid (335 K, about 36 bar), and interior mixture',
        '(344 K, Q about 0.5) have independently verified local mathematical roots,',
        'endpoint stability and the stated inequalities. Full stable-equilibrium',
        'qualification of these requested positive controls is **not established**:',
        'the same missing topology gate applies. They are never substituted for',
        'historical inventories. Construction operands and bits are in `inputs.json`.','',
        'The dome-interior homogeneous control has positive cv and dp/drho, but a',
        'validated same-U,V mixture has entropy greater by about 0.07058947 J/kg/K.',
        'That homogeneous root is rigorously excluded under additive bulk-phase',
        'thermodynamics; global optimality of the competitor remains unproved.','',
        'Negative controls retain Q<0 and Q>1 algebraic roots, an endpoint-sign',
        'overlapping validated box, a non-enclosing box, singular preconditioner,',
        'equal-density root, invalid/nonfinite coordinates, bad seed, insufficient',
        'parameter coverage and pressure-inside evidence without topology proof.',
        'See `evidence/verification.json`; none emits a physical-branch success.','',
        'Optional Gate B 148, 162 and 165 use C2’s saved exact M/U/V, separately from',
        'Gate B rounded-DU inputs. Ledger 164 is not expanded. Original endpoint',
        'independent-reference qualification remains unresolved.','']
    (B/'PHASE_CERTIFICATION_MATRIX.md').write_text('\n'.join(md))
    write('phase-matrix.json',dict(classification='PARTIAL PHASE CERTIFICATION',rows=output))
    c2={r['case']['key']:r for r in json.loads((dg.C2/'evidence/references.json').read_text())['rows']}
    budgets=[]
    for r in output:
        if not (r['key'].startswith('webkit') or r['key'].startswith('chromium')):continue
        raw=c2[r['key']]['case']['raw']['bits']
        d,u=F(r['exactDensity']),F(r['exactEnergyJkg'])
        p=r['homogeneousPressureEnclosure']
        h=dict(lower=str(u+F(p['lower'])/d),upper=str(u+F(p['upper'])/d))
        bounds=dict(pressurePa=diffbound(F(dg.decode(raw['p'])),p),
                    enthalpyJkg=diffbound(F(dg.decode(raw['h'])),h),
                    temperatureK=diffbound(F(dg.decode(raw['T'])),r['homogeneousTemperature']))
        assert bounds['pressurePa']<=F('.1') and bounds['enthalpyJkg']<=F('.1') and bounds['temperatureK']<=F('.0001')
        assert bounds['pressurePa']<10 and bounds['enthalpyJkg']<50 and bounds['temperatureK']<F('.01')
        budgets.append(dict(key=r['key'],absoluteErrorUpperRational={k:str(v) for k,v in bounds.items()},
                            display={k:float(v) for k,v in bounds.items()}))
    write('scientific-contract-audit.json',dict(
        canonicalLimits=dict(pressurePa='0.1 inclusive',enthalpyJkg='0.1 inclusive',temperatureK='1e-4 inclusive'),
        standaloneLimits=dict(pressurePa='10 strict',enthalpyJkg='50 strict',temperatureK='0.01 strict'),
        normalizedFluidResidualMax='1e-11',independentReferenceResolution=dict(pressurePa='1e-5',energyJkg='1e-8'),
        hardPressureMaximumPa=3500000,lowerPressurePa=30000,propertyTemperatureFloorK='195.495',
        newSameEOSHomogeneousComparisons=budgets,
        comparisonScope='historical raw getters vs rigorous exact-MUV LOCAL homogeneous root; physical branch/reference unresolved',
        acceptedTrajectoryTests='not rerun; all accepted and historical files byte-preserved',
        originalPhaseQualification='unresolved',fullBackendQualified=False,fullA2Qualified=False,
        originalConservationThermalSignedDerivativeNewtonTRBDF2DomainStopRollbackContracts='unchanged; preservation audit',
        manufacturedMeasurementAccuracy=False,modifiedScientificLimits=False))
    timings=read('performance.json')
    summary={str(p):dict(count=len(a),medianMs=statistics.median(a)*1000,minMs=min(a)*1000,maxMs=max(a)*1000)
             for p in [192,256] if (a:=[x['seconds'] for x in timings['validatedAttempts'] if x['precision']==p])}
    write('performance-summary.json',dict(byPrecision=summary,totalRunSeconds=timings['totalSeconds'],
          verificationSeconds=read('verification.json')['seconds'],scope=timings['scope']))
    print('matrix and scientific-contract audit written; 9 exact local pressure comparisons; no qualified property states')

if __name__=='__main__':main()
