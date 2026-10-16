# 🔧 Ammonia Lab — The Mechanic’s Report

**CONTRACT DESIGN SUPPORTED**

The strict 35-bar check stays. All seven original browser recoveries still fail
that check in Chromium and desktop WebKit, with their original input/output bits.
The raw numerical recoveries are accurate; the complete adapter calls fail.

Two exact inventories are mathematically inside and recover to the wrong side.
Five are mathematically outside after the accepted binary64 construction. Better
inverse accuracy alone cannot make those five satisfy exact inventory and the
hard maximum together. These tiny same-EOS differences do not establish a real
plant pressure excursion.

The opposite hazard is real too: two saved exact inventories mathematically
outside recover inward and the unchanged adapter returns them. A separate
one-ULP-above PH request is refused as PH but its rounded mixture inventory
returns through MVU. We must protect against false acceptance as well as false
rejection. No tolerance is justified by these examples.

The proposed contract keeps five outcomes distinct: confirmed physical exit,
numerical failure, unresolved boundary/conflict, supported success, and independently
unsupported input. Only supported success may supply an accepted property state.
The diagnostic prototype returns classifications and no property states.

MVU lacks original PH provenance and physical direction. Distinct original
pressures can produce identical inventory bits, so that information cannot be
reconstructed. A2 currently trusts a domain-labeled conservative recovery probe
as proof of refrigerant exit. The next narrow step is reviewed failure reporting
and propagation that preserves strict refusal and exact rollback, with independent
proof required for a physical-exit assertion. Implementation remains pending.

Gate B's four endpoint cases, Gate A browser qualification, rejected-PT cleanup
and full accepted A2 qualification all remain separate blockers. No backend,
adapter, loader, accepted solver, pressure limit, numerical budget, production,
UI, Live Plant or deployment was changed.

All 1838 historical files, five inherited patches, property artifacts, accepted
A2 dependencies and protected remote refs are preserved. Only additive B5B
research is committed on the requested branch. Stop for engineering review and
explicit approval; do not automatically start implementation.
