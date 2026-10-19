# Exact scientific parity

PASS against saved B10 same-browser references and original accepted controls. Every normal cold/warm session stays within 0/.0001/.0005/.001 simulated seconds. Cross-browser bit equality is not assumed.

| Browser | Fixture | Saved B10 state + record | Attempt hashes | Residuals | Accepted half-steps | Rejections |
|---|---|---|---|---:|---:|---:|
| chromium | cold | bit-exact at all four times | exact | 2914 | 16 | 1 |
| chromium | warm | bit-exact at all four times | exact | 7710 | 34 | 3 |
| webkit | cold | bit-exact at all four times | exact | 2914 | 16 | 1 |
| webkit | warm | bit-exact at all four times | exact | 7710 | 34 | 3 |

`production-projection-parity.json` also compares actual production panel final projections and all accepted history to saved B10, excluding only the fresh session UUID. `integration-{browser}.json.gz` retains complete exactly encoded accepted state/record at every checkpoint, original attempt hashes, source-to-render comparisons and saved-control identity. `review-{browser}.json.gz` retains full science/component hashes from the unchanged exhaustive harness, ten original and fourteen additional supported paired regressions and C1 refusal/rollback contracts. Original raw reference arrays remain protected in B9C/B9D; no rounded gauge is used as a reference.

Coverage: five refrigerant M/U/V inventories and pressure/enthalpy states, eleven tube/fin/air nodes and energies, original face/heat fluxes and ledgers, conservation budgets, 21 coordinates, signed finite differences, Newton/Jacobian/correction/line search, both TR-BDF2 stages, error/step proposals, accepted/rejected trials and exact physical/object rollback. Support limits, phase/refusal rules, PH/MUV recovery and exact B9C boundary PH reuse are unchanged.

Owned-table hardening passes in both browsers: 38,335 recursively frozen objects, unowned/injected/proxy/other-registry/null refusal, signed zero/exact key/nonfinite rules, failed-cache exclusion, two-slot clearing and independent new closures. These are trusted-registry mechanical eligibility checks, not hostile-code sandbox claims. No property substitution, EOS repair, optimizer, CoolProp backend or extended A2 campaign is introduced.
