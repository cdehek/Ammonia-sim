# 🔧 Ammonia Lab — The Mechanic’s Report

**FOCUSED REPAIR PASS. Full backend qualification remains pending.**

The saved liquid ammonia fault is repaired in a separate experimental property
calculator. The calculator now recognizes that the requested heat content is
below the boiling boundary and solves for the actual liquid temperature and
density. It no longer invents a negative amount of vapor and runs that through
the liquid/vapor volume calculation.

At the original pressure and heat content, the repaired result is liquid at
218.26293702735882 K and 707.4983265879039 kg/m³ in both browser engines.
Checking those coordinates independently against the ammonia equation of state
gives a pressure error of about 0.000000081 Pa.

The mass-and-energy recovery check is the important practical result. The old
PH result recovered about **4,245 Pa too high**. The repaired result misses by
about **0.000431 Pa**, safely inside the original **0.1 Pa** allowance. Its heat
content and temperature also pass their original limits. We did not change the
pressure request, mass, energy balance, solver settings or acceptance limits.

We kept three inventories separate: an independent physical liquid reference,
the old faulty calculator output and the new repaired output. The new one agrees
with the physical reference. The old inventory still recovers its old higher
pressure, as it should; its history has not been rewritten.

The original liquid initialization trial that failed in B2 now succeeds in both
Chromium and desktop WebKit. Short cold, warm, feed-change and heat-reversal
checks also pass the original five-section model's scientific assertions.
The earlier B1 precision improvement is preserved. Real boiling mixtures retain
their original behavior, and genuine boiling-boundary crossings are not treated
as failed smooth liquid derivatives.

There is a cost: the saved near-boiling liquid state now takes roughly ten to
twelve times as long to calculate because it solves the real liquid problem
instead of using the wrong shortcut. The mixed boundary workload is about
20–44% slower in the two browser observations. Observed WASM memory is unchanged.

There are still separate faults to review. The saved vapor cache mismatch is
unchanged and remains a failure. The upper vapor-quality tolerance band still
admits some invalid extrapolations. Some 35-bar inventory recoveries still
throw or overshoot the strict support guard; fixed-input comparisons show these
same failures in the unchanged control. None is hidden or called repaired.

This is a focused liquid repair, not approval of the whole property backend.
No production calculator, UI, Live Plant, ammonia coefficients or accepted model
equations were changed. No full qualification matrix, actual iPad test, merge,
deployment or next vapor repair has been performed.

The isolated research branch, exact patch, binaries, measurements and reproduction
instructions are ready for engineering review. Further work requires explicit
approval.
