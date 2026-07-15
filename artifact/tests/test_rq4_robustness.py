"""RQ4 robustness alignment tests.

Assert the artifact's recorded RQ4 evidence matches the paper's Table IV / RQ4
finding (verdicts mostly stable under tested checks, but not uniformly). csv-only,
qiskit-free; reads the locked Tier-1 robustness tables.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T1 = ROOT / "artifact/external_audit/tier1_robustness"
SECTION5 = ROOT / "artifact/results/paper/output/figures/section5"
BUDGET = ROOT / "artifact/external_audit/budget_sensitivity"


def _rows(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_exc7_primary_zero_of_80() -> None:
    prim = {r["record_id"]: r for r in _rows(T1 / "tier1_primary_evidence.csv")}
    assert int(prim["EX-C7"]["preserved"]) == 0
    assert int(prim["EX-C7"]["N"]) == 80


def test_exc7_seed_expansion_zero_of_320() -> None:
    seed = _rows(BUDGET / "expanded_seed_sensitivity.csv")
    r320 = [r for r in seed if r["record_id"] == "EX-C7" and int(r["N"]) == 320]
    assert len(r320) == 1 and int(r320[0]["k_preserved"]) == 0


def test_exc3_cluster_sensitive() -> None:
    clu = {r["record_id"]: r for r in _rows(T1 / "tier1_cluster_resampling.csv")}
    assert "sensitive" in clu["EX-C3"]["cluster_status"].lower()


def test_exc2_exc4_dependence_unavailable() -> None:
    clu = {r["record_id"]: r for r in _rows(T1 / "tier1_cluster_resampling.csv")}
    assert "not-available" in clu["EX-C2"]["cluster_status"].lower()
    assert "not-available" in clu["EX-C4"]["cluster_status"].lower()


def test_tau99_softens_finite_n_extremes() -> None:
    thr = _rows(T1 / "tier1_threshold_sensitivity.csv")
    soft = {r["record_id"] for r in thr if r["tau"] == "0.99" and r["changed_from_primary"] == "True"}
    assert soft == {"EX-C1", "EX-C2", "EX-C7", "EX-C8"}
    assert all(r["changed_from_primary"] == "False" for r in thr if r["tau"] in ("0.9", "0.95"))


def test_exc7_tie_policy_bounded() -> None:
    tie = [r for r in _rows(T1 / "tier1_tie_policy_sensitivity.csv") if r["record_id"] == "EX-C7"]
    main = next(r for r in tie if r["tie_policy"] == "main_ties_nonpreserving")
    excl = next(r for r in tie if r["tie_policy"] == "ties_excluded")
    half = next(r for r in tie if r["tie_policy"] == "ties_half_preserving")
    assert main["verdict_projection"] == "Reversed" and float(main["preserved_effective"]) == 0.0
    assert float(excl["preserved_effective"]) == 0.0          # 0 actual preserved
    assert excl["changed_from_primary"] == "True" and half["changed_from_primary"] == "True"


def test_no_forbidden_overclaims_in_tier1_docs() -> None:
    forbidden = ["all verdicts are stable", "stable under all", "robust under all",
                 "fully robust", "no sensitivity", "unqualifiedly robust"]
    blob = "\n".join(p.read_text().lower() for p in T1.glob("*.md"))
    assert not [f for f in forbidden if f in blob]
