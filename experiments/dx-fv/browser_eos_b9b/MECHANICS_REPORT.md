# 🔧 Ammonia Lab — The Mechanic’s Report

The virtual coil is doing far more than updating five temperature readings.
It stores refrigerant mass and internal energy in five sections, plus heat in
the tube, fins and air. Those inventories must agree with pressure, enthalpy,
density, flow and heat transfer at the same instant.

Newton tries a set of pressures, enthalpies and metal/air energies, checks all
21 balances, then nudges each coordinate to learn how the balances respond.
Every correction here requires 21 separate probe evaluations and another
evaluation to check the proposed correction. TR-BDF2 then compares a full
interval with two half intervals before accepting the half-step inventories.
That is six nonlinear stage solves per attempted interval. A rejected interval
is the model refusing an inaccurate advance. The accepted inventories stay at
their last proven values until a smaller interval passes the original numerical
test; the rejection is not automatically wasted calculation.

The property engine also does real work. For a two-phase mixture it can use
saturation and mixture relations. For superheated refrigerant it searches the
bounded property table 38 times to recover temperature from pressure and
enthalpy. Each search interpolates several rows and evaluates density logarithms
and exponentials. A table lookup is therefore often an inverse calculation.

Warm begins with superheated vapor and much less mass in each section. It also
starts discharging through the outlet while cold initially has zero outlet
flow. The initial tube/refrigerant heat transfer is quite similar in the two
cases. The trace shows warm needs smaller accurate intervals and more Newton
corrections, and each property workload contains more expensive vapor inverses.
It is not simply “higher temperature makes the computer slow.” There are no
Newton failures or line-search rejection storms in these short fixtures.

The model already reuses exact section PH results inside each stage. Cold has
12,398 cache hits, warm 32,871. However, it calculates the two unchanged imposed
boundary states again whenever it evaluates rates. That repetition is a concrete
future opportunity to investigate. We have not removed it. A boundary result
could only be reused after proving identical values, support checks, failure
meaning and ownership for the exact table engine and exact unchanged inputs.

In the unchanged runs, advancing only .001 simulated seconds takes median
advance sums of about 106/306 ms cold/warm in Chromium and 140/314 ms in desktop
WebKit. Most measured computation belongs to nonlinear residual/property work;
the small matrix solve is not the main expense. Separately copying the full
research state and attempt history adds a separate measured cost over the endpoint
copies. We cannot honestly assign every remaining millisecond to physics versus
diagnostic construction. Fine profiling itself adds substantial overhead, so
its slower timings are not used as the original coil's performance.

Any future improvement must conserve the same refrigerant and heat, keep the
same phase and support checks, reject the same inaccurate steps and restore the
same accepted inventories exactly after failure. A fast calculation that hides
a property refusal or quietly creates/removes mass or energy is not progress.

The next engineering review should consider a very small table-only experiment:
prove whether the unchanged boundary PH calculations can be reused within one
stage. Keep Newton, signed probes, time-step acceptance and canonical recovery
intact. If that proof fails, stop and examine duplicate saturation intermediates
within a single property call. B9B provides evidence for that decision; it claims
no speedup. The responsive operator workstation, longer operation and physical
iPad/Safari performance still require separate qualification.
