# Original accepted A2 compatibility contract

Source checkpoint: `be9eb35a4ddf5098e685182f8104685127c6a6ee`.
`accepted/` contains verbatim dependency-closure snapshots, verified against Git
objects by `audit.py`; the current branch's later nine-section model is not used
for the coupled operating runs. The original generic Newton routine also runs
the static five/nine-section closure, with its diagnostic ten-row split caveat
recorded separately. No original or snapshot solver implementation is edited.

The engine contract is synchronous `ph(p_bar,h_kJkg)`, `sat(p_bar)` and
`stateMVU(M_kg,V_m3,U_kJ,p_guess)`. Fluid temperatures are Celsius; thermal-node
temperatures are Kelvin. Quality is defined only within `[0,1]`; homogeneous
sentinels are not interpreted as liquid fraction. The adapter classifies known
single-phase results using enthalpy relative to saturation, not `Q<1`.

Canonical balances are `M=rho*V`, `U=M*h-100*p_bar*V` in kJ, with recovery
`rho=M/V`, `u=U/M`. Each shared face has one signed mass and donor-enthalpy flux.
Tube/fluid and tube/fin/air transfers remain equal/opposite signed ledgers.
Five fluid sections share 0.003 m³; eleven original tube/fin/air nodes, finite-air
load, hydraulics, effective 0.60 kW/K total conductance and material capacities
remain the original fixture values. No equipment calibration, dry-out or wet-
suction physics is introduced. `wet` retains the existing equilibrium indicator.

Numerical requirements retained verbatim:

| Requirement | Accepted value or rule |
|---|---|
| Fluid nonlinear norm | ≤ `1e-11` |
| Thermal stage closure | ≤ `1e-12 K`, through its original capacity scale |
| Newton limit | 30 iterations |
| Pressure FD | `1e-7*max(1,abs(p_bar))` bar |
| Enthalpy FD | `1e-8*max(1,abs(h_kJkg))` kJ/kg |
| Thermal FD | `capacity_kJ/K * 1e-6` kJ |
| Probe search | signs `+1,-1`; at most 12 shrink levels; retain branch checks |
| Line search | strict norm reduction, factors 1 down to `2^-28` |
| Fluid residual scales | `max(.01,M)` kg; `max(1,abs(U))` kJ |
| PH versus recovered M/U/V | ≤ `1e-6 bar`, `1e-4 kJ/kg`, `1e-4 K` |
| Integration | Original two-stage TR-BDF2; `gamma=2-sqrt(2)` |
| Adaptive comparison | One full versus two half steps, divisor 3; accept norm ≤1 |
| Committed state | Two half steps, without extrapolating physical inventory |
| Minimum step / attempt budget | `1e-9 s` / 100,000 per advance |
| Phase events | Original h−hf/hg sign crossings and event refinement |
| Domain | 0.3–35 bar; bounded table support; up to 30 K subcooling / 250 K superheat; thermal 200–400 K |

The selected accepted option is `timestepGrowth:'failure-aware'`; thermal
Jacobian remains finite difference. A1 exact thermal columns and alternate
controllers are not selected. Original rejected-trial halving, phase/event
clipping, scheduled boundary resets, domain proof, rollback and stop rules run
unchanged. The adapter calls the unchanged table PH interface **only as a support
guard**; it does not return table properties or interpolate EOS values. Its
additional physical-temperature check cannot expand the original envelope.
Out-of-domain/failed flashes throw; there is no property fallback or correction.

The original `accuracyOptions` supplies the three standard regimes, without
alteration: relative tolerance `1e-6,1e-7,1e-8`; max full trial intervals
`0.5,0.25,0.125 s`; event half-step limits `0.002,0.0005,0.0001 s`; all absolute
mass, energy, pressure, h and temperature budgets come from that same function.

Separate scientific comparisons retain their original limits:

- Every required mass ledger `<1e-8 kg`; energy ledger `<1e-6 kJ`.
- Same-EOS temporal pressure `<5e-5 bar`, h `<.05 kJ/kg`; nominal temperature
  `<.01 K`, tighter comparison `<.001 K`; event identities match and clocks
  differ by `<.001 s`.
- Frozen independent direct-EOS trajectory comparison: pressure `<1e-4 bar`
  (strictly below 10 Pa), h `<.05 kJ/kg`, temperatures `<.01 K`, terminal vapor
  event clock `<.001 s`. Refinement comparisons use the unchanged 1e-8 regime.
- Standalone value comparison: pressure `<10 Pa`, h `<50 J/kg`, T `<.01 K`.
  These coarse value budgets do not establish small-probe consistency.

The focused standalone risk screen compares normalized liquid caloric residual
and pressure/enthalpy probe density contamination with the existing `1e-11`
nonlinear scale. That is a necessary local screening argument, not a new
universal EOS acceptance threshold or a proof of coupled convergence. The 1%
derivative-ratio counts are descriptive only. Independent native reference roots
use the prior diagnostic evaluation limits `1e-5 Pa,1e-8 J/kg`; no polished root
or correction is inserted into the browser backend.

Ordinary property getters may echo specified p/h. The adapter preserves the
original requested-PH coordinate semantics for stage accounting, while density
is the untouched native flash result. Actual EOS pressure/enthalpy residuals are
evaluated separately at returned density/temperature. Full PH/DU consistency is
then subject to the original stage/recovery check above. This does not permit
rounding an input, returning a corrected density or hiding an unsuccessful flash.
