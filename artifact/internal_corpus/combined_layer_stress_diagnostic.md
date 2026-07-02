# Combined-Layer Stress Diagnostic

Controlled internal diagnostic that exercises **L1, L2, and L3 jointly**
to probe multi-layer interaction effects on the same QAOA layer-count
claim used by the other RQ3 diagnostics.

## Audit-space construction

| Axis | Status | Levels |
|---|---|---|
| $\mathcal{B}_A/\mathcal{B}_B$ | layer-count contrast at fixed angles | $\mathrm{QAOA}_{p=2}$ vs $\mathrm{QAOA}_{p=1}$ |
| Metric $\mathcal{M}$ | expected cut value | counts-derived |
| Direction | $p=2$ > $p=1$ | margin > 0 when preserving |
| INSTANCE | ACTIVE | 20 deterministic Erdős–Rényi graphs ($n=10$, $p \in \{0.2,0.3,0.4\}$, seeds 0–6 / 0–6 / 0–5) |
| L1 regime | ACTIVE | 4 regimes (see below) |
| L2 shots | ACTIVE | $\{512, 1024\}$ |
| L2 simulator seed | ACTIVE | $\{0, 1, 2\}$ |
| L3 noise regime | ACTIVE | $\{ideal, depol\text{-}medium, depol\text{-}high\}$ |
| ALGO | FIXED-BY-DESIGN | $\gamma{=}0.8$, $\beta{=}0.4$ |

### L1 regimes (joint opt × layout × basis)

| Regime | `opt_level` | `layout_method` | `basis_gates` |
|---|---:|---|---|
| default-low | 0 | trivial | default `{u, cx}` |
| sabre-mid | 1 | sabre | default |
| dense-high | 3 | dense | default |
| constrained-basis | 3 | sabre | `{rz, sx, cx}` |

**Cell construction**: 20 instances × 4 L1 regimes × 2 shot levels × 3 simulator seeds × 3 noise regimes = **1,440 cells per claim**.

**Deviation from request**: 20 instances instead of the requested 45,
to keep the noisy simulator runtime within the budget (≈ 5 minutes
vs ≈ 12 minutes at 45 instances).

## Outputs

- `paper/output/figures/section5/combined_layer_diagnostic_data.csv` — 4,320 per-cell rows.
- `paper/output/figures/section5/combined_layer_diagnostic_summary.csv` — 3 claims.

## Results

| Claim | $\delta$ | $k/N$ | $\hat{s}$ | CI | Class. | Bootstrap |
|---|---|---|---:|---|---|---|
| COMB-C1 | 0.00 | 866/1440 | 0.601 | [0.576, 0.626] | Unresolved | 1000/1000 |
| COMB-C2 | 0.01 | 850/1440 | 0.590 | [0.565, 0.615] | Unresolved | 1000/1000 |
| COMB-C3 | 0.05 | 723/1440 | 0.502 | [0.476, 0.528] | Unresolved | 1000/1000 |

The joint L1 × L2 × L3 perturbation surface yields essentially the
same direction-preservation rate as the L2-only sampling diagnostic
($\hat{s}$ in [0.50, 0.60] for both). No additional multi-layer
interaction effect is observed at the controlled diagnostic level.
INSTANCE between-instance heterogeneity remains dominant.

## Limitations

1. The four L1 regimes are illustrative, not exhaustive. The
   `constrained-basis` regime is the only one that exercises
   basis-gate variation jointly with opt-level and layout.
2. Reduced instance pool (20 vs 45) is documented as a runtime
   deviation.
3. L3 noise regimes are a subset of the expanded six-regime L3
   diagnostic (ideal, depol-medium, depol-high). The two asymmetric
   regimes are not tested jointly with L1+L2.
4. ALGO remains fixed by design (layer-count claim).
