# B7 isolated generated artifacts

`control/` is exact reconstructed B4C. `candidate/` is B4C plus the preserved
three-file Gate A patch. `control-diagnostic/` and `candidate-diagnostic/` contain
the separately identified logging-only builds, with exact source differences in
`../evidence/diagnostic-*.patch` and parity checks in `gate1-audit.json`.

The authoritative JS/WASM identities are
`../evidence/artifacts-with-diagnostics.json`. Native matched controls are verified
historical B5A archives, identified in `native-artifact-identities.json`, not new
native build outputs. Historical vendor directories remain protected.

CoolProp and inherited dependency/runtime notices accompany these artifacts in
`CoolProp-LICENSE.txt` and `notices/`. No production selection or license/data
change occurs.
