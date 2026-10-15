# 🔧 Ammonia Lab — The Mechanic’s Report

The property calculator sometimes calls perfectly good liquid ammonia “liquid
and vapor” just before it reaches its boiling point. The saved case is liquid
at about 0.303 bar absolute. We checked that against the actual ammonia equation
of state and found a stable liquid solution at the pressure and heat content
the laboratory asked for.

The cause is now visible in an execution trace. CoolProp calculates a tiny
**negative vapor fraction**, roughly minus seven parts in ten billion. Its
phase-selection rule allows that number into the boiling-mixture calculation.
That calculation works for real liquid/vapor mixtures, but extending it to a
negative amount of vapor gives the wrong volume and density for liquid.

A tiny fraction can matter here because vapor occupies much more space than
the same mass of liquid. The returned density is only about 0.001214 kg/m³ too
high, but liquid is hard to compress. Checking that density and temperature
against the EOS raises the pressure by about **2,870 Pa** above the request.

The inventory check then uses the returned density with the pressure and heat
content originally requested. Those numbers no longer describe one consistent
physical state. Recovering the supplied mass and energy gives a pressure about
**4,245 Pa higher** than the requested pressure. The accepted model permits only
**0.1 Pa** difference, so it correctly refuses the result.

We tested the distinction directly. An inventory built from the independently
calculated physical liquid recovers within the original limits. An inventory
built from the faulty PH density recovers the different state implied by that
inventory. For this counterexample, the large extra pressure movement does not
show that the inventory recovery itself is broken.

This happens at ordinary refrigeration pressures too. Near the liquid boundary,
the tested 3.5-bar and 8-bar cases move about 274 Pa and 95 Pa on recovery. At
35 bar, a diagnostic just inside the same bad quality band moves about 8 Pa.
There are also successful boundary results. The problem depends on the state
and the selected calculation path; these tests do not certify every condition.

There is a second, smaller vapor problem. Think of finishing a calculation with
the density from the latest worksheet but some thermodynamic values from the
previous worksheet. The source trace shows exactly that mismatch between the
final density and cached derivatives. It is separate from the negative vapor
fraction problem and needs its own repair and checks.

CoolProp 7.2 also fails to recover some valid 35-bar liquid inventories. Small
numerical recovery overshoots can separately trip the accepted support guard.
Those findings remain visible; neither should be folded into the first fault
without evidence.

**Finding: ROOT CAUSE CONFIRMED.** This is a diagnosis, not a repair. We changed
no ammonia data, model equations, solver settings, inventory accounting or
production backend. The proposed repair work and its acceptance gates are in
[REPAIR_PROPOSALS.md](REPAIR_PROPOSALS.md). Engineering review and explicit
approval are required before corrective B4 work begins.
