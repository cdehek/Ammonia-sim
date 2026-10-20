# Physical-domain and phase analysis

All times above 0.001 s are UNQUALIFIED RESEARCH. No longer-duration scientific qualification is claimed.

The fixture has five fixed refrigerant control volumes totaling 0.003 m³, with original mass/internal-energy/volume state and P/H nonlinear coordinates. Tube/fin/finite-air storage adds eleven thermal nodes. The illustrative 20 mm bore corresponds to about 9.55 m of tube. These are research inputs, not equipment calibration.

| Fixture | Initial inventory kg | Final inventory kg | Boundary Δmass kg | Boundary enthalpy kJ | Tube→fluid heat kJ |
|---|---|---|---|---|---|
| cold | 0.05955 | 0.05954 | -4.022e-06 | -0.002063 | 0.03183 |
| warm | 0.008173 | 0.00807 | -0.0001025 | -0.3351 | 0.05468 |

Cold inventory changes from 0.05954796 to 0.05954394 kg; all sections remain liquid–vapor mixture. At 0.01 s, pressure decreases spatially from about 3.51005 to 3.50371 bar and enthalpy from 500.579 to 500.555 kJ/kg. Quality spans about 0.13995–0.14008. Refrigerant temperature spans about 267.839–267.885 K.

Warm inventory changes from 0.00817275 to 0.00807025 kg. All sections start superheated; section 0 becomes two phase while the remaining four stay superheated. At 0.01 s, pressure spans about 3.50977–3.52133 bar and enthalpy about 1566.14–1649.79 kJ/kg; section 0 quality is about 0.972244. Section 0 crosses the vapor saturation boundary at interpolated t=0.0053754278 s in bracket [0.0053591276, 0.0053820385] s. This is supported in the measured trajectory; it does not qualify general phase-transition dynamics.

Supported public PH pressure is 0.3–35 bar. Superheated support ends at 250 K above saturation; subcooled support depends on populated liquid-table temperatures. The thermal-node domain is [200,400] K. No property/domain refusal occurred in the normal fixtures. A second diagnostic replay records successful public property pressure, enthalpy, temperature and quality ranges for each tested interval, separately for PH, M/U/V recovery and saturation; `T` is original engine °C, so add 273.15 for kelvin. Phase histograms count property results, not physical time or inventory. These include boundary states and nonlinear probe states and therefore exceed the physical-cell range. See `propertyRangesByInterval` in `evidence/analysis.json` for every interval. The range replay's exact state/attempt hashes match canonical; range-accounting overhead is included in the primary observed cost profile.

Successful public-property call envelopes per interval ending at the listed time (PH includes fixed boundary donors and Newton probes; recovery includes committed and stage candidate states):

| Fixture | Interval end s | PH pressure bar | PH temperature K | Recovery pressure bar | Recovery temperature K | PH phase labels |
|---|---|---|---|---|---|---|
| cold | 0.0001 | 3.5–4 | 267.812–308.116 | 3.5–3.50032 | 267.812–267.814 | Liquid + vapor, Superheated vapor |
| cold | 0.0005 | 3.5–4 | 267.812–308.116 | 3.50006–3.50121 | 267.812–267.82 | Liquid + vapor, Superheated vapor |
| cold | 0.001 | 3.5–4 | 267.812–308.116 | 3.50026–3.50208 | 267.813–267.827 | Liquid + vapor, Superheated vapor |
| cold | 0.002 | 3.5–4 | 267.812–308.116 | 3.50051–3.50348 | 267.815–267.837 | Liquid + vapor, Superheated vapor |
| cold | 0.005 | 3.5–4 | 267.812–308.116 | 3.50099–3.50658 | 267.819–267.859 | Liquid + vapor, Superheated vapor |
| cold | 0.01 | 3.5–4 | 267.812–308.116 | 3.50222–3.51005 | 267.828–267.885 | Liquid + vapor, Superheated vapor |
| warm | 0.0001 | 3.5–4 | 271.278–308.116 | 3.63836–3.65001 | 287.173–287.575 | Liquid + vapor, Superheated vapor |
| warm | 0.0005 | 3.5–4 | 271.278–308.116 | 3.61134–3.64922 | 285.647–287.57 | Liquid + vapor, Superheated vapor |
| warm | 0.001 | 3.5–4 | 271.278–308.116 | 3.59116–3.64197 | 283.724–287.506 | Liquid + vapor, Superheated vapor |
| warm | 0.002 | 3.5–4 | 271.278–308.116 | 3.56712–3.63073 | 279.907–287.388 | Liquid + vapor, Superheated vapor |
| warm | 0.005 | 3.5–4 | 269.29–308.116 | 3.52733–3.60628 | 269.293–287.119 | Liquid + vapor, Superheated vapor |
| warm | 0.01 | 3.5–4 | 267.967–308.116 | 3.50977–3.54312 | 267.967–287.064 | Liquid + vapor, Superheated vapor |

Tube/fin storage is active. Cold tubes lose roughly 0.006 kJ each while fins gain about 0.008735 kJ each; finite air loses 0.03557 kJ despite receiving 0.01 kJ external load. Warm tubes lose about 0.00752–0.02398 kJ each; the air gains about 0.009988 kJ while feeding small net heat to solids. Signed link and tube–refrigerant ledgers close with these changes. Air is a fixed-volume, fixed-mass, perfectly mixed energy node; no ventilation or air-pressure dynamics are coupled.

Boundaries are fixed inlet 4 bar / 500 kJ/kg and outlet 3.5 bar / 1700 kJ/kg reservoirs, with the original signed donor-enthalpy transport. The actual outlet energy uses the internal donor under forward flow. Fixed pressures and hydraulic loss coefficients determine flow; there is no valve/controller response to refrigerant inventory. The warm initial pressure mismatch produces a large initial outflow transient. Constant uncalibrated tube-to-bulk conductance is 0.60 kW/K distributed over sections; film/radial and phase-dependent transfer are unresolved.

The formulation is a credible conservation-based component research foundation: spatial pressure/enthalpy, liquid–vapor transition and solid/air energy storage are represented. It is not a complete refrigeration system. No scientific compressor, receiver, condenser, feed valve or plant control has been coupled. Slip/void dynamics, detailed boiling/dryout, oil, frost/defrost, distributor maldistribution and validated equipment correlations are absent. Manufacturer/measurement calibration, realistic reservoir dynamics and mesh/time convergence remain gaps.

Bulk wet indication is an equilibrium section diagnostic. It is not compressor suction protection; even a dry terminal reading would not establish a safe compressor inlet. Missing plant coupling limits physical interpretation independently of the observed numerical integration cost. Numerical accuracy rejections near the transition are not fabricated physical alarms.
