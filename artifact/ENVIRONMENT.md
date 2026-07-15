# Toolchain / environment

## Reviewer checks (this artifact)

The reviewer-facing checks are **qiskit-free**. The tested environment is:

- Python **3.12.13**
- the exact package set in `../requirements-lock.txt`

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/build_rq1_claim_decisions.py
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py
python3 artifact/external_audit/budget_sensitivity/recon_driver.py
```

The compatible, non-locked ranges in `../requirements.txt` support Python 3.10+
when an exact Python 3.12 environment is unavailable. The bundled verdict-core
(`artifact/src/claimstab/`) imports no qiskit/numpy/scipy.

NumPy is used only by the optional Tier-1 robustness regeneration
(`external_audit/tier1_robustness/tier1_robustness_analysis.py`). Default reviewer
commands write nothing. The three report-producing checkers accept
`--write-report`; the RQ1 registry and agreement scripts accept `--write` only for
intentional regeneration of their committed derived CSVs.

## Full-framework / external-audit toolchain (pinned)

The RQ2 external audits and the validated reconstruction were produced under a
pinned toolchain, recorded with the locked traces:

- Python **3.12.4**
- Qiskit **2.3.1**
- pytket **2.16.0** (RQ2 reconstruction); pytket **2.18.0** for the SD4 current-baseline comparison
- NumPy, SciPy, pandas (declared pins: `qiskit 2.3.1` as used for the locked audits,
  `numpy>=1.24`, `pandas>=2.0`)

Sources in the artifact:
- `external_audit/budget_sensitivity/RECONSTRUCTION_README.md` — exact versions,
  cell-level reconstruction gate, and evidence boundary for EX-C3/C5/C6/C7.
- `external_audit/budget_sensitivity/reconstruction_gate_report.csv` and
  `reconstructed_vs_locked_diff.csv` — 80/80 metric and label matches for all four
  reconstruction records, with zero mismatch rows.
- `external_audit/budget_sensitivity/recon_driver.py` and `recon_raw/` — optional
  compute/consolidate driver and the locked raw reconstruction outputs.
- `rq2_audit_design_ledger.csv` — per-record toolchain notes (e.g. SD4 baseline
  Qiskit 2.3.1 / pytket 2.18.0).

Compiler and runtime verdicts are interpreted relative to the locked toolchain
(see the paper, Threats — Hardware and toolchain coverage). The four compiler
reconstructions can be recomputed with the pinned qiskit/pytket environment, but
the complete RQ2 and RQ3 long-run generators are not bundled. Reproducing the
reported **numbers** does not require qiskit/pytket: the default checks derive them
from the shipped row-level and aggregate evidence.
