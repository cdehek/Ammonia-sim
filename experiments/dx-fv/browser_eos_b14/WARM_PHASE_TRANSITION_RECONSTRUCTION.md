# Warm phase transition reconstruction

Observed direction is **superheated vapor into liquid–vapor equilibrium**, in section index 0. It is not the opposite transition proposed in the mission wording. Original B13 and original B9C scientific traces agree exactly on the event and direction; no classification has been changed.

## Actual accepted bracket

| Quantity | Left accepted state | Right accepted state |
|---|---|---|
| Time s | 0.0053591276016748427 | 0.0053820385212110817 |
| Phase | Superheated vapor | Liquid + vapor |
| Pressure bar absolute | 3.536724628731566 | 3.5366027162082014 |
| Recovered enthalpy kJ/kg | 1601.9251351171029 | 1601.7448627836231 |
| Recovered temperature K | 268.12791881582734 | 268.07815267859576 |
| Quality | undefined (null) | 0.9999595758797615 |
| Physical superheat K | 0.04888194962404668 | not a superheated state |
| Mass kg | 0.0017258764979199356 | 0.001726297263493033 |
| Internal energy kJ | 2.5525214644916754 | 2.5528916104649 |
| Fixed volume m³ | 0.0006000000000000001 | 0.0006000000000000001 |
| Tube 0 temperature K | 293.13970590341154 | 293.1396353195192 |
| Fin 0 temperature K | 293.14999041334556 | 293.1499903079286 |
| Air temperature K | 293.151243181539 | 293.1512484926965 |

The bracket width is 2.2910919536238937e-05 s (22.911 µs). The original interpolated event is 0.0053754278169825922 s. It linearly weights signed h−hg between accepted half endpoints. The event is not a new accepted state and is not a precision root. Floating additions of half steps and outer accepted intervals can differ in their last time bit; receipts retain original values without rounding them into equality.

`accepted-warm.json` contains every actual accepted half piece, all five conserved M/U/V inventories, eleven thermal energies/capacities/temperatures, recovered properties and original accepted PH states, saturation references, endpoint and integrated hydraulic/thermal rates, signed ledger, conservation audits, and section-wise changes. `transition-bracket.json` extracts the bracket. `temporal-warm.json` links attempts, accept/reject, original error and controller proposals. No output requests were added to the canonical schedule merely to observe these states.

## Inventory and transport interpretation

Over the bracket, section 0 mass increases by 4.207655730974289e-7 kg and U increases by 0.00037014597322482246 kJ, while specific h and temperature decrease. This is consistent with lower-enthalpy feed and changing inventory, not a loss of conserved energy. The fixed inlet is 4 bar absolute / 500 kJ/kg. At the left endpoint its signed transport is +0.014907647 kg/s / +7.45382349 kW. Face 1 is negative: −0.003703384 kg/s / −6.10415490 kW, so its donor is section 1 and it supplies energy to section 0. Tube-to-refrigerant heat is positive, about 3.00141445 kW. At the right endpoint those values are +0.014909608 kg/s / +7.45480419 kW, −0.002852126 kg/s / −4.70105291 kW, and +3.00737792 kW. Ledger integration, not endpoint-rate × time approximations, closes each balance.

Tube and fin energies are conserved thermal coordinates relative to the original 273.15 K anchor; temperatures are derived with each capacity. Tube 0 energy is 19.470533261688175 → 19.47046451100065 kJ, fin 0 is 16.984026834518538 → 16.984026744998257 kJ, finite air is 86.16535562607002 → 86.16537850653644 kJ. Original record energy references are retained separately. Neither p/h/T nor quality is a conserved coordinate.

Canonical M/U/V recovery and the implicit PH representation are separately retained: at the left endpoint recovered h differs from PH-coordinate h by about 5.2e-8 kJ/kg within the original recovery tolerance. Event left/right values use original PH coordinates (0.12753262334285864 and −0.05172204394148139 kJ/kg), not the separately recovered h. Both representations classify these endpoints identically.

## Constitutive regularity and solver behavior

At the left pressure, offline original-engine PH probes give dT/dh ≈0 on the mixture side and ≈0.38329 K/(kJ/kg) on the vapor side; dρ/dh ≈−0.00223865 versus −0.0053264 (kg/m³)/(kJ/kg). This is a measured slope change. Zero-offset vapor table rows agree with saturation rows; direct original `statePT(p,Tsat)` h and density match saturation bit exactly at the independently checked pressure. There is no evidence of a macroscopic value jump here. Piecewise interpolation has derivative changes, plus the original 1e-8 classification band and finite inversion precision; B14 leaves all intact. This is local evidence, not a proof of global table smoothness.

All 306 warm Newton solves converge, all 867 recorded line searches accept factor 1, and all 18,207 derivatives use the first positive probe. No normal domain probe fails. The event bracket therefore does not diagnose Newton failure.

An independently observed face-1 flow reversal lies in [0.005382038521211082, 0.005397063933720186] s, after entry to the mixture. The last rejected trial spans it. The donor rule switches there and the pressure gradient is small. These dynamics and the phase slope change jointly support a local accuracy burden; their individual causal shares are not isolated. See `hydraulic-transition.json` and [the figure](figures/warm-transition.png). Connecting lines are visual guides, not additional accepted states.
