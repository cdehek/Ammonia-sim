# 🔧 Ammonia Lab — The Mechanic’s Report

**ROOT CAUSE CONFIRMED. Several small numerical problems are involved.**

The ammonia model is not being asked to do something physically impossible in
the saved cases. We found stable liquid, vapor or equilibrium references for
the inventories. Very close endpoint labels remain uncertain at the original
reference resolution.

One failure is inside the native calculator. On the full-VLE route it uses a
saturation result from the previous iteration to decide which kind of state to
solve. For the resolved liquid failures, that small stale result puts the state
on the wrong side of the decision. It sends liquid into a mixture calculation.
The mixture calculation finds a mathematical answer with a negative vapor
fraction, which the calculator correctly refuses.

The vapor endpoint cases reach that same refusal with a vapor fraction a few
floating-point increments above one. The calculation has converged according
to its stopping rule, but its final result is not an admissible mixture. That
needs a physical recovery check, not permission to accept an impossible fraction.

The browser issue is different. Its property calculation returns an accurate
pressure, but the adapter refuses anything above exactly 35 bar. All seven saved
browser recoveries meet the original recovery accuracy limits. Two have a tiny
upward error that changes which side of the limit they appear on. Five already
have a microscopic mathematical pressure overshoot after the supported PH state
has been converted into rounded mass and energy. An even more accurate inverse
alone would not remove those five crossings.

The guard is doing what its comparison says. Its error label does not tell us
whether the plant physically left the operating range. We must preserve the
difference between an unsupported physical state, a rounded boundary inventory
and an inaccurate recovery. We did not round pressure down, widen the limit or
turn a failed recovery into a successful stop.

Both Chromium and desktop WebKit reproduce the saved browser failures. Native
8.0 instrumentation reproduces the uninstrumented results exactly. Historical
7.2 also shows quality-range failures, although its internals were not traced.
The separate browser rejected-PT cleanup defect did not interfere and was left
alone.

The next sensible job is a small native DU correction, reviewed and tested
against the same fixed inventories. Boundary representation and error
classification need their own subsequent review. No repair, new production
backend, model change or deployment has been made. Full A2 qualification still
has to pass before any integration can be considered.
