# Canonical C1–C24 Audit-Space Construction

This file is the reviewer-facing audit-space construction record for the
24 canonical / internal-corpus claims that appear in Section V-D as part of the
RQ3 controlled-validation evidence. C1–C24 are **canonical
internal-corpus claims, not synthetic claims and not external published
claims**. They are designed to exercise specific CLAIMSTAB-QC
audit-space constructions $\mathcal{S}_{\textit{audit}} =
\mathcal{S}_{\textit{scope}} \times \mathcal{E}_{\textit{env}}$ under
controlled conditions. The synthetic calibration corpus described in
Section V-D is a separate Wilson / S-U/R classifier test; it does not
exercise L1/L2/L3/INSTANCE coverage.

## 1. Purpose

For each canonical claim, this note records:

- which axes of $\mathcal{S}_{\textit{audit}}$ are **active**;
- which axes are **fixed by design**, **fixed by source**, or **outside
  the controlled diagnostic purpose**;
- which axes are **metric-irrelevant**, **folded into INSTANCE scope**,
  or **folded into precomputed scores**;
- which axes are **evidence gaps** if any.

The goal is to make the canonical experiment design complete enough
that reviewers can decide whether the design is appropriate without
opening the full-repository cell-construction code.

## 2. Shipped evidence and original provenance

| File | Role |
|---|---|
| `artifact/results/paper/output/figures/section5/canonical24_forest_data.csv` | Per-claim ID, paradigm, family, scope preset, $\delta$, $\hat{s}$, Wilson CI, classification. |
| `paper/output/figures/section5/canonical24_label_map.csv` | Original-generation provenance (not shipped): comparator labels. |
| `output/paper/icse_pack/derived/ANALYSIS/pes_margin_full.csv` | Original-generation provenance (not shipped): per-claim block metadata. |
| `output/paper/internal_surface_v2/runs/S2_arithmetic_qiskit_vs_pytket/scores.csv` | Block A raw cells: 168 rows, 3 instances × 7 transpiler seeds × 2 opt levels × 2 layouts × 2 methods. *(Provenance path; not redistributed in the anonymous artifact package; aggregated outputs are in `canonical24_forest_data.csv`.)* |
| `output/paper/internal_surface_v2/runs/S2_ghz_qiskit_vs_pytket/scores.csv` | Block A raw cells: 280 rows, 5 instances × 7 × 2 × 2 × 2. *(Provenance path; not redistributed; aggregates above.)* |
| `output/paper/internal_surface_v2/runs/S2_qft_qiskit_vs_pytket/scores.csv` | Block A raw cells: 280 rows, 5 instances × 7 × 2 × 2 × 2. *(Provenance path; not redistributed; aggregates above.)* |
| `output/paper/evaluation_v3/runs/W1_max2sat_second_family/scores.csv` | Blocks B + C raw cells: 1026 rows, 6 instances under both compilation_only_exact and combined_light_exact, 3 methods. *(Historical generation provenance; aggregates are shipped above. The directory label is retained only to identify the originating run.)* |
| `output/paper/evaluation_v2/runs/E1_maxcut_main/scores.csv` | Blocks D + E + F raw cells: 6930 rows, 30 instances under three presets, 3 methods. *(Historical generation provenance; aggregates are shipped above.)* |
| `claimstab/perturbations/space.py` lines 198–240 | Original-generation provenance (not shipped): preset axis definitions copied into §3. |
| `claimstab/tasks/maxcut.py` lines 102–135 | Original-generation provenance (not shipped): fixed-angle initialization recorded below. |

## 3. Locked preset definitions

