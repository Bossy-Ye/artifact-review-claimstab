# Focused QVAns Materialization-Feasibility Review

This record assesses whether two QVAns claims from `2308.01789v1` can support a
proxy-free perturbation audit from the available source artifact:

- `ext_2308_01789v1_claim1`
- `ext_2308_01789v1_claim2`

Boundary: this review evaluates materialization feasibility. It does not introduce
an adapter, modify locked results, or report an N=80 verdict.

## Source-artifact evidence

- Source repository commit inspected: `6ee11399dd89b82709cf51da902f2af22d8495fd`.
- Public artifact contents: VAns implementation (`main.py`, `utilities/`), tutorials,
  and TFIM example results.
- Toolchain requirement: legacy Python 3.7–3.9 with TensorFlow Quantum, including
  `cirq`, `tensorflow`, and `tensorflow_quantum`.
- Evidence boundary: the source artifact does not materialize the Table II/III
  EVQE, RA-VQE, and QAOA comparator surface, exact QUBO instance seeds/data, or
  per-instance gate/CNOT outputs needed for the reported comparisons.

## Paper evidence

The paper reports ten QUBO instances per problem type and size, COBYLA as the
parameter optimizer, computational budgets and selected hyperparameters in Table IV,
and aggregate approximation-ratio, expectation, gate, CNOT, and timing values in
Tables II and III. These aggregates support qualitative table inspection but do not
provide the per-cell comparator evidence required for a proxy-free N=80 stability
audit.

## Claim decisions

| Claim | Tier | Included in main audit? | Evidence boundary |
|---|---|---:|---|
| `ext_2308_01789v1_claim1` | keep_T3 | no | The EVQE/RA-VQE/QAOA comparator surface and exact QUBO instances are not materialized. |
| `ext_2308_01789v1_claim2` | keep_T3 | no | VAns is implemented, but the reported multi-comparator benchmark surface is not materialized. |

## N=80 and smoke-test boundary

The available artifact cannot define 80 proxy-free perturbation cells for these
comparisons. Repeating aggregate table values would be static verification, while
new QUBO instances or substituted comparator implementations would introduce proxy
assumptions. The materialization gate therefore stops before a five-cell smoke test.

## Reviewer interpretation

Both rows remain T3. They document the boundary between paper-level resource-table
claims and an executable stability-audit surface; they do not report empirical
audit outcomes.
