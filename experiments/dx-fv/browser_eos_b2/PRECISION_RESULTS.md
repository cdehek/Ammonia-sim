# Precision and phase-boundary results

Exact saved vapor: P=799999.9981754856Pa, h=1624022.744737779J/kg.
Independent residuals are evaluated at returned density/temperature, not input-echoing getters.

| Engine | Backend | T K | rho kg/m³ | DT pressure residual Pa | DT enthalpy residual J/kg | T−Tsat K |
|---|---|---:|---:|---:|---:|---:|
| chromium | build30 | 291.01436145355 | 6.2665509047477 | 1.16415321827e-10 | -0.00011946214363 | 0.00100001804913 |
| chromium | build44 | 291.01436145364 | 6.2665509047447 | 0 | -0.000119190430269 | 0.00100001813962 |
| chromium | official72 | 291.01436145363 | 6.2665509047451 | 0 | -0.000119222328067 | 0.00100001812899 |
| chromium | official8 | 291.01436145355 | 6.2665509047477 | 1.16415321827e-10 | -0.00011946214363 | 0.00100001804913 |
| webkit | build30 | 291.01436145355 | 6.2665509047477 | 1.16415321827e-10 | -0.00011946214363 | 0.00100001804913 |
| webkit | build44 | 291.01436145364 | 6.2665509047447 | 0 | -0.000119190430269 | 0.00100001813962 |
| webkit | official72 | 291.01436145363 | 6.2665509047451 | 0 | -0.000119222328067 | 0.00100001812899 |
| webkit | official8 | 291.01436145355 | 6.2665509047477 | 1.16415321827e-10 | -0.00011946214363 | 0.00100001804913 |

| Engine | Backend | Original saved liquid rho_P FD / analytic | Perturbed DT enthalpy residual J/kg |
|---|---|---:|---:|
| chromium | official8 | 20.1904555282 | -0.000474579064758 |
| chromium | build30 | 20.1904555282 | -0.000474579064758 |
| chromium | build44 | 0.999959589003 | -2.09547579288e-09 |
| webkit | official8 | 20.1904555282 | -0.000474579064758 |
| webkit | build30 | 20.1904555282 | -0.000474579064758 |
| webkit | build44 | 0.999959589003 | -2.09547579288e-09 |

| 44-bit physical region, Chromium (WebKit values identical) | Samples | Maximum DT pressure residual Pa | Maximum DT enthalpy residual J/kg |
|---|---:|---:|---:|
| homogeneous | 747 | 1.35815935209e-06 | 0.000119761098176 |
| physicalCoexistence | 410 | 9.75378497969e-08 | 4.65661287308e-10 |
| unphysicalCoexistenceQuality | 23 | 2870.50263307 | 2.58914243804 |

The corrected matrix includes homogeneous supercritical-gas derivatives. All physical outputs are bit-identical to the first B2 matrix; the earlier incomplete phase-code analysis remains under phase-v1.
The backend-homogeneous subset ratio range does not cover invalid Q-band states. Independent physical-branch roots reveal liquid ratios near−182709/+4535 and vapor ratio1.02523 while preserving all original probes; genuine physical crossings/endpoints are excluded.

At P=30298.937123458254Pa, h=hf−.001J/kg, independent DT pressure/h residuals reach2870.502633Pa/2.589142438J/kg and canonical recovery shifts pressure4245.087Pa. At3.5bar, the same liquid-side offset shifts canonical pressure about273.579Pa. Existing pressure compatibility is0.1Pa. The35bar offset recovers at35.00000088166694bar in matching native DU and the unchanged guard rejects it; this is not evidence of a genuine outward physical trajectory.

Read ENGINEERING_REPORT.md for source-path attribution and phase-aware interpretation. All source/raw-reference limits remain unchanged; no EOS repair or polished property is fed to the model.