| Preset | Active axes | Pinned axes | Product (per instance, per method) |
|---|---|---|---|
| `compilation_only_exact` | `seeds_transpiler ∈ {0,1,2}` × `opt_levels ∈ {0,1,2}` × `layout_methods ∈ {trivial,dense,sabre}` | `shots=1024`, `seeds_simulator=[0]` | 3 × 3 × 3 = 27 |
| `sampling_only_exact` | `shots_list ∈ {16,64,256,1024}` × `seeds_simulator ∈ {0..4}` | `seeds_transpiler=[0]`, `opt_levels=[1]`, `layout_methods=[sabre]` | 4 × 5 = 20 |
| `combined_light_exact` | `seeds_transpiler ∈ {0,1,2}` × `layout_methods ∈ {trivial,sabre}` × `seeds_simulator ∈ {0..4}` | `opt_levels=[1]`, `shots=64` | 3 × 2 × 5 = 30 |

Block A (software-stack) uses an **alternative L1 axis set** in its
scores.csv — `seed_transpiler ∈ {17,23,31,47,61,73,89}` × `opt_levels ∈
{1,3}` × `layout_methods ∈ {trivial,sabre}` (7 × 2 × 2 = 28 per
instance), which is the `compilation_stress`-style configuration the
internal-surface-v2 run used. The recorded `space_preset` label is
`compilation_only_exact` for compatibility with the preset taxonomy;
the actual axis grid differs from the §3 default preset above. This is
documented for reviewer transparency, not a redesign.

## 4. Axis-status vocabulary

| Status | Meaning |
|---|---|
| **ACTIVE** | Axis is exercised by the audit cells. |
| **FIXED-BY-DESIGN** | Axis is intentionally pinned by the canonical preset to isolate other axes. |
| **FIXED-BY-SOURCE** | Axis would be set by a source paper for external claims; not applicable here. |
| **METRIC-IRRELEVANT** | Varying the axis cannot affect the metric. |
| **OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE** | Axis is intentionally absent because canonical claims are not designed to test that surface. |
| **FOLDED-INTO-INSTANCE-SCOPE** | Axis variation is captured by enumerating $\mathcal{S}_{\textit{scope}}$ instances. |
| **FOLDED-INTO-PRECOMPUTED-SCORES** | Axis is collapsed into the per-cell `score` column by the run script. |
| **ARTIFACT-UNSUPPORTED** | Axis cannot be exercised with the current canonical artifact. |
| **EVIDENCE-GAP** | Axis status cannot be determined from existing files. |

## 5. Block-level construction

The six canonical blocks below partition C1–C24 and record block-level
design decisions. Cell counts $N$ are `n_paired_cells` from
`pes_margin_full.csv`. Variance shares are from the same file.

### Block A — C1–C9 (software-stack)

- **Claims:** Arithmetic / GHZ / QFT software-stack pairs, comparator `pytket > Qiskit` on `two_qubit_gate_count`.
- **Semantics:** structural compilation-output comparison; metric is a count, not an execution outcome.
- **Sub-blocks:**
  - C1–C3 (Arithmetic, 3 $\delta$ values): INSTANCE = 3 (n3, n4, n5).
  - C4–C6 (GHZ, 3 $\delta$ values): INSTANCE = 5 (n6, n8, n10, n12, n14).
  - C7–C9 (QFT, 3 $\delta$ values): INSTANCE = 5 (n4, n6, n8, n10, n12).
- **INSTANCE:** ACTIVE — folded into the cell product as per-instance enumeration. Software-stack claims quantify over the named-family circuits.
- **L1:** ACTIVE — `seed_transpiler ∈ {17,23,31,47,61,73,89}` × `opt_levels ∈ {1,3}` × `layout_methods ∈ {trivial,sabre}` = 28 L1 cells per instance.
- **L2:** METRIC-IRRELEVANT — `two_qubit_gate_count` is a structural metric on the compiled circuit; finite-shot sampling cannot change it. Confirmed by `shots=0`, `seed_simulator=0` in scores.csv.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE — `device_provider`, `device_name`, `device_mode` are non-empty with `transpile_only` value, but no backend execution occurs.
- **ALGO:** METRIC-IRRELEVANT — no algorithmic stochasticity is meaningful for a compilation-output comparison.
- **Cell construction:** $N = 84$ (C1–C3), $N = 140$ (C4–C9). Verified: 3 × 28 = 84 and 5 × 28 = 140.
- **Variance shares (per `pes_margin_full.csv`):** Arith share_L1 = 0.85, GHZ share_L1 = 0.85, QFT share_L1 = 0.65; share_L2 = share_L3 = 0 throughout. Dominant variance source = **L1**.
- **Why this construction is appropriate:** the claim "pytket yields fewer two-qubit gates than Qiskit on family X" is a compilation-output claim; varying L1 perturbation (transpiler seed × opt level × layout) tests whether the direction survives reasonable compilation choices. L2/L3/ALGO would not affect the metric.

