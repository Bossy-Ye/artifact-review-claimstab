# Toolchain / environment

## Reviewer checks (this artifact)

The reviewer-facing checks are **pure Python and qiskit-free**. They need only:

- Python 3.10+ (developed on 3.12)
- `pandas>=2.0`, `pytest>=7.0`  (see `../requirements.txt`)

```bash
pip install -r requirements.txt
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
```

The bundled verdict-core (`artifact/src/claimstab/`) imports no qiskit/numpy/scipy.

The optional Tier-1 robustness regeneration
(`external_audit/tier1_robustness/tier1_robustness_analysis.py`) additionally uses
`numpy`; it is not required by the reviewer checks above.

## Full-framework / external-audit toolchain (pinned)

The RQ2 external audits and the validated reconstruction were produced under a
pinned toolchain, recorded with the locked traces:

- Python **3.12.4**
- Qiskit **2.3.1**
- pytket **2.16.0** (RQ2 reconstruction); pytket **2.18.0** for the SD4 current-baseline comparison
- NumPy, SciPy, pandas (declared pins: `qiskit 2.3.1` as used for the locked audits,
  `numpy>=1.24`, `pandas>=2.0`)

Sources in the artifact:
- `external_audit/budget_sensitivity/RECONSTRUCTION_README.md` — exact versions used
  for the EX-C3/C5/C6/C7 reconstruction gate (Python 3.12.4, Qiskit 2.3.1, pytket 2.16.0).
- `rq2_audit_design_ledger.csv` — per-record toolchain notes (e.g. SD4 baseline
  Qiskit 2.3.1 / pytket 2.18.0).

Compiler and runtime verdicts are interpreted relative to this locked toolchain
version (see the paper, Threats — Hardware and toolchain coverage). Reproducing the
external audits requires this qiskit/pytket toolchain; reproducing the reported
**numbers** does not (the checks above read the locked outputs).
