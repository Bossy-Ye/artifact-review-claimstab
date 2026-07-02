# Anonymous submission artifact

This repository contains the **artifact for the submitted paper** on auditing the
directional stability of comparative claims in quantum software. It is prepared for
**double-anonymous review**.

Everything reviewer-facing is under [`artifact/`](artifact/). Start with
[`artifact/README.md`](artifact/README.md), which maps each reported result to its
evidence and verification command.

## Main checks

The checks are read-only, run in well under a minute, and do **not** require qiskit
or any quantum simulation. Only `pandas` and `pytest` are needed
(`pip install -r requirements.txt`).

```bash
python3 -m pytest artifact/tests/ -q
python3 artifact/scripts/check_headline_numbers.py
python3 artifact/scripts/check_artifact_files.py
python3 artifact/data/corpus/coding_validity/recompute_agreement.py
python3 artifact/scripts/check_markdown_links.py
python3 artifact/scripts/check_rq4_robustness.py
```

## Layout

- `artifact/` — data, scripts, locked outputs, the 120-item coding-validity package,
  the minimal qiskit-free verdict-core (`artifact/src/`), and the smoke tests
  (`artifact/tests/`).
- `LICENSE` — Apache-2.0.
- `requirements.txt` — minimal dependencies for the reviewer checks.

The artifact is self-contained: the checks above pass from this repository as
mirrored, with no additional setup.

> Note: author names, institutions, acknowledgments, funding, personal URLs, and
> DOIs are intentionally omitted during anonymous review and will be added in the
> camera-ready version.
