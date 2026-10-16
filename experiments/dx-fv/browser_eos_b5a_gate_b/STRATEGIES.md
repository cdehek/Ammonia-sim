# Engineering comparison and future design gates

Every candidate below retains original d/u. No candidate may use a preferred
pressure, modified endpoint inventory, quality clamp, enlarged support, or a
metastable root merely to remove the exception.

| Strategy | Physical validity and conservation | Conditioning, binary64, exact endpoints | Branch/metastability risk | Cost and portability | Source/caller interaction and regression risk | Verification required |
|---|---|---|---|---|---|---|
| Current Gate A plus legacy quality Brent | Strict QT refusal protects quality; original three liquid controls recover; four endpoints remain unresolved | Quality-difference stop meets residual test while Q exceeds 1; endpoint sign below reference resolution | Equality dispatch can choose coexistence for mathematical vapor; no justified fallback | Native measured, inherited WASM binding does not expose this full-VLE path | Preserve all existing source paths and failures; H/S/U untouched | Current reproduction is a control, not a proposed repair |
| Endpoint-centered coupled equilibrium solve | Enforces p/g, volume and u jointly; accepts genuine coexistence only with physical fractions | Demonstrated high-precision roots; float64 quality sign depends on seed/stop; Q=0/1 still needs certification | Separate stable homogeneous validation is essential; local derivatives alone insufficient | Two DT evaluations and dense 3x3 solve per iteration; Python median 0.816 ms across mixed stopping policies; C++/WASM cost unmeasured | Future DU-specific design could avoid altering H/S callers; common VLE routines require separate review | Error bounds, four exact inventories, neighbors, original gates, native and candidate WASM parity |
| Physically bracketed saturation-T/quality solve | Volume determines quality; energy root must stay within [0,1]; exact inventory preserved | No physical adjacent-temperature sign bracket established for four cases; endpoint resolution limits scalar QT approach | Enforcing interval prevents extrapolation but may honestly refuse; scalar convergence does not prove global stability | Repeated saturation solves; likely more EOS work; no new browser measurements | Would interact with legacy two-phase DU and QT; shared H/S/U consequences must be isolated/reviewed | Certify feasible T interval, p/g accuracy, endpoint residual signs and original acceptance at actual inputs |
| Stable homogeneous recovery after independent phase proof | Correct for mathematical 162 liquid and 165 vapor; conserves original rho/u; invalid for 148/164 | Native liquid return reproducible; vapor/liquid saturation sign can be below reference resolution | Unconditional fallback would accept inside-dome algebraic roots for 148/164 | cv Newton is cheap and portable; measured native roots only, no browser implementation | Narrow DU dispatch possible only with defensible phase proof; no generic H/S/U fallback justified | Positive cv/cp/p_r, stable side of saturation, independent resolved root, exact inventory and cache checks |
| Higher-precision or compensated EOS and coupled recovery | Mathematical branch validated here; no physical certainty beyond original reference resolution | 65/90-digit convergence demonstrated; compensated binary64/double-double and interval certification NOT implemented | Can resolve mathematical signs; original reference uncertainty remains | Python equilibrium median 0.170 s, 2–3 Newton steps in local seeds; not a native/WASM benchmark; extra arithmetic/portability cost unknown | Separate evaluated EOS kernel would be substantial source work; reference convention and other H/S/U callers need verification | Error analysis and cross-runtime coefficient/operation parity, limits, performance, then full original contracts |
| Explicit numerical uncertainty classification | Truthful refusal when phase cannot be resolved; does not recover a state | Can represent the observed uncertainty without inventing a tolerance; no accepted policy defined here | Prevents unjustified homogeneous or endpoint choice | Small policy overhead expected, unmeasured | Caller/domain lifecycle implications require separate scientific review; must not masquerade as B5B or loader repair | Specify error-bound provenance; keep numerical failure distinct from domain exit and successful recovery |

The most defensible future design is an endpoint-centered equilibrium method
with explicit stable-branch checks and a truthful unresolved outcome when its
error bounds cannot establish physical quality. Current evidence supports that
design research; it does not establish an ordinary-binary64 functional repair
meeting the original independently resolved phase contract.

Before separately authorized functional Gate B work:

1. Review equations and uncertainty evidence. Establish how native/WASM endpoint
   evaluations can certify the original inventories. A tighter iteration stop
   alone is insufficient. Do not derive a new tolerance from these observed errors.
2. Keep the Gate A patch and all B1/B4 corrections exact. Any future DU-specific
   source change needs a pre-edit design and isolated branch. Preserve strict QT
   validation, exact mass/molar conversion, input inventory, and final caches.
3. Require all seven original cases individually, fixed-input independent roots,
   p/g and volume/u closure, correct stable/coexistence branch, physical quality,
   all original canonical/nonlinear/standalone/reference limits and perturbations.
   An unresolved independent phase remains unresolved, even if a number returns.
4. Include true endpoint, deeper coexistence, stable liquid/vapor, one-sided
   boiling behavior, critical/pseudopure/shared-caller risks in proportion to
   source scope, failure propagation, fresh/reused parity and B1/B4 regressions.
5. Build and measure the actual candidate native and WASM interfaces, with
   source/binary provenance and Chromium/WebKit evidence. Preserve all seven B5B
   guard rejections and the rejected-PT loader defect for separate milestones.
6. Only after the essential property gates pass may separately authorized A2
   qualification run the original full suite and accepted numerical contracts.

No such functional change, policy change, qualification, merge or deployment is
part of this research delivery. Engineering review and explicit approval are
required before starting it.
