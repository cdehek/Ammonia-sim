# Measured property-call reduction

| Engine | Fixture | Logical inlet | Logical outlet | Inlet misses | Outlet misses | Hits / PH saved | All real PH control | All real PH candidate | Non-stage PH each |
|---|---|---|---|---|---|---|---|---|---|
| chromium | cold | 2914 | 2914 | 54 | 54 | 5720 | 8476.0 | 2756.0 | 476 |
| chromium | warm | 7710 | 7710 | 120 | 120 | 15180 | 22072.0 | 6892.0 | 973 |
| webkit | cold | 2914 | 2914 | 54 | 54 | 5720 | 8476.0 | 2756.0 | 476 |
| webkit | warm | 7710 | 7710 | 120 | 120 | 15180 | 22072.0 | 6892.0 | 973 |

Logical requests remain one inlet and outlet per residual. In the fixed fixtures
each stage retains one successful call of each boundary. Savings include solved
stages in accuracy-rejected trials, whose slots are discarded before retry.
No reduction in residual work is counted as savings.

evidence/qualification.json records public SAT, nested lexical SAT, independent
canonical recoveries, section-cache requests/hits/misses, non-stage boundary
requests, outside-stage PH and thrown operations separately. The primary raw
original/candidate ledgers are evidence/parity-{chromium,webkit}.json.gz under
runs[].evidence.properties and .boundaries. All numeric fields are tagged binary64.
The property list is an actual public engine-call ledger; boundaries lists all
logical requests with realPH=0/1. Section hits are counted separately.

The analyzer checks every logical boundary p/h/result exactly, identifies each
stage's retained value, proves every omitted call equal to it, and removes ONLY
that request's original successful engine.ph followed by public engine.sat.
The remaining sequence must equal the complete candidate sequence, including
inputs, outputs, throws, stage/role/request identities and order. Nested lexical
saturation calls disappear as a consequence of the omitted genuine engine.ph,
not as a second optimization. Raw lexical counts corroborate this attribution.

Trial direction/initial rates, coordinates, recovery, domain proof, create/update
validation, event checks, records and outlet diagnostics remain genuine calls.
The full fixtures retain 476 cold / 973 warm outside-stage PH calls each.
Original thrown property operations are zero in the fixed fixtures. Refusal
regressions retain their original errors and are reported separately.
