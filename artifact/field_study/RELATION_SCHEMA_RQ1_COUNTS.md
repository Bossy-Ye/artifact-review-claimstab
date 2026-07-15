# RQ1 Relation-Schema Count Traceability

This note maps the RQ1 relation-schema terminology in the manuscript to
reviewer-facing artifact files. It does not introduce new experiments or
new result values; it exposes locked per-claim flags derived from the
corrected source-grounded accepted comparative claims (455; see the
Authority note below), the materialization-tier census, and the 8-card
scalar RQ2 output file.

## Authority note

The 457-row registry records raw Stage-3 extraction records before claim-level
correction. The paper-facing final accepted-claim count is 455, supported by
`corrected_headline_counts.csv` and `source_grounded_claim_adjudication.csv` (both
located one directory above this note). The derived row-level crosscheck
`claims/rq1_claim_decisions_457.csv` applies the 16-row source-grounded decisions to
the base per-claim flags and must agree with the corrected paper-facing count table:

| count | corrected (authority) | prior |
|---|---:|---:|
| accepted comparative claims | 455 | 457 |
| claim-card-specifiable | 175 | 166 |
| scalar-directional | 145 | 142 |
| planning-feasible | 93 | 92 |
| scalar-oriented planning records | 79 | 78 |
| broader auditable designs | 53 | 53 |
| proxy-free exact cards | 8 | 8 |
| non-scalar relation-typed (specifiable) | 30 = 26 + 2 + 2 | 24 = 23 + 1 + 0 |

The raw extraction file `claims/extracted_claims_457.csv` (457 rows) and
the locked materialization-tier census
`../external_audit/materialization/materialization_tiers_76.csv` (76 rows:
8 T1, 58 T3, 10 T4) retain their pre-adjudication values and are historical
inputs; naive row counts over them therefore reflect the prior counts, not
the corrected authority. The corrected counts differ by a small set of
source-grounded adjudication decisions documented in
`../headline_count_final_crosscheck_decisions.csv`. The decision crosscheck is regenerated or
verified by `../scripts/build_rq1_claim_decisions.py`.

## Terminology Crosswalk

| Manuscript term | Artifact term or filter | Reviewer-facing file |
|---|---|---|
| representation | source text contains enough relation-card fields to identify problem/scope, compared baselines, metric, and relation | `claims/rq1_claim_decisions_457.csv` |
| planning | relation-card fields plus artifact/support and feasibility gates needed to plan an audit surface | `claims/rq1_claim_decisions_457.csv` |
| materialization | proxy-free executable, parser-backed, or otherwise source-supported evidence sufficient to evaluate the declared audit surface | `../external_audit/materialization/materialization_tiers_76.csv` |
| scalar-oriented planning record | relation-aware planning candidate that also has scalar-directional form | `claims/rq1_claim_decisions_457.csv` |
| proxy-free materialized | row appears in the 8-card scalar external audit output | `../../artifact/results/paper/output/figures/section5/external_forest_data.csv` |
| O1--O7 | operationalizability gates recorded per claim | `claims/extracted_claims_457.csv` |
| T1/T2/T3/T4 | materialization tiers over perturbation-audit candidates | `../external_audit/materialization/materialization_tiers_76.csv` |
| operationalizable | row passes O1--O7 under the field-study screen | `claims/extracted_claims_457.csv` |
| audit eligible | `operationalizability_category == audit_eligible_operationalizable` | `claims/relation_schema_rq1_flags.csv` |
| verification-only | deterministic verification record, not a perturbation-audit candidate | `claims/relation_schema_rq1_flags.csv` |

## Locked Count Table and row-level crosscheck

