# Coding-validity package (120-item consistency audit)

This folder is the reviewer-facing evidence for the paper's coding-validity check.
It reproduces, from source, the three headline numbers reported in the manuscript:

| Decision boundary | n | % agreement | Cohen's kappa |
|---|---:|---:|---:|
| planning-feasible | 114 | 92.11 | 0.835 |
| auditable-design | 58 | 96.55 | 0.782 |
| proxy-free exact vs non-exact | 58 | 100.0 | 1.000 |

(Two further binary fields are reported for completeness: scalar-directional
76.32% / kappa 0.424 (n=114); claim-card-specifiable 89.47% / kappa 0.116 (n=114)
— for the last, the recode distribution is one-class-dominated, so percent
agreement and the confusion matrix are the primary read and kappa is deflated.)

## Design

A stratified **120-item** sample of the 455-claim corpus was drawn to span the
consequential auditability-funnel boundaries (claim-card specifiable, scalar vs
non-scalar, planning-feasible, auditable-design, proxy-free exact). The sample was
independently **re-coded against the source texts**; every disagreement was
adjudicated by revisiting the source paper, the worksheet, and the auditability
definitions. All eight Tier-1 exact records in the sample remained defensible after
adjudication (8/8); the adjudicated corrections move the broader funnel counts
(claim-card-specifiable +9 -> 175, scalar-directional +3 -> 145, planning-feasible
+1 -> 93) but leave the eight proxy-free exact cards unchanged — consistent with
`artifact/corrected_headline_counts.csv`.

## Files

| File | Contents |
|---|---|
| `agreement_tables.csv` | per-field n, label distributions, % agreement, Cohen's kappa, kappa status |
| `confusion_matrices.csv` | first x recode cell counts per field |
| `adjudication_records.csv` | every disagreement with adjudicated label + rationale + whether it changes a headline count |
| `recode_labels_120.csv` | the independent re-code labels for the 120 sampled items |
| `stratified_sample_120.csv` | the blinded sample (source location/excerpt + claim-card fields; first-pass labels hidden) |
| `blinded_recode_package_120.csv` | the blinded recode worksheet handed to the second coder (paper ids blinded) |
| `recompute_agreement.py` | regenerates `agreement_tables.csv` + `confusion_matrices.csv` from source |

## Reproduce

```bash
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
```

Both label states are traced to a single in-artifact file,
`artifact/source_grounded_claim_adjudication.csv`: the **first** (initial worksheet
annotation) labels are its `previous_*` columns and the **recode** labels are its
`adjudicated_*` columns. The script restricts to the 120 sampled `claim_id`s
(`recode_labels_120.csv`) and recomputes agreement, Cohen's kappa, and the
confusion matrices with no external dependencies. The printed values reproduce the
table above exactly.

## Anonymization

All files here are blinded: items are keyed by `item_id`/`claim_id`, paper ids are
either invariant arXiv-style ids or blinded, and no coder identities appear. The
unblinding key and any coder-named adjudication notes are **author-only** and are
deliberately kept outside the artifact (see the resolution report).
