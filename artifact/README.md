# CLAIMSTAB-QC Anonymous Submission Artifact

This artifact supports the paper:

**When "A Beats B" Needs Evidence: CLAIMSTAB-QC for Auditing Comparative Claims in Quantum Software.**

It provides the data, locked outputs, and lightweight verification scripts needed to
inspect and verify the committed evidence for the paper's main results. The package is anonymized for
double-anonymous review; a permanent public archival link will be provided after
acceptance.

Start here:

- [PAPER_CLAIMS_TO_EVIDENCE.md](PAPER_CLAIMS_TO_EVIDENCE.md) — maps each paper-facing number to its source file and verification command.
- [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) — short top-level directory map and the 53-design auditability inventory note.
- [ENVIRONMENT.md](ENVIRONMENT.md) — reviewer dependencies and the pinned full-framework toolchain.

## Reproduction scope and paths

This anonymous artifact ships **locked outputs, row-level RQ1/RQ3 evidence, and
lightweight verification scripts**, not the complete long-run simulation pipeline.
Two conventions apply throughout:

- **Locked derived outputs** that the verification scripts read are mirrored under
  `artifact/results/<original-repository-path>` — for example
  [results/paper/output/figures/section5/external_forest_data.csv](results/paper/output/figures/section5/external_forest_data.csv)
  and [results/data/synthetic/calibration_results.csv](results/data/synthetic/calibration_results.csv).
- The five manuscript-facing RQ3 diagnostic grids and their summaries are bundled
  under `artifact/results/paper/output/figures/section5/` and are checked directly.
  The qiskit-heavy generators that produced those grids are not bundled. Thus the
  diagnostic outcomes are independently inspectable and arithmetically verifiable,
  but the long simulations are not one-command reproducible from this package.

## Quick start — reviewer verification

From the repository root (read-only; under one minute; no quantum simulation):

```bash
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/build_rq1_claim_decisions.py
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py
python3 artifact/external_audit/budget_sensitivity/recon_driver.py
```

What each command does:

- [tests/](tests/) — verdict-core + funnel/RQ smoke tests.
- [scripts/build_rq1_claim_decisions.py](scripts/build_rq1_claim_decisions.py) — verifies that the derived row-level decision crosscheck and 119-paper rollup match the raw extraction plus the 16-row source-grounded crosscheck (use `--write` only to regenerate them).
- [scripts/check_headline_numbers.py](scripts/check_headline_numbers.py) — RQ1–RQ4 headline numbers from locked CSVs, including the RQ1 materialization-disposition sums (Table III: 79 = 53 + 26).
- [scripts/check_artifact_files.py](scripts/check_artifact_files.py) — required-file availability.
- [data/corpus/coding_validity/recompute_agreement.py](data/corpus/coding_validity/recompute_agreement.py) — coding-validity agreement / kappa.
- [scripts/check_markdown_links.py](scripts/check_markdown_links.py) — local Markdown links.
- [scripts/check_rq4_robustness.py](scripts/check_rq4_robustness.py) — RQ4 robustness alignment.
- [external_audit/budget_sensitivity/recon_driver.py](external_audit/budget_sensitivity/recon_driver.py) — read-only recomputation of the four-record reconstruction gate and seed-expansion tables from shipped raw JSONL plus Tier-1 cells (`consolidate` is the explicit write mode).

Use the tested lock in `requirements-lock.txt`, or the compatible ranges in
`requirements.txt`. The verdict-core under [src/claimstab/](src/claimstab/) is
pure-Python. Default verification is read-only. Pass `--write-report` to the three
report-producing checkers only when a Markdown report is wanted; pass `--write` to
the registry/agreement scripts only when intentionally regenerating derived files.

## Reviewer-facing evidence map

The artifact mirrors the four research questions in the submitted manuscript.

### RQ1 — Field auditability surface

Paper-facing funnel:

