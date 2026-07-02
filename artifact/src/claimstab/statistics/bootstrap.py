"""Cluster-bootstrap utilities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from random import Random
from typing import Hashable, Iterable


@dataclass(frozen=True)
class BootstrapInterval:
    """Empirical percentile interval for a bootstrap statistic."""

    lower: float
    upper: float


def cluster_percentile_interval(
    outcomes: Iterable[tuple[Hashable, bool]],
    *,
    n_resamples: int = 1000,
    confidence: float = 0.95,
    seed: int = 0,
) -> BootstrapInterval:
    """Bootstrap a direction-preservation rate by resampling clusters."""

    clusters: dict[Hashable, list[bool]] = defaultdict(list)
    for cluster_id, outcome in outcomes:
        clusters[cluster_id].append(bool(outcome))
    if not clusters:
        return BootstrapInterval(0.0, 1.0)
    keys = list(clusters)
    rng = Random(seed)
    estimates: list[float] = []
    for _ in range(n_resamples):
        sampled: list[bool] = []
        for _ in keys:
            sampled.extend(clusters[rng.choice(keys)])
        estimates.append(sum(sampled) / len(sampled))
    estimates.sort()
    alpha = 1.0 - confidence
    lo_idx = max(0, int((alpha / 2.0) * (n_resamples - 1)))
    hi_idx = min(n_resamples - 1, int((1.0 - alpha / 2.0) * (n_resamples - 1)))
    return BootstrapInterval(estimates[lo_idx], estimates[hi_idx])
