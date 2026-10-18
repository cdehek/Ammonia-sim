# Mechanic’s Report

The old worker sends a laboratory notebook with every gauge reading: refrigerant
inventory, thermal ledgers, thousands of Newton derivative/line-search records
and full model state. An operator needs a small set of honest readings, not that
whole notebook on every refresh. The compact view carries five section pressures,
temperatures, masses and energies, coil-metal/air temperatures, clock and fault
status. Detailed evidence stays available by accepted-state version.

Changing the gauge face cannot change how much ammonia or energy is in a section.
The worker keeps the exact original mass, internal energy and volume and performs
the same accepted property, conservation and numerical checks. Display values
never rebuild or update refrigerant inventory. Wet is the modeled bulk indication,
not a compressor protection or safe-suction signal.

Smaller messages improved measured button-response tails in both browsers.
Chromium A→B automation p95 went 24.38→4.41 ms; WebKit 12.82→9.99 ms. It did not
make the underlying physics reliably faster. WebKit still had long frame gaps.
The main remaining expense is the original nonlinear/property work, with extra
cost from laboratory trace copying and traffic. This .001-second workload says
nothing about sustained real-time plant simulation.

When an ammonia property calculation refuses, the model keeps its last accepted
inventory, follows the original retries/halvings and reports the actual numerical
fault. A failed accepted-state record is unavailable; the panel marks the older
reading stale. Only independently proven modeled thermal exits keep their distinct
physical-domain meaning. Less diagnostic traffic cannot make an unresolved fluid
state valid. Synthetic fault tests prove handling, not natural EOS reachability.

The worker is **not ready for operator-workstation integration**. Exact tested
science and useful communication savings justify more isolated engineering work;
remaining frame behavior, startup/memory uncertainty and scientific qualification
gaps still require review. No plant alarm, valve, receiver level, compressor
measurement or safety trip has been invented.
