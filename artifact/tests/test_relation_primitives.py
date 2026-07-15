"""Relation primitives + materialization (reused verbatim from the repo suite).
Imports the bundled claimstab.audit (artifact/src via conftest); no qiskit needed."""
import math

import pytest

from claimstab.audit import (
    ComparativeClaim,
    MaterializationStatus,
    MetricDirection,
    RelationType,
    ScalarDirectionalWilsonChecker,
    check_relation_materialization,
    direction_preserved,
)


def test_comparative_claim_resolves_legacy_direction_to_relation():
    claim = ComparativeClaim(
        problem="p",
        baseline_a="A",
        baseline_b="B",
        metric="cost",
        direction=MetricDirection.LOWER_IS_BETTER,
    )

    assert claim.resolved_relation.relation_type is RelationType.SCALAR_DIRECTIONAL
    assert claim.resolved_relation.direction == "<"


def test_scalar_materialization_maps_to_existing_matched_cell_fields():
    card = {
        "relation_type": "scalar_directional",
        "baselines": "A vs B",
        "metric": "cost",
        "direction": "<",
        "instance_universe": "locked cells",
        "active_axes": "L1",
        "comparator_implementation": "source adapter",
        "metric_computation": "structural count",
        "resource_budget": "fixed",
    }

    report = check_relation_materialization(card)

    assert report.status is MaterializationStatus.MATERIALIZED
    assert report.missing_fields == ()


def test_runtime_relation_requires_host_policy():
    card = {
        "relation_type": "runtime_ratio",
        "metric": "runtime",
        "source_universe": "source table",
        "comparator_evidence": "rows",
        "relation_rule": "candidate <= baseline/10",
        "zero_failure_status_convention": "positive times only",
        "artifact_provenance": ("table.csv",),
    }

    report = check_relation_materialization(card)

    assert report.status is MaterializationStatus.INFEASIBLE
    assert "execution_or_host_policy" in report.missing_fields


def test_scalar_wilson_checker_preserves_existing_verdicts():
    card = {
        "relation_type": "scalar_directional",
        "baselines": "A vs B",
        "metric": "cost",
        "direction": "<",
        "instance_universe": "80 cells",
        "active_axes": "L1",
        "comparator_implementation": "source adapter",
        "metric_computation": "structural count",
        "resource_budget": "fixed",
    }

    result = ScalarDirectionalWilsonChecker().check(card, {"successes": 80, "total": 80})

    assert result.verdict == "Sustained"
    assert result.statistics["successes"] == 80
    assert round(result.statistics["wilson_lower"], 3) == 0.954


@pytest.mark.parametrize(
    "direction",
    [MetricDirection.LOWER_IS_BETTER, MetricDirection.HIGHER_IS_BETTER],
)
def test_strict_direction_ties_are_not_preserved(direction):
    assert direction_preserved(1.0, 1.0, direction) is False


def test_practical_threshold_is_inclusive_after_strict_direction():
    assert direction_preserved(1.0, 2.0, MetricDirection.LOWER_IS_BETTER, epsilon=1.0)
    assert not direction_preserved(1.1, 2.0, MetricDirection.LOWER_IS_BETTER, epsilon=1.0)


@pytest.mark.parametrize("epsilon", [-0.1, math.inf, math.nan])
def test_invalid_practical_threshold_is_rejected(epsilon):
    with pytest.raises(ValueError):
        direction_preserved(1.0, 2.0, MetricDirection.LOWER_IS_BETTER, epsilon=epsilon)


def test_nonfinite_metric_margin_is_rejected():
    with pytest.raises(ValueError):
        direction_preserved(math.inf, 1.0, MetricDirection.LOWER_IS_BETTER)
