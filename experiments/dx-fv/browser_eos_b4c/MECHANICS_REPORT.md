# 🔧 Ammonia Lab — The Mechanic’s Report

**FOCUSED REPAIR PASS. Full backend qualification remains pending.**

The property engine had a narrow fault just above dry saturated vapor. Ammonia
with a little extra heat could still be sent through the wet-mixture calculation.
That produced a vapor fraction above 100 percent. The reported temperature,
density and energy could then describe different physical conditions closely
enough to fool a coarse property check, but far enough apart to upset the
refrigeration solver's energy balance.

We repaired the decision at the property-engine source. When pressure and a
caloric property place ammonia above the vapor endpoint, the engine now uses
its existing vapor flash at the original requested inputs. It calculates the
vapor state rather than stretching the wet-mixture equation past dry vapor.
Pressure, enthalpy, density and stored energy were independently checked.

The saved failures were reproduced before repair: eleven native and nine browser
base cases. Seven are demonstrably superheated vapor; the closest endpoint
neighbors remain too close to distinguish from saturation numerically. They
are documented that way. Genuine saturated and wet-mixture behavior remains
consistent. The earlier liquid classification, PH precision and vapor-cache
repairs remain intact.

Every affected saved base or probe inventory now recovers within the original
pressure, enthalpy and temperature limits. Original signed probes also meet the
unchanged mass/energy numerical scale. We did not loosen the refrigeration
solver to accommodate inconsistent ammonia properties.

The accepted five-section model passed short cold/warm starts, feed disturbance,
heat reversal, and liquid/vapor zero-exchange trials in Chromium and desktop
WebKit. Its equations, TR-BDF2, Newton limits, perturbations and conservation
checks are unchanged. A new isolated trial at the repaired vapor condition
also passed. These are focused compatibility checks, not the complete campaign.

The corrected edge case costs more than the old mixture shortcut because the
engine now performs a vapor flash. Ordinary vapor and liquid call costs stayed
close to the control in these measurements. Browser linear memory remained
56,360,960 bytes after initialization, and workers remained responsive. These
Linux desktop measurements say nothing yet about a physical iPad.

The 35-bar recovery/support fault and the research loader's rejected-PT cleanup
assertions remain on the work list, with their failures preserved. They were
not repaired here. Production, the workstation UI, Live Plant and Cloudflare
were not changed.

The isolated B4C branch, exact patch, binaries, hashes and machine-readable
evidence are ready for engineering review. Stop here. A separate approval is
required before starting the 35-bar repair or full backend qualification.
