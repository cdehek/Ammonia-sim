# Requested output boundary sensitivity

Three distinct warm integration trajectories use the identical original model, reservoirs, tables and numerical settings, all bounded to 0–0.01 s. Every schedule has a canonical uninstrumented and an observed replay; exact scientific/decision/Jacobian comparisons pass within its own schedule.

Original B13 requests: .0001, .0005, .001, .002, .005, .01 s. Added schedule inserts .00525 and .0055. Fine schedule inserts .0051, .0052, .0053, .0054, .0055, .0056. No setting, minStep, retry, stage, signed probe, eventStep or convergence tolerance changes. Boundary clipping is actual numerical segmentation and is not a pure observation call.

| Schedule | Accepted physical halves | Rejected trials | Interpolated event s | Final max tolerance ratio |
|---|---|---|---|---|
| original | 86 | 8 | 0.00537543 | reference |
| added | 88 | 7 | 0.0053753175346457826 | 0.092746 |
| fine | 98 | 5 | 0.005375175168270083 | 0.239237 |

At common requested times (0, .0001, .0005, .001, .002, .005, .01), differences in M/U/P/H are divided by the original absolute+relative scales, using max magnitude of the two compared states. Thermal differences are divided by capacity and the original .00015 K scale. For this **comparison only**, maximum ratio <=1 is a stated sensitivity criterion. There is no step-doubling divisor in this between-trajectory comparison. This diagnostic criterion does not replace the original solver's tolerance or qualify either trajectory.

Both schedules are exactly identical through .005 s. At .01, the added trajectory's maximum is .09274604145 (section 1 M difference +1.47427221e-10 kg). The fine trajectory's max is .23923652252 (M1 +3.80285566e-10 kg); U1 differs +5.26685075e-7 kJ, P0 +6.11135749e-7 bar, and U0 +4.11484011e-7 kJ. Full coordinate comparisons are retained in `analysis.json:boundaries`.

All accepted half states pass independent conservation audits: max combined errors 1.41501082e-10 and 1.61447633e-10 kJ. No failure/refusal, extra retry strategy or unsupported state occurred. Their brackets are [.005362130816122282,.00538042006543758] and [.005371654811139449,.005386134121015835] s. The event times differ by fractions of a microsecond, smaller than any accepted bracket width; none is a root-solved truth.

Observed rejection counts vary 8→7→5, confirming boundary/controller sensitivity. They do not improve monotonically in final distance from the original trajectory. Additional partitions are not a formal convergence proof or an established optimal output cadence. Common final-state differences are small under declared scales, but no long-duration accuracy, global order or equipment qualification follows.
