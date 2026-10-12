# Stage 2B opt-in saturation-temperature experiment

**Stopped at the focused property gate: candidate preserved, not qualified.**
PCHIP considerably improves general saturation-temperature accuracy, but shifting
the saturation anchor consistently in the unchanged subcooled-liquid property
grid worsens liquid PH temperature accuracy. The user's explicit instruction,
"If the candidate introduces regressions or thermodynamic inconsistency, preserve
the evidence and stop rather than applying compensating corrections," applies.
No event trajectories, compensating corrections or full qualification matrix
were run after this finding. The strict 1 ms event requirement is unchanged.

Repository `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`, HEAD
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. All **192 pre-existing tracked and
untracked candidate files** are byte-for-byte preserved, including the eight-file
Stage 2B candidate and five-file phase-event investigation. No existing file was
modified in this experiment; no commit, push, default promotion or reference
regeneration. No applicable AGENTS.md was found in the workspace.

## Method and dependency paths

The immutable table has 241 saturation rows on an approximately uniform log-pressure
grid, nominally 0.3–35 bar absolute. Its last stored pressure is
35.00000000000001 bar due to floating-point generation; the coupled PH guard
remains exactly 35 bar. Temperature rises strictly with log pressure.
The production engine interpolates T, h and s linearly in log pressure, and
densities logarithmically. Single-phase tables use temperature offsets from this
same saturation anchor. Neither frozen data nor the production engine is changed.

The candidate is piecewise cubic Hermite interpolation (PCHIP) of
`x_i=log(p_i)`, `y_i=T_sat,i`. For interval width `h_i` and secant `d_i`, its
interior slope is the weighted harmonic mean
`m_i=(w1+w2)/(w1/d_(i-1)+w2/d_i)`, with
`w1=2*h_i+h_(i-1)` and `w2=h_i+2*h_(i-1)`.
Endpoint slopes use the standard one-sided three-point rule with sign/shape
limiting. On an interval, normalized coordinate w gives

`T=(2w³−3w²+1)y_i+(w³−2w²+w)h_i*m_i+(-2w³+3w²)y_(i+1)+(w³−w²)h_i*m_(i+1)`.

This uses existing samples only, reproduces knots exactly, preserves monotonicity,
is C1 across knots and forbids extrapolation. It avoids the possible overshoot of
an unrestricted higher-order polynomial. Second derivatives need not be continuous.
Independent SciPy `PchipInterpolator` agrees with the JavaScript values within
1e-11 K on all sampled intervals. Measured dT/dlog(p) stays positive, approximately
16.017–44.141 K. Monotonicity follows the shape-preserving construction; dense
checks also verify it numerically.

`saturation-temperature.cjs` adds a separate research factory. An example is

```js
const {createSaturationCoupledModel}=require('./saturation-temperature.cjs');
const model=createSaturationCoupledModel(originalEngine,immutableData,{
  saturationTemperature:'pchip-log-pressure'
});
const state=model.create({sectionCount:9});
```

Omitting the option or selecting `linear` returns the **original engine object by
identity**. No option is inserted into the existing coupled factory. A1/A2 options
are forwarded independently and unchanged. The candidate adapter consistently
changes `sat`, `satP`, `statePX`, `ph`, `ps`, `statePT`, `stateDU` and `stateMVU`:
for single-phase PH/inventory states, T shifts by `T_pchip(p)−T_linear(p)`; PT
uses the candidate saturation anchor to determine the original branch offset.
Two-phase T equals the candidate saturation temperature. The old PH and density
inversions remain untouched, with their original iteration counts and residual
criteria. The inverse saturation-temperature API uses bounded bisection of the
candidate curve; it is not used by coupled integration. Private application-cycle
closures that capture the old interpolation are unavailable in the candidate
adapter, so no mixed-definition application solver is exposed.

At fixed PH or M/U/V, all non-temperature fields are identical: h, s, rho, u,
quality, phase classification, canonical residuals and liquid inventory. At fixed
absolute PT, the offset and resulting inventory can change as intended; PT tests
compare the same offset from each method's saturation anchor. Refrigerant energy
still obeys `U=M*h−100*p*V`. No hydraulic, conductance, balance or integration
equation is modified.

## Focused EOS results

