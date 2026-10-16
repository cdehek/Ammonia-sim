# Engineering review and future qualification gates

No B4B work is started by this milestone. Engineering must review the two-condition
patch, both saturation paths, endpoint rounding and the explicit inverse/support
limitations before authorizing further work.

1. Select and separately review a vapor PT/cache correction using B3's exact
   saved PH and isolated PT traces. Prove final density, derivative caches,
   returned pressure and caloric properties refer to the same DT coordinates.
   Preserve original request bits, derivative probes and nonlinear scales.
2. Resolve the upper 1<Q<=1+1e-9 classification band as a distinct boundary
   question. Do not treat its unchanged invalid lever extrapolation as legitimate
   equilibrium or assume the PT cache correction resolves it.
3. Resolve or explicitly bound default 35-bar recovery overshoot/support behavior,
   full-VLE DU exceptions and native 7.2's historical DU limitations. Preserve
   fixed inventories and the accepted guard; do not round recovered pressure.
4. Extend endpoint/branch qualification to the complete accepted support envelope,
   cold/warm/reused/fresh inverse routes and option combinations. If a generic
   CoolProp source patch is proposed upstream, test its effects beyond ammonia,
   including pseudo-pure fluids, critical/triple neighborhoods and mixtures as
   applicable. B4A's finite ammonia sample cannot certify those regions.
5. Run the complete accepted A2 checkpoint matrix with unchanged equations,
   conservation, TR-BDF2, Newton/thermal limits, finite differences, temporal
   refinements, frozen independent references, phase/event clocks, domain stops
   and exact rollback. Complete unfinished B2 options/reference coverage.
6. Repeat independent builds and native/browser precision/lifecycle/memory and
   runtime tests. Assess longer supported runs, real Safari/iPad and deployment
   requirements only in separately authorized work. Linux WPE is not an iPad.

Any production backend selection, migration, UI/Live Plant integration, merge,
release or deployment remains outside this research branch and requires explicit
approval after qualification. A bounded A2 pass does not remove these gates.
