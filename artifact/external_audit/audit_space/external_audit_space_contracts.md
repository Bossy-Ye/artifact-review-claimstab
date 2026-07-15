# External Audit-Space Contracts (EX-C1--EX-C8)

Per-claim contracts that document, for every external T1 audit reported in
Section V-C: claim identity, five-tuple, metric-to-axis
reasoning, the active and inactive perturbation axes, exact instance scope
and cell construction, evidence pointers, and an admissibility verdict.
This file is limited to EX-C1--EX-C8 scalar-directional audit-space
contracts. Relation-specific boundary sweep records, including EX-C9,
are documented under `artifact/external_audit/road_b/` and are not RQ2
scalar Wilson verdicts.

No new empirical values are introduced. Every quantity here is sourced from
existing locked files. Where a value cannot be recovered from those files,
the field is marked **EVIDENCE-GAP** rather than inferred.

**Core principle.** Perturbation axes are selected by the claim's metric,
execution path, source-supported evidence, and the R1–R3 admissibility
protocol (Section III) — not by broad domain label. A compilation claim
does not automatically activate only L1; an optimization claim does not
automatically activate only algorithmic stochasticity; a benchmark claim
does not automatically activate only timing.

**Inactive-axis reason codes.** FIXED-BY-SOURCE (axis pinned by the source
paper's claim scope); METRIC-IRRELEVANT (axis cannot move the metric);
ARTIFACT-UNSUPPORTED (axis would require resources beyond the materialized
artifact); INADMISSIBLE-CHANGES-CLAIM (axis would alter the audited
comparison's identity); EVIDENCE-GAP (insufficient existing evidence to
classify).

**Admissibility verdicts.** CLEAR (evidence sufficient for reviewer
inspection); NEEDS-ARTIFACT-CLARIFICATION (artifact files exist but a
small addition would close ambiguity); NEEDS-MANUSCRIPT-CLARIFICATION (a
short manuscript note would close ambiguity); DESIGN-GAP (the audit-space
design itself has an open question).

Claims are listed in the requested triage order (highest-ambiguity first),
not in numeric order.

---

## EX-C4 — Probability value (Copula-QAOA vs QTG-based AAM-QAOA)

### 1. Claim identity
- **EX-C ID:** EX-C4
- **Anonymized source:** P4 (paper-id `2411.00518v2`, claim `ext_2411_00518v2_claim3`)
- **Domain:** optimization / QAOA / variational
- **Original claim text:** "It should be noted, however, that it achieves significantly better probability values between five and ten items compared to the QTG-based AAM-QAOA, with the global maxima being around 0.9 and 0.55, respectively."
- **Formalized claim:** "For 5–10 item knapsack instances, Copula-QAOA yields higher probability value than QTG-based AAM-QAOA."

### 2. Five-tuple
- **P_fam:** knapsack-instance QAOA benchmarks (Damuna QAOA-with-Grover-mixer repository).
- **P_inst / operational scope:** small knapsack instances with item count `n_items ∈ {6, 7, 8, 9, 10}`, instance generator parameters `c=1023`, `g∈{1,2,3}`, `f=0.3`, `eps=0`, `s=50`; one instance per `(n_items, g)` cell as recorded in the locked perturbation log.
- **P_alg:** QAOA-style ansatz parameters; `optimizer ∈ {bfgs, powell}`; `copula_depth ∈ {1..8}` for Copula-QAOA; `qtg_depth = 1` (fixed by source) for QTG-based AAM-QAOA.
- **P_res:** repository-stored evaluations from the paper's result CSVs; budget is the paper's recorded budget per cell.
- **B_A:** Copula-QAOA (as implemented in the source repository).
- **B_B:** QTG-based AAM-QAOA (as implemented in the source repository).
- **M:** probability value (probability of measuring the global optimum / target eigenstate, as reported in the paper's result CSV).
- **D:** A > B (Copula > QTG) on the audited 5–10 item regime.

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** No. The probability value is read from the paper's pre-computed result files, not recompiled per cell.
- **Finite-shot sampling required?** No. The probability is the paper's own analytic / repository-stored value per `(instance, copula_depth, optimizer)` tuple.
- **Backend/noise modelling required?** No. No backend is executed during the audit; results are parser-backed.
- **Optimizer initialization / algorithmic stochasticity?** Yes. Both `optimizer ∈ {bfgs, powell}` and `copula_depth` vary across cells; these constitute the algorithmic-stochasticity axis in this audit.
- **Host/runtime timing?** No. The metric is value, not timing.

### 4. Active axes
- S_scope / instance scope: `n_items ∈ {6, 7, 8, 9, 10}` (5 values).
- Algorithmic stochasticity: `optimizer ∈ {bfgs, powell}` × `copula_depth ∈ {1..8}` (16 combinations).
- No L1, L2, L3, timing, or resource-budget axis is active in this audit.

### 5. Inactive axes and reasons
- **L1 (compilation):** METRIC-IRRELEVANT — the audited metric is read from the paper's result CSV, not from a re-transpiled circuit.
- **L2 (sampling):** METRIC-IRRELEVANT — the probability values are parser-backed; no finite-shot resampling occurs in the audited path.
- **L3 (backend / noise):** METRIC-IRRELEVANT and ARTIFACT-UNSUPPORTED — the audited surface is repository-stored values, and live hardware execution is explicitly excluded by the perturbation log.
- **Timing / runtime:** METRIC-IRRELEVANT — metric is probability, not wall-clock.
- **Resource budget:** FIXED-BY-SOURCE — budget per `(instance, depth, optimizer)` tuple is the paper's logged budget; alternative budgets are not in the repository.

### 6. Instance scope
- 5 `n_items` values (6–10), one paper-supplied instance per value, recorded in `artifact/results/paper/output/figures/section5/per_claim_perturbations.csv` row `ext_2411_00518v2_claim3` field `scope_perturbation`.
- Instance generator strings preserved verbatim from the locked perturbation log; no replacement instances were introduced.

### 7. Cell construction
- **N = 80** (per `artifact/results/paper/output/figures/section5/external_forest_data.csv`).
- **Axis product:** 5 `n_items` × 8 `copula_depth` × 2 `optimizer` = 80 cells.
- **Axis values:** `n_items ∈ {6,7,8,9,10}`; `copula_depth ∈ {1,2,3,4,5,6,7,8}`; `optimizer ∈ {bfgs, powell}`.
- Verified against `per_claim_perturbations.csv` row `ext_2411_00518v2_claim3` (`alg_stochasticity` field).

### 8. Evidence pointers
- Five-tuple / claim text: `artifact/field_study/claims/extracted_claims_457.csv` (`ext_2411_00518v2_claim3`).
- Tier and adapter: `artifact/external_audit/materialization/materialization_tier_report.md` (row `ext_2411_00518v2_claim3`); `artifact/external_audit/materialization/materialization_tiers_76.csv`.
- Anonymized source mapping (P4): `artifact/external_audit/mapping/source_mapping_anonymized.csv`.
- Per-claim perturbations: `artifact/results/paper/output/figures/section5/per_claim_perturbations.csv`.
- Per-claim audit result: `artifact/results/paper/output/figures/section5/external_forest_data.csv` (row EX-C4: $\hat{s}=0.5625$, CI [0.4534, 0.6659], Unresolved, N=80, k=45).
- Manuscript: Section V-C "Classification outcomes" paragraph; Table IV row EX-C4.

### 9. Admissibility verdict
**NEEDS-MANUSCRIPT-CLARIFICATION.** The probability value metric in this audit is **parser-backed** (read from repository result CSVs), not recomputed by fresh quantum simulation. The omitted L1/L2/L3 axes are honestly omitted because the metric is not regenerated; this is correct, but the manuscript currently labels EX-C4 perturbations as "alg + scope" without explicitly stating that the value source is paper-published per-cell results. A one-sentence note in Table IV (see "Manuscript additions" below) closes this gap.

---

## EX-C2 — Approximation ratio (QTG-based AAM-QAOA vs Copula-QAOA)

### 1. Claim identity
- **EX-C ID:** EX-C2
- **Anonymized source:** P4 (paper-id `2411.00518v2`, claim `ext_2411_00518v2_claim1`)
- **Domain:** optimization / QAOA / variational
- **Original claim text:** "we conduct numerical experiments for our method on the same benchmark instances as for the Copula-QAOA and demonstrate that our method is able to provide higher approximation ratios on a consistent level, that is, without the drop in quality for instance sizes above ten."
- **Formalized claim:** "On the paper's knapsack QAOA benchmarks, QTG-based AAM-QAOA yields higher approximation ratio than Copula-QAOA."

### 2. Five-tuple
- **P_fam:** knapsack-instance QAOA benchmarks (same family as EX-C4).
- **P_inst / operational scope:** 16 paper-supplied knapsack instances spanning `n_items ∈ {5..20}` (verbatim instance strings such as `n_10_c_1023_g_3_f_0.3_eps_0_s_50`, …), as recorded in the locked perturbation log.
- **P_alg:** `optimizer = powell` (fixed); `qtg_depth = 1` (fixed); `copula_depth ∈ {1..5}`.
- **P_res:** repository-stored evaluations; budget is the paper's recorded budget per cell.
- **B_A:** QTG-based AAM-QAOA (source repository).
- **B_B:** Copula-QAOA (source repository).
- **M:** approximation ratio (paper's reported approximation ratio per cell).
- **D:** A > B (QTG > Copula) on the paper's benchmark surface.

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** No. Approximation ratio is read from the paper's result CSVs; no re-transpilation is part of the audited path.
- **Finite-shot sampling required?** No. Approximation ratio per `(instance, copula_depth)` tuple is parser-backed; no fresh sampling.
- **Backend/noise modelling required?** No. No backend is executed during this audit.
- **Optimizer initialization / algorithmic stochasticity?** Yes, but partially fixed by source: `optimizer = powell` and `qtg_depth = 1` are pinned by the paper; the active algorithmic axis is `copula_depth ∈ {1..5}`.
- **Host/runtime timing?** No.

### 4. Active axes
- S_scope / instance scope: 16 knapsack instances.
- Algorithmic stochasticity: `copula_depth ∈ {1..5}`.
- No L1, L2, L3, timing, or resource-budget axis is active.

### 5. Inactive axes and reasons
- **L1 (compilation):** METRIC-IRRELEVANT — metric is repository-stored; no transpilation in the audited path.
- **L2 (sampling):** METRIC-IRRELEVANT — parser-backed value; no finite-shot resampling.
- **L3 (backend / noise):** ARTIFACT-UNSUPPORTED and METRIC-IRRELEVANT — live hardware execution is excluded by the perturbation log; backend noise does not modify a stored value.
- **`optimizer` and `qtg_depth`:** FIXED-BY-SOURCE — pinned at `powell` and `1` respectively by the paper's reported configuration.
- **Timing / runtime:** METRIC-IRRELEVANT.
- **Resource budget:** FIXED-BY-SOURCE.

### 6. Instance scope
- 16 instances (verbatim strings) recorded in `per_claim_perturbations.csv` row `ext_2411_00518v2_claim1` (`scope_perturbation` field).
- Includes `n_items ∈ {5,6,7,8,9,10,…}` per the same field's `n_items: 16 values` enumeration.

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C2).
- **Axis product:** 16 instances × 5 `copula_depth` = 80 cells.
- **Axis values:** instances enumerated above; `copula_depth ∈ {1,2,3,4,5}`.

### 8. Evidence pointers
- Same set as EX-C4 (anonymized source group P4; source-paper repository indirection via `artifact/external_audit/mapping/source_mapping_anonymized.csv`; `materialization_tier_report.md` row `ext_2411_00518v2_claim1`).
- Per-claim audit result: `external_forest_data.csv` row EX-C2: $\hat{s}=1.000$, CI [0.9542, 1.000], Sustained, N=80, k=80.
- Manuscript: Section V-C; Table IV row EX-C2.

### 9. Admissibility verdict
**NEEDS-MANUSCRIPT-CLARIFICATION.** Same structural issue as EX-C4: the approximation ratio is parser-backed, and L1/L2/L3 are honestly METRIC-IRRELEVANT under the materialized audit path. The Table IV label "alg + scope" is correct but does not flag the parser-backed evidence path. A single Table IV note (below) is sufficient; no manuscript number changes.

---

## EX-C8 — Construction time (Cirq vs Qiskit / nearest competitor)

### 1. Claim identity
- **EX-C ID:** EX-C8
- **Anonymized source:** P3 (paper-id `2409.08844v2`, claim `ext_2409_08844v2_claim1`)
- **Domain:** benchmark / toolkit
- **Original claim text:** "Results worth highlighting include Cirq's performance at constructing a set of Hamiltonian simulation circuits (test_DTC100_set_build) in a time 55x faster than the nearest competitor Qiskit."
- **Formalized (narrowed) claim:** "For Hamiltonian-simulation-like circuit construction, Cirq yields lower construction time than Qiskit on the local pairwise constructor surface."

### 2. Five-tuple
- **P_fam:** Hamiltonian-simulation-like circuit construction (benchmark constructor surface; narrowed from the Benchpress `test_DTC100_set_build` test).
- **P_inst / operational scope:** deterministic Hamiltonian-simulation-like circuits at `circuit_size ∈ {4, 6, 8, 10}`.
- **P_alg:** none (construction, not algorithmic execution).
- **P_res:** host-wallclock single-process timing; repetition count `r ∈ {0..19}` for timing aggregation.
- **B_A:** Cirq constructor (as executed under the locked toolchain).
- **B_B:** Qiskit constructor (as executed under the locked toolchain).
- **M:** construction time (host wallclock, seconds).
- **D:** A < B (Cirq < Qiskit).

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** No. Construction time measures circuit-object instantiation, not transpilation.
- **Finite-shot sampling required?** No. No quantum execution.
- **Backend/noise modelling required?** No. No quantum execution.
- **Optimizer / algorithmic stochasticity?** No.
- **Host/runtime timing?** Yes — this is the metric. Timing repetition is the host-aggregation axis.

### 4. Active axes
- S_scope / instance scope: `circuit_size ∈ {4, 6, 8, 10}` (4 sizes).
- Timing/runtime: `timing_repetition ∈ {0..19}` (20 repetitions per cell, used as host-timing aggregation).
- No L1, L2, L3, algorithmic-stochasticity, or alternative-resource-budget axis is active.

### 5. Inactive axes and reasons
- **L1 (compilation):** METRIC-IRRELEVANT — the metric is constructor instantiation time, prior to any compilation step.
- **L2 (sampling):** METRIC-IRRELEVANT — no quantum execution.
- **L3 (backend / noise):** METRIC-IRRELEVANT and ARTIFACT-UNSUPPORTED — explicitly excluded by the perturbation log (`live hardware execution`).
- **Memory profiler / host-hardware-swap:** ARTIFACT-UNSUPPORTED — listed as `excluded_variation_candidates` in the inventory.
- **Algorithmic stochasticity:** METRIC-IRRELEVANT.
- **Resource budget:** FIXED-BY-SOURCE — single-process constructor invocation as the paper's described benchmark mode.

### 6. Instance scope
- 4 sizes: `circuit_size ∈ {4, 6, 8, 10}`, recorded in `per_claim_perturbations.csv` row `ext_2409_08844v2_claim1` (`scope_perturbation` field).
- Note: the published claim cites `test_DTC100_set_build` (DTC at N=100); the audited surface narrows to constructor-only timing across `n ∈ {4,6,8,10}`. This narrowing is logged in `artifact/claim_cards/EX-C8.yaml`.

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C8).
- **Axis product:** 4 circuit sizes × 20 timing repetitions = 80 cells.
- **Axis values:** `circuit_size ∈ {4, 6, 8, 10}`; `timing_repetition ∈ {0..19}`.
- **Per-cell timing protocol (recovered).** Each `(circuit_size, repetition)` tuple is **one audit cell, with no per-cell aggregation**. The locked provenance records a fresh subprocess per cell, one warm-up per constructor, and a single `time.perf_counter()` delta for each constructor; outcome is `cirq_time < qiskit_time`. The 20 `timing_repetition` values are therefore 20 *cells along the timing axis*, not 20 measurements aggregated into one cell. This is corroborated by `artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim1_measurements.csv`, which contains 80 rows and all 80 outcomes equal to `0`, consistent with $\hat{s}=0.000$. The original execution adapter is not bundled.

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2409_08844v2_claim1`.
- `artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim1_measurements.csv` (per-cell timing pairs and `outcome` values; 80 rows).
- `artifact/claim_cards/EX-C8.yaml` (claim text, narrowing rationale, host-timing boundary, and locked result pointer).
- `external_forest_data.csv` row EX-C8: $\hat{s}=0.000$, CI [0.000, 0.0458], Reversed, N=80, k=0.
- Manuscript: Section V-C "Classification outcomes" paragraph; Table IV row EX-C8.

### 9. EVIDENCE-GAP
**Resolved.** Earlier versions of this contract flagged the "per-cell timing aggregation rule" as an EVIDENCE-GAP. The adapter source and per-cell measurements file (cited above) establish that no per-cell aggregation occurs — each `(circuit_size, repetition)` tuple is its own cell with a single `cirq_time` and `qiskit_time` measurement.

### 10. Admissibility verdict
**CLEAR for inspection.** The shipped evidence contains 4 × 20 = 80 single-measurement cells and per-cell outcomes. The original execution adapter is not bundled, so the timing run is not one-command reproducible. The narrowing from `test_DTC100_set_build` is recorded in `artifact/claim_cards/EX-C8.yaml` and reflected in the manuscript's Table IV row label.

---

## EX-C1 — Runtime performance (Pytket vs Qiskit)

### 1. Claim identity
- **EX-C ID:** EX-C1
- **Anonymized source:** P1 (paper-id `2202.14025v1`, claim `ext_2202_14025v1_legacy_claim12`)
- **Domain:** transpiler / compiler
- **Original claim text:** "We found that Pytket with the backend implemented in C++ showed the best runtime performance."
- **Formalized (narrowed) claim:** "For compiler runtime on random circuits, Pytket yields lower runtime than Qiskit on the local pairwise compilation surface."
- **Runtime type:** **compilation runtime** (transpile-pipeline wall-clock from input circuit to compiled output), not construction time and not quantum-execution time.

### 2. Five-tuple
- **P_fam:** random line-coupled circuits across sizes and Qiskit optimization levels.
- **P_inst / operational scope:** `circuit_size ∈ {4, 6, 8, 10}` (4 sizes).
- **P_alg:** Qiskit transpiler stochasticity controlled by `qiskit_optimization_level ∈ {0,1,2,3}` and `random_circuit_seed ∈ {0..4}`.
- **P_res:** host-wallclock single-process; Pytket and Qiskit compiled under the same locked toolchain.
- **B_A:** Pytket (C++ backend) compiler.
- **B_B:** Qiskit transpiler.
- **M:** compilation runtime (host wallclock seconds).
- **D:** Pytket < Qiskit (Pytket faster). Direction `A > B` in the tier CSV is interpreted as "Pytket exceeds Qiskit on the runtime-performance metric" where the metric is encoded such that the published direction is preserved when Pytket is faster; the locked forest data records EX-C1 as Sustained 80/80, consistent with Pytket faster across all cells.

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** Yes — this is the metric (compilation wall-clock). L1 is therefore active by definition.
- **Finite-shot sampling required?** No.
- **Backend/noise modelling required?** No.
- **Optimizer / algorithmic stochasticity?** Partly: `qiskit_optimization_level` and `qiskit_seed` are transpiler-side stochastic and operating-point choices, treated here as part of the L1 (compilation) axis rather than a separate algorithmic axis.
- **Host/runtime timing?** Yes — this is the metric; timing repetition is used for host-noise reduction.

### 4. Active axes
- S_scope / instance scope: `circuit_size ∈ {4, 6, 8, 10}`.
- L1 (compilation): `qiskit_optimization_level ∈ {0,1,2,3}`.
- Timing/runtime: per-cell repeated timing under `repetition ∈ {0..4}` (used for host-wallclock aggregation, not L2 quantum sampling).
- No L2 (quantum sampling), L3 (backend / noise), independent algorithmic-stochasticity, or resource-budget axis.

### 5. Inactive axes and reasons
- **L2 (sampling):** METRIC-IRRELEVANT — compilation runtime does not involve quantum sampling.
- **L3 (backend / noise):** METRIC-IRRELEVANT and ARTIFACT-UNSUPPORTED — live hardware excluded by the perturbation log.
- **PyZX, Cirq comparator backends:** ARTIFACT-UNSUPPORTED — the source claim names Pytket vs Qiskit/PyZX/Cirq, but the audit is narrowed to Pytket-vs-Qiskit (logged in `artifact/claim_cards/EX-C1.yaml`).
- **Host-hardware swap:** ARTIFACT-UNSUPPORTED — explicitly listed as `excluded_variation_candidates`.
- **Independent `algorithmic stochasticity` axis:** METRIC-IRRELEVANT — Qiskit transpiler seed is treated as part of the L1 compilation surface, not as a separate variational-algorithmic axis.
- **Resource budget:** FIXED-BY-SOURCE — fixed invocation budget per cell under the locked toolchain.

### 6. Instance scope
- 4 sizes (`circuit_size ∈ {4, 6, 8, 10}`), random line-coupled circuits, recorded in `per_claim_perturbations.csv` row `ext_2202_14025v1_legacy_claim12` (`scope_perturbation` field).
- Narrowing from the broader Pytket-vs-Qiskit/PyZX/Cirq comparator set is logged in `artifact/claim_cards/EX-C1.yaml`.

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C1).
- **Axis product:** 4 circuit sizes × 4 Qiskit optimization levels × 5 timing repetitions = 80 cells.
- **Axis values:** `circuit_size ∈ {4,6,8,10}`; `qiskit_optimization_level ∈ {0,1,2,3}`; `repetition ∈ {0,1,2,3,4}`.
- **Per-cell timing protocol (recovered).** Each `(circuit_size, qiskit_optimization_level, repetition)` triple is **one audit cell, with no per-cell aggregation**. Locked provenance records a fresh subprocess per cell, deterministic QASM seeded by `rep`, and one timing delta for each compiler. Cell outcome is `pytket_time < qiskit_time`. The 5 repetitions are 5 *cells*, not 5 measurements aggregated into one cell. The original execution adapter is not bundled.
- The locked per-cell measurements file `artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2202_14025v1_legacy_claim12_measurements.csv` contains 80 rows — one per `(circuit_size, repetition, qiskit_optimization_level)` triple — with `pytket_time_seconds`, `qiskit_time_seconds`, and `outcome` columns; all 80 outcomes equal `1` (Pytket faster), consistent with the locked $\hat{s}=1.000$.
- **Schema note on `L2_perturbation` column.** In `per_claim_perturbations.csv`, the third axis for EX-C1 appears under the column header `L2_perturbation` with the value `repetition: 0, 1, 2, 3, 4`. This is a **legacy column name**; the value stored there is a *host timing repetition*, not an L2 quantum sampling perturbation. See "Schema note on `L2_perturbation`" at the end of this document for the canonical reading rule applied across all runtime/timing-style claims.

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2202_14025v1_legacy_claim12`.
- `artifact/claim_cards/EX-C1.yaml` (source claim, narrowing, host boundary, and locked result pointer).
- `artifact/results/paper/output/figures/section5/external_forest_data.csv` row EX-C1 (Sustained aggregate).
- `artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2202_14025v1_legacy_claim12_measurements.csv` (per-cell timing pairs and `outcome` values; 80 rows).
- `external_forest_data.csv` row EX-C1: $\hat{s}=1.000$, CI [0.9542, 1.000], Sustained, N=80, k=80.
- Manuscript: Section V-C "Classification outcomes" paragraph; Table IV row EX-C1.

### 9. EVIDENCE-GAP
**Resolved (cell-construction part).** The adapter source and the per-cell measurements file (cited above) establish that each `(circuit_size, repetition, qiskit_optimization_level)` triple is its own audit cell with a single per-process timing measurement, and that the row in `per_claim_perturbations.csv` labeled `L2_perturbation: repetition: 0,1,2,3,4` is a *legacy-column timing-axis entry*, not an L2 sampling perturbation. The schema note below makes the reading rule explicit. No invented values are introduced.

### 10. Admissibility verdict
**CLEAR.** Runtime type ("compilation runtime") is recoverable from the adapter source (`transpile(...)` and Pytket `DefaultMappingPass(...) → DecomposeSwapsToCXs(...)`), confirming the metric measures compile-pipeline wall-clock, not construction or execution time. The legacy `L2_perturbation` column is documented via the schema note below; no CSV is renamed in this pass.

---

## EX-C7 — Two-qubit gate count (Qiskit vs Tket, narrowed from Qiskit vs BQSKit/Staq/Tket)

### 1. Claim identity
- **EX-C ID:** EX-C7
- **Anonymized source:** P3 (paper-id `2409.08844v2`, claim `ext_2409_08844v2_claim3`)
- **Domain:** transpiler / compiler
- **Original claim text:** "First, we see that, as a whole, Qiskit outperforms BQSKit, Staq, and Tket in terms of 2Q gate count; a trend clearly seen in the BQSKit and Tket data."
- **Formalized (narrowed) claim:** "For transpilation resource benchmarks, Qiskit yields lower two-qubit gate count than Tket on the connectivity-stress surface."
- This is the worked-case study used in Section V-C.

### 2. Five-tuple
- **P_fam:** transpilation resource benchmarking on deterministic connectivity-stress circuits.
- **P_inst / operational scope:** 4 circuits {`linear_3_remote_cx`, `linear_4_bidirectional_mix`, `linear_4_crossing_ladder`, `linear_4_repeated_remote`} on a 4-node line architecture.
- **P_alg:** Qiskit transpiler stochasticity controlled by `qiskit_optimization_level` and `qiskit_seed`; Tket invoked with default mapping/decomposition pipeline.
- **P_res:** artifact-supported compilation budget; single-process invocation.
- **B_A:** Qiskit transpiler.
- **B_B:** Tket mapping/decomposition pipeline.
- **M:** two-qubit (CX) gate count of the compiled circuit.
- **D:** A < B (Qiskit < Tket).

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** Yes — the metric is gate count after compilation. L1 is active.
- **Finite-shot sampling required?** No — gate count is a property of the compiled circuit, not of an execution.
- **Backend/noise modelling required?** No — gate count is independent of backend noise.
- **Optimizer / algorithmic stochasticity?** Qiskit transpiler seed is the relevant transpiler-side stochastic axis, treated as part of L1.
- **Host/runtime timing?** No.

### 4. Active axes
- S_scope / instance scope: 4 circuits.
- L1 (compilation): `qiskit_optimization_level ∈ {0,1,2,3}` × `qiskit_seed ∈ {0,1,2,3,4}`.
- No L2, L3, independent algorithmic-stochasticity, timing, or resource-budget axis.

### 5. Inactive axes and reasons
- **L2 (sampling):** METRIC-IRRELEVANT — gate count is structural, not statistical.
- **L3 (backend / noise):** FIXED-BY-SOURCE — architecture pinned to a single 4-node line topology with edges `[(0,1),(1,2),(2,3)]` (per `per_claim_perturbations.csv` `L3_perturbation` field); live hardware execution excluded by the perturbation log.
- **BQSKit, Staq comparator tools:** ARTIFACT-UNSUPPORTED — original claim names a 4-tool comparison; audit narrows to Qiskit-vs-Tket, as recorded in `artifact/claim_cards/EX-C7.yaml`.
- **Runtime metric:** INADMISSIBLE-CHANGES-CLAIM — switching to runtime would change the audited metric.
- **Timing / runtime:** METRIC-IRRELEVANT.
- **Resource budget:** FIXED-BY-SOURCE.

### 6. Instance scope
- 4 named connectivity-stress circuits, listed verbatim in `per_claim_perturbations.csv` row `ext_2409_08844v2_claim3` (`scope_perturbation` field).
- Architecture: 4-node line `[(0,1),(1,2),(2,3)]` (`L3_perturbation` field — value-fixed, not varied).
- Narrowing from the broader Qiskit vs BQSKit/Staq/Tket comparator set is logged in `artifact/claim_cards/EX-C7.yaml`.

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C7).
- **Axis product:** 4 circuits × 4 `qiskit_optimization_level` × 5 `qiskit_seed` = 80 cells. **This matches the manuscript Section V-C "Worked case study: EX-C7" statement** "80 cells (4 circuits × 4 Qiskit optimization levels × 5 seeds)" — verified against `per_claim_perturbations.csv`.
- **Axis values:** circuits as enumerated; `qiskit_optimization_level ∈ {0,1,2,3}`; `qiskit_seed ∈ {0,1,2,3,4}`.

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2409_08844v2_claim3`.
- `artifact/claim_cards/EX-C7.yaml` (narrowing rationale and admissible variation candidates).
- `artifact/results/paper/output/figures/section5/external_forest_data.csv` row EX-C7 (Reversed aggregate).
- `external_forest_data.csv` row EX-C7: $\hat{s}=0.000$, CI [0.000, 0.0458], Reversed, N=80, k=0.
- Manuscript: Section V-C worked case study, Table V representative cells, Table IV row EX-C7.

### 9. Admissibility verdict
**CLEAR.** The 4 × 4 × 5 = 80 construction in the manuscript is exactly recoverable from `per_claim_perturbations.csv`. The L2 / L3 / runtime / additional-comparator exclusions are each justified by an explicit reason code with an artifact pointer. Table V already shows representative cells from this audit.

---

## EX-C3 — CNOT gate count (TKET vs Qiskit)

### 1. Claim identity
- **EX-C ID:** EX-C3
- **Anonymized source:** P2 (paper-id `2304.08814v2`, claim `ext_2304_08814v2_claim5`)
- **Domain:** transpiler / compiler
- **Original claim text:** "Qiskit and TKET have a similar runtime, where TKET is slightly slower with much better CNOT counts."
- **Formalized claim:** "For DAG-based quantum compilation, TKET yields lower CNOT gate count than Qiskit."

### 2. Five-tuple
- **P_fam:** DAG-based quantum compilation; connectivity-stress benchmark family.
- **P_inst / operational scope:** 4 named circuits (`linear_3_remote_cx`, `linear_4_bidirectional_mix`, `linear_4_crossing_ladder`, `linear_4_repeated_remote`) on a 4-node line architecture.
- **P_alg:** Qiskit transpiler stochasticity (`qiskit_optimization_level`, `qiskit_seed`); TKET default pipeline.
- **P_res:** artifact-supported compilation budget.
- **B_A:** TKET (pytket) compiler.
- **B_B:** Qiskit transpiler.
- **M:** CNOT gate count of the compiled circuit.
- **D:** A < B (TKET < Qiskit).

### 3. Metric-to-axis reasoning
- **Compilation/transpilation required?** Yes. L1 is active.
- **Finite-shot sampling required?** No.
- **Backend/noise modelling required?** No.
- **Optimizer / algorithmic stochasticity?** Qiskit transpiler seed is the transpiler-side stochastic axis (part of L1).
- **Host/runtime timing?** No.

### 4. Active axes
- S_scope: 4 circuits.
- L1: `qiskit_optimization_level ∈ {0,1,2,3}` × `qiskit_seed ∈ {0,1,2,3,4}`.

### 5. Inactive axes and reasons
- **L2 (sampling):** METRIC-IRRELEVANT — CNOT count is structural.
- **L3 (backend / noise):** FIXED-BY-SOURCE — 4-node line architecture `[(0,1),(1,2),(2,3)]`.
- **Runtime metric, phase-polynomial compiler family, hardware noise:** all listed as `excluded_variation_candidates` in the inventory; INADMISSIBLE-CHANGES-CLAIM (would alter the metric or comparator family).
- **Independent algorithmic stochasticity:** METRIC-IRRELEVANT.
- **Resource budget / timing:** METRIC-IRRELEVANT.

### 6. Instance scope
- 4 named circuits per `per_claim_perturbations.csv` row `ext_2304_08814v2_claim5` (`scope_perturbation`).
- Architecture pinned (`L3_perturbation` value-fixed).

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C3).
- **Axis product:** 4 circuits × 4 `qiskit_optimization_level` × 5 `qiskit_seed` = 80 cells.
- Same construction as EX-C5 and EX-C7 (shared connectivity-stress adapter).

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2304_08814v2_claim5`.
- `artifact/claim_cards/EX-C3.yaml` (source claim, narrowing, and result pointer).
- `artifact/results/paper/output/figures/section5/external_forest_data.csv` row EX-C3 (Unresolved aggregate).
- `artifact/external_audit/tier1_robustness/per_cell_inputs/ext_2304_08814v2_claim5_measurements.csv` (80-row per-cell log).
- `external_forest_data.csv` row EX-C3: $\hat{s}=0.775$, CI [0.6721, 0.8527], Unresolved, N=80, k=62.
- Manuscript: Section V-C; Table IV row EX-C3.

