# Cache scope and invalidation

One actual solveStage call owns two lazy slots, separately from its section Map.
Exact Object.is(p,h) checks preserve original numbers, including signed zero.
Only successful original PH+SAT+validation results enter slots. Property failure
clears both. Input mismatch invalidates its slot before original evaluation.
No object is retained by returned stage data, inventories, accepted state,
module-level storage, another stage/trial or worker. Only engine eligibility,
never PH values, uses module-private weak ownership registration.

Thermal validation precedes lookup. Inlet failure precedes outlet. Original trial
initial rates, domain evidence, create/update validation and records bypass the
slots. A rejected accuracy attempt, failed solve, coarse/fine comparison, manual
update or scheduled event cannot carry a slot into the next invocation.
The entry refuses unowned engines; experimental C1 remains on its unchanged path.
