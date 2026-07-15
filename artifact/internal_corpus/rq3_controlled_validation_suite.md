# RQ3 Controlled Audit-Space Validation Suite

This document describes the **controlled RQ3 validation suite** used
to exercise the Section III audit-space taxonomy (INSTANCE, L1, L2,
L3, ALGO) under reproducible, simulator-only conditions. The suite
operates **alongside** the existing canonical C1–C24 and synthetic
calibration evidence, and does not modify the external EX-C audits
or any RQ2 results.

The suite produces five diagnostics (15 claims) totalling 16,830
audit cells over a shared family / instance basis.

## Purpose

The audit-space taxonomy in Section III declares L1 / L2 / L3 / ALGO
as separable perturbation layers, but the existing canonical
diagnostics primarily exercise compilation-side L1 (`opt_level ×
transpiler_seed × layout_method`). This suite extends the controlled
diagnostic coverage by isolating each layer in its own claim family
and by adding a combined-layer stress claim.

## Why two families

- **Software-stack / structural circuit family** is the natural home
  for the within-Qiskit L1 diagnostic (L1Q-C1/C2/C3): structural
  metrics (two-qubit gate count, depth, two-qubit depth) are
  L2-/L3-/ALGO-irrelevant and let the L1 axes vary cleanly.
- **MaxCut / QAOA family** is the natural home for L2, L3, ALGO, and
  combined-layer diagnostics: the metric depends on quantum execution
  and on optimization initialization, so the L2 / L3 / ALGO axes
  have measurable effects.

## Section III mapping

| Section III layer | Diagnostic that exercises it |
|---|---|
| INSTANCE / $\mathcal{S}_{\textit{scope}}$ | All five diagnostics (10–45 instances) |
| L1 transpiler seed / opt level / layout / basis | L1Q within-Qiskit (structural) + Combined |
| L2 shots / simulator seed | L2 sampling + Combined |
| L3 noise model | L3 noise + Combined |
| ALGO optimizer / init seed | ALGO |

## Instance pools

### L1Q within-Qiskit diagnostic (30 structural circuits)

- 10 GHZ circuits at $n \in \{4,5,6,7,8,9,10,11,12,14\}$
- 10 hardware-efficient circuits at $n=6$, depth 3, seeds 0–9
- 10 hardware-efficient circuits at $n=10$, depth 3, seeds 0–9

**Documented boundary:** QFT circuits are excluded from the structural pool because
Pytket's `DefaultMappingPass` routes QFT through a linear architecture with high
SWAP overhead (depth quadratic in $n$). The retained pool covers both linear-CX
entanglement and random parametric layers within the controlled simulator budget.

### MaxCut pool — 45 deterministic Erdős–Rényi graphs

Built from `make_maxcut_pool_45()` in `_rq3_shared.py`:

```
n ∈ {8, 10, 12}  ×  p ∈ {0.2, 0.3, 0.4}  ×  seeds {0, 1, 2, 3, 4}  =  45 instances
```

Used directly by L2 sampling and L3 noise. ALGO and Combined use
20- or 30-instance subsets (documented deviations) to keep runtime
within the simulator budget.

## Axis-level choices

Each diagnostic documents its exact axis levels in the corresponding
`*_diagnostic_data.csv` (per-cell measurements) and
`*_diagnostic_summary.csv` (per-claim Wilson outcomes). Concrete
choices:

- **L1Q within-Qiskit**: Baseline A = `(optimization_level=3,
  layout_method=sabre)`; Baseline B = `(optimization_level=0,
  layout_method=trivial)`. Both Qiskit, same coupling map and basis
  per cell. Active axes: `transpiler_seed ∈ {0..9}` (joint A/B),
  coupling topology $\in \{linear, ring\}$, basis regime $\in
  \{\{u,cx\}, \{rz,sx,cx\}\}$.
- **L2 sampling**: `shots ∈ {128, 512, 1024, 4096}`, `sim_seed ∈
  {0..9}`. Comparator is fixed-angle QAOA $p{=}2$ vs $p{=}1$.
