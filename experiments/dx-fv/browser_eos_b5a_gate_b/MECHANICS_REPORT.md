# 🔧 Ammonia Lab — The Mechanic’s Report

**CONDITIONALLY FEASIBLE**

The four remaining inventories do have solutions in the unchanged mathematical
ammonia model. We recovered them with higher-precision calculations while
holding the original density and energy fixed. Two are just inside boiling
coexistence, one is just on the vapor side, and one is just on the liquid side.

Those distinctions are smaller than the original independent reference can
qualify. Extra arithmetic digits reveal the model's mathematical signs; they
do not turn those signs into independently established physical phase certainty.

The ordinary-precision prototype handles the equations more carefully, but it
still cannot reliably tell which side of the endpoint it has reached. It can
pass the original residual checks and select the wrong branch. Tightening the
iteration stop does not consistently solve that problem. The three vapor QT
exceptions remain, and the returning liquid case remains scientifically unresolved.

The three liquids repaired by Gate A still work. We also kept every neighboring
failure in the evidence. No mass or energy was adjusted, no quality was clipped,
and no endpoint was substituted. The accepted solver and backend are untouched.

The useful next design is an equilibrium recovery with explicit branch checks
and defensible numerical error bounds. When those checks cannot settle the
phase, it must preserve the uncertainty. A functional repair and its acceptance
policy need separate engineering review and explicit approval. This research
does not qualify a browser backend or authorize plant integration.
