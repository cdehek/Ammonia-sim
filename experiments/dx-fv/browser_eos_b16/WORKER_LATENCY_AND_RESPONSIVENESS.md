# Genuine Worker latency and main-thread observations

Timing separates solver compute, service, request/response transport, main handler and text assignment. Original/candidate use the same message and snapshot format. Fresh-JIT primary rows below pool six cold and six warm sessions per variant (n=12); ping has 144 and snapshot echo 96 observations per variant. Source import/table creation follow an identical fetch/hash verification step. Browser cache is not emptied. Worker startup and init are latency costs, not solver CPU.

| Scope | Original median ms (range) | Candidate median ms (range) |
|---|---:|---:|
| constructMS | 0.20 (0.10–0.30) | 0.20 (0.00–0.90) |
| readyMS | 9.80 (8.50–18.40) | 10.00 (8.70–12.70) |
| assetVerificationMS | 5.35 (4.80–12.80) | 5.80 (5.60–9.40) |
| importMS | 5.55 (4.80–8.40) | 5.40 (5.00–6.70) |
| tableMS | 15.65 (12.90–57.70) | 14.10 (12.10–16.20) |
| initializeMS | 5.25 (3.10–10.40) | 4.40 (2.80–6.60) |
| initialSnapshotRoundtripMS | 32.60 (27.70–91.60) | 31.50 (26.40–34.90) |
| disposeMS | 1.60 (0.50–4.00) | 1.35 (0.50–1.90) |
| projectionMS | 0.10 (0.00–1.20) | 0.10 (0.00–0.20) |
| mainPostMS | 0.00 (0.00–0.10) | 0.00 (0.00–0.10) |
| dispatchToWorkerMS | 0.10 (0.00–2.10) | 0.45 (-0.00–1.80) |
| returnDeliveryMS | 0.15 (-0.10–1.30) | 0.05 (0.00–0.30) |
| handlerMS | 0.15 (0.00–0.20) | 0.10 (0.00–0.20) |
| textAssignmentMS | 0.00 (0.00–0.10) | 0.00 (0.00–0.10) |
| ping-roundtripMS | 0.10 (0.00–4.70) | 0.05 (0.00–12.80) |
| echo-roundtripMS | 0.10 (0.00–0.40) | 0.10 (0.00–1.10) |
| workerPostMS | 0.00 (0.00–29.10) | 0.00 (0.00–32.70) |

Worker construction is synchronous new Worker time; ready includes module loading/scheduling before the handshake. First snapshot roundtrip includes asset verification, engine/table initialization and original model create/record. The synchronous Worker post cost is reported after the original reply; it includes clone/enqueue and is not exclusive serialization CPU. Epoch-based dispatch and return-delivery contain scheduling/queueing; timer quantization affects tiny values. Structured clone is exercised with actual compact snapshots in echo controls. Service and roundtrip summaries for every solver case are in `analysis.json`; no inclusive-scope subtraction is claimed as exclusive clone cost.

| Variant | Heartbeats | Delay median/p95/max ms | Synthetic input count | Input median/max ms | Tool switch median/max ms | Observed long tasks |
|---|---:|---:|---:|---:|---:|---:|
| control | 370 | 0.00/0.70/21.20 | 145 | 4.10/8.90 | 4.10/9.00 | 0 |
| candidate | 335 | 0.00/0.63/3.70 | 129 | 4.10/6.90 | 4.10/7.00 | 0 |

Heartbeat period is 10 ms; delays are excess over scheduled period. It runs independently on the main thread while Worker initialization/warmups/computation proceeds, ending at the accepted response, before deliberate diagnostic transfer/hash validation. Input and tool measurements are actual timer-scheduled DOM click acknowledgements in this harness, not fabricated interaction numbers or physical device input latency. Long Tasks observer is available in Chromium. Zero observed long tasks in these windows is a bounded observation, not full workstation responsiveness qualification. Main-thread handler includes compact display bookkeeping; textContent assignment is measured separately. No layout/paint latency is measured.

In-flight termination/refusal/restart evidence is retained in the science protocol receipt. Worker loss occurs at the harness boundary, rejects pending work as externally lost/unknown, and a fresh session restarts at zero. Terminate/disposal timing is not an OS process reclamation or memory-release guarantee. No responsive full workstation UI, browser background behavior, or owner laptop is qualified.
