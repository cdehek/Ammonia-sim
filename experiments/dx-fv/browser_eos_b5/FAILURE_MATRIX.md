# Original B4C failure matrix

Derived from the preserved candidate C results. WebKit reproduces the same seven browser identities and bits. All decimals below are Python round-trip binary64 representations; exact bits and all inventories are in `evidence/original-failures.json` and `evidence/fixed-inventory.csv`. No row is a new or normalized inventory.

## Full-VLE native exceptions

| Fixed key | Original fixture ID | Exact h J/kg | Exact rho DU kg/m³ | Exact u DU J/kg | Traced final Q | Independent physical classification |
|---|---|---:|---:|---:|---:|---|
| native-ledger-146 | `approach-3500000.0-liquid-0.001` | 703826.5644298478 | 521.5319011003699 | 697115.5655578412 | -1.826556176446871e-12 | liquid |
| native-ledger-148 | `approach-3500000.0-vapor-0.0` | 1628069.3277690788 | 28.051377447197577 | 1503298.271282166 | 1.000000000000002 | endpoint-unresolved at original resolution |
| native-ledger-151 | `diagnostic-quality-band-3500000.0-hf--1.01e-09` | 703826.5644963626 | 521.5319010741065 | 697115.5656240181 | -1.7050594278322192e-12 | liquid |
| native-ledger-152 | `diagnostic-quality-band-3500000.0-hf--9.9e-10` | 703826.5645148475 | 521.5319010668067 | 697115.5656424091 | -1.6712644584214701e-12 | liquid |
| native-ledger-162 | `ULP-3500000.0-hf--1` | 703826.5654298477 | 521.531900705505 | 697115.5665527601 | -1.8873281520885622e-16 | endpoint-unresolved at original resolution |
| native-ledger-164 | `ULP-3500000.0-hg--1` | 1628069.3277690785 | 28.05137744719758 | 1503298.2712821658 | 1.0000000000000018 | endpoint-unresolved at original resolution |
| native-ledger-165 | `ULP-3500000.0-hg-1` | 1628069.327769079 | 28.05137744719757 | 1503298.2712821662 | 1.0000000000000024 | endpoint-unresolved at original resolution |

Every P input above is exactly 3,500,000 Pa, bits `414ab3f000000000`. All fail at the final QT_INPUTS quality range check; no raw DU state is returned. The C API exposes an error string; the research Python wrapper raises ValueError. The underlying pinned C++ type at that location is OutOfRangeError.

## Strict browser recovery rejections

| Chromium fixed key (WebKit key) | Original fixture ID | Exact h J/kg | Exact rho DU kg/m³ | Exact u DU J/kg | Raw ΔP Pa | Independent fixed-inventory ΔP Pa | Raw minus independent Pa |
|---|---|---:|---:|---:|---:|---:|---:|
| chromium-ledger-64 (webkit-ledger-64) | `approach-3500000.0-liquid-0.001` | 703826.5644298478 | 521.5319011003706 | 697115.5655578412 | 1.49011611938e-07 | -2.58101716514e-09 | 1.51592629104e-07 |
| chromium-ledger-65 (webkit-ledger-65) | `approach-3500000.0-liquid-0.01` | 703826.5554298478 | 521.5319046541697 | 697115.556603571 | 3.6833807826e-07 | 4.01190221955e-07 | -3.28521436947e-08 |
| chromium-ledger-67 (webkit-ledger-67) | `approach-3500000.0-vapor-0.001` | 1628069.3287690787 | 28.051377396718905 | 1503298.2720576394 | 2.79396772385e-09 | 7.02192693616e-09 | -4.22795921231e-09 |
| chromium-ledger-68 (webkit-ledger-68) | `approach-3500000.0-vapor-0.01` | 1628069.3377690788 | 28.051376942410506 | 1503298.2790368996 | 1.86264514923e-09 | 7.04166454343e-10 | 1.15847869489e-09 |
| chromium-ledger-70 (webkit-ledger-70) | `diagnostic-quality-band-3500000.0-hf--9.9e-10` | 703826.5645148475 | 521.5319010668079 | 697115.5656424091 | 7.65547156334e-07 | 7.72409866695e-07 | -6.86271036147e-09 |
| chromium-ledger-75 (webkit-ledger-75) | `diagnostic-quality-band-3500000.0-hg-9.9e-10` | 1628069.3286840792 | 28.051377401009518 | 1503298.2719917244 | 1.39698386192e-09 | -8.24286338428e-10 | 2.22127020035e-09 |
| chromium-ledger-79 (webkit-ledger-79) | `focused-3500000.0-stable-vapor` | 1638069.3277690788 | 27.554827993594685 | 1511049.8449832092 | 1.86264514923e-09 | 1.79967963169e-09 | 6.29655175452e-11 |

