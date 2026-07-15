# Tier-1 statistical robustness summary (EX-C1 … EX-C8)

Scope: the 8 **exact** scalar-directional external audit records. This note
separates four things the headline S/U/R verdicts conflate, and reports how
sensitive each verdict is to choices that are *policy*, not *evidence*.

**Interpretation stance (design-first).** The primary evidence for each record is
the finite locked audit design: the per-cell preserved count `k`, the tie count,
the contradiction count, and the signed margins over the `N` enumerated cells.
The Wilson 95% interval is the **predeclared policy classifier** that maps `(k,N)`
to Sustained / Unresolved / Reversed at threshold `tau`; it is **not** an estimate
of a universal claim-stability probability. Cluster resampling, leave-one-cluster-out,
tie-policy, threshold, and seed-budget checks test *sensitivity* of the policy
output to grouping, threshold, tie convention, and budget — they do **not**
establish cell independence.

All numbers below are reproduced by `tier1_robustness_analysis.py`, whose
validation gates assert exact agreement with the locked artifacts
(`per_claim_external_audit.csv`, `external_forest_data.csv`,
`expanded_seed_sensitivity.csv`). Cluster bootstrap: B = 10,000, clusters
resampled with replacement (all cells inside a sampled cluster retained), fixed seed.

## Primary finite-design evidence

| Record | metric | N | preserved k | tied | contradicted | k/N | Wilson 95% | verdict (tau=.95) |
|---|---|---|---|---|---|---|---|---|
| EX-C1 | compilation runtime | 80 | 80 | 0 | 0 | 1.000 | [0.954, 1.000] | Sustained |
| EX-C2 | approximation ratio | 80 | 80 | 0 | 0 | 1.000 | [0.954, 1.000] | Sustained |
| EX-C3 | CNOT count | 80 | 62 | 18 | 0 | 0.775 | [0.672, 0.853] | Unresolved |
| EX-C4 | probability value | 80 | 45 | — | — | 0.563 | [0.453, 0.666] | Unresolved |
| EX-C5 | 2q gate depth | 80 | 44 | 15 | 21 | 0.550 | [0.441, 0.654] | Unresolved |
| EX-C6 | CX-depth overhead | 80 | 34 | 26 | 20 | 0.425 | [0.323, 0.534] | Unresolved |
| EX-C7 | 2q gate count | 80 | 0 | 18 | 62 | 0.000 | [0.000, 0.046] | Reversed |
| EX-C8 | construction time | 80 | 0 | 0 | 80 | 0.000 | [0.000, 0.046] | Reversed |

EX-C2 and EX-C4 (`ext_2411_00518v2`) have **no materialized per-cell file** on this
branch — only the locked aggregate. Their per-cell-dependent checks (cluster,
leave-one-cluster-out, and for EX-C4 the tie/contradiction split) are reported as
**not available**, not imputed.

## Answers to the robustness questions

**1. Which verdicts are stable under tested grouping choices?**
Cluster bootstrap (design-motivated clusters: benchmark circuit / circuit size /
random-circuit instance):
- **Stable:** EX-C1 (Sustained, 100% of resamples), EX-C5 and EX-C6 (Unresolved,
  100%), EX-C7 and EX-C8 (Reversed, 100%).
- **Cluster-sensitive:** **EX-C3** — with only 4 circuit clusters and strong
  between-circuit heterogeneity (one circuit at 57/60 ≈ 0.95 vs. the others at
  ≈0.70), 6.4% of cluster resamples flip to Sustained and the resampled rate CI is
  wide ([0.44, 1.00]). Leave-one-cluster-out does **not** flip EX-C3 (all four
  single-circuit deletions stay Unresolved, rates 0.70–0.95), so EX-C3 is
  *bootstrap-sensitive but deletion-stable*: its Unresolved label is genuine but
  rests on circuit heterogeneity that few clusters cannot pin down.
- **Not assessable:** EX-C2, EX-C4 (no per-cell data).

**2. Which verdicts are threshold-sensitive?**
The four **extreme** verdicts flip at the stricter `tau=0.99`:
EX-C1, EX-C2 (Sustained → Unresolved) and EX-C7, EX-C8 (Reversed → Unresolved).
This is a finite-`N` artifact: with N=80 the Wilson interval cannot get within 0.01
of the boundary (80/80 lower = 0.954 < 0.99; 0/80 upper = 0.046 > 0.01). The four
**middle** records (EX-C3–EX-C6, all Unresolved) are threshold-stable across
`tau ∈ {0.90, 0.95, 0.99}`.