### Block B — C10–C12 (Max-2-SAT QAOA, combined surface)

- **Claims:** `QAOA_p2 > QAOA_p1` on the QAOA `objective` metric, scope = `combined_light_exact`, 3 $\delta$ values.
- **Semantics:** optimization-objective claim evaluated under combined compilation + sampling perturbation.
- **INSTANCE:** ACTIVE — 6 Max-2-SAT instances (`max2sat_core_0..5`).
- **L1:** ACTIVE (narrow) — `seed_transpiler ∈ {0,1,2}` × `layout_method ∈ {trivial,sabre}` = 6 L1 cells; `optimization_level` pinned at the preset default (verified: `opt_levels=[1]` in `combined_light_exact`).
- **L2:** ACTIVE — `seed_simulator ∈ {0,1,2,3,4}` = 5 L2 cells; `shots` pinned at 64.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE — `device_provider/name/mode` blank.
- **ALGO:** FIXED-BY-DESIGN — QAOA uses **fixed angles** ($\gamma=0.8$, $\beta=0.4$ in `claimstab/tasks/maxcut.py` line 128–130; explicit comment "no optimizer loop in this benchmark"). No `init_strategy` or `init_seed` column in `scores.csv`. The QAOA $p=2$ vs $p=1$ comparison is therefore a **layer-count comparison at fixed angles**, not an optimizer comparison.
- **Cell construction:** $N = 180$ = 6 instances × 6 L1 × 5 L2 = 180. ✓
- **Variance shares:** share_L1 = 0.01, share_L2 = 0.17, share_residual = 0.82. Dominant = **residual** (within-instance / between-instance variation).
- **Why this construction is appropriate:** isolates the layer-count effect from L1+L2 environment noise on a small problem family. Because ALGO is fixed, the claim is "the QAOA at $p=2$ outperforms the QAOA at $p=1$ at these fixed angles, on these instances, under combined-light perturbation."

### Block C — C13–C15 (Max-2-SAT QAOA, compilation-only surface)

- **Claims:** Same comparator as Block B, scope = `compilation_only_exact`, 3 $\delta$ values.
- **Semantics:** optimization-objective claim evaluated under L1-only perturbation. **Not a compiler-output claim** — the metric is the QAOA objective, evaluated after compilation.
- **INSTANCE:** ACTIVE — 6 Max-2-SAT instances.
- **L1:** ACTIVE — `seed_transpiler ∈ {0,1,2}` × `opt_levels ∈ {0,1,2}` × `layout_methods ∈ {trivial,dense,sabre}` = 27 L1 cells per instance.
- **L2:** FIXED-BY-DESIGN — `shots=1024`, `seed_simulator=[0]` pinned.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE.
- **ALGO:** FIXED-BY-DESIGN — same as Block B.
- **Cell construction:** $N = 162$ = 6 × 27 = 162. ✓
- **Variance shares:** share_L1 = 0.22, share_L2 = share_L3 = 0, share_residual = 0.78. Dominant = **residual**.
- **Why this construction is appropriate:** the L1-only surface lets the audit ask whether the layer-count direction survives compilation perturbation alone, with sampling noise held essentially constant.

### Block D — C16–C18 (MaxCut QAOA, combined surface)

