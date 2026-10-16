# Repair proposals for engineering review — none implemented

The evidence supports separate native inverse and browser boundary work. These
are proposals, not accepted corrections or authorization to implement them.
Original failures remain in the delivered backend.

## B5A.1 — legacy saturation state and decision consistency

**Owner:** `src/Backends/Helmholtz/VLERoutines.cpp::saturation_D_pure` and its
`FlashRoutines.cpp::HSU_D_flash` consumer. The four inherited patches stay exact.

**Demonstrated mechanism:** three resolved subcooled-liquid examples and the hf
ULP example compare against a saturation substate left at the prior evaluated
iterate. Its ~9.26e-5 J/kg energy error reverses the resolved cases' phase decision.
The trace's advanced local coordinates closely match an independent fixed-density
saturation root, while the substate getter describes the earlier coordinates.
The stable homogeneous solver is bypassed.

**Conceptual alternatives:**

1. Complete saturation finalization at the actual converged coordinates, verify
   pressure/chemical-potential consistency and expose a truthful final state to
   the consumer. Review all callers because `saturation_D_pure` is shared.
2. If a shared change is too broad, make DU's legacy decision independently
   validate/refine its fixed-density saturation boundary before dispatch. Keep
   its actual input density/internal energy, physically stable branch and failure
   propagation. Do not hide uncertainty inside a negative-quality mixture.

Finalization alone must not be presumed sufficient: the solver's stopping norm
and the required caloric separation are different quantities. A fresh cache at
an insufficiently accurate coordinate can still misclassify a near endpoint.
The evidence justifies validation of the final decision, not a global tightening
of every CoolProp tolerance or a generic Brent rewrite.

**Physical/numerical justification:** at fixed positive density, the stable
homogeneous branch has positive cv and a physical u root. Its u position relative
to true saturation has the opposite sign from the current decision. A mixture
with Q<0 is an algebraic extrapolation, not an acceptable alternate root.

**Phase-boundary consequences:** correct dispatch must retain legitimate
coexistence, saturated endpoints, tiny supported subcooling/superheat and their
one-sided derivatives. It must not select a homogeneous root inside the dome or
infer phase from an uncertainty sign smaller than reference resolution.

**Domain-stop consequences:** unsupported inventories must still fail honestly;
no 35-bar rounding, support expansion or saturation-density substitution. This
change will not address all representational pressure crossings in B5B.

**Required independent tests:** every exact B5 fixed inventory, all seven original
exceptions, independent fixed-density saturation p/g equations, positive cv and
compressibility, actual final-coordinate getter/cache checks, both saturation
paths, fresh/reused states, multiple local reference seeds and native/browser
comparisons where the interface exposes them. Replay all B1/B4A/B4B/B4C focused
regressions with their unchanged signed perturbations. For a shared saturation
routine change, separately review affected pure/pseudopure fluids and callers.

**Acceptance:** no original failure omitted; stable same-inventory reference
agreement, independent p/h resolution 1e-5 Pa / 1e-8 J/kg where applicable,
canonical <=.1 Pa / <=.1 J/kg / <=1e-4 K, normalized original mass/energy <=1e-11,
standalone strictly <10 Pa / <50 J/kg / <.01 K, and preserved domain behavior.
No polished reference is substituted into an accepted backend result.

**Risks:** global saturation callers, last-iterate changes to endpoint values,
false phase flips where saturation uncertainty exceeds separation, performance,
critical/density-anomaly topology and altered exceptions after state reuse.
A local consumer correction can duplicate logic; a global correction has a
larger qualification obligation. Choose only after a pre-edit design review.

This belongs in **B5A**, with a separately reported saturation-decision gate.

## B5A.2 — physical acceptance of legacy two-phase DU roots

**Owner:** `FlashRoutines.cpp::HSU_D_flash_twophase` and the surrounding pure-fluid
`HSU_D_flash` phase dispatcher. The strict QT quality validator is correctly
refusing invalid Q and should remain protective.

