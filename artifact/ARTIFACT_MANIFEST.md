# CLAIMSTAB-QC artifact manifest

Directory map. Checks and scope: [README.md](README.md). Number → file:
[PAPER_CLAIMS_TO_EVIDENCE.md](PAPER_CLAIMS_TO_EVIDENCE.md).

| Path | Contents |
|---|---|
| `field_study/` | RQ1: 250-paper screened pool, raw extraction (457), decision crosscheck (455), 119-paper rollup, coding protocol, Table III summary and its 79 records. |
| `data/corpus/coding_validity/` | 120-item consistency audit and `recompute_agreement.py`. |
| `claim_cards/` | EX-C1–EX-C8 claim cards. |
| `rq2_audit_design_ledger.csv`, `rq2_relation_checker_alignment.csv` | RQ2 ledger (17 records: EX-C, SD, BD) and relation-checker alignment. |
| `dry_run_visibility/evidence_inventory.csv` | Per RQ2 unit: design lock, trace, report; absent files marked `[not bundled]`. |
| `external_audit/` | Audit-space contracts, source mapping, Tier-1 per-cell traces and robustness, seed expansion, SD5/SD6 tables. |
| `internal_corpus/` | RQ3 design records (L1Q, L2, six-regime L3, ALGO, combined) and the C1–C24 construction. |
| `results/` | Locked outputs read by the checks, including the five RQ3 grids. |
| `src/` | Verdict core (`claimstab/`), pure Python. |
| `scripts/` | Checks: files, headline numbers, admissibility, EX-C7 worked example, links, RQ4. |
| `tests/` | Verdict core, funnel counts, manifests, relation checkers, RQ4, worked example. |

## 53 designs (RQ1 → RQ2)

`field_study/rq1_materialization_barrier_records_79.csv` assigns each of the 79
scalar-directional planning records one disposition: 8 proxy-free scoped,
2 source-materialized, 43 extension, 20 relation-specific boundary, 2 verification-only,
4 no lockable design. 8 + 2 + 43 = 53 designs; 20 + 2 + 4 = 26 boundaries.
`rq1_materialization_barrier_taxonomy.csv` is the six-row Table III summary.

`field_study/auditable_design_inventory.csv` is an implementation manifest, not a
53-row census: `AUD-01`–`AUD-15` are the 15 individually locked designs (8 proxy-free
scoped, 2 source-materialized, 5 extensions); `AUD-EXT-REGISTRY` points to the other 38
extensions; `BD-01`, `BD-02` are RQ2 stop examples, not among the 53.

SD4 is a diagnostic current-baseline extension, not a Tier-1 verdict. SD6 is a
source-rule aggregate: 0.36 follows the source's row selection; alternative ratios are
in `rq2_relation_checker_alignment.csv`.