Node 22.23.3 property checks cover all knots, 33 points per interval (7,920
observations including duplicate interval endpoints), both domain edges, inverse
saturation, C1 boundaries and unsupported inputs. PH/PS/PX/PT/MUV probes cover
2,319 states: every fourth knot and the following interval midpoint, 35 bar,
3.5/3.65 bar, qualities 0/0.01/0.5/0.99/1, liquid offsets
0.001/0.1/1/5/15/30 K, and vapor offsets 0.001/0.1/1/5/15/75/150/250 K.
Eighteen 30 K liquid-offset points are unsupported by the existing low-temperature
table in both methods; neither method extrapolates. No additional MUV recovery
failures occurred among supported probes.

Direct EOS is CoolProp 7.2.0 HEOS ammonia, independently evaluated in Python
3.12.14, NumPy 2.5.3, SciPy 1.16.2. Saturation truth uses PQ; PH truth uses the
same absolute p and h, not a nominal interpolation offset.

| Temperature error | Original maximum / RMS | PCHIP maximum / RMS |
| --- | ---: | ---: |
| Saturation, K | 5.460527e-4 / 2.260991e-4 | 9.492759e-7 / 5.195516e-8 |
| Two-phase PH probes, K | 5.378338e-4 / 2.169122e-4 | 5.938046e-5 / 8.218495e-6 |
| Liquid PH probes, K | 6.031138e-4 / 8.835942e-5 | **1.140942e-3 / 2.951109e-4** |
| Vapor PH probes, K | 1.029586e-2 / 2.126498e-3 | 9.758028e-3 / 2.017967e-3 |

Saturation maximum error improves by approximately 575× and RMS by 4,352×.
Median saturation error falls from 164.369 µK to 0.004766 µK; candidate 95th
percentile is 0.090672 µK. None of the saturation probes worsen beyond 1e-12 K.
Near the two previously failing event pressures, the preliminary EOS comparison
reduces approximately 108.36/108.39 µK bias to 0.010480/0.010481 µK.
This is promising property evidence, **not an event accuracy result**.

Liquid maximum error worsens 1.89× and RMS 3.34×; 363 of 720 liquid PH points
worsen. Vapor aggregate accuracy improves, but 127 of 984 individual PH points
worsen. The worst original vapor probe already exceeds 0.01 K; that is an
existing property approximation limitation at an additional whole-domain probe,
not a failure newly introduced by this candidate or a revised fixture contract.
Two-phase PH errors are larger than saturation PQ errors because unchanged
interpolated hf/hg can place nominal endpoint enthalpies slightly beyond the
exact-EOS phase boundary. Phase labels are not artificially changed to hide this.

All other saturation properties remain identical. Their maximum EOS errors are
hf 0.005179 and hg 0.004775 kJ/kg; sf 9.661e-6 and sg 9.063e-6 kJ/(kg K);
rhof 0.003485 and rhog 0.0002851 kg/m³. These remaining constitutive errors
matter when assessing a temperature-only improvement.

## Regression mechanism and consistency

At 32.653149020386 bar and h=686.779725665 kJ/kg (nominal 0.1 K subcooling):

| PH temperature | °C | Signed EOS error |
| --- | ---: | ---: |
| Direct EOS | 69.277778043862 | — |
| Original | 69.277174930034 | -0.603114 mK |
| Candidate | 69.276637102348 | -1.140942 mK |

The saturation-temperature error at this pressure falls from +0.537834 mK to
approximately +0.000006 mK. Its removal shifts PH temperature down by
0.537828 mK. The unchanged branch enthalpy interpolation/inversion has a negative
temperature-offset error; the original positive saturation error partly cancels
it. Removing one source improves the saturation curve while exposing the other
source in liquid PH. Both PH and MUV show the same consistent change; canonical
energy residual is unchanged at 5.80144e-9 kJ/kg. This is not an inversion failure,
phase-definition mismatch or loss of M/U/V conservation.

The property approximation is not a fully thermodynamically consistent EOS in
either mode. As diagnostic consistency screens, maximum
`(hg−hf)−T*(sg−sf)` falls from 0.004958 to 0.003494 kJ/kg; RMS falls from
0.001772 to 0.000930 kJ/kg. Maximum relative Clausius-Clapeyron mismatch falls
from 0.002506 to 8.270e-6; RMS falls from 0.001267 to 4.857e-7. These use
`dT/dlog(p)=100*p*T*(vg−vf)/(hg−hf)` in bar/kJ units. The identities are still
approximate because h/s/rho interpolation is unchanged. No exact consistency
claim is made from these improved aggregate diagnostics.

