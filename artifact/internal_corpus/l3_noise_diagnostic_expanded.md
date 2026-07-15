# L3 Noise Diagnostic (Expanded — 6 regimes, 45 instances)

This file supports the manuscript-facing L3 diagnostic for the RQ3 controlled
validation suite. The active six-regime / 45-instance surface is not combined with
the earlier four-regime configuration, which is not bundled. This diagnostic's outputs are
`l3_noise_diagnostic_data.csv` / `l3_noise_diagnostic_summary.csv`.

## Audit-space construction

| Axis | Status | Levels |
|---|---|---|
| $\mathcal{B}_A/\mathcal{B}_B$ | layer-count contrast at fixed angles | $\mathrm{QAOA}_{p=2}$ vs $\mathrm{QAOA}_{p=1}$ |
| Metric $\mathcal{M}$ | expected cut value | counts-derived |
| Direction | $p=2$ > $p=1$ | margin > 0 when preserving |
| INSTANCE | ACTIVE | 45 deterministic Erdős–Rényi graphs (same pool as L2 sampling) |
| L1 | FIXED | seed_t=0, opt=1, sabre |
| L2 | FIXED | shots=1024, sim_seed=0 |
| L3 noise regime | ACTIVE | 6 regimes: ideal, depol-low, depol-medium, depol-high, readout-heavy, two-qubit-heavy |
| ALGO | FIXED-BY-DESIGN | $\gamma{=}0.8$, $\beta{=}0.4$ |

### L3 noise-model presets

| Regime | $p_1$ | $p_2$ | $r$ |
|---|---:|---:|---:|
| ideal | — | — | — |
| depol-low | 0.0005 | 0.005 | 0.01 |
| depol-medium | 0.001 | 0.01 | 0.02 |
| depol-high | 0.003 | 0.03 | 0.05 |
| readout-heavy | 0.001 | 0.005 | **0.08** |
| two-qubit-heavy | 0.001 | **0.05** | 0.02 |

The last two regimes test asymmetric noise-channel emphasis.

**Cell construction**: 45 × 6 = **270 cells per claim**.

## Outputs

- `paper/output/figures/section5/l3_noise_diagnostic_data.csv` — 810 per-cell rows.
- `paper/output/figures/section5/l3_noise_diagnostic_summary.csv` — 3 claims.

## Results

| Claim | $\delta$ | $k/N$ | $\hat{s}$ | CI | Class. | Bootstrap |
|---|---|---|---:|---|---|---|
| L3-C1 | 0.00 | 178/270 | 0.659 | [0.601, 0.713] | Unresolved | 1000/1000 |
| L3-C2 | 0.01 | 174/270 | 0.644 | [0.586, 0.699] | Unresolved | 1000/1000 |
| L3-C3 | 0.05 | 147/270 | 0.544 | [0.485, 0.603] | Unresolved | 1000/1000 |

The expanded six-regime ladder confirms the legacy four-regime
finding: depolarizing + readout magnitudes in the tested range do
not flip the fixed-angle QAOA layer-count comparison; the asymmetric
readout-heavy and two-qubit-heavy regimes do not break the
between-instance-dominated regime either.

## Evidence boundaries

Same as the legacy L3 diagnostic: controlled simulator only, no live
hardware, no amplitude/phase damping, no crosstalk, no calibration
drift. Section VII Threats already disclaims these as future work.
