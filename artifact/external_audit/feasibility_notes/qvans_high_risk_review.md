# Focused QVAns High-Risk Tier Review

## Scope

Reviewed the two high-risk materialization rows from `2308.01789v1`:

- `ext_2308_01789v1_claim1`
- `ext_2308_01789v1_claim2`

No adapters were implemented, no locked results were modified, and no N=80 audit was run.

## Artifact Inspection

- Repository inspected: `/private/tmp/qvans`
- Repository commit: `6ee11399dd89b82709cf51da902f2af22d8495fd`
- Artifact status: public repository available.
- Dependency status in current environment: `cirq`, `tensorflow`, and `tensorflow_quantum` are not installed; the repository requires legacy Python 3.7-3.9 / TensorFlow Quantum stack.
- Repository contents relevant to this review: VAns implementation (`main.py`, `utilities/`), tutorials, TFIM example results.
- Missing for the approved claims: a Table II/III benchmark reproduction path for EVQE, RA-VQE, QAOA, exact QUBO instance seeds/data, and per-instance gate/CNOT outputs.

## Paper Evidence

The paper provides useful aggregate information:

- It reports ten QUBO instances per problem type and size.
- It reports COBYLA as the parameter optimizer.
- It reports computational budgets and selected hyperparameters in Table IV.
- Tables II and III provide aggregate approximation ratio, expectation, gates, CNOT, and time.

This is enough to understand and verify the published table qualitatively, but not enough to run a no-proxy ClaimStab-QC audit with N=80 meaningful perturbation cells.

## Claim Decisions

| Claim | Recommended tier | Include in main audit? | Reason |
|---|---|---:|---|
| `ext_2308_01789v1_claim1` | keep_T3 | no | Comparator benchmark surface is incomplete; EVQE/RA-VQE/QAOA reproduction and exact QUBO instances are not materialized. |
| `ext_2308_01789v1_claim2` | keep_T3 | no | VAns is implemented, but the full no-proxy comparison against EVQE/RA-VQE/QAOA over the reported benchmark surface is not available. |

## N=80 Audit Meaningfulness

N=80 audit cells are not meaningful from the available artifact. Repeating aggregate table values would reproduce a deterministic resource table, not a perturbation audit. Creating cells by generating new QUBO instances or rerunning substituted comparator implementations would require proxy assumptions.

## Smoke Test Decision

No 5-cell smoke test was attempted. The validation gate failed before smoke-test execution because the required comparator and benchmark materialization is incomplete.

## Final Recommendation

Keep both rows as T3. If discussed in the paper, characterize them as evidence of the gap between paper-level resource-table claims and executable stability-audit materialization, not as failed empirical claims.
