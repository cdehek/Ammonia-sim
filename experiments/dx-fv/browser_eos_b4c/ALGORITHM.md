# B4C decision recorded before functional source modification

Start: exact clean B4B d0d11d59756c4dc32bbfdb22a5975fd6f4527e05.
Upstream: CoolProp 8.0.0 ae81610e7d23efc57f9d051c8e70a4d66e87537f.
All tracked B4B source hashes match after applying unchanged B1, B4A and B4B
patches. The archived B4B native replay matches every historical scientific
result exactly, excluding timing. Read B4B report/algorithm/patch, B4A
report/algorithm/liquid patch and B3 report/proposals/source phase traces.

## Thermodynamic evidence and selected algorithm

`preimplementation-thermodynamics.json` contains independent homogeneous DT
Newton roots at all 14 unique invalid native base/probe coordinates. The ten
resolved vapor snapshots converge with original reference limits 1e-5 Pa and
1e-8 J/kg, positive cp, cv and compressibility, and T above coexistence by
1.89e-7 to 6.66e-7 K. The other four are one-ULP endpoint neighbors, unresolved
at that reference resolution; their roots are indistinguishable from saturation.
Full-VLE saturation independently agrees with superancillary equilibrium at
the original standalone budgets, with chemical-potential residuals recorded.
The endpoint disagreement (up to 8.82e-8 J/kg in hg here) is much smaller than
the resolved 0.000915–0.001416 J/kg superheat. It still exceeds one ULP: endpoint
neighbors must not be labeled proven superheated merely from the sign of Q.

For H/S/U-at-pressure, extend the existing vapor dispatch to computed Q>1 in
both saturation-decision paths. Preserve the existing Q>1+1e-9 behavior for
density input, the B4A liquid condition byte-for-byte, and the equilibrium path
at exactly Q=1, Q=0 and 0<Q<1. This selects the existing bounded homogeneous
vapor inversion at the original pressure and original caloric value. It does
not install a final state or prove stability solely by choosing a phase enum.
Independent roots, equilibrium and EOS residual gates provide that proof for
the focused ammonia envelope. No new quality tolerance is introduced.

Positive vapor cp gives increasing h at fixed p; positive cp/T and
du/dT|p=cp-p*d(v)/dT|p are explicitly checked for S/U in the shared-caller
campaign. The matching vapor branch is therefore justified by caloric endpoint
ordering and independent stable roots, not by symmetry with the liquid patch.
Existing PH/PS/PU bounds, convergence and rejection behavior remain authoritative.

## Source owner and exact lifecycle

Owner: `HelmholtzEOSMixtureBackend.cpp::p_phase_determination_pure_or_pseudopure`.
Superancillary: T(p), rhoL/V(T), unchecked saturated states, their actual H/S/U
getters and raw Q. Q>1 currently falls into the lever equation until 1+1e-9.
Use its existing gas branch, clearing SatL/V and assigning dispatch sentinel
1000. `HSU_P_flash` reconstructs the same superancillary Tmin=Tsat and uses
Tmax=1.5*Tmax(fluid). No liquid `_TLanc` change is needed for gas dispatch.

Full VLE: preserve ancillary fast decisions and error bands; ambiguous values
invoke PQ equilibrium, copy SatL/V, set `saturation_called=true`, calculate Q,
then dispatch. Existing gas Tmin=SatV->T() is retained. Genuine equilibrium
keeps its endpoint T and lever density. No extrapolated lever density is used
for caloric Q>1. Density classification, PT iT selection, DU HSU_D_flash and
mixtures remain unchanged. The B4B PT commit and B1 44-bit bracket remain exact.

Pressure-caloric mass variants convert through existing molar conversion. The
shared classifier covers PH, PS and PU. Pure fluids share the superancillary
path; pure/pseudopure fluids share the full-VLE path. These source consequences
are not qualified for other fluids, critical/triple regions or mixtures by this
ammonia experiment.

## Endpoint uncertainty and alternatives

Exact endpoint h can round during mass/molar conversion or disagree across
saturation implementations. Preserve original inputs and record actual raw Q;
tiny positive excess may enter homogeneous inversion and resolve an
indistinguishable endpoint, or explicitly fail. Do not clamp Q, substitute
rhog, round p/h, widen brackets, suppress an inversion exception or invent a
vapor fraction. Record one-sided continuity and canonical behavior. Never
impose a two-sided homogeneous derivative across a physical boiling boundary.
At 35 bar distinguish property correctness from unchanged DU exceptions and
strict adapter support rejection after numerical overshoot.

A blind replacement for all callers would alter density behavior without
evidence. An EOS change, new solver, precision change, quality clamp or solver
tolerance change is unnecessary and unauthorized. Rejecting every slight
superheat would deny stable supported roots already demonstrated independently.

## Gates and runtime limits

Baseline inspection/reproduction: 10 minutes each. Setup/build: 60 minutes
total, each native/WASM build <=900 s, <=2 compiler jobs. Focused property
campaigns <=120 s, browser campaigns <=180 s, limited A2 <=300 s, performance
<=180 s. Preserve failures and partial output at deadlines.

First require all resolved upper-quality cases: stable homogeneous vapor,
independent EOS consistency, original canonical .1 Pa/.1 J/kg/1e-4 K, original
standalone <10 Pa/<50 J/kg/<.01 K, local normalized energy <=1e-11, and original
signed same-vapor mass/energy contamination <=1e-11. Include original B1/B4A/B4B
regressions. Then saturation boundaries/default and full VLE, native/browser,
PH/PS/PU/PT reused/fresh lifecycle. Preserve every unsupported probe and known
35-bar failure. If an essential gate fails, stop unnecessary A2/performance,
retain the candidate and report failure/inconclusive instead of weakening gates.
Only after focused gates pass run bounded unchanged accepted A2 fixtures and
matched runtime measurements. No full qualification, production change,
deployment or physical iPad claim. Stop for engineering review afterward.