- **250 screened** candidate papers; **119 included** (`screening_decision = include`) and **131 excluded** (`screening_decision = exclude`).
- **455 accepted comparative claims** through the three-stage extraction protocol and source-grounded Layer-1 adjudication.
- **175 claim-card-specifiable** claims.
- **145 scalar-directional** claims.
- **93 planning-feasible** relation-aware candidates.
- **79 scalar-directional planning records** (`145 ∩ 93`).
- **53 auditable designs**.
- **8 exact records** — the proxy-free materialized external audit surface (8 / 455 = 1.76%).
- A blinded **120-item coding-validity audit** supports the auditability-funnel boundaries: planning-feasible 92.11% ($\kappa$=0.835, n=114), auditable-design 96.55% ($\kappa$=0.782, n=58), proxy-free exact vs non-exact 100% ($\kappa$=1.000, n=58).

**Corpus construction.** The corpus was constructed through a **Google Scholar
search-and-screen protocol** with artifact-side normalized provenance. The search was
initially run on 2026-01-28 using 13 predefined query strings combining
quantum-software terms with comparison terms; per-query results were deduplicated by
title and available identifiers such as DOI or arXiv ID, and capped at 250 candidates
for manual screening. The artifact records the archived retrieval/export timestamp as
`2026-04-28T19:33:02`. Raw Google Scholar result pages are not bundled; the artifact
preserves normalized reviewer-facing provenance (see
[field_study/corpus/search_protocol.md](field_study/corpus/search_protocol.md)). The
screened 250-paper corpus is fixed in
[field_study/corpus/paper_list_250_screened.csv](field_study/corpus/paper_list_250_screened.csv),
whose screened-paper metadata spans publication dates 2020-02-23 to 2024-12-23.

**Raw extraction vs. final decisions.**
[field_study/claims/extracted_claims_457.csv](field_study/claims/extracted_claims_457.csv)
holds the **raw Stage-3 candidate records before claim-level correction**: 457 records
over 118 unique papers, raw paradigm split 314 variational / 143 compilation, with
per-claim O1–O7 screen reasons. **The 457-row registry records raw Stage-3 extraction
records before claim-level correction. The paper-facing final accepted-claim count is
455, supported by `corrected_headline_counts.csv` and
`source_grounded_claim_adjudication.csv`.** The derived decision crosscheck
[field_study/claims/rq1_claim_decisions_457.csv](field_study/claims/rq1_claim_decisions_457.csv),
is generated from the raw flags plus
[headline_count_final_crosscheck_decisions.csv](headline_count_final_crosscheck_decisions.csv)
and crosschecked against [source_grounded_claim_adjudication.csv](source_grounded_claim_adjudication.csv).
It records **455 accepted claims** (313 variational / 142 compilation after two
Layer-1 demotions) as true decision flags across the candidate rows. The compact
[corrected_headline_counts.csv](corrected_headline_counts.csv) is the paper-facing
count table and must match that derived crosscheck. The
78 operationalizable rows flagged by the O1–O7 screen are the operationalizability
screen, distinct from the 79 paper-facing scalar-directional planning records.

**Materialization disposition (Table III).**
[field_study/rq1_materialization_barrier_taxonomy.csv](field_study/rq1_materialization_barrier_taxonomy.csv)
supports manuscript Table III. It decomposes the 79 scalar-directional planning records
by strongest lockable evidence object or blocking evidence boundary: proxy-free scoped
(8), lockable but not proxy-free scoped (43 + 2), and boundary (20 + 2 + 4). The counts
sum to 79 and explain the 79-to-8 materialization gap; 8 + 43 + 2 correspond to the 53
registry-level auditable design entries. The separate
`field_study/rq1_materialization_barrier_records_79.csv`
provides record-level inspection and is not manuscript Table III itself. Both layers
are verified by [scripts/check_headline_numbers.py](scripts/check_headline_numbers.py).

**Supporting evidence (not the paper-facing funnel).** The locked materialization-tier
census over the 76 pre-adjudication candidates splits **8 T1** (proxy-free
materialized), **0 T2**, **58 T3** (proxy or inferred only), **10 T4** (blocked by
missing operational specification); the corrected count adds one source-grounded
candidate (77 total) not in that locked census. These tier counts are verified from
[external_audit/materialization/materialization_tiers_76.csv](external_audit/materialization/materialization_tiers_76.csv)
by [scripts/check_headline_numbers.py](scripts/check_headline_numbers.py).

Evidence:

