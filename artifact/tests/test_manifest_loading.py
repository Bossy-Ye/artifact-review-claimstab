"""Manifest / locking-layer loading smoke test (qiskit-free, stdlib csv only).

Section IV's locking layer + evidence manifests are evidenced in the artifact as
DATA. This test asserts those manifests parse and carry the expected RQ2 records
(EX-C1..C8, SD1..SD7, BD1..BD2) and boundary rows.
"""
from __future__ import annotations

import csv
from pathlib import Path

ART = Path(__file__).resolve().parents[1]  # artifact/
LEDGER = ART / "rq2_audit_design_ledger.csv"
EVIDENCE = ART / "dry_run_visibility/evidence_inventory.csv"

EXACT = {f"EX-C{i}" for i in range(1, 9)}
SD = {f"SD{i}" for i in range(1, 8)}
BD = {"BD1", "BD2"}


def _ids(path: Path, col: str) -> set[str]:
    return {r[col].strip() for r in csv.DictReader(open(path))}


def test_rq2_ledger_has_17_records_ex_sd_bd() -> None:
    rows = list(csv.DictReader(open(LEDGER)))
    ids = {r["unit_id"].strip() for r in rows}
    assert len(rows) == 17
    assert EXACT <= ids                       # 8 exact records
    assert SD <= ids                          # 7 relation-level records
    assert BD <= ids                          # 2 boundary records


def test_boundary_records_have_no_verdict() -> None:
    rows = {r["unit_id"].strip(): r for r in csv.DictReader(open(LEDGER))}
    for bd in BD:
        formal = rows[bd]["formal_outcome"].lower()
        assert "no verdict" in formal


def test_evidence_inventory_covers_all_rq2_units() -> None:
    ids = _ids(EVIDENCE, "unit_id")
    assert EXACT <= ids and SD <= ids and BD <= ids


def test_exact_records_are_scalar_directional() -> None:
    rows = {r["unit_id"].strip(): r for r in csv.DictReader(open(LEDGER))}
    for ex in EXACT:
        assert "scalar_directional" in rows[ex]["source_relation_type"].lower()
