# 🔧 Ammonia Lab — The Mechanic’s Report

**FOCUSED BROWSER GATE A PASS**

Three old liquid failures now recover correctly in both tested browser engines.
We rebuilt the same repair accepted in native C++, kept the exact original
conserved inventories, and watched the actual browser code take the repaired
route. Four near-endpoint cases remain unqualified.

## What was wrong with the liquid decision

The legacy DU flash starts with density and internal energy. Near saturation,
it first finds a saturation state at the imposed density, then compares the
requested energy with that state's energy to choose the next calculation.

The old saturation loop evaluated one point, calculated a Newton correction,
advanced its local coordinates, and stopped using the residual from the earlier
evaluation. Its stored saturated liquid/vapor states still described the earlier
point. The three liquids sit close enough to saturation that this small mismatch
reversed the caloric decision.

For inventory 146, the old comparison was about **−0.000050070 J/kg**. It sent
the calculation toward coexistence, which eventually refused an invalid quality.
The corrected comparison is about **+0.000042558 J/kg**, consistent with the
independent **+0.000042557 J/kg** separation. The existing homogeneous liquid
solver can then recover the requested inventory. Inputs are not nudged toward a
convenient solution.

Gate A waits for the accepted DU coordinate-polishing condition and stops at the
point it actually evaluated. Its final local coordinates, cached saturated
states and caloric decision refer to the same point. It keeps the imposed
density and the original iteration/retry limits. Generic Newton/Brent, ammonia
coefficients, the quality validator and support guard are untouched.

## What we proved in browser WASM

The default browser route uses superancillaries and bypasses this repair. Merely
getting a good answer on that route would prove very little about Gate A.

The isolated harness supplies CoolProp's existing full-VLE configuration through
its process-environment imports. It adds no thermodynamic export or new flash
equation. Browser traces show the legacy DU call entering saturation-D with the
candidate's opt-in enabled. Separately identified diagnostic binaries have exact
on/off/ordinary-result parity. The scientific binaries retain the exact accepted
three-file source repair.

Inventories **146, 151 and 152** return homogeneous liquid in Chromium and desktop
WebKit, matching the independently resolved phase and native A1. Their largest
pressure error against originating PH is about **0.000000628 Pa**; fresh-EOS
normalized mass/energy mismatch stays below **6.52e-16**. Original acceptance
limits remain unchanged. The 250-record ledger, separate 21 references, inherited
phase/precision/cache probes, rejected-PT lifecycle and bounded C1/A2 subset are
retained and checked.

## Why four endpoints are still on the bench

Inventories **148, 164 and 165** still fail the strict quality check. No state
exists after those refusals. Inventory **162** returns numerical liquid, but its
energy separation is around **2.33e-9 J/kg**, below the original **1e-8 J/kg**
phase-reference resolution. A small residual and a returned number cannot decide
that physical phase under the accepted contract.

Some mathematical coexistence roots are infinitesimally inside the vapor
endpoint. Forcing vapor or clipping quality to one could replace that equilibrium
with the wrong branch. Gate A does not solve this endpoint problem. The original
35-bar refusals and inward false-acceptance hazards also remain qualification
blockers; a raw pressure that looks supported is not a certificate about the
exact stored mass/energy/volume.

Additional DP endpoint probes also return raw qualities just outside [0,1] in
both builds. Those fail physical admissibility and are not accepted as states in
this qualification or fed into the model. They are another reason this result
qualifies only the three Gate A liquids, not the whole property interface.

## The browser also needs to put its tools away correctly

The B6 exception repair was checked again against every newly generated module.
The generated JS is byte-identical, and the actual WASM imports, signatures and
live ownership observations match. A native escape arrives without an acquired
catch reference. The loader restores the stack, enters the generated catch and
exits it once. It preserves the real property error and allows subsequent
supported requests. A JS-origin error receives no native cleanup.

This does not make the application ready for production. Main-thread
initialization/sampling showed timer gaps around **1.5–1.8 seconds**; worker
campaigns still showed gaps up to **77–94 ms**. Those need separate responsiveness
work. Desktop WebKit is not a physical Safari or iPad test. Full Gate B, backend
and A2 qualification are still open. The next step is engineering review of this
limited result, followed only by separately authorized scientific work.
