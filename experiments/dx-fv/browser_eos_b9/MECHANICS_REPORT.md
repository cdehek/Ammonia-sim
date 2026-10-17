# Mechanic’s report

The five-section coil calculation can run in its own browser worker while keeping
the same refrigerant mass, internal energy and heat accounting in the tested runs.
The displays became substantially more responsive during calculations in both
desktop browsers. This is a useful architecture result, not a qualified plant
simulator or an approved operator-panel change.

A browser normally has one main thread attending to screen updates and operator
input. An ammonia property recovery and the coil solver can occupy that thread
while Newton tries pressures/enthalpies and the time integrator checks its trials.
During that calculation, a button press can wait and the screen can appear frozen.

The worker gives the calculation its own execution thread. It owns the refrigerant
inventories, tube and fin metal, finite air, trial calculations and accepted
records. The panel receives copies of completed accepted readings. It cannot
change inventory by rounding a displayed pressure or temperature. A stop request
waits for the current synchronous calculation to finish at its command boundary;
there is no claim that a Newton calculation can safely be cut in half.

Every tested section retained exactly the same mass, internal energy and volume
between the two modes in each browser. Tube, fin and air energies, inlet/outlet
flows, heat transfers, clocks and records also matched. Original conservation
checks passed. The trials cover only 0.001 simulated seconds from each original
cold/warm start; they do not prove indefinite refrigeration operation.

When a property calculation legitimately refuses, it remains a refusal. The model
retries with the original smaller time step. Persistent numerical refusal reaches
the original minimum-step rule and reports a numerical stop. It does not invent
a compressor trip or claim the plant crossed a physical boundary. Tests preserve
the last accepted inventory, metal/air energies and event clock exactly. Separate
200 K and 400 K outward-direction tests retain their independently proven thermal
domain stops. Those meanings must stay different for an operator.

During the measured physics, maximum panel heartbeat gaps fell from 196.8 to
30.3 ms in Chromium and from 187 to 39 ms in desktop WebKit. The calculation itself
was generally slower in the worker, and starting a worker costs more time.
Some input/frame stalls remain; desktop WebKit still showed a 354-ms frame gap.
The current full-diagnostic harness is not ready for workstation integration.

The experimental CoolProp backend is still NOT SCIENTIFICALLY QUALIFIED as a
complete backend. Three previously qualified liquid cases work in the worker,
but four endpoint cases, historical 35-bar refusals, two inward false-acceptance
hazards and phase/topology obligations remain. Invalid DP diagnostic states remain
refused and are not required by the accepted table model. A terminal bulk wet
indication is not proof of safe compressor suction. No production protection or
physical iPad validation is supplied by this research.

Continue isolated worker research only after review. Do not integrate or deploy
this harness as an operator workstation. Moving an incorrect property calculation
to another thread would only move the error; it would not correct the physics.
