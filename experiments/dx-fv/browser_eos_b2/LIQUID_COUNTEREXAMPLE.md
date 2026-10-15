# Same-phase liquid derivative counterexample

**FAIL — valid liquid input, unchanged backend and probes.**

P = 30298.937123458254 Pa (`40dd96bbf9d4ab61`); h = 98904.56398938334 J/kg (`40f825890619bb4c`). The requested enthalpy is about 0.001 J/kg below the native saturated-liquid value. Actual backend classification is phase 6 with Q = −6.99036205016646e−10.

The returned T = 218.26293725550536 K and rho = 707.4995406964335 kg/m³ independently produce pressure residual +2870.5026330731307 Pa and enthalpy residual +2.5891424380388344 J/kg. All four browser backends reproduce this fault in both engines. No decimal substitution is used.

A separate native homogeneous-liquid DT root converges at T = 218.26293702735904 K, rho = 707.49832658790388 kg/m³, with pressure/enthalpy residuals 6.88974978402e-07 Pa / 1.20780896395e-09 J/kg. It is -2.28146291192e-07 K below saturation; cp = 4383.1389876, cv = 2963.1955668 J/(kg K), and isothermal compressibility = 5.97960986829e-10 1/Pa, all positive. This reference root is diagnostic only and never enters the browser model.

| Probe | Nominal signed size | Actual binary64 increment | Physical probe phase | FD density derivative | Homogeneous analytic derivative | FD / analytic |
|---|---:|---:|---|---:|---:|---:|
| P | 0.01 | 0.0099999999983992893 | liquid | -0.121410188478 | 6.644991730529736e-07 | -182709.31462655496 |
| P | -0.01 | -0.0099999999983992893 | two-phase | 2.81888465079 | excluded | excluded |
| H | 0.00098904563989383348 | 0.00098904564219992608 | liquid | -1.21437697984 | -0.0002677841271333407 | 4534.910238475705 |
| H | -0.00098904563989383348 | -0.00098904564219992608 | liquid | 1.22728783142 | -0.0002677841271333407 | -4583.123893689126 |

| Probe | Exact P Pa | Exact h J/kg | Returned T K / rho kg/m³ | Independent DT ΔP Pa / Δh J/kg | Backend phase / Q |
|---|---:|---:|---|---|---|
| P +0.01 | 30298.947123458252 | 98904.563989383343 | 218.26293702530182 / 707.49832659454876 | 8.698261808604002e-07 / 1.4988472685217857e-09 | 0 / -1 |
| P -0.01 | 30298.927123458256 | 98904.563989383343 | 218.26293196031 / 707.47135184992567 | -1.3824319466948509e-10 / -1.4551915228366852e-11 | 6 / 1.5531609308105042e-08 |
| H +0.00098904563989383348 | 30298.937123458254 | 98904.564978428985 | 218.26293725550536 / 707.49833962217645 | 31.442751009752101 / 0.028360747048282064 | 6 / -7.6571274703551574e-12 |
| H -0.00098904563989383348 | 30298.937123458254 | 98904.563000337701 | 218.26293680171074 / 707.49832685275499 | 3.3349351724609733e-08 / -2.0809238776564598e-09 | 0 / -1 |

The +P, +h and −h probes remain physically liquid. Only −P crosses into physical coexistence and is excluded from a homogeneous derivative assertion. Backend phase codes alone conceal the +h failure because both returned states are erroneously called two-phase. The normalized mass contamination is about 1.70–1.72e−6, compared with the existing nonlinear scale 1e−11; this is a diagnostic comparison, not a replacement acceptance rule.

The upstream quality tolerance admits Q down to −1e−9 and extrapolates the coexistence specific-volume formula below the saturated-liquid enthalpy. Its legitimate one-sided coexistence density/enthalpy slope is about −1.214375, versus the liquid slope −0.000267784, a factor about 4534.902. That physical one-sided slope explains the +h result; applying it to valid subcooled liquid is the fault. The reverse-h/forward-pressure probes switch back to liquid and reveal the resulting artificial density jump. This is not ordinary finite-difference truncation or a smoothness requirement across boiling.

The preserved canonical PH→M/U/V→DU test moves P by about 4245.087 Pa (allowed 0.1 Pa), h by 6.000127 J/kg (allowed 0.1 J/kg) and T by 0.000495447 K (allowed 0.0001 K). This does not by itself prove a DU solver defect: combining requested P/h with an inconsistent PH density constructs different physical inventories. The unchanged coupled solver rejects the zero-exchange pure trial even after Newton converges at iteration zero, and the exact original state survives.

The defect is a phase-selection/extrapolation path shared by 30-bit, 44-bit, official 8.0 and official 7.2. The adjusted B1 single-phase stopping rule does not govern this path. No number of precision bits is established as a remedy. The separate superheated-vapor cache residual has separate evidence and must not be conflated with it.

Recommended next scientific experiment (engineering approval first): preserve these exact base/probe inputs and instrument the unmodified upstream PH phase decision to record saturation enthalpies, pre/post quality tests, chosen branch and lever-volume density. On matching native source, compare DU recovery of (a) the independently converged physical-liquid DT inventory and (b) the unchanged returned-PH inventory. Record residuals and the original canonical budgets separately. Repeat at 0.30298937123458254, 3.5, approximately 8 and 35 bar, with the existing signed probes; add a labelled quality-tolerance sweep only as a diagnostic. This isolates the classifier from the caloric/inversion paths before proposing any repair. Do not modify EOS data, clamp Q, alter probes/budgets or feed reference-polished properties into the accepted solver. A source patch requires separate explicit authorization.

Raw reproduction: phase matrices → native.py / boundary-reference.py → analyze-boundary-derivatives.py (both native versions), plus run-boundary.py and run-initialization.py. See README.md for isolated output paths. The earlier relative-density derivation and first phase matrix remain archived; corrected measurements are additive and explicitly identified.
