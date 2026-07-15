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
| `artifact/field_study/` | RQ1 field corpus (250 screened → 119 included), raw extraction, derived claim-decision crosscheck, included-paper rollup, coding protocol, six-row Table III summary, and 79 supporting records. |
| `artifact/data/corpus/coding_validity/` | 120-item coding-validity package + `recompute_agreement.py`. |
| `artifact/claim_cards/` | Locked claim cards for the 8 exact records (EX-C1..EX-C8). |
| `artifact/rq2_audit_design_ledger.csv`, `artifact/rq2_relation_checker_alignment.csv` | RQ2 ledger (17 records: EX-C*, SD*, BD*) and relation-checker alignment. |
| `artifact/dry_run_visibility/evidence_inventory.csv` | Maps every RQ2 unit to its design-lock and measured-trace evidence. |
| `artifact/external_audit/` | RQ2 materialization tiers, audit-space contracts, anonymized source mapping, Tier-1 per-cell evidence, read-only reconstruction verification and seed/budget expansion, and road_b SD5/SD6 source tables. |
| `artifact/internal_corpus/` | RQ3 controlled-validation design records (L1Q / L2 / expanded-six-regime L3 / ALGO / combined) and canonical-24 audit-space construction. |
| `artifact/results/` | Vendored locked Section-5 outputs, including the five RQ3 row-level diagnostic grids and summaries consumed by the checks. |
| `artifact/src/` | Minimal qiskit-free verdict-core (`claimstab/`) exercised by the tests. |
| `artifact/scripts/` | Reviewer check scripts (file availability, headline numbers, Markdown links, RQ4 robustness). |
| `artifact/tests/` | Verdict-core, funnel-count, manifest-loading, relation-checker, and RQ4 tests. |
| `artifact/outputs/reports/` | Check reports generated on run (not tracked). |

## Auditable-design inventory (RQ1 → RQ2)

The six-row manuscript-facing summary for the reported **53 registry-level auditable
designs** is `artifact/field_study/rq1_materialization_barrier_taxonomy.csv`. The
separate `artifact/field_study/rq1_materialization_barrier_records_79.csv` enumerates
all 79 scalar-directional planning records and assigns exactly **8 exact, 2
source-materialized, 43 source-supported-extension, 20 relation-specific boundary,
2 verification-only, and 4 no-lockable-design** dispositions. Thus 8 + 2 + 43 = 53
are on the auditable-design side and 20 + 2 + 4 = 26 are boundaries.

`artifact/field_study/auditable_design_inventory.csv` is a compact implementation
manifest, not a 53-row census. Its `AUD-01`–`AUD-15` rows describe the 15 designs
with individual locks (8 exact + 2 source-materialized + 5 extensions); its single
`AUD-EXT-REGISTRY` row points to the record-level file for the remaining 38 registry-level
extensions. `BD-01` and `BD-02` are RQ2 stop-condition examples and are not counted
among the 53. The inventory is cross-referenced to `rq2_audit_design_ledger.csv`,
`dry_run_visibility/evidence_inventory.csv`, `rq2_relation_checker_alignment.csv`,
and `claim_cards/`.

[`field_study/rq1_materialization_barrier_taxonomy.csv`](field_study/rq1_materialization_barrier_taxonomy.csv)
supports manuscript Table III: it decomposes the 79 scalar-directional planning records
by strongest lockable evidence object or blocking evidence boundary — proxy-free scoped
(8), lockable but not proxy-free scoped (43 + 2), and boundary (20 + 2 + 4). The counts
sum to 79 and explain the 79-to-8 materialization gap. The summary, separate
record-level evidence, derived RQ1 decision crosscheck, and corrected count table are
jointly verified by
`scripts/build_rq1_claim_decisions.py`, `scripts/check_headline_numbers.py`, and the
test suite.

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

The submission authors are not identified. `external_audit/mapping/source_mapping_anonymized.csv`
uses P1–P4 source groups to crosswalk the manuscript's anonymized baseline labels;
public third-party paper titles, arXiv stems, and source-artifact URLs are retained
where required for evidence traceability. No submission-author identities,
institutions, or unblinding keys are included.
