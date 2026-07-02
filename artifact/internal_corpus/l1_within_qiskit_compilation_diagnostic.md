# L1 Within-Qiskit Compilation Diagnostic

This is the **main RQ3 L1 evidence**. It replaces the asymmetric
cross-compiler `L1-rich` diagnostic, which remains in the artifact
as exploratory / predecessor evidence (see "Predecessor" below).

## Audit-space construction

Both baselines run on Qiskit, the same input circuit, the same
transpiler seed, the same coupling map, and the same basis gates.
**Only the L1 regime differs.**

| Aspect | Baseline A (high-opt) | Baseline B (low-opt) |
|---|---|---|
| Compiler / tool | Qiskit `transpile()` (Qiskit 2.4.0) | Qiskit `transpile()` (Qiskit 2.4.0) |
| `optimization_level` | **3** | **0** |
| `layout_method` | **`sabre`** | **`trivial`** |
| `seed_transpiler` | varied (active L1 axis; same value as Baseline B per cell) | same as Baseline A |
| `coupling_map` | per cell (active axis: linear or ring) | identical to Baseline A in that cell |
| `basis_gates` | per cell (active axis: `{u,cx}` or `{rz,sx,cx}`) | identical to Baseline A in that cell |

### Claims

- **L1Q-C1**: Baseline A produces strictly fewer two-qubit gates than Baseline B (`margin = B − A > 0`).
- **L1Q-C2**: Baseline A produces strictly lower total circuit depth than Baseline B.
- **L1Q-C3**: Baseline A produces strictly lower two-qubit depth than Baseline B.

### Active axes

| Axis | Status | Levels |
|---|---|---|
| INSTANCE | ACTIVE | 30 deterministic circuits (10 GHZ at $n\in\{4,5,6,7,8,9,10,11,12,14\}$; 10 hardware-efficient $n=6$ d=3 seeds 0–9; 10 hardware-efficient $n=10$ d=3 seeds 0–9) — same pool as the L1-rich predecessor |
| L1 regime | the comparator (A vs B) | 2 regimes: A `(opt=3, sabre)` vs B `(opt=0, trivial)` |
| Transpiler seed | ACTIVE (joint A/B) | $\{0,1,\dots,9\}$, both baselines use the **same** seed per cell |
| Coupling topology | ACTIVE (joint A/B) | $\{linear, ring\}$ |
| Basis regime | ACTIVE (joint A/B) | $\{$ `u_cx` $= \{u, cx\}$; `rz_sx_cx` $= \{rz, sx, cx\}$ $\}$ |
| L2 / L3 / ALGO / timing | inactive | (structural metric) |

**N construction**: 30 instances × 10 seeds × 2 topologies × 2 basis regimes = **1,200 cells per claim**; 3 claims × 1,200 = 3,600 per-cell rows total.

## Outputs

- `paper/output/figures/section5/l1_within_qiskit_diagnostic_data.csv` — 3,600 per-cell rows.
- `paper/output/figures/section5/l1_within_qiskit_diagnostic_summary.csv` — 3 claims with extra columns (`n_margin_gt0`, `n_margin_eq0`, `n_margin_lt0`, `tie_rate`).

## Results

### Direction-preservation + Wilson classification

| Claim | $k/N$ | $\hat{s}$ | Wilson 95% CI | Class. | Cluster bootstrap |
|---|---|---:|---|---|---|
| L1Q-C1 | 0/1200 | 0.000 | [0.000, 0.003] | **Reversed** | 1000/1000 |
| L1Q-C2 | 400/1200 | 0.333 | [0.307, 0.360] | **Unresolved** | 1000/1000 |
| L1Q-C3 | 0/1200 | 0.000 | [0.000, 0.003] | **Reversed** | 1000/1000 |

### Tie analysis

