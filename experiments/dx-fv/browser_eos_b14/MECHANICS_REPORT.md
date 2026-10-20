# Mechanics report

B14 explains why this research evaporator sometimes asks the computer to take a smaller time step. It does not add a control, alarm or solver feature, and it does not change the working B12 simulator.

In the warm example, the first section starts as superheated vapor. Near 0.005375 simulated seconds it enters the liquid-and-vapor region. This is the cooling direction, contrary to the initial question's assumed direction. We know it changes between two accepted times, 0.00535913 and 0.00538204 s. The displayed event time is an interpolation inside that interval.

Mass and total internal energy in that section both increase while its specific enthalpy and temperature fall. Low-enthalpy feed and changing flow explain why falling temperature does not mean energy disappeared. Tube heat still enters the refrigerant. Every signed mass/energy ledger stays within the original tight limits.

The solver checks one full trial against two half trials. If their predicted inventories or properties differ too much, it discards the trial and tries a shorter interval. Near the transition, refrigerant internal energy, mass and pressure drive those decisions. Metal/fin/air temperature errors do not. Internal flow between the first two sections also reverses shortly after the phase change. This helps explain why not every extra rejection is caused by crossing the phase label itself.

All ordinary warm Newton solves converge and all their line searches accept their first full correction. These time-step accuracy rejections are therefore not evidence of a broken nonlinear solver or a physical equipment fault. A separate test deliberately reaches the model's temperature support boundary; it stops honestly and preserves earlier accepted progress. A computer time-budget kill is recorded separately again.

The expensive Jacobian is built by slightly changing each of 21 coordinates and recalculating the residual. Thermal changes already reuse cached refrigerant properties correctly. Pressure/enthalpy changes need new properties. Superheated PH recovery makes 38 bisection iterations per call, even near saturation, and repeatedly locates the same pressure in the table. The recommended next experiment is to investigate reusing that pressure location within one call while preserving every calculation and answer. B14 implements none of it.

The longest research run is only 0.01 simulated seconds. The accepted qualified horizon remains 0.001 s. This is one modeled evaporator with artificial fixed reservoirs and uncalibrated heat transfer, not a commissioned refrigeration plant. A wet terminal bulk state does not measure compressor liquid carryover or establish a safety limit.

Future throughput assessment should use ordinary Windows/macOS desktops and Chrome/Edge. The owner's iPad startup/disposal feedback remains useful but cannot measure solver throughput. Production, PR #3, the original workstation and Cloudflare deployments are unchanged. Work stops for engineering review.
