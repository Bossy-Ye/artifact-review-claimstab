# CLAIMSTAB-QC artifact

Evidence for *When "A Beats B" Needs Evidence: CLAIMSTAB-QC for Auditing Comparative
Claims in Quantum Software* (ICSE 2027): locked outputs and read-only checks. The
long quantum simulations are not rerun.

- [PAPER_CLAIMS_TO_EVIDENCE.md](PAPER_CLAIMS_TO_EVIDENCE.md): reported number → file → check.
- [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md): directory map.
- [ENVIRONMENT.md](ENVIRONMENT.md): dependencies and the pinned toolchain.

## Checks

From the repository root. Read-only, under a minute, no qiskit.

```bash
python3 -m pytest artifact/tests/ -q                                 # verdict core, funnel, manifests
python3 artifact/scripts/build_rq1_claim_decisions.py                # 457 records -> 455 accepted
python3 artifact/scripts/check_headline_numbers.py                   # RQ1-RQ4 numbers
python3 artifact/scripts/check_artifact_files.py                     # files; inventory paths
python3 artifact/scripts/check_admissibility_sensitivity.py          # RQ1: 8 stays 8
python3 artifact/scripts/worked_example_exc7.py                      # EX-C7, paper Figs. 4-5
python3 artifact/data/corpus/coding_validity/recompute_agreement.py  # 120-item agreement, kappa
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py                     # RQ4
python3 artifact/external_audit/budget_sensitivity/recon_driver.py   # seed expansion to N = 320
```

`--write` and `--write-report` regenerate derived files or reports; by default nothing
is written. Locked outputs read by the checks sit under `results/<original path>`.

## Map

| Paper | Evidence |
|---|---|
| RQ1 corpus: 250 screened, 119 included, 131 excluded | [paper_list_250_screened.csv](field_study/corpus/paper_list_250_screened.csv), [inclusion_exclusion_criteria.md](field_study/corpus/inclusion_exclusion_criteria.md), [search_protocol.md](field_study/corpus/search_protocol.md), [search_log.csv](field_study/corpus/search_log.csv) |
| RQ1 claims: 630 → 628 → 457 → 455 | [extracted_claims_457.csv](field_study/claims/extracted_claims_457.csv) (raw records), [rq1_claim_decisions_457.csv](field_study/claims/rq1_claim_decisions_457.csv) (455 accepted), [corrected_headline_counts.csv](corrected_headline_counts.csv), [source_grounded_claim_adjudication.csv](source_grounded_claim_adjudication.csv), unit and acceptance rule in [claim_unitization_rules.md](field_study/coding_protocol/claim_unitization_rules.md) |
| RQ1 funnel 175 → 79 → 53 → 8; Table III | [rq1_materialization_barrier_taxonomy.csv](field_study/rq1_materialization_barrier_taxonomy.csv) (Table III), [rq1_materialization_barrier_records_79.csv](field_study/rq1_materialization_barrier_records_79.csv) (per record) |
| RQ1 coding validity | [data/corpus/coding_validity/](data/corpus/coding_validity/) |
| RQ2 Tier 1: EX-C1–EX-C8, 2 S / 4 U / 2 NP; Table IV, Fig. 3 | [claim_cards/](claim_cards/), [external_forest_data.csv](results/paper/output/figures/section5/external_forest_data.csv), [external_audit_space_contracts.md](external_audit/audit_space/external_audit_space_contracts.md), per-cell traces in [per_cell_inputs/](external_audit/tier1_robustness/per_cell_inputs/) (six records) |
| RQ2 Tiers 2–3: SD1–SD7, BD1–BD2 | [rq2_audit_design_ledger.csv](rq2_audit_design_ledger.csv), [rq2_relation_checker_alignment.csv](rq2_relation_checker_alignment.csv), [evidence_inventory.csv](dry_run_visibility/evidence_inventory.csv), SD5/SD6 tables in [road_b/](external_audit/road_b/) |
| RQ3 canonical C1–C24 | [canonical24_forest_data.csv](results/paper/output/figures/section5/canonical24_forest_data.csv), [baseline_diagnostic_fallback.csv](results/paper/output/figures/section5/baseline_diagnostic_fallback.csv), [canonical24_audit_space_construction.md](internal_corpus/canonical24_audit_space_construction.md) |
| RQ3 axis surfaces (15 claims) | [rq3_controlled_validation_summary.csv](results/paper/output/figures/section5/rq3_controlled_validation_summary.csv), per-surface grids in [section5/](results/paper/output/figures/section5/), [rq3_controlled_validation_suite.md](internal_corpus/rq3_controlled_validation_suite.md) |
| RQ3 decision-rule controls | [calibration_results.csv](results/data/synthetic/calibration_results.csv), [synthetic_reversed_expanded.csv](results/output/paper/icse_pack/derived/ANALYSIS/synthetic_reversed_expanded.csv) |
| RQ4 robustness | [tier1_robustness/](external_audit/tier1_robustness/), [budget_sensitivity/](external_audit/budget_sensitivity/), [cluster_bootstrap_47.csv](results/paper/output/figures/section5/cluster_bootstrap_47.csv), [sensitivity_summary.csv](results/paper/output/figures/section5/sensitivity_summary.csv) |

