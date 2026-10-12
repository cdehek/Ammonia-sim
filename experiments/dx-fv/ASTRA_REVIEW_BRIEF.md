# Independent Astra mathematical review request

Review the **unqualified research** snapshot on
`wip/dx-fv-stage2b-property-research-20261012`, based on accepted A2
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. The exact preservation commit is in
the package manifest/delivery. Read `RESEARCH_WIP_HANDOFF.md` first. No mathematical
review is claimed already completed. This request is for analysis and a decision
recommendation; it is not implementation or integration authorization.

The objective is a robust common ammonia thermodynamic foundation for future
evaporators, receivers, compressors and valves, using unchanged frozen samples
if they are sufficient. Do not specialize a correction to the 146-second event.

Examine, in this order:

1. `JOINT_PROPERTY_CONSISTENCY.md` and `STATIC_PROPERTY_RECONSTRUCTION.md`:
   source of the ~0.033-bar compressed-liquid error, stability and uniqueness failures.
2. `engine.js`, `properties.json`, `tools/generate_properties.py`, and
   `experiments/dx-fv/thermodynamics.cjs`: source coordinates, rounded h/s/rho/T,
   PH and canonical M/U/V pathways, units and reference conventions.
3. `static_property_reconstruction.py`: curvilinear Gibbs derivatives,
   Hermite first/second/mixed jets, bounded projection and joint-PCHIP comparator.
4. `static_property_qualification.py`, `static_property_diagnostics.py`,
   `audit_static_properties.py` and supplied compact/static root evidence:
   EOS methodology, masks, stability tests, numerical conditioning, root validation.
5. The phase/saturation/trajectory reports and research adapter for context;
   coupled model/solver sources show where properties influence physical evolution.

Please answer:

* Are Gibbs identities and all log-pressure/subcooling coordinate transformations
  correct? Do interpolation continuity and conditioning claims follow mathematically?
* Are source rounding intervals/correlated true-T coordinates handled correctly?
  Is the available first-jet information sufficient to establish existence of a
  stable consistent potential, or only compatible point values? What is missing?
* Why do exact-knot potentials and the rounding-bounded projection fail curvature,
  compressibility, cv and canonical uniqueness despite good energy values?
  Distinguish representation defects from inversion/bracketing failures.
* Is the current projection objective scientifically adequate? Its entropy-based
  edge weight scales are not rigorous integral bounds; h/rho knots stay fixed,
  and Hessian stability/coexistence are not constrained. Identify consequences.
* What constraints guarantee positive kappa/cp/cv and unique PH/MUV recovery on
  the intended stable liquid domain? What between-node certification is possible
  without claiming global results from finite collocation?
* Should a bounded constrained Gibbs fit, direct Helmholtz fit or another common
  potential be attempted first? Compare feasibility, conditioning, accuracy,
  implementation cost and regression risk. Monotonic field interpolation alone
  does not satisfy the Maxwell identity.
* How must the liquid fit meet saturation enthalpy/density/temperature and vapor
  coexistence/Clapeyron conditions without introducing contradictory definitions?
* Is the first-low-pressure-cell static feasibility experiment the smallest safe
  next step? Specify falsifiable pass/fail criteria and required evidence. If
  frozen data are insufficient, explain why before recommending new information.

Concrete counterexample: p=0.3029893712344606 bar, EOS 1 K subcooling;
original inventory rho=708.6710262223568 kg/m³, u=94.48059153610271 kJ/kg.
Original surface has three roots and negative compressibility; direct EOS gives
positive compressibility and p=0.301747903655 bar for that inventory. The projected
Gibbs fit has nine validated roots. The shape-preserving field comparator fixes
the sampled sign/root problem but violates Maxwell and fails broader pressure accuracy.

At the saved high-pressure endpoint, original / joint-PCHIP / projected
inventory-equivalent pressure errors are +3263.893 / +46.0055 / −131.818 Pa,
against an unchanged 10 Pa budget. All current candidates are rejected. Earlier
saturation-only PCHIP remains separately unqualified because liquid PH T regresses.

Preserve: frozen data, energy references, original equations/hydraulics/conductances,
Newton/TR-BDF2, all acceptance budgets (including strict 1 ms events), existing
defaults and the distinction between reported historical qualification and current
evidence availability. No new simulations, fit, code correction, tables, adoption,
commit, production changes or full qualification are requested in this review.

Deliver a mathematical critique, ranked alternatives and the smallest defensible
engineering decision. State unresolved assumptions and guarantees not established.
The user will approve the next action after reviewing your conclusions.
