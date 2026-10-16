# Diagnostic boundary and rounding matrix

All actual outcomes below are observed with the unchanged B4C candidate WASM and
historical adapter in **both** Chromium and desktop WebKit. Proposed classes
are offline research outputs. Numerical raw accuracy is not adapter acceptance.

## Original seven — all remain refused

Every original requested pressure is exactly 3500000 Pa, bits `414ab3f000000000`.
See `fixed-inventory.csv` and `fixed-inputs.json` for M,V,U/rho/u bits, exact PH
inputs, all raw getters and original outputs. WebKit uses its own ledger keys.

| Key suffix (both engines) | Original fixture ID | Phase independently resolved | Mathematical P−Pmax, Pa | Raw P−Pmax, Pa | Raw−mathematical P, Pa | Mechanism | Proposed |
|---|---|---|---:|---:|---:|---|---|
| 64 | `approach-3500000.0-liquid-0.001` | liquid | -2.58101716514e-09 | +1.49011611938e-07 | +1.51592629104e-07 | numerical-wrong-side | C, refused |
| 65 | `approach-3500000.0-liquid-0.01` | liquid | +4.01190221955e-07 | +3.6833807826e-07 | -3.28521436947e-08 | rounded-inventory-conflict | C, refused |
| 67 | `approach-3500000.0-vapor-0.001` | vapor | +7.02192693616e-09 | +2.79396772385e-09 | -4.22795921231e-09 | rounded-inventory-conflict | C, refused |
| 68 | `approach-3500000.0-vapor-0.01` | vapor | +7.04166454343e-10 | +1.86264514923e-09 | +1.15847869489e-09 | rounded-inventory-conflict | C, refused |
| 70 | `diagnostic-quality-band-3500000.0-hf--9.9e-10` | liquid | +7.72409866695e-07 | +7.65547156334e-07 | -6.86271036147e-09 | rounded-inventory-conflict | C, refused |
| 75 | `diagnostic-quality-band-3500000.0-hg-9.9e-10` | vapor | -8.24286338428e-10 | +1.39698386192e-09 | +2.22127020035e-09 | numerical-wrong-side | C, refused |
| 79 | `focused-3500000.0-stable-vapor` | vapor | +1.79967963169e-09 | +1.86264514923e-09 | +6.29655175452e-11 | rounded-inventory-conflict | C, refused |

Mathematical sign: independent unchanged-EOS 65/90-digit roots. Phase:
independently stable homogeneous branch and excluded extrapolated coexistence
quality, resolved caloric offsets at inherited resolution. Raw sign and guard
outcomes: actual binary64 browser execution. No nanopa physical certainty is
asserted. All original table PH guards pass; strict sat throws domain before SAT.

## Both sides, meaningful interior/exterior, all appropriate phases

The first 21 PH inputs are saved B5 diagnostics, unchanged. The last three are
new +100 Pa diagnostics constructed separately with B4C saturation h offsets
(hf−1000, midpoint, hg+10000 J/kg), not substitute original inventories.
One Pa ULP at the maximum is `4.6566128730773926e-10 Pa`. The three adjacent
Pa requests convert to bar 35, 34.99999999999999 and 35.00000000000001;
the latter neighbors round-trip one extra Pa ULP outward. None collapses to 35.

