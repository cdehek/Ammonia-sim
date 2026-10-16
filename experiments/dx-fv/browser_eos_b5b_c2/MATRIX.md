# Focused exact-inventory matrix

All complete certificate outcomes are **UNRESOLVED**. Signed numbers below are Level-1 diagnostics; homogeneous local pressure bounds are separately retained in `evidence/local-enclosures.json`. PH input support is a separate fact.

| Case | PH input supported | Raw p−max (Pa) | Exact M/U/V p−max (Pa) | Rounded DU p−max (Pa) | Branch diagnostic | Historical MVU |
|---|---|---:|---:|---:|---|---|
| chromium-ledger-64 | True | +1.49011611938e-07 | +3.22972603677e-09 | -2.58101716514e-09 | liquid | refuse |
| chromium-ledger-65 | True | +3.6833807826e-07 | +3.73186568858e-07 | +4.01190221955e-07 | liquid | refuse |
| chromium-ledger-67 | True | +2.79396772385e-09 | +7.07996082661e-09 | +7.02192693616e-09 | vapor | refuse |
| chromium-ledger-68 | True | +1.86264514923e-09 | +1.0267011886e-09 | +7.04166454343e-10 | vapor | refuse |
| chromium-ledger-70 | True | +7.65547156334e-07 | +7.3396167196e-07 | +7.72409866695e-07 | liquid | refuse |
| chromium-ledger-75 | True | +1.39698386192e-09 | -1.45517845677e-09 | -8.24286338428e-10 | vapor | refuse |
| chromium-ledger-79 | True | +1.86264514923e-09 | +1.20428458609e-09 | +1.79967963169e-09 | vapor | refuse |
| webkit-ledger-69 | True | -3.49245965481e-07 | +3.04967661516e-07 | +2.94076290925e-07 | liquid | return |
| webkit-ledger-76 | True | -3.25962901115e-09 | +4.66917128521e-11 | +2.50420072426e-10 | vapor | return |
| B5-sweep-0 | True | +1.49011611938e-07 | +3.22972603677e-09 | -2.58101716514e-09 | liquid | refuse |
| B5-sweep-1 | True | -7.45058059692e-09 | -2.57055354848e-08 | -2.56909195634e-08 | equilibrium | return |
| B5-sweep-2 | True | +2.79396772385e-09 | +7.07996082661e-09 | +7.02192693616e-09 | vapor | refuse |
| B5-sweep-3 | True | +1.49011611938e-07 | +3.22972603677e-09 | -2.58101716514e-09 | liquid | refuse |
| B5-sweep-4 | True | -7.45058059692e-09 | -2.57055354848e-08 | -2.56909195634e-08 | equilibrium | return |
| B5-sweep-5 | True | +2.79396772385e-09 | +4.11777521237e-09 | +4.06162821858e-09 | vapor | refuse |
| B5-sweep-6 | False | +1.49011611938e-07 | +3.22972603677e-09 | -2.58101716514e-09 | liquid | refuse |
| B5-sweep-7 | False | -7.45058059692e-09 | -2.57055354848e-08 | -2.56909195634e-08 | equilibrium | return |
| B5-sweep-8 | False | +7.91624188423e-09 | +1.01193930503e-08 | +1.09405183642e-08 | vapor | refuse |
| B5-sweep-9 | True | -0.350001534447 | -0.350001153118 | -0.350001115583 | liquid | return |
| B5-sweep-10 | True | -0.350000009872 | -0.350000029017 | -0.350000028425 | equilibrium | return |
| B5-sweep-11 | True | -0.349999995437 | -0.34999999482 | -0.349999995049 | vapor | return |
| B5-sweep-12 | True | -9.99999993807 | -10.0000002945 | -10.0000003215 | liquid | return |
| B5-sweep-13 | True | -10.0000000079 | -10.0000000257 | -10.000000025 | equilibrium | return |
| B5-sweep-14 | True | -9.99999999907 | -9.99999999782 | -9.99999999833 | vapor | return |
| B5-sweep-15 | True | -10000.000002 | -10000.0000018 | -10000.0000018 | liquid | return |
| B5-sweep-16 | True | -10000 | -10000 | -10000 | equilibrium | return |
| B5-sweep-17 | True | -10000 | -10000 | -10000 | vapor | return |
| B5-sweep-18 | True | -99999.999999 | -99999.9999989 | -99999.9999989 | liquid | return |
| B5-sweep-19 | True | -100000 | -100000 | -100000 | equilibrium | return |
| B5-sweep-20 | True | -100000 | -100000 | -100000 | vapor | return |
| outside-100Pa-liquid | False | +100.000000092 | +100.000000378 | +100.000000357 | liquid | refuse |
| outside-100Pa-mixture | False | +99.9999999963 | +99.9999999788 | +99.9999999793 | equilibrium | refuse |
| outside-100Pa-vapor | False | +99.9999999939 | +99.9999999971 | +99.9999999972 | vapor | refuse |
| native-ledger-148 | unknown | +1.95577740669e-08 | +2.57777190386e-09 | +2.77274401769e-09 | equilibrium | refuse |
| native-ledger-162 | unknown | +1.07102096081e-08 | +8.24838518944e-07 | +7.77767489467e-07 | liquid | refuse |
| native-ledger-164 | unknown | +2.421438694e-08 | +2.87105897589e-09 | +2.29586318595e-09 | equilibrium | refuse |
| native-ledger-165 | unknown | +1.07102096081e-08 | +3.81257914279e-09 | +3.33190702161e-09 | vapor | refuse |

The first seven contain one exact-M/U/V inside sign and six outside signs; their historical rounded-DU split remains two inside/five outside. No historical file or classification wrapper changes. Gate B endpoint rows remain unqualified. B5-sweep-19 retains its initial algebraic diagnostic failure and successful physical-equation supplement.
