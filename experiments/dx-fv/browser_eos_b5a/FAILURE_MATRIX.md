# Original seven DU failures — preserved before/after identities

All seven originally raised underlying C++ `OutOfRangeError` at the unchanged
`HelmholtzEOSMixtureBackend.cpp:1547` QT range check. The C API reports
`Error: Input vapor quality [Q] must be between 0 and 1`; the research wrapper
raises `ValueError`. No DU state exists after these failed updates. Original
Q, T, residuals, iteration stops, saturation thresholds and independent roots
are in `evidence/original-reproduction.json`, not discarded after repair.

| Fixed key | Original fixture | Requested rho kg/m³ | Requested u J/kg | rho / u binary64 bits | A1 disposition |
|---|---|---:|---:|---|---|
| native-ledger-146 | `approach-3500000.0-liquid-0.001` | 521.5319011003699 | 697115.5655578412 | `40804c41555d365c` / `412546372190cc20` | liquid, Q=10000 sentinel |
| native-ledger-148 | `approach-3500000.0-vapor-0.0` | 28.051377447197577 | 1503298.271282166 | `403c0d271287772f` / `4136f0424572bf7f` | QT refusal; unresolved |
| native-ledger-151 | `diagnostic-quality-band-3500000.0-hf--1.01e-09` | 521.5319010741065 | 697115.5656240181 | `40804c415559aff5` / `41254637219978a7` | liquid, Q=10000 sentinel |
| native-ledger-152 | `diagnostic-quality-band-3500000.0-hf--9.9e-10` | 521.5319010668067 | 697115.5656424091 | `40804c415558b523` / `41254637219be1c1` | liquid, Q=10000 sentinel |
| native-ledger-162 | `ULP-3500000.0-hf--1` | 521.531900705505 | 697115.5665527601 | `40804c41552836e8` / `4125463722133410` | raw liquid; unresolved |
| native-ledger-164 | `ULP-3500000.0-hg--1` | 28.05137744719758 | 1503298.2712821658 | `403c0d2712877730` / `4136f0424572bf7e` | QT refusal; unresolved |
| native-ledger-165 | `ULP-3500000.0-hg-1` | 28.05137744719757 | 1503298.2712821662 | `403c0d271287772d` / `4136f0424572bf80` | QT refusal; unresolved |

Only rows 146, 151 and 152 are independently resolved physical successes.
Row 162 passes raw numerical checks but remains endpoint-unresolved under the
original reference resolution. Rows 148, 164 and 165 retain the exact original
quality-range exception. Their Q remains respectively 1.000000000000002,
1.0000000000000018 and 1.0000000000000024. No clamp is applied.

`gate-A-audit.json` gives each A1 final cached coordinate, both densities,
pressure/chemical-potential residuals, caloric comparison, current output/error,
reference difference and all trace events. `gate-B-characterization.json`
retains every unresolved identity and mathematical reference. `control-comparison.json`
and `A1-comparison.json` include every historical row and all 73 unique pairs
on both paths. `additional-inventories.json` retains all 21 separate saved B5
reference inventories, including the three remaining A1 full-VLE failures.

The seven original browser rejections per engine remain in
`original-failures.json` and the unchanged B5 FAILURE_MATRIX.md, with their
below/above-35-bar mathematical diagnoses. They are separate from this matrix.
No A1 browser candidate was qualified or strict support guard bypassed.
