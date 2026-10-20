# Proposed next solver investigation

Recommend a separate B14-A0 phase-boundary temporal-error and Jacobian/residual cost investigation. Keep this B13 branch frozen for engineering review; implement no optimization here.

First reproduce the warm section-0 vapor crossing around 0.005375 s, with the same table and conserved state. Attribute the normalized temporal error to mass, internal energy, pressure, enthalpy and each thermal component using detached diagnostic copies only. Compare bounded output-boundary sequences and approved time refinements. Establish whether transition-related rejection is expected physical accuracy demand, constitutive interpolation behavior or an estimator sensitivity before changing the controller. Preserve refusal and accepted partial progress.

Then profile allocation and constitutive arithmetic inside the 21-column signed finite-difference Jacobian. Measure where residual object/array construction and warm PH inverse loops consume CPU. The present data show a large Jacobian envelope and fixture-dependent property cost; they do not identify a proven safe speedup.

Candidate experiments, each needing an isolated equivalence gate, include the existing optional exact thermal columns, equivalent residual assembly/allocation changes, and exact-input reuse with strict ownership/lifetime boundaries. Any change must preserve residual/Jacobian coordinates, stage results, controller decisions, M/U/V, thermal storage, signed fluxes, property failures and conservation. If a mathematically equivalent change shifts binary64 decisions, document it separately and obtain a scientific qualification plan rather than silently replacing accepted behavior. Table inversion replacements, new backends, relaxed tolerances and clipping are outside the proposed first comparison.

Prioritize desktop Chrome/Edge worker tests on nominated ordinary hardware with actual CPU/browser versions, main-thread responsiveness, cancel/dispose behavior, memory/history retention and accepted-state delivery measured separately. Keep the deployed B12 assets and accepted UI horizon frozen. Owner physical-device activity stays separate.

A later bounded horizon increment may be proposed only after reviewing the current phase/conservation evidence, with explicit wall/CPU/memory budgets and stop gates. Do not jump to minutes/hours. Physical progress also requires a separate boundary/coupling/calibration program: feed and suction reservoir dynamics, validated equipment correlations and inventory/energy accounting across components. Solver efficiency and plant realism are distinct acceptance decisions.

Review gate: choose the next diagnostic question, equivalence requirements and bounded horizon protocol. No production merge, deployment or optimization is authorized by this proposal.