- **L3 noise**: six regimes — ideal, depol-low (p1=0.0005, p2=0.005,
  r=0.01), depol-medium (p1=0.001, p2=0.01, r=0.02), depol-high
  (p1=0.003, p2=0.03, r=0.05), readout-heavy (p1=0.001, p2=0.005,
  r=0.08), two-qubit-heavy (p1=0.001, p2=0.05, r=0.02).
- **ALGO**: `optimizer ∈ {COBYLA, Nelder-Mead, Powell}`,
  `init_seed ∈ {0..9}`, `maxiter=30` fixed. Comparator is
  *optimized* QAOA $p{=}2$ vs $p{=}1$ (Statevector expectation; no
  L2 sampling axis).
- **Combined**: L1 regimes = `{default-low, sabre-mid, dense-high,
  constrained-basis}`, `shots ∈ {512, 1024}`, `sim_seed ∈ {0,1,2}`,
  noise ∈ {ideal, depol-medium, depol-high}.

## $N$ construction

| Diagnostic | Per-claim $N$ | Construction |
|---|---:|---|
| L1Q within-Qiskit (structural) | 1,200 | 30 instances × 10 transpiler seeds × 2 coupling topologies × 2 basis regimes; Baseline A = (opt=3, sabre) vs Baseline B = (opt=0, trivial) |
| L2 sampling | 1,800 | 45 instances × 4 shots × 10 sim seeds |
| L3 noise | 270 | 45 instances × 6 noise regimes |
| ALGO | 900 | 30 instances × 3 optimizers × 10 init seeds |
| Combined | 1,440 | 20 instances × 4 L1 regimes × 2 shots × 3 sim seeds × 3 noise regimes |

Each diagnostic produces three claims at $\delta \in \{0, 0.01,
0.05\}$ that share the same cell-level measurements (the per-cell
binary `preserves_direction` flag changes with $\delta$).

## Results summary

All counts are reproducible from the locked per-cell CSVs in
`paper/output/figures/section5/*_diagnostic_data.csv`. The aggregate
summary is in
`paper/output/figures/section5/rq3_controlled_validation_summary.csv`.

| Claim | $k/N$ | $\hat{s}$ | Wilson 95% CI | Class. | Bootstrap |
|---|---|---:|---|---|---|
| **L1Q-C1** (two-qubit gate count, A=opt3/sabre < B=opt0/trivial) | 0/1200 | 0.000 | [0.000, 0.003] | **Reversed** (100% ties) | 1000/1000 |
| **L1Q-C2** (depth, A < B) | 400/1200 | 0.333 | [0.307, 0.360] | Unresolved (33% ties) | 1000/1000 |
| **L1Q-C3** (two-qubit depth, A < B) | 0/1200 | 0.000 | [0.000, 0.003] | **Reversed** (100% ties) | 1000/1000 |
| **L2-C1** (p=2 > p=1, δ=0.00) | 1074/1800 | 0.597 | [0.574, 0.619] | Unresolved | 1000/1000 |
| **L2-C2** (p=2 > p=1, δ=0.01) | 1057/1800 | 0.587 | [0.564, 0.610] | Unresolved | 1000/1000 |
| **L2-C3** (p=2 > p=1, δ=0.05) | 941/1800 | 0.523 | [0.500, 0.546] | Unresolved | 1000/1000 |
| **L3-C1** (p=2 > p=1, δ=0.00) | 178/270 | 0.659 | [0.601, 0.713] | Unresolved | 1000/1000 |
| **L3-C2** (p=2 > p=1, δ=0.01) | 174/270 | 0.644 | [0.586, 0.699] | Unresolved | 1000/1000 |
| **L3-C3** (p=2 > p=1, δ=0.05) | 147/270 | 0.544 | [0.485, 0.603] | Unresolved | 1000/1000 |
| **ALGO-C1** (optimized p=2 > p=1, δ=0.00) | 726/900 | 0.807 | [0.780, 0.831] | Unresolved | 1000/1000 |
| **ALGO-C2** (optimized p=2 > p=1, δ=0.01) | 665/900 | 0.739 | [0.709, 0.767] | Unresolved | 1000/1000 |
| **ALGO-C3** (optimized p=2 > p=1, δ=0.05) | 592/900 | 0.658 | [0.626, 0.688] | Unresolved | 1000/1000 |
| **COMB-C1** (p=2 > p=1 under L1+L2+L3, δ=0.00) | 866/1440 | 0.601 | [0.576, 0.626] | Unresolved | 1000/1000 |
| **COMB-C2** (p=2 > p=1 under L1+L2+L3, δ=0.01) | 850/1440 | 0.590 | [0.565, 0.615] | Unresolved | 1000/1000 |
| **COMB-C3** (p=2 > p=1 under L1+L2+L3, δ=0.05) | 723/1440 | 0.502 | [0.476, 0.528] | Unresolved | 1000/1000 |

