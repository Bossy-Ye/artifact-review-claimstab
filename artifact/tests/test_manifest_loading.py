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
CARDS = ART / "claim_cards"
REPO = ART.parent

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
    rows = list(csv.DictReader(open(EVIDENCE, newline="")))
    assert all(None not in row for row in rows), "evidence inventory has unquoted extra CSV fields"
    ids = {row["unit_id"].strip() for row in rows}
    assert EXACT <= ids and SD <= ids and BD <= ids


def test_exact_records_are_scalar_directional() -> None:
    rows = {r["unit_id"].strip(): r for r in csv.DictReader(open(LEDGER))}
    for ex in EXACT:
        assert "scalar_directional" in rows[ex]["source_relation_type"].lower()


def _card_value(path: Path, key: str) -> str:
    prefix = f"{key}:"
    line = next(line for line in path.read_text().splitlines() if line.startswith(prefix))
    return line.split(":", 1)[1].strip().strip('"')


def test_claim_cards_point_to_shipped_result_and_cell_evidence() -> None:
    unavailable = set()
    per_cell = set()
    for card in sorted(CARDS.glob("EX-C*.yaml")):
        claim_id = _card_value(card, "claim_id")
        result = _card_value(card, "result_source")
        assert (REPO / result).is_file(), f"{claim_id}: missing result_source {result}"

        cell_log = _card_value(card, "locked_cell_log")
        if cell_log.startswith("UNAVAILABLE"):
            unavailable.add(claim_id)
        else:
            assert (REPO / cell_log).is_file(), f"{claim_id}: missing locked_cell_log {cell_log}"
            per_cell.add(claim_id)

    assert per_cell == {"EX-C1", "EX-C3", "EX-C5", "EX-C6", "EX-C7", "EX-C8"}
    assert unavailable == {"EX-C2", "EX-C4"}


def test_claim_cards_declare_all_six_audit_axes() -> None:
    for card in sorted(CARDS.glob("EX-C*.yaml")):
        text = card.read_text()
        for axis in ("S_scope", "L1", "L2", "L3", "ALGO", "resource_budget"):
            assert f"  {axis}:" in text, f"{card.name}: missing axis {axis}"