### 9. Admissibility verdict
**CLEAR.** Same axis structure as EX-C7 with all reasons resolved via existing artifact pointers.

---

## EX-C5 — Two-qubit gate depth (Tket vs Qiskit)

### 1. Claim identity
- **EX-C ID:** EX-C5
- **Anonymized source:** P3 (paper-id `2409.08844v2`, claim `ext_2409_08844v2_claim4`)
- **Domain:** transpiler / compiler
- **Original claim text:** "while the two-qubit gate depth is worse than Qiskit for BQSKit and Staq, Tket outperforms Qiskit overall, with prominent gains for more connected topologies."
- **Formalized claim:** "For transpilation resource benchmarks, Tket yields lower two-qubit gate depth than Qiskit."

### 2. Five-tuple
- **P_fam:** transpilation resource benchmarking; connectivity-stress family.
- **P_inst / operational scope:** 4 named connectivity-stress circuits (same as EX-C3 / EX-C7).
- **P_alg:** Qiskit transpiler stochasticity (`qiskit_optimization_level`, `qiskit_seed`); Tket default pipeline.
- **P_res:** artifact-supported compilation budget.
- **B_A:** Tket compiler.
- **B_B:** Qiskit transpiler.
- **M:** two-qubit gate depth of the compiled circuit.
- **D:** A < B (Tket < Qiskit).

