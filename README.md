# CLAIMSTAB-QC artifact

Artifact for B. Ye, P. Liang, M. Tavassoli Sabzevari, A. A. Khan,
*When "A Beats B" Needs Evidence: CLAIMSTAB-QC for Auditing Comparative Claims in
Quantum Software*, ICSE 2027.

Start at [`artifact/README.md`](artifact/README.md). Every reported number maps to a
file and a check in [`artifact/PAPER_CLAIMS_TO_EVIDENCE.md`](artifact/PAPER_CLAIMS_TO_EVIDENCE.md).

## Checks

Read-only, under a minute, no qiskit. Tested on Python 3.12.

```bash
pip install -r requirements-lock.txt
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/build_rq1_claim_decisions.py
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/scripts/check_admissibility_sensitivity.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py
python3 artifact/external_audit/budget_sensitivity/recon_driver.py
```

The checks verify the shipped evidence. They do not rerun the quantum experiments.

## Scope

Not bundled: raw search-result pages, Stage-1/Stage-2 candidate rows (summary counts
only), the row-level 628 → 457 deduplication worksheet, per-paper worksheets, the
qiskit-heavy generators, and the SD/BD files marked `[not bundled]` in
`artifact/dry_run_visibility/evidence_inventory.csv`.

## Labels

`Not preserved`: Wilson upper bound ≤ 1 − τ. It was `Reversed` in the review
version; same rule, same counts. It does not assert the opposite ordering; ties and
contradictions are reported per record. `reporting_status` in
`artifact/results/data/synthetic/calibration_results.csv` is a legacy field, not this
rule; coverage uses `ci_contains_s_true`.

Changes since review: [CHANGELOG.md](CHANGELOG.md). License: Apache-2.0.
