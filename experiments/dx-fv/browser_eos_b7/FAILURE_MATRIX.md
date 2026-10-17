# Original seven — exact inputs and independent disposition

**Three resolved liquid repairs; four endpoints remain unresolved.**

The original full-VLE control refuses all seven in native, Chromium and desktop WebKit. Candidate outcomes below are actual uninstrumented browser results; native A1 agrees. No failed update supplies a returned state. JSON and the original-bit columns are authoritative; displayed decimals are not replacement inputs.

| Ledger | Original rho kg/m³ | Original u J/kg | rho binary64 | u binary64 |
|---|---:|---:|---|---|
| 146 | 521.53190110036985 | 697115.56555784121 | `40804c41555d365c` | `412546372190cc20` |
| 148 | 28.051377447197577 | 1503298.271282166 | `403c0d271287772f` | `4136f0424572bf7f` |
| 151 | 521.53190107410649 | 697115.56562401808 | `40804c415559aff5` | `41254637219978a7` |
| 152 | 521.53190106680665 | 697115.56564240914 | `40804c415558b523` | `41254637219be1c1` |
| 162 | 521.531900705505 | 697115.56655276008 | `40804c41552836e8` | `4125463722133410` |
| 164 | 28.051377447197581 | 1503298.2712821658 | `403c0d2712877730` | `4136f0424572bf7e` |
| 165 | 28.05137744719757 | 1503298.2712821662 | `403c0d271287772d` | `4136f0424572bf80` |

| Ledger | Candidate pressure Pa | T K | h J/kg | Q / phase | Original scientific disposition |
|---|---:|---:|---:|---|---|
| 146 | 3499999.9999996712 | 345.56367341878774 | 703826.56442984706 | 10000 sentinel / liquid | resolved-stable-liquid |
| 148 | — | — | — | No state; strict QT refusal | unresolved historical QT refusal |
| 151 | 3499999.9999997276 | 345.56367343079808 | 703826.56449636177 | 10000 sentinel / liquid | resolved-stable-liquid |
| 152 | 3499999.9999993723 | 345.56367343413575 | 703826.56451484642 | 10000 sentinel / liquid | resolved-stable-liquid |
| 162 | 3500000.0000012456 | 345.563673599352 | 703826.56542985025 | 10000 sentinel / liquid | unresolved physical phase despite raw liquid return |
| 164 | — | — | — | No state; strict QT refusal | unresolved historical QT refusal |
| 165 | — | — | — | No state; strict QT refusal | unresolved historical QT refusal |

Q=10000 is the unchanged homogeneous DU sentinel. It is not an accepted physical mixture fraction. All scientifically accepted two-phase results require 0<=Q<=1. Supplemental invalid raw DP endpoint diagnostics are strictly refused in `evidence/quality-disposition.json` and are not part of this accepted set. Historical native A1 attempted Q values for 148/164/165 are 1.000000000000002 / 1.0000000000000018 / 1.0000000000000024; the B7 browser error confirms the strict validator refusal, not a newly measured returned Q. There is no returned quality after these errors.

## Three resolved liquids

| Ledger | Canonical Δp Pa | Canonical Δh J/kg | Canonical ΔT K | Fresh-EOS normalized energy residual | Native A1 Δp / Δh / ΔT |
|---|---:|---:|---:|---:|---|
| 146 | -3.28756868839e-07 | -6.98491930962e-10 | -3.41060513165e-13 | 1.30290660648e-16 | 0 / 0 / 0 observed |
| 151 | -2.72411853075e-07 | -8.14907252789e-10 | -2.27373675443e-13 | 6.51453303212e-16 | 0 / 0 / 0 observed |
| 152 | -6.27711415291e-07 | -1.04773789644e-09 | -2.84217094304e-13 | 1.30290660641e-16 | 0 / 0 / 0 observed |

Fresh/reused, Chromium/WebKit and normal/logging-on/logging-off states agree exactly in this sample. Cross-compiler acceptance still uses original tolerances. Both cached saturation coordinates equal the final evaluated coordinates and the caloric decision coordinates. Independent 65/90-digit saturation solves verify positive resolved caloric separation and cached energy error below 1e-8 J/kg. Maximum resolved-liquid final pressure/gibbs residuals are 1.3830140233e-7 Pa / 3.5587546035e-10 J/kg; maximum cached energy error is 1.2738973616e-9 J/kg. See `seven-science-audit.json` for all actual traces and independent roots.

## Four retained endpoint obligations

148: unresolved, historical invalid-Q refusal. 162: numerical liquid return, physical phase unresolved under the original reference resolution. 164: unresolved, historical invalid-Q refusal. 165: unresolved, historical invalid-Q refusal. The approximately 2.33e-9 J/kg separation at 162 is below the original 1e-8 J/kg resolution. Mathematical side information is retained separately from original scientific phase qualification.

No Q clipping, saturated-density substitution, forced vapor, alternate energy, relaxed solver limit or reference requirement is used. Default-path endpoint returns do not qualify the intended legacy Gate A path or resolve Gate B. The original seven 35-bar **browser adapter** refusals are a separate set, documented in `c1-*-explicit-bar.json` and `support-attribution.json`.
