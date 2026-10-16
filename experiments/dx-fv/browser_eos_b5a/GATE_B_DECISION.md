# Gate B — physical recovery not established; no source patch

Gate A independently passed before this analysis. Its identity is commit
`b013448bc1005d9bb922c4420772b590180febd2`; `gate-a.patch` is the sole functional
patch. There is no A2 backend candidate and no Gate B source patch.

A1 removes the stale decision for the three resolved original liquids and
recovers their stable homogeneous roots at unchanged rho/u. The hf one-ULP case
also returns a homogeneous raw result, but its ~2.33e-9 J/kg mathematical energy
separation is below the unchanged 1e-8 J/kg reference resolution. It remains
unresolved, not a fourth physically certified success.

For vapor cases 148, 164 and 165, final Q remains respectively
1.000000000000002, 1.0000000000000018 and 1.0000000000000024. The returned and
last-evaluated Brent temperature is 345.5636735993518 K. Quality residuals are
about -2.00e-15, -2.00e-15 and -2.22e-15. The captured scaled-residual stop is
about 1.53e-13; the original iteration-10 stop and strict QT refusal remain.
No physically valid state is returned from these updates.

The fixed-inventory, same-EOS high-precision references find equilibrium roots
below Q=1 for 148 and 164; their homogeneous roots are algebraic diagnostics,
not suitable equilibrium replacements. For 165 the mathematical homogeneous
root is infinitesimally on the vapor side; A1's binary64 caloric comparison is
equal and still dispatches coexistence. Their actual internal energy separations
from saturation are about -1.42e-10, -3.53e-10 and +6.54e-11 J/kg. None resolves
a physical phase under the existing independent reference contract.

For 148/164, an incompatible homogeneous fallback would replace genuine
mathematical equilibrium. The invalid quality results reflect the finite
saturation/quality calculation at an endpoint rather than a supported quality
outside [0,1]. For 165 both equality dispatch at binary64 resolution and the
out-of-range quality contribute. A1's consistent final coordinates do not make
this finer caloric sign representable or establish a physically admissible QT
solution. The small quality residual alone provides no such certificate.

A joint constrained coexistence recovery, higher-precision backend or an explicit
numerical uncertainty policy could be investigated separately. This run does not
establish such an algorithm under the unchanged contract. It does not clamp Q,
substitute an endpoint density, alter u/p, force a homogeneous branch, weaken QT,
change generic Brent/Newton stopping, or relabel numerical refusal as domain proof.

All original failures, including the now-returning hf row, remain individually
retained. `gate-B-characterization.json` contains the A1 decisions, residuals,
current outcomes and mathematical references. Gate B is NOT PASSED. Essential
B5A acceptance is incomplete; no browser candidate qualification, coupled A2
campaign, B5B work or production integration follows from Gate A passing.