**Cluster bootstrap.** All 15 RQ3-suite claims pass cluster
bootstrap at 1000/1000 (cluster on `instance_id`), matching the
Wilson classification under instance-cluster resampling. The
manuscript-facing 47-claim aggregate (24 canonical + 8 external + 15
RQ3 suite) is reproduced into
`artifact/results/paper/output/figures/section5/cluster_bootstrap_47.csv` and gives
**47/47** bootstrap-vs-Wilson classification agreement under the
unified `same_classification` field; the earlier four-regime L3
diagnostic is excluded by construction to avoid double-counting the
expanded six-regime L3 claims.

## Empirical observations (descriptive, not new headline claims)

- **L1Q within-Qiskit diagnostic**: on the 30-circuit pool with a
  joint (transpiler seed × topology × basis) grid, the high-opt
  regime (opt=3, sabre) and the low-opt regime (opt=0, trivial) tie
  on every cell for two-qubit gate count and two-qubit depth (100%
  tie rate) — both regimes produce the same structural 2q counts on
  these linear-arch-friendly circuits. Total depth shows a 33/33/33
  split. The L1Q-C1 and L1Q-C3 Reversed verdicts are tie-driven;
  the evidence supports structural neutrality on this pool.
- **L2 sampling**: fixed-angle QAOA $p{=}2$ beats $p{=}1$ in about
  60% of cells across the 45-graph pool at low δ; the rate falls to
  52% at δ=0.05. Sample-noise (shots ∈ {128..4096}) and simulator
  seed do not shift the verdict — between-instance heterogeneity
  dominates.
- **L3 noise**: the six-regime ladder (ideal → readout-heavy →
  two-qubit-heavy) does not flip the verdict; ŝ stays in [0.54,
  0.66]. The expanded L3 family confirms the original L3-Cx finding
  that depolarizing+readout magnitudes in the tested range do not
  reorder fixed-angle QAOA layer-count comparisons.
- **ALGO**: with a real optimizer loop (COBYLA / Nelder-Mead /
  Powell, maxiter=30) and exact statevector expectation,
  $p{=}2$ beats $p{=}1$ in 81% of cells at δ=0 and 66% at δ=0.05 —
  noticeably higher than the fixed-angle baseline. This is the
  expected effect of optimization closing the layer-count gap.
- **Combined**: jointly varying L1 + L2 + L3 keeps ŝ in [0.50,
  0.60] across the three δ values, mirroring the L2 sampling
  diagnostic. No multi-layer interaction effect is observed in this
  controlled regime.

## Limitations

1. **Simulator only**. No live-hardware execution; no provider
   calibration. The L3 noise family is depolarizing + readout,
   intentionally simple; amplitude/phase damping, crosstalk, and
   asymmetric readout are out of scope. Section VII Threats already
   disclaims live hardware as future work.
