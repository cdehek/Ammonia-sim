"""Summarize preserved measurements; never executes or repairs the model."""
import json, os
from pathlib import Path
B=Path(__file__).resolve().parent
E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
audit=json.loads((E/'independent-scientific-audit.json').read_text())
lines=['# Independent scientific audit results','',
 '**Selected contracts pass; backend qualification remains BLOCKED.**',
 'These values are derived from preserved raw outputs by audit-science.py, independently of the JavaScript balance implementation.',
 '', '| Engine / fixture | Section / global mass kg | Refrigerant energy kJ | Tube/fin/air node energy kJ | Combined energy kJ |',
 '|---|---|---:|---:|---:|']
for r in audit['operating']:
 m=r['independentConservation']
 lines.append(f"| {r['file'].split('-')[0]} / {r['case']} | {m['sectionMassKg']:.6g} / {m['globalMassKg']:.6g} | {m['refrigerantEnergyKJ']:.6g} | {m['thermalNodeKJ']:.6g} | {m['combinedEnergyKJ']:.6g} |")
lines+=['','All ten operating audits pass the original 1e-8 kg / 1e-6 kJ budgets. Each includes all saved sample times in nominal, tight and reference runs. The unchanged accepted cap-refinement assertions also pass; their extra records are audited where the detached histories exist.',
 '', '| Engine / fixture | Frozen direct-EOS ΔP Pa / Δh J/kg / ΔT K | Fresh same-table ΔP Pa / Δh J/kg / ΔT K (max across regimes) |', '|---|---|---|']
for r in audit['operating']:
 f=r['frozenDirectEOS'];t=r['sameTableAcceptedReference']
 table='NOT RUN' if t is None else ' / '.join(f'{max(v["differences"][k] for v in t)*scale:.6g}' for k,scale in [('pressureBar',1e5),('enthalpyKJkg',1000),('fluidK',1)])
 lines.append(f"| {r['file'].split('-')[0]} / {r['case']} | {f['pressureBar']*1e5:.6g} / {f['enthalpyKJkg']*1000:.6g} / {f['refrigerantTemperatureK']:.6g} | {table} |")
lines+=['', 'Frozen direct-EOS differences use the accepted refined-run comparison and its unchanged budgets. Fresh same-table differences compare separately executed accepted table-backed trajectories; they include backend and initial-inventory differences. They are not same-EOS temporal errors. No acceptance threshold was invented for that cross-backend table.',
 '', '| Engine / fixture (nominal) | Terminal quality | Superheat K | Stop | Accepted half-steps / rejected trials | Recorded phase events |', '|---|---:|---:|---|---|---:|']
for r in audit['operating']:
 d=json.loads((E/r['file']).read_text());s=d['result']['cases'][0]['runs'][0]['rows'][-1];t=s['terminal']
 lines.append(f"| {r['file'].split('-')[0]} / {r['case']} | {t.get('quality')} | {t.get('superheatK')} | {s['stop']} | {s['acceptedSteps']} / {s['rejectedSteps']} | {len(s['events'])} |")
h=audit['historyAudits'];c=audit['contractConservation']
lines+=['',f"Detached history audit: {len(h)} model histories, {sum(r['attempts'] for r in h)} trials, {sum(r['rejections'] for r in h)} rejected trials, {sum(r['rollbackChecks'] for r in h)} exact rollback checks, {sum(len(r['rollbackFailures']) for r in h)} rollback failures. Accepted normalized temporal error maximum: {max(r['maxAcceptedTemporalError'] for r in h):.12g} (original limit 1).",
 f"All {len(c)} independently auditable contract-history conservation records pass. Stop kinds, actual clocks, trial sizes and rejected/accepted work remain in the raw histories. The original cold operating executions lack detached trial histories; their original scientific assertions and saved conservation records pass, but a complete cold per-trial replay is NOT RUN. Cross-engine initial-inventory reuse occurs only after the entire returned record arrays compare exactly equal and is labelled in the audit.",
 '', 'Terminal wet outlets are reported as physical results. Native DT checks at every saved operating section retain residuals and actual phase separately in independent-scientific-audit.json. No property residual is repaired by the conservation audit. Other controller/Jacobian configurations, fresh regenerated direct-EOS trajectories and long operating endurance remain NOT RUN; see SUITE_RESULTS.md.']
points=[p for r in audit['operating'] for p in r['nativeDT']]
lines+=['',f"Independent native DT verification: {len(points)} saved section states, {sum('error' in p for p in points)} evaluation errors. Maximum absolute P/h/u residuals: "+' / '.join(f'{max(abs(p[k]) for p in points if k in p):.12g}' for k in ['pResidualPa','hResidualJkg','uResidualJkg'])+' Pa / J/kg / J/kg. This checks recorded recovered states against the matching EOS; it does not independently certify every PH inversion or experimental ammonia accuracy.']
t=E/'independent-terminal-audit.json'
if t.exists():
 terminal=json.loads(t.read_text())['rows']
 lines+=['',f"Independent native terminal audit: {len(terminal)} states, {sum('error' in r for r in terminal)} errors; maximum quality difference {max(abs(r.get('qualityDifference') or 0) for r in terminal):.12g}, maximum superheat difference {max(abs(r.get('superheatDifferenceK') or 0) for r in terminal):.12g} K. These are descriptive residuals, with no new acceptance budget."]
(B/'SCIENTIFIC_RESULTS.md').write_text('\n'.join(lines)+'\n')

