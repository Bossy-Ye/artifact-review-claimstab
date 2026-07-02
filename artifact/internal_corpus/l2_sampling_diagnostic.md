# L2 Sampling Diagnostic

Controlled internal diagnostic isolating the L2 (execution / finite-shot
sampling) axis of the CLAIMSTAB-QC audit space. Not external evidence.

## Audit-space construction

| Axis | Status | Levels |
|---|---|---|
| $\mathcal{B}_A/\mathcal{B}_B$ | layer-count contrast at fixed angles | $\mathrm{QAOA}_{p=2}$ vs $\mathrm{QAOA}_{p=1}$ |
| Metric $\mathcal{M}$ | expected cut value | computed from `counts` |
| Direction | $p=2$ > $p=1$ | margin > 0 when preserving |
| INSTANCE | ACTIVE | 45 deterministic Erdős–Rényi graphs: $n \in \{8,10,12\}$ × $p \in \{0.2,0.3,0.4\}$ × seeds $\{0..4\}$ |
| L1 transpiler seed | FIXED | 0 |
| L1 optimization level | FIXED | 1 |
| L1 layout method | FIXED | sabre |
| L2 shots | ACTIVE | $\{128, 512, 1024, 4096\}$ |
| L2 simulator seed | ACTIVE | $\{0, 1, 2, 3, 4, 5, 6, 7, 8, 9\}$ |
| L3 | FIXED | ideal Aer simulator |
| ALGO | FIXED-BY-DESIGN | $\gamma{=}0.8$, $\beta{=}0.4$ (no optimizer loop) |
| timing | not applicable |

**Cell construction**: 45 instances × 4 shot levels × 10 simulator seeds = **1,800 cells per claim**.

## Outputs

- `paper/output/figures/section5/l2_sampling_diagnostic_data.csv` — 5,400 per-cell rows.
- `paper/output/figures/section5/l2_sampling_diagnostic_summary.csv` — 3 claims.

## Results

| Claim | $\delta$ | $k/N$ | $\hat{s}$ | CI | Class. | Bootstrap |
|---|---|---|---:|---|---|---|
| L2-C1 | 0.00 | 1074/1800 | 0.597 | [0.574, 0.619] | Unresolved | 1000/1000 |
| L2-C2 | 0.01 | 1057/1800 | 0.587 | [0.564, 0.610] | Unresolved | 1000/1000 |
| L2-C3 | 0.05 | 941/1800 | 0.523 | [0.500, 0.546] | Unresolved | 1000/1000 |

## Limitations

1. The fixed-angle QAOA pair is the same comparator used in the
   existing canonical Blocks B / D / F; this diagnostic is **not** a
   test of QAOA optimization but a test of whether finite-shot
   sampling alone shifts the layer-count direction.
2. L1 / L3 / ALGO are pinned. Verdicts are scope-relative.
3. Shots range capped at 4096 (sufficient to demonstrate the
   between-instance-dominated regime). Larger shot counts would
   reduce sampling noise further but not alter the verdict at the
   resolution shown.