**Demonstrated mechanism:** the quality residual converges on the captured
scaled-residual termination condition, then the code passes Q outside [0,1]
into QT. Resolved liquid inputs have a nonphysical negative-Q algebraic root;
vapor endpoint inputs overshoot Q=1 by about 2e-15. The exact source exception,
all residuals and actual stopping events are captured. This is distinct from
failure to converge because no root exists.

**Conceptual correction:** solve and accept only a thermodynamically admissible
branch. Validate both inventory inputs and saturation geometry at the final
coordinate. If the two-phase solve is outside its physical interval, determine
whether a supported homogeneous root exists through an independently justified
phase decision/bracket; otherwise expose numerical failure. Endpoint resolution
must preserve actual inventory to the original gates. A quality clamp or density
replacement alone cannot prove that it recovered the same mass/energy state.

**Justification and boundary effects:** positive stable caloric derivatives and
coexistence equilibrium define the admissible branches. The same numerical
residual can represent an extrapolated mixture outside the dome. A genuine
interior mixture must not be replaced by a homogeneous DT solution, even if that
solution converges. Stable vapor, liquid and endpoint approaches need separate
one-sided checks. Homogeneous Q=10000 is an existing sentinel, not a mixture.

**Domain-stop effects:** retain numerical failure separately from demonstrated
physical support exit. Do not convert a failed inversion into an accepted stop
or enlarge the supported pressure/temperature range. No generic solver stopping
change is justified solely by these endpoint examples.

**Independent tests and gates:** all seven original C cases and the full 73-pair
cross-path ledger, perturbed endpoint inventories, independent equilibrium p/g
and volume/energy equations, true saturation at the actual internal molar inputs,
physical root stability, raw final getters, fresh/reused states and instrumented
parity. Retain all B5A.1 canonical/nonlinear/standalone limits and original FDs.
The two current endpoint-equilibrium roots below Q=1 must recover their own
inventories; the homogeneous-side endpoint neighbor remains separately labeled
unresolved at the original reference resolution.

**Risks:** inventing a fallback that returns a metastable root, hiding an actual
out-of-support inventory, incorrect endpoint density, reference-frame conversion
rounding, shared H/S/U callers and different native/WASM last bits. A fast-path
success is evidence for a physical root, not permission to switch every failing
full-VLE input to a different algorithm without qualification.

This is a **distinct gate within B5A**, with its own before/after evidence. It
must not be represented as automatically fixed by B5A.1.

## B5B — numerical boundary classification and representability policy

**Owner:** research `browser_eos_backend/adapter.mjs::stateMVU`, `convert`, `sat`,
and, only under a separately approved interface design, the accepted caller's
classification of numerical recovery failure versus physical-domain exit.
The table engine and its existing bracketing epsilon are not the rejecting
owner in the original seven cases.

**Demonstrated mechanism:** the raw recovery passes canonical budgets, the table
PH guard passes, then strict `sat(p_bar)` throws `faultKind:'domain'`. Two exact
fixed inventories are below the same-EOS boundary while their numerical DU
outputs are above it. Five are microscopically above after PH and binary64
construction, even with an exact recovery. Unit conversion preserves the guard
side for all original seven. All originate from supported requested PH states.

**Narrowest conceptual option:** preserve refusal, but distinguish a numerically
unresolved boundary recovery from a positively demonstrated physical-domain
exit. Return/retain diagnostic provenance and a numerical-failure classification
when the evidence supports it. This improves scientific interpretation without
claiming a successful accepted recovery. It requires a concrete, reviewable
policy for proving an actual domain exit and handling unresolved cases.

**Further option requiring explicit scientific contract review:** define how an
exact supported PH boundary request and its necessarily rounded conservative
inventory are represented together. Any accepted recovery must report actual
EOS coordinates, demonstrate the original inventory and canonical budgets,
and preserve true unsupported-state rejection. Neither using the previous
pressure guess nor matching an input name is an adequate support certificate.
The existing stateMVU interface does not carry complete originating PH
provenance. A new certificate/interface, if justified, must be explicit and
separately reviewed; B5 does not select one.