| Claim | $\text{margin} > 0$ (A < B) | $\text{margin} = 0$ (tie) | $\text{margin} < 0$ (A > B) | Tie rate |
|---|---:|---:|---:|---:|
| L1Q-C1 (two-qubit count) | 0/1200 (0.0%) | **1200/1200 (100.0%)** | 0/1200 (0.0%) | 100.0% |
| L1Q-C2 (total depth) | 400/1200 (33.3%) | 400/1200 (33.3%) | 400/1200 (33.3%) | 33.3% |
| L1Q-C3 (two-qubit depth) | 0/1200 (0.0%) | **1200/1200 (100.0%)** | 0/1200 (0.0%) | 100.0% |

## Interpretation

- **L1Q-C1 (two-qubit count)** and **L1Q-C3 (two-qubit depth)**: Baseline A and Baseline B produce **identical** structural 2q-count / 2q-depth values on every single cell — a 100% tie rate. The high-opt regime (opt=3, sabre) and the low-opt regime (opt=0, trivial) yield the same 2q structure on this instance pool, because GHZ-style linear-CX entanglement and the hardware-efficient circuits used here are already 2q-minimal under either coupling topology and either basis. The Reversed verdict is driven entirely by ties + the strict-inequality direction-preservation rule, not by Baseline B beating Baseline A. The honest reading is: **"on this instance pool, Qiskit's L1 regime does not change the structural 2q-count or 2q-depth"**.
- **L1Q-C2 (total depth)**: a clean three-way split — Baseline A wins 33.3%, ties 33.3%, loses 33.3%. The Wilson CI [0.307, 0.360] sits below $\tau = 0.95$ and above $1 - \tau = 0.05$, yielding Unresolved within audited scope. The high-opt regime does not consistently produce shorter total circuit depth on this pool: opt=3 may reorder 1q gates and add 1q decompositions that lengthen the depth on some instances.

The verdicts are scope-relative to the chosen instance pool and the linear / ring topology targets; a different pool (e.g., with non-linear connectivity needs) would likely show non-trivial 2q-count differences between the L1 regimes.

## Failures

**0 failures.** All 1,200 cells transpiled successfully for both regimes. No cells were silently skipped. `layout_method='trivial'` succeeded on every (circuit, coupling map) pair because each test circuit has at most 14 qubits and each coupling map provides ≥ that many physical qubits with sufficient connectivity for Qiskit's routing pass at opt=0 to insert SWAPs as needed.

## Design controls

Both baselines run on the same compiler (Qiskit) and the same fixed linear
coupling map, so the comparison isolates the L1 regime; the compilation is
perturbed per cell by the L1 grid (optimization level $\times$ transpiler seed);
and the integer-metric tie collapse on structural metrics is disclosed explicitly
via the `n_margin_eq0` / `tie_rate` columns above.

## Reproducibility

```
./venv/bin/python paper/experiments/scripts/run_rq3_l1_within_qiskit_diagnostic.py
```

Approximate runtime: ~14 s on a standard laptop (single process).
Outputs are deterministic given the fixed seed configuration.

## Limitations

1. **Tie-dominated regime on 2q metrics**. For 2q-count and 2q-depth, the chosen instance pool produces 100% ties; the diagnostic does not distinguish the two L1 regimes on those metrics. A pool with non-linear connectivity requirements (e.g., random ER graphs, all-to-all-coupled QAOA) would expose L1-regime differences more directly.
2. **Two L1 regimes only**. The diagnostic compares the extreme cases (opt=3+sabre vs opt=0+trivial); intermediate L1 settings (opt=1, opt=2; layout=dense) are not exercised. They are exercised in the predecessor L1-rich diagnostic and in the combined-layer COMB-C1..C3 diagnostic.
3. **Instance pool excludes QFT** (carried over from the L1-rich predecessor for runtime reasons).
4. **Scope-relative verdicts**. Verdicts are reported as Reversed within audited scope; they are not generalizations about Qiskit's L1 behavior outside the audited pool / topologies / basis regimes.
