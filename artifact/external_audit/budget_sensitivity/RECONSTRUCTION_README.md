# Validated reconstruction + re-sampled budget sensitivity (EX-C3, EX-C5, EX-C6, EX-C7)

This audit re-executes the four expandable Tier-1 compiler records, validates the
re-execution cell-by-cell against the locked N=80 logs, and reports re-sampled
designs at N=160/240/320 only after the gate passes. EX-C1, EX-C2,
EX-C4, EX-C8 are out of scope here (Class A / proxy / host-sensitive — see
`README.md`).

## Toolchain

- Interpreter: Python 3.12.4.
- Locked dependencies: qiskit 2.3.1 and pytket 2.16.0.
- Driver: `recon_driver.py`. It contains the locked transpilation and metric logic
  used for this reconstruction. The earlier long-run orchestration driver is not
  included in the anonymous package; the shipped driver, raw JSONL, per-cell
  inputs, and gate outputs are sufficient to rerun the consolidation check.
- Execution note: each cell is isolated in a subprocess. Running many pytket calls
  in one long-lived process triggers native instability, so the
  dense 10-qubit record (EX-C6) is computed in 20-seed chunks, each in a fresh
  process. The reconstruction gate certifies fidelity regardless of execution
  mechanism.

## Pass/fail criteria (reconstruction gate)

For each record the reconstructed N=80 design is compared against the locked
per-cell log on every cell (matched by `(circuit, opt, seed)` for the line records,
`(random_seed, opt)` for EX-C6):

- **metric_A**, **metric_B** (exact for integer counts/depths; tol `1e-6` for the
  EX-C6 float overheads),
- **signed margin** (`metric_A - metric_B`),
- **preserved / tied / contradicted label**.

- `PASS` — 80/80 on metric values **and** labels. Expansion permitted.
- `LABEL_COMPATIBLE_METRIC_DRIFT` — labels match 80/80 but metric values drift.
  The record is not eligible for expanded k/N.
- `FAIL` — labels disagree on any cell. Expansion **aborted**; the record is a
  reproduction materialization boundary.

## Result: gate

All four records **PASS** (`reconstruction_gate_report.csv`), with **0 rows** in
`reconstructed_vs_locked_diff.csv`:

| Record | metric match | label match | gate |
|---|---|---|---|
| EX-C3 | 80/80 | 80/80 | PASS |
| EX-C5 | 80/80 | 80/80 | PASS |
| EX-C6 | 80/80 | 80/80 | PASS |
| EX-C7 | 80/80 | 80/80 | PASS |

This confirms that the pinned toolchain reproduces the locked logs exactly.

## Result: re-sampled seed expansion (`expanded_seed_sensitivity.csv`)

Expanded designs add **only transpiler seeds** (EX-C3/C5/C7: seeds 0–9 / 0–14 /
0–19; circuits and opt levels fixed) or **only random instance seeds** (EX-C6:
seeds 0–39 / 0–59 / 0–79; opt levels fixed). No new circuit families, metrics,
baselines, or benchmark scopes are introduced. Seed lists are predeclared
(`range(N)`), outcome-blind, and fixed before computation.

Unlike `external_budget_sensitivity.csv` (which holds `s_hat` fixed and only
recomputes the Wilson width — the manuscript's analytic method), this file reports
the **actually re-sampled** `k/N` from new seeds, so `s_hat` can move.

| Record | N=80 | N=160 | N=240 | N=320 | verdict |
|---|---|---|---|---|---|
| EX-C3 | 62/80 (ŝ=0.775) | 124/160 (0.775) | 184/240 (0.767) | 243/320 (0.759) | Unresolved throughout |
| EX-C5 | 44/80 (0.550) | 91/160 (0.569) | 136/240 (0.567) | 180/320 (0.563) | Unresolved throughout |
| EX-C6 | 34/80 (0.425) | 69/160 (0.431) | 106/240 (0.442) | 144/320 (0.450) | Unresolved throughout |
| EX-C7 | 0/80 (0.000) | 0/160 (0.000) | 0/240 (0.000) | 0/320 (0.000) | Reversed throughout |

**0/4 records change verdict** at any expanded budget. `s_hat` stays within a narrow
band of its N=80 value for the three Unresolved records, and EX-C7 preserves the
claimed direction in **0 of 320** cells (Wilson upper bound tightens from 0.046 at
N=80 to 0.012 at N=320), i.e. the reversal strengthens. EX-C3's non-preserving
cells remain entirely ties (0 contradictions) at every budget.

## Evidence boundaries

- These are re-sampled extensions of an **auditor-constructed sub-scope** (the four
  connectivity-stress circuits for EX-C3/C5/C7; the synthetic dense degree-8
  10-qubit graph for EX-C6), not a reproduction of the source papers' full
  benchmark suites. Verdicts are scoped to that locked surface.
- Expansion adds seeds only. Adding circuit families would be auditor-introduced
  scope and is excluded.
- The gate checks for toolchain drift. All four records match the protected N=80
  metrics and labels at 80/80, so the expanded k/N values are reported. Expansion
  adds N>80 evidence and does not alter the protected N=80 verdicts.
- Protected N=80 values are unchanged: EX-C3 62/80, EX-C5 44/80, EX-C6 34/80,
  EX-C7 0/80 (62 contradictions, 18 ties); verdicts Unresolved / Unresolved /
  Unresolved / Reversed.

## Files

- `reconstruction_gate_report.csv` — per-record gate result.
- `reconstructed_vs_locked_diff.csv` — every mismatching cell (empty = exact match).
- `expanded_seed_sensitivity.csv` — re-sampled k/N, ties, contradictions, Wilson
  bounds, verdict, and verdict-change flag at N=80/160/240/320 (PASS records only).
- `recon_driver.py` — the driver (verify + compute + consolidate modes); default
  verification requires only Python and reads the shipped Tier-1 traces under
  `../tier1_robustness/per_cell_inputs/`.
- `recon_raw/` — raw per-cell reconstruction output (JSONL).

Reviewer verification is read-only and qiskit-free:

```bash
python3 artifact/external_audit/budget_sensitivity/recon_driver.py
```

This default `verify` mode recomputes all three derived tables in memory from
`recon_raw/` and the shipped Tier-1 inputs. Use the explicit `consolidate` mode
only when intentionally replacing the committed tables. The `compute` mode is
the only mode that requires qiskit and pytket.
