# Phase certification matrix

**PARTIAL PHASE CERTIFICATION**. Exact rational outward endpoints are in
`evidence/results.json` and `phase-matrix.json`; decimal table values are
displays. No row has complete physical-branch certification. Conditional
means the explicitly unproved convex-envelope/topology dependency in
`BRANCH_AND_TOPOLOGY.md`. No row is original scientific or browser qualification.

The seven historical refusals remain refused; the two inward hazards retain
their historical returns. Rounded DU remains two inside/five outside;
exact M/U/V remains one inside/six outside. These are different targets.

| Exact-inventory case | Homogeneous p−3,500,000 (Pa) | Validated density side | Validated mixture continuation | Complete diagnostic outcome |
|---|---:|---|---|---|
| webkit-ledger-69 | +3.04967661516e-07 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| webkit-ledger-76 | +4.66917128521e-11 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| native-ledger-148 | +2.09974650846e-09 | DOME_INTERIOR | INTERIOR | UNRESOLVED |
| native-ledger-162 | +8.24838518944e-07 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| native-ledger-165 | +3.81257914279e-09 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| generated-subcooled-liquid | -100000 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| generated-superheated-vapor | -100000 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| generated-outside-liquid | +100000 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| generated-interior-mixture | not used | not used | INTERIOR | UNRESOLVED |
| generated-dome-interior-homogeneous | +158001.142444 | DOME_INTERIOR | INTERIOR | UNRESOLVED |
| chromium-ledger-64 | +3.22972603677e-09 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-65 | +3.73186568858e-07 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-67 | +7.07996082661e-09 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-68 | +1.0267011886e-09 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-70 | +7.3396167196e-07 | LIQUID_SIDE | Q_LT_ZERO | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-75 | -1.45517845677e-09 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |
| chromium-ledger-79 | +1.20428458609e-09 | VAPOR_SIDE | Q_GT_ONE | CONDITIONAL_PHASE_PROOF |

## Primary inventory identity and enclosures

For both primary rows: homogeneous existence and local uniqueness PASS;
parameterized coexistence existence and local uniqueness PASS at every
possible root T; endpoint stability PASS; competing-phase exclusion
UNRESOLVED; complete physical branch FALSE; original scientific qualification
UNRESOLVED; browser arithmetic portability NOT DEMONSTRATED.

### webkit-ledger-69

M `3fd406de00d710be`, U_kJ `406b448176d039b2`, V `3f43a92a30553262`.

| Field | Validated enclosure (display) |
|---|---|
| Root T (K) | `[345.56367343079841661977999199115 +/- 4.15e-30]` |
| Root p−max (Pa) | `[3.049676615158225e-7 +/- 3.47e-23]` |
| rhoL (kg/m³), entire root T interval | `[521.53190104499517563693902 +/- 4.08e-24]` |
| rhoV (kg/m³), entire root T interval | `[28.05137732886882535160284 +/- 5.12e-24]` |
| d*−rhoL (kg/m³) | `[2.911129446658847e-8 +/- 2.52e-24]` |
| d*−rhoV (kg/m³) | `[493.48052374523764475192465 +/- 1.47e-24]` |
| Algebraic continuation Q | `[-1.705132346599769e-12 +/- 5.06e-28]` |

### webkit-ledger-76

M `3f913c19a47fa406`, U_kJ `40394d3fa3941ea6`, V `3f43a92a30553262`.

| Field | Validated enclosure (display) |
|---|---|
| Root T (K) | `[345.56367379185633450450477842409 +/- 3.13e-30]` |
| Root p−max (Pa) | `[4.6691712852129e-11 +/- 2.06e-25]` |
| rhoL (kg/m³), entire root T interval | `[521.53190031777057170914518 +/- 4.12e-24]` |
| rhoV (kg/m³), entire root T interval | `[28.05137758234069986086206 +/- 5.79e-24]` |
| d*−rhoL (kg/m³) | `[-493.48052291769411622253267 +/- 3.37e-24]` |
| d*−rhoV (kg/m³) | `[-1.8226424437424954e-7 +/- 1.27e-24]` |
| Algebraic continuation Q | `[1.0000000008746197306823840 +/- 6.08e-26]` |

## Positive and negative controls

The separately generated liquid (335 K, about 34 bar), vapor (365 K, about
34 bar), exterior liquid (335 K, about 36 bar), and interior mixture
(344 K, Q about 0.5) have independently verified local mathematical roots,
endpoint stability and the stated inequalities. Full stable-equilibrium
qualification of these requested positive controls is **not established**:
the same missing topology gate applies. They are never substituted for
historical inventories. Construction operands and bits are in `inputs.json`.

The dome-interior homogeneous control has positive cv and dp/drho, but a
validated same-U,V mixture has entropy greater by about 0.07058947 J/kg/K.
That homogeneous root is rigorously excluded under additive bulk-phase
thermodynamics; global optimality of the competitor remains unproved.

Negative controls retain Q<0 and Q>1 algebraic roots, an endpoint-sign
overlapping validated box, a non-enclosing box, singular preconditioner,
equal-density root, invalid/nonfinite coordinates, bad seed, insufficient
parameter coverage and pressure-inside evidence without topology proof.
See `evidence/verification.json`; none emits a physical-branch success.

Optional Gate B 148, 162 and 165 use C2’s saved exact M/U/V, separately from
Gate B rounded-DU inputs. Ledger 164 is not expanded. Original endpoint
independent-reference qualification remains unresolved.
