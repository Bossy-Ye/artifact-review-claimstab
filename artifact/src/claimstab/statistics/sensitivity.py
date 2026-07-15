"""Sensitivity-analysis helpers."""

from __future__ import annotations

from collections.abc import Mapping


def count_reclassifications(
    baseline: Mapping[str, str],
    alternative: Mapping[str, str],
) -> int:
    """Count claims whose classification differs between two settings."""

    return sum(
        1
        for claim_id, baseline_class in baseline.items()
        if claim_id in alternative and alternative[claim_id] != baseline_class
    )
