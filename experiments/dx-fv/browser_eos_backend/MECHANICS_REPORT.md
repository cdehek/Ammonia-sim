# 🔧 Ammonia Lab — The Mechanic’s Report

**PROMISING — the precision fix works in the tests, but it is not ready for the
working plant simulator.**

The problem was in how far the browser property calculation followed its search
for the refrigerant state. When we asked for a tiny pressure change, it sometimes
stopped with a slightly different heat-content error. That error was small in
ordinary engineering units, but large compared with the tiny density change our
solver was trying to measure. The liquid appeared about 20 times too responsive.

We built the same CoolProp source two ways. One kept the original stopping rule;
the other made that search more precise. We did not change ammonia's property
equations, adjust reported density, or loosen the simulator's tolerances. The
original setting reproduced the fault. The tighter setting brought the pressure
response back close to the EOS's own calculated response in both desktop browsers.
A second complete compilation produced exactly the same experimental binary.

We then checked the mass-and-energy solver. The tighter build passed the small
inventory checks and completed the five-section cold, warm, load-change,
feed-change and heat-reversal cases at all three original accuracy settings in
Chromium and WebKit. Independent checks found the mass and energy books balanced
within the existing limits. Rejected trial steps stayed rejected.

There is still work to do. One vapor state very close to saturation retains a
small heat-content mismatch. We have not qualified every operating corner,
every safety/rollback check, or long-running simulations. A desktop WebKit result
does not tell us how a real iPad handles memory, battery or heat. An isolated test
package is ready for that physical device test; no iPad result has been claimed.

The tested route is worth pursuing. It is not permission to fit it to Live Plant.
The application, equipment controls, UI and production engines remain untouched.
Engineering review and explicit approval come next; nothing is merged or deployed.
