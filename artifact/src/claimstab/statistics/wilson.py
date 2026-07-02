"""Wilson confidence intervals."""

from __future__ import annotations

from dataclasses import dataclass

from claimstab.inference.policies import wilson_interval


@dataclass(frozen=True)
class WilsonResult:
    k: int
    n: int
    rate: float
    lower: float
    upper: float
    confidence: float


def wilson_ci(k: int, n: int, confidence: float = 0.95) -> WilsonResult:
    lower, upper = wilson_interval(successes=k, total=n, confidence=confidence)
    return WilsonResult(
        k=k,
        n=n,
        rate=0.0 if n == 0 else k / n,
        lower=lower,
        upper=upper,
        confidence=confidence,
    )