- **Claims:** `QAOA_p2 > QAOA_p1`, scope = `combined_light_exact`, 3 $\delta$ values.
- **Semantics:** optimization-objective claim on a larger and more diverse instance family.
- **INSTANCE:** ACTIVE — 30 MaxCut graph instances (`er_n10_p*_seed*`).
- **L1:** ACTIVE — same axes as Block B: 6 L1 cells per instance.
- **L2:** ACTIVE — same axes as Block B: 5 L2 cells per instance.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE.
- **ALGO:** FIXED-BY-DESIGN — same as Block B.
- **Cell construction:** $N = 900$ = 30 × 6 × 5 = 900. ✓
- **Variance shares:** share_L1 = 0.005, share_L2 = 0.026, share_residual = 0.969. Dominant = **residual** (driven by MaxCut graph diversity within $\mathcal{S}_{\textit{scope}}$).
- **Why this construction is appropriate:** at 30 instances, INSTANCE diversity dominates and residual variance reflects between-instance heterogeneity, not algorithmic stochasticity (which is fixed).

### Block E — C19–C21 (MaxCut QAOA, compilation-only surface)

- **Claims:** Same comparator as Block D, scope = `compilation_only_exact`, 3 $\delta$ values.
- **Semantics:** optimization-objective claim under L1-only perturbation.
- **INSTANCE:** ACTIVE — 30 MaxCut graphs.
- **L1:** ACTIVE — 27 cells per instance (same as Block C).
- **L2:** FIXED-BY-DESIGN.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE.
- **ALGO:** FIXED-BY-DESIGN.
- **Cell construction:** $N = 810$ = 30 × 27 = 810. ✓
- **Variance shares:** share_L1 = 0.055, share_L2 = share_L3 = 0, share_residual = 0.945.

### Block F — C22–C24 (MaxCut QAOA, sampling-only surface)

- **Claims:** Same comparator as Block D, scope = `sampling_only_exact`, 3 $\delta$ values.
- **Semantics:** optimization-objective claim under L2-only perturbation.
- **INSTANCE:** ACTIVE — 30 MaxCut graphs.
- **L1:** FIXED-BY-DESIGN — `seed_transpiler=0`, `opt_levels=[1]`, `layout_methods=[sabre]`.
- **L2:** ACTIVE — `shots ∈ {16,64,256,1024}` × `seed_simulator ∈ {0..4}` = 20 L2 cells per instance.
- **L3:** OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE.
- **ALGO:** FIXED-BY-DESIGN.
- **Cell construction:** $N = 600$ = 30 × 20 = 600. ✓
- **Variance shares:** share_L1 = 0, share_L2 = 0.045, share_residual = 0.955. Dominant = **residual**.

## 6. Per-claim audit-space status table (24 rows)

`I` = INSTANCE / $\mathcal{S}_{\textit{scope}}$; `A` = ACTIVE; `F-D` =
FIXED-BY-DESIGN; `M-I` = METRIC-IRRELEVANT; `O-C-D-P` =
OUTSIDE-CONTROLLED-DIAGNOSTIC-PURPOSE; `n_paired` = paired-cell count
from `pes_margin_full.csv`; `dom.` = dominant variance source.

