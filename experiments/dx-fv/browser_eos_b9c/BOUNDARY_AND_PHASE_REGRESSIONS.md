# Boundary and phase regressions

| Bounded original-interface scenario | Result |
|---|---|
| flow-reversal | EXACT in Chromium and WebKit |
| scheduled-boundary | EXACT in Chromium and WebKit |
| manual-boundary | EXACT in Chromium and WebKit |
| saturated-0 | EXACT in Chromium and WebKit |
| saturated-1 | EXACT in Chromium and WebKit |
| saturated-0.4 | EXACT in Chromium and WebKit |
| superheated-outlet | EXACT in Chromium and WebKit |
| thermal-200 | EXACT in Chromium and WebKit |
| thermal-400 | EXACT in Chromium and WebKit |
| numerical-stop | EXACT in Chromium and WebKit |

In addition to frozen cold/warm, each engine executes ten bounded scenario pairs,
31 PH input/phase cases, four refused boundary updates and an original missing-row
statePT refusal. The raw cases and bit encodings remain in regressions-*.json.gz.
All full states, records, attempts, component hashes and logical boundary-result
hashes agree. Property counts differ only by successful stage-boundary hits.

Reversal changes inlet 4→3 bar and outlet 3.5→4 bar after initial supported work.
Both end flows reverse. The outlet now donates 1700 kJ/kg; energyKW is checked
against the signed mass flow times that actual boundary enthalpy. Sections retain
their own dynamic state. Scheduled and manual patches use original paths;
the scheduled event occurs exactly at .0001 s and later stages see 4.2/3.4 bar.
No prior stage cache is reachable from either patch path.

Saturated liquid, vapor and genuine x=.4 mixture boundaries use original sat
values; genuine superheated outlet uses the original expensive inverse. Direct
hf/hg near-edge inputs preserve the original eps classification. Pressures test
.3±1e-12 and 35±1e-12 bar, endpoints, nonfinite and zero inputs. Enthalpies include
supported/subcool/superheat edges, nearby supported and refused states, signed
zero and nonfinite inputs. No epsilon support or physical input change is added.

Cold/warm naturally reject 1/3 accuracy steps. All retries preserve exact original
decisions and successful candidates never contaminate accepted inventories.
The bounded numerical-stop fixture deliberately selects supported restrictive
maxIterations=1,maxAttempts=20 to exercise a numerical stop; these settings NEVER
enter the fixed cold/warm qualification or timing workloads.

Limits: PH branchLimit avoids absent liquid rows, so missing-row refusal is tested
through original statePT, not forced by editing the solver. A caller cannot install
an unsupported boundary using valid create/update. In-stage failure cache behavior
is verified by an exact-source isolated mechanical unit, not a new backend route.
Thermal validation precedence is source-proven; supported genuine outward 200/400 K
cases exercise refusal/rollback without forging invalid accepted state.
