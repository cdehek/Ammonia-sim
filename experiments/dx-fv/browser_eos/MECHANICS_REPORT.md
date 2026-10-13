# Mechanic's Report

**A real ammonia EOS runs locally in the browser. It is promising, but it is not
ready to replace our simulator's property engine.**

We tested official CoolProp builds in Chromium and desktop WebKit. The newer
8.0.0 build supplies all the main state calculations we need. It finds the EOS
answer for the old liquid inventories without using the table surface that
produced extra roots and large pressure errors. Browser answers agree closely
with matching Python CoolProp. That verifies the implementation against the
same formulation; it is not a real-world ammonia experiment.

The useful design keeps one EOS state alive in a worker and reuses exact answers
when the inputs have not changed. That keeps calculations local, can work offline
from cached assets, and leaves the page responsive. Startup takes roughly two
seconds on this desktop host. The EOS reserves about 54 MiB of WebAssembly memory.
Returning several properties after one state calculation is much faster than
asking the string API to repeat the calculation for each property.

Pressure/enthalpy recovery is slower than the current table in single-phase
states, while direct mass/energy recovery is faster in the measured examples.
Exact caching helps repeated solver calls, but does not make multi-hour plant
runs automatically fast. Under the stated desktop assumptions, nine-section
property work alone could take about two to sixteen minutes per simulated hour;
existing difficult nonlinear cases can cost much more. Actual iPad speed and
memory behavior remain untested.

We also found a problem that ordinary accuracy checks missed: one tiny pressure
probe used by our unchanged solver gives a density slope about twenty times the
EOS's analytic slope in the 8.0.0 browser build. The liquid itself is stable;
flash convergence accuracy is affecting the numerical difference. We kept that
evidence and did not change the solver steps or tolerances.

**Recommendation:** retain the current accepted engine for now. Approve a focused
study of EOS flash precision and unchanged-solver compatibility, plus testing on
a real iPad, before deciding on migration. The preferred future architecture is
a persistent EOS in a worker with exact caching. This research branch contains
no replacement, coupled integration, production change or new qualification.