The liquid regression remains below the existing 0.01 K trajectory temperature
budget. No established acceptance limit failed in a newly integrated trajectory;
none was run. Nevertheless, the user explicitly required stopping when the
candidate introduces regressions. We do not replace that instruction with a
claim that the regression is small enough to ignore.

## Events, conservation and cost: held at the decision gate

| Mesh | Preserved original extended-event error | Candidate event error |
| --- | ---: | --- |
| Five | +1.326922 ms | Not run: property regression gate |
| Nine | +1.372407 ms | Not run: property regression gate |

The preserved phase investigation supplies converged independent EOS clocks and
the original accepted five-section full-prefix exact reproduction. The candidate
has not been tested on those trajectories; improved local saturation accuracy
cannot be used to infer that the 1 ms gate passes.

The default adapter is identity, and five/nine default initial states and records
are deep-equal to the existing factory. All pre-existing sources and evidence are
unchanged, so the prior default full-prefix reproduction remains applicable.
No new full five-section integration reproduction is claimed.

Supported PH/MUV probes preserve density/internal-energy recovery limits and all
non-T inventory fields. **Integrated heat transfer, mass/energy conservation,
finite-air evolution, state differences, original-fixture regression suites,
temporal refinement, nonlinear failures/work and runtime remain unmeasured for
the candidate.** No cost reduction or solver-stability improvement is claimed.
The candidate adds curve evaluation overhead; its end-to-end effect cannot be
inferred without comparable integrations. No complete qualification, browser or
performance matrix was launched.

## Evidence, files and reproduction

Five new files only:

* `saturation-temperature.cjs`: isolated selectable adapter and PCHIP curve.
* `saturation-interpolation-test.cjs`: property/path/default/edge checks.
* `audit_saturation_properties.py`: independent SciPy/CoolProp sweep and
  stop-on-region-regression classification.
* `audit_saturation_experiment.py`: saved-evidence/preservation/stop-decision audit.
* `SATURATION_INTERPOLATION_EXPERIMENT.md`: this report.

Evidence: `/tmp/ammonia-saturation-evidence/`. `property-tests.json` contains full
native/candidate state probes; `property-eos.json` contains the evaluated EOS
errors and consistency screens; `final-audit.json` independently verifies the
statistics, 192-file preservation and **candidateQualified=false**. The initial
raw EOS output's `passed` flag covered saturation improvement only; it is not
candidate qualification. The reproduction script now includes the liquid
regression in its decision and exits nonzero as expected. Raw evidence is retained
rather than overwritten to conceal the initial narrower flag.

From the repository root, using the pinned runtime:

```sh
OUT=/tmp/ammonia-saturation-replay
mkdir -p "$OUT"
/tmp/ammonia-stage2b-runtime/node-v22.23.3-linux-x64/bin/node \
  experiments/dx-fv/saturation-interpolation-test.cjs "$OUT/property-tests.json"
PYTHONDONTWRITEBYTECODE=1 /tmp/ammonia-stage2b-runtime/python/bin/python \
  experiments/dx-fv/audit_saturation_properties.py \
  "$OUT/property-tests.json" "$OUT/property-eos.json"
# Expected nonzero exit: liquid PH accuracy regression; do not proceed to events.
python experiments/dx-fv/audit_saturation_experiment.py \
  /tmp/ammonia-saturation-evidence /tmp/ammonia-saturation-evidence/final-audit.json
```

Property/path checks, JS/Python syntax checks, saved-evidence audit and
`git diff --check` pass. The candidate's general PH accuracy gate does not pass.
Approximately 9.7 MB of uncompressed diagnostic JSON is retained separately from
normal model runtime/storage. Archives outside the repository provide a candidate
and evidence snapshot; retention across workspace replacement is not guaranteed.

## Review decision

**Do not qualify or adopt this candidate at the current gate.** PCHIP is a strong
saturation approximation, but a temperature-only change is not a uniform
improvement to the existing PH grid. No liquid-enthalpy compensation, new sample,
branch change or different definition is proposed under this authorization.

The next decision is whether to reject the candidate, or separately authorize
bounded trajectory evaluation while explicitly accepting this documented liquid
PH accuracy tradeoff for investigation. Such evaluation would still require the
unaltered 1 ms event budget, independent conservation/temporal checks and original
fixtures. Either choice requires review; no further experiment starts automatically.
