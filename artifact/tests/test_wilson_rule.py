"""Wilson S/U/R rule — reference math + the bundled implementation agree.

Reused from the repo's tests/test_statistics.py, extended to also exercise the
bundled `claimstab.statistics.wilson_ci`. No qiskit/pandas needed.
"""
from __future__ import annotations

import math

from claimstab.statistics import wilson_ci  # bundled (artifact/src via conftest)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        raise ValueError("n must be positive")
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def classify(wilson_lower: float, wilson_upper: float, tau: float = 0.95) -> str:
    if wilson_lower >= tau:
        return "Sustained"
    if wilson_upper <= 1 - tau:
        return "Reversed"
    return "Unresolved"


def test_wilson_interval_all_successes_n80() -> None:
    lower, upper = wilson_interval(80, 80)
    assert math.isclose(lower, 0.954186, abs_tol=1e-4)
    assert math.isclose(upper, 1.0, abs_tol=1e-9)


def test_wilson_interval_all_failures_n80() -> None:
    lower, upper = wilson_interval(0, 80)
    assert math.isclose(lower, 0.0, abs_tol=1e-9)
    assert math.isclose(upper, 0.045814, abs_tol=1e-4)


def test_classification_rule() -> None:
    assert classify(0.954, 1.0) == "Sustained"
    assert classify(0.323, 0.534) == "Unresolved"
    assert classify(0.0, 0.046) == "Reversed"


def test_bundled_wilson_reproduces_exc3() -> None:
    # The bundled implementation reproduces the EX-C3 audit record (62/80).
    r = wilson_ci(62, 80)
    assert r.k == 62 and r.n == 80
    assert math.isclose(r.lower, 0.6721, abs_tol=1e-3)
    assert math.isclose(r.upper, 0.8527, abs_tol=1e-3)
    # Unresolved at tau=0.95 (lower < 0.95 and upper > 0.05).
    assert classify(r.lower, r.upper) == "Unresolved"


def test_bundled_wilson_reproduces_exc7_reversed() -> None:
    r = wilson_ci(0, 80)
    assert classify(r.lower, r.upper) == "Reversed"
