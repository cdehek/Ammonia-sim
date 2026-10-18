# Why warm requires more work

The fixtures change thermodynamic inventory and hydraulic operating conditions,
as well as metal/air temperatures. Warm is not simply cold with hotter metal.

Cold begins at 3.5 bar, 500 kJ/kg: mixture quality .1397316, T≈267.811544 K,
rho≈19.84932 kg/m³, mass≈.01190959 kg per cell. Tube/fin start at 273.15 K,
air at 278.15 K. Warm begins at 3.65 bar, 1650 kJ/kg: superheated vapor,
T≈287.567822 K, rho≈2.7242515 kg/m³, mass≈.00163455 kg per cell. Tube/fin/air
start at 293.15 K. Fixed five-cell volumes and imposed inlet 4 bar/500 kJ/kg
and outlet 3.5 bar/1700 kJ/kg are unchanged. Original config and full initial
records/fluxes are retained in the baseline and census receipts.

Initial tube-to-refrigerant heat is similar: .640615 kW/cell cold versus
.669861 warm. Cold has nonzero air-to-metal links, warm initially has zero
temperature difference on those links. It is therefore unsupported to blame
warm's extra work on a greatly larger initial metal/refrigerant heat load.

Cold initial outlet flow is zero; warm initial outlet flow is .05216574 kg/s
with ≈86.0735 kW enthalpy transport. Warm's last-cell initial net mass rate is
−.05216574 kg/s and energy rate ≈−85.4036 kW. Its cell inventory is about 7.29×
smaller. These saved rates demonstrate a different rapid hydraulic startup.
They are context for the observed accuracy refinement, not an isolated causal
experiment changing one parameter.

The first .0001 s trial has normalized temporal error 1.11220 cold and 23.96491
warm. Cold rejects once, then accepts .00008 s (error .80937). Warm rejects
.0001, .00002948223 and .00001571608 s, then accepts .00001146767 s (error
.98036). All stages converge, all FD probes remain on branch and every line
search accepts immediately. The original failure-aware nonlinear ceiling stays
inactive: no natural Newton nonconvergence occurs.

| Work | Cold | Warm | Warm/cold |
|---|---|---|---|
| Attempts | 9 | 20 | 2.22 |
| Stages | 54 | 120 | 2.22 |
| Newton corrections | 130 | 345 | 2.65 |
| Residuals | 2914 | 7710 | 2.65 |
| Real PH | 8476 | 22072 | 2.60 |
| Branch interpolations | 119040 | 601320 | 5.05 |

There are 2.222× as many attempted stages, and corrections/stage increase from
2.4074 to 2.8750. Cold iteration distribution is 40 solves at 2, ten at 3,
four at 5. Warm: 41 at 2, 61 at 3, 13 at 4, three at 5, one at 6 and one at 7.
Thus work amplification reflects both more attempts and more iterations/stage.
It is not a line-search rejection storm, FD branch rejection or failed recovery.

Both requested and accepted horizon are .001 s. Divide totals by .001 for
work per requested or accepted second; neither represents sustained operation.
Residuals per stage are 53.963 / 64.250; per accepted half-step 182.125 / 226.765;
per Newton correction 22.415 / 22.348. Real PH per residual is 2.9087 / 2.8628,
so warm does not have more public PH calls per residual. Instead it has more
residuals AND more expensive branches: single-phase PH fraction rises from
35.11% to 64.49%, and total branch interpolation calls rise 5.05×. Warm canonical
density recovery also uses its original 32-iteration single-phase inversion.

Advance-only PH counts are 8,437 / 22,033 (public SAT 9,197 / 23,688; MVU
420 / 915). Initialization and extra snapshots are excluded from those counts.
For wall time per residual or PH, divide a matched run's advance sum by its
advance-only count, as a mixed workload normalization, not isolated function
latency. Full-workload PH/residual ratios above intentionally include the frozen
initialization and extra records, and are work-count ratios only. Timed PH wrappers and original Chromium stacks independently identify
the property engine as substantial. Node differs in warm numerical work and
must not be pooled with the browser denominator.

No condition-number estimate or isolated temporal-error-coordinate breakdown is
available. Conditioning, compiler choices and detailed error-term causation
remain uncertain. The supported explanation is accuracy-driven step refinement,
more Newton iterations and a more expensive single-phase table workload; the
initial hydraulic/inventory evidence explains why temperature alone is inadequate.