- [field_study/corpus/paper_list_250_screened.csv](field_study/corpus/paper_list_250_screened.csv) — 250 screened, 119 included, 131 excluded.
- [field_study/claims/rq1_claim_decisions_457.csv](field_study/claims/rq1_claim_decisions_457.csv) — derived row-level decision crosscheck over the candidate records; 455 rows carry an accepted decision.
- [field_study/corpus/final_rq1_paper_registry_119.csv](field_study/corpus/final_rq1_paper_registry_119.csv) — all 119 included papers, 118 contributing accepted claims.
- [field_study/rq1_materialization_barrier_taxonomy.csv](field_study/rq1_materialization_barrier_taxonomy.csv) — RQ1 materialization disposition (manuscript Table III); 79 = 53 auditable + 26 boundary.
- `field_study/rq1_materialization_barrier_records_79.csv` — record-level support for inspecting the six-row Table III summary.
- [field_study/corpus/search_protocol.md](field_study/corpus/search_protocol.md) — Google Scholar search-and-screen protocol and how the artifact-side normalized provenance is inspected.
- [field_study/corpus/inclusion_exclusion_criteria.md](field_study/corpus/inclusion_exclusion_criteria.md) and [field_study/corpus/search_log.csv](field_study/corpus/search_log.csv) — screening protocol, exclusion taxonomy, and the 13-query normalized retrieval log.
- [field_study/claims/extracted_claims_457.csv](field_study/claims/extracted_claims_457.csv) — raw Stage-3 extraction with per-claim O1–O7 reasons.
- [field_study/claims/failed_criteria_by_claim.csv](field_study/claims/failed_criteria_by_claim.csv) — failed operationalizability criteria.
- [field_study/RELATION_SCHEMA_RQ1_COUNTS.md](field_study/RELATION_SCHEMA_RQ1_COUNTS.md), [field_study/claims/relation_schema_rq1_counts.csv](field_study/claims/relation_schema_rq1_counts.csv), [field_study/claims/relation_schema_rq1_flags.csv](field_study/claims/relation_schema_rq1_flags.csv) — RQ1 count map and per-claim flags.
- [corrected_headline_counts.csv](corrected_headline_counts.csv) and `source_grounded_claim_adjudication.csv` — paper-facing corrected counts and their source-grounded adjudication support.
- [external_audit/materialization/materialization_tiers_76.csv](external_audit/materialization/materialization_tiers_76.csv) — T1/T2/T3/T4 census (supporting evidence).
- [field_study/coding_protocol/](field_study/coding_protocol/) and [data/corpus/coding_validity/](data/corpus/coding_validity/) — coding protocol and the 120-item consistency audit, reproduced by [data/corpus/coding_validity/recompute_agreement.py](data/corpus/coding_validity/recompute_agreement.py).

### RQ2 — Materialized external audit (declared audit designs)

- All 8 artifact-backed T1 claims audited under a per-claim **declared audit design** of $N=80$ cells.
- Verdicts within audited scope: **2 Sustained / 4 Unresolved / 2 Reversed**.
  - Sustained: EX-C1 (compilation runtime), EX-C2 (approximation ratio).
  - Unresolved: EX-C3, EX-C4, EX-C5, EX-C6.
  - Reversed: EX-C7 (two-qubit gate count, $k=0$ of $80$, Wilson CI $[0.000, 0.046]$), EX-C8 (construction time, $k=0$ of $80$, Wilson CI $[0.000, 0.046]$).

**Scope and boundaries.** These are 8 Tier-1 exact / proxy-free directional audit
records within the locked artifact scope: each is exact with respect to the locked
evidence object available in the artifact. Records with aggregate, timing, or
host-sensitive boundaries are explicitly marked in the claim cards and evidence maps.
EX-C2 and EX-C4 have aggregate/cluster traceability boundaries (no independently
inspectable per-cell CSV is bundled). EX-C1 and EX-C8 are host-sensitive local timing
audits. EX-C1, EX-C5, EX-C6, EX-C7, and EX-C8 are scoped local audit designs, not full
source-study replications.

Evidence:

- [results/paper/output/figures/section5/external_forest_data.csv](results/paper/output/figures/section5/external_forest_data.csv) — 8 external Wilson results.
- [results/paper/output/figures/section5/per_claim_perturbations.csv](results/paper/output/figures/section5/per_claim_perturbations.csv) — per-claim audit scope and exclusions.
- [external_audit/audit_space/external_audit_space_contracts.md](external_audit/audit_space/external_audit_space_contracts.md) — per-EX-C audit-space contracts.
- [external_audit/mapping/source_mapping_anonymized.csv](external_audit/mapping/source_mapping_anonymized.csv) — anonymized EX-C source mapping.
- [claim_cards/](claim_cards/) — locked claim cards EX-C1..EX-C8.
- [rq2_audit_design_ledger.csv](rq2_audit_design_ledger.csv) and [rq2_relation_checker_alignment.csv](rq2_relation_checker_alignment.csv) — the 17-record RQ2 ledger (EX-C*, SD*, BD*) and relation-checker alignment.

### Relation-specific boundary sweep

These records are **not** counted as RQ2 scalar Wilson verdicts. They document
relation-specific materialization boundaries and extend the RQ1 materialization map
rather than the RQ2 verdict surface; the source tables are under
[external_audit/road_b/](external_audit/road_b/).

- **EX-C9 PauliOpt CNOT:** clean aggregate-crossover relation, concordant on 5 / 5 devices.
- **OLSQ claim4:** reconstructed geometric-mean relation, concordant only under a reconstructed zero-exclusion convention.
- **SQUANDER claim1+2:** source-limited boundary record.
- **EX-C10 PauliOpt runtime:** indeterminate boundary evidence.
- **ISAAQ claim1:** infeasible under the current artifact.
- **Synthetiq:** missing-source boundary, not evidence.

Reconstructed evidence is not treated as clean source-exposed concordance.

### RQ3 — Controlled audit-space validation

RQ3 evidence has three parts: synthetic decision-rule controls, the simpler-audit
ladder on the C1–C24 dataset, and controlled diagnostic surfaces by audit-axis group.

#### Synthetic decision-rule controls

Mechanism checks on the Wilson S/U/R rule under known preservation profiles — not
corpus-derived RQ1/RQ2 evidence.

- Grid: `s_true ∈ {0.50, 0.70, 0.85, 0.95, 0.99, 1.00}` × `N ∈ {10, 30, 100}` = 18 preservation profiles, 3000 trials.
- Wilson 95% coverage: **94.97%**.
- Reversed-detection control: **26 / 27** known-reversed cases detected (9 synthetic Reversed + 18 H$_2$ chemistry comparators).

Evidence:

- [results/data/synthetic/calibration_results.csv](results/data/synthetic/calibration_results.csv) — 3000-trial coverage grid.
- [results/output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv](results/output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv)
- [results/output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv](results/output/paper/icse_pack/derived/SUPPORT/internal_surface_supporting_metric_dataset.csv)

#### Simpler-audit ladder on the C1–C24 dataset

The C1–C24 synthetic/canonical diagnostic dataset supports the RQ3 simpler-audit ladder
and controlled diagnostic-surface evidence. It contains 24 claims from 8 base setups
across Arithmetic, GHZ, QFT, Max-2-SAT QAOA, and MaxCut QAOA, with fixed QAOA angles
$\gamma = 0.8$ and $\beta = 0.4$. This dataset is RQ3 evidence, not a manuscript figure.

**RQ3 C1–C24 dataset specification.**

| Claim range | Workload family | Comparison object | Fixed settings / metric | RQ3 role |
|---|---|---|---|---|
| C1–C9 | Arithmetic, GHZ, QFT structural circuits | pytket vs Qiskit compiler-output comparison | two-qubit gate count; source-aligned structural compiler-output setting | Tests whether compiler-output directions remain supported under locked audit designs. |
| C10–C24 | Max-2-SAT QAOA and MaxCut QAOA | layer-count comparison, $p{=}2$ vs $p{=}1$ | fixed QAOA angles $\gamma = 0.8$, $\beta = 0.4$ | Tests whether apparent QAOA layer-count advantages remain supported under locked audit designs. |
| All C1–C24 | 8 benchmark-relevant base setups | 24 controlled comparisons | simpler protocols compared with the full locked audit | Single-run: 19/24 match, 5/24 oppose; seed-only: all 24 Unresolved, 14/24 agree with full audit; L1-only: 15 records, 10/15 disagree with full audit; full audit: 10 Sustained, 14 Unresolved, 0 Reversed. |

