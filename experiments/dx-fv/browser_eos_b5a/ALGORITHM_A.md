# Gate A algorithm — recorded before functional edits

Control A is exact B4C. Candidate A1 adds an opt-in saturation-D polish used only
by the pure-fluid legacy DU dispatcher (`other == iUmolar`). The original H/S/P
callers and superancillary path keep their behavior. No EOS/data, generic solver,
quality validation, requested inventory, scientific budget or retry limit changes.

The current saturation-D loop evaluates (T,rhoL,rhoV), forms residuals and a
Newton correction, advances its local coordinates, and tests the old residual.
It returns cached substates at the previous coordinates. Pressure validation
also uses the previous evaluation. A final refresh by itself says nothing about
whether the remaining coordinate error can reverse the DU caloric comparison.

For the opt-in DU path, retain the fixed density exactly, including its actual
mass-to-molar conversion. At each evaluated iterate compute the original
pressure/chemical-potential residual and Newton correction. Accept only when
(a) the original residual norm is <=1e-9 and (b) the undamped correction in tau
and the free density coordinate is <=8*DBL_EPSILON times that coordinate. For
log-density, use <=8*DBL_EPSILON in log space. Break BEFORE applying this final
correction, so cached states, evaluated coordinates and pressure validation
refer to one and the same point. Otherwise advance and evaluate again, under
the original iteration/retry limits. Keep imposed rho exact instead of a
rho/reducing-density round trip. No global tolerance changes.

The coordinate criterion is a local roundoff-level polishing criterion, not a
new scientific acceptance budget or proof of phase sign at an endpoint. Record
actual p/g residuals and compare caloric thresholds to the independent EOS roots.
The existing physical reference resolution remains 1e-5 Pa / 1e-8 J/kg. Resolve
only signs supported by that contract; endpoint-scale signs are reported as
unresolved regardless of whether a candidate returns a number. Gate B separately
examines every invalid quality and ambiguous endpoint; A1 success alone cannot
establish physical acceptance of those roots.

Gate A must independently recover the three resolved original liquids at exact
rho/u, preserve real coexistence, show final-cache consistency and unchanged
relevant non-DU caller outputs. If polishing fails to converge or breaks a
resolved physical state, retain the failure and stop downstream functional work.
