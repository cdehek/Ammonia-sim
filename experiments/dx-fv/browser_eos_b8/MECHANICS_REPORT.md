# Mechanic’s Report

**Our present five-section evaporator does not use the failing density-and-pressure CoolProp lookup.** It uses the accepted property table. That matters when deciding what should stop development today.

Think of the coil as five refrigerant pots exchanging heat with tube metal, fins and a finite air volume. Each pot stores ammonia mass and internal energy in a fixed volume. The solver must repeatedly turn that stored inventory back into pressure, temperature and enthalpy. It also needs pressure/enthalpy lookups and saturation values to calculate flow, boiling and the outlet condition.

The four unresolved **DU** cases concern that necessary inventory-recovery job, but specifically in the experimental CoolProp full-VLE configuration near the 35-bar saturation boundary. Three still refuse the calculation; the fourth returns a numerical liquid without an independently qualified physical phase. They are real problems for that configuration. They are not proof that the accepted table-backed evaporator currently stalls on those exact inventories.

A refusal at startup can prevent loading the coil. A refusal after a Newton solve can reject that trial and force the original timestep halving. If it persists, the calculation stops numerically at the original minimum step. It must retain the last accepted refrigerant charge, energy, metal/air temperatures and event clock. C1’s saved tests demonstrate that behavior using clearly labeled injected property faults. They do not demonstrate a real coil trajectory reaching these exact endpoint cases.

The **11 DP** failures are a different job: asking for a raw CoolProp state from density and pressure. Both browsers return an impossible boiling fraction in these diagnostics; eight full-VLE inputs do the same natively, and three default inputs differ from native endpoint rounding. We traced the actual accepted source and a short unchanged run. There is no implemented DP route into the model or its adapter. Keep those states rejected and documented, but do not hold unrelated evaporator work hostage to repairing an unused lookup.

The **35-bar boundary problem stays on the board separately**. Seven saved default refusals per browser can arise from exactly the same charge/energy arithmetic used to initialize five sections. Two other saved inventories can return an apparently in-range pressure even though their exact-inventory mathematical diagnostics point outward. C1 does not detect those inward-return hazards. A rounded pressure reading below 35 bar is not a certificate that the stored charge/energy is physically supported. The missing complete phase/topology proof also remains open.

The correct operator message for an unresolved property recovery is a **numerical/property stop**, not a claim that the plant has physically crossed its operating envelope. Genuine independently checked thermal-limit stops remain different. A solver refusal must never create an invented liquid fraction, dry vapor state or corrected refrigerant inventory.

The final outlet and “wet” indication describe bulk refrigerant at the terminal section/port. Accepted A2 has no compressor model that removes entrained liquid or guarantees safe dry suction. If the property calculation fails, we cannot fill in a reassuring suction condition. Even a valid bulk dry indication would not prove real compressor protection.

**Recommended next job:** test running initialization and coil physics in a dedicated browser worker, still isolated and nonqualified. B7 measured main-thread campaign stalls around 1.5–1.8 seconds; that can make an operator panel feel frozen. Existing worker campaigns showed much smaller gaps, but the whole five-section workload and its error reporting still need a bounded study. Keep every scientific refusal, original charge/energy ledger and rollback rule intact.

This triage passes because we can distinguish the operating dependencies from diagnostic exposure. It does not qualify the four DU endpoints, DP, exact-boundary acceptance or the complete browser evaporator. No repair, production integration or next milestone starts automatically.
