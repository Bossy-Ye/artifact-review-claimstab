"""Unified relation-checker interface (reused from the repo suite; data paths
repointed to the self-contained artifact tree). Pure recomputation over recorded
evidence + toy fixtures; runs no new audit experiments. No qiskit needed."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from claimstab.audit.relation_checkers import (
    RelationCheckInput,
    RelationCheckOutput,
    aggregate_relation_check,
    boundary_check,
    categorical_check,
    crossover_regional_check,
    run_relation_check,
    scalar_directional_wilson_check,
)

ART = Path(__file__).resolve().parents[1]  # artifact/
FOREST = ART / "results/paper/output/figures/section5/external_forest_data.csv"
SD5_CSV = ART / "external_audit/road_b/exc9_pauliopt/per_device_crossover_table.csv"
SD6_CSV = ART / "external_audit/road_b/olsq_claim4/reduction_calculation_table.csv"


def _scalar(k: int, n: int) -> RelationCheckOutput:
    return scalar_directional_wilson_check(
        RelationCheckInput(relation_type="scalar_directional", claim_id="t", params={"k": k, "n": n})
    )


def test_scalar_sustained_unresolved_reversed():
    assert _scalar(80, 80).outcome == "Sustained"
    assert _scalar(44, 80).outcome == "Unresolved"
    assert _scalar(0, 80).outcome.startswith("Reversed")


def test_scalar_zero_cells_is_boundary():
    out = _scalar(0, 0)
    assert out.outcome == "Boundary"
    assert out.boundary_reason


def test_exc_distribution_is_2_4_2():
    counts = {"Sustained": 0, "Unresolved": 0, "Reversed": 0}
    with open(FOREST) as fh:
        for r in csv.DictReader(fh):
            out = _scalar(int(r["k_preserved"]), int(r["n_cells"]))
            key = "Reversed" if out.outcome.startswith("Reversed") else out.outcome
            counts[key] += 1
    assert counts == {"Sustained": 2, "Unresolved": 4, "Reversed": 2}


def test_aggregate_toy_geomean_preserved():
    out = aggregate_relation_check(
        RelationCheckInput(
            relation_type="aggregate_geomean", claim_id="toy",
            params={"ratios": [0.5, 0.25, 0.8], "aggregation": "geomean", "preservation": "ratio_lt_1"},
        )
    )
    assert out.outcome == "Preserved"
    assert out.quantitative_statistic["aggregate_value"] < 1.0


def test_aggregate_toy_not_preserved():
    out = aggregate_relation_check(
        RelationCheckInput(
            relation_type="aggregate_geomean", claim_id="toy",
            params={"ratios": [1.5, 2.0, 1.1], "preservation": "ratio_lt_1"},
        )
    )
    assert out.outcome == "NotPreserved"


def test_sd6_aggregate_preserved_from_source_rows():
    rows = [{"c_a": r["c_olsq"], "c_b": r["c_tket"]} for r in csv.DictReader(open(SD6_CSV))]
    out = aggregate_relation_check(
        RelationCheckInput(
            relation_type="aggregate_geomean", claim_id="SD6", evidence_object=str(SD6_CSV),
            params={"rows": rows, "aggregation": "geomean_cost_ratio", "preservation": "ratio_lt_1",
                    "row_level_diagnostic": {"k": 16, "n": 22}},
        )
    )
    assert out.outcome == "Preserved"
    assert out.quantitative_statistic["aggregate_value"] < 1.0
    assert out.diagnostic_statistic == {"k": 16, "n": 22}


def test_aggregate_row_level_wilson_is_separate_from_verdict():
    row_level = _scalar(16, 22)
    assert row_level.outcome == "Unresolved"
    rows = [{"c_a": r["c_olsq"], "c_b": r["c_tket"]} for r in csv.DictReader(open(SD6_CSV))]
    agg = aggregate_relation_check(
        RelationCheckInput(relation_type="aggregate_geomean", claim_id="SD6",
                           params={"rows": rows, "preservation": "ratio_lt_1"})
    )
    assert agg.outcome == "Preserved"
    assert row_level.outcome != agg.outcome


def test_aggregate_no_usable_rows_is_boundary():
    out = aggregate_relation_check(
        RelationCheckInput(relation_type="aggregate_geomean", claim_id="t",
                           params={"rows": [{"c_a": 0, "c_b": 0}], "preservation": "ratio_lt_1"})
    )
    assert out.outcome == "Boundary"


def test_crossover_all_concordant():
    out = crossover_regional_check(
        RelationCheckInput(relation_type="aggregate_mean_curve_crossover", claim_id="t",
                           params={"concordant": [True] * 5, "rule": "all_concordant"})
    )
    assert out.outcome == "Concordant"
    assert out.quantitative_statistic == {"concordant": 5, "total": 5, "rule": "all_concordant"}


def test_crossover_one_discordant():
    out = crossover_regional_check(
        RelationCheckInput(relation_type="aggregate_mean_curve_crossover", claim_id="t",
                           params={"concordant": [True, True, False, True, True]})
    )
    assert out.outcome == "Discordant"


def test_sd5_crossover_concordant_from_table():
    flags = [r["device_concordant"] == "True" for r in csv.DictReader(open(SD5_CSV))]
    out = crossover_regional_check(
        RelationCheckInput(relation_type="aggregate_mean_curve_crossover", claim_id="SD5",
                           evidence_object=str(SD5_CSV), params={"concordant": flags})
    )
    assert out.outcome == "Concordant"
    assert out.quantitative_statistic["concordant"] == out.quantitative_statistic["total"]


def test_categorical_equality_preserved():
    out = categorical_check(
        RelationCheckInput(relation_type="categorical_equal_or_better", claim_id="t",
                           params={"expected_category": "equivalent", "observed_category": "equivalent",
                                   "relation": "equal"})
    )
    assert out.outcome == "Preserved"


def test_categorical_equality_violated():
    out = categorical_check(
        RelationCheckInput(relation_type="categorical_equal_or_better", claim_id="t",
                           params={"expected_category": "equivalent", "observed_category": "worse",
                                   "relation": "equal"})
    )
    assert out.outcome == "NotPreserved"


def test_categorical_missing_category_is_boundary():
    out = categorical_check(
        RelationCheckInput(relation_type="categorical_equal_or_better", claim_id="t",
                           params={"expected_category": "equivalent", "observed_category": None})
    )
    assert out.outcome == "Boundary"
    assert out.boundary_reason


def test_boundary_bd1_source_inconsistency():
    out = boundary_check(
        RelationCheckInput(relation_type="complete_table_or_series", claim_id="BD1",
                           boundary_metadata={"blocker": "source-table values inconsistent (467x vs 479.5x)",
                                              "flag": "source_reporting"})
    )
    assert out.outcome == "No verdict"
    assert "inconsistent" in out.boundary_reason
    assert "source_reporting" in out.notes


def test_boundary_bd2_runtime_missing_evidence():
    out = boundary_check(
        RelationCheckInput(relation_type="runtime_ratio", claim_id="BD2",
                           boundary_metadata={"blocker": "non-quiesced host; no source runtime data",
                                              "flag": "methodology_limitation"})
    )
    assert out.outcome == "No verdict"
    assert out.boundary_reason
    assert "methodology_limitation" in out.notes


def test_dispatcher_routes_relation_types():
    assert run_relation_check(
        RelationCheckInput("scalar_directional", "t", params={"k": 80, "n": 80})
    ).outcome == "Sustained"
    assert run_relation_check(
        RelationCheckInput("runtime_ratio", "t", boundary_metadata={"blocker": "x"})
    ).outcome == "No verdict"


def test_dispatcher_unknown_relation_raises():
    with pytest.raises(NotImplementedError):
        run_relation_check(RelationCheckInput("not_a_relation", "t"))
