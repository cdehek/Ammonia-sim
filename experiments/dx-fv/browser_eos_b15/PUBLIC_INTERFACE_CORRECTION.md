# Public interface correction retained before final delivery

The first prototype added a fourth internal `statePT` parameter. That function was also returned as the public engine method. JavaScript historically ignored extra public arguments; supplying `{value:[0,0]}` as a fourth argument could instead force the preliminary candidate to use pressure row zero. This was an API/ownership counterexample even though ordinary PH/solver tests matched. It is not hidden by those passes.

Counterexample: `statePT(4,50,undefined,{value:[0,0]})`:

| Result | h kJ/kg | rho kg/m³ |
|---|---:|---:|
| original | 1732.4302908329043 | 2.6163413709465932 |
| v1 | 1637.601879987556 | 0.22867820865956606 |
| corrected | 1732.4302908329043 | 2.6163413709465932 |

The corrected candidate exports a three-argument forwarding function for public PT. Only the original p/T/kind reach its internal helper. Internal PH invokes the helper directly with its locally owned holder. This preserves public arity 3, ignores extra arguments (including throwing getters) as originally, and prevents public injection of the private helper value. No scientific math or PH operation count changes. One wrapper closure is constructed per engine; one holder remains per eligible PH call.

`prototype-v1/` retains the preliminary candidate bytes/build hashes/patch and all timing samples; `evidence/prototype-v1-*` retains preliminary traces, parity receipts and browser summaries. `interface-regression.json.gz` retains exact original/v1/corrected counterexample fields, root cause and 18 public-argument parity checks. Node and Chromium regress it. No failed comparison was removed or tolerance relaxed.

All final candidate scientific schedules, detailed diagnostics, property/refusal/rollback tests and browser pairs were freshly replayed after this correction, binding the final source build hashes. All final-version paired timings were collected afresh in separate clean processes. Preliminary timing samples remain separate and cannot be selectively substituted for final-version samples. The final classification concerns the corrected candidate only.