This is RQ3 mechanism evidence, not corpus-derived RQ1/RQ2 evidence, and it is not a
manuscript figure.

The ladder compares progressively richer audit designs against the full audit:

- **Single published-configuration run** (1 cell, no uncertainty): 19/24 match direction, 5/24 oppose.
- **Seed-only audit:** all 24 Unresolved; agrees with the full audit on 14/24.
- **Single-axis L1 matched-block audit:** available for 15 records; disagrees with the full audit on 10/15 (post-hoc matched-block diagnostic).
- **Full audit:** **10 Sustained / 14 Unresolved / 0 Reversed** within audited scope; all 9 software-stack claims Sustained.

Evidence:

- [results/paper/output/figures/section5/canonical24_forest_data.csv](results/paper/output/figures/section5/canonical24_forest_data.csv) — full-audit Wilson results.
- [results/paper/output/figures/section5/baseline_diagnostic_fallback.csv](results/paper/output/figures/section5/baseline_diagnostic_fallback.csv) — single-run and seed-only ladder.
- [results/paper/output/figures/section5/perturbation_diagnostic.md](results/paper/output/figures/section5/perturbation_diagnostic.md) — single-axis matched-block diagnostic.
- [internal_corpus/canonical24_audit_space_construction.md](internal_corpus/canonical24_audit_space_construction.md) — per-claim audit-space construction.
- [internal_corpus/rq3_controlled_validation_suite.md](internal_corpus/rq3_controlled_validation_suite.md) — controlled-validation suite record.

#### Controlled diagnostic surfaces by audit-axis group

Five controlled diagnostics (15 claims) exercise one audit-axis group at a time with
the others pinned. Per-axis operationalization is recorded in
[internal_corpus/rq3_controlled_validation_suite.md](internal_corpus/rq3_controlled_validation_suite.md).
The five released diagnostic grids contain **16,830 diagnostic cells** in total;
these are locked evidence cells, while the qiskit-heavy generators are not bundled.

- **L1Q-C1 / L1Q-C2 / L1Q-C3** (within-Qiskit structural; 30 GHZ + hardware-efficient circuits; $N=1200$): **0 S / 1 U / 2 R**. L1Q-C1 and L1Q-C3 are tie-driven; L1Q-C2 shows a $33\%/33\%/33\%$ split.
- **L2-C1 / L2-C2 / L2-C3** (L2 sampling on fixed-angle MaxCut QAOA; 45 ER random graphs; $N=1800$): **3 U**.
- **L3-C1 / L3-C2 / L3-C3** (six-regime simulator-noise diagnostic on fixed-angle MaxCut QAOA; 45 ER random graphs; $N=270$): **3 U**.
- **ALGO-C1 / ALGO-C2 / ALGO-C3** (optimized QAOA over 30 ER graphs; $N=900$): **3 U**.
- **COMB-C1 / COMB-C2 / COMB-C3** (joint L1$\times$L2$\times$L3 stress on 20 ER graphs at $n{=}10$; $N=1440$): **3 U**.
- Aggregate: **0 Sustained / 13 Unresolved / 2 Reversed within audited scope.**
- Cluster bootstrap on `instance_id`: **1000 / 1000 agreement per claim** across all 15 diagnostics.

Evidence:

- [internal_corpus/rq3_controlled_validation_suite.md](internal_corpus/rq3_controlled_validation_suite.md) — umbrella record and per-axis operationalization.
- [internal_corpus/rq3_controlled_validation_matrix.csv](internal_corpus/rq3_controlled_validation_matrix.csv) — coverage matrix.
- Per-diagnostic audit-space records under [internal_corpus/](internal_corpus/) (L1Q / L2 / six-regime L3 / ALGO / combined).
- Row-level grids and summaries:
  [L1Q](results/paper/output/figures/section5/l1_within_qiskit_diagnostic_data.csv),
  [L2](results/paper/output/figures/section5/l2_sampling_diagnostic_data.csv),
  [six-regime L3](results/paper/output/figures/section5/l3_noise_diagnostic_data.csv),
  [ALGO](results/paper/output/figures/section5/algo_diagnostic_data.csv), and
  [combined](results/paper/output/figures/section5/combined_layer_diagnostic_data.csv).