### 3. Metric-to-axis reasoning
- Same as EX-C3 / EX-C7. Compilation required (L1 active); no L2/L3/timing; transpiler stochasticity treated as part of L1.

### 4. Active axes
- S_scope: 4 circuits.
- L1: `qiskit_optimization_level ∈ {0,1,2,3}` × `qiskit_seed ∈ {0,1,2,3,4}`.

### 5. Inactive axes and reasons
- **L2 (sampling):** METRIC-IRRELEVANT.
- **L3 (backend / noise):** FIXED-BY-SOURCE — 4-node line architecture.
- **BQSKit, Staq, QTS comparator tools:** ARTIFACT-UNSUPPORTED — narrowed to Tket-vs-Qiskit pair (per inventory).
- **Runtime metric, full-Benchpress-suite import:** INADMISSIBLE-CHANGES-CLAIM.
- **Resource budget / timing:** METRIC-IRRELEVANT.

### 6. Instance scope
- 4 named circuits per `per_claim_perturbations.csv` row `ext_2409_08844v2_claim4` (`scope_perturbation`).

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C5).
- **Axis product:** 4 circuits × 4 `qiskit_optimization_level` × 5 `qiskit_seed` = 80 cells.

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2409_08844v2_claim4`.
- `artifact/claim_cards/EX-C5.yaml` (source claim, narrowing, and result pointer).
- `artifact/results/paper/output/figures/section5/external_forest_data.csv` row EX-C5 (Unresolved aggregate).
- `external_forest_data.csv` row EX-C5: $\hat{s}=0.550$, CI [0.4412, 0.6542], Unresolved, N=80, k=44.
- Manuscript: Section V-C; Table IV row EX-C5.

### 9. Admissibility verdict
**CLEAR.** Same axis structure as EX-C3 / EX-C7; all reasons resolved via existing artifact pointers.

---

## EX-C6 — CX depth overhead (Qiskit Transpile vs Pytket DefaultMapping)

### 1. Claim identity
- **EX-C ID:** EX-C6
- **Anonymized source:** P1 (paper-id `2202.14025v1`, claim `ext_2202_14025v1_legacy_claim6`)
- **Domain:** transpiler / compiler
- **Original claim text:** "Both algorithms show somewhat different performance according to CX depth overhead, where Transpile (Qiskit) outperforms DefaultMapping (Pytket) for densely connected graphs with node degrees $k \gtrsim 8$."
- **Formalized claim:** "For routing/mapping on densely connected random k-regular graphs, Qiskit Transpile yields lower CX depth overhead than Pytket DefaultMapping."

### 2. Five-tuple
- **P_fam:** routing/mapping on dense random k-regular coupling graphs.
- **P_inst / operational scope:** dense 10-qubit synthetic coupling graph with degree 8; `n_qubits = 10`; random CX circuits.
- **P_alg:** Qiskit transpiler stochasticity (`qiskit_optimization_level`, `random_seed`).
- **P_res:** artifact-supported compilation budget.
- **B_A:** Qiskit Transpile.
- **B_B:** Pytket DefaultMapping.
- **M:** CX depth overhead.
- **D:** A < B (Qiskit < Pytket on CX depth overhead) under the dense-degree regime audited.

### 3. Metric-to-axis reasoning
- Compilation/transpilation required? Yes (L1 active).
- L2 / L3 / timing not part of the audited metric.

### 4. Active axes
- S_scope: `n_qubits = 10` with `removed_edges` configuration listed; random-circuit instance variation supplied via `random_seed`.
- L1: `qiskit_optimization_level ∈ {0,1,2,3}` × `random_seed ∈ {0..19}` (20 values).

### 5. Inactive axes and reasons
- **L2 (sampling):** METRIC-IRRELEVANT — CX depth overhead is structural.
- **L3 (backend / noise):** FIXED-BY-SOURCE — `removed_edges` configuration fixed to `[(0,1),(2,3),(4,5),(6,7),(8,9)]` (per `per_claim_perturbations.csv` `L3_perturbation` field).
- **Runtime metric, non-dense architecture, full Arline suite import:** all `excluded_variation_candidates` — INADMISSIBLE-CHANGES-CLAIM (would alter the comparator's scope or metric).
- **Independent algorithmic stochasticity:** METRIC-IRRELEVANT — `random_seed` here is the random-circuit instance seed, treated as part of S_scope/L1 jointly.
- **Resource budget / timing:** METRIC-IRRELEVANT.

### 6. Instance scope
- 10-qubit dense synthetic coupling graph with degree 8, `n_qubits = 10` (single-size operational regime).
- Random-circuit variation via `random_seed ∈ {0..19}` (20 values).
- Removed-edges configuration value-fixed in the perturbation log.

### 7. Cell construction
- **N = 80** (per `external_forest_data.csv` row EX-C6).
- **Axis product:** 4 `qiskit_optimization_level` × 20 `random_seed` = 80 cells.
- **Axis values:** `qiskit_optimization_level ∈ {0,1,2,3}`; `random_seed ∈ {0..19}`.

### 8. Evidence pointers
- `per_claim_perturbations.csv` row `ext_2202_14025v1_legacy_claim6`.
- `artifact/claim_cards/EX-C6.yaml` (source claim, narrowing, and result pointer).
- `artifact/results/paper/output/figures/section5/external_forest_data.csv` row EX-C6 (Unresolved aggregate).
- `external_forest_data.csv` row EX-C6: $\hat{s}=0.425$, CI [0.3226, 0.5343], Unresolved, N=80, k=34.
- Manuscript: Section V-C; Table IV row EX-C6.

### 9. Admissibility verdict
**CLEAR.** Axis product 4 × 20 = 80 is recoverable from the perturbation log. `random_seed` is correctly treated jointly with L1 transpiler stochasticity (S_scope at the random-circuit instance level), not as a separate algorithmic axis, because the underlying graph is value-fixed.

---

## Cross-claim summary

| EX-C | Active axes | Admissibility | EVIDENCE-GAP |
|---|---|---|---|
| EX-C4 | scope, alg(opt+depth) | CLEAR (after Table IV note) | none |
| EX-C2 | scope, alg(depth) | CLEAR (after Table IV note) | none |
| EX-C8 | scope, timing | CLEAR | none |
| EX-C1 | scope, L1, timing | CLEAR | none (schema note below) |
| EX-C7 | scope, L1 | CLEAR | — |
| EX-C3 | scope, L1 | CLEAR | — |
| EX-C5 | scope, L1 | CLEAR | — |
| EX-C6 | scope (joint with seed), L1 | CLEAR | — |

The two remaining post-Phase-2 artifact issues were closed in this pass:
EX-C8's per-cell aggregation rule is recovered from the adapter source and
the locked `*_measurements.csv` file (no aggregation — each
`(circuit_size, repetition)` is one cell); EX-C1's `L2_perturbation`
legacy-column overload is documented in the schema note below.

## Manuscript additions

A single compact Table IV note is sufficient to absorb the
NEEDS-MANUSCRIPT-CLARIFICATION verdicts for EX-C2 and EX-C4, and to give
reviewers a top-level pointer for the inactive-axis reasons used here:

> "Listed perturbations are admitted source-supported audit-space
> dimensions; omitted axes are fixed or excluded when metric-irrelevant,
> artifact-unsupported, or outside the audited comparison."

This note is in place in `paper/manuscript/ClaimStab/tables/section5/per_claim_external_audit.tex`.

No Table IV data is changed. No numerical results are changed.

## Schema note on `L2_perturbation` in `per_claim_perturbations.csv`

The file `artifact/results/paper/output/figures/section5/per_claim_perturbations.csv` is a
**legacy-column derivative** of the per-claim audit runs. Its column
schema is fixed across all 8 EX-C rows and carries one column per
canonical perturbation layer: `scope_perturbation`, `L1_perturbation`,
`L2_perturbation`, `L3_perturbation`, `alg_stochasticity`,
`excluded_perturbations`.

For runtime/timing-style claims — EX-C1 (`ext_2202_14025v1_legacy_claim12`)
and EX-C8 (`ext_2409_08844v2_claim1`) — the `L2_perturbation` column
**carries timing-repetition values** (e.g., `repetition: 0, 1, 2, 3, 4` for
EX-C1 and `repetition: 20 values (0..19)` for EX-C8). These values are
**host-wallclock timing repetitions**, not L2 quantum execution/sampling
perturbations:

- EX-C1's compilation-runtime metric never executes a quantum sampling
  step, so there is no L2 sampling axis to populate.
- EX-C8's construction-time metric never executes any quantum step, so
  there is no L2 sampling axis to populate.

The audit-space contracts in this file therefore classify those
`L2_perturbation` entries under **`timing / runtime`**, not under L2
execution/sampling. In every contract above, the L2 (quantum sampling)
inactive-axis reason is **METRIC-IRRELEVANT** for runtime/timing claims,
and the timing axis appears as a separate active axis. This preserves the
manuscript interpretation that L2 quantum sampling is inactive /
metric-irrelevant for EX-C1 and EX-C8.

**Reading rule for reviewers.** When inspecting
`per_claim_perturbations.csv` directly, any value in the
`L2_perturbation` column for runtime/timing-style claims should be read
as a timing-repetition axis, not as a finite-shot sampling axis. The
authoritative per-cell evidence is in the corresponding
`artifact/external_audit/tier1_robustness/per_cell_inputs/<claim_id>_measurements.csv`
file. The original execution adapters are not bundled in the anonymous artifact.

No CSV columns are renamed and no CSV data is altered in this pass. The
schema note is documentation of the existing legacy schema, not a data
change.