2. **L1Q uses two architectures (linear, ring)** as joint coupling-topology
   axis. Verdicts are scope-relative to those two targets; other
   architectures (heavy-hex, all-to-all with non-trivial constraints)
   would likely yield different verdicts. The 100% tie rate on
   L1Q-C1/L1Q-C3 is also pool-dependent — a non-linear-friendly pool
   would expose L1-regime differences more directly.
3. **L1 pool excludes QFT** for runtime-budget reasons (see §Instance
   pools). The L1 axis is the diagnostic surface; the pool
   restriction is a runtime trade-off, not a methodological choice.
4. **ALGO uses 30-instance subset** of the 45-instance MaxCut pool;
   Combined uses 20-instance subset. Documented as runtime
   deviations.
5. **Wilson independence assumption** holds across cells within each
   claim. Cluster bootstrap on `instance_id` confirms the Wilson
   classification is robust to instance-cluster resampling.

## Artifact verification and generation boundary

```
python3 artifact/scripts/check_headline_numbers.py
```

This read-only check derives N and k from every shipped cell and crosschecks the 15
claim summaries and five-diagnostic aggregate. The original qiskit-heavy generators
are not bundled.

## Files produced (active manuscript-facing RQ3 suite)

- `artifact/results/paper/output/figures/section5/l1_within_qiskit_diagnostic_data.csv` (3,600 per-cell rows)
- `artifact/results/paper/output/figures/section5/l1_within_qiskit_diagnostic_summary.csv` (3 claims)
- `artifact/results/paper/output/figures/section5/l2_sampling_diagnostic_data.csv` (5,400 per-cell rows)
- `artifact/results/paper/output/figures/section5/l2_sampling_diagnostic_summary.csv` (3 claims)
- `artifact/results/paper/output/figures/section5/l3_noise_diagnostic_data.csv` (810 per-cell rows)
- `artifact/results/paper/output/figures/section5/l3_noise_diagnostic_summary.csv` (3 claims)
- `artifact/results/paper/output/figures/section5/algo_diagnostic_data.csv` (2,700 per-cell rows)
- `artifact/results/paper/output/figures/section5/algo_diagnostic_summary.csv` (3 claims)
- `artifact/results/paper/output/figures/section5/combined_layer_diagnostic_data.csv` (4,320 per-cell rows)
- `artifact/results/paper/output/figures/section5/combined_layer_diagnostic_summary.csv` (3 claims)
- `artifact/results/paper/output/figures/section5/rq3_controlled_validation_summary.csv` (5 diagnostics aggregated)
- `artifact/internal_corpus/rq3_controlled_validation_matrix.csv` (12 parameters × 7 components)
- `artifact/internal_corpus/rq3_controlled_validation_suite.md` (this file)
- `artifact/internal_corpus/l1_within_qiskit_compilation_diagnostic.md` (per-diagnostic note)
- `artifact/internal_corpus/l2_sampling_diagnostic.md`
- `artifact/internal_corpus/l3_noise_diagnostic_expanded.md`
- `artifact/internal_corpus/algo_stochasticity_diagnostic.md`
- `artifact/internal_corpus/combined_layer_stress_diagnostic.md`

## Evidence scope

- **RQ1 evidence is independent of this suite**: 119 included papers, 457 raw
  candidates, 455 final accepted claims, and 8 materialized RQ2 records. The
  76-row T1/T3/T4 file is a retained pre-adjudication census.
- **RQ2 external EX-C audits unchanged**: still 2S / 4U / 2R across
  the 8 source-supported claims; the RQ2 audit summary is unchanged.
- **Existing canonical C1–C24** unchanged; their canonical-forest and
  positioning rows are unaffected.
- **Synthetic calibration** (Wilson coverage 94.97%) unchanged.

## Paper-facing aggregation

RQ3 uses five controlled diagnostics spanning L1 / L2 / L3 / ALGO / combined. The
paper-facing cluster-bootstrap summary is **24 canonical + 8 external + 15 RQ3 suite
= 47/47**. The earlier 35/35 aggregate belongs to the prior four-regime L3
configuration and is retained only as provenance; it is not added to the 47-record
surface.
