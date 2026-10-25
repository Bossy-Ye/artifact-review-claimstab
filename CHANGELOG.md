# Changelog

## Camera-ready (2026)

Review snapshot: commit `d68fa5e`. No new experiments; counts unchanged.

- Label `Reversed` renamed `Not preserved` (rule unchanged) in code, tests, cards,
  docs and derived CSVs. `calibration_results.csv` kept as written (legacy field).
- Cluster bootstrap described as computed: 15 RQ3 rows resampled (B = 1000); the 24
  canonical and 8 external rows carry one iteration. Claim cards cite the Tier-1
  per-cell check (B = 10,000) instead.
- EX-C4: B_A is Copula-QAOA, per the extraction record; audited n_items 6–10 within
  the source's 5–10.
- Evidence inventory: paths absent from the artifact marked `[not bundled]`;
  `check_artifact_files.py` checks every inventory path.
- `recompute_agreement.py` writes LF; it no longer exits 1 on matching tables.
- Added `check_admissibility_sensitivity.py` (RQ1, 79 planning records).
- Removed unused `inference/status_remap.py`.
- De-anonymized README and manifest.
