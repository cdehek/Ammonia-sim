# Mechanic’s report

The computer repeatedly works out temperature, density, phase and wet/superheat
indications from the imposed inlet and outlet pressure and enthalpy. Even a table
lookup can require a bounded inverse calculation, especially at the superheated
outlet. Newton asks for many slightly perturbed section states while finding one
acceptable numerical stage, but those two imposed boundary conditions stay fixed.

This prototype retains each boundary's first successful result for that one stage.
When inlet/outlet pressure or enthalpy changes, the original validation and property
calculation run again. New stages, retries, patches and workers have new slots.
It does not freeze the refrigerant in the five evaporator sections: their mass,
energy, pressure, enthalpy and heat/flow responses continue through the original
finite-volume solver and its original checks.

Real property work fell by 5,720 cold / 15,180 warm PH evaluations, in both tested
browsers. All tested refrigerant inventories, thermal energies, flows, temperatures,
solver decisions and conservation results stayed bit-exact. Numerical refusals
remain refusals with the original rollback; genuine outward 200/400 K stops keep
their original meaning. Nothing invents a compressor trip or dry-suction assurance.

Measured performance improvement: **YES** for these tiny startup workloads;
the actual matched times and variability are in BROWSER_PERFORMANCE_MATRIX.md.
This does not establish sustained real-time operation or physical-device speed.
CoolProp has a different implementation, ownership and failure contract, so the
table purity proof cannot be transferred to it. No CoolProp repair was performed.
This research harness is **not ready for operator use**. Operator integration
remains NO-GO, and the prototype requires engineering review before any separately
authorized next step. It is not merged or deployed.