| Diagnostic | Requested P Pa (round-trip decimal) | Region | Mathematical fixed P−Pmax Pa | Raw P−Pmax Pa | PH adapter | MVU adapter | Proposed |
|---|---:|---|---:|---:|---|---|---|
| B5-sweep-0 | 3500000 | liquid | -2.58101716514e-09 | +1.49011611938e-07 | returns | refuses | C |
| B5-sweep-1 | 3500000 | mixture | -2.56909195634e-08 | -7.45058059692e-09 | returns | returns | C |
| B5-sweep-2 | 3500000 | vapor | +7.02192693616e-09 | +2.79396772385e-09 | returns | refuses | C |
| B5-sweep-3 | 3499999.9999999995 | liquid | -2.58101716514e-09 | +1.49011611938e-07 | returns | refuses | C |
| B5-sweep-4 | 3499999.9999999995 | mixture | -2.56909195634e-08 | -7.45058059692e-09 | returns | returns | C |
| B5-sweep-5 | 3499999.9999999995 | vapor | +4.06162821858e-09 | +2.79396772385e-09 | returns | refuses | C |
| B5-sweep-6 | 3500000.0000000005 | liquid | -2.58101716514e-09 | +1.49011611938e-07 | refuses | refuses | E |
| B5-sweep-7 | 3500000.0000000005 | mixture | -2.56909195634e-08 | -7.45058059692e-09 | refuses | returns | E |
| B5-sweep-8 | 3500000.0000000005 | vapor | +1.09405183642e-08 | +7.91624188423e-09 | refuses | refuses | E |
| B5-sweep-9 | 3499999.65 | liquid | -0.350001115583 | -0.350001534447 | returns | returns | D |
| B5-sweep-10 | 3499999.65 | mixture | -0.350000028425 | -0.350000009872 | returns | returns | D |
| B5-sweep-11 | 3499999.65 | vapor | -0.349999995049 | -0.349999995437 | returns | returns | D |
| B5-sweep-12 | 3499990 | liquid | -10.0000003215 | -9.99999993807 | returns | returns | D |
| B5-sweep-13 | 3499990 | mixture | -10.000000025 | -10.0000000079 | returns | returns | D |
| B5-sweep-14 | 3499990 | vapor | -9.99999999833 | -9.99999999907 | returns | returns | D |
| B5-sweep-15 | 3490000 | liquid | -10000.0000018 | -10000.000002 | returns | returns | D |
| B5-sweep-16 | 3490000 | mixture | -10000 | -10000 | returns | returns | D |
| B5-sweep-17 | 3490000 | vapor | -10000 | -10000 | returns | returns | D |
| B5-sweep-18 | 3400000 | liquid | -99999.9999989 | -99999.999999 | returns | returns | D |
| B5-sweep-19 | 3400000 | mixture | -100000 | -100000 | returns | returns | D |
| B5-sweep-20 | 3400000 | vapor | -100000 | -100000 | returns | returns | D |
| outside-100Pa-liquid | 3500100 | liquid | +100.000000357 | +100.000000092 | refuses | refuses | E |
| outside-100Pa-mixture | 3500100 | mixture | +99.9999999793 | +99.9999999963 | refuses | refuses | E |
| outside-100Pa-vapor | 3500100 | vapor | +99.9999999972 | +99.9999999939 | refuses | refuses | E |

At the exactly supported maximum and the inward one-ULP PH request, liquid
and vapor MVU calls refuse: false rejection of the intended supported originating
PH operation. For the first liquid inventory the exact mathematical inventory
also lies inside: a direct numerical wrong-side rejection. Some other refusals
are representational conflicts, not a claim that an out-of-bound exact inventory
should be accepted.

The one-ULP-above PH input is independently unsupported as an explicit request.
All three PH calls refuse; the mixture MVU call returns after the inventory and
numerical path move inward. This is a false acceptance if that return is treated
as authorizing the original request. Its exact inventory is mathematically inside,
so this example alone is not proof of an unsupported DU inventory being accepted.

+100 Pa liquid, mixture and vapor fixed-inventory roots are independently
resolved outside at approximately +100 Pa and all actual MVU operations refuse
at the table guard (unlabeled Error). These are genuinely unsupported inputs
under the model, not observed plant trajectory exits. The 0.35, 10, 10000 and
100000 Pa inward cases all return and pass focused independent gates.

C for two historically returned boundary-mixture cases is conservative offline
withholding of independent support certification at original reference resolution;
their actual adapter success remains recorded. It is not a new accepted failure
or an implemented tightening of the accepted contract.

## Exact fixed-inventory false-acceptance controls

These two original saved B5 inventories were selected by comparing its existing
73-pair references to raw browser results, then replayed without regeneration.

