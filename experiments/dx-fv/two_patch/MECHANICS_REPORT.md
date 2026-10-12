# Mechanic's Report

**This design is stable, but it still gives the wrong liquid pressure. It is rejected.**

We tested only the two approved small regions. We left the original table,
application and accepted solver alone. One energy formula in each region now
keeps the thermodynamic quantities consistent. We also proved that the fitted
liquid stays physically stable between the table points, within those regions.
The reconstructed table points all stay inside their original rounding limits.

That repairs an important class of defects: each patch gives at most one state
for a supported stored mass, energy and volume. The old low-pressure example
still reproduces three answers with the original interpolator; this fit gives
one. But one answer can still be wrong.

Against direct CoolProp checks, the worst recovered pressure errors were about
**331 Pa and 6,018 Pa**, versus the required **less than 10 Pa**. A high-pressure
point well inside the patch still misses by about **5,048 Pa**. Some EOS states
cannot be recovered inside the candidate's small region at all. Good temperature
and enthalpy results on the successful cases do not compensate for those failures.

The measurements are much more precise than the failures. We froze the fitted
numbers before checking CoolProp and did not tune them afterward. The result
shows that stable fits are possible; it does not show that the frozen samples
can deliver the required pressure accuracy, or prove that they never could.

**Recommendation:** stop this construction here. The next decision should favor
a bounded study of an established EOS-backed browser design. No such design,
production change, longer simulation or new milestone has been started. All
previous research and Stage 2B remain unqualified. This branch is ready for review.
