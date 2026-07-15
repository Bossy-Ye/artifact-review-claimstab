# T3 Auditability-Boundary Mapping

This note records how the T3 missingness signal in RQ1 maps onto the
CLAIMSTAB-QC five-tuple components. It is a reviewer pointer: no new
empirical counts are introduced here. All counts referenced below come
from existing locked artifact files.

## Purpose

RQ1 reports a two-stage auditability surface (specification screen,
materialization screen). T3 is the largest non-T1 bucket on the
materialization screen (58 of 76 perturbation-audit candidates). This
note describes the interpretive boundary RQ1 places on T3: T3 marks
the boundary between scalar-oriented planning records and
source-supported audits, not a gap in the CLAIMSTAB-QC audit space. Some T3 cases omit
audit-space parameters; many others omit the comparison object itself.
For the latter, completing the audit would require reconstituting part
of the source contribution rather than merely sampling
$\mathcal{S}_{\textit{audit}}$.

## Source Data Files

| File | Role |
|---|---|
| `artifact/external_audit/materialization/materialization_tiers_76.csv` | Per-claim T1/T2/T3/T4 labels and missing-element flags for the 76 perturbation-audit candidates. |
| `artifact/external_audit/materialization/materialization_missing_elements.csv` | Multi-label missingness counts (artifact, hyperparameters, baseline, resource_budget, instance_generator, optimizer, data, metric, other) split by T3 and T4. |
| `artifact/external_audit/materialization/materialization_tier_validation.csv` | Validation review for non-T1 claims. |
| `artifact/external_audit/materialization/materialization_tier_report.md` | Narrative tier-assignment report. |

## Missing-Element to CLAIMSTAB-QC Component Mapping

| Missing element in T3 record | CLAIMSTAB-QC component | Auditability consequence |
|---|---|---|
| Proposed method / comparator implementation (`baseline`) | $\mathcal{B}_A$ or $\mathcal{B}_B$, cell execution | Cell execution cannot run without a runnable comparator; completing would reconstitute the source contribution. |
| Metric / measurement protocol (`metric`) | $\mathcal{M}$, $\delta_c$ computation | Per-cell comparative margin $\delta_c$ is not defined without the metric implementation. |
| Instance generator / benchmark data (`instance_generator`, `data`) | $\mathcal{P}_{\textit{inst}}$, $\mathcal{S}_{\textit{scope}}$ | Operational-scope sampling cannot be reproduced; the audit would draw from a different distribution. |
| Hyperparameters / optimizer settings (`hyperparameters`, `optimizer`) | $\mathcal{P}_{\textit{alg}}$, algorithmic axis of $\mathcal{E}_{\textit{env}}$ | Algorithmic-stochasticity axis is undefined; verdicts would reflect the auditor's algorithmic choices. |
| Resource budget (`resource_budget`) | $\mathcal{P}_{\textit{res}}$, fair-comparison boundary | Equal-resource boundary between $\mathcal{B}_A$ and $\mathcal{B}_B$ cannot be enforced. |
| Platform / backend setup (`other`, environment descriptors) | $\mathcal{E}_{\textit{env}}$ | Execution-environment axis is undefined; verdicts would reflect the auditor's platform. |
| Artifact / executable scripts (`artifact`) | Cell execution boundary | Even with the above specified, no runnable adapter exists; absent in all 58 T3 records by construction of the tier. |

## Boundary Interpretation

Two qualitatively different patterns appear in T3:

1. **Missing audit-space parameters only.** The comparison object
   (both $\mathcal{B}_A$ and $\mathcal{B}_B$) is named and externally
   available, but one or more of $\mathcal{P}_{\textit{alg}}$,
   $\mathcal{P}_{\textit{res}}$, $\mathcal{P}_{\textit{inst}}$, or
   $\mathcal{E}_{\textit{env}}$ is left unspecified by the source. A
   completion-supported audit under declared completion rules is
   conceivable for such cases.

2. **Missing comparison object.** The proposed method, its
   implementation, the measurement protocol, the benchmark dataset,
   or a paper-specific platform setup is itself absent. Completing
   the audit would require reimplementing part of the source
   contribution. Such cases are outside the source-supported audit
   surface used in RQ2.

The per-claim records in `materialization_tiers_76.csv` carry the
`missing_elements`, `paper_description_sufficiency`,
`estimated_implementation_effort`, and `reason_for_tier` columns that
support this distinction at the claim level.

## Scope of This Note

- This note is interpretive. It does not assign S/U/R verdicts to T3
  claims, does not introduce a new evidence stream, and does not
  modify Section V's classification outcomes.
- No new counts are claimed beyond those already verified in
  `PAPER_CLAIMS_TO_EVIDENCE.md` rows 14, 17.
- T3 remains outside the materialized external audit surface (RQ2).
  RQ2's audit surface is the 8 T1 scalar-directional cards.
