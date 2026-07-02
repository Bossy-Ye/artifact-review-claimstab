"""Comparative claim representation and signed-margin helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .relations import RelationSpec, RelationType


class MetricDirection(str, Enum):
    """Direction of metric improvement."""

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


@dataclass(frozen=True)
class ComparativeClaim:
    """Claim card C = <P, B_A, B_B, M, R>.

    `direction` is preserved for existing scalar-directional callers. If
    `relation` is omitted, `resolved_relation` maps the legacy direction field to
    `R.type=scalar_directional`.
    """

    problem: str
    baseline_a: str
    baseline_b: str
    metric: str
    direction: MetricDirection
    operational_scope: str | None = None
    relation: RelationSpec | None = None

    @property
    def resolved_relation(self) -> RelationSpec:
        if self.relation is not None:
            return self.relation
        direction = "<" if self.direction == MetricDirection.LOWER_IS_BETTER else ">"
        return RelationSpec(relation_type=RelationType.SCALAR_DIRECTIONAL, direction=direction)


def signed_margin(metric_a: float, metric_b: float, direction: MetricDirection) -> float:
    """Return a positive margin when A is directionally better than B."""

    if direction == MetricDirection.LOWER_IS_BETTER:
        return metric_b - metric_a
    if direction == MetricDirection.HIGHER_IS_BETTER:
        return metric_a - metric_b
    raise ValueError(f"Unsupported metric direction: {direction}")


def direction_preserved(
    metric_a: float,
    metric_b: float,
    direction: MetricDirection,
    *,
    epsilon: float = 0.0,
) -> bool:
    """Return whether the asserted direction is preserved in one audit cell."""

    return signed_margin(metric_a, metric_b, direction) >= epsilon
