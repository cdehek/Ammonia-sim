# Engineering decision

**B13-A0 DIAGNOSTIC CHARACTERIZATION PASS**

The accepted five-section fixture advanced to an actually observed 0.01 s in both cold and warm cases, in three independent canonical processes plus a diagnostic replay for each. All times above 0.001 s are UNQUALIFIED RESEARCH. No longer-duration scientific qualification is claimed. Horizon progression stops here because the A0 characterization is sufficient; no 0.1 s, 1 s, 10 s, 60 s or one-hour solve was attempted.

| Fixture | Actual t (s) | Accepted substeps | Rejected trials | Residuals | Newton corrections / Jacobians | TR-BDF2 stages |
|---|---|---|---|---|---|---|
| cold | 0.01 | 32 | 1 | 5272 | 235 | 102 |
| warm | 0.01 | 86 | 8 | 19380 | 867 | 306 |

Accepted A2 integrity: unchanged fourteen-file source closure, protected B9C bundle identity, all historical B12 tracked bytes and portable assets verified. Fresh original-A2, B9C and instrumented B9C state/record/attempt hashes agree bit exactly at 0, 0.0001, 0.0005 and 0.001 s in Node 24. Canonical repetitions and diagnostic replay also agree through 0.01 s. Retained Chromium 151 receipts are revalidated but differ from Node binary64 results; cross-version/browser equality is not asserted.

Bottleneck ranking depends on fixture. Jacobian construction accounts for about 61% (cold) and 60% (warm) of instrumented advance wall time, including its residual/property work. All public thermodynamic calls account for about 19% and 57%, respectively. Warm PH inversion alone is about 49%. These overlap: property work is mostly inside residuals and Jacobians. Linear algebra is about 6%/2%, respectively. Finite-difference residual assembly and warm vapor-property inversion are demonstrated costs; worker/UI transport is not timed by this harness and is not assigned solver time.

Median total advance cost for the measured 0.01 s is 17.13 wall seconds per accepted simulated second cold and 92.71 warm. This ratio includes startup, accepted diagnostic allocation, record generation, sparse progress output and runtime overhead. Recent-window rates differ strongly, so these are measured local throughput ratios, not steady-state forecasts. CPU includes V8 background/JIT threads and can exceed wall time.

Conservation: maximum sampled global mass residuals are 1.26e-14 kg cold / 8.73e-14 kg warm. Maximum sampled combined-energy residuals are 6.32e-12 / 1.5e-10 kJ. Section/node closures pass the preserved audits. No normal-fixture numerical/domain stop or property exception occurred.

All observed normal-fixture rejections were temporal accuracy rejections. Newton converged in 2–5 corrections per stage cold and 2–7 warm, with every recorded line search accepting factor 1 and every derivative using its first positive probe. The failure-aware nonlinear growth ceiling never activated. Warm section 0 crosses the vapor boundary near 0.00537543 s and incurs five further accuracy rejections in the last interval; this challenges duration extrapolation without demonstrating Newton instability or a physical equipment fault.

A separate sealed, zero-exchange, exact-200 K support-boundary witness commits 0.0001 s of an initial 0.0002 s request, then refuses outward thermal motion with confirmed domain evidence. Earlier progress survives; no current rejected state leaks; stopped repeats and invalid boundary updates preserve physical state. Original A2/B9C contracts agree bit exactly. It is a contract witness, not normal-fixture behavior.

Performance projection confidence: strong for work counts and repeatability at these output boundaries; limited for component-time percentages (one detailed replay, nested probes and JIT noise); low for 0.1 s; unsupported as physical-success predictions for 1–3600 s. The current fixture has fixed pressure/enthalpy reservoirs, uncalibrated hydraulic/heat-transfer inputs and no complete refrigeration loop.

Recommended next investigation: bounded phase-boundary temporal-error and Jacobian/residual decomposition, with independent equivalence gates before any optimization. Keep worker computation and desktop-first review. No production or deployed assets change. Stop for review.
