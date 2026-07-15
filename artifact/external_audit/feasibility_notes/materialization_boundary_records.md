# External-Claim Materialization Boundary Records

This file records selected T3/T4 claims that do not enter the completed external
audit set because the available evidence cannot define a proxy-free perturbation
surface. It supports the materialization boundary without changing any claim tier or
verdict.

| claim_id | paper_id | domain | tier | evidence boundary |
|---|---|---|---|---|
| `ext_2308_02536v1_legacy_claim2` | 2308.02536v1 | Compilation/transpilation | T3 | Available evidence supports a proxy or static verification path, not a perturbation audit. |
| `ext_2110_00592v2_claim1` | 2110.00592v2 | Compilation/transpilation | T4 | The required baseline implementation is unavailable for a bounded artifact audit. |
| `ext_2110_00592v2_claim2` | 2110.00592v2 | Compilation/transpilation | T4 | Required baseline implementations are unavailable. |
| `ext_2110_00592v2_claim3` | 2110.00592v2 | Compilation/transpilation | T4 | The required baseline implementation is unavailable. |
| `ext_2007_15671v1_claim5` | 2007.15671v1 | Compilation/transpilation | T3 | Reconstructing the metric and solver implementation would introduce proxy assumptions. |
| `ext_2302_04479v2_claim1` | 2302.04479v2 | Optimization/VQE/QAOA | T3 | The exact instance set and baseline scripts are not materialized; replacement data would be proxy evidence. |
| `ext_2302_04479v2_claim3` | 2302.04479v2 | Optimization/VQE/QAOA | T3 | The original dataset is not materialized, so reimplementation would introduce proxy evidence. |