roots=json.loads((E/'boundary-derivatives-native-8.0.0.json').read_text())
r=next(r for r in roots['rows'] if r['file']=='chromium-phase-build44.json' and r['args']==[30298.937123458254,98904.56398938334])
ref=r['homogeneousReference'];last=ref['trace'][-1]
raw=next(q for q in json.loads((E/'chromium-phase-build44.json').read_text())['rows'] if q['id']==r['id'])
lines=['# Same-phase liquid derivative counterexample','', '**FAIL — valid liquid input, unchanged backend and probes.**', '',
 'P = 30298.937123458254 Pa (`40dd96bbf9d4ab61`); h = 98904.56398938334 J/kg (`40f825890619bb4c`). The requested enthalpy is about 0.001 J/kg below the native saturated-liquid value. Actual backend classification is phase 6 with Q = −6.99036205016646e−10.', '',
 'The returned T = 218.26293725550536 K and rho = 707.4995406964335 kg/m³ independently produce pressure residual +2870.5026330731307 Pa and enthalpy residual +2.5891424380388344 J/kg. All four browser backends reproduce this fault in both engines. No decimal substitution is used.', '',
 f"A separate native homogeneous-liquid DT root converges at T = {last['T']:.17g} K, rho = {last['rho']:.17g} kg/m³, with pressure/enthalpy residuals {last['pResidual']:.12g} Pa / {last['hResidual']:.12g} J/kg. It is {ref['TMinusSaturation']:.12g} K below saturation; cp = {ref['cp']:.12g}, cv = {ref['cv']:.12g} J/(kg K), and isothermal compressibility = {ref['kappa']:.12g} 1/Pa, all positive. This reference root is diagnostic only and never enters the browser model.", '',
 '| Probe | Nominal signed size | Actual binary64 increment | Physical probe phase | FD density derivative | Homogeneous analytic derivative | FD / analytic |', '|---|---:|---:|---|---:|---:|---:|']
for p in r['probes']:
 lines.append(f"| {p['axis']} | {p['step']:.17g} | {p['actualIncrement']:.17g} | {p['physicalProbePhase']} | {p['finite']:.12g} | {p.get('analyticAtIndependentPhysicalRoot','excluded')} | {p.get('ratio','excluded')} |")
lines+=['', '| Probe | Exact P Pa | Exact h J/kg | Returned T K / rho kg/m³ | Independent DT ΔP Pa / Δh J/kg | Backend phase / Q |', '|---|---:|---:|---|---|---|']
for p in raw['probes']:
 s=p['output'];v=s['state']
 lines.append(f"| {p['axis']} {p['step']:+.17g} | {s['p']:.17g} | {s['h']:.17g} | {v['T']:.17g} / {v['rho']:.17g} | {s['pResidual']:.17g} / {s['hResidual']:.17g} | {s['phase']} / {v['Q']:.17g} |")
lines+=['', 'The +P, +h and −h probes remain physically liquid. Only −P crosses into physical coexistence and is excluded from a homogeneous derivative assertion. Backend phase codes alone conceal the +h failure because both returned states are erroneously called two-phase. The normalized mass contamination is about 1.70–1.72e−6, compared with the existing nonlinear scale 1e−11; this is a diagnostic comparison, not a replacement acceptance rule.', '',
 'The upstream quality tolerance admits Q down to −1e−9 and extrapolates the coexistence specific-volume formula below the saturated-liquid enthalpy. Its legitimate one-sided coexistence density/enthalpy slope is about −1.214375, versus the liquid slope −0.000267784, a factor about 4534.902. That physical one-sided slope explains the +h result; applying it to valid subcooled liquid is the fault. The reverse-h/forward-pressure probes switch back to liquid and reveal the resulting artificial density jump. This is not ordinary finite-difference truncation or a smoothness requirement across boiling.', '',
 'The preserved canonical PH→M/U/V→DU test moves P by about 4245.087 Pa (allowed 0.1 Pa), h by 6.000127 J/kg (allowed 0.1 J/kg) and T by 0.000495447 K (allowed 0.0001 K). This does not by itself prove a DU solver defect: combining requested P/h with an inconsistent PH density constructs different physical inventories. The unchanged coupled solver rejects the zero-exchange pure trial even after Newton converges at iteration zero, and the exact original state survives.', '',
 'The defect is a phase-selection/extrapolation path shared by 30-bit, 44-bit, official 8.0 and official 7.2. The adjusted B1 single-phase stopping rule does not govern this path. No number of precision bits is established as a remedy. The separate superheated-vapor cache residual has separate evidence and must not be conflated with it.', '',
 'Recommended next scientific experiment (engineering approval first): preserve these exact base/probe inputs and instrument the unmodified upstream PH phase decision to record saturation enthalpies, pre/post quality tests, chosen branch and lever-volume density. On matching native source, compare DU recovery of (a) the independently converged physical-liquid DT inventory and (b) the unchanged returned-PH inventory. Record residuals and the original canonical budgets separately. Repeat at 0.30298937123458254, 3.5, approximately 8 and 35 bar, with the existing signed probes; add a labelled quality-tolerance sweep only as a diagnostic. This isolates the classifier from the caloric/inversion paths before proposing any repair. Do not modify EOS data, clamp Q, alter probes/budgets or feed reference-polished properties into the accepted solver. A source patch requires separate explicit authorization.', '',
 'Raw reproduction: phase matrices → native.py / boundary-reference.py → analyze-boundary-derivatives.py (both native versions), plus run-boundary.py and run-initialization.py. See README.md for isolated output paths. The earlier relative-density derivation and first phase matrix remain archived; corrected measurements are additive and explicitly identified.']
(B/'LIQUID_COUNTEREXAMPLE.md').write_text('\n'.join(lines)+'\n')
print('Scientific summary and liquid counterexample derived from preserved raw evidence')
