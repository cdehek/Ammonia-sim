# Exact seven-case refusal matrix

Both engines reproduce their own saved inventories. All original PH inputs are
`3500000 Pa`, bits `414ab3f000000000`. Runtime is C / `boundary-unresolved`,
compatible `solver`, no state returned, no physical-domain proof. Mechanism
and mathematical pressure sign are independent **offline B5B evidence**.
Every M/V/U/rho/u and raw getter bit is in `evidence/classification-matrix.json`.

| Key suffix | Raw p bits | Raw P−max Pa | Mathematical P−max Pa | Independent mechanism |
|---|---|---:|---:|---|
| 64 | `414ab3f000000140` | +1.49011611938e-07 | -2.58101716514e-09 | numerical-wrong-side |
| 65 | `414ab3f000000317` | +3.6833807826e-07 | +4.01190221955e-07 | rounded-inventory-conflict |
| 67 | `414ab3f000000006` | +2.79396772385e-09 | +7.02192693616e-09 | rounded-inventory-conflict |
| 68 | `414ab3f000000004` | +1.86264514923e-09 | +7.04166454343e-10 | rounded-inventory-conflict |
| 70 | `414ab3f00000066c` | +7.65547156334e-07 | +7.72409866695e-07 | rounded-inventory-conflict |
| 75 | `414ab3f000000003` | +1.39698386192e-09 | -8.24286338428e-10 | numerical-wrong-side |
| 79 | `414ab3f000000004` | +1.86264514923e-09 | +1.79967963169e-09 | rounded-inventory-conflict |

There are two numerical wrong-side recoveries and five rounded-inventory
conflicts. All seven pass canonical and normalized mass/energy budgets and
still fail strict support. No pressure epsilon or precision enclosure exists.

## Saved inward false-acceptance controls

| Key | Raw p bits | Raw P−max Pa | Mathematical P−max Pa | Candidate |
|---|---|---:|---:|---|
| webkit-ledger-69 | `414ab3effffffd12` | -3.49245965481e-07 | +2.94076290925e-07 | historical return unchanged; qualification blocker |
| webkit-ledger-76 | `414ab3effffffff9` | -3.25962901115e-09 | +2.50420072426e-10 | historical return unchanged; qualification blocker |

The candidate cannot detect these outside mathematical inventories from a
supported-looking numeric pressure. Additional general numerical certification
is required; no fixture filters, pressure band or input substitution is used.

## Requested inputs versus returned coordinates

The exact/one-Pa-ULP-inward/one-Pa-ULP-outward saved PH triplets and all phase
controls are retained in each replay matrix. The explicit outward request is
refused even when its separately constructed mixture MVU operation returns.
Different original PH requests can have identical inventory bits. MVU cannot
reconstruct that missing request. Returned-coordinate support and input support
remain separate observations. Neither establishes a physical excursion.

See `*-guards.json` for unchanged lower/upper bar comparisons and synthetic
temperature guard isolation. Synthetic outputs are not physical EOS states.
