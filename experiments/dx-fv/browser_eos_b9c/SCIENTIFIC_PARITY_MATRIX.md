# Exact scientific parity

| Engine | Fixture | Result | Residuals | Stages | Newton corrections | Accepted half-steps | Accuracy rejects |
|---|---|---|---|---|---|---|---|
| chromium | cold | EXACT | 2914 | 54.0 | 130 | 16 | 1 |
| chromium | warm | EXACT | 7710 | 120.0 | 345 | 34 | 3 |
| webkit | cold | EXACT | 2914 | 54.0 | 130 | 16 | 1 |
| webkit | warm | EXACT | 7710 | 120.0 | 345 | 34 | 3 |

PASS against both the isolated unchanged control and saved B9B SAME-engine
full scientific hashes at 0/.0001/.0005/.001 seconds. Requested advances remain
.0001/.0004/.0005 with original config/settings and initial, mandatory and extra
snapshot records. No easier performance fixture is substituted.

The full state/record/attempt encoding covers all authoritative M/U/V, guesses,
recovered p/h/T/rho/phase/quality/wet, thermal energies/temperatures, heat and flow
rates, mass/enthalpy fluxes, conservative residuals, ledgers, events/timestamps,
TR-BDF2 errors, acceptance/rejections, next proposals and final accepted states.
Every residual callback's complete return (including inventories/rates/quadrature)
and coordinates are SHA-256 encoded before optional detail reduction. Raw x and
residual arrays, full matrices/rhs/Newton delta, and full stage results remain.
Original observer events retain every signed FD, line search, iteration and
stage context. Independent hashes and raw component equality both pass.

All original converged residuals and section/aggregate conservation budgets pass.
auditRecord independently recomputes signed thermal ledgers. Canonical recovery
and thermal closure use the original unchanged comparisons and source budgets.
Every original internal adaptive attempt/error and endpoint proposal is exact;
unchanged Time.factor plus identical errors preserves the complete proposal
sequence. The preserved B9B same-browser adaptive-proposal-reconstruction.json
already checks these identical captured inputs and endpoints independently.

The frozen startup fixtures have no natural phase events; their empty event lists
are compared exactly. Boundary phase cases do not claim complete inventory phase
crossing or topology qualification.

No tiny numerical tolerance replaces bit equality. Cross-browser values are
not assumed bit-identical; each browser matches its own original baseline.
evidence/qualification.json includes exact hashes and conservation receipts.
