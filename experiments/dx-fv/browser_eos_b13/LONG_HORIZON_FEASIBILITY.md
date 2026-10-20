# Long-horizon feasibility: projections only

Maximum actually simulated time is 0.01 s. The following targets were **not simulated**: 0.1 s, 1 s, 10 s, 60 s and one hour. No scientific qualification expands beyond 0.001 s.

Measured costs vary enough that predictive optimistic/central/pessimistic confidence bounds are unsupported. The table instead gives reproducible conditional arithmetic budgets, in wall seconds: fastest measured recent-window rate × target; median whole-probe rate × target; slowest observed interval rate × target. The slow rate includes tiny startup intervals. These are observed cost scenarios, not probabilities, limits or forecasts of physical success. A domain/numerical refusal can prevent reaching a target at any CPU budget.

| Fixture | Projection target simulated s | Fast recent-rate budget wall s | Median whole-probe-rate budget wall s | Slow observed-rate budget wall s |
|---|---|---|---|---|
| cold | 0.1 | 0.3253 | 1.713 | 51.88 |
| cold | 1 | 3.253 | 17.13 | 518.8 |
| cold | 10 | 32.53 | 171.3 | 5188 |
| cold | 60 | 195.2 | 1028 | 3.113e+04 |
| cold | 3600 | 1.171e+04 | 6.166e+04 | 1.868e+06 |
| warm | 0.1 | 5.625 | 9.271 | 207.1 |
| warm | 1 | 56.25 | 92.71 | 2071 |
| warm | 10 | 562.5 | 927.1 | 2.071e+04 |
| warm | 60 | 3375 | 5563 | 1.243e+05 |
| warm | 3600 | 2.025e+05 | 3.338e+05 | 7.457e+06 |

Formula: interval rate = wallMS / (1000 × actual accepted Δt). Whole-probe rate = sum(advance wallMS) / (1000 × 0.01). Process startup/receipt serialization is excluded. CPU budgets at the median observed CPU rate are 30.59 × target seconds cold and 132 × target warm. CPU and wall differ because V8 compilation/GC/background threads and scheduling contribute. These CPU rates are not assumed to stay constant.

Even 0.1 s is ten times the longest observed horizon and remains a low-confidence extrapolation. For 1, 10, 60 and 3600 s the factors are 100, 1,000, 6,000 and 360,000: current evidence does not establish the phase path, stable adaptive steps, support-domain reachability, inventory positivity, boundary realism, convergence or memory behavior. One hour's arithmetic is especially unsuitable as a feasibility promise.

The warm trajectory already changes phase near 0.005375 s and adds five temporal rejections in the last interval. Cold grows its steps while warm subdivides a saturation crossing. Neither trajectory samples mature coupled plant dynamics or a steady operating condition. Repeating startup tiny-step expense forever is not a justified pessimistic forecast; maintaining the best late-window step is not a justified optimistic forecast. The table exposes the sensitivity without asserting either future.

Measured bottleneck ranking: (1) Jacobian-associated residual workload, plus substantial warm PH inversion inside it; (2) repeated TR-BDF2 stages needed for accepted adaptive accuracy and phase transitions; (3) other recovery/assembly/diagnostic/runtime work; (4) linear algebra, currently small. Fixed boundary physics and thermodynamic domain support limit future physical meaning/reachability but caused no normal-fixture refusal in the measured interval. Worker/UI cost is not measured here and is not ranked as a scientific bottleneck.

Memory cannot be projected from the 21-coordinate state alone: original diagnostic history grows with corrections/attempts, while B13 receipt encoding adds temporary copies. A bounded history/transport design and heap profiling are required before extended worker sessions. No unsupported memory-per-hour figure is supplied.

Required next evidence: controlled desktop-browser timing, phase-boundary error decomposition, support-domain monitoring with accepted partial-state retention, longer-horizon step/energy/refinement checks under a separately approved protocol, and realistic coupled boundaries/calibration. Speed improvements alone would not establish an industrial refrigeration simulator.
