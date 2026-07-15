# Anonymous submission artifact

This repository contains the **artifact for the submitted paper** on auditing the
directional stability of comparative claims in quantum software. It is prepared for
**double-anonymous review**.

Everything reviewer-facing is under [`artifact/`](artifact/). Start with
[`artifact/README.md`](artifact/README.md), which maps each reported result to its
evidence and verification command.

## Main checks

The default checks are read-only, run in well under a minute, and do **not** require
qiskit or quantum simulation. Install the tested reviewer environment with
`pip install -r requirements-lock.txt` (or use the compatible ranges in
`requirements.txt`).

```bash
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/build_rq1_claim_decisions.py
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py
python3 artifact/external_audit/budget_sensitivity/recon_driver.py
```

## Layout

- `artifact/` — data, scripts, locked outputs, the 120-item coding-validity package,
  the minimal qiskit-free verdict-core (`artifact/src/`), and the smoke tests
  (`artifact/tests/`).
- `LICENSE` — Apache-2.0.
- `requirements.txt` — minimal dependencies for the reviewer checks.

The artifact is self-contained: the checks above pass from this repository as
mirrored, with no additional data. The commands verify the shipped evidence; they
do not rerun the long quantum-software experiments. Report files are generated only
when a checker is called with `--write-report` (and agreement tables only with
`--write`).

Anonymization boundary: submission-author names, institutions, acknowledgments,
funding, personal URLs, and author-identifying DOIs are omitted for double-anonymous
review. Third-party paper identifiers and source-artifact URLs remain where required
for evidence traceability.
