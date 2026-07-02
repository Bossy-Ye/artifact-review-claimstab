# `artifact/src/` — minimal verdict-core of CLAIMSTAB-QC

This is a **minimal, dependency-light extract** of the CLAIMSTAB-QC framework
(Section IV). It bundles only the modules that compute the verdict logic, so a
reviewer can run the actual code that produces the paper's outcomes. It is **not**
the full framework: the qiskit-dependent pipeline, runner, figure, and experiment
code is intentionally excluded (the full source lives in the project repository).

## What is here (`src/claimstab/`, 21 files, ~1.2k LOC, pure Python)

| Module | Section IV role |
|---|---|
| `inference/policies.py` | Wilson interval + S/U/R policy |
| `statistics/wilson.py`, `bootstrap.py`, `sensitivity.py` | `wilson_ci`; cluster bootstrap; tau/N sensitivity |
| `audit/relation_checkers.py`, `relations.py`, `verdicts.py`, `cells.py`, `claims.py`, `runner.py` | relation checkers (scalar Wilson, aggregate, crossover, categorical, boundary), verdict classification, materialization check |
| `core_objects/cro.py`, `drr.py`, `oap.py` | comparison/claim core objects |
| `external_ingestion/external_claim.py` | `ExternalClaimRecord` (claim registry record) |

The top-level `claimstab/__init__.py` is a trimmed stub so importing the bundle does
**not** pull in qiskit. No external dependency is needed for the verdict-core
(`pandas` is used only by the funnel test).

## What is NOT here

`pipelines/`, `figures/`, `runners/`, `experiments/`, `atlas/`, `tasks/`,
`commands/`, `devices/`, `claims/` (qiskit-entangled), the evidence/locking code
(`evidence/protocol.py`, `core/trace.py`, also qiskit-entangled — the locking and
manifest claims are evidenced instead by the shipped data in
`artifact/dry_run_visibility/evidence_inventory.csv` and `artifact/rq2_audit_design_ledger.csv`).

## Run the smoke tests (no qiskit required)

```bash
python3 -m pytest artifact/tests/ -q
```

`artifact/tests/conftest.py` puts `artifact/src` first on `sys.path`, so the tests
exercise *this* bundled package. Tests:
- `test_wilson_rule.py` — Wilson math + bundled `wilson_ci` reproduces EX-C3 (62/80 → Unresolved) and EX-C7 (0/80 → Reversed).
- `test_relation_checkers.py` / `test_relation_primitives.py` — the relation-checker interface; reproduces the 2/4/2 distribution and SD5/SD6 outcomes from shipped evidence.
- `test_funnel_counts.py` — reconciles 455/175/145/93/79/53/8 and the RQ2/RQ3/RQ4 distributions from the shipped CSVs (needs `pandas`).
- `test_manifest_loading.py` — the RQ2 ledger + evidence inventory parse and carry EX-C1..C8 / SD1..SD7 / BD1..BD2.

Spot-check the Wilson rule reproduces an audit record directly:

```bash
python3 -c "import sys; sys.path.insert(0,'artifact/src'); \
from claimstab.statistics import wilson_ci; print(wilson_ci(62,80))"
```
