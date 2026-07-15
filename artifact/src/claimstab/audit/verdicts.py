"""ClaimStab-QC three-state verdict rule."""

from __future__ import annotations

from enum import Enum


class ClaimStatus(str, Enum):
    SUSTAINED = "Sustained"
    UNRESOLVED = "Unresolved"
    REVERSED = "Reversed within audited scope"


def classify_direction_preservation(
    wilson_lower: float,
    wilson_upper: float,
    *,
    tau: float = 0.95,
) -> ClaimStatus:
    """Classify a direction-preservation rate from its Wilson CI."""

    if not 0.0 <= tau <= 1.0:
        raise ValueError(f"tau must be in [0,1], got {tau}")
    if wilson_lower >= tau:
        return ClaimStatus.SUSTAINED
    if wilson_upper <= 1.0 - tau:
        return ClaimStatus.REVERSED
    return ClaimStatus.UNRESOLVED
