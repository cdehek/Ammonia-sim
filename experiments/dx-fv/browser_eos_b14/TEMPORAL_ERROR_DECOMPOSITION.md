# Temporal-error decomposition

Observed: every reconstructed original aggregate equals its captured binary64 value exactly. The coupled nonlinear vector has 21 entries (P/H alternating for five sections, ten tube/fin increments and one finite-air increment); the temporal estimator tests **31** scalars. Inventing a 21-vector RMS would give a different acceptance rule.

For each section and each q ∈ M,U,P,H:

`term = abs(fine.q - coarse.q) / 3 / (absolute_q + rtol * max(abs(initial.q), abs(fine.q)))`.

For each thermal node:

`term = abs(Efine - Ecoarse) / 3 / capacity / (temperatureAbsoluteK + rtol * temperatureScaleK)`.

The final error is the maximum of all 31 terms. Operations retain original division order; there is no sum, RMS or norm weighting. `coarse` is the full TR-BDF2 trial, `fine` the endpoint of the second half trial; the first half endpoint supplies its initial inventory. The fine half pieces are committed without extrapolation. Initial P/H are recovered through the unchanged coordinate expression, not substituted from a rounded record.

Original settings include rtol 1e-6, M absolute 1e-11 kg, U absolute 1e-8 kJ, P absolute 1e-6 bar, h absolute 1e-4 kJ/kg, temperature absolute 1e-4 K plus 1e-6×50 K = 0.00015 K. The thermal Newton residual's separate 1e-12 K budget is unchanged and must not be confused with this temporal budget.

`temporal-cold.json` and `temporal-warm.json` retain all 31 initial/coarse/fine/difference/scale/normalized terms per attempt, phase arrays, original error, reason, original next proposal and captured accepted controller decision. The raw observed receipts additionally retain complete coarse/fine stage result objects. `controller-*.json` proves every rejected proposal matches the next actual trial bit exactly. Accepted controller proposals and installed nextStep are copied after the original decision; no hook modifies them.

## Observed contributors

Cold startup: section 0 U leads (initial rejected error 1.1122008032464925, M0 1.0739736506845754); all 17 cold trials are led by U0. Warm startup: section 4 U leads all 20 startup trials; initial rejected error 23.96490890435499, followed by P4 22.472884120582982 and M4 21.973118158527274. Subsequent startup rejections are 4.054196684874863 and 1.5807514032212349. These occur at t=0 while all warm sections are vapor; they cannot be attributed to the later phase crossing.

Near 0.005 s, U0 and U1 dominate, with strong M/P contributions. All five late rejections:

| Start s | Trial s | Error max | Leading term | Next trial s |
|---|---|---|---|---|
| 0 | 0.0001 | 23.9649 | internalEnergyKJ-4 | 2.94822e-05 |
| 0 | 2.94822e-05 | 4.0542 | internalEnergyKJ-4 | 1.57161e-05 |
| 0 | 1.57161e-05 | 1.58075 | internalEnergyKJ-4 | 1.14677e-05 |
| 0.005 | 0.00128453 | 34.2474 | internalEnergyKJ-1 | 0.000336217 |
| 0.00533622 | 0.000672433 | 54.4708 | internalEnergyKJ-0 | 0.000150781 |
| 0.00533622 | 0.000150781 | 3.81319 | internalEnergyKJ-1 | 8.20357e-05 |
| 0.00533622 | 8.20357e-05 | 3.5241 | internalEnergyKJ-0 | 4.58218e-05 |
| 0.00538204 | 3.93276e-05 | 1.37651 | internalEnergyKJ-1 | 3.00508e-05 |

The table also retains the three startup rejections for context. For the largest late error, U0 coarse/fine differ by −0.00041909988638533235 kJ with scale 2.5646744403986444e-6 kJ; division by 3 gives error 54.47083650380577. For the first late rejection U1 difference is +0.00024865981961719186 kJ against scale 2.4202304467561004e-6. These are real discrepancies in the two numerical predictions, not just a pressure scaling artifact.

A pre-transition retry at t=.005, dt=.0003362166821386039 stays entirely vapor at its endpoints and has max error .03585462835163402. Crossing attempts from .005336216682138604 have errors 54.47, 3.813, 3.524, then .971364 on the accepted 45.821839 µs interval. The last 39.327598 µs rejected trial starts after both coarse and fine section-0 endpoints are mixture; U1 error is 1.376511449620906. The accepted following interval is led by P1 at .425918. Endpoint phase equality does not mean the entire dynamics are smooth.

Thermal maxima are about 1.79e-5 in warm startup, .07449 across the broad transition attempts and 7.60e-5 post-transition. No thermal coordinate controls these rejections. Aggregate conservation error also remains tiny, so temporal prediction differences are not conservation leakage.

## Supported interpretation and limits

High confidence: the additional rejections are accuracy decisions driven mainly by refrigerant M/U/P differences, not Newton refusal, a thermal tolerance issue or a fabricated equipment alarm. Several independent variables agree, weakening a single-coordinate scaling explanation. Physical inventory transport and pressure equalization provide a strong transient; section 0 has a measured EOS slope change and the downstream face changes donor direction shortly afterward. Output clipping/growth affects which intervals encounter these changes.

Moderate confidence: the combination of constitutive non-smoothness and hydraulic redistribution explains the locally reduced useful step sizes. The final post-crossing rejection provides independent reason not to blame every late trial on phase classification alone. No experiment isolates an additive percentage for each mechanism. Pressure-table and superheat interpolation knots can affect other intervals; their complete global attribution is unresolved.

Hypothesis not established: the original estimator is overly conservative, poorly scaled or needs replacement. Bisection temperature interval width is ~9.09e-10 K, far below the .00015 K temporal scale; it does not alone explain observed O(1–54) inventory errors. No tolerance or method change, event root solve, or adaptive-controller refinement is authorized here.