An accurate DU improvement can fix a wrong-side numerical recovery. It cannot
make an exact inventory whose mathematical EOS pressure is above the strict
limit simultaneously have that same exact inventory and pressure <=35 bar.
If every existing requirement is retained literally, such a case may have to
remain a failed boundary recovery. That conflict must be surfaced, not solved
with a hidden epsilon, down-rounding, input echo, widened maximum or false pass.

**Physical/numerical justification:** canonical agreement to .1 Pa and strict
side-of-boundary agreement are different tests. EOS numerical uncertainty,
mathematical root residual and experimental EOS accuracy are different scales.
The fixed inventory's mathematical sign is informative about arithmetic; it is
not proof of an operational pressure excursion at nanopa precision.

**Phase/domain consequences:** apply the policy consistently to stable liquid,
vapor, saturated endpoints and equilibrium mixture. Preserve the temperature
floor, subcooling/superheat bounds, lower pressure limit and all accepted domain-
stop/rollback behavior. A non-boundary numerical failure still fails. A genuinely
unsupported physical state still stops. A crossing input one ULP above the
maximum must not acquire a passing requested-PH classification through rounding.

**Required tests:** the seven original browser cases in both engines, 73 fixed
pairs, raw-before-guard capture, exact/nextafter pressures, Pa/bar round trips,
independent same-inventory stable roots, newly rounded reference inventories,
actual physical exits farther outside the envelope, and all original A2 domain
proof/rollback fixtures. Test both signs of boundary error: false rejection
and false acceptance of a numerically shifted unsupported inventory.

**Acceptance and risks:** preserve all B5A scientific gates and original domain
limits. New classifications must never count a failed inversion as a successful
domain stop or passing recovery. Risks include masking EOS error, accepting true
unsupported states, invalid provenance, phase-dependent special cases, changing
trial rejection/step-halving behavior and mistaking a local test for complete
solver qualification. No policy is accepted in this report.

This must be **B5B**, separate from the native correction and separate from the
known rejected-PT loader lifecycle defect. A classification-only B5B is not a
claim that complete exact-boundary backend qualification passes.

## Gates before future complete A2 qualification

After independently reviewed corrections, require the original focused property,
canonical, nonlinear, phase and conservation gates first. Preserve source/data,
fixtures, original perturbations and budgets. Keep reference construction and
accepted backend inventories separate. Verify native/WASM provenance and
instrumented/production equivalence for any proposed functional candidate.

Then run the **complete original accepted five-section A2** suite, with its
accepted dependency closure and checks, rather than a new easier campaign:

1. All accepted options, controllers and Jacobian configurations required by the
   original matrix; original Newton 30, line searches, residual scales and
   TR-BDF2. No new tolerances or perturbation sizes.
2. Canonical and zero-exchange trials at supported liquid, mixture and vapor,
   all original near-boundary regressions, exact inventory preservation and
   independent EOS/phase references.
3. Original temporal/refinement and frozen independent direct-EOS trajectory
   comparisons, unchanged reference files and complete event identity/time
   requirements. Pressure <10 Pa, h <50 J/kg and original thermal/event gates
   remain necessary, not substitutes for local nonlinear consistency.
4. Every aggregate and per-section mass ledger <1e-8 kg and energy ledger
   <1e-6 kJ; original normalized fluid <=1e-11 and thermal <=1e-12 K requirements.
5. Domain proof, genuine domain exits, rejection/halving floors, rollback,
   retained stops, boundary edits, reversal and long-duration supported runs.
   A numerical property error must not be mislabeled physical domain evidence.
6. Chromium/WebKit complete operating/reference coverage, memory/offline/worker
   behavior, and separately physical Safari/iPadOS validation. Desktop WPE is
   insufficient for a physical-device claim.
7. Any shared CoolProp source consequences beyond this ammonia envelope, with
   broader review proportionate to the source owner. Preserve all four inherited
   corrections and rejected-PT failures until their separate lifecycle milestone.

Only a complete passing campaign under the original contract can justify later
backend qualification. Production selection, UI/Live Plant work, merge and
hosting/deployment require separate explicit authorization. **Stop here.**
