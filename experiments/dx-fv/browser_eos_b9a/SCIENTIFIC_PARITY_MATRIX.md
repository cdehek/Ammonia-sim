# Scientific parity

PASS in actual Chromium and desktop WebKit. `scientific-audit.json` independently
compares B/C worker-owned evidence against untouched B9 main/worker controls.
Direct Node versus literal packaging also passes. No compact value reconstructs
scientific state.

| Engine | Fixture | A/B/C checkpoint clocks s | Final half-steps/rejections | Original PH/SAT/MUV counts |
|---|---|---|---|---|
| Chromium | cold | 0/.0001/.0005/.001 | 16/1 | 8476/9261/445 |
| Chromium | warm | 0/.0001/.0005/.001 | 34/3 | 22072/23752/940 |
| WebKit | cold | 0/.0001/.0005/.001 | 16/1 | 8476/9261/445 |
| WebKit | warm | 0/.0001/.0005/.001 | 34/3 | 22072/23752/940 |

Exact bits cover every original state field: all five M/U/V/pressure guesses,
recovered p/T/h/rho/u/phase/quality/wet, eleven thermal energies and temperatures,
all fluid/thermal fluxes and ledgers, counters, trial/FD/line-search histories,
settings, proposal/growth state, clock, schedule and event lists. Each compact
worker executes a separate unchanged B9 control and compares direct authoritative
state/record and original attempt arrays INSIDE its owning worker. C changes
retention only, with zero observer or physical-work count differences. Timed
runs additionally hash full state/record against B9's exact per-engine fixtures
inside the worker, outside service timing; every timed property-call vector
matches across A/B/C.

Original per-section and total mass <1e-8 kg, energy <1e-6 kJ, signed independent
thermal budgets, residual <=1e-11 and temporal acceptance <=1 pass at each point.
Original thermal closure 1e-12 K and all numerical settings are unchanged.
Cross-engine original limits pass separately in scientific-audit.json; engines
are not presumed bit-identical. Natural event lists are empty in these short
fixtures; scheduled long-time events and arbitrary phase crossings are not newly
qualified. Presentation mutation tests and detailed retrieval leave authoritative
state unchanged. Scientific-contract audit retains all inherited restrictions.

Use parityB/C-*-record-cadence.json.gz and baseline-*-export-fixed.json.gz.
Earlier compact parity receipts precede the extra original record-request cadence
and are superseded, not pooled. No sustained or complete A2 qualification.
