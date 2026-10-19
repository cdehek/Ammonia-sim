# Accepted source to instrument contract

All readings refer to the snapshot's accepted `record.seconds`, never wall-clock animation. See unchanged B9D FIELD_AND_UNITS_MAPPING.md for the audited comparison with original plant semantics. No original plant gauge is overwritten.

| Panel field | Original accepted source | Units / display |
|---|---|---|
| Section 1–5 pressure | record.sections[i].p | bar absolute; optional psig=(p−1.01325)×14.503773773 |
| Section refrigerant temperature | record.sections[i].T | °C; optional °F=1.8×C+32 |
| Section refrigerant M/U/V | worker state.cells[i].massKg/internalEnergyKJ/volumeM3 | kg / kJ / m³; no reconstruction |
| Enthalpy | record.sections[i].h | kJ/kg, distinct from total internal energy |
| Phase / quality / bulk wet | record.sections[i].phase/x/wet | original string / dimensionless nullable fraction / Boolean |
| Bulk superheat | record.sections[i].superheatK | K difference; °F difference=1.8×K |
| Tube/fin/finite-air nodes | record.nodes[i].temperatureK/energyKJ | K (optional C/F) / kJ |
| Signed inlet / outlet | record.fluxes.faces[0/5].massKgS/energyKW | kg/s / kW, positive inlet→outlet; instantaneous endpoint |
| Tube→refrigerant heat | record.fluxes.tubeRefrigerant[i] | kW; sum explicitly labeled five-section heat summary |
| Coil refrigerant totals | record.totals.massKg/internalEnergyKJ | kg / kJ; not plant charge |
| Mass closure | record.massResidualKg | kg, original budget unchanged |
| Refrigerant / thermal / combined closure | corresponding record.*EnergyResidualKJ | kJ, original budgets unchanged |
| Integrated boundary / air loads | record.ledger.boundaryMassKg/boundaryEnthalpyKJ/airLoadKJ | kg / kJ / kJ |
| Accepted clock / version | record.seconds / bridge acceptedVersion | seconds, sufficient precision for .0001 s |
| Latest accepted interval | state.trace.at(-1) | original start/end/trial seconds and error, null at initialization |
| Next proposal / accepted step counts | state.nextStepSeconds / record.acceptedSteps/rejectedSteps | original adaptive proposal and counters |

Display units are panel-local and cannot write worker scientific state or original workstation units. Every rendered reading retains a source path and conversion identifier for exact source-to-render checks. Null quality stays unavailable; negative psig remains negative. Bulk wet does not establish compressor suction protection. Finite coil air is not the original connected room.

Compressor suction/discharge, compressor state/performance/protection, condenser, receiver inventories/levels, feed-valve actuator and whole-plant charge/balance are **unavailable** in A2. No defaults, inferred equipment measurements, phase clamps, pressure epsilon or plant coupling are permitted. Original workstation instruments remain powered by their original illustrative circuit.
