# Bounded diagnostic neighborhood

| Inventory | Perturbation | Mathematical branch | Float64 admissible attempts / 6 | Gate A raw outcome |
|---|---|---|---:|---|
| native-ledger-148 | exact saved inventory | equilibrium | 4 | QT exception |
| native-ledger-162 | exact saved inventory | homogeneous | 2 | returned |
| native-ledger-164 | exact saved inventory | equilibrium | 5 | QT exception |
| native-ledger-165 | exact saved inventory | homogeneous | 3 | QT exception |
| native-ledger-148-rho-1 | diagnostic rho -1 ULP | equilibrium | 3 | QT exception |
| native-ledger-148-rho1 | diagnostic rho +1 ULP | equilibrium | 4 | QT exception |
| native-ledger-148-u-1 | diagnostic u -1 ULP | equilibrium | 5 | QT exception |
| native-ledger-148-u1 | diagnostic u +1 ULP | homogeneous | 2 | returned |
| native-ledger-148-rho-16 | diagnostic rho -16 ULP | equilibrium | 3 | returned |
| native-ledger-148-rho16 | diagnostic rho +16 ULP | equilibrium | 4 | returned |
| native-ledger-148-u-16 | diagnostic u -16 ULP | equilibrium | 6 | returned |
| native-ledger-148-u16 | diagnostic u +16 ULP | homogeneous | 1 | returned |
| native-ledger-148-du-0.01 | diagnostic fixed-density u -0.01 J/kg (binary64 addition) | equilibrium | 6 | returned |
| native-ledger-148-du0.01 | diagnostic fixed-density u +0.01 J/kg (binary64 addition) | homogeneous | 0 | returned |
| native-ledger-162-rho-1 | diagnostic rho -1 ULP | homogeneous | 2 | returned |
| native-ledger-162-rho1 | diagnostic rho +1 ULP | homogeneous | 2 | returned |
| native-ledger-162-u-1 | diagnostic u -1 ULP | homogeneous | 2 | returned |
| native-ledger-162-u1 | diagnostic u +1 ULP | homogeneous | 2 | returned |
| native-ledger-162-rho-16 | diagnostic rho -16 ULP | equilibrium | 6 | returned |
| native-ledger-162-rho16 | diagnostic rho +16 ULP | homogeneous | 2 | returned |
| native-ledger-162-u-16 | diagnostic u -16 ULP | homogeneous | 5 | returned |
| native-ledger-162-u16 | diagnostic u +16 ULP | homogeneous | 2 | returned |
| native-ledger-162-du-0.01 | diagnostic fixed-density u -0.01 J/kg (binary64 addition) | equilibrium | 6 | returned |
| native-ledger-162-du0.01 | diagnostic fixed-density u +0.01 J/kg (binary64 addition) | homogeneous | 0 | returned |
| native-ledger-164-rho-1 | diagnostic rho -1 ULP | equilibrium | 5 | QT exception |
| native-ledger-164-rho1 | diagnostic rho +1 ULP | equilibrium | 4 | QT exception |
| native-ledger-164-u-1 | diagnostic u -1 ULP | equilibrium | 4 | returned |
| native-ledger-164-u1 | diagnostic u +1 ULP | equilibrium | 4 | QT exception |
| native-ledger-164-rho-16 | diagnostic rho -16 ULP | equilibrium | 3 | returned |
| native-ledger-164-rho16 | diagnostic rho +16 ULP | equilibrium | 3 | returned |
| native-ledger-164-u-16 | diagnostic u -16 ULP | equilibrium | 6 | returned |
| native-ledger-164-u16 | diagnostic u +16 ULP | homogeneous | 1 | returned |
| native-ledger-164-du-0.01 | diagnostic fixed-density u -0.01 J/kg (binary64 addition) | equilibrium | 6 | returned |
| native-ledger-164-du0.01 | diagnostic fixed-density u +0.01 J/kg (binary64 addition) | homogeneous | 0 | returned |
| native-ledger-165-rho-1 | diagnostic rho -1 ULP | homogeneous | 3 | QT exception |
| native-ledger-165-rho1 | diagnostic rho +1 ULP | homogeneous | 3 | QT exception |
| native-ledger-165-u-1 | diagnostic u -1 ULP | equilibrium | 3 | QT exception |
| native-ledger-165-u1 | diagnostic u +1 ULP | homogeneous | 1 | returned |
| native-ledger-165-rho-16 | diagnostic rho -16 ULP | homogeneous | 3 | returned |
| native-ledger-165-rho16 | diagnostic rho +16 ULP | homogeneous | 3 | QT exception |
| native-ledger-165-u-16 | diagnostic u -16 ULP | equilibrium | 5 | returned |
| native-ledger-165-u16 | diagnostic u +16 ULP | homogeneous | 0 | returned |
| native-ledger-165-du-0.01 | diagnostic fixed-density u -0.01 J/kg (binary64 addition) | equilibrium | 6 | returned |
| native-ledger-165-du0.01 | diagnostic fixed-density u +0.01 J/kg (binary64 addition) | homogeneous | 0 | returned |

Admissible means only that the algebraic mixture fraction lies in [0,1]. It does not certify the correct branch. All quantities use the exact labeled rho/u bits in `evidence/cases.json`. Modified neighbors never replace originals. The +0.01 J/kg cases have stable homogeneous mathematical roots; their extrapolated mixture rejection is expected. All 13 native exceptions remain in evidence. No derivative smoothness is imposed across saturation.
