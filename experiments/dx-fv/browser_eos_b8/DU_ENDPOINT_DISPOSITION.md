# Four DU endpoints retained

All four remain scientifically **UNRESOLVED**. Exact original input and conserved-inventory bits, both native artifacts, both browser artifacts, default/full-VLE paths, fresh/reused results, mathematical diagnostics and reference limits are retained in [du-endpoints.json](evidence/du-endpoints.json). Inputs are decoded/checked from saved binary64 evidence, never rebuilt from rounded report decimals.

| Ledger | Density bits | Internal energy bits (J/kg) | Native / Chromium / desktop WebKit Gate A, actual full VLE |
|---|---|---|---|
| 148 | `403c0d271287772f` | `4136f0424572bf7f` | Strict QT exception; no returned state |
| 162 | `40804c41552836e8` | `4125463722133410` | Raw liquid, phase enum 0, homogeneous DU sentinel Q=10000; phase unqualified |
| 164 | `403c0d2712877730` | `4136f0424572bf7e` | Strict QT exception; no returned state |
| 165 | `403c0d271287772d` | `4136f0424572bf80` | Strict QT exception; no returned state |

The native candidate and two browsers reproduce the same sampled p/h/T results or refusal. B7 Chromium is 151.0.7922.34; desktop WPE WebKit is 26.5. The historical attempted Q values for 148/164/165 are **1.000000000000002 / 1.0000000000000018 / 1.0000000000000024**. These are diagnostics of failed updates, not returned vapor qualities. Their strict QT check refuses the state. Q=10000 at 162 is a homogeneous DU sentinel, not an accepted equilibrium mixture fraction.

## Interpretation retained without physical promotion

148 and 164 have high-precision same-EOS mathematical equilibrium roots infinitesimally inside the vapor endpoint: 1−Q approximately +1.29285e-16 and +4.22208e-16 for the exact external rho/u inputs. Homogeneous fallback would contradict these mathematical equilibrium diagnoses. They remain unqualified at the original independent phase-reference resolution.

165 has a mathematical stable homogeneous vapor-side root; the extended coexistence continuation has 1−Q approximately −1.60082e-16 and is inadmissible. Binary64 caloric equality dispatch still takes coexistence and fails QT. The mathematical sign does not establish a qualified recovered vapor state.

162 returns numerical liquid. Its traced internal-coordinate energy separation is approximately +2.33353e-9 J/kg, below the original **1e-8 J/kg** independent energy resolution. The separately labeled external rho/u separation is approximately +2.27699e-9 J/kg. Neither is a qualified original phase decision. Fresh homogeneous DT residual is 3.4924596548e-10 J/kg with zero volume residual and zero sampled getter/fresh-EOS p/h differences. Those consistency checks do not resolve physical phase.

Traced internal-coordinate u−usat separations are approximately −1.42178e-10 (148), −3.52750e-10 (164), +6.53502e-11 (165) J/kg. External rho/u reference separations differ because molar conversion and rounding are different coordinates; they are not silently interchanged. Full 65/90-digit references and independent reconstruction diagnostics are embedded in the evidence.

For the three refused cases, B5A Gate B's independently reconstructed invalid-Q coordinates have pressure residual about 1.51242e-7 Pa, chemical-potential residual 2.58440e-10 J/kg, specific-volume residuals about 4.48e-17 / 4.19e-17 / 5.08e-17 m³/kg, and energy residuals about 1.66e-9 / 1.71e-9 / 1.78e-9 J/kg. These are **separate reconstructed mathematical audits**, never getters from a failed update. A small residual does not make invalid quality physically acceptable. The binary64 feasibility prototype's seed-dependent invalid/wrong-branch solutions remain failures; B8 performs no new root search.

## Default versus actual full VLE and strict support

Default superancillary instances return raw numerical endpoint states for all four. Their candidate pressures in both browsers/native are respectively:

| Ledger | Default p (Pa) | Default Q / numerical phase | Full-VLE candidate p (Pa) |
|---|---:|---|---:|
| 148 | 3500000.0000000196 | 1 / enum 6 | no state |
| 162 | 3500000.0000000107 | 0 / enum 6 | 3500000.0000012456 |
| 164 | 3500000.000000024 | 1 / enum 6 | no state |
| 165 | 3500000.0000000107 | 0.9999999999999979 / enum 6 | no state |

Every returned coordinate here fails the unchanged strict bar-based adapter upper-pressure support guard. Default return is neither Gate B recovery nor an exact-inventory certificate. The proper C1 result is **B inverse-recovery-failure / solver** for full-VLE 148/164/165; **C boundary-unresolved / solver** for a raw return whose complete conversion fails support (including full-VLE 162 and all four default rows). A refusal does not establish physical trajectory exit. `replay-du-adapter.mjs` passes all 24 saved candidate outcomes through the unchanged C1 wrapper and actual table guard, verifying exactly those refusals. It injects saved observations, not new EOS work or a plant trajectory.

## Inventory and A2 relevance

Each original M/U/V bit pattern is preserved. `initialization-provenance.mjs` applies the unchanged accepted `inventory()` to each saved original PH density and **requested** p/h, recovering the original native M/U bits exactly at the accepted five-section V. This establishes the initialization construction used by the fixtures. It does not establish identical native/browser PH density bits or a complete B7-backed model.create at those exact native inventories.

The original operation order remains `rho=M/V`, `u=(U_kJ/M)*1000`. JSON additionally records exact rational M/V and 1000*U/M and their difference from rounded DU. The high-precision roots for external binary64 rho/u are not quietly converted into exact-rational M/U/V physical/support certificates.

Canonical recovery is mandatory in accepted A2 at startup, trial start, post-Newton stages, error-direction checks and recording. **The baseline implementation is table-backed.** The exact native full-VLE CoolProp failures are configuration-specific **P2**, with high confidence in saved outcome/configuration and explicitly unverified natural exact-input transient occurrence. They are not diagnostic-only P3 merely because a short trace misses them. They can stop a future full-VLE-backed evaporator initialization or a post-Newton stage if encountered; no demonstrated supported baseline path justifies P1 or P0. Signed Newton probes themselves use PH, so these DU refusals do not directly invalidate a PH Jacobian probe.

Retain all four obligations before broader full-VLE endpoint qualification. Do not clip Q, snap density, substitute u, force a preferred phase or loosen the independent reference requirement. No endpoint-repair milestone begins here.
