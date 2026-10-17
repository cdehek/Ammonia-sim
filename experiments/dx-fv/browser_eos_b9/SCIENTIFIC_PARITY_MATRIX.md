# Scientific parity matrix

Within each actual browser, main and worker use the same fourteen-file accepted package, fixtures, numerical settings, duration requests and reporting cadence. Full scientific values use binary64 bit tags. No per-section failure is averaged away.

| Engine | Fixture | Checkpoints | Final accepted half-steps | Rejections | PH / SAT / MUV calls | Result |
|---|---|---:|---:|---:|---|---|
| chromium | cold | 0/.0001/.0005/.001 s | 16 | 1 | 8476 / 9261 / 445 | exact state/record/attempt parity |
| chromium | warm | 0/.0001/.0005/.001 s | 34 | 3 | 22072 / 23752 / 940 | exact state/record/attempt parity |
| webkit | cold | 0/.0001/.0005/.001 s | 16 | 1 | 8476 / 9261 / 445 | exact state/record/attempt parity |
| webkit | warm | 0/.0001/.0005/.001 s | 34 | 3 | 22072 / 23752 / 940 | exact state/record/attempt parity |

`parity-*-serialized.json.gz` contains all full state/record/attempt comparisons,
not just hashes. `scientific-audit.json` supplies section/aggregate/node and
independent signed thermal budgets. `node-baseline.json` independently verifies
direct original CommonJS versus the literal package. Timed runs check every
record/state against `frozen-browser-scientific-hashes.json` before completion.

| Scientific quantity | Same-engine result |
|---|---|
| Each section M/U/V, pressure guess | exact bits; volumes retained |
| Each recovered p/T/h/rho/u/phase/quality/wet/superheat | exact bits/values |
| Tube/fin/finite-air energies and temperatures | exact bits |
| Inlet/outlet signed fluxes; thermal links and refrigerant heat | exact bits |
| Section/total refrigerant and thermal ledgers | exact bits; original budgets pass |
| Newton iterations/residuals/FD/line-search; TR-BDF2 stages | complete observer attempts exact |
| Accepted steps, rejected counts, clocks and proposal history | exact values |
| Phase/boundary events, order/values, records and final state | exact values |
| Record after advance | exact original record; no state mutation |

Both short fixtures have EMPTY physical phase/boundary event lists. This proves
transport retains the observed ordering, not coverage of natural crossings,
scheduled 15/30-s events or every future physical event. Original event and
atomic commit code stays byte-identical. C1 tests independently retain accepted
event/clock history across refusals and test thermal outward-boundary proof.

Cross-engine values are not presumed bit-identical. The original accepted
coupled-browser limits are reapplied in `scientific-audit.json`. Maximum observed
cross-engine differences are pBar=7.83373366176e-11, hKJkg=7.63975549489e-10, fluidK=5.61925617149e-10, thermalK=1.13686837722e-13. All pass original limits. No full/long-duration A2 qualification follows.
