# Mechanic's Report

**The browser EOS still needs a precision fix before it can be considered for the
accepted simulator.** Its ammonia equations behave consistently when we give them
density and temperature. The pressure/enthalpy flash sometimes stops a little early.
The leftover error is tiny for a single property reading, but large compared with
the solver's very small pressure probe. The saved browser probe consequently looks
about **20 times too steep**.

New state objects, different call order, molar inputs and liquid-phase flags do not
fix it. Native 8.0.0 also shows related failures nearby. The official source relaxed
the PH stopping rule substantially between 7.2 and 8.0; the evidence strongly points
there, though we cannot inspect the final bracket inside the shipped browser binary.

The accepted Newton routine failed two small synthetic inventory tests with the
8.0 interface that preserves requested enthalpy. Returning the flash's actual
enthalpy passed those small tests, but left the wrong derivative. That is not a
solution or a coupled-model pass. Version 7.2 behaved better in these tests, but
its shipped browser interface is much slower.

The iPad test ZIP is ready, with both official versions, a worker, offline assets
and evidence export. It passed desktop Chromium/WebKit readiness checks. **No
physical iPad has been tested.** No website was published.

Keep the accepted simulator as it is. The best next decision is whether to authorize
a traceable EOS build with a stricter flash stopping rule and efficient state APIs,
then test that build and the pinned official versions on a physical iPad. This study
does not authorize that build, a property migration, or weaker solver tolerances.