**3. Which verdicts are tie-policy-sensitive?**
Only **EX-C7**. Under the locked main policy (ties non-preserving) it is Reversed;
excluding ties from `N` (0/62) or counting ties as half-preserving (9/80) both give
**Unresolved** — removing/softening the 18 ties widens the interval above 0.05.
EX-C3, EX-C5, EX-C6 are tie-stable (Unresolved under all three policies). EX-C1,
EX-C2, EX-C8 have 0 ties (tie policy is a no-op). EX-C4 is not assessable.
The half-preserving column is an explicit **sensitivity projection**, not a binomial
model (it admits non-integer successes).

**4. Which records are dependence-limited?**
None of the six per-cell records fall below the 3-cluster floor (clusters: EX-C1/C3/C5/
C7/C8 = 4, EX-C6 = 20). The evidence boundary is **dependence-not-assessable** for
EX-C2 and EX-C4, where no per-cell file exists. (Separately, EX-C3 is the one record
whose dependence structure materially moves the verdict — see Q1.)

**5. Does EX-C7 remain contradicted / Reversed under cluster, tie, and seed-expansion checks?**
- **Contradicted-dominance is robust.** EX-C7 has **0 preserved cells under every
  tie policy and every budget** (0/80 at N=80 through 0/320 at the expanded budget;
  0/62 with ties excluded; 9/80 half-preserving). The substantive finding — TKET
  does *not* exceed Qiskit on 2-qubit gate count; the asserted direction reverses —
  does not depend on any analysis choice.
- **Cluster:** Reversed in 100% of cluster resamples.
- **Seed expansion:** Reversed at N = 80, 160, 240, 320 (the Wilson upper bound
  *shrinks* 0.046 → 0.012 as cells accumulate).
- **Tie / threshold:** the *categorical* Reversed label is policy-contingent — it
  softens to Unresolved if ties are excluded/half-counted (Q3) or if `tau` is
  tightened to 0.99 (Q2).
- **Net:** report EX-C7 as **robustly contradicted-dominated (0 preserved)**, with
  the Reversed Wilson label holding under the locked policy, cluster resampling, and
  seed expansion, but contingent on the tie convention and on `tau ≤ 0.95`.

**6. EX-C8 contrast.** EX-C8 is the tie-free Reversed record: 0 preserved, **0 ties**,
80 contradictions. It is Reversed under the main and (identical) tie-excluded/half
policies and under cluster resampling; it is threshold-sensitive (R→U at 0.99) and
budget-unavailable. The EX-C7 vs EX-C8 contrast shows tie-policy sensitivity is
specifically a *tie-mass* phenomenon, not a generic property of Reversed verdicts.

## Reviewer interpretation

**RQ4 robustness.** The per-dimension status grid
(`tier1_robustness_status.csv`) preserves the relevant distinctions rather than
collapsing them into one label. Evidence summary:
the *direction* of each finite-design outcome is stable, but two verdict **labels**
are policy-contingent at N=80 — EX-C3's Unresolved is cluster-heterogeneity-driven
(bootstrap-sensitive, deletion-stable) and EX-C7's Reversed is tie-policy- and
`tau=0.99`-contingent though its 0-preserved contradiction-dominance is not. Sustained
records (EX-C1/C2) and the middle Unresolved records (EX-C5/C6) are stable on every
applicable axis; EX-C8 is a clean Reversed.

**Boundary.** S/U/R are **scoped audit-policy outcomes over locked finite designs**,
not population-level stability estimates: (i) the Wilson
interval classifies the realized `k/N` of the enumerated cells, so it answers "does the
asserted direction hold across *this* locked grid", not "across all instances"; (ii)
cells within a record share circuits/instances and are not independent — cluster
bootstrap and leave-one-cluster-out probe this dependence but cannot prove independence,
and EX-C3 shows the verdict can hinge on which clusters are sampled; (iii) ties and the
`tau`/N choices are policy parameters — EX-C7 is Reversed only under the predeclared
ties-non-preserving, `tau ≤ 0.95` policy; (iv) EX-C2 and EX-C4 lack materialized
per-cell traces, so their dependence and tie structure are unaudited.

## Files

`tier1_primary_evidence.csv`, `tier1_threshold_sensitivity.csv`,
`tier1_cluster_resampling.csv`, `tier1_leave_one_cluster_out.csv`,
`tier1_tie_policy_sensitivity.csv`, `tier1_budget_seed_expansion.csv`,
`tier1_robustness_status.csv`, `tier1_per_cell_table.csv` (per-cell provenance,
6 materialized records × 80 cells), and `tier1_robustness_analysis.py` (deterministic;
re-runs and re-validates all of the above).
