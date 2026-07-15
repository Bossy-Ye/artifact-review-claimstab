# Inter-rater agreement / coding-validity

The paper-facing coding-validity check is the **stratified 120-item consistency
audit**. Its full evidence (agreement tables, confusion matrices, adjudication
records, the blinded recode sample, and a from-source recompute script) lives in
`artifact/data/corpus/coding_validity/`.

A stratified 120-item sample of the 455-claim corpus was drawn to span the
auditability-funnel boundaries and independently re-coded against the source texts;
every disagreement was adjudicated against the source. Headline agreement:

- **Planning-feasible:** 92.11% agreement, Cohen's $\kappa$ = 0.835 (n = 114).
- **Auditable-design:** 96.55% agreement, Cohen's $\kappa$ = 0.782 (n = 58).
- **Proxy-free exact vs non-exact:** 100.0% agreement, Cohen's $\kappa$ = 1.000 (n = 58).

Two further binary fields are reported for completeness: scalar-directional
(76.32%, $\kappa$ = 0.424, n = 114) and claim-card-specifiable (89.47%, n = 114) —
for the latter the recode distribution is one-class-dominated, so percent agreement
and the confusion matrix are the primary read and Cohen's $\kappa$ is deflated by
the skewed marginals. All eight Tier-1 exact records in the sample remained
defensible after adjudication (8/8); the adjudicated corrections move the broader
funnel counts but leave the eight proxy-free exact cards unchanged, consistent with
`artifact/corrected_headline_counts.csv`.

Both label states are traced to a single in-artifact file,
`artifact/source_grounded_claim_adjudication.csv` (`previous_*` = initial
annotation, `adjudicated_*` = recode). To reproduce the numbers above from source:

```bash
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
```
