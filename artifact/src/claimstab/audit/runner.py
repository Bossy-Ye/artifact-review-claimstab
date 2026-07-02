"""Small audit-runner helpers shared by adapters and reports."""

from __future__ import annotations

from collections.abc import Iterable

from .claims import MetricDirection, direction_preserved, signed_margin


def preservation_outcomes(
    rows: Iterable[dict[str, float | str]],
    *,
    metric_a_col: str = "metric_A",
    metric_b_col: str = "metric_B",
    direction: MetricDirection,
    epsilon: float = 0.0,
) -> list[bool]:
    """Compute direction-preservation booleans from cell-level metric rows."""

    outcomes: list[bool] = []
    for row in rows:
        outcomes.append(
            direction_preserved(
                float(row[metric_a_col]),
                float(row[metric_b_col]),
                direction,
                epsilon=epsilon,
            )
        )
    return outcomes


def signed_margins(
    rows: Iterable[dict[str, float | str]],
    *,
    metric_a_col: str = "metric_A",
    metric_b_col: str = "metric_B",
    direction: MetricDirection,
) -> list[float]:
    """Compute signed margins from cell-level metric rows."""

    return [
        signed_margin(float(row[metric_a_col]), float(row[metric_b_col]), direction)
        for row in rows
    ]