| Original fixed key | Original fixture ID | Mathematical P−Pmax Pa | Actual raw P−Pmax Pa | Actual MVU | Proposed |
|---|---|---:|---:|---|---|
| webkit-ledger-69 | `diagnostic-quality-band-3500000.0-hf--1.01e-09` | +2.94076290925e-07 | -3.49245965481e-07 | returns | C |
| webkit-ledger-76 | `diagnostic-quality-band-3500000.0-hg-1.01e-09` | +2.50420072426e-10 | -3.25962901115e-09 | returns | C |

These are mathematical false-acceptance hazards at the exact-inventory level:
the unchanged adapter returns an inward numeric coordinate for an exact inventory
whose converged same-EOS pressure lies outside. They do not establish real plant
pressure excursions below the original physical/reference resolution. The design
must preserve both outward and inward numerical-error risks. A small canonical
residual alone cannot decide strict support. No passing state is produced by the
classification prototype.

## Floating-point attribution

Exact stages retain `V=.003/5`, `M=rho*V`, `U_kJ=M*(h/1000)-100*(P/1e5)*V`,
`rho_DU=M/V`, `u_DU=(U_kJ/M)*1000` in that order. V is
`0.0006000000000000001`, bits `3f43a92a30553262`; no algebraic simplification
is used. `seven-case-analysis.json` records each local rational rounding error
as numerator/denominator and actual output bits, plus the inherited differential
pressure decomposition. The following separates backend getter pressure from
the independent mathematical EOS at those returned PH rho/T coordinates.

| Original key | PH binary64 getter P−request Pa | Independent PH-coordinate EOS P−request Pa | M/V density reconstruction error kg/m³ | u construction roundoff J/kg | Raw DU support side after Pa→bar |
|---|---:|---:|---:|---:|---|
| chromium-ledger-64 | +9.91858541965e-08 | -1.37993073075e-07 | +0 | -3.12760738264e-11 | outside |
| chromium-ledger-65 | +3.6833807826e-07 | +2.90242486063e-07 | +0 | -1.43075790893e-11 | outside |
| chromium-ledger-67 | -1.86264514923e-09 | +8.65653125713e-10 | +3.5527136788e-15 | +2.3589291285e-12 | outside |
| chromium-ledger-68 | -9.31322574615e-10 | +1.86567937742e-09 | +0 | +2.06707858682e-11 | outside |
| chromium-ledger-70 | +1.34576112032e-07 | +3.4367418421e-07 | +0 | +6.49198286271e-11 | outside |
| chromium-ledger-75 | +9.31322574615e-10 | +9.76444832406e-10 | +0 | -2.78963624598e-12 | outside |
| chromium-ledger-79 | +4.65661287308e-10 | +8.50119634952e-11 | +0 | +5.43497145592e-11 | outside |

The decomposition separately retains requested P, PH getter P, PH mathematical
EOS pressure and h/u consistency, density reconstruction, conservative-U
rounding, exact fixed-inventory root, binary64 recovery error and strict support
check. Homogeneous dp/du and dp/drho sensitivities are used only on the stable
homogeneous cases; no homogeneous derivative is imposed across coexistence.

For every original seven, division by exactly 100000 preserves the pressure
side. Its binary64 rounding changes last bits but does not originate rejection.
Exact unit equality Pa/100000 = bar is distinct from the rounded evaluation
of that operation. All decimals in JSON have round-trip binary64 bits alongside;
high-precision EOS strings are explicitly mathematical reference values.

## Inherited lower/temperature protection

Each engine accepts standalone sat(.3) and sat(35), and refuses the representable
bar values one ULP below .3 and one ULP above 35 before any SAT EOS call.
Three clearly labeled synthetic DU-output guard-isolation cases exercise the
195.495 K floor, Tsat−30 K and Tsat+250 K checks. All refuse with domain.
These are predicate tests, not physically generated inventories or phase proofs.
Bounded table availability and the accepted thermal 200–400 K domain remain
source-preserved. No tolerance transfer to other boundaries/phases is proposed.

All 24 generated PH diagnostics have raw canonical and normalized mass/energy
checks within original budgets, including unsupported requests; support is tested
separately. That numerical accuracy does not make them supported. No genuine
thermal/plant trajectory, full A2 sweep or long-duration test is run.
