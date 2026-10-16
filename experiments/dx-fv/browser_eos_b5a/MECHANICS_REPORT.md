# 🔧 Ammonia Lab — The Mechanic’s Report

**PARTIAL REPAIR**

We fixed the demonstrated wrong decision for three valid liquid inventories.
The calculator had advanced its saturation calculation but was using properties
from the previous iteration to decide whether to solve liquid or mixture.
It sent those liquids into a mixture calculation, which then produced a negative
vapor fraction and correctly failed its quality check.

The experimental repair makes that DU decision use one consistent, sufficiently
refined saturation state. The original density and energy are unchanged. All
three resolved liquids now recover as stable liquid and satisfy the original
accuracy and energy checks. The earlier four backend corrections remain intact.

The tiny endpoint cases are still a separate problem. Three vapor examples
still calculate a fraction just above one and are refused. A fourth, near the
liquid endpoint, now returns a number but remains too close to the boundary for
the original reference checks to certify its physical phase. We have not called
that a physical success.

We did not trim a fraction to fit, replace an inventory with a saturated one,
force a vapor/liquid answer or weaken the validator. Two mathematical endpoint
references are equilibrium mixtures, so a blanket single-phase fallback would
be wrong. No defensible Gate B recovery was established under the unchanged
contract, and no Gate B source patch was made.

Native focused regressions pass their applicable checks. The browser candidate
and coupled five-section trials were not run after that scientific blocker.
The separate 35-bar browser guard issue and rejected-PT loader defect remain.
All original failures and exact inventories are retained for review.

This is an experimental partial repair, not a qualified backend or production
change. The accepted five-section model, UI, Live Plant and hosting are unchanged.
Work stops here for engineering review and explicit approval.
