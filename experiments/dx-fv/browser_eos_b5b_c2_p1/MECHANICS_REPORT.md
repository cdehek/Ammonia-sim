# Mechanic’s report

**PARTIAL PHASE CERTIFICATION**

A pressure calculation can balance the ammonia’s stored mass and energy and
still describe the wrong phase. A liquid may be mathematically continued into
a region where an equilibrium liquid/vapor mixture is preferred. The equations
can converge neatly there. Positive heat capacity and compressibility tell us
that the answer behaves sensibly under small local changes; they do not tell
us that it is the equilibrium state the refrigeration model needs.

Think of a sealed section with fixed ammonia mass, volume and total internal
energy. We must recover the state from those quantities without changing them.
We cannot remove a small amount of energy, replace a density or snap a vapor
fraction to one just to obtain a convenient pressure. Those changes would solve
a different problem and break the conserved inventory.

This experiment checks two things that the previous local pressure proof did
not. It encloses the liquid and vapor endpoints with equal temperature,
pressure and chemical potential, and it checks where the original density
sits relative to them. The endpoint proof covers the whole possible root
temperature interval. A single saturation calculation at its midpoint would
not be enough.

For the two saved inward-recovery hazards, the exact stored inventories have
homogeneous EOS pressures slightly above 35 bar while the historical binary64
recoveries returned pressures slightly below it. The new proof places one
density beyond the local liquid endpoint and the other below the local vapor
endpoint. Trying to force those inventories into the nearby coexistence
solution gives a negative vapor fraction in one case and a fraction greater
than one in the other. Those are algebraic continuations, not physical mixtures.
We retain and reject them rather than clipping their qualities.

There is also a deliberately wrong-phase example. Its homogeneous root has
positive local derivatives and an enclosed pressure. A second proved state,
with the same stored mass, energy and volume, is a liquid/vapor mixture with
strictly greater entropy. In the bulk equilibrium model that is enough to rule
out the homogeneous answer. It demonstrates why proving that an answer exists
is weaker than proving that it is the right equilibrium answer.

What remains missing is a proof that the particular saturation branch found
here is the preferred equilibrium branch among every relevant alternative in
a defined operating region. The normal ammonia phase picture suggests it,
but this experiment does not prove that whole picture. The positive controls
therefore have rigorous local results, with full equilibrium qualification
still withheld. More calculator digits cannot supply the missing comparison.

Nothing changes in the simulator. The seven old refusals remain refusals.
The two old inward returns are not repaired by these offline calculations.
An unresolved calculation is not a proved plant-domain exit. A genuine
independently established exit remains protective, and rollback stays exact.

The tiny pressure separations are mathematical statements about the pinned
EOS and exact stored bits. They do not mean a transducer, a real ammonia charge
or the EOS’s experimental fit is accurate to a fraction of a micropascal.
They do not justify inventing a high-pressure trip. A real measured excursion
requires measurements and their uncertainty; a model-domain stop requires its
own independently established trajectory and direction evidence.

The next practical recommendation is to park broader certification work until
the phase-topology obligation receives an independent mathematical review,
and prioritize the separate rejected-PT loader defect under its own repair
scope. No loader repair or production change starts in this experiment.
Stop for explicit engineering review.