| Paper-facing count | Count | Artifact file | Filter definition |
|---|---:|---|---|
| accepted comparative claims | 455 | `claims/rq1_claim_decisions_457.csv` | `final_accepted_comparative_claim == true` |
| claim-card-specifiable under relation schema | 175 | `claims/rq1_claim_decisions_457.csv` | `final_claim_card_specifiable == true` |
| scalar-directional | 145 | `claims/rq1_claim_decisions_457.csv` | `final_scalar_directional == true` |
| planning-feasible | 93 | `claims/rq1_claim_decisions_457.csv` | `final_planning_feasible == true` |
| scalar-oriented planning records | 79 | `claims/rq1_claim_decisions_457.csv` | `final_scalar_oriented_planning == true` |
| non-scalar relation-typed (specifiable) | 30 = 26 + 2 + 2 | `claims/rq1_claim_decisions_457.csv` | final specifiable is true and final scalar-directional is false |
| perturbation-audit candidates | 77 | `../corrected_headline_counts.csv`; locked census `../external_audit/materialization/materialization_tiers_76.csv` (76 pre-adjudication) | `perturbation_audit_candidate == true` |
| verification-only records | 2 | `claims/relation_schema_rq1_flags.csv` | `verification_only == true` |
| scalar-directional claims outside the 79 | 66 | `claims/relation_schema_rq1_flags.csv` + adjudication overlay | `scalar_directional == true` and `planning_feasible == false` (62 lack public artifact/support, 6 require real hardware/noise, 2 in both) |
| broader auditable designs | 53 | `rq1_materialization_barrier_taxonomy.csv`; `rq1_materialization_barrier_records_79.csv` | six-row manuscript summary plus record-level support; exact + source-materialized + source-supported-extension designs over the 79 (8 + 2 + 43) |
| proxy-free materialized RQ2 cards | 8 | `claims/relation_schema_rq1_flags.csv`; `../../artifact/results/paper/output/figures/section5/external_forest_data.csv` | `materialized_rq2 == true` |
| remaining scalar-oriented planning records not materialized | 71 | `claims/relation_schema_rq1_flags.csv` + adjudication overlay | `scalar_oriented_planning == true` and `materialized_rq2 == false` |

The machine-readable version of this table is
`claims/relation_schema_rq1_counts.csv`.

## Filter Definitions

- `specifiable_relation_schema`: O3, O5, O6, and O7 pass. The source
  exposes compared objects, metric, comparator identities, and problem or
  instance family enough to fill an R-based claim card.
- `scalar_directional`: O3, O4, O5, O6, and O7 pass. This is the scalar
  directional instantiation where the source relation is a strict scalar
  ordering.
- `planning_feasible`: O1, O2, O3, O5, O6, and O7 pass. This is a
  relation-aware planning surface and can include non-scalar relations.
- `scalar_oriented_planning`: O1, O2, O3, O4, O5, O6, and O7 pass. This
  equals the intersection of the scalar-directional and planning-feasible
  surfaces.
- `perturbation_audit_candidate`: `operationalizability_category` is
  `audit_eligible_operationalizable`.
- `verification_only`: `operationalizability_category` is
  `verification_eligible_operationalizable`.
- `materialized_rq2`: the claim appears in the locked 8-card scalar
  external audit output.

## Count Relationships (corrected counts)

| Relationship | Value | Interpretation |
|---|---:|---|
| scalar-directional subset of relation-schema specifiable | 145 / 175 | scalar direction is one instantiation of the broader relation card |
| planning-feasible subset of relation-schema specifiable | 93 / 175 | planning feasibility adds artifact/support and feasibility gates |
| scalar-oriented planning records | 79 | `scalar_directional` intersect `planning_feasible` |
| scalar-directional outside planning | 66 | scalar-specifiable but not planning-supported or feasible |
| planning-feasible outside scalar-directional | 14 | relation-aware but non-scalar planning candidates |
| scalar-oriented not materialized as RQ2 | 71 | 58 T3, 10 T4, 2 verification-only records, and 1 adjudication-add candidate not in the locked 76-row census |

## Files Reviewers Should Inspect

1. `../corrected_headline_counts.csv` and `../source_grounded_claim_adjudication.csv`
   for the paper-facing corrected counts and their adjudication support.
2. `claims/rq1_claim_decisions_457.csv` for the derived per-candidate decision crosscheck.
3. `claims/extracted_claims_457.csv` for the original O1--O7 gate labels
   (raw 457-row extraction; pre-adjudication).
4. `claims/relation_schema_rq1_flags.csv` for pre-adjudication per-claim relation-schema
   flags.
5. `rq1_materialization_barrier_taxonomy.csv` for the six-row manuscript Table III summary.
6. `rq1_materialization_barrier_records_79.csv` for record-level inspection of that summary.
7. `claims/relation_schema_rq1_counts.csv` for the compact count summary.
8. `../external_audit/materialization/materialization_tiers_76.csv` for
   the locked 76-row perturbation-audit census and T1/T3/T4 split.
9. `../../artifact/results/paper/output/figures/section5/external_forest_data.csv` for
   the 8 proxy-free scalar RQ2 cards.
