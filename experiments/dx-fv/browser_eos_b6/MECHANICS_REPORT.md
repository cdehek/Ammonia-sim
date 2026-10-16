# Mechanic's report

**FOCUSED LOADER REPAIR PASS**

A property calculation can legitimately refuse a pressure and temperature very
close to ammonia's boiling line. Those two readings do not reliably select the
required liquid/vapor state there. The laboratory must report that property
fault; it must not invent a vapor fraction, move the pressure or temperature,
or pretend that it obtained usable refrigerant properties.

The separate computer fault happened while handling that refusal. The browser
tried to return an exception reference that it had never acquired. The runtime
then asserted, covering up the useful saturation-pressure explanation with a
software cleanup fault. It also left exception bookkeeping behind. A later good
calculation sometimes still worked, which did not make that handling correct.

The isolated repair enters and finishes the runtime's existing exception catch
properly. It releases the fault's allocation once, clears the bookkeeping,
keeps the original property-fault message, and allows the next supported update
to establish its state normally. Real Chromium and desktop WebKit tests preserve
all six original refusals while removing their secondary cleanup assertions.
Supported calculations retain their original results. The repair never resets
the fluid state behind the operator's back.

This fixes the laboratory software's handling of a bad calculation. It does not
change ammonia's rules or certify the plant model. The seven 35-bar research
refusals, two exact-inventory acceptance hazards, unresolved saturation endpoints
and phase-proof limits remain. A numerical property fault does not by itself
prove that a compressor or evaporator physically crossed a pressure limit.
No production controls, trips, operator workstation, Live Plant or physical iPad
were changed or qualified. Engineering review is the next step.