| ID | Group | Family/setup | Preset | I | L1 | L2 | L3 | ALGO | n_paired | dom. | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1  | software-stack | Arithmetic     | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 84  | L1 | design appropriate |
| C2  | software-stack | Arithmetic     | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 84  | L1 | design appropriate |
| C3  | software-stack | Arithmetic     | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 84  | L1 | design appropriate |
| C4  | software-stack | GHZ            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C5  | software-stack | GHZ            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C6  | software-stack | GHZ            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C7  | software-stack | QFT            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C8  | software-stack | QFT            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C9  | software-stack | QFT            | compilation_only_exact | A | A | M-I | O-C-D-P | M-I | 140 | L1 | design appropriate |
| C10 | optimization   | Max-2-SAT QAOA | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 180 | residual | design appropriate |
| C11 | optimization   | Max-2-SAT QAOA | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 180 | residual | design appropriate |
| C12 | optimization   | Max-2-SAT QAOA | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 180 | residual | design appropriate |
| C13 | optimization   | Max-2-SAT QAOA | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 162 | residual | design appropriate |
| C14 | optimization   | Max-2-SAT QAOA | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 162 | residual | design appropriate |
| C15 | optimization   | Max-2-SAT QAOA | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 162 | residual | design appropriate |
| C16 | optimization   | MaxCut QAOA    | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 900 | residual | design appropriate |
| C17 | optimization   | MaxCut QAOA    | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 900 | residual | design appropriate |
| C18 | optimization   | MaxCut QAOA    | combined_light_exact   | A | A | A   | O-C-D-P | F-D | 900 | residual | design appropriate |
| C19 | optimization   | MaxCut QAOA    | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 810 | residual | design appropriate |
| C20 | optimization   | MaxCut QAOA    | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 810 | residual | design appropriate |
| C21 | optimization   | MaxCut QAOA    | compilation_only_exact | A | A | F-D | O-C-D-P | F-D | 810 | residual | design appropriate |
| C22 | optimization   | MaxCut QAOA    | sampling_only_exact    | A | F-D | A | O-C-D-P | F-D | 600 | residual | design appropriate |
| C23 | optimization   | MaxCut QAOA    | sampling_only_exact    | A | F-D | A | O-C-D-P | F-D | 600 | residual | design appropriate |
| C24 | optimization   | MaxCut QAOA    | sampling_only_exact    | A | F-D | A | O-C-D-P | F-D | 600 | residual | design appropriate |

## 7. Evidence boundaries

- **ALGO axis (optimization claims, Blocks B–F).** The QAOA `objective`
  metric is computed at **fixed angles** ($\gamma=0.8$, $\beta=0.4$;
  source: `claimstab/tasks/maxcut.py` lines 127–130 and the absence of
  an `init_strategy` / `init_seed` column in the scores CSVs). The
  canonical optimization claim is therefore a **layer-count comparison at fixed
  angles**, not an optimizer comparison. An optimizer-stochasticity claim would
  require an ALGO-active design and is outside this construction.
- **L3 axis.** No canonical block exercises L3. This is intentional;
  the canonical corpus is a controlled diagnostic surface for classifier
  behavior, not a backend/noise audit. Controlled L3 evidence is recorded in
  `l3_noise_diagnostic_expanded.md` and its shipped row-level grid.
- **INSTANCE counts.** INSTANCE is ACTIVE in every block, with instance
  counts ranging 3 → 30. The instance ID lists are recoverable from the
  scores.csv files cited in §2. They are *not* surfaced as a manuscript
  column because the family identifier already implies the instance
  family.
- **`n_paired_cells` vs Wilson-CI N.** The reported $N$ is
  `n_paired_cells`. The Wilson-CI effective N for optimization rows is
  not always equal to `n_paired_cells`; the upstream CI computation
  uses a paired-block aggregation whose effective unit is not surfaced
  in `canonical24_forest_data.csv`. Reporting $k/N$ would be
  misleading, so the manuscript does not advertise one. This is the
  single remaining **EVIDENCE-GAP**; it does not affect the design
  verdict because the Wilson CIs themselves are locked in
  `canonical24_forest_data.csv` and used directly in the canonical forest data.

## 8. Note on `n_paired_cells`

`n_paired_cells` is the **audit-space paired-cell count** after the
$\mathcal{S}_{\textit{scope}} \times \mathcal{E}_{\textit{env}}$ product
is fully enumerated and paired across $\mathcal{B}_A$ vs
$\mathcal{B}_B$. It is **not** the Wilson denominator: the locked
Wilson CIs in `canonical24_forest_data.csv` are computed with a
paired-block aggregation step whose effective N is sometimes smaller
(e.g., MaxCut combined: `n_paired_cells = 900` but CI width corresponds
to an effective N of order 87). Reviewers should read $N$ as the
audit-space cell count, not as a Wilson denominator.

## 9. Scope of this note

- This note is a **design / construction** record. It does not
  introduce new numerical results.
- All values are recoverable from existing files in §2.
- No CSV is modified by this note.
- No experiments are rerun.
- C1–C24 remain canonical internal-corpus claims throughout the
  manuscript; this note does not promote them to external claims.