All seven raw recoveries satisfy the original canonical limits. The unmodified table PH guard passes. `adapter.mjs::sat` rejects `s.p/1e5 > 35`, with faultKind `domain`, before any SAT EOS call. Originating adapter PH calls pass. High-precision values diagnose the same mathematical EOS with exact binary64 coefficients; they are not experimental EOS accuracy claims.

## Bit-exact original PH and DU inputs

| Failure key | P bits | h bits | rho DU bits | u DU bits |
|---|---|---|---|---|
| native-full-VLE/approach-3500000.0-liquid-0.001 | 414ab3f000000000 | 41257aa520fcf2f2 | 40804c41555d365c | 412546372190cc20 |
| native-full-VLE/approach-3500000.0-vapor-0.0 | 414ab3f000000000 | 4138d7a553e8aca2 | 403c0d271287772f | 4136f0424572bf7f |
| native-full-VLE/diagnostic-quality-band-3500000.0-hf--1.01e-09 | 414ab3f000000000 | 41257aa52105aad0 | 40804c415559aff5 | 41254637219978a7 |
| native-full-VLE/diagnostic-quality-band-3500000.0-hf--9.9e-10 | 414ab3f000000000 | 41257aa521081710 | 40804c415558b523 | 41254637219be1c1 |
| native-full-VLE/ULP-3500000.0-hf--1 | 414ab3f000000000 | 41257aa521800560 | 40804c41552836e8 | 4125463722133410 |
| native-full-VLE/ULP-3500000.0-hg--1 | 414ab3f000000000 | 4138d7a553e8aca1 | 403c0d2712877730 | 4136f0424572bf7e |
| native-full-VLE/ULP-3500000.0-hg-1 | 414ab3f000000000 | 4138d7a553e8aca3 | 403c0d271287772d | 4136f0424572bf80 |
| chromium/approach-3500000.0-liquid-0.001 | 414ab3f000000000 | 41257aa520fcf2f2 | 40804c41555d3663 | 412546372190cc20 |
| chromium/approach-3500000.0-liquid-0.01 | 414ab3f000000000 | 41257aa51c614d0f | 40804c41573a31fe | 412546371cfb24ad |
| chromium/approach-3500000.0-vapor-0.001 | 414ab3f000000000 | 4138d7a5542a35d9 | 403c0d2711aea94c | 4136f04245a591c8 |
| chromium/approach-3500000.0-vapor-0.01 | 414ab3f000000000 | 4138d7a5567808cb | 403c0d270a0f6bee | 4136f042476ef656 |
| chromium/diagnostic-quality-band-3500000.0-hf--9.9e-10 | 414ab3f000000000 | 41257aa521081710 | 40804c415558b52e | 41254637219be1c1 |
| chromium/diagnostic-quality-band-3500000.0-hg-9.9e-10 | 414ab3f000000000 | 4138d7a55424a3cb | 403c0d2711c116e0 | 4136f04245a13fe9 |
| chromium/focused-3500000.0-stable-vapor | 414ab3f000000000 | 4138feb553e8aca2 | 403b8e09351764fc | 41370e89d850d1d1 |
| webkit/approach-3500000.0-liquid-0.001 | 414ab3f000000000 | 41257aa520fcf2f2 | 40804c41555d3663 | 412546372190cc20 |
| webkit/approach-3500000.0-liquid-0.01 | 414ab3f000000000 | 41257aa51c614d0f | 40804c41573a31fe | 412546371cfb24ad |
| webkit/approach-3500000.0-vapor-0.001 | 414ab3f000000000 | 4138d7a5542a35d9 | 403c0d2711aea94c | 4136f04245a591c8 |
| webkit/approach-3500000.0-vapor-0.01 | 414ab3f000000000 | 4138d7a5567808cb | 403c0d270a0f6bee | 4136f042476ef656 |
| webkit/diagnostic-quality-band-3500000.0-hf--9.9e-10 | 414ab3f000000000 | 41257aa521081710 | 40804c415558b52e | 41254637219be1c1 |
| webkit/diagnostic-quality-band-3500000.0-hg-9.9e-10 | 414ab3f000000000 | 4138d7a55424a3cb | 403c0d2711c116e0 | 4136f04245a13fe9 |
| webkit/focused-3500000.0-stable-vapor | 414ab3f000000000 | 4138feb553e8aca2 | 403b8e09351764fc | 41370e89d850d1d1 |
