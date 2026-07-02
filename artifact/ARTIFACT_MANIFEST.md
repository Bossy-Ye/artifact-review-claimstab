# CLAIMSTAB-QC Artifact Manifest

Short top-level map of the anonymous reviewer artifact. The per-claim
evidence-to-file mapping is in `PAPER_CLAIMS_TO_EVIDENCE.md`; reviewer
verification commands and the RQ1–RQ4 evidence summary are in `README.md`;
dependencies and the pinned toolchain are in `ENVIRONMENT.md`.

This artifact ships **locked outputs and lightweight verification scripts**, not
the long-run simulation pipeline or the qiskit-heavy execution adapters. Locked
Section-5 outputs are vendored under `artifact/results/<original-repository-path>`
so the checks run from a self-contained `artifact/` tree.

## Directory map

| Path | Purpose |
|---|---|
| `artifact/field_study/` | RQ1 field corpus (250 screened → 119 included), claim extraction, coding protocol. |
| `artifact/data/corpus/coding_validity/` | 120-item coding-validity package + `recompute_agreement.py`. |
| `artifact/claim_cards/` | Locked claim cards for the 8 exact records (EX-C1..EX-C8). |
| `artifact/rq2_audit_design_ledger.csv`, `artifact/rq2_relation_checker_alignment.csv` | RQ2 ledger (17 records: EX-C*, SD*, BD*) and relation-checker alignment. |
| `artifact/dry_run_visibility/evidence_inventory.csv` | Maps every RQ2 unit to its design-lock and measured-trace evidence. |
| `artifact/external_audit/` | RQ2 materialization tiers, audit-space contracts, anonymized source mapping, Tier-1 seed/budget expansion, Tier-1 robustness, and road_b SD5/SD6 source tables. |
| `artifact/internal_corpus/` | RQ3 controlled-validation suite (L1Q / L2 / expanded-six-regime L3 / ALGO / combined) and canonical-24 audit-space construction. |
| `artifact/results/` | Vendored locked Section-5 outputs (figures, tables, CSVs) consumed by the checks. |
| `artifact/src/` | Minimal qiskit-free verdict-core (`claimstab/`) exercised by the tests. |
| `artifact/scripts/` | Reviewer check scripts (file availability, headline numbers, Markdown links, RQ4 robustness). |
| `artifact/tests/` | Verdict-core, funnel-count, manifest-loading, relation-checker, and RQ4 tests. |
| `artifact/outputs/reports/` | Check reports generated on run (not tracked). |

## Auditable-design inventory (RQ1 → RQ2)

`artifact/field_study/auditable_design_inventory.csv` records the **53 registry-level
auditable design entries** reported in RQ1, including **8 exact records, 2
source-materialized records, and 43 extension/diagnostic entries** over the 79
scalar-directional planning records. 15 entries have individual locked manifests
(8 exact + 2 source-materialized + 5 extension; rows `AUD-01`–`AUD-15`),
cross-referenced to `rq2_audit_design_ledger.csv`, `dry_run_visibility/evidence_inventory.csv`,
`rq2_relation_checker_alignment.csv`, and `claim_cards/`. The remaining registry-level
entries are represented through the registry (`AUD-EXT-DERIVED`) and supporting summary
evidence, with their derivation source recorded in the inventory. The two boundary
records (`BD1`, `BD2`) are materialization stop conditions and are **not** counted
among the 53. The count and its derivation are held in `corrected_headline_counts.csv`,
`field_study/claims/relation_schema_rq1_counts.csv`, and
`field_study/claims/relation_schema_rq1_flags.csv`.

[`field_study/rq1_materialization_barrier_taxonomy.csv`](field_study/rq1_materialization_barrier_taxonomy.csv)
supports manuscript Table III: it decomposes the 79 scalar-directional planning records
by strongest lockable evidence object or blocking evidence boundary — proxy-free scoped
(8), lockable but not proxy-free scoped (43 + 2), and boundary (20 + 2 + 4). The counts
sum to 79 and explain the 79-to-8 materialization gap; 8 + 43 + 2 are the 53
registry-level auditable design entries. Verified by `scripts/check_headline_numbers.py`.

The RQ1 corpus was built through a Google Scholar search-and-screen protocol with
artifact-side normalized provenance; raw Google Scholar pages are not bundled. See
[`field_study/corpus/search_protocol.md`](field_study/corpus/search_protocol.md) for
the normalized query records, screened-paper list, and identifier conventions.

`SD4` is a diagnostic current-baseline extension, not a Tier-1 S/U/R verdict (see its
note in `rq2_audit_design_ledger.csv`). `SD6` is a source-rule aggregate summary: the
artifact records its row-selection and convention boundary — the manuscript-facing 0.36
value follows the source-rule row selection, while alternative formal ratios are
documented in `rq2_relation_checker_alignment.csv`.

## Anonymization

Subject papers are anonymized at the source-group level (P1–P4) in
`external_audit/mapping/source_mapping_anonymized.csv`; per-claim arXiv stems are
retained in claim identifiers for traceability. No author identities, institutions,
or unblinding keys are included.
