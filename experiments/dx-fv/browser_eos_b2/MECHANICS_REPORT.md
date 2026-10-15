# 🔧 Ammonia Lab — The Mechanic’s Report

**The 44-bit backend is BLOCKED from full qualification.**

B1 repaired a real precision fault. B2 found another problem right at the liquid
side of boiling. Ask for a valid liquid state just below saturation, and the
backend can return an impossible negative vapor quality. Its pressure gauge and
its density/temperature calculation then disagree.

At a preserved test point, converting those properties into the model’s stored
mass and energy and recovering them moves pressure by about **4,245 Pa**. The
accepted allowance is **0.1 Pa**. Chromium and WebKit show the same failure. The unchanged coupled model also rejects a sealed, zero-exchange trial at the
problem point and preserves the state exactly. This
is a property calculation problem, not a demand that derivatives stay smooth
through boiling, and not a reason to loosen the evaporator solver.
The same liquid-side problem also appears at an ordinary 3.5 bar, where the
pressure recovery shifts by about 274 Pa.

The smaller vapor error also remains. Source inspection and independent native
calculations strongly identify cached inner-density properties as a separate
problem from the bracket precision that B1 repaired. The browser property getters
can look accurate while a fresh calculation at the same density and temperature
reveals the error.

All 18 selected scientific test groups pass in each browser. The five normal
operating fixtures pass all three tolerance settings and their step refinement.
Independent mass and energy checks pass. The 892 captured rejected trials restore
their original physical state exactly. These successes do not erase the liquid
counterexample or complete the remaining configuration/reference matrix.

The accepted boundary
suite also reaches 33 successful cases in each tested A2 configuration before
three hot-refrigerant cases need an adapter function called `statePT` that B1
does not supply. Those blocked results stay in the record. A separate B2-only
mapping using the existing PT flash then passes all 36 cases in both tested A2
configurations and both browsers. That interface improvement does not repair the
liquid-boundary fault.

The next job is engineering review of these exact failures, followed by separately
authorized backend repair/instrumentation and a complete rerun of the original
scientific gates. No new EOS patch has been made. Longer operating runs and an
actual iPad test remain gated. An intentionally wet outlet is an ordinary model
result; it is not treated as a failed test.

The matched short tests use 53.75 MiB of WASM memory; that is not the whole
browser or iPad footprint. Chromium passes the offline checks. WebKit runs from
its cache with the origin disabled, but the separate offline-context test fails
at navigation. That failure stays open, and desktop WebKit cannot qualify an iPad.

All production, UI, B1 artifacts and accepted A2 physics remain preserved. Nothing
is merged, deployed, connected to Live Plant or published to Cloudflare.
