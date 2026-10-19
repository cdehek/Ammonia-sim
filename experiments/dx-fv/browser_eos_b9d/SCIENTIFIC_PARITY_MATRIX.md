# Scientific parity

**PASS**, same-engine exact binary64 comparison. No tolerance replaces equality.

| Browser | Fixture | Full scientific result | Residual evaluations | Accepted half-steps | Rejected requests within adaptation |
|---|---|---|---|---|---|
| chromium | cold | EXACT / saved B9C match | 2914 | 16 | 1 |
| chromium | warm | EXACT / saved B9C match | 7710 | 34 | 3 |
| webkit | cold | EXACT / saved B9C match | 2914 | 16 | 1 |
| webkit | warm | EXACT / saved B9C match | 7710 | 34 | 3 |

Both browsers additionally pass ten original B9C and fourteen additional supported paired scenarios (24 per browser), 31 original PH support/phase cases, four refused updates and the original missing liquid-row statePT refusal. `review-*.json.gz` retains full states, records, attempts and component hashes. Cold/warm science hashes match the original saved B9C same-browser controls, which retain the earlier B9B/B9A chain. Every additional pair compares complete state/record/attempt encoding and full residual return, Jacobian/correction and converged-stage hashes.

Compared scientific content: section M/U/V and guesses; recovered p/T/h/rho/u, phase/quality/wet; six refrigerant faces; eleven thermal energies/temperatures; heat/enthalpy/mass rates; all residual inputs/outputs, signed FD, matrices and Newton decisions; TR-BDF2 stages; accepted/rejected histories and time errors; conservation ledgers; events, schedules, clocks, domain evidence and final accepted physical state. Original record audits independently recompute signed thermal closure and section/aggregate residuals. Fresh original creates reproduce independent initial state.

The shadow worker matches all four original control checkpoint hashes per fixture (0, .0001, .0005, .001 s) in each browser. `shadow-*.json.gz:science` records these hashes plus source projection audits and verification of all 81 current numerical/phase/wet display cells and historical rows. `shadow-tests.mjs::verify` explicitly maps each field to original record/cells before formatting. Detached mutation cannot change the worker. Raw source science remains available in the review receipts; no rounded display number is a comparison input.

Preserved budgets: canonical p≤0.1 Pa, h≤0.1 J/kg, T≤1e-4 K; normalized fluid mass/energy≤1e-11; standalone p<10 Pa, h<50 J/kg, T<.01 K; original independent reference resolution 1e-5 Pa / 1e-8 J/kg. Section/aggregate mass <1e-8 kg and energy <1e-6 kJ; original thermal nonlinear closure 1e-12 K. Original .3–35 bar absolute, subcool/superheat support, 200–400 K thermal domain, 21 coordinates, finite differences, Newton, TR-BDF2, adaptation and rollback remain unchanged. Complete standalone/reference campaigns are preserved by source/artifact identity, not newly rerun. No EOS repair, new acceptance, pressure epsilon, property substitution, added quality clipping or alternate step.