## Worked example: EX-C7

Source text → claim card → audited scope → 80 matched cells → outcome.

- Claim card: [EX-C7.yaml](claim_cards/EX-C7.yaml). Benchpress's "Qiskit outperforms BQSKit, Staq, and Tket in terms of 2Q gate count", narrowed to Qiskit < Tket.
- Audited scope: four auditor-constructed connectivity-stress circuits on a four-node line; Qiskit at optimization levels 0–3, seeds 0–4; Tket's default pipeline.
- Cells: [ext_2409_08844v2_claim3_measurements.csv](external_audit/tier1_robustness/per_cell_inputs/ext_2409_08844v2_claim3_measurements.csv).
- `worked_example_exc7.py`: level 0 has 20 contradicted cells; levels 1–3 have 14 contradicted and 6 tied each; 0/62/18 overall → Not preserved.

## Scope

- EX-C3, EX-C5 and EX-C7 use the same four auditor-constructed circuits; EX-C6 uses a synthetic dense graph. Verdicts cover these designs only, not the sources' suites.
- Cluster bootstrap resamples only the 15 RQ3 claims (B = 1000). The Tier-1 per-cell check uses B = 10,000: EX-C3 is sensitive, and EX-C2 and EX-C4 have no per-cell traces. The 24 canonical claims are not bootstrapped. Leave-one-cluster-out gives N = 60 < 73.
- Not bundled:
  - raw search-result pages;
  - the row-level 630 and 628 candidate sets (counts only);
  - the 628 → 457 deduplication worksheet;
  - per-paper worksheets;
  - most SD/BD design and trace files (marked `[not bundled]` in the inventory);
  - the qiskit-heavy generators.
- Not reconstructable from the artifact: the search-to-250 step, and the steps from the 119 papers to the 457 extraction records.
- Third-party use has not been evaluated.

## Terms

- **S/U/NP**: Sustained if the Wilson lower bound ≥ τ; Not preserved if the upper bound ≤ 1 − τ; Unresolved otherwise (τ = 0.95). Ties alone can reach Not preserved; tie and contradiction counts are reported per record. Review-version files may say `Reversed`; the rule and counts are the same.
- **Tiers**: Tier 1 is proxy-free scoped: matched cells with source-supported baselines, metric, settings, and rule. Tier 2 covers source-materialized, source-rule, extension, and sensitivity outputs. Tier 3: the design, evidence object, or outcome rule cannot be locked; no verdict.
- In CSVs and code, `exact` means proxy-free scoped.
- Review-version baseline labels (`A vs B` … `A vs I`) map to tools via [source_mapping_anonymized.csv](external_audit/mapping/source_mapping_anonymized.csv).
- Verdict core: [src/claimstab/](src/claimstab/), pure Python.