- [results/paper/output/figures/section5/rq3_controlled_validation_summary.csv](results/paper/output/figures/section5/rq3_controlled_validation_summary.csv) — unified five-diagnostic summary.

The headline checker recomputes each claim's $N$ and preserved-cell count from these
grids and crosschecks all 15 summary rows. The qiskit-heavy grid generators remain
outside this anonymous package. The six-regime L3 is the manuscript-facing L3
diagnostic; an earlier four-regime diagnostic is excluded and not double-counted.

### RQ4 — Stability and robustness

RQ4 checks whether scalar-directional verdicts depend on statistical or audit-policy
choices: preservation threshold $\tau$, dependence-aware grouping, tie handling,
budget / seed-count expansion, the practical-effect threshold $\epsilon$, and ALGO-axis
bookkeeping.

**Finding: the checks preserve primary labels under the main tested settings, with
documented boundary cases** — one record is cluster-sensitive, two records lack the
per-cell traces needed for some checks, and finite-$N$ extreme labels soften at
$\tau=0.99$. The specific sensitivity and evidence-boundary cases are recorded in
[external_audit/tier1_robustness/](external_audit/tier1_robustness/).

- **Threshold $\tau$.** Tier-1 labels are unchanged at $\tau \in \{0.90, 0.95\}$; at
  $\tau=0.99$ the finite-$N$ extreme labels (EX-C1/EX-C2 Sustained, EX-C7/EX-C8 Reversed)
  soften to Unresolved. The canonical check shifts 10 of 24 borderline claims to
  Unresolved at $\tau=0.99$.
- **Dependence-aware grouping.** The 47-claim union (24 canonical $+$ 8 external $+$
  15 RQ3 controlled-validation-suite; earlier four-regime L3 excluded by construction)
  shows cluster-bootstrap agreement **47 / 47** with the primary Wilson classifications
  ($B=1000$ per claim). Tier-1 per-cell cluster bootstrap ($B=10{,}000$) identifies
  **EX-C3 as cluster-bootstrap-sensitive** (one circuit dominates; 6.4\% of resamples
  reach Sustained, although no single-cluster deletion flips its primary Unresolved
  label). **EX-C2 and EX-C4 are unavailable for this check** because their per-cell
  traces are not materialized.
- **Tie handling.** **EX-C7 has 0 preserved cells (0/80 primary; 62 contradictions,
  18 ties) and remains contradicted-dominated**, but its categorical *Reversed* label is
  policy-bounded: it softens to Unresolved if ties are excluded (0/62) or counted as
  half-preserving (9/80). Records without per-cell traces (EX-C2, EX-C4) are unavailable
  for this check.
- **Budget / seed-count expansion.** All replayable Tier-1 compiler records keep their
  primary labels through $N=320$; **EX-C7 remains 0/320 preserved** (Reversed). The
  canonical audit-budget sensitivity over $N \in \{40, 80, 120, 160, 240, 320\}$ yields
  $10 / 1 / 1 / 0 / 0 / 0$ reclassifications.
- **Practical-effect $\epsilon$ and ALGO bookkeeping.** No classification changes among
  the analyzable practical-effect checks (0 of the 13 of 30 claims with a natural
  $\epsilon$); ALGO-axis placement bookkeeping does not change matched records or Wilson
  labels (0 of 24). Both remain descriptive.

Evidence:

- [external_audit/tier1_robustness/](external_audit/tier1_robustness/) — per-cell primary evidence; threshold / cluster / leave-one-cluster-out / tie-policy / budget tables; the per-dimension [tier1_robustness_status.csv](external_audit/tier1_robustness/tier1_robustness_status.csv) and [statistical_robustness_summary.md](external_audit/tier1_robustness/statistical_robustness_summary.md); re-runnable via [tier1_robustness_analysis.py](external_audit/tier1_robustness/tier1_robustness_analysis.py).
- [results/paper/output/figures/section5/cluster_bootstrap_47.csv](results/paper/output/figures/section5/cluster_bootstrap_47.csv) — 47-claim union agreement.
- [results/paper/output/figures/section5/sensitivity_summary.csv](results/paper/output/figures/section5/sensitivity_summary.csv) — $\tau$ / $N$ / ALGO-toggle sensitivity.
- [external_audit/budget_sensitivity/expanded_seed_sensitivity.csv](external_audit/budget_sensitivity/expanded_seed_sensitivity.csv) — seed expansion to $N=320$.
- [external_audit/budget_sensitivity/RECONSTRUCTION_README.md](external_audit/budget_sensitivity/RECONSTRUCTION_README.md) and [recon_driver.py](external_audit/budget_sensitivity/recon_driver.py) — 80/80 reconstruction gate, raw JSONL provenance, and read-only derivation of the N=80..320 expansion tables.
- [results/paper/output/figures/section5/perturbation_diagnostic.md](results/paper/output/figures/section5/perturbation_diagnostic.md) — matched-block diagnostic.

The RQ4 alignment is also verified by
[scripts/check_rq4_robustness.py](scripts/check_rq4_robustness.py).

## Minimal framework core

This artifact includes a qiskit-free verdict-core subset of CLAIMSTAB-QC under
[src/claimstab/](src/claimstab/). The bundled tests in [tests/](tests/) exercise the
Wilson S/U/R rule, relation checkers, funnel-count consistency, and manifest-loading
logic used to verify the paper's reported results. The artifact ships locked outputs
and lightweight verification scripts; the qiskit-heavy execution adapters and the
long-run simulation pipeline are intentionally not bundled.

## Main reviewer entry points

| File | Purpose |
|---|---|
| [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) | Short top-level directory map and the 53-design auditability inventory note. |
| [PAPER_CLAIMS_TO_EVIDENCE.md](PAPER_CLAIMS_TO_EVIDENCE.md) | Traceability table mapping each paper-facing number to source data, scripts, and verification actions. |
| [ENVIRONMENT.md](ENVIRONMENT.md) | Reviewer-check dependencies (pandas, pytest; numpy only for the optional Tier-1 robustness regeneration) and the pinned full-framework toolchain (Python 3.12.4, Qiskit 2.3.1, pytket 2.16.0). |

## Terminology used in this artifact

The artifact uses the manuscript's verdict and design vocabulary throughout.

- **Sustained / Unresolved / Reversed** — the three-state verdict against threshold $\tau$.
- **Declared audit design** — the per-claim enumerated or balanced-sampled design over the source-supported audit axes; $N$ denotes the size of this design and is per-claim.
- **Materialized external audit surface** — the 8 T1 artifact-backed claims that pass both screens in RQ1.
- **Controlled audit-space validation** — the RQ3 five-diagnostic suite that exercises the framework over L1 / L2 / L3 / ALGO / combined surfaces with the remaining axes pinned.
- **Canonical family-diversity contrast** — the C1–C24 paradigm-controlled supporting surface.

## Anonymity

- No submission-author names, institutions, ORCID, or contact information appear in this artifact.
- No public GitHub / GitLab / Zenodo / DOI URLs identifying the authors appear in the manuscript or in artifact-facing documents.
- Verbatim corpus evidence may contain names, affiliations, or contact strings of
  **third-party subject-paper authors**. Those public bibliographic details are
  retained only where needed for source traceability and do not identify the
  submission authors.
- The manuscript's anonymized EX-C baseline labels are crosswalked to the public
  third-party source evidence through
  [external_audit/mapping/source_mapping_anonymized.csv](external_audit/mapping/source_mapping_anonymized.csv).

## Scope notes

- The 8 external audits are the complete materialized subset under the two-stage screen, not a prevalence sample.
- The RQ3 controlled audit-space validation suite validates classifier behavior under designed audit spaces; it does not increase the external published-claim count.
- L3 coverage is limited to controlled simulator noise (Qiskit Aer six-regime ladder); live-hardware drift and cross-vendor calibration are out of scope.
- Quick checks verify locked outputs; they do not rerun long quantum-software simulations.
